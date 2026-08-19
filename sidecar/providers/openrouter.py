"""OpenRouter, and the free models it fronts (Eyaas, 2026-08-19).

One key reaching many vendors, and — the actual request — a supply of **free**
models that changes as new ones appear. The chat endpoint is OpenAI-compatible
down to the SSE framing and the fragmented tool-call deltas, so this subclasses
`OpenAIProvider` rather than restating three hundred lines of parser. What
differs is entirely at the edges: the base URL, two identification headers, and
a rate limit that is a normal operating condition rather than an exception.

**The free tier is 20 requests a minute and 50 a day** (1000/day only if the
account has ever held $10 of credit). That is roughly fifty turns, so free
models are a fallback tier here, not a foundation — and the remaining quota is
worth surfacing, because a cap discovered by hitting it mid-conversation is
the *"on is not the same as working"* failure `settings.online` already exists
to avoid.

**Free endpoints may route to providers that train on what you send.**
OpenRouter has an account-level opt-out and a Zero Data Retention setting, but
those are the user's to set and this code cannot assert they are on. So
`catalog` marks these models `trains_on_data`, and `core/router.py` keeps any
turn carrying the user's own files away from them.
"""

from __future__ import annotations

import time
from typing import Any

import httpx
import structlog

from sidecar.providers.base import ProviderRateLimited, ProviderUnavailable
from sidecar.providers.credentials import CredentialKey, get_key
from sidecar.providers.openai import CONNECT_TIMEOUT_S, READ_TIMEOUT_S, OpenAIProvider

log = structlog.get_logger(__name__)

BASE_URL = "https://openrouter.ai/api/v1"
MODELS_URL = f"{BASE_URL}/models"

#: Sent on every request. OpenRouter uses these to attribute traffic on its
#: public leaderboards; both are optional and neither carries anything about
#: the user. Named honestly rather than left blank.
APP_URL = "https://github.com/da4ngel/ARIA"
APP_TITLE = "ARIA"


class RateLimitState:
    """What the last response said about remaining free quota.

    Read off `X-RateLimit-*` headers rather than counted here: OpenRouter's
    figure accounts for usage from anywhere, and a local counter would drift
    the moment the key is used from another machine or a script.
    """

    def __init__(self) -> None:
        self.limit: int | None = None
        self.remaining: int | None = None
        #: Unix milliseconds, as OpenRouter sends it.
        self.reset_at: int | None = None

    def update(self, headers: httpx.Headers) -> None:
        self.limit = _as_int(headers.get("x-ratelimit-limit")) or self.limit
        remaining = _as_int(headers.get("x-ratelimit-remaining"))
        if remaining is not None:
            self.remaining = remaining
        self.reset_at = _as_int(headers.get("x-ratelimit-reset")) or self.reset_at

    def as_dict(self) -> dict[str, int | None]:
        return {"limit": self.limit, "remaining": self.remaining, "reset_at": self.reset_at}


def _as_int(raw: str | None) -> int | None:
    if raw is None:
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


class OpenRouterProvider(OpenAIProvider):
    """OpenAI's wire format, someone else's models.

    Subclassing rather than copying is the whole point: the streaming loop,
    `_parse_sse`, the fragment accumulator and `_assemble` are all identical
    protocol handling, and two copies of a tool-call assembler is two things to
    fix when one of them is wrong.
    """

    def __init__(self, base_url: str = BASE_URL) -> None:
        super().__init__(base_url)
        #: Shared, so `system.health` and the picker can read it without
        #: making a request of their own.
        self.rate_limit = RateLimitState()

    @property
    def name(self) -> str:
        return "openrouter"

    def _headers(self) -> dict[str, str]:
        key = get_key(CredentialKey.OPENROUTER)
        if not key:
            raise ProviderUnavailable(
                "No OpenRouter API key is stored. Add one in Settings; it is kept "
                "in Windows Credential Manager, not in a file."
            )
        return {
            "Authorization": f"Bearer {key}",
            # Attribution only. Optional per OpenRouter's docs, and it carries
            # nothing about the user or the conversation.
            "HTTP-Referer": APP_URL,
            "X-Title": APP_TITLE,
        }

    async def available(self) -> bool:
        """Reachability, and a free chance to read the quota headers."""
        try:
            headers = self._headers()
        except ProviderUnavailable:
            return False
        try:
            response = await self._client.get(
                "/models", headers=headers, timeout=CONNECT_TIMEOUT_S
            )
        except httpx.HTTPError:
            return False
        self.rate_limit.update(response.headers)
        return response.status_code == 200

    def _raise_for_detail(
        self, status_code: int, detail: str, headers: httpx.Headers | None = None
    ) -> None:
        """OpenRouter's 429 says more than OpenAI's, and it is routine here.

        The free tier rate-limits at 20/minute and 50/day, so this is a normal
        input to routing rather than an incident — `HealthTracker` opens the
        circuit and the router moves to the next model, which is the same path
        Gemini's free tier already exercises. `X-RateLimit-Reset` is Unix
        milliseconds, not the seconds `retry-after` carries.
        """
        if headers is not None:
            self.rate_limit.update(headers)
        if status_code == 429:
            remaining = self.rate_limit.remaining
            spent = "" if remaining is None else f" ({remaining} left)"
            raise ProviderRateLimited(
                f"OpenRouter rate limit reached{spent}. The free tier allows "
                f"20 requests a minute and 50 a day. Server said: {detail}",
                retry_after_s=self._retry_after_s(headers),
            )
        super()._raise_for_detail(status_code, detail, headers)

    def _retry_after_s(self, headers: httpx.Headers | None) -> float | None:
        if headers is None:
            return None
        direct = headers.get("retry-after")
        if direct and direct.isdigit():
            return float(direct)
        # Fall back to the reset stamp, which OpenRouter always sends.
        reset_ms = _as_int(headers.get("x-ratelimit-reset"))
        if reset_ms is None:
            return None
        return max(0.0, reset_ms / 1000 - time.time())

    async def fetch_models(self) -> list[dict[str, Any]]:
        """The raw catalogue OpenRouter offers today.

        Unauthenticated on purpose — `/models` is public, and asking without
        the key means discovery still works before one is stored, so the
        picker can show what *would* be available.
        """
        try:
            async with httpx.AsyncClient(timeout=CONNECT_TIMEOUT_S) as client:
                response = await client.get(MODELS_URL)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderUnavailable(
                f"Could not reach OpenRouter's model list ({type(exc).__name__}: {exc})."
            ) from exc
        payload = response.json()
        data = payload.get("data")
        return list(data) if isinstance(data, list) else []


__all__ = [
    "BASE_URL",
    "MODELS_URL",
    "READ_TIMEOUT_S",
    "OpenRouterProvider",
    "RateLimitState",
]
