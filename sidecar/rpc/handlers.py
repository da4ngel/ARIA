"""JSON-RPC method registry and dispatch (BUILD_SPEC §7.1).

Phase 0 registers only ``system.health``. Every other method in §7.1 arrives with
the phase that implements it; until then an unknown method returns -32601 rather
than a stub that pretends to work.
"""

from __future__ import annotations

import contextlib
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
    # Everything Ollama has pulled, not just the default — the picker greys out
    # local models by exactly this list.
    report.models = list(runtime.local_models)
    report.pending_probes = [p for p in report.pending_probes if p not in ("ollama", "models")]
    return report.model_dump()


# ── chat (Phase 1) ────────────────────────────────────────────────────


@method("chat.send")
async def chat_send(params: dict[str, Any]) -> dict[str, Any]:
    """Start a turn. Returns {turn_id}; the reply streams as `token` events."""
    from sidecar.state import runtime

    text = str(params.get("text", ""))
    session_id = params.get("session_id")
    model = params.get("model")
    started = await runtime.require_conversation().send(
        text,
        session_id if isinstance(session_id, str) else None,
        model if isinstance(model, str) else None,
        spoken=params.get("spoken") is True,
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


@method("chat.new")
async def chat_new(_params: dict[str, Any]) -> dict[str, Any]:
    """Start a fresh conversation. The previous one stays in SQLite."""
    from sidecar.state import runtime

    session_id = await runtime.require_conversation().new_session()
    return {"session_id": session_id}


# ── models (Phase 1.5) ────────────────────────────────────────────────


@method("models.list")
async def models_list(_params: dict[str, Any]) -> dict[str, Any]:
    """Catalog plus live availability. Drives the picker and its tooltips.

    Re-probes Ollama first: the user may have finished an `ollama pull` since
    startup, and opening the picker is exactly when they would look for it.
    """
    from sidecar.providers import catalog
    from sidecar.providers.base import ProviderError
    from sidecar.providers.ollama import OllamaProvider
    from sidecar.state import runtime

    availability = runtime.require_availability()
    conversation = runtime.require_conversation()

    if isinstance(runtime.provider, OllamaProvider):
        with contextlib.suppress(ProviderError):
            models = await runtime.provider.list_models()
            runtime.local_models = models
            availability.set_local_models(models)

    listing = catalog.ModelListing(
        selected=conversation.selected_model,
        bias=str(conversation.routing_bias),
        models=availability.entries(),
    )
    return listing.model_dump(mode="json")


@method("models.select")
async def models_select(params: dict[str, Any]) -> dict[str, Any]:
    """Persist the model choice: a catalog id, or "smart"."""
    from sidecar.memory.settings_store import SELECTED_MODEL
    from sidecar.providers import catalog
    from sidecar.state import runtime

    model_id = params.get("model")
    if not isinstance(model_id, str):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "model is required.")
    if model_id != catalog.SMART_ID and catalog.get(model_id) is None:
        raise RpcMethodError(
            ErrorCode.INVALID_PARAMS,
            f"Unknown model {model_id!r}. Call models.list for the available ids.",
        )

    runtime.require_conversation().set_selected_model(model_id)
    if runtime.settings is not None:
        await runtime.settings.set(SELECTED_MODEL, model_id)
    return {"ok": True, "selected": model_id}


@method("models.bias")
async def models_bias(params: dict[str, Any]) -> dict[str, Any]:
    """Read or set what Smart mode optimises for.

    Phase 2 flips this to "fastest" for voice: §10 budgets ~1000ms end-to-end
    and the cheapest cloud model costs 1236ms on the network hop alone.
    """
    from sidecar.core.router import RoutingBias
    from sidecar.memory.settings_store import ROUTING_BIAS
    from sidecar.state import runtime

    conversation = runtime.require_conversation()
    requested = params.get("bias")

    if requested is not None:
        try:
            bias = RoutingBias(str(requested))
        except ValueError:
            allowed = ", ".join(str(b) for b in RoutingBias)
            raise RpcMethodError(
                ErrorCode.INVALID_PARAMS, f"Unknown bias {requested!r}. Use one of: {allowed}."
            ) from None
        conversation.set_routing_bias(bias)
        if runtime.settings is not None:
            await runtime.settings.set(ROUTING_BIAS, str(bias))

    return {"bias": str(conversation.routing_bias)}


