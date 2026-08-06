"""Sessions and messages — the durable conversation (BUILD_SPEC §7.3).

This is what makes BUILD_SPEC §3's invariant real: kill the Electron window and
the conversation survives, because it was never in the renderer.

Not named in §5, which lists memory/{episodic,semantic,procedural}.py — those
are Phase 5 concepts built *on top of* raw turns. This module is the raw turns.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime

import structlog
from pydantic import BaseModel

from sidecar.memory.db import Database
from sidecar.providers.base import Role

log = structlog.get_logger(__name__)


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class StoredMessage(BaseModel):
    """A row from `messages`, as the UI and context assembly see it."""

    id: int
    session_id: str
    role: Role
    content: str
    route: str | None = None
    latency_ms: int | None = None
    created_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> StoredMessage:
        return cls(
            id=row["id"],
            session_id=row["session_id"],
            role=Role(row["role"]),
            content=row["content"],
            route=row["route"],
            latency_ms=row["latency_ms"],
            created_at=row["created_at"],
        )


class ConversationStore:
    """CRUD over `sessions` and `messages`."""

    def __init__(self, db: Database) -> None:
        self._db = db

    async def ensure_session(self, session_id: str | None) -> str:
        """Return an existing session id, or create one."""
        if session_id:
            exists = await self._db.run(
                lambda c: c.execute(
                    "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
                ).fetchone()
            )
            if exists:
                return session_id

        new_id = session_id or f"s_{uuid.uuid4().hex[:12]}"
        started = _now()

        def _insert(conn: sqlite3.Connection) -> None:
            with conn:
                conn.execute(
                    "INSERT INTO sessions (id, started_at) VALUES (?, ?)",
                    (new_id, started),
                )

        await self._db.run(_insert)
        log.info("session.created", session_id=new_id)
        return new_id

    async def latest_session_id(self) -> str | None:
        """Most recently started session, for reload-on-launch."""
        row = await self._db.run(
            lambda c: c.execute(
                "SELECT id FROM sessions ORDER BY started_at DESC, rowid DESC LIMIT 1"
            ).fetchone()
        )
        return row["id"] if row else None

    async def add_message(
        self,
        session_id: str,
        role: Role,
        content: str,
        *,
        route: str | None = None,
        latency_ms: int | None = None,
        tool_calls: list[dict[str, object]] | None = None,
    ) -> int:
        created = _now()
        payload = json.dumps(tool_calls) if tool_calls else None

        def _insert(conn: sqlite3.Connection) -> int:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO messages "
                    "(session_id, role, content, tool_calls, route, latency_ms, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (session_id, str(role), content, payload, route, latency_ms, created),
                )
            return int(cursor.lastrowid or 0)

        return await self._db.run(_insert)

    async def history(self, session_id: str, limit: int = 200) -> list[StoredMessage]:
        """Oldest-first turns for a session."""

        def _select(conn: sqlite3.Connection) -> list[sqlite3.Row]:
            rows = conn.execute(
                "SELECT * FROM (SELECT * FROM messages WHERE session_id = ? "
                "ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
                (session_id, limit),
            ).fetchall()
            return list(rows)

        rows = await self._db.run(_select)
        return [StoredMessage.from_row(r) for r in rows]

    async def message_count(self, session_id: str) -> int:
        row = await self._db.run(
            lambda c: c.execute(
                "SELECT COUNT(*) AS n FROM messages WHERE session_id = ?", (session_id,)
            ).fetchone()
        )
        return int(row["n"]) if row else 0
