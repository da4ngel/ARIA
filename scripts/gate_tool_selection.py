"""Should tool schemas be filtered by relevance before the model sees them?

§7.2 caps a local model at roughly 12 tools and there are 15, so the answer has
been assumed to be yes since Phase 3. Measured on 2026-08-09, it is **no** —
and this script is the measurement, kept so the decision can be re-checked
rather than re-argued when the count grows again.

    python scripts/gate_tool_selection.py

Two questions, and selection has to win both to be worth building:

  1. Does offering fewer tools make the model choose better?
  2. Would a selector keep the right tool?

It loses both, and lost again when the registry grew from 15 tools to 23:

    15 tools   all 16/17    filtered 9/17
    23 tools   all 21/24    filtered 9/24

A correct tool that was filtered out cannot be chosen, so filtering converts
right answers into wrong ones — and it gets *worse* as the registry grows,
because there are more right answers to throw away. An embedding selector tops
out at 14/15 recall (21/22 at 23 tools), missing `find` for "the quotation I
sent the banquet hall", where it ranks the semantic-search tool **last** for a
semantic-search query.

There is a third reason not to, which needs no measurement. Tool schemas sit in
the stable prefix so Ollama's KV cache can hold them (§8.2, §10). A set that
changes with the message invalidates that prefix *every time the topic moves*,
so selection would spend prefill rather than save it.

Re-run this when the tool count grows. The number to watch is recall: selection
only becomes safe when the right tool is nearly always in the kept set.
"""

from __future__ import annotations

import asyncio
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sidecar.tools  # noqa: F401  — importing registers the tools
from sidecar.core.context import PersonaLevel, stable_prefix
from sidecar.providers import catalog, factory
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    LLMProvider,
    ProviderError,
    Role,
)
from sidecar.providers.embeddings import OllamaEmbeddings
from sidecar.providers.ollama import OllamaProvider
from sidecar.tools import registry

MODEL = "qwen2.5:7b"

#: One request per tool, phrased the way a person asks rather than the way the
#: description is written — otherwise this measures paraphrase, not retrieval.
PROBES: list[tuple[str, str | None]] = [
    ("open calculator", "open_app"),
    ("create a file named hello.txt in downloads", "write_file"),
    ("what is in my downloads folder", "list_folder"),
    ("where did i put my cv", "search_files"),
    ("read hello.txt in downloads", "read_file"),
    ("show me the downloads folder in explorer", "open_path"),
    ("how much memory am i using", "get_system_info"),
    ("the quotation i sent the banquet hall", "find"),
    ("make a folder called receipts in documents", "create_folder"),
    ("turn the volume down to 20", "set_volume"),
    # **The relative form, which was never tested and never worked.** The probe
    # above hands the model the number, so it passed while "increase the volume"
    # was impossible to answer: `percent` was required and absolute, nothing
    # exposed the current level, and the description invited exactly the
    # phrasing the schema refused. A probe that supplies the hard part of the
    # question is not measuring the tool.
    ("increase the volume", "set_volume"),
    ("turn it up a bit", "set_volume"),
    ("rename scan001.pdf to invoice.pdf", "rename_file"),
    ("move budget.xlsx to documents", "move_file"),
    ("which windows are open", "list_windows"),
    ("which files mention the banquet hall", "search_content"),
    ("open my cv", "open_file"),
    # Phase 3's remaining tools, added when the registry went from 17 to 25.
    ("switch to chrome", "focus_window"),
    ("close spotify", "close_app"),
    ("what is using all my memory", "list_processes"),
    ("force quit notepad", "kill_process"),
    ("turn wifi off", "set_wifi"),
    ("what is on my clipboard", "read_clipboard"),
    ("copy that to my clipboard", "write_clipboard"),
    # The control. Selection must not make her reach for a tool she does not
    # need, which is the failure mode a smaller list encourages.
    ("what is the capital of Australia", None),
    ("tell me a joke", None),
]

KEEP_SIZES = (6, 8, 10, 12)


def cosine(a: list[float], b: list[float]) -> float:
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return sum(x * y for x, y in zip(a, b, strict=True)) / norm if norm else 0.0


async def measure_recall() -> bool:
    """Would a selector keep the right tool? The question that decides it."""
    embeddings = OllamaEmbeddings()
    tools = registry.schemas()
    names = [t["function"]["name"] for t in tools]
    vectors = [
        await embeddings.embed(f"{t['function']['name']}: {t['function']['description']}")
        for t in tools
    ]

    wanted = [(text, tool) for text, tool in PROBES if tool]
    ranked_per_probe: list[tuple[str, str, list[str]]] = []
    for text, tool in wanted:
        query = await embeddings.embed(text)
        scored = zip(names, (cosine(query, v) for v in vectors), strict=True)
        order = sorted(scored, key=lambda pair: -pair[1])
        ranked_per_probe.append((text, str(tool), [n for n, _ in order]))
    await embeddings.aclose()

    print(f"\nRecall - is the right tool still there after filtering? ({len(names)} tools)")
    perfect = False
    for keep in KEEP_SIZES:
        if keep >= len(names):
            continue
        hits = [(t, w, r) for t, w, r in ranked_per_probe if w in r[:keep]]
        misses = [(t, w, r) for t, w, r in ranked_per_probe if w not in r[:keep]]
        print(f"  keep {keep:>2}: {len(hits)}/{len(ranked_per_probe)}")
        for text, tool, order in misses:
            print(f"        dropped {tool!r} for {text!r} - it ranked {order.index(tool) + 1}")
        perfect = perfect or not misses
    return perfect


