"""Read-only IMAP, in stdlib.

`imaplib` and `email` both ship with Python, so this costs no dependency —
which is the whole reason it is IMAP rather than a vendor SDK. Eyaas chose this
over BUILD_SPEC §9:947's browser route ("works on a logged-in Gmail tab"); the
trade is a stored app password against not needing a browser open, and it
parses far more reliably than scraping a webmail DOM.

**Nothing here can send.** There is no SMTP anywhere in this module and no
`STORE` command — rule 5 names sending as destructive, and the way to be sure a
read-only feature stays read-only is for the capability to be absent rather than
guarded.

**And it never marks anything as read.** `BODY.PEEK[]` rather than `RFC822`:
the ordinary fetch sets the `\\Seen` flag as a side effect, so a summariser
built the obvious way silently clears somebody's unread badge. That is a
destructive edit to their mailbox performed by a tool that claims to only look.
"""

from __future__ import annotations

import email
import imaplib
import re
from dataclasses import dataclass
from email.header import decode_header, make_header
from email.message import Message
from typing import Any

import structlog

log = structlog.get_logger(__name__)

#: A summariser does not need the whole thread, and a 200KB newsletter would
#: crowd out the conversation it was asked about.
BODY_CHARS = 1500

#: Nobody reads more than this in a summary, and each one is a round trip.
MAX_MESSAGES = 25

CONNECT_TIMEOUT_S = 20.0

#: Common hosts, so "gmail" is enough. Not a whitelist — any host is accepted.
KNOWN_HOSTS = {
    "gmail": "imap.gmail.com",
    "google": "imap.gmail.com",
    "outlook": "outlook.office365.com",
    "hotmail": "outlook.office365.com",
    "office365": "outlook.office365.com",
    "yahoo": "imap.mail.yahoo.com",
    "icloud": "imap.mail.me.com",
    "fastmail": "imap.fastmail.com",
    "zoho": "imap.zoho.com",
    "proton": "127.0.0.1",  # Proton Bridge, local only
}


class EmailUnavailable(RuntimeError):
    """Could not reach or sign in to the mailbox. Carries what to do next."""


@dataclass(frozen=True)
class MailHeader:
    uid: str
    subject: str
    sender: str
    date: str
    unread: bool
    body: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "uid": self.uid,
            "subject": self.subject,
            "from": self.sender,
            "date": self.date,
            "unread": self.unread,
            "body": self.body,
        }


def resolve_host(raw: str) -> str:
    """`"gmail"` into `imap.gmail.com`, or a real hostname straight through."""
    cleaned = raw.strip().lower()
    return KNOWN_HOSTS.get(cleaned, raw.strip())


def _decode(raw: str | None) -> str:
    """A MIME-encoded header into text. Never raises.

    Subjects arrive as `=?UTF-8?B?...?=` far more often than not, and a
    summariser fed that gibberish will faithfully summarise the gibberish.
    """
    if not raw:
        return ""
    try:
        return str(make_header(decode_header(raw)))
    except Exception:  # noqa: BLE001 — a bad header is not worth losing the mail
        return raw


def _body_of(message: Message) -> str:
    """The plain-text part, or the HTML stripped down to something readable."""
    plain, html_part = "", ""
    for part in message.walk() if message.is_multipart() else [message]:
        if part.get_content_maintype() == "multipart":
            continue
        # An attachment is not the message.
        if "attachment" in str(part.get("Content-Disposition", "")).lower():
            continue
        try:
            payload = part.get_payload(decode=True)
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(payload, bytes):
            continue
        charset = part.get_content_charset() or "utf-8"
        text = payload.decode(charset, "replace")
        if part.get_content_subtype() == "plain" and not plain:
            plain = text
        elif part.get_content_subtype() == "html" and not html_part:
            html_part = text

    body = plain or _strip_html(html_part)
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def _strip_html(raw: str) -> str:
    """Tags out, entities in. The same trade `providers/search.py` already made:
    a small stripper whose failure mode is untidy text, against a dependency."""
    if not raw:
        return ""
    without = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", raw)
    without = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>", "\n", without)
    without = re.sub(r"<[^>]+>", " ", without)
    import html as html_module

    return re.sub(r"[ \t]{2,}", " ", html_module.unescape(without))


