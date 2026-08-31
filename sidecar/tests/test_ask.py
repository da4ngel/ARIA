"""`ask_user`: the registry entry, and the schema the model has to produce.

The schema half matters more than it looks. Before this feature the schema
builder had no object support at all, so `list[Question]` came out as
`{"type": "array", "items": {"type": "object"}}` — an object with no
properties, which tells a model nothing and leaves it guessing the shape.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import BaseModel

from sidecar.core.questions import Option, Question
from sidecar.tools import registry
from sidecar.tools.ask import ask_user
from sidecar.tools.registry import SCREEN_ONLY_TOOLS, Tier, Tool, ToolContext


@pytest.fixture
def broker(monkeypatch: pytest.MonkeyPatch):
    """A stand-in for `runtime.questions`, recording what it was asked."""

    class Fake:
        def __init__(self) -> None:
            self.asked: list[list[Question]] = []
            self.result: Any = None

        async def ask(self, questions: list[Question], *, turn_id: str | None = None) -> Any:
            self.asked.append(questions)
            from sidecar.core.questions import Answer, Asked

            return self.result or Asked(
                answers=[Answer(question=q.question, chosen=["Option 0"]) for q in questions]
            )

    fake = Fake()
    from sidecar.state import runtime

    monkeypatch.setattr(runtime, "questions", fake, raising=False)
    return fake


CTX = ToolContext(session_id="s_1", turn_id="t_1")

def ask_tool() -> Tool:
    """`registry.get` is `Tool | None`, and a missing tool here means the
    import in `tools/__init__.py` was dropped — which has its own test
    below rather than being re-checked by every other one."""
    found = registry.get("ask_user")
    assert found is not None
    return found


def a_question(text: str = "Which one?") -> Question:
    return Question(
        question=text, header="Pick", options=[Option(label="Option 0"), Option(label="Option 1")]
    )


# ── the registry entry ────────────────────────────────────────────────


def test_asking_is_never_a_permission_question() -> None:
    """`Tier.AUTO`, because asking changes nothing on the machine.

    A confirmation dialog in front of a question would be absurd — two
    round trips to answer one question — and it would put the tier system in
    charge of something that has no side effect at all.
    """
    assert ask_tool().tier is Tier.AUTO


def test_it_is_registered_at_import() -> None:
    """`tools/__init__.py`'s own docstring records `finder` being silently
    unregistered by a missing import while every test still passed."""
    import sidecar.tools  # noqa: F401

    assert "ask_user" in {t.name for t in registry.all_tools()}


def test_it_is_hidden_on_a_spoken_turn() -> None:
    """Four options on screen are no use to someone across the room, and that
    is the same dead end the confirmation dialog has to work around."""
    assert "ask_user" in SCREEN_ONLY_TOOLS
    offered = {s["function"]["name"] for s in registry.schemas(exclude=SCREEN_ONLY_TOOLS)}
    assert "ask_user" not in offered


def test_the_description_spends_itself_on_when_not_to_ask() -> None:
    """**Most of whether this feature is liveable.**

    §9's warning about proactive messages applies word for word: over-
    triggering is the fastest route to a feature being switched off. The
    guidance lives in the description rather than the persona because the
    stable prefix is at 786 of its measured 800-token budget.
    """
    # Whitespace-collapsed before matching: the phrase below wraps across a
    # line in the source, and asserting on the wrapped form would be a test
    # of the formatting rather than of the prompt. Same fix the persona
    # test already carries for "spoken aloud".
    description = " ".join(ask_tool().description.lower().split())

    assert "do not call it for" in description
    assert "infer" in description
    assert "obvious default" in description
    # And it must say the batch is the point, or it will ask four times.
    assert "one call" in description


def test_being_asked_to_ask_is_itself_the_trigger() -> None:
    """**The first restriction overshot, and Eyaas caught it on screen.**

    Asked "can u ask me some qustions", she wrote the multiple choice out as
    markdown — *"A) beginner  B) some algebra  C) comfortable … Reply like: 1A
    2B 3A 4C"* — because the description said to use the tool only when
    "genuinely blocked", and being asked to ask is not being blocked. The tool
    was registered and offered; she read the restriction and obeyed it.

    So the explicit request is now named first, and writing the options as
    prose is named as the thing this replaces.
    """
    description = " ".join(ask_tool().description.lower().split())

    assert "ask me some questions" in description
    assert "quiz me" in description
    assert "a) b) c)" in description


# ── the schema the model has to produce ───────────────────────────────


def test_the_nested_shape_is_actually_described() -> None:
    schema = ask_tool().parameters
    items = schema["properties"]["questions"]["items"]

    assert items["type"] == "object"
    assert set(items["properties"]) >= {"question", "options", "multi_select"}

    option = items["properties"]["options"]["items"]
    assert option["type"] == "object"
    assert set(option["properties"]) >= {"label", "description"}


def test_no_refs_survive_into_the_schema() -> None:
    """Pydantic hoists nested models into `$defs` and points at them with
    `$ref`. Several providers reject that outright and the rest handle it
    unevenly, so it is inlined into one self-contained fragment."""
    rendered = json.dumps(ask_tool().parameters)

    assert "$ref" not in rendered
    assert "$defs" not in rendered


def test_titles_are_stripped_at_every_depth() -> None:
    """The first version only reached the top level. Pydantic emits a title per
    class and per field, all restating the key they hang off, inside a block
    that is already ~1650 tokens."""
    assert "title" not in json.dumps(ask_tool().parameters)


def test_a_plain_model_argument_also_works() -> None:
    """The schema change is a capability, not a special case for this tool."""

    class Inner(BaseModel):
        name: str

    from sidecar.tools.registry import _json_type

    schema = _json_type(Inner)
    assert schema["type"] == "object"
    assert "name" in schema["properties"]


# ── behaviour ─────────────────────────────────────────────────────────


async def test_the_answer_comes_back_in_the_summary(broker) -> None:
    """`summary` is the only field the model sees."""
    result = await ask_user(CTX, questions=[a_question("Which database?")])

    assert result.ok
    assert "Which database?" in result.summary
    assert "Option 0" in result.summary


async def test_no_answer_is_not_a_failure(broker) -> None:
    """**`ok=False` would make her apologise for his silence.**

    Nothing went wrong; he simply has not picked yet. The summary tells her to
    carry on with a stated assumption, which only works if the turn treats this
    as a normal result.
    """
    from sidecar.core.questions import Asked

    broker.result = Asked(answers=[], timed_out=True)

    result = await ask_user(CTX, questions=[a_question()])

    assert result.ok is True
    assert result.error is None
    assert "assumed" in result.summary.lower()


async def test_an_empty_call_says_what_to_do_instead(broker) -> None:
    result = await ask_user(CTX, questions=[])

    assert result.ok is False
    assert "own words" in result.summary


async def test_a_missing_broker_costs_the_question_not_the_turn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unreachable in the app, but a tool that raises fails the whole turn and
    this one is only ever asking a question."""
    from sidecar.state import runtime

    monkeypatch.setattr(runtime, "questions", None, raising=False)

    result = await ask_user(CTX, questions=[a_question()])

    assert result.ok is False
    assert result.error == "unavailable"


