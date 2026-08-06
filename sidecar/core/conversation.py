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

import structlog
from pydantic import BaseModel

from sidecar.core import context as ctx
from sidecar.memory.messages import ConversationStore, StoredMessage
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    LLMProvider,
    ProviderError,
    Role,
)
from sidecar.rpc.events import AssistantState, Event, EventBus

log = structlog.get_logger(__name__)

SUMMARY_MAX_TOKENS = 400
SUMMARY_MAX_CHARS = SUMMARY_MAX_TOKENS * 4  # defensive clamp; see _summarize


class TurnStarted(BaseModel):
    """`chat.send` result (§7.1)."""

    turn_id: str
    session_id: str


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
    ) -> None:
        self._store = store
        self._provider = provider
        self._bus = bus
        self._model = model
        self._num_ctx = num_ctx
        self._budget = context_token_budget
        self._tasks: dict[str, asyncio.Task[None]] = {}
        # Roll-up notes are per-session and rebuilt on demand; not yet durable.
        # Phase 5 moves this into `episodes` where it belongs.
        self._summaries: dict[str, str] = {}

    # ── public API (called by rpc handlers) ─────────────────────────────

    async def send(self, text: str, session_id: str | None = None) -> TurnStarted:
        """Start a turn. Returns immediately; the reply streams as events."""
        if not text.strip():
            raise ValueError("Cannot send an empty message.")

        resolved_session = await self._store.ensure_session(session_id)
        turn_id = f"t_{uuid.uuid4().hex[:12]}"

        await self._store.add_message(resolved_session, Role.USER, text)

        task = asyncio.create_task(self._run_turn(turn_id, resolved_session, text))
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

    async def _run_turn(self, turn_id: str, session_id: str, user_text: str) -> None:
        started = time.perf_counter()
        first_token_ms: float | None = None
        collected: list[str] = []

        try:
            await self._bus.set_state(AssistantState.THINKING)
            messages = await self._build_context(session_id)

            async for delta in self._provider.stream_chat(
                messages,
                model=self._model,
                options=GenerationOptions(num_ctx=self._num_ctx),
            ):
                if delta.text:
                    if first_token_ms is None:
                        first_token_ms = (time.perf_counter() - started) * 1000
                        # The Phase 1 gate is a number, so it gets logged as one.
                        log.info(
                            "turn.first_token",
                            turn_id=turn_id,
                            first_token_ms=round(first_token_ms, 1),
                            budget_ms=700,
                            within_budget=first_token_ms < 700,
                        )
                    collected.append(delta.text)
                    await self._bus.broadcast(
                        Event.TOKEN, {"turn_id": turn_id, "text": delta.text}
                    )
                if delta.done:
                    break

            await self._finish(turn_id, session_id, collected, started, first_token_ms)

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

    async def _finish(
        self,
        turn_id: str,
        session_id: str,
        collected: list[str],
        started: float,
        first_token_ms: float | None,
    ) -> None:
        full_text = "".join(collected)
        total_ms = int((time.perf_counter() - started) * 1000)

        await self._store.add_message(
            session_id,
            Role.ASSISTANT,
            full_text,
            route="local",
            latency_ms=total_ms,
        )
        await self._bus.broadcast(
            Event.TURN_COMPLETE,
            {
                "turn_id": turn_id,
                "full_text": full_text,
                "route": "local",
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

    async def _build_context(self, session_id: str) -> list[ChatMessage]:
        history: list[StoredMessage] = await self._store.history(session_id)
        turns = ctx.to_chat_messages(history)
        summary = self._summaries.get(session_id)

        # Budget for turns is what's left after identity + any roll-up note.
        turn_budget = self._budget - ctx.overhead_tokens(summary)
        to_summarize, kept = ctx.split_for_rollup(turns, max(turn_budget, 0))
        if to_summarize:
            summary = await self._summarize(to_summarize, summary)
            self._summaries[session_id] = summary
            turns = kept

        # Hard backstop: the summarizer is a model call and can return anything.
        turns = ctx.fit_to_budget(turns, summary=summary, hard_cap_tokens=self._num_ctx)
        return ctx.assemble(turns, summary=summary)

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
