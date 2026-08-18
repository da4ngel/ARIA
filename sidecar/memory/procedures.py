"""Procedural learning — tier 4 of memory (BUILD_SPEC §9 Phase 8).

`procedures` has held its row shape since migration 1 and nothing has ever
written to it — the exact "simply never written to" story `episodes`/
`facts` had before Phase 5, and `affect_state` had before this same phase.

**A confirmed procedure becomes a context hint, never a silent replay.**
CLAUDE.md rule 4 is explicit: every tool goes through the registry with an
explicit tier, no ad-hoc calls. Auto-replaying stored steps the moment a
trigger phrase matches would mean one accepted offer skipping per-tool
confirmation forever, for tools that individually still require it — the
opposite of what rule 4 protects. What accepting an offer actually buys is
the model not having to re-derive the plan from nothing; `context_hint()`
names the procedure and its steps in one line, and every step still goes
through `PermissionEngine.run` exactly as if the model had thought of it
unprompted.

**Detection is a fixed-length window, not full variable-length interval
mining.** BUILD_SPEC says "3+ step... sequences" — this reads windows of
exactly `MIN_STEPS` tool calls. A real 4- or 5-step habit still gets
caught, just as more than one overlapping 3-step window (`[A,B,C]` and
`[B,C,D]` both "repeat" if `[A,B,C,D]` does) — a known, stated
simplification, not full sequence mining.
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from difflib import SequenceMatcher

import structlog

from sidecar.memory.db import Database

log = structlog.get_logger(__name__)

#: BUILD_SPEC's own numbers, verbatim: "3+ step tool sequences... occurred
#: 3 times."
MIN_STEPS = 3
MIN_REPEATS = 3

#: Below this, two phrasings are treated as unrelated rather than the same
#: request in different words. Measured loosely, not tuned — this is one
#: line of context, not a decision anything safety-relevant hinges on.
TRIGGER_MATCH_THRESHOLD = 0.6


@dataclass(frozen=True)
class DetectedSequence:
    tools: tuple[str, ...]
    times_observed: int
    #: A session where it was seen, for `_representative_trigger` to look
    #: up what the user actually said beforehand. The *last* one found, not
    #: the first — a recent example is more likely to still be how the user
    #: phrases the request.
    example_session_id: str

    @property
    def name(self) -> str:
        """The `procedures.name` key — `UNIQUE NOT NULL` in the schema,
        which is the entire de-duplication mechanism: a sequence already
        offered is never inserted again, so it is never re-detected as new
        no matter how many more times it recurs."""
        return " → ".join(self.tools)


def _windows(tools: list[str], length: int) -> list[tuple[str, ...]]:
    return [tuple(tools[i : i + length]) for i in range(len(tools) - length + 1)]


async def _tool_sequences_by_session(db: Database) -> dict[str, list[str]]:
    """Ordered `(tool)` per session, successful calls only — a sequence
    worth turning into a macro is one that worked, not one abandoned after
    a failure."""
    rows = await db.run(
        lambda c: c.execute(
            "SELECT session_id, tool FROM tool_log "
            "WHERE session_id IS NOT NULL AND ok = 1 ORDER BY session_id, id"
        ).fetchall()
    )
    sequences: dict[str, list[str]] = {}
    for row in rows:
        sequences.setdefault(row["session_id"], []).append(row["tool"])
    return sequences


async def detect(
    db: Database, *, min_steps: int = MIN_STEPS, min_repeats: int = MIN_REPEATS
) -> list[DetectedSequence]:
    """Read-only. What to do with what this finds is `record_new_offers`'s
    job, not this function's."""
    by_session = await _tool_sequences_by_session(db)
    counts: Counter[tuple[str, ...]] = Counter()
    last_session: dict[tuple[str, ...], str] = {}

    for session_id, tools in by_session.items():
        # Counted once per *session*, not once per window inside one — a
        # sequence repeated three times back-to-back in a single session is
        # a different signal from three separate occasions choosing it, and
        # only the latter is the habit BUILD_SPEC means to catch.
        seen_this_session = set(_windows(tools, min_steps))
        counts.update(seen_this_session)
        for seq in seen_this_session:
            last_session[seq] = session_id

    return [
        DetectedSequence(tools=seq, times_observed=n, example_session_id=last_session[seq])
        for seq, n in counts.items()
        if n >= min_repeats
    ]


