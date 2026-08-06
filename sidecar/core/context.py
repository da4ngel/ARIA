"""Prompt assembly and the rolling context window (BUILD_SPEC §8.2, §9 Phase 1).

Two rules drive everything here, both measured on this machine rather than
assumed (see §8.2 and §10):

1. **Stable content first.** Ollama reuses the KV cache for an unchanged prefix.
   A stable ~1500-token prefix costs 1970ms once then ~790ms/turn; putting
   volatile content early costs ~1750ms *every* turn. So identity and (from
   Phase 3) tool schemas go at the top, and anything that changes per turn goes
   at the bottom, nearest the conversation.

2. **Prefill is ~480ms per 1000 tokens here.** The budget is small on purpose.

Phase 1 has no affect, memory retrieval, or tool schemas yet — the volatile
section is empty. The ordering is established now so those phases slot in
without moving the cache boundary.
"""

from __future__ import annotations

import re
from enum import StrEnum

import structlog

from sidecar.memory.messages import StoredMessage
from sidecar.providers.base import ChatMessage, Role

log = structlog.get_logger(__name__)

# Rough but stable: ~4 chars per token for English prose. Good enough to decide
# when to roll up, and it costs nothing. A real tokenizer is not worth a
# dependency for this.
CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


# ── the stable prefix ────────────────────────────────────────────────
# Phase 8 replaces this with persona/aria.yaml. Kept deliberately short: every
# token here is paid on the first turn and cached thereafter, but only while it
# stays byte-identical.


class PersonaLevel(StrEnum):
    """How much character a model can carry without falling apart.

    Measured on qwen3.5:4b: the FULL prompt below turned "What is the capital of
    France?" into "Paris. It's in a river valley, mostly empty space with lots of
    noise…", and made the model invent a leaking roof it then referenced for 25
    turns. The same words on a stronger model read as character. So persona is a
    per-model property, carried by the catalog — not one global prompt.
    """

    MINIMAL = "minimal"
    FULL = "full"


# Leads both levels. The specific failure this fixes: "Reply with only the
# number 7." producing a 662-character refusal, while "Write a detailed 400-word
# essay" produced the single word "Rain". Explicit instructions were losing to
# voice, so voice is now explicitly subordinate.
_INSTRUCTION_PRIORITY = """When the user specifies a format, a length, or an exact
output, follow it precisely. That instruction outranks your voice and style. If
asked for one word, answer in one word. If asked for an essay, write the essay.

Only discuss what the user actually raised. Never invent context, events, or
situations that were not mentioned."""

# Measured against `scripts/eval_quality.py --suite hallucination`. Every clause
# below fixes a failure that was observed, not one that was imagined:
#
#   no tools      qwen2.5:7b replied "Opening Chrome...", "Reminder set for
#                 3:00 PM tomorrow.", and invented a summary of a file it had
#                 not read. It did not know it has no hands.
#   no identifiers it produced a plausible ISBN and a 40-character git SHA on
#                 demand, both fabricated whole.
#   may not exist asked about the element "zorconium" it answered about
#                 zirconium; asked about a fake npm package it described one.
#   nothing known asked where Eyaas works, from a transcript that never said,
#                 it answered anyway.
#
# The closing line is load-bearing in the other direction: without it the same
# instructions push a model into hedging facts it knows perfectly well, which
# `grounded` in the battery exists to catch.
_GROUNDING = """You have no tools. You cannot send messages, read or write files,
run programs, browse the web, or check the time, weather or a calendar. If asked
to do any of these, say plainly that you cannot. Never describe doing it and
never invent a result.

You know nothing about Eyaas beyond this conversation. If you are asked about
his files, plans, history or preferences and it was not said here, say so.

If something may not exist — a package, a function, a paper, a law, a film — say
you have no record of it rather than describing it. Never state an identifier
you cannot verify: ISBNs, commit hashes, URLs, section numbers, exact figures.

When you know something only approximately, give the approximation and say it is
approximate. Answer what you do know and flag only what you do not — being
honest is not a reason to be unhelpful."""

