"""The ask-and-wait broker: what it guarantees, and what it refuses to assume.

The interesting property here is the one that differs from
`PermissionEngine._ask`, which this is otherwise modelled on: **a timeout is
not a "no".** A confirmation that times out must deny, because somebody who
walked away has not agreed to anything. A question has no safe default, so the
honest outcome is "nobody answered" — and the difference is load-bearing,
because one of them makes her carry on with a stated assumption and the other
would make her apologise for a refusal that never happened.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from sidecar.core.questions import (
    MAX_OPTIONS,
    MAX_QUESTIONS,
    OTHER_LABEL,
    Answer,
    Asked,
    Option,
    Question,
    QuestionBroker,
    normalise,
    render,
)


class FakeBus:
    """Records broadcasts. The real one is fire-and-forget over websockets."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, dict[str, Any]]] = []

    async def broadcast(self, method: Any, params: dict[str, Any]) -> None:
        self.sent.append((str(method), params))


def a_question(text: str = "Which one?", options: int = 2) -> Question:
    return Question(
        question=text,
        header="Pick",
        options=[Option(label=f"Option {i}") for i in range(options)],
    )


# ── normalising ───────────────────────────────────────────────────────


def test_every_question_gets_an_escape_hatch() -> None:
    """**The guarantee that keeps a badly-framed question from being a trap.**

    A multiple choice you cannot escape converts "you asked the wrong
    question" into "pick one anyway", and a wrong answer given confidently is
    what the rest of this codebase spends its time preventing.
    """
    for question in normalise([a_question(), a_question()]):
        assert question.options[-1].label == OTHER_LABEL


def test_the_model_cannot_add_its_own_other() -> None:
    """Otherwise there would be two, and one of them would do nothing."""
    asked = normalise(
        [Question(question="?", options=[Option(label="other"), Option(label="Keep")])]
    )
    labels = [o.label for o in asked[0].options]
    assert labels.count(OTHER_LABEL) == 1
    assert "Keep" in labels


def test_the_caps_are_enforced_not_hoped_for() -> None:
    too_many = [a_question(f"Q{i}", options=9) for i in range(9)]
    cleaned = normalise(too_many)

    assert len(cleaned) == MAX_QUESTIONS
    for question in cleaned:
        # The cap, plus the "Other" that is always added on top of it.
        assert len(question.options) == MAX_OPTIONS + 1


def test_a_question_with_no_usable_options_degrades_rather_than_failing() -> None:
    """The model got the shape wrong; the question is still real.

    Refusing the whole call would lose what she was trying to ask, which is a
    worse answer than showing it as free text.
    """
    cleaned = normalise([Question(question="What should I call it?", options=[])])

    assert len(cleaned) == 1
    assert [o.label for o in cleaned[0].options] == [OTHER_LABEL]


# ── asking and answering ──────────────────────────────────────────────


async def test_it_broadcasts_then_waits_for_the_answer() -> None:
    bus = FakeBus()
    broker = QuestionBroker(bus)  # type: ignore[arg-type]

    task = asyncio.create_task(broker.ask([a_question()], turn_id="t_1"))
    await asyncio.sleep(0)

    assert bus.sent, "nothing was put on screen"
    method, params = bus.sent[0]
    assert method == "question.ask"
    assert params["turn_id"] == "t_1"
    assert len(params["questions"]) == 1

    assert broker.respond(params["request_id"], [Answer(question="Which one?", chosen=["A"])])
    result = await task

    assert result.timed_out is False
    assert result.answers[0].chosen == ["A"]


async def test_a_late_answer_is_reported_as_late_rather_than_pretended() -> None:
    """`confirm.respond` makes the same call for the same reason."""
    broker = QuestionBroker(FakeBus())  # type: ignore[arg-type]
    assert broker.respond("q_nothing", [Answer(question="?", chosen=["A"])]) is False


async def test_answering_twice_only_lands_once() -> None:
    bus = FakeBus()
    broker = QuestionBroker(bus)  # type: ignore[arg-type]
    task = asyncio.create_task(broker.ask([a_question()]))
    await asyncio.sleep(0)
    request_id = bus.sent[0][1]["request_id"]

    assert broker.respond(request_id, [Answer(question="?", chosen=["A"])])
    assert broker.respond(request_id, [Answer(question="?", chosen=["B"])]) is False

    assert (await task).answers[0].chosen == ["A"]


async def test_a_timeout_is_unanswered_not_declined() -> None:
    """**The mutation target, and the whole reason this is not `_ask`.**

    Make this deny by default and she starts apologising for a refusal nobody
    made, instead of carrying on with a stated assumption.
    """
    broker = QuestionBroker(FakeBus(), timeout_s=0.01)  # type: ignore[arg-type]

    result = await broker.ask([a_question()])

    assert result.timed_out is True
    assert result.answers == []


async def test_stop_releases_a_pending_question() -> None:
    """The wait sits inside the turn task, so cancelling the turn must reach it.

    Asserted rather than assumed: `PermissionEngine.cancel_all` exists and has
    no production caller, and a wait nothing can interrupt is exactly the bug
    just fixed in the composer's Stop button.
    """
    bus = FakeBus()
    broker = QuestionBroker(bus)  # type: ignore[arg-type]
    task = asyncio.create_task(broker.ask([a_question()]))
    await asyncio.sleep(0)
    assert broker.pending_count == 1

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert broker.pending_count == 0, "the pending question outlived its turn"


async def test_shutdown_releases_every_waiter() -> None:
    """By then there is no turn task left to cancel."""
    bus = FakeBus()
    broker = QuestionBroker(bus)  # type: ignore[arg-type]
    task = asyncio.create_task(broker.ask([a_question()]))
    await asyncio.sleep(0)

    assert broker.cancel_all() == 1
    assert (await task).answers == []


async def test_asking_nothing_does_not_put_anything_on_screen() -> None:
    bus = FakeBus()
    result = await QuestionBroker(bus).ask([])  # type: ignore[arg-type]

    assert bus.sent == []
    assert result.timed_out is False


# ── what the model is told ────────────────────────────────────────────


def test_the_chosen_answer_reaches_the_model() -> None:
    """`summary` is the only field the model ever sees, so it has to carry the
    answers — `data` and `display` never enter the prompt (§7.2)."""
    asked = Asked(answers=[Answer(question="Which database?", chosen=["SQLite"])])

    summary = render(asked, [a_question()])

    assert "Which database?" in summary
    assert "SQLite" in summary


def test_free_text_wins_over_the_options_it_replaced() -> None:
    answer = Answer(question="?", chosen=["Option 0"], other="neither, use Postgres")
    assert answer.text == "neither, use Postgres"


def test_a_timeout_tells_her_to_carry_on_rather_than_ask_again() -> None:
    """Otherwise the next step asks the same thing, which is how a question
    becomes a loop."""
    summary = render(Asked(timed_out=True), [a_question()])

    assert "not ask again" in summary.lower() or "do not ask again" in summary.lower()
    assert "assumed" in summary.lower()


def test_unanswered_questions_are_counted_rather_than_silently_dropped() -> None:
    asked = Asked(answers=[Answer(question="Q1", chosen=["A"])])

    summary = render(asked, [a_question("Q1"), a_question("Q2")])

    assert "1 left unanswered" in summary
