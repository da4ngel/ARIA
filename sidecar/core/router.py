"""Smart model selection (BUILD_SPEC §9.7).

The router returns a *decision*, never performs the call. That keeps it pure and
testable: `test_router.py` asserts routing over a labelled message set without
touching a network.

**Bias is a setting, not a constant.** Local TTFT is 491ms against 1236ms for the
fastest cloud option, so cloud is 2.5-11x slower — the cost is the network
round-trip, not the model. But local `qwen3.5:4b` answers badly enough that
Phase 1.5 exists at all, so speed is not automatically the right trade. Eyaas
chose `QUALITY` for text.

Phase 2 will almost certainly need `FASTEST`: §10 budgets ~1000ms end-to-end for
voice and every cloud option blows that on the network hop alone. Rule 10
forbids refactoring this module then, so the knob exists now and voice flips a
value instead.
"""

from __future__ import annotations

import re
from enum import StrEnum

import structlog
from pydantic import BaseModel

from sidecar.providers import catalog
from sidecar.providers.catalog import ModelClass, ModelInfo
from sidecar.providers.health import HealthTracker

log = structlog.get_logger(__name__)


class RoutingBias(StrEnum):
    """How much latency the user will trade for a better answer."""

    FASTEST = "fastest"  # local unless the turn clearly needs more
    BALANCED = "balanced"  # cloud for real work, local for conversation
    QUALITY = "quality"  # cloud unless the turn is trivial or private


class RouteReason(BaseModel):
    """Why this model. Surfaced in the UI so routing is never a black box."""

    stage: str
    detail: str


class RouteDecision(BaseModel):
    model: ModelInfo
    reason: RouteReason
    fallbacks: list[ModelInfo] = []


# ── signals ───────────────────────────────────────────────────────────

# Verbs that imply real work rather than conversation (§9.7 stage 3).
_DEEP_VERBS = re.compile(
    r"\b(analys|analyz|compar|plan|strateg|debug|refactor|implement|draft|"
    r"review|summaris|summariz|translat|design|architect|optimis|optimiz|"
    r"research|investigat|explain how|walk me through)\w*",
    re.IGNORECASE,
)

_CODE_HINTS = re.compile(
    r"(```|\bfunction\b|\bclass\b|\bdef \b|\bimport \b|\bSELECT \b|"
    r"\berror\b|\bstack trace\b|\btraceback\b|\bregex\b|\bAPI\b)",
    re.IGNORECASE,
)

_THINK_HARD = re.compile(r"\b(think hard|think carefully|be thorough|deep dive)\b", re.IGNORECASE)

_SEQUENCED = re.compile(r"\b(and then|after that|then\b.*\bthen\b|first.*then)", re.IGNORECASE)

# Content that must never leave the machine (§9.7 stage 2, §11).
_PRIVATE = re.compile(
    r"\b(my file|my document|this file|clipboard|screenshot|my screen|"
    r"what am i looking at|my password|my email|my calendar)\b",
    re.IGNORECASE,
)

# A closed vocabulary on purpose. Under QUALITY every ambiguous turn goes to
# cloud, so "trivial" has to mean *definitely* trivial — a greeting or an
# acknowledgement, not merely a short question.
_TRIVIAL = re.compile(
    r"^\s*(hi|hey|hello|yo|sup|hiya|thanks|thank you|thx|ty|ok|okay|kk|k|cool|"
    r"nice|great|got it|sure|yes|yeah|yep|no|nope|nah|nvm|never mind|bye|"
    r"goodbye|goodnight|good night|good morning|morning|lol|haha|hm+|ah|oh|"
    r"wow|damn|right)[\s!.,?…]*$",
    re.IGNORECASE,
)

SHORT_MESSAGE_CHARS = 60
LONG_MESSAGE_CHARS = 400


def is_trivial(message: str) -> bool:
    """A greeting or acknowledgement — nothing a 4B model can get wrong."""
    return bool(_TRIVIAL.match(message))


def needs_deep_model(message: str, step: int = 0) -> bool:
    """Reasoning, code, or a multi-step request: the `smart` class earns its cost."""
    return bool(
        _THINK_HARD.search(message)
        or step >= 3
        or _CODE_HINTS.search(message)
        or _SEQUENCED.search(message)
    )


