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


#: What each conversation mode asks of the router. `None` means "leave the
#: user's own setting alone", which is most of them — a mode is a style, and
#: only two genuinely imply a different class of model.
#:
#: Research and Code want reach: each is the user declaring that the whole
#: conversation is the kind of turn `_DEEP_VERBS`/`_CODE_HINTS` try to infer
#: from wording, and a declaration is a cheaper signal than more regex.
#: Quick asks for FASTEST rather than forced-local — hard-forcing local makes
#: it answer a hard question badly, and brevity is never worth being wrong.
#:
#: None of this reaches the privacy stage: `choose` has already returned by
#: the time a bias is consulted, so **no mode can send something private to
#: the cloud.**
MODE_BIAS: dict[str, RoutingBias | None] = {
    "normal": None,
    "study": None,
    "research": RoutingBias.QUALITY,
    "quick": RoutingBias.FASTEST,
    "code": RoutingBias.QUALITY,
}


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
#
# The second line is the way people actually ask. Measured before it existed:
# "write me a python script to sort a file" matched none of these, so quality
# mode sent it to the cheapest cloud model. `write`/`build`/`fix` are only deep
# in company — "write it down", "fix the typo" are not — so they are paired
# with an object below rather than listed bare.
_DEEP_VERBS = re.compile(
    r"\b(analys|analyz|compar|plan|strateg|debug|refactor|implement|draft|"
    r"review|summaris|summariz|translat|design|architect|optimis|optimiz|"
    r"research|investigat|explain how|walk me through|troubleshoot|"
    r"rewrite|restructure|migrat|benchmark|diagnos)\w*",
    re.IGNORECASE,
)

#: Asking for code without using any of the words a parser would recognise.
#: This is the gap that sent "write me a python script" to Flash Lite.
_WRITES_CODE = re.compile(
    r"\b(write|build|create|make|generate|give me|show me)\b[^.?!]{0,40}?"
    r"\b(script|program|code|function|class|query|regex|snippet|app|"
    r"component|module|test|algorithm|command)\b",
    re.IGNORECASE,
)

_CODE_HINTS = re.compile(
    r"(```|\bfunction\b|\bclass\b|\bdef \b|\bimport \b|\bSELECT \b|"
    r"\berror\b|\bstack trace\b|\btraceback\b|\bregex\b|\bAPI\b|"
    # Named languages and runtimes, and the file extensions that stand in for
    # them. "sort a file in python" carries no keyword at all otherwise.
    r"\b(python|javascript|typescript|rust|golang|c\+\+|java|kotlin|swift|"
    r"sql|bash|powershell|react|django|fastapi|numpy|pandas)\b|"
    r"\.(py|ts|tsx|js|jsx|rs|go|java|sql|sh|ps1|css|html)\b|"
    r"\b(stack ?trace|exception|segfault|compile|runtime error|null pointer)\b)",
    re.IGNORECASE,
)

_THINK_HARD = re.compile(r"\b(think hard|think carefully|be thorough|deep dive)\b", re.IGNORECASE)

_SEQUENCED = re.compile(r"\b(and then|after that|then\b.*\bthen\b|first.*then)", re.IGNORECASE)

