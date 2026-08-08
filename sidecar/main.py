"""ARIA sidecar entrypoint — FastAPI app, /health, and the /rpc WebSocket.

Run standalone with ``npm run sidecar``; Electron spawns the same module.
Binds 127.0.0.1 only (BUILD_SPEC §11).
"""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import AsyncIterator
from typing import Any

import structlog
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from sidecar.config import Settings, get_settings
from sidecar.core.conversation import ConversationService
from sidecar.core.listener import Listener, WakeMode
from sidecar.core.router import Router, RoutingBias
from sidecar.core.tasks import spawn
from sidecar.handshake import (
    bearer_from_header,
    clear_handshake,
    resolve_token,
    token_matches,
    write_handshake,
)
from sidecar.logging_setup import configure_logging
from sidecar.memory.db import Database
from sidecar.memory.indexer import Indexer
from sidecar.memory.messages import ConversationStore
from sidecar.memory.settings_store import (
    ROUTING_BIAS,
    SELECTED_MODEL,
    TRUSTED_PATHS,
    WAKE_WORD_ENABLED,
    SettingsStore,
)
from sidecar.memory.tool_log import ToolJournal
from sidecar.providers import catalog
from sidecar.providers.availability import AvailabilityService
from sidecar.providers.base import LLMProvider, ProviderError
from sidecar.providers.connectivity import connectivity
from sidecar.providers.embeddings import OllamaEmbeddings
from sidecar.providers.gemini import GeminiProvider
from sidecar.providers.health import tracker
from sidecar.providers.ollama import OllamaProvider
from sidecar.providers.openai import OpenAIProvider
from sidecar.providers.stt import TranscriptionUnavailable, WhisperSTT
from sidecar.providers.tts import KokoroTTS, SpeechUnavailable
from sidecar.providers.vad import SileroVAD
from sidecar.providers.wakeword import OpenWakeWord, missing_models
from sidecar.rpc.events import bus
from sidecar.rpc.handlers import build_health, dispatch, method_names
from sidecar.state import runtime
from sidecar.tools import finder
from sidecar.tools.files import known_folder
from sidecar.tools.permissions import PermissionEngine

log = structlog.get_logger(__name__)

# Set once at startup, compared against every /rpc upgrade.
_AUTH_TOKEN: str = ""

WS_UNAUTHORIZED = 1008  # RFC 6455 policy violation


def _startup(settings: Settings) -> None:
    """Prepare the filesystem, database, and auth token. Order matters."""
    global _AUTH_TOKEN

    settings.ensure_dirs()
    configure_logging(settings.log_path, dev=settings.dev, level=settings.log_level)

    db = Database(settings.db_path)
    version = db.migrate()
    runtime.db = db
    log.info("db.ready", path=str(settings.db_path), schema_version=version)

    _AUTH_TOKEN = resolve_token(settings.token)
    write_handshake(settings.handshake_path, _AUTH_TOKEN)

    log.info(
        "sidecar.ready",
        host=settings.host,
        port=settings.port,
        dev=settings.dev,
        methods=method_names(),
    )


def _shutdown(settings: Settings) -> None:
    clear_handshake(settings.handshake_path)
    if runtime.db is not None:
        runtime.db.close()
        runtime.reset()
    log.info("sidecar.stopped")


async def _discover_local_models(provider: OllamaProvider) -> list[str]:
    """Ask Ollama what is actually pulled. Never fatal — Ollama may be down."""
    try:
        models = await provider.list_models()
    except ProviderError as exc:
        runtime.ollama_ready = False
        log.warning("ollama.list_failed", error=str(exc))
        return []

    runtime.ollama_ready = True
    log.info("ollama.models", count=len(models), models=models)
    return models


