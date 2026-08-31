"""AWS Signature Version 4, in stdlib only (Eyaas's Bedrock key, 2026-08-23).

**Written here rather than pulled in with `boto3` for the reason every other
hand-rolled parser in this project exists.** `botocore` ships several thousand
JSON service descriptions, needs its own PyInstaller hook, and adds tens of
megabytes to a bundle §2.3 already watches — to sign a request whose whole
algorithm is four nested HMACs. `boto3` is also synchronous, so a streaming
call would have to be pushed onto a thread and lose the cancellation semantics
`stream_chat` promises (Phase 1 gate: abort within 200ms).

The precedents are `providers/search.py`'s HTML parser and `core/extract.py`'s
`.pptx` reader. The difference worth naming: those fail *softly* — a bit of
navigation text in a summary. **A signing bug fails totally, and it fails
identically to a mistyped key**, which is the worst possible diagnostic.

**So the testable seam is the canonical request, not the signature.**
`hashlib` and `hmac` are not what is at risk here; the string fed to them is —
its blank lines, its header ordering, and the double-encoded path below.
`canonical_request()` and `string_to_sign()` are therefore separate pure
functions returning text a test can assert on character for character against
AWS's published specification, rather than against a digest constant nobody
reading this can check by eye.
"""

from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime
from urllib.parse import quote

ALGORITHM = "AWS4-HMAC-SHA256"
#: The signing service name for both `bedrock` and `bedrock-runtime` hosts.
SERVICE = "bedrock"


def _sign(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()


def signing_key(secret: str, datestamp: str, region: str, service: str) -> bytes:
    """The four nested HMACs. Derived per day, per region, per service."""
    date_key = _sign(f"AWS4{secret}".encode(), datestamp)
    region_key = _sign(date_key, region)
    service_key = _sign(region_key, service)
    return _sign(service_key, "aws4_request")


def encode_path_segment(segment: str) -> str:
    """One path segment as it appears in the **request URL**.

    Bedrock model ids carry colons (`anthropic.claude-sonnet-4-5-20250929-v1:0`)
    and inference-profile ids add a region prefix. A bare colon in a path is
    legal, but botocore percent-encodes it, and the signature has to describe
    the bytes actually sent — so it is encoded here too, the same way.
    """
    return quote(segment, safe="")


def canonical_path(path: str) -> str:
    """The path as it appears in the **canonical request**, which is not the
    same string as the one in the URL.

    **This looks like a double-encoding bug and is not.** AWS's own signing
    specification says every path segment is URI-encoded *twice* for every
    service except S3, and `botocore.auth.SigV4Auth` implements exactly that by
    running `quote(..., safe="/~")` over a path that has already been encoded
    once by the serialiser. So a model id containing `:` reaches the wire as
    `%3A` and reaches the string-to-sign as `%253A`.

    Getting this wrong produces `SignatureDoesNotMatch`, which reads exactly
    like a mistyped key — hence the note, and hence the test against AWS's
    published example rather than against this function's own output.
    """
    return quote(path, safe="/~")


def canonical_request(
    *,
    method: str,
    url_path: str,
    query: str,
    headers: dict[str, str],
    payload_hash: str,
) -> tuple[str, str]:
    """`(canonical request, signed header list)`, as plain text.

    `headers` must already be lowercased and complete — including `x-amz-date`
    and any session token — because the signed header list is derived from
    exactly what is passed.
    """
    ordered = sorted(headers)
    canonical_headers = "".join(f"{k}:{headers[k]}\n" for k in ordered)
    header_list = ";".join(ordered)
    request = "\n".join(
        [
            method.upper(),
            canonical_path(url_path),
            query,
            canonical_headers,
            header_list,
            payload_hash,
        ]
    )
    return request, header_list


def string_to_sign(*, amz_date: str, scope: str, request: str) -> str:
    return "\n".join(
        [
            ALGORITHM,
            amz_date,
            scope,
            hashlib.sha256(request.encode("utf-8")).hexdigest(),
        ]
    )


def signed_headers(
    *,
    method: str,
    url_path: str,
    query: str,
    headers: dict[str, str],
    payload: bytes,
    region: str,
    access_key: str,
    secret_key: str,
    session_token: str | None = None,
    service: str = SERVICE,
    now: datetime | None = None,
) -> dict[str, str]:
    """Return `headers` plus `Authorization`, `X-Amz-Date` and the payload hash.

    `url_path` is the path exactly as it will be sent, already encoded by
    `encode_path_segment`. The caller owns the URL; this only describes it.
    """
    moment = now or datetime.now(UTC)
    amz_date = moment.strftime("%Y%m%dT%H%M%SZ")
    datestamp = moment.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(payload).hexdigest()

    to_sign_headers = {k.lower(): v.strip() for k, v in headers.items()}
    to_sign_headers["x-amz-date"] = amz_date
    # **`x-amz-content-sha256` is deliberately not signed or sent.** It is
    # required for S3 and `botocore` adds it for S3 alone; including it here
    # would be harmless on the wire but would put this signer outside AWS's own
    # published test vector, which is the only independent check there is that
    # the canonicalisation below is right.
    if session_token:
        # Temporary credentials. Part of the signature, not merely sent
        # alongside it — omitting it here gives SignatureDoesNotMatch.
        to_sign_headers["x-amz-security-token"] = session_token

    request, header_list = canonical_request(
        method=method,
        url_path=url_path,
        query=query,
        headers=to_sign_headers,
        payload_hash=payload_hash,
    )
    scope = f"{datestamp}/{region}/{service}/aws4_request"
    signature = hmac.new(
        signing_key(secret_key, datestamp, region, service),
        string_to_sign(amz_date=amz_date, scope=scope, request=request).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    out = dict(headers)
    out["X-Amz-Date"] = amz_date
    if session_token:
        out["X-Amz-Security-Token"] = session_token
    out["Authorization"] = (
        f"{ALGORITHM} Credential={access_key}/{scope}, "
        f"SignedHeaders={header_list}, Signature={signature}"
    )
    return out


__all__ = [
    "ALGORITHM",
    "SERVICE",
    "canonical_path",
    "canonical_request",
    "encode_path_segment",
    "signed_headers",
    "signing_key",
    "string_to_sign",
]
