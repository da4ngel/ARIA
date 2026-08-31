"""The clipboard ring — what was copied, newest first.

**Everything copied on this machine lands in this table.** `core/clipboard_watcher.py`
refuses what looks like a credential before calling `remember` here, and that
filter is a reduction in exposure rather than a guarantee: it will miss things,
and `data/aria.db` is not a file to hand to anyone afterwards. That sentence
belongs at the top of this module rather than buried, and the panel repeats it
on screen.

Plain module functions over `Database.run`, the shape `memory/study.py` and
`memory/procedures.py` already use — no class, because there is no state to
hold between calls.
"""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import structlog

from sidecar.memory.db import Database

log = structlog.get_logger(__name__)

#: How many entries the ring keeps. Trimmed oldest-first on every write, so the
#: table cannot grow without bound on a machine that is left running.
MAX_ENTRIES = 500

#: A single entry longer than this is not something anyone pastes from a
#: history; it is a document that happened to go through the clipboard. Kept out
#: so one copy of a whole file cannot dominate the table.
MAX_CHARS = 20_000


@dataclass(frozen=True)
class ClipEntry:
    id: int
    content: str
    chars: int
    copied_at: str
    source: str | None


def _now() -> str:
    """A display stamp. **Deliberately not the ordering key** — see `remember`."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def digest_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


async def remember(db: Database, content: str, *, source: str | None = None) -> int | None:
    """Store one copied string. Returns its row id, or None if it was not kept.

    **Re-copying the same text moves the existing row rather than adding a
    second one.** A history of fifty entries should be fifty different things,
    not one thing copied fifty times — which is exactly what happens when
    somebody copies the same snippet repeatedly while working.

    **"Moves" means delete-then-insert, so it gets a fresh id, and `id` is what
    the ring is ordered by.** The obvious implementation — UPDATE the row's
    `copied_at` — cannot work here: Windows' system clock ticks about every
    15.6ms, so two copies in quick succession get a byte-identical timestamp
    even at microsecond precision (measured, not assumed). Ordering on a
    timestamp that can tie leaves SQLite free to return either, and the `id`
    tie-break makes it actively wrong, because a re-copied row keeps its
    original low id and sorts *behind* newer entries. A monotonic integer has
    none of those problems.
    """
    text = content.strip()
    if not text or len(text) > MAX_CHARS:
        return None

    stamp = _now()
    fingerprint = digest_of(text)

    def _write(conn: sqlite3.Connection) -> int | None:
        with conn:
            # Delete rather than update, so the re-inserted row takes a new
            # id and lands at the front. See the docstring.
            conn.execute(
                "DELETE FROM clipboard_history WHERE digest = ?", (fingerprint,)
            )
            cursor = conn.execute(
                "INSERT INTO clipboard_history (content, chars, digest, copied_at, source) "
                "VALUES (?, ?, ?, ?, ?)",
                (text, len(text), fingerprint, stamp, source),
            )
            conn.execute(
                "DELETE FROM clipboard_history WHERE id NOT IN ("
                "  SELECT id FROM clipboard_history ORDER BY id DESC LIMIT ?"
                ")",
                (MAX_ENTRIES,),
            )
            return int(cursor.lastrowid or 0)

    return await db.run(_write)


async def recent(db: Database, limit: int = 20) -> list[ClipEntry]:
    """Newest first. `limit` is clamped, so a model asking for 10,000 gets 200."""
    capped = max(1, min(int(limit), 200))

    def _read(conn: sqlite3.Connection) -> list[ClipEntry]:
        rows = conn.execute(
            "SELECT id, content, chars, copied_at, source FROM clipboard_history "
            "ORDER BY id DESC LIMIT ?",
            (capped,),
        ).fetchall()
        return [
            ClipEntry(
                id=int(r["id"]),
                content=str(r["content"]),
                chars=int(r["chars"]),
                copied_at=str(r["copied_at"]),
                source=r["source"],
            )
            for r in rows
        ]

    return await db.run(_read)


async def get(db: Database, entry_id: int) -> ClipEntry | None:
    entries = [e for e in await recent(db, MAX_ENTRIES) if e.id == entry_id]
    return entries[0] if entries else None


async def forget(db: Database, entry_id: int) -> bool:
    def _delete(conn: sqlite3.Connection) -> bool:
        with conn:
            cursor = conn.execute(
                "DELETE FROM clipboard_history WHERE id = ?", (entry_id,)
            )
        return cursor.rowcount > 0

    return await db.run(_delete)


async def clear(db: Database) -> int:
    """Empty the ring. The panel's "forget everything" button."""

    def _clear(conn: sqlite3.Connection) -> int:
        with conn:
            cursor = conn.execute("DELETE FROM clipboard_history")
        return cursor.rowcount

    removed = await db.run(_clear)
    log.info("clipboard.cleared", removed=removed)
    return removed


def as_dict(entry: ClipEntry) -> dict[str, Any]:
    return {
        "id": entry.id,
        "content": entry.content,
        "chars": entry.chars,
        "copied_at": entry.copied_at,
        "source": entry.source,
    }
