"""The clipboard ring, and the filter that keeps credentials out of it.

**Everything copied on this machine lands in `data/aria.db`**, so the filter is
the part worth testing hardest. It is imperfect by construction — a passphrase
of ordinary words is indistinguishable from a sentence — and the tests say so
rather than pretending otherwise.

No test touches a real clipboard: `ClipboardWatcher` takes its sequence source,
its reader and its window title as callables.
"""

from __future__ import annotations

from sidecar.core.clipboard_watcher import ClipboardWatcher, looks_like_a_secret
from sidecar.memory import clipboard_store
from sidecar.memory.db import Database

# ── the store ─────────────────────────────────────────────────────────


async def test_entries_come_back_newest_first(database: Database) -> None:
    for text in ("first", "second", "third"):
        await clipboard_store.remember(database, text)
    assert [e.content for e in await clipboard_store.recent(database)] == [
        "third",
        "second",
        "first",
    ]


async def test_copying_the_same_thing_twice_moves_it_rather_than_duplicating(
    database: Database,
) -> None:
    """A history of fifty entries should be fifty *different* things.

    Copying the same snippet repeatedly while working is the normal case, and
    without this the ring fills with one string.
    """
    await clipboard_store.remember(database, "the same thing")
    await clipboard_store.remember(database, "something else")
    await clipboard_store.remember(database, "the same thing")

    entries = await clipboard_store.recent(database)
    assert [e.content for e in entries] == ["the same thing", "something else"]
    assert len(entries) == 2


async def test_the_ring_is_trimmed_to_its_limit(
    database: Database, monkeypatch
) -> None:
    monkeypatch.setattr(clipboard_store, "MAX_ENTRIES", 5)
    for n in range(12):
        await clipboard_store.remember(database, f"entry {n}")
    entries = await clipboard_store.recent(database, 50)
    assert len(entries) == 5
    assert entries[0].content == "entry 11"


async def test_blank_and_oversized_copies_are_not_kept(database: Database) -> None:
    assert await clipboard_store.remember(database, "   ") is None
    assert await clipboard_store.remember(database, "x" * (clipboard_store.MAX_CHARS + 1)) is None
    assert await clipboard_store.recent(database) == []


async def test_one_entry_can_be_forgotten_and_the_ring_emptied(
    database: Database,
) -> None:
    first = await clipboard_store.remember(database, "keep")
    second = await clipboard_store.remember(database, "drop")
    assert second is not None
    assert await clipboard_store.forget(database, second)
    assert [e.id for e in await clipboard_store.recent(database)] == [first]
    assert await clipboard_store.clear(database) == 1
    assert await clipboard_store.recent(database) == []


# ── the filter ────────────────────────────────────────────────────────


def test_published_key_formats_are_refused() -> None:
    """Not heuristics. Every one of these is a documented prefix."""
    for secret in (
        "sk-proj-abc123def456ghi789jkl012mno345pqr",
        "AKIAIOSFODNN7EXAMPLE",
        "ABSKQmVkcm9ja0FQSUtleS0xMjM0LWF0LTk5OTk5OTk5",
        "ghp_16C7e42F292c6912E7710c838347Ae178B4a",
        "AIzaSyD-1234567890abcdefghijklmnopqrstuv",
        "-----BEGIN RSA PRIVATE KEY-----",
    ):
        assert looks_like_a_secret(secret), secret


def test_a_random_looking_blob_is_refused() -> None:
    assert looks_like_a_secret("Xk92mQp4vRt7yLs3wNb8zHc5jFd1gAe6TuIoPyMn")


def test_ordinary_text_is_kept() -> None:
    """The filter must not eat the thing the feature exists for."""
    for ordinary in (
        "https://github.com/anthropics/claude-code",
        "SELECT * FROM messages WHERE session_id = ?",
        "Remember to call the bank about the mortgage on Tuesday",
        "C:\\Users\\Dark_Angel\\Projects\\ARIA\\sidecar\\main.py",
        "def hello(name): return f'hi {name}'",
    ):
        assert not looks_like_a_secret(ordinary), ordinary


