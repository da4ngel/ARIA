"""Measuring a free model before Smart mode is allowed to use it.

Eyaas asked for the best free models, kept current as new ones appear, and for
**Smart mode to "learn them"**. That last part runs straight into a deliberate,
mutation-tested invariant: `catalog.by_class` — the router's only way to reach
a model — has never read the discovered overlay, so an unmeasured model cannot
be routed to. The invariant exists because of a real result. When `gpt-5.6-luna`
and `o4-mini` were measured, **the newest model lost**: both failed `grounded`,
the plain-facts control group, and neither was adopted.

So "learn them" is not "let Smart use whatever OpenRouter lists today". It is:
**automate the measurement, and promote only what passes.** `measure_models.py`
says adopting a model "should cost somebody reading the transcript"; this
softens that deliberately and keeps the half that matters — nothing reaches the
router without passing the same control group, and every verdict is stored with
the probe that decided it.

**The gate is `grounded` alone — 20 probes.** Not a compromise for its own
sake: it is the category both previous rejections actually failed, which makes
it the highest signal per request, and OpenRouter's free tier allows **50
requests a day**. The full 124-probe battery stays a deliberate
`measure_models.py` run. What this will not catch is a model that is honest but
poor at calling tools; `gate_tool_selection.py` remains a manual run, and
`ModelInfo.tool_score` stays `None` until it has been.

**Rationing is the feature.** At most `DAILY_BUDGET` measurement requests a
day, so measuring never competes with ordinary use for the same 50. A candidate
therefore takes two or three days, progress is persisted, and a restart resumes
rather than restarting. Everything is injected — clock, the ask, the listing —
so the tests drive `tick()` across a simulated fortnight without sleeping or
reaching the network once.
"""

from __future__ import annotations

import asyncio
import contextlib
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

import structlog
from pydantic import BaseModel, Field

from sidecar.eval.probes import GROUNDED_PROBES, Probe, universal_failures
from sidecar.providers import catalog
from sidecar.providers.catalog import ModelInfo

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

log = structlog.get_logger(__name__)

#: Where the whole record lives, in the existing settings table. One key, so a
#: half-written state cannot leave a candidate half-measured.
SETTINGS_KEY = "adoption.state"

#: Measurement requests per day. Ten of fifty leaves forty for actual use, and
#: a 20-probe gate therefore takes two days per candidate. Raising this is the
#: right lever if Eyaas ever adds credit — the free tier goes to 1000/day and
#: the rationing simply stops binding.
DAILY_BUDGET = 10

#: An hour between passes. The other limit that matters is 20 requests/minute,
#: and a tick that spends its budget in one burst would take a fifth of it.
DEFAULT_TICK_S = 3600.0

#: How many probes one tick may run. Below the daily budget on purpose: a
#: candidate's measurement is spread across the day rather than fired off in
#: one burst that collides with whatever the user is doing.
PER_TICK = 4


class Verdict(BaseModel):
    """What happened to one candidate, and why — kept whatever the answer.

    A rejection is as much a result as an adoption, and it is **permanent**:
    a model that fabricates does not improve because a day passed. Storing the
    failing probe and the reply is what makes that defensible a year later,
    rather than a model quietly never being tried again for no recorded reason.
    """

    # `model_` is pydantic's own reserved prefix and both fields below use it.
    # Renaming them to dodge the warning would make the record read worse than
    # the warning does — these are, literally, the model's id and the model's
    # serialised info.
    model_config = {"protected_namespaces": ()}

    model_id: str
    #: `pending` while probes remain, then `adopted` or `rejected`.
    state: str = "pending"
    #: Probe ids answered correctly so far. The list, not a count, so a resumed
    #: run knows exactly where it stopped.
    passed: list[str] = Field(default_factory=list)
    #: The probe that decided a rejection, with what the model actually said.
    failed_probe: str | None = None
    failed_reply: str | None = None
    failure_reasons: list[str] = Field(default_factory=list)
    decided_at: str | None = None
    #: The full `ModelInfo` as it was when measured, so an adoption survives a
    #: restart without depending on the model still being in today's listing.
    model_json: dict[str, Any] | None = None


class AdoptionState(BaseModel):
    """Everything the scheduler needs to resume, and nothing else."""

    #: Keyed by model id.
    verdicts: dict[str, Verdict] = Field(default_factory=dict)
    #: ISO date of the day `spent_today` counts against.
    day: str = ""
    spent_today: int = 0

    def budget_left(self, today: date, budget: int) -> int:
        if self.day != today.isoformat():
            return budget
        return max(0, budget - self.spent_today)

    def spend(self, today: date, n: int) -> None:
        if self.day != today.isoformat():
            self.day = today.isoformat()
            self.spent_today = 0
        self.spent_today += n


