"""Seeing and launching what is on the machine (BUILD_SPEC §9 Phase 3).

Two tools, at the two ends of the harmless range: listing windows changes
nothing at all, and launching an app changes something you can close again.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
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


def _start_apps() -> list[tuple[str, str]]:
    """Everything in the Start menu, as (name, AppID).

    `Get-StartApps` is the only thing that knows about Store and Electron apps
    — Notion, Calendar, Calculator and most of what people actually name are
    not executables on PATH, which is why the first version of this tool could
    only open things like notepad.

    Costs most of a second, so it is cached. A miss refreshes it once, on the
    theory that the app was probably installed since we last looked.
    """
    completed = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            "Get-StartApps | ConvertTo-Json -Compress",
        ],
        capture_output=True,
        text=True,
        timeout=20,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        return []

    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        parsed = [parsed]
    return [
        (str(item.get("Name", "")), str(item.get("AppID", "")))
        for item in parsed
        if item.get("Name") and item.get("AppID")
    ]


def _best_match(wanted: str, apps: list[tuple[str, str]]) -> tuple[str, str] | None:
    """Pick the app a person meant.

    Exact name first, then prefix, then substring — and the *shortest* name
    among equals, so "Calendar" wins over "Calendar (Microsoft 365)". Ordering
    matters here: matching on substring first would open "Calculator Help"
    ahead of "Calculator".
    """
    lowered = wanted.lower()
    for test in (
        lambda n: n == lowered,
        lambda n: n.startswith(lowered),
        lambda n: lowered in n,
    ):
        hits = [(name, app_id) for name, app_id in apps if test(name.lower())]
        if hits:
            return min(hits, key=lambda pair: len(pair[0]))
    return None


class _AppIndex:
    """The Start menu list, fetched at most once until a lookup misses."""

    def __init__(self) -> None:
        self._apps: list[tuple[str, str]] | None = None

    async def find(self, wanted: str) -> tuple[str, str] | None:
        if self._apps is None:
            self._apps = await asyncio.to_thread(_start_apps)
        match = _best_match(wanted, self._apps)
        if match is not None:
            return match

        # Missed. It may have been installed since we last looked.
        refreshed = await asyncio.to_thread(_start_apps)
        if refreshed:
            self._apps = refreshed
        return _best_match(wanted, self._apps)


_INDEX = _AppIndex()


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

    # Fast path: a real executable on PATH. Cheap, and covers chrome and code.
    resolved = await asyncio.to_thread(shutil.which, target)
    if resolved:
        try:
            await asyncio.to_thread(os.startfile, resolved)
        except OSError as exc:
            return ToolResult(ok=False, summary=f"{name} would not start.", error=str(exc))
        log.info("tool.opened_app", name=name, via="path", target=resolved)
        return ToolResult(ok=True, data={"name": name, "via": "path"}, summary=f"Opened {name}.")

    # Everything else people actually name — Notion, Calendar, Calculator,
    # Spotify — is a Store or Electron app with no executable on PATH.
    match = await _INDEX.find(target)
    if match is None:
        return ToolResult(
            ok=False,
            summary=(
                f"I could not find an app called {name!r} on this machine. "
                f"Check the name as it appears in the Start menu."
            ),
            error="not_found",
        )

    label, app_id = match
    try:
        # `shell:AppsFolder\<AppID>` is the one launcher that handles Store
        # apps, and it has to go through explorer.
        await asyncio.to_thread(
            subprocess.Popen,
            ["explorer.exe", "shell:AppsFolder\\" + app_id],
        )
    except OSError as exc:
        return ToolResult(ok=False, summary=f"{label} would not start.", error=str(exc))

    log.info("tool.opened_app", name=name, via="startapps", app_id=app_id)
    return ToolResult(
        ok=True,
        data={"name": label, "app_id": app_id, "via": "startapps"},
        summary=f"Opened {label}.",
    )
