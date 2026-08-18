"""What the router decided, and what the user made of it (§9.7).

§9.7's closing paragraph is a plan, and this is the first half of it: *"Log every
routing decision with the provider, the resulting turn's latency and a user
thumbs-up/down. After a few weeks you'll have a labelled dataset to tune the
rules against — that's the upgrade path, not a bigger model."*

None of it existed. `messages.route` held the string `'local'` or `'cloud'`, so
after the fact there was no way to ask which model answered a turn, which stage
chose it, or what bias was in force. "Smart mode isn't that good" was a real
complaint about a real failure — a spoken "increase the volume" could only ever
reach the weakest model in the catalog — and the only way it was found was
reading a structlog line by hand.

**Nothing here runs on the critical path.** The row is written after the reply
has been streamed, and every method swallows its own errors: a routing log that
can break a turn is worse than no routing log.

The second half of §9.7's plan — tuning the rules against the labels — is
deliberately not built. There is no data yet, and rules fitted to no data are
just the same rules with more code around them. `ModelInfo.tool_score` is the
measured stand-in until there is.
"""

from __future__ import annotations

import asyncio
import sqlite3
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import structlog
from pydantic import BaseModel

if TYPE_CHECKING:
    from sidecar.memory.db import Database

log = structlog.get_logger(__name__)

#: A thumbs-down needs at least this many rated turns behind it before it means
#: anything about a model rather than about one bad afternoon.
MIN_RATINGS_FOR_SIGNAL = 10


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class RoutingRecord(BaseModel):
    """One turn's routing decision, as it is written down."""

    message_id: int | None = None
    session_id: str | None = None
    model: str
    provider: str
    local: bool
    stage: str
    detail: str = ""
    bias: str
    spoken: bool = False
    tool_shaped: bool = False
    chars: int = 0
    latency_ms: int | None = None
    tool_called: str | None = None
    tool_ok: bool | None = None


class ModelVerdict(BaseModel):
    """How a model has actually been received, per `routing_log`."""

    model: str
    turns: int
    rated: int
    liked: int
    disliked: int

    @property
    def approval(self) -> float | None:
        """Liked as a fraction of rated, or None while it would be noise."""
        if self.rated < MIN_RATINGS_FOR_SIGNAL:
            return None
        return self.liked / self.rated


class RoutingLog:
    """Writes and reads `routing_log`. Never raises into the turn path."""

    def __init__(self, db: Database) -> None:
        self._db = db

    async def record(self, record: RoutingRecord) -> int | None:
        """Write one decision. Returns its id, or None if it could not be."""

        def _insert(conn: sqlite3.Connection) -> int:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO routing_log
                        (message_id, session_id, model, provider, local, stage,
                         detail, bias, spoken, tool_shaped, chars, latency_ms,
                         tool_called, tool_ok, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.message_id,
                        record.session_id,
                        record.model,
                        record.provider,
                        int(record.local),
                        record.stage,
                        record.detail,
                        record.bias,
                        int(record.spoken),
                        int(record.tool_shaped),
                        record.chars,
                        record.latency_ms,
                        record.tool_called,
                        None if record.tool_ok is None else int(record.tool_ok),
                        _now(),
                    ),
                )
            return int(cursor.lastrowid or 0)

        try:
            return await self._db.run(_insert)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — never worth failing a turn over
            log.warning("routing.log_failed", error=str(exc))
            return None

    async def rate(self, message_id: int, rating: int) -> bool:
        """Attach a thumbs-up or thumbs-down to the turn that message answered.

        Keyed on the message rather than the routing row, because the message id
        is what the renderer has — it never sees this table.
        """
        value = 1 if rating > 0 else -1

        def _update(conn: sqlite3.Connection) -> int:
            with conn:
                cursor = conn.execute(
                    "UPDATE routing_log SET rating = ?, rated_at = ? WHERE message_id = ?",
                    (value, _now(), message_id),
                )
            return cursor.rowcount

        try:
            changed = await self._db.run(_update)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            log.warning("routing.rate_failed", error=str(exc))
            return False

        if changed:
            log.info("routing.rated", message_id=message_id, rating=value)
        return bool(changed)

    async def clear_rating(self, message_id: int) -> bool:
        """Un-rate a turn. Pressing the same thumb twice means "never mind"."""

        def _update(conn: sqlite3.Connection) -> int:
            with conn:
                cursor = conn.execute(
                    "UPDATE routing_log SET rating = NULL, rated_at = NULL "
                    "WHERE message_id = ?",
                    (message_id,),
                )
            return cursor.rowcount

        try:
            return bool(await self._db.run(_update))
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            log.warning("routing.rate_failed", error=str(exc))
            return False

    async def rating_for(self, message_id: int) -> int | None:
        row = await self._db.run(
            lambda c: c.execute(
                "SELECT rating FROM routing_log WHERE message_id = ?", (message_id,)
            ).fetchone()
        )
        return None if row is None or row["rating"] is None else int(row["rating"])

    async def ratings_for_session(self, session_id: str) -> dict[int, int]:
        """Every rating in one conversation, so the panel can render them."""
        rows = await self._db.run(
            lambda c: c.execute(
                "SELECT message_id, rating FROM routing_log "
                "WHERE session_id = ? AND rating IS NOT NULL",
                (session_id,),
            ).fetchall()
        )
        return {int(r["message_id"]): int(r["rating"]) for r in rows if r["message_id"]}

    async def verdicts(self) -> list[ModelVerdict]:
        """Per-model tallies. The dataset §9.7 wants, as far as it has grown."""

        def _query(conn: sqlite3.Connection) -> list[sqlite3.Row]:
            return conn.execute(
                """
                SELECT model,
                       COUNT(*) AS turns,
                       COUNT(rating) AS rated,
                       COALESCE(SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END), 0) AS liked,
                       COALESCE(SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END), 0) AS disliked
                FROM routing_log
                GROUP BY model
                ORDER BY turns DESC
                """
            ).fetchall()

        rows = await self._db.run(_query)
        return [
            ModelVerdict(
                model=str(r["model"]),
                turns=int(r["turns"]),
                rated=int(r["rated"]),
                liked=int(r["liked"]),
                disliked=int(r["disliked"]),
            )
            for r in rows
        ]
