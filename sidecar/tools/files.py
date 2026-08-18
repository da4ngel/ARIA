"""The tools that can cost you something.

`move_file` is CONFIRM and `delete_file` is DANGER, which is the difference
between "you can put it back" and "you cannot". Both refuse before they act on
anything they were not clearly pointed at.

The checks here are deliberately paranoid, because the caller is a language
model working from a transcription of speech. A misheard path is not a rare
event in this system — it is Tuesday — so a tool that cheerfully deletes
whatever it was handed is the wrong shape regardless of what the tier engine
does upstream.
"""

from __future__ import annotations

import asyncio
import ctypes
import os
import re
import shutil
import uuid
from pathlib import Path
from typing import ClassVar

import structlog

from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

#: Directories nothing here will touch, whatever it is asked. These are not
#: user data; a request to delete inside them is a mistake or a misheard path,
#: never an intention.
_FORBIDDEN_ROOTS = (
    Path("C:/Windows"),
    Path("C:/Program Files"),
    Path("C:/Program Files (x86)"),
    Path("C:/ProgramData"),
)


def _scan_changed() -> None:
    """Tell the finder its cached directory scan is out of date.

    Imported here rather than at module scope on purpose: `tools/finder.py`
    imports `known_folder` from this module, so a top-level import back the
    other way is a cycle. One deferred import inside one function is the
    smaller cost, and it is the only edge between the two.

    Every tool below that creates, moves, renames or removes something calls
    this after the filesystem has actually changed — never before, and never
    on a refusal, so a call that did nothing does not throw away a good scan.
    """
    from sidecar.tools.finder import invalidate_scan

    invalidate_scan()


def _refuse(path: Path) -> str | None:
    """Why this path must not be touched, or None if it may be."""
    try:
        resolved = path.resolve()
    except OSError:
        return "that path cannot be resolved"

    if resolved.parent == resolved:
        return "that is a drive root"
    for root in _FORBIDDEN_ROOTS:
        try:
            if resolved.is_relative_to(root):
                return f"that is inside {root}, which is system files rather than yours"
        except ValueError:
            continue
    return None


@tool(
    name="move_file",
    tier=Tier.CONFIRM,
    description=(
        "Move or rename a file. Use when asked to move something to another "
        "folder, or to rename it. The destination folder must already exist."
    ),
)
async def move_file(ctx: ToolContext, source: str, destination: str) -> ToolResult:
    """Move or rename a file.

    Args:
        source: Full path of the file to move, e.g. "C:/Users/me/notes.txt"
        destination: Full path to move it to, including the new filename
    """
    src, dst = Path(source), Path(destination)

    for path in (src, dst):
        refusal = _refuse(path)
        if refusal is not None:
            return ToolResult(
                ok=False, summary=f"I will not touch {path}: {refusal}.", error="path"
            )

    if not await asyncio.to_thread(src.is_file):
        return ToolResult(ok=False, summary=f"There is no file at {src}.", error="missing")
    if await asyncio.to_thread(dst.exists):
        # Overwriting is a *different* destructive act from moving, and the
        # user approved a move.
        return ToolResult(
            ok=False,
            summary=f"{dst} already exists. I would be overwriting it, so I stopped.",
            error="exists",
        )
    if not await asyncio.to_thread(dst.parent.is_dir):
        return ToolResult(ok=False, summary=f"The folder {dst.parent} does not exist.", error="dir")

    await asyncio.to_thread(shutil.move, str(src), str(dst))
    log.info("tool.moved", source=str(src), destination=str(dst))
    _scan_changed()
    return ToolResult(
        ok=True,
        data={"source": str(src), "destination": str(dst)},
        summary=f"Moved {src.name} to {dst}.",
    )


@tool(
    name="delete_file",
    tier=Tier.DANGER,
    description=(
        "Permanently delete a file. This cannot be undone. Only use when the "
        "user has clearly asked for a specific file to be deleted."
    ),
)
async def delete_file(ctx: ToolContext, path: str) -> ToolResult:
    """Permanently delete a file.

    Args:
        path: Full path of the file to delete, e.g. "C:/temp/scratch.txt"
    """
    target = Path(path)

    refusal = _refuse(target)
    if refusal is not None:
        return ToolResult(ok=False, summary=f"I will not delete {target}: {refusal}.", error="path")

    if await asyncio.to_thread(target.is_dir):
        # A folder is a different, much larger promise than a file, and this
        # tool's description says file.
        return ToolResult(
            ok=False,
            summary=f"{target} is a folder, and I only delete single files.",
            error="is_dir",
        )
    if not await asyncio.to_thread(target.is_file):
        return ToolResult(ok=False, summary=f"There is no file at {target}.", error="missing")

    size = (await asyncio.to_thread(target.stat)).st_size
    await asyncio.to_thread(target.unlink)
    log.info("tool.deleted", path=str(target), bytes=size)
    _scan_changed()
    return ToolResult(
        ok=True,
        data={"path": str(target), "bytes": size},
        summary=f"Deleted {target.name}.",
    )


