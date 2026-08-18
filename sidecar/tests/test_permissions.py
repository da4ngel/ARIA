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
from sidecar.tools.permissions import PermissionEngine, PermissionMode
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

    async def _batch_preview(path: str) -> dict[str, Any]:
        return {"kind": "move_plan", "folder": path, "count": 2}

    @tool(
        name="batch",
        tier=Tier.CONFIRM,
        description="Moves several things at once.",
        preview=_batch_preview,
    )
    async def batch(ctx: ToolContext, path: str) -> ToolResult:
        ran.append("batch")
        return ToolResult(ok=True, summary="batched")

    async def _broken_preview(path: str) -> dict[str, Any]:
        raise RuntimeError("could not read the folder")

    @tool(
        name="batch_broken",
        tier=Tier.CONFIRM,
        description="Its preview fails.",
        preview=_broken_preview,
    )
    async def batch_broken(ctx: ToolContext, path: str) -> ToolResult:
        ran.append("batch_broken")
        return ToolResult(ok=True, summary="batched anyway")

    # ── browser.py's two hooks (§9:943), tested at the engine level so a
    # tool built around them only has to prove its own detector logic ──

    async def _escalate_checkout(page: str = "ordinary") -> bool:
        return page == "checkout"

    @tool(
        name="visit",
        tier=Tier.SAFE,
        description="Would otherwise never ask.",
        escalate=_escalate_checkout,
    )
    async def visit(ctx: ToolContext, page: str = "ordinary") -> ToolResult:
        ran.append("visit")
        return ToolResult(ok=True, summary=f"visited {page}")

    async def _escalate_broken(page: str = "ordinary") -> bool:
        raise RuntimeError("could not read the page")

    @tool(
        name="visit_broken",
        tier=Tier.SAFE,
        description="Its escalate check fails.",
        escalate=_escalate_broken,
    )
    async def visit_broken(ctx: ToolContext, page: str = "ordinary") -> ToolResult:
        ran.append("visit_broken")
        return ToolResult(ok=True, summary=f"visited {page}")

    async def _refuse_password(field: str = "name") -> str | None:
        return "that looks like a password field" if field == "password" else None

    @tool(
        name="fill",
        tier=Tier.CONFIRM,
        description="Refuses a password field outright.",
        refuse=_refuse_password,
    )
    async def fill(ctx: ToolContext, field: str = "name") -> ToolResult:
        ran.append("fill")
        return ToolResult(ok=True, summary=f"filled {field}")

    async def _refuse_broken(field: str = "name") -> str | None:
        raise RuntimeError("could not read the form")

    @tool(
        name="fill_broken",
        tier=Tier.CONFIRM,
        description="Its refuse check fails.",
        refuse=_refuse_broken,
    )
    async def fill_broken(ctx: ToolContext, field: str = "name") -> ToolResult:
        ran.append("fill_broken")
        return ToolResult(ok=True, summary=f"filled {field}")

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


# ── permission modes (2026-08-14) ──────────────────────────────────────
# A global preset over the same machinery above, not a new way to decide.
# MANUAL and AUTO change nothing about *what* runs, only whether trust and
# "always allow" get consulted; FULL_ACCESS changes what asks, never what
# `_refuse` forbids outright.


async def test_the_default_mode_is_auto(tmp_path: Path) -> None:
    """The engine you get with no mode set behaves exactly as it always
    has — every other test in this file already proves that; this just
    names the default explicitly."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)
    assert engine_.mode is PermissionMode.AUTO


async def test_manual_asks_even_inside_a_trusted_folder(tmp_path: Path) -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = trusting(bus, journal, [str(tmp_path)], timeout_s=0.05)
    engine_.set_mode(PermissionMode.MANUAL)

    result = await engine_.run("overwrite", {"path": str(tmp_path / "notes.txt")}, CTX)

    assert not result.ok, "unanswered, therefore denied — MANUAL still waits for a real answer"
    assert bus.confirms(), "trusted or not, MANUAL asks"


async def test_manual_asks_even_when_the_tool_was_always_allowed(tmp_path: Path) -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, timeout_s=0.05)
    # "Always allow" said once, in AUTO.
    engine_._always.add("overwrite")  # noqa: SLF001 — simplest way to arm it directly

    engine_.set_mode(PermissionMode.MANUAL)
    result = await engine_.run("overwrite", {"path": str(tmp_path / "a.txt")}, CTX)

    assert not result.ok
    assert bus.confirms(), "a standing yes from another mode is not a yes right now"


async def test_manual_does_not_erase_trust_or_always_allow(tmp_path: Path) -> None:
    """Switching to MANUAL and back must not have silently cleared what was
    configured — it only had to stop being *consulted* for a while."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = trusting(bus, journal, [str(tmp_path)], timeout_s=0.05)
    engine_._always.add("nudge")  # noqa: SLF001

    engine_.set_mode(PermissionMode.MANUAL)
    await engine_.run("overwrite", {"path": str(tmp_path / "a.txt")}, CTX)  # asks, times out

    engine_.set_mode(PermissionMode.AUTO)
    assert engine_.trusted == [tmp_path.resolve()]
    assert "nudge" in engine_._always  # noqa: SLF001

    bus.events.clear()
    result = await engine_.run("overwrite", {"path": str(tmp_path / "b.txt")}, CTX)
    assert result.ok
    assert not bus.confirms(), "trust is back, exactly as it was configured"


