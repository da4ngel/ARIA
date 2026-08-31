"""Study Mode's state — the subject, its concept map, and what he has shown.

Study Mode has had a `ModePolicy` and a prompt since modes shipped, and that
prompt already promises two things nothing could deliver: *"find out what he
already knows before explaining"*, and *"bring back an earlier mistake when it
becomes relevant"*. Both need somewhere to remember what happened. This is it.

**Why not `facts`.** A fact is a belief about the user that an overnight
reflection may supersede, and this project has already recorded what a local
model does when asked to judge something it cannot: it returns a constant.
Mastery is not a belief — it is a count of answers actually given, and a model
call must not be able to overwrite it. Different guarantee, different table.

Module-level functions over a class, the `procedures.py` shape rather than
`semantic.py`'s: there is no embedding pool to hold and no merge threshold to
own, so an object would be a namespace with a `db` in it.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import structlog

from sidecar.memory.db import Database

if TYPE_CHECKING:
    from sidecar.core.study_modes import SubModePolicy

log = structlog.get_logger(__name__)

#: The top of the scale. BUILD_SPEC's own 0-5, and the numbers mean:
#: 0 never seen, 1 introduced, 2-3 shaky, 4 solid, 5 he could teach it.
MAX_LEVEL = 5

#: A wrong answer never takes a concept back to 0, because 0 means "never
#: introduced" and that stops being true the moment it is taught. Getting
#: something wrong is not the same as never having met it, and collapsing
#: the two would make her re-introduce from scratch something he has merely
#: forgotten.
MIN_INTRODUCED_LEVEL = 1

#: At or below this, a concept is named as weak in the prompt block.
WEAK_AT_OR_BELOW = 2

#: At or above this, it is named as solid. Deliberately not `MAX_LEVEL` —
#: 4 is "he has answered it right four more times than he has got it wrong",
#: which is worth not re-explaining.
STRONG_AT_OR_ABOVE = 4

#: How many concept names the prompt block will list per group. The whole
#: block sits in the volatile prefix and is paid on every turn (§8.2), so it
#: is capped rather than allowed to grow with the syllabus.
NAMES_IN_BLOCK = 3


def _now() -> str:
    """Millisecond precision, unlike `procedures._now`'s whole seconds.

    Not cosmetic. `latest_subject_id` orders on `last_studied_at`, and a study
    turn calls `study_begin` and `study_check` well inside the same second —
    at second resolution those tie and SQLite is free to return either, so the
    subject being resumed was effectively arbitrary. Found by a test that
    touched two subjects in a row and got the first one back.
    """
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


@dataclass(frozen=True)
class Concept:
    """One node of the map, with whatever mastery it has accumulated."""

    id: int
    name: str
    summary: str
    position: int
    level: int
    asked: int
    correct: int


@dataclass(frozen=True)
class StudyState:
    """Everything the prompt block and the report are rendered from.

    Assembled in one read so a turn spends a single database hop on it —
    this is built on the turn path, unlike `procedures.context_hint`, which
    can afford to be lazy because it usually returns `None`.
    """

    subject_id: int
    subject: str
    source_path: str | None
    concepts: tuple[Concept, ...]

    @property
    def covered(self) -> tuple[Concept, ...]:
        """Anything that has been taught, whether or not it stuck."""
        return tuple(c for c in self.concepts if c.level > 0)

    @property
    def weak(self) -> tuple[Concept, ...]:
        return tuple(c for c in self.covered if c.level <= WEAK_AT_OR_BELOW)

    @property
    def strong(self) -> tuple[Concept, ...]:
        return tuple(c for c in self.concepts if c.level >= STRONG_AT_OR_ABOVE)

    @property
    def next_concept(self) -> Concept | None:
        """What to teach next: the first weak one, else the first untouched
        one, else nothing left.

        **Weak before new, deliberately.** Moving on while something earlier
        is shaky is the failure the whole mode exists to avoid — the prompt
        says "build from first principles, in layers", and a layer with a
        hole in it is not a foundation.
        """
        for concept in self.concepts:
            if 0 < concept.level <= WEAK_AT_OR_BELOW:
                return concept
        for concept in self.concepts:
            if concept.level == 0:
                return concept
        return None


async def ensure_subject(db: Database, name: str, source_path: str | None = None) -> int:
    """Find or create a subject by name, returning its id.

    `source_path` is filled in when it is known and never cleared by a later
    call that does not have one — resuming with "carry on with information
    security" must not forget which lecture the map came from.
    """
    clean = name.strip()
    if not clean:
        msg = "A subject needs a name."
        raise ValueError(msg)

    def _upsert(c: sqlite3.Connection) -> int:
        row = c.execute(
            "SELECT id, source_path FROM study_subjects WHERE name = ? COLLATE NOCASE",
            (clean,),
        ).fetchone()
        if row is not None:
            if source_path and not row["source_path"]:
                with c:
                    c.execute(
                        "UPDATE study_subjects SET source_path = ? WHERE id = ?",
                        (source_path, row["id"]),
                    )
            return int(row["id"])
        with c:
            cursor = c.execute(
                "INSERT INTO study_subjects (name, source_path, created_at) VALUES (?, ?, ?)",
                (clean, source_path, _now()),
            )
        return int(cursor.lastrowid or 0)

    subject_id = await db.run(_upsert)
    log.info("study.subject", subject=clean, subject_id=subject_id, source=source_path)
    return subject_id


async def add_concepts(db: Database, subject_id: int, names: list[tuple[str, str]]) -> int:
    """Add `(name, summary)` pairs to a subject's map, in order.

    **Additive, never a replace.** Re-running extraction over a second lecture
    in the same subject should extend the map, not discard what was already
    learned against the first — and `concept_mastery` hangs off `concepts.id`
    with `ON DELETE CASCADE`, so a replace would silently destroy the
    measurements. `UNIQUE(subject_id, name)` absorbs the repeats.

    Returns how many were genuinely new.
    """

    def _insert(c: sqlite3.Connection) -> int:
        start = c.execute(
            "SELECT COALESCE(MAX(position), -1) FROM concepts WHERE subject_id = ?",
            (subject_id,),
        ).fetchone()[0]
        added = 0
        with c:
            for offset, (name, summary) in enumerate(names, start=1):
                clean = name.strip()
                if not clean:
                    continue
                cursor = c.execute(
                    "INSERT OR IGNORE INTO concepts (subject_id, name, summary, position) "
                    "VALUES (?, ?, ?, ?)",
                    (subject_id, clean, summary.strip(), start + offset),
                )
                if cursor.rowcount:
                    added += 1
        return added

    added = await db.run(_insert)
    log.info("study.concepts", subject_id=subject_id, offered=len(names), added=added)
    return added


async def state(db: Database, subject_id: int) -> StudyState | None:
    """The whole map with its mastery, in one read."""

    def _read(c: sqlite3.Connection) -> tuple[sqlite3.Row | None, list[sqlite3.Row]]:
        subject = c.execute(
            "SELECT id, name, source_path FROM study_subjects WHERE id = ?",
            (subject_id,),
        ).fetchone()
        if subject is None:
            return None, []
        rows = c.execute(
            "SELECT c.id, c.name, c.summary, c.position, "
            "COALESCE(m.level, 0) AS level, COALESCE(m.asked, 0) AS asked, "
            "COALESCE(m.correct, 0) AS correct "
            "FROM concepts c LEFT JOIN concept_mastery m ON m.concept_id = c.id "
            "WHERE c.subject_id = ? ORDER BY c.position, c.id",
            (subject_id,),
        ).fetchall()
        return subject, list(rows)

    subject, rows = await db.run(_read)
    if subject is None:
        return None
    return StudyState(
        subject_id=int(subject["id"]),
        subject=str(subject["name"]),
        source_path=subject["source_path"],
        concepts=tuple(
            Concept(
                id=int(r["id"]),
                name=str(r["name"]),
                summary=str(r["summary"]),
                position=int(r["position"]),
                level=int(r["level"]),
                asked=int(r["asked"]),
                correct=int(r["correct"]),
            )
            for r in rows
        ),
    )


async def latest_subject_id(db: Database) -> int | None:
    """The subject most recently studied, for resuming without being named."""
    row = await db.run(
        lambda c: c.execute(
            "SELECT id FROM study_subjects "
            # `id DESC` is the tie-break, so even two writes inside the same
            # millisecond resolve to one answer rather than whichever the
            # planner reaches first.
            "ORDER BY COALESCE(last_studied_at, created_at) DESC, id DESC LIMIT 1"
        ).fetchone()
    )
    return None if row is None else int(row["id"])


async def find_subject(db: Database, name: str) -> int | None:
    """Resolve a spoken subject name to an id, loosely.

    Exact first, then substring in either direction — "carry on with
    information security" reaches a subject stored as "Information Security
    Fundamentals", and a subject stored as "Networking" is reached by
    "networking basics". Loose on purpose: the cost of a near miss is
    resuming the wrong subject, which is visible in her first sentence and
    correctable, where the cost of being strict is the resume feature not
    working on any phrasing but one.
    """
    clean = name.strip()
    if not clean:
        return None

    def _find(c: sqlite3.Connection) -> int | None:
        exact = c.execute(
            "SELECT id FROM study_subjects WHERE name = ? COLLATE NOCASE", (clean,)
        ).fetchone()
        if exact is not None:
            return int(exact["id"])
        loose = c.execute(
            "SELECT id FROM study_subjects "
            "WHERE ? LIKE '%' || name || '%' COLLATE NOCASE "
            "   OR name LIKE '%' || ? || '%' COLLATE NOCASE "
            "ORDER BY LENGTH(name) DESC LIMIT 1",
            (clean, clean),
        ).fetchone()
        return None if loose is None else int(loose["id"])

    return await db.run(_find)


async def concept_by_name(db: Database, subject_id: int, name: str) -> int | None:
    """The concept a question was about. Exact, then substring."""
    clean = name.strip()
    if not clean:
        return None

    def _find(c: sqlite3.Connection) -> int | None:
        exact = c.execute(
            "SELECT id FROM concepts WHERE subject_id = ? AND name = ? COLLATE NOCASE",
            (subject_id, clean),
        ).fetchone()
        if exact is not None:
            return int(exact["id"])
        loose = c.execute(
            "SELECT id FROM concepts WHERE subject_id = ? "
            "AND (name LIKE '%' || ? || '%' COLLATE NOCASE "
            "  OR ? LIKE '%' || name || '%' COLLATE NOCASE) "
            "ORDER BY LENGTH(name) DESC LIMIT 1",
            (subject_id, clean, clean),
        ).fetchone()
        return None if loose is None else int(loose["id"])

    return await db.run(_find)


def _next_level(level: int, *, correct: bool) -> int:
    """One answer's effect on a level.

    **A level is a running score, not a verdict on the last answer.** One
    correct answer moves it by one, so reaching `MAX_LEVEL` from nothing takes
    five right answers and any wrong one costs ground that has to be won back.
    A rule that jumped to "mastered" on a single lucky pick from four options
    would be a number that lies — and a mastery display nobody can trust is
    worse than no mastery display, because it gets acted on.
    """
    if correct:
        return min(MAX_LEVEL, level + 1)
    return max(MIN_INTRODUCED_LEVEL, level - 1)


async def record_answer(db: Database, concept_id: int, *, correct: bool) -> int:
    """Record one answer and return the concept's new level."""

    def _record(c: sqlite3.Connection) -> int:
        row = c.execute(
            "SELECT level, asked, correct FROM concept_mastery WHERE concept_id = ?",
            (concept_id,),
        ).fetchone()
        level = 0 if row is None else int(row["level"])
        asked = 0 if row is None else int(row["asked"])
        won = 0 if row is None else int(row["correct"])

        now = _now()
        new_level = _next_level(level, correct=correct)
        with c:
            c.execute(
                "INSERT INTO concept_mastery "
                "(concept_id, level, asked, correct, last_seen_at, last_wrong_at) "
                "VALUES (?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(concept_id) DO UPDATE SET "
                "level = excluded.level, asked = excluded.asked, correct = excluded.correct, "
                "last_seen_at = excluded.last_seen_at, "
                # A right answer must not erase the record of an earlier wrong one:
                # "he got this wrong once" is exactly the thing the prompt promises
                # to bring back when it becomes relevant.
                "last_wrong_at = "
                "COALESCE(excluded.last_wrong_at, concept_mastery.last_wrong_at)",
                (
                    concept_id,
                    new_level,
                    asked + 1,
                    won + (1 if correct else 0),
                    now,
                    None if correct else now,
                ),
            )
        return new_level

    level = await db.run(_record)
    log.info("study.answered", concept_id=concept_id, correct=correct, level=level)
    return level


