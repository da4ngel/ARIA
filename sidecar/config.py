"""Sidecar configuration. Single source of truth for paths, port, and auth token.

All settings are overridable by environment variable with the ``ARIA_`` prefix,
or by a ``.env`` file in the repo root. See ``.env.example``.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

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

    # Supplied by Electron on spawn. Empty means "generate one" — see handshake.py.
    # Never logged.
    token: str = Field(default="", repr=False)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "aria.db"

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