def test_a_long_path_is_not_mistaken_for_a_key() -> None:
    """A path is long and unbroken but not random — all three conditions have
    to hold, or every file path on the machine disappears from the history."""
    assert not looks_like_a_secret("/home/eyaas/projects/aria/sidecar/memory/store.py")


def test_anything_copied_out_of_a_password_manager_is_refused() -> None:
    assert looks_like_a_secret("hunter2", window_title="1Password — Personal")
    assert looks_like_a_secret("anything", window_title="Bitwarden")
    assert not looks_like_a_secret("hunter2", window_title="Visual Studio Code")


def test_a_word_passphrase_is_not_caught_and_that_is_stated() -> None:
    """**The honest limit.** A passphrase of ordinary words is, by design,
    indistinguishable from a sentence. This test exists so the gap is recorded
    rather than discovered."""
    assert not looks_like_a_secret("correct horse battery staple")


# ── the watcher ───────────────────────────────────────────────────────


class _Recorder:
    def __init__(self) -> None:
        self.kept: list[tuple[str, str | None]] = []

    async def __call__(self, content: str, source: str | None) -> None:
        self.kept.append((content, source))


def _watcher(
    recorder: _Recorder,
    sequence: list[int],
    clips: list[str | None],
    title: str = "",
) -> ClipboardWatcher:
    # The arming tick returns before reading, so `clips` holds only what is
    # read on the ticks *after* the first.
    steps = iter(sequence)
    reads = iter(clips)
    return ClipboardWatcher(
        remember=recorder,
        read_text=lambda: next(reads, None),
        sequence=lambda: next(steps, None),
        window_title=lambda: title,
    )


async def test_the_first_tick_only_arms_and_records_nothing() -> None:
    """Whatever was on the clipboard when ARIA started was not copied *now*."""
    recorder = _Recorder()
    watcher = _watcher(recorder, [7, 7], ["was already there"])
    await watcher.tick()
    assert recorder.kept == []


async def test_a_change_in_the_sequence_number_records_the_new_content() -> None:
    recorder = _Recorder()
    watcher = _watcher(recorder, [1, 2], ["the copied thing"], title="Notepad")
    await watcher.tick()  # arms
    await watcher.tick()
    assert recorder.kept == [("the copied thing", "Notepad")]


async def test_an_unchanged_sequence_number_never_opens_the_clipboard() -> None:
    """The whole point of polling the counter: on an idle machine the clipboard
    is never touched, so nothing fights another app for the handle."""
    opened = 0

    def _read() -> str | None:
        nonlocal opened
        opened += 1
        return "x"

    recorder = _Recorder()
    watcher = ClipboardWatcher(
        remember=recorder, read_text=_read, sequence=lambda: 42, window_title=lambda: ""
    )
    for _ in range(5):
        await watcher.tick()
    assert opened == 0
    assert recorder.kept == []


async def test_a_secret_is_counted_and_not_stored() -> None:
    recorder = _Recorder()
    watcher = _watcher(recorder, [1, 2], ["AKIAIOSFODNN7EXAMPLE"])
    await watcher.tick()
    await watcher.tick()
    assert recorder.kept == []
    assert watcher.skipped_secrets == 1


async def test_non_text_clipboard_content_is_skipped() -> None:
    """An image or a file list reads as None and is not an error."""
    recorder = _Recorder()
    watcher = _watcher(recorder, [1, 2], [None])
    await watcher.tick()
    await watcher.tick()
    assert recorder.kept == []


async def test_a_failing_sequence_call_does_not_kill_the_loop() -> None:
    """A watcher that can die is worse than no watcher."""
    recorder = _Recorder()

    def _boom() -> int:
        raise OSError("clipboard is busy")

    watcher = ClipboardWatcher(
        remember=recorder, read_text=lambda: "x", sequence=_boom, window_title=lambda: ""
    )
    await watcher.tick()  # must not raise
