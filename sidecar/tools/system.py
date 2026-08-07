"""Facts about the machine, and the one knob she can turn on it.

`get_system_info` reads; `set_volume` writes something you can immediately
write back. Neither can lose anything, which is why both sit at the bottom of
the tier scale.
"""

from __future__ import annotations

import asyncio
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
    return {
        "os": f"{platform.system()} {platform.release()}",
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
    summary = (
        f"CPU {facts['cpu_percent']}%, "
        f"RAM {facts['ram_used_gb']}/{facts['ram_total_gb']}GB, "
        f"disk {facts['disk_free_gb']}GB free of {facts['disk_total_gb']}GB{battery}."
    )
    return ToolResult(ok=True, data=facts, summary=summary, display=facts)


@tool(
    name="set_volume",
    tier=Tier.SAFE,
    description=(
        "Set the system output volume to a percentage from 0 to 100. Use when "
        "asked to turn the volume up or down, mute, or set it to a level."
    ),
)
async def set_volume(ctx: ToolContext, percent: int) -> ToolResult:
    """Set the system volume.

    Args:
        percent: Volume from 0 (muted) to 100 (loudest)
    """
    try:
        asked = int(percent)
    except (TypeError, ValueError):
        # The model sometimes sends "thirty" or "30%" rather than a number.
        return ToolResult(
            ok=False,
            summary=f"{percent!r} is not a volume. Give me a number from 0 to 100.",
            error="type",
        )

    wanted = max(0, min(100, asked))
    try:
        was = await asyncio.to_thread(_read_volume)
        await asyncio.to_thread(_write_volume, wanted)
    except Exception as exc:  # noqa: BLE001 — no audio device is a normal state
        return ToolResult(
            ok=False,
            summary="I could not reach the audio device to change the volume.",
            error=str(exc),
        )

    log.info("tool.volume", was=was, now=wanted)
    clamped = " (clamped to the 0-100 range)" if wanted != asked else ""
    return ToolResult(
        ok=True,
        data={"was": was, "now": wanted},
        summary=f"Volume {was}% to {wanted}%{clamped}.",
    )
