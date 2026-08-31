"""First run: what is missing, and how to fetch it (BUILD_SPEC §9 Phase 9).

The wizard's five steps are Ollama, models, Everything, the microphone, and an
optional API key — plus wake-word calibration. Four of those were already
answerable; **the two that needed real work are the ones that download
something**, and both had the same shape of gap:

  - `ollama pull` existed nowhere in this repo. See `OllamaProvider.pull`.
  - Kokoro's ~330MB of voice weights had **no fetch path at all**, and the
    wake-word weights had one that is a CLI script. A wizard that tells
    somebody to run `python scripts/fetch_wakeword.py` is not a wizard.

Everything here is a *report* or a *fetch*. Nothing decides anything: the
wizard shows what is missing and the person chooses, because the alternative
is an app that downloads several gigabytes on first launch without asking.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, NamedTuple

import httpx
import structlog

log = structlog.get_logger(__name__)

#: Verified against the live endpoints rather than recalled — both return 200
#: with the sizes below. The voices URL is the one `kokoro_onnx` prints in its
#: own "file not found" message; the model file sits at the same release tag.
KOKORO_RELEASE = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
)

#: `(filename, url, approximate bytes)`. The size is so the wizard can say
#: "about 310MB" *before* anyone commits to it, not for validation — a real
#: `Content-Length` arrives with the response and is what drives the bar.
KOKORO_FILES: tuple[tuple[str, str, int], ...] = (
    ("kokoro-v1.0.onnx", f"{KOKORO_RELEASE}/kokoro-v1.0.onnx", 325_532_387),
    ("voices-v1.0.bin", f"{KOKORO_RELEASE}/voices-v1.0.bin", 28_214_398),
)

CONNECT_TIMEOUT_S = 30.0
#: 256KB — frequent enough for a smooth bar, rare enough that broadcasting
#: progress is not itself the bottleneck on a fast link.
CHUNK_BYTES = 1 << 18


class FetchProgress(NamedTuple):
    """One step of a download, in the terms a progress bar needs."""

    what: str
    received: int
    total: int | None
    done: bool
    note: str | None = None

    @property
    def percent(self) -> float | None:
        if not self.total:
            return None
        return round(min(1.0, self.received / self.total) * 100, 1)


# ── what is present ──────────────────────────────────────────────────


def _voice_state(models_dir: Path) -> dict[str, Any]:
    from sidecar.providers.tts import MODEL_FILE, VOICES_FILE

    missing = [n for n in (MODEL_FILE, VOICES_FILE) if not (models_dir / n).is_file()]
    return {
        "present": not missing,
        "missing": missing,
        "approx_bytes": sum(size for _, _, size in KOKORO_FILES),
    }


def _wake_word_state(models_dir: Path) -> dict[str, Any]:
    from sidecar.providers.wakeword import missing_models

    missing = missing_models(models_dir / "openwakeword")
    return {"present": not missing, "missing": missing, "approx_bytes": 3_500_000}


async def state() -> dict[str, Any]:
    """Everything the wizard needs to draw itself, in one round trip.

    One call rather than six: the wizard renders all its steps at once, and
    six independent fetches could disagree about a machine that is changing
    underneath them — which is exactly what a first run is.
    """
    from sidecar.config import get_settings
    from sidecar.providers.credentials import all_status
    from sidecar.providers.ollama import OllamaProvider
    from sidecar.providers.ollama_supervisor import find_ollama
    from sidecar.state import runtime
    from sidecar.tools.finder import everything_path

    settings = get_settings()
    models_dir = settings.models_dir

    ollama_running = False
    pulled: list[str] = []
    # Narrowed to the concrete class: `list_models` and `pull` are Ollama's,
    # not the `LLMProvider` protocol's — no cloud provider has a local model
    # store to enumerate or a download to run.
    provider = runtime.providers.get("ollama")
    if isinstance(provider, OllamaProvider):
        try:
            ollama_running = await provider.available()
            if ollama_running:
                pulled = await provider.list_models()
        except Exception:  # noqa: BLE001 - a report must not fail on one row
            log.info("setup.ollama_unreadable", exc_info=True)

    return {
        "ollama": {
            "installed": find_ollama() is not None,
            "running": ollama_running,
            "models": pulled,
        },
        "everything": {"present": everything_path() is not None},
        "voice": _voice_state(models_dir),
        "wake_word": _wake_word_state(models_dir),
        # **Presence only.** `hint` is four characters of a real key, and this
        # payload crosses a process boundary into a renderer.
        "keys": [{"key": str(s.key), "present": s.present} for s in all_status()],
        "models_dir": str(models_dir),
    }


# ── fetching ─────────────────────────────────────────────────────────


async def _download(
    client: httpx.AsyncClient, url: str, target: Path, what: str
) -> AsyncIterator[FetchProgress]:
    """Stream one file to disk, yielding progress.

    **Written to a `.part` and renamed at the end.** A 310MB download
    interrupted three quarters of the way through would otherwise leave a
    file at exactly the path `tts.py` checks for — and speech would then fail
    on every launch with an ONNX parse error rather than with the honest
    "the weights are missing from data/models".
    """
    partial = target.with_name(target.name + ".part")
    received = 0
    async with client.stream("GET", url, follow_redirects=True) as response:
        response.raise_for_status()
        raw = response.headers.get("content-length")
        total = int(raw) if raw and raw.isdigit() else None
        yield FetchProgress(what, 0, total, False)
        with partial.open("wb") as fh:
            async for chunk in response.aiter_bytes(CHUNK_BYTES):
                fh.write(chunk)
                received += len(chunk)
                yield FetchProgress(what, received, total, False)
    partial.replace(target)
    yield FetchProgress(what, received, received, True)


async def fetch_voice() -> AsyncIterator[FetchProgress]:
    """The Kokoro weights — about 330MB, and the reason she can speak."""
    from sidecar.config import get_settings

    models_dir = get_settings().models_dir
    models_dir.mkdir(parents=True, exist_ok=True)
    # No read timeout: the default is sized for a chat token, and a large file
    # over a slow link is not a stalled connection. Cancellation stops this.
    timeout = httpx.Timeout(None, connect=CONNECT_TIMEOUT_S)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for name, url, _size in KOKORO_FILES:
            target = models_dir / name
            if target.is_file():
                # Re-downloading 310MB because the wizard was opened twice is
                # not a neutral cost.
                size = target.stat().st_size
                yield FetchProgress(name, size, size, True, "already present")
                continue
            async for progress in _download(client, url, target, name):
                yield progress


async def fetch_wake_word() -> AsyncIterator[FetchProgress]:
    """The `hey_jarvis` ONNX weights, ~3.5MB.

    openwakeword's own downloader is synchronous and has no progress hook, so
    this reports start and finish rather than a bar. 3.5MB does not need one,
    and reimplementing its URL table here would be a second copy of something
    that already exists and is free to change.

    It also fetches tflite copies with no flag to stop it; those are removed,
    exactly as `scripts/fetch_wakeword.py` does, because `wakeword.py` only
    ever loads ONNX.
    """
    from sidecar.config import get_settings
    from sidecar.providers.wakeword import missing_models

    target = get_settings().models_dir / "openwakeword"
    if not missing_models(target):
        yield FetchProgress("hey_jarvis", 1, 1, True, "already present")
        return

    yield FetchProgress("hey_jarvis", 0, None, False)
    target.mkdir(parents=True, exist_ok=True)

    def _pull() -> None:
        from openwakeword.utils import download_models

        download_models(model_names=["hey_jarvis"], target_directory=str(target))
        for stale in target.glob("*.tflite"):
            stale.unlink()

    await asyncio.to_thread(_pull)

    absent = missing_models(target)
    if absent:
        raise RuntimeError(
            f"The wake word weights are still missing after downloading: "
            f"{', '.join(absent)}. Check that {target} is writable, or run "
            f"scripts/fetch_wakeword.py to see the underlying error."
        )
    yield FetchProgress("hey_jarvis", 1, 1, True)
