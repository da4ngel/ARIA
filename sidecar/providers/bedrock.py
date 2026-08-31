"""Amazon Bedrock, over the Converse API (Eyaas, 2026-08-23).

He has a Bedrock key with $100 of credit on it, which makes this the first
provider here that is neither free nor metered in fractions of a cent — and
the first that cannot borrow OpenAI's wire format. **Three things differ, and
each is why a file exists rather than a subclass:**

- **Authentication is signed, not a bearer token** — unless it is. AWS now
  issues *Bedrock API keys*, which are bearer tokens, alongside ordinary IAM
  access keys, which need SigV4. Both are supported because which one Eyaas
  holds is not knowable from here, and shipping the wrong half means it simply
  does not work. See `providers/sigv4.py`.
- **The response is binary**, not SSE — `application/vnd.amazon.eventstream`.
  See `providers/eventstream.py`.
- **The request shape is its own.** Converse puts the system prompt in a
  separate field, takes content as a list of typed blocks, carries tool results
  on a *user* turn, and rejects two messages in a row with the same role. That
  is a real mapping, not a rename, and `_to_converse` is where it lives.

**Converse rather than `InvokeModel`** because it is the one endpoint that
normalises tool calling across Anthropic, Amazon Nova, Meta and Mistral. The
alternative is a per-vendor body format inside a provider — the shape that
already went wrong once here, when Gemini's tool nesting was assumed to match
OpenAI's.

**Nothing in this file writes a measurement.** Bedrock models are *discovered*
(see `discovery.py`), so they can be picked by hand and Smart mode will not
route to them until something has actually measured them — the property
`catalog.by_class` holds and `test_catalog.py` guards three ways.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import urlsplit

import httpx
import structlog

from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    ProviderRateLimited,
    ProviderUnavailable,
    Role,
    StreamDelta,
    ToolCall,
)
from sidecar.providers.credentials import CredentialKey, get_key
from sidecar.providers.eventstream import EventStreamDecoder, EventStreamError
from sidecar.providers.sigv4 import encode_path_segment, signed_headers

log = structlog.get_logger(__name__)

CONNECT_TIMEOUT_S = 10.0
READ_TIMEOUT_S = 300.0

#: Where Bedrock is enabled by default and where the widest model selection
#: lives. Overridden from Settings — `models.bedrock_region`.
DEFAULT_REGION = "us-east-1"

#: The live region, process-global and set once at startup from Settings.
#:
#: **Global rather than an attribute** because three unrelated things need the
#: same answer — the provider, `discovery.discover_bedrock`, and the RPC that
#: reports it — and a region that disagreed between the picker and the request
#: would grey out models that work, or offer models that 400. The same
#: reasoning `core/router.py` applies to `_bias`.
_region = DEFAULT_REGION


def current_region() -> str:
    return _region


def set_region(value: str) -> None:
    global _region
    if value and value != _region:
        _region = value
        log.info("bedrock.region", region=value)


#: Bedrock rejects a Converse request with no `maxTokens`. Every other provider
#: here defaults it server-side, so `GenerationOptions.max_tokens` is usually
#: `None` on the way in and something has to stand in.
DEFAULT_MAX_TOKENS = 4096


def runtime_url(region: str) -> str:
    return f"https://bedrock-runtime.{region}.amazonaws.com"


def control_url(region: str) -> str:
    """The control plane — listing models, not running them. A different host."""
    return f"https://bedrock.{region}.amazonaws.com"


class BedrockCredentials:
    """Whichever of the two credential shapes is stored.

    Read once per request rather than cached: `credentials.get_key` is a
    Credential Manager syscall, but this is not the turn's hot path — the
    router asks `AvailabilityService`, which caches, and by the time this runs
    a network round-trip is already committed.
    """

    def __init__(
        self,
        *,
        bearer: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        session_token: str | None = None,
    ) -> None:
        self.bearer = bearer
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token

    @property
    def usable(self) -> bool:
        return bool(self.bearer) or bool(self.access_key and self.secret_key)

    @property
    def kind(self) -> str:
        if self.bearer:
            return "api_key"
        return "sigv4" if self.usable else "none"


def load_credentials() -> BedrockCredentials:
    """What is in the Credential Manager, in the order of preference.

    **The bearer token wins when both are present.** It is the newer, narrower
    credential — scoped to Bedrock alone — so preferring it means the broader
    IAM key is used only when it is the only thing available.
    """
    return BedrockCredentials(
        bearer=get_key(CredentialKey.BEDROCK),
        access_key=get_key(CredentialKey.AWS_ACCESS_KEY_ID),
        secret_key=get_key(CredentialKey.AWS_SECRET_ACCESS_KEY),
        session_token=get_key(CredentialKey.AWS_SESSION_TOKEN),
    )


NO_CREDENTIAL_MESSAGE = (
    "No Amazon Bedrock credential is stored. Add either a Bedrock API key, or "
    "an AWS access key and secret, in Settings — they are kept in Windows "
    "Credential Manager, not in a file."
)


def auth_headers(method: str, url: str, body: bytes) -> dict[str, str]:
    """Headers for one Bedrock request, by whichever credential is stored.

    A module function rather than a method because **discovery needs it too**,
    and signing is not something to have two copies of. It takes the finished
    URL and the exact body because that is what a SigV4 signature describes —
    which is why this is not the no-argument `_headers()` every other provider
    here has.
    """
    creds = load_credentials()
    if not creds.usable:
        raise ProviderUnavailable(NO_CREDENTIAL_MESSAGE)

    parts = urlsplit(url)
    base = {
        "Content-Type": "application/json",
        "Host": parts.netloc,
    }
    if creds.bearer:
        return {**base, "Authorization": f"Bearer {creds.bearer}"}

    assert creds.access_key and creds.secret_key  # `usable` guarantees it
    return signed_headers(
        method=method,
        url_path=parts.path,
        query=parts.query,
        headers=base,
        payload=body,
        region=_region,
        access_key=creds.access_key,
        secret_key=creds.secret_key,
        session_token=creds.session_token,
    )


async def fetch_control(path: str) -> dict[str, Any]:
    """One GET against the Bedrock **control plane** — listing, not running.

    A different host from the runtime endpoint, and a different set of IAM
    permissions: a key that can run a model may not be allowed to enumerate
    them, which is why callers treat a 403 here as "reachable" rather than as
    a failure.
    """
    url = control_url(_region) + path
    headers = auth_headers("GET", url, b"")
    headers["Accept"] = "application/json"
    async with httpx.AsyncClient(timeout=CONNECT_TIMEOUT_S) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        body = response.json()
    return body if isinstance(body, dict) else {}


def _text_blocks(content: str) -> list[dict[str, Any]]:
    """A text block, or none at all.

    Converse rejects an empty `text` block outright, and an assistant turn that
    only asked for a tool legitimately has no text — so this returns a list
    rather than a block, and callers splice it.
    """
    return [{"text": content}] if content.strip() else []


def _to_converse(
    messages: list[ChatMessage],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """`(system, messages)` in the shape Converse accepts.

    Four rules, all of them Bedrock's rather than choices made here:

    1. **System prompts leave the conversation.** They are a separate top-level
       field, so a system turn buried mid-list would be silently dropped by any
       mapping that just renamed roles.
    2. **A tool result is a `user` turn.** There is no tool role. It carries a
       `toolResult` block naming the `toolUseId` it answers.
    3. **Roles must alternate.** Two tool results in a row — which the agent
       loop produces routinely — are one user turn with two blocks, not two
       turns. Consecutive same-role turns are merged.
    4. **Content is a list of typed blocks**, and an empty text block is a
       validation error rather than an empty string.
    """
    system: list[dict[str, Any]] = []
    turns: list[dict[str, Any]] = []

    for message in messages:
        if message.role is Role.SYSTEM:
            if message.content.strip():
                system.append({"text": message.content})
            continue

        if message.role is Role.TOOL:
            block = {
                "toolResult": {
                    "toolUseId": message.tool_call_id or "",
                    "content": [{"text": message.content or "(no output)"}],
                }
            }
            turns.append({"role": "user", "content": [block]})
            continue

        if message.role is Role.ASSISTANT:
            content = _text_blocks(message.content)
            content.extend(
                {
                    "toolUse": {
                        "toolUseId": call.id,
                        "name": call.name,
                        "input": call.arguments or {},
                    }
                }
                for call in message.tool_calls
            )
            if content:
                turns.append({"role": "assistant", "content": content})
            continue

        content = _text_blocks(message.content)
        if content:
            turns.append({"role": "user", "content": content})

    return system, _merge_adjacent(turns)


def _merge_adjacent(turns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fold consecutive same-role turns into one. Rule 3 above."""
    merged: list[dict[str, Any]] = []
    for turn in turns:
        if merged and merged[-1]["role"] == turn["role"]:
            merged[-1]["content"].extend(turn["content"])
        else:
            merged.append({"role": turn["role"], "content": list(turn["content"])})
    return merged


