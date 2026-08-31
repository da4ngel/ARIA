""""Undo that" — one command, whatever the last thing was.

Before this, undo existed for exactly one tool: `undo_organize` replayed a
folder tidy-up's manifest, and `move_file`, `rename_file`, `write_file` and
`delete_file` left nothing behind that could be reversed at all. The timeline in
`memory/undo.py` is the general form, and this is the way to reach it in
conversation.

**T2, and the tier is not a formality.** Undoing is restorative in intent and a
mutation in fact: it moves files and overwrites them. `undo_organize` carries
CONFIRM for the same reason and its comment says it plainly — rule 5 is about
what an operation *does*, not what it is for. An undo aimed at the wrong entry
is as disruptive as any other batch move.
"""

from __future__ import annotations

import structlog

from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)


async def preview_undo_last(**_kwargs: object) -> dict[str, object] | None:
    """Show what will be reversed, before the dialog asks.

    `Tool.preview` never raises — losing the detail is much better than losing
    the confirmation — so anything unexpected here falls back to the plain
    argument list.
    """
    try:
        from sidecar.memory import undo
        from sidecar.state import runtime

        if runtime.db is None:
            return None
        entry = await undo.last_undoable(runtime.db)
        if entry is None:
            return None
        return {"kind": "undo", "summary": entry.summary, "tool": entry.tool}
    except Exception:  # noqa: BLE001
        return None


@tool(
    name="undo_last",
    tier=Tier.CONFIRM,
    description=(
        "Reverse the last file change she made — a move, a rename, or an "
        "overwrite. Use for 'undo that', 'put it back', 'never mind, revert "
        "it'. For a folder tidy-up use undo_organize instead."
    ),
    preview=preview_undo_last,
)
async def undo_last(ctx: ToolContext) -> ToolResult:
    """Reverse the most recent reversible change."""
    from sidecar.memory import undo
    from sidecar.state import runtime

    if runtime.db is None:
        return ToolResult(
            ok=False, summary="The undo timeline is not available.", error="unavailable"
        )

    entry = await undo.last_undoable(runtime.db)
    if entry is None:
        return ToolResult(
            ok=True,
            data=None,
            summary="There is nothing to undo — nothing reversible has happened yet.",
        )

    ok, message = await undo.apply(runtime.db, entry.id)
    if not ok:
        # The reason is the useful part: a file that moved again, a backup past
        # its keep-window, a Recycle Bin restore only Windows can do.
        return ToolResult(ok=False, summary=message, error="failed")

    from sidecar.tools.files import _scan_changed

    _scan_changed()
    return ToolResult(
        ok=True, data={"id": entry.id, "kind": entry.kind}, summary=message
    )
