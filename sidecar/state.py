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
    from sidecar.core.questions import QuestionBroker
    from sidecar.memory.indexer import Indexer
    from sidecar.memory.reflection import Reflector
    from sidecar.memory.retrieval import MemoryServices
    from sidecar.memory.routing_log import RoutingLog
    from sidecar.memory.scheduler import MemoryScheduler
    from sidecar.memory.settings_store import SettingsStore
    from sidecar.persona.proactivity import ProactivityScheduler
    from sidecar.providers.adoption import AdoptionService
    from sidecar.providers.availability import AvailabilityService
    from sidecar.providers.base import LLMProvider
    from sidecar.providers.embeddings import OllamaEmbeddings
    from sidecar.providers.ollama_supervisor import OllamaSupervisor
    from sidecar.providers.search import WebSearch
    from sidecar.providers.stt import WhisperSTT
    from sidecar.providers.tts import KokoroTTS
    from sidecar.tools.permissions import PermissionEngine


@dataclass
class Runtime:
    """Handles owned by the app lifespan."""

    db: Database | None = None
    provider: LLMProvider | None = None
    conversation: ConversationService | None = None
    settings: SettingsStore | None = None
    local_model: str | None = None
    ollama_ready: bool | None = None
    # Starts Ollama when it is down and re-arms `local_models` when it
    # returns. None when the sidecar is running without one.
    ollama_supervisor: OllamaSupervisor | None = None
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
    # The tier engine. None means she has no hands this session.
    permissions: PermissionEngine | None = None

    #: Puts a multiple-choice question on screen and waits for the answer
    #: (`core/questions.py`). `ask_user` reaches it through here because
    #: `ToolContext` carries no event bus.
    questions: QuestionBroker | None = None
    # Reads documents in the background so they can be found by meaning.
    indexer: Indexer | None = None
    # Text to vectors, on the CPU. Shared by the indexer and memory retrieval:
    # one instance means one connection pool and one lock, so the two never
    # contend for Ollama independently.
    embeddings: OllamaEmbeddings | None = None
    # Whether `nomic-embed-text` is actually pulled. None until probed. False
    # is not a failure — memory falls back to word matching and says so.
    embeddings_ready: bool | None = None
    # Facts, episodes, and retrieval. None when memory is switched off.
    memory: MemoryServices | None = None
    #: §9.7's labelled routing dataset. Built beside the database.
    routing_log: RoutingLog | None = None
    #: Web search for `research`. Built at startup; the switch below is
    #: what decides whether the tool is offered at all.
    search: WebSearch | None = None
    #: **The tool must not exist when this is False.** `allow_danger_tools`
    #: was dead for a whole phase because its execution gate moved and its
    #: schema ceiling did not; both move together here.
    online_mode: bool = False
    # The nightly §8.3 pass, also reachable from `memory.reflect`.
    reflector: Reflector | None = None
    # Idle sweeps and the 3am catch-up.
    memory_scheduler: MemoryScheduler | None = None
    # Phase 8: unprompted messages. None when `proactivity_enabled` is off.
    proactivity_scheduler: ProactivityScheduler | None = None

    #: Free-model measurement (`providers/adoption.py`). Present even with
    #: no OpenRouter key — `restore()` still has to put past adoptions back
    #: into the routing pool — but only *started* when a key exists.
    adoption: AdoptionService | None = None

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
        self.ollama_supervisor = None
        self.local_models = []
        self.providers = {}
        self.availability = None
        self.tts = None
        self.tts_warm = None
        self.stt = None
        self.stt_warm = None
        self.listener = None
        self.permissions = None
        self.indexer = None
        self.embeddings = None
        self.embeddings_ready = None
        self.memory = None
        self.reflector = None
        self.routing_log = None
        self.search = None
        self.online_mode = False
        self.memory_scheduler = None
        self.proactivity_scheduler = None


runtime = Runtime()
