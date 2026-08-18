"""Unprompted messages — rate-limited, focus-aware, self-checked (BUILD_SPEC
§9 Phase 8).

Same shape as `memory/scheduler.py`'s `MemoryScheduler`: injected clock,
injected sleep, a `tick()` a test can call directly across a simulated week
without sleeping once. A second, separate scheduler rather than overloading
`MemoryScheduler` with an unrelated concern.

**"Over-triggering is the fastest path to uninstall... when in doubt, stay
quiet"** — BUILD_SPEC's own words, in its own §9 Phase 8 risk table. Every
candidate passes through the same gates in order, any one of which drops it
silently and ends the tick: focus, rate limit, the self-check, then
delivery. One candidate per tick, never a burst.

**Calendar-approaching is not a trigger here.** It needs an OAuth +
Google/Outlook Calendar integration this project has no infrastructure for
at all — deliberately deferred, not forgotten (confirmed with Eyaas before
this file was written). Three triggers are built: a pending procedure
offer (Part 2's `memory/procedures.py`), repeated tool failures, and long
idle after a stated intention. The fourth BUILD_SPEC names — a
content-free "scheduled check-in" — is deliberately not implemented as its
own trigger: a message with nothing to say is exactly the noise the rate
limit and self-check exist to prevent.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import structlog

from sidecar.memory import procedures
from sidecar.memory.db import Database
from sidecar.memory.messages import ConversationStore
from sidecar.memory.settings_store import WATCHED_PROJECTS
from sidecar.persona import focus
from sidecar.providers.base import ChatMessage, GenerationOptions, LLMProvider, Role

log = structlog.get_logger(__name__)

#: Five minutes — the same cadence `MemoryScheduler`'s own sweep uses.
DEFAULT_TICK_S = 300.0
#: BUILD_SPEC's own numbers, verbatim: "max 4/day, min 90min apart".
MAX_PER_DAY = 4
MIN_GAP = timedelta(minutes=90)
#: How long a stated intention sits before "still working on this?" is a
#: reasonable thing to ask rather than an interruption.
IDLE_INTENTION_GAP = timedelta(hours=2)


@dataclass(frozen=True)
class Candidate:
    text: str
    trigger: str
    urgency: str = "normal"
    #: Opaque reference for the delivery callback — only meaningful for
    #: `trigger == "procedure_offer"`, where it carries the procedure's
    #: `name` so a plain "yes" in reply can resolve to `procedures.confirm`
    #: without a model call (`ConversationService._resolve_procedure_reply`).
    #: `None` for every other trigger.
    ref: str | None = None


# ── the scheduler ────────────────────────────────────────────────────


class ProactivityScheduler:
    """Sweeps for something worth saying, at most once per tick, and only
    when nothing above says not to."""

    def __init__(
        self,
        *,
        store: ConversationStore,
        find_candidates: Callable[[], Awaitable[list[Candidate]]],
        self_check: Callable[[Candidate], Awaitable[bool]],
        deliver: Callable[[Candidate], Awaitable[None]],
        is_actively_working: Callable[[], bool] = focus.is_actively_working,
        max_per_day: int = MAX_PER_DAY,
        min_gap: timedelta = MIN_GAP,
        tick_s: float = DEFAULT_TICK_S,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        sleep: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        self._store = store
        self._find_candidates = find_candidates
        self._self_check = self_check
        self._deliver = deliver
        self._is_actively_working = is_actively_working
        self._max_per_day = max_per_day
        self._min_gap = min_gap
        self._tick_s = tick_s
        self._clock = clock
        self._sleep = sleep or asyncio.sleep
        self._task: asyncio.Task[None] | None = None

    async def tick(self) -> None:
        """One pass. Never raises — a scheduler that dies stops everything,
        the same reasoning `MemoryScheduler.tick` already states."""
        try:
            await self._tick_once()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            log.warning("proactivity.tick_failed", error=str(exc))

    async def _tick_once(self) -> None:
        if self._is_actively_working():
            return
        if not await self._within_rate_limit():
            return
        candidates = await self._find_candidates()
        if not candidates:
            return
        candidate = candidates[0]
        if not await self._self_check(candidate):
            log.info("proactivity.self_check_dropped", trigger=candidate.trigger)
            return
        await self._deliver(candidate)
        log.info("proactivity.delivered", trigger=candidate.trigger)

    async def _within_rate_limit(self) -> bool:
        now = self._clock().astimezone(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        sent_today = await self._store.count_proactive_since(today_start)
        if sent_today >= self._max_per_day:
            return False

        last_at = await self._store.most_recent_proactive_at()
        if last_at is None:
            return True
        last = datetime.fromisoformat(last_at.replace("Z", "+00:00")).astimezone(UTC)
        return now - last >= self._min_gap

    async def _loop(self) -> None:
        while True:
            await self.tick()
            await self._sleep(self._tick_s)

    def start(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._loop())
        log.info("proactivity.scheduler_started", tick_s=self._tick_s)

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task
        self._task = None


# ── trigger 1: a pending procedure offer (Part 2) ───────────────────


async def procedure_offer_candidate(db: Database) -> Candidate | None:
    """The most concrete, lowest-noise-risk trigger, and checked first for
    that reason: a real, repeated pattern, not a guess about mood or
    timing."""
    offers = await procedures.pending_offers(db)
    if not offers:
        return None
    offer = offers[0]
    steps = json.loads(offer["steps"])
    step_names = ", ".join(s["tool"] for s in steps)
    return Candidate(
        text=(
            f"You've done this a few times now: {step_names}. Want me to "
            f'remember it as "{offer["name"]}" so I recognise it next time?'
        ),
        trigger="procedure_offer",
        ref=str(offer["name"]),
    )


# ── trigger 2: repeated tool failures ───────────────────────────────


async def repeated_failure_candidate(db: Database, session_id: str | None) -> Candidate | None:
    if session_id is None:
        return None
    row = await db.run(
        lambda c: c.execute(
            "SELECT tool, COUNT(*) AS n FROM tool_log WHERE session_id = ? AND ok = 0 "
            "AND created_at > datetime('now', '-15 minutes') "
            "GROUP BY tool HAVING n >= 2 ORDER BY n DESC LIMIT 1",
            (session_id,),
        ).fetchone()
    )
    if row is None:
        return None
    return Candidate(
        text=f"{row['tool']} hasn't been working — want me to try a different approach?",
        trigger="repeated_failure",
        urgency="low",
    )


# ── trigger 3: long idle after a stated intention ───────────────────

#: A small pattern table, the same shape as `router.py`'s own regex
#: constants — Phase 5's own lesson again: a local model classifying "was
#: that an intention" is not reliable enough to build a trigger on
#: (CLAUDE.md: "the model cannot judge X and should stop being asked").
_INTENTION_PATTERNS = (
    re.compile(r"\bi'?ll (get to|do|handle|finish|look at|sort out)\b", re.I),
    re.compile(r"\bremind me to\b", re.I),
    re.compile(r"\bi (need|have) to\b.*\b(later|tomorrow|tonight|this (week|evening))\b", re.I),
    re.compile(r"\blater (i'?ll|i will|i need to)\b", re.I),
)


def is_stated_intention(text: str) -> bool:
    return any(pattern.search(text) for pattern in _INTENTION_PATTERNS)


async def idle_intention_candidate(
    store: ConversationStore, *, now: datetime, min_idle: timedelta = IDLE_INTENTION_GAP
) -> Candidate | None:
    session_id = await store.latest_session_id()
    if session_id is None:
        return None
    history = await store.history(session_id)
    for message in reversed(history):
        if message.role is not Role.USER:
            continue
        if not is_stated_intention(message.content):
            continue
        created = datetime.strptime(message.created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        if now.astimezone(UTC) - created >= min_idle:
            return Candidate(
                text=(
                    f'Still working on "{message.content.strip()[:80]}"? '
                    f"Happy to help if you want to pick it back up."
                ),
                trigger="idle_intention",
            )
        # The most recent intention found is too fresh — do not keep
        # scanning further back for an older, staler one to ask about.
        return None
    return None


# ── trigger 4: a scheduled check-in ──────────────────────────────────
#
# BUILD_SPEC §9 names five triggers; this is the fourth, and it was simply
# absent rather than deferred — it had never been written down as a gap
# either. It is also the one with the worst noise-to-value ratio if built
# carelessly, because unlike the other three it is not a response to
# anything the user did. §9's own warning applies hardest here: *"over-
# triggering is the fastest path to uninstall. When in doubt, stay quiet."*
#
# So it is deliberately the most conditional of the four: waking hours only,
# a long silence only, and once a day at most on top of the global rate
# limit every candidate already passes.

#: Nothing before this hour or after it. A check-in at 3am is not a
#: check-in, it is being woken up — and `affect` already reads late-night
#: activity as something to be gentle about rather than to interrupt.
CHECK_IN_HOURS = range(10, 21)
#: How long the conversation has to have been silent. Shorter than this and
#: she is interrupting a session that is merely paused — someone reading a
#: reply, or thinking.
CHECK_IN_SILENCE = timedelta(hours=20)


async def scheduled_check_in_candidate(
    store: ConversationStore, *, now: datetime, silence: timedelta = CHECK_IN_SILENCE
) -> Candidate | None:
    """"You have not been around in a while" — at most once, and only when
    that is actually true.

    Keyed off the last *message* rather than a stored "last check-in" stamp:
    the silence is the whole precondition, so a check-in that happened resets
    it by definition — it writes a `messages` row itself. That removes a
    piece of state that could disagree with reality.
    """
    local = now.astimezone()
    if local.hour not in CHECK_IN_HOURS:
        return None

    latest = await store.latest_message_at()
    if latest is None:
        # Nothing has ever been said. A brand-new install being greeted
        # unprompted is a strange first experience, not a warm one.
        return None
    last = datetime.strptime(latest, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    if now.astimezone(UTC) - last < silence:
        return None

    days = max(1, int((now.astimezone(UTC) - last).total_seconds() // 86400))
    when = "a day" if days == 1 else f"{days} days"
    return Candidate(
        text=(
            f"It has been about {when}. I am here if you want to pick anything "
            f"back up — no need to reply if not."
        ),
        trigger="scheduled_check_in",
    )


# ── trigger 5: a file event on a watched project ─────────────────────
#
# The fifth of §9's five, and the reason it was never built is that
# **"a watched project" did not exist anywhere in this codebase**. It still
# needs the user to name one, so this is empty by default and cannot fire
# until they do — which is also what keeps it from being noise. A build
# directory churns constantly; a folder somebody deliberately pointed at
# does not.
#
# Polled, not watched. `watchdog` would be a new dependency for one trigger,
# and this project has turned down bigger ones for less (`webrtcvad`,
# `pywinauto`, `APScheduler`). A five-minute tick comparing mtimes is
# enough to notice "you have been working on this" — which is all the
# trigger is for. It is not a build system.

#: Only files changed inside this window count as "just now". Slightly wider
#: than the scheduler's own tick so a change cannot fall between two passes.
FILE_EVENT_WINDOW = timedelta(minutes=15)
#: Below this, it is one save rather than a working session. Saying "I see
#: you are working on X" after a single keystroke is the noise §9 warns of.
FILE_EVENT_MIN_FILES = 3
#: Never walk more than this. A watched folder pointed at a whole drive must
#: cost a bounded scan, exactly as `finder._walk` is bounded.
FILE_EVENT_MAX_ENTRIES = 2000


def _recently_changed(root: Path, *, now: datetime, window: timedelta) -> list[str]:
    """Names of files under `root` modified inside `window`. Bounded, and
    never raises — an unreadable folder is one folder, not a failed tick."""
    from sidecar.tools.finder import _SKIP_DIRS

    cutoff = (now.astimezone(UTC) - window).timestamp()
    found: list[str] = []
    seen = 0
    try:
        for path in root.rglob("*"):
            seen += 1
            if seen > FILE_EVENT_MAX_ENTRIES:
                break
            if path.is_dir() or path.name.startswith("."):
                continue
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            try:
                if path.stat().st_mtime >= cutoff:
                    found.append(path.name)
            except OSError:
                continue
    except OSError:
        return []
    return found


async def watched_project_candidate(
    settings: object, *, now: datetime, window: timedelta = FILE_EVENT_WINDOW
) -> Candidate | None:
    """Notice that a watched folder is being worked in right now.

    Empty by default: `WATCHED_PROJECTS` is unset until the user names a
    folder, so this returns None on every machine that has not opted in.
    """
    if settings is None:
        return None
    roots = await settings.get(WATCHED_PROJECTS, [])  # type: ignore[attr-defined]
    if not isinstance(roots, list) or not roots:
        return None

    for raw in roots:
        if not isinstance(raw, str):
            continue
        root = Path(raw)
        changed = await asyncio.to_thread(_recently_changed, root, now=now, window=window)
        if len(changed) < FILE_EVENT_MIN_FILES:
            continue
        shown = ", ".join(sorted(set(changed))[:3])
        return Candidate(
            text=(
                f"You have been working in {root.name} — {len(changed)} files "
                f"changed just now ({shown}). Say the word if you want a hand."
            ),
            trigger="watched_project",
        )
    return None


# ── composing the default trigger set ───────────────────────────────


async def default_candidates(
    db: Database, store: ConversationStore, settings: object = None
) -> list[Candidate]:
    """Tried in order — the first real one wins, one candidate per tick.
    Ordered from least to most speculative: a repeated pattern is a fact
    about what happened; a stated intention is an inference about what the
    user meant.

    `record_new_offers` runs first, here rather than as its own scheduled
    job: nothing else in production ever called it before this — the whole
    detection step was as dead as `episodes`/`facts` were before Phase 5,
    just never exercised outside `test_procedures.py`. `pending_offers`
    below would always have been empty.
    """
    await procedures.record_new_offers(db)

    procedure = await procedure_offer_candidate(db)
    if procedure is not None:
        return [procedure]

    session_id = await store.latest_session_id()
    failure = await repeated_failure_candidate(db, session_id)
    if failure is not None:
        return [failure]

    intention = await idle_intention_candidate(store, now=datetime.now(UTC))
    if intention is not None:
        return [intention]

    # The two §9 named that had never been built. Both sit last because both
    # are the most speculative: nothing the user did prompted either, which
    # is exactly the shape §9 warns is the fastest path to uninstall.
    project = await watched_project_candidate(settings, now=datetime.now(UTC))
    if project is not None:
        return [project]

    check_in = await scheduled_check_in_candidate(store, now=datetime.now(UTC))
    if check_in is not None:
        return [check_in]

    return []


# ── the self-check ───────────────────────────────────────────────────

#: A prompt constant, not a `.j2` file — this codebase has no Jinja
#: dependency (checked before writing this) and every other prompt here is
#: already a plain Python string.
_SELF_CHECK_PROMPT = (
    "You are about to send this message to the user without being asked:\n\n"
    '"{text}"\n\n'
    "Would this genuinely be useful right now, or is it noise? Reply with "
    "exactly one word: USEFUL or NOISE."
)


async def default_self_check(provider: LLMProvider, model: str, candidate: Candidate) -> bool:
    """Off the interactive path entirely — background, local-only, the same
    shape `ConversationService._generate_title` already uses for its own
    local-only call."""
    messages = [ChatMessage(role=Role.USER, content=_SELF_CHECK_PROMPT.format(text=candidate.text))]
    collected: list[str] = []
    try:
        async for delta in provider.stream_chat(
            messages, model=model, options=GenerationOptions(temperature=0.0)
        ):
            if delta.text:
                collected.append(delta.text)
            if delta.done:
                break
    except Exception:  # noqa: BLE001 — a broken check should drop the
        # candidate, not deliver something unchecked
        log.warning("proactivity.self_check_failed", trigger=candidate.trigger, exc_info=True)
        return False
    reply = "".join(collected).strip().upper()
    return "USEFUL" in reply and "NOISE" not in reply
