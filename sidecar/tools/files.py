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
import shutil
from pathlib import Path

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
