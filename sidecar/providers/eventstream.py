"""AWS's binary event-stream framing, which is what Bedrock streams.

Every other provider here streams SSE — `data: {...}` lines that `aiter_lines`
hands over ready to parse. Bedrock does not: `ConverseStream` responds with
`application/vnd.amazon.eventstream`, a length-prefixed binary framing with its
own header table and two CRCs. So there is a decoder, and it is the reason this
provider could not simply subclass `OpenAIProvider` the way OpenRouter did.

One frame:

    +---------------+---------------+---------------+
    | total length  | header length | prelude CRC   |   4 bytes each, big-endian
    +---------------+---------------+---------------+
    | headers (header length bytes)                 |
    +-----------------------------------------------+
    | payload (total - headers - 16 bytes)          |
    +-----------------------------------------------+
    | message CRC                                   |   4 bytes
    +-----------------------------------------------+

**Both CRCs are checked.** They cost a `zlib.crc32` each and they are the only
thing that can tell a truncated frame from a short one — without them a
half-arrived payload reaches `json.loads` as a syntax error, which reads like
a malformed reply from the model rather than a dropped connection.
"""

from __future__ import annotations

import json
import zlib
from dataclasses import dataclass, field
from typing import Any

_PRELUDE_BYTES = 12
_CRC_BYTES = 4
#: total-length + header-length + prelude CRC + trailing message CRC.
_OVERHEAD = _PRELUDE_BYTES + _CRC_BYTES

# Header value types, from the event-stream specification. Only the string
# type carries anything this project reads (`:event-type`, `:exception-type`),
# but every type has to be *skipped* correctly or the header walk desynchronises
# and every later header is garbage.
_BOOL_TRUE = 0
_BOOL_FALSE = 1
_BYTE = 2
_SHORT = 3
_INTEGER = 4
_LONG = 5
_BYTE_ARRAY = 6
_STRING = 7
_TIMESTAMP = 8
_UUID = 9

_FIXED_WIDTH = {
    _BOOL_TRUE: 0,
    _BOOL_FALSE: 0,
    _BYTE: 1,
    _SHORT: 2,
    _INTEGER: 4,
    _LONG: 8,
    _TIMESTAMP: 8,
    _UUID: 16,
}
_LENGTH_PREFIXED = {_BYTE_ARRAY, _STRING}


class EventStreamError(ValueError):
    """A frame that cannot be trusted — bad CRC, or a length that does not fit."""


@dataclass(slots=True)
class Event:
    """One decoded frame."""

    headers: dict[str, Any] = field(default_factory=dict)
    payload: bytes = b""

    @property
    def event_type(self) -> str:
        """`messageStart`, `contentBlockDelta`, `metadata`, and so on."""
        value = self.headers.get(":event-type")
        return value if isinstance(value, str) else ""

    @property
    def message_type(self) -> str:
        """`event`, or `exception` when the service is reporting a failure."""
        value = self.headers.get(":message-type")
        return value if isinstance(value, str) else ""

    @property
    def exception_type(self) -> str:
        value = self.headers.get(":exception-type")
        return value if isinstance(value, str) else ""

    def json(self) -> dict[str, Any]:
        """The payload, or an empty dict — never an exception.

        A frame whose payload is not an object is not something a caller can
        act on, and raising here would take down a turn that has already
        produced text.
        """
        if not self.payload:
            return {}
        try:
            body = json.loads(self.payload)
        except json.JSONDecodeError:
            return {}
        return body if isinstance(body, dict) else {}


def _parse_headers(raw: bytes) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    at = 0
    end = len(raw)
    while at < end:
        name_len = raw[at]
        at += 1
        name = raw[at : at + name_len].decode("utf-8", "replace")
        at += name_len
        value_type = raw[at]
        at += 1

        if value_type in _FIXED_WIDTH:
            width = _FIXED_WIDTH[value_type]
            if value_type == _BOOL_TRUE:
                headers[name] = True
            elif value_type == _BOOL_FALSE:
                headers[name] = False
            else:
                headers[name] = int.from_bytes(raw[at : at + width], "big", signed=True)
            at += width
        elif value_type in _LENGTH_PREFIXED:
            width = int.from_bytes(raw[at : at + 2], "big")
            at += 2
            chunk = raw[at : at + width]
            headers[name] = (
                chunk.decode("utf-8", "replace") if value_type == _STRING else chunk
            )
            at += width
        else:
            # An unknown type has an unknown width, so the rest of the table
            # cannot be walked. Stop rather than return nonsense.
            break
    return headers


