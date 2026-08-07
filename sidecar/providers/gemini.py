"""Google Gemini provider (BUILD_SPEC §4, §9.7).

Raw HTTP against `:streamGenerateContent?alt=sse`, for the same reasons as the
OpenAI client — small stable wire format, lean bundle, uniform cancellation.

Gemini's shape differs from OpenAI's in two ways that matter here: the system
prompt is a separate `system_instruction` field rather than a message, and roles
are `user`/`model` rather than `user`/`assistant`.
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

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
CONNECT_TIMEOUT_S = 10.0
READ_TIMEOUT_S = 300.0


def _function_call_part(call: ToolCall) -> dict[str, Any]:
    """Replay a tool call in the shape Gemini demands back.

    The signature is not optional: without it the API rejects the follow-up
    with "Function call is missing a thought_signature in functionCall parts",
    and the turn dies rather than degrading.
    """
    part: dict[str, Any] = {"functionCall": {"name": call.name, "args": call.arguments}}
    if call.signature:
        part["thoughtSignature"] = call.signature
    return part


class GeminiProvider:
    """Implements `LLMProvider` against the Gemini generateContent API."""

    def __init__(self, base_url: str = BASE_URL) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(READ_TIMEOUT_S, connect=CONNECT_TIMEOUT_S),
        )

    @property
    def name(self) -> str:
        return "gemini"

    def _headers(self) -> dict[str, str]:
        key = get_key(CredentialKey.GEMINI)
        if not key:
            raise ProviderUnavailable(
                "No Gemini API key is stored. Add one in Settings; it is kept in "
                "Windows Credential Manager, not in a file."
            )
        return {"x-goog-api-key": key}

    async def available(self) -> bool:
        if not get_key(CredentialKey.GEMINI):
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
        body = self._build_body(messages, opts)
        if tools:
            # Gemini nests them differently from everyone else: one `tools`
            # entry holding every declaration, and the OpenAI wrapper object
            # unwrapped down to the function itself.
            body["tools"] = [
                {"functionDeclarations": [t.get("function", t) for t in tools]}
            ]
        url = f"/models/{model}:streamGenerateContent?alt=sse"

        try:
            async with self._client.stream(
                "POST", url, json=body, headers=self._headers()
            ) as response:
                await self._raise_for_stream_status(response)
                async for line in response.aiter_lines():
                    delta = self._parse_sse(line)
                    if delta is None:
                        continue
                    yield delta
                yield StreamDelta(done=True)
        except httpx.HTTPError as exc:
            raise ProviderUnavailable(
                f"Could not reach Gemini ({type(exc).__name__}: {exc}). "
                f"Check your connection, or switch to a local model."
            ) from exc

    async def aclose(self) -> None:
        await self._client.aclose()

    # ── internals ───────────────────────────────────────────────────────

    @staticmethod
    def _build_body(messages: list[ChatMessage], opts: GenerationOptions) -> dict[str, Any]:
        """Split system messages out; map assistant -> model.

        **Tool turns are not text.** Gemini wants a `functionCall` part for the
        request and a `functionResponse` part for the result, and sending them
        as prose is not a formatting nicety — it is why she opened WhatsApp and
        then said "I cannot open WhatsApp directly". Her own tool call arrived
        as an empty model turn, and the result arrived looking like something
        the *user* had said, so she never learned she had done anything.
        """
        system_parts = [m.content for m in messages if m.role is Role.SYSTEM]

        contents: list[dict[str, Any]] = []
        for m in messages:
            if m.role is Role.SYSTEM:
                continue

            if m.role is Role.TOOL:
                contents.append(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": m.name or "tool",
                                    # Gemini requires an object here, not a
                                    # bare string.
                                    "response": {"result": m.content},
                                }
                            }
                        ],
                    }
                )
                continue

            if m.role is Role.ASSISTANT and m.tool_calls:
                contents.append(
                    {
                        "role": "model",
                        "parts": [_function_call_part(c) for c in m.tool_calls],
                    }
                )
                continue

            contents.append(
                {
                    "role": "model" if m.role is Role.ASSISTANT else "user",
                    "parts": [{"text": m.content}],
                }
            )

        body: dict[str, Any] = {"contents": contents}
        if system_parts:
            body["system_instruction"] = {"parts": [{"text": "\n\n".join(system_parts)}]}

        generation: dict[str, Any] = {}
        if opts.temperature is not None:
            generation["temperature"] = opts.temperature
        if opts.max_tokens is not None:
            generation["maxOutputTokens"] = opts.max_tokens
        if opts.stop:
            generation["stopSequences"] = opts.stop
        if generation:
            body["generationConfig"] = generation
        return body

    @staticmethod
    def _parse_sse(line: str) -> StreamDelta | None:
        if not line.startswith("data:"):
            return None
        payload = line[5:].strip()
        if not payload:
            return None

        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            log.warning("gemini.bad_chunk", line=line[:200])
            return None

        text = ""
        calls: list[ToolCall] = []
        for candidate in chunk.get("candidates") or []:
            for part in (candidate.get("content") or {}).get("parts") or []:
                call = part.get("functionCall")
                if call and call.get("name"):
                    calls.append(
                        ToolCall(
                            id=f"c_{uuid.uuid4().hex[:10]}",
                            name=str(call["name"]),
                            arguments=call.get("args") or {},
                            # Required back verbatim on the follow-up turn.
                            signature=part.get("thoughtSignature"),
                        )
                    )
                text += part.get("text") or ""

        usage = chunk.get("usageMetadata") or {}
        if not text and not usage:
            return None
        return StreamDelta(
            text=text,
            done=False,  # the stream's end is the end; Gemini sends no [DONE]
            prompt_tokens=usage.get("promptTokenCount"),
            tool_calls=calls,
            completion_tokens=usage.get("candidatesTokenCount"),
        )

    async def _raise_for_stream_status(self, response: httpx.Response) -> None:
        if response.status_code == 200:
            return
        detail = (await response.aread()).decode(errors="replace")[:300]
        if response.status_code == 429:
            raise ProviderRateLimited(
                f"Gemini rate limit reached — the free tier limits the Pro models "
                f"quickly. Try a Flash model or a local one. Server said: {detail}"
            )
        if response.status_code in (401, 403):
            raise ProviderUnavailable(
                f"Gemini rejected the API key ({response.status_code}). "
                f"Re-enter it in Settings. Server said: {detail}"
            )
        raise ProviderUnavailable(f"Gemini returned HTTP {response.status_code}: {detail}")
