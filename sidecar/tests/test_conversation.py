"""Turn orchestration, cancellation, persistence and context roll-up."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

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
    ToolCall,
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


class OpenEngine:
    """A permission engine that always allows, recording what it ran."""

    def __init__(self, summary: str = "9 windows open") -> None:
        self.ran: list[tuple[str, dict]] = []
        self.summary = summary

    async def run(self, name, arguments, ctx, *, rationale=""):
        from sidecar.tools.registry import ToolResult

        self.ran.append((name, arguments))
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


async def test_the_continuation_is_not_offered_tools_again(
    database: Database, make_service
) -> None:
    """Otherwise a model loops: use a tool, see the tools, use one again."""
    provider = ToolCallingProvider([ToolCall(id="c1", name="list_windows", arguments={})])
    svc, _bus = tool_service(database, make_service, provider, OpenEngine())

    await svc.send("what is open")
    await _drain(svc)

    assert provider.offered[0], "the first pass offers tools"
    assert provider.offered[1] == [], "the second must not"


async def test_extra_tool_calls_are_dropped_and_declared(
    database: Database, make_service
) -> None:
    """One tool per turn until Phase 6. Executing an unreviewed plan is worse
    than doing less than asked."""
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
