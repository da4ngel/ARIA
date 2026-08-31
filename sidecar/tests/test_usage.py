"""Usage accounting, pricing, and reading an action back in plain language.

The rule under test throughout: **unknown is not zero.** A model nobody has
priced, and a turn nobody counted tokens for, both have to survive all the way
to the display as themselves — a total that quietly absorbs them is a total that
is wrong in the expensive direction.
"""

from __future__ import annotations

from sidecar.memory.db import Database
from sidecar.memory.routing_log import RoutingLog, RoutingRecord
from sidecar.providers import pricing
from sidecar.providers.base import ChatMessage, Role
from sidecar.tools.introspect import describe

# ── pricing ───────────────────────────────────────────────────────────


def test_a_model_nobody_has_priced_is_none_not_zero() -> None:
    """`Cost.UNKNOWN`'s rule and `ModelInfo.tool_score`'s rule, a third time.

    Zero here would understate a month silently; None can be counted and shown.
    """
    assert pricing.for_model("some-model-nobody-priced") is None
    assert pricing.estimate("some-model-nobody-priced", 1000, 500) is None
    assert not pricing.is_priced("some-model-nobody-priced")


def test_a_local_model_is_a_real_zero() -> None:
    """Ollama bills nothing. That is a price, not an absence."""
    assert pricing.for_model("qwen2.5:7b", local=True) == pricing.LOCAL
    assert pricing.estimate("qwen2.5:7b", 5000, 900, local=True) == 0.0
    assert pricing.is_priced("qwen2.5:7b", local=True)


def test_an_openrouter_free_endpoint_is_free_on_both_sides() -> None:
    """Read off the suffix `discovery.parse_openrouter` already filters on."""
    assert pricing.estimate("meta/llama-3-8b:free", 100, 100) == 0.0


def test_a_priced_model_multiplies_out_per_million() -> None:
    rate = pricing.Rate(input_per_1m=3.0, output_per_1m=15.0)
    # 1M in, 1M out.
    assert rate.cost(1_000_000, 1_000_000) == 18.0
    assert round(rate.cost(1_000, 500), 6) == round((3.0 + 7.5) / 1000, 6)


def test_missing_token_counts_are_not_a_free_turn() -> None:
    """OpenRouter reports no usage at all. Those turns cost real money."""
    assert pricing.estimate("qwen2.5:7b", None, None, local=True) is None


def test_the_rates_carry_the_date_they_were_true() -> None:
    """They are not discoverable at runtime and they will drift — the same
    treatment `openrouter.FREE_REQUESTS_PER_DAY` gets."""
    assert pricing.PRICES_AS_OF.year >= 2026


# ── the aggregate ─────────────────────────────────────────────────────


def _record(
    model: str, *, local: bool, prompt: int | None, completion: int | None
) -> RoutingRecord:
    return RoutingRecord(
        model=model,
        provider="ollama" if local else "openai",
        local=local,
        stage="quality",
        detail="",
        bias="quality",
        prompt_tokens=prompt,
        completion_tokens=completion,
    )


async def test_tokens_are_summed_per_model(database: Database) -> None:
    log = RoutingLog(database)
    await log.record(_record("qwen2.5:7b", local=True, prompt=100, completion=20))
    await log.record(_record("qwen2.5:7b", local=True, prompt=50, completion=10))
    await log.record(_record("gpt-5.4-nano", local=False, prompt=900, completion=300))

    report = await log.usage_since("2000-01-01T00:00:00Z")
    by_model = {row["model"]: row for row in report["models"]}
    assert report["turns"] == 3
    assert by_model["qwen2.5:7b"]["prompt_tokens"] == 150
    assert by_model["qwen2.5:7b"]["completion_tokens"] == 30
    assert by_model["gpt-5.4-nano"]["turns"] == 1


async def test_a_turn_nobody_counted_is_reported_separately(database: Database) -> None:
    """**Not folded into the token sum as zero.** OpenRouter sends no usage, and
    a dashboard that cannot say so reports a total it knows is short."""
    log = RoutingLog(database)
    await log.record(_record("some/free-model", local=False, prompt=None, completion=None))
    await log.record(_record("some/free-model", local=False, prompt=10, completion=5))

    report = await log.usage_since("2000-01-01T00:00:00Z")
    row = report["models"][0]
    assert row["turns"] == 2
    assert row["uncounted"] == 1
    assert row["prompt_tokens"] == 10


async def test_rows_before_the_window_are_excluded(database: Database) -> None:
    log = RoutingLog(database)
    await log.record(_record("qwen2.5:7b", local=True, prompt=1, completion=1))
    assert (await log.usage_since("2099-01-01T00:00:00Z"))["turns"] == 0


async def test_recent_turns_come_back_newest_first(database: Database) -> None:
    log = RoutingLog(database)
    await log.record(_record("first", local=True, prompt=1, completion=1))
    await log.record(_record("second", local=True, prompt=1, completion=1))
    assert [r["model"] for r in await log.recent_turns(5)] == ["second", "first"]


# ── explaining an action ──────────────────────────────────────────────


def test_nothing_recorded_produces_nothing_rather_than_a_guess() -> None:
    """"I have no record of that" is a true answer; an invented one is not."""
    assert describe(None, None) == ""


def test_the_router_stage_is_translated_into_words() -> None:
    account = describe(
        None,
        {
            "model": "qwen2.5:7b",
            "local": 1,
            "stage": "private",
            "detail": "",
            "latency_ms": 2400,
            "prompt_tokens": 800,
            "completion_tokens": 120,
        },
    )
    assert "qwen2.5:7b" in account
    assert "on this machine" in account
    assert "looked private" in account
    assert "2.4s" in account
    assert "800 in, 120 out" in account


