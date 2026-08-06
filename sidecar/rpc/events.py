"""Server -> client push notifications and the set of live connections (§7.1).

Events are fire-and-forget. A client that has gone away is dropped rather than
allowed to block the sender — the sidecar keeps running whether or not a window
is attached (BUILD_SPEC §3: kill the Electron window without losing state).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Protocol

import structlog

from sidecar.rpc.protocol import RpcNotification

log = structlog.get_logger(__name__)


class AssistantState(StrEnum):
    """The ``state.change`` payload (§7.1)."""

    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    ACTING = "acting"


class Event(StrEnum):
    """Server -> client notification methods (§7.1 events table).

    Only the members implemented so far are defined; later phases add their own.
    """

    STATE_CHANGE = "state.change"
    ERROR = "error"
    # Phase 1
    TOKEN = "token"
    TURN_COMPLETE = "turn.complete"
    # Phase 1.5: a provider died after streaming part of a reply, so the text
    # already on screen belongs to a model that is not going to finish. The
    # renderer discards it before the replacement starts streaming.
    TURN_RESET = "turn.reset"
    # Phase 2: one synthesised chunk, base64 int16 PCM. Emitted while the model
    # is still generating the next sentence — waiting for the whole reply is
    # what puts first audio past the budget (§9 Phase 2).
    AUDIO_OUT = "audio.out"
    # Stop playing and drop anything queued. Cancel uses it today; barge-in
    # reuses it in stage 3, which is why the flush lives here and not in cancel.
    AUDIO_STOP = "audio.stop"
    # Phase 2 stage 3: the transcript of a spoken turn, emitted before the turn
    # starts. The window learns what you said from the message it renders, but
    # the screen overlay has no transcript to render — this is how it knows.
    HEARD = "heard"
    # She has been called by name with no question attached, and is waiting to
    # be asked. The renderer chimes on this; the rim is already lit by the
    # `state.change` that accompanies it.
    WAKE = "wake"
    # Speech that was captured and then thrown away because it did not name
    # her. Surfaced rather than swallowed: 64 silent drops in one session were
    # indistinguishable from an app that had stopped working.
    MISHEARD = "misheard"
    # Someone started talking over her. Playback drops but does not stop,
    # because whether it was an interruption is not known until the utterance
    # has been transcribed — over a second later, all of it with her talking.
    AUDIO_DUCK = "audio.duck"
    # It was not an interruption after all. Back to full volume.
    AUDIO_RESUME = "audio.resume"


class Sender(Protocol):
    """Minimal transport surface — a Starlette WebSocket satisfies this."""

    async def send_text(self, data: str) -> None: ...


class EventBus:
    """Tracks connected clients and broadcasts notifications to them."""

    def __init__(self) -> None:
        self._clients: set[Sender] = set()
        self._state: AssistantState = AssistantState.IDLE

    @property
    def state(self) -> AssistantState:
        return self._state

    @property
    def client_count(self) -> int:
        return len(self._clients)

    def add(self, client: Sender) -> None:
        self._clients.add(client)
        log.info("rpc.client_connected", clients=len(self._clients))

    async def send_state_snapshot(self, client: Sender) -> None:
        """Send the current state to one client, unconditionally.

        A reconnecting renderer has no idea what state the sidecar is in, and
        :meth:`set_state` deliberately suppresses no-op changes — so a client
        that attaches while the state is unchanged would otherwise hear nothing.
        """
        payload = RpcNotification(
            method=str(Event.STATE_CHANGE), params={"state": str(self._state)}
        ).model_dump_json()
        await client.send_text(payload)

    def discard(self, client: Sender) -> None:
        self._clients.discard(client)
        log.info("rpc.client_disconnected", clients=len(self._clients))

    async def broadcast(self, method: Event | str, params: dict[str, Any]) -> None:
        """Send a notification to every live client, dropping dead ones."""
        payload = RpcNotification(method=str(method), params=params).model_dump_json()
        for client in list(self._clients):
            try:
                await client.send_text(payload)
            except Exception as exc:  # noqa: BLE001 — a dead socket must not stop the rest
                log.warning("rpc.push_failed", method=str(method), error=str(exc))
                self._clients.discard(client)

    async def set_state(self, state: AssistantState) -> None:
        """Update the assistant state and notify clients if it actually changed."""
        if state == self._state:
            return
        self._state = state
        await self.broadcast(Event.STATE_CHANGE, {"state": str(state)})

    async def send_error(self, code: str, message: str, *, recoverable: bool = True) -> None:
        await self.broadcast(
            Event.ERROR,
            {"code": code, "message": message, "recoverable": recoverable},
        )


bus = EventBus()
