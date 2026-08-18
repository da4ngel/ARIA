"""Finding files by name: the ranking, and the words people wrap around it.

The scan and Everything are both I/O; what is worth pinning down is the part
that decides *which* file, which is pure.
"""

from __future__ import annotations

import inspect
import time
from pathlib import Path

import pytest

from sidecar.tools import files, finder
from sidecar.tools.finder import FoundFile, _describe, clean_query, rank_files
from sidecar.tools.registry import ToolContext

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


# ── the scan cache, and the file she just wrote ───────────────────────
#
# `_Cache.clear()` existed from the start and nothing outside these tests
# called it, so for 45 seconds after ARIA created a file she could not find
# it — the shape of `gate_agent.py`'s find -> read -> answer line. These go
# through the public surface only: `find_files` for the read, the tools
# themselves for the write.


def _counting_scan(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Make `find_files` deterministic and count how often it really walks."""
    walks: list[int] = []

    def fake_scan(limit: int) -> list[FoundFile]:
        walks.append(limit)
        return [f("cv.pdf", 1)]

    monkeypatch.setattr(finder, "everything_path", lambda: None)
    monkeypatch.setattr(finder, "_search_scan", fake_scan)
    finder.invalidate_scan()
    return walks


async def test_the_scan_is_cached_between_searches(monkeypatch: pytest.MonkeyPatch) -> None:
    """The reason the cache exists at all — two questions in a row must not
    walk three directory trees twice."""
    walks = _counting_scan(monkeypatch)

    await (finder.find_files("cv"))
    await (finder.find_files("cv"))

    assert len(walks) == 1


async def test_invalidating_forces_the_next_search_to_walk_again(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    walks = _counting_scan(monkeypatch)

    await (finder.find_files("cv"))
    finder.invalidate_scan()
    await (finder.find_files("cv"))

    assert len(walks) == 2


async def test_a_write_invalidates_the_cached_scan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The bug, end to end: write a file, and the next search must not be
    answered from a scan taken before it existed."""
    walks = _counting_scan(monkeypatch)
    await (finder.find_files("cv"))
    assert len(walks) == 1

    await (files.write_file(ToolContext(), str(tmp_path / "hello.txt"), "hi"))
    await (finder.find_files("cv"))

    assert len(walks) == 2


async def test_a_refused_write_does_not_throw_away_a_good_scan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalidation happens after the filesystem actually changed, never on
    the way in — a call that did nothing must not cost the next search a
    fresh 163-185ms walk."""
    walks = _counting_scan(monkeypatch)
    await (finder.find_files("cv"))

    result = await (files.write_file(ToolContext(), "C:/Windows/nope.txt", "x"))
    await (finder.find_files("cv"))

    assert not result.ok
    assert len(walks) == 1


@pytest.mark.parametrize(
    "tool_name",
    ["move_file", "delete_file", "create_folder", "write_file", "rename_file", "delete_folder"],
)
def test_every_mutating_file_tool_invalidates_the_scan(tool_name: str) -> None:
    """A guard against the next one being added without it. Reads
    (`read_file`, `list_folder`, `open_path`) deliberately do not."""
    source = inspect.getsource(getattr(files, tool_name))
    assert "_scan_changed()" in source, f"{tool_name} changes the filesystem but never says so"


@pytest.mark.parametrize("tool_name", ["read_file", "list_folder", "open_path"])
def test_reads_do_not_invalidate_the_scan(tool_name: str) -> None:
    source = inspect.getsource(getattr(files, tool_name))
    assert "_scan_changed()" not in source


# ── the summary is the only thing the next step can chain on ──────────


def test_a_search_summary_names_the_full_path() -> None:
    """§7.2 sends `summary` back into the context and keeps `data`/`display`
    out of it, so a summary that names files without saying where they are
    leaves the next tool call nothing to act on. Measured failure: the model
    called `read_file {"path": "aria-agent-gate.txt"}` — a bare name, which
    resolves against the sidecar's own working directory — and got
    `missing`, having just been told the file existed.
    """
    item = f("budget.xlsx", 1)

    assert _describe(item, with_path=True).endswith(f"at {item.path}")
    assert str(item.path) not in _describe(item), "the human-facing form stays short"


async def test_search_files_hands_the_model_something_it_can_open(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    found = [f("budget.xlsx", 1)]
    monkeypatch.setattr(finder, "everything_path", lambda: None)
    monkeypatch.setattr(finder, "_search_scan", lambda limit: found)
    finder.invalidate_scan()

    result = await finder.search_files(ToolContext(), query="budget")

    assert result.ok
    assert str(found[0].path) in result.summary, (
        "a chain can only chain on what the summary tells it"
    )
