"""Asking the user something and waiting for the answer.

Eyaas: *"if u are gonna ask a question and give 4 answers more like an MCQ …
in claude i should be able to select what i want, and one by one it moves to
next."*

**This is not new behaviour, it is a channel for behaviour BUILD_SPEC already
asked for.** §8.1's persona block lists `asks_before_assuming: true` beside
`disagrees_when_warranted`, and the same section warns that an agent tuned
purely to please "converges on agreement". Asking well is part of not doing
that. What was missing was a mechanism: until now she could only ask in prose,
and the answer cost a full round trip to type.

**Why a broker rather than the tool doing it itself.** `ToolContext` carries a
session id and a turn id and nothing else — no event bus. A tool body is
structurally unable to put something on screen. That constraint is what
`Tool.preview` exists for, and preview does not fit here: it runs *before*
approval, returns a dict, and cannot wait. So this owns the pending futures and
the broadcast, and the tool reaches it through `runtime`, the same way
`tools/research.py` already reaches process state.

The shape deliberately mirrors `PermissionEngine`'s pending-request machinery —
a dict of `asyncio.Future`, one broadcast, one `respond()` — because that is
the one ask-and-wait pattern this codebase already trusts. **Two differences,
both deliberate:**

1. **A timeout does not mean "no".** A confirmation that times out *must* deny:
   somebody who walked away has not agreed to anything. A question has no safe
   default — there is nothing to deny — so it resolves as *unanswered*, and the
   tool says so, and she proceeds with a stated assumption rather than
   pretending an answer arrived.
2. **It is ten minutes, not two.** 120s is right for "may I delete this",
   where the cost of waiting is a held lock. Here the cost of waiting is
   nothing, and a person reading four options and thinking about them is the
   feature working, not a stall.

Stop still releases it: the wait sits inside the turn task, so cancelling the
turn raises at the `await`. There is a test for that rather than a comment
hoping so — `PermissionEngine.cancel_all` exists and has no production caller,
and that gap is not one to copy.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import structlog
from pydantic import BaseModel, Field

from sidecar.rpc.events import Event

if TYPE_CHECKING:
    from sidecar.rpc.events import EventBus

log = structlog.get_logger(__name__)

#: Ten minutes. Long enough to read four options and think, short enough that a
#: turn abandoned overnight does not sit in memory until the app restarts.
QUESTION_TIMEOUT_S = 600.0

#: What the user is offered when none of the options fit.
#:
#: **Always appended, never modelled by the caller.** A multiple choice you
#: cannot escape is worse than a plain text box, because it converts "you asked
#: the wrong question" into "pick one anyway" — and a wrong answer given
#: confidently is exactly what the rest of this codebase spends its time
#: preventing.
OTHER_LABEL = "Other"

#: Caps, enforced rather than hoped for. Four questions is what fits on screen
#: without becoming a form, and four options is where a choice stops being
#: quicker to read than to type.
MAX_QUESTIONS = 4
MAX_OPTIONS = 4


class Option(BaseModel):
    """One answer the user can pick."""

    label: str
    #: Optional one-line consequence. Worth having: the difference between two
    #: options is usually *what happens next*, not what they are called.
    description: str = ""


class Question(BaseModel):
    """One question, with the options that answer it."""

    question: str
    #: Very short — it labels the question in a narrow column.
    header: str = ""
    options: list[Option] = Field(default_factory=list)
    multi_select: bool = False


class Answer(BaseModel):
    """What came back for one question."""

    question: str
    #: The chosen labels. More than one only when `multi_select` was set.
    chosen: list[str] = Field(default_factory=list)
    #: Set when the user picked "Other" and typed instead.
    other: str = ""

    @property
    def text(self) -> str:
        if self.other:
            return self.other
        return ", ".join(self.chosen)


class Asked(BaseModel):
    """The result of one `ask_user` call."""

    answers: list[Answer] = Field(default_factory=list)
    #: True when the ten minutes ran out. **Not the same as "no" and not the
    #: same as an error** — she simply did not get an answer, and needs to say
    #: what she assumed instead.
    timed_out: bool = False


@dataclass
class Pending:
    request_id: str
    questions: list[Question]
    future: asyncio.Future[list[Answer]]
    asked_at: float = field(default_factory=time.monotonic)


def normalise(questions: list[Question]) -> list[Question]:
    """Trim to the caps and give every question its escape hatch.

    Done here rather than in the tool so the broker's own guarantees hold
    whatever calls it: never more than `MAX_QUESTIONS`, never more than
    `MAX_OPTIONS` before "Other", and never a question with nothing to click.
    """
    cleaned: list[Question] = []
    for question in questions[:MAX_QUESTIONS]:
        options = [o for o in question.options if o.label.strip()][:MAX_OPTIONS]
        # A question whose options were all blank is still a real question —
        # it just becomes a free-text one rather than an error. Degrading is
        # right here: the model got the shape wrong, and refusing the whole
        # call would lose the question it was trying to ask.
        options = [o for o in options if o.label.strip().lower() != OTHER_LABEL.lower()]
        options.append(Option(label=OTHER_LABEL, description="Something else — type it."))
        cleaned.append(question.model_copy(update={"options": options}))
    return cleaned


class QuestionBroker:
    """Puts a question on screen and waits for the answer."""

    def __init__(self, bus: EventBus, timeout_s: float = QUESTION_TIMEOUT_S) -> None:
        self._bus = bus
        self._timeout_s = timeout_s
        self._pending: dict[str, Pending] = {}

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    async def ask(
        self, questions: list[Question], *, turn_id: str | None = None
    ) -> Asked:
        """Broadcast, then wait. Never raises for an ordinary outcome."""
        prepared = normalise(questions)
        if not prepared:
            return Asked(answers=[], timed_out=False)

        request_id = f"q_{uuid.uuid4().hex[:10]}"
        future: asyncio.Future[list[Answer]] = asyncio.get_running_loop().create_future()
        self._pending[request_id] = Pending(request_id, prepared, future)

        await self._bus.broadcast(
            Event.QUESTION_ASK,
            {
                "request_id": request_id,
                "turn_id": turn_id,
                "questions": [q.model_dump() for q in prepared],
            },
        )
        log.info("question.asked", request_id=request_id, count=len(prepared))

        try:
            answers = await asyncio.wait_for(future, timeout=self._timeout_s)
        except TimeoutError:
            # **Unanswered, not declined.** See the module docstring: there is
            # no safe default to fall back on, so the honest report is that
            # nobody answered.
            log.info("question.timed_out", request_id=request_id)
            return Asked(answers=[], timed_out=True)
        finally:
            self._pending.pop(request_id, None)

        log.info("question.answered", request_id=request_id, count=len(answers))
        return Asked(answers=answers, timed_out=False)

    def respond(self, request_id: str, answers: list[Answer]) -> bool:
        """Resolve a waiting question. False if it already went."""
        pending = self._pending.get(request_id)
        if pending is None or pending.future.done():
            return False
        pending.future.set_result(answers)
        return True

    def cancel_all(self) -> int:
        """Release every waiter as unanswered.

        Wired to shutdown, unlike `PermissionEngine.cancel_all`, which exists
        and is called only by its own tests. An in-flight turn is released by
        cancelling the turn task; this is for the case where there is no task
        left to cancel.
        """
        released = 0
        for pending in list(self._pending.values()):
            if not pending.future.done():
                pending.future.set_result([])
                released += 1
        self._pending.clear()
        return released


def render(asked: Asked, questions: list[Question]) -> str:
    """The one-line-per-question summary that goes back to the model.

    **`summary` is the only field the model ever sees** — `data` and `display`
    never enter the prompt (§7.2 names pasting tool output into the context as
    its second failure mode). So the chosen answers have to be here, in words,
    or the whole round trip was for nothing.
    """
    if asked.timed_out:
        return (
            "No answer — the question is still on screen and he has not picked "
            "yet. Do not ask again. Carry on with the most reasonable default "
            "and say plainly which one you assumed, so he can correct it."
        )
    if not asked.answers:
        return "He dismissed the question without answering."

    lines = [f"{answer.question} -> {answer.text or '(no answer)'}" for answer in asked.answers]
    unanswered = len(questions) - len(asked.answers)
    if unanswered > 0:
        lines.append(f"({unanswered} left unanswered — assume a sensible default and say so.)")
    return "He answered: " + "; ".join(lines)


__all__ = [
    "MAX_OPTIONS",
    "MAX_QUESTIONS",
    "OTHER_LABEL",
    "QUESTION_TIMEOUT_S",
    "Answer",
    "Asked",
    "Option",
    "Question",
    "QuestionBroker",
    "normalise",
    "render",
]