async def test_full_access_runs_a_confirm_tool_with_no_dialog_at_all(tmp_path: Path) -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)  # nothing trusted, nothing always-allowed
    engine_.set_mode(PermissionMode.FULL_ACCESS)

    result = await engine_.run("overwrite", {"path": str(tmp_path / "a.txt")}, CTX)

    assert result.ok
    assert not bus.confirms()


async def test_full_access_runs_a_danger_tool_without_being_turned_on_first(
    tmp_path: Path,
) -> None:
    """`allow_danger` stays False on the engine itself — FULL_ACCESS grants
    the same ceiling `allow_danger` does without needing it flipped too,
    the same way `conversation._tool_schemas` reads `mode` alongside it."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)  # allow_danger defaults False
    engine_.set_mode(PermissionMode.FULL_ACCESS)

    result = await engine_.run("obliterate", {"path": str(tmp_path / "x")}, CTX)

    assert result.ok
    assert not bus.confirms()
    assert engine_.allow_danger is False, "the field itself is untouched, only the effect"


async def test_full_access_skips_a_tools_own_escalation(tmp_path: Path) -> None:
    """`visit`'s checkout-page escalation would normally force a SAFE tool
    to CONFIRM. Confirmed with Eyaas: FULL_ACCESS skips escalations too."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)
    engine_.set_mode(PermissionMode.FULL_ACCESS)

    result = await engine_.run("visit", {"page": "checkout"}, CTX)

    assert result.ok
    assert not bus.confirms()


async def test_full_access_skips_11s_untrusted_source_escalation(tmp_path: Path) -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)
    engine_.set_mode(PermissionMode.FULL_ACCESS)

    result = await engine_.run("nudge", {}, CTX, force_confirm=True)

    assert result.ok
    assert not bus.confirms()


async def test_full_access_still_hits_a_hard_refusal(tmp_path: Path) -> None:
    """The one thing mode never touches: `Tool.refuse`'s password-field
    block runs before tier, trust, or mode are even consulted — "trust
    decides whether she asks, never what is allowed," applied to mode
    exactly as it already applies to a trusted folder."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)
    engine_.set_mode(PermissionMode.FULL_ACCESS)

    result = await engine_.run("fill", {"field": "password"}, CTX)

    assert not result.ok
    assert result.error == "refused"
    assert ran == []


async def test_full_access_is_recorded_as_such(tmp_path: Path) -> None:
    """Same reasoning as trust's own audit-trail test: `approved_by` must
    say *why* nothing was asked, not just that nothing was."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)
    engine_.set_mode(PermissionMode.FULL_ACCESS)

    await engine_.run("overwrite", {"path": str(tmp_path / "a.txt")}, CTX)

    entry = journal.of("overwrite")[0]
    assert entry["approved"] == 1
    assert entry["approved_by"] == "full_access"


# ── allow_danger_tools has to reach the model, not just the engine ────
# The autouse fixture above swaps the real tools for these fakes, so this
# exercises the mechanism rather than whichever tools happen to exist today.
# `obliterate` is the DANGER one; `peek` is harmless.


def test_danger_tools_are_hidden_from_the_model_by_default() -> None:
    """§7.2: "off by default" means the model is not told they exist, which is
    stronger than asking it not to use them."""
    offered = {s["function"]["name"] for s in registry.schemas()}
    assert "obliterate" not in offered
    assert "peek" in offered


def test_raising_the_ceiling_offers_them() -> None:
    offered = {s["function"]["name"] for s in registry.schemas(tier_max=Tier.DANGER)}
    assert "obliterate" in offered


