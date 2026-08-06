"""Is this machine on the internet?

BUILD_SPEC §9.7 asks for "offline detection cached with a short TTL" and gives
the reason: probing the network per turn adds a round-trip to the very path
being optimised. So the probe runs on a timer in the background and the turn
path only ever reads the last answer.

This is not the same question as "can she browse the web" — she cannot, until
Phase 7. It is the difference between *"I have no tool for that"* and *"you are
offline"*, which are different things to tell someone.
"""

from __future__ import annotations

import asyncio
import contextlib

import httpx
import structlog

log = structlog.get_logger(__name__)

# Generates a 204 with an empty body and is designed for exactly this check, so
# it is a few hundred bytes rather than a page load.
PROBE_URL = "http://connectivitycheck.gstatic.com/generate_204"
PROBE_TIMEOUT_S = 3.0
PROBE_INTERVAL_S = 60.0


class Connectivity:
    """Cached reachability. Reads never block; the refresh is a background task."""

    def __init__(self, url: str = PROBE_URL, interval_s: float = PROBE_INTERVAL_S) -> None:
        self._url = url
        self._interval_s = interval_s
        self._task: asyncio.Task[None] | None = None
        # Assume online until proven otherwise: a first turn that lands before
        # the first probe should not tell the user they are offline on a guess.
        self._online = True

    @property
    def online(self) -> bool:
        """Last known state. Never probes, never awaits, never raises."""
        return self._online

    async def probe_once(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=PROBE_TIMEOUT_S) as client:
                response = await client.get(self._url)
            self._online = response.status_code < 500
        except Exception:  # noqa: BLE001 — any failure to reach it means offline
            self._online = False
        return self._online

    async def _loop(self) -> None:
        while True:
            was = self._online
            now = await self.probe_once()
            if now != was:
                log.info("connectivity.changed", online=now)
            await asyncio.sleep(self._interval_s)

    def start(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task
        self._task = None


connectivity = Connectivity()
