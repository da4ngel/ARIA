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
