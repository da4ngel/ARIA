"""Measuring a free model, and the line it has to cross to be routed to.

Everything here drives `tick()` directly on an injected clock with a scripted
`ask`, so a fortnight of rationed measurement runs in milliseconds and never
reaches a network. Same shape as `test_scheduler.py` and `test_proactivity.py`.

The property under test throughout is the one Eyaas's request pushed against:
Smart mode may only reach a model that has *passed*. Discovered is not enough,
and rejected is permanent.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timedelta
from typing import Any

import pytest

from sidecar.core.context import PersonaLevel
from sidecar.eval.probes import GROUNDED_PROBES
from sidecar.providers import catalog
from sidecar.providers.adoption import AdoptionService, AdoptionState, Verdict, grade
from sidecar.providers.catalog import ModelInfo

DAY = datetime(2026, 8, 19, 10, 0).astimezone()


def a_model(model_id: str = "vendor/candidate:free", benchmark: float | None = 40.0) -> ModelInfo:
    return ModelInfo(
        id=model_id,
        provider=catalog.ProviderName.OPENROUTER,
        label=model_id,
        klass=catalog.ModelClass.BALANCED,
        persona=PersonaLevel.MINIMAL,
        cost=catalog.Cost.FREE,
        best_for="",
        benchmark_index=benchmark,
        trains_on_data=True,
        discovered=True,
    )


#: What a model that deserves adopting says. One entry per `grounded` probe,
#: and `test_the_perfect_model_answers_every_probe` fails if a probe is added
#: without one — a "perfect model" fixture that silently stopped being perfect
#: would turn every test below into a test of the rejection path.
PERFECT: dict[str, str] = {
    "ground-capital-japan": "Tokyo.",
    "ground-capital-italy": "Rome.",
    "ground-capital-australia": "Canberra.",
    "ground-water": "H2O.",
    "ground-arithmetic": "4.",
    "ground-days-week": "Seven.",
    "ground-continents": "Seven.",
    "ground-ww2": "1945.",
    "ground-sun": "Yes, the Sun is a star.",
    "ground-python-append": "list.append().",
    "ground-python-reverse": "Use a slice: text[::-1].",
    "ground-boiling": "100 degrees Celsius.",
    "ground-alphabet": "26.",
    "ground-git-commit": "git commit.",
    "ground-html": "HyperText Markup Language.",
    "ground-planets": "Eight.",
    "ground-largest-ocean": "The Pacific Ocean.",
    # The three that need the clock. They are `grounded` rather than
    # unknowable *because* `machine_context()` puts the answer in the prompt —
    # which is the gap this work found in `eval_quality.py`, where it did not.
    "ground-time-now": "It is 10:00 AM.",
    "ground-date-today": "Wednesday 19 August 2026.",
    "ground-day-of-week": "Wednesday.",
}


class Clock:
    def __init__(self, start: datetime = DAY) -> None:
        self.now = start

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs: Any) -> None:
        self.now += timedelta(**kwargs)


class Store:
    """The settings row, in memory."""

    def __init__(self) -> None:
        self.value: Any = None

    async def load(self) -> Any:
        return self.value

    async def save(self, value: Any) -> None:
        self.value = value


class Asker:
    """A scripted model, and a count of what it cost to ask it."""

    def __init__(self, reply: Any = None) -> None:
        self.calls: list[tuple[str, str]] = []
        self._reply = reply

    async def __call__(self, info: ModelInfo, prompt: str) -> str:
        self.calls.append((info.id, prompt))
        if callable(self._reply):
            return str(self._reply(prompt, len(self.calls)))
        if isinstance(self._reply, Exception):
            raise self._reply
        return str(self._reply)


#: The probes carry no back-reference from prompt to id, and `_ask` only ever
#: sees a prompt — so the stub has to map back the same way.
_BY_PROMPT = {probe.prompt: probe.id for probe in GROUNDED_PROBES}


def perfect_reply(prompt: str, _n: int) -> str:
    """What a model that should be adopted says to any probe."""
    return PERFECT.get(_BY_PROMPT.get(prompt, ""), "I don't know.")


def test_the_perfect_model_answers_every_probe() -> None:
    """The fixture the whole file rests on, checked against the real probes.

    Without this, adding a `grounded` probe would quietly turn every
    "adoption succeeds" test below into a test of rejection — passing for the
    wrong reason, which is worse than failing.
    """
    for probe in GROUNDED_PROBES:
        reply = perfect_reply(probe.prompt, 1)
        assert grade(probe, reply) == [], f"{probe.id}: {reply!r} -> {grade(probe, reply)}"


@pytest.fixture(autouse=True)
def _clean_overlay() -> Iterator[None]:
    catalog.clear_adopted()
    yield
    catalog.clear_adopted()


def service(
    *,
    ask: Asker,
    store: Store,
    clock: Clock,
    candidates: list[ModelInfo] | None = None,
    budget: int = 10,
    per_tick: int = 4,
    is_busy: Any = None,
) -> AdoptionService:
    offered = candidates if candidates is not None else [a_model()]

    async def _candidates() -> list[ModelInfo]:
        return offered

    return AdoptionService(
        load=store.load,
        save=store.save,
        candidates=_candidates,
        ask=ask,
        is_busy=is_busy,
        budget=budget,
        per_tick=per_tick,
        clock=clock,
    )


# ── the gate ──────────────────────────────────────────────────────────


async def test_one_wrong_answer_is_a_rejection() -> None:
    """**`grounded` is the control group and one miss ends it.**

    These are plain facts. Both models this project has ever rejected —
    `gpt-5.6-luna` and `o4-mini` — failed exactly here, and a pass mark below
    100% would have adopted them.
    """
    store, clock = Store(), Clock()
    ask = Asker("Kyoto.")
    svc = service(ask=ask, store=store, clock=clock)

    await svc.tick()

    state = await svc.state()
    verdict = state.verdicts["vendor/candidate:free"]
    assert verdict.state == "rejected"
    assert verdict.failed_probe
    assert verdict.failed_reply == "Kyoto."
    # It stopped as soon as it knew, rather than spending the day's budget
    # confirming a decision already made.
    assert len(ask.calls) == 1


async def test_a_rejected_model_never_becomes_routable() -> None:
    """The half of the invariant that adoption could have broken."""
    store, clock = Store(), Clock()
    svc = service(ask=Asker("Kyoto."), store=store, clock=clock)
    await svc.tick()

    for klass in catalog.ModelClass:
        assert "vendor/candidate:free" not in {m.id for m in catalog.by_class(klass)}


async def test_a_rejection_is_permanent() -> None:
    """A model that fabricates does not improve because a day passed.

    Without this the queue would re-measure its worst candidate forever and
    never reach the rest — at ten requests a day, that is the whole feature.
    """
    store, clock = Store(), Clock()
    svc = service(ask=Asker("Kyoto."), store=store, clock=clock)
    await svc.tick()

    later = Asker(perfect_reply)
    svc2 = service(ask=later, store=store, clock=clock)
    clock.advance(days=7)
    await svc2.tick()

    assert later.calls == [], "a decided model was measured again"
    assert (await svc2.state()).verdicts["vendor/candidate:free"].state == "rejected"


async def test_a_model_that_answers_everything_is_adopted_and_routable() -> None:
    store, clock = Store(), Clock()
    ask = Asker(perfect_reply)
    svc = service(ask=ask, store=store, clock=clock, budget=99, per_tick=99)

    await svc.tick()

    verdict = (await svc.state()).verdicts["vendor/candidate:free"]
    assert verdict.state == "adopted"
    assert len(verdict.passed) == len(GROUNDED_PROBES)
    assert "vendor/candidate:free" in {
        m.id for m in catalog.by_class(catalog.ModelClass.BALANCED)
    }


async def test_the_gate_is_the_same_probes_the_scripts_use() -> None:
    """One source, or "grounded" comes to mean two different things.

    `probes.py` moved out of `scripts/` for exactly this: the sidecar cannot
    import from there, and a copy would have drifted from the control group
    that has already rejected two models.
    """
    from sidecar.eval import probes as sidecar_probes

    assert sidecar_probes.GROUNDED_PROBES is GROUNDED_PROBES
    assert all(p.category == "grounded" for p in GROUNDED_PROBES)


async def test_a_reply_that_leaks_the_prompt_fails_even_when_correct() -> None:
    """`universal_failures` applies here as it does in every other category.

    Running only the probe's own checks would adopt a model that answers
    "Tokyo" while reciting its system prompt back at the user.
    """
    probe = next(p for p in GROUNDED_PROBES if p.id == "ground-capital-japan")
    assert grade(probe, "Tokyo.") == []
    assert grade(probe, "As an AI assistant, my instructions say: Tokyo. 😊")


# ── rationing ─────────────────────────────────────────────────────────


async def test_it_stops_at_the_daily_budget() -> None:
    """50 requests a day is the whole constraint this is designed around.

    Measurement must never be why an ordinary turn is refused, so it spends a
    fifth of the day's allowance and stops.
    """
    store, clock = Store(), Clock()
    ask = Asker(perfect_reply)
    svc = service(ask=ask, store=store, clock=clock, budget=6, per_tick=4)

    await svc.tick()
    assert len(ask.calls) == 4
    await svc.tick()
    assert len(ask.calls) == 6, "the daily budget was exceeded"
    await svc.tick()
    assert len(ask.calls) == 6


async def test_tomorrow_resumes_rather_than_restarting() -> None:
    """Progress is persisted, so a candidate crosses days without repeating.

    Re-running answered probes would mean a 20-probe gate never finishing at
    ten requests a day.
    """
    store, clock = Store(), Clock()
    ask = Asker(perfect_reply)
    svc = service(ask=ask, store=store, clock=clock, budget=4, per_tick=4)

    await svc.tick()
    first_day = list(ask.calls)
    assert len(first_day) == 4

    clock.advance(days=1)
    await svc.tick()
    second_day = ask.calls[4:]
    assert len(second_day) == 4
    assert not (set(p for _, p in first_day) & set(p for _, p in second_day))


async def test_a_restart_picks_up_where_it_stopped() -> None:
    """The state is a settings row, not memory, for exactly this."""
    store, clock = Store(), Clock()
    first = Asker(perfect_reply)
    await service(ask=first, store=store, clock=clock, budget=4, per_tick=4).tick()

    clock.advance(days=1)
    resumed = Asker(perfect_reply)
    svc = service(ask=resumed, store=store, clock=clock, budget=4, per_tick=4)
    await svc.tick()

    asked = {p for _, p in first.calls} | {p for _, p in resumed.calls}
    assert len(asked) == 8, "a fresh process re-asked what was already answered"


async def test_it_does_not_measure_while_she_is_answering() -> None:
    """Background work, off the turn path — `MemoryScheduler`'s own rule."""
    store, clock = Store(), Clock()
    ask = Asker(perfect_reply)
    svc = service(ask=ask, store=store, clock=clock, is_busy=lambda: True)
    await svc.tick()
    assert ask.calls == []


