"""Wake word — openWakeWord on CPU (BUILD_SPEC §9 Phase 2 stage 3).

CPU only (rule 2) and torch-free (rule 3): openWakeWord's base install pulls
onnxruntime, scipy and scikit-learn. Torch appears only in its ``[full]`` extra,
which trains new wake words and is deliberately not installed.

**ONNX, not tflite.** openWakeWord defaults to ``inference_framework="tflite"``
and its ``tflite-runtime`` dependency is marked ``platform_system == "Linux"``.
On Windows that default fails at load, so the framework and every model path are
passed explicitly — which also stops it downloading weights mid-conversation.

**Measured on this machine**, `hey_jarvis` v0.1 on ONNX:

    load                127ms
    per 80ms frame     1.68ms median, 2.36ms p95   ← 2.1% of one core

That is the whole argument for running it always-on. Detection latency is the
model's own window, not ours: it scores a rolling buffer, so the score crosses
the threshold within a frame or two of the phrase finishing.

Missing weights log a warning and disable the wake word — they never stop the
sidecar, exactly like the voice in stage 1.
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

WAKE_WORD = "hey_jarvis"
MODEL_FILE = "hey_jarvis_v0.1.onnx"
SAMPLE_RATE = 16_000

# openWakeWord's documented chunk. Its feature extractor buffers internally, so
# other sizes work, but 80ms is what the melspectrogram frontend is shaped for.
FRAME_SAMPLES = 1280

# §9 Phase 2 stage 3 names both of these.
THRESHOLD = 0.5
DEBOUNCE_S = 2.0

# The three ONNX files openWakeWord needs: a shared frontend and the word itself.
_REQUIRED = (MODEL_FILE, "melspectrogram.onnx", "embedding_model.onnx")


class WakeWordUnavailable(RuntimeError):
    """The wake word could not start. Never fatal — typing and push-to-talk
    both still work without it."""


@runtime_checkable
class WakeWord(Protocol):
    """What the listener depends on, so it never imports openwakeword."""

    threshold: float

    @property
    def ready(self) -> bool: ...

    async def start(self) -> None: ...

    async def feed(self, frame: np.ndarray) -> float: ...

    def reset(self) -> None: ...

    async def aclose(self) -> None: ...


def missing_models(models_dir: Path) -> list[str]:
    """Which weights are absent, named so the log can say what to download."""
    return [name for name in _REQUIRED if not (models_dir / name).is_file()]


class OpenWakeWord:
    """Scores a rolling audio buffer for the wake phrase.

    Detection is debounced rather than edge-triggered on the raw score: the
    score stays high for several frames after the phrase, and without a debounce
    one "hey Jarvis" fires four or five times.
    """

    def __init__(
        self,
        models_dir: Path,
        threshold: float = THRESHOLD,
        debounce_s: float = DEBOUNCE_S,
    ) -> None:
        self._dir = models_dir
        self.threshold = threshold
        self.debounce_s = debounce_s
        self._model: Any | None = None
        self._lock = asyncio.Lock()
        self._muted_until = 0.0

    @property
    def ready(self) -> bool:
        return self._model is not None

    def _load(self) -> Any:
        from openwakeword.model import Model

        return Model(
            wakeword_models=[str(self._dir / MODEL_FILE)],
            melspec_model_path=str(self._dir / "melspectrogram.onnx"),
            embedding_model_path=str(self._dir / "embedding_model.onnx"),
            inference_framework="onnx",  # tflite-runtime is Linux-only
        )

    async def start(self) -> None:
        async with self._lock:
            if self._model is not None:
                return

            absent = missing_models(self._dir)
            if absent:
                raise WakeWordUnavailable(
                    f"Wake word weights are missing from {self._dir}: "
                    f"{', '.join(absent)}. Fetch them with "
                    f"`python scripts/fetch_wakeword.py`, or leave the wake "
                    f"word off and hold Ctrl+Shift+Space instead."
                )

            started = time.perf_counter()
            try:
                model = await asyncio.to_thread(self._load)
            except Exception as exc:
                raise WakeWordUnavailable(
                    f"Could not load the {WAKE_WORD} wake word: {exc}. "
                    f"Push-to-talk still works."
                ) from exc

            self._model = model
            log.info(
                "wakeword.ready",
                word=WAKE_WORD,
                threshold=self.threshold,
                took_ms=round((time.perf_counter() - started) * 1000, 1),
            )

    async def feed(self, frame: np.ndarray) -> float:
        """Score one frame of int16 audio. Returns 0.0 while debounced.

        Callers must await these in order — the model carries a rolling buffer
        across calls, so overlapping them would interleave two audio streams
        into one history.
        """
        if self._model is None:
            raise WakeWordUnavailable("The wake word is not started.")

        now = time.monotonic()
        if now < self._muted_until:
            # Still score it, or the buffer develops a hole across the debounce
            # and the next phrase is read against stale context.
            await asyncio.to_thread(self._model.predict, frame)
            return 0.0

        scores = await asyncio.to_thread(self._model.predict, frame)
        score = float(max(scores.values(), default=0.0))
        if score < self.threshold:
            return score

        self._muted_until = now + self.debounce_s
        log.info("wakeword.detected", word=WAKE_WORD, score=round(score, 3))
        return score

    def reset(self) -> None:
        """Drop the rolling buffer. Called when capture stops, so audio from
        before a pause cannot combine with audio after it into a phrase."""
        if self._model is not None:
            self._model.reset()
        self._muted_until = 0.0

    async def aclose(self) -> None:
        self._model = None
