"""What the cloud providers will actually sell us today.

The hand-written `catalog` is measured knowledge — latency on this machine,
which models fabricate, which reject a temperature. It cannot know that the
account gained `gpt-5.6` last week. This fills that gap and nothing else.

**Discovery is a filtering problem, not a fetching one.** Measured against the
live APIs: OpenAI returns 124 models and Gemini 58, and most of them cannot hold
a conversation at all — embeddings, Whisper, TTS, image, Sora, moderation.
Gemini's own `generateContent` flag is *not* a sufficient filter either: it is
set on Lyria (music), Nano Banana (image), the TTS previews, the robotics
models and Deep Research. So both lists are filtered by name on the way out.

Parsing is pure and separate from fetching, so the filters are tested against
the real payloads captured in `tests/fixtures/` rather than against a mock that
agrees with whatever the filter happens to do.

Nothing here invents a number. `best_for`, `caveat`, `ttft_ms_seed` and `cost`
come from measurement, and a discovered model has none, so it gets none.
"""

from __future__ import annotations

import asyncio
import re
from datetime import date
from typing import Any

import httpx
import structlog

from sidecar.core.context import PersonaLevel
from sidecar.providers.catalog import Cost, ModelClass, ModelInfo, ProviderName
from sidecar.providers.credentials import CredentialKey, get_key

log = structlog.get_logger(__name__)

OPENAI_MODELS_URL = "https://api.openai.com/v1/models"
#: Public -- no key needed, so the picker can show what a key *would* reach.
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
GEMINI_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models"
FETCH_TIMEOUT_S = 15.0

# A discovered model's context window is unknown for OpenAI, which returns no
# capability data at all. This is the same figure every curated cloud entry
# carries, and it is used as a `min()` cap on the roll-up budget
# (`conversation.py:837`) — so erring low is safe and erring high is not.
ASSUMED_CONTEXT_TOKENS = 32768


# ── OpenAI ────────────────────────────────────────────────────────────
# The payload is `{id, created, owned_by}` and nothing else: no context window,
# no modality, no capability flags. Every judgement below is therefore made on
# the id, which is why the fixture test matters.

#: Any id containing one of these as a `-`-delimited segment is not a chat
#: model. Checked segment-wise rather than as a substring so that a future
#: `gpt-6-imagex` is not silently dropped for containing "image".
_OPENAI_REJECT_SEGMENTS = frozenset(
    {
        "embedding",
        "embeddings",
        "tts",
        "whisper",
        "transcribe",
        "image",
        "audio",
        "realtime",
        "moderation",
        "sora",
        "dall",
        "search",
        "codex",
        "instruct",
        "diarize",
    }
)

#: Families that can chat. Anything outside them is not ours to guess at.
_OPENAI_KEEP_PREFIXES = ("gpt-", "o1", "o3", "o4", "chat-")

#: Superseded families. They still answer, but listing a dozen dead ids pushes
#: the live ones off the bottom of the picker.
_OPENAI_LEGACY_PREFIXES = ("gpt-3.5", "gpt-4-", "babbage", "davinci")

#: `gpt-4o-2024-08-06`, and the older four-digit `gpt-4-0613` form.
_DATED = re.compile(r"^(?P<base>.+?)-(?:\d{4}-\d{2}-\d{2}|\d{4})$")


def _openai_is_chat(model_id: str) -> bool:
    segments = set(model_id.split("-"))
    if segments & _OPENAI_REJECT_SEGMENTS:
        return False
    if not model_id.startswith(_OPENAI_KEEP_PREFIXES):
        return False
    return not model_id.startswith(_OPENAI_LEGACY_PREFIXES)


def _undated(model_id: str, known: set[str]) -> bool:
    """Whether this id is a dated snapshot of something already in the list.

    Only when the base id is *also* present: `gpt-5.2-2025-12-11` goes because
    `gpt-5.2` is there to stand for it, but a snapshot with no undated alias is
    the only way to reach that model and stays.
    """
    match = _DATED.match(model_id)
    return not (match and match.group("base") in known)


def _openai_class(model_id: str) -> ModelClass:
    if any(s in model_id for s in ("nano", "mini", "lite")):
        return ModelClass.FAST
    # The o-series is the reasoning line — `o3` is not a mid-range model just
    # because its name carries no adjective.
    if "pro" in model_id.split("-") or re.fullmatch(r"o\d", model_id):
        return ModelClass.SMART
    return ModelClass.BALANCED


