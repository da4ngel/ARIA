"""Closing a conversation into an episode, and the foreign key that bites.

The `delete_session` test is the one that matters most: `episodes.session_id`
references `sessions(id)` with `foreign_keys` ON, so the first delete after an
episode exists fails outright. Nothing caught that before Phase 5, because
nothing had ever written an episode.
"""

from __future__ import annotations

import sqlite3
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest

from sidecar.memory.db import Database
from sidecar.memory.episodic import EpisodicMemory, _parse_episode
from sidecar.memory.messages import ConversationStore
from sidecar.providers.base import Role, StreamDelta
from sidecar.providers.embeddings import DIMENSIONS, EmbeddingsUnavailable


def _vector(*leading: float) -> list[float]:
    return [*leading, *([0.0] * (DIMENSIONS - len(leading)))]


class StubEmbeddings:
    def __init__(self, *, working: bool = True) -> None:
        self.working = working
        self.calls = 0

    async def embed(self, text: str) -> list[float]:
        self.calls += 1
        if not self.working:
            raise EmbeddingsUnavailable("Ollama is not running.")
        return _vector(1.0, 0.1)


class StubProvider:
    """Returns a fixed episode JSON, so these tests measure the plumbing."""

    def __init__(
        self, reply: str = '{"summary": "They discussed pricing.", "salience": 0.8}'
    ) -> None:
        self.reply = reply
        self.calls = 0

    async def stream_chat(
        self, messages: object, **kwargs: object
    ) -> AsyncIterator[StreamDelta]:
        self.calls += 1
        yield StreamDelta(text=self.reply, done=True)


async def _conversation(store: ConversationStore, session_id: str, turns: int = 2) -> str:
    resolved = await store.ensure_session(session_id)
    for i in range(turns):
        await store.add_message(resolved, Role.USER, f"question {i}")
        await store.add_message(resolved, Role.ASSISTANT, f"answer {i}")
    return resolved


@pytest.fixture
def store(database: Database) -> ConversationStore:
    return ConversationStore(database)


def _episodic(
    database: Database,
    store: ConversationStore,
    *,
    embeddings: StubEmbeddings | None = None,
    provider: StubProvider | None = None,
) -> EpisodicMemory:
    return EpisodicMemory(
        database,
        embeddings or StubEmbeddings(),  # type: ignore[arg-type]
        store,
        provider or StubProvider(),  # type: ignore[arg-type]
        "qwen2.5:7b",
    )


# ── closing ───────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_a_conversation_becomes_one_episode(
    database: Database, store: ConversationStore
) -> None:
    session = await _conversation(store, "s_one")
    memory = _episodic(database, store)

    episode_id = await memory.close_session(session)

    assert episode_id is not None
    episodes = await memory.list_episodes()
    assert len(episodes) == 1
    assert episodes[0].summary == "They discussed pricing."
    # Salience is computed, not taken from the model — the stub says 0.8 and
    # that is deliberately not what lands. See `_salience`.
    assert 0.1 <= episodes[0].salience <= 0.95
    assert episodes[0].salience != pytest.approx(0.8)


@pytest.mark.anyio
async def test_closing_twice_writes_one_episode(
    database: Database, store: ConversationStore
) -> None:
    """`ended_at` is the guard as well as the record, so an idle sweep racing
    a New Chat cannot double-write."""
    session = await _conversation(store, "s_one")
    memory = _episodic(database, store)

    assert await memory.close_session(session) is not None
    assert await memory.close_session(session) is None
    assert len(await memory.list_episodes()) == 1


@pytest.mark.anyio
async def test_a_two_message_exchange_is_remembered(
    database: Database, store: ConversationStore
) -> None:
    """The regression test for the whole bug.

    Eyaas asked one question about data science jobs, got one answer, opened a
    new chat and asked whether they had discussed jobs. She said no — because a
    threshold of four messages meant the exchange was never written, and because
    `_write` is also the only thing that stamps `ended_at`, no later sweep could
    ever reconsider it. A question and an answer is a conversation.
    """
    resolved = await store.ensure_session("s_short")
    await store.add_message(
        resolved, Role.USER, "if I apply for a data science job, what skills matter most?"
    )
    await store.add_message(resolved, Role.ASSISTANT, "Statistics, SQL and communication.")

    provider = StubProvider()
    memory = _episodic(database, store, provider=provider)

    assert await memory.close_session(resolved) is not None
    assert provider.calls == 1
    assert len(await memory.list_episodes()) == 1


