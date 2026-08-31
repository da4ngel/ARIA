"""`ask_user` — put the choice on screen instead of describing it.

The mechanism, the timeout reasoning and the "Other" guarantee all live in
`core/questions.py`. This is the registry entry and, more importantly, the
**description the model reads when deciding whether to reach for it**.

That description is the whole feature's discipline, and it lives here rather
than in the persona for two reasons. It is where a model looks when choosing a
tool, so it is read at exactly the right moment. And the stable prefix is at
786 of its measured 800-token local budget — a paragraph in `_WITH_TOOLS`
would blow it, while the tool-schema block is separate and already ~1650
tokens. The same trade `research`'s own description already makes.

**A tool that asks too often is worse than no tool.** §9's warning about
proactive messages applies here word for word: over-triggering is the fastest
route to a feature being switched off. So the description spends most of its
length on when *not* to call this.
"""

from __future__ import annotations

import structlog
from pydantic import ValidationError

from sidecar.core.questions import Question, render
from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

_DESCRIPTION = """Ask him to choose, with options he clicks rather than types.

**If he asks you to ask him something — "ask me some questions", "quiz me",
"give me options" — call this. That is the request itself, not a hint.** Never
write the choices out as A) B) C) in your reply: that is the thing this
replaces, and it makes him type an answer you could have collected in a click.

Also call it when you are genuinely blocked: two or more ways forward, and
picking wrong would mean doing the work twice. Each call takes up to 4
questions, each with 2-4 options — batch everything you can into one call. You
may call this more than once in a turn (a quiz is exactly that: one round of
questions, then another), but each call still costs a step.

Do NOT call it for: something you can infer from what he already said; a
question with an obvious default (pick it, do the work, say what you assumed);
permission to do something (that has its own confirmation); or anything you
could simply answer yourself. Unprompted, guessing well and saying so is
usually better than asking.

An option's `description` should say what happens if he picks it, not restate
the label. Do not add an "Other" option — one is always added for you."""


@tool(
    name="ask_user",
    tier=Tier.AUTO,
    description=_DESCRIPTION,
)
async def ask_user(ctx: ToolContext, questions: list[Question]) -> ToolResult:
    """Put one or more multiple-choice questions on screen and wait.

    Args:
        questions: The questions to ask, in order. Each needs `question` (the
            full sentence, ending in a question mark), a short `header`
            labelling it, and 2-4 `options`, each with a `label` and a
            `description` saying what choosing it means. Set `multi_select`
            true only when more than one option can apply at once.
    """
    from sidecar.state import runtime

    broker = runtime.questions
    if broker is None:
        # Not reachable in the app — `main.py` always builds one — but a tool
        # that raises on a missing dependency fails the whole turn, and this
        # one is only ever asking a question.
        return ToolResult(
            ok=False,
            summary="Could not put the question on screen. Answer him directly instead.",
            error="unavailable",
        )

    if not questions:
        return ToolResult(
            ok=False,
            summary="No question was given. Say what you need to know in your own words.",
            error="empty",
        )

    # **The arguments arrive as plain dicts.** Type hints drive the *schema*
    # the model is shown; nothing in the registry coerces what comes back, so
    # `list[Question]` is a description rather than a guarantee — and the first
    # live call died on `'dict' object has no attribute 'options'`.
    #
    # Validated per question rather than for the batch: one malformed entry
    # should cost that question, not the whole call. Degrading is right for the
    # same reason `normalise` degrades a question with no options — the model
    # got the shape wrong, and refusing loses what it was trying to ask.
    prepared: list[Question] = []
    for raw in questions:
        try:
            prepared.append(raw if isinstance(raw, Question) else Question.model_validate(raw))
        except ValidationError as exc:
            log.info("ask.malformed_question", error=str(exc))

    if not prepared:
        return ToolResult(
            ok=False,
            summary=(
                "That question was not in a shape I could show. Each one needs a "
                "`question` string and a list of `options`, each with a `label`. "
                "Ask him in your own words instead."
            ),
            error="malformed",
        )

    asked = await broker.ask(prepared, turn_id=ctx.turn_id)
    summary = render(asked, prepared)

    return ToolResult(
        # `timed_out` is **not** a failure: nothing went wrong, he just has not
        # answered yet. Reporting it as an error would make her apologise for
        # his silence instead of carrying on with a stated assumption.
        ok=True,
        summary=summary,
        data={"answers": [a.model_dump() for a in asked.answers], "timed_out": asked.timed_out},
        display={
            "kind": "answers",
            "answers": [{"question": a.question, "text": a.text} for a in asked.answers],
            "timed_out": asked.timed_out,
        },
    )
