"""The nightly §8.3 pass.

Two things are load-bearing and both are about a local 7B being sloppier than
the cloud model §8.3 assumes: the JSON parser has to survive fences and prose,
and a cloud failure has to fall back rather than lose the day's learning.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest

from sidecar.memory.db import Database
from sidecar.memory.episodic import EpisodicMemory
from sidecar.memory.messages import ConversationStore
from sidecar.memory.reflection import (
    Reflector,
    _extract_json,
    build_prompt,
    choose_model,
)
from sidecar.memory.semantic import FactSource, SemanticMemory
from sidecar.memory.settings_store import SettingsStore
from sidecar.providers.base import LLMProvider, ProviderError, Role, StreamDelta


class StubProvider:
    """Replies with whatever it was given, or raises."""

    def __init__(self, reply: str = "{}", *, fails: bool = False) -> None:
        self.reply = reply
        self.fails = fails
        self.calls = 0

    async def stream_chat(
        self, messages: object, **kwargs: object
    ) -> AsyncIterator[StreamDelta]:
        self.calls += 1
        if self.fails:
            raise ProviderError("That account is not active.")
        yield StreamDelta(text=self.reply, done=True)


async def _reflector(
    database: Database,
    reply: str = "{}",
    *,
    ollama: StubProvider | None = None,
    usable: set[str] | None = None,
) -> tuple[Reflector, SemanticMemory]:
    store = ConversationStore(database)
    session = await store.ensure_session("s_one")
    await store.add_message(session, Role.USER, "I usually work on Sillara pricing before 10am")
    await store.add_message(session, Role.ASSISTANT, "Noted.")

    semantic = SemanticMemory(database, None)
    episodic = EpisodicMemory(
        database,
        None,
        store,
        ollama or StubProvider(reply),  # type: ignore[arg-type]
        "qwen2.5:7b",
    )
    providers = {
        "ollama": ollama or StubProvider(reply),
        "openai": StubProvider(reply),
        "gemini": StubProvider(reply),
    }
    reflector = Reflector(
        database,
        semantic,
        episodic,
        SettingsStore(database),
        providers,  # type: ignore[arg-type]
        usable=usable or set(),
        local_models=["qwen2.5:7b"],
    )
    return reflector, semantic


# ── the prompt ────────────────────────────────────────────────────────


def test_the_prompt_carries_both_slots() -> None:
    """`str.format` would raise on the literal braces in the JSON example —
    hence the sentinel substitution. This is that trap, pinned down."""
    messages = build_prompt("user: hello", "user | prefers | tea (0.80)")
    content = messages[0].content

    assert "user: hello" in content
    assert "user | prefers | tea (0.80)" in content
    assert "<<TRANSCRIPT>>" not in content
    assert "<<EXISTING_FACTS>>" not in content
    # §8.3's schema survives intact.
    assert '"facts"' in content and '"confidence":0.0-1.0' in content


def test_an_empty_fact_list_reads_as_none_yet() -> None:
    assert "(none yet)" in build_prompt("user: hi", "")[0].content


# ── parsing what a 7B actually returns ────────────────────────────────


def test_bare_json_parses() -> None:
    assert _extract_json('{"facts": []}') == {"facts": []}


def test_a_fenced_block_parses() -> None:
    raw = 'Here is the JSON:\n```json\n{"facts": [{"subject": "user"}]}\n```\nHope that helps.'
    parsed = _extract_json(raw)
    assert parsed is not None
    assert parsed["facts"][0]["subject"] == "user"


def test_an_unlabelled_fence_parses() -> None:
    assert _extract_json('```\n{"facts": []}\n```') == {"facts": []}


def test_trailing_commentary_is_ignored() -> None:
    assert _extract_json('{"facts": []}\n\nLet me know if you want more.') == {"facts": []}


@pytest.mark.parametrize("raw", ["", "I could not find any facts.", "{not json at all}"])
def test_unusable_output_returns_none_rather_than_raising(raw: str) -> None:
    assert _extract_json(raw) is None


# ── picking a model ───────────────────────────────────────────────────


def test_a_usable_cloud_model_is_preferred() -> None:
    """§8.3: reflection is the highest-leverage inference in the system."""
    chosen = choose_model({"gpt-5.4-mini", "qwen2.5:7b"}, ["qwen2.5:7b"])
    assert not chosen.local


def test_it_falls_back_to_local_with_no_cloud_key() -> None:
    """Which is the state this machine is actually in."""
    chosen = choose_model(set(), ["qwen2.5:7b"])
    assert chosen.local


# ── running ───────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_extracted_facts_are_stored(database: Database) -> None:
    reply = (
        '{"facts": [{"subject": "user", "predicate": "works_on", '
        '"object": "Sillara pricing before 10am", "confidence": 0.8}]}'
    )
    reflector, semantic = await _reflector(database, reply)

    report = await reflector.run(window_hours=24)

    assert report.error is None
    assert report.inserted == 1
    facts = await semantic.list_facts()
    assert [f.object for f in facts] == ["Sillara pricing before 10am"]


@pytest.mark.anyio
async def test_garbage_output_writes_nothing_and_says_so(database: Database) -> None:
    reflector, semantic = await _reflector(database, "I am afraid I cannot do that.")

    report = await reflector.run()

    assert report.error is not None
    assert await semantic.list_facts() == []


@pytest.mark.anyio
async def test_a_cloud_failure_retries_on_the_local_model(database: Database) -> None:
    """A key can be present while the account is dead, which is exactly this
    machine's state — so the pre-check passes and the call fails."""
    reply = '{"facts": [{"subject": "user", "predicate": "likes", "object": "tea"}]}'
    local = StubProvider(reply)
    store = ConversationStore(database)
    session = await store.ensure_session("s_one")
    await store.add_message(session, Role.USER, "I like tea")
    await store.add_message(session, Role.ASSISTANT, "Noted.")

    semantic = SemanticMemory(database, None)
    reflector = Reflector(
        database,
        semantic,
        EpisodicMemory(database, None, store, local, "qwen2.5:7b"),  # type: ignore[arg-type]
        SettingsStore(database),
        cast(
            "dict[str, LLMProvider]",
            {
                "ollama": local,
                "openai": StubProvider(fails=True),
                "gemini": StubProvider(fails=True),
            },
        ),
        usable={"gpt-5.4-mini"},
        local_models=["qwen2.5:7b"],
    )

    report = await reflector.run()

    assert report.error is None
    assert report.local
    assert local.calls == 1
    assert [f.object for f in await semantic.list_facts()] == ["tea"]


