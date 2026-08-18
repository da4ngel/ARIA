"""§9.7's labelled dataset: what the router decided, and what the user thought.

None of this existed before. `messages.route` held `'local'` or `'cloud'` and
nothing else, so "smart mode picked the wrong model" could not be investigated
after the fact — which is exactly what had to be done by hand, from a structlog
line, to find that spoken commands were pinned to the weakest model.
"""

from __future__ import annotations

import sqlite3

import pytest

from sidecar.memory.db import Database
from sidecar.memory.messages import ConversationStore
from sidecar.memory.routing_log import MIN_RATINGS_FOR_SIGNAL, RoutingLog, RoutingRecord
from sidecar.providers.base import Role


@pytest.fixture
def routing(database: Database) -> RoutingLog:
    return RoutingLog(database)


@pytest.fixture
def store(database: Database) -> ConversationStore:
    return ConversationStore(database)


def _record(**overrides: object) -> RoutingRecord:
    base: dict[str, object] = {
        "model": "gpt-5.4-mini",
        "provider": "openai",
        "local": False,
        "stage": "cloud",
        "detail": "A command, so accuracy won over speed.",
        "bias": "quality",
    }
    return RoutingRecord(**{**base, **overrides})


# ── writing ───────────────────────────────────────────────────────────


async def test_a_decision_records_its_inputs_not_only_its_outcome(
    routing: RoutingLog, conn: sqlite3.Connection
) -> None:
    """A row saying only which model answered cannot be used to tune anything.
    That is what `messages.route` already was."""
    await routing.record(
        _record(spoken=True, tool_shaped=True, chars=19, latency_ms=812,
                tool_called="set_volume", tool_ok=True)
    )

    row = conn.execute("SELECT * FROM routing_log").fetchone()
    assert row["model"] == "gpt-5.4-mini"
    assert row["stage"] == "cloud"
    assert row["bias"] == "quality"
    assert row["spoken"] == 1
    assert row["tool_shaped"] == 1
    assert row["chars"] == 19
    assert row["latency_ms"] == 812
    assert row["tool_called"] == "set_volume"
    assert row["tool_ok"] == 1
    assert row["rating"] is None, "silence is not agreement"


async def test_a_broken_write_never_reaches_the_turn(
    routing: RoutingLog, database: Database
) -> None:
    """A routing log that can fail a turn is worse than no routing log."""
    await database.run(lambda c: c.executescript("DROP TABLE routing_log;"))

    assert await routing.record(_record()) is None  # must not raise


# ── rating ────────────────────────────────────────────────────────────


async def test_a_turn_can_be_rated_and_unrated(
    routing: RoutingLog, store: ConversationStore
) -> None:
    session = await store.ensure_session("s_one")
    message_id = await store.add_message(session, Role.ASSISTANT, "Volume 40% to 55%.")
    await routing.record(_record(message_id=message_id, session_id=session))

    assert await routing.rate(message_id, -1)
    assert await routing.rating_for(message_id) == -1

    assert await routing.rate(message_id, 1)
    assert await routing.rating_for(message_id) == 1

    # Pressing the same thumb twice means "never mind". A rating you cannot
    # take back is one people stop giving.
    assert await routing.clear_rating(message_id)
    assert await routing.rating_for(message_id) is None


async def test_rating_an_unknown_message_changes_nothing(routing: RoutingLog) -> None:
    assert not await routing.rate(9999, 1)


async def test_a_session_reports_every_rating_it_holds(
    routing: RoutingLog, store: ConversationStore
) -> None:
    """Reopening a conversation has to show the thumbs again, or they look
    like they were not saved."""
    session = await store.ensure_session("s_one")
    liked = await store.add_message(session, Role.ASSISTANT, "one")
    disliked = await store.add_message(session, Role.ASSISTANT, "two")
    ignored = await store.add_message(session, Role.ASSISTANT, "three")
    for message_id in (liked, disliked, ignored):
        await routing.record(_record(message_id=message_id, session_id=session))

    await routing.rate(liked, 1)
    await routing.rate(disliked, -1)

    assert await routing.ratings_for_session(session) == {liked: 1, disliked: -1}


# ── reading ───────────────────────────────────────────────────────────


async def test_verdicts_tally_per_model(
    routing: RoutingLog, store: ConversationStore
) -> None:
    session = await store.ensure_session("s_one")
    for index in range(3):
        message_id = await store.add_message(session, Role.ASSISTANT, f"answer {index}")
        await routing.record(
            _record(model="gpt-5.4-nano", message_id=message_id, session_id=session)
        )
        await routing.rate(message_id, -1)
    await routing.record(_record(model="qwen2.5:7b"))

    verdicts = {v.model: v for v in await routing.verdicts()}
    assert verdicts["gpt-5.4-nano"].turns == 3
    assert verdicts["gpt-5.4-nano"].disliked == 3
    assert verdicts["qwen2.5:7b"].turns == 1
    assert verdicts["qwen2.5:7b"].rated == 0


async def test_approval_stays_silent_until_there_is_enough_of_it(
    routing: RoutingLog, store: ConversationStore
) -> None:
    """Three thumbs-down is one bad afternoon, not evidence about a model. A
    number that reports it as 0% invites acting on nothing."""
    session = await store.ensure_session("s_one")
    for index in range(3):
        message_id = await store.add_message(session, Role.ASSISTANT, f"answer {index}")
        await routing.record(_record(message_id=message_id, session_id=session))
        await routing.rate(message_id, -1)

    verdict = (await routing.verdicts())[0]
    assert verdict.rated < MIN_RATINGS_FOR_SIGNAL
    assert verdict.approval is None


async def test_deleting_a_conversation_takes_its_routing_rows_with_it(
    routing: RoutingLog, store: ConversationStore, conn: sqlite3.Connection
) -> None:
    """`ON DELETE CASCADE` on message_id, with `foreign_keys` ON — the same
    foreign key that broke `delete_session` the moment episodes existed."""
    session = await store.ensure_session("s_one")
    message_id = await store.add_message(session, Role.ASSISTANT, "answer")
    await routing.record(_record(message_id=message_id, session_id=session))

    await store.delete_session(session)

    assert conn.execute("SELECT COUNT(*) AS n FROM routing_log").fetchone()["n"] == 0
