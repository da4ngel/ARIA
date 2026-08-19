"""Turn orchestration (BUILD_SPEC §9 Phase 1).

One turn: persist the user message, assemble context, stream from the provider,
push `token` events as deltas arrive, persist the reply, push `turn.complete`.

Cancellation is an `asyncio.Task.cancel()` on the streaming task; the httpx
stream context closes on unwind, which aborts the HTTP request. The Phase 1 gate
requires that to land within 200ms.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import re
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel

from sidecar.core import attachments as attach
from sidecar.core import context as ctx
from sidecar.core.agent import LoopState, exhausted_note, repeat_note, silent_reply_note
from sidecar.core.router import (
    MODE_BIAS,
    RouteDecision,
    Router,
    RoutingBias,
    is_tool_shaped,
)
from sidecar.core.tasks import spawn
from sidecar.memory import procedures
from sidecar.memory.db import Database
from sidecar.memory.messages import ConversationStore, SessionSummary, StoredMessage
from sidecar.memory.retrieval import MemoryServices, Retrieved
from sidecar.memory.routing_log import RoutingLog, RoutingRecord
from sidecar.persona import affect as affect_module
from sidecar.providers import catalog
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    LLMProvider,
    ProviderError,
    ProviderRateLimited,
    ProviderUnavailable,
    Role,
    ToolCall,
)
from sidecar.providers.catalog import ModelInfo
from sidecar.providers.connectivity import connectivity
from sidecar.providers.health import HealthTracker
from sidecar.providers.tts import TextToSpeech, shorten_for_speech, split_for_speech
from sidecar.rpc.events import AssistantState, Event, EventBus
from sidecar.state import runtime
from sidecar.tools import registry
from sidecar.tools.permissions import PermissionEngine, PermissionMode
from sidecar.tools.registry import ONLINE_TOOLS, Tier, ToolContext

log = structlog.get_logger(__name__)


def _session_started_at(history: list[StoredMessage]) -> datetime | None:
    """The first stored message's timestamp, or `None` for an empty history.
    Shared by `_machine_context` and `_update_affect` — both want "when did
    this conversation start" from data already in hand, no extra query."""
    if not history:
        return None
    with contextlib.suppress(ValueError):
        return datetime.strptime(history[0].created_at, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=UTC
        )
    return None


SUMMARY_MAX_TOKENS = 400
SUMMARY_MAX_CHARS = SUMMARY_MAX_TOKENS * 4  # defensive clamp; see _summarize

# Two turns in, there is a subject worth naming. Earlier than that and every
# conversation gets titled "Greeting".
TITLE_MIN_MESSAGES = 4
# Only the opening turns feed the title. A long conversation drifts, and naming
# it by where it ended up makes it unfindable by what you remember starting with.
TITLE_FROM_TURNS = 6
# Wait for the user to stop typing before spending the model on a title.
#
# Measured: firing immediately after a turn put the *next* turn at 924ms against
# a 700ms gate, because both requests queued on the same Ollama instance. A
# title is worth zero of the user's milliseconds, so it waits for real idle.
TITLE_IDLE_DELAY_S = 3.0
TITLE_IDLE_TIMEOUT_S = 90.0
# Opening History should not queue a model call for every conversation ever had.
# A few per open catches up over a couple of visits.
TITLE_BACKFILL_PER_CALL = 3
# A ceiling on reading attachments, so one pathological file cannot hold a
# turn open indefinitely. Generous: several images are several cloud round
# trips, and the point of moving this off the RPC path was to stop racing a
# timeout, not to introduce a tighter one.
ATTACHMENT_READ_TIMEOUT_S = 120.0


class TurnStarted(BaseModel):
    """`chat.send` result (§7.1)."""

    turn_id: str
    session_id: str


# Phase 8's procedure offers: "offer once, wait for a yes" needs something to
# recognise the yes. A small pattern table, the same shape as
# `persona.proactivity._INTENTION_PATTERNS` and `tools.memory._PATTERNS` —
# Phase 5's own lesson again: whether a short reply means yes or no is not
# worth a model call.
_AFFIRMATIVE_REPLY = re.compile(
    r"^(?:yes|yeah|yep|yup|sure|ok(?:ay)?|go ahead|please do|do it|sounds good)[.!]?$",
    re.IGNORECASE,
)
_NEGATIVE_REPLY = re.compile(
    r"^(?:no|nope|nah|not (?:now|really)|don'?t|skip it|no thanks)[.!]?$",
    re.IGNORECASE,
)


def _parse_yes_no(text: str) -> bool | None:
    """True/False for a clearly affirmative/negative one-line reply, else
    None — an unrelated message must fall through to a normal turn, not be
    silently swallowed as a "no"."""
    stripped = text.strip()
    if _AFFIRMATIVE_REPLY.match(stripped):
        return True
    if _NEGATIVE_REPLY.match(stripped):
        return False
    return None


class ProviderRegistry(BaseModel):
    """Providers keyed by name, so the service can follow the router's choice."""

    model_config = {"arbitrary_types_allowed": True}

    providers: dict[str, LLMProvider]

    def for_model(self, info: ModelInfo) -> LLMProvider:
        provider = self.providers.get(str(info.provider))
        if provider is None:
            raise ProviderUnavailable(
                f"No provider is configured for {info.label} "
                f"({info.provider}). Pick a different model."
            )
        return provider


class ConversationHistory(BaseModel):
    """`chat.history` result. Typed at the boundary per CLAUDE.md rule 7."""

    session_id: str | None
    messages: list[StoredMessage]


class SpeechStream:
    """Turns a token stream into audio while it is still arriving.

    BUILD_SPEC §9 Phase 2 calls this the single trick that gets first audio
    under the budget: do not wait for the whole reply. The first speakable
    fragment is synthesised while the model is still writing the next sentence.

    Synthesis is dispatched as a task rather than awaited, because awaiting it
    would stall the token loop — the text on screen would stutter in time with
    the speech. Chunks are numbered so the renderer plays them in order even
    though they finish out of order.
    """

    def __init__(
        self,
        tts: TextToSpeech | None,
        bus: EventBus,
        started: float,
        *,
        speed: float | None = None,
    ) -> None:
        self._tts = tts
        self._bus = bus
        self._started = started
        self._buffer = ""
        self._index = 0
        self._tasks: list[asyncio.Task[None]] = []
        # Phase 8: the turn's affect-derived nudge, applied to every chunk this
        # stream speaks. None (the default in every pre-Phase-8 call site and
        # every test) means "use the engine's own instance default" — see
        # `KokoroTTS.synthesize`.
        self._speed = speed

    @property
    def active(self) -> bool:
        return self._tts is not None and self._tts.ready

    def feed(self, text: str) -> None:
        if self.active:
            self._buffer += text

    async def drain(self, turn_id: str) -> None:
        """Emit every chunk the buffer can currently yield."""
        if not self.active:
            return
        while True:
            chunk, self._buffer = split_for_speech(self._buffer, is_first=self._index == 0)
            if not chunk:
                return
            self._dispatch(turn_id, chunk)

    async def finish(self, turn_id: str) -> None:
        """Speak whatever is left, then wait for the synthesisers to land."""
        if not self.active:
            return
        tail = self._buffer.strip()
        self._buffer = ""
        # The tail never passed through `split_for_speech` — the model simply
        # stopped sending tokens — so the word cap is applied here in a loop
        # rather than dispatching it as one unbounded final breath.
        while tail:
            piece, tail = shorten_for_speech(tail, "")
            if not piece:
                break
            self._dispatch(turn_id, piece)
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    def _dispatch(self, turn_id: str, text: str) -> None:
        index = self._index
        self._index += 1
        task = asyncio.create_task(self._speak(turn_id, index, text))
        self._tasks.append(task)

    async def _speak(self, turn_id: str, index: int, text: str) -> None:
        assert self._tts is not None
        try:
            pcm, sample_rate = await self._tts.synthesize(text, speed=self._speed)
        except Exception as exc:  # noqa: BLE001 — silence is not worth a failed turn
            log.warning("tts.chunk_failed", turn_id=turn_id, error=str(exc))
            return

        if index == 0:
            # The Phase 2 gate is a number, so it gets logged as one.
            elapsed = (time.perf_counter() - self._started) * 1000
            log.info(
                "turn.first_audio",
                turn_id=turn_id,
                first_audio_ms=round(elapsed, 1),
                budget_ms=900,
                within_budget=elapsed < 900,
            )

        await self._bus.broadcast(
            Event.AUDIO_OUT,
            {
                "turn_id": turn_id,
                "index": index,
                "sample_rate": sample_rate,
                "pcm": base64.b64encode(pcm).decode("ascii"),
            },
        )


