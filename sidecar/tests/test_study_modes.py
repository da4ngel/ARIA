"""The six sub-modes: what they change, and the one thing they must not leak.

Most of a sub-mode is prompt text, which a test can only check is *present* —
whether a model follows it is what `scripts/gate_study.py` is for. The two
things asserted here are the ones that are mechanical and would fail silently:
Exam withholding the answers, and Learn being byte-identical to Study before
sub-modes existed.
"""

from __future__ import annotations

import sqlite3

import pytest

from sidecar.core import study_modes
from sidecar.core.study_modes import POLICIES, Scope, StudySubMode, parse, policy_for
from sidecar.memory import study
from sidecar.memory.db import Database


async def _mapped(db: Database) -> int:
    subject_id = await study.ensure_subject(db, "Kestrel")
    await study.add_concepts(
        db, subject_id, [("Handshake", ""), ("Drift Window", ""), ("Seal Rotation", "")]
    )
    return subject_id


async def _state(db: Database, subject_id: int) -> study.StudyState:
    state = await study.state(db, subject_id)
    assert state is not None
    return state


# ── every field is read by something ───────────────────────────────────


@pytest.mark.parametrize("sub_mode", list(StudySubMode))
def test_every_sub_mode_has_a_policy_and_an_opener(sub_mode: StudySubMode) -> None:
    """A sub-mode with no opener is a button that sends nothing."""
    policy = POLICIES[sub_mode]

    assert policy.sub_mode is sub_mode
    assert policy.label
    assert policy.opener


def test_only_learn_has_an_empty_line() -> None:
    """The empty line is what makes Learn byte-identical to no sub-mode at all.
    Any other mode with an empty line is a button that does nothing."""
    empty = {m for m, p in POLICIES.items() if not p.line}

    assert empty == {StudySubMode.LEARN}


def test_an_unknown_sub_mode_lands_on_learn_rather_than_raising() -> None:
    """The caller is a panel button; an unrecognised string should not fail a
    click."""
    assert parse("nonsense") is None
    assert parse(None) is None
    assert parse("exam") is StudySubMode.EXAM
    assert policy_for(None).sub_mode is StudySubMode.LEARN


# ── Exam's one mechanical lever ────────────────────────────────────────


def test_exam_is_the_only_sub_mode_that_withholds_answers() -> None:
    """Everything else about a sub-mode is prose a model may ignore. This one
    cannot be, because a tool result is an instruction to a model — so the
    answers are kept out of the room rather than the model asked not to use
    them."""
    withholding = {m for m, p in POLICIES.items() if not p.reveal_answers}

    assert withholding == {StudySubMode.EXAM}


# ── what the prompt block names ────────────────────────────────────────


@pytest.mark.asyncio
async def test_learn_renders_exactly_what_study_rendered_before_sub_modes(
    database: Database,
) -> None:
    """Nobody who never opens the panel pays a token for this feature — the
    same guarantee NORMAL keeps for `ConversationMode`."""
    subject_id = await _mapped(database)
    state = await _state(database, subject_id)

    assert study.render(state) == study.render(state, policy_for(StudySubMode.LEARN))
    assert "\n" not in study.render(state), "Learn adds no second line"


@pytest.mark.asyncio
async def test_a_sub_mode_puts_its_own_line_in_the_block(database: Database) -> None:
    subject_id = await _mapped(database)
    state = await _state(database, subject_id)

    rendered = study.render(state, policy_for(StudySubMode.EXAM))

    assert "Exam:" in rendered
    assert "not teach" in rendered or "not hint" in rendered


@pytest.mark.asyncio
async def test_revision_does_not_pad_the_block_with_what_he_is_good_at(
    database: Database,
) -> None:
    """Revision is about what failed, and this block is paid on every turn."""
    subject_id = await _mapped(database)
    state = await _state(database, subject_id)
    strong, weak = state.concepts[0], state.concepts[1]
    for _ in range(5):
        await study.record_answer(database, strong.id, correct=True)
    await study.record_answer(database, weak.id, correct=False)

    after = await _state(database, subject_id)
    revision = study.render(after, policy_for(StudySubMode.REVISION))
    learn = study.render(after, policy_for(StudySubMode.LEARN))

    assert "Drift Window" in revision, "the shaky one is the point of revision"
    assert "solid:" not in revision
    assert "solid:" in learn, "or this proves nothing about revision"


@pytest.mark.asyncio
async def test_a_covered_scope_names_every_covered_concept(database: Database) -> None:
    """The one place the bounded list is deliberately unbounded: Rapid review
    is "one line on each concept he has covered", and it cannot do that from a
    list of three. Bounded by the map, which `curriculum.MAX_CONCEPTS` caps."""
    subject_id = await study.ensure_subject(database, "Wide")
    await study.add_concepts(database, subject_id, [(f"Concept {i}", "") for i in range(8)])
    state = await _state(database, subject_id)
    for concept in state.concepts:
        await study.record_answer(database, concept.id, correct=True)

    after = await _state(database, subject_id)
    rendered = study.render(after, policy_for(StudySubMode.RAPID))

    assert POLICIES[StudySubMode.RAPID].scope is Scope.COVERED
    for i in range(8):
        assert f"Concept {i}" in rendered


