"""Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3).

The renderer opens the microphone and streams 80ms frames; **every decision
about them is made here**, in the sidecar, per CLAUDE.md rule 1. The renderer
never decides that a wake word fired or that a sentence ended — it forwards
audio and renders what it is told.

    waiting  --wake word-->  capturing  --700ms silence-->  transcribe -> turn
       ^                                                                   |
       +-------------------------------------------------------------------+

Two ways into `capturing`:

* **the wake word**, scored by openWakeWord on every frame;
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

# Audio kept from before capture starts, so an interruption does not lose the
# word that triggered it. Not used on the wake-word path — there the preceding
# audio is the wake phrase itself.
PREROLL_MS = 400.0

# "hey jarvis, what time is it" arrives as one utterance and the phrase lands in
# the transcript. Strip it rather than sending it to the model as if it were
# part of the question.
_WAKE_PREFIX = re.compile(r"^\W*(hey|hi|ok|okay)?\W*jarvis\b\W*", re.IGNORECASE)


def strip_wake_word(text: str) -> str:
    """Remove a leading wake phrase. Leaves 'jarvis' alone mid-sentence."""
    return _WAKE_PREFIX.sub("", text, count=1).strip()


class ListenerState(StrEnum):
    OFF = "off"
    WAITING = "waiting"
    CAPTURING = "capturing"


class Listener:
    """Owns the always-on audio path. One instance per process."""

    def __init__(
        self,
        *,
        wake: WakeWord,
        vad: SileroVAD,
        stt: SpeechToText,
        conversation: ConversationService,
        bus: EventBus,
        barge_in: bool = True,
    ) -> None:
        self._wake = wake
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

    # ── on/off ──────────────────────────────────────────────────────────

    async def enable(self) -> None:
        """Begin accepting frames. The renderer opens the device separately —
        this only says the sidecar is willing to listen to it."""
        async with self._lock:
            if self._state is not ListenerState.OFF:
                return
            self._reset_buffers()
            self._wake.reset()
            self._vad.reset()
            self._state = ListenerState.WAITING
            log.info("listener.enabled")

    async def disable(self) -> None:
        async with self._lock:
            if self._state is ListenerState.OFF:
                return
            self._state = ListenerState.OFF
            self._reset_buffers()
            self._wake.reset()
            self._vad.reset()
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
        """Waiting: score the wake word, and watch for someone talking over her."""
        import numpy as np

        self._remember(samples)

        speaking = self._bus.state is AssistantState.SPEAKING
        if speaking and self.barge_in_enabled:
            if self._speech_ms(samples) >= BARGE_IN_MS:
                await self._begin_capture(reason="barge_in", preroll=True)
                return
        else:
            self._speech_run_ms = 0.0

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
        self._wake.reset()

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
            text = strip_wake_word(await self._stt.transcribe(pcm, SAMPLE_RATE))
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

    def _reset_buffers(self) -> None:
        self._utterance = None
        self._pending = None
        self._preroll.clear()
        self._speech_run_ms = 0.0
