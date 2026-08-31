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

import asyncio
import re
import sqlite3
from pathlib import Path

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

Call this at the start of a study session, and give it whatever he gave you:

- **A file he attached** — pass its name as `material`. The map is then built
  from what that material actually teaches.
- **Just a goal** — "prepare me for a data science interview", "teach me
  transformers". Leave `material` empty and it plans a roadmap for the goal.
  **Do not ask him for a file first.** A roadmap is a better answer than a
  question, and he can attach material later; it merges into the same map.
- **Neither, because he is carrying on** — "back to networking". It brings
  back the map and his progress.

Call it ONCE per session, before teaching. It is not needed to answer a
one-off question, and calling it again mid-session wastes a step — after the
first call, what he knows is already in front of you.

`subject` should be what he actually said he wants to learn, in his words. It
is what resuming matches on later."""


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


async def _remember_subject(db: object, ctx: ToolContext, subject_id: int) -> None:
    """Note on this conversation which subject it last worked on.

    **A record, not a binding.** The chat may roam and the live subject is
    still whichever was most recently touched anywhere; this only lets the
    Study tab group a chat under where it got to. It is why deleting a subject
    uses `ON DELETE SET NULL` rather than cascading into conversations.

    Off the critical path in the sense that matters: a failure here costs a
    grouping, and must never cost the tool call that was actually asked for.
    """
    from sidecar.state import runtime

    service = runtime.conversation
    if service is None or ctx.session_id is None:
        return
    try:
        await service.store.set_study_subject(ctx.session_id, subject_id)
    except Exception:  # noqa: BLE001 — a grouping is not worth failing a turn
        log.warning("study.subject_stamp_failed", exc_info=True)


def _attached_this_turn(material: str, attachments: tuple[str, ...]) -> str | None:
    """The file he attached *in this message*, matched by name.

    Checked **before** `file_index`, because the index is filled by a
    throttled background sweep that pauses while she is answering and skips
    `AppData` entirely — so a lecture attached seconds ago, or one living
    under `%TEMP%`, is not in it. The turn was handed the absolute path;
    requiring the indexer to have caught up first is the same "a file she
    just touched is invisible for 45 seconds" trap `finder._Cache` already
    had, arriving from a different direction.
    """
    clean = material.strip().strip('"').casefold()
    if not clean or not attachments:
        return None
    for raw in attachments:
        name = Path(raw).name.casefold()
        if clean in (name, raw.casefold()) or clean in name:
            return raw
    return None


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
        subject: What he wants to learn, in his own words — "information
            security", "week 3 networking", "prepare me for a data science
            interview". Used to find the subject again when he asks to carry
            on, and used as the goal when there is no material to read.
        material: The lecture or notes to build the map from, by file name.
            Leave empty when he has not given you a file — a roadmap is then
            planned from the subject itself. Never ask him for a file first.
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
            await _remember_subject(db, ctx, existing)
            return ToolResult(
                ok=True,
                summary=f"Resuming. {_describe(state)}",
                data={"subject_id": existing, "resumed": True},
                display={"kind": "study_map", "subject": state.subject, "resumed": True},
            )

    # **No material is not a dead end any more, and that was the bug.** This
    # used to refuse and tell her to ask him for a file — so she asked, in
    # prose, with A) B) C) D) options that could not be clicked. A goal is
    # enough to plan a roadmap from, and planning one is a better answer to
    # "teach me for my interview" than a question about attachments.
    path: str | None = None
    if material.strip():
        path = _attached_this_turn(material, ctx.attachments) or await db.run(
            lambda c: _resolve_material(c, material)
        )
        if path is None:
            return ToolResult(
                ok=False,
                summary=(
                    f"I could not find '{material}' among the files I have read. "
                    "Ask him to attach it to the conversation, then try again — "
                    "or call this again with no material and I will plan a "
                    "roadmap from the subject instead."
                ),
                error="not_found",
            )

    text = await curriculum.source_text(db, path) if path else ""
    # Which cloud models have a key, so extraction can prefer one. Absent
    # availability is not an error — it means local, which is what
    # `choose_model` falls back to anyway.
    usable = runtime.availability.usable() if runtime.availability else set()
    builder = curriculum.CurriculumBuilder(db, runtime.providers, runtime.local_models)
    report = await builder.build(
        source=text,
        goal=subject,
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
    await _remember_subject(db, ctx, report.subject_id)
    state = await study.state(db, report.subject_id)

    # **A map with nothing on it is not a map, and reporting it as one is how
    # a whole session goes wrong quietly.** Observed live: `study_begin`
    # returned ok with `concepts_added=0` (the extraction produced nothing
    # usable), she read "Built a map — 0 new concepts. Teach the first one
    # now", found nothing to teach, called the same tool again with the same
    # arguments, and the loop guard's own note became her entire reply.
    #
    # `report.error` did not fire because the subject row *was* created. The
    # subject is not the map; the concepts are.
    if state is None or not state.concepts:
        return ToolResult(
            ok=False,
            summary=(
                f"A subject for {report.subject!r} exists but nothing could be "
                f"read into it — no concepts were extracted"
                + (f" from {material}." if not report.planned else " from that goal.")
                + " Do not call this again with the same arguments. Ask him for "
                "the material, or for a narrower goal, and say what happened."
            ),
            error="no_concepts",
        )

    described = _describe(state)
    if report.planned:
        # **Show it, then check — his own answer.** A roadmap is a claim about
        # what he should spend weeks on, and ten sessions built on the wrong one
        # is expensive. The options go through `ask_user`, never written out as
        # A) B) C) in the reply: that is the whole point of having the tool, and
        # writing them as letters is the bug this branch exists to stop.
        summary = (
            f"Planned a roadmap for {report.subject} — {report.concepts_added} "
            f"concepts, from the goal rather than from any material of his.\n"
            f"{described}\n"
            "Show him the roadmap as a numbered list, say plainly that you planned "
            "it rather than read it out of his own notes, then call `ask_user` once "
            "with options like: start with the first one / reorder it / it is too "
            "broad, narrow it / add something missing. **Write the options through "
            "`ask_user`, never as A) B) C) in your reply, and do not start teaching "
            "until he has answered.**"
        )
    else:
        summary = (
            f"Built a map of {report.subject} from {material} "
            f"({report.concepts_added} new concepts).\n{described}\n"
            "Teach the first one now. Do not list the map back at him — start teaching."
        )

    return ToolResult(
        ok=True,
        summary=summary,
        data={
            "subject_id": report.subject_id,
            "added": report.concepts_added,
            "planned": report.planned,
        },
        display={
            "kind": "study_map",
            "subject": report.subject,
            "planned": report.planned,
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

    # **This chat's own subject, never the most recent one anywhere.**
    #
    # It used to be `latest_subject_id`, and on 2026-09-01 that graded a quiz
    # about Vantril transport security against Eyaas's real data-engineering
    # map — `Data Pipelines` went to level 1 on the strength of an answer
    # about something else entirely. `sessions.study_subject_id` exists to
    # stop precisely this and the *prompt* path was fixed to read it on
    # 2026-08-29; the tool that actually writes mastery was not, so the same
    # bug carried on writing to the same table by a different route.
    #
    # **Refusing is the only safe answer when there is none.** Mastery is
    # evidence, not a setting: a row written against the wrong subject cannot
    # be told from a real one afterwards.
    subject_id = (
        await study.session_subject_id(db, ctx.session_id) if ctx.session_id else None
    )
    if subject_id is None:
        return ToolResult(
            ok=False,
            summary=(
                "Nothing has been started in this chat, so there is no map to "
                "record answers against. Call study_begin with his material or "
                "his goal first — do not grade against another chat's subject."
            ),
            error="no_subject",
        )
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
        # **Across a room there is no screen to click.** The options are still
        # broadcast and still clickable — whichever answer arrives first wins —
        # but on a spoken turn they are read out too, and the listener resolves
        # the question from speech instead of starting a new turn.
        spoken=ctx.spoken,
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
        await _remember_subject(db, ctx, subject_id)

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


#: Where an export lands. A named folder rather than wherever the sidecar
#: happens to be running, which is the repo.
EXPORT_FOLDER = "Documents"
EXPORT_SUBFOLDER = "ARIA Study"


@tool(
    name="study_export",
    # **SAFE, not CONFIRM, and the difference is the never-overwrite
    # guarantee.** `write_file` is CONFIRM because it takes an arbitrary path
    # and replaces whatever is there; rule 5 names overwriting. This writes a
    # generated name into one folder and steps aside if that name is taken, so
    # nothing of his can be destroyed by it.
    tier=Tier.SAFE,
    description=(
        "Save a subject's roadmap or knowledge map to a file he can keep. "
        "format 'md' for Markdown, or 'html' for a page that prints to PDF "
        "with Ctrl+P. Use when asked to export, save, download or print what "
        "he is studying."
    ),
)
async def study_export(ctx: ToolContext, subject: str = "", format: str = "md") -> ToolResult:
    """Save a knowledge map to a file.

    Args:
        subject: Which subject, by name. Leave empty for the current one.
        format: "md" for Markdown, or "html" for a printable page
    """
    from sidecar.memory import study_export as render
    from sidecar.state import runtime

    db = runtime.db
    if db is None:
        return ToolResult(
            ok=False, summary="Study is not available in this session.", error="unavailable"
        )

    # Same rule as `study_check`: this chat's subject, not the most recently
    # touched one anywhere. Exporting somebody else's map is a smaller harm
    # than grading against it, and it is the same mistake.
    subject_id = (
        await study.find_subject(db, subject)
        if subject.strip()
        else (await study.session_subject_id(db, ctx.session_id) if ctx.session_id else None)
    )
    if subject_id is None:
        return ToolResult(
            ok=False,
            summary=(
                f"I have no map for {subject!r}. Call study_begin first, or ask "
                f"him which subject he means."
                if subject.strip()
                else "Nothing has been studied yet, so there is no map to export."
            ),
            error="no_subject",
        )

    state = await study.state(db, subject_id)
    if state is None or not state.concepts:
        return ToolResult(
            ok=False, summary="That subject has no concepts to export yet.", error="empty"
        )

    chosen = "html" if format.strip().lower() in {"html", "pdf", "print"} else "md"
    text, extension = render.render(state, chosen)
    path = await asyncio.to_thread(_write_export, state.subject, text, extension)
    if path is None:
        return ToolResult(
            ok=False,
            summary="I could not find your Documents folder to save it in.",
            error="no_folder",
        )

    printable = (
        " Open it and press Ctrl+P to save it as a PDF." if chosen == "html" else ""
    )
    return ToolResult(
        ok=True,
        data={"path": str(path), "format": chosen, "concepts": len(state.concepts)},
        summary=(
            f"Saved {state.subject} ({len(state.concepts)} concepts) to {path}.{printable}"
        ),
        display={"kind": "export", "path": str(path), "format": chosen},
    )


def _write_export(subject: str, text: str, extension: str) -> Path | None:
    """Write it, never over anything. Blocking, so callers use a thread."""
    from sidecar.tools.files import known_folder
    from sidecar.tools.organize import _unique

    root = known_folder(EXPORT_FOLDER)
    if root is None:
        return None
    folder = root / EXPORT_SUBFOLDER
    folder.mkdir(parents=True, exist_ok=True)

    # A subject name is free text and reaches the filesystem here.
    safe = re.sub(r'[<>:"/\|?*]', "-", subject).strip() or "study"
    target = _unique(folder / f"{safe}{extension}", set())
    target.write_text(text, encoding="utf-8")
    log.info("study.exported", path=str(target), chars=len(text))
    return target