async def _start_conversation(settings: Settings) -> None:
    """Wire every provider, the router, and the conversation service.

    §12: a model that unloaded costs 8-15s. The user must never hit that, so we
    pay it here at startup instead. Warm-up failure is not fatal — the sidecar
    stays up and reports it, because Ollama not running is a recoverable state
    the UI should show rather than a crash.
    """
    ollama = OllamaProvider(settings.ollama_url)
    providers: dict[str, LLMProvider] = {
        str(catalog.ProviderName.OLLAMA): ollama,
        str(catalog.ProviderName.OPENAI): OpenAIProvider(),
        str(catalog.ProviderName.GEMINI): GeminiProvider(),
    }

    runtime.provider = ollama
    runtime.providers = providers
    runtime.local_models = await _discover_local_models(ollama)

    availability = AvailabilityService(tracker)
    availability.set_local_models(runtime.local_models)
    runtime.availability = availability

    # Refreshes on a timer so a turn never waits on a network round-trip to
    # answer "are you online" — §9.7 asks for exactly this caching.
    connectivity.start()

    settings_store = SettingsStore(runtime.require_db())
    runtime.settings = settings_store

    # The picker fills in from the last listing immediately; a refresh only
    # happens if that listing is stale, and never on the path of a turn.
    fresh = await availability.load_discovered(settings_store)
    if not fresh:
        spawn(availability.refresh_discovered(settings_store), "discovery")

    selected = await settings_store.get(SELECTED_MODEL, catalog.SMART_ID)
    bias = _resolve_bias(await settings_store.get(ROUTING_BIAS, str(RoutingBias.QUALITY)))

    # One tracker shared by the router and `models.list`, so the picker greys out
    # exactly what the router refuses to use.
    local_default = catalog.default_local(runtime.local_models)
    runtime.local_model = local_default.id
    # Importing the package is what registers the tools (rule 4).
    import sidecar.tools  # noqa: F401

    runtime.permissions = PermissionEngine(
        bus,
        ToolJournal(runtime.require_db()),
        allow_danger=settings.allow_danger_tools,
    )
    stored_trusted = await settings_store.get(TRUSTED_PATHS)
    if stored_trusted:
        import json as _json

        with contextlib.suppress(ValueError, TypeError):
            runtime.permissions.set_trusted(_json.loads(str(stored_trusted)))

    runtime.tts = _build_tts(settings)
    runtime.stt = _build_stt(settings)
    runtime.conversation = ConversationService(
        store=ConversationStore(runtime.require_db()),
        provider=ollama,
        bus=bus,
        model=local_default.id,
        num_ctx=settings.num_ctx,
        context_token_budget=settings.context_token_budget,
        providers=providers,
        router=Router(tracker, bias),
        health=tracker,
        selected_model=selected if isinstance(selected, str) else catalog.SMART_ID,
        usable_models=availability.usable,
        permissions=runtime.permissions,
        tts=runtime.tts,
    )
    log.info(
        "conversation.ready",
        local_default=local_default.id,
        selected=selected,
        bias=str(bias),
    )

    await _build_listener(settings, settings_store)
    _build_indexer(settings)

    if not settings.warm_on_startup:
        return
    if local_default.id not in runtime.local_models:
        log.warning(
            "model.warm_skipped",
            model=local_default.id,
            fix=f"Run: ollama pull {local_default.id}",
        )
        return

    try:
        took_ms = await ollama.warm(local_default.id)
        runtime.ollama_ready = True
        log.info("model.warm", model=local_default.id, took_ms=round(took_ms, 1))
    except ProviderError as exc:
        runtime.ollama_ready = False
        log.warning("model.warm_failed", model=local_default.id, error=str(exc))


