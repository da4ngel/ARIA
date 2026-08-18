"""`browser.setup`'s launcher detection.

The bug this guards against was real, not hypothetical: the first version
hardcoded `chrome.exe`, and on the reference machine the actual default
browser is Brave (CLAUDE.md, Phase 3). A launcher that starts the *wrong*
browser starts it with an empty, logged-out profile — which defeats the
entire point of connecting over CDP rather than launching a fresh one.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sidecar.rpc.handlers import _default_browser, _write_browser_launcher
from sidecar.tools.apps import AppEntry, Launch


def test_a_non_chrome_default_is_detected_and_used(monkeypatch: pytest.MonkeyPatch) -> None:
    import sidecar.tools.apps as apps_module

    monkeypatch.setattr(
        apps_module,
        "default_app",
        lambda query: AppEntry(
            "Brave",
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            Launch.EXECUTABLE,
        ),
    )
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\test\AppData\Local")

    detected = _default_browser()

    assert detected is not None
    exe, profile = detected
    assert exe.lower().endswith("brave.exe")
    assert "BraveSoftware" in profile
    assert "Chrome" not in profile


def test_an_undetectable_default_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    import sidecar.tools.apps as apps_module

    monkeypatch.setattr(apps_module, "default_app", lambda query: None)

    assert _default_browser() is None


def test_a_non_chromium_default_is_not_guessed_at(monkeypatch: pytest.MonkeyPatch) -> None:
    """Firefox is a real default browser some people have, and CDP does not
    work with it the same way — better to fall through to "unknown" than to
    write a launcher that silently does nothing useful."""
    import sidecar.tools.apps as apps_module

    monkeypatch.setattr(
        apps_module,
        "default_app",
        lambda query: AppEntry(
            "Firefox", r"C:\Program Files\Mozilla Firefox\firefox.exe", Launch.EXECUTABLE
        ),
    )

    assert _default_browser() is None


def test_a_store_app_default_is_not_treated_as_an_executable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import sidecar.tools.apps as apps_module

    monkeypatch.setattr(
        apps_module,
        "default_app",
        lambda query: AppEntry(
            "Some Store Browser", "SomeVendor.App_8wekyb3d8bbwe", Launch.APPS_FOLDER
        ),
    )

    assert _default_browser() is None


def test_the_launcher_names_the_detected_browser_by_full_path(tmp_path: Path) -> None:
    target = tmp_path / "start.bat"

    brave = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    _write_browser_launcher(target, (brave, r"C:\profile"))

    script = target.read_text(encoding="utf-8")
    assert r'"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"' in script
    assert "--remote-debugging-port=9222" in script
    assert r'--user-data-dir="C:\profile"' in script


def test_a_failed_detection_falls_back_to_a_guess_not_a_crash(tmp_path: Path) -> None:
    target = tmp_path / "start.bat"

    _write_browser_launcher(target, None)

    script = target.read_text(encoding="utf-8")
    assert "chrome.exe" in script
