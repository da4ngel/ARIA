"""Retrieval, and the 80ms budget that shapes it (§9 Phase 5).

The mechanisms are the tests. "Most turns retrieve nothing" is only true if
nothing embeds on a trivial message, so that is asserted on the embed *call
count* rather than on the result — a version that embedded and then discarded
would pass a result-only check while blowing the budget.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest

from sidecar.core import context as ctx
from sidecar.memory.db import Database
from sidecar.memory.episodic import EpisodicMemory
from sidecar.memory.messages import ConversationStore
from sidecar.memory.retrieval import (
    MAX_FACTS,
    MIN_SCORE,
    Retriever,
    recency_decay,
    score,
)
from sidecar.memory.semantic import FactSource, SemanticMemory
from sidecar.providers.base import StreamDelta
from sidecar.providers.embeddings import DIMENSIONS, EmbeddingsUnavailable


def _vector(*leading: float) -> list[float]:
    return [*leading, *([0.0] * (DIMENSIONS - len(leading)))]


class StubEmbeddings:
    """Counts calls, and can be made slow or broken on demand."""

    def __init__(self, *, delay_s: float = 0.0, working: bool = True) -> None:
        self.calls = 0
        self.delay_s = delay_s
        self.working = working

    async def embed(self, text: str) -> list[float]:
        self.calls += 1
        if self.delay_s:
            await asyncio.sleep(self.delay_s)
        if not self.working:
            raise EmbeddingsUnavailable("Ollama is not running.")
        lowered = text.lower()
        if "pricing" in lowered or "sillara" in lowered:
            return _vector(1.0, 0.05)
        return _vector(0.0, 1.0)


class StubProvider:
    async def stream_chat(
        self, messages: object, **kwargs: object
    ) -> AsyncIterator[StreamDelta]:
        yield StreamDelta(text='{"summary": "s", "salience": 0.5}', done=True)


def _retriever(
    database: Database, embeddings: StubEmbeddings | None, **kwargs: object
) -> Retriever:
    store = ConversationStore(database)
    semantic = SemanticMemory(database, embeddings)  # type: ignore[arg-type]
    episodic = EpisodicMemory(
        database,
        embeddings,  # type: ignore[arg-type]
        store,
        StubProvider(),  # type: ignore[arg-type]
        "qwen2.5:7b",
    )
    return Retriever(semantic, episodic, embeddings, **kwargs)  # type: ignore[arg-type]


# ── the scoring formula ───────────────────────────────────────────────


def test_recency_halves_over_a_month() -> None:
    assert recency_decay(0) == pytest.approx(1.0)
    assert recency_decay(30) == pytest.approx(0.5)
    assert recency_decay(60) == pytest.approx(0.25)


def test_the_score_is_the_spec_formula() -> None:
    """0.6·cosine + 0.25·recency + 0.15·salience, plus the access nudge."""
    got = score(cosine=1.0, age_days=0.0, weight=1.0, access_count=10)
    assert got == pytest.approx(0.6 + 0.25 + 0.15 + 0.05)

    fresh_but_irrelevant = score(cosine=0.0, age_days=0.0, weight=1.0, access_count=0)
    assert fresh_but_irrelevant == pytest.approx(0.25 + 0.15)


def test_relevance_outweighs_recency() -> None:
    """0.6 against 0.25 — an old fact about the question beats a new one about
    something else, which is the whole point of the weighting."""
    relevant_old = score(cosine=0.9, age_days=365.0, weight=0.6, access_count=0)
    irrelevant_new = score(cosine=0.1, age_days=0.0, weight=0.6, access_count=0)
    assert relevant_old > irrelevant_new


def test_the_access_boost_saturates() -> None:
    """A memory that keeps coming up is worth surfacing, but not enough to
    outrank relevance."""
    once = score(cosine=0.5, age_days=0.0, weight=0.5, access_count=1)
    often = score(cosine=0.5, age_days=0.0, weight=0.5, access_count=100)
    assert often - once < 0.05


# ── mechanism 1: most turns cost nothing ──────────────────────────────


@pytest.mark.anyio
@pytest.mark.parametrize("message", ["ok", "thanks", "yes", "go on", "hey aria", "  Stop. "])
async def test_a_trivial_message_never_embeds(database: Database, message: str) -> None:
    stub = StubEmbeddings()
    retriever = _retriever(database, stub)

    result = await retriever.retrieve(message)

    assert result.empty
    # The call count *is* the mechanism. A version that embedded and then
    # threw the result away would pass a result-only assertion.
    assert stub.calls == 0


@pytest.mark.anyio
async def test_an_empty_store_never_embeds(database: Database) -> None:
    """A fresh install answers every turn with no memory to search."""
    stub = StubEmbeddings()
    retriever = _retriever(database, stub)

    result = await retriever.retrieve("what am I working on at the moment?")

    assert result.empty
    assert stub.calls == 0


# ── mechanism 3: the deadline ─────────────────────────────────────────


@pytest.mark.anyio
async def test_a_slow_embed_degrades_instead_of_blowing_the_budget(
    database: Database,
) -> None:
    stub = StubEmbeddings(delay_s=0.5)
    retriever = _retriever(database, stub, deadline_s=0.05)
    semantic = SemanticMemory(database, None)
    await semantic.upsert("user", "works_on", "Sillara pricing before 10am")

    result = await retriever.retrieve("what am I working on for Sillara pricing?")

    assert result.degraded
    assert result.took_ms < 400  # the deadline held, not the 500ms embed
    # And the fallback still found it, because a fact is a short triple whose
    # words overlap the question.
    assert [f.fact.object for f in result.facts] == ["Sillara pricing before 10am"]

    await retriever.aclose()


@pytest.mark.anyio
async def test_a_timed_out_embed_still_warms_the_cache(database: Database) -> None:
    """Cancelling it outright would mean paying for the same string twice."""
    stub = StubEmbeddings(delay_s=0.08)
    retriever = _retriever(database, stub, deadline_s=0.02)
    semantic = SemanticMemory(database, None)
    await semantic.upsert("user", "works_on", "Sillara pricing")

    first = await retriever.retrieve("tell me about Sillara pricing")
    assert first.degraded

    await asyncio.sleep(0.15)  # let the detached embed land
    second = await retriever.retrieve("tell me about Sillara pricing")
    assert not second.degraded
    assert stub.calls == 1


# ── mechanism 4: no embedder at all ───────────────────────────────────


@pytest.mark.anyio
async def test_retrieval_works_with_no_embedder(database: Database) -> None:
    semantic = SemanticMemory(database, None)
    await semantic.upsert("user", "works_on", "Sillara pricing")
    retriever = _retriever(database, None)

    result = await retriever.retrieve("what is happening with Sillara pricing?")

    assert result.degraded
    assert len(result.facts) == 1


@pytest.mark.anyio
async def test_a_broken_embedder_never_raises_into_the_turn(database: Database) -> None:
    stub = StubEmbeddings(working=False)
    retriever = _retriever(database, stub)
    semantic = SemanticMemory(database, None)
    await semantic.upsert("user", "works_on", "Sillara pricing")

    result = await retriever.retrieve("what about Sillara pricing?")
    assert result.degraded


# ── mechanism 5: the cache ────────────────────────────────────────────


@pytest.mark.anyio
async def test_the_same_query_embeds_once(database: Database) -> None:
    """`_build_context` runs once per attempt inside the failover loop, so
    without this a provider failover pays for the embed twice."""
    stub = StubEmbeddings()
    retriever = _retriever(database, stub)
    semantic = SemanticMemory(database, stub)  # type: ignore[arg-type]
    await semantic.upsert("user", "works_on", "Sillara pricing")
    before = stub.calls

    await retriever.retrieve("what about Sillara pricing?")
    after_first = stub.calls
    await retriever.retrieve("what about Sillara pricing?")

    assert after_first == before + 1
    assert stub.calls == after_first


# ── what comes back ───────────────────────────────────────────────────


@pytest.mark.anyio
async def test_weak_matches_are_left_out_entirely(database: Database) -> None:
    """Below MIN_SCORE nothing is injected, so the prompt stays byte-identical
    to a no-memory build — which is where the prefill saving comes from."""
    semantic = SemanticMemory(database, None)
    await semantic.upsert("user", "owns", "a bicycle")
    retriever = _retriever(database, None)

    result = await retriever.retrieve("what is the capital of Australia?")

    assert result.empty
    assert result.render() is None


@pytest.mark.anyio
async def test_no_more_than_five_facts_reach_the_prompt(database: Database) -> None:
    semantic = SemanticMemory(database, None)
    for i in range(10):
        await semantic.upsert("user", f"fact{i}", "Sillara pricing detail")
    retriever = _retriever(database, None)

    result = await retriever.retrieve("tell me about Sillara pricing")

    assert len(result.facts) <= MAX_FACTS


@pytest.mark.anyio
async def test_everything_returned_clears_the_floor(database: Database) -> None:
    semantic = SemanticMemory(database, None)
    await semantic.upsert("user", "works_on", "Sillara pricing")
    retriever = _retriever(database, None)

    result = await retriever.retrieve("Sillara pricing")

    assert all(f.score >= MIN_SCORE for f in result.facts)


@pytest.mark.anyio
async def test_the_rendered_block_never_lands_in_the_stable_prefix(
    database: Database,
) -> None:
    """The KV-cache invariant, asserted from the retrieval side too."""
    semantic = SemanticMemory(database, None)
    await semantic.upsert("user", "works_on", "Sillara pricing")
    retriever = _retriever(database, None)

    result = await retriever.retrieve("what about Sillara pricing?")
    rendered = result.render()

    assert rendered is not None
    stable = "".join(m.content for m in ctx.stable_prefix())
    assert "Sillara" not in stable


# ── instrumentation ───────────────────────────────────────────────────


@pytest.mark.anyio
async def test_stats_count_skipped_turns_separately(database: Database) -> None:
    """`empty` being 0 over a varied run means the trivial filter regressed."""
    semantic = SemanticMemory(database, None)
    await semantic.upsert("user", "works_on", "Sillara pricing")
    retriever = _retriever(database, None)

    await retriever.retrieve("ok")
    await retriever.retrieve("thanks")
    await retriever.retrieve("what about Sillara pricing?")

    stats = retriever.stats()
    assert stats.count == 3
    assert stats.empty == 2


@pytest.mark.anyio
async def test_degraded_retrievals_are_counted(database: Database) -> None:
    semantic = SemanticMemory(database, None)
    await semantic.upsert("user", "works_on", "Sillara pricing")
    retriever = _retriever(database, None)

    await retriever.retrieve("what about Sillara pricing?")

    assert retriever.stats().degraded == 1


# ── ageing ────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_a_recent_fact_outranks_an_identical_older_one(
    database: Database, conn
) -> None:
    semantic = SemanticMemory(database, None)
    await semantic.upsert("user", "mentioned", "Sillara pricing once")
    await semantic.upsert("user", "noted", "Sillara pricing again")
    old = (datetime.now(UTC) - timedelta(days=200)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with conn:
        conn.execute("UPDATE facts SET updated_at = ? WHERE predicate = 'mentioned'", (old,))

    retriever = _retriever(database, None)
    result = await retriever.retrieve("Sillara pricing")

    assert result.facts[0].fact.predicate == "noted"


@pytest.mark.anyio
async def test_a_pinned_fact_is_not_automatically_first(database: Database) -> None:
    """Pinning protects a fact from reflection; it does not make it relevant."""
    semantic = SemanticMemory(database, None)
    await semantic.upsert(
        "user", "owns", "a bicycle", source=FactSource.USER, confidence=0.95
    )
    await semantic.upsert("user", "works_on", "Sillara pricing")

    retriever = _retriever(database, None)
    result = await retriever.retrieve("Sillara pricing")

    assert [f.fact.object for f in result.facts] == ["Sillara pricing"]
