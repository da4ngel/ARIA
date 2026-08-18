"""Facts about the machine, and the one knob she can turn on it.

`get_system_info` reads; `set_volume` writes something you can immediately
write back. Neither can lose anything, which is why both sit at the bottom of
the tier scale.
"""

from __future__ import annotations

import asyncio
import contextlib
import subprocess
from typing import Any

import structlog

from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)


def _endpoint_volume() -> Any:
    """The default output device's volume interface.

    COM has to be initialised on the thread that talks to it, and this runs in
    a worker thread — so it is initialised here rather than once at startup.

    `AudioDevice.EndpointVolume` rather than the `Activate(IID, CLSCTX, None)`
    dance every example on the internet still shows: pycaw wraps the device
    now, and the raw COM call fails with `'AudioDevice' object has no attribute
    'Activate'`.
    """
    import comtypes
    from pycaw.pycaw import AudioUtilities

    comtypes.CoInitialize()
    return AudioUtilities.GetSpeakers().EndpointVolume


def _read_volume() -> int:
    volume = _endpoint_volume()
    scalar: float = volume.GetMasterVolumeLevelScalar()
    return round(scalar * 100)


def _write_volume(percent: int) -> None:
    volume = _endpoint_volume()
    # Scalar, not decibels: `SetMasterVolumeLevel` takes dB and is logarithmic,
    # so "30" there is nowhere near where a person means by 30%.
    volume.SetMasterVolumeLevelScalar(percent / 100, None)


def _facts() -> dict[str, Any]:
    import platform

    import psutil

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")
    # Volume belongs here because `set_volume` used to be the only way to learn
    # it, and `set_volume` is a write. A model asked to "turn it up" had nowhere
    # to read the current level from and had to guess one.
    try:
        volume: int | None = _read_volume()
    except Exception:  # noqa: BLE001 — a machine with no audio device is normal
        volume = None
    return {
        "os": f"{platform.system()} {platform.release()}",
        "volume_percent": volume,
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "cpu_cores": psutil.cpu_count(logical=False),
        "ram_used_gb": round((memory.total - memory.available) / 1e9, 1),
        "ram_total_gb": round(memory.total / 1e9, 1),
        "disk_free_gb": round(disk.free / 1e9, 1),
        "disk_total_gb": round(disk.total / 1e9, 1),
        "battery_percent": (
            round(psutil.sensors_battery().percent) if psutil.sensors_battery() else None
        ),
    }


@tool(
    name="get_system_info",
    tier=Tier.AUTO,
    description=(
        "Read this computer's current state: CPU load, memory in use, free "
        "disk space and battery. Use when asked how the machine is doing, "
        "whether it is running out of space, or what the specs are."
    ),
)
async def get_system_info(ctx: ToolContext) -> ToolResult:
    """Read CPU, memory, disk and battery."""
    facts = await asyncio.to_thread(_facts)

    battery = (
        f", battery {facts['battery_percent']}%" if facts["battery_percent"] is not None else ""
    )
    volume = (
        f", volume {facts['volume_percent']}%"
        if facts["volume_percent"] is not None
        else ""
    )
    summary = (
        f"CPU {facts['cpu_percent']}%, "
        f"RAM {facts['ram_used_gb']}/{facts['ram_total_gb']}GB, "
        f"disk {facts['disk_free_gb']}GB free of {facts['disk_total_gb']}GB"
        f"{battery}{volume}."
    )
    return ToolResult(ok=True, data=facts, summary=summary, display=facts)


#: How far "up" and "down" move. Ten is too little to hear across a room and
#: twenty-five overshoots; this is one comfortable press of a volume key.
VOLUME_STEP = 15

_DIRECTIONS = {
    "up": VOLUME_STEP,
    "louder": VOLUME_STEP,
    "increase": VOLUME_STEP,
    "raise": VOLUME_STEP,
    "down": -VOLUME_STEP,
    "quieter": -VOLUME_STEP,
    "lower": -VOLUME_STEP,
    "decrease": -VOLUME_STEP,
    "reduce": -VOLUME_STEP,
}


