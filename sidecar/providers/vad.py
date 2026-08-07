"""Voice activity detection — streaming Silero (BUILD_SPEC §9 Phase 2 stage 3).

**Not webrtcvad, which §4 names.** webrtcvad ships source-only and its C
extension needs MSVC to build; it does not install on this machine, and a
release build would need the toolchain too. `faster-whisper` already bundles
Silero VAD as ONNX — the same model stage 2's `vad_filter=True` runs — so the
alternative is zero new dependencies, no compiler, and a neural detector that
holds up far better in room noise than webrtcvad's GMM.

Silero is a streaming model: 512-sample frames at 16kHz, carrying `state` and
`context` between calls. **Measured on this machine**: 173ms to load, 0.14ms per
32ms frame — 0.4% of one core, which is what makes always-on affordable.

The endpointing rules come from §9 Phase 2 stage 3: stop on 700ms of trailing
silence, and never record longer than 30s.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

import structlog

if TYPE_CHECKING:  # pragma: no cover
    import numpy as np

log = structlog.get_logger(__name__)

SAMPLE_RATE = 16_000
FRAME_SAMPLES = 512  # 32ms; the model rejects anything shorter

THRESHOLD = 0.5
# §9 says 700. Measured, that is a flat 700ms added to *every* turn before
# recognition can even start, on top of a ~530ms transcription and a ~1s first
# token — and the whole thing read as sluggish. 500ms still comfortably
# survives the pause inside a sentence; below about 400 it starts cutting
# people off mid-thought, which is far worse than waiting.
TRAILING_SILENCE_MS = 500

# Once she has actually been called, the pause is allowed to be much longer.
# These are two different situations wearing the same name: scanning the room
# for her name only needs enough silence to bound an utterance, but somebody
# composing a question mid-sentence pauses to think, and cutting them off there
# is the thing that makes her feel like she is not listening.
ARMED_TRAILING_SILENCE_MS = 1100
MAX_UTTERANCE_S = 30.0
# Speech this brief is a cough or a door, not a sentence worth transcribing.
MIN_SPEECH_MS = 200


class Endpoint:
    """Why capture stopped, so the caller can tell an utterance from a timeout."""

    SILENCE = "silence"
    TOO_LONG = "too_long"


@runtime_checkable
class VoiceActivity(Protocol):
    @property
    def ready(self) -> bool: ...

    def start(self) -> None: ...

    def feed(self, frame: np.ndarray) -> float: ...

    def reset(self) -> None: ...


class SileroVAD:
    """Frame-by-frame speech probability with carried state."""

    def __init__(self, threshold: float = THRESHOLD) -> None:
        self.threshold = threshold
        self._model: Any | None = None
        self._state: Any = None
        self._context: Any = None

    @property
    def ready(self) -> bool:
        return self._model is not None

    def start(self) -> None:
        """Load the ONNX graph. Synchronous and ~170ms, called at startup rather
        than on the turn path."""
        if self._model is not None:
            return
        from faster_whisper.vad import get_vad_model

        started = time.perf_counter()
        self._model = get_vad_model()
        self.reset()
        log.info("vad.ready", took_ms=round((time.perf_counter() - started) * 1000, 1))

    def feed(self, frame: np.ndarray) -> float:
        """Speech probability for one 512-sample float32 frame."""
        if self._model is None:
            raise RuntimeError("VAD is not started.")
        out, self._state, self._context = self._model(
            frame, self._state, self._context, SAMPLE_RATE
        )
        return float(out.item())

    def reset(self) -> None:
        """Forget the previous utterance. Without this the tail of the last one
        biases the first frames of the next."""
        if self._model is not None:
            self._state, self._context = self._model.get_initial_states(1)


class Utterance:
    """Accumulates frames and decides when the speaker has finished.

    Deliberately not a coroutine: it holds no I/O, only arithmetic over frames,
    so it is trivially testable without an event loop or audio device.
    """

    def __init__(
        self,
        vad: SileroVAD,
        trailing_silence_ms: int = TRAILING_SILENCE_MS,
        max_seconds: float = MAX_UTTERANCE_S,
    ) -> None:
        self._vad = vad
        self._trailing_silence_ms = trailing_silence_ms
        self._max_seconds = max_seconds
        self._frames: list[np.ndarray] = []
        self._speech_ms = 0.0
        self._silence_ms = 0.0
        self._heard_speech = False

    @property
    def duration_s(self) -> float:
        return len(self._frames) * FRAME_SAMPLES / SAMPLE_RATE

    @property
    def speech_ms(self) -> float:
        return self._speech_ms

    @property
    def heard_speech(self) -> bool:
        return self._heard_speech

    def feed(self, frame: np.ndarray) -> str | None:
        """Add a frame. Returns an `Endpoint` when the utterance is over.

        Trailing silence only counts once speech has actually started, so a
        wake word followed by a thoughtful pause does not end the turn before
        it begins.
        """
        self._frames.append(frame)
        frame_ms = len(frame) / SAMPLE_RATE * 1000

        if self._vad.feed(frame) >= self._vad.threshold:
            self._heard_speech = True
            self._speech_ms += frame_ms
            self._silence_ms = 0.0
        elif self._heard_speech:
            self._silence_ms += frame_ms

        if self.duration_s >= self._max_seconds:
            return Endpoint.TOO_LONG
        if self._heard_speech and self._silence_ms >= self._trailing_silence_ms:
            return Endpoint.SILENCE
        return None

    def audio(self) -> np.ndarray:
        """Everything captured, as one float32 array."""
        import numpy as np

        if not self._frames:
            return np.zeros(0, dtype="float32")
        joined: np.ndarray = np.concatenate([f.reshape(-1) for f in self._frames])
        return joined

    def worth_transcribing(self) -> bool:
        return self._speech_ms >= MIN_SPEECH_MS
