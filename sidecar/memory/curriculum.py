"""Turning a lecture into a concept map.

One model call over the source material, producing an ordered list of concepts
that becomes `concepts` rows. Shaped like `reflection.Reflector` — the same
prompt-with-slots, first-brace-to-last JSON extraction, and cloud-then-local
fallback — because that is the idiom this codebase already has for "ask a model
for structured output and survive whatever it actually says".

**Unlike every other model call here, this one runs on the turn path**, and the
difference is who asked. Reflection is a background job because nobody
requested it and its cost must never land on a reply. Here the user has just
said "teach me this lecture" and is waiting for precisely this — a map that
materialised silently some minutes later would be useless. It happens once per
subject, and Study's 4-step budget bounds the turn it sits in.

**The source text needed a reader that did not exist.** `file_chunks` has held
the full text of every indexed document since Phase 4, and nothing on the turn
path has ever read it: `search_content` deliberately collapses chunks down to
file *paths* and discards the text, and `attachments.remember`'s own docstring
records that `Retriever` reads facts and episodes and has never touched that
table. So `source_text` below is a plain ordered read of state this project
already stores and simply never looked at.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence

import structlog
from pydantic import BaseModel, Field

from sidecar.memory import study
from sidecar.memory.db import Database
from sidecar.memory.reflection import _extract_json
from sidecar.providers import catalog
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    LLMProvider,
    ProviderError,
    Role,
)
from sidecar.providers.catalog import ModelClass, ModelInfo

log = structlog.get_logger(__name__)

# `_extract_json` is imported rather than copied. It is private to `reflection`,
# but a second copy of "find the JSON in whatever a 7B actually returned" is a
# second thing to fix when one of them is wrong — the same call this project
# already made when `OpenRouterProvider` subclassed `OpenAIProvider` instead of
# duplicating its tool-call assembler.

#: How much of the lecture is sent. ~8k tokens, which fits every model in the
#: catalog including the local 7B, and is comfortably a full lecture. A longer
#: source is trimmed rather than chunked into several calls: the map wants the
#: *shape* of the material, and the shape is established early.
MAX_SOURCE_CHARS = 32_000

#: Enough for a map of a lecture. Past roughly this many concepts a "map" stops
#: being a map and becomes the transcript again.
MAX_CONCEPTS = 24

CURRICULUM_MAX_TOKENS = 1600

_PROMPT = """Below is teaching material the user wants to learn.

Break it into the concepts it actually teaches, in the order it teaches them.

Return JSON only:
{
  "subject": "a short name for the whole topic",
  "concepts": [
    {"name": "...", "summary": "one sentence, in the material's own words"}
  ]
}

Rules:
- A concept is something that can be understood, explained back, and tested.
  NOT a slide title, a section heading, or "Introduction" / "Summary" /
  "References" / "Any questions?".
- Use the material's own terminology. Do not substitute a term you prefer.
- Order them so each one only needs the ones before it.
- Between 3 and {max_concepts} concepts. If the material genuinely teaches
  fewer, return fewer — do not pad it.
- Include ONLY concepts the material actually covers. Do not add what you
  happen to know about the topic; a map with concepts that are not in the
  lecture teaches the wrong syllabus.

