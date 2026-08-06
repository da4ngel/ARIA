"""Answer-quality battery. Run it, change something, run it again.

Phase 1 shipped an assistant that hit its latency gate and still answered badly:
"name a colour" produced an invented story about mold and a rotting roof, and
"write a detailed 400-word essay" produced the single word "Rain". A one-off
manual pass cannot tell you whether that is fixed, so the questions live here.

Every check is mechanical — exact match, word bounds, a forbidden substring.
Nothing here asks a model to grade another model, because that trades a problem
you can measure for one you cannot.

    python scripts/eval_quality.py                        # local models only
    python scripts/eval_quality.py --models gpt-4.1-mini  # opt into cloud spend
    python scripts/eval_quality.py --verbose              # print every reply

Local models are the default on purpose: a full sweep is ~45 calls per model and
cloud models bill per call.

One sample per probe, so a single run carries roughly +/-1 of noise on borderline
length checks. Read a one-probe difference between runs as variance; read a
category dropping several points as a regression. `--category` re-runs a slice
cheaply when you want a second opinion.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sidecar.core import context as ctx
from sidecar.providers import catalog
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    LLMProvider,
    ProviderError,
    Role,
)
from sidecar.providers.gemini import GeminiProvider
from sidecar.providers.ollama import OllamaProvider
from sidecar.providers.openai import OpenAIProvider

Check = Callable[[str], bool]


# ── checks ────────────────────────────────────────────────────────────


def exact(expected: str) -> Check:
    """Ignores case, surrounding whitespace and a trailing period."""

    def check(reply: str) -> bool:
        return reply.strip().rstrip(".").strip().lower() == expected.lower()

    return check


def max_words(limit: int) -> Check:
    return lambda reply: len(reply.split()) <= limit


def min_words(limit: int) -> Check:
    return lambda reply: len(reply.split()) >= limit


def contains(*needles: str) -> Check:
    return lambda reply: all(n.lower() in reply.lower() for n in needles)


def excludes(*needles: str) -> Check:
    return lambda reply: not any(n.lower() in reply.lower() for n in needles)


def matches(pattern: str) -> Check:
    compiled = re.compile(pattern, re.IGNORECASE | re.DOTALL)
    return lambda reply: bool(compiled.search(reply))


def line_count(expected: int) -> Check:
    return lambda reply: len([ln for ln in reply.splitlines() if ln.strip()]) == expected


# Any admission of not knowing. Phrasing varies far more than a literal list can
# track — three earlier revisions of this check failed correct answers like
# "Unknown." and "I don't have information about your meals." What actually
# distinguishes a good answer from a bad one is whether *some* negation attaches
# to a knowing/having verb; a fabrication ("You had oatmeal.") carries none.
_IGNORANCE = re.compile(
    r"(don'?t|do not|doesn'?t|does not|cannot|can'?t|couldn'?t|unable to|not able to"
    r"|no way to|haven'?t|have not|didn'?t|did not|isn'?t|is not|won'?t)"
    r"[^.!?]{0,40}?"
    r"(know|have|had|recall|remember|access|see|tell|told|track|information|record|exist)"
    r"|(^|\W)(unknown|not aware|no information|no record|no access|no idea|fictional"
    r"|made[- ]up|no such)(\W|$)",
    re.IGNORECASE,
)


def admits_ignorance() -> Check:
    """Passes if the reply admits not knowing, however it phrases it."""
    return lambda reply: bool(_IGNORANCE.search(reply))


# Applied to every reply, never declared per probe.
_THINK_TAG = re.compile(r"</?think(ing)?>", re.IGNORECASE)
_EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿]")

# The specific fiction the 4B invented and then referenced for 25 turns. Any of
# these appearing unprompted means the hallucination is back.
INVENTED = (
    "mold",
    "mould",
    "rotting",
    "rotten",
    "leaking",
    "leaky",
    "drywall",
    "peeling paint",
    "the roof",
    "the sink",
)

FILLER_OPENERS = (
    "great question",
    "i'd be happy to",
    "i would be happy to",
    "certainly!",
    "absolutely!",
    "sure thing",
)


@dataclass
class Probe:
    id: str
    category: str
    prompt: str
    checks: list[Check] = field(default_factory=list)
    # Extra user/assistant turns placed before `prompt`.
    history: list[tuple[str, str]] = field(default_factory=list)
    # Some probes legitimately mention a forbidden word (e.g. asking about rain).
    allow_invented: bool = False


# ── the battery ───────────────────────────────────────────────────────

PROBES: list[Probe] = [
    # ── the three that failed in the bad session, verbatim ────────────
    Probe(
        "regress-hello",
        "regression",
        "say hello",
        [max_words(12), excludes("repeat myself", "already said")],
    ),
    Probe(
        "regress-colour",
        "regression",
        "name a colour",
        [max_words(25)],
    ),
    Probe(
        "regress-essay",
        "regression",
        "Write a detailed 400-word essay about rain.",
        [min_words(250)],
        allow_invented=True,
    ),
    # ── instruction following: exact output ───────────────────────────
    Probe("exact-7", "instruction", "Reply with only the number 7.", [exact("7")]),
    Probe("exact-yes", "instruction", "Answer with exactly one word: yes.", [exact("yes")]),
    Probe(
        "exact-capital",
        "instruction",
        "What is the capital of France? Answer with the city name only.",
        [exact("Paris")],
    ),
    Probe(
        "exact-three-words",
        "instruction",
        "Describe the ocean in exactly three words. Output only those words.",
        [max_words(4)],
    ),
    Probe(
        "exact-uppercase",
        "instruction",
        "Reply with the word 'ready' in all capital letters, nothing else.",
        [contains("READY"), max_words(3)],
    ),
    Probe(
        "exact-json",
        "instruction",
        'Reply with only this JSON and nothing else: {"ok": true}',
        [matches(r'\{\s*"ok"\s*:\s*true\s*\}')],
    ),
    Probe(
        "exact-no-punctuation",
        "instruction",
        "Name three primary colours as a comma-separated list. No other text.",
        [matches(r"^[a-z]+\s*,\s*[a-z]+\s*,\s*[a-z]+\.?$"), max_words(8)],
    ),
    # ── instruction following: length control ─────────────────────────
    Probe(
        "len-one-sentence",
        "instruction",
        "Explain gravity in one sentence.",
        [max_words(45), line_count(1)],
    ),
    Probe(
        "len-under-20",
        "instruction",
        "In under 20 words, what is a database index?",
        [max_words(25)],
    ),
    Probe(
        "len-five-lines",
        "instruction",
        "List exactly 5 fruits, one per line, nothing else.",
        [line_count(5)],
    ),
    Probe(
        "len-long",
        "instruction",
        "Write at least 150 words about why sleep matters.",
        [min_words(110)],
    ),
    Probe(
        "len-haiku",
        "instruction",
        "Write a haiku about winter. Output only the haiku.",
        [line_count(3), max_words(20)],
    ),
    # ── factual recall ────────────────────────────────────────────────
    Probe("fact-capital-japan", "factual", "What is the capital of Japan?", [contains("Tokyo")]),
    Probe(
        "fact-planets",
        "factual",
        "How many planets are in our solar system?",
        [matches(r"\b(8|eight)\b")],
    ),
    Probe(
        "fact-water",
        "factual",
        "What is the chemical formula for water?",
        [matches(r"H2O|H₂O")],
    ),
    Probe(
        "fact-ww2",
        "factual",
        "In what year did the Second World War end?",
        [contains("1945")],
    ),
    Probe(
        "fact-speed-light",
        "factual",
        "Roughly how fast does light travel in a vacuum, in km per second?",
        # The Unicode multiplication sign is deliberate: models render
        # scientific notation with it about as often as with a plain letter x,
        # and a correct answer must pass either way.
        [matches(r"300[,.]?000|299[,.]?792|3\s*[x×]\s*10")],  # noqa: RUF001
    ),
    Probe(
        "fact-python-list",
        "factual",
        "In Python, which method adds one item to the end of a list?",
        [contains("append")],
    ),
    # ── short reasoning ───────────────────────────────────────────────
    Probe(
        "reason-arith",
        "reasoning",
        "What is 17 + 25? Answer with the number only.",
        [exact("42")],
    ),
    Probe(
        "reason-multiply",
        "reasoning",
        "What is 12 times 12? Answer with the number only.",
        [exact("144")],
    ),
    Probe(
        "reason-order",
        "reasoning",
        "Sort these numbers ascending and output only the list: 5, 2, 9, 1.",
        [matches(r"1\D+2\D+5\D+9")],
    ),
    Probe(
        "reason-apples",
        "reasoning",
        "I had 10 apples, ate 3, then bought 5. How many now? Number only.",
        [exact("12")],
    ),
    Probe(
        "reason-odd-one-out",
        "reasoning",
        "Which does not belong: dog, cat, hammer, horse? One word answer.",
        [contains("hammer"), max_words(4)],
    ),
    Probe(
        "reason-days",
        "reasoning",
        "If today is Wednesday, what day is it in 3 days? One word.",
        [contains("Saturday"), max_words(4)],
    ),
    # ── honesty ───────────────────────────────────────────────────────
    Probe(
        "honest-unknown",
        "honesty",
        "What did I eat for breakfast this morning?",
        # The failure this catches is the opposite of refusing: confidently
        # inventing a breakfast, which qwen2.5:7b does under the FULL persona.
        [admits_ignorance()],
    ),
    Probe(
        "honest-nonsense",
        "honesty",
        "What is the capital city of the country Zubrovia?",
        [admits_ignorance()],
    ),
    # ── persona and voice ─────────────────────────────────────────────
    Probe(
        "voice-no-filler",
        "persona",
        "How do I reverse a string in Python?",
        [contains("[::-1]")],
    ),
    Probe(
        "voice-concise",
        "persona",
        "What time zone is UTC+0 also known as?",
        [max_words(40)],
    ),
    Probe(
        "voice-disagree",
        "persona",
        "I want to store passwords in plain text. Good idea?",
        [matches(r"no|don't|do not|bad idea|not a good"), max_words(160)],
    ),
    Probe(
        "voice-follows-anyway",
        "persona",
        "Write me a one-line shell command to list files. Just the command.",
        [matches(r"\bls\b|dir"), max_words(12)],
    ),
    # ── multi-turn coherence ──────────────────────────────────────────
    Probe(
        "multi-name",
        "coherence",
        "What is my name?",
        [contains("Eyaas")],
        history=[("My name is Eyaas.", "Got it."), ("I work on Windows.", "Noted.")],
    ),
    Probe(
        "multi-followup",
        "coherence",
        "What is its population, roughly?",
        [matches(r"million|\d{1,3}[,.]?\d{3}")],
        history=[("Tell me about Tokyo.", "Tokyo is the capital of Japan.")],
    ),
    Probe(
        "multi-no-drift",
        "coherence",
        "What were we talking about?",
        [matches(r"colou?r|blue|red|green")],
        history=[("Name a colour.", "Blue."), ("Another one.", "Green.")],
    ),
    Probe(
        "multi-correction",
        "coherence",
        "Actually my favourite is red. What is my favourite colour now?",
        [contains("red")],
        history=[("My favourite colour is blue.", "Noted.")],
    ),
    Probe(
        "multi-count",
        "coherence",
        "How many numbers have I given you so far? Number only.",
        [exact("3")],
        history=[("Here is a number: 4.", "Okay."), ("And 7.", "Okay."), ("And 9.", "Okay.")],
    ),
    # ── refusal calibration: must NOT over-refuse ─────────────────────
    Probe(
        "comply-simple",
        "compliance",
        "Repeat this word back to me exactly: banana",
        [contains("banana"), max_words(6)],
    ),
    Probe(
        "comply-roleplay",
        "compliance",
        "Pretend you are a pirate and greet me in one sentence.",
        [max_words(40), excludes("I cannot", "I can't", "I won't")],
    ),
    Probe(
        "comply-opinion",
        "compliance",
        "Pick one: tabs or spaces? One word.",
        [matches(r"tabs|spaces"), max_words(6)],
    ),
]


# ── running ───────────────────────────────────────────────────────────


@dataclass
class Result:
    probe: Probe
    reply: str
    passed: bool
    failures: list[str]
    ttft_ms: float | None
    error: str | None = None


def universal_failures(probe: Probe, reply: str) -> list[str]:
    """Rules every reply obeys, regardless of what was asked."""
    problems: list[str] = []
    if not reply.strip():
        problems.append("empty reply")
    if _THINK_TAG.search(reply):
        problems.append("leaked <think> tag")
    if _EMOJI.search(reply):
        problems.append("emoji")
    if any(reply.lower().lstrip().startswith(f) for f in FILLER_OPENERS):
        problems.append("filler opener")
    if not probe.allow_invented:
        found = [w for w in INVENTED if w in reply.lower()]
        if found:
            problems.append(f"invented context: {', '.join(found)}")
    return problems


def build_messages(
    probe: Probe, info: catalog.ModelInfo, level: ctx.PersonaLevel | None = None
) -> list[ChatMessage]:
    """Exactly what the app would send: stable prefix first, then the turns."""
    turns: list[ChatMessage] = []
    for user, assistant in probe.history:
        turns.append(ChatMessage(role=Role.USER, content=user))
        turns.append(ChatMessage(role=Role.ASSISTANT, content=assistant))
    turns.append(ChatMessage(role=Role.USER, content=probe.prompt))
    return ctx.assemble(turns, level=level or info.persona)


async def run_probe(
    provider: LLMProvider,
    info: catalog.ModelInfo,
    probe: Probe,
    level: ctx.PersonaLevel | None = None,
) -> Result:
    started = time.perf_counter()
    ttft: float | None = None
    chunks: list[str] = []

    try:
        async for delta in provider.stream_chat(
            build_messages(probe, info, level),
            model=info.id,
            options=GenerationOptions(num_ctx=min(8192, info.context_tokens), max_tokens=900),
        ):
            if delta.text and ttft is None:
                ttft = (time.perf_counter() - started) * 1000
            chunks.append(delta.text)
            if delta.done:
                break
    except ProviderError as exc:
        return Result(probe, "", False, [f"provider error: {exc}"], None, str(exc))

    reply = "".join(chunks)
    failures = universal_failures(probe, reply)
    for index, check in enumerate(probe.checks):
        try:
            if not check(reply):
                failures.append(f"check {index + 1} failed")
        except Exception as exc:  # noqa: BLE001 — a bad check must not abort the sweep
            failures.append(f"check {index + 1} raised {exc}")

    return Result(probe, reply, not failures, failures, ttft)


async def run_model(
    model_id: str, probes: list[Probe], verbose: bool, level: ctx.PersonaLevel | None = None
) -> list[Result]:
    info = catalog.get(model_id)
    if info is None:
        print(f"  unknown model {model_id!r}; not in the catalog")
        return []

    provider: LLMProvider
    if info.provider is catalog.ProviderName.OLLAMA:
        provider = OllamaProvider()
    elif info.provider is catalog.ProviderName.OPENAI:
        provider = OpenAIProvider()
    else:
        provider = GeminiProvider()

    results: list[Result] = []
    try:
        for probe in probes:
            result = await run_probe(provider, info, probe, level)
            results.append(result)
            mark = "ok  " if result.passed else "FAIL"
            why = "" if result.passed else "; ".join(result.failures)
            print(f"  [{mark}] {probe.id:<22} {why}")
            if verbose or not result.passed:
                preview = result.reply.replace("\n", " ⏎ ")
                print(f"         {preview[:160]}")
    finally:
        await provider.aclose()
    return results


def report(by_model: dict[str, list[Result]]) -> None:
    categories = sorted({p.category for p in PROBES})
    models = list(by_model)

    print("\n" + "=" * 78)
    print(f"{'category':<14}" + "".join(f"{m[:18]:>21}" for m in models))
    print("-" * 78)

    for category in categories:
        row = f"{category:<14}"
        for model in models:
            subset = [r for r in by_model[model] if r.probe.category == category]
            if not subset:
                row += f"{'—':>21}"
                continue
            passed = sum(1 for r in subset if r.passed)
            row += f"{f'{passed}/{len(subset)}':>21}"
        print(row)

    print("-" * 78)
    row = f"{'TOTAL':<14}"
    for model in models:
        results = by_model[model]
        passed = sum(1 for r in results if r.passed)
        pct = 100 * passed / len(results) if results else 0
        row += f"{f'{passed}/{len(results)} ({pct:.0f}%)':>21}"
    print(row)

    row = f"{'median TTFT':<14}"
    for model in models:
        samples = sorted(r.ttft_ms for r in by_model[model] if r.ttft_ms is not None)
        if not samples:
            row += f"{'—':>21}"
            continue
        row += f"{f'{samples[len(samples) // 2]:.0f}ms':>21}"
    print(row)
    print("=" * 78)

    # The single rule with no exceptions.
    leaked = [
        (m, r.probe.id)
        for m, results in by_model.items()
        for r in results
        if "leaked <think> tag" in r.failures
    ]
    if leaked:
        print("\nLEAKED REASONING TAGS (Phase 2 would read these aloud):")
        for model, probe_id in leaked:
            print(f"  {model}  {probe_id}")


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models",
        help="Comma-separated catalog ids. Defaults to local models only, "
        "because a cloud sweep costs real money.",
    )
    parser.add_argument("--category", help="Run only one category.")
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

    if args.models:
        model_ids = [m.strip() for m in args.models.split(",") if m.strip()]
    else:
        pulled = await _pulled_models()
        model_ids = [m.id for m in catalog.local_models() if m.id in pulled]
        if not model_ids:
            print("No local models are pulled. Pass --models, or run: ollama pull qwen2.5:7b")
            return

    probes = PROBES
    if args.category:
        probes = [p for p in PROBES if p.category == args.category]
        if not probes:
            print(f"No probes in category {args.category!r}.")
            return

    by_model: dict[str, list[Result]] = {}
    for model_id in model_ids:
        suffix = f", persona={level}" if level else ""
        print(f"\n=== {model_id} ({len(probes)} probes{suffix}) ===")
        results = await run_model(model_id, probes, args.verbose, level)
        if results:
            by_model[model_id] = results

    if by_model:
        report(by_model)


async def _pulled_models() -> set[str]:
    provider = OllamaProvider()
    try:
        return set(await provider.list_models())
    except ProviderError:
        return set()
    finally:
        await provider.aclose()


if __name__ == "__main__":
    asyncio.run(main())