@tool(
    name="set_volume",
    tier=Tier.SAFE,
    description=(
        "Change the system output volume. Give `percent` for an exact level "
        "(0-100), or `direction` for a relative change: 'up', 'down', 'mute' "
        "or 'unmute'. Use direction when the user says 'louder', 'turn it "
        "down', 'increase the volume' — anything without a number in it."
    ),
)
async def set_volume(
    ctx: ToolContext, percent: int | None = None, direction: str | None = None
) -> ToolResult:
    """Set or nudge the system volume.

    Args:
        percent: An exact level, 0 (silent) to 100 (loudest). Omit for a
            relative change.
        direction: "up", "down", "mute" or "unmute". Omit when giving a percent.
    """
    # **"Increase the volume" used to be impossible to answer.** `percent` was
    # required and absolute, nothing exposed the current level, and the
    # description invited exactly the relative phrasing the schema refused — so
    # the model had to invent a number blind. The cloud models guessed a
    # plausible 70 and looked right; qwen2.5:7b sent "up" and failed. It was
    # read as a routing problem for a week. It was this.
    try:
        was = await asyncio.to_thread(_read_volume)
    except Exception as exc:  # noqa: BLE001 — no audio device is a normal state
        return ToolResult(
            ok=False,
            summary="I could not reach the audio device to change the volume.",
            error=str(exc),
        )

    wanted, failure = _target(was, percent, direction)
    if failure is not None:
        return failure

    try:
        await asyncio.to_thread(_write_volume, wanted)
    except Exception as exc:  # noqa: BLE001
        return ToolResult(
            ok=False,
            summary="I could not reach the audio device to change the volume.",
            error=str(exc),
        )

    log.info("tool.volume", was=was, now=wanted, direction=direction)
    if wanted == was:
        edge = "already at 100%" if wanted == 100 else "already silent"
        return ToolResult(
            ok=True, data={"was": was, "now": wanted}, summary=f"Volume {edge}."
        )
    return ToolResult(
        ok=True,
        data={"was": was, "now": wanted},
        summary=f"Volume {was}% to {wanted}%.",
    )


def _target(
    was: int, percent: int | None, direction: str | None
) -> tuple[int, ToolResult | None]:
    """Resolve the requested volume against the current one."""
    if direction is not None:
        word = str(direction).strip().lower().lstrip("+")
        if word in {"mute", "silent", "off"}:
            return (0, None)
        if word in {"unmute", "on"}:
            # Unmuting from silence has to land somewhere audible; restoring the
            # pre-mute level would need state this tool does not keep.
            return (max(was, 30), None)
        if word in _DIRECTIONS:
            return (max(0, min(100, was + _DIRECTIONS[word])), None)
        return (
            was,
            ToolResult(
                ok=False,
                summary=(
                    f"I don't know what volume {direction!r} means. "
                    "Use 'up', 'down', 'mute' or 'unmute', or give a number."
                ),
                error="direction",
            ),
        )

    if percent is None:
        return (
            was,
            ToolResult(
                ok=False,
                summary=(
                    f"Volume is {was}%. Tell me a level from 0 to 100, "
                    "or say up or down."
                ),
                error="no_target",
            ),
        )

    try:
        # The model sometimes sends "thirty" or "30%" rather than a number.
        asked = int(str(percent).strip().rstrip("%"))
    except (TypeError, ValueError):
        return (
            was,
            ToolResult(
                ok=False,
                summary=f"{percent!r} is not a volume. Give me a number from 0 to 100.",
                error="type",
            ),
        )
    return (max(0, min(100, asked)), None)


# ── processes ────────────────────────────────────────────────────────


#: More than this in one reply is a wall of text nobody reads. The full list
#: still goes to `display` (§7.2).
PROCESS_SUMMARY_MAX = 10

#: Killing any of these takes Windows down with it — `lsass` bluescreens the
#: machine outright. Being allowed to *ask* is not the same as it being sane to
#: permit, so these are refused below the tier system rather than by it.
_NEVER_KILL = frozenset(
    {
        "system",
        "system idle process",
        "registry",
        "smss",
        "csrss",
        "wininit",
        "winlogon",
        "services",
        "lsass",
        "svchost",
        "dwm",
        "explorer",
    }
)


