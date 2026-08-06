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

IDENTITY = """You are Aria, a local assistant running on Eyaas's Windows machine.

Voice: warm, direct, a little dry. Short sentences — you are often spoken aloud.
No emoji. No filler openers like "Great question!" or "I'd be happy to".
Minimal hedging.

You have your own read on things and you say it. If something is a bad idea,
say so once, clearly, then do it if he insists. Never claim to have done
something you did not do. If you do not know, say so."""


def stable_prefix() -> list[ChatMessage]:
    """Content identical across turns. Everything here is KV-cached.

    Phase 3 appends tool schemas to this list — they are stable across turns
    only if the relevance-selection sorts deterministically (§8.2 corollary).
    """
    return [ChatMessage(role=Role.SYSTEM, content=IDENTITY)]


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


def overhead_tokens(summary: str | None = None) -> int:
    """Tokens spent before the conversation even starts.

    Roll-up decisions must account for this. An earlier version measured only
    the raw turns, so a long summary could push the assembled prompt back over
    budget immediately after rolling up — the roll-up "succeeded" and the
    context still overflowed.
    """
    prefix = [*stable_prefix(), *volatile_prefix(summary)]
    return sum(estimate_tokens(m.content) for m in prefix)


def assemble(
    turns: list[ChatMessage],
    *,
    summary: str | None = None,
) -> list[ChatMessage]:
    """Build the final message list, stable content first."""
    return [*stable_prefix(), *volatile_prefix(summary), *turns]


def fit_to_budget(
    turns: list[ChatMessage], *, summary: str | None, hard_cap_tokens: int
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
    budget = hard_cap_tokens - overhead_tokens(summary)
    if budget <= 0:
        log.error(
            "context.prefix_exceeds_budget",
            overhead=overhead_tokens(summary),
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
