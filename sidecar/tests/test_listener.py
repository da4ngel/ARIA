"""Hands-free listening: endpointing, the wake word, and barge-in.

No audio device and no models. The wake word and VAD are both scripted, because
what needs testing is the state machine over their answers — whether a real
`hey jarvis` scores 0.6 is openWakeWord's problem, measured in the gate script.
"""

from __future__ import annotations

import asyncio
from typing import Any

import numpy as np
import pytest

from sidecar.core.listener import BARGE_IN_MS, Listener, ListenerState, strip_wake_word
from sidecar.providers.vad import FRAME_SAMPLES, SAMPLE_RATE, Endpoint, Utterance
from sidecar.rpc.events import AssistantState, Event, EventBus

FRAME_MS = FRAME_SAMPLES / SAMPLE_RATE * 1000  # 32ms
# What the renderer actually sends: openWakeWord's 80ms frame.
RENDER_FRAME = 1280


class ScriptedVAD:
    """Silero's seat, answering from a list instead of a model."""

    def __init__(self, threshold: float = 0.5) -> None:
        self.threshold = threshold
        self.speech = False
        self.ready = True

    def start(self) -> None:
        return None

    def feed(self, frame: np.ndarray) -> float:
        return 0.9 if self.speech else 0.1

    def reset(self) -> None:
        return None


class ScriptedWakeWord:
    def __init__(self, threshold: float = 0.5) -> None:
        self.threshold = threshold
        self.ready = True
        self.fire = False
        self.resets = 0

    async def start(self) -> None:
        return None

    async def feed(self, frame: np.ndarray) -> float:
        if self.fire:
            self.fire = False  # one detection per arming, like the debounce
            return 0.9
        return 0.1

    def reset(self) -> None:
        self.resets += 1

    async def aclose(self) -> None:
        return None


class ScriptedSTT:
    def __init__(self, text: str = "what time is it") -> None:
        self.text = text
        self.ready = True
        self.calls: list[int] = []

    async def start(self) -> None:
        return None

    async def transcribe(self, pcm: bytes, sample_rate: int) -> str:
        self.calls.append(len(pcm))
        return self.text

    async def aclose(self) -> None:
        return None


class FakeConversation:
    def __init__(self) -> None:
        self.sent: list[tuple[str, bool]] = []
        self.cancelled = 0

    async def send(self, text: str, spoken: bool = False, **_: object) -> None:
        self.sent.append((text, spoken))

    async def cancel_active(self) -> int:
        self.cancelled += 1
        return 1


class RecordingBus(EventBus):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[tuple[str, dict]] = []

    async def broadcast(self, method: Event | str, params: dict) -> None:
        self.events.append((str(method), params))

    def of(self, method: Event) -> list[dict]:
        return [p for m, p in self.events if m == str(method)]


def frame(samples: int = RENDER_FRAME) -> np.ndarray:
    return np.zeros(samples, dtype="float32")


@pytest.fixture
def parts():
    wake = ScriptedWakeWord()
    vad = ScriptedVAD()
    stt = ScriptedSTT()
    conversation = FakeConversation()
    bus = RecordingBus()
    listener = Listener(
        wake=wake,
        vad=vad,  # type: ignore[arg-type]
        stt=stt,
        conversation=conversation,  # type: ignore[arg-type]
        bus=bus,
    )
    return listener, wake, vad, stt, conversation, bus


async def drain(listener: Listener) -> None:
    """Transcription runs off the frame path, so tests must wait for it."""
    for _ in range(200):
        if not listener._jobs:  # noqa: SLF001
            return
        await asyncio.sleep(0.005)
    raise AssertionError("transcription did not finish")


# ── the wake phrase in the transcript ─────────────────────────────────


