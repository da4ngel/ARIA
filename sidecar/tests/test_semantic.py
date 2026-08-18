"""The §8.3 merge rules, one test per branch.

The pin test is the important one: it is the only thing standing between a
fact the user asserted by hand and an overnight model call that disagrees.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta

import pytest

from sidecar.memory.db import Database
from sidecar.memory.semantic import (
    MAX_CONFIDENCE,
    SUPERSEDED_AFTER_DAYS,
    FactSource,
    MergeOutcome,
    SemanticMemory,
    normalise_triple,
)
from sidecar.providers.embeddings import DIMENSIONS


def _vector(*leading: float) -> list[float]:
    """Pad to the 768 the `vec0` tables are declared for.

    sqlite-vec enforces the width, so a 3-element stub is rejected at insert —
    which is worth knowing rather than working around with a mock database.
    """
    return [*leading, *([0.0] * (DIMENSIONS - len(leading)))]


class StubEmbeddings:
    """Deterministic vectors keyed by a substring, so cosine is controllable.

    Real embeddings would make "is this over 0.85" a property of nomic-embed
    rather than of the merge logic, which is what these tests are about.
    """

    def __init__(self) -> None:
        self.calls = 0

    async def embed(self, text: str) -> list[float]:
        self.calls += 1
        lowered = text.lower()
        # Two nearly-parallel vectors for the "same thing, said differently"
        # case, and an orthogonal one for anything else.
        if "morning" in lowered or "10am" in lowered:
            return _vector(1.0, 0.02)
        if "evening" in lowered:
            return _vector(0.99, 0.14)
        if "weekend" in lowered:
            return _vector(0.98, 0.2)
        # A different subject matter entirely — the measured controls sit at
        # 0.39-0.73, well under the threshold.
        if "bicycle" in lowered:
            return _vector(0.5, 0.87)
        return _vector(0.0, 0.0, 1.0)


@pytest.fixture
def memory(database: Database) -> SemanticMemory:
    return SemanticMemory(database, StubEmbeddings())  # type: ignore[arg-type]


# ── normalisation ─────────────────────────────────────────────────────


def test_triples_are_folded_before_storage() -> None:
    """The UNIQUE index is on raw columns, so "Prefers" and "prefers" would
    otherwise be two facts."""
    assert normalise_triple(" User ", "Works On", "  Sillara   pricing ") == (
        "user",
        "works_on",
        "Sillara pricing",
    )


# ── §8.3 branch 1: exact triple reinforces ────────────────────────────


@pytest.mark.anyio
async def test_an_exact_repeat_reinforces_rather_than_duplicating(
    memory: SemanticMemory,
) -> None:
    first, fact_id = await memory.upsert("user", "prefers", "short answers")
    assert first is MergeOutcome.INSERTED

    again, same_id = await memory.upsert("user", "prefers", "short answers")
    assert again is MergeOutcome.REINFORCED
    assert same_id == fact_id

    fact = await memory.get(fact_id or 0)
    assert fact is not None
    assert fact.evidence_count == 2
    assert fact.confidence == pytest.approx(0.7)
    assert len(await memory.list_facts()) == 1


@pytest.mark.anyio
async def test_confidence_never_reaches_certainty(memory: SemanticMemory) -> None:
    """§8.3 caps at 0.95. Repetition is evidence, not proof."""
    _, fact_id = await memory.upsert("user", "prefers", "short answers")
    for _ in range(20):
        await memory.upsert("user", "prefers", "short answers")

    fact = await memory.get(fact_id or 0)
    assert fact is not None
    assert fact.confidence == pytest.approx(MAX_CONFIDENCE)


@pytest.mark.anyio
async def test_reinforcing_costs_no_embedding(database: Database) -> None:
    """The exact-match check runs before the embed, deliberately — a repeated
    observation is the common case and should cost no inference."""
    stub = StubEmbeddings()
    memory = SemanticMemory(database, stub)  # type: ignore[arg-type]

    await memory.upsert("user", "prefers", "short answers")
    after_insert = stub.calls
    await memory.upsert("user", "prefers", "short answers")

    assert stub.calls == after_insert


# ── §8.3 branch 2: a contradiction supersedes ─────────────────────────


@pytest.mark.anyio
async def test_a_near_identical_object_supersedes_the_old_fact(
    memory: SemanticMemory,
) -> None:
    _, old_id = await memory.upsert("user", "works_on", "pricing in the morning")
    outcome, new_id = await memory.upsert("user", "works_on", "pricing in the evening")

    assert outcome is MergeOutcome.SUPERSEDED
    old = await memory.get(old_id or 0)
    assert old is not None
    assert old.superseded_by == new_id

    active = await memory.list_facts()
    assert [f.id for f in active] == [new_id]


@pytest.mark.anyio
async def test_an_unrelated_object_does_not_supersede(memory: SemanticMemory) -> None:
    """Below the 0.85 threshold both facts are true at once."""
    await memory.upsert("user", "works_on", "pricing in the morning")
    outcome, _ = await memory.upsert("user", "works_on", "a completely different project")

    assert outcome is MergeOutcome.INSERTED
    assert len(await memory.list_facts()) == 2


@pytest.mark.anyio
async def test_the_same_relation_under_a_different_predicate_still_supersedes(
    memory: SemanticMemory,
) -> None:
    """§8.3 says "same subject+predicate". Measured against `qwen2.5:7b`, one
    sentence comes back as `habitually`, `prefers` and `works` across three
    reflections — so keying on the predicate meant nothing ever collided and
    contradictory facts piled up. See CONTRADICTION_COSINE for the numbers."""
    _, old_id = await memory.upsert("user", "habitually", "works on pricing in the morning")
    outcome, new_id = await memory.upsert("user", "works", "on pricing in the evening")

    assert outcome is MergeOutcome.SUPERSEDED
    old = await memory.get(old_id or 0)
    assert old is not None
    assert old.superseded_by == new_id


@pytest.mark.anyio
async def test_one_sentence_extracted_as_two_predicates_collapses(
    memory: SemanticMemory,
) -> None:
    """A local model routinely emits one statement as two facts with the same
    object and different predicates — `habitually` *and* `prefers`.

    Measured in the gate: both stayed active, and a later contradiction
    superseded only one of them, leaving the other contradicting it forever.
    The rivals query must not skip a row just because its object matches; the
    identical-triple case has already returned by then.
    """
    _, first = await memory.upsert("user", "habitually", "works on pricing in the morning")
    outcome, second = await memory.upsert("user", "prefers", "works on pricing in the morning")

    assert outcome is MergeOutcome.SUPERSEDED
    old = await memory.get(first or 0)
    assert old is not None
    assert old.superseded_by == second
    assert len(await memory.list_facts()) == 1


@pytest.mark.anyio
async def test_widening_to_the_subject_does_not_merge_unrelated_facts(
    memory: SemanticMemory,
) -> None:
    """The control for the rule above. Every fact is about 'user', so the
    threshold is the only thing keeping them apart — and measured, it is not
    close: 0.39-0.73 for unrelated facts against 0.87+ for restatements."""
    await memory.upsert("user", "works_on", "pricing in the morning")
    outcome, _ = await memory.upsert("user", "owns", "a bicycle")

    assert outcome is MergeOutcome.INSERTED
    assert len(await memory.list_facts()) == 2


# ── §8.3 branch 3: a pin blocks reflection ────────────────────────────


@pytest.mark.anyio
async def test_reflection_cannot_supersede_a_pinned_fact(memory: SemanticMemory) -> None:
    """The gate's fourth line. A fact the user asserted survives an overnight
    model call that contradicts it."""
    _, pinned_id = await memory.upsert(
        "user", "works_on", "pricing in the morning", source=FactSource.USER
    )
    pinned_before = await memory.get(pinned_id or 0)
    assert pinned_before is not None
    assert pinned_before.user_locked

    outcome, new_id = await memory.upsert(
        "user", "works_on", "pricing in the evening", source=FactSource.REFLECTION
    )

    assert outcome is MergeOutcome.BLOCKED_BY_PIN
    assert new_id is None
    # The loser is not inserted either: two contradictory active facts would
    # both land in the same prompt.
    active = await memory.list_facts()
    assert [f.id for f in active] == [pinned_id]
    after = await memory.get(pinned_id or 0)
    assert after is not None
    assert after.superseded_by is None
    assert after.object == pinned_before.object


@pytest.mark.anyio
async def test_the_user_may_override_their_own_pin(memory: SemanticMemory) -> None:
    """§8.3: pinned facts are superseded "only by the user"."""
    _, pinned_id = await memory.upsert(
        "user", "works_on", "pricing in the morning", source=FactSource.USER
    )
    outcome, new_id = await memory.upsert(
        "user", "works_on", "pricing in the evening", source=FactSource.USER
    )

    assert outcome is MergeOutcome.SUPERSEDED
    old = await memory.get(pinned_id or 0)
    assert old is not None
    assert old.superseded_by == new_id
    # The replacement stays pinned — it is still the user's assertion.
    new = await memory.get(new_id or 0)
    assert new is not None
    assert new.user_locked


# ── editing, forgetting, pruning ──────────────────────────────────────


@pytest.mark.anyio
async def test_pinning_from_the_panel_protects_a_learned_fact(
    memory: SemanticMemory,
) -> None:
    _, fact_id = await memory.upsert("user", "works_on", "pricing in the morning")
    await memory.update(fact_id or 0, user_locked=True)

    outcome, _ = await memory.upsert(
        "user", "works_on", "pricing in the evening", source=FactSource.REFLECTION
    )
    assert outcome is MergeOutcome.BLOCKED_BY_PIN


@pytest.mark.anyio
async def test_forget_removes_the_fact_and_its_vector(
    memory: SemanticMemory, conn: sqlite3.Connection
) -> None:
    _, fact_id = await memory.upsert("user", "prefers", "short answers")
    assert conn.execute("SELECT COUNT(*) FROM fact_vec").fetchone()[0] == 1

    assert await memory.forget(fact_id or 0)
    assert await memory.get(fact_id or 0) is None
    assert conn.execute("SELECT COUNT(*) FROM fact_vec").fetchone()[0] == 0


@pytest.mark.anyio
async def test_forgetting_a_superseded_fact_does_not_trip_the_foreign_key(
    memory: SemanticMemory,
) -> None:
    """`facts.superseded_by` references `facts(id)`, so the pointer has to be
    released before the row goes."""
    _, old_id = await memory.upsert("user", "works_on", "pricing in the morning")
    _, new_id = await memory.upsert("user", "works_on", "pricing in the evening")

    assert await memory.forget(old_id or 0)
    assert await memory.get(new_id or 0) is not None


@pytest.mark.anyio
async def test_forgetting_an_absent_fact_reports_it(memory: SemanticMemory) -> None:
    assert not await memory.forget(9999)


@pytest.mark.anyio
async def test_editing_the_object_rewrites_the_vector(database: Database) -> None:
    """Otherwise the fact keeps retrieving on its old wording."""
    stub = StubEmbeddings()
    memory = SemanticMemory(database, stub)  # type: ignore[arg-type]

    _, fact_id = await memory.upsert("user", "works_on", "pricing in the morning")
    before = stub.calls
    await memory.update(fact_id or 0, object_="pricing in the evening")

    assert stub.calls > before


@pytest.mark.anyio
async def test_prune_drops_only_weak_unpinned_single_sightings(
    database: Database, conn: sqlite3.Connection
) -> None:
    """§8.3: confidence < 0.3, evidence_count = 1, older than 30 days."""
    stale = (datetime.now(UTC) - timedelta(days=40)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Built with no embedder so nothing supersedes anything: supersession is a
    # different rule and it would eat the fixture before prune ever ran.
    memory = SemanticMemory(database, None)
    await memory.upsert("user", "guesses", "something weak", confidence=0.2)
    await memory.upsert("user", "believes", "something confident", confidence=0.8)
    await memory.upsert(
        "user", "asserts", "something pinned", confidence=0.2, source=FactSource.USER
    )
    await memory.upsert("user", "repeats", "something seen twice", confidence=0.2)
    await memory.upsert("user", "repeats", "something seen twice", confidence=0.2)
    with conn:
        conn.execute("UPDATE facts SET created_at = ?", (stale,))

    assert await memory.prune() == 1
    remaining = {f.object for f in await memory.list_facts()}
    assert remaining == {"something confident", "something pinned", "something seen twice"}


@pytest.mark.anyio
async def test_prune_spares_a_recent_weak_fact(memory: SemanticMemory) -> None:
    """The 30-day clock is what makes a low-confidence guess recoverable."""
    await memory.upsert("user", "guesses", "something weak", confidence=0.2)
    assert await memory.prune() == 0


# ── working without embeddings ────────────────────────────────────────


@pytest.mark.anyio
async def test_a_fact_is_still_stored_with_no_embedder(database: Database) -> None:
    """Chat must never wait on Ollama, so a missing embedder costs recall
    quality — never the fact itself."""
    memory = SemanticMemory(database, None)
    outcome, fact_id = await memory.upsert("user", "prefers", "short answers")

    assert outcome is MergeOutcome.INSERTED
    assert await memory.get(fact_id or 0) is not None


@pytest.mark.anyio
async def test_backfill_embeds_facts_written_while_ollama_was_down(
    database: Database, conn: sqlite3.Connection
) -> None:
    without = SemanticMemory(database, None)
    await without.upsert("user", "prefers", "short answers")
    assert conn.execute("SELECT COUNT(*) FROM fact_vec").fetchone()[0] == 0

    with_embedder = SemanticMemory(database, StubEmbeddings())  # type: ignore[arg-type]
    assert await with_embedder.backfill_vectors() == 1
    assert conn.execute("SELECT COUNT(*) FROM fact_vec").fetchone()[0] == 1


# ── the audit trail, eventually ───────────────────────────────────────


async def test_superseded_facts_survive_the_ordinary_prune(memory: SemanticMemory) -> None:
    """`prune` leaves them alone on purpose — they are what MemoryPanel shows
    as "this replaced that", and losing them the moment a belief changes
    would make every correction untraceable."""
    await memory.upsert("user", "works_on", "Sillara pricing", source=FactSource.USER)
    await memory.upsert("user", "works_on", "the ARIA sidecar", source=FactSource.USER)

    removed = await memory.prune(now=datetime.now(UTC) + timedelta(days=400))

    superseded = [f for f in await memory.list_facts(include_superseded=True) if f.superseded_by]
    assert superseded, "the trail is still there"
    assert removed == 0


async def test_an_old_superseded_fact_is_eventually_dropped(memory: SemanticMemory) -> None:
    """They are never retrieved and never reach a prompt, so the only cost of
    keeping one is storage and the only value is being able to look. After
    six months nobody looks."""
    await memory.upsert("user", "works_on", "Sillara pricing", source=FactSource.USER)
    await memory.upsert("user", "works_on", "the ARIA sidecar", source=FactSource.USER)

    removed = await memory.prune_superseded(
        now=datetime.now(UTC) + timedelta(days=SUPERSEDED_AFTER_DAYS + 1)
    )

    assert removed == 1
    remaining = await memory.list_facts(include_superseded=True)
    assert all(f.superseded_by is None for f in remaining)
    assert any("ARIA sidecar" in f.object for f in remaining), "the live fact is untouched"


async def test_a_recently_superseded_fact_is_kept(memory: SemanticMemory) -> None:
    await memory.upsert("user", "works_on", "Sillara pricing", source=FactSource.USER)
    await memory.upsert("user", "works_on", "the ARIA sidecar", source=FactSource.USER)

    assert await memory.prune_superseded(now=datetime.now(UTC) + timedelta(days=30)) == 0
