"""The tool registry (BUILD_SPEC §7.2, CLAUDE.md rule 4).

Every capability she has reaches the machine through here, carrying an explicit
permission tier. There is no second path: an ad-hoc `subprocess.run` somewhere
in a handler is exactly the thing the tier engine exists to prevent, and it
would not appear in `tool_log` either (rule 6).

**The schema is derived, never written twice.** §7.2 is explicit about it, and
the reason is drift: a hand-maintained JSON schema beside a Python signature
disagrees with it the first time an argument is renamed, and the model is then
being told about a function that does not exist. Type hints and the docstring
are the single source.
"""

from __future__ import annotations

import inspect
import re
from collections.abc import Awaitable, Callable, Collection
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, get_args, get_origin, get_type_hints

import structlog
from pydantic import BaseModel

log = structlog.get_logger(__name__)


class Tier(IntEnum):
    """How much damage a tool can do, and therefore what it must ask first.

    The number matters: `permissions.py` compares tiers with `>=`, and the
    ordering *is* the policy.
    """

    #: Read-only, no side effects. Runs silently.
    AUTO = 0
    #: Reversible side effects. Runs, and is shown in the UI afterwards.
    SAFE = 1
    #: Modifies user data or reaches the network. Blocks on approval.
    CONFIRM = 2
    #: Irreversible. Blocks on *typed* approval, and is off by default.
    DANGER = 3


class ToolResult(BaseModel):
    """What a tool hands back.

    The split between `summary` and `display` is load-bearing. §7.2 names
    blowing up the context window with tool output as the second most common
    failure mode: `summary` is the one line the *model* sees, and everything
    bulky goes to `display`, which only the UI ever reads. A tool that finds
    4,000 files summarises them; it does not paste them into the conversation.
    """

    ok: bool
    data: Any = None
    #: ONE line, for the model. Keep it short.
    summary: str
    #: Richer payload for the UI only. Never enters the prompt.
    display: dict[str, Any] | None = None
    error: str | None = None


@dataclass(frozen=True)
class ToolContext:
    """Ambient facts a tool may need, passed rather than reached for.

    Tools take this as their first argument so they never import `runtime` and
    can be called directly from a test with nothing running.
    """

    session_id: str | None = None
    turn_id: str | None = None


#: Tools that reach the internet, and are therefore hidden from the model
#: unless online mode is on. Named here rather than in `conversation.py` so
#: adding a second web tool cannot forget the gate.
ONLINE_TOOLS = frozenset({"research"})

#: Tools whose result is somebody else's writing, not this machine's own
#: state — a search result, a fetched page. §11: "any tool call triggered
#: within one step of reading untrusted content is force-escalated to T2
#: confirmation." `research.py`'s own docstring names the reason this could
#: not be built until the agent loop existed: one tool ran per turn, so there
#: was never a "next call" for the rule to apply to. `core/agent.py` is where
#: it now applies — after a step whose tool is in this set, the *next* step's
#: tool is forced through confirmation regardless of its own registered tier,
#: because a webpage that says "delete everything in Downloads" is a live
#: attack vector the moment something reads pages and can also act.
UNTRUSTED_SOURCE_TOOLS = frozenset({"research", "browser_read", "browser_navigate"})

#: Tools that need somebody looking at the screen, and are therefore hidden
#: from the model on a turn that arrived by voice.
#:
#: `ask_user` puts four options on screen and waits for a click. Said aloud to
#: someone across the room that is a dead end, and it is the *same* dead end
#: the confirmation dialog already has to work around by bringing the window
#: forward. Hiding the tool is the honest version: she asks in words instead,
#: which is what actually works hands-free.
#:
#: Same mechanism as `ONLINE_TOOLS` — named here so a second screen-bound tool
#: cannot forget the gate — and the same lesson behind both: telling a model a
#: tool exists and then having it not work is how "let me look that up"
#: becomes a promise she does not keep.
SCREEN_ONLY_TOOLS = frozenset({"ask_user"})

ToolFn = Callable[..., Awaitable[ToolResult]]
#: A tool's own arguments in, a JSON-serialisable summary of what would
#: happen out. See `Tool.preview`.
PreviewFn = Callable[..., Awaitable["dict[str, Any] | None"]]
#: A tool's own arguments in (as keywords, like `PreviewFn`), whether *this*
#: call should be forced through confirmation regardless of its own
#: registered tier. See `Tool.escalate`.
EscalateFn = Callable[..., Awaitable[bool]]
#: A tool's own arguments in, a refusal reason out (or None to proceed). See
#: `Tool.refuse`.
RefuseFn = Callable[..., Awaitable["str | None"]]