@pytest.mark.parametrize(
    ("heard", "expected"),
    [
        ("Hey Jarvis, what time is it?", "what time is it?"),
        ("hey jarvis what time is it", "what time is it"),
        ("Jarvis, open the project folder.", "open the project folder."),
        ("OK Jarvis — remind me at five.", "remind me at five."),
        ("what time is it", "what time is it"),
    ],
)
def test_strips_a_leading_wake_phrase(heard: str, expected: str) -> None:
    assert strip_wake_word(heard) == expected


def test_leaves_jarvis_alone_mid_sentence() -> None:
    """Only a leading phrase is the wake word. The rest is what was said."""
    said = "tell me about the jarvis project"
    assert strip_wake_word(said) == said


# ── off by default ────────────────────────────────────────────────────


async def test_ignores_frames_until_enabled(parts) -> None:
    listener, wake, _vad, _stt, conversation, _bus = parts
    wake.fire = True
    await listener.feed(frame())
    assert listener.state is ListenerState.OFF
    assert conversation.sent == []


async def test_enable_then_disable_returns_to_off(parts) -> None:
    listener, *_ = parts
    await listener.enable()
    enabled_state = listener.state
    await listener.disable()
    assert enabled_state is ListenerState.WAITING
    assert listener.state is ListenerState.OFF


# ── wake word to turn ─────────────────────────────────────────────────


async def test_wake_word_opens_capture_and_says_so(parts) -> None:
    """The gate is the orb reacting within 300ms, so the state change must
    happen on the detecting frame — not after transcription."""
    listener, wake, _vad, _stt, _conversation, bus = parts
    await listener.enable()

    wake.fire = True
    await listener.feed(frame())

    assert listener.state is ListenerState.CAPTURING
    assert bus.state is AssistantState.LISTENING


async def test_a_full_utterance_becomes_a_spoken_turn(parts) -> None:
    listener, wake, vad, stt, conversation, _bus = parts
    await listener.enable()

    wake.fire = True
    await listener.feed(frame())

    vad.speech = True
    for _ in range(10):  # ~800ms of speech
        await listener.feed(frame())
    vad.speech = False
    for _ in range(12):  # past the 700ms trailing silence
        await listener.feed(frame())

    await drain(listener)
    assert conversation.sent == [("what time is it", True)]
    assert listener.state is ListenerState.WAITING


async def test_a_cough_is_not_a_turn(parts) -> None:
    """Under MIN_SPEECH_MS of speech is a door or a chair, not a question."""
    listener, wake, vad, stt, conversation, _bus = parts
    await listener.enable()

    wake.fire = True
    await listener.feed(frame())

    vad.speech = True
    await listener.feed(frame(FRAME_SAMPLES))  # one 32ms frame
    vad.speech = False
    for _ in range(12):
        await listener.feed(frame())

    await drain(listener)
    assert conversation.sent == []
    assert stt.calls == []


async def test_a_silent_transcript_starts_no_turn(parts) -> None:
    listener, wake, vad, stt, conversation, _bus = parts
    stt.text = "   "
    await listener.enable()

    wake.fire = True
    await listener.feed(frame())
    vad.speech = True
    for _ in range(10):
        await listener.feed(frame())
    vad.speech = False
    for _ in range(12):
        await listener.feed(frame())

    await drain(listener)
    assert conversation.sent == []


async def test_waiting_never_endpoints_on_its_own(parts) -> None:
    """Without a wake word, silence is just silence — no capture, no turn."""
    listener, _wake, _vad, _stt, conversation, _bus = parts
    await listener.enable()
    for _ in range(50):  # 4s
        await listener.feed(frame())
    assert listener.state is ListenerState.WAITING
    assert conversation.sent == []


# ── barge-in ──────────────────────────────────────────────────────────


async def test_talking_over_her_stops_the_audio_and_the_turn(parts) -> None:
    listener, _wake, vad, _stt, conversation, bus = parts
    await listener.enable()
    await bus.set_state(AssistantState.SPEAKING)

    vad.speech = True
    for _ in range(int(BARGE_IN_MS / FRAME_MS) + 2):
        await listener.feed(frame(FRAME_SAMPLES))

    assert listener.state is ListenerState.CAPTURING
    assert conversation.cancelled == 1
    stops = bus.of(Event.AUDIO_STOP)
    assert stops and stops[0]["reason"] == "barge_in"


