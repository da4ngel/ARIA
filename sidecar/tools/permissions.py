"""The tier engine and the confirmation round-trip (BUILD_SPEC §7.1, §7.2).

This is where CLAUDE.md rule 5 lives — *every destructive operation requires
tier T2+ and a user confirmation round-trip, no exceptions* — so the interesting
code here is the code that refuses.

The mechanism §7.1 specifies, quoted because every clause of it matters:

    the agent loop suspends on `confirm.request` and resumes only on
    `confirm.respond`. Implement this as an `asyncio.Future` keyed by
    `request_id`, with a 120s timeout that resolves to *denied*. Never default
    to approved on timeout.

**Never default to approved on timeout** is the whole safety property. A user
who walked away has not agreed to anything, and a dialog nobody answered is the
most likely way a destructive call ever reaches this code.

Two other rules are enforced here rather than trusted to callers:

- **The tier comes from the registry, never from the request.** A model that
  asks to run `delete_file` at `AUTO` is asking the wrong question.
- **Every call is logged** — approved, denied, failed or refused — because rule
  6 says so and because a denial is exactly the event worth having a record of.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol

import structlog

from sidecar.tools.registry import Tier, Tool, ToolContext, ToolResult, get

log = structlog.get_logger(__name__)

#: §7.1. Long enough to read a dialog and think; short enough that a forgotten
#: prompt does not pin the agent loop open for the rest of the session.
CONFIRM_TIMEOUT_S = 120.0

#: Tools above this need a *typed* confirmation, not a click.
TYPED_CONFIRM_FROM = Tier.DANGER


class Bus(Protocol):
    """The slice of the event bus this needs, so tests need no sockets."""

    async def broadcast(self, method: Any, params: dict[str, Any]) -> None: ...


class Journal(Protocol):
    """Where tool calls are recorded (`tool_log`, §7.3)."""

    async def write(self, entry: dict[str, Any]) -> None: ...


@dataclass
class Pending:
    """A confirmation the user has not answered yet."""

    request_id: str
    tool: str
    future: asyncio.Future[bool]
    asked_at: float = field(default_factory=time.monotonic)


class Denied(RuntimeError):
    """The call was refused — by the user, by a timeout, or by policy."""


class PermissionEngine:
    """Decides whether a tool may run, and records that it was asked."""

    def __init__(
        self,
        bus: Bus,
        journal: Journal | None = None,
        *,
        timeout_s: float = CONFIRM_TIMEOUT_S,
        allow_danger: bool = False,
    ) -> None:
        self._bus = bus
        self._journal = journal
        self._timeout_s = timeout_s
        # §7.2: DANGER is off by default. Turning it on is a deliberate act,
        # not a side effect of a model asking nicely.
        self.allow_danger = allow_danger
        self._pending: dict[str, Pending] = {}
        #: Tools the user chose to stop being asked about, this session only.
        #: Deliberately not persisted: "always allow" said once in a hurry
        #: should not silently outlive the session it was said in.
        self._always: set[str] = set()

    # ── the decision ────────────────────────────────────────────────────

    async def run(
        self,
        name: str,
        arguments: dict[str, Any],
        ctx: ToolContext,
        *,
        rationale: str = "",
    ) -> ToolResult:
        """Gate a tool call, run it if allowed, and log it either way."""
        call_id = f"tc_{uuid.uuid4().hex[:10]}"
        tool = get(name)

        if tool is None:
            # A hallucinated tool name is common and is not an error worth
            # raising — the model is told plainly and gets to try again.
            await self._log(
                call_id, ctx, name, arguments, Tier.AUTO, None, False, "unknown tool", 0
            )
            return ToolResult(
                ok=False,
                summary=f"There is no tool called {name!r}.",
                error="unknown_tool",
            )

        if tool.tier >= TYPED_CONFIRM_FROM and not self.allow_danger:
            await self._log(
                call_id, ctx, name, arguments, tool.tier, False, False, "danger disabled", 0
            )
            log.warning("tool.refused", tool=name, tier=int(tool.tier), reason="danger_disabled")
            return ToolResult(
                ok=False,
                summary=(
                    f"{name} is an irreversible action and is switched off. "
                    f"Turn it on in Settings if you want me to be able to do that."
                ),
                error="danger_disabled",
            )

        approved: bool | None = None
        if tool.tier >= Tier.CONFIRM:
            approved = await self._ask(tool, arguments, rationale)
            if not approved:
                await self._log(
                    call_id, ctx, name, arguments, tool.tier, False, False, "denied", 0
                )
                log.info("tool.denied", tool=name, tier=int(tool.tier))
                return ToolResult(ok=False, summary=f"You declined {name}.", error="denied")

        started = time.perf_counter()
        try:
            result = await tool.fn(ctx, **arguments)
        except TypeError as exc:
            # Wrong or missing arguments from the model. Recoverable: tell it
            # what it got wrong rather than tearing down the turn.
            took = int((time.perf_counter() - started) * 1000)
            await self._log(
                call_id, ctx, name, arguments, tool.tier, approved, False, str(exc), took
            )
            return ToolResult(ok=False, summary=f"{name} was called wrongly: {exc}", error="args")
        except Exception as exc:
            took = int((time.perf_counter() - started) * 1000)
            log.exception("tool.failed", tool=name)
            await self._log(
                call_id, ctx, name, arguments, tool.tier, approved, False, str(exc), took
            )
            return ToolResult(ok=False, summary=f"{name} failed: {exc}", error=str(exc))

        took = int((time.perf_counter() - started) * 1000)
        await self._log(
            call_id, ctx, name, arguments, tool.tier, approved, result.ok, result.error, took
        )
        log.info("tool.ran", tool=name, tier=int(tool.tier), ok=result.ok, took_ms=took)
        return result

    # ── the round-trip ──────────────────────────────────────────────────

    async def _ask(self, tool: Tool, arguments: dict[str, Any], rationale: str) -> bool:
        """Suspend until the user answers, or until the timeout denies for them."""
        if tool.name in self._always:
            return True

        request_id = f"cr_{uuid.uuid4().hex[:10]}"
        future: asyncio.Future[bool] = asyncio.get_running_loop().create_future()
        self._pending[request_id] = Pending(request_id, tool.name, future)

        await self._bus.broadcast(
            "confirm.request",
            {
                "request_id": request_id,
                "tool": tool.name,
                "args": arguments,
                "tier": int(tool.tier),
                "rationale": rationale,
                # A click is not enough for something that cannot be undone.
                "typed": tool.tier >= TYPED_CONFIRM_FROM,
            },
        )
        log.info("tool.confirm_requested", tool=tool.name, tier=int(tool.tier))

        try:
            return await asyncio.wait_for(future, timeout=self._timeout_s)
        except TimeoutError:
            # **Denied, not approved.** Nobody answered, so nobody agreed.
            log.warning("tool.confirm_timeout", tool=tool.name, after_s=self._timeout_s)
            return False
        except asyncio.CancelledError:
            # The turn was cancelled underneath us — also not approval.
            log.info("tool.confirm_cancelled", tool=tool.name)
            return False
        finally:
            self._pending.pop(request_id, None)

    def respond(self, request_id: str, approved: bool, remember: bool = False) -> bool:
        """Answer a pending confirmation. Returns whether one was waiting."""
        pending = self._pending.get(request_id)
        if pending is None or pending.future.done():
            return False
        if approved and remember:
            self._always.add(pending.tool)
            log.info("tool.always_allowed", tool=pending.tool)
        pending.future.set_result(approved)
        return True

    def cancel_all(self) -> int:
        """Deny everything outstanding. Used when a turn is cancelled."""
        count = 0
        for pending in list(self._pending.values()):
            if not pending.future.done():
                pending.future.set_result(False)
                count += 1
        self._pending.clear()
        return count

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    # ── the record ──────────────────────────────────────────────────────

    async def _log(
        self,
        call_id: str,
        ctx: ToolContext,
        tool: str,
        arguments: dict[str, Any],
        tier: Tier,
        approved: bool | None,
        ok: bool,
        error: str | None,
        duration_ms: int,
    ) -> None:
        """Rule 6: every call, with its args and result. Including refusals —
        a denial is the entry most worth having."""
        if self._journal is None:
            return
        try:
            await self._journal.write(
                {
                    "call_id": call_id,
                    "session_id": ctx.session_id,
                    "tool": tool,
                    "args": json.dumps(arguments, default=str)[:4000],
                    "tier": int(tier),
                    "approved": None if approved is None else int(approved),
                    "ok": int(ok),
                    "error": error,
                    "duration_ms": duration_ms,
                }
            )
        except Exception:
            log.exception("tool.log_failed", tool=tool)
