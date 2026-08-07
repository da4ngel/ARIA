"""Seeing and launching what is on the machine (BUILD_SPEC §9 Phase 3).

Two tools, at the two ends of the harmless range: listing windows changes
nothing at all, and launching an app changes something you can close again.
"""

from __future__ import annotations

import asyncio
import os
import shutil
from typing import Any

import structlog

from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

#: More than this in one reply is noise. The full list still goes to `display`.
LIST_SUMMARY_MAX = 12

# Friendly names people actually say, mapped to what Windows will start.
# Deliberately small: the fallback below handles anything on PATH or
# registered with the shell, so this only exists for the ones where the
# spoken name and the executable differ.
_ALIASES = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "vs code": "code",
    "vscode": "code",
    "visual studio code": "code",
    "explorer": "explorer",
    "file explorer": "explorer",
    "notepad": "notepad",
    "calculator": "calc",
    "terminal": "wt",
    "spotify": "spotify",
}


def _visible_windows() -> list[dict[str, Any]]:
    """Top-level windows with a title, which is as close to "what is running"
    as a person means when they ask.

    Every process with a message pump has windows; almost none of them are
    things a person would say they have open.
    """
    import win32gui

    found: list[dict[str, Any]] = []

    def visit(handle: int, _: Any) -> None:
        if not win32gui.IsWindowVisible(handle):
            return
        title = win32gui.GetWindowText(handle)
        if not title.strip():
            return
        found.append({"title": title, "handle": handle})

    win32gui.EnumWindows(visit, None)
    return found


@tool(
    name="list_windows",
    tier=Tier.AUTO,
    description=(
        "List the application windows currently open on screen. Use when asked "
        "what is running, what is open, or what the user is working on."
    ),
)
async def list_windows(ctx: ToolContext) -> ToolResult:
    """List open application windows."""
    windows = await asyncio.to_thread(_visible_windows)
    titles = [w["title"] for w in windows]

    if not titles:
        return ToolResult(ok=True, data=[], summary="Nothing is open.")

    shown = titles[:LIST_SUMMARY_MAX]
    more = len(titles) - len(shown)
    # One line for the model; the whole list goes to the UI (§7.2).
    summary = f"{len(titles)} windows open: " + "; ".join(shown)
    if more:
        summary += f"; and {more} more"

    return ToolResult(
        ok=True,
        data=titles,
        summary=summary,
        display={"windows": windows},
    )


@tool(
    name="open_app",
    tier=Tier.SAFE,
    description=(
        "Launch a Windows application by name, for example chrome, code, "
        "excel, notepad, spotify. Use when asked to open or start a program."
    ),
)
async def open_app(ctx: ToolContext, name: str) -> ToolResult:
    """Launch an application.

    Args:
        name: Application name or executable, e.g. "chrome", "code", "excel"
    """
    wanted = name.strip().lower()
    target = _ALIASES.get(wanted, wanted)

    # `shutil.which` first so a missing app is reported as a missing app,
    # rather than as a shell error the model has to interpret.
    resolved = await asyncio.to_thread(shutil.which, target)

    try:
        if resolved:
            await asyncio.to_thread(os.startfile, resolved)
        else:
            # Not on PATH, but the shell may still know it — Store apps and
            # registered protocols both live here.
            await asyncio.to_thread(os.startfile, target)
    except OSError as exc:
        return ToolResult(
            ok=False,
            summary=(
                f"I could not find an app called {name!r}. "
                f"Try the executable name, like 'chrome' or 'code'."
            ),
            error=str(exc),
        )

    log.info("tool.opened_app", name=name, target=target)
    return ToolResult(
        ok=True,
        data={"name": name, "target": target},
        summary=f"Opened {name}.",
    )
