"""One version, reported by two processes that cannot see each other.

`SIDECAR_VERSION` was a bare literal in `handlers.py`, independent of
`package.json`. They agreed only by coincidence — and the moment auto-update
exists, a version bump happens in `package.json` alone, which would leave
`system.health.version` and every exported diagnostic naming a version nothing
is running. A wrong version in a bug report is worse than none: it sends
whoever reads it looking at the wrong code.

Electron is authoritative and passes `ARIA_APP_VERSION`. This file guards the
half Electron cannot: the fallback the gate scripts and `npm run sidecar` get.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sidecar.rpc import handlers

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _package_version() -> str:
    return str(json.loads((REPO_ROOT / "package.json").read_text(encoding="utf8"))["version"])


def test_the_reported_version_is_package_jsons(monkeypatch: pytest.MonkeyPatch) -> None:
    """**Derived, not restated.**

    The first version of this asserted the *literal* equalled `package.json`
    and went red when it did not. That was a real drift guard and it also
    meant every release edited two files in lockstep, on the one action that
    happens most often. Reading the manifest makes drift impossible rather
    than merely detected — so a version bump is one line, and this asserts
    the property that actually matters.
    """
    monkeypatch.delenv("ARIA_APP_VERSION", raising=False)
    assert handlers._detect_version() == _package_version()  # noqa: SLF001


def test_the_literal_is_only_for_a_frozen_run_with_no_manifest(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """`--selftest` on the bundled exe is exactly this: frozen, no Electron,
    and no `package.json` anywhere beside it."""
    monkeypatch.delenv("ARIA_APP_VERSION", raising=False)
    monkeypatch.setattr(handlers, "REPO_ROOT", tmp_path)

    assert handlers._detect_version() == handlers.FALLBACK_VERSION  # noqa: SLF001


def test_electron_wins_over_everything(monkeypatch: pytest.MonkeyPatch) -> None:
    """Once packaged, Electron is the only thing that knows.

    The sidecar is frozen inside the app and cannot see `package.json` at
    all — and after an update the app is whatever electron-updater last
    installed, so a value read from anywhere else would be stale.
    """
    monkeypatch.setenv("ARIA_APP_VERSION", "9.9.9")
    assert handlers._detect_version() == "9.9.9"  # noqa: SLF001


def test_an_empty_value_falls_back_rather_than_reporting_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`ARIA_APP_VERSION=` is what a shell gives you for a variable it exports
    without setting. Reporting "" as the version is worse than reporting a
    slightly stale one."""
    monkeypatch.setenv("ARIA_APP_VERSION", "")
    assert handlers._detect_version() == _package_version()  # noqa: SLF001
