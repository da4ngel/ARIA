"""The general undo timeline.

Undo existed for exactly one tool before this — `undo_organize` replayed a
folder tidy-up's manifest — and the reason was never the missing table. It was
that most tools kept nothing that *could* be reversed. So the tests that matter
are the ones about capture: that `write_file` copies aside what it replaces,
and that `delete_file` no longer destroys.
"""

from __future__ import annotations

from pathlib import Path

from sidecar.memory import undo
from sidecar.memory.db import Database

PAYLOAD = {"source": "a", "destination": "b"}


async def _entry(db: Database, **overrides: object) -> int:
    fields: dict = {
        "tool": "move_file",
        "kind": "move",
        "summary": "Moved notes.txt to Documents",
        "payload": PAYLOAD,
    }
    fields.update(overrides)
    entry_id = await undo.record(db, **fields)
    assert entry_id is not None
    return entry_id


# ── the timeline ──────────────────────────────────────────────────────


async def test_operations_come_back_newest_first(database: Database) -> None:
    await _entry(database, summary="first")
    await _entry(database, summary="second")
    assert [e.summary for e in await undo.recent(database)] == ["second", "first"]


async def test_the_last_undoable_skips_what_has_already_been_undone(
    database: Database, tmp_path: Path
) -> None:
    source, destination = tmp_path / "a.txt", tmp_path / "b.txt"
    destination.write_text("x", encoding="utf-8")
    first = await _entry(database, summary="older")
    await _entry(
        database,
        summary="newer",
        payload={"source": str(source), "destination": str(destination)},
    )

    ok, _ = await undo.apply(database, (await undo.last_undoable(database)).id)  # type: ignore[union-attr]
    assert ok
    remaining = await undo.last_undoable(database)
    assert remaining is not None
    assert remaining.id == first


async def test_the_same_entry_cannot_be_undone_twice(
    database: Database, tmp_path: Path
) -> None:
    """**The claim is the guard**, exactly as `reminders.delivered_at` is: the
    UPDATE matches only while `undone_at` is NULL, so two clicks in quick
    succession cannot both reverse it."""
    source, destination = tmp_path / "a.txt", tmp_path / "b.txt"
    destination.write_text("x", encoding="utf-8")
    entry_id = await _entry(
        database, payload={"source": str(source), "destination": str(destination)}
    )

    first_ok, _ = await undo.apply(database, entry_id)
    second_ok, message = await undo.apply(database, entry_id)
    assert first_ok
    assert not second_ok
    assert "already been undone" in message


async def test_a_failed_undo_says_why_and_does_not_look_successful(
    database: Database, tmp_path: Path
) -> None:
    """Without releasing the claim, a failed undo would hide the button and
    leave the file where it was — the worst of both."""
    entry_id = await _entry(
        database,
        payload={"source": str(tmp_path / "a.txt"), "destination": str(tmp_path / "gone.txt")},
    )
    ok, message = await undo.apply(database, entry_id)
    assert not ok
    assert "not there any more" in message

    entries = await undo.recent(database)
    assert entries[0].blocked is not None
    assert not entries[0].undoable


# ── reversing each kind ───────────────────────────────────────────────


async def test_a_move_is_put_back(database: Database, tmp_path: Path) -> None:
    source, destination = tmp_path / "notes.txt", tmp_path / "sub" / "notes.txt"
    destination.parent.mkdir()
    destination.write_text("hello", encoding="utf-8")
    entry_id = await _entry(
        database, payload={"source": str(source), "destination": str(destination)}
    )

    ok, _ = await undo.apply(database, entry_id)
    assert ok
    assert source.read_text(encoding="utf-8") == "hello"
    assert not destination.exists()


async def test_a_move_back_refuses_to_overwrite(database: Database, tmp_path: Path) -> None:
    """Rule 5 calls overwriting destructive, and an undo that silently
    replaces something is the worst kind: it looks like it worked."""
    source, destination = tmp_path / "notes.txt", tmp_path / "moved.txt"
    source.write_text("the new one", encoding="utf-8")
    destination.write_text("the old one", encoding="utf-8")
    entry_id = await _entry(
        database, payload={"source": str(source), "destination": str(destination)}
    )

    ok, message = await undo.apply(database, entry_id)
    assert not ok
    assert "overwrite" in message
    assert source.read_text(encoding="utf-8") == "the new one"