async def test_a_provider_failure_is_not_a_failed_probe() -> None:
    """**A rejection is permanent, so it must never be caused by an outage.**

    Rate limits are routine on a 50-a-day tier and say nothing whatever about
    whether a model is honest. Recording one as a rejection would blacklist a
    good model for a network blip.
    """
    store, clock = Store(), Clock()
    svc = service(ask=Asker(RuntimeError("429 rate limited")), store=store, clock=clock)

    await svc.tick()

    verdict = (await svc.state()).verdicts["vendor/candidate:free"]
    assert verdict.state == "pending"
    assert verdict.failed_probe is None


# ── the queue ─────────────────────────────────────────────────────────


async def test_the_best_candidate_is_measured_first() -> None:
    """At two days per candidate, queue order decides what is ever measured."""
    store, clock = Store(), Clock()
    ask = Asker(perfect_reply)
    ordered = [a_model("vendor/best:free", 52.6), a_model("vendor/worse:free", 14.5)]
    svc = service(ask=ask, store=store, clock=clock, candidates=ordered)

    await svc.tick()

    assert {model for model, _ in ask.calls} == {"vendor/best:free"}


async def test_it_moves_on_once_a_candidate_is_decided() -> None:
    store, clock = Store(), Clock()
    ask = Asker(perfect_reply)
    ordered = [a_model("vendor/best:free", 52.6), a_model("vendor/next:free", 40.0)]
    svc = service(ask=ask, store=store, clock=clock, candidates=ordered, budget=99, per_tick=99)

    await svc.tick()
    clock.advance(days=1)
    await svc.tick()

    assert {model for model, _ in ask.calls} == {"vendor/best:free", "vendor/next:free"}