@pytest.mark.anyio
async def test_a_pinned_fact_is_counted_as_blocked(database: Database) -> None:
    """The gate's fourth line, from the reflection side."""
    reply = (
        '{"facts": [{"subject": "user", "predicate": "works_on", '
        '"object": "pricing in the evening", "confidence": 0.8}]}'
    )
    reflector, semantic = await _reflector(database, reply)
    await semantic.upsert(
        "user", "works_on", "pricing in the evening", source=FactSource.USER
    )
    # An exact repeat reinforces rather than blocking, so make it a near miss
    # by locking a different wording of the same relation.
    await semantic.forget((await semantic.list_facts())[0].id)
    await semantic.upsert("user", "works_on", "pricing in the morning", source=FactSource.USER)

    report = await reflector.run()

    # With no embedder there is no cosine, so nothing is superseded — the
    # conservative direction, and worth pinning down.
    assert report.blocked_by_pin + report.inserted == 1


@pytest.mark.anyio
async def test_a_second_concurrent_run_is_refused(database: Database) -> None:
    reflector, _ = await _reflector(database, "{}")
    reflector._running = True  # noqa: SLF001

    report = await reflector.run()

    assert report.error == "A reflection is already running."


@pytest.mark.anyio
async def test_an_empty_window_does_not_burn_the_day(database: Database) -> None:
    """This assertion used to be the other way round, and it cost real learning.

    The reasoning behind stamping was "otherwise every tick re-reads an empty
    day and calls the model again" — but an empty read makes **no** model call
    at all; it is one indexed query and then a return. What stamping actually
    bought was this: the app launched at 10:03 into an empty window, marked the
    day done, and then ignored the conversation at 10:50. `facts` had zero rows.
    """
    reflector, _ = await _reflector(database, "{}")

    # A negative window puts the cutoff in the future, so nothing can match —
    # `window_hours=0` is second-granular against messages written in the same
    # second, which is a coin flip rather than a test.
    await reflector.run(window_hours=-1)

    assert await reflector.last_run() is None


@pytest.mark.anyio
async def test_the_mark_advances_only_when_the_batch_was_understood(
    database: Database,
) -> None:
    """A timestamp says an attempt happened; the mark says it was understood.

    Advancing the mark on unparsable output would skip the conversation
    permanently, and not stamping the clock would retry it every five minutes.
    """
    reflector, _ = await _reflector(database, "I am afraid I cannot do that.")

    report = await reflector.run()

    assert report.error is not None
    assert await reflector.last_run() is not None, "an attempt was made; keep the cadence"
    assert await reflector.unreflected_count() > 0, "the messages must be re-read"


@pytest.mark.anyio
async def test_a_conversation_older_than_the_window_is_still_read(
    database: Database,
) -> None:
    """The permanent-loss regression.

    With a wall-clock window, a conversation is unreadable once the app has been
    closed for longer than the window — it is not late, it is gone. A high-water
    mark makes the gap irrelevant.
    """
    reflector, semantic = await _reflector(
        database, '{"facts": [{"subject": "user", "predicate": "likes", "object": "tea"}]}'
    )
    old = (datetime.now(UTC) - timedelta(days=9)).strftime("%Y-%m-%dT%H:%M:%SZ")
    await database.run(
        lambda c: c.executescript(f"UPDATE messages SET created_at = '{old}';")
    )

    report = await reflector.run()

    assert report.messages_read == 2
    assert len(await semantic.list_facts()) == 1


@pytest.mark.anyio
async def test_procedures_are_parsed_and_dropped(database: Database) -> None:
    """The table exists but nothing reads it until Phase 6's agent loop."""
    reply = '{"facts": [], "procedures": [{"name": "deploy", "steps": ["a", "b", "c"]}]}'
    reflector, _ = await _reflector(database, reply)

    report = await reflector.run()

    assert report.error is None
    rows = await database.run(
        lambda c: c.execute("SELECT COUNT(*) AS n FROM procedures").fetchone()
    )
    assert rows["n"] == 0
