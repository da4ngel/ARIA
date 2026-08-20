"""Turning a lecture into a concept map, and surviving what a model returns.

The extraction is one model call over somebody's slides, which makes the
failure modes here the interesting part: fenced JSON, a refusal, a provider
outage, a map with concepts that were never in the material. Every one of them
has to come back as a report the tool can explain rather than an exception
inside a turn.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import AsyncIterator

import pytest

from sidecar.memory import curriculum, study
from sidecar.memory.db import Database
from sidecar.providers.base import ProviderError, StreamDelta

LECTURE = (
    "Information Security. The CIA triad is confidentiality, integrity and "
    "availability. Confidentiality means only authorised parties can read the "
    "data. Integrity means it has not been altered. Availability means the "
    "system responds when it is needed. Access control decides who may do "
    "what, and is usually role-based. A replay attack re-sends a captured "
    "message to impersonate the original sender; nonces and timestamps defeat "
    "it. " * 3
)

GOOD_REPLY = json.dumps(
    {
        "subject": "Information Security",
        "concepts": [
            {"name": "CIA Triad", "summary": "Confidentiality, integrity, availability."},
            {"name": "Access Control", "summary": "Who may do what."},
            {"name": "Replay Attacks", "summary": "Re-sending a captured message."},
        ],
    }
)


class StubProvider:
    """Replies with whatever it was given, or raises."""

    def __init__(self, reply: str = "{}", *, fails: bool = False) -> None:
        self.reply = reply
        self.fails = fails
        self.calls = 0

    async def stream_chat(self, messages: object, **kwargs: object) -> AsyncIterator[StreamDelta]:
        self.calls += 1
        if self.fails:
            raise ProviderError("That account is not active.")
        yield StreamDelta(text=self.reply, done=True)


def _builder(database: Database, provider: StubProvider) -> curriculum.CurriculumBuilder:
    return curriculum.CurriculumBuilder(
        database,
        {"ollama": provider},  # type: ignore[dict-item]
        ["qwen2.5:7b"],
    )


# ── the happy path ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_a_lecture_becomes_a_subject_with_ordered_concepts(database: Database) -> None:
    report = await _builder(database, StubProvider(GOOD_REPLY)).build(
        source=LECTURE, source_path="C:/lectures/infosec.pptx"
    )

    assert report.error is None
    assert report.concepts_added == 3
    state = await study.state(database, report.subject_id or 0)
    assert state is not None
    assert [c.name for c in state.concepts] == ["CIA Triad", "Access Control", "Replay Attacks"]
    assert state.source_path == "C:/lectures/infosec.pptx"


@pytest.mark.asyncio
async def test_the_name_he_used_wins_over_the_model_s_own(database: Database) -> None:
    """Resuming works by matching what he says, so the subject has to be
    filed under his words rather than the model's tidier ones."""
    report = await _builder(database, StubProvider(GOOD_REPLY)).build(
        source=LECTURE, subject_hint="week 3 infosec"
    )

    assert report.subject == "week 3 infosec"
    assert await study.find_subject(database, "week 3 infosec") == report.subject_id


@pytest.mark.asyncio
async def test_json_wrapped_in_a_fence_and_prose_still_parses(database: Database) -> None:
    """What a local 7B actually returns. `_extract_json` is imported from
    `reflection` rather than copied precisely so this keeps working."""
    messy = f"Sure, here is the map:\n```json\n{GOOD_REPLY}\n```\nHope that helps."

    report = await _builder(database, StubProvider(messy)).build(source=LECTURE)

    assert report.error is None
    assert report.concepts_found == 3


# ── the ways it goes wrong ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_material_with_no_text_says_what_to_do_about_it(database: Database) -> None:
    """A scanned PDF or an image-only deck is a normal thing to be handed, and
    "no text layer — export it with text" is worth more than a stack trace."""
    provider = StubProvider(GOOD_REPLY)
    report = await _builder(database, provider).build(source="   ")

    assert report.error is not None
    assert "scanned" in report.error
    assert provider.calls == 0, "nothing to read is not worth a model call"


@pytest.mark.asyncio
async def test_an_unreadable_reply_is_a_report_not_an_exception(database: Database) -> None:
    report = await _builder(database, StubProvider("I'd rather not.")).build(source=LECTURE)

    assert report.error is not None
    assert report.subject_id is None


@pytest.mark.asyncio
async def test_an_empty_concept_list_does_not_create_an_empty_subject(database: Database) -> None:
    """A subject with no concepts would render as "0 of 0 covered" forever and
    win `latest_subject_id` over the real one."""
    report = await _builder(database, StubProvider('{"concepts": []}')).build(source=LECTURE)

    assert report.error is not None
    assert await study.latest_subject_id(database) is None


@pytest.mark.asyncio
async def test_a_provider_outage_falls_back_to_local_and_says_which_model_ran(
    database: Database,
) -> None:
    """`reflection` records why this matters: reporting the model that was
    *tried* made the fallback invisible in the log recording it working."""
    cloud = StubProvider(fails=True)
    local = StubProvider(GOOD_REPLY)
    builder = curriculum.CurriculumBuilder(
        database,
        {"openai": cloud, "ollama": local},  # type: ignore[dict-item]
        ["qwen2.5:7b"],
    )

    report = await builder.build(source=LECTURE, usable_models={"gpt-5"})

    assert report.error is None
    assert report.local is True
    assert report.model == "qwen2.5:7b"
    assert cloud.calls == 1 and local.calls == 1


@pytest.mark.asyncio
async def test_a_map_is_capped_however_many_come_back(database: Database) -> None:
    """Past a couple of dozen a map stops being a map and becomes the
    transcript again — and every concept is a row plus a line in the tool's
    own reply to the model."""
    flood = json.dumps(
        {"subject": "X", "concepts": [{"name": f"C{i}", "summary": ""} for i in range(100)]}
    )

    report = await _builder(database, StubProvider(flood)).build(source=LECTURE)

    assert report.concepts_found == curriculum.MAX_CONCEPTS


@pytest.mark.asyncio
async def test_a_very_long_lecture_is_trimmed_before_it_is_sent(database: Database) -> None:
    provider = StubProvider(GOOD_REPLY)
    await _builder(database, provider).build(source="word " * 200_000)

    assert provider.calls == 1


# ── the reader that did not exist ──────────────────────────────────────


@pytest.mark.asyncio
async def test_indexed_chunks_are_read_back_in_order(database: Database) -> None:
    """`file_chunks` has held this text since Phase 4 and nothing on the turn
    path had ever read it — `search_content` collapses chunks to file paths and
    throws the text away."""

    path = "C:/lectures/infosec.pptx"

    def _seed(conn: sqlite3.Connection) -> None:
        with conn:
            # `file_chunks.path` is a foreign key into `file_index`, so the
            # indexer's own record has to exist first.
            conn.execute(
                "INSERT INTO file_index (path, name, ext, size, mtime, content_hash, "
                "indexed_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (path, "infosec.pptx", ".pptx", 1, 1.0, "hash", "2026-08-20T00:00:00Z", "ok"),
            )
            for idx, text in enumerate(["first part", "second part", "third part"]):
                conn.execute(
                    "INSERT INTO file_chunks (path, chunk_idx, text) VALUES (?, ?, ?)",
                    (path, idx, text),
                )

    await database.run(_seed)

    text = await curriculum.source_text(database, path)

    assert text == "first part\nsecond part\nthird part"


@pytest.mark.asyncio
async def test_a_file_that_was_never_indexed_reads_as_empty(database: Database) -> None:
    assert await curriculum.source_text(database, "C:/nothing/here.pdf") == ""
