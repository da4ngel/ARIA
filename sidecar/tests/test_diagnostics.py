"""Export diagnostics — and the one thing it must never contain.

An export exists to be sent to somebody else. That makes it the single place
in this codebase where a leak is not a leak into a log file on the user's own
machine but into an email — so the tests that matter here are the negative
ones: no credential value, no conversation, no database.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from sidecar.core import diagnostics
from sidecar.providers.credentials import CredentialKey, CredentialStatus


@pytest.fixture()
def archive(tmp_path: Path):
    """Build one export and hand back both the zip and its raw bytes."""

    async def build() -> tuple[zipfile.ZipFile, bytes]:
        path = await diagnostics.export(tmp_path / "d.zip")
        raw = path.read_bytes()
        return zipfile.ZipFile(path), raw

    return build


async def test_it_writes_a_report_and_the_three_logs(archive) -> None:
    zf, _ = await archive()
    names = set(zf.namelist())
    assert "report.json" in names
    # Written even when empty: an absent file reads as "somebody forgot this",
    # a zero-byte one says plainly that there was nothing to collect.
    assert {"logs/sidecar.log", "logs/sidecar.out.log", "logs/electron.log"} <= names


async def test_no_credential_value_reaches_the_archive(
    archive, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**`hint` is the last four characters of a real key.**

    Fine on the user's own screen, and four characters of a secret in a file
    they are about to attach to a bug report. `_credential_presence` drops it;
    this asserts it against the *whole archive*, not just the field, because
    the failure that matters is the string being present anywhere at all.
    """
    monkeypatch.setattr(
        "sidecar.providers.credentials.all_status",
        lambda: [
            CredentialStatus(key=CredentialKey.OPENAI, present=True, hint="Zk9Q"),
            CredentialStatus(key=CredentialKey.GEMINI, present=False, hint=None),
        ],
    )
    zf, raw = await archive()
    assert b"Zk9Q" not in raw

    report = json.loads(zf.read("report.json"))
    creds = {c["key"]: c["present"] for c in report["credentials"]}
    # Presence is the useful half and is kept — "is a key configured at all"
    # is the first question any support conversation asks.
    assert creds["openai_api_key"] is True
    assert creds["gemini_api_key"] is False
    assert all("hint" not in c for c in report["credentials"])


async def test_the_database_is_described_but_never_copied(archive) -> None:
    zf, _ = await archive()
    # `aria.db` holds every message she has ever seen. Its size and existence
    # are diagnostic; its contents are the conversation.
    assert not any(name.endswith(".db") for name in zf.namelist())
    env = json.loads(zf.read("report.json"))["environment"]
    assert "db_bytes" in env and "db_exists" in env


async def test_a_long_log_is_tailed_and_starts_on_a_line_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`sidecar.log` has no rotation and no size cap.

    An uncapped copy produces an archive nobody can open, and the tail is the
    part that describes whatever just went wrong. Landing mid-line would make
    the first entry look corrupt, which is the opposite of diagnostic.
    """
    log = tmp_path / "big.log"
    log.write_bytes(b"".join(f"line {i:06d}\n".encode() for i in range(20_000)))

    body = diagnostics._tail(log, limit=1_000)  # noqa: SLF001
    assert len(body) <= 1_000
    assert body.startswith(b"line ")
    assert body.endswith(b"line 019999\n")


def test_a_missing_log_is_empty_rather_than_an_error(tmp_path: Path) -> None:
    assert diagnostics._tail(tmp_path / "nothing.log") == b""  # noqa: SLF001


async def test_one_unreadable_section_does_not_fail_the_export(
    archive, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A partial export beats none.

    The moment this is reached is the moment something is already broken, so
    a section that raises must not be the reason the user cannot send
    anything at all.
    """

    def boom() -> list[CredentialStatus]:
        raise RuntimeError("credential manager unavailable")

    monkeypatch.setattr("sidecar.providers.credentials.all_status", boom)
    zf, _ = await archive()
    report = json.loads(zf.read("report.json"))
    assert report["credentials"] == []
    assert report["environment"]["sidecar_version"]
