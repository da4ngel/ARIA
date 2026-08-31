"""SQLite connection, sqlite-vec loading, and the migration runner.

One connection for the process, guarded by a lock. BUILD_SPEC §7.3's snippet uses
``check_same_thread=False`` on a bare connection; under async FastAPI that is a
data race, so every call goes through :meth:`Database.run` -> ``asyncio.to_thread``
while the lock serialises actual sqlite access.

Migrations are tracked with ``PRAGMA user_version``. Version 1 is ``schema.sql``.
"""

from __future__ import annotations

import asyncio
import sqlite3
import threading
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

import sqlite_vec
import structlog

log = structlog.get_logger(__name__)

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
MIGRATIONS_DIR = Path(__file__).parent
SCHEMA_VERSION = 10

T = TypeVar("T")


def connect(db_path: Path) -> sqlite3.Connection:
    """Open the database with sqlite-vec loaded and the required pragmas set."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def current_version(conn: sqlite3.Connection) -> int:
    row = conn.execute("PRAGMA user_version").fetchone()
    return int(row[0])


def migrate(conn: sqlite3.Connection) -> int:
    """Bring the database up to :data:`SCHEMA_VERSION`. Returns the version applied.

    Idempotent: a database already at the target version is left untouched.
    """
    version = current_version(conn)
    if version >= SCHEMA_VERSION:
        return version

    started_at = version
    if version == 0:
        _apply_sql(conn, SCHEMA_PATH, target_version=1)
        version = 1
    if version == 1:
        _apply_sql(conn, MIGRATIONS_DIR / "schema_002.sql", target_version=2)
        version = 2
    if version == 2:
        _apply_sql(conn, MIGRATIONS_DIR / "schema_003.sql", target_version=3)
        version = 3
    if version == 3:
        _apply_sql(conn, MIGRATIONS_DIR / "schema_004.sql", target_version=4)
        version = 4
    if version == 4:
        _apply_sql(conn, MIGRATIONS_DIR / "schema_005.sql", target_version=5)
        version = 5
    if version == 5:
        _apply_sql(conn, MIGRATIONS_DIR / "schema_006.sql", target_version=6)
        version = 6
    if version == 6:
        _apply_sql(conn, MIGRATIONS_DIR / "schema_007.sql", target_version=7)
        version = 7
    if version == 7:
        _apply_sql(conn, MIGRATIONS_DIR / "schema_008.sql", target_version=8)
        version = 8
    if version == 8:
        _apply_sql(conn, MIGRATIONS_DIR / "schema_009.sql", target_version=9)
        version = 9
    if version == 9:
        _apply_sql(conn, MIGRATIONS_DIR / "schema_010.sql", target_version=10)
        version = 10

    log.info("db.migrated", from_version=started_at, to_version=version)
    return version


def _apply_sql(conn: sqlite3.Connection, path: Path, *, target_version: int) -> None:
    """Apply one migration file atomically and stamp `user_version`.

    The vec0 virtual tables in schema.sql require the sqlite-vec extension, which
    :func:`connect` has already loaded.
    """
    sql = path.read_text(encoding="utf-8")
    try:
        with conn:
            conn.executescript(sql)
            conn.execute(f"PRAGMA user_version={target_version}")
    except sqlite3.Error as exc:
        raise RuntimeError(
            f"Failed to apply {path.name} to the database. "
            f"SQLite said: {exc}. Delete data/aria.db and restart to rebuild it "
            f"from scratch; if that fails, the sqlite-vec extension is not loading."
        ) from exc


class Database:
    """Async-safe wrapper around the single sqlite connection."""

    def __init__(self, db_path: Path) -> None:
        self._path = db_path
        self._conn = connect(db_path)
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self._path

    def migrate(self) -> int:
        with self._lock:
            return migrate(self._conn)

    async def run(self, fn: Callable[[sqlite3.Connection], T]) -> T:
        """Run ``fn`` against the connection off the event loop, serialised."""

        def _call() -> T:
            with self._lock:
                return fn(self._conn)

        return await asyncio.to_thread(_call)

    def close(self) -> None:
        with self._lock:
            self._conn.close()


def table_names(conn: sqlite3.Connection) -> set[str]:
    """Every table in the database, including vec0 virtual tables."""
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {row[0] for row in rows}
