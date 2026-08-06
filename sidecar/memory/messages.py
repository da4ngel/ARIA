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


class SessionSummary(BaseModel):
    """One row in the history list. Everything the panel shows comes from here."""

    id: str
    started_at: str
    # Model-generated, or None until the background job has run.
    title: str | None = None
    # First thing the user said. The fallback label, so the list is never blank.
    preview: str = ""
    message_count: int = 0
    # Last message time, which is what "recent" should mean — a long-running
    # conversation should not sink below a newer one that was abandoned.
    last_activity: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> SessionSummary:
        return cls(
            id=row["id"],
            started_at=row["started_at"],
            title=row["title"],
            preview=row["preview"] or "",
            message_count=row["message_count"],
            last_activity=row["last_activity"] or row["started_at"],
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

    # ── history browsing ────────────────────────────────────────────────

    def reserve_session_id(self) -> str:
        """A fresh id with no row behind it yet.

        `ensure_session` creates a row for any id it does not recognise, so the
        first message written under this id materialises the session. Pressing
        New Chat and then closing the window therefore leaves nothing behind —
        which is why `data/aria.db` had an empty session before this existed.
        """
        return f"s_{uuid.uuid4().hex[:12]}"

    async def list_sessions(
        self, limit: int = 100, query: str | None = None
    ) -> list[SessionSummary]:
        """Conversations for the history panel, most recently active first.

        Sessions with no messages are excluded rather than deleted: an id
        reserved by New Chat is legitimately empty until the first turn lands,
        and a list that showed it would flicker.

        `query` matches message *content*, not just the title — searching for
        something you remember saying is the point.
        """
        sql = """
            SELECT s.id, s.started_at, s.title,
                   COUNT(m.id) AS message_count,
                   MAX(m.created_at) AS last_activity,
                   (SELECT content FROM messages
                     WHERE session_id = s.id AND role = 'user'
                     ORDER BY id LIMIT 1) AS preview
            FROM sessions s
            JOIN messages m ON m.session_id = s.id
        """
        params: list[object] = []
        if query and query.strip():
            # LIKE over content is a table scan, and correct at this size — the
            # largest session here is 78 rows. FTS5 is Phase 5's problem.
            sql += """
            WHERE s.id IN (
                SELECT DISTINCT session_id FROM messages WHERE content LIKE ?
            ) OR s.title LIKE ?
            """
            like = f"%{query.strip()}%"
            params += [like, like]
        # `created_at` has second resolution, so two conversations touched in the
        # same second tie. Message id breaks it: ids are monotonic, so the one
        # spoken in most recently wins — falling back to session rowid would
        # order by when each was *created*, which is the opposite of the intent.
        sql += " GROUP BY s.id ORDER BY last_activity DESC, MAX(m.id) DESC LIMIT ?"
        params.append(limit)

        rows = await self._db.run(lambda c: list(c.execute(sql, params).fetchall()))
        return [SessionSummary.from_row(r) for r in rows]

    async def set_title(self, session_id: str, title: str) -> None:
        """Name a conversation.

        The `with conn:` is load-bearing. Python's sqlite3 opens an implicit
        transaction for DML and never commits it on its own, so without this the
        title was visible to the writing connection and to nothing else — it
        read back correctly in the same process and was gone after a restart.
        """

        def _update(conn: sqlite3.Connection) -> None:
            with conn:
                conn.execute(
                    "UPDATE sessions SET title = ? WHERE id = ?",
                    (title.strip(), session_id),
                )

        await self._db.run(_update)
        log.info("session.titled", session_id=session_id)

    async def get_title(self, session_id: str) -> str | None:
        row = await self._db.run(
            lambda c: c.execute(
                "SELECT title FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
        )
        return row["title"] if row else None

    async def delete_session(self, session_id: str) -> int:
        """Remove a conversation and everything in it. Returns messages deleted.

        Both tables in one transaction: `messages.session_id` is a foreign key,
        so deleting the session first would either fail or orphan the rows,
        depending on whether `foreign_keys` is on.
        """

        def _delete(conn: sqlite3.Connection) -> int:
            with conn:
                cursor = conn.execute(
                    "DELETE FROM messages WHERE session_id = ?", (session_id,)
                )
                removed = cursor.rowcount
                conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return int(removed)

        removed = await self._db.run(_delete)
        log.info("session.deleted", session_id=session_id, messages=removed)
        return removed
