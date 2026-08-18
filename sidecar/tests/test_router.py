"""Routing decisions, asserted over a labelled message set. No network.

The router is pure by design — it returns a decision and never performs a call —
so every case here is a plain function call against a synthetic catalog state.
"""

from __future__ import annotations

import pytest

from sidecar.core.context import PersonaLevel
from sidecar.core.router import (
    RouteDecision,
    Router,
    RoutingBias,
    is_trivial,
    needs_deep_model,
)
from sidecar.providers import catalog
from sidecar.providers.catalog import ModelClass, ModelInfo
from sidecar.providers.health import HealthTracker

ALL_MODELS = {m.id for m in catalog.CATALOG}
LOCAL_IDS = {m.id for m in catalog.local_models()}


@pytest.fixture
def health() -> HealthTracker:
    return HealthTracker()


def router(health: HealthTracker, bias: RoutingBias) -> Router:
    return Router(health, bias)


def is_local(decision: RouteDecision) -> bool:
    return decision.model.local


# ── the labelled set ──────────────────────────────────────────────────
# (message, must-be-local under QUALITY). Cloud is the default at this bias, so
# only genuinely trivial turns stay on the machine.

QUALITY_CASES: list[tuple[str, bool]] = [
    ("hi", True),
    ("hey", True),
    ("hello!", True),
    ("thanks", True),
    ("thank you", True),
    ("ok", True),
    ("cool", True),
    ("got it", True),
    ("never mind", True),
    ("goodnight", True),
    ("lol", True),
    ("what is the capital of France", False),
    ("explain how a diesel engine works", False),
    ("write me a haiku about rain", False),
    ("compare Postgres and SQLite for this project", False),
    ("debug this traceback: ValueError in handlers.py", False),
    ("refactor this function and then add a test", False),
    ("think hard about the tradeoffs here", False),
]

# Privacy overrides everything except an explicit pick, at every bias.
PRIVATE_CASES = [
    "summarise my file for me",
    "what is on my screen",
    "read this file and explain it",
    "check my email",
    "what am I looking at",
    "paste from my clipboard and analyse it",
]


@pytest.mark.parametrize(("message", "expect_local"), QUALITY_CASES)
def test_quality_bias_routes_as_labelled(
    health: HealthTracker, message: str, expect_local: bool
) -> None:
    decision = router(health, RoutingBias.QUALITY).choose(message, available=ALL_MODELS)
    assert is_local(decision) is expect_local, f"{message!r} -> {decision.model.id}"


@pytest.mark.parametrize("message", PRIVATE_CASES)
@pytest.mark.parametrize("bias", list(RoutingBias))
def test_private_content_never_leaves_the_machine(
    health: HealthTracker, message: str, bias: RoutingBias
) -> None:
    decision = router(health, bias).choose(message, available=ALL_MODELS)
    assert is_local(decision), f"{message!r} leaked to {decision.model.id}"
    assert decision.reason.stage == "local"
    # And no cloud model may sit in the fallback chain either.
    assert all(m.local for m in decision.fallbacks)


def test_explicit_selection_wins_over_privacy(health: HealthTracker) -> None:
    """Picking a cloud model IS the consent (§9.7 stage 1)."""
    decision = router(health, RoutingBias.QUALITY).choose(
        "summarise my file", selected="gpt-5", available=ALL_MODELS
    )
    assert decision.model.id == "gpt-5"
    assert decision.reason.stage == "explicit"


def test_explicit_selection_of_unavailable_model_falls_back_locally(
    health: HealthTracker,
) -> None:
    decision = router(health, RoutingBias.QUALITY).choose(
        "anything", selected="gpt-5", available=LOCAL_IDS
    )
    assert is_local(decision)
    assert "GPT-5" in decision.reason.detail
    assert "unavailable" in decision.reason.detail


def test_unknown_explicit_model_does_not_crash(health: HealthTracker) -> None:
    decision = router(health, RoutingBias.QUALITY).choose(
        "anything", selected="gpt-9-turbo", available=ALL_MODELS
    )
    assert is_local(decision)


