"""The proactivity engine (BUILD_SPEC §9 Phase 8).

`ProactivityScheduler.tick()` is driven with an injected clock and a fake
`is_actively_working`, the same discipline `test_scheduler.py` already uses
for `MemoryScheduler` — nothing here sleeps, and a whole simulated day of
sends runs in milliseconds.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

import pytest

from sidecar.memory.db import Database
from sidecar.memory.messages import ConversationStore
from sidecar.persona.proactivity import (
    Candidate,
    ProactivityScheduler,
    default_candidates,
    idle_intention_candidate,
    is_stated_intention,
    procedure_offer_candidate,
    repeated_failure_candidate,
)


class Recorder:
    """Stands in for `find_candidates`/`self_check`/`deliver`."""

    def __init__(
        self, candidates: list[Candidate] | None = None, *, approve: bool = True
    ) -> None:
        self._candidates = candidates or []
        self._approve = approve
        self.delivered: list[Candidate] = []
        self.checked: list[Candidate] = []
        self.find_calls = 0

    async def find(self) -> list[Candidate]:
        self.find_calls += 1
        return self._candidates

    async def check(self, candidate: Candidate) -> bool:
        self.checked.append(candidate)
        return self._approve

    async def deliver(self, candidate: Candidate) -> None:
        self.delivered.append(candidate)


def _scheduler(
    store: ConversationStore, recorder: Recorder, now: datetime, **kwargs: object
) -> ProactivityScheduler:
    return ProactivityScheduler(
        store=store,
        find_candidates=recorder.find,
        self_check=recorder.check,
        deliver=recorder.deliver,
        is_actively_working=lambda: False,
        clock=lambda: now,
        **kwargs,  # type: ignore[arg-type]
    )


def _candidate(trigger: str = "test") -> Candidate:
    return Candidate(text="hello", trigger=trigger)


# ── the gates, in order ──────────────────────────────────────────────


async def test_a_real_candidate_gets_delivered(database: Database) -> None:
    store = ConversationStore(database)
    recorder = Recorder([_candidate()])

    await _scheduler(store, recorder, datetime(2026, 8, 14, tzinfo=UTC)).tick()

    assert len(recorder.delivered) == 1


async def test_no_candidates_means_nothing_delivered(database: Database) -> None:
    store = ConversationStore(database)
    recorder = Recorder([])

    await _scheduler(store, recorder, datetime(2026, 8, 14, tzinfo=UTC)).tick()

    assert recorder.delivered == []


async def test_actively_working_suppresses_delivery_before_anything_else_runs(
    database: Database,
) -> None:
    store = ConversationStore(database)
    recorder = Recorder([_candidate()])
    scheduler = ProactivityScheduler(
        store=store,
        find_candidates=recorder.find,
        self_check=recorder.check,
        deliver=recorder.deliver,
        is_actively_working=lambda: True,
        clock=lambda: datetime(2026, 8, 14, tzinfo=UTC),
    )

    await scheduler.tick()

    assert recorder.delivered == []
    assert recorder.find_calls == 0, "should not even look for candidates while busy"


async def test_a_declined_self_check_drops_the_candidate(database: Database) -> None:
    store = ConversationStore(database)
    recorder = Recorder([_candidate()], approve=False)

    await _scheduler(store, recorder, datetime(2026, 8, 14, tzinfo=UTC)).tick()

    assert recorder.checked == [_candidate()]
    assert recorder.delivered == []


async def test_only_the_first_candidate_is_considered_per_tick(database: Database) -> None:
    store = ConversationStore(database)
    recorder = Recorder([_candidate("a"), _candidate("b")])

    await _scheduler(store, recorder, datetime(2026, 8, 14, tzinfo=UTC)).tick()

    assert len(recorder.delivered) == 1
    assert recorder.delivered[0].trigger == "a"


# ── the rate limit ────────────────────────────────────────────────────


def _seed_session(conn: sqlite3.Connection, session_id: str = "s1") -> None:
    conn.execute(
        "INSERT INTO sessions (id, started_at) VALUES (?, '2026-08-14T00:00:00Z')",
        (session_id,),
    )


def _seed_proactive_message(conn: sqlite3.Connection, created_at: str) -> None:
    conn.execute(
        "INSERT INTO messages (session_id, role, content, created_at, proactive) "
        "VALUES ('s1', 'assistant', 'hi', ?, 1)",
        (created_at,),
    )


async def test_a_fifth_candidate_in_one_day_is_dropped(database: Database) -> None:
    async def seed() -> None:
        def _do(conn: sqlite3.Connection) -> None:
            _seed_session(conn)
            for hour in (0, 3, 6, 9):
                _seed_proactive_message(conn, f"2026-08-14T{hour:02d}:00:00Z")

        await database.run(_do)

    await seed()
    store = ConversationStore(database)
    recorder = Recorder([_candidate()])

    await _scheduler(store, recorder, datetime(2026, 8, 14, 15, tzinfo=UTC)).tick()

    assert recorder.delivered == [], "4 already sent today — the limit, not 5"


async def test_a_new_day_resets_the_daily_count(database: Database) -> None:
    async def seed() -> None:
        def _do(conn: sqlite3.Connection) -> None:
            _seed_session(conn)
            for hour in (0, 3, 6, 9):
                _seed_proactive_message(conn, f"2026-08-13T{hour:02d}:00:00Z")

        await database.run(_do)

    await seed()
    store = ConversationStore(database)
    recorder = Recorder([_candidate()])

    # A new day, and the last one was well over 90 minutes ago too.
    await _scheduler(store, recorder, datetime(2026, 8, 14, 12, tzinfo=UTC)).tick()

    assert len(recorder.delivered) == 1


async def test_a_candidate_45_minutes_after_the_last_send_is_dropped(
    database: Database,
) -> None:
    async def seed() -> None:
        def _do(conn: sqlite3.Connection) -> None:
            _seed_session(conn)
            _seed_proactive_message(conn, "2026-08-14T09:00:00Z")

        await database.run(_do)

    await seed()
    store = ConversationStore(database)
    recorder = Recorder([_candidate()])

    await _scheduler(store, recorder, datetime(2026, 8, 14, 9, 45, tzinfo=UTC)).tick()

    assert recorder.delivered == []


async def test_a_candidate_91_minutes_after_the_last_send_is_allowed(
    database: Database,
) -> None:
    async def seed() -> None:
        def _do(conn: sqlite3.Connection) -> None:
            _seed_session(conn)
            _seed_proactive_message(conn, "2026-08-14T09:00:00Z")

        await database.run(_do)

    await seed()
    store = ConversationStore(database)
    recorder = Recorder([_candidate()])

    await _scheduler(store, recorder, datetime(2026, 8, 14, 10, 31, tzinfo=UTC)).tick()

    assert len(recorder.delivered) == 1


async def test_the_very_first_send_of_all_time_is_not_blocked(database: Database) -> None:
    store = ConversationStore(database)
    recorder = Recorder([_candidate()])

    await _scheduler(store, recorder, datetime(2026, 8, 14, tzinfo=UTC)).tick()

    assert len(recorder.delivered) == 1


# ── is_stated_intention ──────────────────────────────────────────────


@pytest.mark.parametrize(
    "text",
    [
        "I'll get to the report later",
        "remind me to call the bank",
        "I need to finish this tomorrow",
        "later I'll deal with the budget",
    ],
)
def test_intention_shaped_messages_are_recognised(text: str) -> None:
    assert is_stated_intention(text)


@pytest.mark.parametrize(
    "text",
    ["what is the capital of Australia", "open notepad", "thanks!"],
)
def test_ordinary_messages_are_not_intentions(text: str) -> None:
    assert not is_stated_intention(text)


# ── the individual trigger functions, against a real DB ─────────────


async def test_idle_intention_fires_after_the_gap(database: Database) -> None:
    def _seed(conn: sqlite3.Connection) -> None:
        _seed_session(conn)
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) "
            "VALUES ('s1', 'user', 'I''ll get to the Sillara pricing later', "
            "'2026-08-14T08:00:00Z')"
        )

    await database.run(_seed)
    store = ConversationStore(database)

    too_soon = await idle_intention_candidate(
        store, now=datetime(2026, 8, 14, 8, 30, tzinfo=UTC)
    )
    assert too_soon is None

    later = await idle_intention_candidate(store, now=datetime(2026, 8, 14, 11, tzinfo=UTC))
    assert later is not None
    assert later.trigger == "idle_intention"


async def test_repeated_failure_needs_at_least_two(database: Database) -> None:
    def _seed(conn: sqlite3.Connection, ok: int) -> None:
        _seed_session(conn)
        conn.execute(
            "INSERT INTO tool_log (call_id, session_id, tool, args, tier, ok, created_at) "
            "VALUES ('c1', 's1', 'browser_click', '{}', 1, ?, datetime('now'))",
            (ok,),
        )

    await database.run(lambda c: _seed(c, 0))
    assert await repeated_failure_candidate(database, "s1") is None

    await database.run(
        lambda c: c.execute(
            "INSERT INTO tool_log (call_id, session_id, tool, args, tier, ok, created_at) "
            "VALUES ('c2', 's1', 'browser_click', '{}', 1, 0, datetime('now'))"
        )
    )
    found = await repeated_failure_candidate(database, "s1")
    assert found is not None
    assert found.trigger == "repeated_failure"


async def test_procedure_offer_fires_for_a_pending_offer(database: Database) -> None:
    from sidecar.memory.procedures import record_new_offers

    def _seed(conn: sqlite3.Connection) -> None:
        for i in range(3):
            sid = f"s{i}"
            conn.execute(
                "INSERT INTO sessions (id, started_at) VALUES (?, '2026-08-14T00:00:00Z')",
                (sid,),
            )
            for tool in ("find", "read_file", "browser_navigate"):
                conn.execute(
                    "INSERT INTO tool_log (call_id, session_id, tool, args, tier, ok, "
                    "created_at) VALUES (?, ?, ?, '{}', 1, 1, datetime('now'))",
                    (f"{sid}-{tool}", sid, tool),
                )

    await database.run(_seed)
    await record_new_offers(database)

    found = await procedure_offer_candidate(database)
    assert found is not None
    assert found.trigger == "procedure_offer"
    # `ref` is what lets a plain "yes" resolve without a model call
    # (`ConversationService._resolve_procedure_reply`) — it has to be the
    # real `procedures.name`, not a blank or the display text.
    assert found.ref == "find → read_file → browser_navigate"


async def test_default_candidates_runs_detection_itself(database: Database) -> None:
    """`default_candidates` used to require the caller to run
    `record_new_offers` first — and nothing in production ever did, which is
    exactly the "table nobody writes to" bug this file's own CLAUDE.md
    section keeps finding. No manual call here: seed `tool_log` only and
    prove `default_candidates` still finds the pattern on its own."""

    def _seed(conn: sqlite3.Connection) -> None:
        for i in range(3):
            sid = f"s{i}"
            conn.execute(
                "INSERT INTO sessions (id, started_at) VALUES (?, '2026-08-14T00:00:00Z')",
                (sid,),
            )
            for tool in ("find", "read_file", "browser_navigate"):
                conn.execute(
                    "INSERT INTO tool_log (call_id, session_id, tool, args, tier, ok, "
                    "created_at) VALUES (?, ?, ?, '{}', 1, 1, datetime('now'))",
                    (f"{sid}-{tool}", sid, tool),
                )

    await database.run(_seed)
    store = ConversationStore(database)

    found = await default_candidates(database, store)

    assert len(found) == 1
    assert found[0].trigger == "procedure_offer"


async def test_default_candidates_prefers_a_procedure_offer_over_a_failure(
    database: Database,
) -> None:
    """Least speculative wins: a repeated pattern is a fact about what
    happened, a stated intention is an inference about what was meant."""

    def _seed(conn: sqlite3.Connection) -> None:
        for i in range(3):
            sid = f"s{i}"
            conn.execute(
                "INSERT INTO sessions (id, started_at) VALUES (?, '2026-08-14T00:00:00Z')",
                (sid,),
            )
            for tool in ("find", "read_file", "browser_navigate"):
                conn.execute(
                    "INSERT INTO tool_log (call_id, session_id, tool, args, tier, ok, "
                    "created_at) VALUES (?, ?, ?, '{}', 1, 1, datetime('now'))",
                    (f"{sid}-{tool}", sid, tool),
                )
        conn.execute(
            "INSERT INTO tool_log (call_id, session_id, tool, args, tier, ok, created_at) "
            "VALUES ('fail1', 's0', 'browser_click', '{}', 1, 0, datetime('now'))"
        )
        conn.execute(
            "INSERT INTO tool_log (call_id, session_id, tool, args, tier, ok, created_at) "
            "VALUES ('fail2', 's0', 'browser_click', '{}', 1, 0, datetime('now'))"
        )

    await database.run(_seed)
    store = ConversationStore(database)

    found = await default_candidates(database, store)

    assert len(found) == 1
    assert found[0].trigger == "procedure_offer"


async def test_default_candidates_is_empty_when_nothing_fires(database: Database) -> None:
    store = ConversationStore(database)

    assert await default_candidates(database, store) == []
