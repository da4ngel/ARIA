"""Google Gemini provider (BUILD_SPEC §4, §9.7).

Raw HTTP against `:streamGenerateContent?alt=sse`, for the same reasons as the
OpenAI client — small stable wire format, lean bundle, uniform cancellation.

Gemini's shape differs from OpenAI's in two ways that matter here: the system
prompt is a separate `system_instruction` field rather than a message, and roles
are `user`/`model` rather than `user`/`assistant`.
"""

from __future__ import annotations

import json
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
)
from sidecar.providers.credentials import CredentialKey, get_key

log = structlog.get_logger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
CONNECT_TIMEOUT_S = 10.0
READ_TIMEOUT_S = 300.0


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
        # Accepted and ignored. Phase 3 runs tools on the local model only, and
        # the seam requires every provider to take the argument so the router
        # is free to pick any of them. Ignoring is the documented contract for
        # a provider that cannot call tools — never a hard failure — but a turn
        # that needed a tool and landed here will simply answer without one.
        if tools:
            log.debug("provider.tools_ignored", provider=self.name, count=len(tools))
        opts = options or GenerationOptions()
        body = self._build_body(messages, opts)
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
        """Split system messages out; map assistant -> model."""
        system_parts = [m.content for m in messages if m.role is Role.SYSTEM]
        contents = [
            {
                "role": "model" if m.role is Role.ASSISTANT else "user",
                "parts": [{"text": m.content}],
            }
            for m in messages
            if m.role is not Role.SYSTEM
        ]

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
        for candidate in chunk.get("candidates") or []:
            for part in (candidate.get("content") or {}).get("parts") or []:
                text += part.get("text") or ""

        usage = chunk.get("usageMetadata") or {}
        if not text and not usage:
            return None
        return StreamDelta(
            text=text,
            done=False,  # the stream's end is the end; Gemini sends no [DONE]
            prompt_tokens=usage.get("promptTokenCount"),
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