@pytest.mark.asyncio
async def test_a_next_scope_block_stays_short_however_big_the_syllabus(
    database: Database,
) -> None:
    """Learn is the common case and its block must not grow with the map."""
    subject_id = await study.ensure_subject(database, "Wide")
    await study.add_concepts(database, subject_id, [(f"Concept {i}", "") for i in range(40)])
    state = await _state(database, subject_id)
    for concept in state.concepts:
        await study.record_answer(database, concept.id, correct=False)

    rendered = study.render(await _state(database, subject_id), policy_for(StudySubMode.LEARN))

    assert len(rendered) < 300, rendered


# ── the three edits ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_deleting_a_subject_takes_its_map_and_its_mastery(database: Database) -> None:
    """Not recoverable, which is why the panel arms it with two clicks."""
    subject_id = await _mapped(database)
    state = await _state(database, subject_id)
    await study.record_answer(database, state.concepts[0].id, correct=True)

    assert await study.delete_subject(database, subject_id) is True

    assert await study.state(database, subject_id) is None
    remaining = await database.run(
        lambda c: c.execute("SELECT COUNT(*) FROM concept_mastery").fetchone()[0]
    )
    assert remaining == 0, "mastery must cascade, not be orphaned"


@pytest.mark.asyncio
async def test_deleting_something_that_is_not_there_is_false_not_an_error(
    database: Database,
) -> None:
    assert await study.delete_subject(database, 999) is False


@pytest.mark.asyncio
async def test_a_rename_is_what_resuming_then_matches_on(database: Database) -> None:
    subject_id = await study.ensure_subject(database, "week 3 infosec")

    assert await study.rename_subject(database, subject_id, "Information Security") is True

    assert await study.find_subject(database, "information security") == subject_id


@pytest.mark.asyncio
async def test_a_rename_onto_an_existing_name_is_refused(database: Database) -> None:
    """Two subjects with one name makes `find_subject` a coin flip."""
    first = await study.ensure_subject(database, "Networking")
    second = await study.ensure_subject(database, "Databases")

    assert await study.rename_subject(database, second, "networking") is False

    assert await study.find_subject(database, "Networking") == first


@pytest.mark.asyncio
async def test_resetting_a_concept_returns_it_to_never_introduced(database: Database) -> None:
    subject_id = await _mapped(database)
    concept = (await _state(database, subject_id)).concepts[0]
    await study.record_answer(database, concept.id, correct=True)
    await study.record_answer(database, concept.id, correct=True)

    assert await study.reset_concept(database, concept.id) is True

    after = (await _state(database, subject_id)).concepts[0]
    assert (after.level, after.asked, after.correct) == (0, 0, 0)


@pytest.mark.asyncio
async def test_the_subject_list_carries_progress_and_is_most_recent_first(
    database: Database,
) -> None:
    first = await _mapped(database)
    second = await study.ensure_subject(database, "Networking")
    await study.add_concepts(database, second, [("Subnets", "")])
    await study.touch(database, first)
    await study.touch(database, second)
    state = await _state(database, first)
    await study.record_answer(database, state.concepts[0].id, correct=True)

    subjects = await study.list_subjects(database)

    assert [s["name"] for s in subjects] == ["Networking", "Kestrel"]
    kestrel = next(s for s in subjects if s["name"] == "Kestrel")
    assert (kestrel["total"], kestrel["covered"]) == (3, 1)


def test_the_module_exposes_what_the_panel_needs() -> None:
    """`study_modes` is imported by the RPC layer by name; a rename that missed
    a call site would only show up as a click doing nothing."""
    assert hasattr(study_modes, "POLICIES")
    assert hasattr(study_modes, "parse")
    assert hasattr(study_modes, "policy_for")


@pytest.mark.asyncio
async def test_deleting_a_subject_keeps_the_conversations_about_it(database: Database) -> None:
    """**`ON DELETE SET NULL`, and the reason it is not a cascade.** Deleting a
    subject already destroys its map and every answer given against it. It must
    not also delete the conversations you had while learning it — those are
    yours, and they are still readable without the map.

    Mutation-checked: making the reference cascade deletes the chat.
    """
    subject_id = await study.ensure_subject(database, "Kestrel")

    def _seed(c: sqlite3.Connection) -> None:
        with c:
            c.execute(
                "INSERT INTO sessions (id, started_at, kind, study_subject_id) "
                "VALUES (?, ?, 'study', ?)",
                ("s_study", "2026-08-21T00:00:00Z", subject_id),
            )

    await database.run(_seed)
    await study.delete_subject(database, subject_id)

    row = await database.run(
        lambda c: c.execute(
            "SELECT id, kind, study_subject_id FROM sessions WHERE id = 's_study'"
        ).fetchone()
    )
    assert row is not None, "the conversation must survive its subject"
    assert row["kind"] == "study"
    assert row["study_subject_id"] is None