def test_no_cloud_available_stays_local(health: HealthTracker) -> None:
    decision = router(health, RoutingBias.QUALITY).choose(
        "compare Postgres and SQLite", available=LOCAL_IDS
    )
    assert is_local(decision)
    assert "No cloud provider" in decision.reason.detail


# ── bias behaviour ────────────────────────────────────────────────────


def test_bias_changes_where_an_ordinary_question_goes(health: HealthTracker) -> None:
    """The whole point of the setting: same message, different destination."""
    message = "what is the capital of France"
    assert router(health, RoutingBias.FASTEST).choose(message, available=ALL_MODELS).model.local
    assert router(health, RoutingBias.BALANCED).choose(message, available=ALL_MODELS).model.local
    assert not router(health, RoutingBias.QUALITY).choose(message, available=ALL_MODELS).model.local


def test_deep_work_goes_to_cloud_at_every_bias(health: HealthTracker) -> None:
    message = "debug this traceback and then refactor the handler"
    for bias in RoutingBias:
        decision = router(health, bias).choose(message, available=ALL_MODELS)
        assert not decision.model.local, bias
        assert decision.model.klass is catalog.ModelClass.SMART, bias


def test_agent_loop_depth_forces_a_smart_model(health: HealthTracker) -> None:
    for bias in RoutingBias:
        decision = router(health, bias).choose("continue", available=ALL_MODELS, step=3)
        assert decision.model.klass is catalog.ModelClass.SMART, bias


def test_set_bias_takes_effect(health: HealthTracker) -> None:
    r = router(health, RoutingBias.QUALITY)
    assert not r.choose("name a colour", available=ALL_MODELS).model.local
    r.set_bias(RoutingBias.FASTEST)
    assert r.choose("name a colour", available=ALL_MODELS).model.local


# ── fallback chains ───────────────────────────────────────────────────


def test_cloud_decision_ends_its_chain_locally(health: HealthTracker) -> None:
    """§9.7 stage 7: siblings first, then local as the last resort."""
    decision = router(health, RoutingBias.QUALITY).choose(
        "compare these two designs", available=ALL_MODELS
    )
    assert not decision.model.local
    assert decision.fallbacks, "a cloud pick must carry a fallback chain"
    assert decision.fallbacks[-1].local, "the chain must end on this machine"


def test_chain_contains_no_duplicates(health: HealthTracker) -> None:
    decision = router(health, RoutingBias.QUALITY).choose(
        "debug this stack trace", available=ALL_MODELS
    )
    chain = [decision.model.id, *(m.id for m in decision.fallbacks)]
    assert len(chain) == len(set(chain)), chain


def test_ranking_prefers_the_faster_observed_model(health: HealthTracker) -> None:
    """Observed latency overrides the seeded table as turns land."""
    health.record_success("gpt-4.1-mini", 200.0)  # seed says 1726ms
    decision = router(health, RoutingBias.QUALITY).choose(
        "give me a summary of this topic", available=ALL_MODELS
    )
    assert decision.model.id == "gpt-4.1-mini"


def test_tripped_models_drop_out_of_the_pool(health: HealthTracker) -> None:
    for _ in range(3):
        health.record_failure("gemini-flash-lite-latest", "boom")
    decision = router(health, RoutingBias.QUALITY).choose(
        "give me a summary of this topic", available=ALL_MODELS
    )
    assert decision.model.id != "gemini-flash-lite-latest"


def test_everything_tripped_still_returns_a_model(health: HealthTracker) -> None:
    """The router must always answer. A turn with no candidates is a crash."""
    for model_id in ALL_MODELS:
        health.record_failure(model_id, "boom", rate_limited=True)
    decision = router(health, RoutingBias.QUALITY).choose("hello there", available=ALL_MODELS)
    assert decision.model is not None
    assert decision.model.local


# ── local preference ──────────────────────────────────────────────────


def test_prefers_the_default_local_model_when_it_is_pulled(health: HealthTracker) -> None:
    decision = router(health, RoutingBias.FASTEST).choose("hi", available=ALL_MODELS)
    assert decision.model.id == catalog.PREFERRED_LOCAL


