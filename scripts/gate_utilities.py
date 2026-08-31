"""Clipboard history, reminders, usage and explain-last-action — live.

    npm run dev            # or: npm run sidecar
    python scripts/gate_utilities.py

Four features that each turn something the sidecar already records into
something visible. What can only be checked live is the part where a *real*
model decides to reach for the new tools, and the part where a background loop
actually fires on its own clock.

**Section 3 is the one worth having.** `ProactivityScheduler` would drop a
reminder set by somebody sitting at the machine — its focus check suppresses
delivery for 20 minutes after any keypress, which is exactly the window "remind
me in one minute" lands in. This gate is *driving* the sidecar, so the machine
is unambiguously in use, and a reminder arriving anyway is the direct evidence
that `ReminderScheduler`'s separate loop was the right call.

Each section uses its own session. `chat.send` with no session continues
whatever conversation was most recently active, and this project has already
put real confirmation dialogs into Eyaas's live chat once by forgetting that.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import sys
import time
import uuid
from typing import Any

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import websockets
import websockets.exceptions

URL = "ws://127.0.0.1:8765/rpc"
RULE = "=" * 72
TURN_TIMEOUT_S = 180.0

#: Read-only, and nothing here should reach a confirmation at all. Anything
#: else is denied rather than approved: a gate that waves through whatever it
#: is shown is not testing the permission engine, it is bypassing it.
_AUTO_APPROVE = {"read_clipboard", "read_clipboard_history", "list_reminders"}

#: A string the credential filter must refuse. A real AWS key id shape, which
#: is a published format and not a guess.
SECRET_LOOKING = "AKIAIOSFODNN7EXAMPLE"


class Client:
    """One reader task, everything else off a queue — `gate_modes.py`'s shape.

    `asyncio.wait_for(ws.recv())` in a loop cancels the pending `recv()` on
    every timeout and loses any frame that arrived during the cancellation.
    Cancelling a `Queue.get()` is safe in a way cancelling `recv()` is not.
    """

    def __init__(self, ws: Any) -> None:
        self._ws = ws
        self.events: list[dict[str, Any]] = []
        self._replies: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._inbox: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._reader = asyncio.create_task(self._read())

    async def _read(self) -> None:
        try:
            async for raw in self._ws:
                message = json.loads(raw)
                reply_id = message.get("id")
                if reply_id is not None and reply_id in self._replies:
                    future = self._replies.pop(reply_id)
                    if not future.done():
                        future.set_result(message)
                elif message.get("method"):
                    self.events.append(message)
                    await self._inbox.put(message)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            # Dying silently is what makes a hang look like a product bug.
            print(f"    !! reader died: {type(exc).__name__}: {exc}")
            raise

    async def close(self) -> None:
        self._reader.cancel()

    async def next_event(self, seconds: float) -> dict[str, Any] | None:
        try:
            async with asyncio.timeout(seconds):
                return await self._inbox.get()
        except TimeoutError:
            return None

    async def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        mid = uuid.uuid4().hex[:8]
        future: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
        self._replies[mid] = future
        await self._ws.send(
            json.dumps({"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}})
        )
        message = await asyncio.wait_for(future, timeout=90)
        if message.get("error"):
            raise RuntimeError(f"{method}: {message['error']}")
        return message.get("result")

    async def ask(self, session_id: str, text: str) -> dict[str, Any]:
        self.events.clear()
        while not self._inbox.empty():
            self._inbox.get_nowait()
        started = await self.call("chat.send", {"session_id": session_id, "text": text})
        turn_id = started["turn_id"]
        deadline = time.perf_counter() + TURN_TIMEOUT_S
        while time.perf_counter() < deadline:
            message = await self.next_event(seconds=5)
            if message is None:
                continue
            # A gate that cannot answer a confirmation does not fail, it hangs.
            if message["method"] == "confirm.request":
                request = message["params"]
                tool = request.get("tool", "?")
                approved = tool in _AUTO_APPROVE
                print(f"    confirm: {tool} -> {'approved' if approved else 'DENIED'}")
                await self.call(
                    "confirm.respond",
                    {"request_id": request["request_id"], "approved": approved},
                )
                continue
            if (
                message["method"] == "turn.complete"
                and message["params"].get("turn_id") == turn_id
            ):
                return dict(message["params"])
        raise TimeoutError(f"no turn.complete for {turn_id} within {TURN_TIMEOUT_S}s")

    def tools_used(self) -> list[str]:
        return [
            str(e["params"].get("tool"))
            for e in self.events
            if e["method"] == "tool.call"
        ]

    async def session(self) -> str:
        result = await self.call("chat.new", {})
        return str(result["session_id"])


def _copy(text: str) -> bool:
    """Put something on the real clipboard, so the watcher sees a real change."""
    try:
        import win32clipboard
        import win32con

        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        finally:
            win32clipboard.CloseClipboard()
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"    (clipboard unavailable: {exc})")
        return False


async def main() -> int:
    failures: list[str] = []
    observed: list[str] = []

    try:
        token = pathlib.Path("data/.handshake").read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        print("No data/.handshake — start the sidecar first (npm run sidecar).")
        return 1

    try:
        connection = await websockets.connect(
            URL, additional_headers={"Authorization": f"Bearer {token}"}
        )
    except (OSError, websockets.exceptions.WebSocketException) as exc:
        print(f"Could not reach the sidecar at {URL}: {exc}")
        print("Start it with `npm run sidecar` or `npm run dev`.")
        return 1

    client = Client(connection)
    try:
        # ── 1. clipboard history ─────────────────────────────────────
        print(RULE)
        print("1. WHAT WAS COPIED IS RECORDED, AND DEDUPED")
        print(RULE)
        marker = uuid.uuid4().hex[:8]
        wanted = [f"gate-alpha-{marker}", f"gate-beta-{marker}"]
        if not _copy(wanted[0]):
            print("    SKIPPED  no clipboard on this machine")
        else:
            await asyncio.sleep(2.0)
            _copy(wanted[1])
            await asyncio.sleep(2.0)
            # The same thing again — it must move, not duplicate.
            _copy(wanted[0])
            await asyncio.sleep(2.0)

            history = await client.call("clipboard.history", {"limit": 50})
            contents = [e["content"] for e in history["entries"]]
            print(f"    watching={history['watching']}  entries={len(contents)}")
            print(f"    newest: {contents[:3]}")
            if not history["watching"]:
                failures.append("1. the clipboard watcher is not running")
            elif contents[:1] != [wanted[0]]:
                failures.append(f"1. expected {wanted[0]!r} newest, got {contents[:1]}")
            elif contents.count(wanted[0]) != 1:
                failures.append("1. the same copy was stored twice")
            else:
                print("    PASS  recorded newest-first, and deduped on re-copy")

            # ── 2. the filter ────────────────────────────────────────
            print()
            print(RULE)
            print("2. A CREDENTIAL-SHAPED COPY IS NOT STORED")
            print(RULE)
            before = history.get("skipped_secrets", 0)
            _copy(SECRET_LOOKING)
            await asyncio.sleep(2.5)
            after = await client.call("clipboard.history", {"limit": 50})
            stored = [e["content"] for e in after["entries"]]
            print(f"    skipped_secrets: {before} -> {after.get('skipped_secrets')}")
            if SECRET_LOOKING in stored:
                failures.append("2. a credential-shaped string was stored")
            elif after.get("skipped_secrets", 0) <= before:
                failures.append("2. it was not stored, but nothing counted it as skipped")
            else:
                print("    PASS  refused, and counted")
            # Leave nothing behind on the real clipboard.
            _copy("")

        # ── 3. a reminder fires while the machine is in use ──────────
        print()
        print(RULE)
        print("3. A REMINDER FIRES — WHILE THE MACHINE IS IN USE")
        print(RULE)
        print("    This gate is driving the sidecar, so `is_actively_working()`")
        print("    is true throughout. ProactivityScheduler would drop this.")
        session = await client.session()
        reply = await client.ask(
            session, "remind me in 1 minute to check the oven"
        )
        print(f"    tools: {client.tools_used()}")
        print(f"    reply: {(reply.get('full_text') or '')[:120]}")

        pending = await client.call("reminders.list", {})
        mine = [r for r in pending["reminders"] if "oven" in r["text"].lower()]
        if "set_reminder" not in client.tools_used():
            failures.append("3. she did not reach for set_reminder")
        elif not mine:
            failures.append("3. set_reminder ran but nothing is pending")
        else:
            print(f"    set for {mine[0]['due_at']} — waiting up to 120s…")
            deadline = time.perf_counter() + 120
            fired = False
            while time.perf_counter() < deadline:
                event = await client.next_event(seconds=10)
                if event is None:
                    continue
                if event["method"] == "proactive" and "oven" in str(
                    event["params"].get("text", "")
                ).lower():
                    print(f"    delivered: {event['params']['text']!r}")
                    fired = True
                    break
            if fired:
                print("    PASS  it fired, unsuppressed, on its own loop")
            else:
                failures.append("3. the reminder never arrived within 120s")
            # Whatever happened, do not leave a reminder on his machine.
            for reminder in mine:
                await client.call("reminders.cancel", {"id": reminder["id"]})

        # ── 4. usage ─────────────────────────────────────────────────
        print()
        print(RULE)
        print("4. TOKENS ARE RECORDED FOR A TURN THAT JUST RAN")
        print(RULE)
        usage = await client.call("usage.today", {})
        print(
            f"    turns={usage['turns']} local={usage['local_turns']} "
            f"cloud={usage['cloud_turns']}"
        )
        print(
            f"    tokens: {usage['prompt_tokens']} in / {usage['completion_tokens']} out"
            f"  uncounted={usage['uncounted']}"
        )
        print(
            f"    estimated ${usage['estimated_usd']} "
            f"(rates {usage['prices_as_of']}, {usage['unpriced_turns']} turns unpriced)"
        )
        if usage["turns"] == 0:
            failures.append("4. no turns recorded at all")
        elif usage["prompt_tokens"] == 0:
            # **This check used to also require `uncounted == 0`, and that made
            # it useless.** Every turn was arriving uncounted — the token
            # threading was broken for all three providers — and the gate
            # reported PASS because `uncounted` was non-zero. A gate that
            # accepts "nobody counted anything" as evidence of counting is
            # agreeing with itself.
            failures.append(
                f"4. zero tokens across {usage['turns']} turns "
                f"({usage['uncounted']} uncounted) — the counts are not reaching the log"
            )
        else:
            print("    PASS  token counts reached the log")
            if usage["uncounted"]:
                observed.append(
                    f"4. {usage['uncounted']} turn(s) reported no usage — expected "
                    f"only for providers that do not send it (OpenRouter)"
                )
        if usage["unpriced_turns"] > 0:
            observed.append(
                f"4. {usage['unpriced_turns']} turns have no rate — fill in "
                f"providers/pricing.py to make the total real"
            )

        # ── 5. explain ───────────────────────────────────────────────
        print()
        print(RULE)
        print("5. SHE CAN SAY WHAT SHE ACTUALLY JUST DID")
        print(RULE)
        session = await client.session()
        await client.ask(session, "what time is it?")
        reply = await client.ask(session, "why did you use that model? explain your last action")
        text = (reply.get("full_text") or "").strip()
        print(f"    tools: {client.tools_used()}")
        print(f"    reply: {text[:300]}")
        if "explain_last_action" not in client.tools_used():
            failures.append("5. she did not reach for explain_last_action")
        else:
            recent = await client.call("usage.recent", {"limit": 3})
            models = {str(t["model"]) for t in recent["turns"]}
            if any(m and m in text for m in models):
                print("    PASS  she named the model that actually answered")
            else:
                observed.append("5. the tool ran, but the reply did not name the model")
                print("    OBSERVED  tool ran; read the reply above and judge")
    finally:
        await client.close()
        await connection.close()

    print()
    print(RULE)
    for line in observed:
        print(f"OBSERVED  {line}")
    if failures:
        for line in failures:
            print(f"FAIL  {line}")
        print("GATE FAILED")
        return 1
    print("GATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
