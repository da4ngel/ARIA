"""Bedrock: the Converse mapping, the streaming loop, and the errors.

**The mapping is the risky half, not the transport.** Converse is the only
provider format here that moves the system prompt out of the conversation,
turns a tool result into a *user* turn, and rejects two turns in a row with the
same role — three rules that a mapping written by renaming fields would break
silently, producing a `ValidationException` that says nothing useful.

What no test here can establish is that AWS accepts any of it. That needs a
real key against a real endpoint and is recorded as an open line.
"""

from __future__ import annotations

import json

import httpx
import pytest

from sidecar.providers import bedrock
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    ProviderRateLimited,
    ProviderUnavailable,
    Role,
    StreamDelta,
    ToolCall,
)
from sidecar.providers.bedrock import (
    BedrockCredentials,
    BedrockProvider,
    _to_converse,
    _to_tool_config,
)
from sidecar.providers.eventstream import encode_event


@pytest.fixture(autouse=True)
def _no_real_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """Never read the developer's actual Credential Manager."""
    monkeypatch.setattr(bedrock, "get_key", lambda _: None)


def _with_key(monkeypatch: pytest.MonkeyPatch, **kinds: str) -> None:
    from sidecar.providers.credentials import CredentialKey

    mapping = {
        CredentialKey.BEDROCK: kinds.get("bearer"),
        CredentialKey.AWS_ACCESS_KEY_ID: kinds.get("access_key"),
        CredentialKey.AWS_SECRET_ACCESS_KEY: kinds.get("secret_key"),
        CredentialKey.AWS_SESSION_TOKEN: kinds.get("session_token"),
    }
    monkeypatch.setattr(bedrock, "get_key", lambda k: mapping.get(k))


# ── credentials ───────────────────────────────────────────────────────


def test_either_credential_shape_is_usable() -> None:
    assert BedrockCredentials(bearer="ABSK...").usable
    assert BedrockCredentials(access_key="AKIA", secret_key="s").usable


def test_half_an_aws_key_pair_is_not_a_credential() -> None:
    """A signer with no secret produces a signature nobody can verify, and the
    failure arrives as `SignatureDoesNotMatch` on the first turn instead of as
    "no credential stored" in Settings."""
    assert not BedrockCredentials(access_key="AKIA").usable
    assert not BedrockCredentials(secret_key="s").usable
    assert not BedrockCredentials().usable


def test_the_bedrock_api_key_wins_over_the_broader_iam_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """It is scoped to Bedrock alone, so preferring it means the general-purpose
    AWS credential is only used when it is the only one there."""
    _with_key(monkeypatch, bearer="ABSK", access_key="AKIA", secret_key="s")
    assert bedrock.load_credentials().kind == "api_key"


def test_a_bearer_token_is_sent_unsigned(monkeypatch: pytest.MonkeyPatch) -> None:
    _with_key(monkeypatch, bearer="ABSKtoken")
    headers = bedrock.auth_headers("POST", "https://h.amazonaws.com/x", b"{}")
    assert headers["Authorization"] == "Bearer ABSKtoken"


def test_an_access_key_is_signed(monkeypatch: pytest.MonkeyPatch) -> None:
    _with_key(monkeypatch, access_key="AKIDEXAMPLE", secret_key="secret")
    headers = bedrock.auth_headers("POST", "https://h.amazonaws.com/x", b"{}")
    assert headers["Authorization"].startswith("AWS4-HMAC-SHA256 Credential=AKIDEXAMPLE/")
    assert "X-Amz-Date" in headers


def test_no_credential_says_what_to_add_and_where(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ProviderUnavailable) as caught:
        bedrock.auth_headers("GET", "https://h.amazonaws.com/x", b"")
    message = str(caught.value)
    assert "Bedrock API key" in message and "access key" in message
    assert "Settings" in message


# ── the Converse mapping ──────────────────────────────────────────────


