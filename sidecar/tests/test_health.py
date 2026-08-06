"""Observed latency and the circuit breaker.

A 429 is treated as a routing input rather than an exception (§9.7 stage 7): the
free-tier Gemini key rate-limited on its very first call, so this is a normal
state, not a rare one.
"""

from __future__ import annotations

import pytest

from sidecar.providers.health import (
    EWMA_ALPHA,
    FAILURE_COOLDOWN_S,
    FAILURES_TO_TRIP,
    RATE_LIMIT_COOLDOWN_S,
    HealthTracker,
)


@pytest.fixture
def tracker() -> HealthTracker:
    return HealthTracker()


def test_unseen_model_is_usable() -> None:
    """A fresh process re-probes rather than assuming the worst."""
    assert HealthTracker().is_usable("gpt-5")


def test_first_sample_is_taken_verbatim(tracker: HealthTracker) -> None:
    tracker.record_success("gpt-5", 1000.0)
    assert tracker.get("gpt-5").observed_ttft_ms == pytest.approx(1000.0)


def test_ewma_weights_the_newest_sample(tracker: HealthTracker) -> None:
    tracker.record_success("gpt-5", 1000.0)
    tracker.record_success("gpt-5", 2000.0)
    expected = EWMA_ALPHA * 2000.0 + (1 - EWMA_ALPHA) * 1000.0
    assert tracker.get("gpt-5").observed_ttft_ms == pytest.approx(expected)


def test_ewma_converges_towards_a_stable_latency(tracker: HealthTracker) -> None:
    """A stale seed must self-correct rather than misroute forever."""
    for _ in range(30):
        tracker.record_success("gemini-3.6-flash", 500.0)
    assert tracker.get("gemini-3.6-flash").observed_ttft_ms == pytest.approx(500.0, abs=1.0)


def test_success_without_a_sample_does_not_disturb_the_average(tracker: HealthTracker) -> None:
    tracker.record_success("gpt-5", 800.0)
    tracker.record_success("gpt-5", None)
    assert tracker.get("gpt-5").observed_ttft_ms == pytest.approx(800.0)


# ── circuit breaker ───────────────────────────────────────────────────


def test_stays_usable_below_the_failure_threshold(tracker: HealthTracker) -> None:
    for _ in range(FAILURES_TO_TRIP - 1):
        tracker.record_failure("gpt-5", "timeout")
    assert tracker.is_usable("gpt-5")


def test_trips_on_the_third_consecutive_failure(tracker: HealthTracker) -> None:
    for _ in range(FAILURES_TO_TRIP):
        tracker.record_failure("gpt-5", "timeout")
    assert not tracker.is_usable("gpt-5")
    assert tracker.get("gpt-5").cooldown_remaining_s() == pytest.approx(
        FAILURE_COOLDOWN_S, abs=1.0
    )


def test_rate_limit_trips_immediately_and_cools_down_longer(tracker: HealthTracker) -> None:
    """A 429 is not transient the way a dropped connection is."""
    tracker.record_failure("gemini-3.1-pro-preview", "HTTP 429", rate_limited=True)
    assert not tracker.is_usable("gemini-3.1-pro-preview")
    assert tracker.get("gemini-3.1-pro-preview").cooldown_remaining_s() > FAILURE_COOLDOWN_S
    assert tracker.get("gemini-3.1-pro-preview").cooldown_remaining_s() == pytest.approx(
        RATE_LIMIT_COOLDOWN_S, abs=1.0
    )


def test_success_resets_the_breaker(tracker: HealthTracker) -> None:
    for _ in range(FAILURES_TO_TRIP):
        tracker.record_failure("gpt-5", "timeout")
    tracker.record_success("gpt-5", 900.0)
    assert tracker.is_usable("gpt-5")
    assert tracker.get("gpt-5").consecutive_failures == 0
    assert tracker.get("gpt-5").last_error is None


def test_failures_are_tracked_per_model(tracker: HealthTracker) -> None:
    for _ in range(FAILURES_TO_TRIP):
        tracker.record_failure("gpt-5", "timeout")
    assert not tracker.is_usable("gpt-5")
    assert tracker.is_usable("gpt-4.1-mini")


def test_last_error_is_kept_for_the_tooltip(tracker: HealthTracker) -> None:
    tracker.record_failure("gpt-5", "connection refused")
    assert tracker.get("gpt-5").last_error == "connection refused"


# ── ranking input ─────────────────────────────────────────────────────


def test_latency_prefers_observed_over_the_seed(tracker: HealthTracker) -> None:
    tracker.record_success("gpt-5", 300.0)
    assert tracker.latency_for("gpt-5", 2434) == pytest.approx(300.0)


def test_latency_falls_back_to_the_seed(tracker: HealthTracker) -> None:
    assert tracker.latency_for("gpt-5", 2434) == pytest.approx(2434.0)


def test_unmeasured_model_sorts_last(tracker: HealthTracker) -> None:
    """An unmeasured model must not win a latency ranking by default."""
    assert tracker.latency_for("gpt-4o", None) > 5000.0


def test_snapshot_is_a_copy(tracker: HealthTracker) -> None:
    tracker.record_success("gpt-5", 100.0)
    snapshot = tracker.snapshot()
    snapshot.pop("gpt-5")
    assert "gpt-5" in tracker.snapshot()
