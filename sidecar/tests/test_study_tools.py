"""`study_begin` and `study_check`, and the state she is handed without asking.

The two tools are the ends of the teach → check → record → adapt loop. What is
worth testing here is not that they run, but the three things that would pass
silently while being wrong: that the answer key never reaches the screen, that
a grade is actually written down, and that knowing where he is costs no step.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from sidecar.core import context as ctx
from sidecar.core.questions import Answer, Asked, Option, Question
from sidecar.core.study_modes import StudySubMode
from sidecar.memory import study
from sidecar.memory.db import Database
from sidecar.tools import registry
from sidecar.tools.registry import Tier, Tool, ToolContext
from sidecar.tools.study import QuizQuestion, study_begin, study_check

CTX = ToolContext(session_id="s_1", turn_id="t_1")


@pytest.fixture
def broker(monkeypatch: pytest.MonkeyPatch):
    """Stands in for `runtime.questions`, recording exactly what was shown."""

    class Fake:
        def __init__(self) -> None:
            self.shown: list[list[Question]] = []
            self.picks: list[str] = []
            self.timed_out = False
            #: Whether the last ask was told to read itself out. Recorded
            #: rather than ignored so the voice path is covered here too.
            self.spoken: bool | None = None

        async def ask(
            self,
            questions: list[Question],
            *,
            turn_id: str | None = None,
            spoken: bool = False,
        ) -> Any:
            self.shown.append(questions)
            self.spoken = spoken
            if self.timed_out:
                return Asked(answers=[], timed_out=True)
            picks = self.picks or [q.options[0].label for q in questions]
            return Asked(
                answers=[
                    Answer(question=q.question, chosen=[pick])
                    for q, pick in zip(questions, picks, strict=False)
                ]
            )

    fake = Fake()
    from sidecar.state import runtime

    monkeypatch.setattr(runtime, "questions", fake, raising=False)
    return fake


@pytest.fixture
def wired(monkeypatch: pytest.MonkeyPatch, database: Database) -> Database:
    from sidecar.state import runtime

    monkeypatch.setattr(runtime, "db", database, raising=False)
    return database


async def _mapped(db: Database, session_id: str | None = CTX.session_id) -> int:
    """A mapped subject, **stamped onto a session the way the real tool does.**

    `study_check` used to find its subject with `latest_subject_id` — the most
    recently touched one anywhere — and these tests relied on it, which is why
    none of them caught the leak: on 2026-09-01 a live quiz about transport
    security recorded `Data Pipelines` against a real data-engineering map in
    the real database. Setting up the way the product does is what makes the
    refusal testable at all.
    """
    subject_id = await study.ensure_subject(db, "Information Security")
    await study.add_concepts(
        db, subject_id, [("CIA Triad", ""), ("Access Control", ""), ("Replay Attacks", "")]
    )
    await study.touch(db, subject_id)
    if session_id is not None:
        from sidecar.memory.messages import ConversationStore

        store = ConversationStore(db)
        await store.ensure_session(session_id, kind="study")
        await store.set_study_subject(session_id, subject_id)
    return subject_id


def quiz(concept: str = "CIA Triad", correct: str = "Availability") -> QuizQuestion:
    return QuizQuestion(
        concept=concept,
        question="Which one is not confidentiality?",
        options=["Availability", "Encryption"],
        correct=correct,
    )


# ── registration ───────────────────────────────────────────────────────


@pytest.mark.parametrize("name", ["study_begin", "study_check"])
def test_the_tools_are_registered(name: str) -> None:
    """The import in `tools/__init__.py` is load-bearing: the decorator runs on
    import, and dropping the line silently removes the tool — which is exactly
    what happened to `finder` once, while every test still passed."""
    found = registry.get(name)
    assert isinstance(found, Tool)
    assert found.tier is Tier.AUTO, "neither tool touches the machine"


def test_they_survive_a_read_only_mode_ceiling() -> None:
    """Study's own `ToolPolicy.READ_ONLY` caps schemas at `Tier.SAFE`. Both
    tools sit below it — if either drifted upward it would vanish from the one
    mode built around it, and nothing else would say so."""
    offered = {s["function"]["name"] for s in registry.schemas(tier_max=Tier.SAFE)}

    assert {"study_begin", "study_check"} <= offered


def test_the_quiz_schema_describes_the_nested_shape() -> None:
    """A `list[QuizQuestion]` that came out as `{"type": "object"}` with no
    properties would leave the model guessing the field names — the gap the
    schema builder had before `ask_user` found it."""
    found = registry.get("study_check")
    assert found is not None
    schema = json.dumps(registry.schemas(tier_max=Tier.AUTO))

    assert "concept" in schema
    assert "correct" in schema


# ── the answer key stays here ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_the_answer_key_is_never_put_on_screen(wired: Database, broker: Any) -> None:
    """**The reason `QuizQuestion` is not `core.questions.Question`.** The
    broker broadcasts what it is given straight to the renderer, so a `correct`
    field on that model would ship the answer to the screen displaying the
    question."""
    await _mapped(wired)

    await study_check(CTX, [quiz()])

    shown = broker.shown[0][0]
    assert not hasattr(shown, "correct")
    payload = json.dumps(shown.model_dump())
    assert "correct" not in payload


# ── grading, and that it is written down ───────────────────────────────


@pytest.mark.asyncio
async def test_a_right_answer_raises_the_level_and_a_wrong_one_lowers_it(
    wired: Database, broker: Any
) -> None:
    subject_id = await _mapped(wired)

    broker.picks = ["Availability"]
    await study_check(CTX, [quiz(correct="Availability")])
    after_right = await study.state(wired, subject_id)

    broker.picks = ["Encryption"]
    await study_check(CTX, [quiz(correct="Availability")])
    after_wrong = await study.state(wired, subject_id)

    assert after_right is not None and after_wrong is not None
    assert after_right.concepts[0].level == 1
    assert after_wrong.concepts[0].asked == 2
    assert after_wrong.concepts[0].correct == 1


@pytest.mark.asyncio
async def test_the_summary_tells_the_model_what_was_missed(wired: Database, broker: Any) -> None:
    """Only `summary` reaches the model (§7.2), so the grade has to be in it —
    and the mode's own rule is to say which step failed rather than re-teach."""
    await _mapped(wired)
    broker.picks = ["Encryption"]

    result = await study_check(CTX, [quiz(correct="Availability")])

    assert result.ok
    assert "0 of 1 right" in result.summary
    assert "Availability" in result.summary


