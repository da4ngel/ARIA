"""Ollama provider — the local brain, and the offline fallback (BUILD_SPEC §9.7).

Streams `/api/chat` with `keep_alive=30m` and `num_ctx=8192` per §9 Phase 1.

`think=False` is sent on every request and is not optional: qwen3.x models
stream into a separate `thinking` channel and leave `content` empty until
reasoning ends. Measured on this machine, reasoning-on produced zero content
tokens in 200 tokens / ~6s — see CLAUDE.md.
"""

from __future__ import annotations

import json
import re
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
    StreamDelta,
    ToolCall,
    to_wire,
)

log = structlog.get_logger(__name__)

KEEP_ALIVE = "30m"
CONNECT_TIMEOUT_S = 3.0
READ_TIMEOUT_S = 300.0
WARM_TIMEOUT_S = 120.0

# Reasoning models occasionally emit a literal reasoning tag inside `content`
# even with think=False. Observed once in roughly 16 generations on qwen3.5:4b
# and not reproducible in 36 further attempts — rare, not systematic, and the
# model's doing rather than a parsing error. Stripped anyway: a stray tag in the
# transcript is ugly, and in Phase 2 it would be read aloud.
_REASONING_BLOCK = re.compile(r"<(think|thinking)>.*?</\1>", re.DOTALL | re.IGNORECASE)
_REASONING_TAG = re.compile(r"</?(think|thinking)>", re.IGNORECASE)


def strip_reasoning_artifacts(text: str) -> str:
    """Remove reasoning tags, and any complete block between them, from content."""
    if "<" not in text:  # fast path — the overwhelming majority of deltas
        return text
    return _REASONING_TAG.sub("", _REASONING_BLOCK.sub("", text))


def _tool_calls_of(message: dict[str, Any]) -> list[ToolCall]:
    """Ollama's `message.tool_calls` into the seam's shape.

    Ollama gives no id, so one is minted — the executor needs something to
    match a result back to a request, and an empty string would collide the
    moment a model asks for two things at once.

    Arguments arrive already parsed as an object, but a model that emits a
    JSON *string* instead is common enough to be worth handling rather than
    losing the whole call to a type error.
    """
    calls: list[ToolCall] = []
    for raw in message.get("tool_calls") or []:
        function = raw.get("function") or {}
        name = function.get("name")
        if not name:
            continue
        arguments = function.get("arguments")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                log.warning("ollama.bad_tool_args", tool=name, raw=arguments[:200])
                arguments = {}
        calls.append(
            ToolCall(
                id=f"c_{uuid.uuid4().hex[:10]}",
                name=str(name),
                arguments=arguments if isinstance(arguments, dict) else {},
            )
        )
    return calls


