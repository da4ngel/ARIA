"""JSON-RPC method registry and dispatch (BUILD_SPEC §7.1).

Phase 0 registers only ``system.health``. Every other method in §7.1 arrives with
the phase that implements it; until then an unknown method returns -32601 rather
than a stub that pretends to work.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any, Literal

import structlog
from pydantic import BaseModel, ValidationError

from sidecar.rpc.protocol import ErrorCode, RpcMethodError, RpcRequest, RpcResponse, err, ok

log = structlog.get_logger(__name__)

Handler = Callable[[dict[str, Any]], Awaitable[Any]]

_METHODS: dict[str, Handler] = {}

_STARTED_AT = time.monotonic()
SIDECAR_VERSION = "0.1.0"


def method(name: str) -> Callable[[Handler], Handler]:
    """Register a coroutine as the handler for a JSON-RPC method."""

    def decorator(fn: Handler) -> Handler:
        if name in _METHODS:
            raise RuntimeError(f"JSON-RPC method {name!r} is already registered.")
        _METHODS[name] = fn
        return fn

    return decorator


def method_names() -> list[str]:
    return sorted(_METHODS)


# ── system.health ─────────────────────────────────────────────────────
# The wire shape is fixed now so the UI never has to change as probes land.
# BUILD_SPEC §9.6 lists probes (Ollama, VRAM, Everything, disk) that need
# subprocess/HTTP access; CLAUDE.md rule 4 routes those through the tool
# registry, which does not exist until Phase 3. Fields are typed and present,
# populated by the phase that owns the dependency.


class HealthReport(BaseModel):
    """Rich health snapshot for the UI (§7.1 ``system.health``, §9.6)."""

    status: Literal["ok", "degraded"] = "ok"
    version: str = SIDECAR_VERSION
    uptime_s: float = 0.0
    db: bool = False

    # Filled in by later phases; None means "not probed yet", not "broken".
    ollama: bool | None = None
    gpu_free_mb: int | None = None
    everything: bool | None = None
    models: list[str] = []

    # Phases that have not wired their probe yet, so the UI can say so honestly.
    pending_probes: list[str] = []


def uptime_seconds() -> float:
    return round(time.monotonic() - _STARTED_AT, 3)


def build_health(*, db_ready: bool) -> HealthReport:
    return HealthReport(
        status="ok" if db_ready else "degraded",
        version=SIDECAR_VERSION,
        uptime_s=uptime_seconds(),
        db=db_ready,
        pending_probes=["ollama", "gpu_free_mb", "everything", "models"],
    )


@method("system.health")
async def system_health(_params: dict[str, Any]) -> dict[str, Any]:
    """Return the health snapshot. Never raises — the UI polls this."""
    from sidecar.state import runtime  # local import avoids a startup cycle

    report = build_health(db_ready=runtime.db_ready)
    report.ollama = runtime.ollama_ready
    report.models = [runtime.local_model] if runtime.local_model else []
    report.pending_probes = [p for p in report.pending_probes if p not in ("ollama", "models")]
    return report.model_dump()


# ── chat (Phase 1) ────────────────────────────────────────────────────


@method("chat.send")
async def chat_send(params: dict[str, Any]) -> dict[str, Any]:
    """Start a turn. Returns {turn_id}; the reply streams as `token` events."""
    from sidecar.state import runtime

    text = str(params.get("text", ""))
    session_id = params.get("session_id")
    started = await runtime.require_conversation().send(
        text, session_id if isinstance(session_id, str) else None
    )
    return started.model_dump()


@method("chat.cancel")
async def chat_cancel(params: dict[str, Any]) -> dict[str, Any]:
    """Abort an in-flight turn mid-stream."""
    from sidecar.state import runtime

    turn_id = params.get("turn_id")
    if not isinstance(turn_id, str):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "turn_id is required.")
    cancelled = await runtime.require_conversation().cancel(turn_id)
    return {"ok": cancelled}


@method("chat.history")
async def chat_history(params: dict[str, Any]) -> dict[str, Any]:
    """Reload a session from SQLite.

    Not in §7.1's method table, but §9 Phase 1's gate requires the conversation
    to survive killing the window — which needs a way to read it back.
    """
    from sidecar.state import runtime

    session_id = params.get("session_id")
    limit = params.get("limit", 200)
    history = await runtime.require_conversation().history(
        session_id if isinstance(session_id, str) else None,
        int(limit) if isinstance(limit, int) else 200,
    )
    return history.model_dump(mode="json")


# ── dispatch ──────────────────────────────────────────────────────────


async def dispatch(raw: str) -> RpcResponse | None:
    """Parse and execute one client message. Returns None for notifications."""
    try:
        request = RpcRequest.model_validate_json(raw)
    except ValidationError as exc:
        log.warning("rpc.invalid_request", error=str(exc))
        return err(None, ErrorCode.INVALID_REQUEST, "Malformed JSON-RPC request.", exc.errors())

    handler = _METHODS.get(request.method)
    if handler is None:
        log.warning("rpc.unknown_method", method=request.method)
        return err(
            request.id,
            ErrorCode.METHOD_NOT_FOUND,
            f"Unknown method {request.method!r}. "
            f"Available in this build: {', '.join(method_names())}.",
        )

    return await _invoke(handler, request)


async def _invoke(handler: Handler, request: RpcRequest) -> RpcResponse | None:
    """Run a handler, mapping exceptions onto JSON-RPC errors."""
    started = time.perf_counter()
    try:
        result = await handler(request.params)
    except RpcMethodError as exc:
        log.warning("rpc.method_error", method=request.method, code=exc.code)
        return err(request.id, exc.code, exc.message, exc.data)
    except ValidationError as exc:
        return err(request.id, ErrorCode.INVALID_PARAMS, "Invalid params.", exc.errors())
    except Exception as exc:  # one bad call must not kill the socket
        log.exception("rpc.handler_failed", method=request.method)
        return err(
            request.id,
            ErrorCode.INTERNAL_ERROR,
            f"{request.method} failed: {exc}. See data/logs/sidecar.log for the traceback.",
        )

    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    log.debug("rpc.call", method=request.method, duration_ms=duration_ms)

    if request.id is None:
        return None
    return ok(request.id, result)
