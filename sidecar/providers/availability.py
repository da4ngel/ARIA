"""Which models are usable right now.

One object answers this for both `models.list` and the router. If they computed
it separately they would drift, and the picker would grey out a model the router
happily picks — the UI lying about what pressing send does.

Key presence is cached because reading Windows Credential Manager is a syscall,
and the router asks on every turn, on the latency path. `refresh_keys` is called
whenever a key changes.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import structlog
from pydantic import ValidationError

from sidecar.memory.settings_store import DISCOVERED_AT, DISCOVERED_MODELS
from sidecar.providers import catalog, discovery
from sidecar.providers.catalog import ModelAvailability, ModelInfo, ProviderName
from sidecar.providers.credentials import CredentialKey, get_key
from sidecar.providers.health import HealthTracker

if TYPE_CHECKING:
    from sidecar.memory.settings_store import SettingsStore

log = structlog.get_logger(__name__)

#: How long a provider listing is trusted before it is worth re-fetching.
#: Vendors add models in weeks, not minutes, and this is a network round-trip.
DISCOVERY_MAX_AGE = timedelta(hours=24)

# Which credential unlocks which provider. Ollama needs none.
#
# **A tuple, because Bedrock accepts either of two credential shapes** — a
# Bedrock API key (a bearer token) or an AWS access key that has to be signed
# with. Any one of them present unlocks the provider; requiring a single named
# key would grey out every Bedrock model for whichever half of the users hold
# the other kind.
_KEY_FOR: dict[ProviderName, tuple[CredentialKey, ...]] = {
    ProviderName.OPENAI: (CredentialKey.OPENAI,),
    ProviderName.GEMINI: (CredentialKey.GEMINI,),
    ProviderName.OPENROUTER: (CredentialKey.OPENROUTER,),
    ProviderName.BEDROCK: (
        CredentialKey.BEDROCK,
        # The secret alone is not a credential, so the *id* is what is checked:
        # a half-entered pair reads as "not configured" rather than as a key
        # that will fail at the first turn.
        CredentialKey.AWS_ACCESS_KEY_ID,
    ),
}


class AvailabilityService:
    """Live view of what can actually answer a turn."""

    def __init__(self, health: HealthTracker) -> None:
        self._health = health
        self._local_models: list[str] = []
        self._keys: dict[ProviderName, bool] = {}
        self.refresh_keys()

    # ── inputs ──────────────────────────────────────────────────────────

    def set_local_models(self, models: list[str]) -> None:
        """What Ollama has pulled. Discovered at startup, refreshed on demand."""
        self._local_models = list(models)

    @property
    def local_models(self) -> list[str]:
        return list(self._local_models)

    def refresh_keys(self) -> None:
        """Re-read the Credential Manager. Call after any key change."""
        self._keys = {
            p: any(bool(get_key(k)) for k in keys) for p, keys in _KEY_FOR.items()
        }
        log.info(
            "availability.keys",
            **{str(p): present for p, present in self._keys.items()},
        )

    def has_key(self, provider: ProviderName) -> bool:
        return self._keys.get(provider, False)

    # ── discovery ───────────────────────────────────────────────────────
    # What the cloud vendors say they offer, as opposed to what has been
    # measured here. Never on the turn path: this is a network round-trip and
    # §10 budgets ~1000ms end to end for a spoken reply.

    async def load_discovered(self, settings: SettingsStore) -> bool:
        """Fill the overlay from cache. Returns whether it is still fresh.

        A stale cache is still loaded — an old listing beats an empty picker,
        and offline is exactly when re-fetching cannot help.
        """
        raw = await settings.get(DISCOVERED_MODELS) or []
        models: list[ModelInfo] = []
        for item in raw:
            try:
                models.append(ModelInfo.model_validate(item))
            except ValidationError:
                # The shape changed under a cached row. Drop it and re-fetch
                # rather than refuse to start.
                log.warning("discovery.cache_unreadable")
                return False

        catalog.set_discovered(models)
        log.info("discovery.restored", count=len(models))
        return bool(models) and not await self._is_stale(settings)

    async def _is_stale(self, settings: SettingsStore) -> bool:
        stamp = await settings.get(DISCOVERED_AT)
        if not isinstance(stamp, str):
            return True
        try:
            fetched = datetime.fromisoformat(stamp)
        except ValueError:
            return True
        return datetime.now(UTC) - fetched > DISCOVERY_MAX_AGE

    async def refresh_discovered(self, settings: SettingsStore) -> list[ModelInfo]:
        """Ask both providers what they offer, then remember the answer.

        A provider being unreachable costs its own listing and nothing else —
        `discover_all` already degrades per provider. An empty result is *not*
        written over a good cache: a flaky network should not erase the picker.
        """
        found = await discovery.discover_all()
        if not found:
            log.warning("discovery.empty_kept_cache")
            return catalog.discovered()

        catalog.set_discovered(found)
        await settings.set(DISCOVERED_MODELS, [m.model_dump(mode="json") for m in found])
        await settings.set(DISCOVERED_AT, datetime.now(UTC).isoformat())
        log.info("discovery.refreshed", count=len(found))
        return found

    # ── outputs ─────────────────────────────────────────────────────────

    def entries(self) -> list[ModelAvailability]:
        """Every catalog model with a verdict and a displayable reason."""
        return catalog.resolve_availability(self._local_models, self._keys, self._health)

    def usable(self) -> set[str]:
        """The ids the router may choose from."""
        return catalog.usable_ids(self.entries())
