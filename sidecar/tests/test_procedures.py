"""Procedural learning: detection, dedup, accept/decline, and the context
hint (BUILD_SPEC §9 Phase 8, tier 4).

§9's own line — *"repeat a 3-step workflow 3x -> macro offer appears"* — is
what every detection test here drives at directly: real rows in `tool_log`
across real sessions, not a mocked detector.
"""

from __future__ import annotations

import sqlite3
import uuid

from sidecar.memory.db import Database
from sidecar.memory.procedures import (
    MIN_REPEATS,
    MIN_STEPS,
    confirm,
    context_hint,
    detect,
    discard,
    pending_offers,
    record_new_offers,
)


def _session(conn: sqlite3.Connection, session_id: str) -> None:
    conn.execute(
        "INSERT INTO sessions (id, started_at) VALUES (?, '2026-08-14T00:00:00Z')",
        (session_id,),
    )


def _call(conn: sqlite3.Connection, session_id: str, tool: str, *, ok: bool = True) -> None:
    conn.execute(
        "INSERT INTO tool_log (call_id, session_id, tool, args, tier, ok, created_at) "
        "VALUES (?, ?, ?, '{}', 1, ?, datetime('now'))",
        (uuid.uuid4().hex[:8], session_id, tool, int(ok)),
    )


def _message(conn: sqlite3.Connection, session_id: str, role: str, content: str) -> None:
    conn.execute(
        "INSERT INTO messages (session_id, role, content, created_at) "
        "VALUES (?, ?, ?, datetime('now'))",
        (session_id, role, content),
    )


async def _seed(database: Database, tools: tuple[str, ...], times: int) -> None:
    """Each call uses fresh session ids — calling this more than once in a
    test (to simulate a pattern recurring later) must not collide with
    sessions an earlier call already created."""

    def _do(conn: sqlite3.Connection) -> None:
        for _ in range(times):
            sid = f"s{uuid.uuid4().hex[:8]}"
            _session(conn, sid)
            _message(conn, sid, "user", "find my cv and open it in the browser")
            for tool in tools:
                _call(conn, sid, tool)

    await database.run(_do)


# ── detection ─────────────────────────────────────────────────────────


def test_min_steps_and_repeats_match_build_spec() -> None:
    assert MIN_STEPS == 3
    assert MIN_REPEATS == 3


async def test_a_sequence_repeated_exactly_3_times_is_detected(database: Database) -> None:
    await _seed(database, ("find", "read_file", "browser_navigate"), times=3)

    found = await detect(database)

    assert any(d.tools == ("find", "read_file", "browser_navigate") for d in found)


async def test_a_sequence_repeated_only_twice_is_not_detected(database: Database) -> None:
    await _seed(database, ("find", "read_file", "browser_navigate"), times=2)

    found = await detect(database)

    assert found == []


async def test_a_sequence_within_one_session_only_counts_once(database: Database) -> None:
    """Three occurrences back-to-back in a single session is a different
    signal from three separate occasions — only the latter is a habit."""

    def _seed_one_session(conn: sqlite3.Connection) -> None:
        _session(conn, "s0")
        for _ in range(3):
            _call(conn, "s0", "find")
            _call(conn, "s0", "read_file")
            _call(conn, "s0", "browser_navigate")

    await database.run(_seed_one_session)

    found = await detect(database)

    assert found == []


async def test_a_failed_call_does_not_count_toward_the_sequence(database: Database) -> None:
    def _seed_with_failure(conn: sqlite3.Connection) -> None:
        for i in range(3):
            sid = f"s{i}"
            _session(conn, sid)
            _call(conn, sid, "find")
            _call(conn, sid, "read_file", ok=False)  # the chain breaks here
            _call(conn, sid, "browser_navigate")

    await database.run(_seed_with_failure)

    found = await detect(database)

    assert found == []


async def test_an_unrelated_tool_between_two_real_habits_is_not_confused(
    database: Database,
) -> None:
    def _seed_two_habits(conn: sqlite3.Connection) -> None:
        for i in range(3):
            sid = f"a{i}"
            _session(conn, sid)
            _call(conn, sid, "find")
            _call(conn, sid, "read_file")
            _call(conn, sid, "browser_navigate")
        for i in range(3):
            sid = f"b{i}"
            _session(conn, sid)
            _call(conn, sid, "open_app")
            _call(conn, sid, "set_volume")
            _call(conn, sid, "close_app")

    await database.run(_seed_two_habits)

    found = {d.tools for d in await detect(database)}

    assert ("find", "read_file", "browser_navigate") in found
    assert ("open_app", "set_volume", "close_app") in found
    assert len(found) == 2


# ── recording, dedup, accept/decline ────────────────────────────────


