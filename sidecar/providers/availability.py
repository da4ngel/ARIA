"""Which models are usable right now.

One object answers this for both `models.list` and the router. If they computed
it separately they would drift, and the picker would grey out a model the router
happily picks — the UI lying about what pressing send does.

Key presence is cached because reading Windows Credential Manager is a syscall,
and the router asks on every turn, on the latency path. `refresh_keys` is called
whenever a key changes.
"""

from __future__ import annotations

import structlog

from sidecar.providers import catalog
from sidecar.providers.catalog import ModelAvailability, ProviderName
from sidecar.providers.credentials import CredentialKey, get_key
from sidecar.providers.health import HealthTracker

log = structlog.get_logger(__name__)

# Which credential unlocks which provider. Ollama needs none.
_KEY_FOR: dict[ProviderName, CredentialKey] = {
    ProviderName.OPENAI: CredentialKey.OPENAI,
    ProviderName.GEMINI: CredentialKey.GEMINI,
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
        self._keys = {p: bool(get_key(k)) for p, k in _KEY_FOR.items()}
        log.info(
            "availability.keys",
            **{str(p): present for p, present in self._keys.items()},
        )

    def has_key(self, provider: ProviderName) -> bool:
        return self._keys.get(provider, False)

    # ── outputs ─────────────────────────────────────────────────────────

    def entries(self) -> list[ModelAvailability]:
        """Every catalog model with a verdict and a displayable reason."""
        return catalog.resolve_availability(self._local_models, self._keys, self._health)

    def usable(self) -> set[str]:
        """The ids the router may choose from."""
        return catalog.usable_ids(self.entries())