# ── opening things ───────────────────────────────────────────────────
# Asked to "open downloads folder" with no tool for it, she answered "Opened
# Downloads." and nothing happened. The fix for that is not more prompt: it is
# having the tool, so there is nothing to invent.


class _GUID(ctypes.Structure):
    # ctypes reads this by name; the ClassVar annotation is for the linter's
    # benefit and changes nothing at runtime.
    _fields_: ClassVar = [
        ("d1", ctypes.c_uint32),
        ("d2", ctypes.c_uint16),
        ("d3", ctypes.c_uint16),
        ("d4", ctypes.c_byte * 8),
    ]


# The names people say, and Windows' own ids for them. Resolved through
# `SHGetKnownFolderPath` rather than joined onto %USERPROFILE%: these folders
# move, and OneDrive relocates Documents and Desktop by default, so a
# hardcoded join is wrong on a very ordinary machine.
_KNOWN_FOLDERS = {
    "downloads": "{374DE290-123F-4565-9164-39C4925E467B}",
    "documents": "{FDD39AD0-238F-46AF-ADB4-6C85480369C7}",
    "desktop": "{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}",
    "pictures": "{33E28130-4E1E-4676-835A-98395C3BC3BB}",
    "music": "{4BD8D571-6D19-48D3-BE97-422220080E43}",
    "videos": "{18989B1D-99B5-455B-841C-AB7C74E4DDFC}",
    "home": "{5E6C858F-0E22-4760-9AFE-EA3317B67173}",
}

_FOLDER_WORDS = re.compile(r"\b(the|my|folder|directory|open)\b")


def known_folder(name: str) -> Path | None:
    """A named place, or None if it is not one.

    Tolerant of how people say it — "my downloads folder" and "Downloads" are
    the same request.
    """
    cleaned = _FOLDER_WORDS.sub(" ", name.lower()).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    guid = _KNOWN_FOLDERS.get(cleaned)
    if guid is None:
        return None

    parsed = uuid.UUID(guid)
    handle = _GUID()
    handle.d1, handle.d2, handle.d3 = parsed.time_low, parsed.time_mid, parsed.time_hi_version
    for index, byte in enumerate(parsed.bytes[8:]):
        handle.d4[index] = byte if byte < 128 else byte - 256

    out = ctypes.c_wchar_p()
    if ctypes.windll.shell32.SHGetKnownFolderPath(
        ctypes.byref(handle), 0, None, ctypes.byref(out)
    ):
        return None
    return Path(out.value) if out.value else None


@tool(
    name="open_path",
    tier=Tier.SAFE,
    description=(
        "Open a folder or a file in Windows — for example the Downloads "
        "folder, Documents, or a full path like C:/Users/me/notes.txt. Use "
        "when asked to open, show or go to a folder or a specific file."
    ),
)
async def open_path(ctx: ToolContext, path: str) -> ToolResult:
    """Open a folder or file.

    Args:
        path: A folder name like "downloads", or a full path to a file or folder
    """
    wanted = path.strip().strip('"')
    if not wanted:
        return ToolResult(ok=False, summary="Tell me what to open.", error="empty")

    target = known_folder(wanted) or Path(wanted).expanduser()

    if not await asyncio.to_thread(target.exists):
        return ToolResult(
            ok=False,
            summary=(
                f"There is nothing at {target}. "
                f"Give me a full path, or a name like Downloads or Documents."
            ),
            error="missing",
        )

    try:
        await asyncio.to_thread(os.startfile, str(target))
    except OSError as exc:
        return ToolResult(ok=False, summary=f"{target} would not open.", error=str(exc))

    kind = "folder" if await asyncio.to_thread(target.is_dir) else "file"
    log.info("tool.opened_path", path=str(target), kind=kind)
    return ToolResult(
        ok=True,
        data={"path": str(target), "kind": kind},
        summary=f"Opened {target.name or target} ({kind}).",
    )


# ── the rest of the file tools ───────────────────────────────────────
# §7.2 lists read_file, write_file, create_folder, move_file, rename_file and
# delete_file. Only move and delete were built, so she could destroy a file and
# not create one — and "create a file named hello.txt in downloads" had no tool
# to reach for at all.
#
# `_refuse` above guards every one of these. Those rules are **not** relaxed by
# a trusted folder: trust decides whether she asks first, never whether
# C:/Windows is fair game.

