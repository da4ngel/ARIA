"""OpenAI provider (BUILD_SPEC §4, §9.7).

Raw HTTP against `/v1/chat/completions` rather than the `openai` SDK: the wire
format is small and stable, this keeps the PyInstaller bundle lean (§2.3), and
it gives the same cancellation semantics as the Ollama client — closing the
stream context aborts the request.

Keys come from Credential Manager via `credentials.py`, never `.env` (§11).
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx
import structlog

from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    ProviderRateLimited,
    ProviderUnavailable,
    StreamDelta,
    to_wire,
)
from sidecar.providers.credentials import CredentialKey, get_key

log = structlog.get_logger(__name__)

BASE_URL = "https://api.openai.com/v1"
CONNECT_TIMEOUT_S = 10.0
READ_TIMEOUT_S = 300.0


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
    ) -> AsyncIterator[StreamDelta]:
        opts = options or GenerationOptions()
        body: dict[str, object] = {
            "model": model,
            "messages": to_wire(messages),
            "stream": True,
        }
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
                async for line in response.aiter_lines():
                    delta = self._parse_sse(line)
                    if delta is None:
                        continue
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
    def _parse_sse(line: str) -> StreamDelta | None:
        """One `data:` frame into a StreamDelta. Non-data lines are ignored."""
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
        text = (choices[0].get("delta") or {}).get("content") or ""
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
