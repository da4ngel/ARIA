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
    # Start Ollama if it is not already running, rather than reporting local
    # models as unavailable and leaving the user to work out why. Off is a
    # real choice — somebody running Ollama on another machine, or keeping it
    # off deliberately — so it is a setting rather than unconditional.
    ollama_autostart: bool = True
    ollama_start_timeout_s: float = 20.0
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
    # Speech recognition. `tiny.en` was tried and reverted: it was measured as
    # equally accurate on one synthesised voice and mishears her name badly on
    # a real one — see providers/stt.py.
    stt_model: str = "base.en"
    voice: str = "af_heart"
    voice_speed: float = 1.0
    voice_lang: str = "en-us"

    # ── Wake word (Phase 2 stage 3) ──────────────────────────────────
    # **On by default**, at Eyaas's explicit request: reaching for a key before
    # speaking is the thing hands-free is meant to remove, and an assistant you
    # have to switch on first is a worse one.
    #
    # It is still a real decision, so it stays visible and reversible rather
    # than silent: the microphone is open whenever she is running, Windows
    # shows its indicator, and the header switch says "Listening" in words.
    # Turning it off persists, so it is asked once and not re-asked.
    wake_word_enabled: bool = True
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
    # How long she waits to be asked after being called by name. Zero restores
    # the one-breath-only behaviour that answered 12 of 80 utterances in a
    # measured session — see `core/listener.ListenerState`.
    armed_window_s: float = 10.0
    # How far playback drops when someone starts talking over her, before the
    # transcript decides whether it was actually an interruption. Not silence:
    # a mis-fire should be a dip that comes back, not a lost sentence.
    duck_gain: float = 0.2
    # A short blip when she starts listening. The glow says the same thing, but
    # only if you happen to be looking at the screen when you speak.
    wake_chime: bool = True

    # ── Tools (Phase 3) ──────────────────────────────────────────────
    # DANGER-tier tools are irreversible, so they are off until somebody
    # deliberately turns them on (§7.2). While this is false the model is
    # not even told they exist, which is a stronger guarantee than asking.
    allow_danger_tools: bool = False

    # ── The file index (Phase 4b) ────────────────────────────────────
    # Reads your documents so they can be found by what they say rather than
    # what they are called. Off would leave `search_content` unavailable and
    # name search unaffected.
    #
    # §9: "a background indexer that makes the machine feel slow will get
    # uninstalled." 20 files/min is that number, and it pauses entirely while
    # she is answering or the machine is busy.
    index_files: bool = True
    index_files_per_min: int = 20

    # ── Memory (Phase 5) ─────────────────────────────────────────────
    # Whether she recalls facts and episodes on a turn at all. Off leaves the
    # tables alone and the prompt exactly as Phase 4 assembled it.
    memory_enabled: bool = True
    # The nightly pass that extracts durable facts (§8.3). Separate from the
    # switch above because retrieval is free and reflection is a model call —
    # the test suite turns this off and leaves recall on.
    memory_reflection_enabled: bool = True
    # Local-clock hour for that pass. It is a catch-up, not a cron fire: a
    # machine asleep at 3am reflects on the first tick after it wakes.
    memory_reflection_hour: int = 3
    # §9: "on session end (or 30min idle)". There is no session-end event, so
    # this is what actually closes a conversation into an episode.
    memory_idle_close_minutes: int = 30
    # The ceiling on how long a turn will wait for the retrieval embed before
    # falling back to word matching. §9's gate is 80ms of added latency; this
    # is what makes that structural rather than hopeful. Set below the
    # *contended* embed p90, not the idle one — see retrieval.DEFAULT_DEADLINE_S
    # for both measurements and why the difference decides this number.
    memory_retrieval_deadline_ms: int = 60

    #: Whether she may reach the web at all (§9 Phase 7). **Off by
    #: default**, and deliberately: the query leaves this machine, which is
    #: the user's decision to make rather than a default to inherit. The
    #: stored setting overrides this at startup.
    online_mode: bool = False

    # ── Proactivity (Phase 8) ────────────────────────────────────────
    # On by default, unlike online_mode — this never sends anything off the
    # machine (even the self-check is the local model), so the risk here is
    # annoyance, not privacy. Rate-limited and focus-aware regardless
    # (persona/proactivity.py); this is the switch for turning the whole
    # thing off, not a tuning knob.
    proactivity_enabled: bool = True

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

    @property
    def undo_dir(self) -> Path:
        """Manifests for batch operations (§11: "undo manifests for every one").

        A batch move is the first thing she does that is tedious rather than
        dangerous to reverse by hand — thirty files scattered into six folders.
        The tier system can ask before it happens; only a manifest can put it
        back afterwards.
        """
        return self.data_dir / "undo"

    @property
    def browser_launcher_path(self) -> Path:
        """A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7).

        In `data/`, not the Desktop — writing a shortcut somewhere the user
        did not ask for it to appear is the kind of thing that reads as a
        virus. `browser.setup` returns this path so the UI can tell the user
        where it is and offer to open its folder.
        """
        return self.data_dir / "start_chrome_debug.bat"

    def ensure_dirs(self) -> None:
        """Create the runtime directory tree. Safe to call repeatedly."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.undo_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Process-wide settings singleton."""
    return Settings()