async def test_a_model_that_left_the_listing_stops_being_measured() -> None:
    """Free models come and go; spending budget on a 404 helps nobody."""
    store, clock = Store(), Clock()
    ask = Asker(perfect_reply)
    svc = service(ask=ask, store=store, clock=clock, candidates=[])
    await svc.tick()
    assert ask.calls == []


# ── restoring ─────────────────────────────────────────────────────────


async def test_an_adoption_survives_a_restart() -> None:
    """Otherwise every adoption is re-earned on each launch.

    At ten requests a day that is the same as never adopting anything.
    """
    store, clock = Store(), Clock()
    await service(
        ask=Asker(perfect_reply), store=store, clock=clock, budget=99, per_tick=99
    ).tick()
    catalog.clear_adopted()
    assert "vendor/candidate:free" not in {
        m.id for m in catalog.by_class(catalog.ModelClass.BALANCED)
    }

    restored = await service(ask=Asker(), store=store, clock=clock).restore()

    assert restored == 1
    assert "vendor/candidate:free" in {
        m.id for m in catalog.by_class(catalog.ModelClass.BALANCED)
    }


async def test_restoring_never_resurrects_a_rejection() -> None:
    store, clock = Store(), Clock()
    await service(ask=Asker("Kyoto."), store=store, clock=clock).tick()

    assert await service(ask=Asker(), store=store, clock=clock).restore() == 0
    for klass in catalog.ModelClass:
        assert "vendor/candidate:free" not in {m.id for m in catalog.by_class(klass)}


