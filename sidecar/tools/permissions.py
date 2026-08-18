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
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol

import structlog

from sidecar.tools.registry import Tier, Tool, ToolContext, ToolResult, get

log = structlog.get_logger(__name__)

#: §7.1. Long enough to read a dialog and think; short enough that a forgotten
#: prompt does not pin the agent loop open for the rest of the session.
CONFIRM_TIMEOUT_S = 120.0

#: Tools above this need a *typed* confirmation, not a click.
TYPED_CONFIRM_FROM = Tier.DANGER


class PermissionMode(StrEnum):
    """A global preset over the same machinery below — it never adds a new
    way to decide, it only changes what `is_trusted`/`_ask`/`run` do with
    the decision they'd already make.

    Confirmed with Eyaas, and the one real departure from rule 5 in this
    file: FULL_ACCESS skips *everything*, escalations included — the same
    shape of deliberate, visible exception `allow_danger` already is to
    "DANGER is hidden by default." What neither mode touches: `Tool.refuse`
    and `tools/files.py`'s hard refusals. Those were never "asking"
    mechanisms to begin with — "trust decides whether she asks, never what
    is allowed," applied to mode exactly as it already applies to a
    trusted folder.
    """

    #: Every CONFIRM/DANGER call asks, every time — trusted folders and
    #: "always allow" are both ignored while this is active, without being
    #: cleared. Switching back to AUTO restores them exactly as configured.
    MANUAL = "manual"
    #: Today's behavior, unchanged. The default.
    AUTO = "auto"
    #: Nothing asks — not tier, not an escalation, not DANGER's own
    #: typed-confirmation requirement. Off by default, chosen deliberately.
    FULL_ACCESS = "full_access"


# ── trusted folders ──────────────────────────────────────────────────
# Inside one, she acts without asking — whatever the tier, deletion included.
# That is a deliberate choice and a large one, which is why nothing is trusted
# until it is added by hand.
#
# Two things trust does *not* do. It never relaxes the refusals in
# `tools/files.py`: a trusted folder cannot be C:/Windows, and adding it there
# changes nothing. And it never applies to a call that also touches somewhere
# untrusted — moving a file *out* of a trusted folder is not covered by
# trusting it, because the destination is the part that matters.

#: Argument names whose values are paths. Checked by name rather than by
#: sniffing every string, so a tool taking a `query` cannot accidentally be
#: read as touching the filesystem.
_PATH_ARGS = frozenset({"path", "source", "destination", "folder", "file", "dir", "directory"})


def paths_in(arguments: dict[str, Any]) -> list[Path]:
    """The filesystem paths a call would touch."""
    found: list[Path] = []
    for name, value in arguments.items():
        if name in _PATH_ARGS and isinstance(value, str) and value.strip():
            found.append(Path(value.strip().strip('"')).expanduser())
    return found


