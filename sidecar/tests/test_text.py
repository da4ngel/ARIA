"""Word matching — the layer that decides whether she remembers anything.

Every test here is a case that was measured failing against the live database
on 2026-08-12, when "did we have any conversation regarding any job kind of
things?" retrieved two episodes about the capitals of countries and the time in
Sri Lanka, and nothing about jobs.
"""

from __future__ import annotations

import pytest

from sidecar.memory.text import content_words, coverage, idf, stem

# ── stemming ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("jobs", "job"),
        ("job", "job"),
        ("discussed", "discuss"),
        ("working", "work"),
        ("studies", "study"),
        ("skills", "skill"),
        ("quickly", "quick"),
        ("running", "run"),
        ("stopped", "stop"),
    ],
)
def test_a_suffix_is_stripped(word: str, expected: str) -> None:
    assert stem(word) == expected


@pytest.mark.parametrize(
    "word",
    [
        "class",  # a trailing s after s is not a plural
        "bus",
        "this",
        "data",
        "science",
        "cv",  # under the minimum stem length: returned untouched
        "is",
    ],
)
def test_a_word_that_only_looks_plural_is_left_alone(word: str) -> None:
    assert stem(word) == word


@pytest.mark.parametrize(("word", "expected"), [("pressed", "press"), ("called", "call")])
def test_undoubling_does_not_corrupt_a_real_double(word: str, expected: str) -> None:
    """`runn` -> `run` is right; `pres` is not a word."""
    assert stem(word) == expected


def test_jobs_and_job_are_the_same_word() -> None:
    """The single most consequential line in this module.

    He typed "jobs". Every stored summary said "job". Nothing matched, and she
    answered that they had never discussed it.
    """
    assert stem("jobs") == stem("job")


# ── stopwords ─────────────────────────────────────────────────────────


def test_the_summarisers_own_vocabulary_does_not_count_as_content() -> None:
    """"Discussed" opened most episode summaries in the live database, so it
    matched every query and discriminated between none of them."""
    assert content_words("Discussed various topics regarding user requests") == set()


def test_two_phrasings_of_one_question_reduce_to_the_same_words() -> None:
    """A longer, more specific question used to retrieve *less*, because the
    score divided by the query's own length."""
    terse = content_words("have we discussed about any jobs?")
    wordy = content_words("Did we have any conversation regarding any job kind of things?")

    assert terse == wordy == {"job"}


# ── coverage ──────────────────────────────────────────────────────────


def test_a_rare_word_carries_the_match() -> None:
    documents = [
        content_words("User asked which skills matter for a data science job"),
        content_words("Discussed the capital of Australia"),
        content_words("Discussed the current time in Sri Lanka"),
    ]
    weights = idf(documents)
    query = content_words("have we discussed about any jobs?")

    assert coverage(query, documents[0], weights) == pytest.approx(1.0)
    assert coverage(query, documents[1], weights) == 0.0
    assert coverage(query, documents[2], weights) == 0.0


def test_padding_a_question_with_filler_does_not_dilute_it() -> None:
    """The specific regression: being precise must not cost recall."""
    document = content_words("User asked which skills matter for a data science job")
    weights = idf([document])

    terse = coverage(content_words("any jobs?"), document, weights)
    wordy = coverage(
        content_words("Did we have any conversation regarding any job kind of things?"),
        document,
        weights,
    )

    assert terse == pytest.approx(wordy)


def test_a_word_nothing_has_seen_counts_against_the_match() -> None:
    """It is the most discriminating word in the query. Failing to find it is
    evidence, not a shrug."""
    document = content_words("user prefers tea")
    weights = idf([document])

    assert coverage({"tea", "helicopter"}, document, weights) < 1.0


def test_an_empty_query_or_document_scores_zero() -> None:
    weights = idf([{"tea"}])
    assert coverage(set(), {"tea"}, weights) == 0.0
    assert coverage({"tea"}, set(), weights) == 0.0


def test_idf_of_nothing_is_empty_rather_than_an_error() -> None:
    assert idf([]) == {}