@pytest.mark.asyncio
async def test_a_question_about_something_not_on_the_map_still_grades(
    wired: Database, broker: Any
) -> None:
    """It has nowhere to be recorded, which is a bookkeeping loss. Dropping the
    grading too would be a much bigger one."""
    await _mapped(wired)

    result = await study_check(CTX, [quiz(concept="Steganography")])

    assert result.ok
    assert "1 of 1 right" in result.summary


@pytest.mark.asyncio
async def test_an_unanswered_quiz_is_not_a_failure_and_does_not_leak_the_answers(
    wired: Database, broker: Any
) -> None:
    """A timeout means he has not picked yet. Reporting it as an error would
    have her apologise for his silence; giving the answers would waste the
    question that is still on screen."""
    await _mapped(wired)
    broker.timed_out = True

    result = await study_check(CTX, [quiz(correct="Availability")])

    assert result.ok
    assert "not answered yet" in result.summary
    assert "Availability" not in result.summary


@pytest.mark.asyncio
async def test_a_malformed_question_costs_that_question_not_the_round(
    wired: Database, broker: Any
) -> None:
    """Arguments arrive as plain dicts — type hints drive the schema and
    nothing coerces what comes back. `ask_user`'s first live call died on
    exactly this."""
    await _mapped(wired)

    result = await study_check(
        CTX,
        [
            {"concept": "CIA Triad", "question": "?", "options": ["a", "b"], "correct": "a"},
            {"nonsense": True},
        ],
    )

    assert result.ok
    assert len(broker.shown[0]) == 1


@pytest.mark.asyncio
async def test_a_question_with_one_option_is_not_a_question(wired: Database, broker: Any) -> None:
    await _mapped(wired)

    result = await study_check(
        CTX, [QuizQuestion(concept="CIA Triad", question="?", options=["only"], correct="only")]
    )

    assert not result.ok
    assert result.error == "malformed"


# ── she knows where she is without spending a step ─────────────────────