def test_the_system_prompt_leaves_the_conversation() -> None:
    """It is a separate top-level field. A mapping that only renamed roles
    would drop it, and the entire persona with it."""
    system, turns = _to_converse(
        [
            ChatMessage(role=Role.SYSTEM, content="You are ARIA."),
            ChatMessage(role=Role.USER, content="hello"),
        ]
    )
    assert system == [{"text": "You are ARIA."}]
    assert turns == [{"role": "user", "content": [{"text": "hello"}]}]


def test_a_tool_result_becomes_a_user_turn() -> None:
    """There is no tool role in Converse."""
    _, turns = _to_converse(
        [
            ChatMessage(role=Role.USER, content="open notepad"),
            ChatMessage(
                role=Role.ASSISTANT,
                content="",
                tool_calls=[ToolCall(id="c1", name="open_app", arguments={"n": "x"})],
            ),
            ChatMessage(role=Role.TOOL, content="Opened.", tool_call_id="c1"),
        ]
    )
    assert turns[1]["role"] == "assistant"
    assert turns[1]["content"] == [
        {"toolUse": {"toolUseId": "c1", "name": "open_app", "input": {"n": "x"}}}
    ]
    assert turns[2] == {
        "role": "user",
        "content": [
            {"toolResult": {"toolUseId": "c1", "content": [{"text": "Opened."}]}}
        ],
    }


def test_consecutive_tool_results_merge_into_one_turn() -> None:
    """**Converse rejects two turns in a row with the same role**, and a tool
    result is a user turn — so two of them adjacent are one turn with two
    blocks, not two turns."""
    _, turns = _to_converse(
        [
            ChatMessage(role=Role.TOOL, content="one", tool_call_id="a"),
            ChatMessage(role=Role.TOOL, content="two", tool_call_id="b"),
        ]
    )
    assert len(turns) == 1
    assert [b["toolResult"]["toolUseId"] for b in turns[0]["content"]] == ["a", "b"]


def test_no_two_adjacent_turns_ever_share_a_role() -> None:
    """The invariant itself, over a full agent-loop exchange: user, a tool
    call, its result, a second tool call, its result, then the answer."""
    _, turns = _to_converse(
        [
            ChatMessage(role=Role.SYSTEM, content="You are ARIA."),
            ChatMessage(role=Role.USER, content="find my cv and read it"),
            ChatMessage(
                role=Role.ASSISTANT,
                content="",
                tool_calls=[ToolCall(id="c1", name="search_files", arguments={})],
            ),
            ChatMessage(role=Role.TOOL, content="Found cv.pdf", tool_call_id="c1"),
            ChatMessage(
                role=Role.ASSISTANT,
                content="",
                tool_calls=[ToolCall(id="c2", name="read_file", arguments={})],
            ),
            ChatMessage(role=Role.TOOL, content="...text...", tool_call_id="c2"),
            ChatMessage(role=Role.ASSISTANT, content="Your CV says..."),
        ]
    )
    assert [t["role"] for t in turns] == [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
        "assistant",
    ]


def test_an_assistant_turn_with_only_a_tool_call_carries_no_empty_text_block() -> None:
    """Converse rejects `{"text": ""}` outright, and an assistant turn that
    only asked for a tool legitimately has no text."""
    _, turns = _to_converse(
        [
            ChatMessage(role=Role.USER, content="x"),
            ChatMessage(
                role=Role.ASSISTANT,
                content="   ",
                tool_calls=[ToolCall(id="c1", name="t", arguments={})],
            ),
        ]
    )
    assert turns[1]["content"] == [
        {"toolUse": {"toolUseId": "c1", "name": "t", "input": {}}}
    ]


def test_an_empty_message_is_dropped_rather_than_sent_as_a_blank_block() -> None:
    _, turns = _to_converse(
        [
            ChatMessage(role=Role.USER, content="real"),
            ChatMessage(role=Role.ASSISTANT, content=""),
        ]
    )
    assert turns == [{"role": "user", "content": [{"text": "real"}]}]


def test_a_tool_result_with_no_output_still_says_something() -> None:
    """An empty `text` in a `toolResult` is the same validation error."""
    _, turns = _to_converse(
        [ChatMessage(role=Role.TOOL, content="", tool_call_id="c1")]
    )
    assert turns[0]["content"][0]["toolResult"]["content"] == [{"text": "(no output)"}]


