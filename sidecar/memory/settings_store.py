"""Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).

Values are JSON so a setting can be a scalar, list, or object without a
migration each time. First user is the selected model.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

import structlog

from sidecar.memory.db import Database

log = structlog.get_logger(__name__)

SELECTED_MODEL = "selected_model"
# `core.router.RoutingBias` — how much latency to trade for a better answer.
ROUTING_BIAS = "routing_bias"
# Whether the microphone stays open for "hey jarvis". Persisted rather than
# defaulted on, because an always-open microphone is the user's decision to
# make once and have remembered — not one to rediscover on every launch.
WAKE_WORD_ENABLED = "wake_word_enabled"
ONLINE_MODE = "online_mode"
# Folders she may act in without asking, as a JSON array. Empty until added by
# hand: trust here covers deletion, which is too large a thing to assume on
# someone's behalf.
TRUSTED_PATHS = "trusted_paths"
# The global preset over the same confirmation machinery —
# `sidecar.tools.permissions.PermissionMode` as a plain string. Defaults to
# "auto" (today's behavior) when unset, same as `TRUSTED_PATHS` defaults to
# empty rather than needing a migration.
PERMISSION_MODE = "permission_mode"
# Folders she keeps half an eye on, as a JSON array of absolute paths.
# **Empty until named**, which is what keeps §9's "file event on a watched
# project" trigger from being noise: a build directory churns constantly, a
# folder somebody deliberately pointed at does not.
WATCHED_PROJECTS = "watched_projects"
# What the cloud providers last said they offer, as a list of serialised
# `ModelInfo`. Cached so the picker fills in at startup without a network
# round-trip, and so it still lists something when the machine is offline.
DISCOVERED_MODELS = "discovered_models"
# When that listing was fetched, ISO-8601. Read to decide whether it is stale.
DISCOVERED_AT = "discovered_at"


class SettingsStore:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get(self, key: str, default: Any = None) -> Any:
        row = await self._db.run(
            lambda c: c.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        )
        if row is None:
            return default
        try:
            return json.loads(row["value"])
        except json.JSONDecodeError:
            log.warning("settings.corrupt_value", key=key)
            return default

    async def set(self, key: str, value: Any) -> None:
        payload = json.dumps(value)
        now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        def _upsert(conn: sqlite3.Connection) -> None:
            with conn:
                conn.execute(
                    "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value, "
                    "updated_at = excluded.updated_at",
                    (key, payload, now),
                )

        await self._db.run(_upsert)
        log.info("settings.set", key=key)

    async def all(self) -> dict[str, Any]:
        rows = await self._db.run(
            lambda c: list(c.execute("SELECT key, value FROM settings").fetchall())
        )
        out: dict[str, Any] = {}
        for row in rows:
            try:
                out[row["key"]] = json.loads(row["value"])
            except json.JSONDecodeError:
                continue
        return out
