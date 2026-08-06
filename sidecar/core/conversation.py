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
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime

import structlog
from pydantic import BaseModel

from sidecar.core import context as ctx
from sidecar.core.router import RouteDecision, Router, RoutingBias
from sidecar.memory.messages import ConversationStore, SessionSummary, StoredMessage
from sidecar.providers import catalog
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    LLMProvider,
    ProviderError,
    ProviderRateLimited,
    ProviderUnavailable,
    Role,
)
from sidecar.providers.catalog import ModelInfo
from sidecar.providers.connectivity import connectivity
from sidecar.providers.health import HealthTracker
from sidecar.providers.tts import TextToSpeech, split_for_speech
from sidecar.rpc.events import AssistantState, Event, EventBus

log = structlog.get_logger(__name__)

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


class TurnStarted(BaseModel):
    """`chat.send` result (§7.1)."""

    turn_id: str
    session_id: str


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

    def __init__(self, tts: TextToSpeech | None, bus: EventBus, started: float) -> None:
        self._tts = tts
        self._bus = bus
        self._started = started
        self._buffer = ""
        self._index = 0
        self._tasks: list[asyncio.Task[None]] = []

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
        if tail:
            self._dispatch(turn_id, tail)
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
            pcm, sample_rate = await self._tts.synthesize(text)
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
        tts: TextToSpeech | None = None,
    ) -> None:
        self._store = store
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
        # None means she types and does not speak. Voice is additive: a
        # missing or broken engine must never stop a turn completing.
        self._tts = tts
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
        # Roll-up notes are per-session and rebuilt on demand; not yet durable.
        # Phase 5 moves this into `episodes` where it belongs.
        self._summaries: dict[str, str] = {}

    # ── public API (called by rpc handlers) ─────────────────────────────

    def set_selected_model(self, model_id: str) -> None:
        """Persisted choice: a catalog id, or "smart" to let the router decide."""
        self._selected = model_id

    @property
    def selected_model(self) -> str:
        return self._selected

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
    ) -> TurnStarted:
        """Start a turn. Returns immediately; the reply streams as events.

        Omitting `session_id` continues the most recent conversation rather than
        starting one. `ensure_session(None)` mints a new session every call, so
        a client that forgot to echo the id back silently lost all context one
        turn at a time. Starting fresh is `new_session`, and only that — whose
        reserved id takes precedence here, so New Chat works even if the caller
        drops the id it was handed.
        """
        if not text.strip():
            raise ValueError("Cannot send an empty message.")

        resolved_session = await self._store.ensure_session(
            session_id or self._pending_new or await self._store.latest_session_id()
        )
        self._pending_new = None
        turn_id = f"t_{uuid.uuid4().hex[:12]}"

        await self._store.add_message(resolved_session, Role.USER, text)

        task = asyncio.create_task(
            self._run_turn(
                turn_id, resolved_session, text, model or self._selected, spoken=spoken
            )
        )
        self._tasks[turn_id] = task
        self._turn_sessions[turn_id] = resolved_session
        task.add_done_callback(lambda _: self._tasks.pop(turn_id, None))
        task.add_done_callback(lambda _: self._turn_sessions.pop(turn_id, None))

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
        )
        log.info(
            "turn.routed",
            turn_id=turn_id,
            model=decision.model.id,
            stage=decision.reason.stage,
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
                messages = await self._build_context(session_id, info)
                try:
                    first_token_ms = await self._stream_one(
                        turn_id, info, messages, collected, started
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

                self._health.record_success(info.id, first_token_ms)
                await self._finish(
                    turn_id, session_id, collected, started, first_token_ms, info, decision, note
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
    ) -> float | None:
        """Stream one model's reply into `collected`. Returns TTFT in ms."""
        provider = self._registry.for_model(info)
        await self._free_vram_for(info)
        first_token_ms: float | None = None
        speech = SpeechStream(self._tts, self._bus, started)

        async for delta in provider.stream_chat(
            messages,
            model=info.id,
            options=GenerationOptions(
                num_ctx=min(self._num_ctx, info.context_tokens),
                temperature=info.temperature,
            ),
        ):
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
    ) -> None:
        full_text = "".join(collected)
        total_ms = int((time.perf_counter() - started) * 1000)
        route = "local" if info.local else "cloud"

        await self._store.add_message(
            session_id,
            Role.ASSISTANT,
            full_text,
            route=route,
            latency_ms=total_ms,
        )
        await self._bus.broadcast(
            Event.TURN_COMPLETE,
            {
                "turn_id": turn_id,
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
        self, session_id: str, info: ModelInfo | None = None
    ) -> list[ChatMessage]:
        # Persona is per-model: the full character makes weak models hostile and
        # prone to inventing context (see core/context.PersonaLevel).
        level = info.persona if info else ctx.PersonaLevel.FULL
        cap = min(self._num_ctx, info.context_tokens) if info else self._num_ctx

        history: list[StoredMessage] = await self._store.history(session_id)
        turns = ctx.to_chat_messages(history)
        summary = self._summaries.get(session_id)
        machine = self._machine_context(info, history)

        # Budget for turns is what's left after identity + any roll-up note.
        #
        # Roll-up used to happen *here*, awaited, which put a second model call
        # in front of the first token on whichever turn crossed the budget. It
        # now runs in the background: this turn drops the oldest turns to fit and
        # answers immediately, and the summary it produces lands in time for the
        # next one. Voice has a ~1000ms end-to-end budget and cannot absorb a
        # second generation.
        turn_budget = self._budget - ctx.overhead_tokens(summary, level, machine)
        to_summarize, kept = ctx.split_for_rollup(turns, max(turn_budget, 0))
        if to_summarize:
            self._schedule_roll_up(session_id, to_summarize, summary)
            turns = kept

        # Hard backstop: the summarizer is a model call and can return anything.
        turns = ctx.fit_to_budget(
            turns, summary=summary, hard_cap_tokens=cap, level=level, machine=machine
        )
        return ctx.assemble(turns, summary=summary, level=level, machine=machine)

    def _machine_context(
        self, info: ModelInfo | None, history: list[StoredMessage]
    ) -> ctx.MachineContext:
        """Facts already in hand — no query, no probe, nothing on the hot path.

        The session start comes from the first stored message rather than the
        `sessions` row, and the turn count from the history just loaded, so this
        costs nothing beyond what the turn already did.
        """
        started: datetime | None = None
        if history:
            with contextlib.suppress(ValueError):
                started = datetime.strptime(
                    history[0].created_at, "%Y-%m-%dT%H:%M:%SZ"
                ).replace(tzinfo=UTC)

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
