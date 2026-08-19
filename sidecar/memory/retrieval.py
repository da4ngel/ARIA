"""Retrieval — putting the right memory in front of the model (§9 Phase 5).

**The budget is the design.** §9's gate is "retrieval adds <80ms to turn
latency". A short query embeds in 41ms with Ollama idle and 65-74ms while the
7B is generating — which is the condition that matters, because retrieval
starts when the turn does. So "embed the message, search, inject" does not fit,
and the honest consequence is recorded at `DEFAULT_DEADLINE_S`: on this machine
retrieval is lexical most of the time, with semantic recall arriving via the
warm cache on the next turn about the same thing.

Five mechanisms, layered, each load-bearing:

1. **Most turns retrieve nothing and pay ~0ms.** A trivial message, or an empty
   store, returns before anything is embedded. The same shape as the router's
   private-word check: a cheap word-level decision ahead of an expensive one.
2. **The query is short.** 240 characters is 8-40 tokens against the indexer's
   ~110, and a transformer's cost scales with sequence length.
3. **A hard deadline makes the budget structural rather than hopeful.**
   `asyncio.wait_for` around the embed. `OllamaEmbeddings` serialises on an
   `asyncio.Lock` and lock acquisition is cancellable, so the timeout fires
   whether we are queued behind an indexer chunk or waiting on Ollama itself.
4. **A lexical fallback**, which doubles as the no-Ollama path. Facts are short
   triples that usually contain the literal words of the question, so word
   overlap is a degraded mode rather than a broken one — and every degraded
   retrieval is counted, so "it quietly stopped using embeddings" stays visible.
5. **Overlap and cache.** `prefetch` starts the work the moment the text is
   known so it runs alongside the message write and history read. The LRU is
   not a micro-optimisation: `_build_context` runs once *per attempt* inside the
   provider failover loop, so without it a failover embeds the same string
   twice.

What comes back is small on purpose — 5 facts, 2 episodes, 220 tokens — because
it sits in the volatile section and re-prefills every single turn.
"""

from __future__ import annotations

import asyncio
import re
import time
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import structlog

from sidecar.core import context as ctx
from sidecar.memory import text as words
from sidecar.memory.episodic import Episode, EpisodicMemory
from sidecar.memory.messages import ConversationStore
from sidecar.memory.semantic import Fact, SemanticMemory
from sidecar.providers.embeddings import EmbeddingsUnavailable, OllamaEmbeddings

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

log = structlog.get_logger(__name__)

#: §9 Phase 5's scoring formula, verbatim.
W_COSINE = 0.6
W_RECENCY = 0.25
W_WEIGHT = 0.15
#: "boost access_count" — a small tiebreaker, not a fourth term. A memory that
#: keeps coming up is worth surfacing, but not enough to beat relevance.
W_ACCESS = 0.05
ACCESS_SATURATES_AT = 10

RECENCY_HALF_LIFE_DAYS = 30.0

#: Below this, inject nothing at all. The real prefill saving: a turn about
#: something she has no memory of leaves the prompt byte-identical.
MIN_SCORE = 0.45
MAX_FACTS = 5
MAX_EPISODES = 2

#: Long enough to carry a question, short enough to embed fast.
QUERY_MAX_CHARS = 240
#: Under this, after stripping punctuation, nothing is worth looking up.
TRIVIAL_MAX_CHARS = 12

#: **60ms — and the embed does not fit inside it on this machine.** That is the
#: finding, not a tuning accident, so it is written down rather than smoothed
#: over.
#:
#: Measured `nomic-embed-text` on a short query, three runs of
#: `scripts/gate_memory.py`:
#:
#:     Ollama otherwise idle      p50  41ms   p90  61ms
#:     the 7B generating          p50  65ms   p90 107ms
#:     the 7B generating          p50  74ms   p90  82ms
#:
#: The second condition is the real one: retrieval starts in `send()`, which is
#: the moment the turn begins generating. At a 120ms deadline total retrieval
#: measured **111ms p90, over §9's 80ms gate**; at 70ms it measured 87ms,
#: because the deadline is not the whole cost — the search after it counts too.
#:
#: So the deadline sits below the contended embed rather than above it, and the
#: consequence is stated plainly: **during generation this machine retrieves
#: lexically most of the time.** That is a real cost — word overlap loses
#: paraphrase — and three things stop it being a broken feature:
#:
#: 1. A fact is a short triple that usually contains the question's own words.
#: 2. The abandoned embed is not cancelled; it finishes into the LRU, so the
#:    next turn on the same topic *is* semantic.
#: 3. `degraded` is counted and surfaced in `memory.stats`, so this is visible
#:    rather than a silent quality regression.
#:
#: A faster embedding model — not a larger deadline — is what would change it.
DEFAULT_DEADLINE_S = 0.06
#: What a `_RECALL_QUESTION` gets instead. Long enough for the contended p90
#: above with room to spare, because on these turns retrieval is not an
#: enhancement to the answer — it *is* the answer, and word matching answering
#: "no" to something that did happen is the failure this whole module exists to
#: prevent. Rare enough not to move the aggregate: measured over a real session,
#: 1 turn in 22 matched.
RECALL_DEADLINE_S = 0.4
CACHE_SIZE = 32
STATS_WINDOW = 200

