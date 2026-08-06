"""Machine context: the clock, the model, and what it costs to carry them."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sidecar.core.context import (
    MachineContext,
    PersonaLevel,
    assemble,
    estimate_tokens,
    machine_context,
    overhead_tokens,
    volatile_prefix,
)
from sidecar.providers.base import ChatMessage, Role

AWST = timezone(timedelta(hours=8), "AWST")
NOW = datetime(2026, 8, 6, 20, 47, 30, tzinfo=AWST)


def full() -> MachineContext:
    return MachineContext(
        now=NOW,
        model_label="Qwen2.5 7B (local)",
        model_is_local=True,
        online=True,
        session_started=NOW - timedelta(minutes=12),
        message_count=8,
    )


# ── what it says ──────────────────────────────────────────────────────


def test_renders_the_date_and_time() -> None:
    rendered = machine_context(full()) or ""
    assert "6 August 2026" in rendered
    assert "8:47" in rendered
    assert "Thursday" in rendered


def test_names_the_answering_model_and_where_it_runs() -> None:
    rendered = machine_context(full()) or ""
    assert "Qwen2.5 7B (local)" in rendered
    assert "on this machine" in rendered


def test_says_cloud_for_a_cloud_model() -> None:
    rendered = machine_context(MachineContext(now=NOW, model_label="GPT-5", model_is_local=False))
    assert rendered and "in the cloud" in rendered


def test_distinguishes_no_tool_from_no_internet() -> None:
    """These are different things to tell someone."""
    online = machine_context(MachineContext(now=NOW, online=True)) or ""
    offline = machine_context(MachineContext(now=NOW, online=False)) or ""
    assert "online" in online and "no tool" in online
    assert "offline" in offline


def test_reports_how_long_the_conversation_has_run() -> None:
    rendered = machine_context(full()) or ""
    assert "12 minutes ago" in rendered
    assert "8 messages" in rendered


def test_a_brand_new_conversation_says_just_now() -> None:
    ctx = MachineContext(now=NOW, session_started=NOW, message_count=2)
    assert "just now" in (machine_context(ctx) or "")


def test_singular_minute() -> None:
    ctx = MachineContext(now=NOW, session_started=NOW - timedelta(minutes=1), message_count=2)
    assert "1 minute ago" in (machine_context(ctx) or "")


def test_hours_for_a_long_conversation() -> None:
    ctx = MachineContext(now=NOW, session_started=NOW - timedelta(hours=3), message_count=40)
    assert "3 hours ago" in (machine_context(ctx) or "")


def test_a_conversation_older_than_a_day_omits_the_age() -> None:
    """'4 days ago' is not worth the tokens, and the date already says when."""
    ctx = MachineContext(now=NOW, session_started=NOW - timedelta(days=4), message_count=2)
    rendered = machine_context(ctx) or ""
    assert "ago" not in rendered


def test_empty_context_renders_nothing() -> None:
    """Silence beats a wrong claim: unknown facts are simply not mentioned."""
    assert machine_context(MachineContext()) is None
    assert volatile_prefix(None, MachineContext()) == []


# ── the cache boundary ────────────────────────────────────────────────


def test_time_is_rendered_to_the_minute_not_the_second() -> None:
    """The whole design rests on this.

    This block sits before the conversation, so a string that changed every turn
    would invalidate the KV cache for every turn after it — about a second each,
    per CLAUDE.md. Turns are seconds apart, so minute granularity means
    consecutive turns share the prefix.
    """
    a = machine_context(MachineContext(now=NOW))
    b = machine_context(MachineContext(now=NOW + timedelta(seconds=29)))
    assert a == b


def test_a_new_minute_does_change_the_prefix() -> None:
    a = machine_context(MachineContext(now=NOW))
    b = machine_context(MachineContext(now=NOW + timedelta(minutes=1)))
    assert a != b


# ── budget ────────────────────────────────────────────────────────────


def test_the_block_is_small() -> None:
    assert estimate_tokens(machine_context(full()) or "") < 100


def test_the_whole_prefix_stays_within_the_local_budget() -> None:
    """CLAUDE.md: keep the pre-conversation budget near 800 tokens on local."""
    for level in PersonaLevel:
        assert overhead_tokens(None, level, full()) < 800


def test_overhead_accounts_for_the_machine_block() -> None:
    """Roll-up decisions subtract this; if it were uncounted, a conversation
    could overflow the context immediately after successfully rolling up."""
    assert overhead_tokens(None, PersonaLevel.FULL, full()) > overhead_tokens(
        None, PersonaLevel.FULL, None
    )


# ── ordering ──────────────────────────────────────────────────────────


def test_machine_context_sits_after_identity_and_before_the_turns() -> None:
    turns = [ChatMessage(role=Role.USER, content="what time is it")]
    assembled = assemble(turns, level=PersonaLevel.MINIMAL, machine=full())

    contents = [m.content for m in assembled]
    assert "You are Aria" in contents[0], "identity must stay first and cacheable"
    assert "Right now it is" in contents[1]
    assert contents[-1] == "what time is it"


def test_summary_and_machine_context_can_coexist() -> None:
    messages = volatile_prefix("They discussed rain.", full())
    assert len(messages) == 2
    assert "rain" in messages[0].content
    assert "Right now it is" in messages[1].content
