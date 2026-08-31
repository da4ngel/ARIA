"""Adding a provider obliges five other places to learn about it.

CLAUDE.md carries that checklist in prose, written down after OpenRouter was
wired up and each item was found the hard way. **Prose does not fail a test
run.** Every check here is parametrised over `ProviderName` itself, so the next
member added to that enum is checked by the same tests rather than by whoever
remembers to read the list.

Each of these omissions fails silently in a different way, which is what makes
them worth pinning:

- no `PROVIDER_LABELS` entry — `KeyError` deep inside `_verdict`, on the turn
  path, at the moment a model is being greyed out
- no `factory` branch — `build_all` raises at startup, which is the loud one
  and the reason it is built by iterating the enum
- no `_KEY_FOR` entry — every model from that provider is greyed out forever,
  with a reason that reads like a missing key
- not in `discover_all` — the picker is simply empty and nothing says why
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from sidecar.providers import discovery, factory
from sidecar.providers.availability import _KEY_FOR
from sidecar.providers.catalog import PROVIDER_LABELS, ProviderName

#: Ollama is reached without a credential, so it is exempt from `_KEY_FOR`
#: alone. It is exempt from nothing else.
KEYLESS = {ProviderName.OLLAMA}

#: And it is not a cloud listing, so `discover_all` does not ask it anything —
#: `runtime.local_models` comes from `ollama.list_models` at startup instead.
NOT_DISCOVERED = {ProviderName.OLLAMA}


@pytest.mark.parametrize("provider", list(ProviderName))
def test_every_provider_has_a_display_label(provider: ProviderName) -> None:
    """`_verdict` indexes this directly to say why a model is unavailable."""
    assert provider in PROVIDER_LABELS
    assert PROVIDER_LABELS[provider].strip()


@pytest.mark.parametrize("provider", list(ProviderName))
def test_every_provider_can_be_built(provider: ProviderName) -> None:
    """`for_provider` raises rather than defaulting, deliberately — a
    fall-through here is what once made two scripts measure Gemini while
    printing another model's name."""
    client = factory.for_provider(provider, ollama_url="http://127.0.0.1:11434")
    assert client.name == str(provider)


def test_building_them_all_covers_the_whole_enum() -> None:
    built = factory.build_all(ollama_url="http://127.0.0.1:11434")
    assert set(built) == {str(p) for p in ProviderName}


def test_an_unknown_provider_is_an_error_not_a_default() -> None:
    with pytest.raises(ValueError, match="deliberately an error"):
        factory.for_provider("nothing-of-the-sort")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "provider", [p for p in ProviderName if p not in KEYLESS]
)
def test_every_credentialled_provider_names_its_credential(
    provider: ProviderName,
) -> None:
    """Omitting this greys out every one of that provider's models forever,
    and the displayed reason is "no API key stored" — which is a lie about a
    key that is sitting right there in Credential Manager."""
    assert provider in _KEY_FOR
    assert _KEY_FOR[provider], "at least one credential must unlock it"


@pytest.mark.parametrize(
    "provider", [p for p in ProviderName if p not in NOT_DISCOVERED]
)
def test_every_cloud_provider_is_asked_what_it_offers(
    provider: ProviderName,
) -> None:
    """`discover_all` builds its sources as one sequence of (name, coroutine)
    pairs so the two cannot drift. This checks the sequence is complete."""
    source = inspect.getsource(discovery.discover_all)
    assert f"ProviderName.{provider.name}" in source


# ── the renderer half, which no Python test can import ────────────────


def test_the_picker_can_render_every_provider() -> None:
    """`ModelPicker.tsx` maps over `PROVIDER_ORDER` to draw its groups, and its
    own comment says a provider missing from that array is **invisible** —
    there is no fallback that lists the leftovers. So a provider can be fully
    wired end to end in Python and still not exist as far as anyone using the
    app is concerned.

    Read as text because there is no other way to reach it from here. Crude,
    and it is the only thing standing between a working provider and one
    nobody can select.
    """
    picker = (
        Path(__file__).resolve().parents[2] / "src" / "components" / "ModelPicker.tsx"
    ).read_text(encoding="utf-8")
    order = picker.split("const PROVIDER_ORDER = [", 1)[1].split("]", 1)[0]
    for provider in ProviderName:
        assert f"'{provider}'" in order, (
            f"{provider} is missing from PROVIDER_ORDER in ModelPicker.tsx, so "
            f"its models render nowhere at all"
        )
        assert f"  {provider}: '" in picker, (
            f"{provider} has no PROVIDER_LABEL in ModelPicker.tsx"
        )