def test_an_unknown_stage_falls_back_to_the_detail_the_router_wrote() -> None:
    """`stage`/`detail` are the router's own RouteReason, so a row explains
    itself even when this module has not learned the vocabulary."""
    account = describe(None, {"model": "m", "local": 0, "stage": "brand-new-stage",
                              "detail": "because of a rule added later"})
    assert "because of a rule added later" in account


def test_a_tool_call_names_what_ran_and_who_approved_it() -> None:
    account = describe(
        {
            "tool": "write_file",
            "args": '{"path": "downloads/notes.txt", "content": "hello"}',
            "ok": 1,
            "error": None,
            "duration_ms": 12,
            "approved": 1,
            "approved_by": "user",
        },
        None,
    )
    assert "write_file" in account
    assert "path=downloads/notes.txt" in account
    assert "you approved it" in account
    assert "it worked" in account


def test_the_three_ways_a_call_can_be_approved_read_differently() -> None:
    """`approved_by` was added precisely so an audit trail could tell them
    apart; an explanation that flattens them wastes that."""

    def _by(value: str | None, approved: int | None = 1) -> str:
        return describe(
            {"tool": "t", "args": "{}", "ok": 1, "approved": approved, "approved_by": value},
            None,
        )

    assert "you approved it" in _by("user")
    assert "folder is trusted" in _by("trust")
    assert "Full access" in _by("full_access")
    assert "needed no confirmation" in _by(None, approved=None)
    assert "you denied it" in _by("user", approved=0)


def test_a_failed_call_says_so_with_its_error() -> None:
    account = describe(
        {"tool": "open_app", "args": "{}", "ok": 0, "error": "not_found", "approved": None},
        None,
    )
    assert "it failed (not_found)" in account


def test_a_long_argument_is_clipped_rather_than_read_back_whole() -> None:
    """`type_text`'s argument is an entire essay."""
    account = describe(
        {"tool": "type_text", "args": '{"text": "%s"}' % ("word " * 500), "ok": 1,
         "approved": 1, "approved_by": "user"},
        None,
    )
    assert len(account) < 600


# ── where the tokens come from, which is three different shapes ───────
#
# Every routing row written before 2026-08-25 recorded NULL tokens, and it took
# three separate faults to manage it — one per provider shape. These pin all
# three, because the failure is silent: a NULL column looks like a quiet turn.


def test_an_empty_choices_chunk_carrying_usage_is_not_discarded() -> None:
    """**OpenAI reports usage in a frame with no `choices` at all.**

    `_parse_sse` returned None for anything without choices, so the one frame
    that carries the cost was thrown away.
    """
    from sidecar.providers.openai import OpenAIProvider

    frame = (
        'data: {"id":"x","object":"chat.completion.chunk","choices":[],'
        '"usage":{"prompt_tokens":8,"completion_tokens":4}}'
    )
    delta = OpenAIProvider._parse_sse(frame)  # noqa: SLF001
    assert delta is not None
    assert delta.prompt_tokens == 8
    assert delta.completion_tokens == 4


def test_a_chunk_with_neither_choices_nor_usage_is_still_nothing() -> None:
    from sidecar.providers.openai import OpenAIProvider

    assert OpenAIProvider._parse_sse('data: {"choices":[]}') is None  # noqa: SLF001


async def test_openai_holds_back_done_until_the_usage_frame_has_arrived() -> None:
    """**The ordering that defeated the first two fixes.**

    OpenAI sends `finish_reason`, *then* usage, *then* `[DONE]`. Returning on
    the first of those never saw the usage; and once that was fixed, `[DONE]`
    produced a second done delta that overwrote the merged one.
    """
    import httpx

    from sidecar.providers.credentials import CredentialKey
    from sidecar.providers.openai import OpenAIProvider

    body = (
        'data: {"choices":[{"index":0,"delta":{"content":"OK"},"finish_reason":null}]}\n\n'
        'data: {"choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}\n\n'
        'data: {"choices":[],"usage":{"prompt_tokens":8,"completion_tokens":4}}\n\n'
        "data: [DONE]\n\n"
    )

    provider = OpenAIProvider()
    provider._client = httpx.AsyncClient(  # noqa: SLF001
        base_url="https://api.openai.test/v1",
        transport=httpx.MockTransport(lambda _: httpx.Response(200, text=body)),
    )
    # `monkeypatch` is not available in an async test without the fixture, and
    # the provider reads its key at request time, so the module attribute is
    # what has to move.
    import sidecar.providers.openai as openai_module

    original = openai_module.get_key  # type: ignore[attr-defined]
    setattr(  # noqa: B010 — mypy will not allow a direct assign to an import
        openai_module,
        "get_key",
        lambda key: "sk-test" if key is CredentialKey.OPENAI else None,
    )
    try:
        deltas = [
            d
            async for d in provider.stream_chat(
                [ChatMessage(role=Role.USER, content="hi")], model="gpt-test"
            )
        ]
    finally:
        setattr(openai_module, "get_key", original)  # noqa: B010
        await provider.aclose()

    assert "".join(d.text for d in deltas) == "OK"
    # The done delta is last, and it is the one carrying the cost.
    assert deltas[-1].done
    assert deltas[-1].prompt_tokens == 8
    assert deltas[-1].completion_tokens == 4


def test_gemini_never_sets_done_so_usage_cannot_be_collected_only_on_done() -> None:
    """Gemini's stream ends by ending — `done` is hard-coded False.

    A collector that only reads the done delta records nothing for it, which
    is precisely what happened.
    """
    import inspect

    from sidecar.providers import gemini

    source = inspect.getsource(gemini.GeminiProvider._parse_sse)  # noqa: SLF001
    assert "done=False" in source
