"""Facts — what she has LEARNED about you (BUILD_SPEC §7.3 tier 3, §8.3).

A fact is a triple: `(subject, predicate, object)` plus a confidence. The table
and its UNIQUE-over-active index have existed since migration 1; this is the
first module to write to them.

The merge rules in `upsert` are §8.3 verbatim, and the order they run in is
load-bearing — see the docstring there.
"""

from __future__ import annotations

import sqlite3
import struct
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import TYPE_CHECKING

import structlog
from pydantic import BaseModel

from sidecar.memory import vectors
from sidecar.memory.db import Database
from sidecar.providers.embeddings import EmbeddingsUnavailable, OllamaEmbeddings

if TYPE_CHECKING:
    from collections.abc import Sequence

log = structlog.get_logger(__name__)

#: §8.3: "same subject+predicate, different object, cosine > 0.85 → supersede".
#:
#: **The threshold is the spec's; the "+predicate" half is not, and that is
#: deliberate.** §8.3 assumes a cloud model emitting stable predicates. Measured
#: on `qwen2.5:7b`, one sentence — "I usually work on Sillara pricing before
#: 10am" — came back across three reflections as `habitually`, `prefers` and
#: `works`, so keying on the predicate meant *nothing ever collided* and
#: contradictory facts piled up, all of them active, all of them going into the
#: same prompt. That is the exact failure the rule exists to prevent.
#:
#: Widening to same-subject is safe because the cosine is computed on the whole
#: sentence, and the measured gap is not close (`nomic-embed-text`):
#:
#:     0.97  user habitually works on X before 10am | user prefers ... before 10am
#:     0.92  user habitually works on X before 10am | user works on X in the evenings
#:     0.87  user habitually works on X before 10am | user works on X at weekends
#:     ----- 0.85 -------------------------------------------------------------
#:     0.73  user owns a bicycle                    | user owns a car
#:     0.54  user works on Sillara pricing          | user works on the quarterly report
#:     0.46  user works on Sillara pricing          | user lives in Perth
#:     0.39  user works on Sillara pricing          | user uses vim
#:
#: Re-run `scripts/gate_memory.py` step 3 before touching this number.
CONTRADICTION_COSINE = 0.85
#: §8.3: confidence never reaches certainty from repetition alone.
MAX_CONFIDENCE = 0.95
REINFORCE_STEP = 0.1
#: §8.3's decay rule, in whole days.
PRUNE_AFTER_DAYS = 30
PRUNE_CONFIDENCE = 0.3


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class FactSource(StrEnum):
    """Who asserted this. Decides whether a pin can block it."""

    USER = "user"
    REFLECTION = "reflection"


class MergeOutcome(StrEnum):
    """What `upsert` did. Reflection counts these into its report."""

    INSERTED = "inserted"
    REINFORCED = "reinforced"
    SUPERSEDED = "superseded"
    #: An existing pinned fact contradicted it, and reflection does not win.
    BLOCKED_BY_PIN = "blocked_by_pin"


