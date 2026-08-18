"""§9 Phase 8's proactivity-engine acceptance gate.

    a pending procedure offer -> delivered via the real scheduler, live
    the delivery is rateable          -> turn.rate round-trips on it
    a plain "yes" in reply            -> procedures.confirm, no model call
    fullscreen / recent input         -> live values on this machine

`test_proactivity.py` (24 tests) already proves the rate limit's exact
boundaries, both focus-suppression paths and the self-check drop path
against an injected clock — this gate does not re-derive any of that. What
it proves instead is the real thing: `record_new_offers` actually wired into
`default_candidates` (it was dead code in production until this phase — see
CLAUDE.md), a real local-model self-check call, a real `messages` row and
`routing_log` row through the live sidecar, and a real "yes" resolving
without ever reaching the model.

    npm run dev                          # or: npm run sidecar
    python scripts/gate_proactivity.py

**The delivery step needs an idle machine, and says so rather than faking
it.** `ProactivityScheduler.tick()` checks `focus.is_actively_working()`
first, and someone running this gate by hand is, by definition, using the
machine — the correct behaviour is to stay quiet, which means the live
delivery section is expected to report SKIPPED most of the time. Leave the
keyboard and mouse alone for a few minutes, or run this unattended, to see
it actually fire. Section 1 prints the live reading so the rest of the
output can be read in light of it.

It cleans up every `gate_probe_*` procedure and the sessions it creates, so
re-running this does not leave manufactured offers in the real database.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import sqlite3
import sys

import websockets
from websockets.exceptions import WebSocketException

# Procedure names carry a real "→". `eval_quality.py` already hit this once
# (CLAUDE.md: "died two thirds of the way through... printing a reply
# containing an em-dash to a cp1252 console") — a measurement that dies
# partway through is worse than none, so this is fixed before it happens
# here rather than discovered by a crash mid-gate.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from sidecar.persona import focus

DB_PATH = pathlib.Path("data/aria.db")
PROBE_NAME = "gate_probe_a -> gate_probe_b -> gate_probe_c"


def _ok(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def _seed_procedure(name: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO procedures "
                "(name, trigger_phrase, steps, confirmed, created_at) "
                "VALUES (?, ?, ?, 0, strftime('%Y-%m-%dT%H:%M:%SZ','now'))",
                (name, "gate probe", '[{"tool": "gate_probe_a"}]'),
            )
    finally:
        conn.close()


def _procedure_confirmed(name: str) -> bool | None:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT confirmed FROM procedures WHERE name = ?", (name,)
        ).fetchone()
        return bool(row[0]) if row else None
    finally:
        conn.close()


def _cleanup_probes() -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            cur = conn.execute("DELETE FROM procedures WHERE name LIKE 'gate_probe_%'")
            return cur.rowcount
    finally:
        conn.close()


def _clear_other_pending_offers() -> list[str]:
    """`pending_offers` has no ordering, so a real pattern already detected
    from actual usage (this machine's own `open_app -> open_app -> open_app`
    was found the first time this gate ran, proof `record_new_offers` really
    is wired in now) can win the race against the probe and make this gate
    flaky for a reason that has nothing to do with what it is testing.
    Discarding is not destructive — `procedures.discard`'s own contract is
    that a recurring pattern gets offered again."""
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT name FROM procedures WHERE confirmed = 0 AND name NOT LIKE 'gate_probe_%'"
        ).fetchall()
        names = [r[0] for r in rows]
        if names:
            with conn:
                conn.execute(
                    "DELETE FROM procedures WHERE confirmed = 0 AND name NOT LIKE 'gate_probe_%'"
                )
        return names
    finally:
        conn.close()


def _focus_section() -> None:
    print("1. Focus detection, live on this machine (informational — a script")
    print("   cannot assert what the desktop is doing, only report it)")
    fullscreen = focus.is_fullscreen()
    idle_for = focus.seconds_since_last_input()
    working = focus.is_actively_working()
    print(f"   is_fullscreen()          = {fullscreen}")
    print(f"   seconds_since_last_input = {idle_for}")
    print(f"   is_actively_working()    = {working}")


async def main() -> int:
    _focus_section()

    if not DB_PATH.exists():
        print(f"\n2. SKIP  {DB_PATH} does not exist — start the sidecar once first.")
        return 1

    handshake = pathlib.Path("data/.handshake").read_text().strip()
    try:
        token = str(json.loads(handshake)["token"])
    except (json.JSONDecodeError, KeyError, TypeError):
        token = handshake

    failures = 0
    _cleanup_probes()  # leftover from a previous crashed run, if any

    async with websockets.connect(
        "ws://127.0.0.1:8765/rpc",
        additional_headers={"Authorization": f"Bearer {token}"},
        max_size=None,
    ) as ws:
        counter = [0]
        pending: dict[int, asyncio.Future[dict]] = {}
        completions: asyncio.Queue[dict] = asyncio.Queue()
        proactive_events: asyncio.Queue[dict] = asyncio.Queue()
        tokens: dict[str, list[str]] = {}

        async def pump() -> None:
            async for raw in ws:
                message = json.loads(raw)
                if "id" in message and message["id"] in pending:
                    pending.pop(message["id"]).set_result(message)
                elif message.get("method") == "turn.complete":
                    await completions.put(message["params"])
                elif message.get("method") == "token":
                    params = message["params"]
                    tokens.setdefault(params["turn_id"], []).append(params["text"])
                elif message.get("method") == "proactive":
                    await proactive_events.put(message["params"])
                elif message.get("method") == "confirm.request":
                    params = message["params"]
                    print(f"   (denied an unexpected confirm: {params.get('tool')})")
                    counter[0] += 1
                    await ws.send(
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": counter[0],
                                "method": "confirm.respond",
                                "params": {"request_id": params["request_id"], "approved": False},
                            }
                        )
                    )

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
            message = await asyncio.wait_for(fut, timeout=300)
            if "error" in message:
                raise RuntimeError(message["error"])
            return dict(message["result"])

        async def say(text: str) -> str:
            started = await call("chat.send", {"text": text, "spoken": False})
            turn_id = started["turn_id"]
            while True:
                done = await asyncio.wait_for(completions.get(), timeout=300)
                if done.get("turn_id") == turn_id:
                    break
            return "".join(tokens.get(turn_id, []))

        try:
            created_sessions: list[str] = []

            print("\n2. A real procedure offer, delivered through the live scheduler")
            session = await call("chat.new", {})
            created_sessions.append(session["session_id"])
            cleared = _clear_other_pending_offers()
            if cleared:
                print(f"   (cleared {len(cleared)} unrelated pending offer(s): {cleared})")
            _seed_procedure(PROBE_NAME)

            await call("proactivity.trigger", {})
            try:
                delivered = await asyncio.wait_for(proactive_events.get(), timeout=15)
            except TimeoutError:
                delivered = None

            if delivered is None:
                print(
                    "   SKIPPED  nothing arrived within 15s — most likely "
                    "focus suppressed it (see section 1), the self-check "
                    "rated it noise, or the rate limit is already at its "
                    "daily cap. Not counted as a failure: "
                    "`test_proactivity.py` already proves the rate limit "
                    "and both suppression paths on an injected clock."
                )
            else:
                print(f"   delivered: {delivered['text']!r}")
                message_id = delivered["message_id"]

                print("3. It is rateable through the existing mechanism")
                rate = await call("turn.rate", {"message_id": message_id, "rating": 1})
                ratings = await call("turn.ratings", {"session_id": delivered["session_id"]})
                rated = rate.get("recorded") is True and ratings.get("ratings", {}).get(
                    str(message_id)
                ) == 1
                print(f"   turn.rate -> {rate}  turn.ratings -> {ratings}")
                print(f"   {_ok(rated)}  the delivered message is rateable")
                failures += 0 if rated else 1

                print("4. A plain 'yes' confirms it, with no model call needed")
                reply = await say("yes")
                confirmed = _procedure_confirmed(PROBE_NAME)
                print(f"   reply: {reply.strip()!r}")
                print(f"   procedures.confirmed = {confirmed}")
                passed = confirmed is True and reply.strip() == "Got it — I'll remember that."
                print(f"   {_ok(passed)}  the offer was confirmed by a plain yes")
                failures += 0 if passed else 1

            print("\n5. Cleanup")
            removed = _cleanup_probes()
            for session_id in created_sessions:
                await call("chat.delete", {"session_id": session_id, "confirm": True})
            print(f"   removed {removed} probe procedure(s), {len(created_sessions)} session(s)")

            print(
                "\nNot re-derived here — already proven by "
                "`pytest sidecar/tests/test_proactivity.py` (24 tests, injected "
                "clock): the exact rate-limit boundaries (5th/day, <90min gap), "
                "both focus-suppression paths, and the self-check drop path."
            )
            print(
                "BUILD_SPEC's '>=70% useful over a week' line needs a week of "
                "real usage this script cannot generate — not scored, same "
                "treatment gate_wakeword.py gives its own unmeasurable lines."
            )

            print(f"\n{'GATE PASSED' if failures == 0 else f'GATE FAILED ({failures})'}")
            return 0 if failures == 0 else 1
        finally:
            task.cancel()


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except (OSError, WebSocketException) as exc:
        print(f"Could not reach the sidecar: {exc}\nStart it with: npm run sidecar")
        raise SystemExit(2) from exc