def test_falls_back_to_another_local_model_when_the_default_is_not_pulled(
    health: HealthTracker,
) -> None:
    """Local models are multi-GB downloads that may not have finished."""
    available = ALL_MODELS - {catalog.PREFERRED_LOCAL}
    decision = router(health, RoutingBias.FASTEST).choose("hi", available=available)
    assert decision.model.local
    assert decision.model.id != catalog.PREFERRED_LOCAL


# ── signal helpers ────────────────────────────────────────────────────


@pytest.mark.parametrize("message", ["hi", "HEY", "thanks!", "ok.", "never mind", "hmm"])
def test_is_trivial_accepts_greetings(message: str) -> None:
    assert is_trivial(message)


@pytest.mark.parametrize(
    "message",
    ["hi, can you compare these two files", "ok so what is a monad", "thanks — now explain why"],
)
def test_is_trivial_rejects_real_questions(message: str) -> None:
    assert not is_trivial(message)


@pytest.mark.parametrize(
    "message",
    ["fix this traceback", "```def f(): pass```", "do this and then that", "think hard about it"],
)
def test_needs_deep_model_detects_real_work(message: str) -> None:
    assert needs_deep_model(message)


# ── spoken turns ──────────────────────────────────────────────────────
# Voice has a ~1000ms end-to-end budget (§10) and the network hop alone eats
# most of it, so speech overrides the bias — but never an explicit choice.


@pytest.mark.parametrize("bias", list(RoutingBias))
def test_a_spoken_turn_stays_local_whatever_the_bias(
    health: HealthTracker, bias: RoutingBias
) -> None:
    decision = router(health, bias).choose(
        "compare Postgres and SQLite for this project",
        available=ALL_MODELS,
        spoken=True,
    )
    assert is_local(decision), decision.reason.detail


def test_the_same_question_typed_is_free_to_go_to_the_cloud(health: HealthTracker) -> None:
    """The contrast is the point: only the modality changed."""
    decision = router(health, RoutingBias.QUALITY).choose(
        "compare Postgres and SQLite for this project", available=ALL_MODELS
    )
    assert not is_local(decision)


def test_a_spoken_turn_says_why_it_stayed_local(health: HealthTracker) -> None:
    decision = router(health, RoutingBias.QUALITY).choose(
        "explain how a diesel engine works", available=ALL_MODELS, spoken=True
    )
    assert "keep up" in decision.reason.detail.lower()


def test_speech_never_overrides_an_explicit_cloud_choice(health: HealthTracker) -> None:
    """Picking a model is deliberate. Silently ignoring it is worse than slow."""
    decision = router(health, RoutingBias.QUALITY).choose(
        "explain how a diesel engine works",
        selected="gpt-5",
        available=ALL_MODELS,
        spoken=True,
    )
    assert decision.model.id == "gpt-5"


# ── quality mode has to spend where it helps ──────────────────────────
# Measured before this: "write me a python script to sort a file" routed to
# gemini-flash-lite, the cheapest and weakest cloud model in the catalog.
# `_CODE_HINTS` wanted a code fence or a literal `def `/`import `, and
# `_quality_first` never consulted `_DEEP_VERBS` at all.

CODE_REQUESTS = [
    "write me a python script to sort a file",
    "can you write a function that dedupes a list",
    "how do i sort a list in python",
    "fix the bug in my react component",
    "debug this traceback",
    "generate a regex for email addresses",
    "make me a bash command to find big files",
]


@pytest.mark.parametrize("message", CODE_REQUESTS)
def test_code_requests_reach_a_reasoning_model(message: str) -> None:
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    decision = router.choose(message, available=ALL_MODELS)
    assert decision.model.klass is ModelClass.SMART, f"{message!r} -> {decision.model.id}"


@pytest.mark.parametrize("message", ["analyse this spreadsheet for me", "compare these two plans"])
def test_quality_mode_consults_deep_verbs(message: str) -> None:
    """The line that was missing. Without it these went to the FAST class."""
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    assert router.choose(message, available=ALL_MODELS).model.klass is ModelClass.SMART


