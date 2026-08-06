"""Durable settings and the v1 -> v2 migration.

The migration matters more than the store: an existing `data/aria.db` from
Phase 1 is at `user_version = 1` and must gain the settings table without losing
the conversation already in it.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from sidecar.memory.db import SCHEMA_PATH, SCHEMA_VERSION, Database, connect, table_names
from sidecar.memory.settings_store import ROUTING_BIAS, SELECTED_MODEL, SettingsStore


@pytest.fixture
def store(database: Database) -> SettingsStore:
    return SettingsStore(database)


async def test_default_is_returned_for_a_missing_key(store: SettingsStore) -> None:
    assert await store.get("nope", "fallback") == "fallback"


async def test_round_trips_a_string(store: SettingsStore) -> None:
    await store.set(SELECTED_MODEL, "gpt-5")
    assert await store.get(SELECTED_MODEL) == "gpt-5"


async def test_overwrites_rather_than_duplicating(store: SettingsStore) -> None:
    await store.set(SELECTED_MODEL, "gpt-5")
    await store.set(SELECTED_MODEL, "smart")
    assert await store.get(SELECTED_MODEL) == "smart"


@pytest.mark.parametrize("value", [42, True, None, ["a", "b"], {"k": "v"}, 1.5])
async def test_round_trips_any_json_value(store: SettingsStore, value: object) -> None:
    """Values are JSON so a new setting never needs another migration."""
    await store.set("probe", value)
    assert await store.get("probe") == value


async def test_corrupt_value_returns_the_default_instead_of_raising(
    store: SettingsStore, database: Database
) -> None:
    await store.set("broken", "fine")
    await database.run(
        lambda c: c.execute("UPDATE settings SET value = '{not json' WHERE key = 'broken'")
    )
    assert await store.get("broken", "fallback") == "fallback"


async def test_all_returns_every_setting(store: SettingsStore) -> None:
    await store.set(SELECTED_MODEL, "smart")
    await store.set(ROUTING_BIAS, "quality")
    assert await store.all() == {SELECTED_MODEL: "smart", ROUTING_BIAS: "quality"}


# ── migration ─────────────────────────────────────────────────────────


def test_fresh_database_lands_on_the_current_version(
    database: Database, conn: sqlite3.Connection
) -> None:
    assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    assert "settings" in table_names(conn)


def test_selected_model_is_seeded_to_smart(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT value FROM settings WHERE key = 'selected_model'").fetchone()
    assert row["value"] == '"smart"'


def test_migrate_is_idempotent(database: Database) -> None:
    assert database.migrate() == SCHEMA_VERSION
    assert database.migrate() == SCHEMA_VERSION


def test_upgrades_a_v1_database_without_losing_messages(tmp_path: Path) -> None:
    """The realistic case: a Phase 1 database already holding a conversation."""
    db_path = tmp_path / "v1.db"

    # Build a v1 database by hand — schema.sql stamped at user_version = 1.
    raw = connect(db_path)
    with raw:
        raw.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        raw.execute("PRAGMA user_version=1")
        raw.execute(
            "INSERT INTO sessions (id, started_at) VALUES ('s_old', '2026-01-01T00:00:00Z')"
        )
        raw.execute(
            "INSERT INTO messages (session_id, role, content, created_at) "
            "VALUES ('s_old', 'user', 'remember me', '2026-01-01T00:00:00Z')"
        )
    raw.close()

    db = Database(db_path)
    try:
        assert db.migrate() == SCHEMA_VERSION
        conn = db._conn  # noqa: SLF001
        assert "settings" in table_names(conn)
        survived = conn.execute("SELECT content FROM messages WHERE session_id='s_old'").fetchone()
        assert survived["content"] == "remember me"
        # Migration 3 clears empty sessions; one holding a message must survive.
        assert conn.execute("SELECT 1 FROM sessions WHERE id='s_old'").fetchone()
    finally:
        db.close()