def test_the_registry_schema_becomes_a_tool_spec() -> None:
    """`registry.schemas()` emits the OpenAI shape; Converse renames all three
    fields and nests the JSON Schema one level deeper."""
    config = _to_tool_config(
        [
            {
                "type": "function",
                "function": {
                    "name": "open_app",
                    "description": "Open an app.",
                    "parameters": {"type": "object", "properties": {"name": {}}},
                },
            }
        ]
    )
    assert config == {
        "tools": [
            {
                "toolSpec": {
                    "name": "open_app",
                    "description": "Open an app.",
                    "inputSchema": {
                        "json": {"type": "object", "properties": {"name": {}}}
                    },
                }
            }
        ]
    }


# ── streaming ─────────────────────────────────────────────────────────


def _event(kind: str, body: dict) -> bytes:
    return encode_event(
        {":message-type": "event", ":event-type": kind},
        json.dumps(body).encode("utf-8"),
    )


def _provider(
    monkeypatch: pytest.MonkeyPatch, handler, *, status: int = 200
) -> BedrockProvider:
    _with_key(monkeypatch, bearer="ABSK")
    provider = BedrockProvider()
    provider._client = httpx.AsyncClient(  # noqa: SLF001
        transport=httpx.MockTransport(handler)
    )
    return provider


async def _collect(
    provider: BedrockProvider, options: GenerationOptions | None = None
) -> list[StreamDelta]:
    return [
        d
        async for d in provider.stream_chat(
            [ChatMessage(role=Role.USER, content="hi")], model="m", options=options
        )
    ]


@pytest.mark.asyncio
async def test_text_deltas_stream_through(monkeypatch: pytest.MonkeyPatch) -> None:
    body = (
        _event("messageStart", {"role": "assistant"})
        + _event("contentBlockDelta", {"delta": {"text": "Can"}})
        + _event("contentBlockDelta", {"delta": {"text": "berra."}})
        + _event("messageStop", {"stopReason": "end_turn"})
    )
    provider = _provider(monkeypatch, lambda _: httpx.Response(200, content=body))
    deltas = await _collect(provider)
    assert "".join(d.text for d in deltas) == "Canberra."
    assert deltas[-1].done


@pytest.mark.asyncio
async def test_reasoning_never_reaches_the_text_channel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`base.py`'s rule, and CLAUDE.md's "always send think: false", on a
    fourth provider: thinking must never reach the UI or the TTS buffer."""
    body = (
        _event(
            "contentBlockDelta",
            {"delta": {"reasoningContent": {"text": "let me think"}}},
        )
        + _event("contentBlockDelta", {"delta": {"text": "Answer."}})
        + _event("messageStop", {"stopReason": "end_turn"})
    )
    provider = _provider(monkeypatch, lambda _: httpx.Response(200, content=body))
    deltas = await _collect(provider)
    assert "".join(d.text for d in deltas) == "Answer."
    assert "let me think" in "".join(d.thinking for d in deltas)


@pytest.mark.asyncio
async def test_a_tool_call_is_emitted_whole_not_in_fragments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bedrock streams the argument JSON a piece at a time. A half-parsed
    argument object is not something the agent loop can act on."""
    body = (
        _event(
            "contentBlockStart",
            {
                "contentBlockIndex": 0,
                "start": {"toolUse": {"toolUseId": "t1", "name": "open_app"}},
            },
        )
        + _event(
            "contentBlockDelta",
            {"contentBlockIndex": 0, "delta": {"toolUse": {"input": '{"na'}}},
        )
        + _event(
            "contentBlockDelta",
            {"contentBlockIndex": 0, "delta": {"toolUse": {"input": 'me":"notepad"}'}}},
        )
        + _event("messageStop", {"stopReason": "tool_use"})
    )
    provider = _provider(monkeypatch, lambda _: httpx.Response(200, content=body))
    deltas = await _collect(provider)
    assert all(not d.tool_calls for d in deltas[:-1])
    (call,) = deltas[-1].tool_calls
    assert call.name == "open_app"
    assert call.arguments == {"name": "notepad"}


