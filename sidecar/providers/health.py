"""Per-model health and observed latency.

Two jobs:

1. **Observed TTFT (EWMA).** The catalog's `ttft_ms_seed` values were measured
   once and single samples are weak evidence — one of them (`gemini-3.5-flash`
   at 5440ms vs `3.6-flash` at 2567ms) looks like a cold start. Ranking on
   observed latency means a stale seed self-corrects instead of misrouting
   forever.

2. **Circuit breaker.** A 429 trips immediately and cools down far longer than a
   timeout does, because a rate limit is not transient the way a dropped
   connection is — retrying it promptly just burns quota.
"""

from __future__ import annotations

import time

import structlog
from pydantic import BaseModel

log = structlog.get_logger(__name__)

EWMA_ALPHA = 0.3  # weight of the newest sample
FAILURES_TO_TRIP = 3
FAILURE_COOLDOWN_S = 60.0
RATE_LIMIT_COOLDOWN_S = 300.0


class ModelHealth(BaseModel):
    """Rolling health for one model id."""

    # `model_id` collides with pydantic's protected `model_` namespace; the
    # field name is the clearer one, so disable the guard rather than rename.
    model_config = {"protected_namespaces": ()}

    model_id: str
    observed_ttft_ms: float | None = None
    consecutive_failures: int = 0
    tripped_until: float = 0.0
    last_error: str | None = None

    def healthy(self, now: float | None = None) -> bool:
        return (now or time.monotonic()) >= self.tripped_until

    def cooldown_remaining_s(self, now: float | None = None) -> float:
        return max(0.0, self.tripped_until - (now or time.monotonic()))


class HealthTracker:
    """In-memory health per model. Rebuilt on restart, which is fine —
    a fresh process should re-probe rather than trust a stale verdict."""

    def __init__(self) -> None:
        self._health: dict[str, ModelHealth] = {}

    def get(self, model_id: str) -> ModelHealth:
        return self._health.setdefault(model_id, ModelHealth(model_id=model_id))

    def record_success(self, model_id: str, ttft_ms: float | None) -> None:
        health = self.get(model_id)
        health.consecutive_failures = 0
        health.tripped_until = 0.0
        health.last_error = None
        if ttft_ms is None:
            return
        health.observed_ttft_ms = (
            ttft_ms
            if health.observed_ttft_ms is None
            else EWMA_ALPHA * ttft_ms + (1 - EWMA_ALPHA) * health.observed_ttft_ms
        )

    def record_failure(self, model_id: str, error: str, *, rate_limited: bool = False) -> None:
        health = self.get(model_id)
        health.last_error = error

        if rate_limited:
            health.tripped_until = time.monotonic() + RATE_LIMIT_COOLDOWN_S
            health.consecutive_failures = FAILURES_TO_TRIP
            log.warning(
                "health.rate_limited", model=model_id, cooldown_s=RATE_LIMIT_COOLDOWN_S
            )
            return

        health.consecutive_failures += 1
        if health.consecutive_failures >= FAILURES_TO_TRIP:
            health.tripped_until = time.monotonic() + FAILURE_COOLDOWN_S
            log.warning(
                "health.tripped",
                model=model_id,
                failures=health.consecutive_failures,
                cooldown_s=FAILURE_COOLDOWN_S,
            )

    def is_usable(self, model_id: str) -> bool:
        return self.get(model_id).healthy()

    def latency_for(self, model_id: str, seed_ms: int | None) -> float:
        """Observed latency if we have it, else the catalog seed, else pessimistic.

        Unknown models sort last rather than first — an unmeasured model should
        not win a latency ranking by default.
        """
        observed = self.get(model_id).observed_ttft_ms
        if observed is not None:
            return observed
        return float(seed_ms) if seed_ms is not None else 10_000.0

    def snapshot(self) -> dict[str, ModelHealth]:
        return dict(self._health)


tracker = HealthTracker()
