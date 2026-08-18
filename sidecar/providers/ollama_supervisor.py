"""Keep Ollama running, and notice when it comes back.

Eyaas: *"sometimes when ollama is off, the local models doesnt work, so when
i start aria itself ollama local models should also work."*

Both halves of that were real, and the second is the worse one. `main.py`'s
`_discover_local_models` catches the failure, sets `ollama_ready = False` and
returns `[]` — and **nothing ever retried**. `runtime.local_models` stayed
empty for the life of the process, so starting Ollama afterwards changed
nothing until ARIA itself was restarted. The only recovery was incidental:
opening the model picker re-probes (`rpc/handlers.py`'s `models.list`), which
nobody would think to do to fix a bug they cannot see.

**In the sidecar, not in Electron main.** Electron already supervises the
sidecar itself (`electron/sidecar.ts`) and that is the obvious place to copy
from — but `npm run sidecar` has to work standalone, because every gate
script in `scripts/` drives it directly with no Electron anywhere, and
CLAUDE.md rule 1 puts state here rather than in the shell. The sidecar is
also the only process that knows Ollama is unreachable.

The shape is `providers/connectivity.py`'s: a background task, an injected
interval, a probe that never raises, and cached state the turn path can read
without awaiting. The clock and the spawn are injected the same way
`memory/scheduler.py` and `persona/proactivity.py` inject theirs, so the
tests drive real logic with no subprocess and no sleeping.
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import shutil
import subprocess
from collections.abc import Awaitable, Callable
from pathlib import Path

import structlog

from sidecar.providers.base import ProviderError
from sidecar.providers.ollama import OllamaProvider

log = structlog.get_logger(__name__)

#: How often to re-probe. Long enough that a machine with Ollama
#: deliberately off is not paying for the question, short enough that
#: starting it by hand is noticed before the user gives up and restarts ARIA.
DEFAULT_INTERVAL_S = 20.0
#: How long to wait for a freshly spawned `ollama serve` to answer. Measured
#: cold on this machine at a few seconds; the ceiling is for a first run that
#: is also unpacking.
DEFAULT_START_TIMEOUT_S = 20.0
#: Between readiness polls while waiting for that.
_READY_POLL_S = 0.5

#: Where Ollama installs itself on Windows when it is not on PATH. The
#: per-user location first: that is what the official installer uses, and it
#: is where this machine's own copy is.
_KNOWN_PATHS = (
    r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe",
    r"%PROGRAMFILES%\Ollama\ollama.exe",
    r"%PROGRAMFILES(X86)%\Ollama\ollama.exe",
)


def find_ollama() -> Path | None:
    """The `ollama` executable, or None if it is not installed.

    PATH first, because that is both the common case and the one the user can
    fix. The known install locations are the fallback for a shell that was
    open before Ollama was installed and so never picked up the PATH change —
    a real and confusing state, because `ollama` works in a new terminal and
    not in the running app.
    """
    on_path = shutil.which("ollama")
    if on_path:
        return Path(on_path)
    for template in _KNOWN_PATHS:
        candidate = Path(os.path.expandvars(template))
        if "%" not in str(candidate) and candidate.is_file():
            return candidate
    return None


def _spawn_detached(exe: Path) -> None:
    """Start `ollama serve` as its own process, with no console window.

    Detached on purpose. Ollama outliving ARIA is the friendly behaviour —
    it is a service the user may well be using from a terminal too, and
    killing it on exit would be ARIA taking something away that it did not
    put there. It also means there is no child to reap.
    """
    creation = 0
    creation |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
    creation |= getattr(subprocess, "DETACHED_PROCESS", 0)
    subprocess.Popen(
        [str(exe), "serve"],
        creationflags=creation,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )


class OllamaSupervisor:
    """Starts Ollama if it is down, and re-arms local models when it returns."""

    def __init__(
        self,
        provider: OllamaProvider,
        *,
        autostart: bool = True,
        interval_s: float = DEFAULT_INTERVAL_S,
        start_timeout_s: float = DEFAULT_START_TIMEOUT_S,
        find: Callable[[], Path | None] = find_ollama,
        spawn: Callable[[Path], None] = _spawn_detached,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        on_ready: Callable[[list[str]], Awaitable[bool]] | None = None,
    ) -> None:
        self._provider = provider
        self._autostart = autostart
        self._interval_s = interval_s
        self._start_timeout_s = start_timeout_s
        self._find = find
        self._spawn = spawn
        self._sleep = sleep
        self._on_ready = on_ready
        self._task: asyncio.Task[None] | None = None
        #: Last known reachability. Starts unknown rather than False so the
        #: first transition is always logged.
        self._up: bool | None = None
        #: One log line when Ollama is not installed, not one per tick. A
        #: message repeated every 20 seconds is noise that hides everything
        #: around it.
        self._missing_reported = False
        #: Whether the last `ensure_running` actually launched Ollama, as
        #: opposed to finding it already up. A freshly started daemon holds
        #: **no model** — so the next turn would pay the 8-15s cold start
        #: §12 exists to keep the user away from, even though `running` never
        #: visibly changed. Observed live: killing Ollama mid-session and
        #: having it restarted inside a single tick left it up, correct, and
        #: cold.
        self._started_one = False
        #: Set when Ollama becomes usable, cleared only once the re-arm has
        #: actually succeeded. **`/api/tags` answering is not the same as
        #: "can run a model"** — measured on a cold start here, the daemon
        #: served `/api/tags` immediately while `/api/chat` still returned
        #: 500, so the warm failed and the model stayed cold for the user's
        #: first turn. Retrying on the next tick is what closes that.
        self._pending_rearm = False

    @property
    def running(self) -> bool | None:
        """Last known state. Never probes, never awaits, never raises."""
        return self._up

    async def ensure_running(self) -> bool:
        """Probe, start Ollama if it is down, and wait for it to answer.

        Returns whether it is reachable at the end, and records it — so the
        startup call seeds `running` and the supervisor's own first tick is
        not read as a transition. Without that seeding, startup warmed the
        local model and the first tick immediately warmed it again: two
        model loads eleven seconds apart, seen in the live log.
        """
        self._started_one = False
        if await self._provider.available():
            self._up = True
            return True
        if not self._autostart:
            self._up = False
            return False

        exe = self._find()
        if exe is None:
            if not self._missing_reported:
                self._missing_reported = True
                log.warning(
                    "ollama.not_installed",
                    fix="Install it from https://ollama.com/download, then restart ARIA.",
                )
            self._up = False
            return False

        log.info("ollama.starting", exe=str(exe))
        try:
            await asyncio.to_thread(self._spawn, exe)
        except OSError as exc:
            log.warning("ollama.start_failed", exe=str(exe), error=str(exc))
            self._up = False
            return False

        waited = 0.0
        while waited < self._start_timeout_s:
            await self._sleep(_READY_POLL_S)
            waited += _READY_POLL_S
            if await self._provider.available():
                log.info("ollama.started", took_s=round(waited, 1))
                self._started_one = True
                self._up = True
                return True

        log.warning("ollama.start_timed_out", after_s=self._start_timeout_s)
        self._up = False
        return False

    async def tick(self) -> None:
        """One pass. Never raises — a supervisor that dies takes the thing it
        was supervising with it, the same reasoning `MemoryScheduler.tick`
        already states.
        """
        try:
            await self._tick_once()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            log.warning("ollama.tick_failed", error=str(exc))

    async def _tick_once(self) -> None:
        # Read before, not after: `ensure_running` records the new state
        # itself, so sampling afterwards would compare a value to itself and
        # no transition would ever be seen.
        was = self._up
        up = await self.ensure_running()
        self._up = up
        if up != was:
            log.info("ollama.changed", running=up)
        # Re-arm on either "it came back" or "we just started it". The second
        # is not implied by the first: a daemon restarted inside one tick
        # never looked down from out here, but it is empty all the same.
        if not up:
            return
        if up != was or self._started_one:
            self._pending_rearm = True
        if not self._pending_rearm or self._on_ready is None:
            return

        # **This is the half that was missing entirely.** Coming back up is
        # worth nothing on its own — `runtime.local_models` is what the
        # picker and the router actually read, and it was populated once at
        # startup and never again.
        with contextlib.suppress(ProviderError):
            if await self._on_ready(await self._provider.list_models()):
                self._pending_rearm = False

    async def _loop(self) -> None:
        while True:
            await self.tick()
            await self._sleep(self._interval_s)

    def start(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._loop())
        log.info("ollama.supervisor_started", interval_s=self._interval_s)

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task
        self._task = None
