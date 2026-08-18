"""The affect model (BUILD_SPEC §9 Phase 8).

`update()` and `render()` are pure — every test here drives them with a
fixed `now` and fixed inputs, the same discipline `memory/scheduler.py`'s
own tests already use for a clock, and for the same reason: nothing sleeps,
nothing is flaky, and a test failure points at the formula, not the clock.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import UTC, datetime

import pytest

from sidecar.memory.db import Database
from sidecar.persona import affect as affect_module
from sidecar.persona.affect import (
    BASELINE,
    AffectState,
    is_casual,
    load,
    refresh,
    render,
    save,
    speech_speed,
    update,
)

NOON = datetime(2026, 8, 14, 12, 0, tzinfo=UTC)
TWO_AM = datetime(2026, 8, 14, 2, 0, tzinfo=UTC)


def _neutral(
    *,
    now: datetime = NOON,
    hours_since_last_interaction: float = 0.0,
    session_duration_hours: float = 0.0,
    is_casual_turn: bool = False,
    repeated_failures: bool = False,
    last_user_messages: tuple[str, ...] = (),
) -> AffectState:
    """`update()` called with every delta switched off, so a test can turn
    on exactly the one it means to check."""
    return update(
        BASELINE,
        now=now,
        hours_since_last_interaction=hours_since_last_interaction,
        session_duration_hours=session_duration_hours,
        is_casual_turn=is_casual_turn,
        repeated_failures=repeated_failures,
        last_user_messages=last_user_messages,
    )


# ── update(): drift ──────────────────────────────────────────────────


def test_a_state_already_at_baseline_with_no_deltas_barely_moves() -> None:
    result = _neutral()
    # Not exactly BASELINE — energy still gets the midday +0.05 bump — but
    # nothing has run away either.
    assert abs(result.warmth - BASELINE.warmth) < 0.02
    assert abs(result.playfulness - BASELINE.playfulness) < 0.06


def test_a_displaced_state_drifts_toward_baseline_over_repeated_updates() -> None:
    displaced = AffectState(warmth=0.1, energy=0.6, playfulness=0.5, concern=0.9)
    state = displaced
    for _ in range(30):
        state = update(
            state,
            now=NOON,
            hours_since_last_interaction=0.0,
            session_duration_hours=0.0,
            is_casual_turn=False,
            repeated_failures=False,
        )
    # 30 rounds of 10% drift closes the gap almost completely, with no
    # deltas fighting it except energy's own small midday nudge.
    assert state.warmth == pytest.approx(BASELINE.warmth, abs=0.03)
    assert state.concern == pytest.approx(BASELINE.concern, abs=0.03)


# ── update(): the named deltas ──────────────────────────────────────


def test_late_night_hours_raise_concern() -> None:
    late = _neutral(now=TWO_AM)
    noon = _neutral(now=NOON)
    assert late.concern > noon.concern


def test_a_long_session_raises_concern_even_at_a_reasonable_hour() -> None:
    long_session = _neutral(now=NOON, session_duration_hours=5.0)
    short_session = _neutral(now=NOON, session_duration_hours=0.5)
    assert long_session.concern > short_session.concern


def test_repeated_failures_raise_concern() -> None:
    failing = _neutral(repeated_failures=True)
    fine = _neutral(repeated_failures=False)
    assert failing.concern > fine.concern


def test_a_long_absence_lowers_warmth() -> None:
    returning = _neutral(hours_since_last_interaction=72.0)
    same_session = _neutral(hours_since_last_interaction=0.1)
    assert returning.warmth < same_session.warmth


def test_a_short_absence_does_not_trigger_the_long_absence_penalty() -> None:
    """48 hours is the named threshold — a same-day gap must not be read as
    "returning after a while away"."""
    short_gap = _neutral(hours_since_last_interaction=6.0)
    assert short_gap.warmth == pytest.approx(_neutral(hours_since_last_interaction=0.0).warmth)


def test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() -> None:
    casual = _neutral(is_casual_turn=True)
    task = _neutral(is_casual_turn=False)
    assert casual.playfulness > task.playfulness


def test_positive_words_raise_warmth() -> None:
    grateful = _neutral(last_user_messages=("thanks so much, that's perfect",))
    silent = _neutral(last_user_messages=())
    assert grateful.warmth > silent.warmth


def test_negative_words_lower_warmth() -> None:
    annoyed = _neutral(last_user_messages=("ugh this is broken again",))
    silent = _neutral(last_user_messages=())
    assert annoyed.warmth < silent.warmth


def test_every_float_stays_within_bounds_under_repeated_bad_conditions() -> None:
    """Every delta pushing the same direction, over and over, must still
    clamp — this is a state that persists across a whole session's worth of
    turns, and an unclamped float is a bug that gets *worse* the longer she
    runs, not one a single bad turn would ever reveal."""
    state = BASELINE
    for _ in range(200):
        state = update(
            state,
            now=TWO_AM,
            hours_since_last_interaction=100.0,
            session_duration_hours=10.0,
            is_casual_turn=False,
            repeated_failures=True,
            last_user_messages=("ugh terrible broken hate this",),
        )
        assert 0.0 <= state.warmth <= 1.0
        assert 0.0 <= state.energy <= 1.0
        assert 0.0 <= state.playfulness <= 1.0
        assert 0.0 <= state.concern <= 1.0


# ── render() ──────────────────────────────────────────────────────────


def test_baseline_renders_nothing() -> None:
    """A state that has not moved should not cost a token saying so — the
    same "byte-identical to a no-memory build" discipline `retrieved_block`
    already follows."""
    assert render(BASELINE, NOON) is None


def test_low_energy_names_the_hour() -> None:
    low = AffectState(energy=0.2)
    text = render(low, TWO_AM)
    assert text is not None
    assert "energy low" in text
    assert "2:00am" in text


def test_elevated_concern_is_named_elevated_not_low() -> None:
    """Concern only ever reads as "elevated" — there is no natural English
    phrase for "concern low" the way there is for energy or warmth."""
    text = render(AffectState(concern=0.9), NOON)
    assert text is not None
    assert "concern elevated" in text
    assert "concern low" not in text


def test_low_warmth_reads_as_guarded_not_low() -> None:
    text = render(AffectState(warmth=0.1), NOON)
    assert text is not None
    assert "guarded" in text


def test_a_2am_state_and_a_2pm_state_render_differently() -> None:
    """The mechanism half of BUILD_SPEC's own acceptance line — the string
    fed to the model provably differs. Whether the *model* reads
    differently because of it needs a live comparison; see gate_affect.py."""
    low_energy_night = AffectState(energy=0.2)
    assert render(low_energy_night, TWO_AM) != render(low_energy_night, NOON)


# ── is_casual() ──────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "text",
    ["hey how's it going", "lol nice", "thanks!", "what's up"],
)
def test_short_conversational_messages_are_casual(text: str) -> None:
    assert is_casual(text)


@pytest.mark.parametrize(
    "text",
    [
        "delete the file report_final.docx",
        "can you find every python file that imports requests and list them",
        "move budget.xlsx to the documents folder",
    ],
)
def test_task_shaped_messages_are_not_casual(text: str) -> None:
    assert not is_casual(text)


# ── load / save (real, migrated DB) ─────────────────────────────────


async def test_load_returns_the_seeded_defaults(database: Database) -> None:
    """`schema.sql`'s own seed insert (migration 1) means Phase 8 never has
    to special-case an empty table. Confirmed against the real migration,
    not assumed."""
    state = await load(database)
    assert state == BASELINE


async def test_save_then_load_round_trips(database: Database) -> None:
    written = AffectState(warmth=0.9, energy=0.3, playfulness=0.7, concern=0.4)
    await save(database, written)
    assert await load(database) == written


async def test_save_never_inserts_a_second_row(database: Database) -> None:
    """`affect_state.id` is `CHECK (id = 1)` — a second row is structurally
    impossible, but the update-not-insert shape is what this test actually
    guards: `save` must not try to `INSERT` and hit that constraint."""
    await save(database, AffectState(warmth=0.9))
    await save(database, AffectState(warmth=0.1))
    count = await database.run(
        lambda c: c.execute("SELECT COUNT(*) AS n FROM affect_state").fetchone()["n"]
    )
    assert count == 1


# ── the impure gathering: real tool_log / messages rows ────────────────


def _seed_session(conn: sqlite3.Connection, session_id: str, started_at: str) -> None:
    conn.execute("INSERT INTO sessions (id, started_at) VALUES (?, ?)", (session_id, started_at))


def _log_failure(conn: sqlite3.Connection, session_id: str, *, minutes_ago: int = 0) -> None:
    conn.execute(
        "INSERT INTO tool_log (call_id, session_id, tool, args, tier, ok, created_at) "
        "VALUES (?, ?, 'browser_click', '{}', 2, 0, datetime('now', ?))",
        (uuid.uuid4().hex[:8], session_id, f"-{minutes_ago} minutes"),
    )


async def test_repeated_failures_reads_recent_tool_log(database: Database) -> None:
    await database.run(lambda c: _seed_session(c, "s1", "2026-08-14T00:00:00Z"))

    assert not await affect_module._repeated_failures(database, "s1"), (  # noqa: SLF001
        "no failures logged yet"
    )

    await database.run(lambda c: _log_failure(c, "s1"))
    assert not await affect_module._repeated_failures(database, "s1"), (  # noqa: SLF001
        "one failure is not 'repeated'"
    )

    await database.run(lambda c: _log_failure(c, "s1"))
    assert await affect_module._repeated_failures(database, "s1")  # noqa: SLF001


async def test_a_failure_outside_the_recent_window_does_not_count(database: Database) -> None:
    await database.run(lambda c: _seed_session(c, "s1", "2026-08-14T00:00:00Z"))

    def _log_old(conn: sqlite3.Connection) -> None:
        for _ in range(3):
            _log_failure(conn, "s1", minutes_ago=60)

    await database.run(_log_old)
    assert not await affect_module._repeated_failures(database, "s1")  # noqa: SLF001


async def test_refresh_loads_updates_and_saves_in_one_call(database: Database) -> None:
    await database.run(lambda c: _seed_session(c, "s1", "2026-08-14T00:00:00Z"))

    result = await refresh(
        database,
        session_id="s1",
        session_started_at=NOON,
        message_count=1,
        last_user_messages=("thanks, that's perfect",),
        is_casual_turn=True,
        now=NOON,
    )

    assert result.warmth > BASELINE.warmth  # the positive words moved it
    assert await load(database) == result  # and it was actually saved


# ── speech_speed (Phase 8 voice polish) ──────────────────────────────
# `kokoro_onnx.Kokoro.create()`'s only lever is a single per-utterance
# `speed` float, verified directly against its signature before this was
# written — the honest substitute for "prosody hints".


def test_baseline_speed_is_neutral() -> None:
    assert speech_speed(BASELINE) == 1.0


def test_high_playfulness_speeds_up() -> None:
    playful = BASELINE.model_copy(update={"playfulness": 0.9})
    assert speech_speed(playful) > 1.0


def test_elevated_concern_slows_down() -> None:
    concerned = BASELINE.model_copy(update={"concern": 0.9})
    assert speech_speed(concerned) < 1.0


def test_playfulness_within_the_band_margin_does_not_move_it() -> None:
    """Banding matters here too — a nudge just off baseline should not
    already be audible, or every turn would sound slightly different for no
    reason a person could name."""
    barely = BASELINE.model_copy(update={"playfulness": BASELINE.playfulness + 0.05})
    assert speech_speed(barely) == 1.0


def test_high_playfulness_and_high_concern_partially_cancel() -> None:
    both = BASELINE.model_copy(update={"playfulness": 0.9, "concern": 0.9})
    assert speech_speed(both) == pytest.approx(1.0, abs=0.02)
