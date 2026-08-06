"""Hands-free listening: endpointing, the wake word, and barge-in.

No audio device and no models. The wake word and VAD are both scripted, because
what needs testing is the state machine over their answers — whether a real
`hey jarvis` scores 0.6 is openWakeWord's problem, measured in the gate script.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import numpy as np
import pytest

from sidecar.core.listener import (
    BARGE_IN_MS,
    Listener,
    ListenerState,
    WakeMode,
    is_stop_word,
    starts_with_wake_phrase,
    strip_wake_word,
)
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


_BUILT: list[Listener] = []


@pytest.fixture(autouse=True)
async def _drain_windows() -> AsyncIterator[None]:
    """Cancel every listening window a test left open.

    Not optional: ARMED and OPEN are `asyncio.sleep` tasks, and without this
    asyncio complains they were destroyed while pending — noise that would
    eventually hide a real leak.
    """
    yield
    for listener in _BUILT:
        await listener.aclose()
    _BUILT.clear()


def build(mode: WakeMode, text: str = "aria what time is it", windows: float = 30.0):
    wake = ScriptedWakeWord()
    vad = ScriptedVAD()
    stt = ScriptedSTT(text)
    conversation = FakeConversation()
    bus = RecordingBus()
    listener = Listener(
        vad=vad,  # type: ignore[arg-type]
        stt=stt,
        conversation=conversation,  # type: ignore[arg-type]
        bus=bus,
        wake=wake,
        mode=mode,
        # Long by default so a test never races the window shut; the one test
        # that cares about expiry passes a short one.
        armed_window_s=windows,
    )
    _BUILT.append(listener)
    return listener, wake, vad, stt, conversation, bus


@pytest.fixture
def parts():
    """openWakeWord gating — `hey jarvis` opens capture."""
    return build(WakeMode.MODEL, "what time is it")


@pytest.fixture
def phrase():
    """The default: any speech is captured, and the transcript decides."""
    return build(WakeMode.PHRASE)


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


async def test_talking_over_her_ducks_before_it_decides(parts) -> None:
    """It cannot stop her yet: whether this is an interruption depends on what
    was said, which is a transcription away."""
    listener, _wake, vad, _stt, conversation, bus = parts
    await listener.enable()
    await listener.set_playing(True)

    vad.speech = True
    for _ in range(int(BARGE_IN_MS / FRAME_MS) + 2):
        await listener.feed(frame(FRAME_SAMPLES))

    assert listener.state is ListenerState.CAPTURING
    assert bus.of(Event.AUDIO_DUCK), "volume must drop immediately"
    assert not bus.of(Event.AUDIO_STOP), "and nothing may stop yet"
    assert conversation.cancelled == 0


async def test_a_single_frame_of_noise_does_not_interrupt_her(parts) -> None:
    """One frame is a cough or her own voice leaking past echo cancellation."""
    listener, _wake, vad, _stt, conversation, bus = parts
    await listener.enable()
    await listener.set_playing(True)

    vad.speech = True
    await listener.feed(frame(FRAME_SAMPLES))
    vad.speech = False
    await listener.feed(frame(FRAME_SAMPLES))

    assert listener.state is ListenerState.WAITING
    assert not bus.of(Event.AUDIO_DUCK)
    assert conversation.cancelled == 0


async def test_barge_in_can_be_turned_off(parts) -> None:
    listener, _wake, vad, _stt, conversation, bus = parts
    listener.barge_in_enabled = False
    await listener.enable()
    await listener.set_playing(True)

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


# ── phrase mode: she answers to her own name ──────────────────────────


@pytest.mark.parametrize(
    ("heard", "expected"),
    [
        ("Aria, what time is it?", "what time is it?"),
        ("aria what time is it", "what time is it"),
        ("Hey Aria, open the project folder.", "open the project folder."),
        ("Arya — remind me at five.", "remind me at five."),
        # base.en writes the name several ways and none of them are wrong.
        ("Area, set a timer.", "set a timer."),
        ("Okay Aria, cancel that.", "cancel that."),
    ],
)
def test_the_name_opens_a_request(heard: str, expected: str) -> None:
    assert starts_with_wake_phrase(heard)
    assert strip_wake_word(heard) == expected


@pytest.mark.parametrize(
    "heard",
    [
        "what time is it",
        "tell me about the aria project",
        "I was listening to an aria from Tosca",
        "the area under the curve",
        "so I said to him, aria is the name she picked",
    ],
)
def test_the_room_is_not_a_request(heard: str) -> None:
    """The name has to be first. Anywhere else it is just a word."""
    assert not starts_with_wake_phrase(heard)


async def test_speech_is_captured_then_judged_by_the_transcript(phrase) -> None:
    listener, _wake, vad, _stt, conversation, _bus = phrase
    await listener.enable()

    vad.speech = True
    for _ in range(12):
        await listener.feed(frame())
    vad.speech = False
    for _ in range(12):
        await listener.feed(frame())

    await drain(listener)
    # The stub heard "aria what time is it", so the name is stripped and the
    # question goes through.
    assert conversation.sent == [("what time is it", True)]


async def test_speech_not_addressed_to_her_is_thrown_away(phrase) -> None:
    """Everything in the room is transcribed; only her name survives it."""
    listener, _wake, vad, stt, conversation, _bus = phrase
    stt.text = "so then he said he would be late again"
    await listener.enable()

    vad.speech = True
    for _ in range(12):
        await listener.feed(frame())
    vad.speech = False
    for _ in range(12):
        await listener.feed(frame())

    await drain(listener)
    assert stt.calls, "it must transcribe in order to decide"
    assert conversation.sent == []


async def test_phrase_mode_needs_no_wake_word_model() -> None:
    """The default path must work with nothing downloaded — that is the whole
    reason it is the default."""
    listener = Listener(
        vad=ScriptedVAD(),  # type: ignore[arg-type]
        stt=ScriptedSTT(),
        conversation=FakeConversation(),  # type: ignore[arg-type]
        bus=RecordingBus(),
        wake=None,
        mode=WakeMode.PHRASE,
    )
    await listener.enable()
    await listener.feed(frame())
    assert listener.enabled


def test_model_mode_without_a_model_is_refused_loudly() -> None:
    with pytest.raises(ValueError, match="WakeMode.PHRASE"):
        Listener(
            vad=ScriptedVAD(),  # type: ignore[arg-type]
            stt=ScriptedSTT(),
            conversation=FakeConversation(),  # type: ignore[arg-type]
            bus=RecordingBus(),
            wake=None,
            mode=WakeMode.MODEL,
        )


# ── the conversation ──────────────────────────────────────────────────
# The machine this replaces answered 12 of 80 utterances in a real session,
# because it required the name and the question in one breath. Everything
# below is a case it could not handle.


async def speak(listener: Listener, vad: ScriptedVAD, frames_of_speech: int = 10) -> None:
    """One utterance: speech, then enough silence to end it."""
    vad.speech = True
    for _ in range(frames_of_speech):
        await listener.feed(frame())
    vad.speech = False
    for _ in range(12):
        await listener.feed(frame())
    await drain(listener)


async def test_her_name_alone_arms_her_instead_of_being_dropped(phrase) -> None:
    """The whole bug: "Aria" strips to an empty string, and the first build
    threw it away without a sound."""
    listener, _wake, vad, stt, conversation, bus = phrase
    stt.text = "Aria."
    await listener.enable()

    await speak(listener, vad)

    assert listener.state is ListenerState.ARMED
    assert conversation.sent == [], "being called is not being asked"
    assert bus.of(Event.WAKE), "she must say she is listening"
    assert bus.state is AssistantState.LISTENING


async def test_the_question_after_her_name_needs_no_name(phrase) -> None:
    listener, _wake, vad, stt, conversation, _bus = phrase
    stt.text = "Aria."
    await listener.enable()
    await speak(listener, vad)
    assert listener.state is ListenerState.ARMED

    # A separate utterance, with no name in it at all.
    stt.text = "what is the capital of Australia"
    await speak(listener, vad)

    assert conversation.sent == [("what is the capital of Australia", True)]


async def test_a_follow_up_still_needs_her_name(phrase) -> None:
    """The opposite of what this file asserted an hour ago, on purpose.

    A 12s window once let any speech through after an answer, which is how she
    ends up answering a sentence meant for someone else in the room.
    """
    listener, _wake, vad, stt, conversation, _bus = phrase
    await listener.enable()

    stt.text = "aria what is the capital of Australia"
    await speak(listener, vad)
    assert listener.state is ListenerState.WAITING

    stt.text = "and how many people live there"
    await speak(listener, vad)

    assert conversation.sent == [("what is the capital of Australia", True)]


async def test_one_breath_still_works(phrase) -> None:
    """The old form must not regress just because a new one exists."""
    listener, _wake, vad, stt, conversation, _bus = phrase
    stt.text = "Aria, what time is it?"
    await listener.enable()

    await speak(listener, vad)

    assert conversation.sent == [("what time is it?", True)]


async def test_the_window_closes_and_the_name_is_required_again() -> None:
    """Otherwise one "aria" leaves the microphone answering the room forever."""
    listener, _wake, vad, stt, conversation, _bus = build(WakeMode.PHRASE, windows=0.05)
    stt.text = "Aria."
    await listener.enable()
    await speak(listener, vad)
    armed = listener.state

    # The window is 50ms in this test rather than ten seconds.
    await asyncio.sleep(0.12)
    assert armed is ListenerState.ARMED
    assert listener.state is ListenerState.WAITING

    stt.text = "so anyway I told him it was fine"
    await speak(listener, vad)
    assert conversation.sent == []


async def test_a_miss_is_shown_rather_than_swallowed(phrase) -> None:
    """64 silent drops in one session were indistinguishable from a dead app."""
    listener, _wake, vad, stt, conversation, bus = phrase
    stt.text = "so then he said he would be late"
    await listener.enable()

    await speak(listener, vad)

    assert conversation.sent == []
    misheard = bus.of(Event.MISHEARD)
    assert misheard and misheard[0]["text"] == "so then he said he would be late"


# ── interrupting her ──────────────────────────────────────────────────
# The guard on all of this used to read `AssistantState.SPEAKING`, which
# nothing in the sidecar ever set. The branch was unreachable, so saying
# "stop" over her did nothing at all — zero barge-in events across the whole
# log. `set_playing` is what makes any of it happen.


@pytest.mark.parametrize("word", ["stop", "Stop.", "wait", "never mind", "SHUT UP", "quiet"])
def test_stop_words_are_recognised(word: str) -> None:
    assert is_stop_word(word)


@pytest.mark.parametrize(
    "said",
    ["stop by the shop later", "wait until Tuesday", "I need quiet to think", "stopping now"],
)
def test_a_sentence_containing_one_is_not_an_interruption(said: str) -> None:
    """Matched whole, never as a prefix."""
    assert not is_stop_word(said)


async def interrupt(listener: Listener, vad: ScriptedVAD, heard: str, stt: ScriptedSTT) -> None:
    """Talk over her, long enough to trip the sustained-speech guard."""
    stt.text = heard
    await listener.set_playing(True)
    await speak(listener, vad, frames_of_speech=12)


async def test_stop_cuts_her_off_and_asks_nothing(phrase) -> None:
    listener, _wake, vad, stt, conversation, bus = phrase
    await listener.enable()

    await interrupt(listener, vad, "Stop.", stt)

    assert bus.of(Event.AUDIO_DUCK), "it drops the volume first"
    assert bus.of(Event.AUDIO_STOP), "then stops once it knows"
    assert conversation.cancelled == 1
    assert conversation.sent == [], '"stop" is not a question'


async def test_her_name_over_her_stops_her_and_listens(phrase) -> None:
    listener, _wake, vad, stt, conversation, bus = phrase
    await listener.enable()

    await interrupt(listener, vad, "Aria, what about Sydney?", stt)

    assert bus.of(Event.AUDIO_STOP)
    assert conversation.cancelled == 1
    assert conversation.sent == [("what about Sydney?", True)]


async def test_anything_else_lets_her_carry_on(phrase) -> None:
    """A cough, someone else in the room, or her own voice through the
    speakers. The volume dips and comes back; the sentence is not lost."""
    listener, _wake, vad, stt, conversation, bus = phrase
    await listener.enable()

    await interrupt(listener, vad, "mm, right, yeah", stt)

    assert bus.of(Event.AUDIO_DUCK)
    assert bus.of(Event.AUDIO_RESUME), "it must come back"
    assert not bus.of(Event.AUDIO_STOP)
    assert conversation.cancelled == 0
    assert conversation.sent == []


async def test_a_stop_word_when_she_is_quiet_does_nothing(phrase) -> None:
    """Otherwise "stop" said to someone else in the room is a command to her."""
    listener, _wake, vad, stt, conversation, bus = phrase
    stt.text = "Stop."
    await listener.enable()

    await speak(listener, vad)

    assert conversation.cancelled == 0
    assert conversation.sent == []
    assert not bus.of(Event.AUDIO_STOP)


async def test_playing_is_reported_not_guessed(phrase) -> None:
    """The bug this whole section exists for: the guard read a state that
    nothing ever wrote."""
    listener, _wake, vad, _stt, _conversation, bus = phrase
    await listener.enable()

    # Same speech, the only difference being whether audio is playing.
    vad.speech = True
    for _ in range(int(BARGE_IN_MS / FRAME_MS) + 2):
        await listener.feed(frame(FRAME_SAMPLES))
    assert not bus.of(Event.AUDIO_DUCK)


async def test_reaching_the_end_of_a_sentence_while_ducked_still_resumes(phrase) -> None:
    """13 ducks and 0 resumes in one log.

    She ducked, finished the sentence on her own, and `set_playing(False)`
    cleared the flag without an event — so the renderer's gain node stayed at
    20% for that answer and every answer after it.
    """
    listener, _wake, vad, _stt, _conversation, bus = phrase
    await listener.enable()
    await listener.set_playing(True)

    vad.speech = True
    for _ in range(int(BARGE_IN_MS / FRAME_MS) + 2):
        await listener.feed(frame(FRAME_SAMPLES))
    assert bus.of(Event.AUDIO_DUCK)

    # She simply finishes talking, before anything is decided about the speech.
    await listener.set_playing(False)

    assert bus.of(Event.AUDIO_RESUME), "volume must not be left down"


async def test_switching_her_off_mid_duck_does_not_leave_her_quiet(phrase) -> None:
    listener, _wake, vad, _stt, _conversation, bus = phrase
    await listener.enable()
    await listener.set_playing(True)

    vad.speech = True
    for _ in range(int(BARGE_IN_MS / FRAME_MS) + 2):
        await listener.feed(frame(FRAME_SAMPLES))
    assert bus.of(Event.AUDIO_DUCK)

    await listener.disable()
    assert bus.of(Event.AUDIO_RESUME)