@pytest.mark.anyio
async def test_a_lone_message_is_closed_without_an_episode(
    database: Database, store: ConversationStore, conn: sqlite3.Connection
) -> None:
    """Still too short to summarise — but it must be stamped anyway.

    Skipping without stamping is what left three sessions permanently open in
    the live database: `close_idle_sessions` filters on the same message count,
    so an unstamped short session is reconsidered on every tick forever and
    closed on none of them.
    """
    resolved = await store.ensure_session("s_lone")
    await store.add_message(resolved, Role.USER, "hi")

    provider = StubProvider()
    memory = _episodic(database, store, provider=provider)

    assert await memory.close_session(resolved) is None
    assert provider.calls == 0
    row = conn.execute("SELECT ended_at FROM sessions WHERE id = ?", (resolved,)).fetchone()
    assert row["ended_at"] is not None


@pytest.mark.anyio
async def test_a_trivial_exchange_scores_below_a_substantive_one(
    database: Database, store: ConversationStore
) -> None:
    """Length stopped being the noise filter, so salience has to be one.

    15 of the 18 episodes in the live database are "User asked about the date
    and time", every one of them carrying the salience the model chose: 0.0.
    """
    trivial = await store.ensure_session("s_trivial")
    await store.add_message(trivial, Role.USER, "what time is it")
    await store.add_message(trivial, Role.ASSISTANT, "It is 4pm.")

    real = await store.ensure_session("s_real")
    await store.add_message(
        real,
        Role.USER,
        "I am applying for data science roles and I want to know which skills "
        "actually matter to hiring managers, especially around statistics and "
        "communicating results to people who are not technical.",
    )
    await store.add_message(real, Role.ASSISTANT, "Statistics, SQL and communication.")
    await store.add_message(real, Role.USER, "which of those would you learn first?")
    await store.add_message(real, Role.ASSISTANT, "Statistics.")

    memory = _episodic(database, store)
    await memory.close_session(trivial)
    await memory.close_session(real)

    by_session = {e.session_id: e.salience for e in await memory.list_episodes()}
    assert by_session["s_real"] > by_session["s_trivial"]


@pytest.mark.anyio
async def test_closing_stamps_ended_at(
    database: Database, store: ConversationStore, conn: sqlite3.Connection
) -> None:
    """The column existed since migration 1 and nothing had ever written it."""
    session = await _conversation(store, "s_one")
    await _episodic(database, store).close_session(session)

    row = conn.execute("SELECT ended_at FROM sessions WHERE id = ?", (session,)).fetchone()
    assert row["ended_at"] is not None


@pytest.mark.anyio
async def test_a_model_failure_leaves_the_session_open_to_retry(
    database: Database, store: ConversationStore
) -> None:
    class Failing(StubProvider):
        async def stream_chat(
            self, messages: object, **kwargs: object
        ) -> AsyncIterator[StreamDelta]:
            if self.calls >= 0:
                raise RuntimeError("Ollama fell over.")
            yield StreamDelta(text="", done=True)  # pragma: no cover

    session = await _conversation(store, "s_one")
    memory = _episodic(database, store, provider=Failing())

    assert await memory.close_session(session) is None
    # Not stamped, so the next sweep tries again rather than losing the day.
    assert not await memory._already_closed(session)  # noqa: SLF001