class Router:
    """Chooses a model for a turn."""

    def __init__(self, health: HealthTracker, bias: RoutingBias = RoutingBias.QUALITY) -> None:
        self._health = health
        self._bias = bias

    @property
    def bias(self) -> RoutingBias:
        return self._bias

    def set_bias(self, bias: RoutingBias) -> None:
        self._bias = bias
        log.info("router.bias_changed", bias=str(bias))

    def choose(
        self,
        message: str,
        *,
        selected: str = catalog.SMART_ID,
        available: set[str] | None = None,
        step: int = 0,
    ) -> RouteDecision:
        """Pick a model.

        `selected` is the user's choice — a model id, or "smart" to decide here.
        `available` is the set of currently usable ids, from
        `catalog.resolve_availability`; None means "assume everything works",
        which is only correct in tests.
        `step` is the agent-loop step (Phase 6); >=3 implies a hard task.
        """
        usable = self._usable(available)

        # Stage 1 — explicit choice always wins, including over privacy: the
        # user picking a cloud model IS the consent (§9.7 stage 1).
        if selected != catalog.SMART_ID:
            return self._explicit(selected, usable)

        # Stage 2 — privacy. Never leaves the machine, at any bias.
        if _PRIVATE.search(message):
            return self._local(
                usable, "This mentions your files or screen, so it stayed on this machine."
            )

        # Stage 3 — no cloud reachable.
        if not any(not catalog.require(m).local for m in usable):
            return self._local(usable, "No cloud provider is available right now.")

        return self._by_bias(message, usable, step)

    # ── per-bias policy ─────────────────────────────────────────────────

    def _by_bias(self, message: str, usable: set[str], step: int) -> RouteDecision:
        if self._bias is RoutingBias.QUALITY:
            return self._quality_first(message, usable, step)
        if self._bias is RoutingBias.BALANCED:
            return self._balanced(message, usable, step)
        return self._fastest(message, usable, step)

    def _quality_first(self, message: str, usable: set[str], step: int) -> RouteDecision:
        """Cloud unless the turn is trivial. The default."""
        if is_trivial(message):
            return self._local(usable, "Just a greeting — answered locally, instantly.")
        if needs_deep_model(message, step):
            return self._cloud(usable, ModelClass.SMART, "This needs careful reasoning.")
        return self._cloud(usable, ModelClass.FAST, "Answered by a cloud model for quality.")

    def _balanced(self, message: str, usable: set[str], step: int) -> RouteDecision:
        """Cloud for real work, local for conversation."""
        if needs_deep_model(message, step):
            return self._cloud(usable, ModelClass.SMART, "This needs careful reasoning.")
        if _DEEP_VERBS.search(message) or len(message) >= LONG_MESSAGE_CHARS:
            return self._cloud(usable, ModelClass.FAST, "Needs more than a quick answer.")
        return self._local(usable, "Conversational turn — answered locally, faster.")

    def _fastest(self, message: str, usable: set[str], step: int) -> RouteDecision:
        """Local unless the turn clearly needs more. What voice will want."""
        if _THINK_HARD.search(message) or step >= 3:
            return self._cloud(usable, ModelClass.SMART, "You asked for a careful answer.")
        if len(message) <= SHORT_MESSAGE_CHARS and not _DEEP_VERBS.search(message):
            return self._local(usable, "Short question — answered locally, faster.")
        if _CODE_HINTS.search(message) or _SEQUENCED.search(message):
            return self._cloud(usable, ModelClass.SMART, "Looks like code or a multi-step task.")
        if _DEEP_VERBS.search(message) or len(message) >= LONG_MESSAGE_CHARS:
            return self._cloud(usable, ModelClass.FAST, "Needs more than a quick answer.")
        return self._local(usable, "Ordinary turn — answered locally.")

    # ── helpers ─────────────────────────────────────────────────────────

    def _usable(self, available: set[str] | None) -> set[str]:
        ids = {m.id for m in catalog.CATALOG} if available is None else set(available)
        return {i for i in ids if self._health.is_usable(i)}

    def _explicit(self, selected: str, usable: set[str]) -> RouteDecision:
        info = catalog.get(selected)
        if info is None:
            return self._local(usable, f"{selected!r} is not a known model, so this ran locally.")
        if info.id in usable:
            return RouteDecision(
                model=info,
                reason=RouteReason(stage="explicit", detail="You picked this model."),
                fallbacks=[self._best_local(usable)] if not info.local else [],
            )
        return self._local(usable, f"{info.label} is unavailable right now, so this ran locally.")

    def _rank(self, candidates: list[ModelInfo]) -> list[ModelInfo]:
        """Fastest observed first — the ranking self-corrects as turns land."""
        return sorted(candidates, key=lambda m: self._health.latency_for(m.id, m.ttft_ms_seed))

    def _best_local(self, usable: set[str]) -> ModelInfo:
        """The local model to fall back to. Prefers the instruction-tuned 7B,
        but only among models Ollama has actually pulled."""
        return catalog.default_local({m.id for m in catalog.local_models() if m.id in usable})

    def _cloud(self, usable: set[str], klass: ModelClass, detail: str) -> RouteDecision:
        candidates = [m for m in catalog.by_class(klass) if m.id in usable and not m.local]
        if not candidates:
            # Nothing in the requested class; try any cloud model before local.
            candidates = [m for m in catalog.CATALOG if m.id in usable and not m.local]
        if not candidates:
            return self._local(usable, f"{detail} No cloud model was reachable.")

        ranked = self._rank(candidates)
        # Siblings first, then local as the last resort (§9.7 stage 7).
        return RouteDecision(
            model=ranked[0],
            reason=RouteReason(stage="cloud", detail=detail),
            fallbacks=[*ranked[1:], self._best_local(usable)],
        )

    def _local(self, usable: set[str], detail: str) -> RouteDecision:
        model = self._best_local(usable)
        others = self._rank(
            [m for m in catalog.local_models() if m.id in usable and m.id != model.id]
        )
        return RouteDecision(
            model=model,
            reason=RouteReason(stage="local", detail=detail),
            fallbacks=others,
        )
