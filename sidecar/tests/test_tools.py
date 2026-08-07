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
from sidecar.tools.apps import AppEntry, Launch, best, list_windows, normalise, rank
from sidecar.tools.files import delete_file, known_folder, move_file, open_path
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


# ── finding the app someone meant ─────────────────────────────────────
# A pure function over a fake index: no PowerShell, no registry, no launching.


def app(label: str) -> AppEntry:
    return AppEntry(label, label, Launch.APPS_FOLDER)


INDEX = [
    app("7-Zip File Manager"),
    app("7-Zip Help"),
    app("Adobe Photoshop 2023"),
    app("Calculator"),
    app("Calendar"),
    app("Calendar (Microsoft 365)"),
    app("YouTube Music"),
    app("Spotify"),
    app("Visual Studio Code"),
]


@pytest.mark.parametrize(
    ("said", "expected"),
    [
        ("calculator", "Calculator"),
        ("Calculator", "Calculator"),
        ("spotify", "Spotify"),
        # Punctuation and number words — two of the four original failures.
        ("7 zip", "7-Zip File Manager"),
        ("seven zip", "7-Zip File Manager"),
        ("7zip", "7-Zip File Manager"),
        # Typos — the other two.
        ("photoshp", "Adobe Photoshop 2023"),
        ("youtbe music", "YouTube Music"),
        ("calulator", "Calculator"),
        # Word order and partial names.
        ("photoshop", "Adobe Photoshop 2023"),
        ("code", "Visual Studio Code"),
    ],
)
def test_it_finds_the_app_however_it_was_said(said: str, expected: str) -> None:
    match = best(said, INDEX)
    assert match is not None and match.label == expected


def test_a_help_entry_never_beats_the_app() -> None:
    """"7 zip" matched "7-Zip Help" purely because it is the shorter name."""
    match = best("7 zip", INDEX)
    assert match is not None and "Help" not in match.label


def test_asking_for_help_still_finds_help() -> None:
    """The demotion must not make the entry unreachable."""
    match = best("7 zip help", INDEX)
    assert match is not None and match.label == "7-Zip Help"


def test_the_shortest_name_wins_a_tie() -> None:
    match = best("calendar", INDEX)
    assert match is not None and match.label == "Calendar"


def test_nonsense_matches_nothing() -> None:
    """Opening the wrong app is worse than opening nothing."""
    assert best("qwertyuiop nonsense", INDEX) is None
    assert best("zzzz", INDEX) is None


def test_exact_only_refuses_a_near_match() -> None:
    """This is what stops "open youtube" launching the YouTube Music app: the
    website is checked between the exact and fuzzy passes."""
    assert best("youtube", INDEX, exact_only=True) is None
    assert best("youtube music", INDEX, exact_only=True) is not None


def test_ranking_offers_the_near_misses() -> None:
    """A dead end is useless; naming the closest lets the model retry."""
    labels = [entry.label for _, entry in rank("calend", INDEX)]
    assert "Calendar" in labels


@pytest.mark.parametrize(
    ("raw", "folded"),
    [
        ("7-Zip File Manager", "7 zip file manager"),
        ("seven zip", "7 zip"),
        ("  Visual   Studio  Code ", "visual studio code"),
        ("CapCut", "capcut"),
    ],
)
def test_normalisation_folds_what_should_not_matter(raw: str, folded: str) -> None:
    assert normalise(raw) == folded


# ── opening folders ───────────────────────────────────────────────────
# She was asked to "open downloads folder", had no tool for it, and answered
# "Opened Downloads." anyway. These exist so that gap cannot reopen quietly.


@pytest.mark.parametrize(
    "said",
    ["downloads", "Downloads", "my downloads folder", "the downloads folder", "DOWNLOADS"],
)
def test_a_named_folder_is_found_however_it_was_said(said: str) -> None:
    found = known_folder(said)
    assert found is not None and found.name.lower() == "downloads"


@pytest.mark.parametrize("place", ["documents", "desktop", "pictures", "music", "videos", "home"])
def test_the_usual_places_all_resolve(place: str) -> None:
    found = known_folder(place)
    assert found is not None and found.exists()


def test_it_uses_the_real_location_not_a_guess() -> None:
    """OneDrive relocates Documents and Desktop by default, so joining onto
    %USERPROFILE% is wrong on a very ordinary machine."""
    found = known_folder("documents")
    assert found is not None
    assert found.is_absolute()


def test_a_path_is_not_a_named_folder() -> None:
    assert known_folder("C:/Users/somebody/notes.txt") is None
    assert known_folder("blorptastic") is None


async def test_open_path_refuses_what_is_not_there(tmp_path: Path) -> None:
    """The whole point: when it cannot be done she must say so, not claim it."""
    result = await open_path(CTX, path=str(tmp_path / "nothing-here"))
    assert not result.ok
    assert result.error == "missing"


async def test_open_path_opens_a_real_folder(tmp_path: Path) -> None:
    result = await open_path(CTX, path=str(tmp_path))
    assert result.ok
    assert result.data["kind"] == "folder"
