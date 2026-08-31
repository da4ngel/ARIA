"""Watch the clipboard, and refuse to remember the things that look like keys.

**Polls a sequence number, not the clipboard itself.**
`GetClipboardSequenceNumber()` is a cheap Win32 call that changes only when the
clipboard's contents change, and — unlike reading — it does not open the
clipboard. Opening the clipboard on a timer is what makes clipboard managers
fight with other applications for it; this touches it only when something has
actually been copied, which on an idle machine is never.

Shape borrowed from `memory/scheduler.py` and `persona/proactivity.py`: injected
clock, injected sleep, a `tick()` a test calls directly. No test sleeps, and no
test touches a real clipboard.
"""

from __future__ import annotations

import asyncio
import math
import re
from collections.abc import Awaitable, Callable
from typing import Any

import structlog

log = structlog.get_logger(__name__)

#: One second. The common case is an integer comparison against the last
#: sequence number, so this is cheap enough to be unnoticeable and fine-grained
#: enough that copying twice quickly still records both.
TICK_S = 1.0

#: Prefixes that identify a credential outright. Not a heuristic — every one of
#: these is a published, documented format, and a string starting with one is
#: a secret with no other plausible reading.
_KEY_PREFIXES = (
    "sk-",  # OpenAI, and much of what copies its format
    "sk_live_",
    "sk_test_",
    "rk_live_",
    "ABSK",  # Amazon Bedrock API key
    "AKIA",  # AWS access key id
    "ASIA",  # AWS temporary access key id
    "ghp_",  # GitHub personal access token
    "gho_",
    "ghs_",
    "github_pat_",
    "xox",  # Slack
    "AIza",  # Google API key
    "hf_",  # Hugging Face
    "glpat-",  # GitLab
    "dop_v1_",  # DigitalOcean
    "-----BEGIN",  # a private key of any flavour
)

#: A token that could be a secret purely by shape: long, unbroken, and mixing
#: character classes. Deliberately narrow — `\S{32,}` with no whitespace at all,
#: because a sentence of 32 characters contains spaces and a password does not.
_OPAQUE_TOKEN = re.compile(r"^[A-Za-z0-9+/=_\-.]{32,}$")

#: Foreground windows whose copies are never kept. Matched case-insensitively
#: against the window title.
_SECRET_APPS = (
    "1password",
    "bitwarden",
    "keepass",
    "lastpass",
    "dashlane",
    "nordpass",
    "credential manager",
    "keeper password",
    "proton pass",
)

#: Shannon entropy above which an unbroken token reads as random rather than as
#: a word. Measured against the alternatives: `"correcthorsebatterystaple"`
#: scores ~3.4, a base64 key scores ~5.5.
_ENTROPY_FLOOR = 4.0


def _entropy(text: str) -> float:
    if not text:
        return 0.0
    counts: dict[str, int] = {}
    for char in text:
        counts[char] = counts.get(char, 0) + 1
    total = len(text)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def looks_like_a_secret(text: str, *, window_title: str = "") -> bool:
    """Whether this copy should be left out of the history.

    **This is a reduction in exposure and not a guarantee, and every caller
    should read it that way.** There is no reliable way to tell a password from
    a word, and the failure this cannot avoid is a passphrase of ordinary
    English words — which is, by design, indistinguishable from a sentence.
    What it does catch is the large majority of what actually gets copied: keys
    with published prefixes, random-looking blobs, and anything taken out of a
    password manager.
    """
    stripped = text.strip()
    if not stripped:
        return False

    if any(word in window_title.casefold() for word in _SECRET_APPS):
        return True
    if any(stripped.startswith(prefix) for prefix in _KEY_PREFIXES):
        return True
    # A single unbroken token, long, and random-looking. All three, because any
    # two of them describe a URL or a file path.
    return bool(_OPAQUE_TOKEN.match(stripped)) and _entropy(stripped) >= _ENTROPY_FLOOR


def _sequence_number() -> int | None:
    """The clipboard's change counter, or None if the call is unavailable."""
    try:
        import win32clipboard

        return int(win32clipboard.GetClipboardSequenceNumber())
    except Exception:  # noqa: BLE001 — a missing API must not kill the loop
        return None


def _foreground_title() -> str:
    try:
        import win32gui

        return str(win32gui.GetWindowText(win32gui.GetForegroundWindow()))
    except Exception:  # noqa: BLE001
        return ""


class ClipboardWatcher:
    """Records what is copied. Everything is injected so a test drives it."""

    def __init__(
        self,
        *,
        remember: Callable[[str, str | None], Awaitable[Any]],
        read_text: Callable[[], str | None],
        sequence: Callable[[], int | None] = _sequence_number,
        window_title: Callable[[], str] = _foreground_title,
        tick_s: float = TICK_S,
        sleep: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        self._remember = remember
        self._read_text = read_text
        self._sequence = sequence
        self._window_title = window_title
        self._tick_s = tick_s
        self._sleep = sleep or asyncio.sleep
        self._last_sequence: int | None = None
        self._task: asyncio.Task[None] | None = None
        #: Counted so the honesty of the filter is observable rather than
        #: assumed — a run where this stays 0 forever means it has regressed.
        self.skipped_secrets = 0

    async def tick(self) -> None:
        """One pass. Never raises — a watcher that can die is worse than none."""
        try:
            await self._tick_once()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            log.warning("clipboard.tick_failed", error=str(exc))

    async def _tick_once(self) -> None:
        current = self._sequence()
        if current is None:
            return
        # First observation only arms the watcher. Without this, whatever
        # happened to be on the clipboard when ARIA started would be recorded as
        # though it had just been copied.
        if self._last_sequence is None:
            self._last_sequence = current
            return
        if current == self._last_sequence:
            return
        self._last_sequence = current

        text = self._read_text()
        if text is None:
            # An image, a file list, or rich text with no plain fallback.
            return

        title = self._window_title()
        if looks_like_a_secret(text, window_title=title):
            self.skipped_secrets += 1
            # Length only. Logging the content would defeat the entire point of
            # having refused to store it.
            log.info("clipboard.skipped_secret", chars=len(text))
            return

        await self._remember(text, title or None)

    async def _loop(self) -> None:
        while True:
            await self.tick()
            await self._sleep(self._tick_s)

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._loop(), name="clipboard.watch")
            log.info("clipboard.watching", tick_s=self._tick_s)

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None


__all__ = ["TICK_S", "ClipboardWatcher", "looks_like_a_secret"]