class Fact(BaseModel):
    """A row from `facts`, as the UI, the prompt and the tools see it."""

    id: int
    subject: str
    predicate: str
    object: str
    confidence: float
    evidence_count: int
    user_locked: bool
    source_episode: int | None = None
    created_at: str
    updated_at: str
    superseded_by: int | None = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Fact:
        return cls(
            id=row["id"],
            subject=row["subject"],
            predicate=row["predicate"],
            object=row["object"],
            confidence=float(row["confidence"]),
            evidence_count=int(row["evidence_count"] or 0),
            user_locked=bool(row["user_locked"]),
            source_episode=row["source_episode"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            superseded_by=row["superseded_by"],
        )

    def sentence(self) -> str:
        """The form that gets embedded and shown in the prompt."""
        return f"{self.subject} {self.predicate.replace('_', ' ')} {self.object}"


class FactHit(BaseModel):
    """A fact with its retrieval scoring, for the panel and the prompt."""

    fact: Fact
    score: float
    cosine: float


def normalise_triple(subject: str, predicate: str, object_: str) -> tuple[str, str, str]:
    """Fold a triple to its stored form.

    The UNIQUE index is on the raw columns, so "Prefers" and "prefers" would be
    two facts without this. Predicates become `snake_case` because the model
    emits both "works on" and "works_on" for the same relation.
    """
    return (
        subject.strip().lower(),
        "_".join(predicate.strip().lower().split()),
        " ".join(object_.strip().split()),
    )


def sentence_for(subject: str, predicate: str, object_: str) -> str:
    return f"{subject} {predicate.replace('_', ' ')} {object_}"


def _unpack(blob: bytes | None) -> list[float] | None:
    """A stored `fact_vec` row back into floats, or None if it has no vector."""
    if not blob:
        return None
    raw = bytes(blob)
    return list(struct.unpack(f"<{len(raw) // 4}f", raw))


class SemanticMemory:
    """Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder."""

    def __init__(self, db: Database, embeddings: OllamaEmbeddings | None) -> None:
        self._db = db
        self._embeddings = embeddings

    # ── writing ──────────────────────────────────────────────────────────

    async def upsert(
        self,
        subject: str,
        predicate: str,
        object_: str,
        *,
        confidence: float = 0.6,
        source: FactSource = FactSource.REFLECTION,
        source_episode: int | None = None,
    ) -> tuple[MergeOutcome, int | None]:
        """Merge one observation into the store, per §8.3.

        Order matters:

        1. **Exact active triple first**, because it is a pure SQL lookup and
           the common case. Doing it before the embed means a repeated
           observation costs no inference at all.
        2. **Then the contradiction check**, which needs a vector.
        3. **Insert last**, so the two cheaper outcomes never pay for it.

        Returns the outcome and the id of the row that ended up active
        (`None` when a pin blocked the write).
        """
        subject, predicate, object_ = normalise_triple(subject, predicate, object_)
        if not subject or not predicate or not object_:
            return (MergeOutcome.BLOCKED_BY_PIN, None)

        reinforced = await self._reinforce_exact(subject, predicate, object_)
        if reinforced is not None:
            return (MergeOutcome.REINFORCED, reinforced)

        vector = await self._embed(sentence_for(subject, predicate, object_))
        rivals = await self._active_for(subject)

        contradicted = await self._find_contradiction(vector, rivals)
        if contradicted is not None:
            if contradicted.user_locked and source is FactSource.REFLECTION:
                # §8.3: a pinned fact is never superseded by reflection. Do not
                # insert the loser either — two contradictory facts both active
                # would both land in the same prompt, which is worse than
                # dropping the new one.
                log.info(
                    "memory.pin_protected",
                    kept=contradicted.id,
                    rejected=sentence_for(subject, predicate, object_),
                )
                return (MergeOutcome.BLOCKED_BY_PIN, None)

            new_id = await self._insert(
                subject,
                predicate,
                object_,
                confidence=confidence,
                source_episode=source_episode,
                user_locked=source is FactSource.USER,
                vector=vector,
                supersedes=contradicted.id,
            )
            log.info(
                "memory.superseded", old=contradicted.id, new=new_id, subject=subject
            )
            return (MergeOutcome.SUPERSEDED, new_id)

        new_id = await self._insert(
            subject,
            predicate,
            object_,
            confidence=confidence,
            source_episode=source_episode,
            user_locked=source is FactSource.USER,
            vector=vector,
        )
        return (MergeOutcome.INSERTED, new_id)

    async def _reinforce_exact(self, subject: str, predicate: str, object_: str) -> int | None:
        """§8.3: exact triple → evidence_count += 1, confidence += 0.1 (cap 0.95)."""
        now = _now()

        def _bump(conn: sqlite3.Connection) -> int | None:
            with conn:
                row = conn.execute(
                    """
                    SELECT id FROM facts
                    WHERE subject = ? AND predicate = ? AND object = ?
                      AND superseded_by IS NULL
                    """,
                    (subject, predicate, object_),
                ).fetchone()
                if row is None:
                    return None
                conn.execute(
                    """
                    UPDATE facts
                    SET evidence_count = evidence_count + 1,
                        confidence = MIN(?, confidence + ?),
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (MAX_CONFIDENCE, REINFORCE_STEP, now, row["id"]),
                )
                return int(row["id"])

        return await self._db.run(_bump)

    async def _insert(
        self,
        subject: str,
        predicate: str,
        object_: str,
        *,
        confidence: float,
        source_episode: int | None,
        user_locked: bool,
        vector: list[float] | None,
        supersedes: int | None = None,
    ) -> int:
        """Write the fact and its vector in one transaction.

        One transaction is not tidiness: a crash between the two would leave a
        fact that semantic search can never reach, and nothing would ever
        notice — it would simply never be recalled.
        """
        now = _now()
        packed = vectors.pack(vectors.normalise(vector)) if vector else None

        def _write(conn: sqlite3.Connection) -> int:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO facts
                        (subject, predicate, object, confidence, source_episode,
                         evidence_count, created_at, updated_at, user_locked)
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
                    """,
                    (
                        subject,
                        predicate,
                        object_,
                        confidence,
                        source_episode,
                        now,
                        now,
                        int(user_locked),
                    ),
                )
                new_id = int(cursor.lastrowid or 0)
                if packed is not None:
                    conn.execute(
                        "INSERT INTO fact_vec (fact_id, embedding) VALUES (?, ?)",
                        (new_id, packed),
                    )
                if supersedes is not None:
                    # After the insert, so the new row exists for the FK.
                    conn.execute(
                        "UPDATE facts SET superseded_by = ?, updated_at = ? WHERE id = ?",
                        (new_id, now, supersedes),
                    )
            return new_id

        return await self._db.run(_write)

    async def update(
        self,
        fact_id: int,
        *,
        object_: str | None = None,
        confidence: float | None = None,
        user_locked: bool | None = None,
    ) -> Fact | None:
        """Edit a fact from the panel. Returns None if it is gone."""
        sets: list[str] = []
        params: list[object] = []
        if object_ is not None:
            sets.append("object = ?")
            params.append(" ".join(object_.strip().split()))
        if confidence is not None:
            sets.append("confidence = ?")
            params.append(max(0.0, min(1.0, confidence)))
        if user_locked is not None:
            sets.append("user_locked = ?")
            params.append(int(user_locked))
        if not sets:
            return await self.get(fact_id)

        sets.append("updated_at = ?")
        params.extend([_now(), fact_id])

        def _apply(conn: sqlite3.Connection) -> None:
            with conn:
                conn.execute(f"UPDATE facts SET {', '.join(sets)} WHERE id = ?", params)

        await self._db.run(_apply)

        updated = await self.get(fact_id)
        if updated is not None and object_ is not None:
            # The text changed, so the stored vector is now wrong. Rewrite it
            # rather than leaving a fact that retrieves on its old wording.
            await self._revector(updated)
            updated = await self.get(fact_id)
        return updated

    async def forget(self, fact_id: int) -> bool:
        """Delete a fact outright. Returns whether it existed."""

        def _delete(conn: sqlite3.Connection) -> bool:
            with conn:
                # Anything pointing at it as a supersession must let go first,
                # or the FK rejects the delete.
                conn.execute(
                    "UPDATE facts SET superseded_by = NULL WHERE superseded_by = ?", (fact_id,)
                )
                conn.execute("DELETE FROM fact_vec WHERE fact_id = ?", (fact_id,))
                cursor = conn.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
                return bool(cursor.rowcount)

        removed = await self._db.run(_delete)
        if removed:
            log.info("memory.forgot", fact_id=fact_id)
        return removed

    async def prune(self, *, now: datetime | None = None) -> int:
        """§8.3: drop weak, single-sighting, unpinned facts after 30 days."""
        moment = now or datetime.now(UTC)
        cutoff = (moment - timedelta(days=PRUNE_AFTER_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")

        def _prune(conn: sqlite3.Connection) -> int:
            with conn:
                rows = conn.execute(
                    """
                    SELECT id FROM facts
                    WHERE confidence < ? AND evidence_count = 1 AND user_locked = 0
                      AND superseded_by IS NULL AND created_at < ?
                    """,
                    (PRUNE_CONFIDENCE, cutoff),
                ).fetchall()
                ids = [int(r["id"]) for r in rows]
                if not ids:
                    return 0
                marks = ",".join("?" * len(ids))
                conn.execute(
                    f"UPDATE facts SET superseded_by = NULL WHERE superseded_by IN ({marks})",
                    ids,
                )
                conn.execute(f"DELETE FROM fact_vec WHERE fact_id IN ({marks})", ids)
                conn.execute(f"DELETE FROM facts WHERE id IN ({marks})", ids)
                return len(ids)

        removed = await self._db.run(_prune)
        if removed:
            log.info("memory.pruned", facts=removed, older_than_days=PRUNE_AFTER_DAYS)
        return removed

    # ── reading ──────────────────────────────────────────────────────────

    async def get(self, fact_id: int) -> Fact | None:
        row = await self._db.run(
            lambda c: c.execute("SELECT * FROM facts WHERE id = ?", (fact_id,)).fetchone()
        )
        return Fact.from_row(row) if row else None

    async def list_facts(
        self, *, include_superseded: bool = False, limit: int = 500
    ) -> list[Fact]:
        where = "" if include_superseded else "WHERE superseded_by IS NULL"
        rows = await self._db.run(
            lambda c: c.execute(
                f"""
                SELECT * FROM facts {where}
                ORDER BY user_locked DESC, confidence DESC, updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        )
        return [Fact.from_row(r) for r in rows]

    async def count(self) -> int:
        row = await self._db.run(
            lambda c: c.execute(
                "SELECT COUNT(*) AS n FROM facts WHERE superseded_by IS NULL"
            ).fetchone()
        )
        return int(row["n"]) if row else 0

    async def search(self, vector: list[float], limit: int = 10) -> list[tuple[Fact, float]]:
        """Nearest active facts to a vector, as (fact, cosine).

        Mirrors `indexer.search_chunks`, but converts the L2 distance back to a
        cosine — see `vectors` for why that is exact here and not there.
        """
        packed = vectors.pack(vectors.normalise(vector))

        def _query(conn: sqlite3.Connection) -> list[tuple[Fact, float]]:
            rows = conn.execute(
                """
                SELECT f.*, v.distance
                FROM fact_vec v
                JOIN facts f ON f.id = v.fact_id
                WHERE v.embedding MATCH ? AND k = ?
                ORDER BY v.distance
                """,
                (packed, limit),
            ).fetchall()
            return [
                (Fact.from_row(r), vectors.cosine_from_l2(float(r["distance"])))
                for r in rows
                if r["superseded_by"] is None
            ]

        return await self._db.run(_query)

    # ── vectors ──────────────────────────────────────────────────────────

    async def backfill_vectors(self, limit: int = 50) -> int:
        """Embed facts written while Ollama was down.

        Chat must never wait on embeddings, so a fact is stored without one and
        picked up here on a later scheduler tick.
        """
        if self._embeddings is None:
            return 0

        rows = await self._db.run(
            lambda c: c.execute(
                """
                SELECT * FROM facts
                WHERE superseded_by IS NULL
                  AND id NOT IN (SELECT fact_id FROM fact_vec)
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        )
        done = 0
        for row in rows:
            if not await self._revector(Fact.from_row(row)):
                break
            done += 1
        if done:
            log.info("memory.backfilled", facts=done)
        return done

    async def _revector(self, fact: Fact) -> bool:
        vector = await self._embed(fact.sentence())
        if vector is None:
            return False
        packed = vectors.pack(vectors.normalise(vector))

        def _write(conn: sqlite3.Connection) -> None:
            with conn:
                conn.execute("DELETE FROM fact_vec WHERE fact_id = ?", (fact.id,))
                conn.execute(
                    "INSERT INTO fact_vec (fact_id, embedding) VALUES (?, ?)",
                    (fact.id, packed),
                )

        await self._db.run(_write)
        return True

    async def _embed(self, text: str) -> list[float] | None:
        """Embed, or None. Never raises — a fact without a vector still counts."""
        if self._embeddings is None:
            return None
        try:
            return await self._embeddings.embed(text)
        except EmbeddingsUnavailable as exc:
            log.warning("memory.embed_unavailable", error=str(exc))
            return None

    # ── merge helpers ────────────────────────────────────────────────────

    async def _active_for(self, subject: str) -> list[tuple[Fact, list[float] | None]]:
        """Every active fact about `subject`, each with its stored vector.

        One query joined against the vectors rather than a lookup per rival:
        widening the comparison from same-predicate to same-subject means this
        walks everything known about the user.

        **Nothing is excluded by object.** An earlier version skipped rivals
        sharing the new fact's object, reasoning that an identical triple was
        already handled — but the exact-triple case returns from
        `_reinforce_exact` before reaching here, so the only rows that
        exclusion removed were *same object, different predicate*: the
        `habitually` / `prefers` duplicate that a local model produces from one
        sentence, which is precisely what needs merging. Measured: it left both
        active and only one of them was ever superseded.
        """
        rows = await self._db.run(
            lambda c: c.execute(
                """
                SELECT f.*, v.embedding
                FROM facts f
                LEFT JOIN fact_vec v ON v.fact_id = f.id
                WHERE f.subject = ? AND f.superseded_by IS NULL
                """,
                (subject,),
            ).fetchall()
        )
        return [(Fact.from_row(r), _unpack(r["embedding"])) for r in rows]

    async def _find_contradiction(
        self, vector: list[float] | None, rivals: Sequence[tuple[Fact, list[float] | None]]
    ) -> Fact | None:
        """The closest fact about the same subject, above the §8.3 threshold.

        Same subject rather than same subject *and* predicate — see
        `CONTRADICTION_COSINE` for the measurement that forced that.

        With no embedder there is no cosine to compare, so nothing is
        superseded and the new fact simply joins the old one. That is the
        conservative direction: a duplicate is visible and fixable in the
        panel, a wrongly-deleted fact is not.
        """
        if vector is None or not rivals:
            return None

        best: Fact | None = None
        best_cos = CONTRADICTION_COSINE
        for rival, rival_vector in rivals:
            if rival_vector is None:
                continue
            cos = vectors.cosine(vector, rival_vector)
            if cos > best_cos:
                best, best_cos = rival, cos
        return best
