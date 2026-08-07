"""Finding files by name: the ranking, and the words people wrap around it.

The scan and Everything are both I/O; what is worth pinning down is the part
that decides *which* file, which is pure.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from sidecar.tools.finder import FoundFile, clean_query, rank_files

DAY = 86400.0
NOW = time.time()


def f(name: str, age_days: float) -> FoundFile:
    return FoundFile(Path("C:/Users/x/Documents") / name, NOW - age_days * DAY, 1024)


# The scenario Eyaas described, with the decoys that make it a real test.
LIBRARY = [
    f("Eyaas_CV_2026.pdf", 2),
    f("cv_old_draft.docx", 400),
    f("CV covering letter.docx", 30),
    f("budget_2026.xlsx", 1),
    f("cvs_receipt.png", 3),
    f("resume.pdf", 5),
    f("notes.txt", 10),
]


@pytest.mark.parametrize(
    "said",
    ["cv", "my cv", "the latest cv", "open my cv", "find my cv file", "CV"],
)
def test_the_newest_cv_wins_however_it_was_asked_for(said: str) -> None:
    """"if I say open cv … fetch the latest cv" — this is that, with an old
    draft and a covering letter sitting next to it."""
    top = rank_files(said, LIBRARY, limit=1)
    assert top and top[0].name == "Eyaas_CV_2026.pdf"


def test_recency_does_not_override_the_name() -> None:
    """budget_2026 is newer than every CV, and must not answer "cv"."""
    top = rank_files("cv", LIBRARY, limit=3)
    assert "budget_2026.xlsx" not in [item.name for item in top]


def test_an_older_file_still_wins_on_a_better_name() -> None:
    """Recency is a tiebreaker, never the whole answer."""
    top = rank_files("budget", LIBRARY, limit=1)
    assert top and top[0].name == "budget_2026.xlsx"


def test_a_typo_still_finds_it() -> None:
    top = rank_files("budgt", LIBRARY, limit=1)
    assert top and top[0].name == "budget_2026.xlsx"


def test_nonsense_finds_nothing() -> None:
    """Opening the wrong document is worse than opening none."""
    assert rank_files("qwertyuiop", LIBRARY) == []


def test_results_are_capped() -> None:
    assert len(rank_files("cv", LIBRARY, limit=2)) <= 2


@pytest.mark.parametrize(
    ("said", "wanted"),
    [
        ("my cv", "cv"),
        ("the latest cv", "cv"),
        ("open my cv file", "cv"),
        ("show me the budget", "budget"),
        ("get the invoice", "invoice"),
    ],
)
def test_filler_words_are_dropped(said: str, wanted: str) -> None:
    assert clean_query(said) == wanted


def test_a_query_of_only_filler_keeps_something_to_match_on() -> None:
    """Stripping everything would search for the empty string, which matches
    the entire disk. "find that document" is all filler, so it survives whole
    rather than becoming nothing."""
    assert clean_query("the file") != ""
    assert clean_query("find that document") == "find that document"
