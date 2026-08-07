"""Speech recognition — faster-whisper on CPU (BUILD_SPEC §9 Phase 2).

CPU only per CLAUDE.md rule 2, and torch-free per rule 3: faster-whisper runs on
ctranslate2. `transformers[torch]` is only in its optional `conversion` extra,
which is deliberately not installed.

**Measured on this machine**, int8, greedy: latency is dominated by fixed cost
rather than utterance length across the range a spoken request occupies, which
is why the gate is a flat figure rather than a real-time factor.

**Transcription is serialised.** It was not, and that was the single worst
number in the whole voice path: every utterance in the room started its own
thread, they fought each other and Ollama and Kokoro for cores, and a real
session measured a 534ms median against a **5244ms p90 and a 34s worst case**.
Running them at once never made any of them finish sooner.

`beam_size=1` on purpose (§9 Phase 2): beam search roughly doubles latency for
marginal accuracy gain at this size.
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

import structlog

if TYPE_CHECKING:  # pragma: no cover
    import numpy as np

log = structlog.get_logger(__name__)

# `tiny.en` was measured as accurate as `base.en` and 221ms faster, and that
# measurement was **wrong in the way that mattered**: it used one synthesised
# US voice saying "Aria" cleanly. On a real voice both models mishear the name,
# tiny.en badly — a live session produced "Hallelujah.", "Ah, yeah." and "Oh
# yeah, what's your full name?" where "Aria" had been said every time.
#
# A corpus of one speaker cannot measure a wake word. `scripts/gate_name.py`
# now runs it across every voice kokoro has.
MODEL_SIZE = "base.en"

# **`hotwords="Aria"` was tried and measured worse, twice over.** Across six
# voices (`scripts/gate_name.py`):
#
#     no hint    woke 32/36 (89%)   0 false wakes
#     hotwords   woke 24/36 (67%)   1 false wake
#
# It biases the decoder toward the word, and the way that plays out is that the
# *leading* name gets treated as context already given and dropped: "Aria, what
# is the capital of Australia?" comes back as "What is the capital of
# Australia?". It also turned "Ah, yeah, that makes sense." into "Aria, that
# makes sense." and woke her. Do not re-add it without re-running that gate.
SAMPLE_RATE = 16_000
# Below this there is no speech worth sending to the model — a stray key press
# rather than an utterance.
MIN_AUDIO_MS = 200


class TranscriptionUnavailable(RuntimeError):
    """Speech input could not start. Never fatal — she still reads typing."""


@runtime_checkable
class SpeechToText(Protocol):
    """What the RPC layer depends on, so it never imports ctranslate2."""

    @property
    def ready(self) -> bool: ...

    async def start(self) -> None: ...

    async def transcribe(self, pcm: bytes, sample_rate: int) -> str: ...

    async def aclose(self) -> None: ...


def pcm16_to_float32(pcm: bytes) -> np.ndarray:
    """Little-endian int16 -> float32 in [-1, 1], which is what whisper wants."""
    import numpy as np

    return np.frombuffer(pcm, dtype="<i2").astype("float32") / 32768.0


def resample_to_16k(samples: np.ndarray, sample_rate: int) -> np.ndarray:
    """Nearest-neighbour resample.

    Crude on purpose: the renderer already asks WebAudio for 16kHz, so this only
    runs when the browser refused that rate and picked its own. Speech
    recognition on a 16kHz-target model does not notice the difference, and a
    proper resampler would mean another dependency for a fallback path.
    """
    import numpy as np

    if sample_rate == SAMPLE_RATE:
        return samples
    count = int(len(samples) * SAMPLE_RATE / sample_rate)
    if count <= 0:
        return samples[:0]
    index = (np.arange(count) * sample_rate / SAMPLE_RATE).astype(int)
    resampled: np.ndarray = samples[np.clip(index, 0, len(samples) - 1)]
    return resampled


class WhisperSTT:
    """Lazily loaded, warmed in the background, transcribed off the event loop."""

    def __init__(self, models_dir: Path, model_size: str = MODEL_SIZE) -> None:
        self._dir = models_dir
        self._model_size = model_size
        self._model: Any | None = None
        self._lock = asyncio.Lock()
        # **One transcription at a time.** `_lock` above guards loading only,
        # and without this every utterance in the room started its own thread:
        # they fight each other, Ollama and Kokoro for the same cores, and a
        # queue forms. Measured over a real session that showed up as a 534ms
        # median against a 5244ms p90 and a 34s worst case. Running them
        # concurrently never made them finish sooner.
        self._running = asyncio.Lock()
        # Utterances waiting behind the one in flight. A newer one means the
        # older is almost always room noise nobody is waiting on, so it is
        # dropped rather than transcribed late into an answer nobody wants.
        self._waiting = 0

    @property
    def ready(self) -> bool:
        return self._model is not None

    def _load(self) -> Any:
        from faster_whisper import WhisperModel

        return WhisperModel(
            self._model_size,
            device="cpu",  # rule 2: the GPU belongs to the language model
            compute_type="int8",
            download_root=str(self._dir),
        )

    async def start(self) -> None:
        """Load and warm. First use downloads ~150MB, which must not happen
        while someone is holding the talk button."""
        async with self._lock:
            if self._model is not None:
                return
            started = time.perf_counter()
            try:
                model = await asyncio.to_thread(self._load)
            except Exception as exc:
                raise TranscriptionUnavailable(
                    f"Could not load the {self._model_size} speech model: {exc}. "
                    f"It downloads to {self._dir} on first use, so this usually "
                    f"means no internet yet. Typing still works."
                ) from exc

            # A real pass: the first transcription pays a one-off cost.
            import numpy as np

            await asyncio.to_thread(
                lambda: list(
                    model.transcribe(
                        np.zeros(SAMPLE_RATE // 2, dtype="float32"),
                        beam_size=1,
                        language="en",
                    )[0]
                )
            )
            self._model = model
            log.info(
                "stt.ready",
                model=self._model_size,
                took_ms=round((time.perf_counter() - started) * 1000, 1),
            )

    async def transcribe(self, pcm: bytes, sample_rate: int) -> str:
        """One utterance to text. Empty string when nothing was said."""
        if self._model is None:
            raise TranscriptionUnavailable("Speech recognition is not started.")

        samples = pcm16_to_float32(pcm)
        duration_ms = len(samples) / max(sample_rate, 1) * 1000
        if duration_ms < MIN_AUDIO_MS:
            log.debug("stt.too_short", duration_ms=round(duration_ms, 1))
            return ""

        audio = resample_to_16k(samples, sample_rate)

        self._waiting += 1
        queued = time.perf_counter()
        try:
            async with self._running:
                # Someone spoke again while this waited. Whatever this was, it
                # is now stale — and finishing it would only delay the thing
                # they are actually waiting for.
                if self._waiting > 1:
                    log.info("stt.dropped_stale", behind=self._waiting - 1)
                    return ""

                started = time.perf_counter()
                text = await asyncio.to_thread(self._run, audio)
        finally:
            self._waiting -= 1

        log.info(
            "stt.transcribed",
            audio_ms=round(duration_ms, 1),
            took_ms=round((time.perf_counter() - started) * 1000, 1),
            queued_ms=round((started - queued) * 1000, 1),
            chars=len(text),
        )
        return text

    def _run(self, audio: np.ndarray) -> str:
        assert self._model is not None
        segments, _info = self._model.transcribe(
            audio,
            beam_size=1,  # greedy: beam search doubles latency here
            vad_filter=True,  # drops the silence around a held button
            language="en",
        )
        return " ".join(segment.text for segment in segments).strip()

    async def aclose(self) -> None:
        self._model = None
