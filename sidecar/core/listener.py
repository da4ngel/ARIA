"""Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3).

The renderer opens the microphone and streams 80ms frames; **every decision
about them is made here**, in the sidecar, per CLAUDE.md rule 1. The renderer
never decides that a wake word fired or that a sentence ended — it forwards
audio and renders what it is told.

    waiting  --speech-->  capturing  --700ms silence-->  transcribe
       ^                                                     |
       |                          "aria, ..."? --yes--> turn  |
       +------------------------------------------------------+

**She answers to her own name, decided from the transcript** (`WakeMode.PHRASE`,
the default). openWakeWord ships six pretrained phrases and "aria" is not among
them, so gating on a model would mean answering to "hey jarvis" — the phrase its
weights happen to know. Instead the VAD opens capture on any speech and the
question is asked afterwards: did this start with her name?

The cost is real and worth saying plainly: **everything spoken near the
microphone gets transcribed** in order to be thrown away. It happens on this
machine, nothing is sent anywhere, and nothing that fails the check is kept —
but Whisper runs on the room, not only on her. `WakeMode.MODEL` is the cheap
alternative for anyone who would rather say "hey jarvis".

Three ways into `capturing`:

* **speech**, in phrase mode — the transcript decides afterwards;
* **the wake word**, in model mode, scored by openWakeWord on every frame;
* **barge-in**, when she is speaking and someone talks over her. That path
  stops playback and cancels generation before it starts recording, because
  the alternative is her finishing a paragraph into an interruption.

Barge-in is the one piece here that depends on hardware behaving: the
microphone hears her own voice out of the speakers. The renderer asks for echo
cancellation, and this requires a sustained run of speech rather than a single
frame, but on a machine with the speakers pointed at the microphone it can
still trip. `barge_in_enabled` turns it off without touching the wake word.
"""

from __future__ import annotations

import asyncio
import re
import time
from enum import StrEnum
from typing import TYPE_CHECKING

import structlog

from sidecar.providers.vad import (
    FRAME_SAMPLES as VAD_FRAME,
)
from sidecar.providers.vad import (
    SAMPLE_RATE,
    SileroVAD,
    Utterance,
)
from sidecar.rpc.events import AssistantState, Event, EventBus

if TYPE_CHECKING:  # pragma: no cover
    import numpy as np

    from sidecar.core.conversation import ConversationService
    from sidecar.providers.stt import SpeechToText
    from sidecar.providers.wakeword import WakeWord

log = structlog.get_logger(__name__)

# Sustained speech required to interrupt her, rather than one frame. A single
# frame trips on a cough, a chair, or a syllable of her own voice leaking past
# echo cancellation.
BARGE_IN_MS = 300.0

# Audio kept from before capture starts, so neither an interruption nor the
# name itself is lost. Must comfortably exceed SPEECH_ONSET_MS: in phrase mode
# the deciding word is the first one, and it is already spoken by the time the
# VAD agrees that speech is happening.
PREROLL_MS = 600.0

# Speech needed before phrase mode starts recording. Three VAD frames — long
# enough not to open on a single noisy one, short enough that the pre-roll
# still covers the run-up.
SPEECH_ONSET_MS = 96.0

# Her name, and what Whisper actually writes when it hears it. "Arya" and
# "Aria" are indistinguishable in speech and base.en picks either; "area" is a
# real word, but as the *first* word of an utterance spoken at a computer it is
# almost always the name. Extend this list rather than lowering the bar.
NAME_SPELLINGS = ("aria", "arya", "ariya", "area", "aaria")

# An optional greeting before it: "aria", "hey aria" and "ok aria" are one
# request, and no one says the same one every time.
_GREETING = r"(?:hey|hi|hello|ok|okay|yo)"

# Whisper punctuates with em and en dashes, so both belong in the separator
# class alongside the ASCII ones — "Aria — what time is it" is one utterance.
_AFTER_NAME = "[\\s,.!?:;\\-—–]*"  # noqa: RUF001 — the dashes are the point

