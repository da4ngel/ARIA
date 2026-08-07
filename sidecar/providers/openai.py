"""OpenAI provider (BUILD_SPEC §4, §9.7).

Raw HTTP against `/v1/chat/completions` rather than the `openai` SDK: the wire
format is small and stable, this keeps the PyInstaller bundle lean (§2.3), and
it gives the same cancellation semantics as the Ollama client — closing the
stream context aborts the request.

Keys come from Credential Manager via `credentials.py`, never `.env` (§11).
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from typing import Any

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

log = structlog.get_logger(__name__)

BASE_URL = "https://api.openai.com/v1"
CONNECT_TIMEOUT_S = 10.0
READ_TIMEOUT_S = 300.0


def _to_openai_wire(messages: list[ChatMessage]) -> list[dict[str, Any]]:
    """Messages in the shape OpenAI actually accepts.

    Not `to_wire`: OpenAI needs `type: "function"` and an `id` on every tool
    call, and it wants the arguments as a **JSON string** rather than an
    object. Ollama wants the object. One shared mapping cannot satisfy both, so
    this is the OpenAI one.
    """
    wire: list[dict[str, Any]] = []
    for m in messages:
        if m.role is Role.TOOL:
            wire.append(
                {
                    "role": "tool",
                    "content": m.content,
                    "tool_call_id": m.tool_call_id or "",
                }
            )
            continue

        item: dict[str, Any] = {"role": str(m.role), "content": m.content}
        if m.tool_calls:
            item["tool_calls"] = [
                {
                    "id": c.id,
                    "type": "function",
                    "function": {"name": c.name, "arguments": json.dumps(c.arguments)},
                }
                for c in m.tool_calls
            ]
        wire.append(item)
    return wire


def _assemble(partial: dict[int, dict[str, str]]) -> list[ToolCall]:
    """Streamed fragments into finished calls, dropping anything unusable."""
    calls: list[ToolCall] = []
    for index in sorted(partial):
        slot = partial[index]
        if not slot["name"]:
            continue
        try:
            arguments = json.loads(slot["arguments"] or "{}")
        except json.JSONDecodeError:
            log.warning("openai.bad_tool_args", tool=slot["name"], raw=slot["arguments"][:200])
            arguments = {}
        calls.append(
            ToolCall(
                id=slot["id"] or f"c_{uuid.uuid4().hex[:10]}",
                name=slot["name"],
                arguments=arguments if isinstance(arguments, dict) else {},
            )
        )
    return calls


class OpenAIProvider:
    """Implements `LLMProvider` against the OpenAI chat completions API."""

    def __init__(self, base_url: str = BASE_URL) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(READ_TIMEOUT_S, connect=CONNECT_TIMEOUT_S),
        )

    @property
    def name(self) -> str:
        return "openai"

    def _headers(self) -> dict[str, str]:
        key = get_key(CredentialKey.OPENAI)
        if not key:
            raise ProviderUnavailable(
                "No OpenAI API key is stored. Add one in Settings; it is kept in "
                "Windows Credential Manager, not in a file."
            )
        return {"Authorization": f"Bearer {key}"}

    async def available(self) -> bool:
        if not get_key(CredentialKey.OPENAI):
            return False
        try:
            response = await self._client.get(
                "/models", headers=self._headers(), timeout=CONNECT_TIMEOUT_S
            )
        except (httpx.HTTPError, ProviderUnavailable):
            return False
        return response.status_code == 200

    async def warm(self, model: str) -> float:
        """No-op: cloud models have no local load step to pay for."""
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
        body: dict[str, object] = {
            "model": model,
            "messages": _to_openai_wire(messages),
            "stream": True,
        }
        if tools:
            body["tools"] = tools
        if opts.temperature is not None:
            body["temperature"] = opts.temperature
        if opts.max_tokens is not None:
            # gpt-5 and newer reject `max_tokens`; the replacement is accepted
            # by the older models too.
            body["max_completion_tokens"] = opts.max_tokens
        if opts.stop:
            body["stop"] = opts.stop

        headers = self._headers()
        try:
            async with self._client.stream(
                "POST", "/chat/completions", json=body, headers=headers
            ) as response:
                await self._raise_for_stream_status(response)
                # OpenAI streams a tool call in fragments: the name in one
                # frame, the argument JSON a character at a time after it. They
                # are assembled here and emitted whole, because a half-parsed
                # argument object is not something a caller can act on.
                partial: dict[int, dict[str, str]] = {}
                async for line in response.aiter_lines():
                    delta = self._parse_sse(line, partial)
                    if delta is None:
                        continue
                    if delta.done and partial:
                        delta = delta.model_copy(
                            update={"tool_calls": _assemble(partial)}
                        )
                    yield delta
                    if delta.done:
                        return
        except httpx.HTTPError as exc:
            raise ProviderUnavailable(
                f"Could not reach OpenAI ({type(exc).__name__}: {exc}). "
                f"Check your connection, or switch to a local model."
            ) from exc

    async def aclose(self) -> None:
        await self._client.aclose()

    # ── internals ───────────────────────────────────────────────────────

    @staticmethod
    def _parse_sse(
        line: str, partial: dict[int, dict[str, str]] | None = None
    ) -> StreamDelta | None:
        """One `data:` frame into a StreamDelta. Non-data lines are ignored.

        `partial` accumulates streamed tool-call fragments across frames.
        """
        if not line.startswith("data:"):
            return None
        payload = line[5:].strip()
        if not payload:
            return None
        if payload == "[DONE]":
            return StreamDelta(done=True)

        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            log.warning("openai.bad_chunk", line=line[:200])
            return None

        choices = chunk.get("choices") or []
        if not choices:
            return None
        delta_body = choices[0].get("delta") or {}
        text = delta_body.get("content") or ""
        if partial is not None:
            for fragment in delta_body.get("tool_calls") or []:
                slot = partial.setdefault(
                    int(fragment.get("index", 0)), {"id": "", "name": "", "arguments": ""}
                )
                if fragment.get("id"):
                    slot["id"] = fragment["id"]
                function = fragment.get("function") or {}
                if function.get("name"):
                    slot["name"] = function["name"]
                if function.get("arguments"):
                    slot["arguments"] += function["arguments"]
        finished = choices[0].get("finish_reason") is not None
        usage = chunk.get("usage") or {}
        return StreamDelta(
            text=text,
            done=finished,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )

    async def _raise_for_stream_status(self, response: httpx.Response) -> None:
        if response.status_code == 200:
            return
        detail = (await response.aread()).decode(errors="replace")[:300]
        if response.status_code == 429:
            retry = response.headers.get("retry-after")
            raise ProviderRateLimited(
                f"OpenAI rate limit or quota reached: {detail}",
                retry_after_s=float(retry) if retry and retry.isdigit() else None,
            )
        if response.status_code in (401, 403):
            raise ProviderUnavailable(
                f"OpenAI rejected the API key ({response.status_code}). "
                f"Re-enter it in Settings. Server said: {detail}"
            )
        raise ProviderUnavailable(f"OpenAI returned HTTP {response.status_code}: {detail}")