def _search_terms(query: str, unread_only: bool) -> list[str]:
    """An IMAP SEARCH command. Quoted, so a query cannot inject a command."""
    terms: list[str] = ["UNSEEN"] if unread_only else []
    cleaned = query.strip()
    if cleaned:
        # `TEXT` searches headers and body. The value is passed as its own
        # argument by `imaplib`, so it is escaped rather than interpolated.
        terms += ["TEXT", f'"{cleaned}"']
    return terms or ["ALL"]


def fetch(
    *,
    host: str,
    user: str,
    password: str,
    query: str = "",
    unread_only: bool = False,
    limit: int = 10,
    folder: str = "INBOX",
) -> list[MailHeader]:
    """Newest first. **Blocking** — callers put it on a thread.

    Raises `EmailUnavailable` with a message naming the fix, because "login
    failed" for a mailbox almost always means an app password is needed rather
    than the account password, and that is not obvious.
    """
    capped = max(1, min(int(limit), MAX_MESSAGES))
    server = resolve_host(host)

    try:
        client = imaplib.IMAP4_SSL(server, timeout=CONNECT_TIMEOUT_S)
    except Exception as exc:
        raise EmailUnavailable(
            f"Could not reach {server}: {exc}. Check the host, and that this "
            f"machine is online."
        ) from exc

    try:
        try:
            client.login(user, password)
        except imaplib.IMAP4.error as exc:
            raise EmailUnavailable(
                f"{server} refused the sign-in for {user}. Most providers need an "
                f"**app password** here rather than your account password — "
                f"Google calls it an App Password, Microsoft calls it the same, "
                f"and both require two-factor authentication to be on first. "
                f"Server said: {exc}"
            ) from exc

        status, _ = client.select(folder, readonly=True)
        if status != "OK":
            raise EmailUnavailable(f"There is no folder called {folder!r} in that mailbox.")

        status, data = client.search(None, *_search_terms(query, unread_only))
        if status != "OK":
            raise EmailUnavailable("The mailbox refused that search.")

        ids = (data[0] or b"").split()
        if not ids:
            return []

        found: list[MailHeader] = []
        # Newest first, and only as many as asked for — an inbox is tens of
        # thousands of messages and this is a summary.
        for message_id in reversed(ids[-capped:]):
            header = _fetch_one(client, message_id)
            if header is not None:
                found.append(header)
        return found
    finally:
        # A mailbox left open holds a connection on the user's account, and
        # some providers cap concurrent IMAP sessions hard.
        try:
            client.logout()
        except Exception:  # noqa: BLE001
            pass


def _fetch_one(client: imaplib.IMAP4_SSL, message_id: bytes) -> MailHeader | None:
    # `search` hands back ids as bytes and `fetch` is typed for str; both
    # accept either at runtime, so the decode is for the type checker and
    # for the uid below.
    uid = message_id.decode("ascii", "replace")
    # **PEEK, not RFC822.** The ordinary fetch sets `\Seen` and would clear the
    # user's unread badge as a side effect of being asked to look.
    status, payload = client.fetch(uid, "(FLAGS BODY.PEEK[])")
    if status != "OK" or not payload:
        return None

    raw: bytes | None = None
    flags = ""
    for part in payload:
        if isinstance(part, tuple) and len(part) >= 2 and isinstance(part[1], bytes):
            raw = part[1]
            flags = part[0].decode("utf-8", "replace") if isinstance(part[0], bytes) else ""
        elif isinstance(part, bytes):
            flags += part.decode("utf-8", "replace")
    if raw is None:
        return None

    message = email.message_from_bytes(raw)
    body = _body_of(message)
    return MailHeader(
        uid=uid,
        subject=_decode(message.get("Subject")) or "(no subject)",
        sender=_decode(message.get("From")),
        date=_decode(message.get("Date")),
        unread="\\Seen" not in flags,
        body=body[:BODY_CHARS] + ("…" if len(body) > BODY_CHARS else ""),
    )


__all__ = [
    "BODY_CHARS",
    "KNOWN_HOSTS",
    "MAX_MESSAGES",
    "EmailUnavailable",
    "MailHeader",
    "fetch",
    "resolve_host",
]
