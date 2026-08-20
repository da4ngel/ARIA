"""Phase 0 acceptance gate: the database is created and migrated from schema.sql."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from sidecar.memory.db import SCHEMA_VERSION, Database, current_version, table_names

# BUILD_SPEC §7.3
EXPECTED_TABLES = {
    "sessions",
    "messages",
    "episodes",
    "facts",
    "procedures",
    "affect_state",
    "file_index",
    "file_chunks",
    "tool_log",
    "study_subjects",
    "concepts",
    "concept_mastery",
}
EXPECTED_VEC_TABLES = {"episode_vec", "fact_vec", "file_vec"}


def test_db_file_is_created(db_path: Path, database: Database) -> None:
    assert db_path.exists()
    assert database.path == db_path


def test_sqlite_vec_extension_loads(conn: sqlite3.Connection) -> None:
    version = conn.execute("SELECT vec_version()").fetchone()[0]
    assert version.startswith("v0.1")


def test_all_schema_tables_exist(conn: sqlite3.Connection) -> None:
    names = table_names(conn)
    assert EXPECTED_TABLES <= names, f"missing: {EXPECTED_TABLES - names}"


def test_vec0_virtual_tables_exist(conn: sqlite3.Connection) -> None:
    names = table_names(conn)
    assert EXPECTED_VEC_TABLES <= names, f"missing: {EXPECTED_VEC_TABLES - names}"


def test_vec0_tables_accept_768_dim_embeddings(conn: sqlite3.Connection) -> None:
    """The schema declares float[768]; prove it round-trips."""
    import struct

    embedding = struct.pack("768f", *([0.01] * 768))
    conn.execute("INSERT INTO fact_vec (fact_id, embedding) VALUES (1, ?)", (embedding,))
    assert conn.execute("SELECT COUNT(*) FROM fact_vec").fetchone()[0] == 1


def test_user_version_is_set(conn: sqlite3.Connection) -> None:
    assert current_version(conn) == SCHEMA_VERSION


def test_wal_mode_enabled(conn: sqlite3.Connection) -> None:
    assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"


def test_foreign_keys_enforced(conn: sqlite3.Connection) -> None:
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) "
            "VALUES ('no-such-session', 'user', 'hi', '2026-08-06T00:00:00Z')"
        )
    conn.rollback()


def test_affect_state_singleton_is_seeded(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        "SELECT id, warmth, energy, playfulness, concern FROM affect_state"
    ).fetchall()
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == 1
    assert (row["warmth"], row["energy"], row["playfulness"], row["concern"]) == (
        0.6,
        0.6,
        0.5,
        0.2,
    )


def test_message_role_check_constraint(conn: sqlite3.Connection) -> None:
    conn.execute("INSERT INTO sessions (id, started_at) VALUES ('s1', '2026-08-06T00:00:00Z')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) "
            "VALUES ('s1', 'wizard', 'hi', '2026-08-06T00:00:00Z')"
        )
    conn.rollback()


def test_migration_is_idempotent(db_path: Path) -> None:
    first = Database(db_path)
    assert first.migrate() == SCHEMA_VERSION
    first.close()

    second = Database(db_path)
    assert second.migrate() == SCHEMA_VERSION  # no-op, no error
    second.close()


async def test_run_executes_off_the_event_loop(database: Database) -> None:
    count = await database.run(
        lambda c: c.execute("SELECT COUNT(*) FROM affect_state").fetchone()[0]
    )
    assert count == 1