_WAKE_PREFIX = re.compile(
    rf"^\W*(?:{_GREETING}\W+)?(?:{'|'.join(NAME_SPELLINGS)})\b{_AFTER_NAME}",
    re.IGNORECASE,
)

# The phrase openWakeWord's weights were trained on, which is not her name.
# Only used when that model is doing the gating.
_MODEL_WAKE_PREFIX = re.compile(r"^\W*(hey|hi|ok|okay)?\W*jarvis\b\W*", re.IGNORECASE)


def starts_with_wake_phrase(text: str) -> bool:
    """Was this utterance addressed to her?

    The whole of phrase mode rests on this one question: everything else the
    room says is transcribed, asked this, and thrown away.
    """
    return _WAKE_PREFIX.match(text.strip()) is not None


def strip_wake_word(text: str) -> str:
    """Remove a leading wake phrase. Leaves the name alone mid-sentence."""
    stripped = _WAKE_PREFIX.sub("", text.strip(), count=1)
    return _MODEL_WAKE_PREFIX.sub("", stripped, count=1).strip()


class ListenerState(StrEnum):
    OFF = "off"
    WAITING = "waiting"
    CAPTURING = "capturing"


class WakeMode(StrEnum):
    """How an utterance is decided to be for her.

    ``PHRASE`` gates on the transcript: the VAD opens capture on any speech,
    Whisper writes it down, and it becomes a turn only if it starts with her
    name. Any name works, which is the point — openWakeWord ships six
    pretrained phrases and "aria" is not one of them.

    The cost is honest and worth stating: **everything spoken near the
    microphone is transcribed** to decide whether to ignore it. It happens on
    this machine and nothing is sent anywhere, but Whisper runs on the room's
    speech rather than only on hers. ``MODEL`` is the cheap alternative and
    answers to "hey jarvis", the phrase its weights were trained on.
    """

    PHRASE = "phrase"
    MODEL = "model"


