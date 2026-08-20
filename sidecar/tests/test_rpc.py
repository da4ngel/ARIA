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
    # Nor on the speech models. The lifespan warms both on startup, and the
    # first Whisper load downloads ~150MB and takes ~33s — which turned an
    # 11-second suite into minutes of silence.
    monkeypatch.setenv("ARIA_VOICE_ENABLED", "false")
    # Nor on the file indexer, which otherwise walks the *real* Documents,
    # Desktop and Downloads of whoever runs the suite — reading their
    # spreadsheets, and taking as long as that takes.
    monkeypatch.setenv("ARIA_INDEX_FILES", "false")
    # Nor on the nightly reflection, for the same reason: the scheduler works
    # then sleeps, so starting it inside the fixture fires a real model call on
    # the first tick. Retrieval stays on — it is free and never leaves the box.
    monkeypatch.setenv("ARIA_MEMORY_REFLECTION_ENABLED", "false")
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


# §7.1's method table, in spec order. The test below picks whichever of these
# no phase has implemented yet, rather than naming one — this test used to
# hardcode `memory.forget`, and Phase 5 implementing it turned a passing test
# into a failing one for no reason connected to what it checks.
SPEC_METHODS = (
    "chat.send",
    "chat.cancel",
    "audio.chunk",
    "audio.end",
    "confirm.respond",
    "memory.search",
    "memory.forget",
    "settings.get",
    "settings.set",
    "system.health",
)


def test_unknown_method_returns_32601(client: TestClient) -> None:
    from sidecar.rpc.handlers import method_names

    implemented = method_names()
    unimplemented = next((m for m in SPEC_METHODS if m not in implemented), None)
    assert (
        unimplemented is not None
    ), "Every §7.1 method is implemented — pick a different probe for this test."

    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        response = _call(ws, unimplemented, {})
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
    # Phase 1 filled in ollama and models; Phase 4a filled in everything.
    assert "ollama" not in result["pending_probes"]
    assert "models" not in result["pending_probes"]
    assert "everything" not in result["pending_probes"]
    # Whether Everything is installed varies by machine; that it is now a
    # boolean rather than "not asked yet" does not.
    assert isinstance(result["everything"], bool)
    # ...while the §9.6 probes owned by later phases stay present-and-null
    # rather than missing. The wire shape never changes; only the nulls fill in.
    assert result["gpu_free_mb"] is None
    assert "gpu_free_mb" in result["pending_probes"]


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


# ── proactivity (Phase 8) ─────────────────────────────────────────────


def test_proactivity_trigger_is_registered(client: TestClient) -> None:
    """This machine's `client` fixture runs the real lifespan against a real
    Ollama (the same reason `ARIA_INDEX_FILES=false` exists for the finder),
    so the scheduler is genuinely running here — the call succeeds rather
    than refusing. `test_proactivity_trigger_refuses_when_switched_off`
    covers the off path explicitly, with the flag forced rather than relying
    on it happening to be off."""
    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        response = _call(ws, "proactivity.trigger", {})
    assert response.get("error") is None
    assert response["result"] == {"ok": True}