@tool(
    name="list_processes",
    tier=Tier.AUTO,
    description=(
        "List the programs using the most memory right now. Use when asked "
        "what is running, what is slowing the machine down, or how much "
        "memory something is using."
    ),
)
async def list_processes(ctx: ToolContext) -> ToolResult:
    """List the heaviest running processes."""
    import psutil

    def _read() -> list[dict[str, Any]]:
        found: dict[str, dict[str, Any]] = {}
        for proc in psutil.process_iter(["name", "memory_info", "pid"]):
            try:
                name = proc.info["name"]
                memory = proc.info["memory_info"]
                if not name or memory is None:
                    continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            # Chrome is forty processes; a person means "Chrome". Grouped by
            # name, because per-pid rows answer a question nobody asked.
            entry = found.setdefault(name, {"name": name, "mb": 0.0, "count": 0, "pid": 0})
            entry["mb"] += memory.rss / 1_048_576
            entry["count"] += 1
            entry["pid"] = entry["pid"] or proc.info["pid"]
        ranked = sorted(found.values(), key=lambda p: -float(p["mb"]))
        for entry in ranked:
            entry["mb"] = round(float(entry["mb"]), 1)
        return ranked

    processes = await asyncio.to_thread(_read)
    if not processes:
        return ToolResult(ok=False, summary="I could not read the process list.", error="empty")

    shown = processes[:PROCESS_SUMMARY_MAX]
    parts = [
        f"{p['name']} {p['mb']:.0f}MB" + (f" ({p['count']})" if p["count"] > 1 else "")
        for p in shown
    ]
    return ToolResult(
        ok=True,
        data=shown,
        summary=f"Heaviest {len(shown)} of {len(processes)}: " + ", ".join(parts),
        display={"processes": processes},
    )


