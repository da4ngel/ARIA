"""Permission modes (manual / auto / full_access), against the real sidecar.

    MANUAL,       a trusted-folder write   -> still asks
    FULL_ACCESS,  a DANGER-tier delete     -> no confirm.request at all,
                                               and DANGER did not need
                                               ARIA_ALLOW_DANGER_TOOLS set
    back to AUTO, the exact same delete    -> asks again

`test_permissions.py` proves the engine logic against fake tools with no
sidecar at all. This proves the product: a real turn, the real model
choosing the real tool, the real confirmation round trip (or the real
absence of one) over JSON-RPC, and the real `tool_log` rows after.

Deliberately **not** started with `ARIA_ALLOW_DANGER_TOOLS=true`, unlike
`gate_delete.py` — the point of section 2 is that FULL_ACCESS grants the
DANGER ceiling on its own, the same way the flag does. If this gate needed
the flag too, that would mean the mode and the flag were not actually
independent paths to the same ceiling.

    npm run dev                            # no ARIA_ALLOW_DANGER_TOOLS needed
    python scripts/gate_permission_modes.py

Restores whatever mode and trusted folders it found before touching them,
and cleans up its own scratch files, so re-running this does not leave the
machine in FULL_ACCESS or a stray trusted temp folder behind.

**The first version of this file did not call `chat.new` first**, and every
other gate script here does, for exactly the reason that bit this one:
`chat.send` with no `session_id` continues whatever conversation was most
recently active. The test prompts, and the real `confirm.request` dialogs
they produced, landed in Eyaas's actual, in-progress conversation rather
than an isolated one — caught only because the resulting `tool_log` rows
showed `approved_by=user` on calls this script never approved itself.
Fixed by creating its own session up front and deleting it again when
done; `ask()`'s own docstring says why `session_id` is a required
argument now, not an optional one.

**Two more bugs, both found by running this live rather than by reading
it.** First: waiting for "no more confirmations" by polling
`system.health().busy` raced the agent loop's own inter-step latency — a
denied call's *retry*, one step later, could start after this script had
already decided the turn was over and moved the next section's mode into
place, so the retry ran for real under the wrong mode. Fixed by waiting on
the turn's own `turn.complete` event instead, which the sidecar sends
exactly once, only when every step of every retry is truly finished —
authoritative, not guessed at. Second: `task.cancel()` on the message pump
ran *before* this file's own `finally` block, which still had two more RPC
calls left to make (restoring mode and trusted folders) — with nothing
left reading the socket, those calls hung until their own 180s timeout,
which is where every run's trailing "Could not reach the sidecar" actually
came from. The pump now stops only once, at the very end, after cleanup.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import pathlib
import sqlite3
import sys

import websockets
from websockets.exceptions import WebSocketException

# Every other gate here has hit a cp1252 console crash on real model/tool
# output at least once (CLAUDE.md: eval_quality.py, gate_affect.py,
# gate_proactivity.py) — fixed before it happens here instead of after.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRATCH_DIR = pathlib.Path.home() / "Downloads" / "aria-permission-mode-gate"
MANUAL_FILE = SCRATCH_DIR / "manual-write.txt"
FULL_ACCESS_FILE = SCRATCH_DIR / "full-access-delete.txt"
AUTO_FILE = SCRATCH_DIR / "auto-delete.txt"


def _ok(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


async def main() -> int:
    handshake = pathlib.Path("data/.handshake").read_text().strip()
    try:
        token = str(json.loads(handshake)["token"])
    except (json.JSONDecodeError, KeyError, TypeError):
        token = handshake

    async with websockets.connect(
        "ws://127.0.0.1:8765/rpc",
        additional_headers={"Authorization": f"Bearer {token}"},
        max_size=None,
    ) as ws:
        counter = [0]
        pending: dict[int, asyncio.Future[dict]] = {}
        confirmations: asyncio.Queue[dict] = asyncio.Queue()
        completions: asyncio.Queue[dict] = asyncio.Queue()

        async def pump() -> None:
            async for raw in ws:
                message = json.loads(raw)
                if "id" in message and message["id"] in pending:
                    pending.pop(message["id"]).set_result(message)
                elif message.get("method") == "confirm.request":
                    await confirmations.put(message["params"])
                elif message.get("method") == "turn.complete":
                    await completions.put(message["params"])

        task = asyncio.create_task(pump())

        async def call(method: str, params: dict | None = None) -> dict:
            counter[0] += 1
            rid = counter[0]
            fut: asyncio.Future[dict] = asyncio.get_running_loop().create_future()
            pending[rid] = fut
            await ws.send(
                json.dumps(
                    {"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}}
                )
            )
            message = await asyncio.wait_for(fut, timeout=180)
            if "error" in message:
                raise RuntimeError(message["error"])
            return dict(message["result"])

        async def _deny(request: dict) -> None:
            print(
                f"   confirm.request  tool={request['tool']} tier={request['tier']} "
                f"escalated={request.get('escalated')}"
            )
            await call(
                "confirm.respond", {"request_id": request["request_id"], "approved": False}
            )

        async def ask(text: str, session_id: str) -> list[dict]:
            """Send a turn, deny every confirmation it produces — however
            many, across however many agent-loop steps — and return only
            once the *whole* turn is over. Always denies.

            **`session_id` is required, not optional.** The bug this
            guards against already happened once, live: the first version
            of this gate called `chat.send` with no session, which
            continues *whatever conversation was most recently active* —
            and appended every test prompt, and every real confirm.request
            dialog, straight into Eyaas's actual, in-progress conversation
            rather than an isolated one. `gate_memory.py` and every other
            gate here already call `chat.new` first for exactly this
            reason; this one simply hadn't, until it went wrong.

            **Waits on `turn.complete`, not a `busy` poll.** A denied call
            can be retried by the agent loop's *next* step, seconds later;
            only the sidecar itself knows when every one of those steps —
            not just the first — has actually finished. A poll loop has to
            guess how long is long enough and was wrong twice, in opposite
            directions, before this stopped guessing.
            """
            started = await call(
                "chat.send", {"text": text, "session_id": session_id, "spoken": False}
            )
            turn_id = started["turn_id"]
            handled: list[dict] = []
            confirm_task = asyncio.create_task(confirmations.get())
            complete_task = asyncio.create_task(completions.get())
            try:
                while True:
                    done, _pending = await asyncio.wait(
                        {confirm_task, complete_task},
                        timeout=90,
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    if not done:
                        print("   (gave up waiting — the turn never finished)")
                        break
                    if confirm_task in done:
                        request = confirm_task.result()
                        handled.append(request)
                        await _deny(request)
                        confirm_task = asyncio.create_task(confirmations.get())
                        continue
                    completion = complete_task.result()
                    if completion.get("turn_id") == turn_id:
                        break
                    # A completion for a different turn — should not happen
                    # in a single-session gate, but it is not this one.
                    complete_task = asyncio.create_task(completions.get())
            finally:
                confirm_task.cancel()
                complete_task.cancel()
            return handled

        sessions: list[str] = []

        async def new_session() -> str:
            """A fresh session per section, not one shared across all
            three. One session's agent loop can legitimately take several
            steps to settle (a denied call retried with corrected
            arguments); sharing that history across sections risked the
            model responding to the *previous* section's exchange rather
            than starting the next request cleanly. `ask` already waits
            for the specific `turn_id` it sent, so this is not the fix for
            a hang — it is what keeps section 2 and 3's prompts from
            landing in a conversation that still has section 1's denied
            attempt as its most recent turn.
            """
            session_id = (await call("chat.new", {}))["session_id"]
            sessions.append(session_id)
            print(f"   (gate session: {session_id})")
            return session_id

        try:
            failures = 0

            original_mode = (await call("permissions.mode", {}))["mode"]
            original_trusted = (await call("tools.trusted", {}))["paths"]
            print(f"starting mode={original_mode}  trusted={len(original_trusted)} folder(s)")

            SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
            for f in (MANUAL_FILE, FULL_ACCESS_FILE, AUTO_FILE):
                f.write_text("scratch", encoding="utf-8")

            # ── 1. MANUAL still asks inside a trusted folder ──────────────
            print("\n1. MANUAL — a trusted-folder write still asks")
            await call("tools.trusted", {"paths": [str(SCRATCH_DIR)]})
            await call("permissions.mode", {"mode": "manual"})

            requests = await ask(
                f"write the word hi into the file {MANUAL_FILE}", await new_session()
            )
            asked = len(requests) > 0
            print(f"   {_ok(asked)}  MANUAL asked, even though the folder is trusted")
            failures += 0 if asked else 1

            # ── 2. FULL_ACCESS — a DANGER delete, no dialog, no flag ──────
            print("\n2. FULL_ACCESS — a DANGER delete runs with no confirm.request")
            await call("permissions.mode", {"mode": "full_access"})

            requests = await ask(f"delete the file {FULL_ACCESS_FILE}", await new_session())
            no_dialog = len(requests) == 0
            gone = not FULL_ACCESS_FILE.exists()
            print(f"   {_ok(no_dialog)}  no confirm.request at all")
            print(f"   {_ok(gone)}  the file is actually gone")
            failures += 0 if (no_dialog and gone) else 1

            # ── 3. Back to AUTO — the ordinary ask comes back ─────────────
            #
            # **A CONFIRM-tier write, not a DANGER delete — and that is the
            # fix, not a weakening.** The first version repeated section 2's
            # `delete the file ...` under AUTO and expected a dialog, which
            # cannot happen: `delete_file` is DANGER, and `_tool_schemas`
            # only lifts the schema ceiling that far for `allow_danger` or
            # FULL_ACCESS. Dropping back to AUTO takes the tool out of the
            # model's hands entirely, so there is nothing left to confirm,
            # and this gate is deliberately run *without*
            # `ARIA_ALLOW_DANGER_TOOLS` (see the module docstring).
            #
            # It did sometimes "pass": denied its delete, the model reached
            # for whatever T2 tool it could — `move_file`, once
            # `kill_process` — and those asked. So the probe was really
            # measuring "did the model call any confirm-tier tool at all",
            # and passed or failed on that coin flip. CLAUDE.md recorded the
            # failures as probable machine load from repeated live runs. It
            # was not load. It was a probe that could not test what it named.
            print("\n3. AUTO — the ordinary ask comes back")
            await call("permissions.mode", {"mode": "auto"})
            # Trust is what would legitimately silence this, and section 1
            # put the scratch folder into it. Clear it, or correct behaviour
            # ("AUTO did not ask, because you trust that folder") reads as a
            # failure.
            await call("tools.trusted", {"paths": []})

            requests = await ask(
                f"write the word hi into the file {AUTO_FILE}", await new_session()
            )
            asked_again = any(r["tool"] == "write_file" for r in requests)
            print(f"   {_ok(asked_again)}  AUTO asked again, for the write it was given")
            failures += 0 if asked_again else 1
        finally:
            # Restore whatever was configured before this gate touched it.
            # **The pump must still be running for these to get an answer**
            # — that is the whole second bug this file's docstring names.
            # `task.cancel()` happens only once, at the very end of the
            # `async with` block below, after every RPC call this script
            # will ever make, cleanup included.
            await call("permissions.mode", {"mode": original_mode})
            await call("tools.trusted", {"paths": original_trusted})
            # Safe to delete outright: every one of these was created by
            # the gate itself, above, and holds nothing but its own turns.
            for session_id in sessions:
                await call("chat.delete", {"session_id": session_id, "confirm": True})

        print(f"\nrestored mode={original_mode}  trusted={len(original_trusted)} folder(s)")

        print("\n--- tool_log ---")
        conn = sqlite3.connect("data/aria.db")
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT tool, tier, approved, approved_by, ok, error, duration_ms "
            "FROM tool_log WHERE tool IN ('write_file','delete_file') ORDER BY id DESC LIMIT 6"
        ).fetchall()
        for r in rows:
            print(
                f"   {r['tool']} tier={r['tier']} approved={r['approved']} "
                f"by={r['approved_by']} ok={r['ok']} error={r['error']} {r['duration_ms']}ms"
            )
        conn.close()

        for f in (MANUAL_FILE, FULL_ACCESS_FILE, AUTO_FILE):
            f.unlink(missing_ok=True)
        with contextlib.suppress(OSError):
            SCRATCH_DIR.rmdir()

        task.cancel()  # only now — every RPC call above needed it running

        print(f"\n{'GATE PASSED' if failures == 0 else f'GATE FAILED ({failures})'}")
        return 0 if failures == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except (OSError, WebSocketException) as exc:
        print(f"Could not reach the sidecar: {exc}\nStart it with: npm run sidecar")
        raise SystemExit(2) from exc
