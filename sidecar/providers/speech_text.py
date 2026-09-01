"""Markdown, said out loud.

**Nothing stripped markdown from the speech path, in either direction.**
`SpeechStream.feed` took `delta.text` exactly as the model wrote it, and
`voice.speak` was handed `turn.content` verbatim from the transcript, so Kokoro
has been receiving ``**bold**``, backticks, ``###`` heading hashes, table pipes
and entire code fences since Phase 2. `split_for_speech` splits on sentence
punctuation and never removed a character.

This lives in its own module rather than in `tts.py` because it is pure text
work with no onnxruntime anywhere near it — the same seam `providers/vad.py`
keeps — and because the streaming path and the speak button both import it
without either one owning it.

**What is deliberately kept.** The words inside emphasis, inline code and link
labels are all read: they are usually the most load-bearing part of a sentence
("run `npm run dev`" is useless without the command). What is dropped is the
punctuation that carries no sound, and the two things that are worse than
silence when spoken — a raw URL, and a code block.
"""

from __future__ import annotations

import re

__all__ = ["CODE_STAND_IN", "speech_text", "settled_for_speech"]

#: What a fenced code block becomes.
#:
#: Reading Python aloud a character at a time is useless, and it is *long* —
#: a thirty-line block is well over a minute of speech nobody can act on.
#: Saying so is the honest answer; silently dropping it would leave a reply
#: that skips from "here is how" straight to the next paragraph.
CODE_STAND_IN = "a code block"

# Fenced code, closed or running to the end of the text.
_FENCE = re.compile(r"(?ms)^[ \t]{0,3}(?P<f>```|~~~).*?(?:^[ \t]{0,3}(?P=f)[ \t]*$|\Z)")

_HEADING = re.compile(r"(?m)^[ \t]{0,3}#{1,6}[ \t]+")
_QUOTE = re.compile(r"(?m)^[ \t]*>[ \t]?")
_RULE = re.compile(r"(?m)^[ \t]{0,3}(?:[-*_][ \t]*){3,}$")
_BULLET = re.compile(r"(?m)^[ \t]*[-*+][ \t]+")

# `|---|:--:|` and friends — a row of pure punctuation, which has no sound.
_TABLE_DIVIDER = re.compile(r"(?m)^[ \t]*\|?[ \t:|-]*\|[ \t:|-]*$")
_TABLE_ROW = re.compile(r"(?m)^[ \t]*\|(?P<cells>.+)\|[ \t]*$")

_IMAGE = re.compile(r"!\[(?P<alt>[^\]]*)\]\([^)]*\)")
_LINK = re.compile(r"\[(?P<label>[^\]]+)\]\([^)]*\)")
_BARE_URL = re.compile(r"(?<![\w/])(?:https?://|www\.)\S+")

_CODE_INLINE = re.compile(r"`+([^`]*)`+")
_BOLD_ITALIC = re.compile(r"(?<!\w)(\*{1,3}|_{1,3})(?P<text>\S.*?\S|\S)\1(?!\w)")
_STRIKE = re.compile(r"~~(?P<text>.+?)~~")

_BLANK_LINES = re.compile(r"\n{3,}")
_SPACES = re.compile(r"[ \t]{2,}")


