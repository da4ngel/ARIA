"""Reminders the user sets out loud.

**The model parses the time, not a regex here.** "in twenty minutes", "tomorrow
at nine", "after lunch" — a pattern table for that would be a permanent source
of near-misses, and unlike the yes/no reply in `procedures` or the triple
extraction in `tools/memory.py`, the model is *already* in the loop: this is a
tool call, so the parsing costs nothing extra. It hands back either a count of
minutes or an ISO timestamp.

Two ways to say when, which is `set_volume`'s shape and for the same reason.
That tool took only an absolute `percent`, so a model asked to "turn it up" had
to invent a number blind; giving it `direction` as well is what fixed it. Here,
`in_minutes` is what a relative request produces naturally and `at` is what an
absolute one does, and forcing either through the other is the same mistake.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import structlog

from sidecar.memory import reminders as store
from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

#: Roughly a year. Nobody means "remind me in three years", and an unbounded
#: value lets one mistyped argument park a row in the table forever.
MAX_MINUTES = 366 * 24 * 60


def _local(moment: datetime) -> str:
    """A due time in the user's own timezone. UTC is stored; UTC is not shown."""
    return moment.astimezone().strftime("%a %d %b, %H:%M")


@tool(
    name="set_reminder",
    # **SAFE, not CONFIRM.** A confirmation dialog in front of "remind me in
    # twenty minutes" destroys the feature, which is the same argument that
    # made `remember` T1 — and this changes nothing on the machine, creates
    # nothing outside ARIA, and is cancellable from the panel in one click.
    tier=Tier.SAFE,
    description=(
        "Set a reminder for later. Give EITHER in_minutes for a relative time "
        "('in 20 minutes', 'in an hour') OR at for a specific one, as an "
        "ISO-8601 timestamp you work out yourself from what he said ('tomorrow "
        "at 9' -> '2026-08-25T09:00'). Use his own words as the text."
    ),
)
async def set_reminder(
    ctx: ToolContext,
    text: str,
    in_minutes: int | None = None,
    at: str | None = None,
) -> ToolResult:
    """Set a reminder.

    Args:
        text: What to remind him about, in his own words
        in_minutes: Minutes from now, for a relative time like "in 20 minutes"
        at: An ISO-8601 timestamp for a specific time, e.g. "2026-08-25T09:00".
            Local time unless it carries a timezone.
    """
    from sidecar.state import runtime

    if runtime.db is None:
        return ToolResult(
            ok=False,
            summary="Reminders are not available in this session.",
            error="unavailable",
        )
    if not text.strip():
        return ToolResult(
            ok=False, summary="Tell me what to remind you about.", error="empty"
        )

    now = datetime.now(UTC)
    if in_minutes is not None:
        if in_minutes <= 0:
            return ToolResult(
                ok=False,
                summary="A reminder has to be in the future. Say how long from now.",
                error="past",
            )
        if in_minutes > MAX_MINUTES:
            return ToolResult(
                ok=False,
                summary="That is more than a year away. Pick something nearer.",
                error="too_far",
            )
        due = now + timedelta(minutes=in_minutes)
    elif at is not None:
        parsed = store.parse_due(at)
        if parsed is None:
            return ToolResult(
                ok=False,
                summary=(
                    f"I could not read {at!r} as a time. Give it as an ISO "
                    f"timestamp like 2026-08-25T09:00."
                ),
                error="unparseable",
            )
        if parsed <= now:
            return ToolResult(
                ok=False,
                summary=f"{_local(parsed)} has already passed. When did you mean?",
                error="past",
            )
        due = parsed
    else:
        # Neither given. Say which two things would work rather than "invalid
        # arguments" — an error message has to name the next step.
        return ToolResult(
            ok=False,
            summary=(
                "Say when: either in_minutes for a relative time, or at for a "
                "specific one."
            ),
            error="no_time",
        )

    reminder_id = await store.create(
        runtime.db, text, due, session_id=ctx.session_id, now=now
    )
    return ToolResult(
        ok=True,
        data={"id": reminder_id, "due_at": due.isoformat()},
        summary=f"Reminder set for {_local(due)}: {text.strip()}",
        display={"kind": "reminder", "id": reminder_id, "text": text.strip(),
                 "due_at": due.isoformat()},
    )


@tool(
    name="list_reminders",
    tier=Tier.AUTO,
    description="See the reminders that are set and have not fired yet.",
)
async def list_reminders(ctx: ToolContext) -> ToolResult:
    """List pending reminders."""
    from sidecar.state import runtime

    if runtime.db is None:
        return ToolResult(
            ok=False,
            summary="Reminders are not available in this session.",
            error="unavailable",
        )

    pending = await store.pending(runtime.db)
    if not pending:
        return ToolResult(ok=True, data=[], summary="Nothing is set.")

    now = datetime.now(UTC)
    lines = [
        f"{r.id}. {r.text} — {_local(r.due_at)}"
        + (" (overdue)" if r.due_at <= now else "")
        for r in pending
    ]
    return ToolResult(
        ok=True,
        data=[store.as_dict(r, now=now) for r in pending],
        summary=f"{len(pending)} reminder{'s' if len(pending) != 1 else ''} set:\n"
        + "\n".join(lines),
        display={"kind": "reminders", "reminders": [store.as_dict(r, now=now) for r in pending]},
    )


@tool(
    name="cancel_reminder",
    # **CONFIRM, and the tier is heavier than it feels.** Rule 5 names delete
    # and takes no exceptions, and a reminder cancelled by mistake is silent —
    # you find out by the thing not happening. The *panel* cancels in one click
    # with no dialog, which is the `files.delete` distinction: a click is not a
    # tool call, and nobody should be asked to confirm what they just did.
    tier=Tier.CONFIRM,
    description=(
        "Cancel a reminder that has not fired yet. Call list_reminders first "
        "to get its id."
    ),
)
async def cancel_reminder(ctx: ToolContext, reminder_id: int) -> ToolResult:
    """Cancel a pending reminder.

    Args:
        reminder_id: Which one, from list_reminders
    """
    from sidecar.state import runtime

    if runtime.db is None:
        return ToolResult(
            ok=False,
            summary="Reminders are not available in this session.",
            error="unavailable",
        )

    if await store.cancel(runtime.db, reminder_id):
        return ToolResult(
            ok=True, data={"id": reminder_id}, summary=f"Cancelled reminder {reminder_id}."
        )
    return ToolResult(
        ok=False,
        summary=(
            f"There is no pending reminder {reminder_id} — it may have already "
            f"fired or been cancelled. Call list_reminders to see what is set."
        ),
        error="not_found",
    )
