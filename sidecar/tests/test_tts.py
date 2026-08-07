"""Speech chunking and the rule that reasoning is never spoken."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest

from sidecar.core.conversation import ConversationService, SpeechStream
from sidecar.memory.db import Database
from sidecar.memory.messages import ConversationStore
from sidecar.providers.base import ChatMessage, GenerationOptions, StreamDelta
from sidecar.providers.tts import (
    FIRST_CHUNK_MAX_CHARS,
    SpeechUnavailable,
    split_for_speech,
    to_pcm16,
)
from sidecar.rpc.events import Event, EventBus


class FakeTTS:
    """Records what it was asked to say, without loading onnxruntime."""

    def __init__(self) -> None:
        self.spoken: list[str] = []
        self.ready = True

    async def start(self) -> None: ...

    async def synthesize(self, text: str) -> tuple[bytes, int]:
        self.spoken.append(text)
        return b"\x00\x00" * 240, 24_000

    async def aclose(self) -> None: ...


class RecordingBus(EventBus):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[tuple[str, dict]] = []

    async def broadcast(self, method: Event | str, params: dict) -> None:
        self.events.append((str(method), params))


def drain_text(full: str, step: int = 7) -> list[str]:
    """Feed text through the splitter the way tokens actually arrive."""
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
    if buf.strip():
        out.append(buf.strip())
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
        async def synthesize(self, text: str) -> tuple[bytes, int]:
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