def within(path: Path, roots: list[Path]) -> bool:
    """Whether `path` sits inside any of `roots`. Recursive by design: trusting
    a folder means trusting what is in it, including what is nested."""
    try:
        resolved = path.resolve()
    except OSError:
        return False
    for root in roots:
        try:
            if resolved == root or resolved.is_relative_to(root):
                return True
        except (OSError, ValueError):
            continue
    return False


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
        # not a side effect of a model asking nicely. `mode` can also grant
        # this — see `run()` — but the field itself stays whatever it was
        # explicitly set to; FULL_ACCESS overlays it rather than replacing it,
        # so switching back to AUTO returns to exactly what it was before.
        self.allow_danger = allow_danger
        #: Folders she may act in without asking. Empty until added.
        self.trusted: list[Path] = []
        self._pending: dict[str, Pending] = {}
        #: Tools the user chose to stop being asked about, this session only.
        #: Deliberately not persisted: "always allow" said once in a hurry
        #: should not silently outlive the session it was said in.
        self._always: set[str] = set()
        #: The global preset. Persisted by the caller (settings_store), same
        #: shape as `trusted` — this class only holds the live value.
        self.mode: PermissionMode = PermissionMode.AUTO

    def set_mode(self, mode: PermissionMode) -> None:
        self.mode = mode
        log.info("tool.permission_mode", mode=str(mode))

    def set_trusted(self, paths: list[str]) -> None:
        """Replace the trusted set.

        Resolved once here rather than per call, and silently dropping the ones
        that cannot be resolved — a stale entry for a removed drive should not
        make every later check raise.
        """
        roots: list[Path] = []
        for raw in paths:
            try:
                roots.append(Path(raw).expanduser().resolve())
            except OSError:
                log.warning("tool.bad_trusted_path", path=raw)
        self.trusted = roots
        log.info("tool.trusted_paths", count=len(roots), paths=[str(p) for p in roots])

    def is_trusted(self, arguments: dict[str, Any]) -> bool:
        """Whether every path in this call is somewhere she is trusted.

        **Every** path: a call that reaches outside, even partly, still asks.
        A call with no paths at all is not trusted by default — trust is about
        places, and a tool that names none is not in one.

        MANUAL mode reads as untrusted regardless of what `self.trusted`
        actually holds — checked here, not by clearing `self.trusted`
        itself, so the real configuration survives a round trip through
        MANUAL unchanged.
        """
        if self.mode is PermissionMode.MANUAL:
            return False
        if not self.trusted:
            return False
        targets = paths_in(arguments)
        return bool(targets) and all(within(t, self.trusted) for t in targets)

    # ── the decision ────────────────────────────────────────────────────

    async def run(
        self,
        name: str,
        arguments: dict[str, Any],
        ctx: ToolContext,
        *,
        rationale: str = "",
        force_confirm: bool = False,
    ) -> ToolResult:
        """Gate a tool call, run it if allowed, and log it either way.

        `force_confirm` is §11's escalation, not a per-tool property: a tool
        that is normally AUTO or SAFE still asks when `core/agent.py` sets this,
        because the *reason* it needs asking this time is what the step before
        it did (read untrusted content), not what this tool is. The tool's own
        registered tier is untouched — only the effective floor for *this call*
        moves up to CONFIRM. It never lowers anything: a tool that was already
        CONFIRM or DANGER is unaffected, and it never grants DANGER access —
        `allow_danger` below still gates that separately.

        A tool can reach the same CONFIRM floor on its own, via `tool.escalate`
        — a different *reason* (this call's own arguments or live state, not
        the previous step) landing on the same mechanism. And a tool can skip
        the ask entirely via `tool.refuse`, which is checked first and can
        return a hard "no" before tier, trust, or `allow_danger` are even
        consulted.
        """
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

        # A hard block: no tier, no trust, no dialog. Checked first, and
        # before `allow_danger` too — a refusal is a refusal at any tier.
        refusal = await self._refuse(tool, arguments)
        if refusal is not None:
            await self._log(call_id, ctx, name, arguments, tool.tier, False, False, refusal, 0)
            log.warning("tool.refused", tool=name, tier=int(tool.tier), reason=refusal)
            return ToolResult(ok=False, summary=f"I will not do that: {refusal}.", error="refused")

        # `allow_danger` decides whether the tool exists at all; trust only
        # decides whether it asks. A disabled DANGER tool stays disabled inside
        # a trusted folder. FULL_ACCESS grants this the same way it grants
        # everything else below — deliberately, and visibly in Settings.
        full_access = self.mode is PermissionMode.FULL_ACCESS
        if tool.tier >= TYPED_CONFIRM_FROM and not (self.allow_danger or full_access):
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
        approved_by: str | None = None
        if full_access:
            # Skips tier, trust, and escalation together — including the
            # §11 untrusted-content rule and the checkout/banking hard
            # escalation. `_refuse` above is the one thing that still ran.
            approved, approved_by = True, "full_access"
            log.info("tool.full_access", tool=name, tier=int(tool.tier))
        else:
            # Two independent reasons a call might need to ask when its own
            # tier would not: §11's `force_confirm` (the *previous* step read
            # untrusted content) and `tool.escalate` (*this* call's own
            # arguments or live state look like a checkout/banking page).
            # Either is enough.
            escalated = force_confirm or await self._escalate(tool, arguments)
            effective_tier = Tier.CONFIRM if escalated and tool.tier < Tier.CONFIRM else tool.tier
            if effective_tier >= Tier.CONFIRM:
                if not escalated and self.is_trusted(arguments):
                    # A trusted folder is not consent to skip an escalation —
                    # it is consent to skip asking about *this tool's own*
                    # risk. The risk an escalation exists for came from
                    # somewhere else entirely and a trusted-folder exemption
                    # never heard of it.
                    approved, approved_by = True, "trust"
                    log.info("tool.trusted", tool=name, tier=int(tool.tier))
                else:
                    approved = await self._ask(
                        tool,
                        arguments,
                        rationale,
                        escalated=escalated and tool.tier < Tier.CONFIRM,
                    )
                    approved_by = "user" if approved else None
                if not approved:
                    await self._log(
                        call_id, ctx, name, arguments, tool.tier, False, False, "denied", 0
                    )
                    log.info("tool.denied", tool=name, tier=int(tool.tier))
                    return ToolResult(
                        ok=False, summary=f"You declined {name}.", error="denied"
                    )

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
            call_id,
            ctx,
            name,
            arguments,
            tool.tier,
            approved,
            result.ok,
            result.error,
            took,
            approved_by=approved_by,
        )
        log.info("tool.ran", tool=name, tier=int(tool.tier), ok=result.ok, took_ms=took)
        return result

    # ── the round-trip ──────────────────────────────────────────────────

    async def _refuse(self, tool: Tool, arguments: dict[str, Any]) -> str | None:
        """`tool.refuse`, defensively. See its docstring for why a raise here
        means "no reason found" rather than "found a reason" — the opposite
        default from `_escalate` below."""
        if tool.refuse is None:
            return None
        try:
            return await tool.refuse(**arguments)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — see `Tool.refuse`'s docstring
            log.warning("tool.refuse_check_failed", tool=tool.name, error=str(exc))
            return None

    async def _escalate(self, tool: Tool, arguments: dict[str, Any]) -> bool:
        """`tool.escalate`, defensively. Fails closed: see `Tool.escalate`'s
        docstring for why this is the one hook that escalates on its own
        failure rather than falling back quietly."""
        if tool.escalate is None:
            return False
        try:
            return await tool.escalate(**arguments)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — see `Tool.escalate`'s docstring
            log.warning("tool.escalate_check_failed", tool=tool.name, error=str(exc))
            return True

    async def _preview(self, tool: Tool, arguments: dict[str, Any]) -> dict[str, Any] | None:
        """What the user is about to approve, worked out before it happens.

        Never raises. A preview is detail on top of a confirmation, and losing
        the confirmation because the detail failed would be exactly backwards —
        the dialog still appears, showing the raw arguments as it always did.
        """
        if tool.preview is None:
            return None
        try:
            return await tool.preview(**arguments)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — detail is not worth the dialog
            log.warning("tool.preview_failed", tool=tool.name, error=str(exc))
            return None

    async def _ask(
        self, tool: Tool, arguments: dict[str, Any], rationale: str, *, escalated: bool = False
    ) -> bool:
        """Suspend until the user answers, or until the timeout denies for them."""
        if not escalated and self.mode is not PermissionMode.MANUAL and tool.name in self._always:
            # "Always allow" was said about this tool's *ordinary* risk. §11's
            # escalation is a different risk arriving from a different step,
            # and a standing yes to "open apps without asking" was never a yes
            # to "open whatever a webpage just told you to open." MANUAL
            # ignores it the same way it ignores trust — asked once in a
            # different mode is not a standing yes for "ask me about
            # everything right now."
            return True

        # Before the request, because it *is* the request: §7.2 wants one
        # confirmation describing a batch, not one per file, and a batch nobody
        # can see is not something anybody can meaningfully agree to.
        preview = await self._preview(tool, arguments)

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
                "preview": preview,
                # True only when this call would not normally have asked at
                # all — §11's escalation, not this tool's own tier. The dialog
                # needs to say *why* it appeared, or it reads as a bug.
                "escalated": escalated,
            },
        )
        log.info(
            "tool.confirm_requested", tool=tool.name, tier=int(tool.tier), escalated=escalated
        )

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
        approved_by: str | None = None,
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
                    # "user", "trust", or None when nothing was asked.
                    "approved_by": approved_by,
                }
            )
        except Exception:
            log.exception("tool.log_failed", tool=tool)