#: How much of the store the fallback scans. It runs with whatever is left of
#: the budget after the embed deadline, so it is bounded rather than complete —
#: and the rows come back ordered by confidence and recency, so the cap drops
#: the least likely answers first.
LEXICAL_FACT_SCAN = 200
LEXICAL_EPISODE_SCAN = 60

#: Acknowledgements and control words. Retrieval on these is pure cost — there
#: is no question in them to answer from memory.
_TRIVIAL = frozenset(
    {
        "ok", "okay", "k", "yes", "no", "yep", "nope", "sure", "thanks",
        "thank you", "ta", "cheers", "hi", "hello", "hey", "hey aria", "aria",
        "stop", "wait", "go on", "continue", "carry on", "never mind",
        "nvm", "cool", "nice", "great", "good", "right", "got it", "sounds good",
    }
)

#: A question *about* her memory, which changes what the budget is worth.
#:
#: On an ordinary turn a slow embed costs paraphrase and nothing else — the
#: answer is in the conversation. On "have we discussed jobs?" the retrieval
#: **is** the answer, and falling back to word matching produces a confident
#: "no" about something that did happen. So these turns get a deadline an order
#: of magnitude longer, and the ~340ms is paid on the handful of turns that are
#: entirely about remembering.
_RECALL_QUESTION = re.compile(
    r"\b("
    r"do(?: you)? remember"
    r"|d(?:o|id) we (?:ever )?(?:discuss|talk|speak|chat)"
    r"|have we (?:ever )?(?:discussed|talked|spoken)"
    r"|did i (?:tell|mention|say|ask)"
    r"|what did i (?:say|tell|ask|mention)"
    r"|you (?:said|told me|mentioned)"
    r"|earlier (?:you|we|i)"
    r"|last time"
    r"|previous(?:ly)? (?:chat|conversation|session)"
    r"|any (?:previous|earlier|other) (?:chat|conversation)"
    r"|remind me what"
    r")\b",
    re.I,
)


def recency_decay(age_days: float) -> float:
    """1.0 today, 0.5 after a month, never quite zero."""
    return float(0.5 ** (max(0.0, age_days) / RECENCY_HALF_LIFE_DAYS))


def _age_days(timestamp: str, now: datetime) -> float:
    try:
        moment = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError:
        return 0.0
    return max(0.0, (now - moment).total_seconds() / 86400.0)


def score(*, cosine: float, age_days: float, weight: float, access_count: int) -> float:
    """§9 Phase 5: 0.6·cosine + 0.25·recency + 0.15·salience, boosted by access.

    Two substitutions, both deliberate and neither a bug:

    - **A fact's `weight` is its confidence.** `facts` has no salience column
      and the spec does not ask for one. How sure she is *is* how much a fact
      deserves prompt space.
    - **A fact's `access_count` is always 0.** The column exists on `episodes`
      only. Facts are therefore ranked on the first three terms alone.
    """
    return (
        W_COSINE * cosine
        + W_RECENCY * recency_decay(age_days)
        + W_WEIGHT * weight
        + W_ACCESS * min(1.0, access_count / ACCESS_SATURATES_AT)
    )


@dataclass(frozen=True)
class ScoredFact:
    fact: Fact
    score: float
    cosine: float


@dataclass(frozen=True)
class ScoredEpisode:
    episode: Episode
    score: float
    cosine: float


