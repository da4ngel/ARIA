"""The `vnd.amazon.eventstream` decoder.

Frames are built with `encode_event`, which implements the framing from the
specification independently of the decoder — prelude, header table, both CRCs.
A fixture blob captured from a real response would be better still, but it
cannot be obtained without a key; this at least means the decoder is not being
checked against its own idea of the format.
"""

from __future__ import annotations

import json
import zlib

import pytest

from sidecar.providers.eventstream import (
    EventStreamDecoder,
    EventStreamError,
    encode_event,
)


def _frame(event_type: str, body: dict) -> bytes:
    return encode_event(
        {":message-type": "event", ":event-type": event_type},
        json.dumps(body).encode("utf-8"),
    )


def test_one_whole_frame_decodes() -> None:
    decoder = EventStreamDecoder()
    (event,) = decoder.feed(_frame("contentBlockDelta", {"delta": {"text": "hi"}}))
    assert event.event_type == "contentBlockDelta"
    assert event.message_type == "event"
    assert event.json() == {"delta": {"text": "hi"}}
    assert decoder.pending_bytes == 0


def test_several_frames_in_one_chunk_all_decode() -> None:
    """One TCP read routinely carries more than one frame."""
    blob = _frame("messageStart", {"role": "assistant"}) + _frame(
        "contentBlockDelta", {"delta": {"text": "a"}}
    )
    events = EventStreamDecoder().feed(blob)
    assert [e.event_type for e in events] == ["messageStart", "contentBlockDelta"]


def test_a_frame_split_across_chunks_is_buffered_until_complete() -> None:
    """**The reason a decoder exists at all.** `aiter_bytes` splits wherever
    the network did, which is never at a frame boundary."""
    blob = _frame("contentBlockDelta", {"delta": {"text": "split"}})
    decoder = EventStreamDecoder()
    for at in range(1, len(blob)):
        first = decoder.feed(blob[:at])
        assert first == [], f"emitted a frame after only {at} of {len(blob)} bytes"
        rest = decoder.feed(blob[at:])
        assert len(rest) == 1
        assert rest[0].json() == {"delta": {"text": "split"}}
        decoder = EventStreamDecoder()


def test_one_byte_at_a_time_still_decodes() -> None:
    blob = _frame("messageStop", {"stopReason": "end_turn"})
    decoder = EventStreamDecoder()
    out = [e for byte in blob for e in decoder.feed(bytes([byte]))]
    assert len(out) == 1
    assert out[0].event_type == "messageStop"


def test_an_exception_frame_is_recognisable_as_one() -> None:
    frame = encode_event(
        {":message-type": "exception", ":exception-type": "throttlingException"},
        b'{"message":"Too many requests"}',
    )
    (event,) = EventStreamDecoder().feed(frame)
    assert event.message_type == "exception"
    assert event.exception_type == "throttlingException"
    assert event.json()["message"] == "Too many requests"


def test_a_corrupt_payload_is_caught_by_the_checksum() -> None:
    """Without the CRC this arrives at `json.loads` and reads as a malformed
    reply from the model rather than as a damaged connection."""
    blob = bytearray(_frame("contentBlockDelta", {"delta": {"text": "hello"}}))
    blob[-8] ^= 0xFF  # inside the payload, before the trailing CRC
    with pytest.raises(EventStreamError, match="checksum"):
        EventStreamDecoder().feed(bytes(blob))


def test_a_corrupt_prelude_is_caught_before_its_lengths_are_trusted() -> None:
    blob = bytearray(_frame("messageStop", {}))
    blob[5] ^= 0x0F  # header length, which the prelude CRC covers
    with pytest.raises(EventStreamError):
        EventStreamDecoder().feed(bytes(blob))


def test_a_length_that_cannot_hold_its_own_headers_is_refused() -> None:
    """A frame claiming fewer bytes than its header table needs would make the
    payload slice run backwards and silently produce nonsense."""
    headers = b""
    prelude = (8).to_bytes(4, "big") + (999).to_bytes(4, "big")
    blob = prelude + zlib.crc32(prelude).to_bytes(4, "big") + headers
    with pytest.raises(EventStreamError, match="cannot hold"):
        EventStreamDecoder().feed(blob + b"\x00" * 64)


def test_a_payload_that_is_not_json_yields_an_empty_dict_not_an_exception() -> None:
    """Raising here would end a turn that has already produced text."""
    frame = encode_event({":event-type": "metadata"}, b"not json at all")
    (event,) = EventStreamDecoder().feed(frame)
    assert event.json() == {}


def test_an_unknown_event_type_reads_as_empty_rather_than_raising() -> None:
    (event,) = EventStreamDecoder().feed(encode_event({":other": "x"}, b"{}"))
    assert event.event_type == ""
    assert event.message_type == ""