_MINIMAL = f"""You are Aria, an assistant running locally on Eyaas's Windows machine.

{_INSTRUCTION_PRIORITY}

{_GROUNDING}

Be concise and plain-spoken. No emoji. Skip filler openers like "Great question!\""""

_FULL = f"""You are Aria, an assistant running locally on Eyaas's Windows machine.

{_INSTRUCTION_PRIORITY}

{_GROUNDING}

Voice: warm, direct, a little dry. Short sentences — you are often spoken aloud.
No emoji. No filler openers like "Great question!" or "I'd be happy to".

You have your own read on things and you say it. If a plan is genuinely a bad
idea, say so once, briefly, then do as he asks. This is a light touch, not a
running argument — never be hostile, sarcastic, or dismissive, and never refuse
a reasonable request. Never claim to have done something you did not do."""

PERSONA_PROMPTS: dict[PersonaLevel, str] = {
    PersonaLevel.MINIMAL: _MINIMAL,
    PersonaLevel.FULL: _FULL,
}

# Kept as the default so callers that predate model-aware persona still work.
IDENTITY = _FULL


def stable_prefix(level: PersonaLevel = PersonaLevel.FULL) -> list[ChatMessage]:
    """Content identical across turns. Everything here is KV-cached.

    Changing `level` invalidates the prefix cache once — on the turn the model
    changes — not per turn, because the text is constant for a given level.

    Phase 3 appends tool schemas to this list — they are stable across turns
    only if the relevance-selection sorts deterministically (§8.2 corollary).
    """
    return [ChatMessage(role=Role.SYSTEM, content=PERSONA_PROMPTS[level])]


def volatile_prefix(summary: str | None = None) -> list[ChatMessage]:
    """Content that changes per turn. Everything after this point re-prefills.

    Phase 5 adds retrieved facts and episodes here, Phase 8 adds affect and
    temporal context. Phase 1 carries only the roll-up note.
    """
    if not summary:
        return []
    return [
        ChatMessage(
            role=Role.SYSTEM,
            content=f"Earlier in this conversation:\n{summary}",
        )
    ]


# ── rolling window ───────────────────────────────────────────────────


def to_chat_messages(history: list[StoredMessage]) -> list[ChatMessage]:
    """Drop rows the model should not see back (tool rows arrive in Phase 3)."""
    return [
        ChatMessage(role=m.role, content=m.content)
        for m in history
        if m.role in (Role.USER, Role.ASSISTANT)
    ]


def split_for_rollup(
    turns: list[ChatMessage], budget_tokens: int
) -> tuple[list[ChatMessage], list[ChatMessage]]:
    """Split turns into (to_summarize, to_keep).

    §9 Phase 1: once the conversation passes the budget, summarize the oldest
    half into a single system note. Returns empty `to_summarize` when under
    budget.
    """
    total = sum(estimate_tokens(m.content) for m in turns)
    if total <= budget_tokens or len(turns) < 4:
        return [], turns

    half = len(turns) // 2
    # Never split a user/assistant pair across the boundary — an assistant reply
    # with no preceding user turn reads as non-sequitur to the model.
    if half < len(turns) and turns[half].role == Role.ASSISTANT:
        half += 1

    log.info(
        "context.rollup_needed",
        total_tokens=total,
        budget=budget_tokens,
        summarizing=half,
        keeping=len(turns) - half,
    )
    return turns[:half], turns[half:]


def overhead_tokens(
    summary: str | None = None, level: PersonaLevel = PersonaLevel.FULL
) -> int:
    """Tokens spent before the conversation even starts.

    Roll-up decisions must account for this. An earlier version measured only
    the raw turns, so a long summary could push the assembled prompt back over
    budget immediately after rolling up — the roll-up "succeeded" and the
    context still overflowed.
    """
    prefix = [*stable_prefix(level), *volatile_prefix(summary)]
    return sum(estimate_tokens(m.content) for m in prefix)