@pytest.mark.asyncio
async def test_the_study_block_reaches_the_prompt_in_study_mode(wired: Database) -> None:
    """**Injected, not fetched.** Study's budget is 4 steps; answering "where
    were we" with a tool call would spend one of them plus a model round trip
    on something a single `SELECT` already knows.

    Mutating `_study_state` into a tool call — or simply returning `None` —
    fails this and nothing else.
    """
    subject_id = await _mapped(wired)
    state = await study.state(wired, subject_id)
    assert state is not None
    block = study.render(state)

    assembled = ctx.assemble([], mode=ctx.ConversationMode.STUDY, study_state=block)
    contents = " ".join(m.content for m in assembled)

    assert "Information Security" in contents
    assert "0 of 3 covered" in contents


def test_no_study_block_leaves_the_prompt_exactly_as_it_was() -> None:
    """Every conversation that is not a study session must be byte-identical
    to what it was before any of this existed — the same contract
    `retrieved_block` already keeps."""
    without = ctx.assemble([], mode=ctx.ConversationMode.NORMAL)
    with_none = ctx.assemble([], mode=ctx.ConversationMode.NORMAL, study_state=None)

    assert [m.content for m in without] == [m.content for m in with_none]


def test_the_mode_prompt_names_the_material_as_the_primary_source() -> None:
    """The sharpest requirement in the spec, and the reason Study's block was
    trimmed elsewhere to make room: a question the lecture does not cover must
    be answered as such, not from general knowledge as though it were in it."""
    prompt = ctx.stable_prefix(
        ctx.PersonaLevel.MINIMAL, has_tools=True, mode=ctx.ConversationMode.STUDY
    )[0].content

    assert "primary source" in prompt
    assert "does not cover" in prompt


def test_option_labels_are_carried_through_verbatim(wired: Database) -> None:
    """Grading matches on the option text, so a label the broker altered would
    make every answer wrong. `Option` takes it unchanged."""
    option = Option(label="Availability", description="")

    assert option.label == "Availability"


@pytest.fixture
def exam(monkeypatch: pytest.MonkeyPatch):
    """Put the session into Exam, through the real `ConversationService` API
    rather than by patching the tool — the point is that the sub-mode reaches
    it, not that a flag can be set."""

    class FakeService:
        def study_submode_for(self, session_id: str | None) -> StudySubMode:
            return StudySubMode.EXAM

    from sidecar.state import runtime

    monkeypatch.setattr(runtime, "conversation", FakeService(), raising=False)


@pytest.mark.asyncio
async def test_an_exam_never_reports_which_answer_was_right(
    wired: Database, broker: Any, exam: None
) -> None:
    """**Exam's one mechanical lever.** Everything else about a sub-mode is
    prose a model may ignore; this cannot be, because a tool result is an
    instruction to a model and "the answer was X" halfway through an exam is
    how the answer reaches his screen before the exam is over.

    Mutation-checked: making `reveal` unconditionally True fails exactly this
    and its sibling below.
    """
    await _mapped(wired)
    broker.picks = ["Encryption"]

    result = await study_check(CTX, [quiz(correct="Availability")])

    assert result.ok
    assert "Availability" not in result.summary, "the answer key leaked"
    assert "he chose" not in result.summary
    assert "0 of 1 right" in result.summary


@pytest.mark.asyncio
async def test_an_exam_still_says_what_to_review(wired: Database, broker: Any, exam: None) -> None:
    """Withholding the answers must not withhold the point of sitting it. The
    concept is named; the question, his answer and the right one are not."""
    await _mapped(wired)
    broker.picks = ["Encryption"]

    result = await study_check(CTX, [quiz(concept="CIA Triad", correct="Availability")])

    assert "To review: CIA Triad" in result.summary
    assert "must not invent" in result.summary


@pytest.mark.asyncio
async def test_an_exam_records_mastery_exactly_as_a_quiz_does(
    wired: Database, broker: Any, exam: None
) -> None:
    """Withholding is about what she is told, not about what is measured."""
    subject_id = await _mapped(wired)
    broker.picks = ["Encryption"]

    await study_check(CTX, [quiz(correct="Availability")])

    state = await study.state(wired, subject_id)
    assert state is not None
    assert (state.concepts[0].asked, state.concepts[0].correct) == (1, 0)