def _build_tts(settings: Settings) -> KokoroTTS | None:
    """Speech, warmed in the background.

    Warming is a task rather than awaited: it costs ~2.4s on the first
    synthesis, and holding startup for it would delay the window appearing for
    something the user may not use in this session. Until it finishes,
    `SpeechStream` sees `ready == False` and simply stays quiet.
    """
    if not settings.voice_enabled:
        log.info("tts.disabled")
        return None

    engine = KokoroTTS(
        settings.models_dir,
        voice=settings.voice,
        speed=settings.voice_speed,
        lang=settings.voice_lang,
    )

    async def warm() -> None:
        try:
            await engine.start()
        except SpeechUnavailable as exc:
            # Missing weights is a setup step, not a crash. She types instead.
            log.warning("tts.unavailable", error=str(exc))
        except Exception:
            log.exception("tts.warm_failed")

    runtime.tts_warm = asyncio.create_task(warm())
    return engine


def _build_stt(settings: Settings) -> WhisperSTT | None:
    """Speech recognition, warmed in the background like the voice.

    The first load downloads ~150MB and takes ~33s here. Doing that while
    someone holds the talk button would look broken, so it happens on startup
    and `voice.transcribe` refuses politely until it is ready.
    """
    if not settings.voice_enabled:
        return None

    engine = WhisperSTT(settings.models_dir / "whisper", model_size=settings.stt_model)

    async def warm() -> None:
        try:
            await engine.start()
        except TranscriptionUnavailable as exc:
            log.warning("stt.unavailable", error=str(exc))
        except Exception:
            log.exception("stt.warm_failed")

    runtime.stt_warm = asyncio.create_task(warm())
    return engine


async def _build_listener(settings: Settings, store: SettingsStore) -> None:
    """Hands-free listening.

    Built eagerly rather than warmed in a task: the VAD loads in ~170ms, which
    is cheap enough to pay at startup and buys a `voice.listen` that can answer
    truthfully the moment the window asks.

    **Phrase mode needs no wake word weights**, only the VAD and the recogniser
    that stage 2 already loads — so the default path has nothing extra to
    download. Model mode does, and falls back to phrase mode rather than
    leaving hands-free unavailable, because being able to talk to her matters
    more than which phrase opens the conversation.
    """
    if not settings.voice_enabled or runtime.stt is None:
        return

    mode = WakeMode(settings.wake_mode)
    wake: OpenWakeWord | None = None

    if mode is WakeMode.MODEL:
        models_dir = settings.models_dir / "openwakeword"
        absent = missing_models(models_dir)
        if absent:
            log.warning(
                "wakeword.unavailable",
                missing=absent,
                fix="Run: python scripts/fetch_wakeword.py",
                falling_back_to="phrase",
            )
            mode = WakeMode.PHRASE
        else:
            wake = OpenWakeWord(models_dir, threshold=settings.wake_word_threshold)
            try:
                await wake.start()
            except Exception as exc:  # noqa: BLE001 — never fatal
                log.warning("wakeword.unavailable", error=str(exc), falling_back_to="phrase")
                wake, mode = None, WakeMode.PHRASE

    vad = SileroVAD()
    try:
        await asyncio.to_thread(vad.start)
    except Exception as exc:  # noqa: BLE001 — no VAD means no hands-free, not no sidecar
        log.warning("listener.unavailable", error=str(exc))
        return

    listener = Listener(
        vad=vad,
        stt=runtime.stt,
        conversation=runtime.require_conversation(),
        bus=bus,
        wake=wake,
        mode=mode,
        barge_in=settings.barge_in_enabled,
        armed_window_s=settings.armed_window_s,
    )
    runtime.listener = listener

    # The user's answer from last time, not the config default: turning the
    # microphone on is a decision worth remembering.
    stored = await store.get(WAKE_WORD_ENABLED)
    wanted = settings.wake_word_enabled if stored is None else str(stored) == "true"
    if wanted:
        await listener.enable()
    log.info("listener.ready", mode=str(mode), enabled=listener.enabled)