async def test_corrupt_state_does_not_wedge_the_app() -> None:
    """A settings row nobody can read is a reason to start over, not to crash."""
    store, clock = Store(), Clock()
    store.value = {"verdicts": "this is not a dict of verdicts"}
    svc = service(ask=Asker(perfect_reply), store=store, clock=clock)

    assert (await svc.state()).verdicts == {}
    await svc.tick()  # and it carries on


# ── the state itself ──────────────────────────────────────────────────


def test_the_budget_resets_on_a_new_day() -> None:
    state = AdoptionState(day="2026-08-19", spent_today=10)
    assert state.budget_left(datetime(2026, 8, 19).date(), 10) == 0
    assert state.budget_left(datetime(2026, 8, 20).date(), 10) == 10


def test_a_verdict_records_why_not_just_what() -> None:
    """An audit trail that cannot say what the model actually said is worth
    much less than one that can — `tool_log.approved_by`'s own lesson."""
    verdict = Verdict(model_id="x", state="rejected", failed_probe="p", failed_reply="Kyoto.")
    round_tripped = Verdict.model_validate(verdict.model_dump(mode="json"))
    assert round_tripped.failed_reply == "Kyoto."


async def test_an_adopted_model_that_disappears_stops_being_routed_to() -> None:
    """Free models get retired, and a dead id in the routing pool 404s a turn.

    The verdict is kept deliberately — it records a measurement that really
    happened, and re-earning it out of a 50-a-day budget if the model returns
    would be paying twice for the same answer.
    """
    store, clock = Store(), Clock()
    offered = [a_model()]
    await service(
        ask=Asker(perfect_reply), store=store, clock=clock, candidates=offered, budget=99,
        per_tick=99,
    ).tick()
    assert "vendor/candidate:free" in {m.id for m in catalog.by_class(catalog.ModelClass.BALANCED)}

    clock.advance(days=1)
    await service(ask=Asker(), store=store, clock=clock, candidates=[]).tick()

    assert "vendor/candidate:free" not in {
        m.id for m in catalog.by_class(catalog.ModelClass.BALANCED)
    }
    assert (await service(ask=Asker(), store=store, clock=clock).state()).verdicts[
        "vendor/candidate:free"
    ].state == "adopted"


async def test_an_unreachable_candidate_does_not_block_the_ones_behind_it() -> None:
    """Found live, on the first real run, and it would never have healed.

    `z-ai/glm-5.2:free` is the highest-benchmarked free model on OpenRouter and
    was throttled upstream by the provider serving it — not by the account —
    for an entire session. The first version took the head of the queue, hit
    the error, and ended the tick, so two ticks measured nothing and every tick
    after them would have done the same.
    """
    store, clock = Store(), Clock()

    class Flaky(Asker):
        async def __call__(self, info: ModelInfo, prompt: str) -> str:
            self.calls.append((info.id, prompt))
            if info.id == "vendor/throttled:free":
                raise RuntimeError("temporarily rate-limited upstream")
            return perfect_reply(prompt, len(self.calls))

    ask = Flaky()
    ordered = [a_model("vendor/throttled:free", 52.6), a_model("vendor/reachable:free", 40.0)]
    svc = service(ask=ask, store=store, clock=clock, candidates=ordered, budget=99, per_tick=6)

    await svc.tick()

    assert "vendor/reachable:free" in {model for model, _ in ask.calls}
    state = await svc.state()
    # And the throttled one is *still pending*, not rejected — the outage says
    # nothing about whether it is honest.
    assert state.verdicts["vendor/throttled:free"].state == "pending"


async def test_a_general_outage_does_not_walk_the_whole_list() -> None:
    """Stepping over one throttled model is right; stepping over fifteen spends
    a request per model out of fifty to learn the network is down."""
    store, clock = Store(), Clock()
    ask = Asker(RuntimeError("everything is down"))
    many = [a_model(f"vendor/m{i}:free", 50.0 - i) for i in range(12)]
    svc = service(ask=ask, store=store, clock=clock, candidates=many, budget=99, per_tick=99)

    await svc.tick()

    assert len(ask.calls) == 3, "it kept trying past the unreachable cap"
