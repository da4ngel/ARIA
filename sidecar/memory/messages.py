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

from sidecar.memory import text as words
from sidecar.memory.db import Database
from sidecar.providers.base import Role

log = structlog.get_logger(__name__)

#: How far back `search_messages` looks. A few thousand short rows is single
#: digit milliseconds; the cap exists so the cost stays flat as the database
#: grows rather than because 2000 is where usefulness stops.
RECALL_MESSAGE_SCAN = 2000
#: A single shared word out of a long question is a coincidence, not a memory.
RECALL_MIN_COVERAGE = 0.35


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
    # Phase 8: a message with no preceding question (migration 006). False
    # for every message before this column existed and every ordinary reply
    # since — `messages.proactive` defaults to 0.
    proactive: bool = False

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
            proactive=bool(row["proactive"]) if "proactive" in row.keys() else False,
        )


class MessageHit(BaseModel):
    """One past turn that matched a `recall` query."""

    id: int
    session_id: str
    role: Role
    content: str
    created_at: str
    score: float


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
    #: "chat" or "study". A study chat is a kind of conversation rather than a
    #: mode toggled onto one, so the list carries it as a *field* rather than
    #: being filtered by it — `chat.delete` looks a session up through this same
    #: list, and a narrowed list would 404 its own delete.
    kind: str = "chat"
    #: The subject this chat last worked on, or None. A record of where it got
    #: to, not a binding: a study chat may roam between subjects.
    study_subject_id: int | None = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> SessionSummary:
        return cls(
            id=row["id"],
            started_at=row["started_at"],
            title=row["title"],
            preview=row["preview"] or "",
            message_count=row["message_count"],
            last_activity=row["last_activity"] or row["started_at"],
            kind=row["kind"] or "chat",
            study_subject_id=row["study_subject_id"],
        )


