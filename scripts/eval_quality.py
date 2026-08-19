"""Answer-quality and hallucination battery. Run it, change something, run again.

Phase 1 shipped an assistant that hit its latency gate and still answered badly:
"name a colour" produced an invented story about mold and a rotting roof, and
"write a detailed 400-word essay" produced the single word "Rain". A one-off
manual pass cannot tell you whether that is fixed, so the questions live here.

Every check is mechanical — exact match, word bounds, a forbidden substring.
Nothing here asks a model to grade another model, because that trades a problem
you can measure for one you cannot. The probes themselves are in `probes.py`.

    python scripts/eval_quality.py                          # local models, all probes
    python scripts/eval_quality.py --suite hallucination     # just the honesty work
    python scripts/eval_quality.py --models gpt-4.1-mini     # opt into cloud spend
    python scripts/eval_quality.py --all-models              # every catalog model
    python scripts/eval_quality.py --temperature 0,0.3,0.8   # sweep and compare
    python scripts/eval_quality.py --verbose                 # print every reply

Local models are the default on purpose: a full sweep is ~120 calls per model and
cloud models bill per call.

**Read both headline numbers, never one alone.** A model that fabricates nothing
because it refuses everything has been broken, not fixed. `fabricate` and
`refuse` in the report move in opposite directions and only mean something
together.

One sample per probe, so a single run carries roughly +/-1 of noise on borderline
length checks. Read a one-probe difference between runs as variance; read a
category dropping several points as a regression.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# **A measurement that dies two thirds of the way through is worse than no
# measurement**, because the partial output still looks like a result. This
# suite crashed on `UnicodeEncodeError` printing a model's reply containing ⏎ —
# Windows consoles default to cp1252, and a fabrication preview is exactly the
# kind of text that carries an arbitrary character. The probes themselves are
# already Unicode-aware (`probes.normalise` folds U+2019, which once scored a
# perfect refusal as a 78% fabrication rate); this is the same lesson one layer
# out, in the reporting rather than the checking.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from sidecar.core import context as ctx
from sidecar.eval.probes import (
    SUITES,
    Expect,
    Probe,
    claimed_action,
    first_sentence,
    hedged,
    refused,
    universal_failures,
)
from sidecar.providers import catalog, factory
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    LLMProvider,
    ProviderError,
    ProviderRateLimited,
    Role,
)
from sidecar.providers.ollama import OllamaProvider


@dataclass
class Result:
    probe: Probe
    reply: str
    passed: bool
    failures: list[str]
    ttft_ms: float | None
    error: str | None = None
    # Carried as a flag rather than sniffed out of the message. Matching the
    # string "429" missed OpenAI's "rate limit or quota reached", so a quota
    # exhaustion scored as 76 fabrications and put gpt-5-mini at 11% overall.
    rate_limited: bool = False

    @property
    def refused(self) -> bool:
        return refused(self.reply)

    @property
    def hedged(self) -> bool:
        return hedged(self.reply)

    @property
    def fabricated(self) -> bool:
        """Answered something that has no answer, or claimed an action it
        cannot perform. The number this whole suite exists to drive to zero."""
        if self.probe.expect is not Expect.UNKNOWABLE:
            return False
        return claimed_action(self.reply) or not self.refused

    @property
    def over_refused(self) -> bool:
        """Declined or hedged a solid fact. The counter-metric — a hallucination
        fix that raises this has made the assistant worse, not safer.

        Judged on the sentence carrying the answer, not the whole reply — a
        model that answers plainly and then adds a hedged footnote has not
        over-refused, and counting it as such argues for terser replies.

        `Expect.CORRECTION` is excluded deliberately; see the enum.
        """
        if self.probe.expect is not Expect.GROUNDED:
            return False
        head = first_sentence(self.reply)
        return refused(head) or hedged(head)


# Models whose reasoning tokens are billed against the same output budget, so
# the cap has to leave room for thinking *and* an answer.
#
# `qwen3.5:4b` is deliberately absent despite being a reasoning model: the
# Ollama client sends `think: false`, so it emits none. Including it here only
# licensed 4000 tokens of rambling and stalled the sweep for minutes per probe.
#
# Named rather than inferred: `temperature is None` selects the same set today,
# but for an unrelated reason, and coupling the two would break quietly.
_REASONING_MODELS = frozenset({"gpt-5", "gpt-5-mini", "gemini-3.1-pro-preview"})


def _is_reasoning(info: catalog.ModelInfo) -> bool:
    return info.id in _REASONING_MODELS


def build_messages(
    probe: Probe, info: catalog.ModelInfo, level: ctx.PersonaLevel | None = None
) -> list[ChatMessage]:
    """Exactly what the app would send: stable prefix first, then the turns.

    **Including the clock**, which this did not do until 2026-08-19. Three
    `grounded` probes ask the time, the date and the weekday — they are in the
    control group *because* `machine_context()` puts the answer in the prompt,
    and this sent `machine=None`. So they were scoring whether a model would
    invent a plausible time, which is the opposite of what `grounded` measures:
    a model that correctly said it could not know was marked down, and one that
    made up "3:45 PM" was marked up. Found while building the adoption gate,
    which runs the same probes from inside the sidecar.
    """
    turns: list[ChatMessage] = []
    for user, assistant in probe.history:
        turns.append(ChatMessage(role=Role.USER, content=user))
        turns.append(ChatMessage(role=Role.ASSISTANT, content=assistant))
    turns.append(ChatMessage(role=Role.USER, content=probe.prompt))
    machine = ctx.MachineContext(
        now=datetime.now().astimezone(),
        model_label=info.label,
        model_is_local=info.local,
    )
    return ctx.assemble(turns, level=level or info.persona, machine=machine)


async def run_probe(
    provider: LLMProvider,
    info: catalog.ModelInfo,
    probe: Probe,
    level: ctx.PersonaLevel | None = None,
    temperature: float | None = None,
) -> Result:
    started = time.perf_counter()
    ttft: float | None = None
    chunks: list[str] = []

    try:
        async for delta in provider.stream_chat(
            build_messages(probe, info, level),
            model=info.id,
            options=GenerationOptions(
                num_ctx=min(8192, info.context_tokens),
                # Reasoning models bill their thinking against this same budget,
                # so 900 left GPT-5 returning empty strings on the harder probes
                # — it had spent the lot before writing a word. The battery then
                # scored the silence as a fabrication.
                max_tokens=4000 if _is_reasoning(info) else 900,
                temperature=temperature if temperature is not None else info.temperature,
            ),
        ):
            if delta.text and ttft is None:
                ttft = (time.perf_counter() - started) * 1000
            chunks.append(delta.text)
            if delta.done:
                break
    except ProviderError as exc:
        return Result(
            probe,
            "",
            False,
            [f"provider error: {exc}"],
            None,
            str(exc),
            rate_limited=isinstance(exc, ProviderRateLimited),
        )

    reply = "".join(chunks)
    failures = universal_failures(probe, reply)
    for index, check in enumerate(probe.checks):
        try:
            if not check(reply):
                failures.append(f"check {index + 1} failed")
        except Exception as exc:  # noqa: BLE001 — a bad check must not abort the sweep
            failures.append(f"check {index + 1} raised {exc}")

    return Result(probe, reply, not failures, failures, ttft)


def provider_for(info: catalog.ModelInfo) -> LLMProvider:
    """One line, because the hand-written version here was a trap.

    It mapped Ollama and OpenAI explicitly and let *everything else* fall
    through to `GeminiProvider()` — so measuring an OpenRouter model would
    have measured Gemini and printed the score under the wrong id. A
    measurement naming the wrong model is worse than no measurement, because
    it looks like evidence. `providers/factory.py` raises instead.
    """
    return factory.for_model(info)


async def run_model(
    model_id: str,
    probes: list[Probe],
    verbose: bool,
    level: ctx.PersonaLevel | None = None,
    temperature: float | None = None,
) -> list[Result]:
    info = catalog.get(model_id)
    if info is None:
        print(f"  unknown model {model_id!r}; not in the catalog")
        return []

    provider = provider_for(info)
    results: list[Result] = []
    rate_limited = 0

    try:
        for probe in probes:
            result = await run_probe(provider, info, probe, level, temperature)

            # A rate-limited model is untested, not failing. Counting 429s as
            # wrong answers would libel a model nobody actually measured.
            #
            # Partial results are still reported: an earlier version returned []
            # here and silently dropped two Gemini models that had answered most
            # of the suite before their quota ran out.
            if result.rate_limited:
                rate_limited += 1
                if rate_limited >= 3:
                    print(
                        f"  -- rate limited after {len(results)} probes; "
                        f"reporting those, skipping the rest"
                    )
                    break
                continue

            results.append(result)
            mark = "ok  " if result.passed else "FAIL"
            tag = " FABRICATED" if result.fabricated else ""
            tag += " OVER-REFUSED" if result.over_refused else ""
            why = "" if result.passed else "; ".join(result.failures)
            print(f"  [{mark}]{tag} {probe.id:<28} {why}")
            if verbose or not result.passed:
                preview = result.reply.replace("\n", " ⏎ ")
                print(f"          {preview[:170]}")
    finally:
        # Free the card before the next model loads. Without this, sweeping the
        # 7B then the 4B asks a 6GB GPU to hold both — Ollama keeps a model for
        # 30 minutes — and generation stalls for minutes rather than failing.
        if isinstance(provider, OllamaProvider):
            await provider.unload(info.id)
        await provider.aclose()
    return results


# ── reporting ─────────────────────────────────────────────────────────


def _rate(hits: int, total: int) -> str:
    if total == 0:
        return "—"
    return f"{hits}/{total} ({100 * hits / total:.0f}%)"


def report(by_model: dict[str, list[Result]]) -> None:
    models = list(by_model)
    if not models:
        return

    width = 22
    print("\n" + "=" * (16 + width * len(models)))
    print("HONESTY".ljust(16) + "".join(f"{m[:20]:>{width}}" for m in models))
    print("-" * (16 + width * len(models)))

    def line(label: str, fn) -> None:  # noqa: ANN001 — local formatting helper
        row = label.ljust(16)
        for model in models:
            hits, total = fn(by_model[model])
            row += f"{_rate(hits, total):>{width}}"
        print(row)

    # The two numbers that must be read together.
    line(
        "fabricated",
        lambda rs: (
            sum(1 for r in rs if r.fabricated),
            sum(1 for r in rs if r.probe.expect is Expect.UNKNOWABLE),
        ),
    )
    line(
        "over-refused",
        lambda rs: (
            sum(1 for r in rs if r.over_refused),
            sum(1 for r in rs if r.probe.expect is Expect.GROUNDED),
        ),
    )
    line(
        "hedged well",
        lambda rs: (
            sum(1 for r in rs if r.probe.expect is Expect.UNCERTAIN and r.hedged),
            sum(1 for r in rs if r.probe.expect is Expect.UNCERTAIN),
        ),
    )
    line(
        "claimed action",
        lambda rs: (
            sum(1 for r in rs if claimed_action(r.reply)),
            sum(1 for r in rs if r.probe.category == "false-capability"),
        ),
    )

    categories = sorted({r.probe.category for rs in by_model.values() for r in rs})
    print("\n" + "PASS RATE".ljust(16) + "".join(f"{m[:20]:>{width}}" for m in models))
    print("-" * (16 + width * len(models)))
    for category in categories:
        line(
            category,
            lambda rs, c=category: (
                sum(1 for r in rs if r.probe.category == c and r.passed),
                sum(1 for r in rs if r.probe.category == c),
            ),
        )

    print("-" * (16 + width * len(models)))
    line("TOTAL", lambda rs: (sum(1 for r in rs if r.passed), len(rs)))

    row = "median TTFT".ljust(16)
    for model in models:
        samples = sorted(r.ttft_ms for r in by_model[model] if r.ttft_ms is not None)
        row += f"{f'{samples[len(samples) // 2]:.0f}ms' if samples else '—':>{width}}"
    print(row)
    print("=" * (16 + width * len(models)))

    _report_offenders(by_model)


def _report_offenders(by_model: dict[str, list[Result]]) -> None:
    """The individual failures worth a human reading. A rate tells you there is
    a problem; only the reply tells you what kind."""
    for label, predicate in (
        ("FABRICATIONS", lambda r: r.fabricated),
        ("OVER-REFUSALS", lambda r: r.over_refused),
        ("LEAKED REASONING TAGS", lambda r: "leaked <think> tag" in r.failures),
    ):
        rows = [
            (model, r)
            for model, results in by_model.items()
            for r in results
            if predicate(r)
        ]
        if not rows:
            continue
        print(f"\n{label}:")
        for model, result in rows[:25]:
            preview = result.reply.replace("\n", " ⏎ ")[:110]
            print(f"  {model:<26} {result.probe.id:<28} {preview}")
        if len(rows) > 25:
            print(f"  ... and {len(rows) - 25} more")


# ── entrypoint ────────────────────────────────────────────────────────


async def _pulled_models() -> set[str]:
    provider = OllamaProvider()
    try:
        return set(await provider.list_models())
    except ProviderError:
        return set()
    finally:
        await provider.aclose()


async def _resolve_models(args: argparse.Namespace) -> list[str]:
    if args.models:
        return [m.strip() for m in args.models.split(",") if m.strip()]
    if args.all_models:
        return [m.id for m in catalog.CATALOG]

    pulled = await _pulled_models()
    local = [m.id for m in catalog.local_models() if m.id in pulled]
    if not local:
        print("No local models are pulled. Pass --models, or run: ollama pull qwen2.5:7b")
    return local


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", help="Comma-separated catalog ids.")
    parser.add_argument(
        "--all-models", action="store_true", help="Every model in the catalog (costs money)."
    )
    parser.add_argument("--suite", choices=sorted(SUITES), default="all")
    parser.add_argument("--category", help="Run only one category.")
    parser.add_argument(
        "--temperature",
        help="One value, or a comma-separated sweep (e.g. 0,0.3,0.8). "
        "Omit to use each model's catalog setting.",
    )
    parser.add_argument(
        "--persona",
        choices=[str(level) for level in ctx.PersonaLevel],
        help="Override the catalog's persona level. This is how a model's level "
        "gets decided: run both and compare, rather than assuming.",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print every reply, not just failures."
    )
    args = parser.parse_args()

    level = ctx.PersonaLevel(args.persona) if args.persona else None
    temperatures: list[float | None] = (
        [float(t) for t in args.temperature.split(",")] if args.temperature else [None]
    )

    probes = SUITES[args.suite]
    if args.category:
        probes = [p for p in probes if p.category == args.category]
        if not probes:
            print(f"No probes in category {args.category!r}.")
            return

    model_ids = await _resolve_models(args)
    if not model_ids:
        return

    by_model: dict[str, list[Result]] = {}
    for temperature in temperatures:
        for model_id in model_ids:
            parts = [f"{len(probes)} probes"]
            if level:
                parts.append(f"persona={level}")
            if temperature is not None:
                parts.append(f"temp={temperature}")
            key = model_id if temperature is None else f"{model_id}@{temperature}"

            print(f"\n=== {key} ({', '.join(parts)}) ===")
            results = await run_model(model_id, probes, args.verbose, level, temperature)
            if results:
                by_model[key] = results

    if by_model:
        report(by_model)


if __name__ == "__main__":
    asyncio.run(main())
