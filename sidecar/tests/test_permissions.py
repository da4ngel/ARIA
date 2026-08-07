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
from pathlib import Path
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


# ── trusted folders ───────────────────────────────────────────────────
# Trust is a permission bypass, so what matters is where it stops.


def trusting(bus: RecordingBus, journal: RecordingJournal, roots: list[str], **kw: Any):
    engine_ = engine(bus, journal, **kw)
    engine_.set_trusted(roots)
    return engine_


async def test_inside_a_trusted_folder_it_does_not_ask(tmp_path: Path) -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = trusting(bus, journal, [str(tmp_path)])

    result = await engine_.run("overwrite", {"path": str(tmp_path / "notes.txt")}, CTX)

    assert result.ok
    assert ran == ["overwrite"]
    assert not bus.confirms(), "a trusted folder is not asked about"


async def test_trust_is_recursive(tmp_path: Path) -> None:
    """Trusting a folder means trusting what is nested in it."""
    deep = tmp_path / "projects" / "aria" / "notes"
    deep.mkdir(parents=True)
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = trusting(bus, journal, [str(tmp_path)])

    assert (await engine_.run("overwrite", {"path": str(deep / "a.txt")}, CTX)).ok
    assert not bus.confirms()


async def test_outside_it_still_asks(tmp_path: Path) -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = trusting(bus, journal, [str(tmp_path / "trusted")], timeout_s=0.05)

    result = await engine_.run("overwrite", {"path": str(tmp_path / "elsewhere.txt")}, CTX)

    assert not result.ok, "unanswered, therefore denied"
    assert bus.confirms()


async def test_a_call_spanning_in_and_out_still_asks(tmp_path: Path) -> None:
    """Moving a file *out* of a trusted folder is not covered by trusting it —
    the destination is the part that matters."""
    inside = tmp_path / "trusted"
    inside.mkdir()
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = trusting(bus, journal, [str(inside)], timeout_s=0.05)

    registry.clear()

    @tool(name="relocate", tier=Tier.CONFIRM, description="Move a file.")
    async def relocate(ctx: ToolContext, source: str, destination: str) -> ToolResult:
        ran.append("relocate")
        return ToolResult(ok=True, summary="moved")

    result = await engine_.run(
        "relocate",
        {"source": str(inside / "a.txt"), "destination": str(tmp_path / "out.txt")},
        CTX,
    )

    assert not result.ok
    assert bus.confirms(), "one foot outside is enough to ask"


async def test_trust_does_not_resurrect_a_disabled_danger_tool(tmp_path: Path) -> None:
    """`allow_danger` decides whether the tool exists; trust only decides
    whether it asks."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = trusting(bus, journal, [str(tmp_path)])  # allow_danger defaults False

    result = await engine_.run("obliterate", {"path": str(tmp_path / "x")}, CTX)

    assert not result.ok
    assert result.error == "danger_disabled"
    assert ran == []


async def test_a_trusted_delete_runs_without_asking(tmp_path: Path) -> None:
    """The choice made: trust covers deletion too."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = trusting(bus, journal, [str(tmp_path)], allow_danger=True)

    result = await engine_.run("obliterate", {"path": str(tmp_path / "x")}, CTX)

    assert result.ok
    assert ran == ["obliterate"]
    assert not bus.confirms()


async def test_a_trusted_run_is_recorded_as_such(tmp_path: Path) -> None:
    """An audit trail that cannot tell "you approved this" from "the folder was
    trusted" is worth much less than one that can."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = trusting(bus, journal, [str(tmp_path)])

    await engine_.run("overwrite", {"path": str(tmp_path / "a.txt")}, CTX)

    entry = journal.of("overwrite")[0]
    assert entry["approved"] == 1
    assert entry["approved_by"] == "trust"


async def test_nothing_is_trusted_until_it_is_added(tmp_path: Path) -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, timeout_s=0.05)

    assert engine_.trusted == []
    result = await engine_.run("overwrite", {"path": str(tmp_path / "a.txt")}, CTX)
    assert not result.ok


async def test_a_tool_naming_no_path_is_never_trusted(tmp_path: Path) -> None:
    """Trust is about places. A tool that names none is not in one."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = trusting(bus, journal, [str(tmp_path)], timeout_s=0.05)

    registry.clear()

    @tool(name="broadcast", tier=Tier.CONFIRM, description="Send something.")
    async def broadcast(ctx: ToolContext, message: str) -> ToolResult:
        ran.append("broadcast")
        return ToolResult(ok=True, summary="sent")

    result = await engine_.run("broadcast", {"message": "hello"}, CTX)

    assert not result.ok
    assert bus.confirms()