# ── settings: API keys (Phase 1.5) ────────────────────────────────────
# Presence and the last four characters only. A key value never leaves the
# sidecar once stored — not in a response, not in a log (§11).


@method("settings.keys")
async def settings_keys(_params: dict[str, Any]) -> dict[str, Any]:
    """Which providers are configured. Contains no secrets."""
    from sidecar.providers.credentials import all_status

    return {"keys": [s.model_dump(mode="json") for s in all_status()]}


@method("settings.set_key")
async def settings_set_key(params: dict[str, Any]) -> dict[str, Any]:
    """Store, replace, or clear one API key. Pass value=null to clear."""
    from sidecar.providers.credentials import CredentialKey, delete_key, set_key, status
    from sidecar.state import runtime

    raw_key = params.get("key")
    try:
        key = CredentialKey(str(raw_key))
    except ValueError:
        allowed = ", ".join(str(k) for k in CredentialKey)
        raise RpcMethodError(
            ErrorCode.INVALID_PARAMS, f"Unknown key {raw_key!r}. Use one of: {allowed}."
        ) from None

    value = params.get("value")
    if value is None:
        delete_key(key)
    elif isinstance(value, str) and value.strip():
        set_key(key, value.strip())
    else:
        raise RpcMethodError(
            ErrorCode.INVALID_PARAMS,
            "value must be a non-empty string to store a key, or null to clear it.",
        )

    # The router caches key presence; a new key must take effect on the next
    # turn, not the next restart.
    if runtime.availability is not None:
        runtime.availability.refresh_keys()
    return {"ok": True, "status": status(key).model_dump(mode="json")}


@method("voice.transcribe")
async def voice_transcribe(params: dict[str, Any]) -> dict[str, Any]:
    """Turn a held-button recording into text.

    Takes base64 int16 PCM from the renderer's microphone capture. Returns the
    transcript and how long it took, so the per-stage latency the Phase 2 gate
    asks for is visible rather than buried in one end-to-end number.
    """
    import base64
    import time

    from sidecar.providers.stt import TranscriptionUnavailable
    from sidecar.state import runtime

    stt = runtime.stt
    if stt is None or not stt.ready:
        raise RpcMethodError(
            ErrorCode.INTERNAL_ERROR,
            "Speech recognition is not ready yet. It loads in the background on "
            "startup; try again in a moment, or type instead.",
        )

    encoded = params.get("pcm")
    if not isinstance(encoded, str) or not encoded:
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "pcm (base64 int16) is required.")
    sample_rate = params.get("sample_rate", 16_000)

    started = time.perf_counter()
    try:
        text = await stt.transcribe(
            base64.b64decode(encoded),
            int(sample_rate) if isinstance(sample_rate, int) else 16_000,
        )
    except TranscriptionUnavailable as exc:
        raise RpcMethodError(ErrorCode.INTERNAL_ERROR, str(exc)) from exc

    return {"text": text, "took_ms": round((time.perf_counter() - started) * 1000, 1)}


# ── hands-free (Phase 2 stage 3) ──────────────────────────────────────


@method("voice.listen")
async def voice_listen(params: dict[str, Any]) -> dict[str, Any]:
    """Read or set whether the sidecar accepts a continuous audio stream.

    Turning this on does not open the microphone — the renderer owns the device
    and opens it when this returns true. The two are kept separate so the
    sidecar can refuse before Windows raises an indicator.

    Returns the phrase to say, so the UI never hardcodes one: which phrase is
    live depends on the wake mode, and a label naming the wrong one is worse
    than no label.
    """
    from sidecar.memory.settings_store import WAKE_WORD_ENABLED
    from sidecar.state import runtime

    listener = runtime.listener
    requested = params.get("enabled")

    if requested is not None:
        if listener is None:
            raise RpcMethodError(
                ErrorCode.INTERNAL_ERROR,
                "Hands-free listening is not available in this session — voice "
                "is off, or speech recognition failed to load. Check the log for "
                "stt.unavailable. Hold Ctrl+Shift+Space in the meantime.",
            )
        if requested is True:
            await listener.enable()
        else:
            await listener.disable()
        if runtime.settings is not None:
            await runtime.settings.set(WAKE_WORD_ENABLED, "true" if requested else "false")

    return {
        "available": listener is not None,
        "enabled": listener is not None and listener.enabled,
        # What to actually say, so the UI never has to guess and can never
        # print a phrase the sidecar is not listening for.
        "phrase": listener.wake_phrase if listener is not None else None,
    }


