"""Stage 3 gate, for the parts a machine can check.

    python scripts/gate_wakeword.py

Measures three of BUILD_SPEC §9 Phase 2 stage 3's four numbers:

* **wake word -> reaction**, as frames between the end of the phrase and the
  score crossing the threshold;
* **false positives**, by feeding speech that is not the wake word and
  counting fires — a compressed stand-in for the hour of idle, not a
  replacement for it;
* **barge-in**, as the delay from speech onset to `audio.stop` going out.

**The fourth number needs a person.** "20 triggers with under 2 false
negatives" means a human saying "hey Jarvis" into a real microphone across a
real room; synthesised speech at zero distance says nothing about that. What
this script can tell you is whether the pipeline fires at all, which is the
thing worth knowing before you stand in front of it twenty times.
"""

from __future__ import annotations

import asyncio
import statistics
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sidecar.core.listener import BARGE_IN_MS, Listener
from sidecar.providers.stt import resample_to_16k
from sidecar.providers.tts import KokoroTTS
from sidecar.providers.vad import SileroVAD
from sidecar.providers.wakeword import FRAME_SAMPLES, OpenWakeWord
from sidecar.rpc.events import AssistantState, Event, EventBus

MODELS = Path(__file__).resolve().parent.parent / "data" / "models"
SAMPLE_RATE = 16_000

WAKE_PHRASES = [
    "Hey Jarvis.",
    "Hey Jarvis, what time is it?",
    "Hey Jarvis, open the project folder.",
    "Hey, Jarvis!",
    "Hey Jarvis, remind me at five.",
]

# Things a room says that are not the wake word. Deliberately includes near
# misses — the failure worth catching is firing on "hey" or on "Travis".
DISTRACTORS = [
    "What is the capital of France?",
    "Hey, can you pass me that?",
    "Travis said he would call back later.",
    "Set a timer for ten minutes.",
    "Jarvis is a character in those films.",
    "Hey there, how are you doing today?",
    "The meeting is at four o'clock on Thursday.",
    "Harvest season starts in early September.",
    "Please save the file and close the window.",
    "I was reading about service mesh architecture.",
]


class SilentBus(EventBus):
    def __init__(self) -> None:
        super().__init__()
        self.stamps: list[tuple[str, float]] = []

    async def broadcast(self, method: Event | str, params: dict) -> None:
        self.stamps.append((str(method), time.perf_counter()))


class NullConversation:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def send(self, text: str, spoken: bool = False, **_: object) -> None:
        self.sent.append(text)

    async def cancel_active(self) -> int:
        return 1


class NullSTT:
    ready = True

    async def start(self) -> None: ...
    async def transcribe(self, pcm: bytes, sample_rate: int) -> str:
        return ""

    async def aclose(self) -> None: ...


async def say(tts: KokoroTTS, text: str) -> np.ndarray:
    pcm, rate = await tts.synthesize(text)
    samples = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    return resample_to_16k(samples, rate)


def frames(audio: np.ndarray) -> list[np.ndarray]:
    count = len(audio) // FRAME_SAMPLES
    return [audio[i * FRAME_SAMPLES : (i + 1) * FRAME_SAMPLES] for i in range(count)]