@pytest.mark.asyncio
async def test_unparseable_tool_arguments_do_not_take_down_the_turn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = (
        _event(
            "contentBlockStart",
            {"contentBlockIndex": 0, "start": {"toolUse": {"toolUseId": "t1", "name": "t"}}},
        )
        + _event(
            "contentBlockDelta",
            {"contentBlockIndex": 0, "delta": {"toolUse": {"input": "{oh no"}}},
        )
        + _event("messageStop", {"stopReason": "tool_use"})
    )
    provider = _provider(monkeypatch, lambda _: httpx.Response(200, content=body))
    deltas = await _collect(provider)
    assert deltas[-1].tool_calls[0].arguments == {}


@pytest.mark.asyncio
async def test_a_stream_cut_short_still_closes_the_turn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No `messageStop`. Without a closing delta the caller waits forever, and
    from the outside that is indistinguishable from a hung app."""
    body = _event("contentBlockDelta", {"delta": {"text": "half"}})
    provider = _provider(monkeypatch, lambda _: httpx.Response(200, content=body))
    deltas = await _collect(provider)
    assert deltas[-1].done


@pytest.mark.asyncio
async def test_usage_arrives_without_ending_the_turn_a_second_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`metadata` follows `messageStop`, so marking it done would close twice."""
    body = _event("metadata", {"usage": {"inputTokens": 12, "outputTokens": 3}})
    provider = _provider(monkeypatch, lambda _: httpx.Response(200, content=body))
    deltas = await _collect(provider)
    usage = [d for d in deltas if d.prompt_tokens is not None]
    assert usage[0].prompt_tokens == 12
    assert usage[0].completion_tokens == 3
    assert not usage[0].done


# ── the body that is actually sent ────────────────────────────────────


@pytest.mark.asyncio
async def test_max_tokens_is_always_sent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Converse rejects a request without it, and every other provider here
    defaults it server-side — so `GenerationOptions.max_tokens` is usually
    None on the way in and something has to stand in."""
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content))
        return httpx.Response(200, content=_event("messageStop", {}))

    provider = _provider(monkeypatch, handler)
    await _collect(provider)
    assert seen["inferenceConfig"]["maxTokens"] == bedrock.DEFAULT_MAX_TOKENS


@pytest.mark.asyncio
async def test_the_model_id_is_encoded_into_the_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every Bedrock model id ends in `:0`, and a bare colon in a path is not
    what botocore sends — so it is not what the signature would describe."""
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.raw_path.decode()
        return httpx.Response(200, content=_event("messageStop", {}))

    provider = _provider(monkeypatch, handler)
    async for _ in provider.stream_chat(
        [ChatMessage(role=Role.USER, content="x")],
        model="anthropic.claude-sonnet-4-5-20250929-v1:0",
    ):
        pass
    assert "%3A0/converse-stream" in seen["path"]


@pytest.mark.asyncio
async def test_temperature_is_omitted_unless_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The same rule the catalog states for reasoning models: send nothing and
    let the provider default apply."""
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content))
        return httpx.Response(200, content=_event("messageStop", {}))

    provider = _provider(monkeypatch, handler)
    await _collect(provider, options=GenerationOptions())
    assert "temperature" not in seen["inferenceConfig"]


# ── errors, which must say what to do next ────────────────────────────


@pytest.mark.asyncio
async def test_a_model_needing_an_inference_profile_says_so(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """**The most likely first failure and the least obvious.** AWS's own text
    is accurate and unhelpful; the reply has to name the fix."""
    detail = {
        "message": (
            "Invocation of model ID anthropic.claude-sonnet-4-5-20250929-v1:0 with "
            "on-demand throughput isn't supported. Retry your request with the ID "
            "or ARN of an inference profile that contains this model."
        )
    }
    provider = _provider(
        monkeypatch, lambda _: httpx.Response(400, json=detail)
    )
    with pytest.raises(ProviderUnavailable, match="inference profile"):
        await _collect(provider)


@pytest.mark.asyncio
async def test_a_refused_credential_names_the_three_things_to_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Key, region, and model access — the last one catches people out, because
    a Bedrock account can hold a valid key and no granted models at all."""
    provider = _provider(
        monkeypatch, lambda _: httpx.Response(403, json={"message": "denied"})
    )
    with pytest.raises(ProviderUnavailable) as caught:
        await _collect(provider)
    message = str(caught.value)
    assert "region" in message and "Model access" in message