#: A file bigger than this is not something to put in front of a model.
READ_MAX_BYTES = 1024 * 1024
#: What the *model* sees of a file. The rest goes to `display` (§7.2).
READ_SUMMARY_CHARS = 1500
#: More entries than this in one reply is noise.
LIST_SUMMARY_MAX = 25


def _resolve(raw: str) -> tuple[Path | None, str | None]:
    """A path and why it is refused, if it is."""
    target = Path(raw.strip().strip('"')).expanduser()
    # A bare name means the folder the user is thinking of, not the working
    # directory of the sidecar — which is the repo, and nothing to do with them.
    if not target.is_absolute():
        folder = known_folder(target.parts[0]) if target.parts else None
        if folder is not None:
            target = folder.joinpath(*target.parts[1:])
    return (None, _refuse(target)) if _refuse(target) else (target, None)


@tool(
    name="read_file",
    tier=Tier.AUTO,
    description=(
        "Read the contents of a text file. Use when asked what a file says, "
        "to summarise it, or to check something inside it."
    ),
)
async def read_file(ctx: ToolContext, path: str) -> ToolResult:
    """Read a text file.

    Args:
        path: Full path of the file, e.g. "C:/Users/me/notes.txt"
    """
    target, refusal = _resolve(path)
    if target is None:
        return ToolResult(ok=False, summary=f"I will not read {path}: {refusal}.", error="path")
    if not await asyncio.to_thread(target.is_file):
        return ToolResult(ok=False, summary=f"There is no file at {target}.", error="missing")

    size = (await asyncio.to_thread(target.stat)).st_size
    if size > READ_MAX_BYTES:
        return ToolResult(
            ok=False,
            summary=f"{target.name} is {size // 1024}KB, which is too large to read out.",
            error="too_large",
        )

    text = await asyncio.to_thread(target.read_text, encoding="utf-8", errors="replace")
    if not text.strip():
        return ToolResult(ok=True, data="", summary=f"{target.name} is empty.")

    # The model gets the opening; the UI gets all of it. A 5MB log pasted into
    # the prompt is §7.2's second failure mode with extra steps.
    head = text[:READ_SUMMARY_CHARS]
    clipped = "" if len(text) <= READ_SUMMARY_CHARS else f" (first {READ_SUMMARY_CHARS} characters)"
    return ToolResult(
        ok=True,
        data=head,
        summary=f"{target.name}{clipped}:\n{head}",
        display={"path": str(target), "text": text, "bytes": size},
    )


@tool(
    name="list_folder",
    tier=Tier.AUTO,
    description=(
        "List what is inside a folder. Use when asked what is in a folder, "
        "or to see the files somewhere before doing anything with them."
    ),
)
async def list_folder(ctx: ToolContext, path: str) -> ToolResult:
    """List a folder's contents.

    Args:
        path: Folder to list, e.g. "downloads" or "C:/Users/me/Projects"
    """
    target, refusal = _resolve(path)
    if target is None:
        return ToolResult(ok=False, summary=f"I will not list {path}: {refusal}.", error="path")
    if not await asyncio.to_thread(target.is_dir):
        return ToolResult(ok=False, summary=f"{target} is not a folder.", error="not_a_folder")

    entries = sorted(
        await asyncio.to_thread(lambda: list(target.iterdir())),
        key=lambda p: (not p.is_dir(), p.name.lower()),
    )
    if not entries:
        return ToolResult(ok=True, data=[], summary=f"{target.name} is empty.")

    shown = [f"{e.name}/" if e.is_dir() else e.name for e in entries[:LIST_SUMMARY_MAX]]
    more = len(entries) - len(shown)
    tail = f", and {more} more" if more > 0 else ""
    return ToolResult(
        ok=True,
        data=[str(e) for e in entries],
        summary=f"{len(entries)} in {target.name}: {', '.join(shown)}{tail}.",
        display={"path": str(target), "entries": [str(e) for e in entries]},
    )


@tool(
    name="create_folder",
    tier=Tier.SAFE,
    description="Create a new folder. Use when asked to make a folder or directory.",
)
async def create_folder(ctx: ToolContext, path: str) -> ToolResult:
    """Create a folder.

    Args:
        path: Where to create it, e.g. "downloads/receipts"
    """
    target, refusal = _resolve(path)
    if target is None:
        return ToolResult(ok=False, summary=f"I will not create {path}: {refusal}.", error="path")
    if await asyncio.to_thread(target.exists):
        return ToolResult(ok=True, data={"path": str(target)}, summary=f"{target} already exists.")

    await asyncio.to_thread(lambda: target.mkdir(parents=True, exist_ok=True))
    log.info("tool.created_folder", path=str(target))
    _scan_changed()
    return ToolResult(ok=True, data={"path": str(target)}, summary=f"Created {target}.")


