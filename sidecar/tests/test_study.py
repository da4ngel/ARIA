"""Study Mode's state: the map, the mastery rule, and the prompt line.

The mastery arithmetic is the part worth being strict about. A level is shown
to the user and acted on by the model — it decides what gets taught next — so a
number that can be reached by luck is worse than no number at all.
"""

from __future__ import annotations

import pytest

from sidecar.memory import study
from sidecar.memory.db import Database


async def _subject(db: Database, name: str = "Information Security") -> int:
    subject_id = await study.ensure_subject(db, name, "C:/lectures/infosec.pptx")
    await study.add_concepts(
        db,
        subject_id,
        [
            ("CIA Triad", "Confidentiality, integrity and availability."),
            ("Access Control", "Who may do what."),
            ("Replay Attacks", "Re-sending a captured message."),
        ],
    )
    return subject_id


# ── the map ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_a_subject_and_its_concepts_are_stored_in_order(database: Database) -> None:
    subject_id = await _subject(database)
    state = await study.state(database, subject_id)

    assert state is not None
    assert state.subject == "Information Security"
    assert [c.name for c in state.concepts] == ["CIA Triad", "Access Control", "Replay Attacks"]


@pytest.mark.asyncio
async def test_the_same_subject_is_not_created_twice(database: Database) -> None:
    first = await study.ensure_subject(database, "Networking")
    second = await study.ensure_subject(database, "networking")

    assert first == second


@pytest.mark.asyncio
async def test_re_running_extraction_does_not_duplicate_or_reset_the_map(
    database: Database,
) -> None:
    """`add_concepts` is additive and `UNIQUE(subject_id, name)` absorbs the
    repeats — a replace would cascade-delete `concept_mastery` and silently
    destroy every answer he had given."""
    subject_id = await _subject(database)
    concept = (await study.state(database, subject_id)).concepts[0]  # type: ignore[union-attr]
    await study.record_answer(database, concept.id, correct=True)

    added = await study.add_concepts(
        database, subject_id, [("CIA Triad", "again"), ("Firewalls", "new")]
    )
    state = await study.state(database, subject_id)

    assert added == 1, "only the genuinely new concept counts"
    assert state is not None
    assert [c.name for c in state.concepts].count("CIA Triad") == 1
    assert next(c for c in state.concepts if c.name == "CIA Triad").level == 1


@pytest.mark.asyncio
async def test_a_source_path_is_never_forgotten_by_a_later_resume(database: Database) -> None:
    """Resuming with "carry on with information security" carries no file
    name, and must not erase the one the map was built from."""
    subject_id = await study.ensure_subject(database, "Infosec", "C:/lectures/one.pptx")
    await study.ensure_subject(database, "Infosec")

    await study.add_concepts(database, subject_id, [("A", "")])
    state = await study.state(database, subject_id)

    assert state is not None
    assert state.source_path == "C:/lectures/one.pptx"


# ── resuming by what he actually says ──────────────────────────────────


@pytest.mark.asyncio
async def test_a_subject_is_found_by_a_phrase_that_contains_it(database: Database) -> None:
    subject_id = await study.ensure_subject(database, "Information Security")

    assert await study.find_subject(database, "information security") == subject_id
    assert await study.find_subject(database, "Information Security Fundamentals") == subject_id
    assert await study.find_subject(database, "photosynthesis") is None


@pytest.mark.asyncio
async def test_the_most_recently_studied_subject_is_the_one_resumed(database: Database) -> None:
    first = await study.ensure_subject(database, "Networking")
    second = await study.ensure_subject(database, "Databases")

    await study.touch(database, first)
    await study.touch(database, second)

    assert await study.latest_subject_id(database) == second


# ── the mastery rule ───────────────────────────────────────────────────


def test_mastery_cannot_be_reached_in_one_answer() -> None:
    """**The load-bearing rule.** One correct pick from four options is a 25%
    coin flip, and a level that treats it as mastery is a number that lies —
    which matters because the model reads the level and decides from it what
    to teach next."""
    assert study._next_level(0, correct=True) == 1  # noqa: SLF001

    level = 0
    for _ in range(study.MAX_LEVEL):
        level = study._next_level(level, correct=True)  # noqa: SLF001
    assert level == study.MAX_LEVEL, "five right answers reach the top"

    assert study._next_level(study.MAX_LEVEL, correct=True) == study.MAX_LEVEL  # noqa: SLF001


