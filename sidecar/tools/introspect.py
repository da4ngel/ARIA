""""Why did you do that?" — answered from the record, not from memory.

**This tool exists because the model does not know the answer.** Which model
ran, which router stage picked it and why, whether a confirmation was shown and
who approved it — none of that is in the conversation. Asked without this, the
only thing a model can do is produce a plausible-sounding account of its own
reasoning, which is invention of exactly the kind every anti-invention clause in
`core/context.py` exists to stop. "Why did it do that" is the question most
likely to invite it, because a confident answer sounds like self-awareness.

So the tool hands over **facts** and the model narrates them. `tool_log` has the
call, its arguments, whether it was approved and by what; `routing_log.stage`
and `.detail` are the router's own `RouteReason`, written so a row explains
itself without the code that produced it.
"""

from __future__ import annotations

import json
from typing import Any

import structlog

from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

#: Arguments are stored as JSON truncated to 4000 characters. Nobody needs all
#: of that read back at them, and `type_text`'s argument is an entire essay.
ARG_PREVIEW_CHARS = 300

#: How a stage name reads to a person. `routing_log.stage` is the router's own
#: vocabulary; leaving it raw would make the answer a log line rather than an
#: explanation.
_STAGE_WORDS = {
    "explicit": "you had picked that model by hand",
    "private": "the message looked private, so it stayed on this machine",
    "attachment": (
        "the turn carried one of your files, so it avoided endpoints that may "
        "train on what is sent"
    ),
    "offline": "nothing else was reachable",
    "local_only": "a tool result had to stay on this machine",
    "spoken": "it was a spoken turn",
    "tool": "the message looked like it wanted a tool",
    "quality": "the question looked substantive",
    "fastest": "speed was the priority",
    "balanced": "a middle option",
    "fallback": "the first choice had failed",
    "proactive": "she started this one herself",
    "step": "a later step of a multi-tool turn",
}


def _approval(row: dict[str, Any]) -> str:
    approved, by = row.get("approved"), row.get("approved_by")
    if approved is None:
        return "it needed no confirmation"
    if not approved:
        return "you denied it" if by == "user" else "it was denied (the dialog timed out)"
    return {
        "user": "you approved it",
        "trust": "it ran without asking because the folder is trusted",
        "full_access": "it ran without asking because Full access was on",
    }.get(str(by), "it was approved")


def _arguments(raw: str) -> str:
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw[:ARG_PREVIEW_CHARS]
    if not isinstance(parsed, dict) or not parsed:
        return ""
    parts = []
    for key, value in parsed.items():
        text = value if isinstance(value, str) else json.dumps(value)
        clipped = text[:120] + ("…" if len(text) > 120 else "")
        parts.append(f"{key}={clipped}")
    return ", ".join(parts)[:ARG_PREVIEW_CHARS]


def describe(tool_row: dict[str, Any] | None, route_row: dict[str, Any] | None) -> str:
    """The two rows as plain sentences. Pure, so a test can read it.

    Returns "" when there is nothing recorded, which the caller reports as a
    fact rather than dressing up — "I have no record of that" is a true answer
    and an invented one is not.
    """
    lines: list[str] = []

    if route_row is not None:
        model = route_row.get("model") or "an unknown model"
        stage = str(route_row.get("stage") or "")
        why = _STAGE_WORDS.get(stage, route_row.get("detail") or stage or "no reason recorded")
        where = "on this machine" if route_row.get("local") else "in the cloud"
        latency = route_row.get("latency_ms")
        timing = f", and took {int(latency) / 1000:.1f}s" if latency else ""
        lines.append(f"Model: {model} ({where}) — chosen because {why}{timing}.")
        prompt, completion = route_row.get("prompt_tokens"), route_row.get("completion_tokens")
        if prompt or completion:
            lines.append(f"Tokens: {prompt or 0} in, {completion or 0} out.")

    if tool_row is not None:
        name = tool_row.get("tool") or "a tool"
        args = _arguments(str(tool_row.get("args") or ""))
        with_args = f" with {args}" if args else ""
        outcome = "it worked" if tool_row.get("ok") else f"it failed ({tool_row.get('error')})"
        duration = tool_row.get("duration_ms")
        took = f" in {duration}ms" if duration else ""
        lines.append(
            f"Tool: ran `{name}`{with_args} — {_approval(tool_row)}, and "
            f"{outcome}{took}."
        )

    return "\n".join(lines)


@tool(
    name="explain_last_action",
    tier=Tier.AUTO,
    description=(
        "Look up what actually happened on the previous turn — which model "
        "answered and why it was chosen, and which tool ran with what result. "
        "Use whenever he asks why you did something, why a particular model "
        "was used, or what a tool actually did. Do not answer those from "
        "memory: you cannot see the routing decision, and this can."
    ),
)
async def explain_last_action(ctx: ToolContext) -> ToolResult:
    """Read back the last tool call and routing decision."""
    from sidecar.state import runtime

    journal, routing = runtime.tool_journal, runtime.routing_log
    if journal is None and routing is None:
        return ToolResult(
            ok=False,
            summary="There is no record to read back in this session.",
            error="unavailable",
        )

    tool_row = await journal.last(ctx.session_id) if journal is not None else None
    route_rows = await routing.recent_turns(1) if routing is not None else []
    route_row = route_rows[0] if route_rows else None

    account = describe(tool_row, route_row)
    if not account:
        return ToolResult(
            ok=True,
            data=None,
            summary=(
                "Nothing is recorded yet for this session — no tool has run and "
                "no routing decision has been written. Say so plainly rather "
                "than guessing at what happened."
            ),
        )

    return ToolResult(
        ok=True,
        data={"tool": tool_row, "route": route_row},
        summary=(
            f"{account}\n"
            "Report these facts as they are. Do not add reasoning that is not "
            "here — you did not have access to your own routing decision when "
            "you made it."
        ),
        display={"kind": "explanation", "tool": tool_row, "route": route_row},
    )
