"""Turn orchestration, cancellation, persistence and context roll-up."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest

from sidecar.core import context as ctx
from sidecar.core.conversation import ConversationService
from sidecar.core.router import Router, RoutingBias
from sidecar.memory.db import Database
from sidecar.memory.messages import ConversationStore
from sidecar.providers import catalog
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    ProviderRateLimited,
    ProviderUnavailable,
    Role,
    StreamDelta,
)
from sidecar.providers.health import HealthTracker
from sidecar.rpc.events import AssistantState, Event, EventBus


class FakeProvider:
    """Scriptable stand-in for Ollama."""

    def __init__(self, chunks: list[str] | None = None, delay: float = 0.0) -> None:
        self.chunks = chunks if chunks is not None else ["Hello", " there", "."]
        self.delay = delay
        self.calls: list[list[ChatMessage]] = []
        self.fail_with: Exception | None = None

    @property
    def name(self) -> str:
        return "fake"

    async def available(self) -> bool:
        return True

    async def warm(self, model: str) -> float:
        return 1.0

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        options: GenerationOptions | None = None,
    ) -> AsyncIterator[StreamDelta]:
        self.calls.append(messages)
        if self.fail_with:
            raise self.fail_with
        for chunk in self.chunks:
            if self.delay:
                await asyncio.sleep(self.delay)
            yield StreamDelta(text=chunk)
        yield StreamDelta(done=True)

    async def aclose(self) -> None:
        return None


class RecordingBus(EventBus):
    """EventBus that keeps what it broadcast, without any sockets."""

    def __init__(self) -> None:
        super().__init__()
        self.events: list[tuple[str, dict]] = []

    async def broadcast(self, method, params) -> None:
        self.events.append((str(method), params))

    def texts(self) -> str:
        return "".join(p["text"] for m, p in self.events if m == Event.TOKEN)

    def of(self, method: Event) -> list[dict]:
        return [p for m, p in self.events if m == str(method)]


@pytest.fixture
def service(database: Database) -> tuple[ConversationService, FakeProvider, RecordingBus]:
    provider = FakeProvider()
    bus = RecordingBus()
    svc = ConversationService(
        store=ConversationStore(database),
        provider=provider,
        bus=bus,
        model="test-model",
        context_token_budget=6000,
    )
    return svc, provider, bus


async def _drain(svc: ConversationService) -> None:
    """Wait for all in-flight turns."""
    for _ in range(200):
        if not svc._tasks:  # noqa: SLF001
            return
        await asyncio.sleep(0.01)
    raise AssertionError("turn did not finish")


# ── happy path ────────────────────────────────────────────────────────


async def test_send_streams_tokens_and_persists(service) -> None:
    svc, _provider, bus = service
    result = await svc.send("hi there")
    assert result.turn_id.startswith("t_")
    await _drain(svc)

    assert bus.texts() == "Hello there."
    complete = bus.of(Event.TURN_COMPLETE)
    assert len(complete) == 1
    assert complete[0]["full_text"] == "Hello there."
    assert complete[0]["route"] == "local"

    history = await svc.history(result.session_id)
    roles = [m.role for m in history.messages]
    assert roles == ["user", "assistant"]
    assert history.messages[1].content == "Hello there."


async def test_history_survives_a_new_service_instance(database: Database, service) -> None:
    """The Phase 1 gate: kill the window, conversation reloads from SQLite."""
    svc, provider, bus = service
    result = await svc.send("remember this")
    await _drain(svc)

    # A brand new service over the same database == a relaunched app.
    fresh = ConversationService(
        store=ConversationStore(database),
        provider=FakeProvider(),
        bus=RecordingBus(),
        model="test-model",
    )
    reloaded = await fresh.history(None)  # None -> latest session
    assert reloaded.session_id == result.session_id
    assert [m.content for m in reloaded.messages] == ["remember this", "Hello there."]


async def test_state_transitions_thinking_then_idle(service) -> None:
    svc, _p, bus = service
    await svc.send("hi")
    await _drain(svc)
    states = [p["state"] for m, p in bus.events if m == Event.STATE_CHANGE]
    assert states[0] == AssistantState.THINKING
    assert states[-1] == AssistantState.IDLE


# ── cancellation ──────────────────────────────────────────────────────


async def test_cancel_stops_mid_stream_and_keeps_partial(database: Database) -> None:
    provider = FakeProvider(chunks=["one "] * 50, delay=0.02)
    bus = RecordingBus()
    svc = ConversationService(
        store=ConversationStore(database),
        provider=provider,
        bus=bus,
        model="test-model",
    )
    result = await svc.send("count")
    await asyncio.sleep(0.08)  # let a few chunks through

    assert await svc.cancel(result.turn_id) is True
    await asyncio.sleep(0.1)

    emitted = bus.texts()
    assert 0 < len(emitted) < 50 * 4, "should have stopped early"
    complete = bus.of(Event.TURN_COMPLETE)
    assert complete and complete[0]["cancelled"] is True

    # The partial reply is still conversation and must be persisted.
    history = await svc.history(result.session_id)
    assert history.messages[-1].content == emitted


async def test_cancel_unknown_turn_returns_false(service) -> None:
    svc, _p, _b = service
    assert await svc.cancel("t_nope") is False


# ── failure handling ──────────────────────────────────────────────────


async def test_provider_failure_surfaces_error_not_crash(service) -> None:
    svc, provider, bus = service
    provider.fail_with = ProviderUnavailable("Ollama is not running. Start it with 'ollama serve'.")
    await svc.send("hi")
    await _drain(svc)

    # The router now walks a fallback chain, so the first error is the failover
    # notice and the underlying cause arrives once every candidate is exhausted.
    errors = bus.of(Event.ERROR)
    assert errors, "expected at least one error event"
    assert any("ollama serve" in e["message"] for e in errors), errors
    assert any(e["code"] == "provider_failover" for e in errors), errors
    # Still returns to idle — a failed turn must not wedge the orb.
    states = [p["state"] for m, p in bus.events if m == Event.STATE_CHANGE]
    assert states[-1] == AssistantState.IDLE


async def test_failover_answers_from_the_next_model_and_names_both(
    database: Database,
) -> None:
    """A cloud model that dies mid-chain must never swap silently (§9.7 stage 7)."""
    dead = FakeProvider()
    dead.fail_with = ProviderRateLimited("HTTP 429 from OpenAI.")
    alive = FakeProvider(chunks=["Recovered."])

    bus = RecordingBus()
    health = HealthTracker()
    svc = ConversationService(
        store=ConversationStore(database),
        provider=alive,
        bus=bus,
        model="qwen2.5:7b",
        providers={"openai": dead, "gemini": alive, "ollama": alive},
        router=Router(health, RoutingBias.QUALITY),
        health=health,
        usable_models=lambda: {"gpt-5", "gemini-3.1-pro-preview", "qwen2.5:7b"},
    )

    await svc.send("debug this traceback for me")
    await _drain(svc)

    complete = bus.of(Event.TURN_COMPLETE)
    assert complete, "the turn must still complete"
    assert complete[0]["full_text"] == "Recovered."
    # The turn is attributed to whatever actually answered, not what was chosen.
    assert complete[0]["model"] == "gemini-3.1-pro-preview"
    assert "GPT-5" in (complete[0]["note"] or ""), complete[0]["note"]

    # The 429 trips the breaker so the next turn skips that model entirely.
    assert not health.is_usable("gpt-5")

    errors = bus.of(Event.ERROR)
    assert any(e["code"] == "provider_failover" for e in errors), errors


async def test_failover_after_partial_output_tells_the_ui_to_discard_it(
    database: Database,
) -> None:
    """Otherwise the replacement reply appends to half a sentence from a model
    that never finished."""

    class DiesMidStream(FakeProvider):
        async def stream_chat(
            self,
            messages: list[ChatMessage],
            *,
            model: str,
            options: GenerationOptions | None = None,
        ) -> AsyncIterator[StreamDelta]:
            yield StreamDelta(text="I think the answer is")
            raise ProviderRateLimited("HTTP 429 mid-stream.")

    bus = RecordingBus()
    health = HealthTracker()
    svc = ConversationService(
        store=ConversationStore(database),
        provider=FakeProvider(chunks=["Recovered."]),
        bus=bus,
        model="qwen2.5:7b",
        providers={
            "openai": DiesMidStream(),
            "gemini": FakeProvider(chunks=["Recovered."]),
            "ollama": FakeProvider(chunks=["Recovered."]),
        },
        router=Router(health, RoutingBias.QUALITY),
        health=health,
        usable_models=lambda: {"gpt-5", "gemini-3.1-pro-preview", "qwen2.5:7b"},
    )

    await svc.send("debug this traceback for me")
    await _drain(svc)

    assert bus.of(Event.TURN_RESET), "the UI was never told to drop the partial"
    complete = bus.of(Event.TURN_COMPLETE)
    assert complete[0]["full_text"] == "Recovered."
    # And the abandoned fragment must not reach SQLite either.
    history = await svc.history(None)
    assert history.messages[-1].content == "Recovered."


async def test_failover_records_the_serving_model_route_in_sqlite(
    database: Database,
) -> None:
    alive = FakeProvider(chunks=["Cloud answer."])
    health = HealthTracker()
    svc = ConversationService(
        store=ConversationStore(database),
        provider=alive,
        bus=RecordingBus(),
        model="qwen2.5:7b",
        providers={"openai": alive, "ollama": alive},
        router=Router(health, RoutingBias.QUALITY),
        health=health,
        usable_models=lambda: {"gpt-5", "qwen2.5:7b"},
    )

    result = await svc.send("debug this traceback for me")
    await _drain(svc)

    history = await svc.history(result.session_id)
    assert history.messages[-1].route == "cloud"


async def test_trivial_turn_stays_local_even_at_quality_bias(database: Database) -> None:
    local = FakeProvider(chunks=["Hey."])
    cloud = FakeProvider()
    cloud.fail_with = AssertionError("a greeting must not reach a cloud provider")

    bus = RecordingBus()
    svc = ConversationService(
        store=ConversationStore(database),
        provider=local,
        bus=bus,
        model="qwen2.5:7b",
        providers={"ollama": local, "openai": cloud, "gemini": cloud},
        router=Router(HealthTracker(), RoutingBias.QUALITY),
        usable_models=lambda: {m.id for m in catalog.CATALOG},
    )

    await svc.send("hey")
    await _drain(svc)

    complete = bus.of(Event.TURN_COMPLETE)
    assert complete[0]["route"] == "local"
    assert complete[0]["model"] == catalog.PREFERRED_LOCAL


async def test_empty_message_rejected(service) -> None:
    svc, _p, _b = service
    with pytest.raises(ValueError, match="empty"):
        await svc.send("   ")


# ── context assembly ──────────────────────────────────────────────────


def test_stable_prefix_is_byte_identical_across_calls() -> None:
    """The KV cache only holds if this never varies (§8.2)."""
    assert [m.content for m in ctx.stable_prefix()] == [m.content for m in ctx.stable_prefix()]


def test_assemble_puts_stable_content_first() -> None:
    turns = [ChatMessage(role=Role.USER, content="hi")]
    built = ctx.assemble(turns, summary="we talked about pricing")
    assert built[0].content == ctx.IDENTITY
    assert "pricing" in built[1].content
    assert built[-1].content == "hi"


def test_no_rollup_under_budget() -> None:
    turns = [ChatMessage(role=Role.USER, content="short")] * 4
    to_summarize, kept = ctx.split_for_rollup(turns, budget_tokens=6000)
    assert to_summarize == []
    assert kept == turns


def test_rollup_splits_oldest_half_without_orphaning_a_reply() -> None:
    turns: list[ChatMessage] = []
    for _ in range(10):
        turns.append(ChatMessage(role=Role.USER, content="x" * 4000))
        turns.append(ChatMessage(role=Role.ASSISTANT, content="y" * 4000))

    to_summarize, kept = ctx.split_for_rollup(turns, budget_tokens=6000)
    assert to_summarize, "should have triggered"
    assert len(to_summarize) + len(kept) == len(turns)
    # The kept block must begin with a user turn.
    assert kept[0].role == Role.USER


async def test_long_conversation_triggers_rollup(database: Database) -> None:
    """30-turn coherence gate: stays under budget, no overflow."""
    provider = FakeProvider(chunks=["z" * 3000])
    bus = RecordingBus()
    svc = ConversationService(
        store=ConversationStore(database),
        provider=provider,
        bus=bus,
        model="test-model",
        context_token_budget=2000,
    )

    session_id: str | None = None
    for i in range(12):
        result = await svc.send(f"message {i} " + "q" * 2000, session_id)
        session_id = result.session_id
        await _drain(svc)

    # Every prompt sent to the provider must stay inside the window.
    for messages in provider.calls:
        total = sum(ctx.estimate_tokens(m.content) for m in messages)
        assert total < 8192, f"context overflowed: {total} tokens"