def test_a_short_code_request_is_not_answered_locally_to_save_time() -> None:
    """Even in the latency-first bias. Fast and wrong is not the trade."""
    router = Router(HealthTracker(), RoutingBias.FASTEST)
    decision = router.choose("fix this python script", available=ALL_MODELS)
    assert decision.model.klass is ModelClass.SMART


@pytest.mark.parametrize("message", ["hi", "thanks", "ok"])
def test_greetings_still_never_leave_the_machine(message: str) -> None:
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    assert router.choose(message, available=ALL_MODELS).model.local


def test_ordinary_questions_do_not_get_the_expensive_tier() -> None:
    """The control. Widening the detector must not make everything SMART."""
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    for message in ("what is the capital of Australia", "open calculator", "what time is it"):
        assert router.choose(message, available=ALL_MODELS).model.klass is not ModelClass.SMART


def test_a_spoken_turn_still_stays_local() -> None:
    """§10 budgets ~1000ms end to end; a network hop does not fit in it."""
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    decision = router.choose("write me a python script", available=ALL_MODELS, spoken=True)
    assert decision.model.local


# ── the clipboard must not leave the machine ──────────────────────────


@pytest.mark.parametrize(
    "message",
    [
        "what is on my clipboard",
        "what did i just copy",
        "summarise what i copied",
        "paste what i copied earlier",
    ],
)
def test_clipboard_questions_stay_on_this_machine(message: str) -> None:
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    assert router.choose(message, available=ALL_MODELS).model.local, message


# ── tool-shaped turns (the "increase the volume" failure) ─────────────


def test_every_tool_probe_is_recognised_as_a_command() -> None:
    """The signal is hand-written, so this is what keeps it honest.

    One deliberate exception: "the quotation i sent the banquet hall" carries no
    verb and no machine noun — it is a bare noun phrase, and any pattern broad
    enough to catch it catches ordinary conversation too. It is the same probe
    the embedding selector ranked 21st of 23, for the same reason.
    """
    from sidecar.core.router import is_tool_shaped

    probes = [
        "open calculator",
        "create a file named hello.txt in downloads",
        "what is in my downloads folder",
        "where did i put my cv",
        "read hello.txt in downloads",
        "show me the downloads folder in explorer",
        "how much memory am i using",
        "make a folder called receipts in documents",
        "turn the volume down to 20",
        "increase the volume",
        "rename scan001.pdf to invoice.pdf",
        "move budget.xlsx to documents",
        "which windows are open",
        "which files mention the banquet hall",
        "open my cv",
        "switch to chrome",
        "close spotify",
        "what is using all my memory",
        "force quit notepad",
        "turn wifi off",
        "what is on my clipboard",
        "copy that to my clipboard",
    ]
    missed = [p for p in probes if not is_tool_shaped(p)]
    assert missed == [], f"these commands would be answered by the weakest model: {missed}"


@pytest.mark.parametrize(
    "message",
    [
        "write me a python script",
        "what is the capital of Australia",
        "tell me a joke",
        "why is the sky blue",
        "explain how transformers work",
        "I am open to that idea",
        "that was a close call",
        "I close my eyes and think",
        "can you help me plan my week",
    ],
)
def test_conversation_is_not_mistaken_for_a_command(message: str) -> None:
    """A false positive costs a spoken turn its ~800ms head start, which is the
    thing stage 0 exists to protect."""
    from sidecar.core.router import is_tool_shaped

    assert not is_tool_shaped(message)


def test_a_spoken_command_is_no_longer_forced_onto_the_local_model() -> None:
    """The reported failure. "increase the volume" said aloud could only ever
    reach qwen2.5:7b, whatever model was chosen — stage 0 caught every spoken
    turn, not just conversational ones. GPT and Gemini did it perfectly when
    typed, which is what made it look like a routing problem."""
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    decision = router.choose("increase the volume", available=ALL_MODELS, spoken=True)

    assert not decision.model.local


