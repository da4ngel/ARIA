"""WebSocket auth token lifecycle (BUILD_SPEC §7.1).

The sidecar binds ``127.0.0.1:8765``, which any browser tab on this machine can
reach. Every ``/rpc`` connection must present ``Authorization: Bearer <token>``.

Deviation from §7.1, deliberate: the spec has the sidecar mint the token and
Electron read it back from ``data/.handshake``. That races on restart — Electron
can read the *previous* run's token before the new process overwrites the file,
then get rejected. Instead Electron mints the token and passes it in via
``ARIA_TOKEN``; we use it when present and generate our own otherwise. The file
is still written either way so ``npm run sidecar`` standalone keeps working.
"""

from __future__ import annotations

import hmac
import secrets
from pathlib import Path

import structlog

log = structlog.get_logger(__name__)

TOKEN_BYTES = 32


def resolve_token(supplied: str) -> str:
    """Use the token Electron supplied, or mint one for standalone runs."""
    if supplied:
        return supplied
    return secrets.token_hex(TOKEN_BYTES)


def write_handshake(path: Path, token: str) -> None:
    """Publish the token for a client that did not supply one.

    Written after the server is listening, so a client that sees the file can
    assume the port is live. Never logged.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(token, encoding="utf-8")
    log.info("handshake.written", path=str(path))


def clear_handshake(path: Path, token: str = "") -> None:
    """Remove the token file on clean shutdown so no stale token survives.

    **Only if it is ours.** A second sidecar that cannot bind the port still
    runs its whole startup and then its whole shutdown, and the unconditional
    unlink meant that failed process deleted the *running* one's handshake on
    the way out. The running sidecar keeps serving and every gate script
    immediately dies with `FileNotFoundError: data\\.handshake` — an error about
    the process that worked, caused by the one that did not.

    Passing no token keeps the old behaviour for callers that have none.
    """
    try:
        if token and path.exists() and path.read_text(encoding="utf-8").strip() != token:
            log.info("handshake.kept", path=str(path), reason="written by another process")
            return
        path.unlink(missing_ok=True)
    except OSError as exc:  # pragma: no cover — best effort on shutdown
        log.warning("handshake.clear_failed", path=str(path), error=str(exc))


def token_matches(expected: str, presented: str | None) -> bool:
    """Constant-time comparison of a presented Bearer token."""
    if not presented:
        return False
    return hmac.compare_digest(expected, presented)


def bearer_from_header(header: str | None) -> str | None:
    """Extract the token from an ``Authorization: Bearer <token>`` header."""
    if not header:
        return None
    scheme, _, value = header.partition(" ")
    if scheme.lower() != "bearer" or not value:
        return None
    return value.strip()
