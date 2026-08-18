"""`capture_screen(question)` — the confirmation preview, the stash, §11.

The interesting property here is the same one `test_organize.py` guards for
`organize_folder`: **the frame shown in the confirmation is the frame that
gets sent.** Recomputing at execution time would show the user one screen and
describe a different one taken moments later — a live-updating desktop is at
least as likely to have changed as a folder is.
"""

from __future__ import annotations

import time
from collections.abc import Iterator

import pytest

from sidecar.providers.base import ProviderRateLimited, ProviderUnavailable
from sidecar.tools import screen as screen_module
from sidecar.tools.registry import Tier, ToolContext
from sidecar.tools.screen import (
    _CAPTURES,
    CAPTURE_TTL_S,
    _key,
    capture_screen,
    clear_captures,
    preview_capture_screen,
)

CTX = ToolContext(session_id="s_test", turn_id="t_test")

PREVIEW_JPEG = b"\xff\xd8-preview-frame"
FRESH_JPEG = b"\xff\xd8-fresh-frame"


class StubVision:
    """Stands in for `OpenAIProvider.describe_image`."""

    def __init__(
        self, reply: str = "A code editor and a terminal.", raises: Exception | None = None
    ) -> None:
        self.reply = reply
        self.raises = raises
        self.calls: list[tuple[str, str, str]] = []  # (image_b64, prompt, model)

    async def describe_image(self, image_b64: str, prompt: str, *, model: str) -> str:
        self.calls.append((image_b64, prompt, model))
        if self.raises:
            raise self.raises
        return self.reply


@pytest.fixture(autouse=True)
def _clean_stash() -> Iterator[None]:
    """Every test starts and ends with an empty stash — one test's leftover
    capture must never answer another test's call."""
    clear_captures()
    yield
    clear_captures()


@pytest.fixture
def vision(monkeypatch: pytest.MonkeyPatch) -> StubVision:
    from sidecar.providers import catalog
    from sidecar.state import runtime

    stub = StubVision()
    monkeypatch.setattr(runtime, "providers", {str(catalog.ProviderName.OPENAI): stub})
    return stub


def _fake_capture(monkeypatch: pytest.MonkeyPatch, jpeg: bytes) -> None:
    """`_capture_jpeg` needs a real display; every test replaces it."""

    def fake() -> bytes:
        return jpeg

    monkeypatch.setattr(screen_module, "_capture_jpeg", fake)


