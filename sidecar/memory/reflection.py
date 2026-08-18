"""Reflection — where "learns on its own" actually lives (BUILD_SPEC §8.3).

Once a night she reads the day back and extracts durable facts. §8.3 says to run
it on a cloud model when a key is present, because it is the highest-leverage
inference in the system and a 7B extracts noticeably sloppier facts.

**But the local path is the tested path, not an untested fallback.** CLAUDE.md
records the Gemini free tier as quota-exhausted and the OpenAI account as
inactive, and a key can be *present* while the account is dead — so the
pre-check passes and the call fails. `run()` therefore treats a cloud failure as
routine and retries locally, and the whole thing is exercised against the local
model on this machine.

The prompt is a plain string, not `reflect.j2`: jinja2 is not a dependency and
one substitution does not justify one.
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import time
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import structlog
from pydantic import BaseModel, Field

from sidecar.memory.semantic import FactSource, MergeOutcome, SemanticMemory
from sidecar.providers import catalog
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    LLMProvider,
    ProviderError,
    Role,
)
from sidecar.providers.catalog import ModelClass, ModelInfo

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from sidecar.memory.db import Database
    from sidecar.memory.episodic import EpisodicMemory
    from sidecar.memory.settings_store import SettingsStore

log = structlog.get_logger(__name__)

#: No time limit by default — the high-water mark decides what is unread, and a
#: conversation does not stop being worth learning from because the app was shut
#: for two days. Callers may still pass one; see `_transcript`.
DEFAULT_WINDOW_HOURS: int | None = None
#: Rows per run. Bounds the model call on a fresh install with months of history
#: behind it, which then catches up over successive runs instead of in one call
#: no local model could hold.
MESSAGE_BATCH = 200
REFLECT_MAX_TOKENS = 1200
#: The transcript handed to the model. Beyond this the day is trimmed from the
#: front — the most recent interactions are the ones most likely still true.
REFLECT_MAX_CHARS = 12000
EXISTING_FACTS_LIMIT = 40
LAST_REFLECTION_KEY = "memory.last_reflection"
#: The id of the newest message a reflection has successfully read.
#:
#: **A wall-clock window loses conversations permanently, and this is why the
#: `facts` table was empty.** `_transcript` selected `created_at >= now - 24h`
#: and never consulted the last-reflection stamp, so on a machine that runs for
#: an hour at a time the arithmetic goes: launch, reflect over an empty window,
#: talk for an hour, close. Two days later the app opens again — and everything
#: said in that hour is now more than 24 hours old, outside every window that
#: will ever be selected again. Not delayed. Gone.
#:
#: A high-water mark cannot do that. Messages are read exactly once, whenever
#: the app next happens to be open, however long the gap.
LAST_MESSAGE_KEY = "memory.last_reflected_message_id"

#: Below this there is not enough new conversation for a durable fact to be
#: worth a model call. Applies only to the session-close trigger; the nightly
#: catch-up reads whatever is there.
MIN_MESSAGES_FOR_REFLECTION = 4

#: §8.3 verbatim. The two sentinels are substituted with `str.replace`, never
#: `str.format` — the JSON example below is full of literal braces and
#: `.format` raises on every one of them. This is a trap worth naming.
_PROMPT = """Below are today's interactions between the user and Aria.

Extract DURABLE facts — things likely still true in a month. Ignore
one-off task details.

Return JSON only:
{
  "facts": [
    {"subject":"user","predicate":"prefers","object":"...","confidence":0.0-1.0}
  ],
  "episodes": [
    {"summary":"...","salience":0.0-1.0}
  ],
  "procedures": [
    {"name":"...","steps":[...]}
  ]
}

Rules:
- A fact must be about a stable preference, relationship, project, habit,
  or constraint. NOT "he asked about X today."
- confidence < 0.5 if inferred from a single ambiguous signal.
- If a new fact contradicts an existing one, emit it anyway — the merge
  step handles supersession.

EXISTING FACTS (do not duplicate):
<<EXISTING_FACTS>>