class ConversationStore:
    """CRUD over `sessions` and `messages`."""

    def __init__(self, db: Database) -> None:
        self._db = db

    async def ensure_session(self, session_id: str | None, kind: str = "chat") -> str:
        """Return an existing session id, or create one.

        `kind` is only ever applied at creation. **A conversation cannot change
        kind afterwards** — that is the "one door" guarantee, enforced here
        rather than by leaving Study out of a list in the renderer: an existing
        row returns early and never sees this argument.
        """
        if session_id:
            exists = await self._db.run(
                lambda c: c.execute("SELECT 1 FROM sessions WHERE id = ?", (session_id,)).fetchone()
            )
            if exists:
                return session_id

        new_id = session_id or f"s_{uuid.uuid4().hex[:12]}"
        started = _now()

        def _insert(conn: sqlite3.Connection) -> None:
            with conn:
                conn.execute(
                    "INSERT INTO sessions (id, started_at, kind) VALUES (?, ?, ?)",
                    (new_id, started, kind),
                )

        await self._db.run(_insert)
        log.info("session.created", session_id=new_id, kind=kind)
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
        proactive: bool = False,
    ) -> int:
        created = _now()
        payload = json.dumps(tool_calls) if tool_calls else None

        def _insert(conn: sqlite3.Connection) -> int:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO messages "
                    "(session_id, role, content, tool_calls, route, latency_ms, created_at, "
                    "proactive) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        session_id,
                        str(role),
                        content,
                        payload,
                        route,
                        latency_ms,
                        created,
                        int(proactive),
                    ),
                )
            return int(cursor.lastrowid or 0)

        return await self._db.run(_insert)

    async def count_proactive_since(self, since: str) -> int:
        """How many proactive messages have gone out, this recently — the
        rate limiter's own query, not a parallel log. Global, not scoped to
        one session: the limit is about not overwhelming the person, and
        someone who opens a new conversation has not thereby earned four
        more proactive messages. `since` is an ISO-8601 timestamp — inclusive,
        because a message sent at exactly the start of "today" is part of
        today, not the moment before it.
        """
        row = await self._db.run(
            lambda c: c.execute(
                "SELECT COUNT(*) AS n FROM messages WHERE proactive = 1 AND created_at >= ?",
                (since,),
            ).fetchone()
        )
        return int(row["n"]) if row else 0

    async def most_recent_proactive_at(self) -> str | None:
        """When the last proactive message went out, anywhere, for the
        90-minute spacing rule."""
        row = await self._db.run(
            lambda c: c.execute(
                "SELECT created_at FROM messages WHERE proactive = 1 "
                "ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
        )
        return str(row["created_at"]) if row else None

    async def latest_message_at(self) -> str | None:
        """When anything was last said, in any session.

        The whole precondition for §9's scheduled check-in, and deliberately
        *not* a stored "last checked in" stamp: a check-in writes a `messages`
        row itself, so sending one resets the silence by definition. One
        source of truth rather than two that can disagree.
        """
        row = await self._db.run(
            lambda c: c.execute(
                "SELECT created_at FROM messages ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
        )
        return str(row["created_at"]) if row else None

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

    async def search_messages(
        self,
        query: str,
        *,
        limit: int = 5,
        scan: int = RECALL_MESSAGE_SCAN,
        exclude_session: str | None = None,
    ) -> list[MessageHit]:
        """Find past turns that mention what `query` is about.

        **This is the layer that makes "have we discussed X?" answerable.** Facts
        and episodes are both compressions written by a model — a fact only
        exists if reflection judged it durable, and an episode only exists if the
        session was closed and summarised. Neither had happened for the
        conversation Eyaas asked about, and the raw messages were sitting in the
        table the whole time.

        Bounded rather than complete: the newest `scan` turns, scored by the same
        IDF-weighted coverage retrieval uses. It runs inside a tool call rather
        than on the turn path, so it is allowed to be slower than the 80ms
        budget — and at a few thousand short rows it is single-digit
        milliseconds anyway.

        `exclude_session` drops the current conversation, which the model can
        already see and does not need handed back to it as a discovery.
        """
        wanted = words.content_words(query)
        if not wanted:
            return []

        def _select(conn: sqlite3.Connection) -> list[sqlite3.Row]:
            return conn.execute(
                """
                SELECT id, session_id, role, content, created_at FROM messages
                WHERE role IN ('user', 'assistant')
                ORDER BY id DESC LIMIT ?
                """,
                (scan,),
            ).fetchall()

        rows = await self._db.run(_select)
        kept = [r for r in rows if r["session_id"] != exclude_session]
        if not kept:
            return []

        bodies = [words.content_words(r["content"]) for r in kept]
        weights = words.idf(bodies)

        hits = [
            MessageHit(
                id=int(row["id"]),
                session_id=str(row["session_id"]),
                role=Role(row["role"]),
                content=row["content"],
                created_at=row["created_at"],
                score=coverage,
            )
            for row, body in zip(kept, bodies, strict=True)
            if (coverage := words.coverage(wanted, body, weights)) >= RECALL_MIN_COVERAGE
        ]
        hits.sort(key=lambda h: (-h.score, -h.id))
        return hits[:limit]

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
            SELECT s.id, s.started_at, s.title, s.kind, s.study_subject_id,
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
            lambda c: c.execute("SELECT title FROM sessions WHERE id = ?", (session_id,)).fetchone()
        )
        return row["title"] if row else None

    async def set_study_subject(self, session_id: str, subject_id: int) -> None:
        """Note which subject this chat most recently worked on.

        **A record, not a binding.** A study chat may roam — "now let's do
        networking" — and which subject is live is still inferred per turn from
        whichever was most recently touched. This exists so the Study tab can
        group a chat under where it got to, and `ON DELETE SET NULL` means
        deleting the subject leaves the conversation intact.

        Silently does nothing for a session row that does not exist yet, which
        is the normal case for the first tool call of a brand new chat: the row
        appears with the first *message*, and the stamp lands on the next call.
        """

        def _stamp(conn: sqlite3.Connection) -> None:
            with conn:
                conn.execute(
                    "UPDATE sessions SET study_subject_id = ? WHERE id = ?",
                    (subject_id, session_id),
                )

        await self._db.run(_stamp)

    async def session_kind(self, session_id: str) -> str | None:
        """ "chat", "study", or None when there is no row yet."""
        row = await self._db.run(
            lambda c: c.execute("SELECT kind FROM sessions WHERE id = ?", (session_id,)).fetchone()
        )
        return None if row is None else str(row["kind"] or "chat")

    async def delete_session(self, session_id: str) -> int:
        """Remove a conversation and everything in it. Returns messages deleted.

        Both tables in one transaction: `messages.session_id` is a foreign key,
        so deleting the session first would either fail or orphan the rows,
        depending on whether `foreign_keys` is on.
        """

        def _delete(conn: sqlite3.Connection) -> int:
            with conn:
                cursor = conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
                removed = cursor.rowcount
                conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return int(removed)

        removed = await self._db.run(_delete)
        log.info("session.deleted", session_id=session_id, messages=removed)
        return removed
