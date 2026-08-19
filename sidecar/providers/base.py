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


class ToolCall(BaseModel):
    """A model asking for a tool to be run.

    `id` is the provider's handle for the call where it gives one, so a result
    can be matched back to the request. Ollama does not, so it is minted here
    and the field is never empty.
    """

    id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    #: Opaque token some providers hand back with a call and require echoed
    #: verbatim when the call is replayed. Gemini's `thoughtSignature` is one:
    #: without it the API refuses the follow-up outright. Meaningless to
    #: everyone else, so it is carried and never inspected.
    signature: str | None = None


class ChatMessage(BaseModel):
    """One turn on the wire to a provider."""

    role: Role
    content: str
    # Set on an assistant turn that asked for tools, so the exchange can be
    # replayed back to the model with its own request intact.
    tool_calls: list[ToolCall] = Field(default_factory=list)
    # Set on a Role.TOOL turn, matching the call it answers.
    tool_call_id: str | None = None
    # The tool's name on a Role.TOOL turn. Some providers require it.
    name: str | None = None


class StreamDelta(BaseModel):
    """One chunk of a streaming response.

    `text` carries *content only*. Reasoning models stream a separate thinking
    channel which must never reach the UI or the TTS buffer — see
    `thinking` below and CLAUDE.md.
    """

    text: str = ""
    thinking: str = ""
    done: bool = False

    # Tools the model wants run. **Not streamed token by token** — providers
    # emit these whole, on one delta, because a half-parsed argument object is
    # not something a caller can act on.
    tool_calls: list[ToolCall] = Field(default_factory=list)

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


class ProviderQuotaExhausted(ProviderRateLimited):
    """The **account's** allowance is gone, not this model's.

    A 429 usually means "this endpoint is busy, try another" — and every
    caller that treats it that way is right to. This one means the opposite:
    no model from this provider will answer until the quota resets, so moving
    to the next candidate is not a workaround, it is the same request again
    with a different name on it.

    Found live on OpenRouter, where `limit_source: openrouter_free_tier_daily`
    says exactly which of the two it is. Without the distinction
    `AdoptionService` stepped through three candidates an hour confirming a cap
    it had already been told about.
    """


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
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[StreamDelta]:
        """Stream a completion.

        Cancellation is cooperative: cancelling the consuming task must abort
        the underlying request promptly (Phase 1 gate: within 200ms).

        `tools` is the JSON-schema list from `tools.registry.schemas()`. A
        provider that cannot call tools ignores it — it must never be a hard
        failure, because the router may pick that provider for other reasons.
        """
        ...

    async def aclose(self) -> None:
        """Release connections."""
        ...


def to_wire(messages: list[ChatMessage]) -> list[dict[str, Any]]:
    """Common `[{role, content}]` shape most chat APIs accept.

    Tool fields are only included when set, so a provider that knows nothing
    about tools sees exactly the payload it saw before.
    """
    wire: list[dict[str, Any]] = []
    for message in messages:
        item: dict[str, Any] = {"role": str(message.role), "content": message.content}
        if message.tool_calls:
            item["tool_calls"] = [
                {"function": {"name": c.name, "arguments": c.arguments}}
                for c in message.tool_calls
            ]
        if message.tool_call_id is not None:
            item["tool_call_id"] = message.tool_call_id
        if message.name is not None:
            item["name"] = message.name
        wire.append(item)
    return wire