@pytest.mark.asyncio
async def test_an_ordinary_quiz_still_says_what_the_answer_was(
    wired: Database, broker: Any
) -> None:
    """The other direction, and the reason `reveal` fails open: a wrong default
    that silently withheld every answer from every ordinary quiz would be far
    worse than one that reveals during an exam nobody set."""
    await _mapped(wired)
    broker.picks = ["Encryption"]

    result = await study_check(CTX, [quiz(correct="Availability")])

    assert "Availability" in result.summary


# ── planning from a goal, which is where the A) B) C) bug came from ───


@pytest.fixture
def planner(monkeypatch: pytest.MonkeyPatch):
    """Stand in for the model call, so this tests the tool rather than a 7B."""
    from sidecar.memory import curriculum
    from sidecar.state import runtime

    class FakeBuilder:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def build(self, **kwargs: object) -> curriculum.CurriculumReport:
            report = curriculum.CurriculumReport(
                subject=str(kwargs.get("subject_hint") or "Study"),
                concepts_found=3,
                concepts_added=3,
                planned=not str(kwargs.get("source") or "").strip(),
                model="stub",
            )
            db = runtime.require_db()
            report.subject_id = await study.ensure_subject(db, report.subject)
            await study.add_concepts(
                db, report.subject_id, [("Probability", ""), ("SQL", ""), ("ML", "")]
            )
            return report

    monkeypatch.setattr(curriculum, "CurriculumBuilder", FakeBuilder)


@pytest.mark.asyncio
async def test_a_goal_with_no_file_plans_instead_of_refusing(
    wired: Database, planner: None
) -> None:
    """**The reported bug.** "hey im preparing for a data science internship
    technical interview, i want you to teach me in proper way" returned
    `no_material`, and the failure text told her to ask him for a file — so she
    asked, in prose, with A) B) C) D) options he could not click."""
    result = await study_begin(CTX, subject="data science internship technical interview")

    assert result.ok, result.error
    assert result.data is not None and result.data["planned"] is True


@pytest.mark.asyncio
async def test_a_planned_roadmap_is_shown_and_checked_before_teaching(
    wired: Database, planner: None
) -> None:
    """His own answer: show it, then check. A roadmap is a claim about what he
    should spend weeks on, and ten sessions built on the wrong one is
    expensive."""
    result = await study_begin(CTX, subject="data science interview")

    assert "ask_user" in result.summary
    assert "do not start teaching" in result.summary.lower()


@pytest.mark.asyncio
async def test_a_planned_roadmap_forbids_writing_the_options_as_letters(
    wired: Database, planner: None
) -> None:
    """The exact shape of the bug, named in the instruction that replaces it —
    a tool result is an instruction to a model, and this is the moment she was
    following one that did not mention the tool at all."""
    result = await study_begin(CTX, subject="data science interview")

    assert "A) B) C)" in result.summary


@pytest.mark.asyncio
async def test_a_planned_roadmap_says_it_was_planned_not_read(
    wired: Database, planner: None
) -> None:
    """Provenance reaches the model, not just the database. A roadmap presented
    as though it came from his own notes is the kind of quiet claim every
    anti-invention clause in `context.py` exists to stop."""
    result = await study_begin(CTX, subject="data science interview")

    assert "rather than from any material" in result.summary
    assert "planned it rather than read it" in result.summary


@pytest.mark.asyncio
async def test_a_named_file_that_is_missing_offers_to_plan_instead(
    wired: Database, planner: None
) -> None:
    """A dead end is what caused this whole bug once. Naming a file she cannot
    find should not produce a second one."""
    result = await study_begin(CTX, subject="networking", material="nope.pptx")

    assert not result.ok
    assert result.error == "not_found"
    assert "plan a roadmap" in result.summary


# ── quizzing out loud (2026-08-24) ────────────────────────────────────


async def test_a_typed_quiz_is_not_read_aloud(wired: Database, broker: Any) -> None:
    """The screen path is unchanged, which is the whole point of the flag."""
    await _mapped(wired)
    await study_check(CTX, [quiz()])
    assert broker.spoken is False


async def test_a_spoken_quiz_asks_out_loud(wired: Database, broker: Any) -> None:
    """**The gap that made hands-free study impossible.**

    `study_check` puts options on a screen and waits for a click; across a room
    there is neither. `ToolContext.spoken` is how the tool finds out, and the
    on-screen path stays live either way — whichever answer arrives first wins.
    """
    await _mapped(wired)
    await study_check(ToolContext(session_id="s_1", turn_id="t_1", spoken=True), [quiz()])
    assert broker.spoken is True