async def _representative_trigger(db: Database, session_id: str, first_tool: str) -> str | None:
    """What the user said right before the first tool of a detected
    sequence, in the session it was last seen — a mechanical stand-in for
    "how does this get asked for", not a paraphrase or a summary."""
    row = await db.run(
        lambda c: c.execute(
            "SELECT m.content FROM messages m "
            "WHERE m.session_id = ? AND m.role = 'user' AND m.created_at <= ("
            "  SELECT MIN(created_at) FROM tool_log "
            "  WHERE session_id = ? AND tool = ?"
            ") ORDER BY m.created_at DESC LIMIT 1",
            (session_id, session_id, first_tool),
        ).fetchone()
    )
    return str(row["content"]) if row is not None else None


async def record_new_offers(db: Database) -> list[str]:
    """Detect, then insert exactly the sequences not already known.
    Returns the names newly inserted — the proactivity engine offers those,
    not the ones already sitting in the table from an earlier run.
    """
    detected = await detect(db)
    inserted: list[str] = []
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    for sequence in detected:
        trigger = await _representative_trigger(
            db, sequence.example_session_id, sequence.tools[0]
        )
        steps_json = json.dumps([{"tool": t} for t in sequence.tools])

        def _insert(
            conn: sqlite3.Connection,
            name: str = sequence.name,
            trigger_phrase: str | None = trigger,
            steps: str = steps_json,
            times_observed: int = sequence.times_observed,
        ) -> bool:
            try:
                with conn:
                    conn.execute(
                        "INSERT INTO procedures "
                        "(name, trigger_phrase, steps, times_observed, created_at) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (name, trigger_phrase, steps, times_observed, now),
                    )
                return True
            except sqlite3.IntegrityError:
                # `name` already exists — not new, and not an error. This is
                # the entire dedup mechanism; see `DetectedSequence.name`.
                return False

        if await db.run(_insert):
            inserted.append(sequence.name)
            log.info("procedure.detected", name=sequence.name, times=sequence.times_observed)

    return inserted


async def pending_offers(db: Database) -> list[sqlite3.Row]:
    """Detected, not yet confirmed or declined — what the proactivity
    engine has to offer."""
    return list(
        await db.run(
            lambda c: c.execute(
                "SELECT id, name, trigger_phrase, steps FROM procedures WHERE confirmed = 0"
            ).fetchall()
        )
    )


async def confirm(db: Database, name: str) -> None:
    """Accepted — becomes a context hint from now on."""

    def _confirm(conn: sqlite3.Connection) -> None:
        with conn:
            conn.execute("UPDATE procedures SET confirmed = 1 WHERE name = ?", (name,))

    await db.run(_confirm)
    log.info("procedure.confirmed", name=name)


async def discard(db: Database, name: str) -> None:
    """Declined — forgotten, not just hidden. If the same pattern keeps
    happening, `record_new_offers` will detect and offer it again; a
    standing "no" was never asked for and is not what a decline means here.
    """

    def _delete(conn: sqlite3.Connection) -> None:
        with conn:
            conn.execute("DELETE FROM procedures WHERE name = ?", (name,))

    await db.run(_delete)
    log.info("procedure.declined", name=name)


async def context_hint(db: Database, user_text: str) -> str | None:
    """One line for the prompt when a confirmed procedure's trigger phrase
    is a close match for what was just said. `None` on every turn that
    matches nothing — this must stay as cheap as `retrieved_block`'s own
    "nothing worth injecting" path, since it runs on every turn.
    """
    rows = await db.run(
        lambda c: c.execute(
            "SELECT name, trigger_phrase, steps FROM procedures "
            "WHERE confirmed = 1 AND trigger_phrase IS NOT NULL"
        ).fetchall()
    )
    best_row: sqlite3.Row | None = None
    best_score = 0.0
    for row in rows:
        score = SequenceMatcher(None, user_text.lower(), row["trigger_phrase"].lower()).ratio()
        if score > best_score:
            best_score, best_row = score, row

    if best_row is None or best_score < TRIGGER_MATCH_THRESHOLD:
        return None

    steps = json.loads(best_row["steps"])
    step_names = ", ".join(s["tool"] for s in steps)
    return (
        f'This looks like "{best_row["name"]}", a workflow confirmed before: '
        f"{step_names}. Call each tool normally — this is a reminder of the "
        f"plan, not permission to skip confirming any of its steps."
    )
