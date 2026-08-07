"""Seeing and launching what is on the machine (BUILD_SPEC §9 Phase 3).

Two tools, at the two ends of the harmless range: listing windows changes
nothing at all, and launching an app changes something you can close again.

**Finding the app is the hard part, not starting it.** Measured against 28
names said the way a person actually says them, an earlier three-pass if-ladder
resolved 20 of the 24 that were installed, and all four failures were in the
matching: "7 zip" missed "7-Zip File Manager" over a hyphen, "seven zip" over a
number word, and "photoshp" and "youtbe music" over a single typo each. That
last one is what Eyaas typed unprompted, which is a fair sample of how names
actually arrive.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import StrEnum
from typing import Any

import structlog

from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

#: More than this in one reply is noise. The full list still goes to `display`.
LIST_SUMMARY_MAX = 12

# Spoken names whose executable is genuinely a different word. Applied as a
# *fallback*, never as a replacement: it used to rewrite the query before
# matching, so "terminal" became "wt", and when `wt` was not on PATH the real
# "Terminal" entry was never even considered. An alias could make matching
# worse than not having one.
_ALIASES = {
    "vs code": "code",
    "vscode": "code",
    "visual studio code": "code",
    "file explorer": "explorer",
    "calculator": "calc",
    "cmd": "cmd",
    "command prompt": "cmd",
}

# Things people say "open" about that are sites, not installed apps. Without
# this "open youtube" is a flat refusal, which is a strange answer from
# something sitting on a machine with a browser on it.
_SITES = {
    "youtube": "https://www.youtube.com",
    "youtube music": "https://music.youtube.com",
    "gmail": "https://mail.google.com",
    "google": "https://www.google.com",
    "maps": "https://maps.google.com",
    "google maps": "https://maps.google.com",
    "drive": "https://drive.google.com",
    "google drive": "https://drive.google.com",
    "github": "https://github.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "reddit": "https://reddit.com",
    "chatgpt": "https://chatgpt.com",
    "claude": "https://claude.ai",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.com",
    "linkedin": "https://www.linkedin.com",
    "whatsapp web": "https://web.whatsapp.com",
}

# "notion.so", "example.com" — said as a name, meant as a site.
_DOMAIN = re.compile(r"^[\w-]+(\.[\w-]+)+$")


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

    return ToolResult(ok=True, data=titles, summary=summary, display={"windows": windows})


# ── matching ─────────────────────────────────────────────────────────


class Launch(StrEnum):
    """How an entry has to be started. Three sources, three launchers."""

    #: `explorer.exe shell:AppsFolder\\<AppID>` — Store and Electron apps.
    APPS_FOLDER = "startapps"
    #: A real executable path.
    EXECUTABLE = "path"
    #: A URL, opened by whatever the default browser is.
    BROWSER = "browser"


@dataclass(frozen=True)
class AppEntry:
    label: str
    target: str
    launch: Launch


_NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}

_PUNCT = re.compile(r"[^a-z0-9]+")

# Start menus are full of entries that sit beside an app without being it.
# "7 zip" matched "7-Zip Help" over "7-Zip File Manager" purely because Help is
# the shorter name — nobody asking to open 7-Zip wants its documentation.
_NOT_THE_APP = frozenset(
    {
        "help",
        "uninstall",
        "uninstaller",
        "documentation",
        "docs",
        "readme",
        "manual",
        "website",
        "changelog",
        "support",
        "troubleshoot",
        "repair",
        "setup",
        "installer",
        "remove",
    }
)


def normalise(text: str) -> str:
    """Fold a name to the form both sides are compared in.

    Case, punctuation and number words all disappear, so "7-Zip File Manager"
    and "seven zip" meet in the middle at "7 zip …". Each of those was a real
    miss rather than a hypothetical one.
    """
    lowered = _PUNCT.sub(" ", text.lower()).strip()
    return " ".join(_NUMBER_WORDS.get(word, word) for word in lowered.split())


#: Below this, nothing matches. Without a floor a nonsense name always resolves
#: to *something*, and opening the wrong app is worse than opening nothing —
#: which "open youtube" launching YouTube Music already demonstrated.
MATCH_FLOOR = 0.55


def score(query: str, candidate: str) -> float:
    """How well `candidate` answers `query`, 0..1, over normalised text.

    The bands are ordered by how badly each can go wrong rather than by how
    clever it is: an exact name is certain, shared words are strong, a
    substring is weak, and edit distance is a last resort that exists only so
    a typo is not a dead end.
    """
    q, c = normalise(query), normalise(candidate)
    if not q or not c:
        return 0.0
    if q == c:
        return 1.0

    q_tokens, c_tokens = set(q.split()), set(c.split())

    # A "Help" or "Uninstall" entry is not the app, however well it matches.
    # Only demoted when the user did not ask for it: "uninstall steam" should
    # still find the uninstaller.
    aside = 0.25 if (c_tokens & _NOT_THE_APP) - q_tokens else 0.0

    if q_tokens and q_tokens <= c_tokens:
        # Every word said appears in the name. Extra words cost a little, so
        # "Calendar" stays ahead of "Calendar (Microsoft 365)".
        return 0.90 - min(len(c_tokens) - len(q_tokens), 5) * 0.02 - aside
    if c.startswith(q):
        return 0.80 - aside
    if q in c:
        return 0.70 - aside

    # Spaces removed on both sides, because people run names together as often
    # as not: "7zip" and "7 zip" are the same request.
    q_flat, c_flat = q.replace(" ", ""), c.replace(" ", "")
    if q_flat == c_flat:
        return 0.98 - aside
    if c_flat.startswith(q_flat):
        return 0.78 - aside
    if q_flat in c_flat:
        return 0.68 - aside

    # Typos, last. Compared against the whole name *and* against each run of
    # words in it, so "photoshp" can still reach "Adobe Photoshop 2023" — the
    # extra words would otherwise drown the similarity.
    ratio = _closest_ratio(q, c.split())
    return max(ratio - aside, 0.0) if ratio >= 0.75 else 0.0


def _closest_ratio(query: str, tokens: list[str]) -> float:
    """Best similarity between `query` and any contiguous run of `tokens`."""
    best_seen = SequenceMatcher(None, query, " ".join(tokens)).ratio()
    span = len(query.split())
    for size in (span, span + 1):
        for start in range(len(tokens) - size + 1):
            window = " ".join(tokens[start : start + size])
            best_seen = max(best_seen, SequenceMatcher(None, query, window).ratio())
    return best_seen


def rank(query: str, entries: list[AppEntry]) -> list[tuple[float, AppEntry]]:
    """Everything above the floor, best first, shortest label breaking ties."""
    hits = [(score(query, e.label), e) for e in entries]
    hits = [(s, e) for s, e in hits if s >= MATCH_FLOOR]
    hits.sort(key=lambda pair: (-pair[0], len(pair[1].label)))
    return hits


def best(query: str, entries: list[AppEntry], *, exact_only: bool = False) -> AppEntry | None:
    """The one entry to open, or None.

    `exact_only` preserves the ordering that stopped "open youtube" launching
    the YouTube Music app: an app named exactly this wins, then a website named
    exactly this, and only then an app that merely resembles it.
    """
    hits = rank(query, entries)
    if not hits:
        return None
    if exact_only and hits[0][0] < 1.0:
        return None
    return hits[0][1]


# ── the index ────────────────────────────────────────────────────────


def _start_apps() -> list[AppEntry]:
    """Everything in the Start menu.

    `Get-StartApps` is the only thing that knows about Store and Electron apps
    — Notion, Calendar, Spotify and most of what people actually name have no
    executable on PATH at all.
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
        AppEntry(str(item["Name"]), str(item["AppID"]), Launch.APPS_FOLDER)
        for item in parsed
        if item.get("Name") and item.get("AppID")
    ]


