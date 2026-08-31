"""The wake threshold: reachable at last, and only reported while armed.

`wake_word_threshold` has been a `Settings` field since Phase 2 stage 3 with
**nothing anywhere able to write it** — the only way to move it was an
environment variable and a restart, which is not something a wizard can offer.

Two things have to be true together, and each is a way the other fails
silently: the change has to reach the *running* listener (or the slider does
nothing until a restart and looks broken), and it has to be *stored* (or the
calibration somebody did evaporates at the next launch).
"""

from __future__ import annotations

import numpy as np
import pytest

from sidecar.core.listener import Listener, WakeMode
from sidecar.rpc.events import Event


class _FakeVad:
    """Silent. The barge-in check runs before the wake model and needs one."""

    threshold = 0.5

    def feed(self, frame: np.ndarray) -> float:
        return 0.0


class _FakeWake:
    """A wake model that scores whatever it is told to."""

    def __init__(self, score: float = 0.0, threshold: float = 0.5) -> None:
        self.threshold = threshold
        self._score = score
        self.fed = 0

    async def start(self) -> None: ...

    async def feed(self, frame: np.ndarray) -> float:
        self.fed += 1
        return self._score

    def reset(self) -> None: ...


def _listener(bus, wake: _FakeWake) -> Listener:
    """A listener with everything but the wake model stubbed out."""
    return Listener(
        vad=_FakeVad(),  # type: ignore[arg-type]
        stt=object(),  # type: ignore[arg-type]
        conversation=object(),  # type: ignore[arg-type]
        bus=bus,
        wake=wake,  # type: ignore[arg-type]
        mode=WakeMode.MODEL,
    )


class _Bus:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    async def broadcast(self, method: str, params: dict) -> None:
        self.events.append((str(method), params))


def test_the_threshold_is_a_live_attribute_not_a_construction_argument() -> None:
    """The whole reason a setter is possible at all."""
    wake = _FakeWake(threshold=0.5)
    listener = _listener(_Bus(), wake)
    assert listener.wake is not None
    listener.wake.threshold = 0.3
    assert wake.threshold == 0.3


def test_phrase_mode_has_no_wake_model_to_threshold() -> None:
    """`None` is a real answer, not a failure.

    Phrase mode is the default and gates on the transcript. A UI that could
    not tell "set to 0.4" from "there is nothing listening" would show a
    working slider on a machine with no weights on it.
    """
    listener = Listener(
        vad=_FakeVad(),  # type: ignore[arg-type]
        stt=object(),  # type: ignore[arg-type]
        conversation=object(),  # type: ignore[arg-type]
        bus=_Bus(),  # type: ignore[arg-type]
        mode=WakeMode.PHRASE,
    )
    assert listener.wake is None


async def test_no_score_is_broadcast_until_calibration_is_armed() -> None:
    """Frames arrive 12.5 times a second, beside Whisper and a 7B model.

    Broadcasting a number nobody is looking at, forever, is exactly the cost
    `VoiceAura` was rewritten to avoid.
    """
    bus = _Bus()
    listener = _listener(bus, _FakeWake(score=0.2))
    await listener._watch(np.zeros(1280, dtype="float32"))  # noqa: SLF001
    assert not [e for e in bus.events if e[0] == Event.WAKE_SCORE]


async def test_an_armed_calibration_reports_the_score_even_when_it_does_not_fire() -> None:
    """The below-threshold scores are the useful ones.

    A calibration that only reported successes could not tell "your voice
    scores 0.45 and the bar is 0.5" from "nothing was heard at all", which is
    the entire question somebody is opening this step to answer.
    """
    bus = _Bus()
    listener = _listener(bus, _FakeWake(score=0.42, threshold=0.5))
    listener.calibrate(30)
    await listener._watch(np.zeros(1280, dtype="float32"))  # noqa: SLF001

    scores = [params for method, params in bus.events if method == Event.WAKE_SCORE]
    assert len(scores) == 1
    assert scores[0] == {"score": 0.42, "threshold": 0.5, "fired": False}


async def test_calibration_expires_on_its_own() -> None:
    """A flag somebody has to turn off is one that gets left on."""
    bus = _Bus()
    listener = _listener(bus, _FakeWake(score=0.3))
    listener.calibrate(-1)  # already in the past
    await listener._watch(np.zeros(1280, dtype="float32"))  # noqa: SLF001
    assert not [e for e in bus.events if e[0] == Event.WAKE_SCORE]


async def test_zero_disarms_immediately() -> None:
    bus = _Bus()
    listener = _listener(bus, _FakeWake(score=0.3))
    listener.calibrate(30)
    listener.calibrate(0)
    await listener._watch(np.zeros(1280, dtype="float32"))  # noqa: SLF001
    assert not [e for e in bus.events if e[0] == Event.WAKE_SCORE]


@pytest.mark.parametrize("value", [0.0, -0.1, 1.5])
def test_the_range_is_the_one_the_score_can_actually_take(value: float) -> None:
    """A threshold of 0 wakes on silence; above 1 can never be reached.

    Both are settings that look like a choice and are a broken microphone.
    """
    assert not 0.0 < value <= 1.0