@dataclass(frozen=True)
class Retrieved:
    """What one turn recalled, plus what it cost."""

    facts: list[ScoredFact] = field(default_factory=list)
    episodes: list[ScoredEpisode] = field(default_factory=list)
    took_ms: float = 0.0
    embed_ms: float = 0.0
    #: True when the cosine term came from word overlap rather than embeddings.
    degraded: bool = False
    #: True when the turn was itself a question about memory, and therefore ran
    #: on `RECALL_DEADLINE_S`. Kept out of the gate's aggregate on purpose —
    #: these turns are deliberately over the 80ms budget, and folding them in
    #: would let a genuine regression hide behind them.
    recall_question: bool = False

    def render(self) -> str | None:
        return ctx.retrieved_block(
            [f.fact.sentence() for f in self.facts],
            [e.episode.summary for e in self.episodes],
        )

    def episode_ids(self) -> list[int]:
        return [e.episode.id for e in self.episodes]

    @property
    def empty(self) -> bool:
        return not self.facts and not self.episodes


@dataclass(frozen=True)
class RetrievalStats:
    """What `memory.stats` reports and `gate_memory.py` asserts against."""

    count: int = 0
    p50_ms: float = 0.0
    p90_ms: float = 0.0
    max_ms: float = 0.0
    embed_count: int = 0
    embed_p50_ms: float = 0.0
    embed_p90_ms: float = 0.0
    degraded: int = 0
    #: Turns that skipped retrieval entirely. If this is 0 over a varied run,
    #: the trivial-message filter has regressed and the budget is at risk.
    empty: int = 0
    #: Turns that ran on the longer recall deadline, and their own p90. Reported
    #: beside the gate rather than inside it — see `Retrieved.recall_question`.
    recall_count: int = 0
    recall_p90_ms: float = 0.0


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round(fraction * (len(ordered) - 1))))
    return round(ordered[index], 2)


