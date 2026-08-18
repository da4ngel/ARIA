"""The clock behind memory.

Everything is driven through `tick()` with an injected clock, so a whole
simulated week runs in milliseconds. **No test here sleeps** — that is the
reason the scheduler takes `clock` and `sleep` as arguments at all.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest

from sidecar.memory.reflection import ReflectionReport
from sidecar.memory.scheduler import MemoryScheduler, most_recent_boundary


class Recorder:
    """Stands in for the two jobs, and remembers when it was last reflected."""

    def __init__(self, last: datetime | None = None, unread: int = 0) -> None:
        self.sweeps = 0
        self.reflections = 0
        self.last = last
        self.unread = unread

    async def sweep(self) -> int:
        self.sweeps += 1
        return 0

    async def reflect(self) -> ReflectionReport:
        self.reflections += 1
        return ReflectionReport()

    async def last_run(self) -> datetime | None:
        return self.last

    async def unreflected(self) -> int:
        return self.unread


def _at(hour: int, minute: int = 0, day: int = 10) -> datetime:
    return datetime(2026, 8, day, hour, minute, tzinfo=UTC)


def _scheduler(
    recorder: Recorder, now: datetime, **kwargs: object
) -> MemoryScheduler:
    return MemoryScheduler(
        on_sweep=recorder.sweep,
        on_reflect=recorder.reflect,
        last_reflection=recorder.last_run,
        clock=lambda: now,
        **kwargs,  # type: ignore[arg-type]
    )


# ── the boundary ──────────────────────────────────────────────────────


def test_the_boundary_is_todays_3am_once_it_has_passed() -> None:
    assert most_recent_boundary(_at(9, 30), 3) == _at(3)


def test_before_3am_the_boundary_is_yesterdays() -> None:
    assert most_recent_boundary(_at(1, 30), 3) == _at(3, day=9)


# ── when reflection runs ──────────────────────────────────────────────


@pytest.mark.anyio
async def test_it_does_not_reflect_before_the_hour() -> None:
    recorder = Recorder(last=_at(3, 5, day=9))
    await _scheduler(recorder, _at(2, 59)).tick()

    assert recorder.reflections == 0
    # The sweep runs regardless — it is not on the daily clock.
    assert recorder.sweeps == 1


@pytest.mark.anyio
async def test_it_reflects_once_the_hour_has_passed() -> None:
    recorder = Recorder(last=_at(3, 5, day=9))
    await _scheduler(recorder, _at(3, 1)).tick()

    assert recorder.reflections == 1


@pytest.mark.anyio
async def test_it_does_not_reflect_twice_in_one_day() -> None:
    recorder = Recorder(last=_at(3, 5, day=9))
    scheduler = _scheduler(recorder, _at(3, 1))
    await scheduler.tick()
    recorder.last = _at(3, 1)

    later = _scheduler(recorder, _at(3, 5))
    await later.tick()

    assert recorder.reflections == 1


@pytest.mark.anyio
async def test_a_machine_asleep_at_3am_reflects_when_it_wakes() -> None:
    """The whole reason this is a catch-up and not a cron fire. A personal
    machine is asleep at 3am most nights."""
    recorder = Recorder(last=_at(3, 5, day=9))
    await _scheduler(recorder, _at(9, 0)).tick()

    assert recorder.reflections == 1


@pytest.mark.anyio
async def test_it_reflects_on_a_first_ever_run() -> None:
    recorder = Recorder(last=None)
    await _scheduler(recorder, _at(14, 0)).tick()

    assert recorder.reflections == 1


@pytest.mark.anyio
async def test_a_whole_week_produces_one_reflection_a_day() -> None:
    """Four ticks a day for a week, and exactly seven reflections come out.

    `last` starts just after the previous day's boundary, so this measures the
    steady state rather than the first-ever run — which reflects immediately
    and is covered by its own test above.
    """
    before = 0
    recorder = Recorder(last=_at(3, 5, day=9))
    for day in range(10, 17):
        for hour in (1, 4, 11, 20):
            await _scheduler(recorder, _at(hour, day=day)).tick()
            if recorder.reflections > before:
                before = recorder.reflections
                recorder.last = _at(hour, day=day)

    assert recorder.reflections == 7


# ── standing down ─────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_it_defers_while_she_is_answering() -> None:
    """A second model call mid-turn costs the answer the user is waiting on.
    There is another tick in five minutes."""
    recorder = Recorder(last=None)
    scheduler = _scheduler(recorder, _at(9, 0), is_busy=lambda: True)

    await scheduler.tick()

    assert recorder.reflections == 0
    # The sweep already ran; it is cheap and does its own busy check.
    assert recorder.sweeps == 1


@pytest.mark.anyio
async def test_a_failing_sweep_does_not_stop_reflection() -> None:
    """A scheduler that dies on one bad tick stops everything, silently."""

    async def broken() -> int:
        raise RuntimeError("the database went away")

    recorder = Recorder(last=None)
    scheduler = MemoryScheduler(
        on_sweep=broken,
        on_reflect=recorder.reflect,
        last_reflection=recorder.last_run,
        clock=lambda: _at(9, 0),
    )

    await scheduler.tick()

    assert recorder.reflections == 1


@pytest.mark.anyio
async def test_a_failing_reflection_does_not_kill_the_loop() -> None:
    async def broken() -> ReflectionReport:
        raise RuntimeError("Ollama fell over")

    recorder = Recorder(last=None)
    scheduler = MemoryScheduler(
        on_sweep=recorder.sweep,
        on_reflect=broken,
        last_reflection=recorder.last_run,
        clock=lambda: _at(9, 0),
    )

    await scheduler.tick()  # must not raise
    await scheduler.tick()

    assert recorder.sweeps == 2


# ── the loop ──────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_the_loop_sweeps_before_it_sleeps() -> None:
    """Work-then-sleep is what makes a sweep run seconds after startup, which
    is how a session abandoned by killing the app ever gets closed."""
    recorder = Recorder(last=_at(3, 5, day=9))
    slept = asyncio.Event()

    async def sleep(_seconds: float) -> None:
        slept.set()
        await asyncio.sleep(3600)

    scheduler = MemoryScheduler(
        on_sweep=recorder.sweep,
        on_reflect=recorder.reflect,
        last_reflection=recorder.last_run,
        clock=lambda: _at(2, 0),
        sleep=sleep,
    )

    scheduler.start()
    await asyncio.wait_for(slept.wait(), timeout=1.0)
    await scheduler.stop()

    assert recorder.sweeps == 1


@pytest.mark.anyio
async def test_stop_is_safe_before_start_and_twice() -> None:
    recorder = Recorder()
    scheduler = _scheduler(recorder, _at(2, 0))

    await scheduler.stop()
    scheduler.start()
    scheduler.start()  # idempotent
    await scheduler.stop()
    await scheduler.stop()


# ── learning between nights ───────────────────────────────────────────


@pytest.mark.anyio
async def test_a_finished_conversation_is_learned_from_before_3am() -> None:
    """Once a day was measurably not enough — `facts` stayed empty for a
    fortnight of real use, because the one daily slot is usually spent on an
    empty window by a machine that runs an hour at a time."""
    recorder = Recorder(last=_at(3, 5), unread=8)
    scheduler = _scheduler(recorder, _at(11, 0), unreflected=recorder.unreflected)

    await scheduler.tick()

    assert recorder.reflections == 1


@pytest.mark.anyio
async def test_a_handful_of_messages_does_not_earn_a_model_call() -> None:
    recorder = Recorder(last=_at(3, 5), unread=2)
    scheduler = _scheduler(recorder, _at(11, 0), unreflected=recorder.unreflected)

    await scheduler.tick()

    assert recorder.reflections == 0


@pytest.mark.anyio
async def test_it_does_not_reflect_twice_within_the_gap() -> None:
    """The nightly boundary has passed and there is plenty unread, but a
    reflection ran ten minutes ago. Waiting is the whole point of the gap."""
    recorder = Recorder(last=_at(10, 50), unread=40)
    scheduler = _scheduler(recorder, _at(11, 0), unreflected=recorder.unreflected)

    await scheduler.tick()

    assert recorder.reflections == 0


@pytest.mark.anyio
async def test_without_an_unreflected_source_only_the_night_triggers() -> None:
    """`unreflected` is optional, and omitting it must not make her reflect on
    every tick — that would be a model call every five minutes."""
    recorder = Recorder(last=_at(3, 5))
    scheduler = _scheduler(recorder, _at(23, 0))

    await scheduler.tick()

    assert recorder.reflections == 0
