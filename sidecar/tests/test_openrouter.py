"""OpenRouter: the provider, and the filters that decide what is even offered.

The parsing half is tested against a **captured slice of the real listing**
(`fixtures/openrouter_models.json`, 41 of 414 entries: every free model, every
model carrying an `expiration_date`, and a sample of paid ones). Same reasoning
as the OpenAI and Gemini fixtures — a mock payload agrees with whatever the
filter happens to do, and these filters exist because the live data is full of
things that are not chat models.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest

from sidecar.core.context import PersonaLevel
from sidecar.providers import catalog
from sidecar.providers.base import ProviderRateLimited, ProviderUnavailable
from sidecar.providers.discovery import parse_openrouter
from sidecar.providers.openrouter import (
    APP_TITLE,
    OpenRouterProvider,
    RateLimitState,
)

FIXTURE = Path(__file__).parent / "fixtures" / "openrouter_models.json"


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return loaded


# ── what gets offered ─────────────────────────────────────────────────


def test_only_free_models_survive(payload) -> None:
    found = parse_openrouter(payload)
    assert found, "the fixture holds free models; parsing found none"
    for model in found:
        assert model.cost is catalog.Cost.FREE
        assert model.id.endswith(":free") or "free" in model.id


def test_a_paid_model_is_never_offered(payload) -> None:
    """The fixture deliberately carries real paid entries."""
    free_ids = {m.id for m in parse_openrouter(payload)}
    paid = [
        entry["id"]
        for entry in payload["data"]
        if str((entry.get("pricing") or {}).get("prompt")) != "0"
    ]
    assert paid, "the fixture should contain paid models to reject"
    assert not (set(paid) & free_ids)


def test_free_on_input_but_charged_on_output_is_not_free() -> None:
    """`pricing.prompt == "0"` alone is not the question.

    Nothing in the live listing is currently shaped this way, which is exactly
    why it is worth a test: the day one appears, the filter should already
    have been right rather than the bill being the thing that says so.
    """
    half_free = {
        "data": [
            {
                "id": "vendor/half-free",
                "name": "Half Free",
                "pricing": {"prompt": "0", "completion": "0.0000012"},
                "supported_parameters": ["tools"],
                "context_length": 128000,
            }
        ]
    }
    assert parse_openrouter(half_free) == []


def test_a_model_that_cannot_call_tools_is_not_offered(payload) -> None:
    """A hard filter, and it does two jobs.

    ARIA offers 41 tools, so a model without them fails most of what it would
    be asked here — and measuring one would spend scarce daily quota to learn
    something the payload already stated. The live free listing includes two
    music generators, which this is also what removes.
    """
    offered = {m.id for m in parse_openrouter(payload)}
    toolless = [
        entry["id"]
        for entry in payload["data"]
        if str((entry.get("pricing") or {}).get("prompt")) == "0"
        and "tools" not in (entry.get("supported_parameters") or [])
    ]
    assert toolless, "the fixture should contain free models without tool support"
    assert not (set(toolless) & offered)


def test_the_free_models_router_is_not_a_model(payload) -> None:
    """`openrouter/free` forwards to whichever free model it likes.

    Measuring it would produce a score attributable to nothing, and adopting
    it would put an unmeasured model into Smart's pool through the back door —
    the exact property `by_class` exists to prevent.
    """
    assert "openrouter/free" in {entry["id"] for entry in payload["data"]}
    assert "openrouter/free" not in {m.id for m in parse_openrouter(payload)}


def test_an_expired_model_is_dropped_but_a_future_one_is_kept() -> None:
    """An expired id 404s mid-turn, which reads as ARIA being broken."""
    entries = {
        "data": [
            {
                "id": "vendor/gone:free",
                "name": "Gone",
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["tools"],
                "context_length": 128000,
                "expiration_date": "2026-01-01",
            },
            {
                "id": "vendor/still-here:free",
                "name": "Still Here",
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["tools"],
                "context_length": 128000,
                "expiration_date": "2027-01-01",
            },
        ]
    }
    ids = {m.id for m in parse_openrouter(entries, today=date(2026, 8, 19))}
    assert ids == {"vendor/still-here:free"}


def test_an_unparseable_expiry_does_not_remove_a_model() -> None:
    """Fail towards keeping it: a bad date string is not evidence of anything."""
    entries = {
        "data": [
            {
                "id": "vendor/odd-date:free",
                "name": "Odd Date",
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["tools"],
                "context_length": 4096,
                "expiration_date": "whenever",
            }
        ]
    }
    assert [m.id for m in parse_openrouter(entries)] == ["vendor/odd-date:free"]


# ── what is claimed about them ────────────────────────────────────────


def test_nothing_measured_here_is_invented(payload) -> None:
    """The rule the whole discovery module is built on.

    `Cost.FREE` is the one exception and it is not an exception to the rule:
    the API *states* the price is zero. Everything that would have to be
    measured on this machine stays empty.
    """
    for model in parse_openrouter(payload):
        assert model.ttft_ms_seed is None
        assert model.tool_score is None
        assert model.caveat is None
        assert model.temperature is None
        assert model.persona is not None
        assert model.discovered is True


def test_context_length_is_read_not_assumed(payload) -> None:
    stated = {
        entry["id"]: entry["context_length"]
        for entry in payload["data"]
        if entry.get("context_length")
    }
    for model in parse_openrouter(payload):
        assert model.context_tokens == stated[model.id]


def test_every_free_model_is_marked_as_training_on_data(payload) -> None:
    """A property of the endpoint, not of the model.

    OpenRouter's free tier can route to providers that train on what is sent.
    The account holder can opt out; this code cannot assert that they have, so
    it labels rather than assumes — and `core/router.py` keeps his files away.
    """
    for model in parse_openrouter(payload):
        assert model.trains_on_data is True


def test_the_queue_comes_out_best_first(payload) -> None:
    """Which matters more than it looks at ten measurement requests a day.

    A candidate takes two days, so the order the queue is built in decides
    what gets measured this week and what waits until next month.
    """
    found = parse_openrouter(payload)
    scored = [m.benchmark_index for m in found if m.benchmark_index is not None]
    assert scored == sorted(scored, reverse=True)
    # Unscored models sort last — a published number is better evidence for
    # "worth measuring first" than no number at all.
    first_unscored = next(
        (i for i, m in enumerate(found) if m.benchmark_index is None), len(found)
    )
    assert all(m.benchmark_index is None for m in found[first_unscored:])


def test_a_benchmark_is_carried_verbatim_never_treated_as_a_measurement(payload) -> None:
    published = {
        entry["id"]: (entry.get("benchmarks") or {})
        .get("artificial_analysis", {})
        .get("intelligence_index")
        for entry in payload["data"]
    }
    for model in parse_openrouter(payload):
        assert model.benchmark_index == published[model.id]
        # The distinction that matters: a third party's score is not this
        # machine's measurement, and must never stand in for one.
        assert model.tool_score is None


# ── the provider ──────────────────────────────────────────────────────


def test_it_reuses_the_openai_wire_format() -> None:
    """Subclassing rather than copying is the whole point.

    Two copies of a fragment-accumulating tool-call assembler is two things to
    fix when one of them is wrong.
    """
    from sidecar.providers.openai import OpenAIProvider

    assert issubclass(OpenRouterProvider, OpenAIProvider)
    provider = OpenRouterProvider()
    assert provider.name == "openrouter"
    assert "openrouter.ai" in str(provider._client.base_url)  # noqa: SLF001


def test_no_key_is_a_clear_error_not_a_crash(monkeypatch) -> None:
    monkeypatch.setattr("sidecar.providers.openrouter.get_key", lambda _: None)
    provider = OpenRouterProvider()
    with pytest.raises(ProviderUnavailable) as exc:
        provider._headers()  # noqa: SLF001
    # CLAUDE.md: an error message says what to do next.
    assert "Settings" in str(exc.value)


def test_the_identification_headers_carry_nothing_about_the_user(monkeypatch) -> None:
    monkeypatch.setattr("sidecar.providers.openrouter.get_key", lambda _: "sk-test")
    headers = OpenRouterProvider()._headers()  # noqa: SLF001
    assert headers["Authorization"] == "Bearer sk-test"
    assert headers["X-Title"] == APP_TITLE
    assert "eyaas" not in json.dumps(headers).lower()


def test_a_429_says_how_much_quota_is_left() -> None:
    """The free tier is 50 requests a day, so this is routine, not an incident.

    A rate limit discovered by hitting it mid-conversation is the "on is not
    the same as working" failure `settings.online` already exists to avoid —
    so the remaining count travels with the error rather than being lost.
    """
    provider = OpenRouterProvider()
    headers = httpx.Headers(
        {
            "x-ratelimit-limit": "50",
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": "99999999999999",
        }
    )
    with pytest.raises(ProviderRateLimited) as exc:
        provider._raise_for_detail(429, "rate limit exceeded", headers)  # noqa: SLF001
    assert "0 left" in str(exc.value)
    assert provider.rate_limit.remaining == 0
    assert provider.rate_limit.limit == 50


def test_the_free_allowance_is_counted_here_because_the_api_does_not_say() -> None:
    """**Checked live on 2026-08-19, and the first version was wrong.**

    OpenRouter returns no rate-limit headers on a successful chat completion —
    the only `x-` header is `x-generation-id` — and `GET /api/v1/key` reports
    usage in *credits*, which is `0` for every free model by definition. So the
    remaining free *request* count is not exposed by the API at all, and a
    reader built on those headers would have displayed nothing forever.
    """
    state = RateLimitState()
    assert state.as_dict()["remaining"] == 50

    for _ in range(3):
        state.record_request()
    reported = state.as_dict()
    assert reported["spent_today"] == 3
    assert reported["remaining"] == 47
    # And it says so. A number the UI presents as authoritative when it is an
    # inference from a local count is worse than no number: the same key used
    # from a script or another machine is invisible here.
    assert reported["counted_here"] is True


def test_a_stated_figure_beats_the_local_count() -> None:
    """The header reader is kept because a 429 is documented to carry them.

    If a real figure ever arrives it must win, and stop claiming to be local.
    """
    state = RateLimitState()
    state.record_request()
    state.update(httpx.Headers({"x-ratelimit-limit": "50", "x-ratelimit-remaining": "31"}))
    reported = state.as_dict()
    assert reported["remaining"] == 31
    assert reported["counted_here"] is False
    # A response that says nothing must not silently reset what is known.
    state.update(httpx.Headers({}))
    assert state.remaining == 31
    # Zero is a real reading, not a missing one.
    state.update(httpx.Headers({"x-ratelimit-remaining": "0"}))
    assert state.remaining == 0


def test_a_non_429_still_reaches_the_base_handling() -> None:
    """The override adds to `OpenAIProvider._raise_for_detail`, never replaces it."""
    provider = OpenRouterProvider()
    with pytest.raises(ProviderUnavailable):
        provider._raise_for_detail(401, "invalid key", httpx.Headers({}))  # noqa: SLF001


# ── reasoning, and why it cannot be switched off blindly ──────────────


def test_reasoning_is_turned_off_where_the_endpoint_allows_it() -> None:
    """CLAUDE.md's *"always send `think: false` to Ollama"* rule, second provider.

    A reasoning model streams into a separate channel and leaves `content`
    empty until it is done, so the whole token budget is spent before a word is
    written. Measured live: `nvidia/nemotron-3-super-120b-a12b:free` answers
    "Canberra" with **zero** characters of reasoning once this is sent, and
    reasons by default without it.
    """
    info = catalog.ModelInfo(
        id="vendor/optional-reasoning:free",
        provider=catalog.ProviderName.OPENROUTER,
        label="Optional",
        klass=catalog.ModelClass.FAST,
        persona=PersonaLevel.MINIMAL,
        cost=catalog.Cost.FREE,
        best_for="",
        reasoning_mandatory=False,
        discovered=True,
    )
    catalog.set_discovered([info])
    try:
        body = OpenRouterProvider()._extra_body(info.id)  # noqa: SLF001
        assert body == {"reasoning": {"enabled": False}}
    finally:
        catalog.set_discovered([])


def test_it_is_never_sent_to_an_endpoint_that_requires_reasoning() -> None:
    """**A hard 400, not a warning**, and it kills the whole turn.

    Measured live: `openai/gpt-oss-20b:free` returns *"Reasoning is mandatory
    for this endpoint and cannot be disabled."*
    """
    info = catalog.ModelInfo(
        id="vendor/must-reason:free",
        provider=catalog.ProviderName.OPENROUTER,
        label="Must Reason",
        klass=catalog.ModelClass.FAST,
        persona=PersonaLevel.MINIMAL,
        cost=catalog.Cost.FREE,
        best_for="",
        reasoning_mandatory=True,
        discovered=True,
    )
    catalog.set_discovered([info])
    try:
        assert OpenRouterProvider()._extra_body(info.id) == {}  # noqa: SLF001
    finally:
        catalog.set_discovered([])


def test_an_unknown_model_fails_open() -> None:
    """The cost of not sending it is wasted tokens; the cost of sending it
    wrongly is a dead turn. So an id the catalog has never seen gets nothing."""
    catalog.set_discovered([])
    assert OpenRouterProvider()._extra_body("someone/brand-new:free") == {}  # noqa: SLF001


def test_whether_reasoning_is_mandatory_is_read_from_the_payload(payload) -> None:
    """Not a hand-written list of model ids, which is what `eval_quality.py`
    still carries and which cannot know about a model discovered this morning."""
    stated = {
        entry["id"]: bool((entry.get("reasoning") or {}).get("mandatory", False))
        for entry in payload["data"]
    }
    found = parse_openrouter(payload)
    assert any(m.reasoning_mandatory for m in found), "the fixture should carry one"
    for model in found:
        assert model.reasoning_mandatory == stated[model.id]
