"""Four floats that make the same question read differently at 2am than at
2pm (BUILD_SPEC §9 Phase 8).

`affect_state` has held a row since migration 1 and nothing has ever
written to it — the exact shape `episodes`/`facts` were in before Phase 5:
*"simply never written to."* This finishes what the schema already assumed,
not a design from zero. `core/context.py:377` already names this file
before it existed: *"Phase 8 adds affect. The clock arrived early..."*

**No model call for sentiment, on purpose.** BUILD_SPEC's own formula
includes `sentiment(last_3_user_messages)`, and a per-turn model call for
one float does not fit inside `_finish`'s budget — nor is it likely to be
reliable for this. Phase 5 already paid for this exact lesson once:
*"The model cannot judge salience and should stop being asked... a signal
that is constant is not a signal."* `_sentiment` here is a cheap word-count
heuristic instead, the same shape as `router.py`'s own pattern constants.

`update()` is deliberately pure — no database, no clock reached for
internally, every input named as a parameter — so a test can drive it with
a fixed `now` and fixed inputs and assert on the exact float that comes
back. `load`/`save`/`refresh` are the impure shell around it.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime

import structlog
from pydantic import BaseModel

from sidecar.core.router import is_tool_shaped
from sidecar.memory.db import Database

log = structlog.get_logger(__name__)


class AffectState(BaseModel):
    warmth: float = 0.6
    energy: float = 0.6
    playfulness: float = 0.5
    concern: float = 0.2


#: The row's own defaults (`schema.sql`'s seed values) — what every float
#: drifts back toward between updates.
BASELINE = AffectState()

#: How much of the gap to baseline closes on every update, before that
#: turn's own deltas are applied. Small: this is a mood, not a mood swing —
#: one bad exchange should not erase a week of it, and one good one
#: should not either.
DRIFT_RATE = 0.1

#: BUILD_SPEC's own numbers, verbatim.
LONG_ABSENCE_HOURS = 48.0
LONG_SESSION_HOURS = 4.0
LATE_NIGHT_HOURS = frozenset({1, 2, 3, 4})


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _drift(current: float, baseline: float) -> float:
    return current + DRIFT_RATE * (baseline - current)


#: Not sentiment analysis — a word count. Deliberately small and plain-
#: English rather than tuned, because the float it feeds is a 0.05 nudge,
#: not a decision anything hinges on.
_POSITIVE_WORDS = (
    "thanks",
    "thank you",
    "great",
    "awesome",
    "love",
    "perfect",
    "nice one",
    "appreciate",
    "lol",
    "haha",
    "cool",
    "brilliant",
)
_NEGATIVE_WORDS = (
    "ugh",
    "annoying",
    "hate",
    "terrible",
    "broken",
    "useless",
    "frustrat",
    "sucks",
    "wrong again",
    "stupid",
)


def _sentiment(messages: Sequence[str]) -> float:
    """Roughly `[-1, 1]` from the last few user messages. Zero — the
    common case — means "no signal found", not "neutral mood"."""
    if not messages:
        return 0.0
    text = " ".join(messages).lower()
    positive = sum(text.count(word) for word in _POSITIVE_WORDS)
    negative = sum(text.count(word) for word in _NEGATIVE_WORDS)
    total = positive + negative
    if total == 0:
        return 0.0
    return _clamp((positive - negative) / total, -1.0, 1.0)


def _energy_delta(hour: int) -> float:
    """BUILD_SPEC names this `f(hour_of_day, hours_since_sleep_estimate)`
    without defining it, and there is no sleep tracking anywhere in this
    project — it reduces to the hour alone. Deliberately conservative: a
    small nudge on top of drift-to-baseline, not the dominant term."""
    if 1 <= hour <= 5:
        return -0.1
    if 9 <= hour <= 20:
        return 0.05
    return 0.0


def is_casual(user_text: str) -> bool:
    """A rough stand-in for BUILD_SPEC's own undefined
    `conversation_is_casual` — reuses `router.is_tool_shaped` rather than
    inventing a second classifier for the same question of "is this a task
    or a chat", and adds a length check because a short command
    ("delete file.txt") is not tool-shaped by that function's own
    definition but is not casual chat either."""
    return len(user_text.split()) <= 15 and not is_tool_shaped(user_text)


def update(
    state: AffectState,
    *,
    now: datetime,
    hours_since_last_interaction: float,
    session_duration_hours: float,
    is_casual_turn: bool,
    repeated_failures: bool,
    last_user_messages: Sequence[str] = (),
) -> AffectState:
    """One turn's worth of drift, then BUILD_SPEC's own deltas. Pure — every
    input is a parameter, nothing is read from a clock or a database here.
    """
    warmth = _drift(state.warmth, BASELINE.warmth)
    energy = _drift(state.energy, BASELINE.energy)
    playfulness = _drift(state.playfulness, BASELINE.playfulness)
    concern = _drift(state.concern, BASELINE.concern)

    energy += _energy_delta(now.hour)

    warmth += 0.05 * _sentiment(last_user_messages)
    if hours_since_last_interaction > LONG_ABSENCE_HOURS:
        warmth -= 0.1

    playfulness += 0.1 if is_casual_turn else -0.05

    if session_duration_hours > LONG_SESSION_HOURS or now.hour in LATE_NIGHT_HOURS:
        concern += 0.15
    if repeated_failures:
        concern += 0.1

    return AffectState(
        warmth=_clamp(warmth),
        energy=_clamp(energy),
        playfulness=_clamp(playfulness),
        concern=_clamp(concern),
    )


#: Below this distance from baseline, a float reads as "medium" rather than
#: "low"/"high" — otherwise a state that has barely moved still gets
#: described as if it had, which is worse than saying nothing.
_BAND_MARGIN = 0.15


def _band(
    value: float, baseline: float, low_word: str | None, high_word: str | None
) -> str | None:
    if value < baseline - _BAND_MARGIN:
        return low_word
    if value > baseline + _BAND_MARGIN:
        return high_word
    return None


# Windows' strftime has no %-I (no-leading-zero hour) — the same gap
# `core/context.py` already found and probes around once rather than
# try/except on every render. Duplicated rather than imported: that name is
# module-private there, and re-probing costs nothing at import time.
try:
    datetime(2026, 1, 2).strftime("%-I")
    _SUPPORTS_DASH = True
except ValueError:  # pragma: no cover — platform-dependent
    _SUPPORTS_DASH = False


def _format_hour(now: datetime) -> str:
    if _SUPPORTS_DASH:
        return now.strftime("%-I:%M%p").lower()
    return now.strftime("%I:%M%p").lstrip("0").lower()


def render(state: AffectState, now: datetime) -> str | None:
    """~20 tokens, `machine_context()`'s own style — words, not floats.
    None when nothing is worth saying, the same "byte-identical to a
    no-memory build" discipline `retrieved_block` already follows: a state
    sitting at baseline should not cost a token saying so.
    """
    parts: list[str] = []

    energy_word = _band(state.energy, BASELINE.energy, "low", "high")
    if energy_word == "low":
        parts.append(f"energy low — it's {_format_hour(now)}")
    elif energy_word == "high":
        parts.append("energy high")

    concern_word = _band(state.concern, BASELINE.concern, None, "elevated")
    if concern_word:
        parts.append(f"concern {concern_word}")

    warmth_word = _band(state.warmth, BASELINE.warmth, "guarded", "high")
    if warmth_word:
        parts.append(f"warmth {warmth_word}")

    playful_word = _band(state.playfulness, BASELINE.playfulness, None, "playful")
    if playful_word:
        parts.append(playful_word)

    if not parts:
        return None
    return f"[state: {'; '.join(parts)}]"


#: `kokoro_onnx.Kokoro.create()`'s only lever is a single per-utterance
#: `speed` float — no SSML, no per-word emphasis (checked directly against
#: its signature before writing this). This is the honest substitute for
#: BUILD_SPEC's "prosody hints": a real, audible, affect-driven effect,
#: not literal emphasis — brighter and a touch quicker when playful, a
#: touch slower and steadier when concern is elevated. Small deltas on
#: purpose; a mood should colour her voice, not caricature it.
_BASE_SPEED = 1.0
_PLAYFUL_SPEED_BONUS = 0.06
_CONCERNED_SPEED_PENALTY = 0.05


def speech_speed(state: AffectState) -> float:
    speed = _BASE_SPEED
    if state.playfulness > BASELINE.playfulness + _BAND_MARGIN:
        speed += _PLAYFUL_SPEED_BONUS
    if state.concern > BASELINE.concern + _BAND_MARGIN:
        speed -= _CONCERNED_SPEED_PENALTY
    return speed


async def load(db: Database) -> AffectState:
    """The one row. Falls back to the schema's own defaults if it is
    somehow missing — the seed insert in `schema.sql` should make that
    unreachable, but a fallback here costs nothing and a raised exception
    on every single turn is not the alternative anyone wants."""
    row = await db.run(
        lambda c: c.execute(
            "SELECT warmth, energy, playfulness, concern FROM affect_state WHERE id = 1"
        ).fetchone()
    )
    if row is None:
        return AffectState()
    return AffectState(
        warmth=row["warmth"],
        energy=row["energy"],
        playfulness=row["playfulness"],
        concern=row["concern"],
    )


async def save(db: Database, state: AffectState) -> None:
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _update(conn: sqlite3.Connection) -> None:
        with conn:
            conn.execute(
                "UPDATE affect_state SET warmth = ?, energy = ?, playfulness = ?, "
                "concern = ?, updated_at = ? WHERE id = 1",
                (state.warmth, state.energy, state.playfulness, state.concern, now),
            )

    await db.run(_update)


async def _hours_since_last_interaction(db: Database, session_id: str, now: datetime) -> float:
    """Only meaningful for the first turn of a session — mid-conversation
    this is seconds, and computing it every turn would be a wasted query on
    every single reply for a number that never matters once a session is
    under way. Callers gate on message count; this just answers the query.
    """
    row = await db.run(
        lambda c: c.execute(
            "SELECT created_at FROM messages WHERE session_id != ? "
            "ORDER BY created_at DESC LIMIT 1",
            (session_id,),
        ).fetchone()
    )
    if row is None:
        return 0.0
    last = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    return max(0.0, (now.astimezone(UTC) - last.astimezone(UTC)).total_seconds() / 3600.0)


async def _repeated_failures(db: Database, session_id: str) -> bool:
    """Two or more failed tool calls in this session, recently — 'repeated',
    not 'a tool failed once, which happens'."""
    row = await db.run(
        lambda c: c.execute(
            "SELECT COUNT(*) AS n FROM tool_log WHERE session_id = ? AND ok = 0 "
            "AND created_at > datetime('now', '-15 minutes')",
            (session_id,),
        ).fetchone()
    )
    return bool(row is not None and row["n"] >= 2)


async def refresh(
    db: Database,
    *,
    session_id: str,
    session_started_at: datetime,
    message_count: int,
    last_user_messages: Sequence[str],
    is_casual_turn: bool,
    now: datetime | None = None,
) -> AffectState:
    """Load, update, save — the whole turn-end sequence. Called from
    `ConversationService._finish` via `core.tasks.spawn`, off the turn path;
    a failure here logs and never touches the reply that already went out.
    """
    now = now or datetime.now(UTC)
    state = await load(db)

    # Only the first couple of turns of a session can meaningfully be "a
    # return after being away" — see `_hours_since_last_interaction`'s own
    # docstring for why this is gated rather than queried every turn.
    hours_absent = 0.0
    if message_count <= 2:
        hours_absent = await _hours_since_last_interaction(db, session_id, now)

    session_duration = max(
        0.0, (now.astimezone(UTC) - session_started_at.astimezone(UTC)).total_seconds() / 3600.0
    )
    repeated_failures = await _repeated_failures(db, session_id)

    updated = update(
        state,
        now=now,
        hours_since_last_interaction=hours_absent,
        session_duration_hours=session_duration,
        is_casual_turn=is_casual_turn,
        repeated_failures=repeated_failures,
        last_user_messages=last_user_messages,
    )
    await save(db, updated)
    log.info(
        "affect.updated",
        warmth=round(updated.warmth, 2),
        energy=round(updated.energy, 2),
        playfulness=round(updated.playfulness, 2),
        concern=round(updated.concern, 2),
    )
    return updated