def test_the_service_follows_the_flag() -> None:
    """The half that was missing. `_tool_schemas` always asked for the CONFIRM
    ceiling, so the engine would execute a DANGER tool after a typed
    confirmation that nothing could ever trigger — asked to delete a real file
    with `allow_danger_tools` on, she answered "I cannot delete files with my
    current tools", which was true of what she had been given."""
    from sidecar.core.conversation import ConversationService

    service = ConversationService.__new__(ConversationService)

    class _Engine:
        allow_danger = False
        mode = PermissionMode.AUTO

    service._permissions = _Engine()  # type: ignore[assignment]  # noqa: SLF001
    names = {s["function"]["name"] for s in service._tool_schemas() or []}  # noqa: SLF001
    assert "obliterate" not in names

    _Engine.allow_danger = True
    names = {s["function"]["name"] for s in service._tool_schemas() or []}  # noqa: SLF001
    assert "obliterate" in names, "the flag never reached the model"


# ── the preview channel (§7.2's batch confirmation) ───────────────────


async def test_a_confirmation_carries_what_the_tool_would_do() -> None:
    """§7.2: "if the agent wants to move 30 files, emit one confirm.request
    describing the batch, not 30. Include the full file list." `args` cannot
    do that — for organize_folder it is `{path, strategy}`."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    await engine_.run("batch", {"path": "downloads"}, CTX)

    request = bus.confirms()[0]
    assert request["preview"] == {"kind": "move_plan", "folder": "downloads", "count": 2}


async def test_a_tool_without_a_preview_sends_none() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    await engine_.run("overwrite", {"path": "notes.txt"}, CTX)

    assert bus.confirms()[0]["preview"] is None


async def test_a_broken_preview_still_asks() -> None:
    """Detail on top of a confirmation. Losing the confirmation because the
    detail failed would be exactly backwards."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    result = await engine_.run("batch_broken", {"path": "downloads"}, CTX)

    assert len(bus.confirms()) == 1, "the dialog must still appear"
    assert bus.confirms()[0]["preview"] is None
    assert not result.ok, "and the timeout must still deny it"
    assert "batch_broken" not in ran


async def test_the_preview_runs_before_the_tool_does() -> None:
    """It describes what *would* happen. A preview computed after the fact
    would be describing something that already had."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    await engine_.run("batch", {"path": "downloads"}, CTX)

    assert bus.confirms(), "asked"
    assert "batch" not in ran, "and denied by timeout, so it never ran"


# ── §11's escalation: force_confirm ─────────────────────────────────


async def test_an_auto_tool_still_runs_silently_without_escalation() -> None:
    """The control. force_confirm is opt-in per call, never a default."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    result = await engine_.run("peek", {}, CTX)

    assert result.ok
    assert bus.confirms() == []


async def test_force_confirm_escalates_an_auto_tool() -> None:
    """The whole point: a tool that never asks, asking because the step
    before it read something from outside the machine."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, timeout_s=0.05)

    result = await engine_.run("peek", {}, CTX, force_confirm=True)

    assert bus.confirms(), "it must have asked"
    assert bus.confirms()[0]["escalated"] is True
    assert not result.ok, "denied by the timeout, since nobody answered"
    assert result.error == "denied"


async def test_force_confirm_escalates_a_safe_tool_too() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    await engine_.run("nudge", {"amount": 1}, CTX, force_confirm=True)

    assert bus.confirms()
    assert bus.confirms()[0]["tool"] == "nudge"


async def test_force_confirm_does_not_lower_an_already_confirm_tool() -> None:
    """It only ever raises a floor. A tool already at CONFIRM or DANGER is
    unaffected — and specifically, `escalated` must read False: this dialog
    would have appeared anyway, for the tool's own reason."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    await engine_.run("overwrite", {"path": "x"}, CTX, force_confirm=True)

    assert bus.confirms()[0]["escalated"] is False


async def test_force_confirm_never_grants_a_disabled_danger_tool() -> None:
    """§11's escalation raises a floor toward CONFIRM; it must never be read
    as a way to reach DANGER while allow_danger is off."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, allow_danger=False)

    result = await engine_.run("obliterate", {"path": "x"}, CTX, force_confirm=True)

    assert not result.ok
    assert result.error == "danger_disabled"
    assert bus.confirms() == []


async def test_a_trusted_folder_does_not_exempt_the_escalation() -> None:
    """Trust is consent to skip asking about *this tool's own* risk. The risk
    force_confirm exists for came from a different step, and a folder being
    trusted never heard of it."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)
    engine_.set_trusted([str(Path.cwd())])

    await engine_.run("nudge", {"path": str(Path.cwd())}, CTX, force_confirm=True)

    assert bus.confirms(), "trust must not silently approve an escalated call"


