"""Routing decisions, asserted over a labelled message set. No network.

The router is pure by design — it returns a decision and never performs a call —
so every case here is a plain function call against a synthetic catalog state.
"""

from __future__ import annotations

import pytest

from sidecar.core.router import (
    RouteDecision,
    Router,
    RoutingBias,
    is_trivial,
    needs_deep_model,
)
from sidecar.providers import catalog
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


def test_prefers_the_7b_when_it_is_pulled(health: HealthTracker) -> None:
    decision = router(health, RoutingBias.FASTEST).choose("hi", available=ALL_MODELS)
    assert decision.model.id == catalog.PREFERRED_LOCAL


def test_falls_back_to_the_4b_when_the_7b_is_not_pulled(health: HealthTracker) -> None:
    """The 7B is a 4.7GB download that may not have finished."""
    available = ALL_MODELS - {catalog.PREFERRED_LOCAL}
    decision = router(health, RoutingBias.FASTEST).choose("hi", available=available)
    assert decision.model.id == "qwen3.5:4b"


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