def _registered_executables() -> list[AppEntry]:
    """Executables registered under `App Paths`.

    Installers put things here that never get a Start menu shortcut, so this
    catches a class the Start menu alone misses. The key is the executable
    name; the label drops the extension, since nobody says "chrome dot e x e".
    """
    import winreg

    entries: list[AppEntry] = []
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            key = winreg.OpenKey(
                root, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
            )
        except OSError:
            continue
        with key:
            for index in range(winreg.QueryInfoKey(key)[0]):
                try:
                    name = winreg.EnumKey(key, index)
                    with winreg.OpenKey(key, name) as sub:
                        path, _ = winreg.QueryValueEx(sub, "")
                except OSError:
                    continue
                if not path:
                    continue
                label = name[:-4] if name.lower().endswith(".exe") else name
                entries.append(AppEntry(label, str(path).strip('"'), Launch.EXECUTABLE))
    return entries


def _build_index() -> list[AppEntry]:
    """Every source, merged. Start menu first so its friendlier labels win."""
    entries = _start_apps()
    seen = {normalise(e.label) for e in entries}
    for entry in _registered_executables():
        key = normalise(entry.label)
        if key not in seen:
            seen.add(key)
            entries.append(entry)
    log.info("apps.indexed", count=len(entries))
    return entries


