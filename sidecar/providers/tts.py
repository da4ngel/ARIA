"""Speech synthesis — kokoro-onnx on CPU (BUILD_SPEC §9 Phase 2).

CPU only, per CLAUDE.md rule 2: the 6GB card holds the language model and
nothing else. onnxruntime rather than torch, per rule 3.

**Measured on this machine** (AMD CPU, `data/models/kokoro-v1.0.onnx`):

    first call        2381ms   ← warm-up, must never hit the user
    "Canberra."        420ms   → 1173ms of audio
    14-word sentence   945ms   → 2517ms of audio
    30-word sentence  1618ms   → 4971ms of audio

Two things follow, and they are the whole design:

1. **Warm it at startup.** The first synthesis is 5x slower than the rest. §12
   says the same about the language model and for the same reason.
2. **Real-time factor is ~0.35.** Synthesis runs about three times faster than
   playback, so once the first chunk is out the queue never starves — but only
   if the *first* chunk is short. That is why `split_for_speech` breaks the
   opening fragment early and lets later ones be whole sentences.
"""

from __future__ import annotations

import asyncio
import re
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

import structlog

if TYPE_CHECKING:  # pragma: no cover - import cost is real, typing is free
    import numpy as np

log = structlog.get_logger(__name__)

MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"

# Where the first chunk is allowed to break. Short openings start the audio
# sooner, and that is the entire latency budget for the first word.
#
# Measured end to end, with Ollama generating at the same time (which costs more
# than synthesising alone — RTF goes from ~0.35 to ~0.5 under contention):
#
#     8 chars   ->  441ms
#     85 chars  -> 2470ms
#
# So synthesis is roughly **230ms fixed + 26ms per character**. At 90 the first
# chunk alone cost 2.5s and first audio landed at 3.5s against a 900ms gate.
# Every character in the opening fragment is 26ms of silence, so it is kept
# close to the shortest thing worth saying.
FIRST_CHUNK_MIN_CHARS = 8
FIRST_CHUNK_MAX_CHARS = 32
# After the first, whole sentences: RTF 0.35 means synthesis stays ahead.
CHUNK_MAX_CHARS = 320

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
# Clause boundaries, used only to get the *first* fragment out early.
_CLAUSE_END = re.compile(r"(?<=[,;:])\s+")


class SpeechUnavailable(RuntimeError):
    """Voice could not start. Never fatal — she still types."""


@runtime_checkable
class TextToSpeech(Protocol):
    """What `core/conversation.py` depends on, so it never imports onnxruntime.

    Same seam as `LLMProvider`: the turn loop knows there is a voice, not which
    engine it is.
    """

    @property
    def ready(self) -> bool:
        """False until warmed. The turn loop stays silent rather than blocking."""
        ...

    async def start(self) -> None: ...

    async def synthesize(self, text: str) -> tuple[bytes, int]:
        """int16 PCM and its sample rate."""
        ...

    async def aclose(self) -> None: ...


def split_for_speech(text: str, *, is_first: bool) -> tuple[str | None, str]:
    """Take one speakable chunk off the front. Returns (chunk, remainder).

    `chunk` is None when nothing is ready yet, which is the normal answer while
    tokens are still arriving mid-sentence.
    """
    if not text.strip():
        return None, text

    limit = FIRST_CHUNK_MAX_CHARS if is_first else CHUNK_MAX_CHARS

    match = _SENTENCE_END.search(text)
    if match and match.start() <= limit:
        return text[: match.start()].strip(), text[match.end() :]

    # The opening sentence is long and the user is waiting on silence. Break at
    # a clause instead so audio starts; later chunks stay whole sentences.
    #
    # Every boundary is considered, not just the first. "Well, the answer
    # depends on what you mean, because..." has its first comma four characters
    # in — too short to be worth speaking alone — and checking only that one
    # made the whole 108-character sentence wait for its full stop.
    if is_first:
        for clause in _CLAUSE_END.finditer(text):
            if clause.start() < FIRST_CHUNK_MIN_CHARS:
                continue
            if clause.start() > limit:
                break
            return text[: clause.start()].strip(), text[clause.end() :]

    # No boundary and the buffer is long: emit anyway rather than stall, breaking
    # on a space so a word is never cut in half.
    #
    # The first chunk gives up waiting as soon as it passes the limit; later ones
    # tolerate twice it. A long opening sentence with no commas — "The capital of
    # Australia is Canberra and it has held that status since..." — is the
    # common shape of a reply, and making it wait for the full stop is the worst
    # case for how long the room stays silent.
    patience = limit if is_first else limit * 2
    if len(text) > patience:
        cut = text.rfind(" ", 0, limit)
        if cut > FIRST_CHUNK_MIN_CHARS:
            return text[:cut].strip(), text[cut + 1 :]

    if match:
        return text[: match.start()].strip(), text[match.end() :]
    return None, text


