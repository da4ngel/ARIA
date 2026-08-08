"""Discovery, tested against the payloads the real APIs actually returned.

`fixtures/openai_models.json` and `fixtures/gemini_models.json` were captured
from the live endpoints — 124 and 58 models. A mock would agree with whatever
the filter happens to do; these do not.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from sidecar.core.context import PersonaLevel
from sidecar.providers.catalog import Cost, ModelClass, ProviderName
from sidecar.providers.discovery import parse_gemini, parse_openai

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return payload


@pytest.fixture(scope="module")
def openai_ids() -> set[str]:
    return {m.id for m in parse_openai(_load("openai_models.json"))}


@pytest.fixture(scope="module")
def gemini_ids() -> set[str]:
    return {m.id for m in parse_gemini(_load("gemini_models.json"))}


# ── the filter ────────────────────────────────────────────────────────
# The whole point of the module. Everything below is one question: does
# something that cannot hold a conversation reach the picker?

#: Substrings that must not survive. Each is a real id in the fixtures.
NOT_CHAT = (
    "embedding",
    "whisper",
    "tts-1",
    "-tts",
    "image",
    "sora",
    "moderation",
    "realtime",
    "transcribe",
    "audio",
    "lyria",
    "robotics",
    "deep-research",
    "nano-banana",
    "gemma",
    "computer-use",
    "babbage",
    "davinci",
)


@pytest.mark.parametrize("bad", NOT_CHAT)
def test_nothing_that_cannot_chat_survives(
    bad: str, openai_ids: set[str], gemini_ids: set[str]
) -> None:
    offenders = {i for i in openai_ids | gemini_ids if bad in i}
    assert not offenders, f"{bad!r} reached the picker: {sorted(offenders)}"


def test_the_filter_is_not_simply_rejecting_everything(
    openai_ids: set[str], gemini_ids: set[str]
) -> None:
    """The control. A filter that keeps nothing passes every test above."""
    assert "gpt-5.6-luna" in openai_ids
    assert "gpt-5" in openai_ids
    assert "gemini-3.6-flash" in gemini_ids
    assert "gemini-2.5-pro" in gemini_ids
    # Enough to be worth having, few enough to be a list a person can read.
    assert 8 <= len(openai_ids) <= 40, sorted(openai_ids)
    assert 8 <= len(gemini_ids) <= 40, sorted(gemini_ids)


def test_dated_snapshots_collapse_into_their_alias(openai_ids: set[str]) -> None:
    """`gpt-4o` stands for `gpt-4o-2024-08-06`; listing both is noise."""
    assert "gpt-4o" in openai_ids
    assert "gpt-4o-2024-08-06" not in openai_ids
    assert "gpt-5.2-2025-12-11" not in openai_ids
    # The old four-digit form too.
    assert "gpt-4-0613" not in openai_ids


def test_gemini_pinned_and_preview_aliases_collapse(gemini_ids: set[str]) -> None:
    """`-001` and `-preview` beside the plain id are the same model twice."""
    assert "gemini-2.0-flash" in gemini_ids
    assert "gemini-2.0-flash-001" not in gemini_ids
    assert "gemini-3.1-flash-lite" in gemini_ids
    assert "gemini-3.1-flash-lite-preview" not in gemini_ids
    # But a preview with nothing shipped behind it is the only way there.
    assert "gemini-3-pro-preview" in gemini_ids
    assert "gemini-flash-latest" in gemini_ids


def test_a_snapshot_with_no_alias_is_kept() -> None:
    """Dropping it would make that model unreachable, not merely tidy."""
    only_dated = {"data": [{"id": "gpt-9-turbo-2027-01-01"}]}
    assert [m.id for m in parse_openai(only_dated)] == ["gpt-9-turbo-2027-01-01"]


# ── what a discovered entry claims ────────────────────────────────────


def test_discovery_invents_no_measurements(openai_ids: set[str]) -> None:
    """Latency, cost and caveats are measured here or they are not stated."""
    for model in parse_openai(_load("openai_models.json")):
        assert model.discovered is True
        assert model.ttft_ms_seed is None
        assert model.caveat is None
        assert model.cost is Cost.UNKNOWN
        assert model.best_for == ""
        # The full persona made a *measured* model fabricate; an unmeasured one
        # does not get the benefit of the doubt.
        assert model.persona is PersonaLevel.MINIMAL


def test_no_discovered_model_carries_a_temperature() -> None:
    """CLAUDE.md: reasoning models reject any value but their own default, and
    both cloud clients forward whatever they are handed."""
    everything = parse_openai(_load("openai_models.json")) + parse_gemini(
        _load("gemini_models.json")
    )
    assert everything
    assert all(m.temperature is None for m in everything)


def test_gemini_context_windows_are_the_real_ones() -> None:
    """Gemini reports `inputTokenLimit`; using it beats assuming 32768."""
    by_id = {m.id: m for m in parse_gemini(_load("gemini_models.json"))}
    assert by_id["gemini-2.5-pro"].context_tokens == 1_048_576


def test_providers_are_tagged_correctly(openai_ids: set[str]) -> None:
    assert all(
        m.provider is ProviderName.OPENAI for m in parse_openai(_load("openai_models.json"))
    )
    assert all(
        m.provider is ProviderName.GEMINI for m in parse_gemini(_load("gemini_models.json"))
    )


def test_classes_are_plausible() -> None:
    by_id = {m.id: m for m in parse_openai(_load("openai_models.json"))}
    assert by_id["gpt-5.4-nano"].klass is ModelClass.FAST
    assert by_id["gpt-5.4-mini"].klass is ModelClass.FAST
    assert by_id["gpt-5.5-pro"].klass is ModelClass.SMART
    assert by_id["gpt-5.5"].klass is ModelClass.BALANCED
    # The o-series is the reasoning line, adjective or not.
    assert by_id["o3"].klass is ModelClass.SMART
    assert by_id["o3-mini"].klass is ModelClass.FAST


def test_labels_read_the_way_these_models_are_written() -> None:
    by_id = {m.id: m.label for m in parse_openai(_load("openai_models.json"))}
    assert by_id["gpt-4o"] == "GPT-4o"
    assert by_id["gpt-5.6-luna"] == "GPT-5.6 Luna"
    assert by_id["gpt-4.1-mini"] == "GPT-4.1 Mini"
    assert by_id["o4-mini"] == "O4 Mini"


# ── degradation ───────────────────────────────────────────────────────


def test_a_malformed_payload_yields_nothing_rather_than_raising() -> None:
    """A provider changing shape should empty the discovered list, not take
    the picker down with it."""
    assert parse_openai({}) == []
    assert parse_gemini({}) == []
    assert parse_openai({"data": ["nonsense", {"no_id": True}]}) == []
    assert parse_gemini({"models": [None, {"name": "models/x"}]}) == []