# ── a new study chat is not mid-session, and must not be told it is ────
#
# Every one of these carries the 2026-08-29 gate failure. `_study_block` used
# `latest_subject_id` — the most recently touched subject *globally* — so a
# brand-new study chat opened `[studying: <last week's subject>. next: ...]`.
# The model read that as a session already underway, carried on teaching the
# old subject, and never called `study_begin`. The lecture attached to the new
# chat was never mapped, and its quiz answers were recorded against the old
# subject's concepts, in the real database.


async def test_a_chat_that_has_started_nothing_is_not_told_it_is_studying(
    wired: Database,
) -> None:
    """The exact false claim, asserted against rather than around."""
    await _mapped(wired)  # a subject exists, touched by somebody else's chat
    block = study.render_not_started((("Information Security", 0, 3),))

    assert "studying:" not in block
    assert "next:" not in block
    assert "no subject started" in block
    # And it must point at the way out, or the model has nothing to do.
    assert "study_begin" in block


async def test_it_still_names_what_could_be_resumed(wired: Database) -> None:
    """Not-started is not the same as knowing nothing. "carry on with
    information security" has to keep working, so the prior subjects are
    named — as something to resume, never as something in progress."""
    block = study.render_not_started((("Information Security", 2, 7),))
    assert "Information Security" in block
    assert "2 of 7" in block
    assert "resume" in block


async def test_with_no_prior_subjects_it_asks_for_material_or_a_goal(
    wired: Database,
) -> None:
    block = study.render_not_started(())
    assert "study_begin" in block
    # A first-ever study chat has nothing to resume, and saying "previously:"
    # with an empty list is the kind of sentence that reads as a bug.
    assert "previously" not in block


async def test_the_session_owns_its_subject_not_the_clock(wired: Database) -> None:
    """`sessions.study_subject_id` is stamped by both study tools and was read
    by nothing until this bug. Two chats, two subjects, no bleed."""
    from sidecar.memory.messages import ConversationStore

    store = ConversationStore(wired)
    mine = await _mapped(wired)

    theirs = await store.ensure_session(None, kind="study")
    assert await study.session_subject_id(wired, theirs) is None

    await store.set_study_subject(theirs, mine)
    assert await study.session_subject_id(wired, theirs) == mine

    other = await store.ensure_session(None, kind="study")
    # The other chat is untouched by the first one's subject — which is the
    # whole property the global `latest_subject_id` could not provide.
    assert await study.session_subject_id(wired, other) is None


# ── a file attached this turn does not need the indexer ────────────────


def test_material_matches_a_file_attached_this_turn() -> None:
    """**The indexer cannot be a precondition for reading what he just gave.**

    `_resolve_material` looks in `file_index`, which a throttled background
    sweep fills — and which skips `AppData`, so nothing under `%TEMP%` is ever
    in it. `study_begin` therefore returned `not_found` for a file whose
    absolute path the turn had been handed, and the model fell back to
    planning a roadmap from the lecture's title.
    """
    from sidecar.tools.study import _attached_this_turn

    attached = (r"C:\Temp\aria\Vantril Transport Security Lecture 1.txt",)
    assert _attached_this_turn("Vantril Transport Security Lecture 1.txt", attached) == attached[0]
    # By full path, and by a partial name, which is what a model actually sends.
    assert _attached_this_turn(attached[0], attached) == attached[0]
    assert _attached_this_turn("Vantril Transport Security", attached) == attached[0]
    # And it does not invent a match.
    assert _attached_this_turn("some other lecture.pdf", attached) is None
    assert _attached_this_turn("anything", ()) is None


async def test_unindexed_material_is_read_from_disk(wired: Database, tmp_path) -> None:
    """`source_text` returned "" for anything with no chunks, and "no chunks"
    is the normal state of a file attached seconds ago."""
    from sidecar.memory import curriculum

    lecture = tmp_path / "lecture.txt"
    lecture.write_text("The drift window is 400 milliseconds.", encoding="utf-8")

    text = await curriculum.source_text(wired, str(lecture))
    assert "drift window" in text

    # An unreadable path is "no material", not an exception.
    assert await curriculum.source_text(wired, str(tmp_path / "gone.txt")) == ""