class Listener:
    """Owns the always-on audio path. One instance per process."""

    def __init__(
        self,
        *,
        vad: SileroVAD,
        stt: SpeechToText,
        conversation: ConversationService,
        bus: EventBus,
        wake: WakeWord | None = None,
        mode: WakeMode = WakeMode.PHRASE,
        barge_in: bool = True,
    ) -> None:
        # PHRASE mode needs no wake model at all — that is the point of it.
        if mode is WakeMode.MODEL and wake is None:
            raise ValueError(
                "WakeMode.MODEL needs a wake word model. Pass one, or use "
                "WakeMode.PHRASE, which gates on the transcript instead."
            )
        self._wake = wake
        self._mode = mode
        self._vad = vad
        self._stt = stt
        self._conversation = conversation
        self._bus = bus
        self.barge_in_enabled = barge_in

        self._state = ListenerState.OFF
        self._utterance: Utterance | None = None
        self._pending: np.ndarray | None = None  # float32 not yet a full VAD frame
        self._preroll: list[np.ndarray] = []
        self._speech_run_ms = 0.0
        self._lock = asyncio.Lock()
        self._jobs: set[asyncio.Task[None]] = set()

    @property
    def state(self) -> ListenerState:
        return self._state

    @property
    def enabled(self) -> bool:
        return self._state is not ListenerState.OFF

    @property
    def mode(self) -> WakeMode:
        return self._mode

    @property
    def wake_phrase(self) -> str:
        """What to say to get her attention, in the words a person would use."""
        return "aria" if self._mode is WakeMode.PHRASE else "hey jarvis"

    # ── on/off ──────────────────────────────────────────────────────────

    async def enable(self) -> None:
        """Begin accepting frames. The renderer opens the device separately —
        this only says the sidecar is willing to listen to it."""
        async with self._lock:
            if self._state is not ListenerState.OFF:
                return
            self._reset_buffers()
            self._reset_models()
            self._state = ListenerState.WAITING
            log.info("listener.enabled")

    async def disable(self) -> None:
        async with self._lock:
            if self._state is ListenerState.OFF:
                return
            self._state = ListenerState.OFF
            self._reset_buffers()
            self._reset_models()
            await self._bus.set_state(AssistantState.IDLE)
            log.info("listener.disabled")

    async def aclose(self) -> None:
        for job in list(self._jobs):
            job.cancel()
        await asyncio.gather(*self._jobs, return_exceptions=True)

    # ── the frame path ──────────────────────────────────────────────────

    async def feed(self, samples: np.ndarray) -> None:
        """One frame of float32 audio at 16kHz from the renderer.

        Frames are handled one at a time under a lock: both the wake word and
        the VAD carry state across calls, so two overlapping frames would
        interleave into a single, wrong history.
        """
        if self._state is ListenerState.OFF:
            return
        async with self._lock:
            if self._state is ListenerState.CAPTURING:
                await self._capture(samples)
            else:
                await self._watch(samples)

    async def _watch(self, samples: np.ndarray) -> None:
        """Waiting: decide whether this frame starts something worth hearing."""
        import numpy as np

        self._remember(samples)

        # Barge-in is the same test in both modes: is someone talking over her.
        speaking = self._bus.state is AssistantState.SPEAKING
        speech_ms = self._speech_ms(samples)
        if speaking and self.barge_in_enabled and speech_ms >= BARGE_IN_MS:
            await self._begin_capture(reason="barge_in", preroll=True)
            return

        if self._mode is WakeMode.PHRASE:
            # Any speech opens capture; the transcript decides afterwards
            # whether it was for her. Pre-roll is essential here in a way it
            # never was on the model path — the name is the *first* word, and
            # without it the deciding evidence is the part that got clipped.
            if not speaking and speech_ms >= SPEECH_ONSET_MS:
                await self._begin_capture(reason="speech", preroll=True)
            return

        assert self._wake is not None  # guaranteed by the constructor
        # `feed` returns 0.0 while debounced, so a single phrase cannot open
        # capture twice.
        frame = (np.clip(samples, -1.0, 1.0) * 32767).astype("int16")
        if await self._wake.feed(frame) >= self._wake.threshold:
            await self._begin_capture(reason="wake", preroll=False)

    async def _capture(self, samples: np.ndarray) -> None:
        """Capturing: accumulate until the speaker stops or runs out of time."""
        assert self._utterance is not None
        for frame in self._vad_frames(samples):
            endpoint = self._utterance.feed(frame)
            if endpoint is not None:
                await self._finish(endpoint)
                return

    # ── transitions ─────────────────────────────────────────────────────

    async def _begin_capture(self, *, reason: str, preroll: bool) -> None:
        import numpy as np

        if reason == "barge_in":
            # Silence her before anything else. Audio already queued in the
            # renderer keeps talking for seconds otherwise — the same reason
            # cancel() flushes before the task unwinds.
            await self._bus.broadcast(Event.AUDIO_STOP, {"reason": "barge_in"})
            cancelled = await self._conversation.cancel_active()
            log.info("listener.barge_in", cancelled_turns=cancelled)

        self._utterance = Utterance(self._vad)
        self._vad.reset()
        self._speech_run_ms = 0.0
        self._pending = None

        if preroll and self._preroll:
            seed = np.concatenate([f.reshape(-1) for f in self._preroll])
            for frame in self._vad_frames(seed):
                self._utterance.feed(frame)
        self._preroll.clear()

        self._state = ListenerState.CAPTURING
        # Before any I/O: the gate is orb-reacts-within-300ms of the wake word.
        await self._bus.set_state(AssistantState.LISTENING)
        log.info("listener.capturing", reason=reason)

    async def _finish(self, endpoint: str) -> None:
        """End of utterance. Transcription and the turn run off this path so a
        frame never waits on a model."""
        utterance = self._utterance
        self._utterance = None
        self._state = ListenerState.WAITING
        self._reset_buffers()
        self._reset_models()

        if utterance is None:
            return

        if not utterance.worth_transcribing():
            log.info(
                "listener.discarded",
                reason="too little speech",
                speech_ms=round(utterance.speech_ms),
                endpoint=endpoint,
            )
            await self._bus.set_state(AssistantState.IDLE)
            return

        audio = utterance.audio()
        log.info(
            "listener.endpointed",
            endpoint=endpoint,
            duration_s=round(utterance.duration_s, 2),
            speech_ms=round(utterance.speech_ms),
        )
        job = asyncio.create_task(self._transcribe_and_send(audio))
        self._jobs.add(job)
        job.add_done_callback(self._jobs.discard)

    async def _transcribe_and_send(self, audio: np.ndarray) -> None:
        import numpy as np

        started = time.perf_counter()
        try:
            pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype("<i2").tobytes()
            heard = await self._stt.transcribe(pcm, SAMPLE_RATE)
            addressed = starts_with_wake_phrase(heard)
            text = strip_wake_word(heard)
        except Exception as exc:  # noqa: BLE001 — a bad utterance must not end listening
            log.warning("listener.transcribe_failed", error=str(exc))
            await self._bus.set_state(AssistantState.IDLE)
            await self._bus.send_error(
                "transcribe_failed",
                f"Could not make out that one: {exc}. Try again, or type it.",
            )
            return

        if not text:
            log.info("listener.empty_transcript")
            await self._bus.set_state(AssistantState.IDLE)
            return

        if self._mode is WakeMode.PHRASE and not addressed:
            # The room was talking, not her. Nothing is kept and nothing is
            # sent anywhere — the transcript existed only to answer this.
            log.info("listener.not_addressed", chars=len(heard))
            await self._bus.set_state(AssistantState.IDLE)
            return

        log.info(
            "listener.heard",
            chars=len(text),
            took_ms=round((time.perf_counter() - started) * 1000, 1),
        )
        await self._conversation.send(text, spoken=True)

    # ── frame plumbing ──────────────────────────────────────────────────

    def _vad_frames(self, samples: np.ndarray) -> list[np.ndarray]:
        """Re-chunk arbitrary input into the 512 samples Silero requires.

        The renderer sends 80ms (1280 samples) because that is openWakeWord's
        frame; the VAD wants 32ms. Neither divides the other evenly, so the
        remainder is carried.
        """
        import numpy as np

        buffer = samples if self._pending is None else np.concatenate([self._pending, samples])
        count = len(buffer) // VAD_FRAME
        frames = [buffer[i * VAD_FRAME : (i + 1) * VAD_FRAME] for i in range(count)]
        self._pending = buffer[count * VAD_FRAME :]
        return frames

    def _speech_ms(self, samples: np.ndarray) -> float:
        """Length of the current unbroken run of speech, in ms."""
        for frame in self._vad_frames(samples):
            if self._vad.feed(frame) >= self._vad.threshold:
                self._speech_run_ms += len(frame) / SAMPLE_RATE * 1000
            else:
                self._speech_run_ms = 0.0
        return self._speech_run_ms

    def _remember(self, samples: np.ndarray) -> None:
        """Keep the last `PREROLL_MS` so barge-in does not lose its first word."""
        self._preroll.append(samples)
        budget = PREROLL_MS / 1000 * SAMPLE_RATE
        held = sum(len(f) for f in self._preroll)
        while self._preroll and held - len(self._preroll[0]) >= budget:
            held -= len(self._preroll.pop(0))

    def _reset_models(self) -> None:
        """Forget both rolling histories. Audio from before a pause must not
        combine with audio after it into a phrase that was never said."""
        if self._wake is not None:
            self._wake.reset()
        self._vad.reset()

    def _reset_buffers(self) -> None:
        self._utterance = None
        self._pending = None
        self._preroll.clear()
        self._speech_run_ms = 0.0
