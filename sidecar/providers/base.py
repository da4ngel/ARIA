"""The interface every LLM backend implements.

Phase 1 only ships the Ollama implementation, but the seam exists now on
purpose: BUILD_SPEC §9.7 routes between local, OpenAI and Gemini from Phase 6,
and CLAUDE.md rule 10 forbids refactoring `ollama.py` to fit an abstraction that
did not exist when it was written.

Nothing here knows about routing. Picking a provider is `core/router.py`'s job.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class Role(StrEnum):
    """Matches the `role` CHECK constraint on the messages table (§7.3)."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """One turn on the wire to a provider."""

    role: Role
    content: str


class StreamDelta(BaseModel):
    """One chunk of a streaming response.

    `text` carries *content only*. Reasoning models stream a separate thinking
    channel which must never reach the UI or the TTS buffer — see
    `thinking` below and CLAUDE.md.
    """

    text: str = ""
    thinking: str = ""
    done: bool = False

    # Populated on the final delta where the provider reports them.
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class GenerationOptions(BaseModel):
    """Provider-neutral knobs. Providers map these onto their own APIs."""

    # §2.1: never raise this. Longer context is handled by memory retrieval.
    num_ctx: int = 8192
    temperature: float | None = None
    max_tokens: int | None = None
    stop: list[str] = Field(default_factory=list)


class ProviderError(RuntimeError):
    """Base class for provider failures the router can act on."""


class ProviderUnavailable(ProviderError):
    """The backend could not be reached — offline, not running, DNS, refused.

    Distinct from a request that reached the provider and failed: the router
    treats this as "take it out of the candidate pool", not "retry".
    """


class ProviderRateLimited(ProviderError):
    """HTTP 429. Measured on a free-tier Gemini key, so this is a normal
    routing input rather than an exceptional case (BUILD_SPEC §9.7 stage 7)."""

    def __init__(self, message: str, retry_after_s: float | None = None) -> None:
        super().__init__(message)
        self.retry_after_s = retry_after_s


@runtime_checkable
class LLMProvider(Protocol):
    """What `core/conversation.py` and, later, `core/router.py` depend on."""

    @property
    def name(self) -> str:
        """Stable identifier used in logs, the `route` column, and the UI."""
        ...

    async def available(self) -> bool:
        """Cheap reachability check. Must not raise."""
        ...

    async def warm(self, model: str) -> float:
        """Load the model and return how long it took, in ms.

        Cold start is 8-15s (§12); the user must never pay it mid-conversation.
        """
        ...

    def stream_chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        options: GenerationOptions | None = None,
    ) -> AsyncIterator[StreamDelta]:
        """Stream a completion.

        Cancellation is cooperative: cancelling the consuming task must abort
        the underlying request promptly (Phase 1 gate: within 200ms).
        """
        ...

    async def aclose(self) -> None:
        """Release connections."""
        ...


def to_wire(messages: list[ChatMessage]) -> list[dict[str, Any]]:
    """Common `[{role, content}]` shape most chat APIs accept."""
    return [{"role": str(m.role), "content": m.content} for m in messages]