def _build_indexer(settings: Settings) -> None:
    """Start reading documents in the background, if that is wanted.

    Deliberately last in startup and deliberately lazy: it must never be the
    reason the window takes longer to appear, and the first thing it does is
    ask whether the machine is busy.
    """
    if not settings.index_files:
        log.info("indexer.disabled")
        return

    roots = [p for p in (known_folder(n) for n in ("documents", "desktop", "downloads")) if p]
    if not roots:
        return

    embeddings = OllamaEmbeddings(settings.ollama_url)
    indexer = Indexer(
        runtime.require_db(),
        embeddings,
        roots,
        files_per_min=settings.index_files_per_min,
        # The one input that keeps a turn quick: while she is answering, the
        # indexer stops entirely rather than competing for the same cores.
        is_busy=lambda: bool(runtime.conversation and runtime.conversation.busy),
    )
    runtime.indexer = indexer
    finder.SEMANTIC.db = runtime.require_db()
    finder.SEMANTIC.embeddings = embeddings
    indexer.start()


def _resolve_bias(stored: object) -> RoutingBias:
    """A hand-edited settings row must not stop the sidecar booting."""
    try:
        return RoutingBias(str(stored))
    except ValueError:
        log.warning("router.bad_bias", stored=stored, fix="Using 'quality'.")
        return RoutingBias.QUALITY


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    _startup(settings)
    await _start_conversation(settings)
    try:
        yield
    finally:
        await connectivity.stop()
        if runtime.tts is not None:
            await runtime.tts.aclose()
        if runtime.stt is not None:
            await runtime.stt.aclose()
        if runtime.conversation is not None:
            await runtime.conversation.shutdown()
        # Every provider holds an httpx pool, not just the local one. One that
        # refuses to close must not strand the others still open.
        for name, provider in runtime.providers.items():
            try:
                await provider.aclose()
            except Exception:  # noqa: BLE001 — shutdown path, nothing left to handle it
                log.warning("provider.close_failed", provider=name)
        _shutdown(settings)


app = FastAPI(title="ARIA sidecar", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, Any]:
    """Liveness probe for Electron's supervisor.

    Deliberately cheap and dependency-free: it is polled every 5s and a slow or
    failing answer triggers a restart. The rich report is the ``system.health``
    RPC.
    """
    return build_health(db_ready=runtime.db_ready).model_dump(
        include={"status", "version", "uptime_s", "db"}
    )


@app.websocket("/rpc")
async def rpc(websocket: WebSocket) -> None:
    """Token-gated JSON-RPC endpoint (§7.1).

    The port is reachable by any browser tab on this machine, so an unauthorised
    upgrade is closed before a single message is read.
    """
    presented = bearer_from_header(websocket.headers.get("authorization"))
    if not token_matches(_AUTH_TOKEN, presented):
        log.warning("rpc.unauthorized", client=str(websocket.client))
        await websocket.close(code=WS_UNAUTHORIZED, reason="Invalid or missing bearer token.")
        return

    await websocket.accept()
    bus.add(websocket)
    # Snapshot first: a reconnecting renderer must learn the current state even
    # when nothing has changed since it dropped.
    await bus.send_state_snapshot(websocket)

    try:
        await _serve(websocket)
    except WebSocketDisconnect:
        pass
    finally:
        bus.discard(websocket)
        if websocket.client_state is WebSocketState.CONNECTED:
            with contextlib.suppress(RuntimeError):
                await websocket.close()


async def _serve(websocket: WebSocket) -> None:
    """Read/dispatch/reply until the client goes away."""
    while True:
        raw = await websocket.receive_text()
        response = await dispatch(raw)
        if response is not None:
            await websocket.send_text(response.model_dump_json(exclude_none=True))


def main() -> None:
    """Console entrypoint for ``python -m sidecar.main``."""
    settings = get_settings()
    # Configure early so uvicorn's own startup lines land in the log file too.
    # configure_logging is idempotent; lifespan calls it again after ensure_dirs.
    settings.ensure_dirs()
    configure_logging(settings.log_path, dev=settings.dev, level=settings.log_level)
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_config=None,  # logging_setup owns the handlers
        access_log=False,
    )


if __name__ == "__main__":
    main()
