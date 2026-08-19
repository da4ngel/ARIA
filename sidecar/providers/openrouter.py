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
from datetime import date
from typing import Any

import httpx
import structlog

from sidecar.providers import catalog
from sidecar.providers.base import (
    ProviderQuotaExhausted,
    ProviderRateLimited,
    ProviderUnavailable,
)
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


#: The free tier's daily allowance, from OpenRouter's published limits. Not
#: discoverable from the API (see `RateLimitState`), so it is written down here
#: with the date it was true — the same treatment every other unmeasurable
#: constant in this project gets.
FREE_REQUESTS_PER_DAY = 50


class RateLimitState:
    """How much of the free daily allowance ARIA has spent, and it is a count.

    **The first version read `X-RateLimit-*` headers and would have displayed
    nothing forever.** Checked live on 2026-08-19: OpenRouter returns no
    rate-limit headers on a successful chat completion — the only `x-` header
    is `x-generation-id` — and `GET /api/v1/key` reports usage in *credits*,
    which is `0` for every free model by definition. So the remaining free
    *request* count is not exposed by the API at all.

    Counting locally is therefore the only option, and the honest framing is
    "what this machine has spent", never "what is left on the key": the same
    key used from a script or another machine is invisible here. The header
    reader is kept because OpenRouter's docs say a 429 carries them, and a real
    figure should win over an inferred one the moment one arrives.
    """

    def __init__(self, limit: int = FREE_REQUESTS_PER_DAY) -> None:
        self.limit: int | None = limit
        #: Only ever set from a response that actually stated it.
        self.remaining: int | None = None
        #: Unix milliseconds, as OpenRouter sends it.
        self.reset_at: int | None = None
        #: Requests this process has made today, and the day they count against.
        self.spent_today = 0
        self._day = date.today()

    def record_request(self) -> None:
        today = date.today()
        if today != self._day:
            self._day = today
            self.spent_today = 0
        self.spent_today += 1

    def update(self, headers: httpx.Headers) -> None:
        self.limit = _as_int(headers.get("x-ratelimit-limit")) or self.limit
        remaining = _as_int(headers.get("x-ratelimit-remaining"))
        if remaining is not None:
            self.remaining = remaining
        self.reset_at = _as_int(headers.get("x-ratelimit-reset")) or self.reset_at

    def as_dict(self) -> dict[str, int | None | bool]:
        # `remaining` prefers a stated figure and falls back to arithmetic on
        # the local count. `counted_here` is what stops that being a lie: a
        # number the UI presents as authoritative when it is an inference is
        # worse than no number.
        inferred = None if self.limit is None else max(0, self.limit - self.spent_today)
        return {
            "limit": self.limit,
            "remaining": self.remaining if self.remaining is not None else inferred,
            "reset_at": self.reset_at,
            "spent_today": self.spent_today,
            "counted_here": self.remaining is None,
        }


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

    def _extra_body(self, model: str) -> dict[str, object]:
        """Turn reasoning off where the endpoint allows it, and count the call.

        This is CLAUDE.md's *"always send `think: false` to Ollama"* rule
        reaching a second provider, and for the identical reason: a reasoning
        model streams into a separate channel and leaves `content` empty until
        it is done, so the tokens are spent before a word is written. Measured
        here on 2026-08-19 — `nvidia/nemotron-3-super-120b-a12b:free` answers
        "Canberra" with **0 characters of reasoning** once this is sent, and
        several free models reason by default without it.

        **It cannot be sent unconditionally.** `openai/gpt-oss-20b:free`
        returns *HTTP 400 "Reasoning is mandatory for this endpoint and cannot
        be disabled"* — a hard failure of the whole turn, not a warning. So the
        catalog is consulted, and an id nobody knows about **fails open**: the
        cost of not sending it is some wasted tokens, and the cost of sending
        it wrongly is a dead turn.
        """
        # `stream_chat` is inherited whole, so this hook is also the one
        # place every outgoing request passes through — which is where the
        # local request count has to live. See `RateLimitState`.
        self.rate_limit.record_request()
        info = catalog.get(model)
        if info is None or info.reasoning_mandatory:
            return {}
        return {"reasoning": {"enabled": False}}

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
            # **Two different 429s, and telling the user the wrong one is
            # actively misleading.** The account-level cap is 20/minute and
            # 50/day; but a *single free model* is also throttled upstream by
            # whichever provider is serving it, independently of the account,
            # and that one is transient and specific to that model. Both were
            # seen within a minute of the first live test.
            if "upstream" in detail or "temporarily rate-limited" in detail:
                raise ProviderRateLimited(
                    "This free model is busy upstream right now — the limit is the "
                    "provider serving it, not your account. Another model will "
                    "answer, or try again shortly.",
                    retry_after_s=self._retry_after_s(headers),
                )
            remaining = self.rate_limit.remaining
            spent = "" if remaining is None else f" ({remaining} left)"
            # **A distinct exception, because the right response is different.**
            # The daily cap is account-wide: no other free model will answer
            # either, so a caller that steps to the next candidate is asking the
            # same question again. `limit_source` says which of the two this is.
            if "free-models-per-day" in detail or "free_tier_daily" in detail:
                raise ProviderQuotaExhausted(
                    f"OpenRouter's free allowance for today is used up{spent} "
                    f"(50 a day). It resets at 00:00 UTC; $10 of credit raises "
                    f"it to 1000/day. Paid models and local ones are unaffected.",
                    retry_after_s=self._retry_after_s(headers),
                )
            raise ProviderRateLimited(
                f"OpenRouter's free-tier limit for this key is reached{spent}: "
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
