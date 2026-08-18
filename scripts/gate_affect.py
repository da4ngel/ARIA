"""§9 Phase 8's affect-model acceptance gate.

    the same question at a 2am-shaped state and a 2pm-shaped state
      -> render() differs textually (deterministic, no model call needed)
    repeated updates with no deltas -> drifts back toward baseline
    a repeated-failure state -> concern rises
    high playfulness / high concern -> speech_speed nudges up / down

`test_affect.py` proves the formula against fixed inputs and a fixed clock —
that is the whole of `update()`/`render()`/`speech_speed()`, since all three
are pure. This gate does two things a unit test cannot: run against the
*actual* database read/write path (`load`/`save`/`refresh`), and put the
live model in front of two real, different affect states to see whether the
same question actually reads differently — which is a property of the
model, not of the formula, and is reported OBSERVED rather than scored, the
exact treatment `gate_memory.py` already gives its own unprovable line.

    npm run dev                        # or: npm run sidecar
    python scripts/gate_affect.py

It restores whatever `affect_state` row it found before touching it, so
re-running this does not leave a manufactured mood in the real database.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import sqlite3
import sys
from datetime import UTC, datetime

import websockets
from websockets.exceptions import WebSocketException

# The live section prints real model replies verbatim, and those routinely
# carry an em-dash or curly quote. `eval_quality.py` already hit this once
# (CLAUDE.md: "died two thirds of the way through... printing a reply
# containing an em-dash to a cp1252 console") — fixed here before it happens
# rather than discovered by a crash mid-gate.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from sidecar.persona import affect as affect_module
from sidecar.persona.affect import BASELINE, AffectState

DB_PATH = pathlib.Path("data/aria.db")

# A 2am-shaped state: tired, guarded, not playful, a little worried — vs. a
# 2pm-shaped one: bright, warm, playful, unconcerned. Chosen to sit well past
# `render()`'s own banding margin on every float, so the difference is not a
# coin flip near a threshold.
LOW_STATE = AffectState(warmth=0.25, energy=0.15, playfulness=0.15, concern=0.75)
HIGH_STATE = AffectState(warmth=0.9, energy=0.9, playfulness=0.9, concern=0.05)

QUESTION = "how's it going?"


def _ok(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def _mechanism_checks() -> int:
    """Section 1: pure functions, no sidecar needed. Mirrors `test_affect.py`
    but as a standalone, human-readable pass/fail narrative."""
    failures = 0
    print("1. Mechanism (no sidecar, no model call)")

    two_am = datetime(2026, 8, 14, 2, 0, tzinfo=UTC)
    two_pm = datetime(2026, 8, 14, 14, 0, tzinfo=UTC)
    low_render = affect_module.render(LOW_STATE, two_am)
    high_render = affect_module.render(HIGH_STATE, two_pm)
    print(f"   render(low, 2am)  = {low_render!r}")
    print(f"   render(high, 2pm) = {high_render!r}")
    differs = low_render != high_render and low_render is not None and high_render is not None
    print(f"   {_ok(differs)}  render() differs textually between the two states")
    failures += 0 if differs else 1

    state = AffectState(warmth=0.05, energy=0.05, playfulness=0.05, concern=0.95)
    for _ in range(30):
        state = affect_module.update(
            state,
            now=two_pm,
            hours_since_last_interaction=0.0,
            session_duration_hours=0.0,
            is_casual_turn=False,
            repeated_failures=False,
        )
    close = (
        abs(state.warmth - BASELINE.warmth) < 0.05
        and abs(state.concern - BASELINE.concern) < 0.05
    )
    print(
        f"   after 30 neutral updates: warmth={state.warmth:.3f} "
        f"concern={state.concern:.3f}  (baseline warmth={BASELINE.warmth} "
        f"concern={BASELINE.concern})"
    )
    print(f"   {_ok(close)}  drifted back toward baseline with no deltas applied")
    failures += 0 if close else 1

    quiet = affect_module.update(
        BASELINE,
        now=two_pm,
        hours_since_last_interaction=0.0,
        session_duration_hours=0.0,
        is_casual_turn=False,
        repeated_failures=False,
    )
    failing = affect_module.update(
        BASELINE,
        now=two_pm,
        hours_since_last_interaction=0.0,
        session_duration_hours=0.0,
        is_casual_turn=False,
        repeated_failures=True,
    )
    raised = failing.concern > quiet.concern
    print(
        f"   concern with no failures={quiet.concern:.3f}  "
        f"with repeated failures={failing.concern:.3f}"
    )
    print(f"   {_ok(raised)}  a repeated-failure state raises concern")
    failures += 0 if raised else 1

    playful_speed = affect_module.speech_speed(
        BASELINE.model_copy(update={"playfulness": 0.9})
    )
    concerned_speed = affect_module.speech_speed(BASELINE.model_copy(update={"concern": 0.9}))
    speed_moves = playful_speed > 1.0 and concerned_speed < 1.0
    print(
        f"   speech_speed: baseline=1.0  high playfulness={playful_speed:.3f}  "
        f"high concern={concerned_speed:.3f}"
    )
    print(f"   {_ok(speed_moves)}  speed nudges up for playfulness, down for concern")
    failures += 0 if speed_moves else 1

    return failures


def _seed_affect(state: AffectState) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            conn.execute(
                "UPDATE affect_state SET warmth=?, energy=?, playfulness=?, concern=?, "
                "updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE id=1",
                (state.warmth, state.energy, state.playfulness, state.concern),
            )
    finally:
        conn.close()


def _read_affect_row() -> sqlite3.Row | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(
            "SELECT warmth, energy, playfulness, concern, updated_at FROM affect_state WHERE id=1"
        ).fetchone()
    finally:
        conn.close()


def _restore_affect(row: sqlite3.Row | None) -> None:
    if row is None:
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            conn.execute(
                "UPDATE affect_state SET warmth=?, energy=?, playfulness=?, concern=?, "
                "updated_at=? WHERE id=1",
                (
                    row["warmth"],
                    row["energy"],
                    row["playfulness"],
                    row["concern"],
                    row["updated_at"],
                ),
            )
    finally:
        conn.close()


async def main() -> int:
    failures = _mechanism_checks()

    if not DB_PATH.exists():
        print(
            f"\n2. SKIP  {DB_PATH} does not exist — start the sidecar once to "
            "create it, then re-run for the live comparison."
        )
        print(f"\n{'GATE PASSED' if failures == 0 else f'GATE FAILED ({failures})'}")
        return 0 if failures == 0 else 1

    handshake = pathlib.Path("data/.handshake").read_text().strip()
    try:
        token = str(json.loads(handshake)["token"])
    except (json.JSONDecodeError, KeyError, TypeError):
        token = handshake

    original_row = _read_affect_row()

    async with websockets.connect(
        "ws://127.0.0.1:8765/rpc",
        additional_headers={"Authorization": f"Bearer {token}"},
        max_size=None,
    ) as ws:
        counter = [0]
        pending: dict[int, asyncio.Future[dict]] = {}
        completions: asyncio.Queue[dict] = asyncio.Queue()
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
            print("\n2. The same question against two real, different affect states")
            print("   (OBSERVED — a property of the model, not scored)")

            _seed_affect(LOW_STATE)
            session = await call("chat.new", {})
            created_sessions.append(session["session_id"])
            low_reply = await say(QUESTION)
            print(f"   low state  -> {low_reply.strip()[:180]}")

            _seed_affect(HIGH_STATE)
            session = await call("chat.new", {})
            created_sessions.append(session["session_id"])
            high_reply = await say(QUESTION)
            print(f"   high state -> {high_reply.strip()[:180]}")

            same = low_reply.strip() == high_reply.strip()
            print(
                f"   OBSERVED  replies {'are identical' if same else 'differ'} "
                "(read them — a formula difference is not the same claim as a "
                "reader noticing a tone difference)"
            )

            print("\n3. Cleanup")
            for session_id in created_sessions:
                await call("chat.delete", {"session_id": session_id, "confirm": True})
            _restore_affect(original_row)
            print(f"   restored affect_state, removed {len(created_sessions)} sessions")

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
