"""Can she hear her own name? Across many voices, because one is not a test.

    python scripts/gate_name.py

**This script exists because an earlier one gave a false pass.**
`gate_latency.py` compared `base.en` and `tiny.en` on a single synthesised US
voice, found them equally accurate, and I switched to the faster one. On a real
voice both mishear the name — a live session logged "Hallelujah.", "Ah, yeah."
and "Oh yeah, what's your full name?" where "Aria" had been said each time. A
corpus of one speaker cannot measure a wake word.

So: every voice kokoro ships, saying the name alone and in front of a question,
scored by whether `starts_with_wake_phrase` actually fires. That is the only
thing that matters — not whether the transcript is pretty, but whether she
wakes up.

`hotwords="Aria"` was measured here too and is **not** used: it scored 24/36
against 32/36 without it, and produced a false wake. See `providers/stt.py`.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sidecar.core.listener import starts_with_wake_phrase
from sidecar.providers.stt import WhisperSTT, resample_to_16k
from sidecar.providers.tts import KokoroTTS

MODELS = Path(__file__).resolve().parent.parent / "data" / "models"
SR = 16_000

# Accents and pitches that differ acoustically, which is the entire point.
VOICES = ["af_heart", "af_bella", "am_michael", "am_adam", "bf_emma", "bm_george"]

PHRASES = [
    "Aria.",
    "Aria?",
    "Hey Aria.",
    "Aria, what is the capital of Australia?",
    "Aria, what time is it?",
    "Hey Aria, set a timer.",
]

# Must never wake her. Kept small but pointed: these are the shapes the name is
# actually confused with, so they are where a hint could do damage.
DECOYS = [
    "Oh yeah, I told him it was fine.",
    "Ah, yeah, that makes sense.",
    "And yeah, we should go.",
    "Maria, can you pass me that?",
]


async def clips(tts: KokoroTTS, voice: str, phrases: list[str]) -> list[tuple[str, np.ndarray]]:
    out = []
    tts.voice = voice
    for phrase in phrases:
        pcm, rate = await tts.synthesize(phrase)
        samples = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        out.append((phrase, resample_to_16k(samples, rate)))
    return out


async def score(
    stt: WhisperSTT, items: list[tuple[str, np.ndarray]]
) -> list[tuple[str, str, bool]]:
    results = []
    for phrase, audio in items:
        pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes()
        heard = await stt.transcribe(pcm, SR)
        results.append((phrase, heard, starts_with_wake_phrase(heard)))
    return results


async def main() -> int:
    tts = KokoroTTS(MODELS)
    await tts.start()

    print("synthesising across voices...")
    wake: dict[str, list[tuple[str, np.ndarray]]] = {}
    decoy: dict[str, list[tuple[str, np.ndarray]]] = {}
    for voice in VOICES:
        wake[voice] = await clips(tts, voice, PHRASES)
        decoy[voice] = await clips(tts, voice, DECOYS)
    await tts.aclose()

    for model in ("base.en", "tiny.en"):
        label = model
        stt = WhisperSTT(MODELS / "whisper", model_size=model)
        await stt.start()

        print(f"\n{label}")
        print("-" * 74)
        woke = total = 0
        false_wakes = 0
        misses: list[str] = []
        for voice in VOICES:
            results = await score(stt, wake[voice])
            hits = sum(1 for _, _, ok in results if ok)
            woke += hits
            total += len(results)
            for phrase, heard, ok in results:
                if not ok:
                    misses.append(f"{voice}: said {phrase!r} -> heard {heard!r}")

            decoys = await score(stt, decoy[voice])
            bad = [(p, h) for p, h, ok in decoys if ok]
            false_wakes += len(bad)
            for phrase, heard in bad:
                misses.append(f"{voice}: FALSE WAKE on {phrase!r} -> {heard!r}")

            print(f"  {voice:12} woke {hits}/{len(results)}   false wakes {len(bad)}")

        print(f"\n  woke on her name: {woke}/{total} ({woke / total:.0%})")
        print(f"  false wakes:      {false_wakes}/{len(VOICES) * len(DECOYS)}")
        for line in misses[:14]:
            print(f"    {line}")
        await stt.aclose()

    print("\nA synthesised voice is a proxy. The test that counts is saying it yourself.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
