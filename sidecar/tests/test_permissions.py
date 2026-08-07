"""The tier engine, tested on what it refuses.

BUILD_SPEC §9 Phase 3 names this file specifically, and names the property it
has to pin down: *a T3 tool cannot execute without an approved confirmation,
including on confirmation timeout.*

So most of what is here asserts a negative. A permission engine that runs the
right things is unremarkable; one that runs the wrong thing once is the reason
the tier column exists.
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from typing import Any

import pytest

from sidecar.tools import registry
from sidecar.tools.permissions import PermissionEngine
from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool


class RecordingBus:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    async def broadcast(self, method: Any, params: dict[str, Any]) -> None:
        self.events.append((str(method), params))

    def confirms(self) -> list[dict[str, Any]]:
        return [p for m, p in self.events if m == "confirm.request"]


class RecordingJournal:
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    async def write(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)

    def of(self, tool: str) -> list[dict[str, Any]]:
        return [e for e in self.entries if e["tool"] == tool]


ran: list[str] = []


@pytest.fixture(autouse=True)
def _tools() -> Iterator[None]:
    """A registry with one tool per tier, put back exactly as found.

    The snapshot matters: the real tools register at import time, and a bare
    `clear()` here left every later test in the suite looking at an empty
    registry — which passed in isolation and failed in the run.
    """
    saved = registry.snapshot()
    registry.clear()
    ran.clear()

    @tool(name="peek", tier=Tier.AUTO, description="Read something harmless.")
    async def peek(ctx: ToolContext) -> ToolResult:
        ran.append("peek")
        return ToolResult(ok=True, summary="peeked")

    @tool(name="nudge", tier=Tier.SAFE, description="A reversible change.")
    async def nudge(ctx: ToolContext, amount: int = 1) -> ToolResult:
        ran.append("nudge")
        return ToolResult(ok=True, summary=f"nudged {amount}")

    @tool(name="overwrite", tier=Tier.CONFIRM, description="Change the user's data.")
    async def overwrite(ctx: ToolContext, path: str) -> ToolResult:
        ran.append("overwrite")
        return ToolResult(ok=True, summary=f"wrote {path}")

    @tool(name="obliterate", tier=Tier.DANGER, description="Irreversible.")
    async def obliterate(ctx: ToolContext, path: str) -> ToolResult:
        ran.append("obliterate")
        return ToolResult(ok=True, summary=f"gone: {path}")

    @tool(name="explode", tier=Tier.SAFE, description="Raises.")
    async def explode(ctx: ToolContext) -> ToolResult:
        raise RuntimeError("boom")

    yield
    registry.restore(saved)


def engine(bus: RecordingBus, journal: RecordingJournal, **kwargs: Any) -> PermissionEngine:
    # Short by default: no test should sit through the real 120s.
    kwargs.setdefault("timeout_s", 0.05)
    return PermissionEngine(bus, journal, **kwargs)


CTX = ToolContext(session_id="s_test", turn_id="t_test")


# ── the refusals ──────────────────────────────────────────────────────


async def test_a_danger_tool_cannot_run_without_approval() -> None:
    """The property §9 Phase 3 names."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, allow_danger=True)

    # Nobody ever answers.
    result = await engine_.run("obliterate", {"path": "C:/x"}, CTX)

    assert not result.ok
    assert "obliterate" not in ran, "it must not have run"
    assert bus.confirms(), "and it must have asked"


async def test_a_timeout_denies_rather_than_approves() -> None:
    """**Never default to approved on timeout** (§7.1).

    Somebody who walked away has not agreed to anything, and an unanswered
    dialog is the most likely way a destructive call ever reaches the engine.
    """
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, allow_danger=True, timeout_s=0.05)

    result = await engine_.run("obliterate", {"path": "C:/x"}, CTX)

    assert not result.ok
    assert result.error == "denied"
    assert ran == []


async def test_danger_is_off_by_default_and_is_not_even_offered() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)  # allow_danger defaults to False

    result = await engine_.run("obliterate", {"path": "C:/x"}, CTX)

    assert not result.ok
    assert result.error == "danger_disabled"
    assert ran == []
    assert not bus.confirms(), "it must not even ask about a disabled tool"
    # And the model is never told the tool exists.
    assert all(s["function"]["name"] != "obliterate" for s in registry.schemas())


async def test_a_denial_leaves_the_target_untouched() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, timeout_s=5)

    async def deny_it() -> None:
        await asyncio.sleep(0.02)
        request = bus.confirms()[0]
        engine_.respond(request["request_id"], approved=False)

    denier = asyncio.create_task(deny_it())
    result = await engine_.run("overwrite", {"path": "C:/notes.txt"}, CTX)
    await denier

    assert not result.ok
    assert ran == []


