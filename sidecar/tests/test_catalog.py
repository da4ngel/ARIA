"""Model availability — the one resolver behind both the picker and the router.

If these two ever disagree the UI is lying about what pressing send does, so
`models.list` and `Router.choose` are fed from the same function.
"""

from __future__ import annotations

import pytest

from sidecar.providers import catalog
from sidecar.providers.catalog import ProviderName
from sidecar.providers.health import HealthTracker

ALL_PULLED = [m.id for m in catalog.local_models()]
BOTH_KEYS = {ProviderName.OPENAI: True, ProviderName.GEMINI: True}
NO_KEYS = {ProviderName.OPENAI: False, ProviderName.GEMINI: False}


def entry_for(entries, model_id: str):
    return next(e for e in entries if e.model.id == model_id)


def test_everything_available_when_pulled_and_keyed() -> None:
    entries = catalog.resolve_availability(ALL_PULLED, BOTH_KEYS)
    assert all(e.available for e in entries)
    assert catalog.usable_ids(entries) == {m.id for m in catalog.CATALOG}


def test_unpulled_local_model_names_the_pull_command() -> None:
    entries = catalog.resolve_availability([], BOTH_KEYS)
    entry = entry_for(entries, catalog.PREFERRED_LOCAL)
    assert not entry.available
    # CLAUDE.md: error messages say what to do next.
    assert f"ollama pull {catalog.PREFERRED_LOCAL}" in (entry.reason or "")


def test_missing_key_blocks_only_that_provider() -> None:
    keys = {ProviderName.OPENAI: False, ProviderName.GEMINI: True}
    entries = catalog.resolve_availability(ALL_PULLED, keys)
    assert not entry_for(entries, "gpt-5").available
    assert entry_for(entries, "gemini-3.6-flash").available


def test_missing_key_reason_spells_the_provider_correctly() -> None:
    """`str.capitalize()` would render these 'Openai' — they are user-facing."""
    entries = catalog.resolve_availability(ALL_PULLED, NO_KEYS)
    assert "OpenAI" in (entry_for(entries, "gpt-5").reason or "")
    assert "Gemini" in (entry_for(entries, "gemini-3.6-flash").reason or "")


def test_no_keys_leaves_only_local_models_usable() -> None:
    entries = catalog.resolve_availability(ALL_PULLED, NO_KEYS)
    assert catalog.usable_ids(entries) == set(ALL_PULLED)


def test_tripped_circuit_marks_a_model_unavailable_with_a_countdown() -> None:
    health = HealthTracker()
    health.record_failure("gpt-5", "429", rate_limited=True)

    entries = catalog.resolve_availability(ALL_PULLED, BOTH_KEYS, health)
    entry = entry_for(entries, "gpt-5")
    assert not entry.available
    assert "retrying in" in (entry.reason or "")
    assert "gpt-5" not in catalog.usable_ids(entries)


def test_observed_latency_is_surfaced_for_tooltips() -> None:
    health = HealthTracker()
    health.record_success("gpt-4.1-mini", 900.0)

    entries = catalog.resolve_availability(ALL_PULLED, BOTH_KEYS, health)
    assert entry_for(entries, "gpt-4.1-mini").observed_ttft_ms == pytest.approx(900.0)
    assert entry_for(entries, "gpt-5").observed_ttft_ms is None


def test_a_known_429_caveat_does_not_block_selection() -> None:
    """The free-tier quota may have reset — show the warning, allow the pick."""
    entries = catalog.resolve_availability(ALL_PULLED, BOTH_KEYS)
    entry = entry_for(entries, "gemini-3.1-pro-preview")
    assert entry.available
    assert "429" in (entry.model.caveat or "")


# ── default_local ─────────────────────────────────────────────────────


def test_default_local_prefers_the_instruction_tuned_7b() -> None:
    assert catalog.default_local(ALL_PULLED).id == catalog.PREFERRED_LOCAL


def test_default_local_falls_back_to_what_is_actually_pulled() -> None:
    assert catalog.default_local(["qwen3.5:4b"]).id == "qwen3.5:4b"


def test_default_local_without_argument_names_the_preferred_model() -> None:
    assert catalog.default_local().id == catalog.PREFERRED_LOCAL


def test_default_local_with_nothing_pulled_still_returns_a_model() -> None:
    """Callers use this as a last resort; it must not raise."""
    assert catalog.default_local([]).id == catalog.PREFERRED_LOCAL


# ── catalog integrity ─────────────────────────────────────────────────


def test_model_ids_are_unique() -> None:
    ids = [m.id for m in catalog.CATALOG]
    assert len(ids) == len(set(ids))


def test_every_provider_in_the_catalog_has_a_display_label() -> None:
    for info in catalog.CATALOG:
        assert catalog.PROVIDER_LABELS[info.provider]


def test_every_model_has_tooltip_content() -> None:
    """The picker builds its tooltip from these — an empty one is a blank box."""
    for info in catalog.CATALOG:
        assert info.label and info.best_for, info.id


def test_each_class_has_a_cloud_model_so_routing_can_resolve() -> None:
    for klass in (catalog.ModelClass.FAST, catalog.ModelClass.SMART):
        assert [m for m in catalog.by_class(klass) if not m.local], klass


def test_persona_for_unknown_model_is_the_safe_minimal_prompt() -> None:
    from sidecar.core.context import PersonaLevel

    assert catalog.persona_for("no-such-model") is PersonaLevel.MINIMAL
