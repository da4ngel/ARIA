"""Speech chunking and the rule that reasoning is never spoken."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest

from sidecar.core.conversation import ConversationService, SpeechStream
from sidecar.memory.db import Database
from sidecar.memory.messages import ConversationStore
from sidecar.providers.base import ChatMessage, GenerationOptions, StreamDelta
from sidecar.providers.tts import (
    FIRST_CHUNK_MAX_CHARS,
    MAX_SPOKEN_WORDS,
    KokoroTTS,
    SpeechUnavailable,
    shorten_for_speech,
    split_for_speech,
    to_pcm16,
)
from sidecar.rpc.events import Event, EventBus


class FakeTTS:
    """Records what it was asked to say, without loading onnxruntime."""

    def __init__(self) -> None:
        self.spoken: list[str] = []
        self.speeds: list[float | None] = []
        self.ready = True

    async def start(self) -> None: ...

    async def synthesize(self, text: str, *, speed: float | None = None) -> tuple[bytes, int]:
        self.spoken.append(text)
        self.speeds.append(speed)
        return b"\x00\x00" * 240, 24_000

    async def aclose(self) -> None: ...


class RecordingBus(EventBus):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[tuple[str, dict]] = []

    async def broadcast(self, method: Event | str, params: dict) -> None:
        self.events.append((str(method), params))


def drain_text(full: str, step: int = 7) -> list[str]:
    """Feed text through the splitter the way tokens actually arrive, then
    flush the tail the way `SpeechStream.finish` does — through
    `shorten_for_speech` in a loop, not appended raw. Mirroring that flush
    here is what lets a test on this helper actually prove something about
    the real tail path, not just the streaming one.
    """
    out: list[str] = []
    buf = ""
    first = True
    for i in range(0, len(full), step):
        buf += full[i : i + step]
        while True:
            chunk, buf = split_for_speech(buf, is_first=first)
            if not chunk:
                break
            out.append(chunk)
            first = False
    tail = buf.strip()
    while tail:
        piece, tail = shorten_for_speech(tail, "")
        if not piece:
            break
        out.append(piece)
    return out


# ── chunking ──────────────────────────────────────────────────────────


def test_a_short_sentence_is_spoken_whole() -> None:
    assert drain_text("Canberra.") == ["Canberra."]


def test_sentences_are_split_on_boundaries() -> None:
    assert drain_text("Canberra. It has been the capital since 1927.") == [
        "Canberra.",
        "It has been the capital since 1927.",
    ]


def test_the_first_chunk_breaks_early_at_a_clause() -> None:
    """The room is silent until the first chunk is synthesised, so the opening
    fragment breaks sooner than a full sentence would allow."""
    chunks = drain_text(
        "Well, the answer depends on what you mean by that, because there are "
        "several different interpretations here."
    )
    assert len(chunks) > 1
    assert len(chunks[0]) <= FIRST_CHUNK_MAX_CHARS


def test_a_long_opening_sentence_does_not_wait_for_its_full_stop() -> None:
    """The common shape of a reply, and the worst case for silence."""
    chunks = drain_text(
        "The capital of Australia is Canberra and it has held that status since "
        "nineteen twenty seven when it was chosen as a compromise."
    )
    assert len(chunks) > 1
    assert len(chunks[0]) <= FIRST_CHUNK_MAX_CHARS * 1.2


@pytest.mark.parametrize(
    "text",
    [
        "Canberra.",
        "Canberra. It has been the capital since 1927.",
        "Well, the answer depends on what you mean, because there are several views.",
        "One sentence with no terminator at all",
    ],
)
def test_no_words_are_lost_or_duplicated(text: str) -> None:
    spoken = " ".join(drain_text(text))
    assert spoken.split() == text.split()


# ── Phase 8: sentence-length enforcement ─────────────────────────────


def test_a_long_sentence_is_split_even_with_no_char_limit_pressure() -> None:
    """A clean, comma-free 24-word sentence sits well under CHUNK_MAX_CHARS,
    so only the word-count cap catches it — the whole reason it exists
    beside the character limit."""
    text = " ".join(f"word{i}" for i in range(24)) + "."
    chunks = drain_text(text)
    assert len(chunks) > 1
    assert len(chunks[0].split()) <= MAX_SPOKEN_WORDS


def test_a_long_sentence_prefers_a_clause_boundary_within_budget() -> None:
    """A comma inside the word budget is a more natural cut than a bare word
    count — every chunk still respects the cap either way."""
    text = (
        "This is a fairly long sentence, and it keeps going well past the "
        "point where a single breath would normally stop for air."
    )
    chunks = drain_text(text)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c.split()) <= MAX_SPOKEN_WORDS
    assert chunks[0].endswith(",")


def test_a_short_sentence_is_not_touched_by_length_enforcement() -> None:
    assert drain_text("Canberra.") == ["Canberra."]


def test_length_enforcement_loses_no_words_on_a_long_clause_free_sentence() -> None:
    """No commas to cut on — falls back to a hard word-count cut rather than
    dropping the tail."""
    text = " ".join(f"word{i}" for i in range(30))
    spoken = " ".join(drain_text(text))
    assert spoken.split() == text.split()


def test_shorten_for_speech_is_a_no_op_under_the_cap() -> None:
    chunk, remainder = shorten_for_speech("Short and sweet.", "rest")
    assert (chunk, remainder) == ("Short and sweet.", "rest")


def test_shorten_for_speech_cuts_at_the_last_comma_in_budget() -> None:
    words = [f"w{i}," if i == 10 else f"w{i}" for i in range(25)]
    chunk, remainder = shorten_for_speech(" ".join(words), "")
    assert chunk == " ".join(words[:11])  # up to and including "w10,"
    assert remainder == " ".join(words[11:])


def test_shorten_for_speech_hard_cuts_with_no_clause_boundary() -> None:
    words = [f"w{i}" for i in range(25)]
    chunk, remainder = shorten_for_speech(" ".join(words), "")
    assert chunk == " ".join(words[:MAX_SPOKEN_WORDS])
    assert remainder == " ".join(words[MAX_SPOKEN_WORDS:])


def test_shorten_for_speech_prepends_the_cut_tail_to_the_existing_remainder() -> None:
    words = [f"w{i}" for i in range(25)]
    _, remainder = shorten_for_speech(" ".join(words), "already queued")
    assert remainder == " ".join(words[MAX_SPOKEN_WORDS:]) + " already queued"


def test_nothing_is_emitted_mid_sentence() -> None:
    chunk, rest = split_for_speech("The capital of", is_first=True)
    assert chunk is None
    assert rest == "The capital of"


def test_blank_input_yields_nothing() -> None:
    assert split_for_speech("   ", is_first=True) == (None, "   ")


# ── encoding ──────────────────────────────────────────────────────────


def test_pcm16_is_little_endian_and_half_the_size_of_float32() -> None:
    import numpy as np

    pcm = to_pcm16(np.array([0.0, 1.0, -1.0], dtype="float32"))
    assert len(pcm) == 6
    assert pcm[0:2] == b"\x00\x00"
    assert pcm[2:4] == b"\xff\x7f"  # +32767


def test_pcm16_clips_rather_than_wrapping() -> None:
    """Wrapping turns a loud sample into a click at the opposite polarity."""
    import numpy as np

    pcm = to_pcm16(np.array([2.0, -2.0], dtype="float32"))
    assert pcm[0:2] == b"\xff\x7f"
    assert pcm[2:4] == b"\x01\x80"


# ── the rule that matters most ────────────────────────────────────────


async def test_reasoning_is_never_spoken(database: Database) -> None:
    """qwen3.5 streams reasoning into a separate channel. Speaking it aloud
    would be the worst bug this project has, so it gets its own test rather
    than an assumption."""

    class ThinkingProvider:
        name = "fake"

        async def available(self) -> bool:
            return True

        async def warm(self, model: str) -> float:
            return 1.0

        async def stream_chat(
            self, messages: list[ChatMessage], *, model: str,
            options: GenerationOptions | None = None,
            tools: list[dict[str, Any]] | None = None,
        ) -> AsyncIterator[StreamDelta]:
            yield StreamDelta(thinking="The user wants the capital. Let me recall.")
            yield StreamDelta(thinking="It is Canberra, not Sydney.")
            yield StreamDelta(text="Canberra.")
            yield StreamDelta(done=True)

        async def aclose(self) -> None: ...

    tts = FakeTTS()
    svc = ConversationService(
        store=ConversationStore(database),
        provider=ThinkingProvider(),
        bus=RecordingBus(),
        model="test-model",
        tts=tts,
    )
    try:
        await svc.send("what is the capital of Australia")
        for _ in range(400):
            if not svc._tasks:  # noqa: SLF001
                break
            await asyncio.sleep(0.01)
    finally:
        await svc.shutdown()

    assert tts.spoken == ["Canberra."]
    joined = " ".join(tts.spoken)
    assert "recall" not in joined and "Sydney" not in joined


async def test_speech_stays_silent_when_there_is_no_engine() -> None:
    """Voice is additive. No engine must not mean no reply."""
    stream = SpeechStream(None, RecordingBus(), 0.0)
    stream.feed("Canberra.")
    await stream.drain("t_1")
    await stream.finish("t_1")
    assert stream.active is False


async def test_a_failing_synthesiser_does_not_break_the_turn() -> None:
    class Broken(FakeTTS):
        async def synthesize(self, text: str, *, speed: float | None = None) -> tuple[bytes, int]:
            raise SpeechUnavailable("no model files")

    bus = RecordingBus()
    stream = SpeechStream(Broken(), bus, 0.0)
    stream.feed("Canberra. And more.")
    await stream.drain("t_1")
    await stream.finish("t_1")
    assert not [e for e in bus.events if e[0] == Event.AUDIO_OUT]


async def test_chunks_carry_an_index_so_playback_can_order_them() -> None:
    """Synthesis is dispatched per fragment, so a short chunk can finish before
    a longer one sent earlier. The renderer sorts on this."""
    tts = FakeTTS()
    bus = RecordingBus()
    stream = SpeechStream(tts, bus, 0.0)
    stream.feed("One. Two. Three.")
    await stream.drain("t_1")
    await stream.finish("t_1")

    emitted = [p for m, p in bus.events if m == Event.AUDIO_OUT]
    assert [p["index"] for p in emitted] == sorted(p["index"] for p in emitted)
    assert len(emitted) == 3


# ── Phase 8: affect-driven speed ─────────────────────────────────────


async def test_speech_stream_passes_its_speed_to_every_chunk() -> None:
    tts = FakeTTS()
    bus = RecordingBus()
    stream = SpeechStream(tts, bus, 0.0, speed=1.06)
    stream.feed("One. Two.")
    await stream.drain("t_1")
    await stream.finish("t_1")
    assert tts.speeds and all(s == 1.06 for s in tts.speeds)


async def test_speech_stream_defaults_to_no_speed_override() -> None:
    """Every pre-Phase-8 call site omits `speed` — the engine's own instance
    default must still apply, not some new hardcoded value."""
    tts = FakeTTS()
    bus = RecordingBus()
    stream = SpeechStream(tts, bus, 0.0)
    stream.feed("One.")
    await stream.drain("t_1")
    await stream.finish("t_1")
    assert tts.speeds == [None]


async def test_kokoro_synthesize_uses_the_override_when_given() -> None:
    """Direct against `KokoroTTS`, not `FakeTTS` — proves the override reaches
    `kokoro_onnx.Kokoro.create` and doesn't just get swallowed."""
    import numpy as np

    tts = KokoroTTS(models_dir=Path("unused"), speed=1.0)
    calls: list[float] = []

    class FakeKokoro:
        def create(
            self, text: str, *, voice: str, speed: float, lang: str
        ) -> tuple[np.ndarray, int]:
            calls.append(speed)
            return np.zeros(10, dtype="float32"), 24_000

    tts._kokoro = FakeKokoro()  # noqa: SLF001 — bypassing the real model load

    await tts.synthesize("hello", speed=1.08)
    await tts.synthesize("hello")  # no override -> falls back to self.speed

    assert calls == [1.08, 1.0]


