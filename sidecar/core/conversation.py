"""Turn orchestration (BUILD_SPEC §9 Phase 1).

One turn: persist the user message, assemble context, stream from the provider,
push `token` events as deltas arrive, persist the reply, push `turn.complete`.

Cancellation is an `asyncio.Task.cancel()` on the streaming task; the httpx
stream context closes on unwind, which aborts the HTTP request. The Phase 1 gate
requires that to land within 200ms.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import Callable

import structlog
from pydantic import BaseModel

from sidecar.core import context as ctx
from sidecar.core.router import RouteDecision, Router, RoutingBias
from sidecar.memory.messages import ConversationStore, StoredMessage
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
from sidecar.providers.health import HealthTracker
from sidecar.rpc.events import AssistantState, Event, EventBus

log = structlog.get_logger(__name__)

SUMMARY_MAX_TOKENS = 400
SUMMARY_MAX_CHARS = SUMMARY_MAX_TOKENS * 4  # defensive clamp; see _summarize


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
        # Defaults to the single provider it was constructed with, so existing
        # callers and tests keep working without a registry.
        self._registry = ProviderRegistry(
            providers=providers or {str(catalog.ProviderName.OLLAMA): provider}
        )
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
        """Start a fresh conversation. The old one stays in SQLite."""
        session_id = await self._store.ensure_session(None)
        self._summaries.pop(session_id, None)
        log.info("session.new", session_id=session_id)
        return session_id

    async def send(
        self, text: str, session_id: str | None = None, model: str | None = None
    ) -> TurnStarted:
        """Start a turn. Returns immediately; the reply streams as events.

        Omitting `session_id` continues the most recent conversation rather than
        starting one. `ensure_session(None)` mints a new session every call, so
        a client that forgot to echo the id back silently lost all context one
        turn at a time. Starting fresh is `new_session`, and only that.
        """
        if not text.strip():
            raise ValueError("Cannot send an empty message.")

        resolved_session = await self._store.ensure_session(
            session_id or await self._store.latest_session_id()
        )
        turn_id = f"t_{uuid.uuid4().hex[:12]}"

        await self._store.add_message(resolved_session, Role.USER, text)

        task = asyncio.create_task(
            self._run_turn(turn_id, resolved_session, text, model or self._selected)
        )
        self._tasks[turn_id] = task
        task.add_done_callback(lambda _: self._tasks.pop(turn_id, None))

        return TurnStarted(turn_id=turn_id, session_id=resolved_session)

    async def cancel(self, turn_id: str) -> bool:
        """Abort an in-flight turn. Returns False if it was already finished."""
        task = self._tasks.get(turn_id)
        if task is None or task.done():
            return False
        task.cancel()
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

    # ── the turn itself ─────────────────────────────────────────────────

    async def _run_turn(
        self, turn_id: str, session_id: str, user_text: str, selected: str
    ) -> None:
        started = time.perf_counter()
        collected: list[str] = []
        decision = self._router.choose(
            user_text,
            selected=selected,
            available=self._usable_models() if self._usable_models else None,
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
        first_token_ms: float | None = None

        async for delta in provider.stream_chat(
            messages,
            model=info.id,
            options=GenerationOptions(num_ctx=min(self._num_ctx, info.context_tokens)),
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
            if delta.done:
                break
        return first_token_ms

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

        # Budget for turns is what's left after identity + any roll-up note.
        turn_budget = self._budget - ctx.overhead_tokens(summary, level)
        to_summarize, kept = ctx.split_for_rollup(turns, max(turn_budget, 0))
        if to_summarize:
            summary = await self._summarize(to_summarize, summary)
            self._summaries[session_id] = summary
            turns = kept

        # Hard backstop: the summarizer is a model call and can return anything.
        turns = ctx.fit_to_budget(
            turns, summary=summary, hard_cap_tokens=cap, level=level
        )
        return ctx.assemble(turns, summary=summary, level=level)

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