# Content that must never leave the machine (§9.7 stage 2, §11).
_PRIVATE = re.compile(
    r"\b(my file|my document|this file|clipboard|screenshot|my screen|"
    r"what am i looking at|my password|my email|my calendar|"
    # "what did I just copy" names the clipboard without using the word, and
    # it is how people actually ask. Belt and braces: `read_clipboard` is
    # marked `local_only`, so a turn that reaches it finishes locally whatever
    # this pattern decided — but staying local from the start is better than
    # switching models mid-turn.
    r"just cop(y|ied)|what i cop(y|ied)|i cop(y|ied)|copied earlier)\b",
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

#: A request to *do* something to the machine, rather than to talk about one.
#:
#: The router has never known that tools exist — it is regex over text and a
#: latency ranking, and nothing in it had heard of `set_volume`. That was
#: tolerable while every turn was a conversation, and it stopped being tolerable
#: at stage 0: a spoken turn is forced onto the local model whatever the bias
#: says, so **"increase the volume" could only ever be answered by the weakest
#: model in the catalog** no matter which one was chosen.
#:
#: Stage 0 exists for a measured reason (872ms to first audio locally against
#: 1707ms via Gemini, inside §10's ~1000ms budget), so it is narrowed rather
#: than deleted: conversation stays local and stays fast, commands route by
#: bias. The latency lands only on turns where something is supposed to happen,
#: and an action that silently does not happen costs far more than 800ms.
#:
#: Derived by hand rather than from the registry on purpose — importing
#: `sidecar.tools` here would couple routing to tool registration, and the
#: schemas already live in the stable prefix for KV-cache reasons. The test that
#: keeps it honest asserts every probe in `gate_tool_selection.py` matches.
#:
#: **Narrow beats broad here.** The first version listed the verbs bare, and
#: `write` promptly matched "write me a python script" — a request for prose
#: about code, not a command to the machine. So the ambiguous verbs are paired
#: with an object the way `_WRITES_CODE` pairs its own, and only words that
#: cannot mean anything else stand alone.
_TOOL_SHAPED = re.compile(
    # Settings and hardware. None of these words means anything conversational.
    r"\b(volume|louder|quieter|mute|unmute|wi-?fi|bluetooth|brightness"
    r"|clipboard|screenshot|shut ?down|reboot|restart|log ?out"
    r"|minimi[sz]e|maximi[sz]e)\b"
    # Starting and stopping programs. The lookaheads are the difference between
    # "close spotify" and "that was a close call".
    r"|\bopen(?!\s+(?:to|question|minded|source|ended|air|secret))\b"
    r"|\bclose(?!\s+(?:call|to|enough|shave|friend|second|my eyes))\b"
    r"|\b(launch|quit|kill|force[- ]?quit|uninstall|switch to|focus on"
    r"|bring up)\b"
    # Things about this machine's state.
    r"|\bhow much (memory|ram|space|storage|disk|battery)\b"
    r"|\b(ram|cpu|disk space|free space|battery)\b"
    r"|\b(memory|storage|space) (?:am i |is |i'm )?(?:using|used|free|left)\b"
    r"|\busing (?:all )?(?:my|the) (memory|ram|cpu)\b"
    # Acting on files. Paired with an object, or a bare extension.
    r"|\b(delete|rename|organi[sz]e)\b"
    r"|\b(move|copy|save|writ(?:e|ing)|read|creat(?:e|ing)|make|put)\b"
    r"[^.?!]{0,30}?\b(file|folder|directory|document|note|shortcut)\b"
    r"|\b(move|copy|save|rename|open|delete|read)\b[^.?!]{0,30}?"
    r"\.(txt|pdf|docx?|xlsx?|csv|png|jpe?g|md|zip|pptx?)\b"
    # Finding something on disk, as opposed to asking a question about the world.
    r"|\b(find|search for|look for|locate)\b[^.?!]{0,40}?"
    r"\b(file|folder|document|pdf|photo|picture|note|cv|resume|invoice"
    r"|receipt|spreadsheet|download|quotation)\b"
    # Places on disk, named as places rather than acted on.
    r"|\b(downloads?|documents?|desktop|folder|directory) folder\b"
    r"|\b(in|on|from|to) (?:my |the )?(downloads|documents|desktop)\b"
    r"|\bwhat(?:'s| is| are)?\s+in (?:my|the)\b"
    r"|\bwhere (?:is|are|did i put|can i find)\b"
    r"|\b(which|what) files?\b"
    # Memory.
    r"|\b(remember|forget|recall)\b",
    re.IGNORECASE,
)

#: Where an unmeasured model sorts on a tool-shaped turn. Middling on purpose:
#: promoting it would be preferring a model on no evidence, and demoting it
#: would freeze the catalog at whatever happened to be measured first.
UNMEASURED_TOOL_SCORE = 0.5

#: **Scores closer than this are the same score.** Measured 2026-08-13, four
#: runs of `gate_tool_selection.py` over one 26-probe set:
#:
#:     qwen2.5:7b     0.88  0.88  0.81  0.85
#:     gpt-5.4-nano   0.92  0.88  0.92  0.85
#:     gpt-5.4-mini   0.88  0.88  0.88  0.92
#:
#: Every model's own spread is ~0.07 and the gap between their means is ~0.03.
#: A single run of this measurement told a clean story — the local model beating
#: the fastest cloud one — and a routing rule was built on it before anyone ran
#: it twice. `eval_quality.py`'s docstring already says the thing that would
#: have prevented that: "read a one-probe difference between runs as variance".
#:
#: So the band is wider than the noise, and a model has to be *visibly* worse at
#: tools before latency stops deciding.
TOOL_SCORE_MARGIN = 0.1

SHORT_MESSAGE_CHARS = 60
LONG_MESSAGE_CHARS = 400


def is_trivial(message: str) -> bool:
    """A greeting or acknowledgement — nothing a 4B model can get wrong."""
    return bool(_TRIVIAL.match(message))


def is_tool_shaped(message: str) -> bool:
    """A request to act on the machine rather than to talk about something."""
    return bool(_TOOL_SHAPED.search(message))


def needs_deep_model(message: str, step: int = 0) -> bool:
    """Reasoning, code, or a multi-step request: the `smart` class earns its cost."""
    return bool(
        _THINK_HARD.search(message)
        or step >= 3
        or _CODE_HINTS.search(message)
        or _WRITES_CODE.search(message)
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
        spoken: bool = False,
        bias: RoutingBias | None = None,
    ) -> RouteDecision:
        """Pick a model.

        `selected` is the user's choice — a model id, or "smart" to decide here.
        `available` is the set of currently usable ids, from
        `catalog.resolve_availability`; None means "assume everything works",
        which is only correct in tests.
        `step` is the agent-loop step (Phase 6); >=3 implies a hard task.
        `spoken` marks a turn that arrived by voice and will be answered aloud.
        """
        usable = self._usable(available)

        # Stage 0 — a spoken *conversational* turn is answered on this machine,
        # whatever the bias says. Measured: the same reply routed to Gemini put
        # first audio at 1707ms against 872ms locally, because the network hop
        # lands before synthesis can even start. §10 budgets ~1000ms end to end.
        #
        # **A spoken command is not a conversational turn.** This used to catch
        # both, so "increase the volume" said out loud could only ever reach the
        # local model — which is exactly the turn Eyaas reported failing while
        # GPT and Gemini did it perfectly. Nobody is waiting on the prosody of
        # "Volume 40% to 55%"; they are waiting for the volume to change.
        #
        # An explicit model choice still wins below: picking a cloud model is a
        # deliberate act, and silently overriding it would be worse than slow.
        if spoken and selected == catalog.SMART_ID and not is_tool_shaped(message):
            return self._local(usable, "Spoken, so it stayed on this machine to keep up.")

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

        return self._by_bias(message, usable, step, bias)

    # ── per-bias policy ─────────────────────────────────────────────────

    def _by_bias(
        self, message: str, usable: set[str], step: int, bias: RoutingBias | None = None
    ) -> RouteDecision:
        """`bias` overrides the instance setting for this call only.

        **A parameter, not a save-and-restore around `self._bias`.** The bias
        is process-global and a conversation mode is not; mutating a shared
        field across `await` points would mean a voice turn and a typed turn
        overlapping — which `busy` shows is a real state — could run at each
        other's bias, silently and unreproducibly. A parameter is pure, which
        is what the rest of this module already is.

        This only reaches stage 4. Stages 0-3 — spoken-conversational, an
        explicit model choice, the `_PRIVATE` check, and no-cloud-available —
        have already returned by here, so **no mode can route something
        private to the cloud**.
        """
        effective = bias or self._bias
        if effective is RoutingBias.QUALITY:
            return self._quality_first(message, usable, step)
        if effective is RoutingBias.BALANCED:
            return self._balanced(message, usable, step)
        return self._fastest(message, usable, step)

    def _quality_first(self, message: str, usable: set[str], step: int) -> RouteDecision:
        """Cloud unless the turn is trivial. The default.

        `_DEEP_VERBS` is checked here and was not before, which is the whole
        reason "analyse this" and "write me a python script" were answered by
        the cheapest model in the catalog. In this bias the user has already
        said they want the better answer, so a deep verb is enough on its own —
        `balanced` still requires more.
        """
        if is_trivial(message):
            return self._local(usable, "Just a greeting — answered locally, instantly.")
        if needs_deep_model(message, step) or _DEEP_VERBS.search(message):
            return self._cloud(usable, ModelClass.SMART, "This needs careful reasoning.", message)
        # **A command used to be sent to BALANCED here, and it should not have
        # been.** The justification was one run of `gate_tool_selection.py` in
        # which `gpt-5.4-nano` — what this branch reaches for — scored 19/24
        # against the local model's 21/24. Re-measured four times on one probe
        # set, nano scores 0.92 / 0.88 / 0.92 / 0.85 and the 7B 0.88 / 0.88 /
        # 0.81 / 0.85: the spread *within* a model is wider than the gap
        # between them, so there was never a difference to route on.
        #
        # Left as a comment rather than deleted, because the reasoning was
        # right and only the evidence was thin — if a model does turn out to be
        # measurably worse at tools, this is where that belongs.
        return self._cloud(
            usable, ModelClass.FAST, "Answered by a cloud model for quality.", message
        )

    def _balanced(self, message: str, usable: set[str], step: int) -> RouteDecision:
        """Cloud for real work, local for conversation."""
        if needs_deep_model(message, step):
            return self._cloud(usable, ModelClass.SMART, "This needs careful reasoning.", message)
        if _DEEP_VERBS.search(message) or len(message) >= LONG_MESSAGE_CHARS:
            return self._cloud(usable, ModelClass.FAST, "Needs more than a quick answer.", message)
        # Doing something to the machine is real work by this bias's own
        # description, and it is the case where being wrong is visible: a
        # conversational answer that is a bit worse is a bit worse, while a tool
        # call the model fumbles simply does not happen.
        if is_tool_shaped(message):
            return self._cloud(usable, ModelClass.FAST, "A command, so accuracy won.", message)
        return self._local(usable, "Conversational turn — answered locally, faster.")

    def _fastest(self, message: str, usable: set[str], step: int) -> RouteDecision:
        """Local unless the turn clearly needs more. What voice will want."""
        if _THINK_HARD.search(message) or step >= 3:
            return self._cloud(usable, ModelClass.SMART, "You asked for a careful answer.", message)
        # Before the length rule, not after. "fix this python script" is 22
        # characters and a 7B answer to it is worth nothing — being fast is
        # the point of this bias, but not at the price of being wrong.
        if (
            _CODE_HINTS.search(message)
            or _WRITES_CODE.search(message)
            or _SEQUENCED.search(message)
        ):
            return self._cloud(
                usable, ModelClass.SMART, "Looks like code or a multi-step task.", message
            )
        if len(message) <= SHORT_MESSAGE_CHARS and not _DEEP_VERBS.search(message):
            return self._local(usable, "Short question — answered locally, faster.")
        if _DEEP_VERBS.search(message) or len(message) >= LONG_MESSAGE_CHARS:
            return self._cloud(usable, ModelClass.FAST, "Needs more than a quick answer.", message)
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

    def rank(
        self, candidates: list[ModelInfo], *, tool_shaped: bool = False
    ) -> list[ModelInfo]:
        """Fastest observed first — the ranking self-corrects as turns land.

        On a tool-shaped turn a **measured** tool score outranks latency, but
        only when the difference is bigger than the measurement's own noise —
        see `TOOL_SCORE_MARGIN`. Scores are banded before they are compared, so
        three models within 0.03 of each other are ranked by speed, as they
        should be, and one that is genuinely worse still loses.

        The two are not comparable goods when they do differ: 300ms of extra
        latency is a pause, and a model that picks the wrong tool produces
        nothing at all while reporting that it did. Models with no measurement
        sort as if average — neither promoted nor punished — the same rule
        `by_class` already applies to discovered models.
        """
        if not tool_shaped:
            return sorted(
                candidates, key=lambda m: self._health.latency_for(m.id, m.ttft_ms_seed)
            )

        def band(model: ModelInfo) -> int:
            score = model.tool_score
            if score is None:
                score = UNMEASURED_TOOL_SCORE
            return int(score / TOOL_SCORE_MARGIN)

        return sorted(
            candidates,
            key=lambda m: (-band(m), self._health.latency_for(m.id, m.ttft_ms_seed)),
        )

    def _best_local(self, usable: set[str]) -> ModelInfo:
        """The local model to fall back to. Prefers the instruction-tuned 7B,
        but only among models Ollama has actually pulled."""
        return catalog.default_local({m.id for m in catalog.local_models() if m.id in usable})

    def _cloud(
        self, usable: set[str], klass: ModelClass, detail: str, message: str = ""
    ) -> RouteDecision:
        candidates = [m for m in catalog.by_class(klass) if m.id in usable and not m.local]
        if not candidates:
            # Nothing in the requested class; try any cloud model before local.
            candidates = [m for m in catalog.CATALOG if m.id in usable and not m.local]
        if not candidates:
            return self._local(usable, f"{detail} No cloud model was reachable.")

        ranked = self.rank(candidates, tool_shaped=is_tool_shaped(message))
        # Siblings first, then local as the last resort (§9.7 stage 7).
        return RouteDecision(
            model=ranked[0],
            reason=RouteReason(stage="cloud", detail=detail),
            fallbacks=[*ranked[1:], self._best_local(usable)],
        )

    def _local(self, usable: set[str], detail: str) -> RouteDecision:
        model = self._best_local(usable)
        others = self.rank(
            [m for m in catalog.local_models() if m.id in usable and m.id != model.id]
        )
        return RouteDecision(
            model=model,
            reason=RouteReason(stage="local", detail=detail),
            fallbacks=others,
        )
