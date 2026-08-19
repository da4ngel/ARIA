"""The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6).

Multi-step tool chaining lives here in the same relationship `core/router.py`
already has with `core/conversation.py`: this module holds the decisions that
need no bus, no store, and no live model connection to make, and
`ConversationService._run_turn` calls into it from the loop that does the
actual work. **The loop itself stays a method on `ConversationService`, not a
class here.** It needs `_stream_one`, `self._permissions`, `self._router`,
`self._registry` and half of what the class already owns — duplicating that
surface behind a second stateful object would be indirection for its own
sake, not a real seam. `core/router.py` already sets the precedent: a pure
module beside the service, not a replacement for it.

Before this existed, a tool call got exactly one continuation pass with
`offer_tools=False`, hard-coded — §9 Phase 3's own words, "One tool per turn
until Phase 6". Everything below is what turns that into a bounded loop
without turning it into an unbounded one.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from sidecar.tools.registry import UNTRUSTED_SOURCE_TOOLS

#: §9's number, verbatim. A task that has not finished in 8 tool calls is more
#: likely stuck than nearly done, and a hard stop with an honest message beats
#: both a silent truncation and a loop nobody bounded.
MAX_STEPS = 8

def call_key(name: str, arguments: dict[str, Any]) -> tuple[str, str]:
    """A hashable fingerprint of one tool call, for loop detection.

    Sorted so argument order never matters — `{"a": 1, "b": 2}` and
    `{"b": 2, "a": 1}` are the same call and must be seen as one.

    **Serialised rather than tupled, because the tuple was not hashable.**
    `tuple(sorted(arguments.items()))` crashed with `TypeError: unhashable
    type: 'list'` the moment any argument was a list — and the key goes
    straight into a `set`, so the old docstring's claim that "a dict or list
    argument compares by its own `==`" described behaviour the code could not
    reach. It took a turn down with it, from the loop-detection check that runs
    before every single tool call.

    Latent until `ask_user` arrived with a `list[Question]`, but never specific
    to it: a model passing a list to *any* tool — including by mistake — hit
    the same crash. JSON with sorted keys is hashable, order-independent, and
    still compares structurally, which is what "the same call twice" means.
    """
    return (name, json.dumps(arguments, sort_keys=True, default=str))


@dataclass
class LoopState:
    """What one turn's agent loop is tracking, across its steps.

    Deliberately not `ConversationService` state — one of these exists for the
    lifetime of a single turn and is discarded when it ends, the same as
    `collected: list[str]` already is in `_run_turn`. A fresh one is built for
    each provider-failover attempt in the outer `chain` loop: a model that
    failed mid-chain is not replayed a broken tool history on the next
    provider, it starts clean, exactly as a single-tool failure already does
    today.
    """

    step: int = 0
    seen: set[tuple[str, str]] = field(default_factory=set)
    #: The most recently *run* tool's name, for §11's escalation below.
    last_tool: str | None = None
    #: Whether that tool actually succeeded. §11 escalates the step after
    #: *reading* untrusted content — a `research` call that was denied at the
    #: dialog, or that errored, read nothing at all, so there is no untrusted
    #: content in the context for the next step to be protected from.
    #: Observed live: one `research` timing out at its confirmation made the
    #: next `research` escalate too, which timed out in turn, and the whole
    #: turn spent four minutes asking about reads that never occurred.
    last_ok: bool = True
    #: **Sticky, not per-step.** The single-tool design only ever had to ask
    #: "is *this* tool local-only" because there was no next step. Once a
    #: local-only result (e.g. `read_clipboard`) is sitting in this turn's
    #: message history, every later step that can see that history must also
    #: stay local — not just the one continuation immediately after it. A
    #: flag that reset each step would leak the clipboard to the cloud the
    #: moment a second, unrelated tool ran after it.
    sticky_local: bool = False
    #: The last tool result's own one-line summary, kept for `silent_reply_note`
    #: below. Only ever the summary — never `data` or `display` — so nothing
    #: here can widen what §7.2 allows back into the user's sight.
    last_summary: str | None = None

    #: What the *next* call is, once the loop knows. `should_escalate` is a
    #: property with no arguments — it reads this, set immediately before the
    #: permission engine is asked to run that call.
    pending_tool: str | None = None

    def would_repeat(self, name: str, arguments: dict[str, Any]) -> bool:
        return call_key(name, arguments) in self.seen

    def record(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        local_only: bool = False,
        summary: str | None = None,
        ok: bool = True,
    ) -> None:
        """Mark one step as run. `local_only` is unknown, not False, for a
        tool the registry has never heard of — but a hallucinated tool name
        cannot have leaked anything real, so treating that case as "no new
        privacy constraint" is correct, not a shortcut.
        """
        self.seen.add(call_key(name, arguments))
        self.last_tool = name
        self.sticky_local = self.sticky_local or local_only
        self.last_summary = summary
        self.last_ok = ok
        self.step += 1

    #: This turn's ceiling, from the conversation's `ModePolicy`. Defaults to
    #: `MAX_STEPS` so every existing caller and test is unchanged — Quick mode
    #: lowers it to 2, because a turn that quietly ran six tools has broken
    #: that mode's only promise whatever the answer was.
    max_steps: int = MAX_STEPS

    @property
    def exhausted(self) -> bool:
        return self.step >= self.max_steps

    @property
    def offer_tools(self) -> bool:
        """Whether the model should be handed tools on the next pass.

        False exactly on what would be the ninth call: the model still
        answers in text with whatever it has, but is not offered a step this
        loop has no budget left to run.
        """
        return not self.exhausted

    @property
    def should_escalate(self) -> bool:
        """§11: the call immediately after reading untrusted content is
        forced through confirmation, regardless of its own registered tier.

        `research.py`'s own docstring names this exact spot: *"Phase 6's agent
        loop is exactly where that stops being true, and must land with the
        escalation."* One tool ran per turn before this, so there was never a
        "next call" for the rule to apply to.

        **`last_ok` is part of the condition, and narrows nothing that
        matters.** §11's trigger is *reading* untrusted content; a read that
        was refused, denied at its dialog, or errored put nothing into the
        context, so the step after it has nothing to be protected from.
        Without this the rule fed itself: a `research` whose confirmation
        timed out (120s, resolving to DENIED) made the *next* `research`
        escalate as well, which also timed out, and the turn spent four
        minutes asking about pages nobody ever fetched.

        **One more read is not the action §11 guards against.** Decided with
        Eyaas (2026-08-18), on the same reasoning that moved
        `browser_click`/`browser_fill` off blanket CONFIRM: judge the action,
        not the tool. §11 exists so a page saying *"delete all files in
        Downloads"* cannot reach a tool that deletes; a second `research` or
        `browser_read` reaches nothing on this machine, changes nothing, and
        is already gated by the online-mode switch — the consent
        `research.py` itself calls "the consent that matters". Measured
        before this: one *"what is the latest Python"* turn raised **three**
        confirmation dialogs for a read-only T1 tool. Every other tool after
        an untrusted read still escalates, unchanged.

        The residual risk is stated rather than smoothed over: an injected
        page can steer the *next search query*, which is a narrow
        exfiltration channel. It is narrower than the friction of a dialog
        per search, which is the thing that gets a confirmation reflexively
        approved — and an approval nobody reads protects nothing.
        """
        if self.last_tool not in UNTRUSTED_SOURCE_TOOLS or not self.last_ok:
            return False
        return self.pending_tool not in UNTRUSTED_SOURCE_TOOLS


def repeat_note(name: str) -> str:
    """Told to the model, not just logged — it should know why it stopped."""
    return (
        f"That would repeat the exact {name} call already made this turn with "
        f"the same arguments, which usually means stuck rather than making "
        f"progress — so it was not run again."
    )


def exhausted_note(max_steps: int = MAX_STEPS) -> str:
    """The budget is per-turn now, so the number has to be passed in.

    It reads as a plain sentence to the model, and Quick mode's "more than 2
    steps" is a very different claim from Normal's "more than 8" — a note that
    named the wrong ceiling would be telling it something untrue about its own
    limits.
    """
    return (
        f"That took more than {max_steps} steps in one turn, which is the "
        f"most allowed at once, so it stopped there rather than continue "
        f"indefinitely. Ask again to pick up where it left off."
    )


#: How much of a tool's own summary goes into the fallback below. Long enough
#: to carry a file list or an error, short enough that a runaway summary
#: cannot become the whole reply.
SILENT_REPLY_MAX_CHARS = 400


def silent_reply_note(tool_name: str | None, summary: str | None) -> str:
    """What the user sees when the model produced no words at all.

    A real, observed failure, not a defensive nicety: `gate_agent.py`'s
    find -> read -> answer line records that *"some runs end in an empty
    reply rather than an explanation"* — the model burns its steps, the last
    pass returns zero text deltas, and `_finish` stores and broadcasts an
    empty `full_text`. From the outside that is indistinguishable from a
    hung app, and it is the one outcome a turn must never have.

    So the tool's own result stands in for the sentence the model did not
    write. It is deliberately framed as a report of what ran rather than
    dressed up as her own words — she did not say this, and text invented on
    her behalf is the exact thing every anti-invention clause in
    `core/context.py` exists to stop.
    """
    if not tool_name:
        # No tool ran either, so there is nothing to report but the silence.
        # Rarer, and usually a provider returning an empty completion (GPT-5
        # spending its whole `max_tokens` on reasoning is the recorded case).
        return (
            "That came back empty — the model returned no text at all. "
            "Ask again, or try a different model from the picker."
        )
    said = (summary or "").strip()
    if len(said) > SILENT_REPLY_MAX_CHARS:
        said = said[: SILENT_REPLY_MAX_CHARS - 1].rstrip() + "…"
    detail = f" {said}" if said else ""
    return (
        f"I ran {tool_name} but did not get an answer written for you."
        f"{detail} Ask again if that is not what you needed."
    )