class ConversationService:
    """Owns in-flight turns. All durable state goes to SQLite."""

    def __init__(
        self,
        *,
        store: ConversationStore,
        provider: LLMProvider,
        bus: EventBus,
        model: str,
        num_ctx: int = 8192,
        context_token_budget: int = 6000,
        providers: dict[str, LLMProvider] | None = None,
        router: Router | None = None,
        health: HealthTracker | None = None,
        selected_model: str = catalog.SMART_ID,
        usable_models: Callable[[], set[str]] | None = None,
        permissions: PermissionEngine | None = None,
        tts: TextToSpeech | None = None,
        memory: MemoryServices | None = None,
        routing_log: RoutingLog | None = None,
        db: Database | None = None,
    ) -> None:
        self._store = store
        # Phase 8's affect model reads/writes `affect_state` directly — its
        # own table, no reason to route it through `ConversationStore`.
        # None means no affect is rendered and none is updated, the same
        # "every call site is a no-op" shape `memory` already has.
        self._db = db
        self._provider = provider
        self._bus = bus
        self._model = model
        self._num_ctx = num_ctx
        self._budget = context_token_budget
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._health = health or HealthTracker()
        self._router = router or Router(self._health)
        self._selected = selected_model
        # None means "assume every catalog model works", which is only true in
        # tests. Startup injects the real resolver so the router never picks a
        # provider with no key behind it.
        self._usable_models = usable_models
        # None means she has no hands, and the model is never told a tool
        # exists — which is the only safe default for a thing that can
        # delete files.
        self._permissions = permissions
        # None means she types and does not speak. Voice is additive: a
        # missing or broken engine must never stop a turn completing.
        self._tts = tts
        # §9.7's labelled dataset. None simply means the decisions are not
        # written down — every call site is a no-op, as with `memory`.
        self._routing_log = routing_log
        # Defaults to the single provider it was constructed with, so existing
        # callers and tests keep working without a registry.
        self._registry = ProviderRegistry(
            providers=providers or {str(catalog.ProviderName.OLLAMA): provider}
        )
        # Which local model Ollama currently holds in VRAM, so switching models
        # can evict the old one first (see `_free_vram_for`).
        self._resident_local: str | None = model if catalog.get(model) else None
        # turn_id -> session_id, so deleting a conversation can cancel a turn
        # still streaming into it.
        self._turn_sessions: dict[str, str] = {}
        # turn_id -> (tool, ok), carried from `_use_one_tool` to `_finish` for
        # the routing log. Popped there, so it cannot grow.
        self._turn_tools: dict[str, tuple[str, bool]] = {}
        # Background jobs that must not outlive the process — currently title
        # generation. Kept apart from `_tasks`, which `cancel()` reaches into.
        self._jobs: set[asyncio.Task[None]] = set()
        # Sessions already titled this run, so a busy conversation does not
        # re-ask the model on every turn.
        self._titled: set[str] = set()
        # Sessions with a roll-up in flight, so overlapping turns do not queue
        # several summarisations of nearly the same history.
        self._rolling_up: set[str] = set()
        # An id handed out by `new_session` that no message has landed in yet.
        self._pending_new: str | None = None
        # Roll-up notes are per-session and rebuilt on demand, and deliberately
        # NOT moved into `episodes` by Phase 5. A roll-up is within-session
        # working state; an episode is cross-session memory. Merging them would
        # have retrieval hand the current conversation back to itself.
        self._summaries: dict[str, str] = {}
        # Facts and episodes. None means memory is off, and every call site
        # below is a no-op — Phase 4's behaviour, unchanged.
        self._memory = memory
        # turn_id -> the retrieval started when the message arrived, awaited
        # later in `_build_context`. Started early so the embed overlaps the
        # message write and the history read.
        self._retrievals: dict[str, asyncio.Task[Retrieved]] = {}
        #: What the user attached to the turn in flight. Started in `send`,
        #: awaited by `_build_context`, remembered by `_finish`, dropped when
        #: the turn ends — the same lifetime and the same shape `_retrievals`
        #: has, for the same reason: it is slow, and the turn should not wait
        #: on it any longer than the one point that genuinely needs it.
        #: The conversation mode, per session. **Per conversation rather
        #: than global**, at Eyaas's explicit choice: a new chat starts at
        #: NORMAL, so a mode set last week cannot silently shape today's
        #: answers. In memory and keyed by session id, the shape
        #: `_summaries` already uses — `sessions` has no settings column,
        #: and a migration for a value that resets on New Chat would be
        #: storing something whose whole point is not to persist.
        self._modes: dict[str, ctx.ConversationMode] = {}
        self._attachment_reads: dict[str, asyncio.Task[list[attach.Attachment]]] = {}
        self._attachments: dict[str, list[attach.Attachment]] = {}
        # Phase 8: the name of the procedure most recently offered via
        # `send_proactive`, if the very next `send()` turns out to be a plain
        # yes/no reply to it. Global, not per-session — proactive messages
        # already are (see `count_proactive_since`) — and one-shot: `send()`
        # clears this on the *next* call regardless of what that call turns
        # out to be, so a stale offer never gets attached to an unrelated
        # message sent an hour later.
        self._pending_procedure_offer: str | None = None

    # ── public API (called by rpc handlers) ─────────────────────────────

    def set_selected_model(self, model_id: str) -> None:
        """Persisted choice: a catalog id, or "smart" to let the router decide."""
        self._selected = model_id

    @property
    def busy(self) -> bool:
        """Whether a turn is in flight.

        Read by the file indexer, which stops entirely while she is answering:
        a turn has a ~1s budget and background embedding competes for the same
        cores (§9 Phase 4b).
        """
        return any(not task.done() for task in self._tasks.values())

    @property
    def selected_model(self) -> str:
        return self._selected

    @property
    def store(self) -> ConversationStore:
        """The message store, for callers that need to resolve a session id."""
        return self._store

    @property
    def routing_bias(self) -> RoutingBias:
        return self._router.bias

    def set_routing_bias(self, bias: RoutingBias) -> None:
        self._router.set_bias(bias)

    async def new_session(self) -> str:
        """Start a fresh conversation, without writing anything yet.

        Returns a *reserved* id: no row exists behind it until the first
        message, because `ConversationStore.ensure_session` creates a row for
        any id it does not recognise. Opening a new chat and closing the window
        therefore leaves no trace.

        The id matters. `send()` with no `session_id` continues the most recent
        conversation by design, so without one to hand back, the first message
        after New Chat would land in the previous conversation.
        """
        # New Chat is the one explicit "I am done with that" the app ever
        # gets, so it is worth an episode. Fire-and-forget: the user is opening
        # a blank page, not waiting on a summary of the old one.
        if self._memory is not None:
            previous = await self._store.latest_session_id()
            if previous:
                spawn(self._memory.episodic.close_session(previous), "memory.close_session")

        session_id = self._store.reserve_session_id()
        self._summaries.pop(session_id, None)
        # Also held here, so a caller that forgets to echo the id back still
        # gets a new conversation rather than silently resuming the old one.
        # Belt and braces on purpose: that failure is invisible until you
        # notice the assistant answering with context you thought you cleared.
        self._pending_new = session_id
        log.info("session.new", session_id=session_id)
        return session_id

    async def list_sessions(
        self, limit: int = 100, query: str | None = None
    ) -> list[SessionSummary]:
        """The history list, plus a nudge to name anything still unnamed.

        Conversations that predate titling — or that ended before the idle job
        could run — would otherwise sit in the list forever labelled by their
        first message, which for three of them here reads "hi", "hi", and "what
        did ieat for breakfast". Opening History queues a few titles in the
        background; the list returned now is unaffected, and the next open shows
        them.
        """
        sessions = await self._store.list_sessions(limit, query)
        queued = 0
        for session in sessions:
            if queued >= TITLE_BACKFILL_PER_CALL:
                break
            if session.title or session.message_count < TITLE_MIN_MESSAGES:
                continue
            if session.id in self._titled:
                continue
            self._maybe_title(session.id)
            queued += 1
        return sessions

    async def rename_session(self, session_id: str, title: str) -> None:
        await self._store.set_title(session_id, title)

    async def delete_session(self, session_id: str) -> int:
        """Remove a conversation. Cancels it first if it is the one in flight."""
        for turn_id, task in list(self._tasks.items()):
            if self._turn_sessions.get(turn_id) == session_id and not task.done():
                task.cancel()

        # Before the store, not after. `episodes.session_id` is a foreign key
        # and `foreign_keys` is ON, so deleting the session with an episode
        # still pointing at it raises FOREIGN KEY constraint failed. Facts
        # learned from those episodes survive with `source_episode` nulled —
        # deleting the conversation does not make what you said untrue.
        if self._memory is not None:
            await self._memory.episodic.forget_session(session_id)

        removed = await self._store.delete_session(session_id)
        # Drop the roll-up note too, or a later session reusing the id would
        # inherit a summary of a conversation that no longer exists.
        self._summaries.pop(session_id, None)
        self._titled.discard(session_id)
        return removed

    async def send(
        self,
        text: str,
        session_id: str | None = None,
        model: str | None = None,
        spoken: bool = False,
        attachments: list[str] | None = None,
    ) -> TurnStarted:
        """Start a turn. Returns immediately; the reply streams as events.

        Omitting `session_id` continues the most recent conversation rather than
        starting one. `ensure_session(None)` mints a new session every call, so
        a client that forgot to echo the id back silently lost all context one
        turn at a time. Starting fresh is `new_session`, and only that — whose
        reserved id takes precedence here, so New Chat works even if the caller
        drops the id it was handed.
        """
        # A message can be nothing but files. Dragging a PDF in and saying
        # nothing is a complete request — "what is this?" is implied by the
        # act, and refusing it would make attaching a two-step operation.
        if not text.strip() and not attachments:
            raise ValueError("Cannot send an empty message.")

        offer = self._pending_procedure_offer
        # One-shot regardless of what this message turns out to be — a
        # window that outlives its own reply is exactly the "follow-up
        # window" mistake §9 Phase 2 already found and removed once.
        self._pending_procedure_offer = None
        if offer is not None:
            resolved = await self._resolve_procedure_reply(text, session_id, offer)
            if resolved is not None:
                return resolved

        resolved_session = await self._store.ensure_session(
            session_id or self._pending_new or await self._store.latest_session_id()
        )
        self._pending_new = None
        turn_id = f"t_{uuid.uuid4().hex[:12]}"

        # Started before the write, not after: the embed then runs alongside
        # the message insert, the router decision and the history read, all of
        # which the turn pays for anyway. §9's 80ms budget is tight enough that
        # this overlap is worth having.
        if self._memory is not None:
            retrieval = self._memory.retriever.prefetch(text)
            self._retrievals[turn_id] = retrieval
            retrieval.add_done_callback(lambda _: None)

        # **Started here, awaited in `_build_context` — not awaited here.**
        #
        # The excerpt does have to reach the prompt the first pass sees, but
        # that point is `_build_context`, not the return of `TurnStarted`, and
        # the gap between them is the whole fix. Reading is sequential and
        # every image is a cloud round trip, so a few of them took longer than
        # the renderer's 30s RPC timeout (`electron/rpc.ts`): the UI reported
        # a failed send while the sidecar carried happily on, and the two
        # states diverged. Now the read overlaps the history read and the
        # memory retrieval instead of preceding them, which is also faster
        # than it was.
        if attachments:
            describe = getattr(
                self._registry.providers.get(str(catalog.ProviderName.OPENAI)),
                "describe_image",
                None,
            )
            self._attachment_reads[turn_id] = asyncio.create_task(
                self._read_attachments(turn_id, attachments, describe)
            )

        # Names come from the paths, not from the read, precisely because the
        # read has not finished. That is also more honest: a file that turns
        # out to be unreadable still belongs in the transcript, or a week
        # later "summarise this" has no record of what "this" was.
        names = [Path(p).name for p in attachments or []]
        stored = text if not names else f"{text}\n\n[attached: {', '.join(names)}]"
        await self._store.add_message(resolved_session, Role.USER, stored.strip())

        task = asyncio.create_task(
            self._run_turn(
                turn_id, resolved_session, text, model or self._selected, spoken=spoken
            )
        )
        self._tasks[turn_id] = task
        self._turn_sessions[turn_id] = resolved_session
        task.add_done_callback(lambda _: self._tasks.pop(turn_id, None))
        task.add_done_callback(lambda _: self._turn_sessions.pop(turn_id, None))
        task.add_done_callback(lambda _: self._retrievals.pop(turn_id, None))
        task.add_done_callback(lambda _: self._attachments.pop(turn_id, None))
        task.add_done_callback(lambda _: self._attachment_reads.pop(turn_id, None))

        return TurnStarted(turn_id=turn_id, session_id=resolved_session)

    def mode_for(self, session_id: str | None) -> ctx.ConversationMode:
        """This conversation's mode, NORMAL until it is set."""
        if session_id is None:
            return ctx.ConversationMode.NORMAL
        return self._modes.get(session_id, ctx.ConversationMode.NORMAL)

    def set_mode(self, session_id: str, mode: ctx.ConversationMode) -> None:
        """Set it for one conversation. NORMAL is stored as an absence, so a
        session that has been set back to NORMAL is indistinguishable from one
        that never moved — which is what it should be."""
        if mode is ctx.ConversationMode.NORMAL:
            self._modes.pop(session_id, None)
        else:
            self._modes[session_id] = mode
        log.info("chat.mode_changed", session_id=session_id, mode=str(mode))

    async def _resolve_procedure_reply(
        self, text: str, session_id: str | None, procedure_name: str
    ) -> TurnStarted | None:
        """The other half of "offer once, wait for a yes" (Part 2). Returns a
        completed `TurnStarted` when `text` was a clear yes/no to the offer
        named `procedure_name`; `None` when it was not, so `send()` falls
        through to an entirely normal turn — an unrelated reply must never be
        read as a decline.

        No model call, on purpose: a plain "yes" or "no" is exactly the case
        Phase 5 already learned not to spend one on. It also means this never
        touches `_run_turn`, so nothing here can invalidate the KV cache the
        stable prefix exists to protect.
        """
        if self._db is None:
            return None
        accepted = _parse_yes_no(text)
        if accepted is None:
            return None

        if accepted:
            await procedures.confirm(self._db, procedure_name)
            reply = "Got it — I'll remember that."
        else:
            await procedures.discard(self._db, procedure_name)
            reply = "No problem, I won't remember it."

        resolved_session = await self._store.ensure_session(
            session_id or self._pending_new or await self._store.latest_session_id()
        )
        self._pending_new = None
        turn_id = f"t_{uuid.uuid4().hex[:12]}"

        await self._store.add_message(resolved_session, Role.USER, text)
        message_id = await self._store.add_message(
            resolved_session, Role.ASSISTANT, reply, route="local"
        )
        await self._bus.broadcast(Event.TOKEN, {"turn_id": turn_id, "text": reply})
        await self._bus.broadcast(
            Event.TURN_COMPLETE,
            {
                "turn_id": turn_id,
                "message_id": message_id,
                "full_text": reply,
                "route": "local",
                "model": self._model,
                "model_label": self._model,
                "route_reason": "procedure_offer_reply",
                "note": None,
                "latency_ms": 0,
                "first_token_ms": None,
            },
        )
        await self._bus.set_state(AssistantState.IDLE)
        log.info("procedure.offer_resolved", name=procedure_name, accepted=accepted)
        return TurnStarted(turn_id=turn_id, session_id=resolved_session)

    async def cancel(self, turn_id: str) -> bool:
        """Abort an in-flight turn. Returns False if it was already finished."""
        task = self._tasks.get(turn_id)
        if task is None or task.done():
            return False
        task.cancel()
        # Silence first, and without waiting for the task to unwind: audio
        # already queued in the renderer would otherwise keep talking for
        # seconds after the stop button. Stage 3's barge-in reuses this exact
        # event, which is why the flush lives here rather than inside cancel's
        # own cleanup.
        await self._bus.broadcast(Event.AUDIO_STOP, {"turn_id": turn_id})
        log.info("turn.cancel_requested", turn_id=turn_id)
        return True

    async def cancel_active(self) -> int:
        """Cancel every in-flight turn. Returns how many there were.

        Barge-in has no turn id to aim at — someone talked over whatever was
        speaking — so it stops all of them. In practice that is zero or one.
        """
        cancelled = 0
        for turn_id, task in list(self._tasks.items()):
            if task.done():
                continue
            task.cancel()
            await self._bus.broadcast(Event.AUDIO_STOP, {"turn_id": turn_id})
            cancelled += 1
        return cancelled

    async def history(self, session_id: str | None, limit: int = 200) -> ConversationHistory:
        """Reload the conversation — the Phase 1 gate's relaunch requirement."""
        resolved = session_id or await self._store.latest_session_id()
        if resolved is None:
            return ConversationHistory(session_id=None, messages=[])
        return ConversationHistory(
            session_id=resolved,
            messages=await self._store.history(resolved, limit),
        )

    async def shutdown(self) -> None:
        for task in list(self._tasks.values()):
            task.cancel()
        await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        # Background titling holds a database handle. Cancel and drain it too,
        # or the connection closes underneath a job still writing to it.
        for job in list(self._jobs):
            job.cancel()
        await asyncio.gather(*self._jobs, return_exceptions=True)
        # A retrieval that passed its deadline is still running detached, for
        # the cache. It also holds a database handle.
        for retrieval in list(self._retrievals.values()):
            retrieval.cancel()
        await asyncio.gather(*self._retrievals.values(), return_exceptions=True)
        self._retrievals.clear()
        if self._memory is not None:
            await self._memory.retriever.aclose()

    # ── the turn itself ─────────────────────────────────────────────────

    async def _run_turn(
        self,
        turn_id: str,
        session_id: str,
        user_text: str,
        selected: str,
        spoken: bool = False,
    ) -> None:
        started = time.perf_counter()
        collected: list[str] = []
        # A spoken turn ignores the quality bias and stays on this machine.
        # Measured in stage 1: routed to Gemini, first audio landed at 1707ms
        # against 872ms locally — the network hop alone eats the budget.
        decision = self._router.choose(
            user_text,
            selected=selected,
            available=self._usable_models() if self._usable_models else None,
            spoken=spoken,
            # The conversation's mode may ask for a different class of model.
            # It cannot reach past the privacy or explicit-choice stages —
            # `_by_bias` runs after both.
            bias=MODE_BIAS[str(self.mode_for(session_id))],
            # Router stage 2b. The attachment is not in `user_text` — the
            # excerpt is assembled later — so the privacy regex cannot see it.
            carries_user_content=self._turn_has_attachments(turn_id),
        )
        log.info(
            "turn.routed",
            turn_id=turn_id,
            model=decision.model.id,
            stage=decision.reason.stage,
            mode=str(self.mode_for(session_id)),
            bias=str(self._router.bias),
            fallbacks=[m.id for m in decision.fallbacks],
        )

        # The chosen model, then its fallbacks (§9.7 stage 7). Never a silent
        # swap: each attempt after the first tells the user what happened.
        chain: list[ModelInfo] = [decision.model, *decision.fallbacks]
        note: str | None = None

        try:
            await self._bus.set_state(AssistantState.THINKING)

            for attempt, info in enumerate(chain):
                messages = await self._build_context(session_id, info, turn_id)
                state = LoopState()
                try:
                    first_token_ms, final_info, loop_note = await self._agent_loop(
                        turn_id,
                        session_id,
                        info,
                        messages,
                        collected,
                        started,
                        user_text=user_text,
                        selected=selected,
                        spoken=spoken,
                        state=state,
                    )
                except (ProviderUnavailable, ProviderRateLimited) as exc:
                    self._health.record_failure(
                        info.id, str(exc), rate_limited=isinstance(exc, ProviderRateLimited)
                    )
                    # Anything already on screen came from a model that will not
                    # finish. Tell the renderer to drop it, or the replacement
                    # reply appends to a half-sentence from someone else.
                    if collected:
                        collected.clear()
                        await self._bus.broadcast(Event.TURN_RESET, {"turn_id": turn_id})
                    if attempt + 1 >= len(chain):
                        await self._on_error(turn_id, str(exc))
                        return
                    nxt = chain[attempt + 1]
                    note = f"{info.label} was unavailable, so {nxt.label} answered instead."
                    log.warning(
                        "turn.failover", turn_id=turn_id, tried=info.id, next=nxt.id
                    )
                    await self._bus.send_error("provider_failover", note, recoverable=True)
                    continue

                if loop_note:
                    note = f"{note} {loop_note}".strip() if note else loop_note

                self._health.record_success(final_info.id, first_token_ms)
                tool_name, tool_ok = self._turn_tools.pop(turn_id, (None, None))
                await self._finish(
                    turn_id,
                    session_id,
                    collected,
                    started,
                    first_token_ms,
                    final_info,
                    decision,
                    note,
                    spoken=spoken,
                    asked=user_text,
                    tool_called=tool_name,
                    tool_ok=tool_ok,
                )
                return

        except asyncio.CancelledError:
            await self._on_cancelled(turn_id, session_id, collected, started)
            raise
        except ProviderError as exc:
            await self._on_error(turn_id, str(exc))
        except Exception as exc:  # one bad turn must not kill the sidecar
            log.exception("turn.failed", turn_id=turn_id)
            await self._on_error(
                turn_id,
                f"That turn failed: {exc}. See data/logs/sidecar.log for the traceback.",
            )

    async def _stream_one(
        self,
        turn_id: str,
        info: ModelInfo,
        messages: list[ChatMessage],
        collected: list[str],
        started: float,
        *,
        tool_calls: list[ToolCall] | None = None,
        offer_tools: bool = True,
    ) -> float | None:
        """Stream one model's reply into `collected`. Returns TTFT in ms.

        `tool_calls` collects anything the model asked to run. `offer_tools`
        is False once `_agent_loop`'s step budget is spent (BUILD_SPEC §9
        Phase 6) — a model handed its own tools with no budget left to run
        one would just be asked to describe the call it cannot make.
        """
        provider = self._registry.for_model(info)
        await self._free_vram_for(info)
        first_token_ms: float | None = None
        speech = SpeechStream(
            self._tts, self._bus, started, speed=await self._current_speech_speed()
        )

        async for delta in provider.stream_chat(
            messages,
            model=info.id,
            options=GenerationOptions(
                num_ctx=min(self._num_ctx, info.context_tokens),
                temperature=info.temperature,
            ),
            tools=self._tool_schemas() if offer_tools else None,
        ):
            if delta.tool_calls and tool_calls is not None:
                tool_calls.extend(delta.tool_calls)
            if delta.text:
                if first_token_ms is None:
                    first_token_ms = (time.perf_counter() - started) * 1000
                    # The Phase 1 gate is a number, so it gets logged as one.
                    log.info(
                        "turn.first_token",
                        turn_id=turn_id,
                        model=info.id,
                        first_token_ms=round(first_token_ms, 1),
                        budget_ms=700,
                        within_budget=first_token_ms < 700,
                    )
                collected.append(delta.text)
                await self._bus.broadcast(Event.TOKEN, {"turn_id": turn_id, "text": delta.text})
                # Speech reads `delta.text` — the content channel — and never
                # `delta.thinking`. qwen3.5 streams reasoning separately, and
                # reading that aloud would be the worst bug this project has.
                speech.feed(delta.text)
                await speech.drain(turn_id)
            if delta.done:
                break

        await speech.finish(turn_id)
        return first_token_ms

    def _tool_schemas(self) -> list[dict[str, Any]] | None:
        """What the model is allowed to know exists.

        None rather than an empty list when there is no permission engine:
        some Ollama builds refuse a request carrying an empty `tools` array.

        **The ceiling follows `allow_danger_tools`.** It did not, and the flag
        was therefore dead: the engine would happily execute a DANGER tool
        after a typed confirmation, but `schemas()` never told the model such a
        tool existed, so nothing could ever ask for one. Asked to delete a real
        file with the flag on, she answered "I cannot delete files with my
        current tools" — correctly, from what she had been given.

        Off, the behaviour is unchanged and is the one §7.2 wants: the model is
        not told those tools exist at all, which is stronger than asking it not
        to use them.

        **`research` is hidden the same way when online mode is off**, and for
        the same reason stated the other way round: telling a model a tool
        exists and then refusing it is how she ends up saying "let me look that
        up" and then not looking it up. The tool refuses too — two gates, and
        the whole lesson of `allow_danger_tools` is that they must move
        together.

        **`PermissionMode.FULL_ACCESS` grants the same ceiling `allow_danger`
        does, for the identical reason.** `PermissionEngine.run` already lets
        a DANGER tool execute in that mode with nothing asked; a model never
        told the tool exists would be the exact "I cannot delete files"
        contradiction above, reintroduced through a second flag instead of
        the first one.
        """
        if self._permissions is None:
            return None
        full_access = self._permissions.mode is PermissionMode.FULL_ACCESS
        ceiling = Tier.DANGER if (self._permissions.allow_danger or full_access) else Tier.CONFIRM
        hidden = set() if runtime.online_mode else ONLINE_TOOLS
        return registry.schemas(tier_max=ceiling, exclude=hidden) or None

    async def _agent_loop(
        self,
        turn_id: str,
        session_id: str,
        info: ModelInfo,
        messages: list[ChatMessage],
        collected: list[str],
        started: float,
        *,
        user_text: str,
        selected: str,
        spoken: bool,
        state: LoopState,
    ) -> tuple[float | None, ModelInfo, str | None]:
        """Run steps until a text answer, loop detection, or the step budget
        ends it (BUILD_SPEC §9 Phase 6). Returns `(first_token_ms, model that
        answered, a note worth surfacing)`.

        **A provider failure on step 0 propagates.** The caller's own
        `chain`/`attempt` loop already handles that exactly as it always has —
        rebuild context, try the next provider. A failure on step ≥ 1 is
        different: this loop has already made progress this turn, and losing
        it to fail over the *whole turn* onto a fresh context would throw away
        real tool results for the failure of one step. It degrades to the
        local default instead and keeps going — §9's own acceptance line asks
        for a mid-chain network pull to recover, not to abort.
        """
        current = info
        note: str | None = None
        first_token_ms: float | None = None
        # Set right after a mid-task degrade, and only there. It exists so
        # the *next* line — the top-of-loop router reselect — does not
        # immediately undo the degrade it is about to retry. Without this a
        # degrade routed straight back through `Router.choose`, which had
        # just watched `_health.record_failure` trip that model's cooldown
        # and dutifully handed back the *next*-best cloud model instead of
        # local — so one outage walked the entire catalog, health-tripping
        # every model in it, before finally reaching local by attrition.
        just_degraded = False

        while True:
            # Step-aware routing (§9.7 stage 3's `step >= 3` upgrade) only
            # ever *raises* the model reached for — a local-only tool's
            # privacy constraint (`state.sticky_local`) always wins over it,
            # or a deep-reasoning upgrade on step 3 could leak a clipboard
            # read on step 1 to the cloud on step 3.
            if state.step > 0 and not state.sticky_local and not just_degraded:
                decision = self._router.choose(
                    user_text,
                    selected=selected,
                    available=self._usable_models() if self._usable_models else None,
                    step=state.step,
                    spoken=spoken,
                    bias=MODE_BIAS[str(self.mode_for(session_id))],
                    # Still true on step 4 as it was on step 0: the excerpt is
                    # in the message history the whole turn, so a later step
                    # re-routing away from the constraint would hand the file
                    # to exactly the endpoint it was kept from.
                    carries_user_content=self._turn_has_attachments(turn_id),
                )
                current = decision.model
            just_degraded = False

            requested: list[ToolCall] = []
            try:
                first_token_ms = await self._stream_one(
                    turn_id,
                    current,
                    messages,
                    collected,
                    started,
                    tool_calls=requested,
                    offer_tools=state.offer_tools,
                )
            except (ProviderUnavailable, ProviderRateLimited) as exc:
                if state.step == 0:
                    raise
                local = catalog.get(self._model) or catalog.default_local()
                if current.id == local.id:
                    # Already degraded to the local default once this loop and
                    # it failed too — retrying the same model forever is not a
                    # degrade, it's a hang. Let it propagate: the outer
                    # `chain`/`attempt` loop's own failover, or a plain error,
                    # is the honest fallback left when even Ollama is down.
                    raise
                self._health.record_failure(
                    current.id, str(exc), rate_limited=isinstance(exc, ProviderRateLimited)
                )
                # Appended, never overwritten — a turn that degrades more than
                # once (one per cloud model it tries, in the worst case) must
                # not have every note but the last one silently vanish, and an
                # exhaustion note already sitting here from an earlier step
                # must survive a later degrade too.
                degrade_note = (
                    f"{current.label} was unavailable mid-task, so {local.label} finished it."
                )
                note = f"{note} {degrade_note}".strip() if note else degrade_note
                log.warning(
                    "turn.agent_degrade",
                    turn_id=turn_id,
                    step=state.step,
                    tried=current.id,
                    next=local.id,
                )
                await self._bus.send_error("provider_failover", note, recoverable=True)
                current = local
                just_degraded = True
                continue  # retry the same step locally, nothing lost

            if requested and not state.offer_tools:
                # No real provider does this — `tools=None` was sent, so it
                # has nothing to call. Trusting a `tool_calls` list anyway
                # would let a misbehaving provider keep this loop going past
                # its own budget forever; discard it and let the text (if
                # any) stand as the answer instead.
                log.warning(
                    "turn.agent_ignored_unsolicited_call", turn_id=turn_id, step=state.step
                )
                requested = []

            if not requested:
                # A turn must never end silently. The model can finish a pass
                # with zero text deltas — observed on `gate_agent.py`'s
                # find -> read -> answer line, where it spends its steps on a
                # file it cannot see and then says nothing — and everything
                # downstream of here happily stores and broadcasts that empty
                # string. To the user it is identical to a hung app.
                if not "".join(collected).strip():
                    log.warning(
                        "turn.empty_reply",
                        turn_id=turn_id,
                        step=state.step,
                        tool=state.last_tool,
                    )
                    collected.append(silent_reply_note(state.last_tool, state.last_summary))
                return first_token_ms, current, note

            call = requested[0]
            dropped = requested[1:]
            if dropped:
                log.info(
                    "turn.tools_dropped", turn_id=turn_id, dropped=[c.name for c in dropped]
                )

            if state.would_repeat(call.name, call.arguments):
                log.info(
                    "turn.loop_detected", turn_id=turn_id, tool=call.name, step=state.step
                )
                if collected:
                    collected.clear()
                    await self._bus.broadcast(Event.TURN_RESET, {"turn_id": turn_id})
                collected.append(repeat_note(call.name))
                return first_token_ms, current, note

            tool = registry.get(call.name)

            await self._bus.broadcast(
                Event.TOOL_CALL,
                {
                    "turn_id": turn_id,
                    "call_id": call.id,
                    "tool": call.name,
                    "args": call.arguments,
                    "step": state.step,
                },
            )

            # A tool call can only ever be `requested` when `_tool_schemas()`
            # offered them in the first place, and that already requires a
            # permission engine (`_tool_schemas` returns None without one) —
            # so this can't fire, but it says so rather than a bare crash if
            # that invariant is ever broken by a future change.
            assert self._permissions is not None
            # §11 asks about the *next* call, so the loop has to name it
            # before asking. Set here rather than passed as an argument, so
            # `should_escalate` stays a property one test can drive off a
            # bare `LoopState` with nothing running.
            state.pending_tool = call.name
            result = await self._permissions.run(
                call.name,
                call.arguments,
                ToolContext(session_id=session_id, turn_id=turn_id),
                rationale="".join(collected).strip()[:400],
                # §11: a call right after reading untrusted content is forced
                # through confirmation regardless of its own registered tier.
                force_confirm=state.should_escalate,
            )

            # For the routing log: whether the model's chosen tool actually
            # worked is the single most useful label there is about a
            # tool-shaped turn, and `_finish` is where the row is written.
            self._turn_tools[turn_id] = (call.name, result.ok)

            await self._bus.broadcast(
                Event.TOOL_RESULT,
                {
                    "turn_id": turn_id,
                    "call_id": call.id,
                    "tool": call.name,
                    "ok": result.ok,
                    "summary": result.summary,
                    "display": result.display,
                    "step": state.step,
                },
            )

            # Whatever it said before asking for the tool was preamble to an
            # answer it did not have yet. Clearing stops the reply reading as
            # two halves of different sentences.
            if collected:
                collected.clear()
                await self._bus.broadcast(Event.TURN_RESET, {"turn_id": turn_id})

            drop_note = ""
            if dropped:
                names = ", ".join(c.name for c in dropped)
                drop_note = (
                    f" You also asked for {names} in the same step; only one "
                    f"tool runs per step, so those were not done."
                )

            state.record(
                call.name,
                call.arguments,
                local_only=bool(tool and tool.local_only),
                summary=result.summary,
                ok=result.ok,
            )

            # Only `summary` goes back — never `data` or `display`. §7.2 names
            # pasting tool output into the context as the second failure mode.
            messages.append(ChatMessage(role=Role.ASSISTANT, content="", tool_calls=[call]))
            messages.append(
                ChatMessage(
                    role=Role.TOOL,
                    content=result.summary + drop_note,
                    tool_call_id=call.id,
                    name=call.name,
                )
            )

            if state.exhausted:
                # Not a return here — one more pass still runs below, with
                # `state.offer_tools` now False, so the model gets to answer
                # in text with whatever it has gathered rather than being cut
                # off mid-task. The explanation goes out on `note`
                # (surfaced via `TURN_COMPLETE`), the same channel a
                # provider failover already uses — never smuggled into the
                # model's own words as if it had said this itself.
                note = f"{note} {exhausted_note()}".strip() if note else exhausted_note()
                log.warning("turn.agent_exhausted", turn_id=turn_id, step=state.step)

            # This tool's own local-only-ness, or a prior step's, sticks for
            # every step after it — not just the one immediately following.
            current = self._continuation_model(call.name, current)
            if state.sticky_local and not current.local:
                current = catalog.get(self._model) or catalog.default_local()

            await self._bus.set_state(AssistantState.THINKING)

    def _continuation_model(self, tool_name: str, info: ModelInfo) -> ModelInfo:
        """Which model gets to see the tool's result.

        `router._PRIVATE` already keeps a turn local when the *message* names
        something private, but it decides before the tool has run, from the
        user's words. "what did I just copy" does not match it, would route to
        a cloud provider, and that provider would then be handed the clipboard
        on this pass — which is the pass where the result actually enters a
        prompt. So the decision belongs here, after the call, not there.
        """
        tool = registry.get(tool_name)
        if tool is None or not tool.local_only or info.local:
            return info

        # `self._model` is the local default this service was started with,
        # already checked against what Ollama has pulled.
        local = catalog.get(self._model) or catalog.default_local()
        log.info(
            "turn.forced_local",
            tool=tool_name,
            was=info.id,
            now=local.id,
            why="tool result must not leave the machine",
        )
        return local

    async def _free_vram_for(self, info: ModelInfo) -> None:
        """Evict the previous local model before loading a different one.

        CLAUDE.md rule 2: one model on the GPU. Ollama holds a model for
        `keep_alive=30m`, so switching local models in the picker would ask a
        6GB card to hold both — measured, that stalls generation for minutes
        rather than failing, which the user experiences as a hang.
        """
        if not info.local or info.id == self._resident_local:
            return

        previous = self._resident_local
        self._resident_local = info.id
        if previous is None:
            return

        provider = self._registry.providers.get(str(catalog.ProviderName.OLLAMA))
        unload = getattr(provider, "unload", None)
        if unload is None:
            return
        log.info("model.switch", was=previous, now=info.id)
        await unload(previous)

    async def _finish(
        self,
        turn_id: str,
        session_id: str,
        collected: list[str],
        started: float,
        first_token_ms: float | None,
        info: ModelInfo,
        decision: RouteDecision,
        note: str | None = None,
        *,
        spoken: bool = False,
        asked: str = "",
        tool_called: str | None = None,
        tool_ok: bool | None = None,
    ) -> None:
        full_text = "".join(collected)
        total_ms = int((time.perf_counter() - started) * 1000)
        route = "local" if info.local else "cloud"

        message_id = await self._store.add_message(
            session_id,
            Role.ASSISTANT,
            full_text,
            route=route,
            latency_ms=total_ms,
        )
        self._log_route(
            message_id,
            session_id,
            info,
            decision,
            total_ms,
            spoken=spoken,
            asked=asked,
            tool_called=tool_called,
            tool_ok=tool_ok,
        )
        if self._db is not None and asked:
            # Off the turn path, same as `_log_route` above — the reply is
            # already on screen, and a mood update is worth none of the
            # user's milliseconds. A failure here logs and never touches it.
            spawn(self._update_affect(session_id, asked), "affect.update")

        attached = self._attachments.get(turn_id, [])
        if attached and self._memory is not None:
            # Indexing embeds every chunk and a big PDF is a lot of chunks —
            # nowhere near the turn path. Same channel as the affect update,
            # and it swallows its own errors for the same reason: failing to
            # remember a file must never cost the answer about it.
            spawn(
                attach.remember(attached, self._memory.semantic, runtime.indexer),
                "attachment.remember",
            )
        await self._bus.broadcast(
            Event.TURN_COMPLETE,
            {
                "turn_id": turn_id,
                "message_id": message_id,
                "full_text": full_text,
                "route": route,
                # The UI must always name what actually answered, including
                # after a failover — never a silent swap.
                "model": info.id,
                "model_label": info.label,
                "route_reason": decision.reason.detail,
                "note": note,
                "latency_ms": total_ms,
                "first_token_ms": round(first_token_ms, 1) if first_token_ms else None,
            },
        )
        await self._bus.set_state(AssistantState.IDLE)
        self._maybe_title(session_id)

    def _log_route(
        self,
        message_id: int,
        session_id: str,
        info: ModelInfo,
        decision: RouteDecision,
        latency_ms: int,
        *,
        spoken: bool,
        asked: str,
        tool_called: str | None,
        tool_ok: bool | None,
    ) -> None:
        """Record the decision for §9.7's labelled dataset. Off the turn path.

        Spawned rather than awaited, and after `add_message` rather than before:
        the reply is already on screen, and no routing statistic is worth a
        millisecond of the user's time. `RoutingLog.record` swallows its own
        errors on top of that — this must never be able to fail a turn.

        The *inputs* are recorded beside the outcome (bias, spoken, tool_shaped,
        length), because a row saying only which model answered cannot be used
        to tune anything. That is what `messages.route` already was.
        """
        if self._routing_log is None:
            return
        record = RoutingRecord(
            message_id=message_id,
            session_id=session_id,
            model=info.id,
            provider=str(info.provider),
            local=info.local,
            stage=decision.reason.stage,
            detail=decision.reason.detail,
            bias=str(self._router.bias),
            spoken=spoken,
            tool_shaped=is_tool_shaped(asked),
            chars=len(asked),
            latency_ms=latency_ms,
            tool_called=tool_called,
            tool_ok=tool_ok,
        )
        spawn(self._routing_log.record(record), "routing.record")

    # ── proactivity (Phase 8) ──────────────────────────────────────────

    async def send_proactive(
        self,
        text: str,
        *,
        urgency: str = "normal",
        trigger: str = "",
        procedure_name: str | None = None,
    ) -> int | None:
        """Deliver a message with no preceding question. Called by
        `persona.proactivity.ProactivityScheduler`, never by a turn.

        Reuses `_finish`'s own shapes rather than inventing new ones: a
        `messages` row (`proactive=1`, migration 006) through the same
        `ConversationStore` every reply already goes through, and a
        `routing_log` row through the same `RoutingLog` every reply already
        writes — which is what makes the *existing* `turn.rate` thumbs
        mechanism work on a proactive message for free, no parallel rating
        system, no new UI. Returns the stored message id, or `None` if there
        is nowhere to attach it (no session exists yet).

        `procedure_name` is set only for a `procedure_offer` candidate
        (`persona.proactivity.Candidate.ref`) — it arms `_resolve_procedure_reply`
        so the very next `send()` can turn a plain "yes" into
        `procedures.confirm` without a model call.
        """
        self._pending_procedure_offer = procedure_name
        session_id = await self._store.latest_session_id()
        if session_id is None:
            session_id = await self._store.ensure_session(None)

        message_id = await self._store.add_message(
            session_id, Role.ASSISTANT, text, route="local", proactive=True
        )

        if self._routing_log is not None:
            local = catalog.get(self._model) or catalog.default_local()
            record = RoutingRecord(
                message_id=message_id,
                session_id=session_id,
                model=local.id,
                provider=str(local.provider),
                local=True,
                stage="proactive",
                detail=trigger,
                bias=str(self._router.bias),
                chars=len(text),
            )
            spawn(self._routing_log.record(record), "routing.record")

        await self._bus.broadcast(
            Event.PROACTIVE,
            {
                "text": text,
                "urgency": urgency,
                "message_id": message_id,
                "session_id": session_id,
            },
        )
        log.info("proactive.sent", trigger=trigger, chars=len(text))
        return message_id

    # ── titles ──────────────────────────────────────────────────────────

    def _maybe_title(self, session_id: str) -> None:
        """Name the conversation once it has enough content to name.

        Deliberately fire-and-forget, after `set_state(IDLE)`: the reply is
        already on screen, and a title is worth zero milliseconds of the user's
        time. Awaiting it here would put a second model call on the latency path
        that Phase 1 spent itself measuring.
        """
        if session_id in self._titled:
            return
        self._titled.add(session_id)  # claim it now; one attempt per session per run

        job = asyncio.create_task(self._generate_title(session_id))
        self._jobs.add(job)
        job.add_done_callback(self._jobs.discard)

    async def _wait_for_idle(self) -> bool:
        """Hold until no turn is in flight. False if the user never stops."""
        deadline = time.monotonic() + TITLE_IDLE_TIMEOUT_S
        while time.monotonic() < deadline:
            await asyncio.sleep(TITLE_IDLE_DELAY_S)
            if not self._tasks:
                return True
        return False

    async def _generate_title(self, session_id: str) -> None:
        """Ask the local model for a short label. Never raises."""
        try:
            if not await self._wait_for_idle():
                self._titled.discard(session_id)  # a later turn will retry
                return
            if await self._store.get_title(session_id):
                return
            history = await self._store.history(session_id)
            if len(history) < TITLE_MIN_MESSAGES:
                self._titled.discard(session_id)  # try again once it has grown
                return

            # `history` is oldest-first, so this is the *opening* of the
            # conversation. Titling by the tail would name a long session after
            # wherever it drifted to, which is not what you would search for.
            opening = ctx.to_chat_messages(history[:TITLE_FROM_TURNS])

            chunks: list[str] = []
            async for delta in self._provider.stream_chat(
                ctx.title_request(opening),
                model=self._model,
                options=GenerationOptions(num_ctx=self._num_ctx, max_tokens=32),
            ):
                chunks.append(delta.text)
                if delta.done:
                    break

            title = ctx.clean_title("".join(chunks))
            if title:
                await self._store.set_title(session_id, title)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — a title is never worth an error
            log.warning("session.title_failed", session_id=session_id, error=str(exc))

    async def _on_cancelled(
        self, turn_id: str, session_id: str, collected: list[str], started: float
    ) -> None:
        """Persist whatever was generated — a half reply is still conversation."""
        partial = "".join(collected)
        if partial:
            await self._store.add_message(
                session_id,
                Role.ASSISTANT,
                partial,
                route="local",
                latency_ms=int((time.perf_counter() - started) * 1000),
            )
        await self._bus.broadcast(
            Event.TURN_COMPLETE,
            {
                "turn_id": turn_id,
                "full_text": partial,
                "route": "local",
                "cancelled": True,
            },
        )
        await self._bus.set_state(AssistantState.IDLE)
        log.info("turn.cancelled", turn_id=turn_id, kept_chars=len(partial))

    async def _on_error(self, turn_id: str, message: str) -> None:
        await self._bus.send_error("turn_failed", message, recoverable=True)
        await self._bus.broadcast(
            Event.TURN_COMPLETE,
            {"turn_id": turn_id, "full_text": "", "route": "local", "error": message},
        )
        await self._bus.set_state(AssistantState.IDLE)

    # ── context ─────────────────────────────────────────────────────────

    async def _build_context(
        self, session_id: str, info: ModelInfo | None = None, turn_id: str | None = None
    ) -> list[ChatMessage]:
        # Persona is per-model: the full character makes weak models hostile and
        # prone to inventing context (see core/context.PersonaLevel).
        level = info.persona if info else ctx.PersonaLevel.FULL
        cap = min(self._num_ctx, info.context_tokens) if info else self._num_ctx
        mode = self.mode_for(session_id)

        # Gathered, not sequenced: the retrieval started back in `send()` and
        # the history read is a thread hop, so the two overlap instead of
        # adding up.
        # Three slow things at once rather than in a row: the history read is
        # a thread hop, the retrieval started back in `send()`, and so did the
        # attachment read. Overlapping them makes an attached image cost less
        # than it did when it blocked `send()` outright.
        history, retrieval, _ = await asyncio.gather(
            self._store.history(session_id),
            self._await_retrieval(turn_id),
            self._await_attachments(turn_id),
        )
        retrieved = retrieval.render() if retrieval else None
        turns = ctx.to_chat_messages(history)
        summary = self._summaries.get(session_id)
        machine = self._machine_context(info, history)
        affect = await self._current_affect()
        # The most recent stored message is this turn's own user text —
        # `send()` already persisted it before `_run_turn` started, so this
        # is what's already loaded rather than a new parameter threaded
        # through from the call site.
        procedure_hint = None
        if self._db is not None and history and history[-1].role is Role.USER:
            procedure_hint = await procedures.context_hint(self._db, history[-1].content)

        # Budget for turns is what's left after identity + any roll-up note.
        #
        # Roll-up used to happen *here*, awaited, which put a second model call
        # in front of the first token on whichever turn crossed the budget. It
        # now runs in the background: this turn drops the oldest turns to fit and
        # answers immediately, and the summary it produces lands in time for the
        # next one. Voice has a ~1000ms end-to-end budget and cannot absorb a
        # second generation.
        has_tools = self._tool_schemas() is not None
        # The capability paragraph has to follow the switch, or she declines to
        # look up something she can look up — the Phase 3 "I cannot run
        # programs" failure, in the other direction.
        online = has_tools and runtime.online_mode
        turn_budget = self._budget - ctx.overhead_tokens(
            summary,
            level,
            machine,
            has_tools=has_tools,
            retrieved=retrieved,
            online=online,
            affect=affect,
            procedure_hint=procedure_hint,
            mode=mode,
        )
        to_summarize, kept = ctx.split_for_rollup(turns, max(turn_budget, 0))
        if to_summarize:
            self._schedule_roll_up(session_id, to_summarize, summary)
            turns = kept

        # Hard backstop: the summarizer is a model call and can return anything.
        turns = ctx.fit_to_budget(
            turns,
            summary=summary,
            hard_cap_tokens=cap,
            level=level,
            machine=machine,
            has_tools=has_tools,
            retrieved=retrieved,
            online=online,
            affect=affect,
            procedure_hint=procedure_hint,
            mode=mode,
        )
        messages = ctx.assemble(
            turns,
            summary=summary,
            level=level,
            machine=machine,
            has_tools=has_tools,
            retrieved=retrieved,
            online=online,
            affect=affect,
            procedure_hint=procedure_hint,
            mode=mode,
        )

        # **After the turns, not in the volatile prefix.** An attached file is
        # about the question being asked right now, so it belongs next to it —
        # and appending here leaves the stable prefix byte-identical, which is
        # what keeps Ollama's KV cache worth having (~1s a turn). It is also
        # dropped the moment the turn ends: the *text* of a PDF is not
        # conversation history, and re-sending it on every later turn would
        # eat the budget for something already summarised into memory.
        block = attach.render(self._attachments.get(turn_id or "", []))
        if block:
            messages.append(ChatMessage(role=Role.SYSTEM, content=block))
        return messages

    def _turn_has_attachments(self, turn_id: str) -> bool:
        """Whether this turn is carrying files the user handed over.

        True while the read is still in flight, not only once it lands: the
        routing decision happens before `_build_context` awaits the excerpt,
        and a check that waits for the content would put a file read in front
        of the first token. Erring towards "yes" costs at most a free model not
        being used for one turn; erring the other way sends his document
        somewhere it should not go.
        """
        return turn_id in self._attachment_reads or bool(self._attachments.get(turn_id))

    async def _read_attachments(
        self, turn_id: str, paths: list[str], describe: object
    ) -> list[attach.Attachment]:
        """Read each file, telling the UI about each one as it lands.

        The per-file event is the fix for the bug this whole feature had: a
        `.ppt` that could not be parsed was recorded in a log line and nowhere
        else, so the only clue was a vague reply. It doubles as the progress
        signal — reading is off the RPC path now, and without this the
        composer would sit silent while several images make cloud round trips.
        """
        read: list[attach.Attachment] = []
        for path in paths:
            one = await attach.read_one(Path(path), describe)
            read.append(one)
            await self._bus.broadcast(
                Event.ATTACHMENT_READ,
                {
                    "turn_id": turn_id,
                    "name": one.name,
                    "ok": one.ok,
                    "summary": one.summary,
                },
            )
        self._attachments[turn_id] = read
        log.info(
            "turn.attachments",
            turn_id=turn_id,
            files=[a.name for a in read],
            unreadable=[a.name for a in read if not a.ok],
        )
        return read

    async def _await_attachments(self, turn_id: str | None) -> None:
        """Collect what `send()` started, and never let it hold the turn.

        A pathological file must not hang the answer forever — moving the read
        off the RPC path removed the *timeout*, not the possibility of a hang,
        so this is the ceiling. On expiry the turn proceeds with whatever
        finished, which is the same call `_await_retrieval` makes: losing an
        attachment costs the answer some context, losing the answer costs
        everything.
        """
        if turn_id is None:
            return
        task = self._attachment_reads.get(turn_id)
        if task is None:
            return
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=ATTACHMENT_READ_TIMEOUT_S)
        except TimeoutError:
            log.warning("turn.attachments_timed_out", turn_id=turn_id)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            log.warning("turn.attachments_failed", turn_id=turn_id, error=str(exc))

    async def _await_retrieval(self, turn_id: str | None) -> Retrieved | None:
        """Collect what `send()` started. None when memory is off or it failed.

        Retrieval is never allowed to break a turn: anything that goes wrong
        here costs recall, which the user can live without, rather than the
        answer, which they cannot.
        """
        if turn_id is None:
            return None
        task = self._retrievals.get(turn_id)
        if task is None:
            return None
        try:
            result = await task
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            log.warning("memory.retrieval_failed", turn_id=turn_id, error=str(exc))
            return None

        if not result.empty and self._memory is not None:
            # An access is a database write and the user is waiting. Off the
            # path, like titling.
            spawn(
                self._memory.episodic.record_access(result.episode_ids()),
                "memory.record_access",
            )
        return result

    async def _current_affect(self) -> str | None:
        """The one line naming how she currently reads (Phase 8).

        Read-only and cheap — a single-row `SELECT` — so this is awaited
        inline like `machine_context`'s own reads, not spawned. Only the
        *write* after the turn (`_finish`, below) is off the critical path;
        there is nothing to gain by delaying a read this small.
        """
        if self._db is None:
            return None
        try:
            state = await affect_module.load(self._db)
        except Exception:  # noqa: BLE001 — never let this fail a turn
            log.warning("affect.load_failed", exc_info=True)
            return None
        return affect_module.render(state, datetime.now().astimezone())

    async def _current_speech_speed(self) -> float:
        """Phase 8 voice polish's affect-driven nudge to `KokoroTTS.synthesize`.

        Same single-row read as `_current_affect`, kept separate because that
        one wants a rendered string for the prompt and this one wants the raw
        floats. `1.0` — the engine's own neutral default — whenever there is
        no affect to read, so a turn with memory off sounds exactly as it did
        before this phase existed.
        """
        if self._db is None:
            return 1.0
        try:
            state = await affect_module.load(self._db)
        except Exception:  # noqa: BLE001 — a voice nudge is never worth a failed turn
            log.warning("affect.load_failed", exc_info=True)
            return 1.0
        return affect_module.speech_speed(state)

    async def _update_affect(self, session_id: str, latest_user_text: str) -> None:
        """The write half of Phase 8's affect model — spawned from `_finish`,
        never awaited on the turn. Re-reads history rather than threading it
        through from `_build_context`: this runs seconds after the reply
        already streamed, on a background task, so one more cheap read costs
        nothing a user is waiting on.
        """
        if self._db is None:
            return
        history = await self._store.history(session_id)
        started = _session_started_at(history) or datetime.now(UTC)
        user_texts = [m.content for m in history if m.role is Role.USER][-3:]
        await affect_module.refresh(
            self._db,
            session_id=session_id,
            session_started_at=started,
            message_count=len(history),
            last_user_messages=user_texts,
            is_casual_turn=affect_module.is_casual(latest_user_text),
        )

    def _machine_context(
        self, info: ModelInfo | None, history: list[StoredMessage]
    ) -> ctx.MachineContext:
        """Facts already in hand — no query, no probe, nothing on the hot path.

        The session start comes from the first stored message rather than the
        `sessions` row, and the turn count from the history just loaded, so this
        costs nothing beyond what the turn already did.
        """
        started = _session_started_at(history)

        return ctx.MachineContext(
            # Local time: she is answering someone sitting at this machine, and
            # "what time is it" means their clock, not UTC.
            now=datetime.now().astimezone(),
            model_label=info.label if info else None,
            model_is_local=info.local if info else None,
            online=connectivity.online,
            session_started=started.astimezone() if started else None,
            message_count=len(history),
        )

    def _schedule_roll_up(
        self, session_id: str, to_summarize: list[ChatMessage], previous: str | None
    ) -> None:
        """Compress the oldest turns without the current turn waiting for it.

        One at a time per session: a fast typist could otherwise queue several
        summarisations of overlapping history, which would burn the model and
        produce a note built from a race.
        """
        if session_id in self._rolling_up:
            return
        self._rolling_up.add(session_id)

        async def run() -> None:
            try:
                summary = await self._summarize(to_summarize, previous)
                if summary:
                    self._summaries[session_id] = summary
            finally:
                self._rolling_up.discard(session_id)

        job = asyncio.create_task(run())
        self._jobs.add(job)
        job.add_done_callback(self._jobs.discard)

    async def _summarize(
        self, to_summarize: list[ChatMessage], previous: str | None
    ) -> str:
        """Compress the oldest turns. Folds in any earlier note so it compounds."""
        request = ctx.summarization_request(to_summarize)
        if previous:
            request.insert(
                1,
                ChatMessage(
                    role=Role.SYSTEM, content=f"Earlier summary to fold in:\n{previous}"
                ),
            )

        chunks: list[str] = []
        try:
            async for delta in self._provider.stream_chat(
                request,
                model=self._model,
                options=GenerationOptions(
                    num_ctx=self._num_ctx, max_tokens=SUMMARY_MAX_TOKENS
                ),
            ):
                chunks.append(delta.text)
                if delta.done:
                    break
        except ProviderError as exc:
            log.warning("context.summarize_failed", error=str(exc))
            # Better a stale note than a dropped conversation.
            return previous or ""

        summary = "".join(chunks).strip()

        # max_tokens is a request, not a guarantee — clamp it. An oversized
        # summary is pure loss: it evicts real turns and costs prefill forever,
        # since it sits in the volatile section and re-prefills every turn.
        if len(summary) > SUMMARY_MAX_CHARS:
            log.warning(
                "context.summary_truncated",
                got_chars=len(summary),
                cap_chars=SUMMARY_MAX_CHARS,
            )
            summary = summary[:SUMMARY_MAX_CHARS].rsplit(" ", 1)[0] + "…"

        log.info("context.rolled_up", summary_chars=len(summary))
        return summary