def _fake_thumbnail(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pillow's actual resize/encode is not the thing under test here, and
    running it on arbitrary fake bytes would just raise."""
    monkeypatch.setattr(
        screen_module,
        "_thumbnail_b64",
        lambda jpeg: "thumb-" + jpeg.decode(errors="replace")[:8],
    )


# ── tier and registration ────────────────────────────────────────────


def test_it_sits_at_confirm_not_the_spec_tables_auto() -> None:
    """BUILD_SPEC's own tier table (§9:474) lists this AUTO — that line is
    about the act of *capturing*. Sending the frame to a cloud vision API is
    the sensitive step and happens inside the same call, so the tool's tier
    has to cover the whole thing. Decided with Eyaas: ask every time."""
    from sidecar.tools import registry

    assert registry.snapshot()["capture_screen"].tier is Tier.CONFIRM


# ── the preview stashes what gets sent ───────────────────────────────


async def test_the_preview_shows_a_real_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_capture(monkeypatch, PREVIEW_JPEG)
    _fake_thumbnail(monkeypatch)

    preview = await preview_capture_screen("what's on screen")

    assert preview is not None
    assert preview["kind"] == "image_preview"
    assert preview["thumbnail_b64"]
    assert preview["provider"] == "GPT-4o"


async def test_a_failed_capture_falls_back_to_no_preview(monkeypatch: pytest.MonkeyPatch) -> None:
    """Never raises — losing the thumbnail is far better than losing the
    confirmation dialog itself. Same shape as `organize_folder`'s preview."""

    def broken() -> bytes:
        raise OSError("no display attached")

    monkeypatch.setattr(screen_module, "_capture_jpeg", broken)

    assert await preview_capture_screen("anything") is None


async def test_the_frame_shown_is_the_frame_sent(
    monkeypatch: pytest.MonkeyPatch, vision: StubVision
) -> None:
    """The load-bearing guarantee. Mutation-checked below: recomputing at
    execution time instead of using the stash makes this test fail."""
    _fake_capture(monkeypatch, PREVIEW_JPEG)
    _fake_thumbnail(monkeypatch)
    await preview_capture_screen("what's on screen")

    # Between the preview and the call, the screen "changes" — a fresh
    # capture would now return something different.
    _fake_capture(monkeypatch, FRESH_JPEG)

    result = await capture_screen(CTX, "what's on screen")

    assert result.ok
    sent_b64, _prompt, _model = vision.calls[0]
    import base64

    assert base64.b64decode(sent_b64) == PREVIEW_JPEG, "sent the stale frame, not the fresh one"


async def test_no_stash_falls_back_to_a_fresh_capture(
    monkeypatch: pytest.MonkeyPatch, vision: StubVision
) -> None:
    """The trusted / always-allow / direct-call path: preview never ran, so
    there is nothing to have shown and nothing to be stale."""
    _fake_capture(monkeypatch, FRESH_JPEG)

    result = await capture_screen(CTX, "never previewed")

    assert result.ok
    import base64

    sent_b64, _prompt, _model = vision.calls[0]
    assert base64.b64decode(sent_b64) == FRESH_JPEG


async def test_a_stale_stash_is_not_reused(
    monkeypatch: pytest.MonkeyPatch, vision: StubVision
) -> None:
    """Longer than the 120s confirmation timeout would ever take, but not
    forever — a captured frame answered long after it was shown is not the
    frame the user actually approved sending."""
    _fake_capture(monkeypatch, PREVIEW_JPEG)
    _fake_thumbnail(monkeypatch)
    await preview_capture_screen("old question")
    # Back-date it past the TTL rather than sleeping in a test.
    jpeg, _created = _CAPTURES[_key("old question")]
    _CAPTURES[_key("old question")] = (jpeg, time.monotonic() - CAPTURE_TTL_S - 1)

    _fake_capture(monkeypatch, FRESH_JPEG)
    result = await capture_screen(CTX, "old question")

    assert result.ok
    import base64

    sent_b64, _prompt, _model = vision.calls[0]
    assert base64.b64decode(sent_b64) == FRESH_JPEG


async def test_the_stash_is_consumed_not_kept(
    monkeypatch: pytest.MonkeyPatch, vision: StubVision
) -> None:
    """A capture left behind after being used would answer a *later*,
    unrelated call with a stale frame — `organize_folder`'s manifest has the
    same one-shot rule for the same reason."""
    _fake_capture(monkeypatch, PREVIEW_JPEG)
    _fake_thumbnail(monkeypatch)
    await preview_capture_screen("q")

    assert _key("q") in _CAPTURES
    await capture_screen(CTX, "q")
    assert _key("q") not in _CAPTURES


# ── the vision call itself ───────────────────────────────────────────


async def test_the_question_becomes_the_prompt(
    monkeypatch: pytest.MonkeyPatch, vision: StubVision
) -> None:
    _fake_capture(monkeypatch, PREVIEW_JPEG)

    await capture_screen(CTX, "what error is shown?")

    _image, prompt, model = vision.calls[0]
    assert prompt == "what error is shown?"
    assert model == "gpt-4o"


async def test_the_description_becomes_the_summary(
    monkeypatch: pytest.MonkeyPatch, vision: StubVision
) -> None:
    _fake_capture(monkeypatch, PREVIEW_JPEG)
    vision.reply = "A terminal showing a stack trace."

    result = await capture_screen(CTX, "what's wrong?")

    assert result.ok
    assert result.summary == "A terminal showing a stack trace."


async def test_no_vision_provider_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    from sidecar.state import runtime

    monkeypatch.setattr(runtime, "providers", {})

    result = await capture_screen(CTX, "anything")

    assert not result.ok
    assert result.error == "no_vision_provider"
    assert "OpenAI" in result.summary


async def test_a_provider_that_cannot_do_vision_is_treated_the_same_as_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ollama and Gemini are both registered under `runtime.providers` too,
    and neither has `describe_image`. `getattr(..., None)` is what stops one
    of those answering this call and crashing instead of refusing cleanly."""
    from sidecar.providers import catalog
    from sidecar.state import runtime

    class NoVision:
        pass

    monkeypatch.setattr(runtime, "providers", {str(catalog.ProviderName.OPENAI): NoVision()})

    result = await capture_screen(CTX, "anything")

    assert not result.ok
    assert result.error == "no_vision_provider"


async def test_a_rate_limit_is_reported_not_raised(
    monkeypatch: pytest.MonkeyPatch, vision: StubVision
) -> None:
    _fake_capture(monkeypatch, PREVIEW_JPEG)
    vision.raises = ProviderRateLimited("OpenAI rate limit or quota reached")

    result = await capture_screen(CTX, "anything")

    assert not result.ok
    assert result.error == "vision_unavailable"
    assert "rate limit" in result.summary


async def test_an_unavailable_provider_names_the_fix(
    monkeypatch: pytest.MonkeyPatch, vision: StubVision
) -> None:
    _fake_capture(monkeypatch, PREVIEW_JPEG)
    vision.raises = ProviderUnavailable("No OpenAI API key is stored. Add one in Settings.")

    result = await capture_screen(CTX, "anything")

    assert not result.ok
    assert "Settings" in result.summary