def _to_tool_config(tools: list[dict[str, Any]]) -> dict[str, Any]:
    """`registry.schemas()` output as a Converse `toolConfig`.

    The registry emits the OpenAI/Ollama shape, which every other provider here
    either accepts directly or unwraps by one level. Bedrock renames all three
    fields and nests the JSON Schema under `inputSchema.json`.
    """
    specs: list[dict[str, Any]] = []
    for entry in tools:
        function = entry.get("function", entry)
        name = function.get("name")
        if not name:
            continue
        specs.append(
            {
                "toolSpec": {
                    "name": name,
                    "description": function.get("description", ""),
                    "inputSchema": {
                        "json": function.get("parameters")
                        or {"type": "object", "properties": {}}
                    },
                }
            }
        )
    return {"tools": specs}


class _ToolAssembler:
    """Streamed `toolUse` fragments into finished calls.

    Bedrock fragments a tool call the same way OpenAI does — the name arrives
    on `contentBlockStart`, the arguments as JSON *string* pieces across many
    `contentBlockDelta` frames — so they are accumulated and emitted whole. A
    half-parsed argument object is not something the agent loop can act on.

    Keyed by `contentBlockIndex`, because a model may open more than one tool
    block and the fragments interleave.
    """

    def __init__(self) -> None:
        self._slots: dict[int, dict[str, str]] = {}

    def start(self, index: int, call_id: str, name: str) -> None:
        self._slots[index] = {"id": call_id, "name": name, "input": ""}

    def add(self, index: int, fragment: str) -> None:
        if index in self._slots:
            self._slots[index]["input"] += fragment

    def finish(self) -> list[ToolCall]:
        calls: list[ToolCall] = []
        for index in sorted(self._slots):
            slot = self._slots[index]
            if not slot["name"]:
                continue
            try:
                arguments = json.loads(slot["input"] or "{}")
            except json.JSONDecodeError:
                log.warning(
                    "bedrock.bad_tool_args", tool=slot["name"], raw=slot["input"][:200]
                )
                arguments = {}
            calls.append(
                ToolCall(
                    id=slot["id"] or f"c_{uuid.uuid4().hex[:10]}",
                    name=slot["name"],
                    arguments=arguments if isinstance(arguments, dict) else {},
                )
            )
        return calls

    def __bool__(self) -> bool:
        return bool(self._slots)


