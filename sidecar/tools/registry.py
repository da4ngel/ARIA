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
from collections.abc import Awaitable, Callable
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


ToolFn = Callable[..., Awaitable[ToolResult]]


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
    return {"type": _JSON_TYPES.get(annotation, "string")}


def _arg_docs(doc: str) -> dict[str, str]:
    """Per-argument descriptions out of a Google-style Args: block.

    These are what the model actually reads to decide what to put in a field,
    so they are worth more than the function description on its own.
    """
    lines = doc.splitlines()
    descriptions: dict[str, str] = {}
    inside = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("args:"):
            inside = True
            continue
        if inside:
            if not stripped or stripped.endswith(":") and " " not in stripped:
                break
            match = _ARG_DOC.match(line)
            if match:
                descriptions[match.group(1)] = match.group(2).strip()
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
    *, name: str, tier: Tier, description: str, local_only: bool = False
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
        )
        return fn

    return decorator


def get(name: str) -> Tool | None:
    return _REGISTRY.get(name)


def names() -> list[str]:
    return sorted(_REGISTRY)


def all_tools() -> list[Tool]:
    return [_REGISTRY[n] for n in sorted(_REGISTRY)]


def schemas(*, tier_max: Tier = Tier.CONFIRM) -> list[dict[str, Any]]:
    """Tool schemas for the model, up to and including `tier_max`.

    **DANGER is excluded by default**, which is what §7.2 means by "off by
    default": the model is not told those tools exist unless something
    deliberately raises the ceiling. A capability the model cannot see is one
    it cannot be talked into using.
    """
    return [t.schema for t in all_tools() if t.tier <= tier_max]


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
