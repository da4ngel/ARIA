"""The clock behind memory: idle sweeps, and reflection at 3am (§8.3).

§8.3 names APScheduler. This does not use it, on the same grounds every other
deferred dependency here was reconsidered on: the sidecar already has this
pattern three times over (`providers/connectivity.py`, `memory/indexer.py`,
`ConversationService._wait_for_idle`), it is one daily job, and one fewer
dependency tree is one fewer thing to survive PyInstaller (§2.3).

**It is a catch-up, not a cron fire.** The question asked each tick is "has a
reflection happened since the most recent 3am?", not "is it 3am now". A
personal machine is asleep at 3am most nights, and a scheduler that only fires
on the exact minute would mean she never learns anything. Waking at 9am runs
last night's reflection immediately.

Everything is injected — clock, sleep, and the two jobs — so the tests drive
`tick()` directly across a whole simulated week without sleeping once.
"""

from __future__ import annotations

import asyncio
import contextlib
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from sidecar.memory.reflection import ReflectionReport

log = structlog.get_logger(__name__)

#: Five minutes. The sweep is the only thing that needs to be timely, and it is
#: looking for conversations idle for thirty.
DEFAULT_TICK_S = 300.0
DEFAULT_HOUR = 3

#: Enough new conversation to be worth a model call between nightly runs.
DEFAULT_MIN_UNREFLECTED = 4
#: And no more often than this. **Once a day was measurably not enough**: the
#: `facts` table sat empty through a fortnight of real use, because one daily
#: slot on a machine that runs an hour at a time is one slot that is usually
#: spent on an empty window. Reflection is a background local call behind
#: `is_busy`, so the cost of running it more often is small and the cost of
#: never running it is a memory that learns nothing.
DEFAULT_MIN_GAP = timedelta(minutes=30)


def most_recent_boundary(now: datetime, hour: int) -> datetime:
    """The last time the clock passed `hour`:00, today or yesterday."""
    today = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    return today if now >= today else today - timedelta(days=1)


class MemoryScheduler:
    """Sweeps idle sessions, and runs reflection once per day."""

    def __init__(
        self,
        *,
        on_sweep: Callable[[], Awaitable[int]],
        on_reflect: Callable[[], Awaitable[ReflectionReport]],
        last_reflection: Callable[[], Awaitable[datetime | None]],
        unreflected: Callable[[], Awaitable[int]] | None = None,
        is_busy: Callable[[], bool] | None = None,
        hour: int = DEFAULT_HOUR,
        tick_s: float = DEFAULT_TICK_S,
        min_unreflected: int = DEFAULT_MIN_UNREFLECTED,
        min_gap: timedelta = DEFAULT_MIN_GAP,
        clock: Callable[[], datetime] = lambda: datetime.now().astimezone(),
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._on_sweep = on_sweep
        self._on_reflect = on_reflect
        self._last_reflection = last_reflection
        self._unreflected = unreflected
        self._is_busy = is_busy or (lambda: False)
        self._hour = hour
        self._min_unreflected = min_unreflected
        self._min_gap = min_gap
        self._tick_s = tick_s
        self._clock = clock
        self._sleep = sleep
        self._task: asyncio.Task[None] | None = None

    async def tick(self) -> None:
        """One pass. Never raises — a scheduler that dies stops everything."""
        try:
            await self._on_sweep()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            log.warning("memory.sweep_failed", error=str(exc))

        if self._is_busy():
            # A second model call while she is mid-answer costs the turn the
            # user is waiting on. There is another tick in five minutes.
            return

        try:
            if await self._reflection_due():
                report = await self._on_reflect()
                log.info(
                    "reflection.scheduled_run",
                    model=report.model,
                    inserted=report.inserted,
                    error=report.error,
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            log.warning("reflection.tick_failed", error=str(exc))

    async def _reflection_due(self) -> bool:
        """Two reasons to reflect: the night has turned, or a conversation has.

        The nightly boundary alone is what §8.3 asks for and it is not enough on
        its own — see `DEFAULT_MIN_GAP`. The second reason is the one that makes
        her learn from a conversation on the day it happened.
        """
        now = self._clock()
        boundary = most_recent_boundary(now, self._hour)
        last = await self._last_reflection()
        if last is None:
            return True
        # Both sides need the same awareness or the comparison raises. The
        # stored stamp is UTC; the boundary follows the local clock, which is
        # what "3am" means to the person asleep at it.
        if last.tzinfo is None:
            last = last.astimezone()
        if last < boundary.astimezone(last.tzinfo):
            return True

        if self._unreflected is None or now - last.astimezone(now.tzinfo) < self._min_gap:
            return False
        return await self._unreflected() >= self._min_unreflected

    async def _loop(self) -> None:
        # Work first, then sleep. That ordering is what makes a sweep run
        # seconds after startup, which is how a session abandoned by killing
        # the app ever gets closed.
        while True:
            await self.tick()
            await self._sleep(self._tick_s)

    def start(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._loop())
        log.info("memory.scheduler_started", hour=self._hour, tick_s=self._tick_s)

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task
        self._task = None
