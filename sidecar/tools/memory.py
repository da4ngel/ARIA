"""Teaching her directly: `remember` and `forget` (§9 Phase 5).

Reflection learns on its own overnight. These two are for the times you do not
want to wait for that, or want to correct something it got wrong — "remember
that I prefer short answers", "forget what you know about my old job".

Everything durable still lives in `facts`; these are a front door to the same
table MemoryPanel edits.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

import structlog

from sidecar.memory.semantic import FactSource, MergeOutcome
from sidecar.state import runtime
from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

#: A fact the user stated by hand. High, but not 1.0 — people misremember, and
#: §8.3 reserves certainty for nothing.
USER_CONFIDENCE = 0.9
#: Never delete more than this in one call, whatever matched.
FORGET_MAX = 3
#: Below this the match is a guess, and a wrong guess deletes the wrong memory.
FORGET_MIN_SCORE = 0.6

#: How many past turns `recall` quotes back. Two is enough to prove she
#: remembers and to name the subject; more is a wall of transcript in the
#: prompt, and only `summary` reaches the model (§7.2).
RECALL_MESSAGES = 2
RECALL_QUOTE_CHARS = 160
RECALL_SUMMARY_MAX_CHARS = 700

#: Free text to a triple. Deliberately a small pattern table and not a model
#: call: a tool that generates is a tool that takes a second and can fail, and
#: a mis-parsed predicate is fixable in MemoryPanel while a hung tool is not.
_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^i(?:'m| am) (?:currently )?working on (?P<o>.+)$", re.I), "works_on"),
    (re.compile(r"^i work (?:on|at) (?P<o>.+)$", re.I), "works_on"),
    (re.compile(r"^i (?:usually|normally|always|often) (?P<o>.+)$", re.I), "habitually"),
    (re.compile(r"^i prefer (?P<o>.+)$", re.I), "prefers"),
    (re.compile(r"^i like (?P<o>.+)$", re.I), "likes"),
    (re.compile(r"^i (?:dislike|hate|don'?t like) (?P<o>.+)$", re.I), "dislikes"),
    (re.compile(r"^i use (?P<o>.+)$", re.I), "uses"),
    (re.compile(r"^i live in (?P<o>.+)$", re.I), "lives_in"),
    (re.compile(r"^i(?:'m| am) (?P<o>.+)$", re.I), "is"),
    (re.compile(r"^my (?P<o>.+)$", re.I), "has"),
]

#: Lead-ins people put in front of the actual fact.
_LEAD_IN = re.compile(
    r"^(?:please\s+)?(?:remember|note|keep in mind)\s+(?:that\s+)?", re.IGNORECASE
)


def to_triple(text: str) -> tuple[str, str, str]:
    """Parse a plain sentence into (subject, predicate, object).

    The fallback is `("user", "stated", <the whole sentence>)`, which is not a
    failure: it is still retrievable, still shown in the panel, and still
    editable into a better predicate. Losing the fact would be the failure.
    """
    cleaned = _LEAD_IN.sub("", text.strip()).strip().rstrip(".")
    for pattern, predicate in _PATTERNS:
        match = pattern.match(cleaned)
        if match:
            return ("user", predicate, match.group("o").strip())
    return ("user", "stated", cleaned)


@tool(
    name="remember",
    tier=Tier.SAFE,
    description=(
        "Store something about the user that will still be true in a month — a "
        "preference, a habit, a project, a constraint, a relationship. Use when "
        "they say 'remember that...' or state a lasting fact about themselves. "
        "Not for one-off task details or anything about the current request."
    ),
)
async def remember(ctx: ToolContext, fact: str) -> ToolResult:
    """Keep something about the user for later conversations.

    Args:
        fact: The thing to remember, in plain words, e.g. "I work on Sillara
            pricing before 10am"
    """
    memory = runtime.memory
    if memory is None:
        return ToolResult(
            ok=False,
            summary="Memory is switched off, so there is nowhere to keep that.",
            error="memory_disabled",
        )
    if not fact.strip():
        return ToolResult(
            ok=False, summary="There was nothing to remember.", error="empty_fact"
        )

    subject, predicate, object_ = to_triple(fact)
    outcome, fact_id = await memory.semantic.upsert(
        subject,
        predicate,
        object_,
        confidence=USER_CONFIDENCE,
        # A fact the user asserted is pinned: §8.3 says reflection may not
        # overwrite it, only the user may.
        source=FactSource.USER,
    )

    said = {
        MergeOutcome.INSERTED: "I'll remember that.",
        MergeOutcome.REINFORCED: "I already knew that — noted again.",
        MergeOutcome.SUPERSEDED: "Updated — I had that differently before.",
        MergeOutcome.BLOCKED_BY_PIN: "I could not store that.",
    }[outcome]

    return ToolResult(
        ok=fact_id is not None,
        data={"fact_id": fact_id, "outcome": str(outcome)},
        summary=said,
        display={
            "subject": subject,
            "predicate": predicate,
            "object": object_,
            "outcome": str(outcome),
        },
    )


@tool(
    name="recall",
    tier=Tier.AUTO,
    description=(
        "Search your own memory of past conversations with the user. Use "
        "whenever they refer to something outside this chat — 'did we talk "
        "about X', 'what did I say about Y', 'do you remember Z' — or when "
        "answering needs something you were told before. Always search before "
        "saying you do not remember something."
    ),
)
async def recall(ctx: ToolContext, query: str) -> ToolResult:
    """Look through past conversations, remembered facts and episodes.

    Args:
        query: What to look for, e.g. "data science jobs" or "the banquet hall"
    """
    memory = runtime.memory
    if memory is None:
        return ToolResult(
            ok=False,
            summary="Memory is switched off, so there is nothing to search.",
            error="memory_disabled",
        )

    found = await memory.retriever.retrieve(query)
    messages = await memory.store.search_messages(
        query, limit=RECALL_MESSAGES, exclude_session=ctx.session_id
    )

    facts = [f.fact.sentence() for f in found.facts]
    episodes = [e.episode.summary for e in found.episodes]
    quotes = [f"{_when(m.created_at)}, {m.role.value}: {_clip(m.content)}" for m in messages]

    if not facts and not episodes and not quotes:
        # Said precisely, because the difference matters: a search that found
        # nothing is not the same as having no memory, and the model has to be
        # able to tell the user which one happened.
        return ToolResult(
            ok=True,
            data={"facts": [], "episodes": [], "messages": []},
            summary=f'I searched everything I remember for "{query}" and found nothing.',
            display={"query": query, "found": 0},
        )

    lines = [*(f"You know: {f}" for f in facts)]
    lines += [f"A past conversation: {e}" for e in episodes]
    lines += [f"He said, {q}" for q in quotes]

    log.info(
        "memory.recall_tool",
        facts=len(facts),
        episodes=len(episodes),
        messages=len(quotes),
    )
    return ToolResult(
        ok=True,
        data={"facts": facts, "episodes": episodes, "messages": quotes},
        summary=" | ".join(lines)[:RECALL_SUMMARY_MAX_CHARS],
        display={
            "query": query,
            "facts": facts,
            "episodes": episodes,
            "messages": [m.model_dump(mode="json") for m in messages],
        },
    )


def _clip(content: str) -> str:
    flat = " ".join(content.split())
    return flat if len(flat) <= RECALL_QUOTE_CHARS else flat[:RECALL_QUOTE_CHARS] + "…"


def _when(timestamp: str) -> str:
    """`2026-08-12T10:50:12Z` -> `on 12 Aug`. The date is what makes it a memory."""
    try:
        moment = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError:
        return "earlier"
    return f"on {moment.day} {moment:%b}"


@tool(
    name="forget",
    tier=Tier.CONFIRM,
    description=(
        "Remove something she has remembered about the user. Use when they say "
        "to forget something, that a remembered fact is wrong, or that they no "
        "longer want it kept."
    ),
)
async def forget(ctx: ToolContext, query: str) -> ToolResult:
    """Delete remembered facts matching a description.

    Args:
        query: What to forget, e.g. "my old job" or "that I use vim"
    """
    memory = runtime.memory
    if memory is None:
        return ToolResult(
            ok=False,
            summary="Memory is switched off, so there is nothing stored to forget.",
            error="memory_disabled",
        )

    found = await memory.retriever.retrieve(query)
    candidates = found.facts
    if not candidates:
        return ToolResult(
            ok=False,
            summary="I could not find anything I remember matching that.",
            error="no_match",
        )

    best = candidates[0]
    if best.score < FORGET_MIN_SCORE:
        # Refusing beats guessing. A wrongly deleted memory is silent and
        # unrecoverable; an extra question costs one turn.
        near = "; ".join(c.fact.sentence() for c in candidates[:3])
        return ToolResult(
            ok=False,
            summary=f"I'm not sure which one you mean. I know: {near}",
            display={"near_misses": [c.fact.model_dump(mode="json") for c in candidates[:3]]},
            error="ambiguous",
        )

    doomed = [c for c in candidates[:FORGET_MAX] if c.score >= FORGET_MIN_SCORE]
    removed: list[str] = []
    for candidate in doomed:
        if await memory.semantic.forget(candidate.fact.id):
            removed.append(candidate.fact.sentence())

    if not removed:
        return ToolResult(
            ok=False, summary="Those had already gone.", error="already_gone"
        )

    log.info("memory.forget_tool", removed=len(removed))
    head = removed[0]
    rest = "" if len(removed) == 1 else f" and {len(removed) - 1} more"
    return ToolResult(
        ok=True,
        data={"removed": len(removed)},
        summary=f'Forgotten: "{head}"{rest}.',
        display={"removed": removed},
    )