async def mark_taught(db: Database, concept_id: int) -> None:
    """Introduce a concept without asking anything about it.

    Level 1 means "he has met this", which is a different claim from having
    answered a question on it — `asked` stays 0, so nothing here can be
    mistaken for evidence later.
    """

    def _mark(c: sqlite3.Connection) -> None:
        with c:
            c.execute(
                "INSERT INTO concept_mastery (concept_id, level, last_seen_at) "
                "VALUES (?, ?, ?) ON CONFLICT(concept_id) DO UPDATE SET "
                "last_seen_at = excluded.last_seen_at",
                (concept_id, MIN_INTRODUCED_LEVEL, _now()),
            )

    await db.run(_mark)


async def touch(db: Database, subject_id: int) -> None:
    """Stamp a subject as studied now, so resuming picks the right one."""

    def _touch(c: sqlite3.Connection) -> None:
        with c:
            c.execute(
                "UPDATE study_subjects SET last_studied_at = ? WHERE id = ?",
                (_now(), subject_id),
            )

    await db.run(_touch)


async def session_subject_id(db: Database, session_id: str) -> int | None:
    """Which subject *this* chat got to, or None if it has touched none.

    **`sessions.study_subject_id` has been stamped by both study tools since
    migration 008 and was read by nothing until 2026-08-29.** The turn path
    used `latest_subject_id` instead — the most recently touched subject
    *globally* — so a brand-new study chat opened with

        [studying: Introduction to Information Security Analytics - 0 of 22
         covered. next: Module Overview]

    which is a claim that a session is already underway, and the model acted
    on it exactly as written: it carried on teaching a subject from days
    earlier, never mapped the lecture attached to the new chat, and graded
    that quiz against the old subject's concepts, in the real database.

    A record, not a binding. Nothing constrains where a study chat roams; the
    column says where it ended up, which is what lets the panel group by
    subject while the conversation stays free.
    """
    row = await db.run(
        lambda c: c.execute(
            "SELECT study_subject_id FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    )
    if row is None or row["study_subject_id"] is None:
        return None
    return int(row["study_subject_id"])


def render_not_started(previous: tuple[tuple[str, int, int], ...]) -> str:
    """The block for a study chat that has not touched a subject yet.

    **A separate wording, and that is the whole point.** `render` opens
    "studying: X", which is a claim that a session is underway. In a chat
    where nothing has been studied it is a false one, and keeping "studying:"
    while merely correcting *which* subject it named would have left the same
    false claim with a better id in it.

    So this says what is true - nothing started here - and names the prior
    subjects only as something he could ask to resume. Shorter than the real
    state block, because a chat with no session has less to say, not more.
    """
    if not previous:
        return "[no subject started yet. Call study_begin with his material or his goal.]"
    listed = "; ".join(f"{name} ({covered} of {total})" for name, covered, total in previous)
    return (
        "[no subject started in this chat. previously: "
        f"{listed}. Call study_begin - with his material or goal for a new one, "
        "or with one of the names above to resume it.]"
    )



def render(state: StudyState, policy: SubModePolicy | None = None) -> str:
    """The block that goes in the volatile prefix.

    Bounded by construction, and the bound depends on what the sub-mode is
    doing. `Scope.NEXT` and `Scope.WEAK` name at most `NAMES_IN_BLOCK` each,
    because a lesson only needs the thing in front of it. **`Scope.COVERED`
    names all of them**, which is the one deliberate exception: Rapid review
    is *"one line on each concept he has covered"*, and it cannot do that from
    a list of three. Bounded anyway by `curriculum.MAX_CONCEPTS` — at most 24
    short names, and only during a session that asked for them.

    `policy=None` is Learn, and Learn's line is empty, so the block is
    byte-for-byte what it was before sub-modes existed.
    """
    from sidecar.core.study_modes import Scope, policy_for

    resolved = policy_for(policy.sub_mode if policy else None)

    def names(group: tuple[Concept, ...], limit: int | None = NAMES_IN_BLOCK) -> str:
        chosen = group if limit is None else group[:limit]
        return ", ".join(c.name for c in chosen)

    parts = [f"studying: {state.subject} — {len(state.covered)} of {len(state.concepts)} covered"]

    if resolved.scope is Scope.COVERED:
        if state.covered:
            parts.append(f"covered: {names(state.covered, limit=None)}")
    else:
        nxt = state.next_concept
        if nxt is not None:
            parts.append(f"next: {nxt.name}")

    if state.weak:
        parts.append(f"shaky: {names(state.weak)}")
    if state.strong and resolved.scope is not Scope.WEAK:
        # Revision is about what failed. Naming what he is good at there is
        # padding in a block paid for on every turn.
        parts.append(f"solid: {names(state.strong)}")

    block = "[" + ". ".join(parts) + "]"

    # **The map is the boundary of the material, and it goes on its own line.**
    #
    # Observed twice in `gate_study.py`: asked "how does Vantril handle
    # certificate revocation?", a topic the lecture does not touch, she
    # answered *"From what was in the document, Vantril uses OCSP..."* -
    # inventing content and attributing it to his own file - and the exam
    # that followed then tested him on it.
    #
    # The first attempt put this *inside* the bracket, as one more clause in
    # a line that otherwise reads as status. It did not take: the next run
    # dropped the false attribution but still described OCSP and CRLs as
    # Vantril's own. **An instruction buried in a state blob reads as state.**
    # `resolved.line` has always been outside the bracket, for this reason.
    #
    # It names *which* material, because the two cases are not the same
    # falsehood: a planned roadmap has no document at all (`source_path` is
    # NULL), so quoting one is invention twice over.
    if state.source_path:
        boundary = (
            "The map above is the whole of this material. If he asks about "
            "anything not on it, say that first, plainly — then answer from "
            "ordinary knowledge if you can, making clear the answer is yours "
            "and not his source's. Never describe it as being in his file."
        )
    else:
        boundary = (
            "This map was planned from his goal, not read from a file. There "
            "is no document here, so nothing can be quoted from one — if he "
            "asks what his material says, say there is none yet."
        )

    return "\n".join(part for part in (block, boundary, resolved.line) if part)


# ── editing, from the panel rather than from a tool ────────────────────
#
# These are reached by `study.*` RPCs, not by anything in the registry. A click
# is not a tool call — the `files.browse` distinction, already made here: a
# confirmation dialog in front of the button somebody just pressed is asking
# them to confirm the thing they just did.


async def list_subjects(db: Database) -> list[dict[str, object]]:
    """Every subject with its progress, most recently studied first."""
    rows = await db.run(
        lambda c: c.execute(
            "SELECT s.id, s.name, s.source_path, s.last_studied_at, "
            "  COUNT(c2.id) AS total, "
            "  COALESCE(SUM(CASE WHEN m.level > 0 THEN 1 ELSE 0 END), 0) AS covered "
            "FROM study_subjects s "
            "LEFT JOIN concepts c2 ON c2.subject_id = s.id "
            "LEFT JOIN concept_mastery m ON m.concept_id = c2.id "
            "GROUP BY s.id "
            "ORDER BY COALESCE(s.last_studied_at, s.created_at) DESC, s.id DESC"
        ).fetchall()
    )
    return [
        {
            "id": int(r["id"]),
            "name": str(r["name"]),
            "source_path": r["source_path"],
            "last_studied_at": r["last_studied_at"],
            "total": int(r["total"]),
            "covered": int(r["covered"]),
        }
        for r in rows
    ]


async def rename_subject(db: Database, subject_id: int, name: str) -> bool:
    """Rename a subject. False if the new name is taken or empty.

    The name is what resuming matches on, so this is not cosmetic — she files a
    subject under whatever words he used, and "week 3 infosec" is a worse handle
    than "Information Security" for every session after the first.
    """
    clean = name.strip()
    if not clean:
        return False

    def _rename(c: sqlite3.Connection) -> bool:
        clash = c.execute(
            "SELECT id FROM study_subjects WHERE name = ? COLLATE NOCASE AND id != ?",
            (clean, subject_id),
        ).fetchone()
        if clash is not None:
            return False
        with c:
            cursor = c.execute(
                "UPDATE study_subjects SET name = ? WHERE id = ?", (clean, subject_id)
            )
        return bool(cursor.rowcount)

    renamed = await db.run(_rename)
    log.info("study.renamed", subject_id=subject_id, name=clean, ok=renamed)
    return renamed


async def delete_subject(db: Database, subject_id: int) -> bool:
    """Delete a subject, its map, and every answer recorded against it.

    **This is the destructive one.** `concepts` cascades from `study_subjects`
    and `concept_mastery` cascades from `concepts`, so one row taken here
    removes the whole history — which is why the panel arms it with two clicks
    rather than one.
    """

    def _delete(c: sqlite3.Connection) -> bool:
        with c:
            cursor = c.execute("DELETE FROM study_subjects WHERE id = ?", (subject_id,))
        return bool(cursor.rowcount)

    deleted = await db.run(_delete)
    log.info("study.subject_deleted", subject_id=subject_id, ok=deleted)
    return deleted


async def reset_concept(db: Database, concept_id: int) -> bool:
    """Put one concept back to never-introduced.

    Deletes the mastery row rather than zeroing it: `state` already reads a
    missing row as level 0 with no counts, so an absent row and a zeroed one
    mean the same thing and only one of them can drift.

    Re-earnable by answering, which is why this is one click where deleting a
    subject is two.
    """

    def _reset(c: sqlite3.Connection) -> bool:
        with c:
            cursor = c.execute("DELETE FROM concept_mastery WHERE concept_id = ?", (concept_id,))
        return bool(cursor.rowcount)

    reset = await db.run(_reset)
    log.info("study.concept_reset", concept_id=concept_id, ok=reset)
    return reset