class _AppIndex:
    """The merged list, fetched at most once until a lookup misses."""

    def __init__(self) -> None:
        self._entries: list[AppEntry] | None = None

    async def entries(self) -> list[AppEntry]:
        if self._entries is None:
            self._entries = await asyncio.to_thread(_build_index)
        return self._entries

    async def refresh(self) -> list[AppEntry]:
        """Rebuild. Called after a miss, in case it was installed since."""
        rebuilt = await asyncio.to_thread(_build_index)
        if rebuilt:
            self._entries = rebuilt
        return self._entries or []


_INDEX = _AppIndex()


def _resolve(name: str, entries: list[AppEntry]) -> AppEntry | None:
    """Pick what to open, in the order that has already been argued for.

    An app named exactly this, then a website named exactly this, then an app
    that resembles it. Swapping the middle two is what made "open youtube"
    launch the YouTube Music app.
    """
    query = name.strip()
    normalised = normalise(query)

    exact = best(query, entries, exact_only=True)
    if exact is not None:
        return exact

    if normalised in _SITES:
        return AppEntry(query, _SITES[normalised], Launch.BROWSER)
    if _DOMAIN.match(query.lower()):
        return AppEntry(query, f"https://{query.lower()}", Launch.BROWSER)

    fuzzy = best(query, entries)
    if fuzzy is not None:
        return fuzzy

    # Aliases last, so one can never hide a better match.
    alias = _ALIASES.get(normalised)
    if alias:
        return best(alias, entries)
    return None


async def _start(entry: AppEntry) -> None:
    """Run it, however this kind of thing has to be run."""
    if entry.launch is Launch.APPS_FOLDER:
        await asyncio.to_thread(
            subprocess.Popen, ["explorer.exe", "shell:AppsFolder\\" + entry.target]
        )
        return
    await asyncio.to_thread(os.startfile, entry.target)


@tool(
    name="open_app",
    tier=Tier.SAFE,
    description=(
        "Open an application or a website by name — for example chrome, "
        "notion, spotify, calculator, youtube, gmail. Use whenever the user "
        "asks to open, launch or start something. Pass the name exactly as "
        "they said it; do not substitute a different app you think is similar."
    ),
)
async def open_app(ctx: ToolContext, name: str) -> ToolResult:
    """Open an application or website.

    Args:
        name: What to open, as the user said it, e.g. "notion", "youtube"
    """
    wanted = name.strip()
    if not wanted:
        return ToolResult(ok=False, summary="Tell me what to open.", error="empty")

    # A real executable on PATH is the cheapest possible answer, and covers
    # notepad, chrome and code without touching the index.
    direct = await asyncio.to_thread(shutil.which, _ALIASES.get(normalise(wanted), wanted))
    if direct:
        try:
            await _start(AppEntry(wanted, direct, Launch.EXECUTABLE))
        except OSError as exc:
            return ToolResult(ok=False, summary=f"{wanted} would not start.", error=str(exc))
        log.info("tool.opened_app", name=wanted, via="path", target=direct)
        return ToolResult(
            ok=True, data={"name": wanted, "via": "path"}, summary=f"Opened {wanted}."
        )

    entries = await _INDEX.entries()
    entry = _resolve(wanted, entries)
    if entry is None:
        entries = await _INDEX.refresh()
        entry = _resolve(wanted, entries)

    if entry is None:
        # A dead end is useless to the model and to the user. Naming the near
        # misses lets either of them retry immediately.
        near = [e.label for _, e in rank(wanted, entries)[:3]] or [
            e.label for e in entries if normalise(wanted)[:3] in normalise(e.label)
        ][:3]
        hint = f" The closest I have are {', '.join(near)}." if near else ""
        return ToolResult(
            ok=False,
            summary=f"I could not find {wanted!r} on this machine.{hint}",
            error="not_found",
            display={"closest": near},
        )

    try:
        await _start(entry)
    except OSError as exc:
        return ToolResult(ok=False, summary=f"{entry.label} would not start.", error=str(exc))

    log.info("tool.opened_app", name=wanted, via=str(entry.launch), target=entry.target)
    where = " in your browser" if entry.launch is Launch.BROWSER else ""
    return ToolResult(
        ok=True,
        data={"name": entry.label, "via": str(entry.launch), "target": entry.target},
        summary=f"Opened {entry.label}{where}.",
    )
