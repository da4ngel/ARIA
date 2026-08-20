"""JSON-RPC method registry and dispatch (BUILD_SPEC §7.1).

Phase 0 registers only ``system.health``. Every other method in §7.1 arrives with
the phase that implements it; until then an unknown method returns -32601 rather
than a stub that pretends to work.
"""

from __future__ import annotations

import contextlib
import os
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
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

    # Phase 4a. Carried as null since Phase 0; it is now a thing that has an
    # answer, and the UI can say plainly that search is running narrow.
    from sidecar.tools.finder import everything_path

    report.everything = everything_path() is not None
    report.pending_probes = [
        p for p in report.pending_probes if p not in ("ollama", "models", "everything")
    ]
    return report.model_dump()


# ── chat (Phase 1) ────────────────────────────────────────────────────


@method("chat.send")
async def chat_send(params: dict[str, Any]) -> dict[str, Any]:
    """Start a turn. Returns {turn_id}; the reply streams as `token` events."""
    from sidecar.state import runtime

    text = str(params.get("text", ""))
    session_id = params.get("session_id")
    model = params.get("model")
    # Absolute paths, not bytes: the renderer picks files through Electron's
    # own dialog and hands over where they are, and the sidecar opens them
    # itself. The preload exposes no filesystem by design, so a path is the
    # narrowest thing that can cross that boundary and still be useful.
    raw = params.get("attachments")
    attachments = [p for p in raw if isinstance(p, str)] if isinstance(raw, list) else None
    started = await runtime.require_conversation().send(
        text,
        session_id if isinstance(session_id, str) else None,
        model if isinstance(model, str) else None,
        spoken=params.get("spoken") is True,
        attachments=attachments or None,
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


@method("voice.speak")
async def voice_speak(params: dict[str, Any]) -> dict[str, Any]:
    """Read one reply aloud, because he pressed the button on it.

    Typed turns no longer speak by themselves. This is deliberate rather than
    a setting: hearing a reply you are already reading is noise, and hands-free
    still speaks on its own because there nobody is looking.
    """
    from sidecar.state import runtime

    text = params.get("text")
    if not isinstance(text, str) or not text.strip():
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "text is required.")

    spoke = await runtime.require_conversation().speak(text)
    # Not an error: no voice weights is a real state with an honest answer,
    # and the button can grey itself out rather than failing silently.
    return {"ok": spoke, "reason": None if spoke else "no_voice"}


@method("question.answer")
async def question_answer(params: dict[str, Any]) -> dict[str, Any]:
    """Answer a question she is waiting on (`core/questions.py`).

    The turn is suspended on an `asyncio.Future`. If nothing is waiting the
    answer is late — the ten minutes already elapsed and she carried on — and
    saying so beats pretending it landed, which is the same call
    `confirm.respond` makes for the same reason.
    """
    from sidecar.core.questions import Answer
    from sidecar.state import runtime

    request_id = params.get("request_id")
    if not isinstance(request_id, str):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "request_id is required.")

    broker = runtime.questions
    if broker is None:
        raise RpcMethodError(
            ErrorCode.INTERNAL_ERROR, "Questions are not available in this session."
        )

    raw = params.get("answers")
    if not isinstance(raw, list):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "answers must be a list.")
    try:
        answers = [Answer.model_validate(item) for item in raw]
    except ValidationError as exc:
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, f"Bad answer: {exc}") from exc

    delivered = broker.respond(request_id, answers)
    return {"ok": delivered, "expired": not delivered}


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


@method("models.refresh")
async def models_refresh(_params: dict[str, Any]) -> dict[str, Any]:
    """Ask the cloud providers what they offer today, and re-list.

    Deliberately synchronous, unlike the startup refresh: this is behind a
    button, so the caller wants to know the answer before the list redraws.
    """
    from sidecar.providers import catalog
    from sidecar.state import runtime

    availability = runtime.require_availability()
    conversation = runtime.require_conversation()

    if runtime.settings is not None:
        await availability.refresh_discovered(runtime.settings)

    listing = catalog.ModelListing(
        selected=conversation.selected_model,
        bias=str(conversation.routing_bias),
        models=availability.entries(),
    )
    return listing.model_dump(mode="json")


@method("models.adoption")
async def models_adoption(_params: dict[str, Any]) -> dict[str, Any]:
    """How free-model measurement is going, and what quota is left today.

    Two things the user otherwise has no way to see: why a free model they can
    see in the picker is not being routed to yet (it has not passed), and how
    much of a 50-a-day allowance is left. A cap discovered by hitting it
    mid-conversation is the "on is not the same as working" failure
    `settings.online` already exists to avoid.
    """
    from sidecar.providers.openrouter import OpenRouterProvider
    from sidecar.state import runtime

    report: dict[str, Any] = {
        "running": False,
        "budget": 0,
        "left_today": 0,
        "spent_today": 0,
        "probe_count": 0,
        "models": [],
        "quota": {"limit": None, "remaining": None, "reset_at": None},
    }
    if runtime.adoption is not None:
        report.update(await runtime.adoption.report())
        report["running"] = True

    provider = runtime.providers.get("openrouter")
    if isinstance(provider, OpenRouterProvider):
        # Read off the last response rather than counted here: OpenRouter's own
        # figure accounts for the key being used from anywhere.
        report["quota"] = provider.rate_limit.as_dict()
    return report


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
        # A key that has just been added unlocks a provider whose models have
        # never been listed. Detached, so saving a key does not wait on two
        # network round-trips before the dialog closes.
        if value is not None and runtime.settings is not None:
            from sidecar.core.tasks import spawn

            spawn(
                runtime.availability.refresh_discovered(runtime.settings),
                "discovery.after_key",
            )
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


