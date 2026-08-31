"""Export diagnostics — one zip a person can attach to a bug report.

BUILD_SPEC §9 Phase 9 asks for this beside crash reporting. **The sidecar
builds the archive, not Electron**, for two reasons: Node has no built-in zip
and Python has `zipfile`, so this costs no dependency; and `data/` belongs to
the sidecar (rule 1), which also means it is the only side that knows where
`aria.db`, the logs and the undo manifests actually are once frozen.

**Nothing here reads a credential value.** `credentials.py` never logs one and
this must not become the first thing that does — the whole point of an export
is that somebody sends it to somebody else. Presence and provider name only.

The logs are tail-capped. `sidecar.log` has no rotation and no size cap, so an
uncapped copy would produce an archive nobody can open, and the tail is the
part that describes whatever just went wrong.
"""

from __future__ import annotations

import io
import json
import os
import platform
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

log = structlog.get_logger(__name__)

#: Bytes kept from the end of each log file. Roughly the last few thousand
#: lines — enough to cover a session, small enough to email.
LOG_TAIL_BYTES = 2_000_000


def _tail(path: Path, limit: int = LOG_TAIL_BYTES) -> bytes:
    """The last `limit` bytes of a file, or b"" if it is not there."""
    try:
        size = path.stat().st_size
        with path.open("rb") as fh:
            if size > limit:
                fh.seek(size - limit)
                # The seek lands mid-line; drop the partial one so the first
                # entry in the export is not a fragment that looks corrupt.
                fh.readline()
            return fh.read()
    except OSError:
        return b""


def _credential_presence() -> list[dict[str, Any]]:
    """Which providers have a key, and never what it is."""
    from sidecar.providers.credentials import all_status

    try:
        # **`hint` is deliberately dropped.** It is the last four characters
        # of the key, which is fine on the user's own screen and is four
        # characters of a secret in a file they are about to email someone.
        return [{"key": str(s.key), "present": s.present} for s in all_status()]
    except Exception:  # noqa: BLE001 - an export must not fail on one section
        log.warning("diagnostics.credentials_unreadable", exc_info=True)
        return []


async def _health() -> dict[str, Any]:
    from sidecar.rpc.handlers import system_health

    try:
        report: dict[str, Any] = await system_health({})
        return report
    except Exception:  # noqa: BLE001
        log.warning("diagnostics.health_unreadable", exc_info=True)
        return {}


def _environment() -> dict[str, Any]:
    """The build, the OS and where things are. No user content."""
    from sidecar.config import get_settings
    from sidecar.memory.db import SCHEMA_VERSION
    from sidecar.rpc.handlers import SIDECAR_VERSION

    settings = get_settings()
    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "sidecar_version": SIDECAR_VERSION,
        "schema_version": SCHEMA_VERSION,
        "frozen": bool(getattr(sys, "frozen", False)),
        "python": sys.version,
        "platform": platform.platform(),
        "windows_build": platform.version(),
        "data_dir": str(settings.data_dir),
        "db_exists": settings.db_path.exists(),
        "db_bytes": settings.db_path.stat().st_size if settings.db_path.exists() else 0,
    }


async def build_report() -> dict[str, Any]:
    """Everything the archive describes, as one JSON-able mapping."""
    return {
        "environment": _environment(),
        "health": await _health(),
        "credentials": _credential_presence(),
    }


async def export(destination: Path | None = None) -> Path:
    """Write the archive and return its path.

    `destination` is for tests; production writes into the data directory,
    which is somewhere the user can already reach and which the installer
    does not replace.
    """
    from sidecar.config import get_settings

    settings = get_settings()
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    path = destination or (settings.data_dir / f"aria-diagnostics-{stamp}.zip")
    path.parent.mkdir(parents=True, exist_ok=True)

    report = await build_report()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("report.json", json.dumps(report, indent=2, default=str))
        for name in ("sidecar.log", "sidecar.out.log", "electron.log"):
            body = _tail(settings.log_dir / name)
            # Written even when empty, so "there is no Electron log" is
            # visible in the archive rather than being an absent file that
            # looks like it was forgotten.
            archive.writestr(f"logs/{name}", body)

    # Written in one go: a half-finished zip left behind by a crash mid-write
    # is a file that looks like an export and cannot be opened.
    path.write_bytes(buffer.getvalue())
    log.info("diagnostics.exported", path=str(path), bytes=path.stat().st_size)
    return path


def reveal(path: Path) -> None:
    """Show the archive in Explorer. Best effort — the path is returned anyway."""
    try:
        os.startfile(str(path.parent))
    except OSError:
        log.info("diagnostics.reveal_failed", path=str(path), exc_info=True)
