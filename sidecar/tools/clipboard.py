"""The clipboard (BUILD_SPEC §9 Phase 3).

`win32clipboard` ships with pywin32, which has been a dependency since Phase 3,
so this costs no new package.

**Reading the clipboard is harmless; sending what it contained to somebody
else's server is not.** Clipboards hold passwords, card numbers and 2FA codes —
whatever was last copied, not whatever the user had in mind when they asked.
So `read_clipboard` runs silently (tier 0, it changes nothing) but is marked
`local_only`, and the turn that reads it finishes on the local model however it
was routed. Decided with Eyaas: no prompt, and it never leaves the machine.

The clipboard is also *shared*: any process can open it, and a handle held open
blocks everyone else. Every call here opens, reads or writes, and closes in a
`finally`.
"""

from __future__ import annotations

import asyncio

import structlog

from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

#: What the *model* is shown. The rest goes to `display` (§7.2) — a clipboard
#: holding a whole document should not become a whole prompt.
READ_SUMMARY_CHARS = 1500

#: Windows will accept far more, but nothing good comes of a model composing
#: half a megabyte into someone's clipboard.
WRITE_MAX_CHARS = 100_000


def read_text() -> str | None:
    """The clipboard's text, or None when it holds something else.

    An image, a file list or a rich-text-only payload are all `None` rather
    than an error — "there is no text on the clipboard" is the true answer and
    a more useful one than a traceback.

    Public because `tools/apps.py` borrows it: `type_text` pastes long text
    rather than typing it, and has to put back whatever was on the clipboard
    afterwards. Reaching across modules into a `_name` is the kind of thing
    ruff's SLF rules exist to stop, and the honest fix is to admit this is
    part of the module's surface.
    """
    import win32clipboard
    import win32con

    win32clipboard.OpenClipboard()
    try:
        if not win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            return None
        return str(win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT))
    finally:
        # Always. A clipboard left open blocks every other program on the
        # machine from using it, including the one the user is looking at.
        win32clipboard.CloseClipboard()


def write_text(text: str) -> None:
    """Replace the clipboard's contents. Public for the same reason as
    `read_text` above."""
    import win32clipboard
    import win32con

    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
    finally:
        win32clipboard.CloseClipboard()


@tool(
    name="read_clipboard",
    tier=Tier.AUTO,
    description=(
        "Read what is currently on the clipboard. Use when asked about what "
        "the user just copied, or to work with something they have copied."
    ),
    # Never to a cloud model. See the module docstring.
    local_only=True,
)
async def read_clipboard(ctx: ToolContext) -> ToolResult:
    """Read the clipboard's text."""
    try:
        text = await asyncio.to_thread(read_text)
    except OSError as exc:
        # Another program had it open. Worth saying plainly — it is transient
        # and trying again usually works.
        return ToolResult(
            ok=False,
            summary="Something else is using the clipboard. Try again in a moment.",
            error=str(exc),
        )

    if text is None:
        return ToolResult(
            ok=True, data=None, summary="There is no text on the clipboard right now."
        )
    if not text.strip():
        return ToolResult(ok=True, data="", summary="The clipboard is empty.")

    # Logged as a length, never as content. This is the one tool whose
    # arguments and result are the thing being protected, and `tool_log` is
    # not a place to copy someone's password into.
    log.info("tool.read_clipboard", chars=len(text))

    head = text[:READ_SUMMARY_CHARS]
    clipped = "" if len(text) <= READ_SUMMARY_CHARS else f" (first {READ_SUMMARY_CHARS} characters)"
    return ToolResult(
        ok=True,
        data=head,
        summary=f"The clipboard has{clipped}:\n{head}",
        display={"text": text, "chars": len(text)},
    )


@tool(
    name="write_clipboard",
    tier=Tier.SAFE,
    description=(
        "Put text on the clipboard so the user can paste it. Use when asked to "
        "copy something for them."
    ),
)
async def write_clipboard(ctx: ToolContext, text: str) -> ToolResult:
    """Put text on the clipboard.

    Args:
        text: What to copy
    """
    if not text:
        return ToolResult(ok=False, summary="Tell me what to copy.", error="empty")
    if len(text) > WRITE_MAX_CHARS:
        return ToolResult(
            ok=False,
            summary=f"That is {len(text)} characters, which is too much to put on the clipboard.",
            error="too_long",
        )

    try:
        await asyncio.to_thread(write_text, text)
    except OSError as exc:
        return ToolResult(
            ok=False,
            summary="Something else is using the clipboard. Try again in a moment.",
            error=str(exc),
        )

    log.info("tool.write_clipboard", chars=len(text))
    preview = text if len(text) <= 60 else text[:57] + "…"
    return ToolResult(
        ok=True,
        data={"chars": len(text)},
        summary=f"Copied to the clipboard: {preview}",
    )


#: A history entry is shown to the model in preview form only. The whole point
#: of the ring is that it holds things worth pasting; pasting a whole document
#: into a prompt is what `READ_SUMMARY_CHARS` already exists to prevent.
HISTORY_PREVIEW_CHARS = 200


@tool(
    name="read_clipboard_history",
    tier=Tier.AUTO,
    description=(
        "See what was copied recently, newest first. Use when asked about "
        "something copied earlier rather than what is on the clipboard now — "
        "'what did I copy before that', 'find the link I copied'."
    ),
    # **Not optional.** `read_clipboard` carries this flag because a clipboard
    # holds passwords and card numbers; a *history* of clipboards is strictly
    # more of the same thing, and a version of it that could reach a cloud
    # model would be a hole in exactly the guarantee that flag exists to make.
    local_only=True,
)
async def read_clipboard_history(ctx: ToolContext, count: int = 10) -> ToolResult:
    """Read what was copied recently.

    Args:
        count: How many entries to look back over, newest first
    """
    from sidecar.memory import clipboard_store
    from sidecar.state import runtime

    if runtime.db is None:
        return ToolResult(
            ok=False,
            summary="The clipboard history is not available in this session.",
            error="unavailable",
        )

    entries = await clipboard_store.recent(runtime.db, count)
    if not entries:
        return ToolResult(
            ok=True,
            data=[],
            summary=(
                "Nothing has been copied since ARIA started, or the history is "
                "switched off."
            ),
        )

    # Lengths only, as in `read_clipboard`. This tool's whole payload is the
    # thing being protected and `tool_log` is not a place to copy it into.
    log.info("tool.read_clipboard_history", entries=len(entries))

    lines = []
    for position, entry in enumerate(entries, start=1):
        head = entry.content[:HISTORY_PREVIEW_CHARS].replace("\n", " ")
        more = "…" if entry.chars > HISTORY_PREVIEW_CHARS else ""
        lines.append(f"{position}. {head}{more}")

    return ToolResult(
        ok=True,
        data=[e.content for e in entries],
        summary=f"The last {len(entries)} things copied:\n" + "\n".join(lines),
        display={
            "kind": "clipboard_history",
            "entries": [
                {"id": e.id, "content": e.content, "chars": e.chars, "copied_at": e.copied_at}
                for e in entries
            ],
        },
    )
