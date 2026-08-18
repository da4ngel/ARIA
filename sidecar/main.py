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
from sidecar.memory.episodic import EpisodicMemory
from sidecar.memory.indexer import Indexer
from sidecar.memory.messages import ConversationStore
from sidecar.memory.reflection import Reflector
from sidecar.memory.retrieval import MemoryServices, Retriever
from sidecar.memory.routing_log import RoutingLog
from sidecar.memory.scheduler import MemoryScheduler
from sidecar.memory.semantic import SemanticMemory
from sidecar.memory.settings_store import (
    ONLINE_MODE,
    PERMISSION_MODE,
    ROUTING_BIAS,
    SELECTED_MODEL,
    TRUSTED_PATHS,
    WAKE_WORD_ENABLED,
    SettingsStore,
)
from sidecar.memory.tool_log import ToolJournal
from sidecar.persona import focus
from sidecar.persona import proactivity as proactivity_module
from sidecar.providers import catalog
from sidecar.providers.availability import AvailabilityService
from sidecar.providers.base import LLMProvider, ProviderError
from sidecar.providers.connectivity import connectivity
from sidecar.providers.embeddings import MODEL as EMBEDDING_MODEL
from sidecar.providers.embeddings import OllamaEmbeddings
from sidecar.providers.gemini import GeminiProvider
from sidecar.providers.health import tracker
from sidecar.providers.ollama import OllamaProvider
from sidecar.providers.ollama_supervisor import OllamaSupervisor
from sidecar.providers.openai import OpenAIProvider
from sidecar.providers.search import WebSearch
from sidecar.providers.search import available as search_backend
from sidecar.providers.stt import TranscriptionUnavailable, WhisperSTT
from sidecar.providers.tts import KokoroTTS, SpeechUnavailable
from sidecar.providers.vad import SileroVAD
from sidecar.providers.wakeword import OpenWakeWord, missing_models
from sidecar.rpc.events import bus
from sidecar.rpc.handlers import build_health, dispatch, method_names
from sidecar.state import runtime
from sidecar.tools import finder
from sidecar.tools.files import known_folder
from sidecar.tools.permissions import PermissionEngine, PermissionMode

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
    # Our token, so a sidecar that failed to bind cannot delete the running
    # one's handshake on its way out.
    clear_handshake(settings.handshake_path, _AUTH_TOKEN)
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

    availability = AvailabilityService(tracker)
    runtime.availability = availability

    async def _local_models_arrived(models: list[str]) -> bool:
        """Ollama is reachable again — re-arm everything that reads from it.

        `local_models` is what the picker greys out against and what the
        router checks before choosing a local model, and it used to be
        written exactly once, at startup. Starting Ollama afterwards left it
        empty, so local models stayed dead until ARIA itself was restarted —
        which is what Eyaas kept hitting.
        """
        runtime.local_models = models
        runtime.ollama_ready = True
        availability.set_local_models(models)
        log.info("ollama.models", count=len(models), models=models)

        # A daemon that has just been (re)started holds no model at all, so
        # the next turn would pay the 8-15s cold start §12 exists to keep the
        # user away from. Warming here is safe against rule 2 for exactly
        # that reason — there is nothing resident to sit beside.
        local_id = runtime.local_model
        if not (settings.warm_on_startup and local_id and local_id in models):
            return True
        try:
            took_ms = await ollama.warm(local_id)
        except ProviderError as exc:
            # Measured on a cold start: Ollama serves `/api/tags` well before
            # it can serve `/api/chat`, so a warm fired the moment it looks
            # reachable can come back 500. Reporting False asks the
            # supervisor to try again next tick rather than leaving the model
            # cold for the user's first turn.
            log.warning("model.warm_failed", model=local_id, error=str(exc))
            return False
        log.info("model.warm", model=local_id, took_ms=round(took_ms, 1))
        return True

    supervisor = OllamaSupervisor(
        ollama,
        autostart=settings.ollama_autostart,
        start_timeout_s=settings.ollama_start_timeout_s,
        on_ready=_local_models_arrived,
    )
    runtime.ollama_supervisor = supervisor
    # **Before discovery, not after.** A cold start with Ollama not running
    # is the case this exists for: probe, start it, wait for it, and only
    # then ask what is pulled. Never fatal — `ensure_running` returns False
    # and the sidecar comes up with cloud models and an honest health report.
    await supervisor.ensure_running()

    runtime.local_models = await _discover_local_models(ollama)
    availability.set_local_models(runtime.local_models)
    supervisor.start()

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

    # Defaults to AUTO (the field's own default) when unset — a fresh
    # install must not launch into FULL_ACCESS just because the key is
    # missing. Unlike TRUSTED_PATHS this is stored single-encoded, the same
    # plain `get`/`set` shape ONLINE_MODE already uses below.
    stored_mode = await settings_store.get(PERMISSION_MODE)
    if stored_mode:
        with contextlib.suppress(ValueError):
            runtime.permissions.set_mode(PermissionMode(str(stored_mode)))

    # Off unless it has been switched on before. The query leaves this
    # machine, so the default is the user's decision, not an inherited one.
    stored_online = await settings_store.get(ONLINE_MODE)
    runtime.online_mode = (
        bool(stored_online) if stored_online is not None else settings.online_mode
    )
    runtime.search = WebSearch()
    log.info(
        "online.ready",
        enabled=runtime.online_mode,
        backend=search_backend(),
    )

    runtime.tts = _build_tts(settings)
    runtime.stt = _build_stt(settings)

    # Built before the conversation, because the conversation takes it. Longer
    # keep-alive than the indexer's: a 752ms cold start does not fit inside
    # §9's 80ms retrieval budget, so the model stays resident.
    runtime.embeddings = OllamaEmbeddings(settings.ollama_url, keep_alive="30m")
    spawn(_probe_embeddings(), "embeddings.probe")

    store = ConversationStore(runtime.require_db())
    # §9.7's labelled dataset. Written after each reply, never on the path.
    runtime.routing_log = RoutingLog(runtime.require_db())
    memory = _build_memory(settings, store, ollama, local_default.id)

    runtime.conversation = ConversationService(
        store=store,
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
        memory=memory,
        routing_log=runtime.routing_log,
        db=runtime.require_db(),
    )
    log.info(
        "conversation.ready",
        local_default=local_default.id,
        selected=selected,
        bias=str(bias),
        memory=memory is not None,
    )

    _start_memory_scheduler(settings, settings_store, providers, availability)
    _start_proactivity_scheduler(settings, ollama, local_default.id)

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