MATERIAL:
<<SOURCE>>""".replace("{max_concepts}", str(MAX_CONCEPTS))


class ExtractedConcept(BaseModel):
    name: str
    summary: str = ""


class CurriculumOutput(BaseModel):
    subject: str = ""
    concepts: list[ExtractedConcept] = Field(default_factory=list)


class CurriculumReport(BaseModel):
    """What the extraction did, for the tool result and the log."""

    subject: str = ""
    subject_id: int | None = None
    concepts_found: int = 0
    concepts_added: int = 0
    model: str = ""
    local: bool = False
    error: str | None = None


def build_prompt(source: str) -> list[ChatMessage]:
    return [ChatMessage(role=Role.USER, content=_PROMPT.replace("<<SOURCE>>", source))]


def choose_model(usable: set[str], local_models: Sequence[str]) -> ModelInfo:
    """Cloud if a key is present, local otherwise — `reflection.choose_model`'s
    rule, and for the same reason: this is structured extraction, where the
    difference between a 7B and a cloud model is most visible."""
    for klass in (ModelClass.SMART, ModelClass.BALANCED):
        for info in catalog.by_class(klass):
            if not info.local and info.id in usable:
                return info
    return catalog.default_local(local_models)


async def source_text(db: Database, path: str) -> str:
    """The indexed text of one file, in order, or `""` if it was never indexed.

    The chunks overlap by `indexer.OVERLAP_CHARS`, which is left alone: the
    repeated 200 characters cost a little of the budget and removing them
    correctly would mean trusting that every chunk was written by the current
    chunker. A model reading a sentence twice is not a failure mode.
    """

    def _read(c: sqlite3.Connection) -> list[str]:
        rows = c.execute(
            "SELECT text FROM file_chunks WHERE path = ? ORDER BY chunk_idx",
            (path,),
        ).fetchall()
        return [str(r["text"]) for r in rows]

    return "\n".join(await db.run(_read))


class CurriculumBuilder:
    """Builds a subject's concept map from source material."""

    def __init__(
        self,
        db: Database,
        providers: Mapping[str, LLMProvider],
        local_models: Sequence[str],
    ) -> None:
        self._db = db
        self._providers = providers
        self._local_models = local_models

    async def build(
        self,
        *,
        source: str,
        subject_hint: str = "",
        source_path: str | None = None,
        usable_models: set[str] | None = None,
    ) -> CurriculumReport:
        """Extract concepts from `source` and write them to a subject.

        Never raises. A failure comes back as a report with `error` set, so the
        tool above can say what went wrong rather than dying inside a turn.
        """
        report = CurriculumReport(subject=subject_hint.strip())

        trimmed = source.strip()[:MAX_SOURCE_CHARS]
        if len(trimmed) < 200:
            report.error = (
                "There is not enough text in that material to build a map from. "
                "If it is a scanned PDF or an image-only deck there is no text "
                "layer to read — export it with text, or paste the content in."
            )
            return report

        info = choose_model(usable_models or set(), self._local_models)
        report.model, report.local = info.id, info.local

        raw = await self._generate(info, trimmed, report)
        if raw is None:
            return report

        parsed = _extract_json(raw)
        if parsed is None:
            report.error = (
                f"{report.model} did not return a readable concept map. "
                "Ask again — this usually works on a second attempt."
            )
            log.warning("curriculum.unparsable", model=report.model, raw=raw[:200])
            return report

        output = CurriculumOutput.model_validate(parsed)
        concepts = [c for c in output.concepts if c.name.strip()][:MAX_CONCEPTS]
        report.concepts_found = len(concepts)
        if not concepts:
            report.error = "No teachable concepts came back from that material."
            return report

        # The model's own name for the topic, unless the caller named it. The
        # caller's name wins because it is what the user typed, and resuming
        # works by matching what he says.
        report.subject = report.subject or output.subject.strip() or "Study"

        subject_id = await study.ensure_subject(self._db, report.subject, source_path)
        report.subject_id = subject_id
        report.concepts_added = await study.add_concepts(
            self._db, subject_id, [(c.name, c.summary) for c in concepts]
        )
        log.info(
            "curriculum.built",
            subject=report.subject,
            found=report.concepts_found,
            added=report.concepts_added,
            model=report.model,
        )
        return report

    async def _generate(self, info: ModelInfo, source: str, report: CurriculumReport) -> str | None:
        """Ask the chosen model, falling back to local on a provider failure.

        `report.model` is rewritten on the fallback path. `reflection` records
        why: logging the model that was *tried* made a fallback invisible in
        the very log line recording it working.
        """
        try:
            return await self._stream(info, source)
        except ProviderError as exc:
            if info.local:
                report.error = f"The local model could not read that material: {exc}"
                log.warning("curriculum.local_failed", error=str(exc))
                return None
            log.warning("curriculum.fell_back_to_local", model=info.id, error=str(exc))

        fallback = catalog.default_local(self._local_models)
        report.model, report.local = fallback.id, True
        try:
            return await self._stream(fallback, source)
        except ProviderError as exc:
            report.error = f"No model could read that material: {exc}"
            log.warning("curriculum.local_failed", error=str(exc))
            return None

    async def _stream(self, info: ModelInfo, source: str) -> str:
        provider = self._providers.get(info.provider)
        if provider is None:
            raise ProviderError(f"No provider configured for {info.provider}.")

        chunks: list[str] = []
        async for delta in provider.stream_chat(
            build_prompt(source),
            model=info.id,
            options=GenerationOptions(
                num_ctx=info.context_tokens, max_tokens=CURRICULUM_MAX_TOKENS
            ),
        ):
            chunks.append(delta.text)
            if delta.done:
                break
        return "".join(chunks)