class Retriever:
    """Turns a user message into the memory worth putting in front of the model."""

    def __init__(
        self,
        semantic: SemanticMemory,
        episodic: EpisodicMemory,
        embeddings: OllamaEmbeddings | None,
        *,
        deadline_s: float = DEFAULT_DEADLINE_S,
        recall_deadline_s: float = RECALL_DEADLINE_S,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._semantic = semantic
        self._episodic = episodic
        self._embeddings = embeddings
        self._deadline_s = deadline_s
        self._recall_deadline_s = recall_deadline_s
        self._clock = clock
        self._cache: OrderedDict[str, list[float]] = OrderedDict()
        self._samples: deque[tuple[float, float, bool, bool, bool]] = deque(
            maxlen=STATS_WINDOW
        )
        self._detached: set[asyncio.Task[None]] = set()
        #: Latches true once anything has been stored. See `_has_anything`.
        self._store_populated = False

    # ── the turn path ────────────────────────────────────────────────────

    def prefetch(self, query: str, *, deep: bool = False) -> asyncio.Task[Retrieved]:
        """Start retrieval now, await it later.

        Called from `send()` so the embed overlaps the message write, the router
        decision and the history read — all of which the turn does anyway.
        """
        return asyncio.create_task(self.retrieve(query, deep=deep))

    async def retrieve(self, query: str, *, deep: bool = False) -> Retrieved:
        """Facts and episodes worth injecting. Never raises, never over budget."""
        started = time.perf_counter()

        if self._is_trivial(query):
            return self._record(Retrieved(took_ms=self._elapsed(started)), empty=True)

        if not await self._has_anything():
            return self._record(Retrieved(took_ms=self._elapsed(started)), empty=True)

        # `deep` is a mode asking for the same longer deadline a recall
        # question already earns — not a second budget. Study, Research and
        # Critic build on what came before, and at 60ms most retrievals fall
        # back to word matching, which loses paraphrase.
        recall = deep or bool(_RECALL_QUESTION.search(query))
        vector, embed_ms, degraded = await self._vector_for(query, recall=recall)

        if vector is not None:
            facts, episodes = await self._semantic_search(query, vector)
        else:
            facts, episodes = await self._lexical_search(query)

        result = Retrieved(
            facts=facts,
            episodes=episodes,
            took_ms=self._elapsed(started),
            embed_ms=embed_ms,
            degraded=degraded,
            recall_question=recall,
        )
        log.info(
            "memory.retrieved",
            took_ms=round(result.took_ms, 1),
            embed_ms=round(embed_ms, 1),
            facts=len(facts),
            episodes=len(episodes),
            degraded=degraded,
            recall_question=recall,
        )
        return self._record(result, empty=result.empty)

    def _is_trivial(self, query: str) -> bool:
        stripped = query.strip().strip(".!?,;:").lower()
        return len(stripped) < TRIVIAL_MAX_CHARS or stripped in _TRIVIAL

    async def _has_anything(self) -> bool:
        """Whether there is anything to search. Cached once it is true.

        This was two `COUNT(*)` queries on every non-trivial turn, and each one
        is an `asyncio.to_thread` hop — measurable against an 80ms budget for a
        question whose answer changes exactly once in the life of the install
        and never changes back. Nothing here deletes the last fact and expects
        retrieval to notice within a turn.
        """
        if self._store_populated:
            return True
        self._store_populated = bool(await self._semantic.count()) or bool(
            await self._episodic.count()
        )
        return self._store_populated

    async def _vector_for(
        self, query: str, *, recall: bool = False
    ) -> tuple[list[float] | None, float, bool]:
        """Embed within the deadline, or give up and say so.

        On timeout the embed is **not** cancelled outright — it is left running
        detached so its result lands in the cache and the next turn on the same
        topic is semantic rather than lexical. Paying for it twice would be the
        only worse option.
        """
        if self._embeddings is None:
            return (None, 0.0, True)

        key = query.strip().lower()[:QUERY_MAX_CHARS]
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return (cached, 0.0, False)

        deadline = self._recall_deadline_s if recall else self._deadline_s
        started = time.perf_counter()
        task = asyncio.create_task(self._embed_and_cache(key))
        try:
            vector = await asyncio.wait_for(asyncio.shield(task), deadline)
        except TimeoutError:
            self._detach(task)
            log.warning(
                "memory.retrieval_slow",
                deadline_ms=round(deadline * 1000),
                recall_question=recall,
                fix="Falling back to word matching for this turn.",
            )
            return (None, self._elapsed(started), True)
        except EmbeddingsUnavailable:
            return (None, self._elapsed(started), True)

        return (vector, self._elapsed(started), vector is None)

    async def _embed_and_cache(self, key: str) -> list[float] | None:
        try:
            vector = await self._embeddings.embed(key)  # type: ignore[union-attr]
        except EmbeddingsUnavailable as exc:
            log.warning("memory.embed_unavailable", error=str(exc))
            return None
        self._cache[key] = vector
        while len(self._cache) > CACHE_SIZE:
            self._cache.popitem(last=False)
        return vector

    def _detach(self, task: asyncio.Task[list[float] | None]) -> None:
        """Keep a strong ref so the timed-out embed still reaches the cache."""
        self._detached.add(task)  # type: ignore[arg-type]
        task.add_done_callback(self._detached.discard)  # type: ignore[arg-type]

    async def aclose(self) -> None:
        """Cancel any embed still running past its deadline.

        Without this, shutting down mid-retrieval leaves a task pending on a
        loop that is closing — which Python reports as "Task was destroyed but
        it is pending". Harmless, but it is the kind of warning that trains
        people to ignore warnings.
        """
        for task in list(self._detached):
            task.cancel()
        if self._detached:
            await asyncio.gather(*self._detached, return_exceptions=True)
        self._detached.clear()

    # ── searching ────────────────────────────────────────────────────────

    async def _semantic_search(
        self, query: str, vector: list[float]
    ) -> tuple[list[ScoredFact], list[ScoredEpisode]]:
        now = self._clock()
        # Concurrently: two independent KNN queries, each a thread hop, and the
        # turn is waiting on both.
        fact_hits, episode_hits = await asyncio.gather(
            self._semantic.search(vector, limit=MAX_FACTS * 3),
            self._episodic.search(vector, limit=MAX_EPISODES * 3),
        )

        facts = [
            ScoredFact(
                fact=fact,
                cosine=cos,
                score=score(
                    cosine=cos,
                    age_days=_age_days(fact.updated_at, now),
                    weight=fact.confidence,
                    access_count=0,
                ),
            )
            for fact, cos in fact_hits
        ]
        episodes = [
            ScoredEpisode(
                episode=episode,
                cosine=cos,
                score=score(
                    cosine=cos,
                    age_days=_age_days(episode.ended_at, now),
                    weight=episode.salience,
                    access_count=episode.access_count,
                ),
            )
            for episode, cos in episode_hits
        ]
        return (_top(facts, MAX_FACTS), _top(episodes, MAX_EPISODES))

    async def _lexical_search(
        self, query: str
    ) -> tuple[list[ScoredFact], list[ScoredEpisode]]:
        """Word overlap in place of cosine. Sub-millisecond, and honest about it.

        Not a placeholder — it carries 77% of real retrievals on this machine —
        so it is IDF-weighted rather than a plain overlap fraction. The three
        reasons that matters are in `memory/text.py`; the short version is that
        the old form could not match `jobs` to `job`, scored the summariser's
        own word "discussed" as though it meant something, and gave a *lower*
        score to a more specific question.

        Facts and episodes are weighted against one shared corpus. They are
        ranked against one shared floor, so scoring them on two different
        notions of rarity would make that floor mean two different things.
        """
        now = self._clock()
        wanted = words.content_words(query)
        if not wanted:
            return ([], [])

        # Concurrently, as above: this path runs *after* the embed deadline has
        # already been spent, so what is left of the budget is small.
        stored_facts, stored_episodes = await asyncio.gather(
            self._semantic.list_facts(limit=LEXICAL_FACT_SCAN),
            self._episodic.list_episodes(limit=LEXICAL_EPISODE_SCAN),
        )

        fact_words = [words.content_words(f.sentence()) for f in stored_facts]
        episode_words = [words.content_words(e.summary) for e in stored_episodes]
        weights = words.idf([*fact_words, *episode_words])

        facts = [
            ScoredFact(
                fact=fact,
                cosine=(cos := words.coverage(wanted, have, weights)),
                score=score(
                    cosine=cos,
                    age_days=_age_days(fact.updated_at, now),
                    weight=fact.confidence,
                    access_count=0,
                ),
            )
            for fact, have in zip(stored_facts, fact_words, strict=True)
        ]
        episodes = [
            ScoredEpisode(
                episode=episode,
                cosine=(cos := words.coverage(wanted, have, weights)),
                score=score(
                    cosine=cos,
                    age_days=_age_days(episode.ended_at, now),
                    weight=episode.salience,
                    access_count=episode.access_count,
                ),
            )
            for episode, have in zip(stored_episodes, episode_words, strict=True)
        ]
        return (_top(facts, MAX_FACTS), _top(episodes, MAX_EPISODES))

    # ── instrumentation ──────────────────────────────────────────────────

    def _elapsed(self, started: float) -> float:
        return (time.perf_counter() - started) * 1000.0

    def _record(self, result: Retrieved, *, empty: bool) -> Retrieved:
        self._samples.append(
            (result.took_ms, result.embed_ms, result.degraded, empty, result.recall_question)
        )
        return result

    def stats(self) -> RetrievalStats:
        """The numbers §9's gate is measured against.

        **Recall questions are excluded from the headline percentiles**, and
        reported separately. They run on a deadline six times longer by design,
        so averaging them in would raise the p90 for a reason that is not a
        regression — and, worse, would leave room for a real regression to hide
        underneath. A number that mixes two budgets measures neither.
        """
        ordinary = [s for s in self._samples if not s[4]]
        recalls = [s for s in self._samples if s[4]]
        if not ordinary and not recalls:
            return RetrievalStats()

        totals = [s[0] for s in ordinary]
        embeds = [s[1] for s in ordinary if s[1] > 0]
        return RetrievalStats(
            count=len(totals),
            p50_ms=_percentile(totals, 0.5),
            p90_ms=_percentile(totals, 0.9),
            max_ms=round(max(totals), 2) if totals else 0.0,
            embed_count=len(embeds),
            embed_p50_ms=_percentile(embeds, 0.5),
            embed_p90_ms=_percentile(embeds, 0.9),
            degraded=sum(1 for s in ordinary if s[2]),
            empty=sum(1 for s in ordinary if s[3]),
            recall_count=len(recalls),
            recall_p90_ms=_percentile([s[0] for s in recalls], 0.9),
        )


def _top(items: Sequence[ScoredFact] | Sequence[ScoredEpisode], limit: int) -> list:  # type: ignore[type-arg]
    """Best `limit` above the floor. Below it, nothing goes in the prompt.

    **A zero similarity is rejected before the floor is consulted**, and that
    guard is doing real work rather than tidying. Recency and salience alone
    sum to 0.25 + 0.15 = 0.40, so a fresh, highly-salient episode sits within
    0.05 of `MIN_SCORE` on its own merits — and would surface for a query it
    has not one word in common with. Relevance is not one term among four; it
    is the precondition for the other three meaning anything.
    """
    ranked = sorted(
        (i for i in items if i.cosine > 0.0 and i.score >= MIN_SCORE),
        key=lambda i: -i.score,
    )
    return list(ranked[:limit])


@dataclass(frozen=True)
class MemoryServices:
    """Everything Phase 5 hands to the conversation, as one argument.

    `ConversationService` takes this or `None`; `None` is a build with memory
    switched off, and every call site is a no-op in that case.
    """

    semantic: SemanticMemory
    episodic: EpisodicMemory
    retriever: Retriever
    #: Raw turns, for `recall` to search. Facts and episodes are both model-made
    #: compressions that may never have been written; the messages always exist.
    store: ConversationStore