@method("confirm.respond")
async def confirm_respond(params: dict[str, Any]) -> dict[str, Any]:
    """Answer a pending confirmation (§7.1).

    The agent loop is suspended on an `asyncio.Future` waiting for exactly
    this. If nothing is waiting the answer is late — the 120s timeout already
    denied it — and saying so is better than pretending it landed.
    """
    from sidecar.state import runtime

    request_id = params.get("request_id")
    if not isinstance(request_id, str):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "request_id is required.")

    engine = runtime.permissions
    if engine is None:
        raise RpcMethodError(ErrorCode.INTERNAL_ERROR, "Tools are not available in this session.")

    delivered = engine.respond(
        request_id,
        approved=params.get("approved") is True,
        remember=params.get("remember") is True,
    )
    return {"ok": delivered, "expired": not delivered}


@method("tools.list")
async def tools_list(_params: dict[str, Any]) -> dict[str, Any]:
    """Every registered tool and the tier it runs at (rule 4, rule 6).

    Read-only, and it names the DANGER tools too — `schemas()` hides those
    from the *model* when they are switched off, but the person deciding what
    to trust a folder with should be able to see the whole list.
    """
    from sidecar.state import runtime
    from sidecar.tools import registry

    engine = runtime.permissions
    return {
        "allow_danger": bool(engine and engine.allow_danger),
        "mode": str(engine.mode) if engine is not None else "auto",
        "tools": [
            {
                "name": t.name,
                "tier": int(t.tier),
                "description": t.description,
            }
            for t in sorted(registry.all_tools(), key=lambda t: (t.tier, t.name))
        ],
    }


@method("tools.trusted")
async def tools_trusted(params: dict[str, Any]) -> dict[str, Any]:
    """Read or replace the folders she may act in without asking.

    Whole-list replacement rather than add/remove: the UI holds the list, and
    two half-applied edits racing is a worse failure than re-sending four
    strings.
    """
    import json

    from sidecar.memory.settings_store import TRUSTED_PATHS
    from sidecar.state import runtime

    engine = runtime.permissions
    if engine is None:
        raise RpcMethodError(ErrorCode.INTERNAL_ERROR, "Tools are not available in this session.")

    requested = params.get("paths")
    if requested is not None:
        if not isinstance(requested, list):
            raise RpcMethodError(ErrorCode.INVALID_PARAMS, "paths must be a list of folders.")
        cleaned = [str(p) for p in requested if str(p).strip()]
        engine.set_trusted(cleaned)
        if runtime.settings is not None:
            await runtime.settings.set(TRUSTED_PATHS, json.dumps(cleaned))

    return {"paths": [str(p) for p in engine.trusted]}


def _enumerate_drives() -> list[str]:
    """Every fixed drive letter Windows reports, as root paths ("C:\\").

    `GetLogicalDriveStrings` returns one null-terminated block
    (`"C:\\\\\\x00D:\\\\\\x00\\x00"`) rather than a list — that's the real
    Win32 wire format, not a parsing quirk introduced here.
    """
    import win32api

    raw = win32api.GetLogicalDriveStrings()
    return [d for d in raw.split("\x00") if d]


@method("tools.trust_all_drives")
async def tools_trust_all_drives(_params: dict[str, Any]) -> dict[str, Any]:
    """Trust every drive letter on the machine, in one call.

    The direct answer to "give her access to my whole computer" without
    adding each drive to `tools.trusted` by hand — reuses that method's own
    replace-and-persist path; this is only where the list of paths comes
    from. Available regardless of `permissions.mode`: FULL_ACCESS makes it
    moot while active, but MANUAL and AUTO both still read `trusted`.
    """
    import json

    from sidecar.memory.settings_store import TRUSTED_PATHS
    from sidecar.state import runtime

    engine = runtime.permissions
    if engine is None:
        raise RpcMethodError(ErrorCode.INTERNAL_ERROR, "Tools are not available in this session.")

    drives = _enumerate_drives()
    engine.set_trusted(drives)
    if runtime.settings is not None:
        await runtime.settings.set(TRUSTED_PATHS, json.dumps(drives))

    return {"paths": [str(p) for p in engine.trusted]}