async def test_record_new_offers_inserts_once_per_sequence(database: Database) -> None:
    await _seed(database, ("find", "read_file", "browser_navigate"), times=3)

    inserted_first = await record_new_offers(database)
    inserted_second = await record_new_offers(database)

    assert inserted_first == ["find → read_file → browser_navigate"]
    assert inserted_second == [], "already known — not re-inserted, not re-offered"

    rows = await database.run(
        lambda c: c.execute("SELECT COUNT(*) AS n FROM procedures").fetchone()
    )
    assert rows["n"] == 1


async def test_the_representative_trigger_is_captured(database: Database) -> None:
    await _seed(database, ("find", "read_file", "browser_navigate"), times=3)

    await record_new_offers(database)

    row = await database.run(
        lambda c: c.execute(
            "SELECT trigger_phrase FROM procedures WHERE name LIKE 'find%'"
        ).fetchone()
    )
    assert row["trigger_phrase"] == "find my cv and open it in the browser"


async def test_a_pending_offer_appears_until_confirmed_or_declined(database: Database) -> None:
    await _seed(database, ("find", "read_file", "browser_navigate"), times=3)
    await record_new_offers(database)

    assert len(await pending_offers(database)) == 1

    await confirm(database, "find → read_file → browser_navigate")

    assert await pending_offers(database) == []


async def test_declining_deletes_the_row_rather_than_marking_it(database: Database) -> None:
    await _seed(database, ("find", "read_file", "browser_navigate"), times=3)
    await record_new_offers(database)

    await discard(database, "find → read_file → browser_navigate")

    count = await database.run(
        lambda c: c.execute("SELECT COUNT(*) AS n FROM procedures").fetchone()
    )
    assert count["n"] == 0


async def test_a_declined_pattern_can_be_offered_again_if_it_recurs(database: Database) -> None:
    """A decline is not a standing "never ask again" — nothing asked for
    that, and the schema has no column to record it even if it had."""
    await _seed(database, ("find", "read_file", "browser_navigate"), times=3)
    await record_new_offers(database)
    await discard(database, "find → read_file → browser_navigate")

    # It happens a fourth time.
    await _seed(database, ("find", "read_file", "browser_navigate"), times=1)
    inserted = await record_new_offers(database)

    assert inserted == ["find → read_file → browser_navigate"]


# ── the context hint ─────────────────────────────────────────────────


async def test_no_hint_when_nothing_is_confirmed(database: Database) -> None:
    await _seed(database, ("find", "read_file", "browser_navigate"), times=3)
    await record_new_offers(database)  # pending, not confirmed

    assert await context_hint(database, "find my cv and open it in the browser") is None


async def test_a_close_match_to_a_confirmed_trigger_produces_a_hint(database: Database) -> None:
    await _seed(database, ("find", "read_file", "browser_navigate"), times=3)
    await record_new_offers(database)
    await confirm(database, "find → read_file → browser_navigate")

    hint = await context_hint(database, "find my cv and open it in the browser")

    assert hint is not None
    assert "find → read_file → browser_navigate" in hint
    assert "find, read_file, browser_navigate" in hint


async def test_an_unrelated_message_produces_no_hint(database: Database) -> None:
    await _seed(database, ("find", "read_file", "browser_navigate"), times=3)
    await record_new_offers(database)
    await confirm(database, "find → read_file → browser_navigate")

    assert await context_hint(database, "what is the capital of Australia") is None


async def test_the_hint_never_tells_the_model_to_skip_confirmation(database: Database) -> None:
    """The one line this whole design exists to protect — rule 4."""
    await _seed(database, ("find", "read_file", "browser_navigate"), times=3)
    await record_new_offers(database)
    await confirm(database, "find → read_file → browser_navigate")

    hint = await context_hint(database, "find my cv and open it in the browser")

    assert hint is not None
    assert "skip" in hint and "not permission to skip" in hint


async def test_the_hint_reflects_the_steps_confirmed_not_a_live_recompute(
    database: Database,
) -> None:
    """"The plan you approved is the plan that runs" — `organize_folder`'s own
    guarantee (CLAUDE.md, Phase 4), mirrored here. `context_hint` reads the
    `steps` column stored at detection time. `tool_log` keeps growing after
    that, and a hint that went back to recompute from it live would drift
    from what was actually confirmed — mutation-checked below."""
    await _seed(database, ("find", "read_file", "browser_navigate"), times=3)
    await record_new_offers(database)
    await confirm(database, "find → read_file → browser_navigate")

    # Grows *after* confirmation: a longer pattern sharing the same prefix,
    # which a live recompute would have every chance to notice and fold in.
    await _seed(database, ("find", "read_file", "browser_navigate", "open_app"), times=3)

    hint = await context_hint(database, "find my cv and open it in the browser")

    assert hint is not None
    assert "find, read_file, browser_navigate" in hint
    assert "open_app" not in hint