TODAY'S INTERACTIONS:
<<TRANSCRIPT>>"""


class ExtractedFact(BaseModel):
    subject: str
    predicate: str
    object: str
    confidence: float = 0.6


class ExtractedEpisode(BaseModel):
    summary: str
    salience: float = 0.5


class ReflectionOutput(BaseModel):
    """What the model returned, once it survives validation."""

    facts: list[ExtractedFact] = Field(default_factory=list)
    episodes: list[ExtractedEpisode] = Field(default_factory=list)
    procedures: list[dict[str, Any]] = Field(default_factory=list)


class ReflectionReport(BaseModel):
    """What one run did. Shown in MemoryPanel and asserted by the gate."""

    model: str = ""
    local: bool = True
    window_hours: int | None = DEFAULT_WINDOW_HOURS
    messages_read: int = 0
    inserted: int = 0
    reinforced: int = 0
    superseded: int = 0
    blocked_by_pin: int = 0
    pruned: int = 0
    took_ms: int = 0
    error: str | None = None


def build_prompt(transcript: str, existing_facts: str) -> list[ChatMessage]:
    """§8.3's prompt, with the two slots filled."""
    filled = _PROMPT.replace("<<EXISTING_FACTS>>", existing_facts or "(none yet)")
    filled = filled.replace("<<TRANSCRIPT>>", transcript)
    return [ChatMessage(role=Role.USER, content=filled)]


def choose_model(usable: set[str], local_models: Sequence[str]) -> ModelInfo:
    """§8.3: cloud if a key is present, local otherwise.

    Walks SMART then BALANCED, which is the order that matters for extraction
    quality. Falls through to the local default, which is what actually happens
    on this machine.
    """
    for klass in (ModelClass.SMART, ModelClass.BALANCED):
        for info in catalog.by_class(klass):
            if not info.local and info.id in usable:
                return info
    return catalog.default_local(local_models)


def _extract_json(raw: str) -> dict[str, Any] | None:
    """Find the JSON object in whatever the model actually returned.

    A local 7B wraps JSON in fences, prefaces it with "Here is the JSON:", and
    sometimes adds a paragraph afterwards. None of that is worth failing over,
    and none of it is worth a parser more clever than "first brace to last".
    """
    text = raw.strip()
    if "```" in text:
        blocks = text.split("```")
        # Odd indices are fenced bodies. Take the first that looks like JSON.
        for block in blocks[1::2]:
            body = block.removeprefix("json").strip()
            if body.startswith("{"):
                text = body
                break

    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


