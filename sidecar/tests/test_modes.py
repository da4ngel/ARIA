"""Modes as operating systems, not tones.

Eyaas's own framing after using the first version: *"Don't make them just
different personalities. Make them genuinely different reasoning policies,
tool strategies, context handling, and output standards."* He was right —
mode reached three call sites, all of them prompt text plus one routing hint.

So what is tested here is the *mechanism*: that a policy exists for every mode,
that each lever is read by something, and that the one which touches safety
can only ever narrow. The prose lives in `test_context.py` with the rest of the
prompt.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from sidecar.core import modes
from sidecar.core.context import ConversationMode
from sidecar.core.modes import POLICIES, ModePolicy, ToolPolicy, policy_for, suggest
from sidecar.core.router import RoutingBias
from sidecar.tools.registry import Tier

# ── the policies themselves ───────────────────────────────────────────


@pytest.mark.parametrize("mode", list(ConversationMode))
def test_every_mode_has_a_policy(mode: ConversationMode) -> None:
    """A mode with no policy would silently behave like Normal, which is the
    worst outcome: it would look like it worked."""
    assert mode in POLICIES
    assert POLICIES[mode].mode is mode


@pytest.mark.parametrize("mode", list(ConversationMode))
def test_every_mode_states_when_it_is_done(mode: ConversationMode) -> None:
    """The lever Eyaas called the secret. It is what makes a mode a standard
    the answer is held to rather than a voice it is written in."""
    assert POLICIES[mode].done_when.strip()


def test_an_unknown_mode_falls_back_to_normal_rather_than_raising() -> None:
    """A stale client sending a mode this build has never heard of is a reason
    to behave like Normal, not a reason to fail the turn."""
    assert policy_for("nonsense") is POLICIES[ConversationMode.NORMAL]  # type: ignore[arg-type]


def test_normal_keeps_todays_behaviour_exactly() -> None:
    """The whole "you pay nothing for a feature you never switch on" property,
    stated as mechanism rather than as prompt bytes.

    Normal's *prompt* did gain a definition of done — deliberately, because
    Eyaas asked for Normal specifically. Its **behaviour** must not move: same
    step budget, same tools, same routing, same retrieval depth.
    """
    normal = POLICIES[ConversationMode.NORMAL]

    assert normal.max_steps == 8
    assert normal.tools is ToolPolicy.ALL
    assert normal.bias is None
    assert normal.retrieval_deadline_s is None


def test_quick_actually_costs_less_rather_than_only_sounding_shorter() -> None:
    """A mode that promises speed and then runs a six-tool chain has broken its
    only promise, whatever the answer looked like."""
    quick = POLICIES[ConversationMode.QUICK]

    assert quick.max_steps < POLICIES[ConversationMode.NORMAL].max_steps
    assert quick.bias is RoutingBias.FASTEST
    assert quick.tools is ToolPolicy.READ_ONLY


@pytest.mark.parametrize(
    "mode", [ConversationMode.STUDY, ConversationMode.RESEARCH, ConversationMode.CRITIC]
)
def test_the_modes_that_build_on_context_get_the_longer_deadline(
    mode: ConversationMode,
) -> None:
    """At the 60ms default most retrievals fall back to word matching, which
    loses paraphrase — an accepted trade on an ordinary turn and a bad one when
    the whole mode is about what came before."""
    assert POLICIES[mode].retrieval_deadline_s is not None


# ── the lever that touches safety ─────────────────────────────────────


def test_a_tool_policy_can_only_narrow() -> None:
    """**The load-bearing property of this whole file.**

    A mode is a one-click header control. If one could raise its own ceiling,
    it would be a route around the tier system — which is exactly the
    `allow_danger_tools` drift CLAUDE.md records, arriving through a second
    door.
    """
    assert ToolPolicy.READ_ONLY.ceiling() == Tier.SAFE
    assert ToolPolicy.NONE.ceiling() is None
    # ALL means "whatever the permission engine already allowed", so it must be
    # at least the highest tier — `_tool_schemas` takes the `min` of the two.
    assert ToolPolicy.ALL.ceiling() == Tier.DANGER

    for policy in POLICIES.values():
        ceiling = policy.tools.ceiling()
        assert ceiling is None or ceiling <= Tier.DANGER


def test_read_only_stops_below_the_tier_where_damage_starts() -> None:
    """Leans on rule 5's own invariant rather than a second hand-written list.

    Every destructive operation is CONFIRM or above, so "tiers that change
    nothing" is a thing the tier system already defines. A parallel list would
    be free to drift from it.
    """
    ceiling = ToolPolicy.READ_ONLY.ceiling()
    assert ceiling is not None and ceiling < Tier.CONFIRM


# ── suggesting, never switching ───────────────────────────────────────


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("compare XGBoost vs random forest for this", ConversationMode.RESEARCH),
        ("is Postgres or SQLite better here", ConversationMode.RESEARCH),
        ("why does my test keep failing", ConversationMode.CODE),
        ("review my PR before I merge it", ConversationMode.CODE),
        ("poke holes in this plan", ConversationMode.CRITIC),
        ("what am I missing here", ConversationMode.CRITIC),
    ],
)
def test_it_recognises_the_shapes_it_claims_to(message: str, expected: ConversationMode) -> None:
    assert suggest(message, ConversationMode.NORMAL) is expected


@pytest.mark.parametrize(
    "message",
    ["teach me how TCP congestion control works", "quiz me on the renal system"],
)
def test_a_teaching_shaped_message_offers_a_study_chat_not_a_mode(message: str) -> None:
    """**Study left `_SUGGESTIONS` when it stopped being a mode.** Suggesting it
    would propose a switch nothing can perform — a normal conversation cannot
    become a study one. The pattern is unchanged; the offer is now to open a
    study chat instead."""
    assert suggest(message, ConversationMode.NORMAL) is not ConversationMode.STUDY
    assert modes.suggests_study_chat(message, ConversationMode.NORMAL) is True


def test_a_study_chat_is_not_offered_another_one() -> None:
    """Inside a study chat the answer is obviously yes, and the offer is noise."""
    assert modes.suggests_study_chat("teach me this", ConversationMode.STUDY) is False


def test_an_ordinary_message_offers_nothing() -> None:
    assert (
        modes.suggests_study_chat("what is the capital of Australia", ConversationMode.NORMAL)
        is False
    )


@pytest.mark.parametrize(
    "message",
    [
        "hi",
        "what is the capital of Australia",
        "open notepad",
        "turn the volume up",
        "what time is it",
        "how does a diesel engine work",
        "write me a haiku about rain",
        "thanks, that worked",
    ],
)
def test_silence_is_the_common_answer(message: str) -> None:
    """**The property that decides whether this is usable.**

    §9's own warning is that over-triggering is the fastest route to a feature
    being switched off, and a banner on every third message is exactly that.
    "How does X work" is deliberately not a Study trigger: it is the single
    most common shape of an ordinary question.
    """
    assert suggest(message, ConversationMode.NORMAL) is None


def test_it_never_suggests_the_mode_already_in_use() -> None:
    """Otherwise Study mode would spend its life offering Study mode."""
    assert suggest("teach me about nephrons", ConversationMode.STUDY) is None
    assert suggest("compare these two papers", ConversationMode.RESEARCH) is None


def test_critique_beats_code_when_a_message_is_both() -> None:
    """ "What's wrong with my code" is a request to be argued with. Code mode
    would answer it by silently fixing the thing, which is a different and
    less useful reply."""
    assert suggest("what's wrong with my code here", ConversationMode.NORMAL) is (
        ConversationMode.CRITIC
    )


def test_quick_is_never_suggested() -> None:
    """Brevity is a preference to set, not something to infer from a short
    question — and inferring it wrongly means answering a real question with a
    line."""
    for message in ("2+2", "capital of France", "yes", "when did WW2 end"):
        assert suggest(message, ConversationMode.NORMAL) is not ConversationMode.QUICK


def test_a_policy_is_frozen() -> None:
    """Process-global and shared by every turn — one mutated in place would be
    a mode change nobody asked for, on every conversation at once."""
    with pytest.raises(FrozenInstanceError):
        POLICIES[ConversationMode.QUICK].max_steps = 99  # type: ignore[misc]


def test_the_policy_object_is_the_single_lookup() -> None:
    """Levers and prose live in different modules on purpose — but a caller
    should not have to know that."""
    policy: ModePolicy = policy_for(ConversationMode.CRITIC)
    assert policy.label == "Critic"
    assert "weakest point" in policy.done_when


# ── the narrowing, where it is actually enforced ──────────────────────


def _schemas(policy: ModePolicy | None, *, allow_danger: bool = False) -> set[str]:
    """`_tool_schemas` on a bare service, the shape `test_permissions.py` uses."""
    from sidecar.core.conversation import ConversationService
    from sidecar.tools.permissions import PermissionMode

    service = ConversationService.__new__(ConversationService)

    class _Engine:
        mode = PermissionMode.AUTO

    _Engine.allow_danger = allow_danger  # type: ignore[attr-defined]
    service._permissions = _Engine()  # type: ignore[assignment]  # noqa: SLF001
    return {s["function"]["name"] for s in service._tool_schemas(policy) or []}  # noqa: SLF001


def test_a_read_only_mode_is_not_told_about_the_tools_that_change_things() -> None:
    """Not a refusal — the model is never told they exist, which §7.2 calls the
    stronger form: a capability it cannot see is one it cannot be talked into."""
    everything = _schemas(POLICIES[ConversationMode.NORMAL])
    read_only = _schemas(POLICIES[ConversationMode.QUICK])

    assert read_only < everything, "READ_ONLY offered the same set as ALL"
    assert "delete_file" not in read_only
    assert "write_file" not in read_only
    # And it is still useful: the things that only look land in it.
    assert "get_system_info" in read_only
    assert "read_file" in read_only


def test_a_mode_cannot_raise_its_own_ceiling() -> None:
    """**The mutation this file exists for.**

    `_tool_schemas` takes `min(engine ceiling, mode ceiling)`. Replace that
    `min` with the mode's own value and `ToolPolicy.ALL` starts handing DANGER
    tools to a model whose permission engine never allowed them — a one-click
    header control reaching the tier system, which is the `allow_danger_tools`
    drift arriving through a second door.
    """
    with_mode = _schemas(POLICIES[ConversationMode.NORMAL], allow_danger=False)
    without = _schemas(None, allow_danger=False)

    assert "delete_file" not in with_mode, "a mode raised the ceiling above the engine's"
    assert with_mode == without, "ToolPolicy.ALL changed what an unmoded turn would see"


def test_the_engine_still_wins_when_it_is_the_stricter_of_the_two() -> None:
    """Both directions, so `min` is not passing by luck: with DANGER allowed,
    a read-only mode still sees only read-only tools."""
    assert "delete_file" not in _schemas(POLICIES[ConversationMode.QUICK], allow_danger=True)
    assert "delete_file" in _schemas(POLICIES[ConversationMode.NORMAL], allow_danger=True)
