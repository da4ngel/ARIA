"""`study_begin` and `study_check` — the two things Study Mode could not do.

Study Mode has had a prompt since modes shipped, and that prompt promises to
find out what he already knows and to bring back an earlier mistake when it
becomes relevant. Neither was true, because nothing recorded either. These two
tools are the ends of the loop the mode is built around: **teach → check →
record → adapt**. The recording is what makes the next session different from
the first.

Both are `Tier.AUTO`. Neither touches the machine — one reads a file this
program already indexed, the other puts a question on screen.
"""

from __future__ import annotations

import sqlite3

import structlog
from pydantic import BaseModel, Field, ValidationError

from sidecar.core.questions import Option, Question
from sidecar.core.study_modes import policy_for as study_policy_for
from sidecar.memory import curriculum, study
from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

#: The broker's own cap. Named again here because `study_check`'s docstring
#: quotes it to the model, and two numbers that can disagree is one too many.
MAX_QUIZ_QUESTIONS = 4


class QuizQuestion(BaseModel):
    """One multiple-choice question, with the answer key attached.

    Deliberately **not** `core/questions.Question`. That model is broadcast to
    the renderer as-is, so a `correct` field on it would ship the answer key to
    the screen the question is displayed on. The two are converted here, and
    the key never leaves the sidecar.
    """

    concept: str = Field(description="Which concept from the map this tests.")
    question: str
    options: list[str] = Field(description="2-4 answers, one of which is right.")
    correct: str = Field(description="The option text that is correct, copied exactly.")


_BEGIN_DESCRIPTION = """Start or resume teaching a subject.

Call this at the start of a study session — when he attaches lecture material
and asks to be taught it, or when he says to carry on with something ("carry on
with information security", "back to networking"). It builds a map of what the
material teaches, or brings back the map and his progress if the subject
already exists.

Call it ONCE per session, before teaching. It is not needed to answer a
one-off question, and calling it again mid-session wastes a step — after the
first call, what he knows is already in front of you.

`material` is the file he attached. Give its name exactly as he gave it; the
path is worked out here."""


_CHECK_DESCRIPTION = f"""Ask him a question about what you just taught, and
record whether he got it right.

**This is how anything is ever learned here.** A study turn that explains
something and stops has taught nothing you can build on — the mode's own
standard is that he could reproduce the idea without you, and the only way to
find out is to ask. Use it after teaching a concept, and when he says to quiz
or test him.

Up to {MAX_QUIZ_QUESTIONS} at once, stepped one at a time on screen. Each needs
the `concept` it tests, named as it appears in the map, so the answer is
recorded against the right thing.

Ask about the idea, not the wording — a question answerable by matching a
phrase from what you just wrote tests reading, not understanding. Make the
wrong options plausible: an obviously silly option removes itself and turns
four choices into two."""


def _resolve_material(conn: sqlite3.Connection, material: str) -> str | None:
    """A file name or path as the model gave it, resolved to an indexed path.

    The model only ever sees a *name* — `attachments._read_document` puts
    `"lecture.pptx: ..."` in the excerpt and never the path — so a bare name
    has to work. Exact path first, then a name match against `file_index`,
    newest indexed first, because "the lecture" means the one just handed over.
    """
    clean = material.strip().strip('"')
    if not clean:
        return None
    exact = conn.execute("SELECT path FROM file_index WHERE path = ?", (clean,)).fetchone()
    if exact is not None:
        return str(exact["path"])
    row = conn.execute(
        "SELECT path FROM file_index WHERE name = ? COLLATE NOCASE "
        "OR name LIKE '%' || ? || '%' COLLATE NOCASE "
        "ORDER BY indexed_at DESC LIMIT 1",
        (clean, clean),
    ).fetchone()
    return None if row is None else str(row["path"])


def _describe(state: study.StudyState) -> str:
    """What comes back to the model after a begin — the map and where he is."""
    lines = [f"Subject: {state.subject} ({len(state.concepts)} concepts)."]
    for concept in state.concepts:
        mark = {0: "not started"}.get(concept.level, f"level {concept.level}/5")
        lines.append(f"- {concept.name} — {mark}")
    nxt = state.next_concept
    if nxt is None:
        lines.append("Everything on the map has been covered. Test him on the weakest parts.")
    else:
        lines.append(f"Teach next: {nxt.name}.")
    if state.weak:
        shaky = ", ".join(c.name for c in state.weak)
        lines.append(f"He has been shaky on: {shaky}. Work these back in rather than re-teaching.")
    return "\n".join(lines)