def test_it_stays_available_for_a_quiz() -> None:
    """**There was a one-question-per-turn cap here, and it was wrong.**

    Asked to "test with set of mcqs one after the other", she asked the first
    through the tool and then wrote every following question out as A) B) C)
    markdown — because the cap had taken the tool away from her. A quiz *is*
    asking repeatedly; it is the case the feature exists for.

    What the cap guarded — an unprompted interrogation — was already covered
    three times over: the description says not to ask unprompted,
    `would_repeat` blocks an identical re-ask, and `MAX_STEPS` bounds the turn
    (Quick mode's 2 bounds it hard). And the observed failure has consistently
    been the opposite one: she under-asks.
    """
    from sidecar.core.conversation import ConversationService
    from sidecar.tools.permissions import PermissionMode

    service = ConversationService.__new__(ConversationService)

    class _Engine:
        allow_danger = False
        mode = PermissionMode.AUTO

    service._permissions = _Engine()  # type: ignore[assignment]  # noqa: SLF001

    offered = {s["function"]["name"] for s in service._tool_schemas() or []}  # noqa: SLF001
    assert "ask_user" in offered

    # And it is still gone the moment the turn is spoken, which is the one
    # condition that genuinely makes it useless.
    silent = {
        s["function"]["name"]
        for s in service._tool_schemas(spoken=True) or []  # noqa: SLF001
    }
    assert "ask_user" not in silent


def test_the_description_does_not_reintroduce_a_per_turn_cap() -> None:
    """The cap itself (`LoopState.asked_already`) is gone — see the test
    above — but the description shipped with it once said *"because you get
    one of these per turn"*. That sentence survived the code change and told
    the model the opposite of what `test_it_stays_available_for_a_quiz`
    proves: a quiz is repeated calls in one turn, bounded only by the step
    budget. A stale restriction in the prompt is as effective at stopping the
    behaviour as the removed cap was — the model reads what it is told, not
    what agent.py actually enforces.
    """
    description = " ".join(ask_tool().description.lower().split())

    assert "one of these per turn" not in description
    assert "more than once in a turn" in description
