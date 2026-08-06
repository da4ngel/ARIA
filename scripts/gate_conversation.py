"""Can she hold a conversation? Measured, not assumed.

    python scripts/gate_conversation.py

Every phrase is spoken by the TTS voice, resampled, and pushed through
`Listener.feed` as 80ms frames — the same path the renderer uses. Nothing is
stubbed but the model that answers, because what is under test is whether she
*hears* you, not what she says back.

**The number to beat is 15%.** A real session before this change answered 12 of
80 captured utterances; the rest were dropped for not naming her, including
every "Aria" said on its own and every question that followed one.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sidecar.core.listener import Listener, WakeMode
from sidecar.providers.stt import WhisperSTT, resample_to_16k
from sidecar.providers.tts import KokoroTTS
from sidecar.providers.vad import SileroVAD
from sidecar.rpc.events import Event, EventBus

MODELS = Path(__file__).resolve().parent.parent / "data" / "models"
SR = 16_000
FRAME = 1280

# (spoken phrase, must produce a turn, note)
Case = tuple[str, bool, str]

# Said one after another, in order, against one listener — the whole point is
# that what happened a moment ago changes what should happen next.
SCRIPT: list[Case] = [
    ("Aria.", False, "her name alone: arms her, no turn yet"),
    ("What is the capital of Australia?", True, "the question, no name needed"),
    # These three asserted the opposite an hour ago, when a 12s window let any
    # speech through after an answer. Flipped rather than deleted: the old
    # behaviour was wrong and the record should show it.
    ("And how many people live there?", False, "follow-up now needs her name"),
    ("So then he said he would be late again.", False, "room speech, never hers"),
    ("Aria, what time is it?", True, "one breath, must not regress"),
    ("Tell me about the aria project.", False, "name mid-sentence is not a wake"),
]

# Said cold, with the windows shut. None of these may produce a turn.
COLD: list[Case] = [
    ("So then he said he would be late again.", False, "room speech"),
    ("Tell me about the aria project.", False, "name mid-sentence"),
    ("What is the capital of Australia?", False, "a question at nobody"),
    ("Maria, can you pass me that?", False, "a name one edit from hers"),
]


class Bus(EventBus):
    def __init__(self) -> None:
        super().__init__()
        self.seen: list[str] = []

    async def broadcast(self, method: Event | str, params: dict) -> None:
        self.seen.append(str(method))

    def saw(self, event: Event) -> bool:
        return str(event) in self.seen

    def forget(self) -> None:
        self.seen.clear()


class Conv:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def send(self, text: str, spoken: bool = False, **_: object) -> None:
        self.sent.append(text)

    async def cancel_active(self) -> int:
        return 0


async def say(tts: KokoroTTS, text: str) -> np.ndarray:
    pcm, rate = await tts.synthesize(text)
    return resample_to_16k(np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0, rate)


async def utter(listener: Listener, audio: np.ndarray) -> None:
    """Speak, then go quiet long enough to end the utterance."""
    padded = np.concatenate(
        [np.zeros(SR // 3, "float32"), audio, np.zeros(int(SR * 1.4), "float32")]
    )
    for i in range(0, len(padded) - FRAME, FRAME):
        await listener.feed(padded[i : i + FRAME])
    for _ in range(400):
        if not listener._jobs:  # noqa: SLF001
            break
        await asyncio.sleep(0.005)


async def run(
    label: str,
    cases: list[Case],
    fresh_each: bool,
    tts: KokoroTTS,
    stt: WhisperSTT,
    vad: SileroVAD,
) -> tuple[int, int]:
    print(f"\n{label}")
    print("-" * 72)
    conv = Conv()
    listener = Listener(vad=vad, stt=stt, conversation=conv, bus=Bus(), mode=WakeMode.PHRASE)
    await listener.enable()

    right = 0
    for phrase, want_turn, note in cases:
        if fresh_each:
            # Shut every window, so each phrase is judged cold.
            await listener.disable()
            await listener.enable()
        before = len(conv.sent)
        await utter(listener, await say(tts, phrase))
        got = len(conv.sent) > before
        ok = got == want_turn
        right += ok
        mark = "ok " if ok else "BAD"
        got_text = repr(conv.sent[-1]) if got else "(no turn)"
        print(f"  {mark} {listener.state!s:9} {got_text:44} {note}")
        print(f"      said {phrase!r}")

    await listener.aclose()
    return right, len(cases)


# (spoken over her, must cut her off, must produce a turn, note)
Interrupt = tuple[str, bool, bool, str]

INTERRUPTS: list[Interrupt] = [
    ("Stop.", True, False, "stops her, and asks nothing"),
    ("Wait.", True, False, "same"),
    ("Aria, what about Sydney?", True, True, "her name cuts in and asks"),
    ("Mm, right, yeah.", False, False, "not for her — dips and resumes"),
    ("So anyway I told him it was fine.", False, False, "someone else in the room"),
]


async def run_interrupts(tts: KokoroTTS, stt: WhisperSTT, vad: SileroVAD) -> tuple[int, int]:
    """Talk over her and see what happens.

    This is the part that was unreachable: the guard read a state nothing ever
    wrote, so every one of these did nothing at all.
    """
    print("\ninterrupting her while she is speaking")
    print("-" * 72)
    conv = Conv()
    bus = Bus()
    listener = Listener(vad=vad, stt=stt, conversation=conv, bus=bus, mode=WakeMode.PHRASE)
    await listener.enable()

    right = 0
    for phrase, want_stop, want_turn, note in INTERRUPTS:
        bus.forget()
        before = len(conv.sent)
        listener.set_playing(True)
        await utter(listener, await say(tts, phrase))
        listener.set_playing(False)

        ducked = bus.saw(Event.AUDIO_DUCK)
        stopped = bus.saw(Event.AUDIO_STOP)
        resumed = bus.saw(Event.AUDIO_RESUME)
        turned = len(conv.sent) > before
        # Ducking is unconditional on sustained speech; what follows is the
        # decision, and it must be exactly one of stop or resume.
        ok = ducked and stopped == want_stop and resumed != want_stop and turned == want_turn
        right += ok
        outcome = "stopped" if stopped else ("resumed" if resumed else "nothing")
        print(f"  {'ok ' if ok else 'BAD'} duck={ducked!s:5} {outcome:8} turn={turned!s:5} {note}")
        print(f"      said {phrase!r} over her")

    await listener.aclose()
    return right, len(INTERRUPTS)


async def main() -> int:
    tts = KokoroTTS(MODELS)
    await tts.start()
    stt = WhisperSTT(MODELS / "whisper")
    await stt.start()
    vad = SileroVAD()
    vad.start()

    a = await run("a conversation, in order", SCRIPT, False, tts, stt, vad)
    b = await run("cold, windows shut — none of these may answer", COLD, True, tts, stt, vad)
    c = await run_interrupts(tts, stt, vad)

    await tts.aclose()
    await stt.aclose()

    right, total = a[0] + b[0] + c[0], a[1] + b[1] + c[1]
    print("\n" + "=" * 72)
    print(f"correct: {right}/{total}  ({right / total:.0%})")
    print("baseline before this change: 12/80 utterances answered (15%)")
    return 0 if right == total else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