async def choose_with(
    provider: LLMProvider,
    tools: list[dict],
    model: str = MODEL,
    level: PersonaLevel = PersonaLevel.MINIMAL,
) -> tuple[int, list[str]]:
    prefix = stable_prefix(level, has_tools=True)
    right = 0
    wrong: list[str] = []
    for text, want in PROBES:
        got: str | None = None
        try:
            async for delta in provider.stream_chat(
                [*prefix, ChatMessage(role=Role.USER, content=text)],
                model=model,
                options=GenerationOptions(max_tokens=600),
                tools=tools,
            ):
                if delta.tool_calls:
                    got = delta.tool_calls[0].name
                    break
                if delta.done:
                    break
        except ProviderError as exc:
            # A dead account or an exhausted quota is not a wrong answer, and
            # recording it as one would put a fabricated `tool_score` in the
            # catalog. Abandon the model instead.
            wrong.append(f"provider error: {exc}")
            return (right, wrong)
        if got == want:
            right += 1
        else:
            wrong.append(f"{text!r} wanted {want} got {got}")
    return right, wrong


async def measure_per_model(model_ids: list[str]) -> None:
    """Score each model's tool choice, for `ModelInfo.tool_score`.

    **There was no such measurement anywhere in this repo**, which is why the
    router had nothing to consult when it needed to know which model could be
    trusted with a command. The only tool number that existed was this script's
    own, on `qwen2.5:7b` alone; CLAUDE.md's "all five models pick `open_app`
    correctly 6/6" was a manual probe that left no script behind, and so could
    not be re-run when the registry doubled.

    Full registry every time — never the filtered subset. Selection is closed
    (see the module docstring); what is being measured here is the model, on the
    tool list it will actually be given.
    """
    everything = registry.schemas()
    print(f"\nTool choice per model ({len(everything)} tools, {len(PROBES)} probes):")
    scores: list[tuple[str, float]] = []

    for model_id in model_ids:
        info = catalog.get(model_id)
        if info is None:
            print(f"  {model_id:28} not in the catalog")
            continue
        provider = provider_for(info)
        try:
            right, wrong = await choose_with(provider, everything, model_id, info.persona)
        finally:
            if isinstance(provider, OllamaProvider):
                # 6GB card, rule 2: the next model cannot load beside this one.
                await provider.unload(model_id)
            await provider.aclose()

        errored = [w for w in wrong if w.startswith("provider error")]
        if errored:
            print(f"  {model_id:28} unreachable - {errored[0]}")
            continue
        score = right / len(PROBES)
        scores.append((model_id, score))
        print(f"  {model_id:28} {right:>2}/{len(PROBES)}  tool_score={score:.2f}")
        for line in wrong:
            print(f"        {line}")

    if scores:
        print("\n  Paste into providers/catalog.py — measured, so it may be routed on:")
        for model_id, score in scores:
            print(f"    {model_id:28} tool_score={score:.2f},")


def provider_for(info: catalog.ModelInfo) -> LLMProvider:
    """One line, because the hand-written version here was a trap.

    It mapped Ollama and OpenAI explicitly and let *everything else* fall
    through to `GeminiProvider()` — so measuring an OpenRouter model would
    have measured Gemini and printed the score under the wrong id. A
    measurement naming the wrong model is worse than no measurement, because
    it looks like evidence. `providers/factory.py` raises instead.
    """
    return factory.for_model(info)


async def measure_choice() -> None:
    """Does a shorter list make the model choose better? Measured, not assumed."""
    provider = OllamaProvider()
    everything = registry.schemas()

    # A generous stand-in for a selector: the file and app tools, which is what
    # relevance would keep for most of these. It still drops two right answers,
    # and that is the point — this is what a selector does when it is wrong.
    subset_names = {
        "open_app",
        "open_path",
        "list_folder",
        "read_file",
        "write_file",
        "search_files",
        "find",
        "get_system_info",
    }
    subset = [t for t in everything if t["function"]["name"] in subset_names]

    print(f"\nTool choice on {MODEL}:")
    for label, tools in (("all", everything), ("filtered", subset)):
        right, wrong = await choose_with(provider, tools)
        print(f"  {label:9} ({len(tools):>2} tools): {right}/{len(PROBES)}")
        for line in wrong:
            print(f"        {line}")
    await provider.aclose()


async def main() -> None:
    models = [m for m in sys.argv[1:] if not m.startswith("-")]
    if models:
        # `--models a,b` scores each model for `ModelInfo.tool_score`; the
        # selection question below is settled and does not need re-running to
        # measure a new model.
        await measure_per_model([m for spec in models for m in spec.split(",")])
        return

    perfect_recall = await measure_recall()
    await measure_choice()
    print(
        "\nSelection is worth building when the filtered list scores higher than "
        "the full one\nand recall is perfect. Neither held on 2026-08-09 - see "
        "CLAUDE.md."
    )
    if perfect_recall:
        print("Recall is now perfect at some size. Worth re-testing choice properly.")
    print(
        "\nTo score models for ModelInfo.tool_score instead:\n"
        "    python scripts/gate_tool_selection.py qwen2.5:7b,gpt-5.4-nano"
    )


if __name__ == "__main__":
    asyncio.run(main())