def _state(source_path: str | None) -> study.StudyState:
    return study.StudyState(
        subject_id=1,
        subject="Vantril Transport Security",
        source_path=source_path,
        concepts=(
            study.Concept(
                id=1, name="Drift Window", summary="", position=0, level=1, asked=1, correct=1
            ),
        ),
    )


def test_the_block_says_the_map_is_the_boundary_of_the_material() -> None:
    """**Observed live, and it is the worst failure this project has.**

    Asked "how does Vantril handle certificate revocation?" — a topic the
    lecture does not touch — she answered *"From what was in the document,
    Vantril uses OCSP..."*, attributing invented content to his own file, and
    the next sub-mode then examined him on it. Nothing anywhere had said that
    the map is all the material covers.
    """
    block = study.render(_state("C:/x/lecture.txt"))
    assert "the whole of this material" in block
    assert "not on it" in block
    # **On its own line, outside the bracket.** The first attempt put it
    # inside, as one more clause in a line that otherwise reads as status,
    # and the next live run still described OCSP as Vantril's own. An
    # instruction buried in a state blob reads as state.
    assert block.splitlines()[0].endswith("]")
    assert "The map above" in block.splitlines()[1]


def test_a_planned_roadmap_says_there_is_no_document_to_quote() -> None:
    """The two cases are not the same falsehood.

    A planned roadmap has no file behind it at all, so "from what was in the
    document" is invention twice over — and `source_path` being NULL is the
    only thing that tells them apart.
    """
    block = study.render(_state(None))
    assert "planned from his goal, not read from a file" in block
    assert "no document here" in block
    assert "the whole of this material" not in block


async def test_a_quiz_never_grades_against_another_chats_subject(
    wired: Database, broker: Any
) -> None:
    """**The leak, asserted against.**

    `study_check` resolved its subject with `latest_subject_id` — the most
    recently touched subject *anywhere* — so a quiz in a chat that had started
    nothing was graded against somebody else's map. Observed live on
    2026-09-01: a run about transport security moved `Data Pipelines` to
    level 1 in a real data-engineering subject, in the real database.

    **Refusing is the only safe answer.** Mastery is evidence, not a setting,
    and a row written against the wrong subject cannot be told from a real one
    afterwards.
    """
    # A subject exists and was touched most recently — by a different chat.
    theirs = await _mapped(wired, session_id="s_theirs")
    before = await study.state(wired, theirs)
    assert before is not None

    broker.picks = ["Availability"]
    result = await study_check(
        ToolContext(session_id="s_mine", turn_id="t_1"), [quiz()]
    )

    assert not result.ok
    assert result.error == "no_subject"
    assert "study_begin" in result.summary

    # And nothing was written. This is the half that matters: a refusal that
    # still recorded the answer would be a worse bug wearing an error message.
    after = await study.state(wired, theirs)
    assert after is not None
    assert [(c.name, c.level, c.asked) for c in after.concepts] == [
        (c.name, c.level, c.asked) for c in before.concepts
    ]


async def test_a_map_with_no_concepts_is_reported_as_a_failure(
    wired: Database, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A subject row is not a map, and saying otherwise wastes a whole session.

    Observed live: `study_begin` returned ok with `concepts_added=0`, she read
    "Built a map — 0 new concepts. Teach the first one now", found nothing to
    teach, called the same tool again with identical arguments, and the loop
    guard's note became her entire reply. `report.error` never fired, because
    the *subject* had been created — the subject is not the map.
    """
    from sidecar.memory import curriculum

    subject_id = await study.ensure_subject(wired, "Empty")

    async def _empty(self: object, **_kwargs: object) -> curriculum.CurriculumReport:
        return curriculum.CurriculumReport(
            subject="Empty", subject_id=subject_id, concepts_added=0, planned=True
        )

    monkeypatch.setattr(curriculum.CurriculumBuilder, "build", _empty)

    result = await study_begin(CTX, subject="something", material="")

    assert not result.ok
    assert result.error == "no_concepts"
    # The instruction matters as much as the flag: the live failure was her
    # retrying the identical call, which the loop guard then had to stop.
    assert "same arguments" in result.summary
