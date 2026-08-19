"""Turn orchestration, cancellation, persistence and context roll-up."""

from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from sidecar.core import context as ctx
from sidecar.core.conversation import ConversationService, _parse_yes_no
from sidecar.core.router import Router, RoutingBias
from sidecar.memory import procedures
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
    ToolCall,
)
from sidecar.providers.health import HealthTracker
from sidecar.rpc.events import AssistantState, Event, EventBus
from sidecar.state import runtime
from sidecar.tools.permissions import PermissionMode


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
        tools: list[dict[str, Any]] | None = None,
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
async def make_service():
    """Build services that are all shut down when the test ends.

    The teardown is not optional: finishing a turn spawns a background title
    job, and without a drain those tasks outlive the test and asyncio complains
    they were destroyed while pending. Several tests build more than one
    service, so cleanup lives here rather than at each call site where an
    assertion failure would skip it.
    """
    built: list[ConversationService] = []

    def build(**kwargs: object) -> ConversationService:
        svc = ConversationService(**kwargs)  # type: ignore[arg-type]
        built.append(svc)
        return svc

    yield build
    for svc in built:
        await svc.shutdown()


@pytest.fixture
async def service(database: Database, make_service):
    provider = FakeProvider()
    bus = RecordingBus()
    svc = make_service(
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


async def test_history_survives_a_new_service_instance(
    database: Database, service, make_service
) -> None:
    """The Phase 1 gate: kill the window, conversation reloads from SQLite."""
    svc, provider, bus = service
    result = await svc.send("remember this")
    await _drain(svc)

    # A brand new service over the same database == a relaunched app.
    fresh = make_service(
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


async def test_cancel_stops_mid_stream_and_keeps_partial(database: Database, make_service) -> None:
    provider = FakeProvider(chunks=["one "] * 50, delay=0.02)
    bus = RecordingBus()
    svc = make_service(
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


async def test_send_without_a_session_id_continues_the_conversation(service) -> None:
    """A client that forgets to echo the id back must not silently lose context."""
    svc, _p, _b = service
    first = await svc.send("my name is Eyaas")
    await _drain(svc)
    second = await svc.send("what is my name")
    await _drain(svc)

    assert second.session_id == first.session_id
    history = await svc.history(None)
    assert [m.content for m in history.messages] == [
        "my name is Eyaas",
        "Hello there.",
        "what is my name",
        "Hello there.",
    ]


async def test_new_session_is_the_only_way_to_start_fresh(service) -> None:
    svc, _p, _b = service
    first = await svc.send("remember this")
    await _drain(svc)

    fresh = await svc.new_session()
    assert fresh != first.session_id

    after = await svc.send("a new topic")
    await _drain(svc)
    assert after.session_id == fresh

    # The old conversation is still in SQLite, just not the active one.
    old = await svc.history(first.session_id)
    assert [m.content for m in old.messages] == ["remember this", "Hello there."]


async def test_new_session_writes_no_row_until_a_message_is_sent(service) -> None:
    """New Chat then closing the window must leave nothing behind."""
    svc, _p, _b = service
    await svc.send("first conversation")
    await _drain(svc)

    reserved = await svc.new_session()
    assert [s.id for s in await svc.list_sessions()] != [reserved]
    assert len(await svc.list_sessions()) == 1

    await svc.send("second conversation")
    await _drain(svc)
    listed = await svc.list_sessions()
    assert listed[0].id == reserved


async def test_reserved_session_wins_over_continuing_the_latest(service) -> None:
    """The sharp edge: `send` with no id continues the most recent conversation,
    so New Chat has to take precedence or the first message lands in the old one."""
    svc, _p, _b = service
    first = await svc.send("original conversation")
    await _drain(svc)

    reserved = await svc.new_session()
    after = await svc.send("brand new topic")  # deliberately passes no session_id
    await _drain(svc)

    assert after.session_id == reserved
    assert after.session_id != first.session_id


async def test_deleting_a_conversation_removes_it_from_the_list(service) -> None:
    svc, _p, _b = service
    first = await svc.send("delete this one")
    await _drain(svc)
    await svc.new_session()
    second = await svc.send("keep this one")
    await _drain(svc)

    assert await svc.delete_session(first.session_id) == 2
    assert [s.id for s in await svc.list_sessions()] == [second.session_id]


async def test_next_turn_works_after_deleting_the_active_conversation(service) -> None:
    """Deleting what you are looking at must not wedge the assistant."""
    svc, _p, bus = service
    started = await svc.send("about to be deleted")
    await _drain(svc)
    await svc.delete_session(started.session_id)

    await svc.send("a fresh start")
    await _drain(svc)

    complete = bus.of(Event.TURN_COMPLETE)
    assert complete, "the turn after a delete must still complete"
    assert (await svc.history(None)).messages[-1].content == "Hello there."


async def test_titling_waits_for_idle_rather_than_racing_the_next_turn(service) -> None:
    """Measured: firing a title straight after a turn pushed the *next* turn to
    924ms against a 700ms gate, because both queued on the same Ollama."""
    svc, _p, _b = service
    await svc.send("what is the capital of Japan")
    await _drain(svc)
    await svc.send("and the population")
    await _drain(svc)

    # A title job is queued, and deliberately has not run yet.
    assert svc._jobs, "expected a background title job"  # noqa: SLF001
    assert await svc._store.get_title((await svc.history(None)).session_id or "") is None  # noqa: SLF001


async def test_rename_sticks(service) -> None:
    svc, _p, _b = service
    started = await svc.send("hello")
    await _drain(svc)

    await svc.rename_session(started.session_id, "Named by hand")
    assert (await svc.list_sessions())[0].title == "Named by hand"


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
    database: Database, make_service
) -> None:
    """A cloud model that dies mid-chain must never swap silently (§9.7 stage 7)."""
    dead = FakeProvider()
    dead.fail_with = ProviderRateLimited("HTTP 429 from OpenAI.")
    alive = FakeProvider(chunks=["Recovered."])

    bus = RecordingBus()
    health = HealthTracker()
    svc = make_service(
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
    database: Database, make_service
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
            tools: list[dict[str, Any]] | None = None,
        ) -> AsyncIterator[StreamDelta]:
            yield StreamDelta(text="I think the answer is")
            raise ProviderRateLimited("HTTP 429 mid-stream.")

    bus = RecordingBus()
    health = HealthTracker()
    svc = make_service(
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
    database: Database, make_service
) -> None:
    alive = FakeProvider(chunks=["Cloud answer."])
    health = HealthTracker()
    svc = make_service(
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


async def test_trivial_turn_stays_local_even_at_quality_bias(
    database: Database, make_service
) -> None:
    local = FakeProvider(chunks=["Hey."])
    cloud = FakeProvider()
    cloud.fail_with = AssertionError("a greeting must not reach a cloud provider")

    bus = RecordingBus()
    svc = make_service(
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


async def test_long_conversation_triggers_rollup(database: Database, make_service) -> None:
    """30-turn coherence gate: stays under budget, no overflow."""
    provider = FakeProvider(chunks=["z" * 3000])
    bus = RecordingBus()
    svc = make_service(
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


async def test_rollup_does_not_block_the_turn_that_triggers_it(
    database: Database, make_service
) -> None:
    """Roll-up is a second model call. Awaiting it put a whole generation in
    front of the first token, which a ~1000ms voice budget cannot absorb."""
    provider = FakeProvider(chunks=["z" * 3000])
    svc = make_service(
        store=ConversationStore(database),
        provider=provider,
        bus=RecordingBus(),
        model="test-model",
        context_token_budget=2000,
    )

    session_id: str | None = None
    for i in range(6):
        result = await svc.send(f"message {i} " + "q" * 2000, session_id)
        session_id = result.session_id
        await _drain(svc)

    # `_drain` waits only for turns, so a summary present here would mean the
    # turn had waited for it.
    assert svc._jobs or svc._summaries, "expected a roll-up to have been scheduled"  # noqa: SLF001

    await svc.shutdown()  # drains the background jobs
    assert session_id in svc._summaries, "the summary should land after the turn"  # noqa: SLF001


async def test_only_one_rollup_per_session_at_a_time(
    database: Database, make_service
) -> None:
    """A fast typist would otherwise queue several summarisations of nearly the
    same history, burning the model on a race."""
    svc = make_service(
        store=ConversationStore(database),
        provider=FakeProvider(chunks=["z" * 3000]),
        bus=RecordingBus(),
        model="test-model",
        context_token_budget=2000,
    )

    turns = [ChatMessage(role=Role.USER, content="x" * 4000)]
    svc._schedule_roll_up("s_1", turns, None)  # noqa: SLF001
    first = len(svc._jobs)  # noqa: SLF001
    svc._schedule_roll_up("s_1", turns, None)  # noqa: SLF001
    assert len(svc._jobs) == first, "a second roll-up for the same session was queued"  # noqa: SLF001


async def test_a_spoken_turn_is_answered_locally(database: Database, make_service) -> None:
    """End to end through the service: the modality reaches the router, so a
    question that would otherwise go to GPT-5 is answered on this machine."""
    local = FakeProvider(chunks=["Local."])
    cloud = FakeProvider(chunks=["Cloud."])
    bus = RecordingBus()

    svc = make_service(
        store=ConversationStore(database),
        provider=local,
        bus=bus,
        model="qwen2.5:7b",
        providers={"openai": cloud, "gemini": cloud, "ollama": local},
        router=Router(HealthTracker(), RoutingBias.QUALITY),
        usable_models=lambda: {m.id for m in catalog.CATALOG},
    )

    await svc.send("compare Postgres and SQLite for this project", spoken=True)
    await _drain(svc)

    complete = bus.of(Event.TURN_COMPLETE)
    assert complete[0]["full_text"] == "Local."
    answered = catalog.get(complete[0]["model"])
    assert answered is not None and answered.local, complete[0]["model"]


# ── tools on the turn path (Phase 3) ──────────────────────────────────


class ToolCallingProvider(FakeProvider):
    """Asks for a tool on the first pass, then answers on the second.

    The two-pass shape is the whole point: a tool call is not an answer, and
    the model has to be given the result and asked again.
    """

    def __init__(self, calls: list[ToolCall], reply: str = "Done.") -> None:
        super().__init__(chunks=[reply])
        self._calls = calls
        self.passes = 0
        self.offered: list[list[str]] = []

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        options: GenerationOptions | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[StreamDelta]:
        self.passes += 1
        self.calls.append(messages)
        self.offered.append([t["function"]["name"] for t in (tools or [])])
        if self.passes == 1:
            yield StreamDelta(text="Let me check. ")
            yield StreamDelta(tool_calls=self._calls, done=True)
            return
        for chunk in self.chunks:
            yield StreamDelta(text=chunk)
        yield StreamDelta(done=True)


class ScriptedToolProvider(FakeProvider):
    """One entry per pass: a list of `ToolCall`s to ask for, or `None` to
    answer in text with `reply`. `ToolCallingProvider` can only ever request
    *one* shape of thing (its constructor's calls, once) and always answers
    text from the second pass on — too fixed to exercise genuine multi-step
    chaining, a repeated call, or a model that never stops asking.
    """

    def __init__(
        self, script: list[list[ToolCall] | None], reply: str = "Done."
    ) -> None:
        super().__init__(chunks=[reply])
        self._script = script
        self.passes = 0
        self.offered: list[list[str]] = []

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        options: GenerationOptions | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[StreamDelta]:
        self.calls.append(messages)
        self.offered.append([t["function"]["name"] for t in (tools or [])])
        # Once the script runs out, repeat its last entry — the exhaustion
        # test relies on this to keep asking forever without growing a
        # script MAX_STEPS long.
        step = self._script[min(self.passes, len(self._script) - 1)]
        self.passes += 1
        if step is not None:
            yield StreamDelta(tool_calls=step, done=True)
            return
        for chunk in self.chunks:
            yield StreamDelta(text=chunk)
        yield StreamDelta(done=True)


class OpenEngine:
    """A permission engine that always allows, recording what it ran."""

    def __init__(self, summary: str = "9 windows open") -> None:
        self.ran: list[tuple[str, dict]] = []
        self.summary = summary
        # One entry per call, in order — whether *that* call arrived with
        # §11's escalation set, not just the most recent one.
        self.escalated: list[bool] = []
        # The real engine has this, and `_tool_schemas` reads it to decide
        # whether the model is told DANGER tools exist. A double missing a
        # field the production code depends on is a test that stops testing.
        self.allow_danger = False
        # Same reasoning, same fix, the day `_tool_schemas` learned to read
        # `mode` too (permission modes, 2026-08-14).
        self.mode = PermissionMode.AUTO
        # Tools this engine should report as having failed — a denied
        # confirmation, a refusal, an error. Set per test; empty by default.
        self.fails: frozenset[str] = frozenset()

    async def run(self, name, arguments, ctx, *, rationale="", force_confirm=False):
        from sidecar.tools.registry import ToolResult

        self.ran.append((name, arguments))
        self.escalated.append(force_confirm)
        if name in self.fails:
            return ToolResult(ok=False, summary=f"{name} did not run.", error="denied")
        return ToolResult(ok=True, summary=self.summary, display={"big": "payload"})


def tool_service(database: Database, make_service, provider, engine):
    bus = RecordingBus()
    svc = make_service(
        store=ConversationStore(database),
        provider=provider,
        bus=bus,
        model="test-model",
        permissions=engine,
    )
    return svc, bus


async def test_a_tool_call_runs_and_the_model_answers_with_it(
    database: Database, make_service
) -> None:
    provider = ToolCallingProvider([ToolCall(id="c1", name="list_windows", arguments={})])
    engine = OpenEngine()
    svc, bus = tool_service(database, make_service, provider, engine)

    await svc.send("what is open")
    await _drain(svc)

    assert engine.ran == [("list_windows", {})]
    assert provider.passes == 2, "the result has to go back to the model"
    assert bus.of(Event.TOOL_CALL) and bus.of(Event.TOOL_RESULT)
    assert bus.of(Event.TURN_COMPLETE)[0]["full_text"] == "Done."


async def test_only_the_summary_reaches_the_model(database: Database, make_service) -> None:
    """§7.2's second failure mode: never paste the payload into the context."""
    provider = ToolCallingProvider([ToolCall(id="c1", name="list_windows", arguments={})])
    engine = OpenEngine(summary="9 windows open")
    svc, _bus = tool_service(database, make_service, provider, engine)

    await svc.send("what is open")
    await _drain(svc)

    second_pass = provider.calls[-1]
    tool_turn = [m for m in second_pass if m.role is Role.TOOL]
    assert tool_turn and "9 windows open" in tool_turn[0].content
    assert all("payload" not in m.content for m in second_pass)


async def test_the_continuation_is_offered_tools_again_for_chaining(
    database: Database, make_service
) -> None:
    """Phase 6: a continuation *can* call another tool — that's the whole
    point of the agent loop. `ToolCallingProvider` only ever asks for a tool
    on its very first pass and answers in text from its second pass on, so
    this just proves the option was there: offering tools again is what makes
    a second, sequential call possible at all, even though this particular
    provider stub doesn't take it."""
    provider = ToolCallingProvider([ToolCall(id="c1", name="list_windows", arguments={})])
    svc, _bus = tool_service(database, make_service, provider, OpenEngine())

    await svc.send("what is open")
    await _drain(svc)

    assert provider.offered[0], "the first pass offers tools"
    assert provider.offered[1], "so does the continuation — chaining needs this"


async def test_extra_tool_calls_in_one_response_are_dropped_and_declared(
    database: Database, make_service
) -> None:
    """A model asking for several tools *in the same response* still only
    runs the first — executing an unreviewed plan is worse than doing less
    than asked. That's a different question from chaining across steps,
    which the agent loop now allows one call at a time."""
    provider = ToolCallingProvider(
        [
            ToolCall(id="c1", name="list_windows", arguments={}),
            ToolCall(id="c2", name="delete_file", arguments={"path": "C:/x"}),
        ]
    )
    engine = OpenEngine()
    svc, _bus = tool_service(database, make_service, provider, engine)

    await svc.send("tidy up")
    await _drain(svc)

    assert [name for name, _ in engine.ran] == ["list_windows"]
    tool_turn = next(m for m in provider.calls[-1] if m.role is Role.TOOL)
    assert "delete_file" in tool_turn.content, "the model is told what was skipped"


async def test_no_engine_means_the_model_is_never_told_tools_exist(
    database: Database, make_service
) -> None:
    provider = ToolCallingProvider([])
    bus = RecordingBus()
    svc = make_service(
        store=ConversationStore(database),
        provider=provider,
        bus=bus,
        model="test-model",
    )

    await svc.send("hello")
    await _drain(svc)

    assert provider.offered[0] == []


# ── the agent loop chains steps (Phase 6) ──────────────────────────────


async def test_a_second_step_can_call_a_different_tool(
    database: Database, make_service
) -> None:
    """The whole point of Phase 6: find, then open, then answer — three
    passes, two different tools, one turn."""
    provider = ScriptedToolProvider(
        [
            [ToolCall(id="c1", name="find", arguments={"query": "cv"})],
            [ToolCall(id="c2", name="open_file", arguments={"path": "cv.docx"})],
            None,
        ]
    )
    engine = OpenEngine()
    svc, bus = tool_service(database, make_service, provider, engine)

    await svc.send("find my cv and open it")
    await _drain(svc)

    assert [name for name, _ in engine.ran] == ["find", "open_file"]
    assert bus.of(Event.TURN_COMPLETE)[0]["full_text"] == "Done."
    calls = bus.of(Event.TOOL_CALL)
    assert [c["step"] for c in calls] == [0, 1], "each step is numbered, not repeated"


async def test_a_turn_never_ends_with_an_empty_reply(
    database: Database, make_service
) -> None:
    """The observed half of `gate_agent.py`'s open line: the model runs a
    tool, then finishes its next pass with no text at all. `_finish` would
    store and broadcast an empty `full_text`, which from the outside is
    indistinguishable from a hung app.

    The tool's own summary stands in — framed as a report of what ran, not
    dressed up as something she said.
    """
    provider = ScriptedToolProvider(
        [[ToolCall(id="c1", name="find", arguments={"query": "cv"})], None],
        reply="",
    )
    engine = OpenEngine(summary="Found 1: cv.pdf (by name).")
    svc, bus = tool_service(database, make_service, provider, engine)

    await svc.send("find my cv")
    await _drain(svc)

    full_text = bus.of(Event.TURN_COMPLETE)[0]["full_text"]
    assert full_text.strip(), "a turn that says nothing is the one outcome never allowed"
    assert "find" in full_text, "it names the tool that did run"
    assert "cv.pdf" in full_text, "and carries what that tool actually found"


async def test_an_empty_reply_with_no_tool_still_says_something(
    database: Database, make_service
) -> None:
    """No tool ran either, so there is nothing to report but the silence —
    a provider returning an empty completion (GPT-5 spending its whole
    `max_tokens` on reasoning is the recorded case)."""
    provider = ScriptedToolProvider([None], reply="")
    engine = OpenEngine()
    svc, bus = tool_service(database, make_service, provider, engine)

    await svc.send("hello")
    await _drain(svc)

    full_text = bus.of(Event.TURN_COMPLETE)[0]["full_text"]
    assert full_text.strip()
    assert "empty" in full_text.lower()


async def test_a_real_reply_is_never_replaced_by_the_fallback(
    database: Database, make_service
) -> None:
    """The guard fires on silence only. A model that answered — however
    briefly — keeps its own words."""
    provider = ScriptedToolProvider(
        [[ToolCall(id="c1", name="find", arguments={"query": "cv"})], None],
        reply="It's in Downloads.",
    )
    engine = OpenEngine()
    svc, bus = tool_service(database, make_service, provider, engine)

    await svc.send("find my cv")
    await _drain(svc)

    assert bus.of(Event.TURN_COMPLETE)[0]["full_text"] == "It's in Downloads."


async def test_the_same_call_twice_aborts_as_loop_detection(
    database: Database, make_service
) -> None:
    """Asking for the exact same tool with the exact same arguments twice in
    one turn means stuck, not progress — stop rather than repeat it."""
    provider = ScriptedToolProvider(
        [
            [ToolCall(id="c1", name="list_windows", arguments={})],
            [ToolCall(id="c2", name="list_windows", arguments={})],
        ]
    )
    engine = OpenEngine()
    svc, bus = tool_service(database, make_service, provider, engine)

    await svc.send("what is open")
    await _drain(svc)

    assert [name for name, _ in engine.ran] == ["list_windows"], "the repeat never ran"
    full_text = bus.of(Event.TURN_COMPLETE)[0]["full_text"]
    assert "list_windows" in full_text, "the model is told why it stopped"


async def test_a_tool_that_never_stops_asking_hits_the_step_budget(
    database: Database, make_service
) -> None:
    """A model that just keeps asking for something new must still end the
    turn — a bounded loop, not an unbounded one."""
    from sidecar.core.agent import MAX_STEPS

    # `MAX_STEPS` tool-requesting passes, then one more with no tools
    # offered — a real model, offered nothing, answers in text; the trailing
    # `None` is what that looks like here.
    script: list[list[ToolCall] | None] = [
        [ToolCall(id=f"c{i}", name="open_app", arguments={"name": f"app{i}"})]
        for i in range(MAX_STEPS)
    ]
    script.append(None)
    provider = ScriptedToolProvider(script)
    engine = OpenEngine()
    svc, bus = tool_service(database, make_service, provider, engine)

    await svc.send("open a lot of things")
    await _drain(svc)

    assert len(engine.ran) == MAX_STEPS, "exactly the budget, not more"
    complete = bus.of(Event.TURN_COMPLETE)[0]
    assert complete["note"] and str(MAX_STEPS) in complete["note"]
    assert complete["full_text"] == "Done.", "the final pass still gets to answer in text"


async def test_the_step_after_an_untrusted_source_tool_is_escalated(
    database: Database, make_service
) -> None:
    """§11: a call right after reading something from outside the machine is
    forced through confirmation, regardless of that tool's own tier —
    `open_app` is SAFE and would otherwise run silently."""
    provider = ScriptedToolProvider(
        [
            [ToolCall(id="c1", name="research", arguments={"query": "x"})],
            [ToolCall(id="c2", name="open_app", arguments={"name": "notepad"})],
            None,
        ]
    )
    engine = OpenEngine()
    svc, _bus = tool_service(database, make_service, provider, engine)

    await svc.send("look that up and open notepad")
    await _drain(svc)

    assert [name for name, _ in engine.ran] == ["research", "open_app"]
    assert engine.escalated == [False, True], "only the step after research is escalated"


async def test_a_denied_untrusted_read_does_not_escalate_the_next_step(
    database: Database, make_service
) -> None:
    """§11 escalates the step after *reading* untrusted content. A `research`
    that was denied at its own dialog, or that errored, read nothing — so
    there is no untrusted content in the context for the next step to be
    protected from, and asking about it is pure friction.

    Observed live, and it compounds: one `research` whose confirmation timed
    out (120s, resolving to DENIED) made the *next* `research` escalate too,
    which also timed out, and the turn spent four minutes asking about pages
    nobody ever fetched.
    """
    provider = ScriptedToolProvider(
        [
            [ToolCall(id="c1", name="research", arguments={"query": "x"})],
            [ToolCall(id="c2", name="open_app", arguments={"name": "notepad"})],
            None,
        ]
    )
    engine = OpenEngine()
    engine.fails = frozenset({"research"})
    svc, _bus = tool_service(database, make_service, provider, engine)

    await svc.send("look that up and open notepad")
    await _drain(svc)

    assert [name for name, _ in engine.ran] == ["research", "open_app"]
    assert engine.escalated == [False, False], "nothing was read, so nothing to escalate for"


async def test_one_web_read_after_another_does_not_escalate(
    database: Database, make_service
) -> None:
    """Decided with Eyaas (2026-08-18): §11 guards against untrusted content
    reaching a tool that *does* something. A second `research` does nothing
    to this machine and is already gated by the online-mode switch.

    Measured before this: one "what is the latest Python" turn raised three
    confirmation dialogs for a read-only T1 tool, which is exactly the
    friction that trains a person to approve without reading.
    """
    provider = ScriptedToolProvider(
        [
            [ToolCall(id="c1", name="research", arguments={"query": "python"})],
            [ToolCall(id="c2", name="research", arguments={"query": "python 3.14"})],
            None,
        ]
    )
    engine = OpenEngine()
    svc, _bus = tool_service(database, make_service, provider, engine)

    await svc.send("what is the latest python")
    await _drain(svc)

    assert [name for name, _ in engine.ran] == ["research", "research"]
    assert engine.escalated == [False, False], "a second read is not the action §11 guards"


async def test_a_tool_that_acts_after_a_web_read_still_escalates(
    database: Database, make_service
) -> None:
    """The half that did not move, asserted beside the half that did — the
    narrowing is about *reads*, and nothing else."""
    provider = ScriptedToolProvider(
        [
            [ToolCall(id="c1", name="research", arguments={"query": "x"})],
            [ToolCall(id="c2", name="write_file", arguments={"path": "notes.txt"})],
            None,
        ]
    )
    engine = OpenEngine()
    svc, _bus = tool_service(database, make_service, provider, engine)

    await svc.send("look that up and write it down")
    await _drain(svc)

    assert engine.escalated == [False, True]


# ── a local_only tool moves the continuation off the cloud ────────────
# `_PRIVATE` in the router decides from the user's words, *before* the tool
# runs. This is the guarantee that does not depend on guessing the phrasing:
# whatever model asked for the clipboard, the model that is handed its
# contents is the local one.


def test_a_local_only_tool_forces_the_continuation_local() -> None:
    from sidecar.providers import catalog

    service = ConversationService.__new__(ConversationService)
    service._model = catalog.PREFERRED_LOCAL  # noqa: SLF001

    cloud = catalog.require("gpt-5.4-nano")
    assert not cloud.local

    chosen = service._continuation_model("read_clipboard", cloud)  # noqa: SLF001
    assert chosen.local, "the clipboard's contents would have gone to a cloud model"
    assert chosen.id == catalog.PREFERRED_LOCAL


def test_an_ordinary_tool_leaves_the_model_alone() -> None:
    """The control. Forcing every continuation local would throw away the
    cloud model mid-turn for `open_app`, which has nothing to protect."""
    from sidecar.providers import catalog

    service = ConversationService.__new__(ConversationService)
    service._model = catalog.PREFERRED_LOCAL  # noqa: SLF001

    cloud = catalog.require("gpt-5.4-nano")
    assert service._continuation_model("open_app", cloud) is cloud  # noqa: SLF001


# ── proactivity (Phase 8) ───────────────────────────────────────────


def _proactivity_service(
    database: Database, make_service, **kwargs: object
) -> tuple[ConversationService, RecordingBus]:
    bus = RecordingBus()
    svc = make_service(
        store=ConversationStore(database),
        provider=FakeProvider(),
        bus=bus,
        model="test-model",
        **kwargs,
    )
    return svc, bus


async def test_send_proactive_persists_as_a_flagged_message(
    database: Database, make_service
) -> None:
    svc, _bus = _proactivity_service(database, make_service)
    await svc.send("hello")
    await _drain(svc)

    message_id = await svc.send_proactive(
        "Still working on Sillara pricing?", trigger="idle_intent"
    )

    assert message_id is not None
    history = await svc.history(None)
    proactive_rows = [m for m in history.messages if m.proactive]
    assert len(proactive_rows) == 1
    assert proactive_rows[0].content == "Still working on Sillara pricing?"
    assert proactive_rows[0].role == Role.ASSISTANT


async def test_send_proactive_broadcasts_the_event(database: Database, make_service) -> None:
    svc, bus = _proactivity_service(database, make_service)
    await svc.send("hello")
    await _drain(svc)

    await svc.send_proactive("Ready when you are.", urgency="low", trigger="scheduled")

    events = bus.of(Event.PROACTIVE)
    assert len(events) == 1
    assert events[0]["text"] == "Ready when you are."
    assert events[0]["urgency"] == "low"


async def test_send_proactive_creates_a_session_if_none_exists(
    database: Database, make_service
) -> None:
    """A proactive message needs somewhere to live even before the user has
    ever said anything — the trigger can fire on a machine that was just
    started."""
    svc, _bus = _proactivity_service(database, make_service)

    message_id = await svc.send_proactive("Good morning.")

    assert message_id is not None
    history = await svc.history(None)
    assert len(history.messages) == 1
    assert history.messages[0].proactive


async def test_send_proactive_is_rateable_through_the_existing_mechanism(
    database: Database, make_service
) -> None:
    """The whole point of writing a `routing_log` row for it: the *existing*
    `turn.rate` thumbs mechanism must work on a proactive message with no
    new code path."""
    from sidecar.memory.routing_log import RoutingLog

    provider = FakeProvider()
    bus = RecordingBus()
    routing_log = RoutingLog(database)
    svc = make_service(
        store=ConversationStore(database),
        provider=provider,
        bus=bus,
        model="test-model",
        routing_log=routing_log,
    )

    message_id = await svc.send_proactive("Checking in.", trigger="scheduled")
    assert message_id is not None
    for _ in range(20):
        row = await database.run(
            lambda c: c.execute(
                "SELECT stage FROM routing_log WHERE message_id = ?", (message_id,)
            ).fetchone()
        )
        if row is not None:
            break
        await asyncio.sleep(0.01)
    assert row is not None and row["stage"] == "proactive"

    await routing_log.rate(message_id, 1)
    assert await routing_log.rating_for(message_id) == 1


# ── procedure offer replies (Phase 8 Part 2) ─────────────────────────
# "Offer once, wait for a yes" needs something to recognise the yes.
# `_resolve_procedure_reply` is the other half of `send_proactive`'s
# `procedure_name` — these prove a plain yes/no resolves it without ever
# reaching the model.


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("yes", True),
        ("Yes.", True),
        ("yeah", True),
        ("sure!", True),
        ("go ahead", True),
        ("sounds good", True),
        ("no", False),
        ("no thanks", False),
        ("nah", False),
        ("skip it", False),
        ("not now", False),
        ("what's the weather like", None),
        ("yes please remember that I also like tea", None),
        ("", None),
    ],
)
def test_parse_yes_no(text: str, expected: bool | None) -> None:
    assert _parse_yes_no(text) is expected


def _seed_procedure(conn: sqlite3.Connection, name: str) -> None:
    conn.execute(
        "INSERT INTO procedures (name, trigger_phrase, steps, confirmed, created_at) "
        "VALUES (?, ?, '[{\"tool\": \"find\"}]', 0, datetime('now'))",
        (name, "organise downloads"),
    )


async def test_a_yes_reply_confirms_the_pending_offer_without_a_model_call(
    database: Database, make_service
) -> None:
    provider = FakeProvider()
    bus = RecordingBus()
    svc = make_service(
        store=ConversationStore(database),
        provider=provider,
        bus=bus,
        model="test-model",
        db=database,
    )
    await database.run(lambda c: _seed_procedure(c, "find -> read_file"))

    await svc.send_proactive("Want me to remember that?", procedure_name="find -> read_file")
    started = await svc.send("yes")

    assert provider.calls == []  # never reached the model
    offers = await procedures.pending_offers(database)
    assert offers == []  # no longer pending — it is confirmed now
    row = await database.run(
        lambda c: c.execute(
            "SELECT confirmed FROM procedures WHERE name = ?", ("find -> read_file",)
        ).fetchone()
    )
    assert row["confirmed"] == 1

    history = await svc.history(started.session_id)
    assert history.messages[-2].content == "yes"
    assert history.messages[-1].content == "Got it — I'll remember that."
    assert bus.of(Event.TURN_COMPLETE)[-1]["turn_id"] == started.turn_id


async def test_a_no_reply_discards_the_pending_offer(database: Database, make_service) -> None:
    svc, _bus = _proactivity_service(database, make_service, db=database)
    await database.run(lambda c: _seed_procedure(c, "find -> read_file"))

    await svc.send_proactive("Want me to remember that?", procedure_name="find -> read_file")
    await svc.send("no")

    row = await database.run(
        lambda c: c.execute(
            "SELECT * FROM procedures WHERE name = ?", ("find -> read_file",)
        ).fetchone()
    )
    assert row is None  # discarded, not just left unconfirmed


async def test_an_unrelated_reply_falls_through_to_a_normal_turn(
    database: Database, make_service
) -> None:
    """A pending offer must never swallow an unrelated message as if it were
    a decline — the model still answers it normally."""
    provider = FakeProvider(chunks=["Paris."])
    bus = RecordingBus()
    svc = make_service(
        store=ConversationStore(database),
        provider=provider,
        bus=bus,
        model="test-model",
        db=database,
    )
    await database.run(lambda c: _seed_procedure(c, "find -> read_file"))

    await svc.send_proactive("Want me to remember that?", procedure_name="find -> read_file")
    await svc.send("what is the capital of France?")
    await _drain(svc)

    assert len(provider.calls) == 1  # the normal turn reached the model
    offers = await procedures.pending_offers(database)
    assert len(offers) == 1  # still pending — an unrelated message is not a decline


async def test_the_pending_offer_window_is_one_shot(database: Database, make_service) -> None:
    """Only the very next `send()` after the offer can resolve it — a second
    "yes" sent later is an ordinary message, not a second chance to confirm."""
    provider = FakeProvider(chunks=["Sure."])
    bus = RecordingBus()
    svc = make_service(
        store=ConversationStore(database),
        provider=provider,
        bus=bus,
        model="test-model",
        db=database,
    )
    await database.run(lambda c: _seed_procedure(c, "find -> read_file"))

    await svc.send_proactive("Want me to remember that?", procedure_name="find -> read_file")
    await svc.send("what is the capital of France?")  # unrelated -> falls through
    await _drain(svc)
    await svc.send("yes")  # too late; the window already closed
    await _drain(svc)

    assert len(provider.calls) == 2  # both turns reached the model
    row = await database.run(
        lambda c: c.execute(
            "SELECT confirmed FROM procedures WHERE name = ?", ("find -> read_file",)
        ).fetchone()
    )
    assert row["confirmed"] == 0  # never got the chance to be confirmed


# ── memory (Phase 5) ──────────────────────────────────────────────────


@pytest.mark.anyio
async def test_deleting_a_conversation_clears_its_episodes_first(
    database: Database, make_service
) -> None:
    """`episodes.session_id` is a foreign key, so the store's delete raises
    unless the episodes go first.

    Asserted here rather than only against `ConversationStore`, because the
    ordering lives in `ConversationService` — a test that calls the store
    directly still passes with the fix removed.
    """
    from sidecar.memory.episodic import EpisodicMemory
    from sidecar.memory.retrieval import MemoryServices, Retriever
    from sidecar.memory.semantic import SemanticMemory

    store = ConversationStore(database)
    session = await store.ensure_session("s_mem")
    for i in range(2):
        await store.add_message(session, Role.USER, f"question {i}")
        await store.add_message(session, Role.ASSISTANT, f"answer {i}")

    class EpisodeProvider:
        async def stream_chat(
            self, messages: object, **kwargs: object
        ) -> AsyncIterator[StreamDelta]:
            yield StreamDelta(text='{"summary": "A chat.", "salience": 0.5}', done=True)

    semantic = SemanticMemory(database, None)
    episodic = EpisodicMemory(database, None, store, EpisodeProvider(), "test-model")  # type: ignore[arg-type]
    memory = MemoryServices(
        semantic=semantic,
        episodic=episodic,
        retriever=Retriever(semantic, episodic, None),
        store=store,
    )
    assert await episodic.close_session(session) is not None

    svc = make_service(
        store=store,
        provider=FakeProvider(),
        bus=RecordingBus(),
        model="test-model",
        memory=memory,
    )

    assert await svc.delete_session(session) > 0
    assert await episodic.list_episodes() == []


@pytest.mark.anyio
async def test_a_turn_without_memory_behaves_exactly_as_before(service) -> None:
    """Every memory call site is a no-op when `memory` is None — Phase 4's
    behaviour, so the whole feature can be switched off."""
    svc, provider, bus = service
    provider.chunks = ["Can", "berra."]

    started = await svc.send("what is the capital of Australia?")
    await asyncio.gather(*svc._tasks.values())  # noqa: SLF001

    assert bus.texts() == "Canberra."
    assert started.session_id


# ── attachments no longer block the send, and never fail silently ─────


async def test_send_returns_before_the_files_are_read(
    database: Database, make_service, tmp_path: Path
) -> None:
    """The divergent-state bug: reading is sequential and every image is a
    cloud round trip, so several of them took longer than the renderer's 30s
    RPC timeout. The UI reported a failed send while the sidecar carried on.

    The excerpt still has to reach the first pass — but that point is
    `_build_context`, not the return of `TurnStarted`, and the gap between
    them is the whole fix.
    """
    import sidecar.core.attachments as attach_module

    target = tmp_path / "slow.txt"
    target.write_text("the contents", encoding="utf-8")
    released = asyncio.Event()

    async def _slow(path: Path, describe: object = None) -> attach_module.Attachment:
        await released.wait()
        return attach_module.Attachment(
            path=path, kind="document", excerpt="x", summary="read", ok=True
        )

    svc, _bus = tool_service(database, make_service, FakeProvider(chunks=["hi"]), OpenEngine())
    with patch.object(attach_module, "read_one", _slow):
        started = await svc.send("what is this", attachments=[str(target)])
        assert started.turn_id, "send returned while the read was still blocked"
        released.set()
        await _drain(svc)


async def test_every_attachment_is_reported_to_the_renderer(
    database: Database, make_service, tmp_path: Path
) -> None:
    """The actual bug. An unreadable file was recorded in a log line and
    nowhere a person would look, so a skipped `.ppt` lecture surfaced only as
    a vague answer."""
    good = tmp_path / "notes.txt"
    good.write_text("readable", encoding="utf-8")
    bad = tmp_path / "lecture.ppt"
    bad.write_bytes(b"\xd0\xcf\x11\xe0")

    svc, bus = tool_service(database, make_service, FakeProvider(chunks=["hi"]), OpenEngine())
    await svc.send("summarise these", attachments=[str(good), str(bad)])
    await _drain(svc)

    events = bus.of(Event.ATTACHMENT_READ)
    assert [e["name"] for e in events] == ["notes.txt", "lecture.ppt"]
    failed = next(e for e in events if not e["ok"])
    assert ".pptx" in failed["summary"], "the message names the fix, not just the failure"


async def test_a_readable_attachment_still_reaches_the_first_pass(
    database: Database, make_service, tmp_path: Path
) -> None:
    """The guarantee the non-blocking move must not break."""
    target = tmp_path / "lease.txt"
    target.write_text("The rent is 1250 a month.", encoding="utf-8")
    provider = FakeProvider(chunks=["ok"])

    svc, _bus = tool_service(database, make_service, provider, OpenEngine())
    await svc.send("what is the rent", attachments=[str(target)])
    await _drain(svc)

    sent = "\n".join(m.content for m in provider.calls[0])
    assert "1250 a month" in sent
    assert "<untrusted_content>" in sent, "a document is still somebody else's writing"


# ── conversation modes ────────────────────────────────────────────────


async def test_chat_mode_reads_without_setting_anything(
    database: Database, make_service, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sidecar.rpc.handlers import chat_mode

    svc = make_service(
        store=ConversationStore(database),
        provider=FakeProvider(),
        bus=RecordingBus(),
        model="test-model",
    )
    session = await svc.new_session()
    await svc.send("hello", session)
    monkeypatch.setattr(runtime, "conversation", svc, raising=False)
    result = await chat_mode({"session_id": session})

    assert result["mode"] == "normal"
    assert result["label"] == "Normal"
    assert result["effective_bias"] is None


async def test_chat_mode_sets_and_echoes(
    database: Database, make_service, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sidecar.rpc.handlers import chat_mode

    svc = make_service(
        store=ConversationStore(database),
        provider=FakeProvider(),
        bus=RecordingBus(),
        model="test-model",
    )
    session = await svc.new_session()
    await svc.send("hello", session)
    monkeypatch.setattr(runtime, "conversation", svc, raising=False)
    result = await chat_mode({"session_id": session, "mode": "research"})

    assert result["mode"] == "research"
    # Research reaches for a better model — but only through the bias, and
    # only after the privacy and explicit-choice stages have had their say.
    assert result["effective_bias"] == "quality"
    assert result["online_required"] is True


async def test_chat_mode_rejects_an_unknown_mode(
    database: Database, make_service, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sidecar.rpc.handlers import chat_mode
    from sidecar.rpc.protocol import RpcMethodError

    svc = make_service(
        store=ConversationStore(database),
        provider=FakeProvider(),
        bus=RecordingBus(),
        model="test-model",
    )
    session = await svc.new_session()
    await svc.send("hello", session)
    monkeypatch.setattr(runtime, "conversation", svc, raising=False)
    with pytest.raises(RpcMethodError) as raised:
        await chat_mode({"session_id": session, "mode": "socratic"})

    # Naming the allowed values beats "invalid" — the same courtesy
    # `models.bias` already extends.
    assert "study" in str(raised.value)


async def test_a_mode_belongs_to_its_own_conversation(
    database: Database, make_service, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The whole reason this is per-conversation rather than a setting: a
    mode chosen last week must not shape today's answers."""
    from sidecar.rpc.handlers import chat_mode

    svc = make_service(
        store=ConversationStore(database),
        provider=FakeProvider(),
        bus=RecordingBus(),
        model="test-model",
    )
    first = await svc.new_session()
    await svc.send("hello", first)
    monkeypatch.setattr(runtime, "conversation", svc, raising=False)
    await chat_mode({"session_id": first, "mode": "study"})

    second = await svc.new_session()
    await svc.send("hello again", second)
    fresh = await chat_mode({"session_id": second})

    assert fresh["mode"] == "normal", "a new chat starts back at Normal"


async def test_only_one_question_is_asked_per_turn(
    database: Database, make_service
) -> None:
    """**A different question is blocked, not just a repeat.**

    `would_repeat` already covers the identical re-ask. The failure this
    guards is the other one — four separate questions in a row, which is an
    interrogation rather than a conversation, and §9's warning about
    over-triggering applies word for word. The tool takes four questions in a
    single call precisely so this cap costs nothing.
    """
    provider = ScriptedToolProvider(
        [
            [ToolCall(id="c1", name="ask_user", arguments={"questions": [{"question": "A?"}]})],
            [ToolCall(id="c2", name="ask_user", arguments={"questions": [{"question": "B?"}]})],
            None,
        ]
    )
    engine = OpenEngine()
    svc, bus = tool_service(database, make_service, provider, engine)

    await svc.send("help me decide")
    await _drain(svc)

    assert [name for name, _ in engine.ran] == ["ask_user"], "it asked twice in one turn"
    # **And the note never becomes the reply.** Ending the turn with it put
    # "You have already asked him a question this turn" on screen as her whole
    # answer — seen live on the first run of `gate_ask.py`. It goes back to the
    # model as a tool result so she can actually answer with what she has.
    full_text = bus.of(Event.TURN_COMPLETE)[0]["full_text"]
    assert "already asked" not in full_text.lower(), "an internal note reached the user"
    assert full_text.strip(), "a turn that says nothing is the one outcome never allowed"


async def test_a_second_ask_does_not_block_an_ordinary_tool(
    database: Database, make_service
) -> None:
    """The cap is on questions, not on the turn. Blocking everything after one
    would make asking a decision she pays for by giving up her tools."""
    provider = ScriptedToolProvider(
        [
            [ToolCall(id="c1", name="ask_user", arguments={"questions": [{"question": "A?"}]})],
            [ToolCall(id="c2", name="find", arguments={"query": "cv"})],
            None,
        ]
    )
    engine = OpenEngine()
    svc, bus = tool_service(database, make_service, provider, engine)

    await svc.send("ask me then find it")
    await _drain(svc)

    assert [name for name, _ in engine.ran] == ["ask_user", "find"]