@tool(name="study_begin", tier=Tier.AUTO, description=_BEGIN_DESCRIPTION)
async def study_begin(ctx: ToolContext, subject: str, material: str = "") -> ToolResult:
    """Build or resume a subject's concept map.

    Args:
        subject: What he is studying, in his own words — "information
            security", "week 3 networking". Used to find the subject again
            when he asks to carry on.
        material: The lecture or notes to build the map from, by file name.
            Leave empty to resume a subject that already has a map.
    """
    from sidecar.state import runtime

    db = runtime.db
    if db is None:
        return ToolResult(
            ok=False,
            summary="Memory is not available, so I cannot keep track of a study session.",
            error="unavailable",
        )

    # Resume first, and cheaply. A subject that already has a map must not pay
    # for a second extraction just because he mentioned the file again — the
    # map is the expensive part, and `add_concepts` is additive, so a repeat
    # run costs a model call to learn nothing.
    existing = await study.find_subject(db, subject)
    if existing is not None:
        state = await study.state(db, existing)
        if state is not None and state.concepts:
            await study.touch(db, existing)
            return ToolResult(
                ok=True,
                summary=f"Resuming. {_describe(state)}",
                data={"subject_id": existing, "resumed": True},
                display={"kind": "study_map", "subject": state.subject, "resumed": True},
            )

    if not material.strip():
        return ToolResult(
            ok=False,
            summary=(
                f"There is no map for '{subject}' yet and no material was named. "
                "Ask him to attach the lecture, slides or notes he wants to work "
                "from, then call this again with the file name."
            ),
            error="no_material",
        )

    path = await db.run(lambda c: _resolve_material(c, material))
    if path is None:
        return ToolResult(
            ok=False,
            summary=(
                f"I could not find '{material}' among the files I have read. "
                "Ask him to attach it to the conversation, then try again."
            ),
            error="not_found",
        )

    text = await curriculum.source_text(db, path)
    # Which cloud models have a key, so extraction can prefer one. Absent
    # availability is not an error — it means local, which is what
    # `choose_model` falls back to anyway.
    usable = runtime.availability.usable() if runtime.availability else set()
    builder = curriculum.CurriculumBuilder(db, runtime.providers, runtime.local_models)
    report = await builder.build(
        source=text,
        subject_hint=subject,
        source_path=path,
        usable_models=usable,
    )
    if report.error or report.subject_id is None:
        return ToolResult(
            ok=False,
            summary=report.error or "The map could not be built.",
            error="build_failed",
        )

    await study.touch(db, report.subject_id)
    state = await study.state(db, report.subject_id)
    described = _describe(state) if state is not None else ""
    return ToolResult(
        ok=True,
        summary=(
            f"Built a map of {report.subject} from {material} "
            f"({report.concepts_added} new concepts).\n{described}\n"
            "Teach the first one now. Do not list the map back at him — start teaching."
        ),
        data={"subject_id": report.subject_id, "added": report.concepts_added},
        display={
            "kind": "study_map",
            "subject": report.subject,
            "concepts": [c.name for c in (state.concepts if state else ())],
        },
    )


