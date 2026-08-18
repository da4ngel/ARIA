"""The one Phase 3 acceptance-gate line that has never actually been run.

    "delete C:\\temp\\test.txt"  -> Deny -> file untouched
                                 -> Approve -> deleted, logged in tool_log

`test_permissions.py` proves the logic. This proves the product: a real file, a
real tier-3 tool, the real confirmation round trip over JSON-RPC, and the real
`tool_log` rows afterwards.

Answers the confirmation over RPC rather than by clicking, because the thing
under test is the sidecar's contract; the dialog itself is verified on screen.

Needs the sidecar running **with DANGER tools enabled**, or she is never told
`delete_file` exists and the gate cannot even start:

    ARIA_ALLOW_DANGER_TOOLS=true npm run dev
    python scripts/gate_delete.py

Measured 2026-08-09, the first time this line was ever actually run:

    DENY     -> file still there; tool_log approved=0 ok=0 error=denied
    APPROVE  -> file gone;        tool_log approved=1 by=user ok=1 2ms
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import sys

import websockets

SCRATCH = pathlib.Path.home() / "Downloads" / "aria-delete-gate.txt"


async def main() -> int:
    handshake = pathlib.Path("data/.handshake").read_text().strip()
    # `.handshake` is JSON when the sidecar wrote it, and a bare token when
    # Electron passed one in via ARIA_TOKEN.
    try:
        token = str(json.loads(handshake)["token"])
    except (json.JSONDecodeError, KeyError, TypeError):
        token = handshake

    async with websockets.connect(
        "ws://127.0.0.1:8765/rpc",
        additional_headers={"Authorization": f"Bearer {token}"},
        # She speaks, and synthesised audio is broadcast to every connected
        # client. The default 1MB frame limit closed this socket mid-gate.
        max_size=None,
    ) as ws:
        counter = [0]
        pending: dict[str, asyncio.Future[dict]] = {}
        confirmations: asyncio.Queue[dict] = asyncio.Queue()

        async def pump() -> None:
            async for raw in ws:
                message = json.loads(raw)
                if "id" in message and message["id"] in pending:
                    pending.pop(message["id"]).set_result(message)
                elif message.get("method") == "confirm.request":
                    await confirmations.put(message["params"])

        task = asyncio.create_task(pump())

        async def call(method: str, params: dict | None = None) -> dict:
            counter[0] += 1
            rid = counter[0]
            fut: asyncio.Future[dict] = asyncio.get_running_loop().create_future()
            pending[rid] = fut
            await ws.send(
                json.dumps({"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}})
            )
            message = await asyncio.wait_for(fut, timeout=180)
            if "error" in message:
                raise RuntimeError(message["error"])
            return dict(message["result"])

        async def ask_delete(approve: bool) -> None:
            """Send the turn, answer the confirmation, wait for the turn to end.

            **Its own session, never the user's.** `chat.send` with no
            `session_id` continues whatever conversation was most recently
            active, so a gate's probes — and the real `confirm.request`
            dialogs they raise — land in whatever Eyaas has open. That
            happened once already, with `gate_permission_modes.py`. The
            write-up of that incident said "unlike every other gate script
            here, all of which call `chat.new` first"; five of them did not,
            and this was one.
            """
            session = (await call("chat.new"))["session_id"]
            started = await call(
                "chat.send",
                {"text": f"delete the file {SCRATCH}", "session_id": session, "spoken": False}
            )
            turn_id = started["turn_id"]
            request = await asyncio.wait_for(confirmations.get(), timeout=120)
            print(
                f"   confirm.request  tool={request['tool']} tier={request['tier']} "
                f"args={request.get('args')}"
            )
            await call(
                "confirm.respond", {"request_id": request["request_id"], "approved": approve}
            )
            # Let the continuation finish so `tool_log` is written.
            for _ in range(120):
                await asyncio.sleep(0.25)
                if not (await call("system.health")).get("busy"):
                    break
            await asyncio.sleep(1.5)
            del turn_id

        SCRATCH.parent.mkdir(parents=True, exist_ok=True)
        SCRATCH.write_text("delete me", encoding="utf-8")
        print(f"scratch file: {SCRATCH}  exists={SCRATCH.exists()}")

        print("\n1. DENY")
        await ask_delete(approve=False)
        survived = SCRATCH.exists()
        print(f"   file still there: {survived}")

        print("\n2. APPROVE")
        await ask_delete(approve=True)
        gone = not SCRATCH.exists()
        print(f"   file gone: {gone}")

        task.cancel()

    print("\n--- tool_log ---")
    import sqlite3

    conn = sqlite3.connect("data/aria.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT tool, tier, approved, approved_by, ok, error, duration_ms, args "
        "FROM tool_log WHERE tool LIKE 'delete%' ORDER BY id DESC LIMIT 4"
    ).fetchall()
    for r in rows:
        print(
            f"   {r['tool']} tier={r['tier']} approved={r['approved']} "
            f"by={r['approved_by']} ok={r['ok']} error={r['error']} "
            f"{r['duration_ms']}ms args={r['args']}"
        )

    ok = survived and gone and len(rows) >= 2
    print("\nGATE:", "PASS" if ok else "FAIL")
    if SCRATCH.exists():
        SCRATCH.unlink()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
