"""Where every tool call is recorded (BUILD_SPEC §7.3, CLAUDE.md rule 6).

Append-only and deliberately dumb. The one property worth stating is that a
*denied* call is written too — an audit trail that records only what succeeded
answers the wrong question, and "what did it try to do" is the question you
actually have at 2am.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from typing import Any

import structlog

from sidecar.memory.db import Database

log = structlog.get_logger(__name__)


class ToolJournal:
    """Writes `tool_log`, and — since 2026-08-24 — reads it.

    **It was write-only for eight phases.** Four modules grew raw SQL against
    this table (`episodic`, `procedures`, `affect`, `proactivity`) because
    there was nowhere else to ask, and nothing anywhere could answer "what did
    she just do" — the question every incident write-up in CLAUDE.md has had to
    reconstruct by hand from structlog.

    Satisfies `tools.permissions.Journal`, which declares only `write`.
    """

    def __init__(self, db: Database) -> None:
        self._db = db

    async def write(self, entry: dict[str, Any]) -> None:
        row = (
            entry["call_id"],
            entry.get("session_id"),
            entry["tool"],
            entry["args"],
            entry["tier"],
            entry.get("approved"),
            entry.get("ok"),
            entry.get("error"),
            entry.get("duration_ms"),
            entry.get("approved_by"),
            datetime.now(UTC).isoformat(),
        )

        def _insert(conn: sqlite3.Connection) -> None:
            # `with conn` is the commit. Python's sqlite3 opens an implicit
            # transaction, and without this the row is visible in-process and
            # gone on restart — which is exactly how the session titles were
            # lost once already.
            with conn:
                conn.execute(
                    """
                    INSERT INTO tool_log
                      (call_id, session_id, tool, args, tier, approved, ok,
                       error, duration_ms, approved_by, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    row,
                )

        await self._db.run(_insert)

    async def last(self, session_id: str | None = None) -> dict[str, Any] | None:
        """The most recent call, optionally within one session.

        Ordered by `id`, not `created_at`: two calls inside the same second are
        routine in an agent loop, and a timestamp tie makes SQLite free to
        return either. `study.latest_subject_id` learned this the hard way.
        """

        def _query(conn: sqlite3.Connection) -> dict[str, Any] | None:
            if session_id is None:
                row = conn.execute(
                    "SELECT * FROM tool_log ORDER BY id DESC LIMIT 1"
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM tool_log WHERE session_id = ? ORDER BY id DESC LIMIT 1",
                    (session_id,),
                ).fetchone()
            return dict(row) if row is not None else None

        try:
            return await self._db.run(_query)
        except Exception as exc:  # noqa: BLE001 — a read must not break a turn
            log.warning("tool_log.read_failed", error=str(exc))
            return None

    async def recent(
        self, limit: int = 20, session_id: str | None = None
    ) -> list[dict[str, Any]]:
        """The last few calls, newest first."""
        capped = max(1, min(int(limit), 200))

        def _query(conn: sqlite3.Connection) -> list[dict[str, Any]]:
            if session_id is None:
                rows = conn.execute(
                    "SELECT * FROM tool_log ORDER BY id DESC LIMIT ?", (capped,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM tool_log WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                    (session_id, capped),
                ).fetchall()
            return [dict(r) for r in rows]

        try:
            return await self._db.run(_query)
        except Exception as exc:  # noqa: BLE001
            log.warning("tool_log.read_failed", error=str(exc))
            return []