@dataclass(frozen=True)
class Tool:
    name: str
    tier: Tier
    description: str
    parameters: dict[str, Any]
    fn: ToolFn
    #: This tool's result must not reach a cloud model. The tier says whether
    #: she may run it; this says where the *answer* is allowed to go, which is
    #: a different question — reading the clipboard is harmless, and sending
    #: what it contained to someone else's server is not.
    #:
    #: `core/conversation.py` moves the continuation pass onto the local model
    #: when a tool declares this. That has to happen after the call rather than
    #: before it, because the continuation is where the result enters a prompt.
    local_only: bool = False
    #: Compute what the user is being asked to approve, before it happens.
    #:
    #: **The confirmation fires before the tool body runs**, and `ToolContext`
    #: carries no event bus — so a tool that works out a plan is structurally
    #: unable to be the tool that shows it. Without this, `organize_folder` can
    #: only put its raw arguments in front of the user (`path`, `strategy`),
    #: which says nothing about the thirty files about to move. BUILD_SPEC §7.2
    #: asks for the opposite: "if the agent wants to move 30 files, emit **one**
    #: `confirm.request` describing the batch, not 30. Include the full file
    #: list."
    #:
    #: Called with the tool's own arguments, never `ctx`. Must not mutate
    #: anything — it runs whether or not the user then approves — and must not
    #: raise: a preview that fails falls back to showing the arguments, because
    #: losing the *confirmation* would be far worse than losing the detail.
    preview: PreviewFn | None = None
    #: A second, independent reason to force confirmation — not §11's
    #: `force_confirm` (a decision the *agent loop* makes from the previous
    #: step), but one the tool itself makes from *this* call's own arguments
    #: or live state. Built for `tools/browser.py`'s checkout/banking hard
    #: block (BUILD_SPEC §9:943): "any page whose URL or DOM matches banking,
    #: payment, or checkout patterns requires T2 confirmation regardless of
    #: tool tier." `browser_navigate` is ordinarily SAFE and would otherwise
    #: never ask at all.
    #:
    #: A check that raises escalates anyway — fail closed, not open. This is
    #: the one hook in this file where "detail lost, confirmation kept" is
    #: the wrong default: the entire point is deciding *whether* to ask, and
    #: a broken detector silently waving through a checkout page is worse
    #: than an unnecessary confirmation on an ordinary one.
    escalate: EscalateFn | None = None
    #: A hard block, checked **before** any confirmation would fire — not a
    #: dialog that can be declined, a call that never reaches one. Built for
    #: `browser_fill`'s password-field refusal (§9:943): approving a fill
    #: without knowing it targets a password field is not a choice anyone
    #: should be asked to make, so the choice is never offered. Returns a
    #: reason to refuse, or None to proceed as normal. A check that raises is
    #: treated as "no reason found" — this one is a cheap, synchronous read of
    #: the call's own arguments, not live page state, so failing open here
    #: does not carry `escalate`'s risk.
    refuse: RefuseFn | None = None

    @property
    def schema(self) -> dict[str, Any]:
        """The OpenAI/Ollama tool-calling shape."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


_REGISTRY: dict[str, Tool] = {}

# Python type -> JSON schema type. Anything unmapped becomes a string, which
# every model can produce and every tool can validate for itself.
_JSON_TYPES: dict[Any, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}

# "    name: what it is" inside an Args: block.
_ARG_DOC = re.compile(r"^\s*(\w+)\s*:\s*(.+)$")


def _json_type(annotation: Any) -> dict[str, Any]:
    """One annotation into a JSON-schema fragment.

    `str | None` is unwrapped to its non-None member: optionality is expressed
    by absence from `required`, not by a union in the type, and models handle
    that far more reliably than a nullable.
    """
    origin = get_origin(annotation)
    if origin is not None:
        args = [a for a in get_args(annotation) if a is not type(None)]
        if origin in (list, set, tuple):
            inner = _json_type(args[0]) if args else {"type": "string"}
            return {"type": "array", "items": inner}
        if len(args) == 1:
            return _json_type(args[0])
        return {"type": "string"}
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return _model_schema(annotation)
    return {"type": _JSON_TYPES.get(annotation, "string")}


def _model_schema(model: type[BaseModel]) -> dict[str, Any]:
    """A pydantic model as an inline JSON-schema object.

    Without this a `list[Question]` came out as `{"type": "array", "items":
    {"type": "object"}}` — an object with no properties, which tells the model
    nothing about the shape it is supposed to produce, so it guesses.

    **Inlined, with no `$defs` or `$ref`.** Pydantic hoists nested models into
    `$defs` and refers to them, which several providers reject outright and the
    rest handle unevenly. Flattening keeps one self-contained fragment per
    argument, which is what every provider's function-calling schema expects.
    """
    schema = model.model_json_schema()
    defs = schema.pop("$defs", {})

    def inline(node: Any) -> Any:
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/$defs/"):
                return inline(defs.get(ref.removeprefix("#/$defs/"), {"type": "object"}))
            return {key: inline(value) for key, value in node.items()}
        if isinstance(node, list):
            return [inline(item) for item in node]
        return node

    def untitled(node: Any) -> Any:
        """Drop every `title`, at every depth.

        Cosmetic on the wire and worth dropping: pydantic emits one per class
        and one per field, all of them restating the key they hang off, in a
        block that is already ~1650 tokens. Recursive because the first version
        only reached the top level and left the nested model's titles behind.
        """
        if isinstance(node, dict):
            return {k: untitled(v) for k, v in node.items() if k != "title"}
        if isinstance(node, list):
            return [untitled(item) for item in node]
        return node

    resolved: dict[str, Any] = untitled(inline(schema))
    return resolved


def _arg_docs(doc: str) -> dict[str, str]:
    """Per-argument descriptions out of a Google-style Args: block.

    These are what the model actually reads to decide what to put in a field,
    so they are worth more than the function description on its own.

    **Wrapped lines are joined**, and that is not a nicety. A description was
    silently cut at the first line break, so `remember` had been handing every
    model `The thing to remember, in plain words, e.g. "I work on Sillara` —
    truncated mid-example, with an unterminated quote — since Phase 5. Anything
    that needed more than one line to explain was documented for humans and
    hidden from the only reader that matters.
    """
    lines = doc.splitlines()
    descriptions: dict[str, str] = {}
    order: list[str] = []
    inside = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("args:"):
            inside = True
            continue
        if not inside:
            continue
        if not stripped or (stripped.endswith(":") and " " not in stripped):
            break
        match = _ARG_DOC.match(line)
        if match:
            descriptions[match.group(1)] = match.group(2).strip()
            order.append(match.group(1))
        elif order:
            descriptions[order[-1]] += " " + stripped
    return descriptions


def build_parameters(fn: ToolFn) -> dict[str, Any]:
    """Derive a JSON schema from a tool's signature and docstring."""
    hints = get_type_hints(fn)
    signature = inspect.signature(fn)
    docs = _arg_docs(fn.__doc__ or "")

    properties: dict[str, Any] = {}
    required: list[str] = []
    for name, parameter in signature.parameters.items():
        # `ctx` is supplied by the executor, not the model, so it must not
        # appear in the schema at all — offered as a field, models try to fill
        # it, and then argue with themselves about what a session id is.
        if name in ("ctx", "self") or name == "return":
            continue
        field = _json_type(hints.get(name, str))
        if name in docs:
            field["description"] = docs[name]
        properties[name] = field
        if parameter.default is inspect.Parameter.empty:
            required.append(name)

    return {"type": "object", "properties": properties, "required": required}


