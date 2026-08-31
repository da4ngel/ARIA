"""Reminders — the ones the user asked for out loud.

Deliberately **not** a `persona/proactivity.py` trigger, and the reason is worth
keeping next to the code. That scheduler drops a candidate when the machine has
been touched in the last 20 minutes, when four proactive messages have already
gone out today, when the last one was under 90 minutes ago, or when a local
model calls it noise — and nothing re-queues what it drops. Every one of those
gates exists to stop *unsolicited* nagging.

"Remind me in 20 minutes" is precisely the case the focus check suppresses, and
a reminder that silently does not arrive is worse than one that was never
offered. So these are rows with a due time and their own loop.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog

from sidecar.memory.db import Database

log = structlog.get_logger(__name__)

#: Nobody means "remind me in three years", and an unbounded value lets one
#: mistyped argument park a row in the table forever.
MAX_HORIZON = timedelta(days=365)

#: A reminder is a sentence, not a document.
MAX_TEXT_CHARS = 500


@dataclass(frozen=True)
class Reminder:
    id: int
    text: str
    due_at: datetime
    created_at: str
    session_id: str | None

    def overdue_by(self, now: datetime) -> timedelta:
        return now - self.due_at


def _stamp(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def parse_due(raw: str) -> datetime | None:
    """An ISO-8601 string into an aware UTC datetime, or None.

    A value with no timezone is read as **local** time, because that is what a
    person means when they say "at 9pm" and it is what the model will emit when
    it turns their words into a timestamp.
    """
    text = raw.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.astimezone()
    return parsed.astimezone(UTC)


async def create(
    db: Database,
    text: str,
    due_at: datetime,
    *,
    session_id: str | None = None,
    now: datetime | None = None,
) -> int:
    moment = (now or datetime.now(UTC)).astimezone(UTC)
    body = text.strip()[:MAX_TEXT_CHARS]
    due = due_at.astimezone(UTC)

    def _write(conn: sqlite3.Connection) -> int:
        with conn:
            cursor = conn.execute(
                "INSERT INTO reminders (text, due_at, created_at, session_id) "
                "VALUES (?, ?, ?, ?)",
                (body, _stamp(due), _stamp(moment), session_id),
            )
        return int(cursor.lastrowid or 0)

    reminder_id = await db.run(_write)
    log.info("reminder.set", reminder_id=reminder_id, due_at=_stamp(due))
    return reminder_id


def _row_to_reminder(row: sqlite3.Row) -> Reminder | None:
    due = parse_due(str(row["due_at"]))
    if due is None:
        return None
    return Reminder(
        id=int(row["id"]),
        text=str(row["text"]),
        due_at=due,
        created_at=str(row["created_at"]),
        session_id=row["session_id"],
    )


async def due(db: Database, *, now: datetime | None = None) -> list[Reminder]:
    """Everything that has come due and not yet been delivered.

    **Includes reminders that came due while ARIA was closed.** Late is the
    normal case for an app that is not always running, and the alternative —
    dropping anything older than some window — throws away exactly the thing
    the user asked for. `MemoryScheduler`'s own principle: a catch-up, not a
    cron fire.
    """
    moment = (now or datetime.now(UTC)).astimezone(UTC)

    def _read(conn: sqlite3.Connection) -> list[sqlite3.Row]:
        return conn.execute(
            "SELECT id, text, due_at, created_at, session_id FROM reminders "
            "WHERE delivered_at IS NULL AND cancelled_at IS NULL AND due_at <= ? "
            "ORDER BY due_at ASC",
            (_stamp(moment),),
        ).fetchall()

    rows = await db.run(_read)
    return [r for r in (_row_to_reminder(row) for row in rows) if r is not None]


async def pending(db: Database, limit: int = 50) -> list[Reminder]:
    """Set, not yet fired, not cancelled — including ones not yet due."""

    def _read(conn: sqlite3.Connection) -> list[sqlite3.Row]:
        return conn.execute(
            "SELECT id, text, due_at, created_at, session_id FROM reminders "
            "WHERE delivered_at IS NULL AND cancelled_at IS NULL "
            "ORDER BY due_at ASC LIMIT ?",
            (max(1, min(int(limit), 200)),),
        ).fetchall()

    rows = await db.run(_read)
    return [r for r in (_row_to_reminder(row) for row in rows) if r is not None]


async def mark_delivered(db: Database, reminder_id: int, *, now: datetime | None = None) -> bool:
    """Stamp it sent. **Both the record and the guard against sending twice.**

    The `delivered_at IS NULL` in the WHERE clause is what makes this safe if
    two ticks ever overlap: the second update matches nothing. Same mechanism
    `sessions.ended_at` gives `close_session`.
    """
    moment = (now or datetime.now(UTC)).astimezone(UTC)

    def _write(conn: sqlite3.Connection) -> bool:
        with conn:
            cursor = conn.execute(
                "UPDATE reminders SET delivered_at = ? "
                "WHERE id = ? AND delivered_at IS NULL",
                (_stamp(moment), reminder_id),
            )
        return cursor.rowcount > 0

    return await db.run(_write)


async def cancel(db: Database, reminder_id: int, *, now: datetime | None = None) -> bool:
    moment = (now or datetime.now(UTC)).astimezone(UTC)

    def _write(conn: sqlite3.Connection) -> bool:
        with conn:
            cursor = conn.execute(
                "UPDATE reminders SET cancelled_at = ? "
                "WHERE id = ? AND delivered_at IS NULL AND cancelled_at IS NULL",
                (_stamp(moment), reminder_id),
            )
        return cursor.rowcount > 0

    return await db.run(_write)


def as_dict(reminder: Reminder, *, now: datetime | None = None) -> dict[str, Any]:
    moment = (now or datetime.now(UTC)).astimezone(UTC)
    return {
        "id": reminder.id,
        "text": reminder.text,
        "due_at": _stamp(reminder.due_at),
        "created_at": reminder.created_at,
        "overdue": reminder.due_at <= moment,
    }
