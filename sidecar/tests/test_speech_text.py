"""Markdown must not be read aloud.

Both speech paths took the model's text exactly as written: `SpeechStream.feed`
received `delta.text` unmodified, and `voice.speak` was handed `turn.content`
straight from the transcript. `split_for_speech` splits on sentence punctuation
and never removed a character, so Kokoro has been receiving ``**bold**``,
backticks, heading hashes, table pipes and whole code fences since Phase 2.
"""

from __future__ import annotations

import pytest

from sidecar.providers.speech_text import CODE_STAND_IN, settled_for_speech, speech_text

FENCE = "`" * 3


class TestNothingWithoutASoundSurvives:
    @pytest.mark.parametrize(
        ("markdown", "expected"),
        [
            ("**bold**", "bold"),
            ("*italic*", "italic"),
            ("__bold__", "bold"),
            ("_italic_", "italic"),
            ("***both***", "both"),
            ("~~struck~~", "struck"),
            ("`code`", "code"),
            ("### Heading", "Heading"),
            ("> quoted", "quoted"),
            ("- bullet", "bullet"),
            ("* bullet", "bullet"),
        ],
    )
    def test_the_marker_goes_and_the_words_stay(self, markdown: str, expected: str) -> None:
        # The words inside are usually the load-bearing part of the sentence.
        # "run `npm run dev`" is useless without the command.
        assert speech_text(markdown).strip() == expected

    def test_no_syntax_character_reaches_the_synthesiser(self) -> None:
        reply = (
            "## Setup\n\n"
            "Run `npm run dev`, then **open** the app.\n\n"
            "| step | note |\n| --- | --- |\n| 1 | go |\n\n"
            "- a point\n- another\n\n"
            "---\n\n"
            "See [the docs](https://example.com/very/long/path).\n"
        )

        spoken = speech_text(reply)

        for character in ("*", "`", "#", "|", "~"):
            assert character not in spoken, f"{character!r} survived: {spoken!r}"

    def test_an_underscore_inside_a_word_is_left_alone(self) -> None:
        # `snake_case_name` is one word, not italics. Splitting it would change
        # what is said, which is worse than leaving a character in.
        assert "snake_case_name" in speech_text("The snake_case_name value.")


class TestTheTwoThingsWorseThanSilence:
    def test_a_code_block_is_named_rather_than_read(self) -> None:
        # A thirty-line block is over a minute of speech nobody can act on.
        reply = f"Here:\n\n{FENCE}python\ndef solve(n):\n    return n * 2\n{FENCE}\n\nThat is it."

        spoken = speech_text(reply)

        assert CODE_STAND_IN in spoken
        assert "def solve" not in spoken
        assert "That is it." in spoken

    def test_a_fence_that_never_closed_is_still_not_read(self) -> None:
        # Mid-stream this is the normal state, and at `finish` it is what a
        # truncated reply leaves behind.
        spoken = speech_text(f"Here:\n\n{FENCE}python\ndef solve(n):")

        assert CODE_STAND_IN in spoken
        assert "def solve" not in spoken

    def test_a_bare_url_is_not_spelled_out(self) -> None:
        # Unusable by ear, and longer to say than the sentence around it. The
        # screen still has it.
        spoken = speech_text("Go to https://example.com/a/b?c=d#e now.")

        assert "example.com" not in spoken
        assert "a link" in spoken

    def test_a_link_keeps_its_label_and_loses_its_url(self) -> None:
        spoken = speech_text("See [the release notes](https://example.com/notes).")

        assert "the release notes" in spoken
        assert "example.com" not in spoken

    def test_a_table_is_read_as_cells_not_as_pipes(self) -> None:
        spoken = speech_text("| model | speed |\n| --- | --- |\n| nano | fast |")

        assert "model, speed" in spoken
        assert "nano, fast" in spoken
        assert "---" not in spoken


