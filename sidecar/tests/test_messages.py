"""Session listing, search, titles and deletion — what the history panel reads."""

from __future__ import annotations

import pytest

from sidecar.memory.db import Database
from sidecar.memory.messages import ConversationStore
from sidecar.providers.base import Role


@pytest.fixture
def store(database: Database) -> ConversationStore:
    return ConversationStore(database)


async def make_session(store: ConversationStore, *turns: str) -> str:
    session_id = await store.ensure_session(None)
    for index, text in enumerate(turns):
        role = Role.USER if index % 2 == 0 else Role.ASSISTANT
        await store.add_message(session_id, role, text)
    return session_id


# ── reserved ids ──────────────────────────────────────────────────────


async def test_reserved_id_writes_nothing(store: ConversationStore) -> None:
    """New Chat must not litter the database with empty conversations."""
    reserved = store.reserve_session_id()
    assert reserved.startswith("s_")
    assert await store.list_sessions() == []


async def test_reserved_id_materialises_on_first_message(store: ConversationStore) -> None:
    reserved = store.reserve_session_id()
    resolved = await store.ensure_session(reserved)
    assert resolved == reserved

    await store.add_message(reserved, Role.USER, "first thing said")
    sessions = await store.list_sessions()
    assert [s.id for s in sessions] == [reserved]


# ── listing ───────────────────────────────────────────────────────────


async def test_empty_sessions_are_not_listed(store: ConversationStore) -> None:
    await store.ensure_session(None)  # created but never spoken in
    await make_session(store, "hello")
    assert len(await store.list_sessions()) == 1


async def test_preview_is_the_first_user_message(store: ConversationStore) -> None:
    await make_session(store, "what did I eat", "I don't know.", "fair enough")
    listed = await store.list_sessions()
    assert listed[0].preview == "what did I eat"
    assert listed[0].message_count == 3


async def test_untitled_session_reports_no_title(store: ConversationStore) -> None:
    await make_session(store, "hi")
    assert (await store.list_sessions())[0].title is None


async def test_ordered_by_most_recent_activity(store: ConversationStore) -> None:
    older = await make_session(store, "first conversation")
    newer = await make_session(store, "second conversation")

    # A reply in the older conversation should lift it back to the top: recency
    # means last spoken, not first created.
    await store.add_message(older, Role.USER, "still going")

    listed = await store.list_sessions()
    assert [s.id for s in listed] == [older, newer]


async def test_limit_is_respected(store: ConversationStore) -> None:
    for i in range(5):
        await make_session(store, f"conversation {i}")
    assert len(await store.list_sessions(limit=2)) == 2


# ── search ────────────────────────────────────────────────────────────


async def test_search_matches_message_content(store: ConversationStore) -> None:
    """You look for a conversation by something you remember saying in it."""
    wanted = await make_session(store, "hi", "Hello.", "tell me about zorconium")
    await make_session(store, "hi", "Hello.", "something unrelated")

    hits = await store.list_sessions(query="zorconium")
    assert [s.id for s in hits] == [wanted]


async def test_search_matches_the_assistant_side_too(store: ConversationStore) -> None:
    wanted = await make_session(store, "why", "Because of the photoelectric effect.")
    hits = await store.list_sessions(query="photoelectric")
    assert [s.id for s in hits] == [wanted]


async def test_search_matches_the_title(store: ConversationStore) -> None:
    session_id = await make_session(store, "hi", "Hello.")
    await store.set_title(session_id, "Ollama VRAM limits")
    assert [s.id for s in await store.list_sessions(query="VRAM")] == [session_id]


async def test_search_is_case_insensitive(store: ConversationStore) -> None:
    await make_session(store, "Tell me about Einstein")
    assert len(await store.list_sessions(query="einstein")) == 1


async def test_search_miss_returns_nothing(store: ConversationStore) -> None:
    await make_session(store, "hello there")
    assert await store.list_sessions(query="zzzznope") == []


async def test_blank_query_lists_everything(store: ConversationStore) -> None:
    await make_session(store, "one")
    await make_session(store, "two")
    assert len(await store.list_sessions(query="   ")) == 2


# ── titles ────────────────────────────────────────────────────────────


async def test_title_round_trip(store: ConversationStore) -> None:
    session_id = await make_session(store, "hi")
    await store.set_title(session_id, "  Phase 1.5 wiring  ")
    assert await store.get_title(session_id) == "Phase 1.5 wiring"
    assert (await store.list_sessions())[0].title == "Phase 1.5 wiring"


async def test_get_title_of_unknown_session_is_none(store: ConversationStore) -> None:
    assert await store.get_title("s_nope") is None


# ── deletion ──────────────────────────────────────────────────────────


async def test_delete_removes_session_and_its_messages(store: ConversationStore) -> None:
    doomed = await make_session(store, "delete me", "Alright.", "yes really")
    kept = await make_session(store, "keep me")

    assert await store.delete_session(doomed) == 3
    assert [s.id for s in await store.list_sessions()] == [kept]
    assert await store.history(doomed) == []
    # The surviving conversation must be untouched.
    assert len(await store.history(kept)) == 1


async def test_delete_unknown_session_is_harmless(store: ConversationStore) -> None:
    await make_session(store, "hello")
    assert await store.delete_session("s_nope") == 0
    assert len(await store.list_sessions()) == 1
