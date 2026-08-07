"""Chunking, extraction and the rules that keep the indexer out of the way.

Embedding is a network call to Ollama, so the parts worth pinning down here
are the ones that decide *what* gets read and *whether it runs at all* — the
throttle is the feature, per §9 Phase 4b.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from sidecar.memory.indexer import (
    CHUNK_CHARS,
    MAX_BYTES,
    OVERLAP_CHARS,
    Indexer,
    chunk,
    extract_text,
    should_index,
)

# ── what gets read ────────────────────────────────────────────────────


@pytest.mark.parametrize("name", ["notes.txt", "readme.md", "main.py", "data.json", "q.pdf"])
def test_documents_and_code_are_indexable(tmp_path: Path, name: str) -> None:
    target = tmp_path / name
    target.write_text("content")
    assert should_index(target)


@pytest.mark.parametrize("name", ["photo.jpg", "clip.mp4", "app.exe", "lib.dll", "song.mp3"])
def test_binaries_are_not(tmp_path: Path, name: str) -> None:
    target = tmp_path / name
    target.write_text("x")
    assert not should_index(target)


def test_very_large_files_are_skipped(tmp_path: Path) -> None:
    """§9: skip over 20MB. Extraction cost is otherwise unbounded."""
    big = tmp_path / "huge.txt"
    big.write_bytes(b"x" * (MAX_BYTES + 1))
    assert not should_index(big)


def test_a_directory_is_not_a_file(tmp_path: Path) -> None:
    folder = tmp_path / "sub.txt"
    folder.mkdir()
    assert not should_index(folder)


# ── chunking ──────────────────────────────────────────────────────────


def test_short_text_is_one_chunk() -> None:
    assert chunk("a short note") == ["a short note"]


def test_empty_text_yields_nothing() -> None:
    assert chunk("") == []
    assert chunk("      \n\t  ") == []


def test_long_text_is_split_with_overlap() -> None:
    """The overlap is why a sentence spanning a boundary is still findable."""
    text = " ".join(f"word{i}" for i in range(4000))
    pieces = chunk(text)

    assert len(pieces) > 1
    assert all(len(p) <= CHUNK_CHARS for p in pieces)
    # The tail of one piece reappears at the head of the next.
    tail = pieces[0][-OVERLAP_CHARS:]
    assert any(fragment in pieces[1] for fragment in tail.split()[:3])


def test_unreadable_files_cost_only_themselves(tmp_path: Path) -> None:
    """A corrupt PDF is a normal event in a folder of downloads."""
    broken = tmp_path / "broken.pdf"
    broken.write_bytes(b"this is not a pdf at all")
    assert extract_text(broken) == ""


# ── staying out of the way ────────────────────────────────────────────


async def test_it_does_not_run_while_she_is_answering(tmp_path: Path) -> None:
    """§9: "a background indexer that makes the machine feel slow will get
    uninstalled." A turn has a ~1s budget; this competes for the same cores."""
    (tmp_path / "a.txt").write_text("some content worth reading")

    answering = True
    indexer = Indexer(
        db=None,  # type: ignore[arg-type]
        embeddings=None,  # type: ignore[arg-type]
        roots=[tmp_path],
        is_busy=lambda: answering,
    )

    waiting = asyncio.create_task(indexer._wait_until_free())  # noqa: SLF001
    await asyncio.sleep(0.05)
    assert not waiting.done(), "it must wait while a turn is in flight"

    answering = False
    await asyncio.wait_for(waiting, timeout=15)


def test_the_rate_comes_from_the_configured_limit() -> None:
    fast = Indexer(db=None, embeddings=None, roots=[], files_per_min=60)  # type: ignore[arg-type]
    slow = Indexer(db=None, embeddings=None, roots=[], files_per_min=20)  # type: ignore[arg-type]
    assert fast._interval_s < slow._interval_s  # noqa: SLF001
    assert slow._interval_s == pytest.approx(3.0)  # noqa: SLF001
