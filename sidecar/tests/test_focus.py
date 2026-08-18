"""Focus detection (BUILD_SPEC §9 Phase 8): the comparison logic and the
combination rule, both testable without mocking three Win32 modules.

`is_fullscreen()`/`seconds_since_last_input()` themselves call real Win32
APIs and are verified live instead — the same treatment this project
already gives its other OS-integration code (CLAUDE.md: the overlay's
window flags, "verified via GetWindowLong").
"""

from __future__ import annotations

import pytest

from sidecar.persona import focus
from sidecar.persona.focus import RECENT_ACTIVITY_S, is_actively_working
from sidecar.persona.focus import _covers_monitor as covers_monitor


def test_a_window_exactly_matching_its_monitor_is_fullscreen() -> None:
    assert covers_monitor((0, 0, 1920, 1080), (0, 0, 1920, 1080))


def test_a_maximized_but_not_fullscreen_window_is_not() -> None:
    """A maximized window on Windows typically sits a few pixels inside the
    monitor bounds (the invisible resize border) — this must not count."""
    assert not covers_monitor((0, 0, 1912, 1040), (0, 0, 1920, 1080))


def test_a_window_on_a_different_monitor_is_not_fullscreen() -> None:
    assert not covers_monitor((0, 0, 1920, 1080), (1920, 0, 3840, 1080))


@pytest.fixture(autouse=True)
def _isolate(monkeypatch: pytest.MonkeyPatch) -> None:
    """`is_actively_working` calls the two live-verified functions by
    name — patch both so every test here controls exactly what they see."""
    monkeypatch.setattr(focus, "is_fullscreen", lambda: False)
    monkeypatch.setattr(focus, "seconds_since_last_input", lambda: 99999.0)


def test_fullscreen_alone_is_enough(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(focus, "is_fullscreen", lambda: True)
    assert is_actively_working()


def test_recent_input_alone_is_enough(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(focus, "seconds_since_last_input", lambda: 5.0)
    assert is_actively_working()


def test_neither_signal_means_not_working() -> None:
    assert not is_actively_working()


def test_input_right_at_the_boundary_still_counts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(focus, "seconds_since_last_input", lambda: RECENT_ACTIVITY_S - 1)
    assert is_actively_working()


def test_input_just_past_the_boundary_does_not(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(focus, "seconds_since_last_input", lambda: RECENT_ACTIVITY_S + 1)
    assert not is_actively_working()


def test_an_unknown_last_input_reading_is_not_read_as_idle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A broken probe must not block every proactive message forever —
    `None` (the check failed) is treated as "not actively working", not as
    "definitely idle" either; it just does not, on its own, suppress a
    send."""
    monkeypatch.setattr(focus, "seconds_since_last_input", lambda: None)
    assert not is_actively_working()
