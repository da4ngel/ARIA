"""Process-wide runtime handles.

Not in BUILD_SPEC §5. Added because RPC handlers receive only their params, so
they need somewhere to reach the database and readiness flags without importing
``main`` (which imports them — a cycle).

This holds *process handles*, not domain state. Conversation, memory, and task
state live in SQLite per CLAUDE.md rule 1.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sidecar.memory.db import Database

if TYPE_CHECKING:
    from sidecar.core.conversation import ConversationService
    from sidecar.core.listener import Listener
    from sidecar.memory.settings_store import SettingsStore
    from sidecar.providers.availability import AvailabilityService
    from sidecar.providers.base import LLMProvider
    from sidecar.providers.stt import WhisperSTT
    from sidecar.providers.tts import KokoroTTS


@dataclass
class Runtime:
    """Handles owned by the app lifespan."""

    db: Database | None = None
    provider: LLMProvider | None = None
    conversation: ConversationService | None = None
    settings: SettingsStore | None = None
    local_model: str | None = None
    ollama_ready: bool | None = None
    # Model ids Ollama actually has pulled — drives picker availability.
    local_models: list[str] = field(default_factory=list)
    # Every provider, keyed by `catalog.ProviderName`. `provider` above stays as
    # the local one, which startup and `system.health` still special-case.
    providers: dict[str, LLMProvider] = field(default_factory=dict)
    # Shared by `models.list` and the router so they can never disagree.
    availability: AvailabilityService | None = None
    # Speech. None when voice is off or the weights are missing — she types.
    tts: KokoroTTS | None = None
    tts_warm: asyncio.Task[None] | None = None
    # Speech recognition. None when voice is off or the model is missing.
    stt: WhisperSTT | None = None
    stt_warm: asyncio.Task[None] | None = None
    # Hands-free listening. None when the wake word weights are absent — the
    # rest of voice still works, so this is never a startup failure.
    listener: Listener | None = None

    @property
    def db_ready(self) -> bool:
        return self.db is not None

    def require_db(self) -> Database:
        if self.db is None:
            raise RuntimeError(
                "Database is not open yet. The sidecar is still starting; "
                "retry once GET /health reports db=true."
            )
        return self.db

    def require_conversation(self) -> ConversationService:
        if self.conversation is None:
            raise RuntimeError(
                "Conversation service is not ready. The sidecar is still starting; "
                "retry once GET /health reports db=true."
            )
        return self.conversation

    def require_availability(self) -> AvailabilityService:
        if self.availability is None:
            raise RuntimeError(
                "Model availability is not resolved yet. The sidecar is still "
                "starting; retry once GET /health reports db=true."
            )
        return self.availability

    def reset(self) -> None:
        self.db = None
        self.provider = None
        self.conversation = None
        self.settings = None
        self.local_model = None
        self.ollama_ready = None
        self.local_models = []
        self.providers = {}
        self.availability = None
        self.tts = None
        self.tts_warm = None
        self.stt = None
        self.stt_warm = None
        self.listener = None


runtime = Runtime()
