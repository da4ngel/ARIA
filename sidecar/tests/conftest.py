"""Shared fixtures. Every test gets a throwaway data dir — never the real data/."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from sidecar.memory.db import Database


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "aria.db"


@pytest.fixture
def database(db_path: Path) -> Iterator[Database]:
    """A migrated database on a temp path."""
    db = Database(db_path)
    db.migrate()
    yield db
    db.close()


@pytest.fixture
def conn(database: Database) -> sqlite3.Connection:
    """Raw connection to the migrated database, for schema assertions."""
    # Tests are single-threaded; reaching past the lock keeps assertions readable.
    return database._conn  # noqa: SLF001
