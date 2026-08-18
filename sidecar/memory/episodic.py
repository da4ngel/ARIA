"""Episodes — what happened, compressed and kept (BUILD_SPEC §7.3 tier 2).

One episode per conversation, written when the conversation is over.

**Sessions have no end event**, which is the whole design problem here. Nothing
in the app has ever written `sessions.ended_at`, and the user does not announce
that they are finished — they walk away. So four triggers converge on one
idempotent `close_session`, with `ended_at` acting as both the record and the
guard:

1. the idle sweep, every scheduler tick, for anything quiet 30 minutes (§9's
   "on session end (or 30min idle)");
2. the sweep that runs seconds after startup, which is what catches a session
   abandoned by killing the app;
3. pressing New Chat, which is an explicit "I am done with that";
4. **not** shutdown — that path must be fast, and it is exactly when Ollama may
   already be gone. Trigger 2 catches it next launch.

Summarising is a model call, so it defers while she is answering and retries on
the next tick. It never raises: an episode is worth less than the turn the user
is waiting on.
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import structlog
from pydantic import BaseModel

from sidecar.core import context as ctx
from sidecar.memory import text as words
from sidecar.memory import vectors
from sidecar.memory.db import Database
from sidecar.memory.messages import ConversationStore, StoredMessage
from sidecar.providers.base import GenerationOptions, LLMProvider, Role
from sidecar.providers.embeddings import EmbeddingsUnavailable, OllamaEmbeddings

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

log = structlog.get_logger(__name__)

#: **Two, and it was four.** That single number is why she forgot a conversation
#: that had just happened: Eyaas asked what skills matter for a data science job,
#: opened a new chat, and asked whether they had discussed jobs. The exchange was
#: two messages, so `close_session` returned before writing anything — and
#: because `_write` is also the only thing that stamps `ended_at`, the session
#: stayed open forever while `close_idle_sessions`' own `HAVING COUNT(m.id) >= ?`
#: excluded it from every future sweep. Permanently invisible, by construction.
#:
#: A question and an answer *is* a conversation. It is the most common shape a
#: useful one takes — you ask her something, she tells you, you get on with it.
#:
#: What this threshold was really guarding against is noise, and it was bad at
#: that too: 15 of the 18 episodes it did admit are "User asked about the date
#: and time." Noise is `_salience`'s job now, and it can weigh a two-message
#: exchange about a career against a two-message exchange about the clock.
#: Filtering on length could never tell those apart.
MIN_MESSAGES_FOR_EPISODE = 2
#: §9: "on session end (or 30min idle)".
DEFAULT_IDLE_MINUTES = 30
EPISODE_MAX_TOKENS = 300
EPISODE_MAX_CHARS = 700
#: The transcript handed to the summariser. A long session is compressed from
#: its opening and its tail; the middle of a rambling conversation is the least
#: durable part of it.
TRANSCRIPT_MAX_CHARS = 8000

#: `_salience`'s weights. They sum to 1.0 before clamping, so the arithmetic is
#: readable at a glance and a change to one is visibly a change to the balance.
SALIENCE_BASE = 0.15
SALIENCE_W_TURNS = 0.25
SALIENCE_W_CHARS = 0.25
SALIENCE_W_VOCAB = 0.20
SALIENCE_W_TOOL = 0.15
#: Where each signal stops earning. Four exchanges is a real conversation; 400
#: characters is a paragraph of intent; 25 distinct words is a subject rather
#: than a request.
SALIENCE_TURNS_SATURATE = 4
SALIENCE_CHARS_SATURATE = 400
SALIENCE_VOCAB_SATURATE = 25
#: At most ±0.05, and only when the model gave a non-zero answer. See `_salience`.
SALIENCE_HINT_WEIGHT = 0.1
#: Never zero: a stored episode that can never clear the retrieval floor is a
#: row that costs a model call and can never be read.
SALIENCE_MIN = 0.1
SALIENCE_MAX = 0.95


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class Episode(BaseModel):
    """A row from `episodes`, as the panel and retrieval see it."""

    id: int
    session_id: str | None
    summary: str
    started_at: str
    ended_at: str
    salience: float
    access_count: int
    last_accessed: str | None = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Episode:
        return cls(
            id=row["id"],
            session_id=row["session_id"],
            summary=row["summary"],
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            salience=float(row["salience"] if row["salience"] is not None else 0.5),
            access_count=int(row["access_count"] or 0),
            last_accessed=row["last_accessed"],
        )


class EpisodicMemory:
    """Writes and reads `episodes`. Never raises into the turn path."""

    def __init__(
        self,
        db: Database,
        embeddings: OllamaEmbeddings | None,
        store: ConversationStore,
        provider: LLMProvider,
        model: str,
        *,
        num_ctx: int = 8192,
        is_busy: Callable[[], bool] | None = None,
    ) -> None:
        self._db = db
        self._embeddings = embeddings
        self._store = store
        self._provider = provider
        self._model = model
        self._num_ctx = num_ctx
        self._is_busy = is_busy or (lambda: False)

    # ── closing sessions ─────────────────────────────────────────────────

    async def close_idle_sessions(
        self, *, now: datetime | None = None, idle_minutes: int = DEFAULT_IDLE_MINUTES
    ) -> int:
        """Summarize every conversation that has gone quiet. Returns how many."""
        moment = now or datetime.now(UTC)
        cutoff = (moment - timedelta(minutes=idle_minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")

        def _idle(conn: sqlite3.Connection) -> list[str]:
            rows = conn.execute(
                """
                SELECT s.id
                FROM sessions s
                JOIN messages m ON m.session_id = s.id
                WHERE s.ended_at IS NULL
                GROUP BY s.id
                HAVING COUNT(m.id) >= ? AND MAX(m.created_at) < ?
                """,
                (MIN_MESSAGES_FOR_EPISODE, cutoff),
            ).fetchall()
            return [str(r["id"]) for r in rows]

        written = 0
        for session_id in await self._db.run(_idle):
            if self._is_busy():
                # She is mid-answer. The sweep runs again in five minutes and
                # nothing here is urgent.
                break
            if await self.close_session(session_id) is not None:
                written += 1
        return written

    async def close_session(self, session_id: str) -> int | None:
        """Summarize one session into an episode. Idempotent; never raises.

        `ended_at` is the guard as well as the record, so a sweep that overlaps
        a New Chat cannot write the same conversation twice.
        """
        try:
            if await self._already_closed(session_id):
                return None

            history = await self._store.history(session_id)
            if len(history) < MIN_MESSAGES_FOR_EPISODE:
                # Nothing worth summarising, but the session is still finished.
                # Stamping it is what stops the sweep reconsidering it on every
                # tick for the life of the install.
                await self._mark_closed(session_id)
                return None

            summary, hinted = await self._summarize(history)
            if not summary:
                return None

            salience = await self._salience(session_id, history, hinted)
            started = history[0].created_at
            ended = history[-1].created_at
            vector = await self._embed(summary)
            episode_id = await self._write(
                session_id, summary, started, ended, salience, vector
            )
            log.info(
                "memory.episode_written",
                episode_id=episode_id,
                session_id=session_id,
                salience=round(salience, 2),
                chars=len(summary),
            )
            return episode_id
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — an episode is never worth an error
            log.warning("memory.episode_failed", session_id=session_id, error=str(exc))
            return None

    async def _mark_closed(self, session_id: str) -> None:
        """Stamp `ended_at` without writing an episode."""

        def _stamp(conn: sqlite3.Connection) -> None:
            with conn:
                conn.execute(
                    "UPDATE sessions SET ended_at = ? WHERE id = ? AND ended_at IS NULL",
                    (_now(), session_id),
                )

        await self._db.run(_stamp)

    async def _already_closed(self, session_id: str) -> bool:
        row = await self._db.run(
            lambda c: c.execute(
                "SELECT ended_at FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
        )
        return row is not None and row["ended_at"] is not None

    async def _write(
        self,
        session_id: str,
        summary: str,
        started_at: str,
        ended_at: str,
        salience: float,
        vector: list[float] | None,
    ) -> int:
        packed = vectors.pack(vectors.normalise(vector)) if vector else None

        def _insert(conn: sqlite3.Connection) -> int:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO episodes
                        (session_id, summary, started_at, ended_at, salience)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (session_id, summary, started_at, ended_at, salience),
                )
                episode_id = int(cursor.lastrowid or 0)
                if packed is not None:
                    conn.execute(
                        "INSERT INTO episode_vec (episode_id, embedding) VALUES (?, ?)",
                        (episode_id, packed),
                    )
                # Stamping this is what makes close_session idempotent, and it
                # is the first thing in the app ever to write the column.
                conn.execute(
                    "UPDATE sessions SET ended_at = ? WHERE id = ?", (_now(), session_id)
                )
            return episode_id

        return await self._db.run(_insert)

    async def forget_session(self, session_id: str) -> int:
        """Drop a session's episodes, so the session itself can be deleted.

        `episodes.session_id` is a foreign key and `foreign_keys` is ON, so
        `ConversationStore.delete_session` — which deletes messages then the
        session — raises `FOREIGN KEY constraint failed` the moment one episode
        exists. This must run first.

        Facts learned from those episodes are **kept**, with `source_episode`
        nulled. Deleting the conversation where you mentioned something does not
        make the something untrue.
        """

        def _delete(conn: sqlite3.Connection) -> int:
            with conn:
                rows = conn.execute(
                    "SELECT id FROM episodes WHERE session_id = ?", (session_id,)
                ).fetchall()
                ids = [int(r["id"]) for r in rows]
                if not ids:
                    return 0
                marks = ",".join("?" * len(ids))
                conn.execute(
                    f"UPDATE facts SET source_episode = NULL WHERE source_episode IN ({marks})",
                    ids,
                )
                conn.execute(f"DELETE FROM episode_vec WHERE episode_id IN ({marks})", ids)
                conn.execute(f"DELETE FROM episodes WHERE id IN ({marks})", ids)
                return len(ids)

        removed = await self._db.run(_delete)
        if removed:
            log.info("memory.episodes_forgotten", session_id=session_id, episodes=removed)
        return removed

    # ── reading ──────────────────────────────────────────────────────────

    async def list_episodes(self, limit: int = 100) -> list[Episode]:
        rows = await self._db.run(
            lambda c: c.execute(
                "SELECT * FROM episodes ORDER BY ended_at DESC LIMIT ?", (limit,)
            ).fetchall()
        )
        return [Episode.from_row(r) for r in rows]

    async def count(self) -> int:
        row = await self._db.run(
            lambda c: c.execute("SELECT COUNT(*) AS n FROM episodes").fetchone()
        )
        return int(row["n"]) if row else 0

    async def search(self, vector: list[float], limit: int = 10) -> list[tuple[Episode, float]]:
        """Nearest episodes to a vector, as (episode, cosine)."""
        packed = vectors.pack(vectors.normalise(vector))

        def _query(conn: sqlite3.Connection) -> list[tuple[Episode, float]]:
            rows = conn.execute(
                """
                SELECT e.*, v.distance
                FROM episode_vec v
                JOIN episodes e ON e.id = v.episode_id
                WHERE v.embedding MATCH ? AND k = ?
                ORDER BY v.distance
                """,
                (packed, limit),
            ).fetchall()
            return [
                (Episode.from_row(r), vectors.cosine_from_l2(float(r["distance"])))
                for r in rows
            ]

        return await self._db.run(_query)

    async def record_access(self, episode_ids: Sequence[int]) -> None:
        """Mark episodes as recalled. Feeds the access_count term in scoring.

        Called off the turn path — it is a write, and the user is waiting.
        """
        if not episode_ids:
            return
        now = _now()
        ids = list(episode_ids)
        marks = ",".join("?" * len(ids))

        def _bump(conn: sqlite3.Connection) -> None:
            with conn:
                conn.execute(
                    f"""
                    UPDATE episodes
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE id IN ({marks})
                    """,
                    [now, *ids],
                )

        await self._db.run(_bump)

    # ── salience ─────────────────────────────────────────────────────────

    async def _salience(
        self, session_id: str, history: list[StoredMessage], hint: float
    ) -> float:
        """How much this conversation deserves to be remembered, computed.

        **The model was asked this and could not do it.** `context.episode_request`
        asks for a salience and `qwen2.5:7b` answered 0.0 for 15 of the 18
        episodes in the live database — including one about a machine running
        out of RAM and one about planning a story. Since salience is 15% of the
        retrieval score, a uniform zero did not merely fail to rank episodes: it
        docked every one of them 0.15 against a 0.45 floor, which is enough on
        its own to sink a correct hit. A signal that is constant is not a signal.

        So it is computed from four things already in hand, none of which needs
        a model or a second query beyond the tool count:

        - **how many times the user spoke.** A back-and-forth means they cared
          enough to stay; one question and a thank-you does not.
        - **how much they wrote.** Substance takes characters.
        - **how varied the vocabulary was**, which is what separates "what time
          is it" from a conversation about a career.
        - **whether a tool ran**, because then something actually happened to
          the machine, and that is worth being able to recall.

        The model's own number survives only as a nudge of at most ±0.05, and
        only when it is non-zero — a zero is read as "did not answer" rather
        than "nothing here matters", which is what the measurement above says it
        actually means.
        """
        user_turns = 0
        user_chars = 0
        vocabulary: set[str] = set()
        for message in history:
            if message.role is not Role.USER:
                continue
            user_turns += 1
            user_chars += len(message.content)
            vocabulary |= words.content_words(message.content)

        computed = (
            SALIENCE_BASE
            + SALIENCE_W_TURNS * min(1.0, user_turns / SALIENCE_TURNS_SATURATE)
            + SALIENCE_W_CHARS * min(1.0, user_chars / SALIENCE_CHARS_SATURATE)
            + SALIENCE_W_VOCAB * min(1.0, len(vocabulary) / SALIENCE_VOCAB_SATURATE)
            + SALIENCE_W_TOOL * (1.0 if await self._used_a_tool(session_id) else 0.0)
        )
        if hint > 0.0:
            computed += SALIENCE_HINT_WEIGHT * (hint - 0.5)
        return round(max(SALIENCE_MIN, min(SALIENCE_MAX, computed)), 3)

    async def _used_a_tool(self, session_id: str) -> bool:
        row = await self._db.run(
            lambda c: c.execute(
                "SELECT 1 FROM tool_log WHERE session_id = ? AND ok = 1 LIMIT 1",
                (session_id,),
            ).fetchone()
        )
        return row is not None

    # ── summarising ──────────────────────────────────────────────────────

    async def _summarize(self, history: list[StoredMessage]) -> tuple[str, float]:
        """One model call for the summary and a salience hint. ("", 0.5) on failure."""
        messages = ctx.to_chat_messages(history)
        if not messages:
            return ("", 0.5)

        transcript = "\n".join(f"{m.role}: {m.content}" for m in messages)
        if len(transcript) > TRANSCRIPT_MAX_CHARS:
            # Keep the opening and the tail: how it started and what it settled
            # on. The middle of a long conversation is its least durable part.
            head = TRANSCRIPT_MAX_CHARS // 2
            transcript = f"{transcript[:head]}\n…\n{transcript[-head:]}"

        chunks: list[str] = []
        async for delta in self._provider.stream_chat(
            ctx.episode_request(transcript),
            model=self._model,
            options=GenerationOptions(num_ctx=self._num_ctx, max_tokens=EPISODE_MAX_TOKENS),
        ):
            chunks.append(delta.text)
            if delta.done:
                break

        return _parse_episode("".join(chunks))

    async def backfill_vectors(self, limit: int = 20) -> int:
        """Embed episodes written while Ollama was down."""
        if self._embeddings is None:
            return 0

        rows = await self._db.run(
            lambda c: c.execute(
                """
                SELECT * FROM episodes
                WHERE id NOT IN (SELECT episode_id FROM episode_vec)
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        )
        done = 0
        for row in rows:
            episode = Episode.from_row(row)
            vector = await self._embed(episode.summary)
            if vector is None:
                break
            packed = vectors.pack(vectors.normalise(vector))

            def _write(
                conn: sqlite3.Connection, eid: int = episode.id, blob: bytes = packed
            ) -> None:
                with conn:
                    conn.execute(
                        "INSERT INTO episode_vec (episode_id, embedding) VALUES (?, ?)",
                        (eid, blob),
                    )

            await self._db.run(_write)
            done += 1
        if done:
            log.info("memory.episodes_backfilled", episodes=done)
        return done

    async def _embed(self, text: str) -> list[float] | None:
        if self._embeddings is None:
            return None
        try:
            return await self._embeddings.embed(text)
        except EmbeddingsUnavailable as exc:
            log.warning("memory.embed_unavailable", error=str(exc))
            return None


def _parse_episode(raw: str) -> tuple[str, float]:
    """Read the summariser's JSON, tolerating a model that wrapped it in prose.

    A local 7B does not reliably return bare JSON. Falling back to the raw text
    matters more than the salience does: a summary with a guessed 0.5 is a
    working episode, a dropped episode is a lost conversation.
    """
    text = raw.strip()
    if not text:
        return ("", 0.5)

    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            parsed = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict) and isinstance(parsed.get("summary"), str):
            summary = parsed["summary"].strip()
            raw_salience = parsed.get("salience", 0.5)
            salience = float(raw_salience) if isinstance(raw_salience, int | float) else 0.5
            return (_clamp_summary(summary), max(0.0, min(1.0, salience)))

    log.info("memory.episode_unparsed", chars=len(text))
    return (_clamp_summary(text), 0.5)


def _clamp_summary(summary: str) -> str:
    """max_tokens is a request, not a guarantee, and this is read for months."""
    if len(summary) <= EPISODE_MAX_CHARS:
        return summary
    return summary[:EPISODE_MAX_CHARS].rsplit(" ", 1)[0] + "…"