def to_pcm16(samples: np.ndarray) -> bytes:
    """float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and
    half the bytes of sending floats over the socket."""
    import numpy as np

    clipped = np.clip(samples, -1.0, 1.0)
    pcm: bytes = (clipped * 32767.0).astype("<i2").tobytes()
    return pcm


class KokoroTTS:
    """Lazily loaded, warmed in the background, synthesised off the event loop."""

    def __init__(
        self,
        models_dir: Path,
        voice: str = "af_heart",
        speed: float = 1.0,
        lang: str = "en-us",
    ) -> None:
        self._dir = models_dir
        self.voice = voice
        self.speed = speed
        self.lang = lang
        self._kokoro: Any | None = None
        self._lock = asyncio.Lock()
        self.sample_rate = 24_000

    @property
    def ready(self) -> bool:
        return self._kokoro is not None

    def _paths(self) -> tuple[Path, Path]:
        return self._dir / MODEL_FILE, self._dir / VOICES_FILE

    def _load(self) -> Any:
        model, voices = self._paths()
        if not model.exists() or not voices.exists():
            raise SpeechUnavailable(
                f"Speech model files are missing from {self._dir}. Download "
                f"{MODEL_FILE} and {VOICES_FILE} from the kokoro-onnx releases "
                f"page into that folder, or set voice_enabled=false to run silent."
            )
        from kokoro_onnx import Kokoro

        return Kokoro(str(model), str(voices))

    async def start(self) -> None:
        """Load and warm. The first synthesis is ~5x slower than the rest, and
        the user must never be the one who pays for it (§12)."""
        async with self._lock:
            if self._kokoro is not None:
                return
            started = time.perf_counter()
            kokoro = await asyncio.to_thread(self._load)
            # A real synthesis, not just a load: the cost is in the first run,
            # measured at 2381ms against ~420ms for every call after it.
            await asyncio.to_thread(
                kokoro.create, "Ready.", voice=self.voice, speed=self.speed, lang=self.lang
            )
            self._kokoro = kokoro
            log.info(
                "tts.ready",
                voice=self.voice,
                took_ms=round((time.perf_counter() - started) * 1000, 1),
            )

    async def synthesize(self, text: str) -> tuple[bytes, int]:
        """One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is
        blocking, and holding the event loop would stall the token stream that
        is still arriving."""
        if self._kokoro is None:
            raise SpeechUnavailable("Speech is not started.")

        started = time.perf_counter()
        samples, sample_rate = await asyncio.to_thread(
            self._kokoro.create, text, voice=self.voice, speed=self.speed, lang=self.lang
        )
        pcm = await asyncio.to_thread(to_pcm16, samples)
        audio_ms = len(samples) / sample_rate * 1000
        took_ms = (time.perf_counter() - started) * 1000
        log.debug(
            "tts.chunk",
            chars=len(text),
            took_ms=round(took_ms, 1),
            audio_ms=round(audio_ms, 1),
            # Above 1.0 and synthesis falls behind playback — the queue starves
            # and she stutters. Worth seeing in the log if it ever happens.
            rtf=round(took_ms / audio_ms, 2) if audio_ms else None,
        )
        return pcm, int(sample_rate)

    async def aclose(self) -> None:
        self._kokoro = None