class Reflector:
    """One nightly pass: read the day, extract facts, merge, prune."""

    def __init__(
        self,
        db: Database,
        semantic: SemanticMemory,
        episodic: EpisodicMemory,
        settings_store: SettingsStore,
        providers: Mapping[str, LLMProvider],
        *,
        usable: set[str] | None = None,
        local_models: Sequence[str] | None = None,
    ) -> None:
        self._db = db
        self._semantic = semantic
        self._episodic = episodic
        self._settings = settings_store
        self._providers = providers
        self._usable = usable or set()
        self._local_models = list(local_models or [])
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    async def last_run(self) -> datetime | None:
        stamp = await self._settings.get(LAST_REFLECTION_KEY)
        if not isinstance(stamp, str):
            return None
        try:
            return datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        except ValueError:
            return None

    async def run(
        self, *, window_hours: int | None = DEFAULT_WINDOW_HOURS
    ) -> ReflectionReport:
        """Read the window, extract, merge, prune. Never raises."""
        if self._running:
            return ReflectionReport(
                window_hours=window_hours,
                error="A reflection is already running.",
            )
        self._running = True
        started = time.perf_counter()
        report = ReflectionReport(window_hours=window_hours)
        try:
            await self._run_into(report, window_hours)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — surfaced in the panel, never fatal
            report.error = str(exc)
            log.warning("reflection.failed", error=str(exc))
        finally:
            self._running = False
            report.took_ms = int((time.perf_counter() - started) * 1000)
        return report

    async def _run_into(
        self, report: ReflectionReport, window_hours: int | None
    ) -> None:
        transcript, count, high_water = await self._transcript(window_hours)
        report.messages_read = count
        if not transcript:
            # **Nothing read is not a reflection, and stamping it here cost a
            # whole day of learning.** The app launched at 10:03 with no
            # messages in the window, this branch stamped `last_reflection`, and
            # `_reflection_due` then answered False for every tick until the
            # next 3am — including the conversation at 10:50 that it should have
            # learned from. An empty read leaves the mark alone so the next tick
            # tries again, which costs one indexed query.
            log.info("reflection.nothing_to_read", window_hours=window_hours)
            return

        existing = await self._existing_facts()
        info = choose_model(self._usable, self._local_models)
        report.model, report.local = info.id, info.local

        raw = await self._generate(info, transcript, existing, report)
        if raw is None:
            await self._stamp()
            return

        parsed = _extract_json(raw)
        if parsed is None:
            report.error = "The model did not return usable JSON."
            log.warning("reflection.unparsed", head=raw[:300])
            await self._stamp()
            return

        try:
            output = ReflectionOutput.model_validate(parsed)
        except ValueError as exc:
            report.error = "The model's JSON did not match the expected shape."
            log.warning("reflection.invalid", error=str(exc), head=raw[:300])
            await self._stamp()
            return

        await self._merge(output, report)
        report.pruned = await self._semantic.prune()
        await self._stamp(high_water)

        if output.episodes:
            # Parsed by `ReflectionOutput` and never merged: episodes are
            # written by `EpisodicMemory` when a session closes, from the real
            # transcript, and a second set invented here from a day's worth of
            # mixed conversation would compete with them in retrieval. Counted
            # rather than silently dropped, so this stays a decision.
            log.info("reflection.episodes_ignored", count=len(output.episodes))

        if output.procedures:
            # The table exists but nothing reads it until Phase 6's agent loop.
            # Rows nothing reads are dead data that will be stale by the time
            # something wants them, so they are counted and dropped.
            log.info("reflection.procedures_ignored", count=len(output.procedures))

        log.info(
            "reflection.done",
            # `report.model`, not `info.id`: a cloud model that 429s is replaced
            # by the local one in `_generate`, and logging the one that failed
            # makes the fallback invisible in the log that records it working.
            model=report.model,
            local=report.local,
            inserted=report.inserted,
            reinforced=report.reinforced,
            superseded=report.superseded,
            blocked_by_pin=report.blocked_by_pin,
            pruned=report.pruned,
        )

    async def _generate(
        self,
        info: ModelInfo,
        transcript: str,
        existing: str,
        report: ReflectionReport,
    ) -> str | None:
        """Ask the chosen model, falling back to local on any provider failure."""
        try:
            return await self._stream(info, transcript, existing)
        except ProviderError as exc:
            if info.local:
                report.error = f"The local model could not reflect: {exc}"
                log.warning("reflection.local_failed", error=str(exc))
                return None
            log.warning("reflection.fell_back_to_local", model=info.id, error=str(exc))

        fallback = catalog.default_local(self._local_models)
        report.model, report.local = fallback.id, True
        try:
            return await self._stream(fallback, transcript, existing)
        except ProviderError as exc:
            report.error = f"No model could reflect: {exc}"
            log.warning("reflection.local_failed", error=str(exc))
            return None

    async def _stream(self, info: ModelInfo, transcript: str, existing: str) -> str:
        provider = self._providers.get(info.provider)
        if provider is None:
            raise ProviderError(f"No provider configured for {info.provider}.")

        chunks: list[str] = []
        async for delta in provider.stream_chat(
            build_prompt(transcript, existing),
            model=info.id,
            options=GenerationOptions(
                num_ctx=info.context_tokens, max_tokens=REFLECT_MAX_TOKENS
            ),
        ):
            chunks.append(delta.text)
            if delta.done:
                break
        return "".join(chunks)

    async def _merge(self, output: ReflectionOutput, report: ReflectionReport) -> None:
        """Fold extracted facts in, one at a time.

        **Sequentially, deliberately.** The merge compares a new fact against
        what is *stored*, so two contradictory facts extracted in the same pass
        would both go active if they were written together. Going one at a time
        means the second sees the first.
        """
        counts = {
            MergeOutcome.INSERTED: 0,
            MergeOutcome.REINFORCED: 0,
            MergeOutcome.SUPERSEDED: 0,
            MergeOutcome.BLOCKED_BY_PIN: 0,
        }
        for fact in output.facts:
            outcome, _ = await self._semantic.upsert(
                fact.subject,
                fact.predicate,
                fact.object,
                confidence=max(0.0, min(1.0, fact.confidence)),
                source=FactSource.REFLECTION,
            )
            counts[outcome] += 1

        report.inserted = counts[MergeOutcome.INSERTED]
        report.reinforced = counts[MergeOutcome.REINFORCED]
        report.superseded = counts[MergeOutcome.SUPERSEDED]
        report.blocked_by_pin = counts[MergeOutcome.BLOCKED_BY_PIN]

    async def _mark(self) -> int | None:
        value = await self._settings.get(LAST_MESSAGE_KEY)
        return int(value) if isinstance(value, int | float) else None

    async def unreflected_count(self) -> int:
        """How many messages have arrived since the last successful reflection.

        Cheap enough for the session-close trigger to ask on every close: one
        indexed count, no model, no embedding.
        """
        mark = await self._mark()

        def _count(conn: sqlite3.Connection) -> int:
            if mark is None:
                row = conn.execute(
                    "SELECT COUNT(*) AS n FROM messages WHERE role IN ('user', 'assistant')"
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT COUNT(*) AS n FROM messages
                    WHERE id > ? AND role IN ('user', 'assistant')
                    """,
                    (mark,),
                ).fetchone()
            return int(row["n"]) if row else 0

        return await self._db.run(_count)

    async def _transcript(self, window_hours: int | None) -> tuple[str, int, int | None]:
        """The oldest unread messages, with the id to mark on success.

        **Oldest first, and the tail rolls to the next run.** The old code took
        the most recent messages and trimmed the front, which is right when a
        wall-clock window means the front is about to expire anyway. Under a
        high-water mark nothing expires, so trimming the front would be the one
        way to lose a message permanently — it would sit below a mark that had
        advanced past it. Dropping from the *end* instead costs nothing: those
        messages are simply the next batch.

        `window_hours` is no longer how the batch is chosen. It survives as an
        optional extra ceiling for callers that want one — `gate_memory.py` asks
        for an hour so a gate run cannot reflect over months of real
        conversation — and defaults to no limit at all.
        """
        mark = await self._mark() or 0
        cutoff = (
            None
            if window_hours is None
            else (datetime.now(UTC) - timedelta(hours=window_hours)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        )

        def _read(conn: sqlite3.Connection) -> list[sqlite3.Row]:
            if cutoff is None:
                return conn.execute(
                    """
                    SELECT id, role, content FROM messages
                    WHERE id > ? AND role IN ('user', 'assistant')
                    ORDER BY id ASC LIMIT ?
                    """,
                    (mark, MESSAGE_BATCH),
                ).fetchall()
            return conn.execute(
                """
                SELECT id, role, content FROM messages
                WHERE id > ? AND created_at >= ? AND role IN ('user', 'assistant')
                ORDER BY id ASC LIMIT ?
                """,
                (mark, cutoff, MESSAGE_BATCH),
            ).fetchall()

        rows = await self._db.run(_read)
        if not rows:
            return ("", 0, None)

        kept: list[str] = []
        high_water = mark
        size = 0
        for row in rows:
            line = f"{row['role']}: {row['content']}"
            if kept and size + len(line) > REFLECT_MAX_CHARS:
                break
            kept.append(line)
            size += len(line) + 1
            high_water = int(row["id"])
        return ("\n".join(kept), len(kept), high_water)

    async def _existing_facts(self) -> str:
        facts = await self._semantic.list_facts(limit=EXISTING_FACTS_LIMIT)
        return "\n".join(
            f"{f.subject} | {f.predicate} | {f.object} ({f.confidence:.2f})" for f in facts
        )

    async def _stamp(self, high_water: int | None = None) -> None:
        """Record that a reflection was attempted, and how far it got.

        Two marks, deliberately separate. The **timestamp** says an attempt
        happened, so the scheduler keeps its daily cadence and a model that
        returns garbage does not cause a retry every five minutes. The
        **message id** says the material was actually understood, so it advances
        only on success and a failed batch is re-read next time rather than
        silently skipped.
        """
        await self._settings.set(
            LAST_REFLECTION_KEY, datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        if high_water is not None:
            await self._settings.set(LAST_MESSAGE_KEY, high_water)
