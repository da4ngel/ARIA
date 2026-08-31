"""What a turn cost, estimated — and the word *estimated* is load-bearing.

`catalog.Cost` is a band (`$`/`$$`/`$$$`) chosen by hand to order the picker. It
was never a number and must not start being read as one. This module is the
separate thing: real per-token rates, so `prompt_tokens * rate` produces a
figure.

**Three rules, and the first two are why this file is not just a dict.**

1. **An unknown model is `None`, never `0.0`.** A model nobody has priced
   costing "nothing" is a lie that compounds silently across a month; a model
   that reports no price is a fact the dashboard can show. This is
   `ModelInfo.tool_score`'s rule and `Cost.UNKNOWN`'s rule, restated a third
   time because it keeps mattering.
2. **The rates carry the date they were true.** They are not discoverable at
   runtime for most providers and they *will* drift — the same treatment
   `openrouter.FREE_REQUESTS_PER_DAY = 50` gets, and for the same reason.
3. **Local models are a genuine `0.0`**, not an unknown. Ollama bills nothing;
   the electricity is real and is not what anyone means by this number.

The figure this produces is an estimate from a table that goes stale, over token
counts that are real. Every surface that shows it says "estimated", never
"spent" — presenting an inference as billing is the `settings.online` "on is not
the same as working" failure in a more expensive costume.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

#: When the rates below were last checked against the providers' own pricing
#: pages. Shown in the UI beside every figure derived from them.
PRICES_AS_OF = date(2026, 8, 24)


@dataclass(frozen=True)
class Rate:
    """US dollars per million tokens."""

    input_per_1m: float
    output_per_1m: float

    def cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        return (
            prompt_tokens * self.input_per_1m + completion_tokens * self.output_per_1m
        ) / 1_000_000


#: Anything that runs on this machine. Zero because no invoice exists, and it
#: is a real zero rather than an absence — a local turn is not "unpriced".
LOCAL = Rate(0.0, 0.0)

#: Per-model rates, in US dollars per million tokens.
#:
#: **Ships mostly empty on purpose.** Filling it with plausible-looking numbers
#: from memory is exactly the fabrication every honesty probe in this project
#: exists to catch, and a wrong rate is worse than a blank one because it looks
#: like an answer. Populate it from each provider's pricing page — or run
#: `scripts/refresh_pricing.py`, which reads OpenRouter's live listing, where
#: the prices are stated by the API rather than remembered.
#:
#: Keys are catalog model ids. A model missing from here is counted as
#: *unpriced* and reported as such.
RATES: dict[str, Rate] = {
    # ── free tiers, stated by the provider ──────────────────────────
    # OpenRouter's `:free` endpoints are free on both sides of the meter, which
    # `discovery._openrouter_is_free` already asserts from the live payload.
    # They are added dynamically by `for_model` rather than listed here.
}


def for_model(model_id: str, *, local: bool = False) -> Rate | None:
    """The rate for a model, or None when nobody has priced it.

    `local` comes from `ModelInfo.local` rather than being guessed from the id,
    because an Ollama tag looks like any other string.
    """
    if local:
        return LOCAL
    # OpenRouter's free endpoints are free on both sides — read off the id,
    # which is the same suffix `discovery.parse_openrouter` filters on.
    if model_id.endswith(":free"):
        return LOCAL
    return RATES.get(model_id)


def estimate(
    model_id: str, prompt_tokens: int | None, completion_tokens: int | None, *, local: bool = False
) -> float | None:
    """Cost for one turn, or None if it cannot be known.

    **Missing token counts are `None`, not zero.** OpenRouter reports no usage
    at all, so a turn through it has real tokens that nobody counted; calling
    that $0 would quietly understate a month.
    """
    if prompt_tokens is None and completion_tokens is None:
        return None
    rate = for_model(model_id, local=local)
    if rate is None:
        return None
    return rate.cost(prompt_tokens or 0, completion_tokens or 0)


def is_priced(model_id: str, *, local: bool = False) -> bool:
    return for_model(model_id, local=local) is not None


__all__ = ["LOCAL", "PRICES_AS_OF", "RATES", "Rate", "estimate", "for_model", "is_priced"]
