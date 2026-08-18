"""Machine context: the clock, the model, and what it costs to carry them."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sidecar.core.context import (
    PERSONA_PROMPTS,
    PERSONA_PROMPTS_ONLINE,
    PERSONA_PROMPTS_WITH_TOOLS,
    RETRIEVED_MAX_TOKENS,
    MachineContext,
    PersonaLevel,
    assemble,
    estimate_tokens,
    fit_to_budget,
    machine_context,
    overhead_tokens,
    retrieved_block,
    stable_prefix,
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


# ── retrieved memory (Phase 5) ────────────────────────────────────────


def test_nothing_retrieved_renders_nothing() -> None:
    """A turn about something she has no memory of must leave the prompt
    byte-identical to a build with no memory at all."""
    assert retrieved_block([], []) is None


def test_facts_and_episodes_render_distinctly() -> None:
    rendered = retrieved_block(["user works on pricing"], ["They settled on £2,400."])
    assert rendered is not None
    assert "- user works on pricing" in rendered
    assert "Earlier: They settled on £2,400." in rendered


def test_the_block_is_capped() -> None:
    rendered = retrieved_block([f"fact number {i} " + "x" * 200 for i in range(20)], [])
    assert rendered is not None
    assert estimate_tokens(rendered) <= RETRIEVED_MAX_TOKENS


def test_episodes_are_dropped_before_facts() -> None:
    """A fact is a standing truth; an episode is one conversation."""
    rendered = retrieved_block(["a short fact"], ["y" * 4000], max_tokens=30)
    assert rendered is not None
    assert "a short fact" in rendered
    assert "Earlier:" not in rendered


def test_one_oversized_fact_is_truncated_rather_than_dropped() -> None:
    """A clipped fact beats silence — the cap is a prefill guard, not a
    correctness one."""
    rendered = retrieved_block(["z" * 4000], [], max_tokens=30)
    assert rendered is not None
    assert "z" in rendered


def test_memory_never_touches_the_stable_prefix() -> None:
    """The KV-cache bargain, asserted directly.

    CLAUDE.md's measured rule: an unchanged prefix costs ~480ms/1000 tokens
    once instead of every turn. If retrieval ever leaked into `stable_prefix`,
    every topic change would re-prefill the identity block and the tool
    schemas — about a second a turn, invisibly.
    """
    for level in PersonaLevel:
        for has_tools in (False, True):
            assert stable_prefix(level, has_tools=has_tools) == stable_prefix(
                level, has_tools=has_tools
            )

    baseline = "".join(m.content for m in stable_prefix())
    assembled = assemble(
        [ChatMessage(role=Role.USER, content="hi")],
        machine=full(),
        retrieved=retrieved_block(["user works on Sillara pricing"], []),
    )
    assert assembled[0].content == baseline
    assert "Sillara" not in assembled[0].content


def test_retrieved_memory_sits_after_the_clock() -> None:
    """§8.2's order: temporal, then facts. Memory sits nearest the turns
    because that is what it is about."""
    messages = volatile_prefix(None, full(), retrieved_block(["user likes tea"], []))
    assert len(messages) == 2
    assert "Right now it is" in messages[0].content
    assert "user likes tea" in messages[1].content


def test_overhead_counts_the_retrieved_block() -> None:
    """Uncounted, a roll-up could 'succeed' and still overflow the context —
    the same failure the machine block was fixed for."""
    rendered = retrieved_block(["user works on Sillara pricing before 10am"], [])
    assert overhead_tokens(None, PersonaLevel.FULL, full(), retrieved=rendered) > (
        overhead_tokens(None, PersonaLevel.FULL, full())
    )


def test_fit_to_budget_reserves_room_for_the_tool_schemas() -> None:
    """It used to omit them, so it trimmed against a budget ~1650 tokens too
    generous. Phase 5 threads `has_tools` through rather than adding a second
    under-count beside it."""
    turns = [ChatMessage(role=Role.USER, content="x" * 400) for _ in range(8)]
    # Derived from the real overhead rather than hard-coded, so that editing the
    # persona changes what this measures and not whether it measures anything.
    # At a fixed 700 it silently became "both trim to nothing", which passes for
    # the wrong reason right up until it fails for one.
    cap = overhead_tokens(None, PersonaLevel.FULL, None, has_tools=False) + 500
    without = fit_to_budget(turns, summary=None, hard_cap_tokens=cap, has_tools=False)
    with_tools = fit_to_budget(turns, summary=None, hard_cap_tokens=cap, has_tools=True)

    assert without, "the no-tools case must keep some turns or this proves nothing"
    assert len(with_tools) < len(without)


def test_fit_to_budget_reserves_room_for_memory() -> None:
    turns = [ChatMessage(role=Role.USER, content="x" * 400) for _ in range(8)]
    rendered = retrieved_block([f"a remembered fact number {i}" for i in range(5)], [])
    without = fit_to_budget(turns, summary=None, hard_cap_tokens=700)
    with_memory = fit_to_budget(
        turns, summary=None, hard_cap_tokens=700, retrieved=rendered
    )
    assert len(with_memory) <= len(without)


# ── she has a memory, and the prompt has to say so ────────────────────


def test_the_prompt_never_claims_she_remembers_nothing() -> None:
    """The sentence that made her deny a conversation she had just had.

    "You know nothing about Eyaas beyond this conversation" was written in
    Phase 1, when it was true, and survived Phase 5 giving her episodes, facts
    and retrieval. Asked whether they had discussed jobs, she answered "I don't
    have any record of conversations outside this chat" — compliance, not a
    retrieval miss.
    """
    for prompts in (PERSONA_PROMPTS, PERSONA_PROMPTS_WITH_TOOLS):
        for prompt in prompts.values():
            assert "know nothing about Eyaas" not in prompt
            assert "You remember earlier conversations" in prompt


def test_with_tools_she_is_told_to_look_before_denying() -> None:
    """`recall` is a tool, so the instruction to search only makes sense when
    tools are offered — and when they are not, she must not be told to call
    something that does not exist."""
    with_tools = PERSONA_PROMPTS_WITH_TOOLS[PersonaLevel.FULL]
    without = PERSONA_PROMPTS[PersonaLevel.FULL]

    assert "`recall`" in with_tools
    assert "recall" not in without


def test_both_levels_still_forbid_inventing_a_memory() -> None:
    """The anti-invention force is what took the 7B from 57% fabrication to
    27%. Making her memory-aware must not cost it."""
    for prompts in (PERSONA_PROMPTS, PERSONA_PROMPTS_WITH_TOOLS):
        for prompt in prompts.values():
            assert "Never invent" in prompt


def test_the_warm_voice_carries_no_emoji_or_filler_opener() -> None:
    """`universal_failures` fails *every* probe in *every* category on either
    of these, so a persona containing one would fail 100+ probes at once."""
    for prompts in (PERSONA_PROMPTS, PERSONA_PROMPTS_WITH_TOOLS):
        for prompt in prompts.values():
            assert "No emoji" in prompt or "no emoji" in prompt
            assert "filler openers" in prompt


def test_warmth_did_not_displace_the_capacity_to_disagree() -> None:
    """BUILD_SPEC §8.1's boundary, and the thing that keeps her from being a
    mirror: an agent tuned purely to please stops reading as anybody."""
    full = PERSONA_PROMPTS_WITH_TOOLS[PersonaLevel.FULL]
    assert "bad idea" in full
    assert "Agreeing with everything is not warmth" in full


def test_she_is_pointed_at_type_text_for_a_native_app() -> None:
    """Real failure, live: asked to "write hi in notepad", she opened it fine
    (`open_app`) then tried `browser_fill` on it (only reaches a browser tab)
    and then `write_file` to a guessed path. `type_text` was built for
    exactly this and the prompt has to say so — the first draft of this fix
    told her no tool could do it at all, written *before* `type_text`
    existed, and never updated once it did. She then told Eyaas she still
    could not type into Notepad — the "Calculator... I cannot run programs"
    failure, reproduced by this file's own edit in the same session it
    documents that failure in. Assert the *positive* claim, not just that
    "Notepad" appears — a stale negative claim would still contain it."""
    for prompts in (PERSONA_PROMPTS_WITH_TOOLS, PERSONA_PROMPTS_ONLINE):
        for prompt in prompts.values():
            assert "type_text" in prompt
            assert "Notepad" in prompt
            # The old, now-false claim must not survive beside the new tool.
            assert "nothing can type into it" not in prompt


def test_she_is_told_to_use_relative_paths_not_a_guessed_account_name() -> None:
    """The other half of the same failure: `write_file` was called with
    `C:/Users/Eyaas/Downloads/hi.txt` — his display name, not his real
    Windows account folder (`Dark_Angel`), guessed because nothing told her
    the difference. `write_file`'s own docstring already gives a relative
    example; this is the same guidance stated as an instruction, not just an
    example a model under pressure can drift past."""
    for prompts in (PERSONA_PROMPTS_WITH_TOOLS, PERSONA_PROMPTS_ONLINE):
        for prompt in prompts.values():
            assert "relative path" in prompt
            assert "guessed absolute" in prompt