@method("permissions.mode")
async def permissions_mode(params: dict[str, Any]) -> dict[str, Any]:
    """Read or replace the global permission mode (manual / auto / full_access).

    Same read-or-replace shape as `tools.trusted`: omit `mode` to read the
    current one, pass it to switch. `PermissionMode`'s own docstring names
    exactly what each value changes.
    """
    from sidecar.memory.settings_store import PERMISSION_MODE
    from sidecar.state import runtime
    from sidecar.tools.permissions import PermissionMode

    engine = runtime.permissions
    if engine is None:
        raise RpcMethodError(ErrorCode.INTERNAL_ERROR, "Tools are not available in this session.")

    requested = params.get("mode")
    if requested is not None:
        try:
            mode = PermissionMode(str(requested))
        except ValueError:
            raise RpcMethodError(
                ErrorCode.INVALID_PARAMS,
                f"mode must be one of: {', '.join(m.value for m in PermissionMode)}.",
            ) from None
        engine.set_mode(mode)
        if runtime.settings is not None:
            await runtime.settings.set(PERMISSION_MODE, mode.value)

    return {"mode": str(engine.mode)}


@method("voice.interrupt")
async def voice_interrupt(_params: dict[str, Any]) -> dict[str, Any]:
    """Stop her talking, now.

    The key-press path. Everything the spoken interrupt does once it has
    decided — flush the audio, cancel the turn — but with no utterance to
    capture and no transcription to wait for, which is the whole point: saying
    "stop" cannot beat 700ms of silence plus half a second of recognition, and
    a key can.
    """
    from sidecar.rpc.events import AssistantState, Event, bus
    from sidecar.state import runtime

    await bus.broadcast(Event.AUDIO_STOP, {"reason": "interrupt"})
    cancelled = 0
    if runtime.conversation is not None:
        cancelled = await runtime.conversation.cancel_active()
    if runtime.listener is not None:
        await runtime.listener.set_playing(False)
    await bus.set_state(AssistantState.IDLE)
    log.info("voice.interrupted", cancelled_turns=cancelled)
    return {"ok": True, "cancelled": cancelled}


@method("voice.playing")
async def voice_playing(params: dict[str, Any]) -> None:
    """The renderer reporting whether sound is coming out of the speakers.

    A notification, and transitions only. The sidecar cannot work this out for
    itself — generation finishing is not playback finishing, and the gap
    between them is precisely when someone talks over her.
    """
    from sidecar.state import runtime

    listener = runtime.listener
    if listener is not None:
        await listener.set_playing(params.get("playing") is True)
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


@method("settings.online")
async def settings_online(params: dict[str, Any]) -> dict[str, Any]:
    """Read or set online mode (§9 Phase 7).

    One method for both, the house pattern (`voice.listen`, `models.bias`):
    pass `enabled` to change it, pass nothing to read it, and either way get
    the current state back.

    Reports `backend` and `key_present` too, because "on" is not the same as
    "working" — the switch can be on with no search key stored, and a UI that
    cannot tell those apart makes the user debug it by asking her a question
    and reading the refusal.
    """
    from sidecar.memory.settings_store import ONLINE_MODE
    from sidecar.providers.search import available as search_backend
    from sidecar.state import runtime

    requested = params.get("enabled")
    if isinstance(requested, bool):
        runtime.online_mode = requested
        if runtime.settings is not None:
            await runtime.settings.set(ONLINE_MODE, requested)
        log.info("online.changed", enabled=requested)

    backend = search_backend()
    return {
        "enabled": runtime.online_mode,
        "backend": backend,
        "key_present": backend is not None,
    }


#: Chromium-based browsers CDP works with, and where each keeps its real
#: profile. **Chrome is not a safe default** — on this project's own
#: reference machine the default browser is Brave (CLAUDE.md, Phase 3:
#: "'browser' opens the default handler... the default is Brave"), and
#: writing a launcher that starts a *different* browser than the one the
#: user actually uses starts it with an empty, logged-out profile, which
#: defeats the entire point of connecting over CDP rather than launching a
#: fresh Playwright-bundled one. Detected via the same `UserChoice` registry
#: lookup `tools/apps.py` already uses for `open_app`'s "browser" category,
#: not assumed.
_KNOWN_BROWSERS: dict[str, str] = {
    "chrome.exe": r"Google\Chrome\User Data",
    "brave.exe": r"BraveSoftware\Brave-Browser\User Data",
    "msedge.exe": r"Microsoft\Edge\User Data",
}


def _default_browser() -> tuple[str, str] | None:
    """(exe path, profile dir) for the user's actual default browser."""
    import os

    from sidecar.tools.apps import Launch, default_app

    entry = default_app("browser")
    if entry is None or entry.launch is not Launch.EXECUTABLE:
        return None
    exe_name = os.path.basename(entry.target).lower()
    profile_suffix = _KNOWN_BROWSERS.get(exe_name)
    if profile_suffix is None:
        return None
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    return entry.target, os.path.join(local_app_data, profile_suffix)