# ── the idle sweep ────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_the_sweep_closes_only_quiet_conversations(
    database: Database, store: ConversationStore, conn: sqlite3.Connection
) -> None:
    quiet = await _conversation(store, "s_quiet")
    await _conversation(store, "s_live")

    stale = (datetime.now(UTC) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with conn:
        conn.execute("UPDATE messages SET created_at = ? WHERE session_id = ?", (stale, quiet))

    memory = _episodic(database, store)
    assert await memory.close_idle_sessions(idle_minutes=30) == 1

    episodes = await memory.list_episodes()
    assert [e.session_id for e in episodes] == [quiet]


@pytest.mark.anyio
async def test_the_sweep_stands_down_while_she_is_answering(
    database: Database, store: ConversationStore, conn: sqlite3.Connection
) -> None:
    """A second model call mid-turn costs the answer the user is waiting on."""
    session = await _conversation(store, "s_quiet")
    stale = (datetime.now(UTC) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with conn:
        conn.execute("UPDATE messages SET created_at = ? WHERE session_id = ?", (stale, session))

    provider = StubProvider()
    memory = EpisodicMemory(
        database,
        StubEmbeddings(),  # type: ignore[arg-type]
        store,
        provider,  # type: ignore[arg-type]
        "qwen2.5:7b",
        is_busy=lambda: True,
    )

    assert await memory.close_idle_sessions(idle_minutes=30) == 0
    assert provider.calls == 0


# ── the foreign key ───────────────────────────────────────────────────


@pytest.mark.anyio
async def test_deleting_a_session_with_an_episode_needs_forget_session_first(
    database: Database, store: ConversationStore
) -> None:
    """The regression test for the bug Phase 5 introduces into Phase 1's code.

    Without `forget_session`, `delete_session` raises FOREIGN KEY constraint
    failed — silently, on the first conversation anyone deletes after memory
    starts writing episodes.
    """
    session = await _conversation(store, "s_one")
    memory = _episodic(database, store)
    await memory.close_session(session)

    with pytest.raises(sqlite3.IntegrityError):
        await store.delete_session(session)

    await memory.forget_session(session)
    assert await store.delete_session(session) > 0


@pytest.mark.anyio
async def test_forgetting_a_session_keeps_the_facts_it_taught(
    database: Database, store: ConversationStore, conn: sqlite3.Connection
) -> None:
    """Deleting the conversation where you said something does not make it
    untrue — `source_episode` is nulled, the fact stays."""
    session = await _conversation(store, "s_one")
    memory = _episodic(database, store)
    episode_id = await memory.close_session(session)

    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    with conn:
        conn.execute(
            """
            INSERT INTO facts (subject, predicate, object, confidence, source_episode,
                               created_at, updated_at)
            VALUES ('user', 'works_on', 'pricing', 0.8, ?, ?, ?)
            """,
            (episode_id, now, now),
        )

    await memory.forget_session(session)

    row = conn.execute("SELECT source_episode FROM facts").fetchone()
    assert row is not None
    assert row["source_episode"] is None


# ── working without embeddings ────────────────────────────────────────


@pytest.mark.anyio
async def test_an_episode_is_written_even_with_ollama_down(
    database: Database, store: ConversationStore, conn: sqlite3.Connection
) -> None:
    session = await _conversation(store, "s_one")
    memory = _episodic(database, store, embeddings=StubEmbeddings(working=False))

    assert await memory.close_session(session) is not None
    assert conn.execute("SELECT COUNT(*) FROM episode_vec").fetchone()[0] == 0


@pytest.mark.anyio
async def test_backfill_vectors_catches_up_later(
    database: Database, store: ConversationStore, conn: sqlite3.Connection
) -> None:
    session = await _conversation(store, "s_one")
    await _episodic(database, store, embeddings=StubEmbeddings(working=False)).close_session(
        session
    )

    recovered = _episodic(database, store)
    assert await recovered.backfill_vectors() == 1
    assert conn.execute("SELECT COUNT(*) FROM episode_vec").fetchone()[0] == 1


# ── parsing what the model returned ───────────────────────────────────


def test_a_fenced_json_reply_parses() -> None:
    summary, salience = _parse_episode(
        'Here you go:\n```json\n{"summary": "A chat about pricing.", "salience": 0.7}\n```'
    )
    assert summary == "A chat about pricing."
    assert salience == pytest.approx(0.7)


def test_plain_prose_is_kept_as_the_summary() -> None:
    """A dropped episode is a lost conversation; a guessed salience is not."""
    summary, salience = _parse_episode("They talked about the banquet hall quotation.")
    assert summary == "They talked about the banquet hall quotation."
    assert salience == pytest.approx(0.5)


def test_salience_is_clamped() -> None:
    _, salience = _parse_episode('{"summary": "x", "salience": 4.2}')
    assert salience == pytest.approx(1.0)


def test_an_empty_reply_produces_no_episode() -> None:
    assert _parse_episode("   ") == ("", 0.5)
