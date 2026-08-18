"""Is this a bad moment to interrupt? (BUILD_SPEC §9 Phase 8)

Two read-only Win32 checks, both already-used primitives elsewhere in this
project (`tools/apps.py`'s own `GetForegroundWindow` polling) applied to a
new question. Neither one hooks a keyboard, records a keystroke, or reads
what any window contains — the same restraint `listener.py` already applies
to audio: this looks at *whether* the machine is busy, never *what* with.

**"20min uninterrupted typing" becomes sustained recent input activity, and
that relabelling is deliberate, not a shortcut taken quietly.** Windows has
no API that reports "the user is typing" specifically — `GetLastInputInfo`
reports the tick of the last keyboard *or* mouse event, system-wide, with no
key values and no window context. It cannot tell typing from clicking, and
this module does not claim it can. What it answers honestly is "has anyone
touched this machine recently", which is what BUILD_SPEC's trigger actually
needs stopped: a proactive message arriving while the user is visibly, if
not necessarily by keyboard, mid-task.
"""

from __future__ import annotations

import structlog

log = structlog.get_logger(__name__)

#: BUILD_SPEC's own number for what counts as "still working" — an idle gap
#: shorter than this reads as the same uninterrupted stretch it names.
RECENT_ACTIVITY_S = 20 * 60.0


def _covers_monitor(
    window_rect: tuple[int, int, int, int], monitor_rect: tuple[int, int, int, int]
) -> bool:
    """The comparison alone, pulled out so it can be unit-tested without
    mocking three Win32 modules — the wrapper below is verified live
    instead, the same treatment this project already gives its other
    OS-integration code (CLAUDE.md: the overlay's window flags, "verified
    via GetWindowLong")."""
    return tuple(window_rect) == tuple(monitor_rect)


def is_fullscreen() -> bool:
    """The foreground window covers its entire monitor — a game, a video, a
    presentation. Read-only; never raises past this function."""
    try:
        import win32api
        import win32con
        import win32gui

        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return False
        window_rect = win32gui.GetWindowRect(hwnd)
        monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        monitor_rect = win32api.GetMonitorInfo(monitor)["Monitor"]
        return _covers_monitor(window_rect, monitor_rect)
    except Exception:  # noqa: BLE001 — a failed check is not evidence of focus
        log.warning("focus.fullscreen_check_failed", exc_info=True)
        return False


def seconds_since_last_input() -> float | None:
    """How long since any keyboard or mouse event, system-wide. `None` when
    the check itself fails — callers treat that as "unknown", not "idle"."""
    try:
        import win32api

        last_input_tick = int(win32api.GetLastInputInfo())
        now_tick = int(win32api.GetTickCount())
        return max(0.0, (now_tick - last_input_tick) / 1000.0)
    except Exception:  # noqa: BLE001
        log.warning("focus.last_input_check_failed", exc_info=True)
        return None


def is_actively_working() -> bool:
    """Fullscreen, or touched the machine within the last
    `RECENT_ACTIVITY_S` — either one is reason enough to stay quiet. An
    unknown last-input reading (the check failed) is read as "not actively
    working" rather than blocking every proactive message forever on a
    broken probe.
    """
    if is_fullscreen():
        return True
    idle_for = seconds_since_last_input()
    return idle_for is not None and idle_for < RECENT_ACTIVITY_S
