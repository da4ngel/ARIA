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


def test_the_fallback_matches_package_json() -> None:
    """**The drift guard.** Bump `package.json` and this fails until the
    fallback follows, which is the only moment anybody would think to."""
    assert handlers.FALLBACK_VERSION == _package_version()


def test_electron_wins_when_it_says_anything(monkeypatch: pytest.MonkeyPatch) -> None:
    """An installed app is whatever electron-updater last installed, and the
    sidecar ships inside it — so the number Electron holds is the true one and
    a stale constant must not override it."""
    monkeypatch.setenv("ARIA_APP_VERSION", "9.9.9")
    import importlib

    reloaded = importlib.reload(handlers)
    try:
        assert reloaded.SIDECAR_VERSION == "9.9.9"
    finally:
        # The module registers every RPC method at import, and a reload with
        # the variable still set would leave the whole process reporting 9.9.9.
        monkeypatch.delenv("ARIA_APP_VERSION", raising=False)
        importlib.reload(handlers)


def test_an_empty_value_falls_back_rather_than_reporting_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`ARIA_APP_VERSION=` is what a shell gives you for an unset variable it
    still exports. Reporting "" as the version is worse than reporting a
    slightly stale number."""
    monkeypatch.setenv("ARIA_APP_VERSION", "")
    import importlib

    reloaded = importlib.reload(handlers)
    try:
        assert reloaded.SIDECAR_VERSION == handlers.FALLBACK_VERSION
    finally:
        monkeypatch.delenv("ARIA_APP_VERSION", raising=False)
        importlib.reload(handlers)