async def test_an_overwrite_is_restored_from_the_backup(
    database: Database, tmp_path: Path
) -> None:
    target = tmp_path / "notes.txt"
    target.write_text("what it was before", encoding="utf-8")
    backup = undo.save_backup(tmp_path / "undo", target)
    assert backup is not None
    target.write_text("what it is now", encoding="utf-8")

    entry_id = await _entry(
        database, kind="write", payload={"path": str(target), "backup": backup}
    )
    ok, _ = await undo.apply(database, entry_id)
    assert ok
    assert target.read_text(encoding="utf-8") == "what it was before"


async def test_undoing_a_create_removes_the_file(database: Database, tmp_path: Path) -> None:
    target = tmp_path / "new.txt"
    target.write_text("made by her", encoding="utf-8")
    entry_id = await _entry(
        database,
        kind="write",
        payload={"path": str(target), "backup": None, "wrote": "made by her"},
    )
    ok, _ = await undo.apply(database, entry_id)
    assert ok
    assert not target.exists()


async def test_undoing_a_create_refuses_once_it_has_been_edited(
    database: Database, tmp_path: Path
) -> None:
    """**The dangerous case.** Undoing a create means deleting, and somebody
    who edited the file since would lose that work to an undo they thought was
    safe."""
    target = tmp_path / "new.txt"
    target.write_text("made by her", encoding="utf-8")
    entry_id = await _entry(
        database,
        kind="write",
        payload={"path": str(target), "backup": None, "wrote": "made by her"},
    )
    target.write_text("made by her, then edited by me", encoding="utf-8")

    ok, message = await undo.apply(database, entry_id)
    assert not ok
    assert "changed since" in message
    assert target.exists()


async def test_a_delete_points_at_the_recycle_bin(database: Database) -> None:
    """It is genuinely recoverable and genuinely not from here — the shell has
    no "undelete this path" call. Saying exactly where it is beats a button
    that quietly does nothing."""
    entry_id = await _entry(
        database, kind="delete", payload={"path": "C:/temp/gone.txt", "bytes": 10}
    )
    ok, message = await undo.apply(database, entry_id)
    assert not ok
    assert "Recycle Bin" in message


async def test_an_unknown_kind_is_reported_rather_than_crashing(
    database: Database,
) -> None:
    entry_id = await _entry(database, kind="teleport")
    ok, message = await undo.apply(database, entry_id)
    assert not ok
    assert "teleport" in message


# ── backups ───────────────────────────────────────────────────────────


def test_a_backup_is_skipped_rather_than_failing_the_write(tmp_path: Path) -> None:
    """Best-effort by design: refusing to write because the backup failed
    would break a working tool to protect a convenience."""
    assert undo.save_backup(tmp_path / "undo", tmp_path / "not-there.txt") is None


def test_a_huge_file_is_not_copied_aside(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(undo, "MAX_BACKUP_BYTES", 10)
    target = tmp_path / "big.txt"
    target.write_text("x" * 100, encoding="utf-8")
    assert undo.save_backup(tmp_path / "undo", target) is None


def test_old_backups_are_pruned(tmp_path: Path) -> None:
    import os
    import time

    undo_dir = tmp_path / "undo"
    undo_dir.mkdir()
    old = undo_dir / "write-old-notes.txt"
    old.write_text("x", encoding="utf-8")
    (undo_dir / "unrelated.json").write_text("{}", encoding="utf-8")

    # **The mtime is set rather than the window being zero.** `days=0` puts the
    # cutoff at *now*, which races a file written microseconds earlier — the
    # first version of this test passed and failed on alternate runs.
    long_ago = time.time() - 60 * 86400
    os.utime(old, (long_ago, long_ago))

    assert undo.prune_backups(undo_dir, days=30) == 1
    # A manifest belonging to `organize_folder` is not this function's business.
    assert (undo_dir / "unrelated.json").exists()