class BedrockProvider:
    """Implements `LLMProvider` against `bedrock-runtime` ConverseStream."""

    def __init__(self) -> None:
        # **No `base_url`.** The region is in the hostname and it can change
        # from Settings at any time; a client pinned to one host would have to
        # be torn down and rebuilt, leaking connections on every change. Every
        # request passes an absolute URL built from the live region instead.
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(READ_TIMEOUT_S, connect=CONNECT_TIMEOUT_S)
        )

    @property
    def name(self) -> str:
        return "bedrock"

    @property
    def region(self) -> str:
        return current_region()

    # ── protocol ────────────────────────────────────────────────────────

    async def available(self) -> bool:
        """Reachability. Must not raise (`LLMProvider`).

        **403 counts as reachable.** A Bedrock API key scoped to running models
        may legitimately not be allowed to *list* them, and reporting the
        provider as down because of a missing list permission would grey out
        models that answer perfectly well.
        """
        if not load_credentials().usable:
            return False
        try:
            await fetch_control("/foundation-models")
        except httpx.HTTPStatusError as exc:
            return exc.response.status_code == 403
        except (httpx.HTTPError, ProviderUnavailable):
            return False
        return True

    async def warm(self, model: str) -> float:
        """No-op: a cloud model has no local load step to pay for."""
        return 0.0

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        options: GenerationOptions | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[StreamDelta]:
        opts = options or GenerationOptions()
        system, turns = _to_converse(messages)

        inference: dict[str, Any] = {
            # Required by Converse. See DEFAULT_MAX_TOKENS.
            "maxTokens": opts.max_tokens or DEFAULT_MAX_TOKENS,
        }
        if opts.temperature is not None:
            inference["temperature"] = opts.temperature
        if opts.stop:
            inference["stopSequences"] = opts.stop

        body: dict[str, Any] = {"messages": turns, "inferenceConfig": inference}
        if system:
            body["system"] = system
        if tools:
            body["toolConfig"] = _to_tool_config(tools)

        payload = json.dumps(body).encode("utf-8")
        url = (
            f"{runtime_url(current_region())}/model/"
            f"{encode_path_segment(model)}/converse-stream"
        )
        headers = auth_headers("POST", url, payload)
        headers["Accept"] = "application/vnd.amazon.eventstream"

        try:
            async with self._client.stream(
                "POST", url, content=payload, headers=headers
            ) as response:
                await self._raise_for_stream_status(response, model)
                decoder = EventStreamDecoder()
                assembler = _ToolAssembler()
                async for chunk in response.aiter_bytes():
                    for event in decoder.feed(chunk):
                        delta = self._handle(event, assembler)
                        if delta is None:
                            continue
                        yield delta
                        if delta.done:
                            return
                # The stream ended without a `messageStop`. Everything already
                # yielded stands; this only closes the turn so the caller is
                # not left waiting on a `done` that is never coming.
                yield StreamDelta(done=True, tool_calls=assembler.finish())
        except EventStreamError as exc:
            raise ProviderUnavailable(f"Bedrock's reply arrived damaged: {exc}") from exc
        except httpx.HTTPError as exc:
            raise ProviderUnavailable(
                f"Could not reach Bedrock in {current_region()} "
                f"({type(exc).__name__}: {exc}). Check your connection, or "
                f"switch to a local model."
            ) from exc

    def _handle(self, event: Any, assembler: _ToolAssembler) -> StreamDelta | None:
        """One decoded frame into a delta, or None where there is nothing to say."""
        if event.message_type == "exception":
            self._raise_for_event(event)

        kind = event.event_type
        body = event.json()

        if kind == "contentBlockStart":
            use = (body.get("start") or {}).get("toolUse") or {}
            if use:
                assembler.start(
                    int(body.get("contentBlockIndex", 0)),
                    str(use.get("toolUseId") or ""),
                    str(use.get("name") or ""),
                )
            return None

        if kind == "contentBlockDelta":
            delta = body.get("delta") or {}
            if "text" in delta:
                return StreamDelta(text=str(delta["text"]))
            # Reasoning models on Bedrock stream a separate channel, and it
            # must never reach the UI or the TTS buffer — `base.py` and
            # CLAUDE.md's "always send think: false" rule, a fourth time.
            reasoning = delta.get("reasoningContent") or {}
            if "text" in reasoning:
                return StreamDelta(thinking=str(reasoning["text"]))
            use = delta.get("toolUse") or {}
            if "input" in use:
                assembler.add(
                    int(body.get("contentBlockIndex", 0)), str(use.get("input") or "")
                )
            return None

        if kind == "messageStop":
            return StreamDelta(done=True, tool_calls=assembler.finish())

        if kind == "metadata":
            usage = body.get("usage") or {}
            # Not `done`: `messageStop` has already closed the turn on a normal
            # reply, and this frame follows it. Emitting `done` here would end
            # the turn twice.
            return StreamDelta(
                prompt_tokens=usage.get("inputTokens"),
                completion_tokens=usage.get("outputTokens"),
            )

        return None

    def _raise_for_event(self, event: Any) -> None:
        """An error delivered inside the stream rather than as a status code."""
        kind = event.exception_type or "unknown"
        detail = str(event.json().get("message") or "").strip()
        if kind == "throttlingException":
            raise ProviderRateLimited(
                f"Bedrock is throttling this model in {current_region()}. Another "
                f"model will answer, or try again shortly. {detail}".strip()
            )
        raise ProviderUnavailable(
            f"Bedrock stopped mid-reply ({kind}). {detail}".strip()
        )

    async def _raise_for_stream_status(self, response: httpx.Response, model: str) -> None:
        """Turn an HTTP failure into an error that says what to do next."""
        if response.status_code < 400:
            return
        raw = await response.aread()
        detail = raw.decode("utf-8", "replace")[:500]
        try:
            parsed = json.loads(raw)
            detail = str(parsed.get("message") or parsed.get("Message") or detail)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

        status = response.status_code
        if status == 429:
            raise ProviderRateLimited(
                f"Bedrock is throttling requests in {current_region()}: {detail}"
            )
        if status == 403:
            raise ProviderUnavailable(
                f"Bedrock refused the credential for {model} in {current_region()}. "
                f"Check the key is right, that the region matches where it was "
                f"issued, and that model access is granted in the Bedrock "
                f"console under Model access. Server said: {detail}"
            )
        if status == 400 and "inference profile" in detail.lower():
            # **The most likely first failure, and the least obvious.** Newer
            # Anthropic models on Bedrock have no on-demand throughput under
            # their bare id and must be called through a cross-region
            # inference profile, whose id is the same string behind a region
            # prefix. `discovery.py` prefers profile ids for exactly this
            # reason; this catches a hand-typed one.
            raise ProviderUnavailable(
                f"{model} cannot be called directly — it needs a cross-region "
                f"inference profile. Pick the '{current_region().split('-')[0]}.' "
                f"prefixed version of this model in the picker instead. "
                f"Server said: {detail}"
            )
        raise ProviderUnavailable(
            f"Bedrock rejected the request for {model} (HTTP {status}): {detail}"
        )

    async def aclose(self) -> None:
        await self._client.aclose()


__all__ = [
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_REGION",
    "NO_CREDENTIAL_MESSAGE",
    "BedrockCredentials",
    "BedrockProvider",
    "auth_headers",
    "control_url",
    "current_region",
    "fetch_control",
    "load_credentials",
    "runtime_url",
    "set_region",
]