async def test_always_allow_set_during_an_escalation_does_not_cover_the_next_one() -> None:
    """`nudge` is SAFE, so an escalated call is the *only* way it can ever
    reach a confirmation at all — this is the sole place "always allow" could
    ever get set on it. If that shortcut carried forward, one webpage's
    escalated confirmation would quietly disable every future one for the
    same tool. `_ask` never consults `_always` while `escalated` is true, by
    design — asserted here rather than only in the implementation."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    first = asyncio.create_task(engine_.run("nudge", {}, CTX, force_confirm=True))
    await asyncio.sleep(0)
    engine_.respond(bus.confirms()[0]["request_id"], True, remember=True)
    await first
    bus.events.clear()

    second = asyncio.create_task(engine_.run("nudge", {}, CTX, force_confirm=True))
    await asyncio.sleep(0)
    assert bus.confirms(), "a second escalation must still ask, always-allow notwithstanding"
    engine_.respond(bus.confirms()[0]["request_id"], True)
    await second


# ── `tool.escalate` — a tool's own reason to ask (browser.py's checkout gate) ─


async def test_escalate_forces_a_silent_tool_to_ask() -> None:
    """`visit` is SAFE and would otherwise run without a dialog — its own
    `escalate` hook says this particular call looks like a checkout page."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    task = asyncio.create_task(engine_.run("visit", {"page": "checkout"}, CTX))
    await asyncio.sleep(0)

    assert bus.confirms(), "it must have asked"
    assert bus.confirms()[0]["escalated"] is True
    engine_.respond(bus.confirms()[0]["request_id"], True)
    await task


async def test_escalate_stays_quiet_when_its_own_check_says_no() -> None:
    """The control: an ordinary page must not pay the cost of a check meant
    for checkout pages."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    result = await engine_.run("visit", {"page": "ordinary"}, CTX)

    assert result.ok
    assert bus.confirms() == []
    assert "visit" in ran


async def test_escalate_fails_closed_on_its_own_exception() -> None:
    """The one hook in this file where a broken check is treated as "yes,
    ask" rather than "detail lost, proceed anyway" — a detector that cannot
    tell is not license to skip asking about a checkout page."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    task = asyncio.create_task(engine_.run("visit_broken", {"page": "ordinary"}, CTX))
    await asyncio.sleep(0)

    assert bus.confirms(), "a broken detector must escalate, not wave it through"
    engine_.respond(bus.confirms()[0]["request_id"], True)
    await task


async def test_escalate_does_not_grant_danger(tmp_path: Path) -> None:
    """`escalate` reaches the same CONFIRM floor `force_confirm` does — it
    must not be able to reach further than that on its own."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal, allow_danger=False)

    result = await engine_.run("obliterate", {"path": str(tmp_path)}, CTX)

    assert not result.ok
    assert result.error == "danger_disabled"


# ── `tool.refuse` — a hard block, no dialog at all (password fields) ────


async def test_refuse_blocks_before_any_confirmation_fires() -> None:
    """Not a dialog that can be declined — a call that never reaches one.
    Approving a fill without knowing it targets a password field is not a
    choice anyone should be asked to make."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    result = await engine_.run("fill", {"field": "password"}, CTX)

    assert not result.ok
    assert result.error == "refused"
    assert bus.confirms() == [], "no dialog — refused before one could fire"
    assert "fill" not in ran


async def test_refuse_lets_an_ordinary_call_through_to_the_usual_ask() -> None:
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    task = asyncio.create_task(engine_.run("fill", {"field": "email"}, CTX))
    await asyncio.sleep(0)

    assert bus.confirms(), "an ordinary field still asks — CONFIRM is CONFIRM"
    engine_.respond(bus.confirms()[0]["request_id"], True)
    await task
    assert "fill" in ran


async def test_refuse_fails_open_on_its_own_exception() -> None:
    """The opposite default from `escalate`, and deliberately so: this check
    reads only the call's own arguments, not live page state, so a broken
    check here is not the same risk as a broken checkout detector — falling
    back to the normal ask is consistent with `preview`'s own "detail lost,
    confirmation kept" rule."""
    bus, journal = RecordingBus(), RecordingJournal()
    engine_ = engine(bus, journal)

    task = asyncio.create_task(engine_.run("fill_broken", {"field": "email"}, CTX))
    await asyncio.sleep(0)

    assert bus.confirms(), "a broken refuse check must not silently block everything"
    engine_.respond(bus.confirms()[0]["request_id"], True)
    await task
    assert "fill_broken" in ran