async def test_a_denial_is_still_written_to_the_log() -> None:
    """Rule 6, and the entry most worth having."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, allow_danger=True, timeout_s=0.05)

    await engine_.run("obliterate", {"path": "C:/x"}, CTX)

    entries = journal.of("obliterate")
    assert entries, "a refused call must still be recorded"
    assert entries[0]["approved"] == 0
    assert entries[0]["ok"] == 0
    assert entries[0]["tier"] == int(Tier.DANGER)


async def test_an_unknown_tool_is_answered_not_raised() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    result = await engine(bus, journal).run("teleport", {}, CTX)

    assert not result.ok
    assert result.error == "unknown_tool"
    assert "teleport" in result.summary


# ── the permissions ───────────────────────────────────────────────────


async def test_low_tiers_run_without_asking() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    assert (await engine_.run("peek", {}, CTX)).ok
    assert (await engine_.run("nudge", {"amount": 3}, CTX)).ok

    assert ran == ["peek", "nudge"]
    assert not bus.confirms(), "AUTO and SAFE must never interrupt"


async def test_approval_lets_it_through() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, timeout_s=5)

    async def approve() -> None:
        await asyncio.sleep(0.02)
        engine_.respond(bus.confirms()[0]["request_id"], approved=True)

    approver = asyncio.create_task(approve())
    result = await engine_.run("overwrite", {"path": "C:/notes.txt"}, CTX)
    await approver

    assert result.ok
    assert ran == ["overwrite"]
    assert journal.of("overwrite")[0]["approved"] == 1


async def test_always_allow_stops_asking_for_that_tool_only() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, allow_danger=True, timeout_s=5)

    async def approve_and_remember() -> None:
        await asyncio.sleep(0.02)
        engine_.respond(bus.confirms()[0]["request_id"], approved=True, remember=True)

    approver = asyncio.create_task(approve_and_remember())
    await engine_.run("overwrite", {"path": "a"}, CTX)
    await approver

    # Second call to the same tool: no new question.
    before = len(bus.confirms())
    assert (await engine_.run("overwrite", {"path": "b"}, CTX)).ok
    assert len(bus.confirms()) == before

    # But a different tool still asks, and a DANGER one still times out.
    result = await engine(bus, journal, allow_danger=True, timeout_s=0.05).run(
        "obliterate", {"path": "c"}, CTX
    )
    assert not result.ok


async def test_a_typed_confirmation_is_demanded_for_danger_only() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, allow_danger=True, timeout_s=0.05)

    await engine_.run("overwrite", {"path": "a"}, CTX)
    await engine_.run("obliterate", {"path": "b"}, CTX)

    asked = bus.confirms()
    assert asked[0]["tool"] == "overwrite" and asked[0]["typed"] is False
    assert asked[1]["tool"] == "obliterate" and asked[1]["typed"] is True


async def test_cancelling_a_turn_denies_everything_outstanding() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, timeout_s=5)

    call = asyncio.create_task(engine_.run("overwrite", {"path": "a"}, CTX))
    await asyncio.sleep(0.02)
    assert engine_.pending_count == 1

    assert engine_.cancel_all() == 1
    result = await call
    assert not result.ok
    assert ran == []


# ── the bookkeeping ───────────────────────────────────────────────────


async def test_a_failing_tool_is_reported_not_raised() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    result = await engine(bus, journal).run("explode", {}, CTX)

    assert not result.ok
    assert "boom" in result.summary
    assert journal.of("explode")[0]["ok"] == 0


async def test_wrong_arguments_come_back_as_an_answer() -> None:
    """Models get argument names wrong. That is a thing to say, not to crash on."""
    bus, journal = RecordingBus(), RecordingJournal()
    result = await engine(bus, journal).run("nudge", {"nonsense": 1}, CTX)

    assert not result.ok
    assert result.error == "args"


async def test_every_call_is_logged_with_its_duration() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    await engine(bus, journal).run("peek", {}, CTX)

    entry = journal.of("peek")[0]
    assert entry["session_id"] == "s_test"
    assert entry["ok"] == 1
    assert entry["approved"] is None, "nothing was asked, so nothing was approved"
    assert entry["duration_ms"] >= 0


# ── the schema ────────────────────────────────────────────────────────


def test_the_schema_comes_from_the_signature() -> None:
    schema = next(s for s in registry.schemas() if s["function"]["name"] == "nudge")
    params = schema["function"]["parameters"]

    assert params["properties"]["amount"]["type"] == "integer"
    # `amount` has a default, so it is optional; `ctx` is the executor's.
    assert params["required"] == []
    assert "ctx" not in params["properties"]


def test_a_required_argument_is_marked_required() -> None:
    schema = next(s for s in registry.schemas() if s["function"]["name"] == "overwrite")
    assert schema["function"]["parameters"]["required"] == ["path"]
