"""Tidying a folder, reversibly (§9 Phase 4c, §11).

The last unbuilt item of Phase 4, and the one that needed a protocol change
before it could exist at all.

**Three shapes this had to fit, none of them optional:**

1. *"Emits **one** batch confirmation"* (§7.2, BUILD_SPEC:481) — not thirty.
   Rule 5 says every destructive operation gets a confirmation round-trip;
   thirty dialogs to tidy Downloads is a feature nobody uses twice.
2. *"Include the full file list"* — and `confirm.request` had nowhere to put
   one. `Tool.preview` is that channel; see its docstring for why the tool
   could not simply show its own plan.
3. *"Undo restores exactly"* — so a manifest is written before the first file
   moves, not after the last.

**The plan the user approves is the plan that runs.** `preview` computes it,
stashes it, and the tool executes the stash. Recomputing after approval would
be a different plan whenever a file arrived in the meantime — the folder is
Downloads, so that is a browser away — and quietly moving a thirty-first file
nobody agreed to is precisely the failure a confirmation exists to prevent.

Deliberately narrow: files only, one level deep, no recursion into the
subfolders it creates. A tidy-up that reorganises what it has already
organised is impossible to reason about the second time you run it.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import shutil
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from sidecar.config import get_settings
from sidecar.tools.files import _refuse, _resolve, _scan_changed
from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

#: One confirmation covers this many moves, and no more. A plan bigger than a
#: person will read is a plan they approve without reading, which is the same
#: as no confirmation at all.
MAX_MOVES = 200
#: Shown in the dialog. The rest are counted, not listed.
PREVIEW_ROWS = 12
#: How long a previewed plan stays executable. Comfortably longer than the
#: 120s confirmation timeout, short enough that a plan cannot be replayed
#: against a folder that has moved on.
PLAN_TTL_S = 600.0

#: Where each extension goes under `by_type`. Lowercase, no leading dot.
_BY_TYPE: dict[str, str] = {
    **dict.fromkeys(
        ["pdf", "doc", "docx", "odt", "rtf", "txt", "md", "tex", "epub"], "Documents"
    ),
    **dict.fromkeys(["xls", "xlsx", "csv", "ods", "tsv"], "Spreadsheets"),
    **dict.fromkeys(["ppt", "pptx", "odp", "key"], "Presentations"),
    **dict.fromkeys(
        ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg", "heic", "tif", "tiff", "ico"],
        "Images",
    ),
    **dict.fromkeys(["mp4", "mov", "avi", "mkv", "wmv", "webm", "m4v", "flv"], "Video"),
    **dict.fromkeys(["mp3", "wav", "flac", "m4a", "aac", "ogg", "wma"], "Audio"),
    **dict.fromkeys(["zip", "rar", "7z", "tar", "gz", "bz2", "xz", "iso"], "Archives"),
    **dict.fromkeys(
        ["exe", "msi", "msix", "appx", "bat", "cmd", "ps1", "sh", "deb", "dmg"], "Installers"
    ),
    **dict.fromkeys(
        ["py", "js", "ts", "tsx", "jsx", "rs", "go", "java", "c", "cpp", "h", "cs",
         "rb", "php", "sql", "json", "yaml", "yml", "toml", "xml", "html", "css"],
        "Code",
    ),
    **dict.fromkeys(["ttf", "otf", "woff", "woff2"], "Fonts"),
}
_OTHER = "Other"

STRATEGIES = ("by_type", "by_date")

#: Never moved, whatever the strategy. Windows keeps state in some of these and
#: a browser is actively writing to others.
_SKIP_NAMES = frozenset({"desktop.ini", "thumbs.db", ".ds_store"})
_SKIP_SUFFIXES = (".tmp", ".crdownload", ".part", ".partial", ".!ut", ".lnk")


@dataclass(frozen=True)
class Move:
    source: Path
    destination: Path

    def as_json(self) -> dict[str, str]:
        return {"from": str(self.source), "to": str(self.destination)}


@dataclass(frozen=True)
class Plan:
    root: Path
    strategy: str
    moves: list[Move]
    skipped: int
    created_at: float

    @property
    def folders(self) -> list[str]:
        seen = {m.destination.parent.name for m in self.moves}
        return sorted(seen)


#: Previewed plans, keyed by folder+strategy. See the module docstring: this is
#: what makes "the plan you approved is the plan that runs" true.
_PLANS: dict[str, Plan] = {}


def clear_plans() -> None:
    """Forget every previewed plan. For tests, and for a fresh session."""
    _PLANS.clear()


def _key(root: Path, strategy: str) -> str:
    return hashlib.sha256(f"{root}|{strategy}".encode()).hexdigest()[:16]


def _bucket(entry: Path, strategy: str) -> str:
    if strategy == "by_date":
        stamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=UTC)
        return stamp.strftime("%Y-%m")
    suffix = entry.suffix.lower().lstrip(".")
    return _BY_TYPE.get(suffix, _OTHER)


def _skip(entry: Path, buckets: set[str]) -> bool:
    """Whether this entry is not ours to move."""
    name = entry.name.lower()
    if name in _SKIP_NAMES or name.startswith("."):
        return True
    if name.endswith(_SKIP_SUFFIXES):
        return True
    # A folder this tool created on an earlier run. Re-sorting its contents is
    # how "organise Downloads" twice produces Documents/Documents.
    return entry.name in buckets


def _unique(destination: Path, taken: set[Path]) -> Path:
    """A free name at `destination`, without ever overwriting.

    Rule 5 calls overwriting destructive, and a tidy-up that silently replaces
    `invoice.pdf` with a different `invoice.pdf` is the worst kind: it looks
    like it worked.
    """
    candidate = destination
    index = 1
    while candidate.exists() or candidate in taken:
        candidate = destination.with_name(f"{destination.stem} ({index}){destination.suffix}")
        index += 1
    return candidate


def build_plan(root: Path, strategy: str) -> Plan:
    """Work out what would move where. Reads the folder; changes nothing."""
    buckets = set(_BY_TYPE.values()) | {_OTHER}
    moves: list[Move] = []
    taken: set[Path] = set()
    skipped = 0

    for entry in sorted(root.iterdir()):
        if not entry.is_file():
            skipped += 1
            continue
        if _skip(entry, buckets):
            skipped += 1
            continue
        try:
            folder = _bucket(entry, strategy)
        except OSError:
            skipped += 1
            continue
        destination = _unique(root / folder / entry.name, taken)
        taken.add(destination)
        moves.append(Move(source=entry, destination=destination))
        if len(moves) >= MAX_MOVES:
            break

    return Plan(
        root=root,
        strategy=strategy,
        moves=moves,
        skipped=skipped,
        created_at=time.monotonic(),
    )


async def preview_organize(path: str, strategy: str = "by_type") -> dict[str, Any] | None:
    """What `organize_folder` would do, for the confirmation dialog.

    Runs before the user is asked, and stashes the plan so the answer they give
    applies to the plan they were shown.
    """
    root, refusal = _resolve(path)
    if root is None or not root.is_dir():
        return None
    if strategy not in STRATEGIES:
        return None

    plan = await asyncio.to_thread(build_plan, root, strategy)
    _PLANS[_key(root, strategy)] = plan
    return {
        "kind": "move_plan",
        "folder": str(root),
        "strategy": strategy,
        "count": len(plan.moves),
        "skipped": plan.skipped,
        "folders": plan.folders,
        "moves": [m.as_json() for m in plan.moves[:PREVIEW_ROWS]],
        "truncated": max(0, len(plan.moves) - PREVIEW_ROWS),
    }


def _take_plan(root: Path, strategy: str) -> Plan | None:
    plan = _PLANS.pop(_key(root, strategy), None)
    if plan is None or time.monotonic() - plan.created_at > PLAN_TTL_S:
        return None
    return plan


def _write_manifest(plan: Plan, moved: list[Move]) -> Path:
    """Record how to put everything back, before anything is put anywhere."""
    undo_dir = get_settings().undo_dir
    undo_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    manifest = undo_dir / f"organize-{stamp}.json"
    manifest.write_text(
        json.dumps(
            {
                "operation": "organize_folder",
                "folder": str(plan.root),
                "strategy": plan.strategy,
                "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "moves": [m.as_json() for m in moved],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return manifest


def _apply(plan: Plan) -> tuple[list[Move], list[str]]:
    """Move the files. Returns what actually moved, and what failed."""
    done: list[Move] = []
    failures: list[str] = []
    for move in plan.moves:
        try:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            # `shutil.move` rather than `Path.rename`: Downloads and the target
            # can sit on different volumes once OneDrive is involved, and
            # `rename` raises across them.
            shutil.move(str(move.source), str(move.destination))
            done.append(move)
        except OSError as exc:
            failures.append(f"{move.source.name}: {exc}")
    return done, failures


@tool(
    name="organize_folder",
    tier=Tier.CONFIRM,
    description=(
        "Tidy a folder by moving its files into subfolders. Strategy is "
        "'by_type' (Documents, Images, Archives…) or 'by_date' (2026-08). Use "
        "when asked to organise, tidy, sort or clean up a folder. Shows the "
        "whole plan for approval first and can be undone afterwards."
    ),
    preview=preview_organize,
)
async def organize_folder(
    ctx: ToolContext, path: str, strategy: str = "by_type"
) -> ToolResult:
    """Sort a folder's files into subfolders.

    Args:
        path: The folder to tidy, e.g. "downloads" or a full path.
        strategy: "by_type" to group by kind of file, or "by_date" to group by
            the month each file was last changed.
    """
    root, refusal = _resolve(path)
    if root is None:
        return ToolResult(
            ok=False, summary=f"I will not organise that — {refusal}.", error="refused"
        )
    if not root.is_dir():
        return ToolResult(
            ok=False,
            summary=f"{root} is not a folder, so there is nothing to organise.",
            error="not_a_folder",
        )
    if strategy not in STRATEGIES:
        return ToolResult(
            ok=False,
            summary=f"I can organise by_type or by_date, not {strategy!r}.",
            error="strategy",
        )

    # The plan the user was shown, not a fresh one. See the module docstring.
    # Falling back to a fresh one covers the paths that never previewed at all:
    # a trusted folder, "always allow", or a direct call from a test.
    approved = _take_plan(root, strategy)
    plan = approved if approved is not None else await asyncio.to_thread(
        build_plan, root, strategy
    )
    if not plan.moves:
        return ToolResult(
            ok=True,
            data={"moved": 0},
            summary=f"Nothing to move in {root.name} — it is already tidy.",
            display={"folder": str(root), "moved": 0, "skipped": plan.skipped},
        )

    moved, failures = await asyncio.to_thread(_apply, plan)
    manifest = await asyncio.to_thread(_write_manifest, plan, moved)
    # A batch move is the largest staleness this cache can suffer — thirty
    # files at once — so the next search must not be answered from a scan
    # taken before it. Same reasoning as every `_scan_changed()` in files.py.
    _scan_changed()

    log.info(
        "tool.organized",
        folder=str(root),
        strategy=strategy,
        moved=len(moved),
        failed=len(failures),
        manifest=manifest.name,
    )

    trouble = f" {len(failures)} could not be moved." if failures else ""
    return ToolResult(
        ok=True,
        data={"moved": len(moved), "manifest": manifest.name},
        summary=(
            f"Moved {len(moved)} files in {root.name} into "
            f"{len(plan.folders)} folders.{trouble} Say undo to put them back."
        ),
        display={
            "folder": str(root),
            "strategy": strategy,
            "moved": len(moved),
            "skipped": plan.skipped,
            "folders": plan.folders,
            "failures": failures,
            "manifest": manifest.name,
        },
    )


def _latest_manifest() -> Path | None:
    undo_dir = get_settings().undo_dir
    if not undo_dir.is_dir():
        return None
    manifests = sorted(undo_dir.glob("organize-*.json"))
    return manifests[-1] if manifests else None


async def preview_undo(**_kwargs: object) -> dict[str, Any] | None:
    """Show what putting it back would move, before asking."""
    manifest = _latest_manifest()
    if manifest is None:
        return None
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    moves = payload.get("moves", [])
    return {
        "kind": "move_plan",
        "folder": payload.get("folder", ""),
        "strategy": f"undo {payload.get('strategy', '')}".strip(),
        "count": len(moves),
        "skipped": 0,
        "folders": [],
        # Reversed for display too, so the dialog reads the way the operation
        # runs rather than the way the original one did.
        "moves": [{"from": m["to"], "to": m["from"]} for m in moves[:PREVIEW_ROWS]],
        "truncated": max(0, len(moves) - PREVIEW_ROWS),
    }


@tool(
    name="undo_organize",
    # T2, and it is worth saying why: undoing is restorative, not destructive,
    # so the tier looks heavy-handed. But it moves files, and `move_file` is
    # T2 — rule 5 is about what an operation *does*, not what it is for. An
    # undo aimed at the wrong folder is as disruptive as any other batch move.
    tier=Tier.CONFIRM,
    description=(
        "Put back the files from the last organize_folder. Use when asked to "
        "undo tidying, or to reverse organising a folder."
    ),
    preview=preview_undo,
)
async def undo_organize(ctx: ToolContext) -> ToolResult:
    """Reverse the most recent folder tidy-up."""
    manifest = _latest_manifest()
    if manifest is None:
        return ToolResult(
            ok=False,
            summary="I have no record of tidying a folder, so there is nothing to undo.",
            error="no_manifest",
        )

    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ToolResult(
            ok=False,
            summary=f"The undo record at {manifest.name} could not be read.",
            error=str(exc),
        )

    restored, failures = await asyncio.to_thread(_restore, payload.get("moves", []))
    _scan_changed()

    # Consumed, not kept: a manifest that stays after being replayed is one
    # that gets replayed again, moving files that are already back.
    if not failures:
        manifest.unlink(missing_ok=True)

    log.info(
        "tool.undo_organized",
        manifest=manifest.name,
        restored=len(restored),
        failed=len(failures),
    )
    trouble = f" {len(failures)} could not be put back." if failures else ""
    return ToolResult(
        ok=True,
        data={"restored": len(restored)},
        summary=f"Put {len(restored)} files back where they were.{trouble}",
        display={"restored": len(restored), "failures": failures},
    )


def _restore(moves: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    restored: list[str] = []
    failures: list[str] = []
    # Newest first, so a file moved twice lands back at its original name.
    for move in reversed(moves):
        source, destination = Path(move["to"]), Path(move["from"])
        if _refuse(source) or _refuse(destination):
            failures.append(f"{source.name}: refused")
            continue
        if not source.exists():
            failures.append(f"{source.name}: it is no longer there")
            continue
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(_unique(destination, set())))
            restored.append(destination.name)
        except OSError as exc:
            failures.append(f"{source.name}: {exc}")
    return restored, failures