@tool(
    name="write_file",
    tier=Tier.CONFIRM,
    description=(
        "Create a file with some text in it, or replace what a file contains. "
        "Use when asked to write, save, or create a file with contents."
    ),
)
async def write_file(ctx: ToolContext, path: str, content: str = "") -> ToolResult:
    """Write a text file.

    Args:
        path: Where to write it, e.g. "downloads/hello.txt"
        content: What to put in it. Leave empty for an empty file.
    """
    target, refusal = _resolve(path)
    if target is None:
        return ToolResult(ok=False, summary=f"I will not write to {path}: {refusal}.", error="path")
    if await asyncio.to_thread(target.is_dir):
        return ToolResult(ok=False, summary=f"{target} is a folder.", error="is_dir")

    existed = await asyncio.to_thread(target.is_file)
    try:
        await asyncio.to_thread(lambda: target.parent.mkdir(parents=True, exist_ok=True))
        await asyncio.to_thread(target.write_text, content, encoding="utf-8")
    except OSError as exc:
        return ToolResult(ok=False, summary=f"Could not write {target}: {exc}", error=str(exc))

    log.info("tool.wrote_file", path=str(target), bytes=len(content), replaced=existed)
    _scan_changed()
    verb = "Replaced" if existed else "Created"
    return ToolResult(
        ok=True,
        data={"path": str(target), "bytes": len(content), "replaced": existed},
        summary=f"{verb} {target.name} ({len(content)} characters).",
    )


@tool(
    name="rename_file",
    tier=Tier.CONFIRM,
    description=(
        "Rename a file or folder, leaving it where it is. Use when asked to "
        "rename something rather than move it."
    ),
)
async def rename_file(ctx: ToolContext, path: str, new_name: str) -> ToolResult:
    """Rename a file or folder in place.

    Args:
        path: What to rename, e.g. "downloads/scan001.pdf"
        new_name: The new name only, not a path, e.g. "invoice.pdf"
    """
    target, refusal = _resolve(path)
    if target is None:
        return ToolResult(ok=False, summary=f"I will not rename {path}: {refusal}.", error="path")
    if not await asyncio.to_thread(target.exists):
        return ToolResult(ok=False, summary=f"There is nothing at {target}.", error="missing")

    clean = new_name.strip().strip('"')
    # A name, not a path: "rename it to ../../etc" is not a rename.
    if not clean or set(clean) & set('/\\:*?"<>|'):
        return ToolResult(
            ok=False,
            summary=f"{new_name!r} is not a valid name. Give me just the new filename.",
            error="bad_name",
        )

    destination = target.with_name(clean)
    if await asyncio.to_thread(destination.exists):
        return ToolResult(
            ok=False,
            summary=f"{clean} already exists there, so I stopped rather than overwrite it.",
            error="exists",
        )

    await asyncio.to_thread(target.rename, destination)
    log.info("tool.renamed", was=str(target), now=str(destination))
    _scan_changed()
    return ToolResult(
        ok=True,
        data={"was": str(target), "now": str(destination)},
        summary=f"Renamed {target.name} to {clean}.",
    )


@tool(
    name="delete_folder",
    tier=Tier.DANGER,
    description=(
        "Permanently delete a folder and everything inside it. This cannot be "
        "undone. Only use when the user has clearly asked for a specific "
        "folder to be deleted."
    ),
)
async def delete_folder(ctx: ToolContext, path: str) -> ToolResult:
    """Permanently delete a folder and its contents.

    Args:
        path: Full path of the folder to delete
    """
    target, refusal = _resolve(path)
    if target is None:
        return ToolResult(ok=False, summary=f"I will not delete {path}: {refusal}.", error="path")
    if not await asyncio.to_thread(target.is_dir):
        return ToolResult(ok=False, summary=f"{target} is not a folder.", error="not_a_folder")

    # A named folder is never one of these, so being asked for one means
    # something was misheard or misunderstood.
    if known_folder(target.name) == target:
        return ToolResult(
            ok=False,
            summary=f"{target.name} is one of your main folders. I will not delete it.",
            error="known_folder",
        )

    count = len(await asyncio.to_thread(lambda: list(target.rglob("*"))))
    await asyncio.to_thread(shutil.rmtree, target)
    log.info("tool.deleted_folder", path=str(target), entries=count)
    _scan_changed()
    return ToolResult(
        ok=True,
        data={"path": str(target), "entries": count},
        summary=(
            f"Deleted {target.name} and the {count} "
            f"{'thing' if count == 1 else 'things'} inside it."
        ),
    )
