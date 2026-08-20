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
from sidecar.tools.study import QuizQuestion, study_check

CTX = ToolContext(session_id="s_1", turn_id="t_1")


@pytest.fixture
def broker(monkeypatch: pytest.MonkeyPatch):
    """Stands in for `runtime.questions`, recording exactly what was shown."""

    class Fake:
        def __init__(self) -> None:
            self.shown: list[list[Question]] = []
            self.picks: list[str] = []
            self.timed_out = False

        async def ask(self, questions: list[Question], *, turn_id: str | None = None) -> Any:
            self.shown.append(questions)
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


async def _mapped(db: Database) -> int:
    subject_id = await study.ensure_subject(db, "Information Security")
    await study.add_concepts(
        db, subject_id, [("CIA Triad", ""), ("Access Control", ""), ("Replay Attacks", "")]
    )
    await study.touch(db, subject_id)
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