async def main() -> int:
    tts = KokoroTTS(MODELS)
    await tts.start()
    wake = OpenWakeWord(MODELS / "openwakeword")
    await wake.start()

    failures: list[str] = []

    # ── 1. does the wake word fire, and how fast ────────────────────────
    print("\nwake word")
    print("-" * 62)
    # Measured against the end of the *wake phrase*, not the end of the clip.
    # "Hey Jarvis, what time is it?" should fire on "Jarvis" and leave the
    # question still being spoken — that is capture opening in time to hear it,
    # not a model firing late.
    bare = await say(tts, "Hey Jarvis.")
    wake_phrase_s = len(bare) / SAMPLE_RATE

    detections: list[float] = []
    for phrase in WAKE_PHRASES:
        audio = await say(tts, phrase)
        # Lead-in silence so the model does not start mid-word.
        lead = SAMPLE_RATE // 2
        padded = np.concatenate([np.zeros(lead, dtype="float32"), audio])
        wake.reset()

        fired_at: float | None = None
        best = 0.0
        for index, frame in enumerate(frames(padded)):
            i16 = (np.clip(frame, -1, 1) * 32767).astype("int16")
            score = await wake.feed(i16)
            best = max(best, score)
            if score >= wake.threshold and fired_at is None:
                fired_at = (index + 1) * FRAME_SAMPLES / SAMPLE_RATE

        clip_end = len(padded) / SAMPLE_RATE
        if fired_at is None:
            print(f"  MISS   peak {best:.2f}  {phrase!r}")
            continue

        lag = (fired_at - (lead / SAMPLE_RATE + wake_phrase_s)) * 1000
        detections.append(lag)
        remaining = (clip_end - fired_at) * 1000
        tail = f", {remaining:.0f}ms of speech still to come" if remaining > 250 else ""
        print(f"  fired  peak {best:.2f}  {lag:+6.0f}ms after the phrase{tail}")
        print(f"         {phrase!r}")

    if not detections:
        failures.append(
            "the wake word did not fire on any synthesised phrase — see the note "
            "below before treating this as a defect"
        )

    # ── 2. false positives ──────────────────────────────────────────────
    print("\nfalse positives")
    print("-" * 62)
    false_fires = 0
    spoken_s = 0.0
    for phrase in DISTRACTORS:
        audio = await say(tts, phrase)
        spoken_s += len(audio) / SAMPLE_RATE
        wake.reset()
        for frame in frames(audio):
            i16 = (np.clip(frame, -1, 1) * 32767).astype("int16")
            if await wake.feed(i16) >= wake.threshold:
                false_fires += 1
                print(f"  FIRED on {phrase!r}")
    # Silence, where an always-on model that drifts would show it.
    wake.reset()
    for frame in frames(np.zeros(SAMPLE_RATE * 60, dtype="float32")):
        if await wake.feed(frame.astype("int16")) >= wake.threshold:
            false_fires += 1
    print(f"  {false_fires} fires over {spoken_s:.0f}s of speech + 60s of silence")
    if false_fires:
        failures.append(f"{false_fires} false positive(s)")

    # ── 3. barge-in ─────────────────────────────────────────────────────
    print("\nbarge-in")
    print("-" * 62)
    vad = SileroVAD()
    await asyncio.to_thread(vad.start)
    bus = SilentBus()
    listener = Listener(
        wake=wake,
        vad=vad,
        stt=NullSTT(),  # type: ignore[arg-type]
        conversation=NullConversation(),  # type: ignore[arg-type]
        bus=bus,
    )
    await listener.enable()
    await bus.set_state(AssistantState.SPEAKING)

    interruption = await say(tts, "Stop, that is not what I asked.")
    started = time.perf_counter()
    consumed = 0
    for frame in frames(interruption):
        await listener.feed(frame)
        consumed += 1
        if any(m == str(Event.AUDIO_STOP) for m, _ in bus.stamps):
            break

    stops = [t for m, t in bus.stamps if m == str(Event.AUDIO_STOP)]
    if not stops:
        print("  never cut in")
        failures.append("barge-in did not fire")
    else:
        # Two different numbers, and confusing them is easy. Audio time is how
        # much of the interruption had to be spoken before she stopped — it
        # cannot go below BARGE_IN_MS by construction. Compute is how long the
        # models took on it, and that is what the 150ms budget is about, since
        # frames here are fed as fast as they decode rather than in real time.
        audio_ms = consumed * FRAME_SAMPLES / SAMPLE_RATE * 1000
        compute_ms = (stops[0] - started) * 1000
        print(f"  {audio_ms:.0f}ms of speech before cutting in (floor {BARGE_IN_MS:.0f}ms)")
        print(f"  {compute_ms:.0f}ms of compute over those frames (budget 150ms)")
        if compute_ms > 150:
            failures.append(f"barge-in decision cost {compute_ms:.0f}ms, over the 150ms budget")

    await tts.aclose()

    print("\n" + "=" * 62)
    if detections:
        print(f"detection lag after the phrase: median {statistics.median(detections):+.0f}ms")
    print(f"false positives: {false_fires}")
    for failure in failures:
        print(f"FAIL: {failure}")
    print(
        "\nNot measured here: 20 spoken triggers with under 2 false negatives,\n"
        "and an hour of real idle. Both need a person and a microphone."
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