async def _probe_embeddings() -> None:
    """Ask once whether `nomic-embed-text` is pulled. Never blocks startup.

    A False here is not a failure: memory falls back to word matching, and the
    log says what to run. Chat is unaffected either way — nothing on the turn
    path ever waits on this.
    """
    if runtime.embeddings is None:
        return
    ready = await runtime.embeddings.available()
    runtime.embeddings_ready = ready
    if ready:
        log.info("embeddings.ready", model=EMBEDDING_MODEL)
    else:
        log.warning(
            "embeddings.unavailable",
            model=EMBEDDING_MODEL,
            fix=f"Run: ollama pull {EMBEDDING_MODEL} — until then memory "
            "falls back to word matching and file search by meaning is off.",
        )


def _build_memory(
    settings: Settings,
    store: ConversationStore,
    provider: LLMProvider,
    model: str,
) -> MemoryServices | None:
    """Facts, episodes and retrieval, as one handle for the conversation."""
    if not settings.memory_enabled:
        log.info("memory.disabled")
        return None

    db = runtime.require_db()
    semantic = SemanticMemory(db, runtime.embeddings)
    episodic = EpisodicMemory(
        db,
        runtime.embeddings,
        store,
        provider,
        model,
        num_ctx=settings.num_ctx,
        is_busy=lambda: bool(runtime.conversation and runtime.conversation.busy),
    )
    retriever = Retriever(
        semantic,
        episodic,
        runtime.embeddings,
        deadline_s=settings.memory_retrieval_deadline_ms / 1000.0,
    )
    runtime.memory = MemoryServices(
        semantic=semantic, episodic=episodic, retriever=retriever, store=store
    )
    return runtime.memory


