"""API keys, stored in Windows Credential Manager (BUILD_SPEC §11).

Never `.env`, never the repo, never logged. Only key *presence* and the last
four characters are ever surfaced, so Settings can show which providers are
configured without exposing anything.

Phase 1 does not call a cloud provider; this exists now so keys have one home
from the start rather than migrating out of a config file at Phase 6.
"""

from __future__ import annotations

from enum import StrEnum

import keyring
import structlog
from keyring.errors import KeyringError
from pydantic import BaseModel

log = structlog.get_logger(__name__)

SERVICE = "ARIA"


class CredentialKey(StrEnum):
    """Credential Manager entry names under the ARIA service."""

    OPENAI = "openai_api_key"
    GEMINI = "gemini_api_key"
    #: One key reaching many vendors, and the only source of free models here.
    OPENROUTER = "openrouter_api_key"
    #: Amazon Bedrock accepts **either** of two credential shapes, and which
    #: one a user holds is not knowable from here — so both have a home and
    #: `providers/bedrock.py` prefers the narrower one. A Bedrock API key is a
    #: bearer token scoped to Bedrock alone; an AWS access key is a general IAM
    #: credential that has to be signed with (`providers/sigv4.py`).
    BEDROCK = "bedrock_api_key"
    AWS_ACCESS_KEY_ID = "aws_access_key_id"
    AWS_SECRET_ACCESS_KEY = "aws_secret_access_key"
    #: Only set for temporary credentials. Part of the signature when present,
    #: not merely sent alongside it.
    AWS_SESSION_TOKEN = "aws_session_token"
    #: The mailbox `read_email` reads, read-only. **The password is an app
    #: password**, not the account password: Google and Microsoft both
    #: require one and both need two-factor authentication on first. Host
    #: and address are not secrets, but they live here so a mailbox is
    #: configured or removed in one place rather than two.
    IMAP_HOST = "imap_host"
    IMAP_USER = "imap_user"
    IMAP_PASSWORD = "imap_password"
    #: Web search, for `research`. Either one is enough — see
    #: `providers/search.py` for why there are two rather than a choice.
    BRAVE = "brave_api_key"
    TAVILY = "tavily_api_key"


class CredentialStatus(BaseModel):
    """Safe-to-display description of a stored key."""

    key: CredentialKey
    present: bool
    hint: str | None = None  # last 4 chars, for "is this the key I think it is"


def get_key(key: CredentialKey) -> str | None:
    """Read a key, or None if unset. Never logs the value."""
    try:
        return keyring.get_password(SERVICE, str(key))
    except KeyringError as exc:
        log.error("credentials.read_failed", key=str(key), error=str(exc))
        return None


def set_key(key: CredentialKey, value: str) -> None:
    """Store a key. Callers must never log `value`."""
    if not value.strip():
        raise ValueError(f"Refusing to store an empty value for {key}.")
    keyring.set_password(SERVICE, str(key), value)
    log.info("credentials.stored", key=str(key), length=len(value))


def delete_key(key: CredentialKey) -> None:
    try:
        keyring.delete_password(SERVICE, str(key))
        log.info("credentials.deleted", key=str(key))
    except KeyringError as exc:
        log.warning("credentials.delete_failed", key=str(key), error=str(exc))


def status(key: CredentialKey) -> CredentialStatus:
    value = get_key(key)
    if not value:
        return CredentialStatus(key=key, present=False)
    return CredentialStatus(key=key, present=True, hint=f"...{value[-4:]}")


def all_status() -> list[CredentialStatus]:
    """For Settings and `system.health`. Contains no secrets."""
    return [status(k) for k in CredentialKey]
