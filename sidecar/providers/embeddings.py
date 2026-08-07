"""Embeddings, on the CPU, over Ollama (BUILD_SPEC §4, CLAUDE.md rule 2).

`nomic-embed-text` at 768 dimensions, which is what the `vec0` tables in
`schema.sql` are declared for.

**`num_gpu: 0` is the whole reason this module exists rather than being three
lines inside the indexer.** Rule 2 allows exactly one model on the card, and
CLAUDE.md already records what happens otherwise: a 6GB card asked to hold two
models does not fail cleanly, it stalls generation for minutes and reads as a
hang. Verified with `ollama ps` after wiring this up:

    nomic-embed-text    376 MB    100% CPU
    qwen2.5:7b          5.1 GB    18%/82% CPU/GPU

Both resident, the language model undisturbed.

**Measured on this machine**: 752ms cold, then ~154ms per chunk of roughly 450
characters. That figure is what the indexer's throttle is built around.
"""

from __future__ import annotations

import asyncio

import httpx
import structlog

log = structlog.get_logger(__name__)

MODEL = "nomic-embed-text"
#: Must match `float[768]` in schema.sql.
DIMENSIONS = 768

_TIMEOUT_S = 120.0


class EmbeddingsUnavailable(RuntimeError):
    """Ollama could not embed. Never fatal — the name search still works."""


class OllamaEmbeddings:
    """Text to vectors, one call at a time.

    Serialised deliberately, like the speech recogniser: concurrent requests
    to one Ollama instance do not finish sooner, they contend, and this runs
    in the background behind whatever the user is actually doing.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = MODEL) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=_TIMEOUT_S)
        self._model = model
        self._lock = asyncio.Lock()

    async def embed(self, text: str) -> list[float]:
        """One chunk to one vector."""
        async with self._lock:
            try:
                response = await self._client.post(
                    "/api/embeddings",
                    json={
                        "model": self._model,
                        "prompt": text,
                        # Not optional. See the module docstring.
                        "options": {"num_gpu": 0},
                        # Let it fall out of memory between bursts rather than
                        # sitting on 376MB while nobody is indexing.
                        "keep_alive": "5m",
                    },
                )
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise EmbeddingsUnavailable(
                    f"Could not reach Ollama to embed text ({exc}). "
                    f"Is it running? Pull the model with: ollama pull {self._model}"
                ) from exc

        vector = response.json().get("embedding")
        if not isinstance(vector, list) or len(vector) != DIMENSIONS:
            raise EmbeddingsUnavailable(
                f"{self._model} returned {len(vector) if vector else 0} dimensions, "
                f"but the database is built for {DIMENSIONS}."
            )
        return [float(v) for v in vector]

    async def available(self) -> bool:
        """Whether the model is pulled. Never raises."""
        try:
            response = await self._client.get("/api/tags")
            response.raise_for_status()
        except httpx.HTTPError:
            return False
        return any(
            m.get("name", "").startswith(self._model) for m in response.json().get("models", [])
        )

    async def aclose(self) -> None:
        await self._client.aclose()