def _openai_label(model_id: str) -> str:
    """`gpt-5.6-luna` -> `GPT-5.6 Luna`, `gpt-4o` -> `GPT-4o`.

    Cosmetic and never load-bearing. The hyphen is kept where a version number
    follows and turned into a space where a word does, which is how these are
    written everywhere else.
    """
    head, *rest = model_id.split("-")
    out = head.upper() if head.startswith(("gpt", "o")) else head.capitalize()
    for word in rest:
        joiner = "-" if word[:1].isdigit() else " "
        out += joiner + (word if word[:1].isdigit() else word.capitalize())
    return out


def parse_openai(payload: dict[str, Any]) -> list[ModelInfo]:
    """Chat models from a `GET /v1/models` body."""
    ids = {
        entry["id"]
        for entry in payload.get("data", [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    keep = sorted(i for i in ids if _openai_is_chat(i) and _undated(i, ids))
    return [
        ModelInfo(
            id=model_id,
            provider=ProviderName.OPENAI,
            label=_openai_label(model_id),
            klass=_openai_class(model_id),
            # Nothing has been measured about this model's honesty, and the
            # full persona is what made a *measured* model invent breakfasts.
            persona=PersonaLevel.MINIMAL,
            cost=Cost.UNKNOWN,
            best_for="",
            ttft_ms_seed=None,
            context_tokens=ASSUMED_CONTEXT_TOKENS,
            discovered=True,
        )
        for model_id in keep
    ]


# ── Gemini ────────────────────────────────────────────────────────────
# Much richer: displayName, description, inputTokenLimit, thinking, and the
# temperature bounds. Enough to fill in real values instead of assuming them.

_GEMINI_REJECT_SUBSTRINGS = (
    "tts",
    "image",
    "nano-banana",
    "lyria",
    "robotics",
    "computer-use",
    "deep-research",
    "embedding",
    "aqa",
    "gemma",
    "antigravity",
    "customtools",
    "veo",
)


#: `gemini-2.0-flash-001` beside `gemini-2.0-flash`, and
#: `gemini-3.1-flash-lite-preview` beside the shipped `gemini-3.1-flash-lite`.
#: Both name a model already in the list under its plain id.
_GEMINI_SUPERSEDED = re.compile(r"^(?P<base>.+?)-(?:\d{3}|preview|latest)$")


def _gemini_is_chat(name: str, methods: list[str]) -> bool:
    if "generateContent" not in methods:
        return False
    return not any(bad in name for bad in _GEMINI_REJECT_SUBSTRINGS)


def _gemini_is_duplicate(name: str, known: set[str]) -> bool:
    """A pinned or preview alias of something already listed plainly.

    Only when the plain id is present: `gemini-3-flash-preview` has no shipped
    equivalent, so dropping it would remove the model rather than de-duplicate
    it. Same reasoning as `_undated` on the OpenAI side.
    """
    match = _GEMINI_SUPERSEDED.match(name)
    return bool(match and match.group("base") in known)


def _gemini_class(name: str) -> ModelClass:
    if "lite" in name or "nano" in name:
        return ModelClass.FAST
    if "pro" in name or "ultra" in name:
        return ModelClass.SMART
    return ModelClass.BALANCED


def parse_gemini(payload: dict[str, Any]) -> list[ModelInfo]:
    """Chat models from a `GET /v1beta/models` body."""
    chat: list[tuple[str, dict[str, Any]]] = []
    for entry in payload.get("models", []):
        if not isinstance(entry, dict):
            continue
        model_id = str(entry.get("name", "")).removeprefix("models/")
        methods = entry.get("supportedGenerationMethods") or []
        if model_id and _gemini_is_chat(model_id, methods):
            chat.append((model_id, entry))

    known = {model_id for model_id, _ in chat}

    found: list[ModelInfo] = []
    for model_id, entry in chat:
        if _gemini_is_duplicate(model_id, known):
            continue

        found.append(
            ModelInfo(
                id=model_id,
                provider=ProviderName.GEMINI,
                label=str(entry.get("displayName") or model_id),
                klass=_gemini_class(model_id),
                persona=PersonaLevel.MINIMAL,
                cost=Cost.UNKNOWN,
                # The vendor's own one-liner is a fact about the model, not a
                # claim about how it behaves here. Measured notes stay empty.
                best_for=str(entry.get("description") or "").split(".")[0][:160],
                ttft_ms_seed=None,
                # Real, unlike the OpenAI side.
                context_tokens=int(entry.get("inputTokenLimit") or ASSUMED_CONTEXT_TOKENS),
                # CLAUDE.md: never set a temperature on a reasoning model — they
                # reject any value but their own default, and `gemini.py`
                # forwards whatever it is handed. The payload says which these
                # are, so the rule enforces itself rather than being remembered.
                temperature=None,
                discovered=True,
            )
        )
    return sorted(found, key=lambda m: m.id)


# ── OpenRouter ────────────────────────────────────────────────────
# The richest payload of the three, and the only one that states a price. That
# matters: `Cost.FREE` here is read, not guessed, which is why it does not
# breach "nothing invents a measurement" the way a hand-assigned cost would.
#
# Measured against the live endpoint on 2026-08-19: **414 models, 19 free, 16
# of those tool-capable.** The plan for this work assumed four, so the filters
# below are doing considerably more work than expected.

#: A meta-endpoint, not a model: it forwards to whichever free model it likes
#: at the time. Measuring it would produce a score attributable to nothing, and
#: adopting it would put an unmeasured model into Smart's pool through the back
#: door -- the exact property `by_class` exists to prevent.
_OPENROUTER_REJECT_IDS = frozenset({"openrouter/free"})


def _openrouter_is_free(entry: dict[str, Any]) -> bool:
    """Free on **both** sides of the meter.

    `pricing.prompt == "0"` alone would admit a model that is free to send to
    and charged to hear back from, which is not free in any sense the user
    means. Nothing in the live listing is currently shaped that way; the check
    costs nothing and stops it becoming a surprise on a bill.
    """
    pricing = entry.get("pricing") or {}
    return str(pricing.get("prompt")) == "0" and str(pricing.get("completion")) == "0"


def _openrouter_benchmark(entry: dict[str, Any]) -> float | None:
    """Artificial Analysis' published intelligence index, if OpenRouter has one.

    A third party's number about the model, carried verbatim -- never treated
    as a measurement made here. It orders the adoption queue so scarce free-tier
    quota is spent on the most promising candidate first, and it is *not* a
    substitute for the gate: the queue decides what is measured, the `grounded`
    probes decide what is adopted.
    """
    benchmarks = entry.get("benchmarks") or {}
    aa = benchmarks.get("artificial_analysis") or {}
    raw = aa.get("intelligence_index")
    return float(raw) if isinstance(raw, int | float) else None


def _openrouter_expired(entry: dict[str, Any], today: date) -> bool:
    """Free models come and go, and OpenRouter says when.

    An expired id 404s mid-turn, which reads as ARIA being broken rather than
    as a model having been retired. One in the live listing expires five days
    from today.
    """
    raw = entry.get("expiration_date")
    if not isinstance(raw, str):
        return False
    try:
        return date.fromisoformat(raw) < today
    except ValueError:
        return False


#: Bucketing a published index, not measuring anything. The boundaries come
#: from where the live free listing actually clusters -- the nano/lightning end
#: sits at 14-24, the mid-size open weights at 25-38, and only `glm-5.2` (52.6)
#: reaches what this project would call SMART.
_BENCHMARK_FAST_BELOW = 25.0
_BENCHMARK_SMART_FROM = 45.0


def _openrouter_class(model_id: str, benchmark: float | None) -> ModelClass:
    """Prefer the number; fall back to what the vendor called it.

    The other two parsers have only the name to go on. Here a stated benchmark
    is better evidence than the word "nano", so it wins where it exists.
    """
    if benchmark is not None:
        if benchmark < _BENCHMARK_FAST_BELOW:
            return ModelClass.FAST
        if benchmark >= _BENCHMARK_SMART_FROM:
            return ModelClass.SMART
        return ModelClass.BALANCED

    name = model_id.lower()
    if any(word in name for word in ("nano", "mini", "lite", "flash", "-xs", "small")):
        return ModelClass.FAST
    if any(word in name for word in ("ultra", "-pro", "max", "large", "opus")):
        return ModelClass.SMART
    return ModelClass.BALANCED


def parse_openrouter(payload: dict[str, Any], *, today: date | None = None) -> list[ModelInfo]:
    """Free, tool-capable chat models from a `GET /api/v1/models` body.

    **Tool-capable is a hard filter, not a preference.** ARIA offers 41 tools
    and a model that cannot call them fails most of what it would be asked to
    do here -- and measuring one would spend scarce daily quota to learn
    something the payload already stated. The live listing has three free
    models without tools, and two of them are music generators, so this filter
    is also doing the job Gemini's `generateContent` flag failed to do.
    """
    now = today or date.today()
    found: list[ModelInfo] = []
    for entry in payload.get("data", []):
        if not isinstance(entry, dict):
            continue
        model_id = entry.get("id")
        if not isinstance(model_id, str) or model_id in _OPENROUTER_REJECT_IDS:
            continue
        if not _openrouter_is_free(entry):
            continue
        if "tools" not in (entry.get("supported_parameters") or []):
            continue
        if _openrouter_expired(entry, now):
            continue

        benchmark = _openrouter_benchmark(entry)
        found.append(
            ModelInfo(
                id=model_id,
                provider=ProviderName.OPENROUTER,
                label=str(entry.get("name") or model_id),
                klass=_openrouter_class(model_id, benchmark),
                # Unmeasured here, exactly like every other discovered model.
                persona=PersonaLevel.MINIMAL,
                # Read off the payload rather than assumed -- the one
                # discovered field in this file allowed to be a real value.
                cost=Cost.FREE,
                best_for=str(entry.get("description") or "").split(".")[0][:160],
                ttft_ms_seed=None,
                context_tokens=int(entry.get("context_length") or ASSUMED_CONTEXT_TOKENS),
                temperature=None,
                benchmark_index=benchmark,
                reasoning_mandatory=bool(
                    (entry.get("reasoning") or {}).get("mandatory", False)
                ),
                # A property of the endpoint, not of the model. OpenRouter's
                # free tier may route to providers that train on what is sent;
                # the opt-out is the account holder's to set and this code
                # cannot assert it is on.
                trains_on_data=True,
                discovered=True,
            )
        )
    # Best first, so the adoption queue is already in the order it wants.
    return sorted(found, key=lambda m: (-(m.benchmark_index or 0.0), m.id))


# ── fetching ──────────────────────────────────────────────────────────
# Never on the turn path. §10 budgets ~1000ms end to end for voice and this is
# a network round-trip; callers run it at startup or from the refresh button.


async def _fetch(url: str, headers: dict[str, str], params: dict[str, str] | None = None) -> Any:
    async with httpx.AsyncClient(timeout=FETCH_TIMEOUT_S) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


async def discover_openai() -> list[ModelInfo]:
    key = get_key(CredentialKey.OPENAI)
    if not key:
        return []
    payload = await _fetch(OPENAI_MODELS_URL, {"Authorization": f"Bearer {key}"})
    return parse_openai(payload)


async def discover_gemini() -> list[ModelInfo]:
    key = get_key(CredentialKey.GEMINI)
    if not key:
        return []
    payload = await _fetch(GEMINI_MODELS_URL, {"x-goog-api-key": key}, {"pageSize": "200"})
    return parse_gemini(payload)


async def discover_openrouter() -> list[ModelInfo]:
    """No key required -- `/models` is public.

    So the picker can show what a key would reach *before* one is stored,
    which is the difference between "OpenRouter is empty" and "OpenRouter
    needs a key".
    """
    payload = await _fetch(OPENROUTER_MODELS_URL, {})
    return parse_openrouter(payload)


async def discover_all() -> list[ModelInfo]:
    """Everything both providers will answer with, or as much as is reachable.

    One provider being down, rate-limited or keyless must not cost the other
    its listing — a failure here degrades the picker, it does not break it.
    """
    sources = (
        (ProviderName.OPENAI, discover_openai()),
        (ProviderName.GEMINI, discover_gemini()),
        (ProviderName.OPENROUTER, discover_openrouter()),
    )
    # One sequence, so a provider cannot be added to the coroutines and
    # forgotten in the names -- the mismatch `strict=True` was catching after
    # the fact, moved to somewhere it cannot happen.
    results = await asyncio.gather(*(c for _, c in sources), return_exceptions=True)

    found: list[ModelInfo] = []
    for (provider, _), result in zip(sources, results, strict=True):
        if isinstance(result, BaseException):
            log.warning("discovery.failed", provider=str(provider), error=str(result))
            continue
        found.extend(result)
        log.info("discovery.found", provider=str(provider), count=len(result))
    return found
