"""Sidecar configuration. Single source of truth for paths, port, and auth token.

All settings are overridable by environment variable with the ``ARIA_`` prefix,
or by a ``.env`` file in the repo root. See ``.env.example``.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# sidecar/config.py -> sidecar/ -> repo root
REPO_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Sidecar settings, loaded once per process."""

    model_config = SettingsConfigDict(
        env_prefix="ARIA_",
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 8765
    dev: bool = False
    log_level: str = "INFO"

    data_dir: Path = REPO_ROOT / "data"

    # ── Local model (Phase 1) ────────────────────────────────────────
    # Interim per CLAUDE.md; switches to qwen2.5:7b-instruct-q4_K_M once pulled.
    # A models.yaml registry lands in Phase 6 with the router, when more than
    # one model exists to choose between — a registry of one is not a registry,
    # and it would pull in pyyaml outside the phase that needs it.
    ollama_url: str = "http://127.0.0.1:11434"
    local_model: str = "qwen3.5:4b"
    warm_on_startup: bool = True

    # §2.1: do not raise. Longer context is memory retrieval's job, not the
    # context window's.
    num_ctx: int = 8192
    # §9 Phase 1: roll up the conversation once it passes this.
    context_token_budget: int = 6000

    # ── Voice (Phase 2) ──────────────────────────────────────────────
    # CPU only, per rule 2: the 6GB card holds the language model alone.
    # Off leaves her fully usable by typing — voice is additive, never required.
    voice_enabled: bool = True
    voice: str = "af_heart"
    voice_speed: float = 1.0
    voice_lang: str = "en-us"

    # ── Wake word (Phase 2 stage 3) ──────────────────────────────────
    # **Off by default, unlike the rest of voice.** Everything above runs on
    # audio the user deliberately handed over by holding a key; this one holds
    # the microphone open indefinitely, and Windows shows an indicator saying
    # so for as long as it does. That is a choice to opt into, not a default to
    # discover. The UI toggle flips it and `settings` persists the answer.
    wake_word_enabled: bool = False
    # "phrase" answers to her own name, decided from the transcript. "model"
    # answers to "hey jarvis" — openWakeWord's pretrained phrase — and costs a
    # fraction as much CPU, because it never transcribes what was not for her.
    # `core/listener.WakeMode` spells the trade out.
    wake_mode: Literal["phrase", "model"] = "phrase"
    # §9 Phase 2 stage 3, and only read by "model". Lower catches more and
    # false-fires more; the gate is 20 triggers with under 2 misses and an
    # hour of idle with no false positive.
    wake_word_threshold: float = 0.5
    # Speech while she is talking cuts her off. The microphone hears her own
    # voice through the speakers, so this needs the renderer's echo cancellation
    # to be working; set it false if she interrupts herself.
    barge_in_enabled: bool = True

    # Supplied by Electron on spawn. Empty means "generate one" — see handshake.py.
    # Never logged.
    token: str = Field(default="", repr=False)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "aria.db"

    @property
    def models_dir(self) -> Path:
        """Speech model weights. Gitignored with the rest of `data/`, and large
        enough (~340MB) that they are downloaded rather than vendored."""
        return self.data_dir / "models"

    @property
    def log_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def log_path(self) -> Path:
        return self.log_dir / "sidecar.log"

    @property
    def handshake_path(self) -> Path:
        return self.data_dir / ".handshake"

    def ensure_dirs(self) -> None:
        """Create the runtime directory tree. Safe to call repeatedly."""
        self.log_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Process-wide settings singleton."""
    return Settings()
