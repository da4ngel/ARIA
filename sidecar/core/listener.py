"""Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3).

The renderer opens the microphone and streams 80ms frames; **every decision
about them is made here**, in the sidecar, per CLAUDE.md rule 1. The renderer
never decides that a wake word fired or that a sentence ended — it forwards
audio and renders what it is told.

    waiting  --"aria"-->  armed  --any speech-->  capturing  --> turn --+
       ^                    |  10s quiet                                 |
       +--------------------+---------------------------------------------+

**Saying her name arms her; the question is a separate sentence.** The first
build required both in one continuous breath, and measured over a real session
it answered 12 of 80 utterances — everything else was dropped for not naming
her, including every "Aria" said on its own and every question that followed
one. `ARMED` is the window in which the name is not required, because she has
just been called.

**Every turn needs the name.** A follow-up window briefly did not: for 12s
after an answer, any speech became a turn. That is how she ends up answering a
sentence meant for someone else, so it was removed.

**She answers to her own name, decided from the transcript** (`WakeMode.PHRASE`,
the default). openWakeWord ships six pretrained phrases and "aria" is not among
them, so gating on a model would mean answering to "hey jarvis" — the phrase its
weights happen to know. Instead the VAD opens capture on any speech and the
question is asked afterwards: did this start with her name?

The cost is real and worth saying plainly: **everything spoken near the
microphone gets transcribed** in order to be thrown away. It happens on this
machine, nothing is sent anywhere, and nothing that fails the check is kept —
but Whisper runs on the room, not only on her. `WakeMode.MODEL` is the cheap
alternative for anyone who would rather say "hey jarvis".

Three ways into `capturing`:

* **speech** — inside a window it is the question; outside one the transcript
  decides afterwards whether it was for her;
* **the wake word**, in model mode, scored by openWakeWord on every frame;
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
from collections.abc import Callable
from difflib import SequenceMatcher
from enum import StrEnum
from typing import TYPE_CHECKING

import structlog

from sidecar.providers.vad import (
    ARMED_TRAILING_SILENCE_MS,
    SAMPLE_RATE,
    TRAILING_SILENCE_MS,
    SileroVAD,
    Utterance,
)
from sidecar.providers.vad import (
    FRAME_SAMPLES as VAD_FRAME,
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

# Audio kept from before capture starts, so neither an interruption nor the
# name itself is lost. Must comfortably exceed SPEECH_ONSET_MS: in phrase mode
# the deciding word is the first one, and it is already spoken by the time the
# VAD agrees that speech is happening.
PREROLL_MS = 600.0

# Speech needed before phrase mode starts recording. Three VAD frames — long
# enough not to open on a single noisy one, short enough that the pre-roll
# still covers the run-up.
SPEECH_ONSET_MS = 96.0

# Deciding whether an utterance was for her only needs its opening, because the
# name is the first word. Above this length, the opening is transcribed on its
# own first and the rest only if it turns out to be hers.
#
# **Only long ones.** A normal request is a few seconds and transcribes once;
# paying twice for those would add ~300ms to exactly the path the user is
# waiting on. What this saves is the monologue across the room, which today is
# transcribed in full so it can be thrown away.
PREFIX_CHECK_OVER_S = 4.0
PREFIX_S = 2.5

# How long she waits to be asked after being called by name.
#
# It exists because saying a name and then talking is how every voice assistant
# has trained people to behave, and requiring one continuous breath instead
# threw away 64 of 80 utterances in a measured session.
#
# **There is deliberately no follow-up window.** One briefly existed: for 12s
# after an answer, any speech became a turn. That is how she ends up answering a
# sentence meant for someone else in the room, so every turn now needs her name.
ARMED_WINDOW_S = 10.0

# Said on their own while she is talking, these stop her. Matched against the
# whole utterance rather than as a prefix, so "stop by the shop later" is a
# sentence and not an interruption.
STOP_WORDS = frozenset(
    {
        "stop",
        "wait",
        "hold on",
        "never mind",
        "nevermind",
        "shut up",
        "enough",
        "cancel",
        "quiet",
        "be quiet",
        "stop it",
    }
)


def is_stop_word(text: str) -> bool:
    """Is this whole utterance just a request to stop talking?"""
    return text.strip().strip(_SEPARATORS).lower() in STOP_WORDS

# How often to report the arrival rate of frames. ~20s at 12.5/s.
#
# This exists because "is she still hearing me with the window hidden" is not
# answerable by looking at the app: Chromium throttles renderers it thinks
# nobody is watching, and a throttled capture goes quiet without erroring.
# A rate well under FRAMES_EXPECTED_PER_S means the microphone has been
# suspended, whatever the UI says.
FRAME_REPORT_EVERY = 250
FRAMES_EXPECTED_PER_S = 12.5

# Her name, and what Whisper actually writes when it hears it. "Arya" and
# "Aria" are indistinguishable in speech and base.en picks either; "area" is a
# real word, but as the *first* word of an utterance spoken at a computer it is
# almost always the name. Extend this list rather than lowering the bar.
NAME_SPELLINGS = ("aria", "arya", "ariya", "area", "aaria")

# An optional greeting before it: "aria", "hey aria" and "ok aria" are one
# request, and no one says the same one every time.
#
# "hay" is in there because it is what Whisper writes for "hey" in front of a
# vowel — "Hey Aria, set a timer" came back as "Hay Area set a timer" on four
# of six voices, and was the only remaining miss in `scripts/gate_name.py`.
_GREETING = r"(?:hey|hay|hi|hello|ok|okay|yo)"

# Whitespace and punctuation that can follow the name — em and en dashes
# included, because Whisper writes both and "Aria — what time is it" is one
# utterance, not a name followed by a sentence about a dash.
_SEPARATORS = " ,.!?:;-—–"  # noqa: RUF001 — both dashes are deliberate
_AFTER_NAME = f"[\\s{re.escape(_SEPARATORS)}]*"

_WAKE_PREFIX = re.compile(
    rf"^\W*(?:{_GREETING}\W+)?(?:{'|'.join(NAME_SPELLINGS)})\b{_AFTER_NAME}",
    re.IGNORECASE,
)

# The phrase openWakeWord's weights were trained on, which is not her name.
# Only used when that model is doing the gating.
_MODEL_WAKE_PREFIX = re.compile(r"^\W*(hey|hi|ok|okay)?\W*jarvis\b\W*", re.IGNORECASE)


# Pulls the first word out, ignoring a greeting in front of it, so the fuzzy
# pass has something to compare.
_FIRST_WORD = re.compile(rf"^\W*(?:{_GREETING}\W+)?([A-Za-z']+)", re.IGNORECASE)


def _near_the_name(word: str) -> bool:
    """Is this first word a plausible mishearing of her name?

    `base.en` on a single short word is not reliable, and every miss was
    silent — 64 of them in one session. One edit away from a known spelling is
    the right bar: it catches "ariah", "arya", "aaria" and "aria" heard with a
    dropped letter, while three-letter words that merely rhyme fail the length
    check before the ratio is even considered.
    """
    lowered = word.lower()
    if len(lowered) < 3:
        return False
    for spelling in NAME_SPELLINGS:
        if abs(len(lowered) - len(spelling)) > 1:
            continue
        # The first letter must survive. Without this "Maria" is one edit from
        # "aria" and every Maria in earshot wakes her up.
        if lowered[0] != spelling[0]:
            continue
        # `difflib` rather than a hand-rolled Levenshtein: stdlib, and its
        # ratio over words this short is equivalent for our purposes.
        if SequenceMatcher(None, lowered, spelling).ratio() >= 0.8:
            return True
    return False


def starts_with_wake_phrase(text: str) -> bool:
    """Was this utterance addressed to her?

    The whole of phrase mode rests on this one question: everything else the
    room says is transcribed, asked this, and thrown away.

    Exact spellings first, then one fuzzy pass over the first word. The strict
    pass carries the common case; the fuzzy one exists because a name she does
    not recognise is indistinguishable, to the user, from an app that ignores
    them.
    """
    stripped = text.strip()
    if _WAKE_PREFIX.match(stripped) is not None:
        return True
    match = _FIRST_WORD.match(stripped)
    return match is not None and _near_the_name(match.group(1))


def strip_wake_word(text: str) -> str:
    """Remove a leading wake phrase. Leaves the name alone mid-sentence."""
    stripped = text.strip()
    before = stripped
    stripped = _WAKE_PREFIX.sub("", stripped, count=1)
    if stripped == before:
        # The fuzzy pass matched, so the exact one will not strip anything.
        # Drop the first word by hand rather than leaving a misheard name
        # sitting at the front of the question.
        match = _FIRST_WORD.match(before)
        if match is not None and _near_the_name(match.group(1)):
            stripped = before[match.end() :].lstrip(_SEPARATORS)
    return _MODEL_WAKE_PREFIX.sub("", stripped, count=1).strip()


class ListenerState(StrEnum):
    """Where she is in a conversation.

    ``WAITING`` and ``CAPTURING`` are the whole machine as first built, and it
    could not hold a conversation: the name and the question had to arrive in
    one breath, because anything else was two utterances and the second one did
    not start with her name. Measured over a real session, 64 of 80 utterances
    were thrown away for exactly that reason.

    ``ARMED`` is the fix: a window in which the name is not required, because
    she has just been called and is waiting to be asked.

    A second window once followed an answer, so that a follow-up needed no
    name. It was removed on purpose — for those 12 seconds she would answer a
    sentence aimed at someone else in the room, which is worse than having to
    say her name twice.
    """

    OFF = "off"
    #: Only an utterance starting with her name gets through.
    WAITING = "waiting"
    #: Called, and waiting for the question. Any speech counts.
    ARMED = "armed"
    #: Recording an utterance.
    CAPTURING = "capturing"


class WakeMode(StrEnum):
    """How an utterance is decided to be for her.

    ``PHRASE`` gates on the transcript: the VAD opens capture on any speech,
    Whisper writes it down, and it becomes a turn only if it starts with her
    name. Any name works, which is the point — openWakeWord ships six
    pretrained phrases and "aria" is not one of them.

    The cost is honest and worth stating: **everything spoken near the
    microphone is transcribed** to decide whether to ignore it. It happens on
    this machine and nothing is sent anywhere, but Whisper runs on the room's
    speech rather than only on hers. ``MODEL`` is the cheap alternative and
    answers to "hey jarvis", the phrase its weights were trained on.
    """

    PHRASE = "phrase"
    MODEL = "model"


class Listener:
    """Owns the always-on audio path. One instance per process."""

    def __init__(
        self,
        *,
        vad: SileroVAD,
        stt: SpeechToText,
        conversation: ConversationService,
        bus: EventBus,
        wake: WakeWord | None = None,
        mode: WakeMode = WakeMode.PHRASE,
        barge_in: bool = True,
        armed_window_s: float = ARMED_WINDOW_S,
    ) -> None:
        # PHRASE mode needs no wake model at all — that is the point of it.
        if mode is WakeMode.MODEL and wake is None:
            raise ValueError(
                "WakeMode.MODEL needs a wake word model. Pass one, or use "
                "WakeMode.PHRASE, which gates on the transcript instead."
            )
        self._wake = wake
        self._mode = mode
        self._vad = vad
        self._stt = stt
        self._conversation = conversation
        self._bus = bus
        self.barge_in_enabled = barge_in
        self.armed_window_s = armed_window_s
        #: Monotonic deadline for wake-score reporting. Zero means off, which
        #: is what it always is unless somebody is looking at the calibration
        #: step right now.
        self._calibrating_until = 0.0

        self._state = ListenerState.OFF
        self._utterance: Utterance | None = None
        self._pending: np.ndarray | None = None  # float32 not yet a full VAD frame
        self._preroll: list[np.ndarray] = []
        self._speech_run_ms = 0.0
        self._lock = asyncio.Lock()
        self._jobs: set[asyncio.Task[None]] = set()
        self._frames = 0
        self._frames_since = time.monotonic()
        self._window: asyncio.Task[None] | None = None
        self._needs_name = True
        #: Offered every transcript before the wake-phrase gate; returns
        #: whether it was consumed as the answer to a spoken question.
        #: Injected rather than reaching for `runtime`, so a test drives it.
        self._answer_spoken: Callable[[str], bool] | None = None
        self._armed_until = 0.0
        # Whether sound is actually coming out of the speakers, reported by the
        # renderer that owns the audio graph.
        #
        # This used to read `bus.state is AssistantState.SPEAKING`, which
        # **nothing in the sidecar ever set** — so the barge-in branch below was
        # unreachable and interrupting her silently did nothing. The renderer is
        # the only thing that knows, including for the tail of audio still
        # playing after generation has finished, which is exactly when someone
        # interrupts.
        self._playing = False
        self._ducked = False

    @property
    def state(self) -> ListenerState:
        return self._state

    @property
    def enabled(self) -> bool:
        return self._state is not ListenerState.OFF

    @property
    def mode(self) -> WakeMode:
        return self._mode

    @property
    def wake(self) -> WakeWord | None:
        """The wake model, or None in PHRASE mode - which is the default.

        Exposed so the threshold can be changed on a running listener rather
        than only at construction. `None` is a real answer, not a failure:
        PHRASE mode gates on the transcript and has no model at all.
        """
        return self._wake

    async def set_playing(self, playing: bool) -> None:
        """Told by the renderer when audio starts and stops coming out.

        Transitions only, not a heartbeat: there is nothing to do while the
        answer is merely continuing.

        **Ending playback while ducked must still resume.** Clearing the flag
        on its own was the bug: she reached the end of a sentence, the flag was
        dropped with no event, and the renderer's gain node stayed at 20% — for
        that answer and every answer after it, until something else happened to
        call `stop()`. That is what "the interruption isn't working" looked
        like from the outside.
        """
        if playing == self._playing:
            return
        self._playing = playing
        if not playing:
            await self._unduck()
        log.debug("listener.playing", playing=playing)

    def calibrate(self, seconds: float) -> None:
        """Report wake scores on the bus for the next `seconds`.

        **Self-disarming, and that is deliberate.** A flag somebody has to
        turn off is one that gets left on — and this one broadcasts on every
        frame, 12.5 times a second, beside Whisper and a 7B model. Zero
        disarms it immediately, for closing the step.
        """
        self._calibrating_until = time.monotonic() + seconds if seconds > 0 else 0.0

    @property
    def wake_phrase(self) -> str:
        """What to say to get her attention, in the words a person would use."""
        return "aria" if self._mode is WakeMode.PHRASE else "hey jarvis"

    # ── on/off ──────────────────────────────────────────────────────────

    async def enable(self) -> None:
        """Begin accepting frames. The renderer opens the device separately —
        this only says the sidecar is willing to listen to it."""
        async with self._lock:
            if self._state is not ListenerState.OFF:
                return
            self._reset_buffers()
            self._reset_models()
            self._frames = 0
            self._frames_since = time.monotonic()
            self._state = ListenerState.WAITING
            log.info("listener.enabled")

    async def disable(self) -> None:
        async with self._lock:
            if self._state is ListenerState.OFF:
                return
            self._state = ListenerState.OFF
            self._reset_buffers()
            self._reset_models()
            await self._unduck()
            await self._bus.set_state(AssistantState.IDLE)
            log.info("listener.disabled")

    async def aclose(self) -> None:
        self._close_window()
        for job in list(self._jobs):
            job.cancel()
        await asyncio.gather(*self._jobs, return_exceptions=True)

    # ── the windows in which her name is not required ───────────────────

    def _close_window(self) -> None:
        """Cancel any open listening window. Safe to call repeatedly."""
        if self._window is not None:
            self._window.cancel()
            self._window = None

    async def _open_window(self, state: ListenerState, seconds: float, reason: str) -> None:
        """Listen without the name for a while, then stop.

        The timer matters as much as the window does: an assistant that stays
        open indefinitely after one "aria" is one that answers the room, and
        the microphone is already the thing people are right to be wary of.
        """
        self._close_window()
        self._state = state
        if state is ListenerState.ARMED:
            self._armed_until = time.monotonic() + seconds
        await self._bus.set_state(
            AssistantState.LISTENING if state is ListenerState.ARMED else AssistantState.IDLE
        )
        log.info("listener.window_open", state=str(state), seconds=seconds, reason=reason)

        async def expire() -> None:
            try:
                await asyncio.sleep(seconds)
            except asyncio.CancelledError:
                return
            async with self._lock:
                # Speech may have moved her on while the sleep was unwinding.
                if self._state is not state:
                    return
                self._state = ListenerState.WAITING
                self._window = None
                await self._bus.set_state(AssistantState.IDLE)
                log.info("listener.window_closed", was=str(state))

        self._window = asyncio.create_task(expire())

    # ── the frame path ──────────────────────────────────────────────────

    async def feed(self, samples: np.ndarray) -> None:
        """One frame of float32 audio at 16kHz from the renderer.

        Frames are handled one at a time under a lock: both the wake word and
        the VAD carry state across calls, so two overlapping frames would
        interleave into a single, wrong history.
        """
        if self._state is ListenerState.OFF:
            return
        self._count_frame()
        async with self._lock:
            if self._state is ListenerState.CAPTURING:
                await self._capture(samples)
            else:
                await self._watch(samples)

    async def _watch(self, samples: np.ndarray) -> None:
        """Waiting: decide whether this frame starts something worth hearing."""
        import numpy as np

        self._remember(samples)

        # Barge-in is the same test in both modes: is someone talking over her.
        speaking = self._playing
        speech_ms = self._speech_ms(samples)
        if speaking and self.barge_in_enabled and speech_ms >= BARGE_IN_MS:
            await self._begin_capture(reason="barge_in", preroll=True)
            return

        if self._mode is WakeMode.PHRASE:
            # Any speech opens capture; the transcript decides afterwards
            # whether it was for her. Pre-roll is essential here in a way it
            # never was on the model path — the name is the *first* word, and
            # without it the deciding evidence is the part that got clipped.
            if not speaking and speech_ms >= SPEECH_ONSET_MS:
                # Inside a window she has already been addressed, so this is
                # the question rather than a candidate for one.
                inside = self._state is ListenerState.ARMED
                self._close_window()
                await self._begin_capture(
                    reason="answering" if inside else "speech",
                    preroll=True,
                    needs_name=not inside,
                )
            return

        assert self._wake is not None  # guaranteed by the constructor
        # `feed` returns 0.0 while debounced, so a single phrase cannot open
        # capture twice.
        frame = (np.clip(samples, -1.0, 1.0) * 32767).astype("int16")
        score = await self._wake.feed(frame)
        fired = score >= self._wake.threshold
        if self._calibrating_until > time.monotonic():
            # **Only while calibration is armed.** A threshold is unpickable
            # without seeing what your own voice in your own room actually
            # scores, and the number is otherwise invisible — it exists for
            # one frame inside this comparison and is thrown away.
            await self._bus.broadcast(
                Event.WAKE_SCORE,
                {
                    "score": round(score, 3),
                    "threshold": self._wake.threshold,
                    "fired": fired,
                },
            )
        if fired:
            # The model firing *is* the confirmation, so this lights up
            # immediately and the transcript is not asked for the name again.
            await self._begin_capture(reason="wake", preroll=False, needs_name=False)

    async def _capture(self, samples: np.ndarray) -> None:
        """Capturing: accumulate until the speaker stops or runs out of time."""
        assert self._utterance is not None
        for frame in self._vad_frames(samples):
            endpoint = self._utterance.feed(frame)
            if endpoint is not None:
                await self._finish(endpoint)
                return

    # ── transitions ─────────────────────────────────────────────────────

    async def _begin_capture(self, *, reason: str, preroll: bool, needs_name: bool = True) -> None:
        import numpy as np

        # Remembered for `_transcribe_and_send`, which runs after the state has
        # already moved on and so cannot ask the state machine.
        self._needs_name = needs_name

        if reason == "barge_in":
            # **Duck, do not stop.** Whether this is really an interruption
            # depends on what was said, and that is a whole utterance plus a
            # transcription away — over a second, all of it with her still
            # talking. Dropping the volume now is immediate, makes the
            # microphone hear the speaker better, and a false alarm costs a dip
            # that comes back rather than a sentence lost.
            self._ducked = True
            await self._bus.broadcast(Event.AUDIO_DUCK, {"reason": "speech"})
            log.info("listener.ducked")

        # Someone answering her has room to think; someone who has not called
        # her yet only needs an utterance boundary.
        self._utterance = Utterance(
            self._vad,
            trailing_silence_ms=(
                TRAILING_SILENCE_MS if needs_name else ARMED_TRAILING_SILENCE_MS
            ),
        )
        self._vad.reset()
        self._speech_run_ms = 0.0
        self._pending = None

        if preroll and self._preroll:
            seed = np.concatenate([f.reshape(-1) for f in self._preroll])
            for frame in self._vad_frames(seed):
                self._utterance.feed(frame)
        self._preroll.clear()

        self._state = ListenerState.CAPTURING
        # **Only light up once she knows it is for her.** Every capture used to
        # set LISTENING, so the rim went blue for any noise in the room and
        # then quietly went out again — which says "I heard you" to someone she
        # is about to ignore. Blue now means she has been called: it is set on
        # arming, and a capture that follows arming keeps it.
        if not needs_name:
            await self._bus.set_state(AssistantState.LISTENING)
        log.info("listener.capturing", reason=reason)

    def set_answer_sink(self, sink: Callable[[str], bool] | None) -> None:
        """Where a spoken answer to a pending question should go."""
        self._answer_spoken = sink

    async def _rearm(self) -> bool:
        """Go back to waiting for the question, if there is time left on the
        window she was called with. Returns whether she is still armed."""
        remaining = self._armed_until - time.monotonic()
        if not self._needs_name and remaining > 0.5:
            await self._open_window(ListenerState.ARMED, remaining, reason="false start")
            return True
        return False

    async def _unduck(self) -> None:
        """Undo a duck, if one is outstanding.

        **Every exit from the interrupt path must pass through here.** It did
        not before: a ducked utterance too short to transcribe returned early,
        `_ducked` stayed set and no resume was sent, so she dropped to 20% and
        stayed there — 13 ducks and 0 resumes in one log. A duck with no
        matching resume is worse than never ducking, because it is silent,
        permanent, and looks like the interrupt simply not working.
        """
        if not self._ducked:
            return
        self._ducked = False
        await self._bus.broadcast(Event.AUDIO_RESUME, {})
        log.info("listener.resumed", reason="nothing to act on")

    async def _finish(self, endpoint: str) -> None:
        """End of utterance. Transcription and the turn run off this path so a
        frame never waits on a model."""
        utterance = self._utterance
        self._utterance = None
        self._state = ListenerState.WAITING
        self._reset_buffers()
        self._reset_models()

        if utterance is None:
            await self._unduck()
            return

        if not utterance.worth_transcribing():
            log.info(
                "listener.discarded",
                reason="too little speech",
                speech_ms=round(utterance.speech_ms),
                endpoint=endpoint,
            )
            await self._unduck()
            # A cough after "Aria" must not disarm her. It used to: the capture
            # opened, produced nothing, and dropped back to WAITING with the
            # window gone, so the question that followed was ignored for want
            # of a second "Aria".
            if not await self._rearm():
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
            def pcm_of(samples: np.ndarray) -> bytes:
                encoded: bytes = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2").tobytes()
                return encoded

            duration_s = len(audio) / SAMPLE_RATE
            if (
                self._needs_name
                and not self._ducked
                and duration_s > PREFIX_CHECK_OVER_S
            ):
                # Cheap first pass over the opening. If her name is not there,
                # the rest of a long stretch of room speech never gets read.
                opening = audio[: int(PREFIX_S * SAMPLE_RATE)]
                prefix = await self._stt.transcribe(pcm_of(opening), SAMPLE_RATE)
                if not starts_with_wake_phrase(prefix):
                    log.info(
                        "listener.not_addressed",
                        heard=prefix,
                        checked="opening only",
                        of_s=round(duration_s, 1),
                    )
                    await self._bus.broadcast(Event.MISHEARD, {"text": prefix})
                    await self._bus.set_state(AssistantState.IDLE)
                    return

            heard = await self._stt.transcribe(pcm_of(audio), SAMPLE_RATE)
            addressed = starts_with_wake_phrase(heard)
            text = strip_wake_word(heard)
        except Exception as exc:  # noqa: BLE001 — a bad utterance must not end listening
            log.warning("listener.transcribe_failed", error=str(exc))
            await self._unduck()
            await self._bus.set_state(AssistantState.IDLE)
            await self._bus.send_error(
                "transcribe_failed",
                f"Could not make out that one: {exc}. Try again, or type it.",
            )
            return

        # ── talking over her ────────────────────────────────────────
        if self._ducked:
            self._ducked = False
            stop_word = is_stop_word(heard)
            if stop_word or addressed:
                await self._bus.broadcast(Event.AUDIO_STOP, {"reason": "barge_in"})
                cancelled = await self._conversation.cancel_active()
                log.info(
                    "listener.barge_in", heard=heard, stop_word=stop_word, cancelled=cancelled
                )
                if stop_word and not text:
                    # "stop" is not a question. Answering it would be absurd.
                    await self._bus.set_state(AssistantState.IDLE)
                    return
            else:
                # Not for her after all — someone talking near her, or her own
                # voice leaking back through the speakers.
                self._ducked = True  # `_unduck` owns the event and the flag
                await self._unduck()
                log.info("listener.not_an_interruption", heard=heard)
                await self._bus.set_state(AssistantState.IDLE)
                return

        # Her name and nothing else: she has been called, not asked. **This is
        # the case the first build dropped on the floor** — it stripped the
        # name, found an empty string, and silently gave up, which is exactly
        # what everyone does when they expect to be acknowledged before
        # speaking. Now it opens the window instead.
        if addressed and not text:
            async with self._lock:
                await self._open_window(
                    ListenerState.ARMED, self.armed_window_s, reason="name"
                )
            await self._bus.broadcast(Event.WAKE, {"listening_for_s": self.armed_window_s})
            log.info("listener.armed", heard=heard)
            return

        if not text:
            log.info("listener.empty_transcript")
            if not await self._rearm():
                await self._bus.set_state(AssistantState.IDLE)
            return

        # **She just asked something out loud, so an answer needs no name.**
        # Checked before the wake-phrase gate for exactly that reason: with
        # `_needs_name` still true, "the second one" would be dropped as
        # room noise. `answer_from_speech` returns False when the utterance
        # is not an answer, and it then falls through to the ordinary path —
        # so changing the subject mid-quiz is not a trap.
        if text and self._answer_spoken is not None and self._answer_spoken(text):
            log.info("listener.answered_question", heard=text)
            await self._bus.broadcast(Event.HEARD, {"text": text})
            await self._bus.set_state(AssistantState.IDLE)
            return

        if self._mode is WakeMode.PHRASE and self._needs_name and not addressed:
            # The room was talking, not her. Nothing is kept and nothing is
            # sent anywhere — the transcript existed only to answer this.
            #
            # It *is* logged, and shown. A character count was all this
            # recorded before, which made 64 dropped utterances in one session
            # impossible to explain: there was no way to see what she had
            # mistaken the name for.
            log.info("listener.not_addressed", heard=heard)
            await self._bus.broadcast(Event.MISHEARD, {"text": heard})
            await self._bus.set_state(AssistantState.IDLE)
            return

        log.info(
            "listener.heard",
            # The words, not a character count. `not_addressed` was fixed for
            # exactly this reason and this line was left behind — so when
            # spoken turns stopped acting, the log said `chars=42` and there
            # was no way to tell a request from "hi".
            heard=text,
            took_ms=round((time.perf_counter() - started) * 1000, 1),
        )
        # Before the turn, not after: the overlay should show what you said
        # while she is still thinking about it.
        await self._bus.broadcast(Event.HEARD, {"text": text})
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

    def _count_frame(self) -> None:
        """Report how fast frames are actually arriving, periodically."""
        self._frames += 1
        if self._frames < FRAME_REPORT_EVERY:
            return
        now = time.monotonic()
        elapsed = now - self._frames_since
        rate = self._frames / elapsed if elapsed > 0 else 0.0
        log.info(
            "listener.frame_rate",
            per_s=round(rate, 1),
            expected=FRAMES_EXPECTED_PER_S,
            healthy=rate > FRAMES_EXPECTED_PER_S * 0.8,
        )
        self._frames = 0
        self._frames_since = now

    def _reset_models(self) -> None:
        """Forget both rolling histories. Audio from before a pause must not
        combine with audio after it into a phrase that was never said."""
        if self._wake is not None:
            self._wake.reset()
        self._vad.reset()

    def _reset_buffers(self) -> None:
        self._utterance = None
        self._pending = None
        self._preroll.clear()
        self._speech_run_ms = 0.0