def test_a_spoken_conversational_turn_still_stays_local() -> None:
    """Nobody is waiting on the prosody of "Volume 40% to 55%", but they are
    waiting on the first syllable of an answer. §10 budgets ~1000ms."""
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    decision = router.choose("why is the sky blue", available=ALL_MODELS, spoken=True)

    assert decision.model.local


def test_a_measured_tool_score_outranks_latency_on_a_command() -> None:
    """300ms of extra latency is a pause. A model that picks the wrong tool
    produces nothing at all while reporting that it did."""
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    quick = _cloud_model("quick", ModelClass.FAST, ttft=200, tool_score=0.4)
    capable = _cloud_model("capable", ModelClass.FAST, ttft=900, tool_score=0.95)

    ranked: list[ModelInfo] = router.rank([quick, capable], tool_shaped=True)
    assert ranked[0].id == "capable"

    conversational = router.rank([quick, capable], tool_shaped=False)
    assert conversational[0].id == "quick"


def test_an_unmeasured_model_is_neither_promoted_nor_punished() -> None:
    """Nothing invents a measurement — the same rule the catalog already keeps
    for `ttft_ms_seed`, `cost` and `best_for`."""
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    good = _cloud_model("good", ModelClass.FAST, ttft=900, tool_score=0.9)
    unknown = _cloud_model("unknown", ModelClass.FAST, ttft=100, tool_score=None)
    poor = _cloud_model("poor", ModelClass.FAST, ttft=100, tool_score=0.2)

    ranked = router.rank([poor, unknown, good], tool_shaped=True)
    assert [m.id for m in ranked] == ["good", "unknown", "poor"]


def _cloud_model(
    model_id: str, klass: ModelClass, *, ttft: int, tool_score: float | None
) -> catalog.ModelInfo:
    return catalog.ModelInfo(
        id=model_id,
        provider=catalog.ProviderName.OPENAI,
        label=model_id,
        klass=klass,
        persona=PersonaLevel.FULL,
        cost=catalog.Cost.LOW,
        best_for="",
        ttft_ms_seed=ttft,
        tool_score=tool_score,
    )


def test_a_command_is_not_slowed_down_for_a_difference_that_is_noise() -> None:
    """This assertion used to be the other way round, and it was wrong.

    One run of `gate_tool_selection.py` put `gpt-5.4-nano` at 19/24 against the
    local model's 21/24, and this bias was changed to route commands to the
    BALANCED class on the strength of it. Four runs over one probe set:
    nano 0.92/0.88/0.92/0.85, the 7B 0.88/0.88/0.81/0.85. The spread inside one
    model is wider than the gap between them.
    """
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    decision = router.choose("turn the volume up", available=ALL_MODELS)

    assert decision.model.klass is ModelClass.FAST


def test_an_ordinary_question_still_takes_the_fast_class() -> None:
    """Narrowing must not turn every turn into the slow path."""
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    decision = router.choose("what is the capital of Australia", available=ALL_MODELS)

    assert decision.model.klass is ModelClass.FAST


def test_scores_within_the_noise_are_ranked_by_speed() -> None:
    """The three measured models sit within 0.03 of each other, and the
    measurement moves by 0.07 between runs. Preferring one on that basis would
    be reading noise as signal."""
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    quick = _cloud_model("quick", ModelClass.FAST, ttft=200, tool_score=0.86)
    slow = _cloud_model("slow", ModelClass.FAST, ttft=900, tool_score=0.89)

    ranked = router.rank([slow, quick], tool_shaped=True)

    assert ranked[0].id == "quick"


def test_a_model_that_is_visibly_worse_still_loses() -> None:
    """The mechanism has to keep working, or banding would just be a way of
    ignoring the measurement entirely."""
    router = Router(HealthTracker(), RoutingBias.QUALITY)
    quick = _cloud_model("quick", ModelClass.FAST, ttft=200, tool_score=0.55)
    capable = _cloud_model("capable", ModelClass.FAST, ttft=900, tool_score=0.9)

    ranked = router.rank([quick, capable], tool_shaped=True)

    assert ranked[0].id == "capable"