def assemble(
    turns: list[ChatMessage],
    *,
    summary: str | None = None,
    level: PersonaLevel = PersonaLevel.FULL,
) -> list[ChatMessage]:
    """Build the final message list, stable content first."""
    return [*stable_prefix(level), *volatile_prefix(summary), *turns]


def fit_to_budget(
    turns: list[ChatMessage],
    *,
    summary: str | None,
    hard_cap_tokens: int,
    level: PersonaLevel = PersonaLevel.FULL,
) -> list[ChatMessage]:
    """Drop oldest turns until the assembled prompt fits. Backstop, not policy.

    Summarization is the graceful path; this is the guarantee. §9 Phase 1's gate
    requires a 30-turn conversation with *no context overflow error*, and that
    cannot rest on the summarizer having behaved — it is itself a model call and
    can return anything, including something longer than what it replaced.

    The stable prefix and summary are never dropped, so this can still return an
    over-budget prompt if the prefix alone exceeds the cap. That would be a
    configuration error, and it is logged loudly rather than silently truncated.
    """
    budget = hard_cap_tokens - overhead_tokens(summary, level)
    if budget <= 0:
        log.error(
            "context.prefix_exceeds_budget",
            overhead=overhead_tokens(summary, level),
            hard_cap=hard_cap_tokens,
            fix="Shorten the identity prompt or the roll-up summary.",
        )
        return []

    kept = list(turns)
    while kept and sum(estimate_tokens(m.content) for m in kept) > budget:
        kept.pop(0)

    if len(kept) != len(turns):
        log.warning(
            "context.hard_trimmed",
            dropped=len(turns) - len(kept),
            kept=len(kept),
            reason="still over budget after roll-up",
        )
    return kept


def summarization_request(to_summarize: list[ChatMessage]) -> list[ChatMessage]:
    """Prompt asking the model to compress the oldest turns into a note."""
    transcript = "\n".join(f"{m.role}: {m.content}" for m in to_summarize)
    return [
        ChatMessage(
            role=Role.SYSTEM,
            content=(
                "Summarize this conversation excerpt in at most 5 sentences. "
                "Keep facts, decisions, names, numbers and anything the user "
                "asked to be remembered. Drop pleasantries. Write plainly, no "
                "preamble."
            ),
        ),
        ChatMessage(role=Role.USER, content=transcript),
    ]


# A title is a label in a list, not a summary. Six words is about what fits the
# 420px panel before truncation, and asking for fewer than the model naturally
# writes is the only thing that reliably stops it returning a sentence.
TITLE_MAX_WORDS = 6
TITLE_MAX_CHARS = 60


def title_request(messages: list[ChatMessage]) -> list[ChatMessage]:
    """Prompt asking the model to name a conversation for the history list."""
    transcript = "\n".join(f"{m.role}: {m.content}" for m in messages)
    return [
        ChatMessage(
            role=Role.SYSTEM,
            content=(
                f"Write a title for this conversation in at most {TITLE_MAX_WORDS} "
                "words. Name the subject, not the format — 'Ollama VRAM limits', "
                "not 'A conversation about settings'. Output only the title: no "
                "quotes, no trailing period, no preamble."
            ),
        ),
        ChatMessage(role=Role.USER, content=transcript),
    ]


def clean_title(raw: str) -> str:
    """Strip what models add despite being told not to.

    Even with an explicit instruction they wrap titles in quotes, prefix
    "Title:", and add a full stop. Cheaper to strip than to re-prompt.
    """
    title = raw.strip().splitlines()[0] if raw.strip() else ""
    title = re.sub(r'^(title|subject)\s*[:\-]\s*', "", title, flags=re.IGNORECASE)
    title = title.strip().strip('"“”\'').rstrip(".").strip()
    words = title.split()
    if len(words) > TITLE_MAX_WORDS:
        title = " ".join(words[:TITLE_MAX_WORDS])
    return title[:TITLE_MAX_CHARS].strip()