async def test_cancel_tells_the_renderer_to_stop_playing(database: Database) -> None:
    """Audio already queued would otherwise keep talking after the stop button."""

    class Slow:
        name = "fake"

        async def available(self) -> bool:
            return True

        async def warm(self, model: str) -> float:
            return 1.0

        async def stream_chat(
            self, messages: list[ChatMessage], *, model: str,
            options: GenerationOptions | None = None,
            tools: list[dict[str, Any]] | None = None,
        ) -> AsyncIterator[StreamDelta]:
            for _ in range(200):
                await asyncio.sleep(0.02)
                yield StreamDelta(text="word ")

        async def aclose(self) -> None: ...

    bus = RecordingBus()
    svc = ConversationService(
        store=ConversationStore(database),
        provider=Slow(),
        bus=bus,
        model="test-model",
    )
    try:
        started = await svc.send("count")
        await asyncio.sleep(0.08)
        assert await svc.cancel(started.turn_id) is True
    finally:
        await svc.shutdown()

    assert [m for m, _ in bus.events if m == Event.AUDIO_STOP], "expected audio.stop"


def test_generation_options_are_untouched_by_speech() -> None:
    """Voice must not change what the model is asked for."""
    assert GenerationOptions().num_ctx == 8192
    assert ChatMessage(role="user", content="hi").content == "hi"
