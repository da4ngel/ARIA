"""`capture_screen(question)` — let her see what's on screen (§9 Phase 6).

Screenshot plus a single cloud vision call, self-contained the way
`research.py` is: no local vision model exists on this hardware (rule 2, the
6GB VRAM ceiling), so there is nothing for `core/router.py` to choose between
— this tool reaches the one designated vision provider directly rather than
through the general chat pipeline. `ChatMessage.content` stays a plain `str`
everywhere else in the stack; teaching it an image type for exactly one
caller would be a bigger change than the feature is worth.

§11 is explicit: *"Screen captures are ephemeral — never written to disk
unless the user asks."* Captured straight into memory and never touches
`data/` anywhere in this file.

**Consent is per-call, not a switch like online mode.** BUILD_SPEC's own tier
table (§9:474) lists `capture_screen` as AUTO — that line is about the act of
*taking* a screenshot. Sending it to a cloud vision API is the sensitive
step, and it happens inside this same call, so the tool's own tier has to
cover the whole thing. Decided with Eyaas: CONFIRM, every time, with a
thumbnail preview via `Tool.preview` — a screenshot is a much bigger and more
variable exposure per call than a typed search query, which is why this
doesn't get `research`'s always-on switch.

`router._PRIVATE` keeping a *conversational* turn local when the user's words
mention "my screen" is a different question from this tool's own internal
vision call: that governs which model answers ordinary text, and this call
never goes through `router.choose()` at all — there is nothing local to route
to.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import io
import time
from typing import Any

import mss
import structlog
from PIL import Image

from sidecar.providers import catalog
from sidecar.providers.base import ProviderRateLimited, ProviderUnavailable
from sidecar.state import runtime
from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

#: The one model this tool ever calls — not a router decision. `gpt-4o`'s own
#: `best_for` text already names this duty ("the vision model for screen
#: questions"); this is what makes that sentence literally true.
VISION_MODEL_ID = "gpt-4o"
#: Small enough for a fast round-trip through the confirmation dialog. The
#: full frame — not this — is what actually goes to the model.
THUMBNAIL_MAX_PX = 480
#: Comfortably longer than the 120s confirmation timeout, short enough that a
#: captured frame is never sent long after what it showed has changed.
CAPTURE_TTL_S = 150.0

DEFAULT_QUESTION = "Describe what's on screen right now."


def _capture_jpeg() -> bytes:
    """The whole screen (every monitor), as JPEG bytes.

    Synchronous — both `mss` and Pillow block — so every caller runs this
    through `asyncio.to_thread`.
    """
    with mss.mss() as sct:
        # Index 0 is mss's own convention for "every monitor, as one image".
        shot = sct.grab(sct.monitors[0])
    image = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()


def _thumbnail_b64(jpeg: bytes) -> str:
    image = Image.open(io.BytesIO(jpeg))
    image.thumbnail((THUMBNAIL_MAX_PX, THUMBNAIL_MAX_PX))
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=70)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


#: One captured frame per pending confirmation, keyed by the question asked.
#: The same "the plan you approve is the plan that runs" guarantee
#: `organize_folder` established (CLAUDE.md): a fresh screenshot taken at
#: execution time would show the user one frame in the dialog and send the
#: model a different one, whatever changed on screen in the meantime.
_CAPTURES: dict[str, tuple[bytes, float]] = {}


def _key(question: str) -> str:
    return hashlib.sha256(question.encode()).hexdigest()[:16]


def clear_captures() -> None:
    """Forget every previewed capture. For tests, and for a fresh session."""
    _CAPTURES.clear()


async def preview_capture_screen(question: str = DEFAULT_QUESTION) -> dict[str, Any] | None:
    """Take the screenshot *now*, before the user is even asked — the dialog
    has to show a real frame, not a promise of one. Stashed so the frame the
    model sees is the frame that was shown.

    Never raises: a preview that fails falls back to the dialog's plain
    argument view, because losing the thumbnail is far better than losing
    the confirmation itself.
    """
    try:
        jpeg = await asyncio.to_thread(_capture_jpeg)
        thumbnail = _thumbnail_b64(jpeg)
    except Exception:  # noqa: BLE001 — see the docstring
        log.warning("screen.preview_failed", exc_info=True)
        return None
    _CAPTURES[_key(question)] = (jpeg, time.monotonic())
    provider = catalog.get(VISION_MODEL_ID)
    return {
        "kind": "image_preview",
        "thumbnail_b64": thumbnail,
        "provider": provider.label if provider else VISION_MODEL_ID,
    }


def _take_capture(question: str) -> bytes | None:
    entry = _CAPTURES.pop(_key(question), None)
    if entry is None:
        return None
    jpeg, created_at = entry
    if time.monotonic() - created_at > CAPTURE_TTL_S:
        return None
    return jpeg


@tool(
    name="capture_screen",
    tier=Tier.CONFIRM,
    description=(
        "Take a screenshot of everything currently on screen and answer a "
        "question about it, or describe it if no question is given. Use when "
        "asked what is on screen, to read something visible, or to check the "
        "state of a window without a tool that reads its content directly."
    ),
    preview=preview_capture_screen,
)
async def capture_screen(ctx: ToolContext, question: str = DEFAULT_QUESTION) -> ToolResult:
    """Look at the screen and answer something about it.

    Args:
        question: What to look for or ask about. Defaults to a general
            description of what is currently visible if not given.
    """
    provider = runtime.providers.get(str(catalog.ProviderName.OPENAI))
    describe = getattr(provider, "describe_image", None)
    if provider is None or describe is None:
        return ToolResult(
            ok=False,
            summary="Looking at the screen needs an OpenAI key, which is not set up.",
            error="no_vision_provider",
        )

    # The frame shown in the confirmation, not a fresh one — see the module
    # docstring. Falls back to a fresh capture for the paths that never
    # preview at all: a trusted call, "always allow", or a direct test.
    jpeg = _take_capture(question)
    if jpeg is None:
        jpeg = await asyncio.to_thread(_capture_jpeg)
    image_b64 = base64.b64encode(jpeg).decode("ascii")

    try:
        description = await describe(image_b64, question, model=VISION_MODEL_ID)
    except (ProviderUnavailable, ProviderRateLimited) as exc:
        return ToolResult(ok=False, summary=str(exc), error="vision_unavailable")

    log.info("tool.capture_screen", question=question[:80], chars=len(description))
    return ToolResult(
        ok=True,
        data={"question": question},
        summary=description,
        display={"question": question},
    )