@tool(
    name="kill_process",
    tier=Tier.CONFIRM,
    description=(
        "Force a program to quit. Use only when the user asks to kill, end or "
        "force-quit something that is stuck. Unsaved work in it is lost."
    ),
)
async def kill_process(ctx: ToolContext, name: str) -> ToolResult:
    """Force a program to quit.

    Args:
        name: The program's name, e.g. "notepad" or "chrome"
    """
    import os

    import psutil

    wanted = name.strip().lower().removesuffix(".exe")
    if not wanted:
        return ToolResult(ok=False, summary="Tell me which program.", error="empty")
    if wanted in _NEVER_KILL:
        return ToolResult(
            ok=False,
            summary=f"{name} is part of Windows. Killing it would take the machine down.",
            error="protected",
        )

    def _kill() -> tuple[int, list[str]]:
        killed: list[str] = []
        targets = []
        for proc in psutil.process_iter(["name", "pid"]):
            try:
                proc_name = (proc.info["name"] or "").lower().removesuffix(".exe")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            # Never the sidecar. Ending our own process mid-tool would look
            # exactly like a crash, and nothing would be there to say why.
            if proc.info["pid"] == os.getpid():
                continue
            if proc_name == wanted:
                targets.append(proc)

        for proc in targets:
            try:
                # Ask first. `terminate` is WM_CLOSE-like on Windows; `kill` is
                # the one that discards unsaved work without asking.
                proc.terminate()
                killed.append(proc.info["name"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        gone, alive = psutil.wait_procs(targets, timeout=3)
        for proc in alive:
            with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                proc.kill()
        return len(gone) + len(alive), killed

    count, killed = await asyncio.to_thread(_kill)
    if not killed:
        return ToolResult(ok=False, summary=f"{name} is not running.", error="not_running")

    log.info("tool.killed_process", name=wanted, count=count)
    plural = "es" if count != 1 else ""
    return ToolResult(
        ok=True,
        data={"name": wanted, "count": count},
        summary=f"Ended {count} {killed[0]} process{plural}.",
    )


# ── the network, and a shell that can only look ──────────────────────


#: A read-only command that has not answered by now is not going to.
RUN_TIMEOUT_S = 20.0


async def _run(args: list[str]) -> tuple[int, str]:
    """Run a program with a fixed argument list. **Never through a shell.**

    `shell=True` would make every quoting bug a command-injection bug, and the
    strings here are partly composed by a language model.
    """

    def _call() -> tuple[int, str]:
        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT_S,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return completed.returncode, (completed.stdout or completed.stderr or "").strip()

    return await asyncio.to_thread(_call)


@tool(
    name="set_wifi",
    tier=Tier.CONFIRM,
    description=(
        "Turn the wireless adapter on or off. Use when asked to enable or "
        "disable wifi. Turning it off will disconnect the machine."
    ),
)
async def set_wifi(ctx: ToolContext, enabled: bool) -> ToolResult:
    """Enable or disable the wireless adapter.

    Args:
        enabled: True to turn wifi on, False to turn it off
    """
    # The adapter's name is read from the machine, never taken from the model:
    # `netsh` takes a name, and a name that arrives from a prompt is a value
    # somebody else could have chosen.
    code, output = await _run(["netsh", "interface", "show", "interface"])
    if code != 0:
        return ToolResult(ok=False, summary="I could not read the network adapters.", error=output)

    adapter: str | None = None
    for line in output.splitlines():
        name = line.strip().rsplit("  ", 1)[-1].strip()
        if "wi-fi" in name.lower() or "wireless" in name.lower():
            adapter = name
            break
    if adapter is None:
        return ToolResult(
            ok=False, summary="This machine has no wireless adapter.", error="no_adapter"
        )

    state = "enabled" if enabled else "disabled"
    code, output = await _run(
        ["netsh", "interface", "set", "interface", f"name={adapter}", f"admin={state}"]
    )
    if code != 0:
        # Changing an adapter needs elevation, and the sidecar does not have it.
        hint = " It needs administrator rights, which I do not have."
        return ToolResult(
            ok=False, summary=f"I could not turn wifi {'on' if enabled else 'off'}.{hint}",
            error=output or "netsh_failed",
        )

    log.info("tool.set_wifi", adapter=adapter, enabled=enabled)
    return ToolResult(
        ok=True,
        data={"adapter": adapter, "enabled": enabled},
        summary=f"Turned wifi {'on' if enabled else 'off'} ({adapter}).",
    )


# **This allowlist is the security boundary, not the tier.** A shell driven by
# a language model is the largest attack surface in the project: a prompt
# injected through a web page, a filename or a document would aim here first.
# So the tool cannot write, cannot chain, and cannot compose — it can only
# read state, and anything it does not recognise is refused rather than
# sanitised. Sanitising is where these things go wrong.
_ALLOWED_CMDLETS = frozenset(
    {
        "get-process",
        "get-service",
        "get-netadapter",
        "get-netipaddress",
        "get-netconnectionprofile",
        "get-volume",
        "get-psdrive",
        "get-computerinfo",
        "get-date",
        "get-hotfix",
        "get-winevent",
        "get-scheduledtask",
        "get-timezone",
        "get-culture",
        "get-host",
    }
)

#: Any of these and the whole string is refused. `|` alone would turn
#: `Get-Process` into `Get-Process | Stop-Process`, which is the entire point.
_SHELL_METACHARACTERS = set("|;&><$`(){}[]#\n\r\"'")


def powershell_refusal(command: str) -> str | None:
    """Why this command will not run, or None if it may.

    Split out from the tool so the table of attempted escapes can be tested
    directly. That table is the point of this module's tests.
    """
    text = command.strip()
    if not text:
        return "there is nothing to run"
    if set(text) & _SHELL_METACHARACTERS:
        return "it contains shell characters, and I only run plain read-only commands"
    first = text.split(" ", 1)[0].lower()
    if first not in _ALLOWED_CMDLETS:
        return (
            f"{first} is not one of the commands I am allowed to run. "
            "I can only read state, never change it"
        )
    return None


@tool(
    name="run_powershell",
    tier=Tier.SAFE,
    description=(
        "Run one read-only PowerShell command to inspect this machine — for "
        "example Get-Service, Get-NetIPAddress, Get-Volume. Only a fixed list "
        "of Get- commands is permitted; nothing that changes anything will run."
    ),
)
async def run_powershell(ctx: ToolContext, command: str) -> ToolResult:
    """Run one allowlisted read-only PowerShell command.

    Args:
        command: The command, e.g. "Get-Service" or "Get-NetIPAddress"
    """
    refusal = powershell_refusal(command)
    if refusal is not None:
        log.info("tool.powershell_refused", command=command[:120], why=refusal)
        return ToolResult(
            ok=False, summary=f"I will not run that: {refusal}.", error="not_allowed"
        )

    text = command.strip()
    # Arguments as a list, and `-Command` last, so the string is one argument
    # rather than something the launcher re-parses.
    code, output = await _run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", text]
    )
    if code != 0:
        return ToolResult(ok=False, summary=f"{text} failed: {output[:200]}", error=output[:400])

    log.info("tool.powershell", command=text)
    head = output[:800]
    return ToolResult(
        ok=True,
        data=head,
        summary=f"{text}:\n{head}" if head else f"{text} returned nothing.",
        display={"command": text, "output": output},
    )