def test_proactivity_trigger_refuses_when_switched_off(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The `client` fixture above leaves `proactivity_enabled` at its
    default (True) and happens to have a real Ollama to start against on
    this machine — a separate app instance here forces the flag off, the
    same explicit-not-incidental style `client`'s own env vars use."""
    monkeypatch.setenv("ARIA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("ARIA_TOKEN", TOKEN)
    monkeypatch.setenv("ARIA_DEV", "true")
    monkeypatch.setenv("ARIA_WARM_ON_STARTUP", "false")
    monkeypatch.setenv("ARIA_VOICE_ENABLED", "false")
    monkeypatch.setenv("ARIA_INDEX_FILES", "false")
    monkeypatch.setenv("ARIA_MEMORY_REFLECTION_ENABLED", "false")
    monkeypatch.setenv("ARIA_PROACTIVITY_ENABLED", "false")
    get_settings.cache_clear()
    try:
        with TestClient(sidecar_main.app) as test_client:
            with test_client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
                response = _call(ws, "proactivity.trigger", {})
    finally:
        get_settings.cache_clear()
    assert response["error"]["code"] == ErrorCode.INTERNAL_ERROR
    assert "not available" in response["error"]["message"]


def test_token_comparison_rejects_empty() -> None:
    assert token_matches("abc", "abc") is True
    assert token_matches("abc", "abd") is False
    assert token_matches("abc", None) is False
    assert token_matches("abc", "") is False


# ── a second sidecar must not touch the first one's state ─────────────


def test_a_taken_port_is_detected_before_anything_starts() -> None:
    """The incident, in one assertion. uvicorn runs the lifespan *before* it
    binds, so a duplicate sidecar used to run all of `_startup` — new token,
    handshake overwritten, database opened, Ollama spawned — fail to bind,
    then run all of `_shutdown` and delete the handshake it had just made its
    own. The running sidecar kept serving with no handshake on disk, and
    every gate script died with `FileNotFoundError` naming the process that
    worked.
    """
    import socket

    from sidecar.main import _port_is_free

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as held:
        held.bind(("127.0.0.1", 0))
        held.listen(1)
        port = held.getsockname()[1]

        assert not _port_is_free("127.0.0.1", port)

    # And free again once the holder lets go, or a restart could never work.
    assert _port_is_free("127.0.0.1", port)


# ── the file browser panel's own RPCs (Part 3) ────────────────────────
#
# UI-facing, not model-facing. `list_folder` summarises for a model and caps
# at what fits in a prompt; a panel wants everything, with sizes and dates,
# and pays no context for it. What does *not* differ is the refusals —
# `tools/files.py`'s hard blocks were never confirmation mechanisms, and a
# click is not a reason to relax them.


async def test_browse_with_no_path_offers_somewhere_to_start() -> None:
    from sidecar.rpc.handlers import files_browse

    listing = await files_browse({})

    assert listing["path"] == ""
    assert listing["entries"], "an empty first render is a dead end"
    assert any(e["kind"] == "drive" for e in listing["entries"]), "the whole machine is reachable"


async def test_browse_lists_a_real_folder_with_sizes_and_dates(tmp_path: Path) -> None:
    from sidecar.rpc.handlers import files_browse

    (tmp_path / "b.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "sub").mkdir()

    listing = await files_browse({"path": str(tmp_path)})

    names = [e["name"] for e in listing["entries"]]
    # Folders first, then by name — Explorer's own order, and the one people
    # navigate by without thinking about it.
    assert names == ["sub", "b.txt"]
    found = next(e for e in listing["entries"] if e["name"] == "b.txt")
    assert found["size"] == 5
    assert found["modified"] > 0
    assert listing["parent"] == str(tmp_path.parent)


async def test_browsing_something_that_is_not_a_folder_is_a_clear_error(tmp_path: Path) -> None:
    from sidecar.rpc.handlers import files_browse
    from sidecar.rpc.protocol import RpcMethodError

    target = tmp_path / "a.txt"
    target.write_text("x", encoding="utf-8")

    with pytest.raises(RpcMethodError):
        await files_browse({"path": str(target)})


async def test_rename_refuses_a_path_that_is_a_name(tmp_path: Path) -> None:
    """ "Rename it to ../../etc" is not a rename. Same guard `rename_file`
    already carries, because it is as true of a click as of a tool call."""
    from sidecar.rpc.handlers import files_rename
    from sidecar.rpc.protocol import RpcMethodError

    target = tmp_path / "a.txt"
    target.write_text("x", encoding="utf-8")

    with pytest.raises(RpcMethodError):
        await files_rename({"path": str(target), "name": "../../elsewhere.txt"})
    assert target.exists()


async def test_rename_works_and_will_not_overwrite(tmp_path: Path) -> None:
    from sidecar.rpc.handlers import files_rename
    from sidecar.rpc.protocol import RpcMethodError

    target = tmp_path / "a.txt"
    target.write_text("x", encoding="utf-8")
    (tmp_path / "taken.txt").write_text("y", encoding="utf-8")

    result = await files_rename({"path": str(target), "name": "b.txt"})
    assert (tmp_path / "b.txt").exists()
    assert result["path"] == str(tmp_path / "b.txt")

    with pytest.raises(RpcMethodError):
        await files_rename({"path": str(tmp_path / "b.txt"), "name": "taken.txt"})


async def test_the_panel_cannot_touch_a_system_folder() -> None:
    """The refusals in `tools/files.py` are reused rather than reimplemented.
    Trust and mode decide whether she *asks*; these decide what is allowed at
    all, and a panel does not get its own answer to that."""
    from sidecar.rpc.handlers import files_delete, files_rename
    from sidecar.rpc.protocol import RpcMethodError

    with pytest.raises(RpcMethodError):
        await files_rename({"path": "C:/Windows", "name": "Windows2"})
    with pytest.raises(RpcMethodError):
        await files_delete({"path": "C:/Windows"})


# ── study state ───────────────────────────────────────────────────────


def test_study_state_is_empty_before_anything_is_studied(client: TestClient) -> None:
    """`None`, not an error. A fresh install has never studied anything, and a
    read that raises for the ordinary case would make the caller treat a normal
    state as a fault."""
    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        result = _call(ws, "study.state")["result"]

    assert result == {"subject": None, "concepts": []}


def test_study_state_reports_the_map_and_what_it_has_earned(client: TestClient) -> None:
    """The read `scripts/gate_study.py` asserts on instead of on her prose — a
    model that says it recorded an answer and a row that changed are different
    claims, and only the second is what the next session reads."""
    import anyio

    from sidecar.memory import study
    from sidecar.state import runtime

    async def _seed() -> None:
        db = runtime.require_db()
        subject_id = await study.ensure_subject(db, "Kestrel", "C:/lectures/kestrel.txt")
        await study.add_concepts(db, subject_id, [("Handshake", "three messages"), ("Drift", "")])
        state = await study.state(db, subject_id)
        assert state is not None
        await study.record_answer(db, state.concepts[0].id, correct=True)

    anyio.run(_seed)

    with client.websocket_connect("/rpc", headers=_auth(TOKEN)) as ws:
        result = _call(ws, "study.state")["result"]

    assert result["subject"] == "Kestrel"
    assert result["source_path"] == "C:/lectures/kestrel.txt"
    assert [c["name"] for c in result["concepts"]] == ["Handshake", "Drift"]
    assert result["covered"] == 1
    assert result["next"] == "Handshake", "a shaky concept is taught before a new one"
