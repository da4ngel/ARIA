"""What a mode actually *does*, as opposed to what it says.

Eyaas, after using the first version: *"Don't make them just different
personalities. Make them genuinely different reasoning policies, tool
strategies, context handling, and output standards. The modes should feel like
the same AI with different operating systems underneath."*

He was right, and the gap was more literal than it sounds. Mode reached exactly
three call sites — `stable_prefix`, `fit_to_budget`, and one `bias` argument to
`Router.choose`. Prompt text and a routing hint. Everything else a mode ought to
change had no hook to hang on at all.

`ModePolicy` is that hook. One frozen record per mode carrying every lever, and
**every field here is read by something**: `max_steps` by the agent loop,
`bias` by the router, `tools` by `_tool_schemas`, `retrieval_deadline_s` by the
retriever, `done_when` by the prompt. A field nothing consumes is not a policy,
it is the `affect_state`/`procedures`/`record_new_offers` pattern this codebase
keeps rediscovering — a table nobody writes to, shipped and invisible.

**What a mode still cannot do is change what is permitted.** No tier moves, no
confirmation is skipped, `Tool.refuse` and the `_PRIVATE` routing stage are
untouched. `tools` below narrows what the model is *told about*; it can never
widen it, and `_tool_schemas` still applies the DANGER ceiling on top. The tier
system is the safety boundary and a one-click header control must not be able
to reach it — CLAUDE.md's own recorded lesson about `allow_danger_tools`
drifting from the gate it gated is what happens otherwise.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from sidecar.core.context import ConversationMode, mode_done_when
from sidecar.core.router import RoutingBias
from sidecar.tools.registry import Tier


class ToolPolicy(StrEnum):
    """How much of the registry a mode lets the model see.

    **Narrowing, never widening**, and it is a different mechanism from the
    relevance-based selection this project measured and closed. That one
    guessed which tools suited *this message* and made choice much worse —
    21/24 down to 9/24 — because a correct tool that is not offered cannot be
    chosen, and filtering converts right answers into wrong ones.

    Two things make a per-mode set a different proposition. It is *declared*
    rather than inferred, so it cannot be wrong about a particular sentence in
    the way a similarity score can. And it is stable for the whole
    conversation, so the tool schemas stay byte-identical inside the KV-cached
    stable prefix — where a per-message set would spend prefill every time the
    topic moved, which was the third argument against the closed design.

    It is still a real cost and it still wants measuring: `READ_ONLY` in Quick
    mode means a turn that genuinely needed to write a file cannot. Run
    `gate_tool_selection.py` before trusting any of these.
    """

    #: Everything the permission engine would allow. Today's behaviour.
    ALL = "all"
    #: Tiers that change nothing — `AUTO` and `SAFE`. Rule 5 puts every
    #: destructive operation at `CONFIRM` or above, so this leans on an
    #: invariant that already exists rather than a second hand-written list
    #: that could drift from it.
    READ_ONLY = "read_only"
    #: No tools offered at all. Not used by any mode today, and kept because
    #: "answer from what you know" is a coherent policy someone will want.
    NONE = "none"

    def ceiling(self) -> Tier | None:
        """The highest tier this policy will show, or None for no tools."""
        if self is ToolPolicy.NONE:
            return None
        return Tier.SAFE if self is ToolPolicy.READ_ONLY else Tier.DANGER


@dataclass(frozen=True)
class ModePolicy:
    """One mode's operating system.

    Frozen and pure: a test builds one and asserts on it with no bus, no
    database and nothing running — the same shape `agent.LoopState` already
    has, and for the same reason.
    """

    mode: ConversationMode
    label: str

    #: Ceiling on agent-loop steps. Quick's whole promise is latency, and a
    #: turn that quietly ran six tools has broken it whatever the answer was.
    max_steps: int

    #: What Smart mode optimises for. `None` leaves the user's own setting
    #: alone, which is right for most modes — a mode is a style, and only some
    #: of them genuinely imply a different class of model.
    bias: RoutingBias | None

    tools: ToolPolicy

    #: Retrieval's hard deadline. `None` takes the default. Study and Research
    #: earn a longer one for the same reason a recall question already does:
    #: when the retrieval *is* the answer, a lexical fallback that loses
    #: paraphrase costs more than the milliseconds do.
    retrieval_deadline_s: float | None

    @property
    def done_when(self) -> str:
        """This mode's standard for a finished answer.

        Eyaas's own framing, and the most load-bearing idea here: it is what
        stops a mode being a tone and makes it a standard the answer is held
        to. The **string** lives in `context._MODE_TEXT` beside the rest of the
        prompt — one source for prose, one for levers — and this delegates so
        that `ModePolicy` is still the single place to ask what a mode does.
        """
        return mode_done_when(self.mode)


#: Longer than the 60ms default, and the same figure `_RECALL_QUESTION` already
#: uses. Measured: during generation the embed p90 is 107ms on this machine, so
#: 60ms means most retrievals fall back to word matching. That is an accepted
#: trade on an ordinary turn and a bad one when the whole mode is about
#: building on what came before.
_DEEP_RETRIEVAL_S = 0.4


POLICIES: dict[ConversationMode, ModePolicy] = {
    ConversationMode.NORMAL: ModePolicy(
        mode=ConversationMode.NORMAL,
        label="Normal",
        # Today's `agent.MAX_STEPS`, unchanged. Normal must stay byte-identical
        # in behaviour as well as in prompt: anyone who never opens the control
        # pays nothing for the feature existing.
        max_steps=8,
        bias=None,
        tools=ToolPolicy.ALL,
        retrieval_deadline_s=None,
    ),
    ConversationMode.QUICK: ModePolicy(
        mode=ConversationMode.QUICK,
        label="Quick",
        # Two, not one: a turn that needs a tool still gets the tool and one
        # step to use the result. What it does not get is a chain.
        max_steps=2,
        bias=RoutingBias.FASTEST,
        tools=ToolPolicy.READ_ONLY,
        retrieval_deadline_s=None,
    ),
    ConversationMode.STUDY: ModePolicy(
        mode=ConversationMode.STUDY,
        label="Study",
        max_steps=4,
        bias=None,
        tools=ToolPolicy.READ_ONLY,
        retrieval_deadline_s=_DEEP_RETRIEVAL_S,
    ),
    ConversationMode.RESEARCH: ModePolicy(
        mode=ConversationMode.RESEARCH,
        label="Research",
        max_steps=8,
        bias=RoutingBias.QUALITY,
        tools=ToolPolicy.ALL,
        retrieval_deadline_s=_DEEP_RETRIEVAL_S,
    ),
    ConversationMode.CODE: ModePolicy(
        mode=ConversationMode.CODE,
        label="Code",
        max_steps=8,
        bias=RoutingBias.QUALITY,
        tools=ToolPolicy.ALL,
        retrieval_deadline_s=None,
    ),
    ConversationMode.CRITIC: ModePolicy(
        mode=ConversationMode.CRITIC,
        label="Critic",
        max_steps=4,
        bias=RoutingBias.QUALITY,
        # Read-only on purpose. This mode's job is to attack an idea, and an
        # attack that also moves files is a strange thing to have built.
        tools=ToolPolicy.READ_ONLY,
        retrieval_deadline_s=_DEEP_RETRIEVAL_S,
    ),
}


def policy_for(mode: ConversationMode) -> ModePolicy:
    """The policy, or Normal's. Never raises.

    A mode arriving from a stale client is a reason to behave like Normal, not
    a reason to fail a turn.
    """
    return POLICIES.get(mode, POLICIES[ConversationMode.NORMAL])


# ── suggesting a mode ─────────────────────────────────────────────────
#
# **It suggests; it never switches.** Modes are per-conversation and reset to
# Normal precisely so that "a mode set last week cannot silently shape today's
# answers" — and a mode ARIA chose for itself mid-conversation is that same
# invisible shaping, arriving faster. Confirmed with Eyaas before building it.
#
# Patterns rather than a model call, which is this project's settled position
# on small classifications: the salience score was taken off the model after it
# returned 0.0 for fifteen of eighteen episodes, and a plain yes/no reply is
# matched by a table for the same reason. A classifier that costs a second and
# can fail is worse than one that is occasionally quiet.
#
# **Silence is the default and the common case.** §9's own warning is that
# over-triggering is the fastest route to something being turned off, and a
# banner on every third message is exactly that.

#: Asking to be taught, rather than told. "How does X work" deliberately does
#: *not* match on its own — it is the single most common shape of an ordinary
#: question, and suggesting Study for it would fire constantly.
_WANTS_TEACHING = re.compile(
    r"\b(teach me|help me understand|i don'?t understand|explain it like|"
    r"walk me through|i'?m (studying|revising|learning)|for my exam|"
    r"quiz me|test me on|make me (some )?questions)\b",
    re.IGNORECASE,
)

#: A question that wants evidence rather than an opinion. The comparison forms
#: carry most of it — "X vs Y", "which is better", "is X worth it".
_WANTS_EVIDENCE = re.compile(
    r"\b(compare|comparison|versus|vs\.?|which is better|what'?s better|"
    r"is .{2,30} (better|worth it|any good)|evidence|studies|research on|"
    r"papers? on|state of the art|benchmark(s|ed)?|pros and cons)\b",
    re.IGNORECASE,
)

#: Wanting the idea attacked. Deliberately narrow: these are phrasings nobody
#: uses by accident, because a wrongly-suggested Critic mode reads as ARIA
#: being keen to argue.
_WANTS_CRITIQUE = re.compile(
    r"\b(poke holes|tear (it|this) apart|what'?s wrong with (my|this)|"
    r"critique|criticis[ez]|red team|devil'?s advocate|why (would|might) "
    r"(this|it) fail|talk me out of|is this a (good|bad) idea|"
    r"what am i missing)\b",
    re.IGNORECASE,
)

#: Working on existing code, as opposed to asking about a language. Reuses the
#: router's own two patterns rather than restating them — they are already
#: tested against every probe in `gate_tool_selection.py`, and a second
#: definition of "this is about code" is one that will drift.
_DEBUGGING = re.compile(
    r"\b(this (error|traceback|stack trace|exception)|why (is|does) (my|this) "
    r"(code|script|function|app|test)|my (code|script|build|test)s? "
    r"(is|are|keeps?|won'?t|doesn'?t)|fix (my|this) (code|bug|test)|"
    r"refactor (my|this)|review (my|this) (code|pr|patch|diff))\b",
    re.IGNORECASE,
)

_SUGGESTIONS: tuple[tuple[re.Pattern[str], ConversationMode], ...] = (
    # Order matters where a message could match two. Critique is checked first
    # because "what's wrong with my code" is a request to be argued with, and
    # Code mode would answer it by silently fixing the thing.
    (_WANTS_CRITIQUE, ConversationMode.CRITIC),
    (_DEBUGGING, ConversationMode.CODE),
    (_WANTS_TEACHING, ConversationMode.STUDY),
    (_WANTS_EVIDENCE, ConversationMode.RESEARCH),
)


def suggest(message: str, current: ConversationMode) -> ConversationMode | None:
    """A mode this turn would be better served by, or None.

    None is the answer for the overwhelming majority of messages, and that is
    the design rather than a shortfall. Never suggests the mode already in use,
    and never suggests Quick — brevity is a preference to set, not something to
    infer from a short question.
    """
    for pattern, mode in _SUGGESTIONS:
        if mode is not current and pattern.search(message):
            return mode
    return None


__all__ = ["POLICIES", "ModePolicy", "ToolPolicy", "policy_for", "suggest"]
