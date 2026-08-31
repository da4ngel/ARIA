"""Answering a question out loud.

The property that makes this safe to run on *every* utterance is negative:
`match_spoken` returns None rather than guessing, and the listener then lets
the utterance become an ordinary turn. Somebody who changes the subject
mid-quiz must not be trapped in it, and most of these tests are about that.
"""

from __future__ import annotations

import pytest

from sidecar.core.questions import (
    OTHER_LABEL,
    Option,
    Question,
    match_spoken,
    normalise,
    speakable,
)


def _question() -> Question:
    return normalise(
        [
            Question(
                question="Which layer does TCP sit at?",
                options=[
                    Option(label="Transport"),
                    Option(label="Network"),
                    Option(label="Application"),
                ],
            )
        ]
    )[0]


# ── the option's own words ────────────────────────────────────────────


def test_saying_the_answer_picks_it() -> None:
    answer = match_spoken("Transport", _question())
    assert answer is not None
    assert answer.chosen == ["Transport"]


def test_saying_the_answer_in_a_sentence_still_picks_it() -> None:
    answer = match_spoken("I think it's the transport layer", _question())
    assert answer is not None
    assert answer.chosen == ["Transport"]


def test_matching_is_case_insensitive_and_ignores_trailing_punctuation() -> None:
    answer = match_spoken("network.", _question())
    assert answer is not None
    assert answer.chosen == ["Network"]


# ── ordinals and letters ──────────────────────────────────────────────


@pytest.mark.parametrize(
    ("said", "expected"),
    [
        ("one", "Transport"),
        ("first", "Transport"),
        ("two", "Network"),
        ("second", "Network"),
        ("B", "Network"),
        ("three", "Application"),
        ("C", "Application"),
    ],
)
def test_a_position_picks_that_option(said: str, expected: str) -> None:
    answer = match_spoken(said, _question())
    assert answer is not None
    assert answer.chosen == [expected]


def test_a_position_past_the_end_is_not_an_answer() -> None:
    """Three options, and "five" is a mis-transcription rather than a choice."""
    assert match_spoken("five", _question()) is None


def test_a_number_inside_a_sentence_is_not_a_vote() -> None:
    """**The reason ordinals are tried last and only alone.** "two of them are
    wrong" is a remark about the question, not an answer to it."""
    assert match_spoken("two of them are wrong, surely", _question()) is None


# ── not an answer ─────────────────────────────────────────────────────


def test_changing_the_subject_is_not_an_answer() -> None:
    """The load-bearing negative: this is what stops a quiz becoming a trap."""
    for said in (
        "actually what time is it",
        "open notepad for me",
        "hang on, my phone is ringing",
    ):
        assert match_spoken(said, _question()) is None, said


def test_silence_is_not_an_answer() -> None:
    assert match_spoken("   ", _question()) is None


def test_saying_you_do_not_know_is_recorded_rather_than_matched() -> None:
    """**"I don't know" is a real answer to a quiz.** Left to the fuzzy path it
    would hit whichever option happened to share a syllable with it."""
    answer = match_spoken("no idea", _question())
    assert answer is not None
    assert answer.chosen == []
    assert "no idea" in answer.other


# ── reading it out ────────────────────────────────────────────────────


def test_the_spoken_form_numbers_the_options() -> None:
    said = speakable(_question())
    assert "Which layer does TCP sit at?" in said
    assert "1. Transport" in said
    assert "2. Network" in said


def test_other_is_never_read_out() -> None:
    """On screen it is an escape hatch you can see and ignore; spoken it would
    be a fifth thing to listen to on every question. Saying something that
    matches nothing still reaches it."""
    assert OTHER_LABEL not in speakable(_question())


def test_a_batch_says_where_it_is_up_to() -> None:
    said = speakable(_question(), position=2, total=4)
    assert said.startswith("Question 3 of 4.")


def test_a_single_question_is_not_numbered() -> None:
    assert not speakable(_question(), position=0, total=1).startswith("Question")


def test_the_second_one_means_the_second_not_the_first() -> None:
    """**The ambiguity in "one".** It is both a filler ("the second one") and
    the way somebody says the first option. Resolved by requiring every
    surviving token to be positional and taking the first."""
    answer = match_spoken("the second one", _question())
    assert answer is not None
    assert answer.chosen == ["Network"]

    bare = match_spoken("one", _question())
    assert bare is not None
    assert bare.chosen == ["Transport"]
