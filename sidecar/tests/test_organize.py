"""Tidying a folder, and putting it back exactly (§9 Phase 4c).

The acceptance line is "plan is sane, one confirmation, undo restores exactly",
and the third clause is the one worth most of these tests: a batch move that
cannot be reversed is worse than no batch move, because the alternative was
dragging thirty files by hand and *that* was reversible.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from sidecar.tools import organize
from sidecar.tools.organize import (
    Move,
    build_plan,
    organize_folder,
    preview_organize,
    undo_organize,
)
from sidecar.tools.registry import ToolContext

CTX = ToolContext(session_id="s_test", turn_id="t_test")


@pytest.fixture(autouse=True)
def undo_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Manifests go to a temp directory, never the real `data/undo`."""
    target = tmp_path / "undo"
    target.mkdir()

    class Fake:
        undo_dir = target

    monkeypatch.setattr(organize, "get_settings", lambda: Fake())
    organize.clear_plans()
    return target


def messy(root: Path) -> Path:
    """A Downloads folder as they actually look."""
    root.mkdir(parents=True, exist_ok=True)
    for name in (
        "invoice.pdf",
        "notes.txt",
        "holiday.png",
        "screenshot.PNG",
        "budget.xlsx",
        "setup.exe",
        "archive.zip",
        "script.py",
        "mystery.qqq",
    ):
        (root / name).write_text(name, encoding="utf-8")
    return root


# ── planning ──────────────────────────────────────────────────────────


def test_a_plan_groups_files_by_kind(tmp_path: Path) -> None:
    plan = build_plan(messy(tmp_path / "dl"), "by_type")

    destinations = {m.source.name: m.destination.parent.name for m in plan.moves}
    assert destinations["invoice.pdf"] == "Documents"
    assert destinations["holiday.png"] == "Images"
    assert destinations["budget.xlsx"] == "Spreadsheets"
    assert destinations["setup.exe"] == "Installers"
    assert destinations["archive.zip"] == "Archives"
    assert destinations["script.py"] == "Code"
    assert destinations["mystery.qqq"] == "Other", "an unknown kind still has a home"


def test_extensions_match_whatever_their_case(tmp_path: Path) -> None:
    plan = build_plan(messy(tmp_path / "dl"), "by_type")
    destinations = {m.source.name: m.destination.parent.name for m in plan.moves}
    assert destinations["screenshot.PNG"] == "Images"


def test_by_date_groups_by_month(tmp_path: Path) -> None:
    plan = build_plan(messy(tmp_path / "dl"), "by_date")
    month = datetime.now(UTC).strftime("%Y-%m")
    assert {m.destination.parent.name for m in plan.moves} == {month}


def test_planning_changes_nothing(tmp_path: Path) -> None:
    """It runs before the user has agreed to anything at all."""
    root = messy(tmp_path / "dl")
    before = sorted(p.name for p in root.iterdir())

    build_plan(root, "by_type")

    assert sorted(p.name for p in root.iterdir()) == before


def test_folders_and_part_files_are_left_alone(tmp_path: Path) -> None:
    """A `.crdownload` is a browser mid-write, and moving it corrupts the
    download. A folder is not this tool's business at all."""
    root = messy(tmp_path / "dl")
    (root / "a-folder").mkdir()
    (root / "big.iso.crdownload").write_text("partial", encoding="utf-8")
    (root / "desktop.ini").write_text("x", encoding="utf-8")
    (root / ".hidden").write_text("x", encoding="utf-8")

    names = {m.source.name for m in build_plan(root, "by_type").moves}

    assert "a-folder" not in names
    assert "big.iso.crdownload" not in names
    assert "desktop.ini" not in names
    assert ".hidden" not in names


def test_running_it_twice_does_not_re_sort_its_own_folders(tmp_path: Path) -> None:
    """Otherwise "organise Downloads" twice gives you Documents/Documents."""
    root = messy(tmp_path / "dl")
    (root / "Documents").mkdir()
    (root / "Documents" / "old.pdf").write_text("x", encoding="utf-8")

    plan = build_plan(root, "by_type")

    assert not any(m.source.name == "Documents" for m in plan.moves)
    assert not any("old.pdf" == m.source.name for m in plan.moves)


def test_a_name_collision_never_overwrites(tmp_path: Path) -> None:
    """Rule 5 calls overwriting destructive, and silently replacing one
    invoice.pdf with another looks like it worked."""
    root = tmp_path / "dl"
    root.mkdir()
    (root / "invoice.pdf").write_text("new", encoding="utf-8")
    (root / "Documents").mkdir()
    (root / "Documents" / "invoice.pdf").write_text("existing", encoding="utf-8")

    plan = build_plan(root, "by_type")

    assert plan.moves[0].destination.name == "invoice (1).pdf"
    assert (root / "Documents" / "invoice.pdf").read_text(encoding="utf-8") == "existing"


# ── one confirmation, showing the batch ───────────────────────────────


async def test_the_preview_describes_the_batch_not_the_arguments(tmp_path: Path) -> None:
    """§7.2: one confirm.request describing the batch, with the file list.
    `args` is `{path, strategy}` and says nothing about what will happen."""
    root = messy(tmp_path / "dl")

    preview = await preview_organize(str(root))

    assert preview is not None
    assert preview["kind"] == "move_plan"
    assert preview["count"] == 9
    assert "Documents" in preview["folders"]
    assert any(m["from"].endswith("invoice.pdf") for m in preview["moves"])


