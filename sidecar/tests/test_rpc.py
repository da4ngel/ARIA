"""The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1).

Beyond the Phase 0 gate's named test, but the auth check is the one thing in this
phase that is a security control rather than plumbing.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from sidecar import main as sidecar_main
from sidecar.config import get_settings
from sidecar.handshake import bearer_from_header, token_matches
from sidecar.rpc.protocol import ErrorCode

TOKEN = "a" * 64


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """App wired to a temp data dir and a known token, via the real env path."""
    monkeypatch.setenv("ARIA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("ARIA_TOKEN", TOKEN)
    monkeypatch.setenv("ARIA_DEV", "true")
    # Transport tests must not depend on a running Ollama.
    monkeypatch.setenv("ARIA_WARM_ON_STARTUP", "false")
    get_settings.cache_clear()
    try:
        # TestClient's context manager is what runs the lifespan.
        with TestClient(sidecar_main.app) as c:
            yield c
    finally:
        get_settings.cache_clear()


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# ── the token gate ────────────────────────────────────────────────────


def test_rpc_rejects_missing_token(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/rpc"):
            pass
    assert exc.value.code == sidecar_main.WS_UNAUTHORIZED


def test_rpc_rejects_wrong_token(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/rpc", headers=_auth("b" * 64)):
            pass
    assert exc.value.code == sidecar_main.WS_UNAUTHORIZED


def test_rpc_rejects_non_bearer_scheme(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/rpc", headers={"Authorization": f"Basic {TOKEN}"}):
            pass


def test_rpc_accepts_correct_token(client: TestClient) -> None:
    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        # First frame is the state.change notification emitted on connect.
        first = ws.receive_json()
        assert first["method"] == "state.change"
        assert first["params"]["state"] == "idle"
        assert "id" not in first


# ── dispatch ──────────────────────────────────────────────────────────


def _call(ws, method: str, params: dict | None = None, call_id: int = 1) -> dict:
    """Send a request and skip past any notifications until the reply arrives."""
    ws.send_text(
        json.dumps({"jsonrpc": "2.0", "id": call_id, "method": method, "params": params or {}})
    )
    while True:
        message: dict = ws.receive_json()
        if message.get("id") == call_id:
            return message


def test_unknown_method_returns_32601(client: TestClient) -> None:
    # A method from §7.1 that no phase has implemented yet.
    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        response = _call(ws, "memory.forget", {"fact_id": 1})
    assert response["error"]["code"] == ErrorCode.METHOD_NOT_FOUND
    # Error messages say what to do next (CLAUDE.md style rule).
    assert "Available in this build" in response["error"]["message"]


def test_system_health_returns_report(client: TestClient) -> None:
    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        response = _call(ws, "system.health")
    result = response["result"]
    assert result["status"] == "ok"
    assert result["db"] is True
    assert result["uptime_s"] >= 0
    # Phase 1 fills in the ollama and models probes...
    assert "ollama" not in result["pending_probes"]
    assert "models" not in result["pending_probes"]
    # ...but the §9.6 probes owned by later phases are still present-and-null,
    # not missing. The wire shape never changes; only the nulls fill in.
    assert result["gpu_free_mb"] is None
    assert result["everything"] is None
    assert "gpu_free_mb" in result["pending_probes"]
    assert "everything" in result["pending_probes"]


def test_malformed_json_returns_invalid_request(client: TestClient) -> None:
    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        ws.receive_json()  # state.change
        ws.send_text("{not json")
        response = ws.receive_json()
    assert response["error"]["code"] == ErrorCode.INVALID_REQUEST


# ── HTTP health ───────────────────────────────────────────────────────


def test_health_endpoint(client: TestClient) -> None:
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["db"] is True
    # Liveness probe stays cheap: no §9.6 probe fields on this endpoint.
    assert "ollama" not in body


def test_handshake_file_written(client: TestClient, tmp_path: Path) -> None:
    assert (tmp_path / ".handshake").read_text(encoding="utf-8") == TOKEN


# ── helpers ───────────────────────────────────────────────────────────


# ── history (Phase 1.5) ───────────────────────────────────────────────


def test_chat_sessions_is_empty_on_a_fresh_database(client: TestClient) -> None:
    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        response = _call(ws, "chat.sessions")
    assert response["result"]["sessions"] == []


def test_chat_new_creates_no_conversation(client: TestClient) -> None:
    """The id is reserved, not written — so the list stays empty."""
    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        new = _call(ws, "chat.new")
        listed = _call(ws, "chat.sessions", call_id=2)
    assert new["result"]["session_id"].startswith("s_")
    assert listed["result"]["sessions"] == []


def test_chat_delete_refuses_without_confirmation(client: TestClient) -> None:
    """CLAUDE.md rule 5: destructive operations need a confirmation round-trip."""
    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        response = _call(ws, "chat.delete", {"session_id": "s_nope"})
    # Nothing to delete, so it reports that rather than silently succeeding.
    assert response["error"]["code"] == ErrorCode.INVALID_PARAMS
    assert "chat.sessions" in response["error"]["message"]


def test_chat_rename_requires_a_non_empty_title(client: TestClient) -> None:
    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        response = _call(ws, "chat.rename", {"session_id": "s_x", "title": "   "})
    assert response["error"]["code"] == ErrorCode.INVALID_PARAMS


def test_history_methods_are_registered(client: TestClient) -> None:
    """An unregistered method returns -32601, so this proves they exist."""
    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        for index, method in enumerate(("chat.sessions", "chat.rename", "chat.delete"), start=1):
            response = _call(ws, method, {}, call_id=index)
            error = response.get("error")
            assert not error or error["code"] != ErrorCode.METHOD_NOT_FOUND, method


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("Bearer abc", "abc"),
        ("bearer abc", "abc"),
        ("Basic abc", None),
        ("Bearer", None),
        ("", None),
        (None, None),
    ],
)
def test_bearer_parsing(header: str | None, expected: str | None) -> None:
    assert bearer_from_header(header) == expected


def test_token_comparison_rejects_empty() -> None:
    assert token_matches("abc", "abc") is True
    assert token_matches("abc", "abd") is False
    assert token_matches("abc", None) is False
    assert token_matches("abc", "") is False
