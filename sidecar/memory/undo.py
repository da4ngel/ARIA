"""One timeline of things that can be taken back.

`organize_folder` has had a real undo since Phase 4 and nothing else did. This
is the general form — record on the way out, reverse on request — and the hard
part was never the table. It was that most tools kept nothing that *could* be
reversed: `write_file` overwrote without reading, and `delete_file` unlinked.
Those changed; this stores what they now keep.

**Recording is best-effort and reversing is not.** A failure to write a row must
never fail the operation the user asked for — losing the undo is a much smaller
harm than losing the action. A failure to *reverse* is reported in full, because
somebody is standing there expecting their file back.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from sidecar.memory.db import Database

log = structlog.get_logger(__name__)

#: Anything bigger is not copied aside before being overwritten. A backup is
#: worth having; silently consuming a gigabyte of disk to make one is not.
MAX_BACKUP_BYTES = 20 * 1024 * 1024

#: How long a backup is kept. Long enough that "undo that" a day later works,
#: short enough that data/undo/ does not grow without bound.
BACKUP_DAYS = 30


@dataclass(frozen=True)
class UndoEntry:
    id: int
    tool: str
    kind: str
    summary: str
    created_at: str
    undone_at: str | None
    blocked: str | None

    @property
    def undoable(self) -> bool:
        return self.undone_at is None and self.blocked is None

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "tool": self.tool,
            "kind": self.kind,
            "summary": self.summary,
            "created_at": self.created_at,
            "undone_at": self.undone_at,
            "blocked": self.blocked,
            "undoable": self.undoable,
        }


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


async def record(
    db: Database,
    *,
    tool: str,
    kind: str,
    summary: str,
    payload: dict[str, Any],
    session_id: str | None = None,
) -> int | None:
    """Note that something reversible happened. **Never raises.**"""

    def _write(conn: sqlite3.Connection) -> int:
        with conn:
            cursor = conn.execute(
                "INSERT INTO undo_log (tool, kind, summary, payload, session_id, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (tool, kind, summary, json.dumps(payload), session_id, _now()),
            )
        return int(cursor.lastrowid or 0)

    try:
        return await db.run(_write)
    except Exception as exc:  # noqa: BLE001 — an undo row is not worth a turn
        log.warning("undo.record_failed", tool=tool, error=str(exc))
        return None


def _row(record: sqlite3.Row) -> UndoEntry:
    return UndoEntry(
        id=int(record["id"]),
        tool=str(record["tool"]),
        kind=str(record["kind"]),
        summary=str(record["summary"]),
        created_at=str(record["created_at"]),
        undone_at=record["undone_at"],
        blocked=record["blocked"],
    )


async def recent(db: Database, limit: int = 25) -> list[UndoEntry]:
    capped = max(1, min(int(limit), 200))

    def _read(conn: sqlite3.Connection) -> list[UndoEntry]:
        rows = conn.execute(
            "SELECT * FROM undo_log ORDER BY id DESC LIMIT ?", (capped,)
        ).fetchall()
        return [_row(r) for r in rows]

    try:
        return await db.run(_read)
    except Exception as exc:  # noqa: BLE001
        log.warning("undo.read_failed", error=str(exc))
        return []


async def last_undoable(db: Database) -> UndoEntry | None:
    """The most recent thing that can still be taken back."""

    def _read(conn: sqlite3.Connection) -> UndoEntry | None:
        row = conn.execute(
            "SELECT * FROM undo_log WHERE undone_at IS NULL AND blocked IS NULL "
            "ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return _row(row) if row is not None else None

    return await db.run(_read)


async def _claim(db: Database, entry_id: int) -> dict[str, Any] | None:
    """Take the row, if it is still there to take.

    The `undone_at IS NULL` in the WHERE clause is what stops two clicks
    reversing the same operation twice — the second UPDATE matches nothing.
    """

    def _take(conn: sqlite3.Connection) -> dict[str, Any] | None:
        with conn:
            row = conn.execute(
                "SELECT * FROM undo_log WHERE id = ? AND undone_at IS NULL "
                "AND blocked IS NULL",
                (entry_id,),
            ).fetchone()
            if row is None:
                return None
            conn.execute(
                "UPDATE undo_log SET undone_at = ? WHERE id = ? AND undone_at IS NULL",
                (_now(), entry_id),
            )
            return dict(row)

    return await db.run(_take)


async def _release(db: Database, entry_id: int, reason: str) -> None:
    """Hand the row back after a failed reverse, and say why it is stuck.

    Without this a failed undo would look successful: the row is claimed, the
    button disappears, and the file never came back.
    """

    def _write(conn: sqlite3.Connection) -> None:
        with conn:
            conn.execute(
                "UPDATE undo_log SET undone_at = NULL, blocked = ? WHERE id = ?",
                (reason[:300], entry_id),
            )

    await db.run(_write)


async def apply(db: Database, entry_id: int) -> tuple[bool, str]:
    """Reverse one operation. Returns `(ok, what happened)`."""
    claimed = await _claim(db, entry_id)
    if claimed is None:
        return False, "That has already been undone, or cannot be."

    try:
        payload = json.loads(claimed["payload"])
    except json.JSONDecodeError:
        await _release(db, entry_id, "the record could not be read")
        return False, "That record is unreadable, so I cannot reverse it."

    kind = str(claimed["kind"])
    try:
        message = _reverse(kind, payload)
    except Exception as exc:  # noqa: BLE001 — the reason is what the user needs
        await _release(db, entry_id, str(exc))
        log.warning("undo.failed", entry_id=entry_id, kind=kind, error=str(exc))
        return False, f"I could not undo that: {exc}"

    log.info("undo.applied", entry_id=entry_id, kind=kind)
    return True, message


def _reverse(kind: str, payload: dict[str, Any]) -> str:
    """The actual reversal, blocking. Raises with a reason a person can act on."""
    if kind == "move":
        return _reverse_move(Path(payload["source"]), Path(payload["destination"]))
    if kind == "write":
        return _reverse_write(payload)
    if kind == "delete":
        # A recycled file is genuinely still there and genuinely not restorable
        # from here — the shell offers no "undelete this path" call. Saying
        # exactly where it is beats a button that quietly does nothing.
        target = payload.get("path", "the file")
        raise RuntimeError(
            f"{target} went to the Recycle Bin rather than being destroyed, so "
            f"it is recoverable — but only from the Recycle Bin itself, where "
            f"Windows keeps the restore information. Open it and choose Restore."
        )
    if kind == "organize":
        raise RuntimeError(
            "Use the undo_organize tool for a folder tidy-up — it replays the "
            "whole manifest, which is more than this row knows about."
        )
    raise RuntimeError(f"I do not know how to reverse a {kind!r} operation.")


def _reverse_move(source: Path, destination: Path) -> str:
    if not destination.exists():
        raise RuntimeError(f"{destination} is not there any more — it may have moved again.")
    if source.exists():
        raise RuntimeError(
            f"There is already something at {source}, so putting it back would "
            f"overwrite that. Move it out of the way first."
        )
    source.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(destination), str(source))
    return f"Put {source.name} back where it was."


def _reverse_write(payload: dict[str, Any]) -> str:
    target = Path(payload["path"])
    backup = payload.get("backup")

    if backup is None:
        # It created the file, so undoing it means removing it — but only if
        # nobody has touched it since, or an edit somebody made by hand would
        # be thrown away by an undo they thought was safe.
        if not target.exists():
            return f"{target.name} is already gone."
        if payload.get("wrote") is not None and target.read_text(
            encoding="utf-8", errors="replace"
        ) != payload["wrote"]:
            raise RuntimeError(
                f"{target.name} has been changed since, so deleting it now would "
                f"lose those changes. Left alone."
            )
        target.unlink()
        return f"Removed {target.name}, which had not existed before."

    source = Path(backup)
    if not source.exists():
        raise RuntimeError(
            f"The saved copy of {target.name} is no longer in data/undo — "
            f"backups are kept for {BACKUP_DAYS} days."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return f"Restored {target.name} to what it was before."


def save_backup(undo_dir: Path, target: Path) -> str | None:
    """Copy a file aside before it is overwritten. Returns the copy's path.

    Best-effort by design: a file too large, or one that cannot be read, gives
    `None` and the write still happens. The alternative — refusing to write
    because the backup failed — would break a working tool to protect a
    convenience.
    """
    try:
        if not target.is_file():
            return None
        if target.stat().st_size > MAX_BACKUP_BYTES:
            log.info("undo.backup_skipped", path=str(target), reason="too large")
            return None
        undo_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
        copy = undo_dir / f"write-{stamp}-{target.name}"
        shutil.copy2(target, copy)
        return str(copy)
    except Exception as exc:  # noqa: BLE001
        log.warning("undo.backup_failed", path=str(target), error=str(exc))
        return None


def prune_backups(undo_dir: Path, *, days: int = BACKUP_DAYS) -> int:
    """Drop backups past their keep-window. Called from the nightly sweep."""
    if not undo_dir.is_dir():
        return 0
    cutoff = datetime.now(UTC).timestamp() - days * 86400
    removed = 0
    for path in undo_dir.glob("write-*"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
        except OSError:
            continue
    if removed:
        log.info("undo.pruned", removed=removed)
    return removed


__all__ = [
    "BACKUP_DAYS",
    "MAX_BACKUP_BYTES",
    "UndoEntry",
    "apply",
    "last_undoable",
    "prune_backups",
    "recent",
    "record",
    "save_backup",
]
