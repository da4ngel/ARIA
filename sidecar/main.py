"""ARIA sidecar entrypoint — FastAPI app, /health, and the /rpc WebSocket.

Run standalone with ``npm run sidecar``; Electron spawns the same module.
Binds 127.0.0.1 only (BUILD_SPEC §11).
"""

from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator
from typing import Any

import structlog
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from sidecar.config import Settings, get_settings
from sidecar.core.conversation import ConversationService
from sidecar.handshake import (
    bearer_from_header,
    clear_handshake,
    resolve_token,
    token_matches,
    write_handshake,
)
from sidecar.logging_setup import configure_logging
from sidecar.memory.db import Database
from sidecar.memory.messages import ConversationStore
from sidecar.providers.base import ProviderError
from sidecar.providers.ollama import OllamaProvider
from sidecar.rpc.events import bus
from sidecar.rpc.handlers import build_health, dispatch, method_names
from sidecar.state import runtime

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


async def _start_conversation(settings: Settings) -> None:
    """Wire the provider and conversation service, then warm the model.

    §12: a model that unloaded costs 8-15s. The user must never hit that, so we
    pay it here at startup instead. Warm-up failure is not fatal — the sidecar
    stays up and reports it, because Ollama not running is a recoverable state
    the UI should show rather than a crash.
    """
    provider = OllamaProvider(settings.ollama_url)
    store = ConversationStore(runtime.require_db())

    runtime.provider = provider
    runtime.local_model = settings.local_model
    runtime.conversation = ConversationService(
        store=store,
        provider=provider,
        bus=bus,
        model=settings.local_model,
        num_ctx=settings.num_ctx,
        context_token_budget=settings.context_token_budget,
    )

    if not settings.warm_on_startup:
        return

    try:
        took_ms = await provider.warm(settings.local_model)
        runtime.ollama_ready = True
        log.info("model.warm", model=settings.local_model, took_ms=round(took_ms, 1))
    except ProviderError as exc:
        runtime.ollama_ready = False
        log.warning("model.warm_failed", model=settings.local_model, error=str(exc))


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    _startup(settings)
    await _start_conversation(settings)
    try:
        yield
    finally:
        if runtime.conversation is not None:
            await runtime.conversation.shutdown()
        if runtime.provider is not None:
            await runtime.provider.aclose()
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