def test_a_wrong_answer_never_takes_a_concept_back_to_never_introduced() -> None:
    """0 means "never seen", and that stops being true once it is taught.
    Collapsing "got it wrong" into "never met it" would have her re-introduce
    from scratch something he has merely forgotten."""
    level = 1
    for _ in range(5):
        level = study._next_level(level, correct=False)  # noqa: SLF001

    assert level == study.MIN_INTRODUCED_LEVEL


@pytest.mark.asyncio
async def test_answers_move_the_level_and_keep_the_counts(database: Database) -> None:
    subject_id = await _subject(database)
    concept = (await study.state(database, subject_id)).concepts[0]  # type: ignore[union-attr]

    await study.record_answer(database, concept.id, correct=True)
    await study.record_answer(database, concept.id, correct=True)
    level = await study.record_answer(database, concept.id, correct=False)

    state = await study.state(database, subject_id)
    assert state is not None
    stored = state.concepts[0]
    assert level == 1
    assert (stored.asked, stored.correct) == (3, 2)


@pytest.mark.asyncio
async def test_a_later_right_answer_does_not_erase_that_he_got_it_wrong(
    database: Database,
) -> None:
    """The prompt promises to "bring back an earlier mistake when it becomes
    relevant", so the mistake has to survive being corrected."""
    subject_id = await _subject(database)
    concept = (await study.state(database, subject_id)).concepts[0]  # type: ignore[union-attr]

    await study.record_answer(database, concept.id, correct=False)
    await study.record_answer(database, concept.id, correct=True)

    row = await database.run(
        lambda c: c.execute(
            "SELECT last_wrong_at FROM concept_mastery WHERE concept_id = ?", (concept.id,)
        ).fetchone()
    )
    assert row["last_wrong_at"] is not None


# ── what to teach next ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_a_shaky_concept_is_taught_before_a_new_one(database: Database) -> None:
    """ "Build from first principles, in layers" — a layer with a hole in it is
    not a foundation, so weak beats new."""
    subject_id = await _subject(database)
    state = await study.state(database, subject_id)
    assert state is not None
    first, second = state.concepts[0], state.concepts[1]

    await study.record_answer(database, first.id, correct=True)
    await study.record_answer(database, second.id, correct=True)
    for _ in range(4):
        await study.record_answer(database, second.id, correct=True)

    after = await study.state(database, subject_id)
    assert after is not None
    assert after.next_concept is not None
    assert after.next_concept.name == "CIA Triad", "the shaky one, not the untouched third"


@pytest.mark.asyncio
async def test_nothing_left_to_teach_reports_none(database: Database) -> None:
    subject_id = await _subject(database)
    state = await study.state(database, subject_id)
    assert state is not None
    for concept in state.concepts:
        for _ in range(4):
            await study.record_answer(database, concept.id, correct=True)

    after = await study.state(database, subject_id)
    assert after is not None and after.next_concept is None


@pytest.mark.asyncio
async def test_being_taught_is_not_recorded_as_having_been_asked(database: Database) -> None:
    subject_id = await _subject(database)
    concept = (await study.state(database, subject_id)).concepts[0]  # type: ignore[union-attr]

    await study.mark_taught(database, concept.id)
    state = await study.state(database, subject_id)

    assert state is not None
    assert (state.concepts[0].level, state.concepts[0].asked) == (1, 0)


# ── the prompt line ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_the_prompt_line_names_where_he_is(database: Database) -> None:
    subject_id = await _subject(database)
    state = await study.state(database, subject_id)
    assert state is not None
    await study.record_answer(database, state.concepts[0].id, correct=False)

    rendered = study.render(await study.state(database, subject_id))  # type: ignore[arg-type]

    assert "Information Security" in rendered
    assert "1 of 3 covered" in rendered
    assert "CIA Triad" in rendered


@pytest.mark.asyncio
async def test_the_prompt_line_is_bounded_however_big_the_syllabus(database: Database) -> None:
    """It sits in the volatile prefix and is paid on every turn of a study
    session, so it must be a constant cost rather than one that grows with the
    number of concepts."""
    subject_id = await study.ensure_subject(database, "Everything")
    await study.add_concepts(database, subject_id, [(f"Concept {i}", "") for i in range(40)])
    state = await study.state(database, subject_id)
    assert state is not None
    for concept in state.concepts:
        await study.record_answer(database, concept.id, correct=False)

    rendered = study.render(await study.state(database, subject_id))  # type: ignore[arg-type]

    assert len(rendered) < 300, rendered