async def test_a_single_frame_of_noise_does_not_interrupt_her(parts) -> None:
    """One frame is a cough or her own voice leaking past echo cancellation."""
    listener, _wake, vad, _stt, conversation, bus = parts
    await listener.enable()
    await bus.set_state(AssistantState.SPEAKING)

    vad.speech = True
    await listener.feed(frame(FRAME_SAMPLES))
    vad.speech = False
    await listener.feed(frame(FRAME_SAMPLES))

    assert listener.state is ListenerState.WAITING
    assert conversation.cancelled == 0


async def test_barge_in_can_be_turned_off(parts) -> None:
    listener, _wake, vad, _stt, conversation, bus = parts
    listener.barge_in_enabled = False
    await listener.enable()
    await bus.set_state(AssistantState.SPEAKING)

    vad.speech = True
    for _ in range(20):
        await listener.feed(frame(FRAME_SAMPLES))

    assert listener.state is ListenerState.WAITING
    assert conversation.cancelled == 0


async def test_speech_while_she_is_quiet_is_not_a_barge_in(parts) -> None:
    """Only an interruption interrupts. Otherwise every noise in the room would
    open a recording."""
    listener, _wake, vad, _stt, conversation, _bus = parts
    await listener.enable()

    vad.speech = True
    for _ in range(20):
        await listener.feed(frame(FRAME_SAMPLES))

    assert listener.state is ListenerState.WAITING
    assert conversation.cancelled == 0


# ── endpointing arithmetic ────────────────────────────────────────────


def utterance(vad: ScriptedVAD, **kwargs: Any) -> Utterance:
    return Utterance(vad, **kwargs)  # type: ignore[arg-type]


def test_endpoints_after_the_trailing_silence() -> None:
    vad = ScriptedVAD()
    u = utterance(vad, trailing_silence_ms=700)

    vad.speech = True
    for _ in range(20):  # 640ms of speech
        assert u.feed(frame(FRAME_SAMPLES)) is None

    vad.speech = False
    silence_frames = 0
    while True:
        end = u.feed(frame(FRAME_SAMPLES))
        silence_frames += 1
        if end is not None:
            break

    assert end == Endpoint.SILENCE
    # 700ms of silence at 32ms a frame is 22 frames; it must not fire early.
    assert silence_frames * FRAME_MS >= 700


def test_a_pause_mid_sentence_does_not_end_the_turn() -> None:
    """Thinking for half a second in the middle of a question is not the end
    of the question."""
    vad = ScriptedVAD()
    u = utterance(vad, trailing_silence_ms=700)

    vad.speech = True
    for _ in range(10):
        u.feed(frame(FRAME_SAMPLES))
    vad.speech = False
    for _ in range(15):  # 480ms — under the threshold
        assert u.feed(frame(FRAME_SAMPLES)) is None
    vad.speech = True
    for _ in range(10):
        assert u.feed(frame(FRAME_SAMPLES)) is None


def test_silence_before_speech_never_endpoints() -> None:
    """The trailing-silence clock starts at the first word. Otherwise a wake
    word followed by a breath would end the turn before it began."""
    vad = ScriptedVAD()
    vad.speech = False
    u = utterance(vad, trailing_silence_ms=700, max_seconds=30)
    for _ in range(60):  # ~2s, well past the silence threshold
        assert u.feed(frame(FRAME_SAMPLES)) is None
    assert not u.heard_speech


def test_a_monologue_is_cut_off_at_the_cap() -> None:
    vad = ScriptedVAD()
    vad.speech = True
    u = utterance(vad, max_seconds=1.0)
    end = None
    for _ in range(60):
        end = u.feed(frame(FRAME_SAMPLES))
        if end is not None:
            break
    assert end == Endpoint.TOO_LONG
    assert u.duration_s >= 1.0
