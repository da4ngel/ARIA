"""Measure a discovered model well enough to let Smart route to it.

`providers/discovery.py` finds what the account can reach; it cannot find out
whether a model is fast, or honest. `CATALOG` only carries numbers somebody
measured, which is why a discovered model sits beside it and Smart will not
touch it. This is the bridge: run the battery, read the output, and write the
survivors into `CATALOG` by hand.

    python scripts/measure_models.py                  # the shortlist
    python scripts/measure_models.py --models gpt-5.6-luna,gemini-3.5-flash
    python scripts/measure_models.py --list           # what is reachable

**Read `fabricated` and `over-refused` together.** A model that invents nothing
because it refuses everything has been broken, not fixed — CLAUDE.md is blunt
about this, and the `qwen3.5:4b` reversal is what it is blunt about.

Nothing here writes to the catalog. Adopting a model is a judgement, and it
should cost somebody reading the transcript.
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval_quality import provider_for, run_probe

from sidecar.core import context as ctx
from sidecar.eval.probes import SUITES, Probe
from sidecar.providers import catalog, discovery
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    ProviderError,
    Role,
)

#: The plausible ones. Deliberately not the `-pro` tier: it is expensive, it is
#: unpriced here, and Smart reaching for it unprompted is exactly the surprise
#: nobody wants on a bill.
SHORTLIST = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gpt-5.4-mini",
    "gpt-5.4-nano",
    "gpt-5.6-luna",
    "o4-mini",
]

#: Turn 1 pays for a cold connection and an empty KV cache, which is not the
#: number the router should rank on. §10: measure turn 2 onwards.
LATENCY_RUNS = 4

LATENCY_PROMPT = "In one sentence, what is a compiler?"


@dataclass
class Measurement:
    model_id: str
    ttft_ms: list[float] = field(default_factory=list)
    fabricated: int = 0
    over_refused: int = 0
    grounded_ok: int = 0
    grounded_total: int = 0
    passed: int = 0
    total: int = 0
    rate_limited: int = 0
    error: str | None = None

    @property
    def median_ttft(self) -> float | None:
        return statistics.median(self.ttft_ms) if self.ttft_ms else None

    @property
    def verdict(self) -> str:
        """A recommendation, not a decision. Somebody still reads the replies."""
        if self.rate_limited > max(2, self.total // 10):
            # Quota exhaustion says nothing about the model. Scoring it as a
            # wrong answer is how gpt-5-mini once came out at 11%.
            return f"RATE LIMITED ({self.rate_limited}/{self.total}) - rerun"
        if self.error:
            return "unreachable"
        if self.grounded_total and self.grounded_ok < self.grounded_total:
            # The control group. A model that fails these is broken, not strict.
            return "REJECT (fails grounded)"
        if self.fabricated > 2:
            return "REJECT (fabricates)"
        if self.over_refused > 2:
            return "REJECT (over-refuses)"
        if self.median_ttft is None:
            return "no latency"
        return "adopt"


async def measure_latency(info: catalog.ModelInfo) -> tuple[list[float], str | None]:
    """TTFT over several turns, ignoring the first."""
    provider = provider_for(info)
    samples: list[float] = []
    error: str | None = None
    messages = [
        *ctx.stable_prefix(info.persona),
        ChatMessage(role=Role.USER, content=LATENCY_PROMPT),
    ]
    try:
        for run in range(LATENCY_RUNS):
            started = time.perf_counter()
            first: float | None = None
            async for delta in provider.stream_chat(
                messages,
                model=info.id,
                # Enough that a reasoning model can finish thinking and still
                # speak; it bills reasoning against the same budget.
                options=GenerationOptions(max_tokens=2000),
            ):
                if delta.text and first is None:
                    first = (time.perf_counter() - started) * 1000
                if delta.done:
                    break
            if first is not None and run > 0:
                samples.append(first)
    except ProviderError as exc:
        error = str(exc)
    finally:
        await provider.aclose()
    return samples, error


async def measure_honesty(info: catalog.ModelInfo, probes: list[Probe]) -> Measurement:
    """The hallucination battery, scored the way `eval_quality` scores it."""
    result = Measurement(model_id=info.id)
    provider = provider_for(info)
    try:
        for probe in probes:
            outcome = await run_probe(provider, info, probe)
            result.total += 1
            result.passed += int(outcome.passed)
            if outcome.rate_limited:
                # Quota exhaustion is not a wrong answer. Scoring it as one is
                # exactly how gpt-5-mini once came out at 11%.
                result.rate_limited += 1
                continue
            # `Result` already knows the difference, and it knows it the same
            # way `eval_quality` reports it — deriving it a second time here is
            # how the two would drift and disagree.
            result.fabricated += int(outcome.fabricated)
            result.over_refused += int(outcome.over_refused)
            if probe.category == "grounded":
                result.grounded_total += 1
                result.grounded_ok += int(outcome.passed)
    except ProviderError as exc:
        result.error = str(exc)
    finally:
        await provider.aclose()
    return result


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", help="Comma-separated ids. Defaults to the shortlist.")
    parser.add_argument("--list", action="store_true", help="Show what discovery can reach.")
    parser.add_argument("--suite", default="hallucination", choices=sorted(SUITES))
    args = parser.parse_args()

    found = await discovery.discover_all()
    catalog.set_discovered(found)
    if args.list:
        for info in sorted(found, key=lambda m: m.id):
            print(f"  {info.id:34} {info.provider:8} {info.klass}")
        return

    wanted = [m.strip() for m in args.models.split(",")] if args.models else SHORTLIST
    probes = SUITES[args.suite]

    print(f"{len(wanted)} models, {len(probes)} probes each, {LATENCY_RUNS - 1} latency samples.\n")

    results: list[Measurement] = []
    for model_id in wanted:
        info = catalog.get(model_id)
        if info is None:
            print(f"  {model_id:30} not reachable with these keys")
            continue

        print(f"  {model_id:30} ", end="", flush=True)
        samples, latency_error = await measure_latency(info)
        measurement = await measure_honesty(info, probes)
        measurement.ttft_ms = samples
        measurement.error = measurement.error or latency_error
        results.append(measurement)

        ttft = f"{measurement.median_ttft:.0f}ms" if measurement.median_ttft else "-"
        print(f"{ttft:>8}  {measurement.passed}/{measurement.total}  {measurement.verdict}")

    print("\n| model | TTFT | battery | fabricated | over-refused | verdict |")
    print("|---|---|---|---|---|---|")
    for r in sorted(results, key=lambda m: m.median_ttft or 1e9):
        ttft = f"{r.median_ttft:.0f}ms" if r.median_ttft else "-"
        print(
            f"| `{r.model_id}` | {ttft} | {r.passed}/{r.total} | "
            f"{r.fabricated} | {r.over_refused} | {r.verdict} |"
        )

    print(
        "\nRead fabricated and over-refused together: a model that invents "
        "nothing because it refuses everything has been broken, not fixed.\n"
        "Nothing was written to the catalog — adopting is a judgement."
    )


if __name__ == "__main__":
    asyncio.run(main())
