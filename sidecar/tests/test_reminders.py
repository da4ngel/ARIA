"""Reminders, and the gates they deliberately do not have.

The load-bearing property is negative: `ReminderScheduler` must fire **while the
user is at the machine**, because `ProactivityScheduler` would not. Its focus
check suppresses delivery for 20 minutes after any keypress, which is precisely
the window "remind me in 20 minutes" lands in.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sidecar.core.reminder_scheduler import ReminderScheduler, compose, describe_delay
from sidecar.memory import reminders as store
from sidecar.memory.db import Database

NOW = datetime(2026, 8, 24, 12, 0, tzinfo=UTC)


class _Deliveries:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def __call__(self, text: str) -> None:
        self.sent.append(text)


def _scheduler(
    database: Database, deliver: _Deliveries, *, now: datetime = NOW
) -> ReminderScheduler:
    return ReminderScheduler(db=database, deliver=deliver, clock=lambda: now)


# ── the store ─────────────────────────────────────────────────────────


async def test_a_reminder_is_not_due_before_its_time(database: Database) -> None:
    await store.create(database, "call the bank", NOW + timedelta(minutes=20), now=NOW)
    assert await store.due(database, now=NOW) == []
    assert len(await store.due(database, now=NOW + timedelta(minutes=21))) == 1


async def test_pending_includes_reminders_that_are_not_due_yet(database: Database) -> None:
    await store.create(database, "later", NOW + timedelta(hours=5), now=NOW)
    assert [r.text for r in await store.pending(database)] == ["later"]


async def test_delivering_twice_is_refused(database: Database) -> None:
    """**The guard, not merely the record.** Two overlapping ticks must not
    send the same reminder twice; the second UPDATE matches nothing."""
    reminder_id = await store.create(database, "once", NOW, now=NOW)
    assert await store.mark_delivered(database, reminder_id, now=NOW)
    assert not await store.mark_delivered(database, reminder_id, now=NOW)


async def test_a_delivered_reminder_stops_being_due(database: Database) -> None:
    reminder_id = await store.create(database, "done", NOW, now=NOW)
    await store.mark_delivered(database, reminder_id, now=NOW)
    assert await store.due(database, now=NOW) == []


async def test_a_cancelled_reminder_never_fires(database: Database) -> None:
    reminder_id = await store.create(database, "never mind", NOW, now=NOW)
    assert await store.cancel(database, reminder_id, now=NOW)
    assert await store.due(database, now=NOW) == []
    # Cancelling twice is not an error worth raising, but it is not a success.
    assert not await store.cancel(database, reminder_id, now=NOW)


async def test_a_naive_timestamp_is_read_as_local_time() -> None:
    """What a person means by "at 9pm", and what the model will emit."""
    parsed = store.parse_due("2026-08-25T21:00")
    assert parsed is not None
    assert parsed.tzinfo is not None
    assert parsed == datetime(2026, 8, 25, 21, 0).astimezone().astimezone(UTC)


async def test_an_unparseable_time_is_none_rather_than_an_exception() -> None:
    assert store.parse_due("next tuesday-ish") is None


# ── the scheduler ─────────────────────────────────────────────────────


async def test_a_due_reminder_is_delivered(database: Database) -> None:
    await store.create(database, "check the oven", NOW - timedelta(seconds=1), now=NOW)
    deliveries = _Deliveries()
    assert await _scheduler(database, deliveries).tick() == 1
    assert deliveries.sent == ["Reminder: check the oven"]


async def test_it_fires_while_the_machine_is_in_use(database: Database) -> None:
    """**The whole reason this is not a proactivity trigger.**

    `ProactivityScheduler` consults `is_actively_working()` before anything
    else, and `focus.RECENT_ACTIVITY_S` is 20 minutes — so a reminder set for
    20 minutes' time would be dropped by the very act of the user being there
    to set it. This scheduler has no such check, and this test is what fails if
    one is ever added.
    """
    import inspect

    # The *tick body*, not the module — the docstring above explains these
    # gates at length and a naive source scan would match its own prose.
    tick = inspect.getsource(ReminderScheduler._tick_once)  # noqa: SLF001
    assert "is_actively_working" not in tick
    assert "self_check" not in tick
    # And nothing can inject one: there is no parameter to pass it through.
    accepts = set(inspect.signature(ReminderScheduler.__init__).parameters)
    assert "is_actively_working" not in accepts
    assert "self_check" not in accepts

    await store.create(database, "still fires", NOW, now=NOW)
    deliveries = _Deliveries()
    assert await _scheduler(database, deliveries).tick() == 1


async def test_a_reminder_is_delivered_once_across_repeated_ticks(
    database: Database,
) -> None:
    await store.create(database, "only once", NOW, now=NOW)
    deliveries = _Deliveries()
    scheduler = _scheduler(database, deliveries)
    await scheduler.tick()
    await scheduler.tick()
    await scheduler.tick()
    assert deliveries.sent == ["Reminder: only once"]


async def test_a_reminder_missed_while_closed_still_fires_and_says_it_is_late(
    database: Database,
) -> None:
    """A catch-up, not a cron fire — `MemoryScheduler`'s own principle.

    Dropping anything older than a window would throw away exactly the thing
    the user asked for, and delivering it silently would read as though it were
    due now.
    """
    await store.create(database, "bin day", NOW - timedelta(days=2), now=NOW)
    deliveries = _Deliveries()
    await _scheduler(database, deliveries).tick()
    assert deliveries.sent == ["Reminder (2 days late): bin day"]


async def test_a_failed_delivery_is_not_retried_forever(database: Database) -> None:
    """A reminder that cannot be sent must not re-attempt every 30 seconds."""

    async def _broken(_text: str) -> None:
        raise RuntimeError("bus is down")

    await store.create(database, "doomed", NOW, now=NOW)
    scheduler = ReminderScheduler(db=database, deliver=_broken, clock=lambda: NOW)
    assert await scheduler.tick() == 0
    assert await scheduler.tick() == 0
    assert await store.due(database, now=NOW) == []


async def test_a_tick_never_raises(database: Database) -> None:
    class _Exploding:
        async def run(self, _fn: object) -> None:
            raise sqlite_error()

    def sqlite_error() -> Exception:
        return RuntimeError("database is locked")

    scheduler = ReminderScheduler(db=_Exploding(), deliver=_Deliveries(), clock=lambda: NOW)  # type: ignore[arg-type]
    assert await scheduler.tick() == 0


# ── wording ───────────────────────────────────────────────────────────


def test_a_reminder_on_time_says_nothing_about_delay() -> None:
    assert describe_delay(timedelta(seconds=30)) == ""
    assert compose("water the plants", timedelta(seconds=5)) == "Reminder: water the plants"


def test_delay_is_described_in_the_largest_sensible_unit() -> None:
    assert describe_delay(timedelta(minutes=17)) == "17 minutes late"
    assert describe_delay(timedelta(hours=1)) == "1 hour late"
    assert describe_delay(timedelta(hours=5)) == "5 hours late"
    assert describe_delay(timedelta(days=1, hours=3)) == "1 day late"