@method("voice.frame")
async def voice_frame(params: dict[str, Any]) -> None:
    """One 80ms frame of base64 int16 PCM from the open microphone.

    Sent as a *notification* — twelve a second with a reply each would be
    twelve round-trips a second to say "yes, received". Returns None so
    `dispatch` sends nothing back.

    Errors are logged, never raised: a bad frame must not tear down the socket
    carrying the conversation.
    """
    import base64

    from sidecar.state import runtime

    listener = runtime.listener
    if listener is None or not listener.enabled:
        return None

    encoded = params.get("pcm")
    if not isinstance(encoded, str) or not encoded:
        return None

    try:
        from sidecar.providers.stt import pcm16_to_float32, resample_to_16k

        samples = pcm16_to_float32(base64.b64decode(encoded))
        rate = params.get("sample_rate", 16_000)
        await listener.feed(
            resample_to_16k(samples, int(rate) if isinstance(rate, int) else 16_000)
        )
    except Exception as exc:  # noqa: BLE001 — one bad frame must not stop listening
        log.warning("voice.frame_failed", error=str(exc))
    return None


@method("chat.sessions")
async def chat_sessions(params: dict[str, Any]) -> dict[str, Any]:
    """Past conversations for the history panel, most recently active first.

    `query` searches message content, not just titles — you look for a
    conversation by something you remember saying in it.
    """
    from sidecar.state import runtime

    query = params.get("query")
    limit = params.get("limit", 100)
    sessions = await runtime.require_conversation().list_sessions(
        int(limit) if isinstance(limit, int) else 100,
        query if isinstance(query, str) else None,
    )
    return {"sessions": [s.model_dump(mode="json") for s in sessions]}


@method("chat.rename")
async def chat_rename(params: dict[str, Any]) -> dict[str, Any]:
    """Set a conversation's title by hand, overriding the generated one."""
    from sidecar.state import runtime

    session_id = params.get("session_id")
    title = params.get("title")
    if not isinstance(session_id, str) or not isinstance(title, str) or not title.strip():
        raise RpcMethodError(
            ErrorCode.INVALID_PARAMS, "session_id and a non-empty title are required."
        )

    await runtime.require_conversation().rename_session(session_id, title)
    return {"ok": True, "session_id": session_id, "title": title.strip()}


@method("chat.delete")
async def chat_delete(params: dict[str, Any]) -> dict[str, Any]:
    """Delete a conversation. Requires an explicit confirmation round-trip.

    CLAUDE.md rule 5: every destructive operation confirms first. The tool
    registry that normally enforces that arrives in Phase 3, so this method
    enforces it itself — called without `confirm`, it deletes nothing and
    reports what would go, which is what the UI shows in its confirm step.
    """
    from sidecar.state import runtime

    session_id = params.get("session_id")
    if not isinstance(session_id, str):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "session_id is required.")

    conversation = runtime.require_conversation()

    if params.get("confirm") is not True:
        matches = [s for s in await conversation.list_sessions() if s.id == session_id]
        if not matches:
            raise RpcMethodError(
                ErrorCode.INVALID_PARAMS,
                f"No conversation {session_id!r}. Call chat.sessions for the current list.",
            )
        found = matches[0]
        return {
            "ok": False,
            "confirm_required": True,
            "session_id": session_id,
            "title": found.title or found.preview,
            "message_count": found.message_count,
        }

    removed = await conversation.delete_session(session_id)
    return {"ok": True, "session_id": session_id, "messages_deleted": removed}


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
