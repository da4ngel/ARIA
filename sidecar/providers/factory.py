"""One place that knows how to build a provider from its name.

**This exists because the same three-line if/elif was written twice and both
copies ended in `return GeminiProvider()`.** `scripts/eval_quality.py` and
`scripts/gate_tool_selection.py` each mapped Ollama and OpenAI explicitly and
let *everything else* fall through to Gemini — so the moment a fourth provider
existed, measuring one of its models would have quietly measured Gemini
instead and reported the score against the wrong name. A measurement that
names the wrong model is worse than no measurement, because it looks like
evidence.

So the fall-through is gone: an unknown provider raises. `main.py` builds its
runtime dict from here too, which is what keeps the scripts and the app
agreeing about what "openrouter" means.
"""

from __future__ import annotations

from sidecar.providers.base import LLMProvider
from sidecar.providers.catalog import ModelInfo, ProviderName
from sidecar.providers.gemini import GeminiProvider
from sidecar.providers.ollama import OllamaProvider
from sidecar.providers.openai import OpenAIProvider
from sidecar.providers.openrouter import OpenRouterProvider


def for_provider(name: ProviderName, *, ollama_url: str | None = None) -> LLMProvider:
    """A client for one provider. Raises on anything unrecognised.

    **Never a default.** Returning "some provider" for an unknown name is how
    the scripts came to measure Gemini while printing another model's id.
    """
    if name is ProviderName.OLLAMA:
        return OllamaProvider(ollama_url) if ollama_url else OllamaProvider()
    if name is ProviderName.OPENAI:
        return OpenAIProvider()
    if name is ProviderName.GEMINI:
        return GeminiProvider()
    if name is ProviderName.OPENROUTER:
        return OpenRouterProvider()
    raise ValueError(
        f"No client is built for provider {name!r}. Add one in providers/factory.py "
        f"— it is deliberately an error rather than a default."
    )


def for_model(info: ModelInfo, *, ollama_url: str | None = None) -> LLMProvider:
    """The client that answers for this model."""
    return for_provider(info.provider, ollama_url=ollama_url)


def build_all(
    *, ollama: LLMProvider | None = None, ollama_url: str | None = None
) -> dict[str, LLMProvider]:
    """Every provider, keyed by name — the shape `ProviderRegistry` wants.

    Built by iterating `ProviderName` rather than from a hand-written literal,
    so a member cannot be added to the enum and forgotten here. That literal
    is exactly what `main.py` had, and it is the same shape of omission as the
    scripts' fall-through: nothing errors, the provider is simply absent.

    `ollama` accepts a client the caller already holds — `main.py` keeps a
    typed reference for model discovery and warm-up, and building a second
    one would leave an unclosed HTTP client behind.
    """
    built: dict[str, LLMProvider] = {}
    for name in ProviderName:
        if name is ProviderName.OLLAMA and ollama is not None:
            built[str(name)] = ollama
        else:
            built[str(name)] = for_provider(name, ollama_url=ollama_url)
    return built
