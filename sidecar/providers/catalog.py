"""The model catalog — one structure behind the picker, the tooltips, and routing.

Deliberately a single source. If tooltips said one thing and the router did
another, the UI would be lying about what happens when you press send.

Plain Python rather than YAML: no phase needs `pyyaml` yet, and the data is
typed here for free.

`ttft_ms_seed` values are measured on the target machine (RTX 4050, 6GB) — see
BUILD_SPEC §10. They seed the ranking; `providers/health.py` replaces them with
observed latency as turns accumulate, so a stale number self-corrects.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from enum import StrEnum

from pydantic import BaseModel, Field

from sidecar.core.context import PersonaLevel
from sidecar.providers.health import HealthTracker


class ProviderName(StrEnum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"
    #: One key, many vendors — and the free tier this project actually wants.
    #: Adding a member here obliges four other places to learn about it;
    #: `providers/factory.py` builds its dict from this enum so a forgotten
    #: registration is an error rather than a silently missing provider.
    OPENROUTER = "openrouter"


# `str.capitalize()` would render these "Openai" and "Ollama". They appear in
# user-facing tooltips, so they are spelled out.
PROVIDER_LABELS: dict[ProviderName, str] = {
    ProviderName.OLLAMA: "Ollama",
    ProviderName.OPENAI: "OpenAI",
    ProviderName.GEMINI: "Gemini",
    ProviderName.OPENROUTER: "OpenRouter",
}


class ModelClass(StrEnum):
    """What a model is *for*. The router picks a class, then a model in it."""

    FAST = "fast"  # short turns, chat, quick edits
    BALANCED = "balanced"  # general work
    SMART = "smart"  # reasoning, multi-step, code, long synthesis
    VISION = "vision"  # screen understanding (Phase 6)


class Cost(StrEnum):
    FREE = "free"
    LOW = "$"
    MEDIUM = "$$"
    HIGH = "$$$"
    # A discovered model whose price nobody here has looked up. Shown as a
    # blank, never as a guess: "$" on a model that turns out to be "$$$" is
    # worse than saying nothing.
    UNKNOWN = "?"


class ModelInfo(BaseModel):
    """A selectable model. Everything the UI shows comes from here."""

    id: str
    provider: ProviderName
    label: str
    klass: ModelClass
    persona: PersonaLevel
    cost: Cost
    best_for: str
    ttft_ms_seed: int | None = None
    # Fraction of `scripts/gate_tool_selection.py`'s probes this model answers
    # with the right tool. **`None` means unmeasured, never "average"** — the
    # router may only prefer a model on evidence, and there was none of this
    # kind anywhere in the repo until now: the only tool measurement that
    # existed ran `qwen2.5:7b` alone, and CLAUDE.md's "all five models pick
    # open_app correctly 6/6" was a manual probe that left no script behind.
    # Same discipline as `ttft_ms_seed`, `best_for` and `cost`: measured or blank.
    tool_score: float | None = None
    caveat: str | None = None
    local: bool = False
    context_tokens: int = 8192
    # Sampling temperature, opt-in per model. `None` means "send nothing and let
    # the provider default apply" — which is required, not merely tidy: GPT-5
    # and the other reasoning models reject any value but 1.0, and `openai.py`
    # forwards whatever it is given. Set this only where it was measured.
    temperature: float | None = None
    # A third party's published score for this model (Artificial Analysis'
    # intelligence index, as OpenRouter reports it), carried verbatim.
    #
    # **Not a measurement made here, and it must never stand in for one.** It
    # orders the adoption queue — which candidate is worth spending scarce
    # free-tier quota on first — and nothing else. `tool_score` and
    # `ttft_ms_seed` stay `None` until this machine has actually measured them.
    benchmark_index: float | None = None
    # Whether the endpoint may train on what is sent to it. A property of the
    # *endpoint*, not of the model: OpenRouter's free tier can route to
    # providers that do, and while the account holder can opt out, this code
    # cannot assert that they have. `core/router.py` keeps turns carrying the
    # user's own files away from these — see `carries_user_content`.
    trains_on_data: bool = False
    # Found by asking the provider what it sells, rather than written down here
    # after being measured. A discovered model can be chosen by hand but is
    # never routed to automatically — see `by_class`.
    discovered: bool = False


SMART_ID = "smart"

CATALOG: list[ModelInfo] = [
    # ── local ────────────────────────────────────────────────────────
    ModelInfo(
        # Ollama's `qwen2.5:7b` tag already resolves to 7.6B at Q4_K_M — the
        # long `7b-instruct-q4_K_M` form names the same weights and is not what
        # `ollama list` reports, so matching on it greyed the model out.
        id="qwen2.5:7b",
        provider=ProviderName.OLLAMA,
        label="Qwen2.5 7B (local)",
        klass=ModelClass.BALANCED,
        # Measured, 8 runs of `eval_quality.py --category honesty`: under FULL
        # this model invented a breakfast every single time ("Oatmeal.", "Bagel
        # with cream cheese.") when asked what the user ate. Under MINIMAL it
        # declined all 8. The battery scores 41/41 on MINIMAL against 40/41 on
        # FULL. Character is not worth a model that fabricates.
        persona=PersonaLevel.MINIMAL,
        cost=Cost.FREE,
        best_for=(
            "The default. Fastest model here, crisp and consistent, and the "
            "best local one at following an exact format."
        ),
        ttft_ms_seed=325,
        # Mean of 4 runs, `gate_tool_selection.py` at 28 tools / 26 probes
        # (2026-08-13): 0.88, 0.88, 0.81, 0.85. **Read the spread, not the
        # mean** — see `UNMEASURED_TOOL_SCORE` in router.py. On one run this
        # model scored above `gpt-5.4-nano` and that difference did not survive
        # re-measurement.
        tool_score=0.86,
        caveat=(
            "Will describe things that do not exist as though they were real — "
            "a made-up npm package, a made-up git flag. Check anything obscure."
        ),
        local=True,
    ),
    ModelInfo(
        id="qwen3.5:4b",
        provider=ProviderName.OLLAMA,
        label="Qwen3.5 4B (local, fast)",
        klass=ModelClass.FAST,
        # Measured: the full persona makes this model hostile and prone to
        # inventing context. It gets the stripped prompt.
        persona=PersonaLevel.MINIMAL,
        cost=Cost.FREE,
        best_for=(
            "Lowest VRAM here. Declines unanswerable questions more reliably "
            "than the 7B, so useful as a second opinion on obscure facts."
        ),
        # Slower than the 7B despite being smaller: it is a reasoning model and
        # pays for that even with think=false. Still inside the 700ms gate.
        ttft_ms_seed=560,
        caveat=(
            "Rambles, sometimes quotes its own instructions back at you, and "
            "occasionally states a confident falsehood about a real topic. "
            "Slower than the 7B despite being smaller."
        ),
        local=True,
    ),
    # ── Gemini ───────────────────────────────────────────────────────
    ModelInfo(
        id="gemini-flash-lite-latest",
        provider=ProviderName.GEMINI,
        label="Gemini Flash Lite",
        klass=ModelClass.FAST,
        persona=PersonaLevel.FULL,
        cost=Cost.LOW,
        best_for="Quick questions, rewriting, summarising. Fastest cloud option here.",
        ttft_ms_seed=1236,
        context_tokens=32768,
    ),
    ModelInfo(
        id="gemini-3.6-flash",
        provider=ProviderName.GEMINI,
        label="Gemini 3.6 Flash",
        klass=ModelClass.BALANCED,
        persona=PersonaLevel.FULL,
        cost=Cost.LOW,
        best_for="General work with more depth than Flash Lite, still cheap.",
        ttft_ms_seed=2567,
        context_tokens=32768,
    ),
    ModelInfo(
        id="gemini-3.1-pro-preview",
        provider=ProviderName.GEMINI,
        label="Gemini 3.1 Pro",
        klass=ModelClass.SMART,
        persona=PersonaLevel.FULL,
        cost=Cost.HIGH,
        best_for="Hard reasoning and long documents.",
        ttft_ms_seed=None,
        caveat="Returned HTTP 429 on this key — the free tier rate-limits it quickly.",
        context_tokens=32768,
    ),
    # ── OpenAI ───────────────────────────────────────────────────────
    # The two below were discovered by `providers/discovery.py` and adopted on
    # evidence, by `scripts/measure_models.py` — 83 honesty probes and TTFT
    # over three warm turns each. They are curated, and therefore routable,
    # because somebody measured them; that is the only thing that qualifies a
    # model for Smart mode.
    #
    #   | model         | TTFT   | battery | fabricated | over-refused |
    #   |---------------|--------|---------|------------|--------------|
    #   | gpt-5.4-nano  |  700ms |   76/83 |          0 |            0 |
    #   | gpt-5.4-mini  |  960ms |   78/83 |          2 |            0 |
    #   | gpt-5.6-luna  | 1177ms |   74/83 |          3 |            1 |  rejected
    #   | o4-mini       | 1619ms |   69/83 |          7 |            2 |  rejected
    #
    # **The newest model lost.** `gpt-5.6-luna` and `o4-mini` both failed the
    # `grounded` category — the control group, plain facts they should simply
    # know — so neither is here. Reading the aggregate alone would have adopted
    # luna at 74/83; the same mistake the `qwen3.5:4b` reversal records.
    ModelInfo(
        id="gpt-5.4-nano",
        provider=ProviderName.OPENAI,
        label="GPT-5.4 nano",
        klass=ModelClass.FAST,
        persona=PersonaLevel.FULL,
        cost=Cost.LOW,
        best_for=(
            "The quickest cloud model measured here, and the only one that "
            "fabricated nothing at all across 83 probes."
        ),
        ttft_ms_seed=700,
        # Mean of 4 runs (2026-08-13): 0.92, 0.88, 0.92, 0.85. A single
        # earlier run put this at 0.79 and a routing rule was briefly built on
        # it; the rule is gone and the run was noise.
        tool_score=0.89,
        context_tokens=32768,
    ),
    ModelInfo(
        id="gpt-5.4-mini",
        provider=ProviderName.OPENAI,
        label="GPT-5.4 mini",
        klass=ModelClass.BALANCED,
        persona=PersonaLevel.FULL,
        cost=Cost.LOW,
        best_for=(
            "Best honesty score of anything measured here, and still under a "
            "second to first token."
        ),
        ttft_ms_seed=960,
        # Mean of 4 runs (2026-08-13): 0.88, 0.88, 0.88, 0.92 — the steadiest
        # of the three, and still inside every other model's spread.
        tool_score=0.89,
        context_tokens=32768,
    ),
    ModelInfo(
        id="gpt-4.1-mini",
        provider=ProviderName.OPENAI,
        label="GPT-4.1 mini",
        klass=ModelClass.FAST,
        persona=PersonaLevel.FULL,
        cost=Cost.LOW,
        best_for="Fast, reliable general answers. The quickest OpenAI option measured.",
        ttft_ms_seed=1726,
        context_tokens=32768,
    ),
    ModelInfo(
        id="gpt-4o",
        provider=ProviderName.OPENAI,
        label="GPT-4o",
        klass=ModelClass.BALANCED,
        persona=PersonaLevel.FULL,
        cost=Cost.MEDIUM,
        best_for="Solid all-rounder, and the vision model for screen questions.",
        ttft_ms_seed=None,
        context_tokens=32768,
    ),
    ModelInfo(
        id="gpt-5",
        provider=ProviderName.OPENAI,
        label="GPT-5",
        klass=ModelClass.SMART,
        persona=PersonaLevel.FULL,
        cost=Cost.HIGH,
        best_for="Hardest reasoning, multi-step planning, and code.",
        ttft_ms_seed=2434,
        context_tokens=32768,
    ),
    ModelInfo(
        id="gpt-5-mini",
        provider=ProviderName.OPENAI,
        label="GPT-5 mini",
        klass=ModelClass.BALANCED,
        persona=PersonaLevel.FULL,
        cost=Cost.MEDIUM,
        best_for="GPT-5 reasoning at lower cost.",
        ttft_ms_seed=2446,
        caveat="Measured no faster than full GPT-5 — it saves money, not time.",
        context_tokens=32768,
    ),
]

_BY_ID = {m.id: m for m in CATALOG}

# ── discovered models ─────────────────────────────────────────────────
# `CATALOG` above is measured knowledge: latency on this machine, which models
# fabricate, which reject a temperature. `providers/discovery.py` asks the
# vendors what else the account can reach, and the answer lands here — beside
# the catalog, never merged into it.
#
# That separation is the whole design. The user chose "hand-pick only": a
# discovered model can be selected deliberately, but Smart mode keeps routing
# among the ones with measured behaviour, so what happens when you press send
# never changes underneath you. `get` and `require` read the overlay so an
# explicit choice resolves; `by_class` — which is the router's only way to
# reach for a model — does not. The rule is a property of the data structure
# rather than a flag someone has to remember to check.

_DISCOVERED: dict[str, ModelInfo] = {}


def set_discovered(models: Iterable[ModelInfo]) -> None:
    """Replace what the providers said they offer.

    A curated id always wins: `gpt-5` appearing in both keeps its measured
    latency and its caveat rather than being overwritten by a bare listing.
    """
    _DISCOVERED.clear()
    for info in models:
        if info.id not in _BY_ID:
            _DISCOVERED[info.id] = info


def discovered() -> list[ModelInfo]:
    return list(_DISCOVERED.values())


#: Models this machine has measured *itself*, at runtime, and which passed.
#:
#: The middle ground between `CATALOG` and `_DISCOVERED`, and the only reason
#: it can exist: `providers/adoption.py` runs the same `grounded` probes that
#: rejected `gpt-5.6-luna` and `o4-mini`, and only a clean sweep lands a model
#: here. So this is not "discovered models the router is allowed to use after
#: all" — it is the measurement requirement being met by a scheduler instead of
#: by a person reading a transcript. A model that fails, or has not been
#: measured yet, stays in `_DISCOVERED` and stays unroutable.
_ADOPTED: dict[str, ModelInfo] = {}


def adopt(info: ModelInfo) -> None:
    """Record a model as measured-and-passed, making it routable.

    Curated ids still win: an entry already in `CATALOG` carries measurements
    this cannot improve on.
    """
    if info.id in _BY_ID:
        return
    _ADOPTED[info.id] = info


def unadopt(model_id: str) -> None:
    """Drop an adoption — used when a free model expires or disappears."""
    _ADOPTED.pop(model_id, None)


def adopted() -> list[ModelInfo]:
    return list(_ADOPTED.values())


def clear_adopted() -> None:
    """Tests only. The overlay is process-global, like `_DISCOVERED`."""
    _ADOPTED.clear()


def all_models() -> list[ModelInfo]:
    """Everything selectable: measured first, then adopted, then found."""
    seen = {m.id for m in CATALOG}
    adopted_only = [m for m in _ADOPTED.values() if m.id not in seen]
    seen |= {m.id for m in adopted_only}
    return [*CATALOG, *adopted_only, *(m for m in _DISCOVERED.values() if m.id not in seen)]


class ModelAvailability(BaseModel):
    """A catalog entry plus whether it can actually be used right now."""

    model: ModelInfo
    available: bool
    reason: str | None = None
    observed_ttft_ms: float | None = None


class ModelListing(BaseModel):
    """`models.list` result."""

    selected: str = SMART_ID
    # `core.router.RoutingBias` as a string — what Smart mode currently optimises
    # for. Kept as `str` so catalog does not import the router.
    bias: str = "quality"
    models: list[ModelAvailability] = Field(default_factory=list)


def get(model_id: str) -> ModelInfo | None:
    """Curated first, then adopted, then discovered.

    So an explicit choice always resolves, whichever tier it came from.
    """
    return _BY_ID.get(model_id) or _ADOPTED.get(model_id) or _DISCOVERED.get(model_id)


def require(model_id: str) -> ModelInfo:
    info = get(model_id)
    if info is None:
        known = ", ".join(sorted(_BY_ID))
        raise KeyError(f"Unknown model {model_id!r}. Known models: {known}.")
    return info


def by_class(klass: ModelClass) -> list[ModelInfo]:
    """The router's pool: **measured only** — curated, or adopted after passing.

    The property has not been weakened by adoption, it has been restated. What
    must never happen is Smart routing a turn to a model whose honesty nobody
    has checked, and `_ADOPTED` is populated by exactly one thing: a clean
    sweep of the `grounded` probes, the control group that has already rejected
    two models outright. A merely *discovered* model is still unreachable from
    here, and so is a rejected one.

    Reading `all_models()` here would undo all of it. `test_catalog.py` holds
    the line three ways — discovered, rejected, and adopted — and changing this
    to `all_models()` must fail the first two.
    """
    return [m for m in (*CATALOG, *_ADOPTED.values()) if m.klass is klass]


def local_models() -> list[ModelInfo]:
    return [m for m in CATALOG if m.local]


# The 4B scores better on the probe battery (92% against 79%) and this was
# briefly set to it on that basis. Reading real transcripts reversed the call:
#
#   - Asked why Einstein won the Nobel for relativity, the 4B answered that he
#     "never won the Nobel Prize" and that the 1921 physics prize "went instead
#     to Henri Poincare" — fluent, confident and entirely invented. The 7B gets
#     this right 5 times out of 5, in nearly identical words.
#   - The 4B hedges settled facts into mush: "Canberra is approximated as the
#     capital. It is an approximation since official status may vary by source."
#   - It recites its own system prompt at the user mid-refusal, and takes 60
#     words to say what the 7B says in eight.
#
# The 7B's weakness is narrower: it describes non-existent packages and flags
# as though they were real. That is on adversarial probes about obscure things,
# and `quality` bias routes substantive questions to cloud anyway. Its caveat
# says so in the picker.
#
# The lesson, recorded in CLAUDE.md: an aggregate score over single-turn probes
# is not a substitute for reading a conversation.
PREFERRED_LOCAL = "qwen2.5:7b"


def default_local(pulled: Iterable[str] | None = None) -> ModelInfo:
    """The local fallback. Prefers the instruction-tuned 7B.

    `pulled` is what Ollama actually has. Pass it whenever it is known: the 7B
    is a 4.7GB download that may not have finished, and returning a model that
    is not on disk turns the last-resort fallback into a second failure.
    """
    if pulled is None:
        return require(PREFERRED_LOCAL)

    on_disk = set(pulled)
    if PREFERRED_LOCAL in on_disk:
        return require(PREFERRED_LOCAL)
    for info in local_models():
        if info.id in on_disk:
            return info
    return require(PREFERRED_LOCAL)


def persona_for(model_id: str) -> PersonaLevel:
    """Persona level for a model; unknown ids get the safe, minimal prompt."""
    info = _BY_ID.get(model_id)
    return info.persona if info else PersonaLevel.MINIMAL


# ── availability ──────────────────────────────────────────────────────
# One resolver, used by both `models.list` and the router. They must never
# disagree: a picker that offers a model the router refuses to use, or greys out
# one the router happily picks, is the UI lying about what pressing send does.


def resolve_availability(
    pulled: Iterable[str],
    keys: Mapping[ProviderName, bool],
    health: HealthTracker | None = None,
) -> list[ModelAvailability]:
    """Every catalog entry with a live verdict and a reason fit to display."""
    on_disk = set(pulled)
    entries: list[ModelAvailability] = []

    for info in all_models():
        available, reason = _verdict(info, on_disk, keys)
        observed: float | None = None

        if health is not None:
            state = health.get(info.id)
            observed = state.observed_ttft_ms
            if available and not state.healthy():
                available = False
                reason = (
                    f"Failing right now — retrying in "
                    f"{int(state.cooldown_remaining_s())}s."
                )

        entries.append(
            ModelAvailability(
                model=info, available=available, reason=reason, observed_ttft_ms=observed
            )
        )
    return entries


def _verdict(
    info: ModelInfo, on_disk: set[str], keys: Mapping[ProviderName, bool]
) -> tuple[bool, str | None]:
    """Why a model can or cannot be used, in words the picker can show."""
    if info.local:
        if info.id in on_disk:
            return True, None
        return False, f"Not pulled yet. Run: ollama pull {info.id}"

    if not keys.get(info.provider, False):
        return False, f"No {PROVIDER_LABELS[info.provider]} API key stored. Add one in Settings."

    # A known 429 is a caveat shown in the tooltip, not a block — the free-tier
    # quota may have reset since it was last measured.
    return True, None


def usable_ids(entries: Iterable[ModelAvailability]) -> set[str]:
    """The ids the router is allowed to choose from."""
    return {e.model.id for e in entries if e.available}
