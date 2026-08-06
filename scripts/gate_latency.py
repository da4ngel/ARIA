"""Where the time goes between you stopping and her starting.

    python scripts/gate_latency.py

Measures the two stages the sidecar controls end to end — endpoint and speech
recognition — and compares the recognition model against the faster one, on
speed *and* on what it gets wrong. Reputation is not a measurement.

The rest of the chain (first token, first audio) is already logged per turn by
`core/conversation.py`; read it out of `data/logs/sidecar.log` rather than
re-measuring it here, since it depends on whatever the model is doing.
"""

from __future__ import annotations

import asyncio
import statistics
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sidecar.providers.stt import WhisperSTT, resample_to_16k
from sidecar.providers.tts import KokoroTTS
from sidecar.providers.vad import TRAILING_SILENCE_MS

MODELS = Path(__file__).resolve().parent.parent / "data" / "models"
SR = 16_000

# The kind of thing actually said to her, including the parts recognition is
# worst at: names, numbers, and words no language model expects.
PHRASES = [
    "Aria, what is the capital of Australia?",
    "Aria, set a timer for twenty five minutes.",
    "Aria, remind me to call Priya at half past four.",
    "Aria, how do I run pytest with coverage?",
    "Aria, what is the weather in Thiruvananthapuram?",
    "Aria, add eggs and sourdough to the shopping list.",
    "Aria, spell the word onomatopoeia.",
    "Aria, what is seventeen times forty three?",
]


# Whisper writes "17" where the speaker said "seventeen", and both are correct.
# Counting that as an error would make the comparison meaningless — which the
# first version of this script did, and it scored both models 8/8 wrong.
_NUMBERS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18",
    "nineteen": "19", "twenty": "20", "twentyfive": "25", "forty": "40",
    "fortythree": "43",
}


def normalise(text: str) -> set[str]:
    words = {w.strip(".,?!'\"").lower() for w in text.split()}
    return {_NUMBERS.get(w, w) for w in words if w}


def missing_words(said: str, heard: str) -> list[str]:
    """Words that actually went missing, ignoring differences nothing downstream
    cares about: how a number is spelled, and how her name is heard — which
    `starts_with_wake_phrase` matches fuzzily anyway."""
    from sidecar.core.listener import NAME_SPELLINGS

    want = normalise(said) - set(NAME_SPELLINGS)
    got = normalise(heard)
    # A digit run covers the words that make it up: "25" answers "twenty five".
    digits = "".join(w for w in got if w.isdigit())
    return sorted(w for w in want - got if not (w.isdigit() and w in digits))


async def measure(model_size: str, clips: list[tuple[str, np.ndarray]]) -> tuple[list[float], int]:
    stt = WhisperSTT(MODELS / "whisper", model_size=model_size)
    await stt.start()

    took: list[float] = []
    wrong = 0
    print(f"\n{model_size}")
    print("-" * 74)
    for said, audio in clips:
        pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes()
        start = time.perf_counter()
        heard = await stt.transcribe(pcm, SR)
        took.append((time.perf_counter() - start) * 1000)

        missed = missing_words(said, heard)
        if missed:
            wrong += 1
        mark = "ok " if not missed else "..."
        print(f"  {mark} {took[-1]:6.0f}ms  {heard!r}")
        if missed:
            print(f"       missed {sorted(missed)}")

    await stt.aclose()
    return took, wrong


async def main() -> int:
    tts = KokoroTTS(MODELS)
    await tts.start()

    clips: list[tuple[str, np.ndarray]] = []
    for phrase in PHRASES:
        pcm, rate = await tts.synthesize(phrase)
        samples = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        clips.append((phrase, resample_to_16k(samples, rate)))
    await tts.aclose()

    base_took, base_wrong = await measure("base.en", clips)
    tiny_took, tiny_wrong = await measure("tiny.en", clips)

    print("\n" + "=" * 74)
    print(f"{'model':10}{'median':>10}{'p90':>10}{'max':>10}{'clips with a missed word':>28}")
    for name, took, wrong in (
        ("base.en", base_took, base_wrong),
        ("tiny.en", tiny_took, tiny_wrong),
    ):
        ordered = sorted(took)
        p90 = ordered[int(len(ordered) * 0.9)]
        print(
            f"{name:10}{statistics.median(ordered):>8.0f}ms{p90:>8.0f}ms"
            f"{max(ordered):>8.0f}ms{f'{wrong}/{len(took)}':>28}"
        )
    print(f"\nplus a flat {TRAILING_SILENCE_MS}ms of silence before any of this starts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