def _probes_by_id() -> dict[str, Probe]:
    return {probe.id: probe for probe in GROUNDED_PROBES}


def grade(probe: Probe, reply: str) -> list[str]:
    """Why this reply fails, or an empty list.

    The same two-part judgement `eval_quality.py` makes — the probe's own
    checks, plus `universal_failures`, which is what bans emoji, filler openers
    and prompt leakage across every probe in every category. Running only the
    checks would let a model pass `grounded` while reciting its system prompt.
    """
    reasons = list(universal_failures(probe, reply))
    for index, check in enumerate(probe.checks):
        try:
            if not check(reply):
                reasons.append(f"check {index + 1} failed")
        except Exception as exc:  # noqa: BLE001 — a bad check must not abort a run
            reasons.append(f"check {index + 1} raised {exc}")
    return reasons


class AdoptionService:
    """Works through free candidates, a few probes at a time, and decides.

    Injected clock, injected listing, injected ask: `tick()` is what the tests
    call and it never sleeps, never reaches a network and never touches a real
    settings table unless one is handed to it.
    """

    def __init__(
        self,
        *,
        load: Callable[[], Awaitable[Any]],
        save: Callable[[Any], Awaitable[None]],
        candidates: Callable[[], Awaitable[list[ModelInfo]]],
        ask: Callable[[ModelInfo, str], Awaitable[str]],
        is_busy: Callable[[], bool] | None = None,
        budget: int = DAILY_BUDGET,
        per_tick: int = PER_TICK,
        tick_s: float = DEFAULT_TICK_S,
        clock: Callable[[], datetime] = lambda: datetime.now().astimezone(),
    ) -> None:
        self._load = load
        self._save = save
        self._candidates = candidates
        self._ask = ask
        self._is_busy = is_busy or (lambda: False)
        self._budget = budget
        self._per_tick = per_tick
        self._tick_s = tick_s
        self._clock = clock
        self._task: asyncio.Task[None] | None = None
        self._probes = _probes_by_id()

    # ── state ───────────────────────────────────────────────────────────

    async def state(self) -> AdoptionState:
        raw = await self._load()
        if not raw:
            return AdoptionState()
        try:
            return AdoptionState.model_validate(raw)
        except Exception as exc:  # noqa: BLE001 — corrupt state must not wedge the app
            log.warning("adoption.state_unreadable", error=str(exc))
            return AdoptionState()

    async def restore(self) -> int:
        """Put previously adopted models back into the routing pool.

        Called at startup. Without it every adoption would have to be re-earned
        on each launch, which at ten requests a day is the same as never
        adopting anything.
        """
        state = await self.state()
        restored = 0
        for verdict in state.verdicts.values():
            if verdict.state != "adopted" or verdict.model_json is None:
                continue
            try:
                catalog.adopt(ModelInfo.model_validate(verdict.model_json))
            except Exception as exc:  # noqa: BLE001
                log.warning("adoption.restore_failed", model=verdict.model_id, error=str(exc))
                continue
            restored += 1
        if restored:
            log.info("adoption.restored", count=restored)
        return restored

    # ── the pass ────────────────────────────────────────────────────────

    async def tick(self) -> None:
        """One pass. Never raises — a scheduler that dies stops everything."""
        try:
            await self._tick_once()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            log.warning("adoption.tick_failed", error=str(exc))

    async def _tick_once(self) -> None:
        if self._is_busy():
            # Measurement is background work. There is another tick in an hour.
            return

        today = self._clock().date()
        state = await self.state()

        # Listing and pruning come **before** the budget check. Withdrawing a
        # model that has left the listing costs no requests, and gating it
        # behind the daily allowance would leave a dead id in the routing pool
        # for the rest of any day that spent its budget.
        offered = await self._candidates()
        self._prune(offered, state)

        left = min(state.budget_left(today, self._budget), self._per_tick)
        if left <= 0:
            return

        candidate = self._next_candidate(offered, state)
        if candidate is None:
            return

        verdict = state.verdicts.setdefault(candidate.id, Verdict(model_id=candidate.id))
        verdict.model_json = candidate.model_dump(mode="json")

        spent = 0
        for probe in self._remaining(verdict):
            if spent >= left:
                break
            try:
                reply = await self._ask(candidate, probe.prompt)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                # A provider error is not a failed probe. Rate limits and
                # outages say nothing about whether the model is honest, and
                # recording one as a rejection would be permanent.
                log.info("adoption.probe_unreachable", model=candidate.id, error=str(exc))
                break

            spent += 1
            reasons = grade(probe, reply)
            if reasons:
                self._reject(verdict, probe, reply, reasons, today)
                break
            verdict.passed.append(probe.id)

        if verdict.state == "pending" and not self._remaining(verdict):
            self._promote(verdict, candidate, today)

        if spent:
            state.spend(today, spent)
        await self._save(state.model_dump(mode="json"))

    def _prune(self, offered: list[ModelInfo], state: AdoptionState) -> None:
        """Drop adoptions for models OpenRouter no longer lists.

        Free models are retired, and an adopted id that has gone stays in the
        routing pool forever otherwise — so Smart would keep choosing something
        that 404s. `discovery` already drops expired entries from the listing;
        this is what makes that reach the pool.

        The verdict itself is kept. It is a record of a measurement that
        happened, and if the model comes back it should not have to be re-earned
        out of a 50-a-day budget.
        """
        live = {info.id for info in offered}
        for verdict in state.verdicts.values():
            if verdict.state == "adopted" and verdict.model_id not in live:
                catalog.unadopt(verdict.model_id)
                log.info("adoption.withdrawn", model=verdict.model_id, reason="no longer offered")

    def _next_candidate(
        self, offered: list[ModelInfo], state: AdoptionState
    ) -> ModelInfo | None:
        """The most promising model still undecided.

        `discovery.parse_openrouter` already sorts by the published benchmark,
        so "first still pending" is "best still pending" — which is what makes
        a slow queue tolerable: the model most likely to be worth adopting is
        also the one measured first.
        """
        for info in offered:
            decided = state.verdicts.get(info.id)
            if decided is None or decided.state == "pending":
                return info
        return None

    def _remaining(self, verdict: Verdict) -> list[Probe]:
        done = set(verdict.passed)
        return [p for p in GROUNDED_PROBES if p.id not in done]

    def _reject(
        self, verdict: Verdict, probe: Probe, reply: str, reasons: list[str], today: date
    ) -> None:
        """**One miss is a rejection.** These are facts a model should know.

        `grounded` is the control group precisely because there is no honest
        way to get it wrong, and both models this project has rejected were
        rejected on it. A pass mark below 100% would have adopted them.
        """
        verdict.state = "rejected"
        verdict.failed_probe = probe.id
        verdict.failed_reply = reply[:400]
        verdict.failure_reasons = reasons
        verdict.decided_at = today.isoformat()
        log.info(
            "adoption.rejected",
            model=verdict.model_id,
            probe=probe.id,
            reasons=reasons,
            passed=len(verdict.passed),
        )

    def _promote(self, verdict: Verdict, info: ModelInfo, today: date) -> None:
        verdict.state = "adopted"
        verdict.decided_at = today.isoformat()
        catalog.adopt(info)
        log.info("adoption.adopted", model=info.id, probes=len(verdict.passed))

    # ── lifecycle ───────────────────────────────────────────────────────

    async def _loop(self) -> None:
        # Sleep first, unlike `MemoryScheduler`. Nothing here needs to be
        # timely, and a measurement burst racing the app's own startup work is
        # the one thing that would make adoption visible to the user at all.
        while True:
            await asyncio.sleep(self._tick_s)
            await self.tick()

    def start(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._loop())
        log.info("adoption.started", budget=self._budget, tick_s=self._tick_s)

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task
        self._task = None

    # ── reporting ───────────────────────────────────────────────────────

    async def report(self) -> dict[str, Any]:
        """What the UI shows: progress, verdicts and what is left today."""
        state = await self.state()
        today = self._clock().date()
        return {
            "budget": self._budget,
            "spent_today": state.spent_today if state.day == today.isoformat() else 0,
            "left_today": state.budget_left(today, self._budget),
            "probe_count": len(GROUNDED_PROBES),
            "models": [
                {
                    "id": v.model_id,
                    "state": v.state,
                    "passed": len(v.passed),
                    "failed_probe": v.failed_probe,
                    "failed_reply": v.failed_reply,
                    "decided_at": v.decided_at,
                }
                for v in state.verdicts.values()
            ],
        }
