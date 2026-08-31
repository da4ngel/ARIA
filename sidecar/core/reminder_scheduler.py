"""Deliver reminders when they come due, and do not let anything stop them.

**This scheduler exists because `ProactivityScheduler` would drop these.** Its
gates run in this order and each returns silently: `is_actively_working()`, then
a 4-a-day budget with 90 minutes between messages, then a local model asked
whether the message is noise, then only `candidates[0]` survives — and nothing
re-queues what was dropped.

Every one of those is right for an *unsolicited* message. None of them is right
for one the user asked for out loud. `focus.RECENT_ACTIVITY_S` is 20 minutes, so
"remind me in 20 minutes" is the exact case that check suppresses; and a
reminder that quietly does not arrive is worse than a reminder never offered.

So this loop has no focus check, no budget and no self-check. What it does have
is a 30-second tick, because five minutes is too coarse for "in 20 minutes", and
delivery that stamps `delivered_at` in the same step so a reminder cannot be
sent twice.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

import structlog

from sidecar.memory import reminders as store
from sidecar.memory.db import Database

log = structlog.get_logger(__name__)

#: Half a minute. The tick is one indexed SELECT against a partial index over
#: rows that are almost always zero in number, so this is close to free.
TICK_S = 30.0

#: Past this, the delivery says how late it is. Under it, saying "(2 minutes
#: late)" is noise about a delay nobody noticed.
LATE_AFTER = timedelta(minutes=2)


def describe_delay(late_by: timedelta) -> str:
    """How overdue a reminder is, in words, or "" when it is on time.

    **Said out loud because the alternative is a lie by omission.** If ARIA was
    closed for two days, delivering "call the bank" with no acknowledgement that
    it was due on Tuesday reads as though it is due now.
    """
    if late_by < LATE_AFTER:
        return ""
    minutes = int(late_by.total_seconds() // 60)
    if minutes < 60:
        return f"{minutes} minutes late"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} late"
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} late"


def compose(text: str, late_by: timedelta) -> str:
    delay = describe_delay(late_by)
    return f"Reminder ({delay}): {text}" if delay else f"Reminder: {text}"


class ReminderScheduler:
    """Fires due reminders. Clock and sleep injected; no test sleeps."""

    def __init__(
        self,
        *,
        db: Database,
        deliver: Callable[[str], Awaitable[object]],
        tick_s: float = TICK_S,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        sleep: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        self._db = db
        self._deliver = deliver
        self._tick_s = tick_s
        self._clock = clock
        self._sleep = sleep or asyncio.sleep
        self._task: asyncio.Task[None] | None = None

    async def tick(self) -> int:
        """One pass. Returns how many were delivered. Never raises."""
        try:
            return await self._tick_once()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — a dead loop is the worst outcome
            log.warning("reminder.tick_failed", error=str(exc))
            return 0

    async def _tick_once(self) -> int:
        now = self._clock().astimezone(UTC)
        pending = await store.due(self._db, now=now)
        if not pending:
            return 0

        sent = 0
        for reminder in pending:
            # **Claim it before delivering.** `mark_delivered` only matches rows
            # where `delivered_at IS NULL`, so if a tick ever overlaps its
            # predecessor the second one loses the race and sends nothing.
            if not await store.mark_delivered(self._db, reminder.id, now=now):
                continue
            try:
                await self._deliver(compose(reminder.text, reminder.overdue_by(now)))
            except Exception as exc:  # noqa: BLE001
                # Deliberately left marked delivered. A reminder that failed to
                # send and stays pending would retry every 30 seconds forever,
                # which is a far worse failure than one missed message.
                log.warning(
                    "reminder.deliver_failed", reminder_id=reminder.id, error=str(exc)
                )
                continue
            sent += 1
            log.info("reminder.delivered", reminder_id=reminder.id)
        return sent

    async def _loop(self) -> None:
        while True:
            await self.tick()
            await self._sleep(self._tick_s)

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._loop(), name="reminders")
            log.info("reminder.scheduler_started", tick_s=self._tick_s)

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None


__all__ = ["LATE_AFTER", "TICK_S", "ReminderScheduler", "compose", "describe_delay"]