class EventStreamDecoder:
    """Bytes in, whole frames out. Holds the partial frame between reads.

    `httpx.aiter_bytes` yields whatever arrived, which splits frames at
    arbitrary points and packs several into one chunk. This buffers until a
    frame is complete and never assumes a chunk boundary means anything.
    """

    def __init__(self) -> None:
        self._buffer = bytearray()

    def feed(self, chunk: bytes) -> list[Event]:
        """Add bytes; return every frame that is now complete."""
        self._buffer.extend(chunk)
        events: list[Event] = []
        while (event := self._take_one()) is not None:
            events.append(event)
        return events

    @property
    def pending_bytes(self) -> int:
        """What is buffered but not yet a whole frame. For tests and logs."""
        return len(self._buffer)

    def _take_one(self) -> Event | None:
        if len(self._buffer) < _PRELUDE_BYTES:
            return None

        total = int.from_bytes(self._buffer[0:4], "big")
        headers_len = int.from_bytes(self._buffer[4:8], "big")
        prelude_crc = int.from_bytes(self._buffer[8:12], "big")

        if total < _OVERHEAD + headers_len:
            raise EventStreamError(
                f"Event frame declares {total} bytes, which cannot hold "
                f"{headers_len} bytes of headers. The stream is out of step; "
                f"the connection has to be restarted."
            )
        if len(self._buffer) < total:
            return None

        if zlib.crc32(self._buffer[0:8]) != prelude_crc:
            raise EventStreamError(
                "Event frame prelude failed its checksum — the stream is "
                "corrupt or out of step. Retry the request."
            )
        stated = int.from_bytes(self._buffer[total - _CRC_BYTES : total], "big")
        if zlib.crc32(self._buffer[0 : total - _CRC_BYTES]) != stated:
            raise EventStreamError(
                "Event frame failed its checksum — the reply arrived damaged. "
                "Retry the request."
            )

        headers_end = _PRELUDE_BYTES + headers_len
        event = Event(
            headers=_parse_headers(bytes(self._buffer[_PRELUDE_BYTES:headers_end])),
            payload=bytes(self._buffer[headers_end : total - _CRC_BYTES]),
        )
        del self._buffer[:total]
        return event


def encode_event(headers: dict[str, str], payload: bytes) -> bytes:
    """Build one frame. **Tests only** — nothing here ever sends this framing.

    It exists so the decoder is tested against frames built to the
    specification rather than against a fixture that agrees with whatever the
    decoder happens to do, which is the same reason `discovery.py` keeps real
    provider payloads in `tests/fixtures/`.
    """
    raw_headers = bytearray()
    for name, value in headers.items():
        encoded_name = name.encode("utf-8")
        encoded_value = value.encode("utf-8")
        raw_headers.append(len(encoded_name))
        raw_headers.extend(encoded_name)
        raw_headers.append(_STRING)
        raw_headers.extend(len(encoded_value).to_bytes(2, "big"))
        raw_headers.extend(encoded_value)

    total = _OVERHEAD + len(raw_headers) + len(payload)
    prelude = total.to_bytes(4, "big") + len(raw_headers).to_bytes(4, "big")
    frame = bytearray(prelude)
    frame.extend(zlib.crc32(prelude).to_bytes(4, "big"))
    frame.extend(raw_headers)
    frame.extend(payload)
    frame.extend(zlib.crc32(frame).to_bytes(4, "big"))
    return bytes(frame)


__all__ = ["Event", "EventStreamDecoder", "EventStreamError", "encode_event"]
