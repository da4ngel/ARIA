"""Finding files by name (BUILD_SPEC §9 Phase 4a).

Two backends behind one function.

**Everything (voidtools) is the primary**, as §4 specifies: it keeps a live
index of every drive and answers in single-digit milliseconds over hundreds of
thousands of files. `es.exe` is its command line.

**A bounded scan is the fallback**, and it is deliberately narrow: Documents,
Desktop, Downloads and the home directory, depth-limited, skipping the
directories that make a filesystem walk hopeless. It exists because the whole
point of this — "say 'open cv' and get the latest CV" — cannot work at all
without *some* backend, and asking someone to install a program before the
feature does anything is a poor first impression. It is not a replacement:
whole-disk searches still want Everything, and the tool says so.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import structlog

from sidecar.tools.apps import score
from sidecar.tools.files import known_folder
from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

#: Where `es.exe` usually lives when it is not on PATH.
_ES_LOCATIONS = (
    Path("C:/Program Files/Everything/es.exe"),
    Path("C:/Program Files (x86)/Everything/es.exe"),
    Path(__file__).resolve().parent.parent.parent / "resources" / "bin" / "es.exe",
)

#: Roots the fallback will walk. Everywhere a person keeps things they name.
_SCAN_ROOTS = ("documents", "desktop", "downloads")

#: Never walked. These are where a filesystem scan goes to die.
_SKIP_DIRS = frozenset(
    {
        "node_modules",
        ".git",
        "venv",
        ".venv",
        "__pycache__",
        "appdata",
        "$recycle.bin",
        "system volume information",
        ".cache",
        "site-packages",
        "dist-info",
        ".next",
        "build",
        "target",
    }
)

#: Deep enough for how people actually organise; shallow enough to stay quick.
_MAX_DEPTH = 6
#: A hard stop, so a pathological tree cannot hang a turn.
_SCAN_BUDGET_S = 4.0


@dataclass(frozen=True)
class FoundFile:
    path: Path
    modified: float
    size: int

    @property
    def name(self) -> str:
        return self.path.name


def everything_path() -> Path | None:
    """Where `es.exe` is, or None if Everything is not installed."""
    on_path = shutil.which("es")
    if on_path:
        return Path(on_path)
    return next((p for p in _ES_LOCATIONS if p.is_file()), None)


def _search_everything(query: str, limit: int) -> list[FoundFile]:
    """Ask Everything. Returns [] if it is not installed or not running."""
    exe = everything_path()
    if exe is None:
        return []

    completed = subprocess.run(
        [
            str(exe),
            "-json",
            "-n",
            str(limit),
            # Sorting here rather than in Python: Everything has the index, and
            # "the most recent one" is most of what people mean.
            "-sort",
            "date-modified-descending",
            "-date-modified",
            "-size",
            query,
        ],
        capture_output=True,
        text=True,
        timeout=15,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        return []

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        log.warning("finder.bad_es_json", head=completed.stdout[:200])
        return []

    found: list[FoundFile] = []
    for item in payload.get("results", []):
        raw = Path(item.get("path", "")) / item.get("name", "")
        try:
            stat = raw.stat()
        except OSError:
            continue
        found.append(FoundFile(raw, stat.st_mtime, stat.st_size))
    return found


def _walk(root: Path, deadline: float) -> list[FoundFile]:
    """Everything under `root`, bounded by depth, junk directories and time."""
    found: list[FoundFile] = []
    stack: list[tuple[Path, int]] = [(root, 0)]

    while stack:
        if time.monotonic() > deadline:
            log.info("finder.scan_truncated", root=str(root), found=len(found))
            break
        current, depth = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            if depth < _MAX_DEPTH and entry.name.lower() not in _SKIP_DIRS:
                                stack.append((Path(entry.path), depth + 1))
                            continue
                        stat = entry.stat()
                        found.append(FoundFile(Path(entry.path), stat.st_mtime, stat.st_size))
                    except OSError:
                        continue
        except OSError:
            continue
    return found


def _search_scan(limit: int) -> list[FoundFile]:
    """The fallback: every file under the usual roots, unfiltered.

    Filtering happens in `search_files`, because the ranking wants to see all
    the candidates rather than a truncated prefix of them.
    """
    deadline = time.monotonic() + _SCAN_BUDGET_S
    found: list[FoundFile] = []
    seen: set[Path] = set()
    for name in _SCAN_ROOTS:
        root = known_folder(name)
        if root is None or not root.is_dir():
            continue
        for item in _walk(root, deadline):
            if item.path not in seen:
                seen.add(item.path)
                found.append(item)
    return found[: limit * 40]


class _Cache:
    """The fallback scan, kept for a short while.

    Walking three directory trees per question is wasteful when people ask two
    or three things in a row, and long enough to go stale is long enough to
    miss a file they just saved — so this is deliberately brief.
    """

    ttl_s = 45.0

    def __init__(self) -> None:
        self._files: list[FoundFile] = []
        self._at = 0.0

    async def files(self) -> list[FoundFile]:
        if time.monotonic() - self._at > self.ttl_s or not self._files:
            self._files = await asyncio.to_thread(_search_scan, 2000)
            self._at = time.monotonic()
        return self._files

    def clear(self) -> None:
        self._files, self._at = [], 0.0


_SCAN = _Cache()


# Words that carry no information about *which* file. "my cv" and "cv" are one
# request, and without stripping these the first returned nothing at all.
_FILLER = frozenset(
    {
        "my", "the", "a", "an", "that", "this", "some",
        "file", "files", "document", "documents", "doc",
        "please", "for", "me", "of", "latest", "recent", "last", "newest",
        # Verbs, because the model often passes the whole phrase through
        # rather than the noun it contains.
        "open", "show", "find", "get", "bring", "pull", "load", "up",
    }
)


def clean_query(query: str) -> str:
    """Drop the words that do not name anything.

    Everything left is what the file is actually called. If that removes the
    whole query the original is kept, since "the document" is at least a word
    to match on.
    """
    kept = [w for w in query.lower().split() if w.strip(".,?!") not in _FILLER]
    return " ".join(kept) or query


#: Below this a filename is not what was asked for. Same reasoning as the app
#: matcher: opening the wrong file is worse than opening none.
NAME_FLOOR = 0.55

#: How much a file's age counts against it. Recency is a tiebreaker, never the
#: whole answer — "the latest CV" still has to be a CV.
_RECENCY_WEIGHT = 0.25
_RECENT_DAYS = 90.0


def rank_files(query: str, files: list[FoundFile], limit: int = 20) -> list[FoundFile]:
    """Best matches first: how well the name fits, then how recent it is.

    The name scorer is `tools.apps.score`, unchanged. It was built for
    application names and a filename is the same problem — typos, punctuation,
    words run together — so reusing it costs nothing and keeps one set of
    behaviour to reason about.
    """
    wanted = clean_query(query)
    now = time.time()
    scored: list[tuple[float, FoundFile]] = []
    for item in files:
        stem = item.path.stem
        fit = max(score(wanted, stem), score(wanted, item.name))
        if fit < NAME_FLOOR:
            continue
        age_days = max(now - item.modified, 0) / 86400
        freshness = max(0.0, 1.0 - age_days / _RECENT_DAYS)
        scored.append((fit + freshness * _RECENCY_WEIGHT, item))

    scored.sort(key=lambda pair: -pair[0])
    return [item for _, item in scored[:limit]]


async def find_files(query: str, limit: int = 20) -> tuple[list[FoundFile], str]:
    """Search by name. Returns the matches and which backend answered."""
    if everything_path() is not None:
        results = await asyncio.to_thread(_search_everything, clean_query(query), limit * 10)
        if results:
            return rank_files(query, results, limit), "everything"

    return rank_files(query, await _SCAN.files(), limit), "scan"


# ── the tools ────────────────────────────────────────────────────────


def _describe(item: FoundFile) -> str:
    """One file, in the words a person would use about it."""
    age_days = (time.time() - item.modified) / 86400
    when = (
        "today"
        if age_days < 1
        else "yesterday"
        if age_days < 2
        else f"{int(age_days)} days ago"
        if age_days < 60
        else time.strftime("%b %Y", time.localtime(item.modified))
    )
    return f"{item.name} ({when})"


def _install_hint(backend: str) -> str:
    """Told once, where it is useful, rather than nagged about."""
    if backend == "everything":
        return ""
    return (
        " I only searched your Documents, Desktop and Downloads. "
        "Installing Everything from voidtools.com would let me search every "
        "drive, instantly."
    )


@tool(
    name="search_files",
    tier=Tier.AUTO,
    description=(
        "Find files on this computer by name. Use when asked where a file is, "
        "to list matching files, or to find something before doing anything "
        "with it. Returns the best matches, most relevant and recent first."
    ),
)
async def search_files(ctx: ToolContext, query: str, limit: int = 10) -> ToolResult:
    """Find files by name.

    Args:
        query: What to look for, e.g. "cv", "budget spreadsheet", "invoice"
        limit: How many results to return at most
    """
    wanted = query.strip()
    if not wanted:
        return ToolResult(ok=False, summary="Tell me what to look for.", error="empty")

    started = time.perf_counter()
    found, backend = await find_files(wanted, limit=max(1, min(limit, 50)))
    took = round((time.perf_counter() - started) * 1000)
    log.info("tool.searched", query=wanted, backend=backend, hits=len(found), took_ms=took)

    if not found:
        return ToolResult(
            ok=True,
            data=[],
            summary=f"I could not find anything called {wanted!r}.{_install_hint(backend)}",
            display={"backend": backend, "took_ms": took},
        )

    # One line for the model; the paths go to the UI (§7.2).
    listed = "; ".join(_describe(f) for f in found[:5])
    more = f", and {len(found) - 5} more" if len(found) > 5 else ""
    return ToolResult(
        ok=True,
        data=[str(f.path) for f in found],
        summary=f"Found {len(found)}: {listed}{more}.",
        display={
            "backend": backend,
            "took_ms": took,
            "files": [
                {"path": str(f.path), "name": f.name, "modified": f.modified, "size": f.size}
                for f in found
            ],
        },
    )


@tool(
    name="open_file",
    tier=Tier.SAFE,
    description=(
        "Find a file by name and open it. Use when asked to open a document "
        "the user names loosely rather than by full path — 'open my cv', "
        "'open the budget spreadsheet'. Opens the best and most recent match."
    ),
)
async def open_file(ctx: ToolContext, query: str) -> ToolResult:
    """Find a file by name and open it.

    Args:
        query: What to open, e.g. "cv", "the budget spreadsheet"
    """
    wanted = query.strip()
    if not wanted:
        return ToolResult(ok=False, summary="Tell me what to open.", error="empty")

    found, backend = await find_files(wanted, limit=8)
    if not found:
        return ToolResult(
            ok=False,
            summary=f"I could not find a file called {wanted!r}.{_install_hint(backend)}",
            error="not_found",
        )

    # Best guess, as decided for apps — but the alternatives are named, because
    # the wrong document opening silently is the failure worth avoiding.
    chosen = found[0]
    try:
        await asyncio.to_thread(os.startfile, str(chosen.path))
    except OSError as exc:
        return ToolResult(ok=False, summary=f"{chosen.name} would not open.", error=str(exc))

    log.info("tool.opened_file", path=str(chosen.path), backend=backend)
    others = (
        f" I also found {', '.join(f.name for f in found[1:3])}."
        if len(found) > 1
        else ""
    )
    return ToolResult(
        ok=True,
        data={"path": str(chosen.path), "backend": backend},
        summary=f"Opened {_describe(chosen)}.{others}",
        display={"chosen": str(chosen.path), "others": [str(f.path) for f in found[1:]]},
    )
