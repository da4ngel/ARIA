"""JSON-RPC 2.0 envelope types (BUILD_SPEC §7.1).

Requests and responses are correlated by ``id``. Server-initiated notifications
carry no ``id`` and expect no reply.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

JSONRPC_VERSION: Literal["2.0"] = "2.0"


class ErrorCode(IntEnum):
    """Standard JSON-RPC codes plus ARIA's application range."""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    # Application-defined (-32000 .. -32099)
    UNAUTHORIZED = -32000
    NOT_READY = -32001


class RpcRequest(BaseModel):
    """Client -> server call."""

    jsonrpc: Literal["2.0"] = JSONRPC_VERSION
    id: str | int | None = None
    method: str
    params: dict[str, Any] = Field(default_factory=dict)


class RpcError(BaseModel):
    code: int
    message: str
    data: Any = None


class RpcResponse(BaseModel):
    """Server -> client reply. Exactly one of ``result``/``error`` is set."""

    jsonrpc: Literal["2.0"] = JSONRPC_VERSION
    id: str | int | None = None
    result: Any = None
    error: RpcError | None = None


class RpcNotification(BaseModel):
    """Server -> client push. No ``id``, no reply expected (§7.1 events table)."""

    jsonrpc: Literal["2.0"] = JSONRPC_VERSION
    method: str
    params: dict[str, Any] = Field(default_factory=dict)


def ok(request_id: str | int | None, result: Any) -> RpcResponse:
    return RpcResponse(id=request_id, result=result)


def err(
    request_id: str | int | None,
    code: ErrorCode | int,
    message: str,
    data: Any = None,
) -> RpcResponse:
    return RpcResponse(id=request_id, error=RpcError(code=int(code), message=message, data=data))


class RpcMethodError(Exception):
    """Raised by a handler to return a specific JSON-RPC error to the client."""

    def __init__(self, code: ErrorCode | int, message: str, data: Any = None) -> None:
        super().__init__(message)
        self.code = int(code)
        self.message = message
        self.data = data