async def test_the_plan_shown_is_the_plan_that_runs(tmp_path: Path) -> None:
    """The whole reason the plan is stashed rather than recomputed.

    The user approves 9 moves; a browser finishes a download while the dialog
    is open; executing a fresh plan would move a 10th file nobody agreed to.
    """
    root = messy(tmp_path / "dl")
    preview = await preview_organize(str(root))
    assert preview is not None and preview["count"] == 9

    (root / "sneaky.pdf").write_text("arrived after approval", encoding="utf-8")
    result = await organize_folder(CTX, str(root))

    assert result.data["moved"] == 9
    assert (root / "sneaky.pdf").exists(), "it was never in the approved plan"


async def test_without_a_preview_it_still_works(tmp_path: Path) -> None:
    """A trusted folder, "always allow", or a direct call never previews."""
    root = messy(tmp_path / "dl")

    result = await organize_folder(CTX, str(root))

    assert result.ok
    assert result.data["moved"] == 9


# ── executing ─────────────────────────────────────────────────────────


async def test_files_actually_move(tmp_path: Path) -> None:
    root = messy(tmp_path / "dl")

    result = await organize_folder(CTX, str(root))

    assert result.ok
    assert (root / "Documents" / "invoice.pdf").exists()
    assert (root / "Images" / "holiday.png").exists()
    assert not (root / "invoice.pdf").exists()


async def test_an_already_tidy_folder_is_left_alone(tmp_path: Path) -> None:
    root = tmp_path / "dl"
    root.mkdir()

    result = await organize_folder(CTX, str(root))

    assert result.ok
    assert result.data["moved"] == 0
    assert "already tidy" in result.summary


async def test_it_refuses_a_system_folder() -> None:
    result = await organize_folder(CTX, "C:/Windows")

    assert not result.ok
    assert result.error == "refused"


async def test_it_refuses_a_strategy_it_does_not_have(tmp_path: Path) -> None:
    result = await organize_folder(CTX, str(messy(tmp_path / "dl")), strategy="by_vibes")

    assert not result.ok
    assert result.error == "strategy"
    assert "by_type" in result.summary, "a refusal names what would have worked"


# ── undo restores exactly ─────────────────────────────────────────────


async def test_undo_restores_exactly(tmp_path: Path) -> None:
    """The acceptance line, asserted literally: every file back where it was,
    with the same contents, and no folder left holding anything."""
    root = messy(tmp_path / "dl")
    before = {p.name: p.read_text(encoding="utf-8") for p in root.iterdir()}

    await organize_folder(CTX, str(root))
    undone = await undo_organize(CTX)

    assert undone.ok
    after = {p.name: p.read_text(encoding="utf-8") for p in root.iterdir() if p.is_file()}
    assert after == before
    assert all(not any(p.iterdir()) for p in root.iterdir() if p.is_dir())


async def test_a_manifest_is_written(tmp_path: Path, undo_dir: Path) -> None:
    root = messy(tmp_path / "dl")

    await organize_folder(CTX, str(root))

    manifests = list(undo_dir.glob("organize-*.json"))
    assert len(manifests) == 1
    payload = json.loads(manifests[0].read_text(encoding="utf-8"))
    assert payload["operation"] == "organize_folder"
    assert len(payload["moves"]) == 9
    assert Path(payload["moves"][0]["from"]).parent == root


async def test_the_manifest_is_consumed_so_undo_cannot_run_twice(
    tmp_path: Path, undo_dir: Path
) -> None:
    """A manifest left behind gets replayed, moving files that are already
    back — out of the folders they were just restored to."""
    root = messy(tmp_path / "dl")
    await organize_folder(CTX, str(root))

    assert (await undo_organize(CTX)).ok
    assert list(undo_dir.glob("organize-*.json")) == []

    again = await undo_organize(CTX)
    assert not again.ok
    assert again.error == "no_manifest"


async def test_undo_with_nothing_to_undo_says_so() -> None:
    result = await undo_organize(CTX)

    assert not result.ok
    assert result.error == "no_manifest"


async def test_undo_reports_a_file_that_has_since_been_moved(tmp_path: Path) -> None:
    """Half a restore is still worth doing, and the part that failed has to be
    said out loud rather than counted as success."""
    root = messy(tmp_path / "dl")
    await organize_folder(CTX, str(root))
    (root / "Images" / "holiday.png").unlink()

    result = await undo_organize(CTX)

    assert result.ok
    assert result.data["restored"] == 8
    assert result.display is not None
    assert any("holiday.png" in f for f in result.display["failures"])


async def test_undo_does_not_overwrite_something_that_took_the_name(
    tmp_path: Path,
) -> None:
    root = messy(tmp_path / "dl")
    await organize_folder(CTX, str(root))
    (root / "invoice.pdf").write_text("a different invoice", encoding="utf-8")

    await undo_organize(CTX)

    assert (root / "invoice.pdf").read_text(encoding="utf-8") == "a different invoice"
    assert (root / "invoice (1).pdf").read_text(encoding="utf-8") == "invoice.pdf"


def test_a_manifest_records_both_ends_of_every_move() -> None:
    """Undo is a replay of this file and nothing else, so a move missing
    either end is a file that cannot be put back."""
    move = Move(source=Path("C:/dl/a.pdf"), destination=Path("C:/dl/Documents/a.pdf"))
    assert move.as_json() == {"from": "C:\\dl\\a.pdf", "to": "C:\\dl\\Documents\\a.pdf"}