def tool(
    *,
    name: str,
    tier: Tier,
    description: str,
    local_only: bool = False,
    preview: PreviewFn | None = None,
    escalate: EscalateFn | None = None,
    refuse: RefuseFn | None = None,
) -> Callable[[ToolFn], ToolFn]:
    """Register a coroutine as a tool.

    The function is returned unchanged, so it stays directly callable and a
    test can exercise it without the registry, the tier engine, or a model.
    """

    def decorator(fn: ToolFn) -> ToolFn:
        if name in _REGISTRY:
            raise RuntimeError(f"Tool {name!r} is already registered.")
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(f"Tool {name!r} must be async (CLAUDE.md rule 7).")
        _REGISTRY[name] = Tool(
            name=name,
            tier=tier,
            description=description,
            parameters=build_parameters(fn),
            fn=fn,
            local_only=local_only,
            preview=preview,
            escalate=escalate,
            refuse=refuse,
        )
        return fn

    return decorator


def get(name: str) -> Tool | None:
    return _REGISTRY.get(name)


def names() -> list[str]:
    return sorted(_REGISTRY)


def all_tools() -> list[Tool]:
    return [_REGISTRY[n] for n in sorted(_REGISTRY)]


def schemas(
    *, tier_max: Tier = Tier.CONFIRM, exclude: Collection[str] = ()
) -> list[dict[str, Any]]:
    """Tool schemas for the model, up to and including `tier_max`.

    **DANGER is excluded by default**, which is what §7.2 means by "off by
    default": the model is not told those tools exist unless something
    deliberately raises the ceiling. A capability the model cannot see is one
    it cannot be talked into using.

    `exclude` is the same idea for a capability that is switched off rather
    than dangerous — online mode. Not a relevance filter: that question is
    closed and measured (see CLAUDE.md), and this set changes only when a
    setting does, so the stable prefix still holds its KV cache across a
    conversation.
    """
    return [
        t.schema for t in all_tools() if t.tier <= tier_max and t.name not in exclude
    ]


def snapshot() -> dict[str, Tool]:
    """A copy of the registry, for tests that install their own tools.

    Paired with `restore`, because `clear` on its own is global vandalism: the
    real tools register at import time, so a test that clears and walks away
    leaves every later test looking at an empty registry.
    """
    return dict(_REGISTRY)


def restore(state: dict[str, Tool]) -> None:
    """Put back what `snapshot` took. For tests only."""
    _REGISTRY.clear()
    _REGISTRY.update(state)


def clear() -> None:
    """Empty the registry. For tests only, and only with `restore` after it."""
    _REGISTRY.clear()
