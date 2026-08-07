"""The six tools, and mostly the paths where they refuse.

`delete_file` is tested against files this creates in a temporary directory.
Nothing here touches anything real, which is also why the forbidden-root cases
below assert on *paths that do exist* — refusing a path that was never there
would prove nothing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import sidecar.tools  # noqa: F401 — registers everything
from sidecar.tools.apps import list_windows
from sidecar.tools.files import delete_file, move_file
from sidecar.tools.registry import Tier, ToolContext, get, schemas
from sidecar.tools.system import get_system_info

CTX = ToolContext(session_id="s_test")


# ── the tiers are the policy ──────────────────────────────────────────


@pytest.mark.parametrize(
    ("name", "tier"),
    [
        ("list_windows", Tier.AUTO),
        ("get_system_info", Tier.AUTO),
        ("open_app", Tier.SAFE),
        ("set_volume", Tier.SAFE),
        ("move_file", Tier.CONFIRM),
        ("delete_file", Tier.DANGER),
    ],
)
def test_each_tool_sits_at_its_declared_tier(name: str, tier: Tier) -> None:
    tool = get(name)
    assert tool is not None, f"{name} is not registered"
    assert tool.tier is tier


def test_deleting_is_never_offered_to_the_model_by_default() -> None:
    """DANGER is off by default, and a tool the model cannot see is one it
    cannot be talked into using."""
    offered = {s["function"]["name"] for s in schemas()}
    assert "delete_file" not in offered
    assert "move_file" in offered, "CONFIRM is offered; it just has to ask"


# ── delete refuses more than it accepts ───────────────────────────────


async def test_it_deletes_a_file_it_was_pointed_at(tmp_path: Path) -> None:
    target = tmp_path / "scratch.txt"
    target.write_text("delete me")

    result = await delete_file(CTX, path=str(target))

    assert result.ok
    assert not target.exists()
    assert "scratch.txt" in result.summary


@pytest.mark.parametrize("path", ["C:/Windows/System32", "C:/Program Files", "C:/ProgramData"])
async def test_it_refuses_system_directories(path: str) -> None:
    result = await delete_file(CTX, path=path)
    assert not result.ok
    assert result.error == "path"


async def test_it_refuses_a_drive_root() -> None:
    result = await delete_file(CTX, path="C:/")
    assert not result.ok
    assert result.error == "path"


async def test_it_refuses_a_folder(tmp_path: Path) -> None:
    """A folder is a much larger promise than a file, and this tool says file."""
    folder = tmp_path / "keep"
    folder.mkdir()
    (folder / "inside.txt").write_text("still here")

    result = await delete_file(CTX, path=str(folder))

    assert not result.ok
    assert result.error == "is_dir"
    assert (folder / "inside.txt").exists()


async def test_a_missing_file_is_said_plainly(tmp_path: Path) -> None:
    result = await delete_file(CTX, path=str(tmp_path / "never.txt"))
    assert not result.ok
    assert result.error == "missing"


# ── move ──────────────────────────────────────────────────────────────


async def test_it_moves_a_file(tmp_path: Path) -> None:
    src = tmp_path / "a.txt"
    src.write_text("contents")
    dst = tmp_path / "sub"
    dst.mkdir()

    result = await move_file(CTX, source=str(src), destination=str(dst / "b.txt"))

    assert result.ok
    assert not src.exists()
    assert (dst / "b.txt").read_text() == "contents"


async def test_it_will_not_overwrite_on_a_move(tmp_path: Path) -> None:
    """Overwriting is a different destructive act from moving, and the user
    approved a move."""
    src = tmp_path / "a.txt"
    src.write_text("new")
    dst = tmp_path / "b.txt"
    dst.write_text("precious")

    result = await move_file(CTX, source=str(src), destination=str(dst))

    assert not result.ok
    assert result.error == "exists"
    assert dst.read_text() == "precious"
    assert src.exists(), "and the source is left alone too"


async def test_it_refuses_a_missing_destination_folder(tmp_path: Path) -> None:
    src = tmp_path / "a.txt"
    src.write_text("x")

    result = await move_file(CTX, source=str(src), destination=str(tmp_path / "nope" / "b.txt"))

    assert not result.ok
    assert result.error == "dir"
    assert src.exists()


# ── the read-only pair actually read the machine ──────────────────────


async def test_system_info_reports_this_machine() -> None:
    result = await get_system_info(CTX)
    assert result.ok
    assert result.data["ram_total_gb"] > 0
    assert "CPU" in result.summary


async def test_listing_windows_summarises_rather_than_dumps() -> None:
    """§7.2's second failure mode: the model gets one line, the UI gets the lot."""
    result = await list_windows(CTX)
    assert result.ok
    assert "\n" not in result.summary
    if result.data:
        assert result.display is not None