@pytest.mark.asyncio
async def test_throttling_is_a_rate_limit_the_router_can_act_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider(
        monkeypatch, lambda _: httpx.Response(429, json={"message": "slow down"})
    )
    with pytest.raises(ProviderRateLimited):
        await _collect(provider)


@pytest.mark.asyncio
async def test_an_error_delivered_inside_the_stream_is_raised_too(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bedrock reports mid-reply failures as a frame, not a status code — so a
    200 can still be a throttle."""
    body = _event("contentBlockDelta", {"delta": {"text": "part"}}) + encode_event(
        {":message-type": "exception", ":exception-type": "throttlingException"},
        b'{"message":"Too many"}',
    )
    provider = _provider(monkeypatch, lambda _: httpx.Response(200, content=body))
    with pytest.raises(ProviderRateLimited):
        await _collect(provider)


@pytest.mark.asyncio
async def test_a_damaged_frame_is_reported_as_a_damaged_reply(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    blob = bytearray(_event("messageStop", {"stopReason": "end_turn"}))
    blob[-8] ^= 0xFF
    provider = _provider(monkeypatch, lambda _: httpx.Response(200, content=bytes(blob)))
    with pytest.raises(ProviderUnavailable, match="damaged"):
        await _collect(provider)


# ── region ────────────────────────────────────────────────────────────


def test_the_region_reaches_both_hostnames() -> None:
    assert bedrock.runtime_url("eu-west-2") == (
        "https://bedrock-runtime.eu-west-2.amazonaws.com"
    )
    assert bedrock.control_url("eu-west-2") == "https://bedrock.eu-west-2.amazonaws.com"


def test_setting_the_region_changes_what_requests_are_built_against() -> None:
    original = bedrock.current_region()
    try:
        bedrock.set_region("ap-south-1")
        assert bedrock.current_region() == "ap-south-1"
        assert "ap-south-1" in bedrock.runtime_url(bedrock.current_region())
    finally:
        bedrock.set_region(original)


def test_an_empty_region_is_ignored_rather_than_stored() -> None:
    """An unset settings row must not blank out a working region."""
    original = bedrock.current_region()
    bedrock.set_region("")
    assert bedrock.current_region() == original


# ── discovery's classifier, corrected by the live listing ─────────────


@pytest.mark.parametrize(
    ("model_id", "expected"),
    [
        # **The bug the real listing found.** "27b" contains "7b", so a
        # substring match called a 27-billion-parameter model FAST.
        ("google.gemma-3-27b-it", "balanced"),
        ("google.gemma-3-4b-it", "fast"),
        ("meta.llama3-8b-instruct-v1:0", "fast"),
        ("meta.llama3-70b-instruct-v1:0", "smart"),
        ("mistral.mistral-large-3-675b-instruct", "smart"),
        ("us.anthropic.claude-haiku-4-5-20251001-v1:0", "fast"),
        ("us.anthropic.claude-opus-4-5-20251101-v1:0", "smart"),
        ("amazon.nova-micro-v1:0", "fast"),
    ],
)
def test_a_model_is_classified_by_whole_tokens_not_substrings(
    model_id: str, expected: str
) -> None:
    from sidecar.providers.discovery import _bedrock_class

    assert _bedrock_class(model_id, "").value == expected


def test_an_id_is_split_on_every_separator_bedrock_uses() -> None:
    """Dots, dashes and colons all at once, in one id."""
    from sidecar.providers.discovery import _bedrock_tokens

    tokens = _bedrock_tokens("us.anthropic.claude-haiku-4-5-20251001-v1:0")
    assert {"us", "anthropic", "claude", "haiku", "v1", "0"} <= tokens