class TestWhatIsSafeToSayYet:
    """Deltas arrive a few characters at a time, which is what makes this hard.

    Stripping each delta as it lands would see ``**bo`` and then ``ld**``, match
    neither, and read both asterisks aloud — the bug being fixed, arriving by a
    different route.
    """

    @pytest.mark.parametrize(
        ("raw", "safe", "held"),
        [
            ("a **bo", "a ", "**bo"),
            ("a **bold** c", "a **bold** c", ""),
            ("run `npm", "run ", "`npm"),
            ("run `npm dev` now", "run `npm dev` now", ""),
            ("see [label", "see ", "[label"),
            # **Both halves, or neither.** Releasing on the "]" alone let
            # "[the docs]" through as literal text and then converted the
            # "(url)" that followed separately — found by driving the real
            # stream, not by reading the function.
            ("see [label]", "see ", "[label]"),
            ("see [label](htt", "see ", "[label](htt"),
            ("see [label](url)", "see [label](url)", ""),
            # A bracket that is not a link must not stall the stream.
            ("the array [1, 2] there", "the array [1, 2] there", ""),
            ("plain words", "plain words", ""),
        ],
    )
    def test_an_unfinished_marker_is_held_back(self, raw: str, safe: str, held: str) -> None:
        assert settled_for_speech(raw) == (safe, held)

    def test_an_open_fence_holds_everything_after_it(self) -> None:
        safe, held = settled_for_speech(f"Intro.\n\n{FENCE}python\ndef f():")

        assert safe == "Intro.\n\n"
        assert held.startswith(FENCE)

    def test_a_closed_fence_is_released(self) -> None:
        safe, held = settled_for_speech(f"{FENCE}py\nx = 1\n{FENCE}\ndone")

        assert held == ""
        assert "done" in safe

    def test_ordinary_prose_is_never_delayed(self) -> None:
        # Holding the current line as a matter of course would delay the
        # opening fragment, and 872ms to first audio is the whole reason
        # `split_for_speech` breaks it early in the first place.
        assert settled_for_speech("The capital of Australia is Canberra.") == (
            "The capital of Australia is Canberra.",
            "",
        )


class TestItLeavesOrdinarySpeechAlone:
    @pytest.mark.parametrize(
        "plain",
        [
            "The capital of Australia is Canberra.",
            "It is 3:45pm, and you have two reminders.",
            "I could not find that file. Try naming the folder?",
            "",
        ],
    )
    def test_text_with_no_markdown_is_unchanged(self, plain: str) -> None:
        assert speech_text(plain) == plain


class TestTheStreamActuallyUsesIt:
    """The pure function above is not the fix; wiring it in is.

    Both mutation checks on `speech_text` and `settled_for_speech` failed only
    their own unit tests and left `test_conversation.py` entirely green — which
    is precisely the shape of gap this project keeps finding (`affect_state`,
    `procedures`, `record_new_offers`: a thing written, tested, and called by
    nothing). These drive the real `SpeechStream`.
    """

    @staticmethod
    async def _say(reply: str, *, step: int = 6) -> list[str]:
        """Feed a reply through a real stream the way tokens actually arrive."""
        from sidecar.core.conversation import SpeechStream
        from sidecar.tests.test_tts import FakeTTS, RecordingBus

        tts = FakeTTS()
        stream = SpeechStream(tts, RecordingBus(), 0.0)
        for i in range(0, len(reply), step):
            stream.feed(reply[i : i + step])
            await stream.drain("t1")
        await stream.finish("t1")
        return tts.spoken

    @pytest.mark.asyncio
    async def test_no_markdown_reaches_the_synthesiser(self) -> None:
        spoken = " ".join(
            await self._say(
                "## Setup\n\nRun `npm run dev`, then **open** it. See "
                "[the docs](https://example.com/x) for more.\n"
            )
        )

        for character in ("*", "`", "#", "["):
            assert character not in spoken, f"{character!r} was spoken: {spoken!r}"
        assert "npm run dev" in spoken
        assert "the docs" in spoken

    @pytest.mark.asyncio
    async def test_a_marker_split_across_two_deltas_is_still_stripped(self) -> None:
        # The reason stripping cannot happen in `feed`. At this step size
        # "**open**" is guaranteed to arrive in pieces.
        spoken = " ".join(await self._say("Please **open** the file now. Thanks.", step=3))

        assert "*" not in spoken
        assert "open" in spoken

    @pytest.mark.asyncio
    async def test_a_code_block_is_never_read_out(self) -> None:
        # The reason stripping cannot happen per chunk either: a fence spans
        # many sentences, so `split_for_speech` would emit its lines as speech
        # long before the closing fence arrived.
        spoken = " ".join(
            await self._say(
                f"Here you go.\n\n{FENCE}python\n"
                "def solve(n):\n    total = 0\n    return total\n"
                f"{FENCE}\n\nThat should do it.\n"
            )
        )

        assert "def solve" not in spoken
        assert "total" not in spoken
        assert CODE_STAND_IN in spoken
        assert "That should do it." in spoken

    @pytest.mark.asyncio
    async def test_a_reply_ending_mid_marker_still_gets_spoken(self) -> None:
        # `finish` has to flush what was held back, or a reply that stops
        # inside a bold span loses its last words entirely — silence is a
        # worse failure than a stray asterisk.
        spoken = " ".join(await self._say("All done. **Almost"))

        assert "All done." in spoken
        assert "Almost" in spoken