def _start_memory_scheduler(
    settings: Settings,
    settings_store: SettingsStore,
    providers: dict[str, LLMProvider],
    availability: AvailabilityService,
) -> None:
    """Idle sweeps always; the nightly §8.3 pass only if it is wanted."""
    memory = runtime.memory
    if memory is None:
        return

    runtime.reflector = Reflector(
        runtime.require_db(),
        memory.semantic,
        memory.episodic,
        settings_store,
        providers,
        usable=availability.usable(),
        local_models=runtime.local_models,
    )

    if not settings.memory_reflection_enabled:
        log.info("reflection.disabled")
        return

    reflector = runtime.reflector
    scheduler = MemoryScheduler(
        on_sweep=lambda: memory.episodic.close_idle_sessions(
            idle_minutes=settings.memory_idle_close_minutes
        ),
        on_reflect=reflector.run,
        last_reflection=reflector.last_run,
        unreflected=reflector.unreflected_count,
        is_busy=lambda: bool(runtime.conversation and runtime.conversation.busy),
        hour=settings.memory_reflection_hour,
    )
    runtime.memory_scheduler = scheduler
    scheduler.start()


def _start_proactivity_scheduler(
    settings: Settings, local_provider: LLMProvider, local_model: str
) -> None:
    """Unprompted messages (Phase 8). Off entirely when the switch is off —
    the same "no tool at all" shape `allow_danger_tools` and online mode
    already use, not a scheduler that starts and immediately declines to
    do anything.
    """
    if not settings.proactivity_enabled:
        log.info("proactivity.disabled")
        return
    if runtime.conversation is None:
        return

    conversation = runtime.conversation
    db = runtime.require_db()
    store = ConversationStore(db)

    async def find_candidates() -> list[proactivity_module.Candidate]:
        return await proactivity_module.default_candidates(db, store)

    async def self_check(candidate: proactivity_module.Candidate) -> bool:
        return await proactivity_module.default_self_check(local_provider, local_model, candidate)

    async def deliver(candidate: proactivity_module.Candidate) -> None:
        await conversation.send_proactive(
            candidate.text,
            urgency=candidate.urgency,
            trigger=candidate.trigger,
            procedure_name=candidate.ref,
        )

    def is_actively_working() -> bool:
        # Two different "busy" signals, composed here rather than baked into
        # `focus.py`: whether the *user* is at the keyboard (Win32) and
        # whether *she* is mid-reply. Interrupting either is the wrong kind
        # of proactive.
        return focus.is_actively_working() or conversation.busy

    scheduler = proactivity_module.ProactivityScheduler(
        store=store,
        find_candidates=find_candidates,
        self_check=self_check,
        deliver=deliver,
        is_actively_working=is_actively_working,
    )
    runtime.proactivity_scheduler = scheduler
    scheduler.start()


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

    # Shared with memory retrieval rather than a second instance: one Ollama
    # connection pool and one lock, so the two never contend independently.
    embeddings = runtime.embeddings or OllamaEmbeddings(settings.ollama_url)
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
        if runtime.ollama_supervisor is not None:
            await runtime.ollama_supervisor.stop()
        if runtime.memory_scheduler is not None:
            await runtime.memory_scheduler.stop()
        if runtime.proactivity_scheduler is not None:
            await runtime.proactivity_scheduler.stop()
        if runtime.embeddings is not None:
            await runtime.embeddings.aclose()
        if runtime.search is not None:
            await runtime.search.aclose()
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