def speech_text(text: str) -> str:
    """Turn one piece of a reply into something worth hearing.

    Safe to call on a partial reply: an unclosed fence is treated as a code
    block that has not finished, which is what it is. Prefer handing it text
    that `settled_for_speech` has already vetted, so a half-written ``**`` is
    not read as two asterisks.
    """
    if not text:
        return text

    out = _FENCE.sub(f" {CODE_STAND_IN}. ", text)

    out = _TABLE_DIVIDER.sub("", out)
    # A table read cell by cell is a wall of pipes. Commas are what a person
    # would say, and they double as pauses for the synthesiser.
    out = _TABLE_ROW.sub(
        lambda m: ", ".join(cell.strip() for cell in m.group("cells").split("|") if cell.strip()),
        out,
    )

    out = _RULE.sub("", out)
    out = _HEADING.sub("", out)
    out = _QUOTE.sub("", out)
    out = _BULLET.sub("", out)

    # Labels before bare URLs, or the label's own URL is caught first.
    out = _IMAGE.sub(lambda m: m.group("alt"), out)
    out = _LINK.sub(lambda m: m.group("label"), out)
    # **A spoken URL is worse than no URL.** It is unusable by ear and takes
    # longer to say than the sentence around it. The screen still has it.
    out = _BARE_URL.sub("a link", out)

    # Inline code keeps its contents: it is usually the filename or the command
    # the whole sentence is about.
    out = _CODE_INLINE.sub(lambda m: m.group(1), out)
    out = _STRIKE.sub(lambda m: m.group("text"), out)
    out = _BOLD_ITALIC.sub(lambda m: m.group("text"), out)

    out = _BLANK_LINES.sub("\n\n", out)
    out = _SPACES.sub(" ", out)
    return out


# --- what is safe to convert yet -------------------------------------------

_FENCE_LINE = re.compile(r"(?m)^[ \t]{0,3}(```|~~~)")


def _open_fence_start(text: str) -> int | None:
    """Where an unterminated fence begins, if one does."""
    opener: str | None = None
    at: int | None = None
    for match in _FENCE_LINE.finditer(text):
        if opener is None:
            opener, at = match.group(1), match.start()
        elif match.group(1) == opener:
            opener, at = None, None
    return at


def _unbalanced_start(text: str) -> int | None:
    """Where a half-written inline marker begins, if one does."""
    candidates: list[int] = []

    if text.count("`") % 2 == 1:
        candidates.append(text.rfind("`"))
    if text.count("**") % 2 == 1:
        candidates.append(text.rfind("**"))

    link = _incomplete_link_start(text)
    if link is not None:
        candidates.append(link)

    return min(candidates) if candidates else None


def _incomplete_link_start(text: str) -> int | None:
    """Where a link that has not finished arriving begins.

    **A link has two halves and releasing between them is a real bug**, found
    by driving the actual stream rather than the function: holding only until
    the ``]`` arrived let ``[the docs]`` through as literal text, and the
    ``(url)`` that followed was then converted on its own. The whole thing has
    to be intact before `speech_text` ever sees it.
    """
    start = text.rfind("[")
    if start == -1:
        return None
    if text[start - 1 : start] == "!":  # an image, whose "!" is not speech
        start -= 1

    rest = text[start:]
    if "]" not in rest:
        return start

    after = rest[rest.index("]") + 1 :]
    # Nothing after the "]" yet: a "(" may still be on its way.
    if after == "":
        return start
    if after.startswith("(") and ")" not in after:
        return start
    return None


def settled_for_speech(text: str) -> tuple[str, str]:
    """Split raw model text into (safe to speak now, hold for later).

    **This is what makes stripping work on a stream at all.** Deltas arrive a
    few characters at a time, so ``**bold**`` routinely lands as ``**bo`` and
    then ``ld**``. Stripping each delta as it arrives would match neither half
    and read both asterisks aloud — the exact bug being fixed, arriving by a
    different route.

    So the tail is held back whenever it *could* be the first half of
    something: an unterminated fence, an odd backtick, an odd ``**``, an
    unclosed ``[``. It is retried on the next delta, and `SpeechStream.finish`
    flushes whatever is still held when the model stops.

    Held back only when genuinely unbalanced, never as a matter of course —
    holding the current line always would delay the opening fragment, and the
    872ms to first audio is the whole reason `split_for_speech` exists.
    """
    cuts = [at for at in (_open_fence_start(text), _unbalanced_start(text)) if at is not None]
    if not cuts:
        return text, ""
    cut = min(cuts)
    return text[:cut], text[cut:]
