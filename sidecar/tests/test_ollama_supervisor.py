"""Starting Ollama, and noticing when it comes back.

Eyaas: *"sometimes when ollama is off, the local models doesnt work, so when
i start aria itself ollama local models should also work."*

The second half is the one worth testing hardest. Ollama being down at
startup was always survivable; what was not is that **nothing ever retried**,
so `runtime.local_models` stayed empty for the life of the process and
starting Ollama by hand afterwards changed nothing at all.

No subprocess is spawned and nothing sleeps here: the spawn, the executable
lookup and the sleep are all injected, the same shape `MemoryScheduler` and
`ProactivityScheduler` already use for their clocks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from sidecar.providers.base import ProviderUnavailable
from sidecar.providers.ollama_supervisor import OllamaSupervisor

EXE = Path(r"C:\Users\Dark_Angel\AppData\Local\Programs\Ollama\ollama.exe")


class FakeOllama:
    """Reachability on a script: one entry per `available()` call, the last
    repeating forever."""

    def __init__(self, script: list[bool], models: list[str] | None = None) -> None:
        self._script = script
        self._models = models if models is not None else ["qwen2.5:7b"]
        self.probes = 0

    async def available(self) -> bool:
        answer = self._script[min(self.probes, len(self._script) - 1)]
        self.probes += 1
        return answer

    async def list_models(self) -> list[str]:
        return list(self._models)


def _supervisor(provider: Any, **kwargs: Any) -> tuple[OllamaSupervisor, list[Path]]:
    spawned: list[Path] = []

    async def _no_sleep(_s: float) -> None:
        return None

    supervisor = OllamaSupervisor(
        provider,
        find=kwargs.pop("find", lambda: EXE),
        spawn=lambda exe: spawned.append(exe),
        sleep=_no_sleep,
        **kwargs,
    )
    return supervisor, spawned


async def test_it_starts_ollama_when_it_is_down() -> None:
    """Down on the first probe, up once it has been started."""
    provider = FakeOllama([False, True])
    supervisor, spawned = _supervisor(provider)

    assert await supervisor.ensure_running()
    assert spawned == [EXE]


async def test_it_does_not_start_a_second_one_when_it_is_already_up() -> None:
    """The precedent `electron/sidecar.ts` already sets for the sidecar
    itself: adopt a running instance rather than spawn a duplicate. A second
    `ollama serve` would lose the bind race and exit, but racing at all is
    worth avoiding — and on this machine Ollama is usually already running.
    """
    provider = FakeOllama([True])
    supervisor, spawned = _supervisor(provider)

    assert await supervisor.ensure_running()
    assert spawned == [], "nothing was launched over a working daemon"


async def test_it_gives_up_rather_than_waiting_forever() -> None:
    """A spawn that never becomes reachable has to end. The sidecar stays up
    either way — Ollama being unavailable is a state the UI reports, not a
    crash."""
    provider = FakeOllama([False])
    supervisor, spawned = _supervisor(provider, start_timeout_s=2.0)

    assert not await supervisor.ensure_running()
    assert spawned == [EXE]


async def test_a_missing_ollama_is_reported_once_and_never_raises() -> None:
    """Not installed is a real state, and it must not crash the sidecar or
    fill the log with the same line every 20 seconds."""
    provider = FakeOllama([False])
    supervisor, spawned = _supervisor(provider, find=lambda: None)

    assert not await supervisor.ensure_running()
    assert not await supervisor.ensure_running()
    assert spawned == []


async def test_autostart_off_probes_but_never_launches() -> None:
    """Somebody running Ollama on another machine, or keeping it off on
    purpose, still wants the probe — just not the launch."""
    provider = FakeOllama([False])
    supervisor, spawned = _supervisor(provider, autostart=False)

    assert not await supervisor.ensure_running()
    assert spawned == []


async def test_local_models_are_re_armed_when_ollama_comes_back() -> None:
    """**The bug this whole file exists for.** Coming back up is worth
    nothing on its own: `local_models` is what the picker greys out against
    and what the router checks before choosing a local model, and it was
    written once at startup and never again.
    """
    provider = FakeOllama([True], models=["qwen2.5:7b", "nomic-embed-text"])
    arrived: list[list[str]] = []

    async def _on_ready(models: list[str]) -> bool:
        arrived.append(models)
        return True

    supervisor, _ = _supervisor(provider, on_ready=_on_ready)

    await supervisor.tick()

    assert arrived == [["qwen2.5:7b", "nomic-embed-text"]]


async def test_it_re_arms_only_on_the_transition_not_every_tick() -> None:
    """Ollama stays up for hours. Re-listing its models every 20 seconds
    would be a pointless HTTP call on a loop."""
    provider = FakeOllama([True])
    arrived: list[list[str]] = []

    async def _on_ready(models: list[str]) -> bool:
        arrived.append(models)
        return True

    supervisor, _ = _supervisor(provider, on_ready=_on_ready)

    await supervisor.tick()
    await supervisor.tick()
    await supervisor.tick()

    assert len(arrived) == 1


async def test_it_re_arms_again_after_ollama_drops_and_returns() -> None:
    """Killing Ollama mid-session and starting it again is exactly the case
    Eyaas hit. The second recovery has to work as well as the first."""
    provider = FakeOllama([True, False, False, True])
    arrived: list[list[str]] = []

    async def _on_ready(models: list[str]) -> bool:
        arrived.append(models)
        return True

    supervisor, _ = _supervisor(provider, autostart=False, on_ready=_on_ready)

    await supervisor.tick()  # up
    await supervisor.tick()  # down
    await supervisor.tick()  # still down
    await supervisor.tick()  # back

    assert len(arrived) == 2


async def test_a_failing_list_models_does_not_kill_the_tick() -> None:
    """`tick` never raises, for the same reason `MemoryScheduler.tick` does
    not: a supervisor that dies takes the thing it supervises with it."""

    class Flaky(FakeOllama):
        async def list_models(self) -> list[str]:
            raise ProviderUnavailable("gone")

    async def _on_ready(models: list[str]) -> bool:
        raise AssertionError("should not be reached")

    supervisor, _ = _supervisor(Flaky([True]), on_ready=_on_ready)

    await supervisor.tick()

    assert supervisor.running is True


async def test_a_spawn_that_raises_is_reported_not_propagated() -> None:
    provider = FakeOllama([False])

    def _boom(_exe: Path) -> None:
        raise OSError("access denied")

    async def _no_sleep(_s: float) -> None:
        return None

    supervisor = OllamaSupervisor(
        cast("Any", provider),
        find=lambda: EXE,
        spawn=_boom,
        sleep=_no_sleep,
        start_timeout_s=1.0,
    )

    assert not await supervisor.ensure_running()


async def test_running_is_unknown_until_the_first_tick() -> None:
    """Not False. "We have not looked yet" and "it is down" are different
    things to show a user, the same distinction `Connectivity` draws."""
    supervisor, _ = _supervisor(FakeOllama([True]))

    assert supervisor.running is None
    await supervisor.tick()
    assert supervisor.running is True


async def test_a_daemon_we_just_started_is_re_armed_even_though_it_never_looked_down() -> None:
    """Found live. Killing Ollama mid-session and having the supervisor
    restart it inside a single tick leaves `running` True the whole way
    through — no transition, so the old code re-armed nothing. But a freshly
    started daemon holds **no model**, and the next turn would pay the 8-15s
    cold start §12 exists to keep the user away from.
    """
    # Down on the first probe of the tick, up once it has been started.
    provider = FakeOllama([False, True])
    arrived: list[list[str]] = []

    async def _on_ready(models: list[str]) -> bool:
        arrived.append(models)
        return True

    supervisor, spawned = _supervisor(provider, on_ready=_on_ready)
    supervisor._up = True  # noqa: SLF001 — it was up as far as anyone outside knew

    await supervisor.tick()

    assert spawned == [EXE]
    assert arrived, "a restarted daemon is empty, and something has to reload it"


async def test_an_untouched_running_daemon_is_not_re_armed() -> None:
    """The other half: `_started_one` must not latch. Ollama stays up for
    hours, and re-listing plus re-warming every 20 seconds would be a model
    load on a loop — squarely against rule 2."""
    provider = FakeOllama([True])
    arrived: list[list[str]] = []

    async def _on_ready(models: list[str]) -> bool:
        arrived.append(models)
        return True

    supervisor, _ = _supervisor(provider, on_ready=_on_ready)

    await supervisor.tick()  # the first, transitional one
    await supervisor.tick()
    await supervisor.tick()

    assert len(arrived) == 1


async def test_the_startup_probe_stops_the_first_tick_double_warming() -> None:
    """Found by reading the live log, not by a test. `_start_conversation`
    calls `ensure_running()` and then warms the local model; the supervisor's
    own first tick then saw `running` go None -> True, read that as a
    recovery, and warmed it a second time. Two model loads eleven seconds
    apart, for nothing — and on a 6GB card model loads are not free (rule 2).
    """
    provider = FakeOllama([True])
    arrived: list[list[str]] = []

    async def _on_ready(models: list[str]) -> bool:
        arrived.append(models)
        return True

    supervisor, _ = _supervisor(provider, on_ready=_on_ready)

    # What startup does, before the loop is running.
    assert await supervisor.ensure_running()
    assert supervisor.running is True, "the startup probe seeds the state"

    await supervisor.tick()

    assert arrived == [], "startup already warmed it; the first tick must not repeat that"


async def test_a_failed_warm_is_retried_on_the_next_tick() -> None:
    """Measured on a real cold start: Ollama answers `/api/tags` before it
    can answer `/api/chat`, so the warm fired the moment it looked reachable
    came back 500 — and the model stayed cold, which is precisely the 8-15s
    §12 says the user must never hit. Reachable is not the same as ready, so
    the re-arm retries until it actually lands.
    """
    provider = FakeOllama([True])
    attempts: list[list[str]] = []

    async def _flaky(models: list[str]) -> bool:
        attempts.append(models)
        return len(attempts) >= 3  # the first two 500, as observed

    supervisor, _ = _supervisor(provider, on_ready=_flaky)

    await supervisor.tick()
    await supervisor.tick()
    await supervisor.tick()
    await supervisor.tick()

    assert len(attempts) == 3, "it kept trying until the warm took, then stopped"