@method("browser.setup")
async def browser_setup(params: dict[str, Any]) -> dict[str, Any]:
    """Write the CDP-debug launcher for the user's real browser, and report
    reachability (§9 Phase 7).

    `settings.online`'s shape: pass `write: true` to (re)write the launcher,
    omit it to just check status. **Never connects through `tools/browser.py`
    to check reachability** — that would open the long-lived connection the
    tools hold for the rest of the session just to answer a status query.
    Chrome's own CDP endpoint (which any Chromium browser exposes under the
    same path) answers a plain HTTP GET, which is what this probes instead.
    """
    from sidecar.config import get_settings

    settings = get_settings()
    detected = _default_browser()
    if params.get("write"):
        _write_browser_launcher(settings.browser_launcher_path, detected)
        log.info(
            "browser.launcher_written",
            path=str(settings.browser_launcher_path),
            browser=detected[0] if detected else "chrome (fallback — could not detect yours)",
        )

    return {
        "cdp_reachable": await _cdp_reachable(),
        "launcher_path": str(settings.browser_launcher_path),
        "launcher_exists": settings.browser_launcher_path.exists(),
        "detected_browser": detected[0] if detected else None,
    }


def _write_browser_launcher(path: Path, detected: tuple[str, str] | None) -> None:
    """A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the
    user can open and read before ever running it.

    The full exe path is used when detection succeeds, rather than relying
    on `start "" chrome.exe` resolving through PATH/App Paths — that only
    works when the detected browser genuinely *is* Chrome, and the whole
    reason this function exists is that it might not be. Falls back to
    Chrome's own name and profile path only when detection fails entirely
    (no default browser set, or it isn't a known Chromium browser) — a
    guess the user can still edit, not silence.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if detected is not None:
        exe, profile = detected
    else:
        exe, profile = "chrome.exe", r"%LocalAppData%\Google\Chrome\User Data"
    script = (
        "@echo off\r\n"
        "REM Written by ARIA (browser.setup). Starts your real browser profile\r\n"
        "REM with remote debugging on, so the browser_* tools can attach to it.\r\n"
        f'start "" "{exe}" --remote-debugging-port=9222 --user-data-dir="{profile}"\r\n'
    )
    path.write_text(script, encoding="utf-8")


async def _cdp_reachable() -> bool:
    import httpx

    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            response = await client.get("http://localhost:9222/json/version")
    except httpx.HTTPError:
        return False
    return response.status_code == 200


@method("turn.rate")
async def turn_rate(params: dict[str, Any]) -> dict[str, Any]:
    """Thumbs up or down on one answer (§9.7).

    §9.7's upgrade path is a labelled dataset, not a bigger model: *"log every
    routing decision with the provider, the resulting turn's latency and a user
    thumbs-up/down. After a few weeks you'll have a labelled dataset to tune the
    rules against."* This is the label half; `routing_log` is the rest.

    `rating: 0` clears it — pressing the same thumb twice means "never mind",
    and a rating you cannot take back is one people stop giving.
    """
    from sidecar.state import runtime

    log_ = runtime.routing_log
    if log_ is None:
        raise RpcMethodError(
            ErrorCode.INTERNAL_ERROR,
            "Ratings are not available in this session. Restart the sidecar.",
        )

    message_id = params.get("message_id")
    if not isinstance(message_id, int):
        raise RpcMethodError(
            ErrorCode.INVALID_PARAMS,
            "turn.rate needs the message_id of the answer being rated.",
        )

    rating = params.get("rating")
    if not isinstance(rating, int) or rating not in (-1, 0, 1):
        raise RpcMethodError(
            ErrorCode.INVALID_PARAMS,
            "rating must be 1 (good), -1 (bad) or 0 (clear it).",
        )

    changed = (
        await log_.clear_rating(message_id) if rating == 0 else await log_.rate(message_id, rating)
    )
    return {"message_id": message_id, "rating": rating or None, "recorded": changed}


@method("turn.ratings")
async def turn_ratings(params: dict[str, Any]) -> dict[str, Any]:
    """Every rating in one conversation, so reopening it shows them again."""
    from sidecar.state import runtime

    log_ = runtime.routing_log
    session_id = params.get("session_id")
    if log_ is None or not isinstance(session_id, str):
        return {"ratings": {}}
    ratings = await log_.ratings_for_session(session_id)
    return {"ratings": {str(k): v for k, v in ratings.items()}}


@method("models.verdicts")
async def models_verdicts(_params: dict[str, Any]) -> dict[str, Any]:
    """How each model has actually been received here.

    The read side of the dataset. Reported rather than acted on: with a handful
    of ratings this is anecdote, and `ModelVerdict.approval` returns None until
    there are enough to be worth reading. Routing still moves on the measured
    `tool_score`, not on this.
    """
    from sidecar.state import runtime

    log_ = runtime.routing_log
    if log_ is None:
        return {"verdicts": []}
    verdicts = await log_.verdicts()
    return {"verdicts": [{**v.model_dump(mode="json"), "approval": v.approval} for v in verdicts]}


# ── memory (Phase 5) ──────────────────────────────────────────────────


def _require_memory() -> Any:
    """The memory services, or a message saying how to turn them on."""
    from sidecar.state import runtime

    if runtime.memory is None:
        raise RpcMethodError(
            ErrorCode.INTERNAL_ERROR,
            "Memory is switched off in this session. Set ARIA_MEMORY_ENABLED=true "
            "and restart the sidecar.",
        )
    return runtime.memory


@method("memory.list")
async def memory_list(params: dict[str, Any]) -> dict[str, Any]:
    """Everything she has learned, for MemoryPanel.

    Superseded facts are excluded by default but askable for: the panel offers
    them as an audit trail, because "why does she think that" is only
    answerable if you can see what it replaced.
    """
    from sidecar.state import runtime

    memory = _require_memory()
    limit = params.get("limit", 200)
    include = bool(params.get("include_superseded", False))

    facts = await memory.semantic.list_facts(
        include_superseded=include, limit=int(limit) if isinstance(limit, int) else 200
    )
    episodes = await memory.episodic.list_episodes(limit=50)
    return {
        "facts": [f.model_dump(mode="json") for f in facts],
        "episodes": [e.model_dump(mode="json") for e in episodes],
        "embeddings_ready": runtime.embeddings_ready,
    }


@method("memory.search")
async def memory_search(params: dict[str, Any]) -> dict[str, Any]:
    """§7.1: search what she remembers. The same path a turn uses."""
    memory = _require_memory()

    query = params.get("query")
    if not isinstance(query, str) or not query.strip():
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "query must be a non-empty string.")

    found = await memory.retriever.retrieve(query)
    return {
        "facts": [
            {"fact": f.fact.model_dump(mode="json"), "score": round(f.score, 4)}
            for f in found.facts
        ],
        "episodes": [
            {"episode": e.episode.model_dump(mode="json"), "score": round(e.score, 4)}
            for e in found.episodes
        ],
        "took_ms": round(found.took_ms, 2),
        "degraded": found.degraded,
    }


@method("memory.forget")
async def memory_forget(params: dict[str, Any]) -> dict[str, Any]:
    """§7.1: delete one fact by id."""
    memory = _require_memory()

    fact_id = params.get("fact_id")
    if not isinstance(fact_id, int):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "fact_id must be an integer.")

    removed = await memory.semantic.forget(fact_id)
    if not removed:
        raise RpcMethodError(
            ErrorCode.INVALID_PARAMS,
            f"No fact {fact_id}. Call memory.list for the current ids.",
        )
    return {"ok": True}


@method("memory.update")
async def memory_update(params: dict[str, Any]) -> dict[str, Any]:
    """Edit a fact, including pinning it.

    Pinning rides here rather than on its own `memory.pin`: it is one column on
    one row, and two methods writing the same row is two ways to race it.
    """
    memory = _require_memory()

    fact_id = params.get("fact_id")
    if not isinstance(fact_id, int):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "fact_id must be an integer.")

    object_ = params.get("object")
    confidence = params.get("confidence")
    user_locked = params.get("user_locked")

    updated = await memory.semantic.update(
        fact_id,
        object_=object_ if isinstance(object_, str) else None,
        confidence=float(confidence) if isinstance(confidence, int | float) else None,
        user_locked=bool(user_locked) if user_locked is not None else None,
    )
    if updated is None:
        raise RpcMethodError(
            ErrorCode.INVALID_PARAMS,
            f"No fact {fact_id}. Call memory.list for the current ids.",
        )
    return {"fact": updated.model_dump(mode="json")}


@method("memory.reflect")
async def memory_reflect(params: dict[str, Any]) -> dict[str, Any]:
    """Run the §8.3 pass now, rather than waiting for 3am.

    Synchronous, like `models.refresh`: it sits behind a button and the caller
    wants the report, not an acknowledgement. A second concurrent run is
    refused rather than queued — two model calls extracting the same facts
    would race each other into the merge.
    """
    from sidecar.state import runtime

    reflector = runtime.reflector
    if reflector is None:
        raise RpcMethodError(
            ErrorCode.INTERNAL_ERROR,
            "Reflection is not available in this session. Memory is switched off.",
        )

    # No window unless one is asked for: the high-water mark decides what is
    # unread, and defaulting to 24h here would reintroduce the bug it fixed —
    # pressing the button after a week away would skip the week.
    window = params.get("window_hours")
    report = await reflector.run(window_hours=window if isinstance(window, int) else None)
    return report.model_dump(mode="json")


@method("study.state")
async def study_state(params: dict[str, Any]) -> dict[str, Any]:
    """Where he is in a subject: the map, and what each concept has earned.

    Read-only, and the same state `_study_state` injects into the prompt — so
    the two can never disagree about what has been learned. Exposed rather than
    only logged for the reason `memory.stats` is: `scripts/gate_study.py`
    asserts on this instead of on her prose, because a model that *says* it
    recorded an answer and a row that actually changed are different claims,
    and only the second is what the next session reads.

    Defaults to the subject most recently studied, which is the same one the
    prompt block shows.
    """
    from sidecar.memory import study
    from sidecar.state import runtime

    db = runtime.db
    if db is None:
        return {"subject": None, "concepts": []}

    raw = params.get("subject")
    subject_id = (
        await study.find_subject(db, raw)
        if isinstance(raw, str) and raw.strip()
        else await study.latest_subject_id(db)
    )
    if subject_id is None:
        return {"subject": None, "concepts": []}

    state = await study.state(db, subject_id)
    if state is None:
        return {"subject": None, "concepts": []}

    nxt = state.next_concept
    return {
        "subject_id": state.subject_id,
        "subject": state.subject,
        "source_path": state.source_path,
        "covered": len(state.covered),
        "next": nxt.name if nxt else None,
        "concepts": [
            {
                "id": c.id,
                "name": c.name,
                "summary": c.summary,
                "level": c.level,
                "asked": c.asked,
                "correct": c.correct,
            }
            for c in state.concepts
        ],
    }


def _study_id(params: dict[str, Any], key: str) -> int:
    """A row id off the wire. The panel always sends one; anything else is a
    caller bug worth naming rather than a row id of 0 quietly matching nothing."""
    raw = params.get(key)
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, f"{key} must be a number.")
    return raw


@method("study.subjects")
async def study_subjects(_params: dict[str, Any]) -> dict[str, Any]:
    """Every subject with its progress, most recently studied first.

    What the Study panel opens on. Separate from `study.state`, which returns
    one subject's whole map — a rail section that had to fetch every concept of
    every subject just to draw a list would get slower the more he studies.
    """
    from sidecar.memory import study
    from sidecar.state import runtime

    db = runtime.db
    if db is None:
        return {"subjects": []}
    return {"subjects": await study.list_subjects(db)}


@method("study.start")
async def study_start(params: dict[str, Any]) -> dict[str, Any]:
    """Put a conversation into Study mode with a sub-mode, and say what to send.

    **The RPC sets the state and the caller sends the message.** It would be
    less code to send it here, but then the thing that starts a study session
    would be invisible in the transcript — and pressing "Exam" *is* asking to
    be examined, so it belongs there in his own words. The panel sends the
    returned `opener` through the ordinary `chat.send` path.
    """
    from sidecar.core import study_modes
    from sidecar.core.context import ConversationMode
    from sidecar.state import runtime

    service = runtime.require_conversation()
    session_id = params.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        session_id = await service.store.latest_session_id()
    if not session_id:
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "There is no conversation to study in.")

    sub_mode = study_modes.parse(params.get("sub_mode")) or study_modes.StudySubMode.LEARN
    service.set_mode(session_id, ConversationMode.STUDY)
    service.set_study_submode(session_id, sub_mode)

    policy = study_modes.policy_for(sub_mode)
    return {
        "session_id": session_id,
        "sub_mode": str(sub_mode),
        "label": policy.label,
        "opener": policy.opener,
    }


@method("study.rename")
async def study_rename(params: dict[str, Any]) -> dict[str, Any]:
    """Rename a subject. Not cosmetic — the name is what resuming matches on.

    `ok: false` with a reason rather than an exception when the name is taken:
    two subjects with one name would make `find_subject` a coin flip, and a
    panel that says so beats one that throws.
    """
    from sidecar.memory import study
    from sidecar.state import runtime

    subject_id = _study_id(params, "subject_id")
    name = params.get("name")
    if not isinstance(name, str) or not name.strip():
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "A subject needs a name.")

    renamed = await study.rename_subject(runtime.require_db(), subject_id, name)
    return {
        "ok": renamed,
        "reason": None if renamed else "There is already a subject with that name.",
    }


@method("study.forget")
async def study_forget(params: dict[str, Any]) -> dict[str, Any]:
    """Delete a subject, its map, and every answer recorded against it.

    **The destructive one, and it is not recoverable.** `concepts` cascades
    from `study_subjects` and `concept_mastery` from `concepts`, so this takes
    the whole learning history with it. There is no confirmation round-trip
    here on purpose — this is a click the user made in a panel, not a tool call
    the model asked for, and a dialog in front of the button somebody just
    pressed is asking them to confirm the thing they just did. The panel arms
    it with two clicks instead, the way `MemoryPanel`'s forget already does.
    """
    from sidecar.memory import study
    from sidecar.state import runtime

    subject_id = _study_id(params, "subject_id")
    return {"ok": await study.delete_subject(runtime.require_db(), subject_id)}


@method("study.reset")
async def study_reset(params: dict[str, Any]) -> dict[str, Any]:
    """Put one concept back to never-introduced.

    One click, where deleting a subject takes two: a reset destroys nothing
    that cannot be earned again by answering a question.
    """
    from sidecar.memory import study
    from sidecar.state import runtime

    concept_id = _study_id(params, "concept_id")
    return {"ok": await study.reset_concept(runtime.require_db(), concept_id)}


@method("memory.stats")
async def memory_stats(_params: dict[str, Any]) -> dict[str, Any]:
    """Counts, retrieval latency, and whether embeddings are actually working.

    The latency block is what §9 Phase 5's "<80ms" gate is measured against, so
    it is exposed rather than only logged — `scripts/gate_memory.py` reads it.
    """
    from dataclasses import asdict

    from sidecar.state import runtime

    memory = _require_memory()
    last = await runtime.reflector.last_run() if runtime.reflector else None
    return {
        "facts": await memory.semantic.count(),
        "episodes": await memory.episodic.count(),
        "retrieval": asdict(memory.retriever.stats()),
        "last_reflection": last.strftime("%Y-%m-%dT%H:%M:%SZ") if last else None,
        "reflecting": bool(runtime.reflector and runtime.reflector.running),
        "embeddings_ready": runtime.embeddings_ready,
    }


# ── proactivity (Phase 8) ────────────────────────────────────────────


@method("proactivity.trigger")
async def proactivity_trigger(_params: dict[str, Any]) -> dict[str, Any]:
    """Run one sweep now, rather than waiting for the next five-minute tick.

    Same reasoning as `memory.reflect`: a scheduler with its own cadence is
    not gate-able without a way to force a pass, so this exists purely for
    `scripts/gate_proactivity.py` and manual debugging — nothing in the
    product UI calls it. `tick()` already never raises and applies every
    real gate (focus, rate limit, self-check) itself; this does not bypass
    any of them, it only stops the caller from waiting on the clock.
    """
    from sidecar.state import runtime

    scheduler = runtime.proactivity_scheduler
    if scheduler is None:
        raise RpcMethodError(
            ErrorCode.INTERNAL_ERROR,
            "Proactivity is not available in this session. It is switched off "
            "(proactivity_enabled=false) or the sidecar has no database open.",
        )
    await scheduler.tick()
    return {"ok": True}


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


# ── the file browser panel (permission-modes Part 3) ──────────────────
#
# **UI-facing, not model-facing, and that distinction is the whole design.**
# `list_folder`, `rename_file` and `delete_file` are tools: the *model* asks
# for them, so they go through `PermissionEngine` and its confirmation
# dialog. These are clicks the user makes in a panel they are looking at, on
# a file they can see. Putting a modal in front of "I clicked Rename" would
# be asking someone to confirm the thing they just did.
#
# What that does **not** mean is fewer safety rails. `tools/files.py`'s hard
# refusals — drive roots, Windows, Program Files, ProgramData — are reused
# unchanged, because those were never confirmation mechanisms: they are
# "this must not happen at all", and a panel is not a reason to relax them.
# Deletes go to the Recycle Bin rather than being permanent, which is what
# Explorer itself does and what makes a misclick survivable.


@method("files.browse")
async def files_browse(params: dict[str, Any]) -> dict[str, Any]:
    """One folder's contents, for the panel.

    Deliberately not `list_folder`: that tool summarises for a model and caps
    at what fits in a prompt. A panel wants everything, with sizes and dates,
    and pays no context for it.
    """
    import asyncio
    from pathlib import Path

    from sidecar.tools.files import known_folder

    raw = str(params.get("path") or "").strip()
    if not raw:
        # No path means "where do I start" — the same three folders the
        # indexer already treats as where a person's files live, plus every
        # drive, so the whole machine is reachable from the first render.
        roots: list[dict[str, Any]] = []
        for name in ("desktop", "documents", "downloads"):
            folder = known_folder(name)
            if folder is not None and folder.is_dir():
                roots.append({"name": name.title(), "path": str(folder), "kind": "folder"})
        roots.extend({"name": d, "path": d, "kind": "drive"} for d in _enumerate_drives())
        return {"path": "", "parent": None, "entries": roots}

    target = Path(raw)
    if not await asyncio.to_thread(target.is_dir):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, f"{target} is not a folder.")

    def _read() -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        # `scandir`, not `iterdir` + `stat`: one syscall per entry instead of
        # two, which is the difference between instant and visibly slow in a
        # folder with a few thousand files.
        with os.scandir(target) as entries:
            for entry in entries:
                try:
                    is_dir = entry.is_dir()
                    info = entry.stat()
                except OSError:
                    continue  # a file that vanished mid-listing is not an error
                out.append(
                    {
                        "name": entry.name,
                        "path": entry.path,
                        "kind": "folder" if is_dir else "file",
                        "size": 0 if is_dir else info.st_size,
                        "modified": info.st_mtime,
                    }
                )
        # Folders first, then by name — Explorer's own order, and the one
        # people navigate by without thinking about it.
        out.sort(key=lambda e: (e["kind"] != "folder", str(e["name"]).lower()))
        return out

    try:
        entries = await asyncio.to_thread(_read)
    except OSError as exc:
        raise RpcMethodError(ErrorCode.INTERNAL_ERROR, f"Could not read {target}: {exc}") from exc

    parent = str(target.parent) if target.parent != target else ""
    return {"path": str(target), "parent": parent, "entries": entries}


@method("files.reveal")
async def files_reveal(params: dict[str, Any]) -> dict[str, Any]:
    """Show it in Explorer. The escape hatch for anything this panel does not do."""
    import asyncio
    import subprocess
    from pathlib import Path

    target = Path(str(params.get("path") or ""))
    if not await asyncio.to_thread(target.exists):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, f"There is nothing at {target}.")
    await asyncio.to_thread(subprocess.Popen, ["explorer.exe", "/select,", str(target)])
    return {"ok": True}


@method("files.rename")
async def files_rename(params: dict[str, Any]) -> dict[str, Any]:
    """Rename in place, from a click in the panel.

    Reuses `tools/files.py`'s own refusals rather than reimplementing them:
    those guard against acting inside Windows or Program Files at all, which
    is as true of a click as of a tool call.
    """
    import asyncio
    from pathlib import Path

    from sidecar.tools.files import _refuse

    target = Path(str(params.get("path") or ""))
    clean = str(params.get("name") or "").strip()
    if not clean or set(clean) & set('/\\:*?"<>|'):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, f"{clean!r} is not a valid name.")
    refusal = _refuse(target)
    if refusal is not None:
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, f"I will not rename {target}: {refusal}.")
    if not await asyncio.to_thread(target.exists):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, f"There is nothing at {target}.")

    destination = target.with_name(clean)
    if await asyncio.to_thread(destination.exists):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, f"{clean} already exists there.")
    await asyncio.to_thread(target.rename, destination)
    log.info("files.renamed", was=str(target), now=str(destination))
    _invalidate_finder_scan()
    return {"path": str(destination)}


@method("files.delete")
async def files_delete(params: dict[str, Any]) -> dict[str, Any]:
    """**To the Recycle Bin, not gone.**

    This is the one place in the codebase that deletes without a confirmation
    round-trip, and the reason it is allowed to is that it does not actually
    destroy anything: `SHFileOperation` with `FOF_ALLOWUNDO` is what Explorer
    itself does, and the undo is the Recycle Bin the user already knows how
    to use. Rule 5 asks for a confirmation before a destructive operation;
    recoverable-by-design is the honest way to satisfy it for a click the
    user made on a file they are looking at.

    `send2trash` would be the obvious library and is deliberately not added —
    `pywin32` is already a dependency and exposes the same shell API.
    """
    import asyncio
    from pathlib import Path

    from sidecar.tools.files import _refuse

    target = Path(str(params.get("path") or ""))
    refusal = _refuse(target)
    if refusal is not None:
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, f"I will not delete {target}: {refusal}.")
    if not await asyncio.to_thread(target.exists):
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, f"There is nothing at {target}.")

    def _recycle() -> None:
        from win32com.shell import shell, shellcon

        # Double-NUL terminated, per the Win32 contract for a path *list*.
        result, aborted = shell.SHFileOperation(
            (
                0,
                shellcon.FO_DELETE,
                str(target) + "\0",
                None,
                shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION | shellcon.FOF_SILENT,
                None,
                None,
            )
        )
        if result != 0 or aborted:
            raise OSError(f"Windows would not recycle {target} (code {result}).")

    try:
        await asyncio.to_thread(_recycle)
    except OSError as exc:
        raise RpcMethodError(ErrorCode.INTERNAL_ERROR, str(exc)) from exc

    log.info("files.recycled", path=str(target))
    _invalidate_finder_scan()
    return {"ok": True, "recycled": True}


def _invalidate_finder_scan() -> None:
    """The panel changed the filesystem, so the finder's cached scan is stale.

    The same call every mutating tool in `tools/files.py` makes. Forgetting it
    here would reproduce, from a different direction, the bug where a file she
    had just touched stayed invisible to `find` for 45 seconds.
    """
    from sidecar.tools.finder import invalidate_scan

    invalidate_scan()


@method("chat.mode")
async def chat_mode(params: dict[str, Any]) -> dict[str, Any]:
    """Read or set a conversation's mode. Omit `mode` to read.

    The read-or-write shape `models.bias`, `permissions.mode` and
    `settings.online` all already use: pass the value to change it, pass
    nothing to read it, and either way get the current state back.

    **Scoped to one conversation, not global.** A new chat starts at NORMAL,
    so a mode chosen last week cannot quietly shape today's answers — the
    behaviour Eyaas asked for, and the one that fails safe, because a
    forgotten global mode is invisible and changes every reply.

    Research reports `online_required` rather than turning online mode on by
    itself. The query leaves the machine, and `settings.online` is deliberate
    for that reason; a style control silently starting to send traffic off the
    machine would be exactly the kind of gate that should not move on its own.
    """
    from sidecar.core.context import ConversationMode
    from sidecar.core.modes import policy_for
    from sidecar.state import runtime

    conversation = runtime.require_conversation()
    session_id = params.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        session_id = await conversation.store.latest_session_id()
    if session_id is None:
        raise RpcMethodError(ErrorCode.INVALID_PARAMS, "There is no conversation yet.")

    requested = params.get("mode")
    if requested is not None:
        try:
            chosen = ConversationMode(str(requested))
        except ValueError as exc:
            allowed = ", ".join(m.value for m in ConversationMode)
            raise RpcMethodError(
                ErrorCode.INVALID_PARAMS, f"Unknown mode {requested!r}. Allowed: {allowed}."
            ) from exc
        conversation.set_mode(session_id, chosen)

    mode = conversation.mode_for(session_id)
    policy = policy_for(mode)
    return {
        "session_id": session_id,
        "mode": str(mode),
        "label": policy.label,
        # "On" is not the same as "working" — the `settings.online` lesson.
        # Research without a web tool is a real state and the UI has to be
        # able to say so rather than leaving her to explain it in a refusal.
        "online_required": mode is ConversationMode.RESEARCH,
        "online_enabled": runtime.online_mode,
        # So `ModelPicker`'s own bias control can say it has been overridden
        # rather than displaying a setting that is not in force.
        "effective_bias": str(policy.bias) if policy.bias else None,
        # What this mode actually *does*, so the control can say so rather
        # than leaving the user to infer it from the answers. These are the
        # levers, not a description of them.
        "done_when": policy.done_when,
        "max_steps": policy.max_steps,
        "tools": str(policy.tools),
    }
