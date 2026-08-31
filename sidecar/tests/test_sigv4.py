"""SigV4, tested where it can actually be wrong.

**The signature itself is not the risk and is not asserted against a
constant.** `hmac.new(..., hashlib.sha256)` is stdlib and is not going to
produce the wrong digest; what goes wrong in a hand-written signer is the
*string* fed to it — a missing blank line, headers in the wrong order, a path
encoded once where AWS wants it twice. So these assert on the canonical
request and the string to sign, which are plain text a reader can check
against AWS's published specification without running anything.

The one thing no test here can establish is that AWS agrees. That needs a real
key and a real request, and it is recorded as an open line rather than implied
by a green suite.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from sidecar.providers.sigv4 import (
    canonical_path,
    canonical_request,
    encode_path_segment,
    signed_headers,
    signing_key,
    string_to_sign,
)

WHEN = datetime(2015, 8, 30, 12, 36, 0, tzinfo=UTC)
SECRET = "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY"
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_the_empty_payload_hash_is_the_known_constant() -> None:
    """A sanity anchor: every canonical request for a GET ends in this."""
    assert hashlib.sha256(b"").hexdigest() == EMPTY_SHA256


def test_the_canonical_request_matches_the_published_form_exactly() -> None:
    """AWS's `get-vanilla` case, written out as the specification gives it.

    Six sections joined by newlines, and **two of them look like mistakes**:
    the empty query string leaves a blank line, and the canonical header block
    ends in its own newline so there is a second blank line before the signed
    header list. Both are required. Dropping either is the classic SigV4 bug
    and produces `SignatureDoesNotMatch` with no other clue.
    """
    request, header_list = canonical_request(
        method="GET",
        url_path="/",
        query="",
        headers={
            "host": "example.amazonaws.com",
            "x-amz-date": "20150830T123600Z",
        },
        payload_hash=EMPTY_SHA256,
    )
    assert request == (
        "GET\n"
        "/\n"
        "\n"
        "host:example.amazonaws.com\n"
        "x-amz-date:20150830T123600Z\n"
        "\n"
        "host;x-amz-date\n" + EMPTY_SHA256
    )
    assert header_list == "host;x-amz-date"


def test_headers_are_sorted_by_name_not_by_insertion() -> None:
    request, header_list = canonical_request(
        method="POST",
        url_path="/",
        query="",
        headers={"x-amz-date": "D", "host": "h", "content-type": "application/json"},
        payload_hash=EMPTY_SHA256,
    )
    assert header_list == "content-type;host;x-amz-date"
    assert "content-type:application/json\nhost:h\nx-amz-date:D\n" in request


def test_the_string_to_sign_is_four_lines_and_hashes_the_request() -> None:
    request, _ = canonical_request(
        method="GET",
        url_path="/",
        query="",
        headers={"host": "h", "x-amz-date": "20150830T123600Z"},
        payload_hash=EMPTY_SHA256,
    )
    signed = string_to_sign(
        amz_date="20150830T123600Z",
        scope="20150830/us-east-1/service/aws4_request",
        request=request,
    )
    assert signed.split("\n") == [
        "AWS4-HMAC-SHA256",
        "20150830T123600Z",
        "20150830/us-east-1/service/aws4_request",
        hashlib.sha256(request.encode()).hexdigest(),
    ]


# ── the path, which is where Bedrock differs from every other service ──


def test_a_model_id_is_percent_encoded_once_for_the_url() -> None:
    """`anthropic.claude-...-v1:0` — the colon is what matters."""
    assert (
        encode_path_segment("anthropic.claude-sonnet-4-5-20250929-v1:0")
        == "anthropic.claude-sonnet-4-5-20250929-v1%3A0"
    )


def test_and_encoded_a_second_time_for_the_canonical_request() -> None:
    """**This is the part that looks like a bug.** AWS signs a doubly-encoded
    path for every service but S3, so `%3A` on the wire is `%253A` in the
    string to sign. Getting it wrong is indistinguishable from a bad key."""
    url_path = "/model/anthropic.claude-v1%3A0/converse-stream"
    assert canonical_path(url_path) == "/model/anthropic.claude-v1%253A0/converse-stream"


def test_slashes_survive_canonicalisation() -> None:
    """Segment separators are not encoded, or the path stops being a path."""
    assert canonical_path("/model/x/converse-stream").count("/") == 3


# ── the assembled header set ──


def _sign(**overrides: object) -> dict[str, str]:
    kwargs: dict = {
        "method": "POST",
        "url_path": "/model/m/converse-stream",
        "query": "",
        "headers": {"Content-Type": "application/json", "Host": "h.amazonaws.com"},
        "payload": b'{"a":1}',
        "region": "us-east-1",
        "access_key": "AKIDEXAMPLE",
        "secret_key": SECRET,
        "now": WHEN,
    }
    kwargs.update(overrides)
    return signed_headers(**kwargs)


def test_the_authorization_header_names_the_scope_and_the_signed_headers() -> None:
    out = _sign()
    assert out["X-Amz-Date"] == "20150830T123600Z"
    assert "Credential=AKIDEXAMPLE/20150830/us-east-1/bedrock/aws4_request" in (
        out["Authorization"]
    )
    assert "SignedHeaders=content-type;host;x-amz-date," in out["Authorization"]


def test_the_caller_s_own_headers_are_returned_untouched() -> None:
    """The signer describes the request; it does not get to rewrite it."""
    out = _sign()
    assert out["Content-Type"] == "application/json"
    assert out["Host"] == "h.amazonaws.com"


def test_content_sha256_is_neither_signed_nor_sent() -> None:
    """S3 wants it and nothing else does — see the note in `sigv4.py`."""
    out = _sign()
    assert not any(k.lower() == "x-amz-content-sha256" for k in out)
    assert "x-amz-content-sha256" not in out["Authorization"]


def test_a_session_token_is_part_of_the_signature_not_merely_sent() -> None:
    """Temporary credentials fail with `SignatureDoesNotMatch` if the token is
    attached to the request but left out of the signed header list."""
    out = _sign(session_token="FQoGZXIvYXdzEBYa")
    assert out["X-Amz-Security-Token"] == "FQoGZXIvYXdzEBYa"
    assert "x-amz-security-token" in out["Authorization"]
    assert _sign()["Authorization"] != out["Authorization"]


def test_the_body_changes_the_signature() -> None:
    """The payload hash is in the canonical request, so it must."""
    assert _sign(payload=b'{"a":1}') != _sign(payload=b'{"a":2}')


def test_the_same_request_signs_identically_given_the_same_clock() -> None:
    assert _sign() == _sign()


def test_the_signing_key_is_derived_per_day_region_and_service() -> None:
    """Four nested HMACs. Any two differing inputs must give different keys."""
    base = signing_key(SECRET, "20150830", "us-east-1", "bedrock")
    assert base != signing_key(SECRET, "20150831", "us-east-1", "bedrock")
    assert base != signing_key(SECRET, "20150830", "eu-west-1", "bedrock")
    assert base != signing_key(SECRET, "20150830", "us-east-1", "s3")
    assert len(base) == 32