@tool(name="study_check", tier=Tier.AUTO, description=_CHECK_DESCRIPTION)
async def study_check(ctx: ToolContext, questions: list[QuizQuestion]) -> ToolResult:
    """Quiz him on named concepts and record how it went.

    Args:
        questions: The questions to ask, in order. Each needs the `concept` it
            tests, the `question` itself, 2-4 `options`, and `correct` — the
            option text that is right, copied exactly from `options`.
    """
    from sidecar.state import runtime

    db, broker = runtime.db, runtime.questions
    if db is None or broker is None:
        return ToolResult(
            ok=False,
            summary="I cannot put a question on screen right now. Ask him directly instead.",
            error="unavailable",
        )

    # Same lesson `ask_user` learned live: type hints drive the schema the model
    # is shown and nothing coerces what comes back, so these arrive as dicts.
    # Validated one at a time — a malformed entry should cost that question
    # rather than the whole round.
    prepared: list[QuizQuestion] = []
    for raw in questions:
        try:
            prepared.append(
                raw if isinstance(raw, QuizQuestion) else QuizQuestion.model_validate(raw)
            )
        except ValidationError as exc:
            log.info("study.malformed_question", error=str(exc))

    prepared = [q for q in prepared if len(q.options) >= 2][:MAX_QUIZ_QUESTIONS]
    if not prepared:
        return ToolResult(
            ok=False,
            summary=(
                "Those questions were not in a shape I could show. Each needs a "
                "`concept`, a `question`, at least two `options`, and `correct` "
                "copied exactly from the options."
            ),
            error="malformed",
        )

    subject_id = await study.latest_subject_id(db)
    # **Exam's one mechanical lever** (`core/study_modes.py`). Everything else
    # about a sub-mode is prompt text a model may or may not follow; this
    # cannot be, because a tool result is an instruction to a model, and
    # handing it "the answer was X" halfway through an exam is exactly how the
    # answer reaches his screen before the exam is over. The information is
    # kept out of the room rather than the model asked not to use it.
    #
    # Fails *open* — no conversation service means no sub-mode, which means
    # Learn, which reveals. The alternative fails closed and silently withholds
    # every answer from every ordinary quiz, which is the far worse direction
    # for a wrong default here.
    service = runtime.conversation
    reveal = (
        study_policy_for(service.study_submode_for(ctx.session_id)).reveal_answers
        if service is not None
        else True
    )
    asked = await broker.ask(
        [
            Question(
                question=q.question,
                header=q.concept[:12],
                options=[Option(label=o, description="") for o in q.options],
            )
            for q in prepared
        ],
        turn_id=ctx.turn_id,
    )

    if asked.timed_out:
        return ToolResult(
            ok=True,
            summary=(
                "He has not answered yet — the questions are still on screen. Do not "
                "ask again and do not give the answers. Wait, or say something short "
                "that leaves them open."
            ),
            data={"timed_out": True},
        )

    # Grading is here, not in the broker: the broker never learns the answer
    # key, and the caller that wrote the question is the only thing that knows
    # it. Matching is on the option text, case-folded — the label came from
    # `options`, so anything else is a mis-copy in `correct` rather than a
    # near miss by him.
    lines: list[str] = []
    missed: list[str] = []
    right = 0
    for question, answer in zip(prepared, asked.answers, strict=False):
        chosen = answer.text.strip()
        correct = chosen.casefold() == question.correct.strip().casefold()
        right += 1 if correct else 0
        if reveal:
            verdict = "correct" if correct else f"wrong (the answer was: {question.correct})"
            lines.append(f"{question.concept}: he chose '{chosen}' — {verdict}")
        elif not correct:
            # The concept, so she knows what to tell him to review. Not the
            # question, not his answer, and above all not the right one.
            missed.append(question.concept)

        if subject_id is None:
            continue
        concept_id = await study.concept_by_name(db, subject_id, question.concept)
        if concept_id is None:
            # A question about something not on the map is still a fair
            # question; it just has nowhere to be recorded. Not an error —
            # losing the grading would be worse than losing the bookkeeping.
            log.info("study.unmapped_concept", concept=question.concept)
            continue
        await study.record_answer(db, concept_id, correct=correct)

    if subject_id is not None:
        await study.touch(db, subject_id)

    unanswered = len(prepared) - len(asked.answers)
    if unanswered > 0:
        lines.append(f"({unanswered} left unanswered.)")

    if not reveal:
        lines.append(f"To review: {', '.join(missed)}." if missed else "Nothing to review.")
        tail = (
            "The exam is over. Give him the score and what to review — you do not "
            "have the individual answers and must not invent them."
        )
    elif right == len(asked.answers) and asked.answers:
        tail = "He got them all. Move on to the next concept."
    else:
        tail = (
            "Say which step of his reasoning went wrong, not the whole thing again, "
            "then give him another way in."
        )
    return ToolResult(
        ok=True,
        summary=f"{right} of {len(asked.answers)} right.\n" + "\n".join(lines) + f"\n{tail}",
        data={"right": right, "asked": len(asked.answers)},
        display={
            "kind": "study_result",
            "right": right,
            "asked": len(asked.answers),
        },
    )