class OllamaProvider:
    """Implements `LLMProvider` against a local Ollama daemon."""

    def __init__(self, base_url: str = "http://127.0.0.1:11434") -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(READ_TIMEOUT_S, connect=CONNECT_TIMEOUT_S),
        )

    @property
    def name(self) -> str:
        return "ollama"

    async def available(self) -> bool:
        """Reachability only — does not check whether any model is loaded."""
        try:
            response = await self._client.get("/api/tags", timeout=CONNECT_TIMEOUT_S)
        except httpx.HTTPError:
            return False
        return response.status_code == 200

    async def list_models(self) -> list[str]:
        try:
            response = await self._client.get("/api/tags", timeout=CONNECT_TIMEOUT_S)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderUnavailable(self._unreachable_message(exc)) from exc
        return [m["name"] for m in response.json().get("models", [])]

    async def warm(self, model: str) -> float:
        """Load `model` with a 1-token request so the user never hits cold start."""
        body = {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "stream": False,
            "think": False,
            "keep_alive": KEEP_ALIVE,
            "options": {"num_predict": 1, "num_ctx": GenerationOptions().num_ctx},
        }
        try:
            response = await self._client.post("/api/chat", json=body, timeout=WARM_TIMEOUT_S)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderUnavailable(self._unreachable_message(exc)) from exc

        total_ns = float(response.json().get("total_duration", 0) or 0)
        took_ms = total_ns / 1e6
        log.info("ollama.warmed", model=model, took_ms=round(took_ms, 1))
        return took_ms

    async def unload(self, model: str) -> None:
        """Evict `model` from VRAM now, instead of after `keep_alive`.

        CLAUDE.md rule 2: one model on the GPU, 6GB ceiling. `keep_alive=30m`
        means a model the user switched away from stays resident for half an
        hour, so selecting the 7B (4.7GB) after the 4B (3.2GB) asks a 6GB card
        to hold both. Measured, that does not fail cleanly — generation slows to
        a stall for minutes as Ollama thrashes, which reads as a hang.

        Best-effort: failing to unload is not worth breaking a turn over, and
        the next request will still work, only slowly.
        """
        try:
            response = await self._client.post(
                "/api/chat",
                json={"model": model, "messages": [], "keep_alive": 0},
                timeout=CONNECT_TIMEOUT_S,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            log.warning("ollama.unload_failed", model=model, error=str(exc))
            return
        log.info("ollama.unloaded", model=model)

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        options: GenerationOptions | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[StreamDelta]:
        opts = options or GenerationOptions()
        body = self._build_body(messages, model=model, options=opts, tools=tools)

        try:
            async with self._client.stream("POST", "/api/chat", json=body) as response:
                await self._raise_for_stream_status(response)
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    delta = self._parse_line(line)
                    if delta is None:
                        continue
                    yield delta
                    if delta.done:
                        return
        except httpx.HTTPError as exc:
            raise ProviderUnavailable(self._unreachable_message(exc)) from exc

    async def aclose(self) -> None:
        await self._client.aclose()

    # ── internals ───────────────────────────────────────────────────────

    def _build_body(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        options: GenerationOptions,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        ollama_options: dict[str, Any] = {"num_ctx": options.num_ctx}
        if options.temperature is not None:
            ollama_options["temperature"] = options.temperature
        if options.max_tokens is not None:
            ollama_options["num_predict"] = options.max_tokens
        if options.stop:
            ollama_options["stop"] = options.stop

        body: dict[str, Any] = {
            "model": model,
            "messages": to_wire(messages),
            "stream": True,
            # Not optional — see the module docstring.
            "think": False,
            "keep_alive": KEEP_ALIVE,
            "options": ollama_options,
        }
        # Omitted entirely when there are none: sending an empty list makes
        # some builds refuse the request outright.
        if tools:
            body["tools"] = tools
        return body

    @staticmethod
    def _parse_line(line: str) -> StreamDelta | None:
        """One NDJSON chunk into a StreamDelta. Unparseable lines are skipped."""
        try:
            chunk = json.loads(line)
        except json.JSONDecodeError:
            log.warning("ollama.bad_chunk", line=line[:200])
            return None

        message = chunk.get("message") or {}
        return StreamDelta(
            text=strip_reasoning_artifacts(message.get("content") or ""),
            thinking=message.get("thinking") or "",
            done=bool(chunk.get("done")),
            tool_calls=_tool_calls_of(message),
            prompt_tokens=chunk.get("prompt_eval_count"),
            completion_tokens=chunk.get("eval_count"),
        )

    async def _raise_for_stream_status(self, response: httpx.Response) -> None:
        if response.status_code == 200:
            return
        detail = (await response.aread()).decode(errors="replace")[:300]
        if response.status_code == 429:
            raise ProviderRateLimited(f"Ollama is rate limiting: {detail}")
        if response.status_code == 404:
            raise ProviderUnavailable(
                f"Ollama does not have that model. Pull it with: ollama pull <model>. "
                f"Server said: {detail}"
            )
        raise ProviderUnavailable(f"Ollama returned HTTP {response.status_code}: {detail}")

    def _unreachable_message(self, exc: httpx.HTTPError) -> str:
        return (
            f"Cannot reach Ollama at {self._base_url} ({type(exc).__name__}: {exc}). "
            f"ARIA tries to start it on its own (see providers/ollama_supervisor.py), "
            f"so this usually means it is not installed — get it from "
            f"https://ollama.com/download — or that something else holds port 11434."
        )
