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
    """Writes to `tool_log`. Satisfies `tools.permissions.Journal`."""

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
                       error, duration_ms, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    row,
                )

        await self._db.run(_insert)
