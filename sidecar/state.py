"""Process-wide runtime handles.

Not in BUILD_SPEC §5. Added because RPC handlers receive only their params, so
they need somewhere to reach the database and readiness flags without importing
``main`` (which imports them — a cycle).

This holds *process handles*, not domain state. Conversation, memory, and task
state live in SQLite per CLAUDE.md rule 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sidecar.memory.db import Database

if TYPE_CHECKING:
    from sidecar.core.conversation import ConversationService
    from sidecar.providers.base import LLMProvider


@dataclass
class Runtime:
    """Handles owned by the app lifespan."""

    db: Database | None = None
    provider: LLMProvider | None = None
    conversation: ConversationService | None = None
    local_model: str | None = None
    ollama_ready: bool | None = None

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

    def reset(self) -> None:
        self.db = None
        self.provider = None
        self.conversation = None
        self.local_model = None
        self.ollama_ready = None


runtime = Runtime()
