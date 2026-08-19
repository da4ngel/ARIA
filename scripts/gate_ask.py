"""Does she ask well, and — more importantly — does she stop asking?

    python scripts/gate_ask.py

Section 5 is the one that decides whether this feature is liveable. Everything
else proves the mechanism works; that one proves it does not fire on an
ordinary question. §9's warning about proactive messages applies word for word:
over-triggering is the fastest route to a feature being switched off.

**It answers rather than stalling.** `gate_research.py` and `gate_modes.py`
both hung for a full timeout because they could not respond to something the
sidecar was waiting on. A question is exactly that, so this replies to
`question.ask` — and to `confirm.request`, for any tool she reaches for after.

**One session per section**, because `chat.send` with no session continues
whatever conversation was most recently active, and this project has already
put real confirmation dialogs into Eyaas's live chat by forgetting that.
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

URL = "ws://127.0.0.1:8765/rpc"
#: Generous, and it needs to be. A turn worth asking about is a substantive
#: one, so QUALITY bias routes it to the SMART class — measured live, that
#: was `gpt-5`, whose TTFT this project records at ~7s and which bills its
#: reasoning against the same budget. The question itself is answered in
#: milliseconds; what takes minutes is the reply after it.
TURN_TIMEOUT_S = 420.0

#: Read-only, and named rather than derived from the tier table — a gate that
#: approves whatever the code under test calls safe is agreeing with itself.
_AUTO_APPROVE = {"research", "browser_read", "read_file", "list_folder", "search_files", "find"}


class Client:
    """One reader task, everything else off a queue.

    `asyncio.wait_for(ws.recv(), ...)` in a loop cancels the pending `recv()`
    on every timeout and can lose the frame that just arrived — it cost
    `gate_modes.py` three runs of phantom 240s timeouts. Cancelling a
    `Queue.get()` is safe in a way cancelling `recv()` is not.
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
            print(f"    !! reader died: {type(exc).__name__}: {exc}")
            raise

    async def close(self) -> None:
        self._reader.cancel()

    async def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        mid = uuid.uuid4().hex[:8]
        future: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
        self._replies[mid] = future
        await self._ws.send(
            json.dumps({"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}})
        )
        message = await asyncio.wait_for(future, timeout=60)
        if message.get("error"):
            raise RuntimeError(f"{method}: {message['error']}")
        return message.get("result")

    async def ask(self, session_id: str, text: str, *, pick: int = 0) -> dict[str, Any]:
        """Send, answer anything she waits on, and return the completed turn.

        `pick` is which option to choose — deliberately not always 0, so a
        reply that merely echoes the first option cannot pass for one that read
        the answer.
        """
        self.events.clear()
        while not self._inbox.empty():
            self._inbox.get_nowait()

        started = await self.call("chat.send", {"session_id": session_id, "text": text})
        turn_id = started["turn_id"]
        self.questions: list[dict[str, Any]] = []
        self.chosen: list[str] = []

        deadline = time.perf_counter() + TURN_TIMEOUT_S
        while time.perf_counter() < deadline:
            try:
                async with asyncio.timeout(5):
                    message = await self._inbox.get()
            except TimeoutError:
                continue

            method = message["method"]
            params = message["params"]

            if method == "question.ask":
                self.questions.append(params)
                answers = []
                for question in params["questions"]:
                    options = question["options"]
                    option = options[min(pick, len(options) - 2)]  # never "Other"
                    self.chosen.append(option["label"])
                    answers.append(
                        {"question": question["question"], "chosen": [option["label"]], "other": ""}
                    )
                    print(f"    asked: {question['question'][:60]}  -> {option['label']}")
                await self.call(
                    "question.answer", {"request_id": params["request_id"], "answers": answers}
                )
                continue

            if method == "confirm.request":
                tool = params.get("tool", "?")
                await self.call(
                    "confirm.respond",
                    {"request_id": params["request_id"], "approved": tool in _AUTO_APPROVE},
                )
                continue

            if method == "turn.complete" and params.get("turn_id") == turn_id:
                return dict(params)

        raise TimeoutError(f"no turn.complete for {turn_id} within {TURN_TIMEOUT_S}s")


async def section(client: Client, title: str, text: str, *, pick: int = 0) -> dict[str, Any]:
    session_id = (await client.call("chat.new"))["session_id"]
    print(f"\n── {title}")
    result = await client.ask(session_id, text, pick=pick)
    reply = (result.get("full_text") or "").strip()
    print(f"    reply: {reply[:200]}")
    return {
        "questions": list(client.questions),
        "chosen": list(client.chosen),
        "reply": reply,
    }


async def main() -> int:
    token = pathlib.Path("data/.handshake").read_text(encoding="utf-8").strip()
    try:
        token = str(json.loads(token)["token"])
    except (json.JSONDecodeError, KeyError, TypeError):
        pass

    try:
        connection = await websockets.connect(
            URL, additional_headers={"Authorization": f"Bearer {token}"}
        )
    except (OSError, websockets.exceptions.WebSocketException) as exc:
        print(f"Could not reach the sidecar at {URL} ({exc}).")
        print("Start it with `npm run sidecar`, or run `npm run dev`.")
        return 2

    failures: list[str] = []
    async with connection as ws:
        client = Client(ws)
        try:
            # 1. A decision she genuinely cannot make for him.
            blocked = await section(
                client,
                "a real fork in the road",
                "I want to add a database to my Python side project. Ask me what I "
                "need before you recommend one.",
                pick=1,
            )
            if not blocked["questions"]:
                failures.append("she never asked, on a turn that explicitly invited it")
            else:
                asked = blocked["questions"][0]["questions"]
                print(f"    PASS  one question set, {len(asked)} question(s)")
                for question in asked:
                    labels = [o["label"] for o in question["options"]]
                    if labels[-1] != "Other":
                        failures.append(f"no escape hatch on {question['question'][:40]!r}")
                    if not 2 <= len(labels) <= 5:
                        failures.append(f"{len(labels)} options on {question['question'][:40]!r}")

            # 2. The answer has to actually reach the model.
            if blocked["chosen"]:
                first = blocked["chosen"][0].lower()
                if first[:12] in blocked["reply"].lower():
                    print(f"    PASS  the reply reflects the chosen option ({first[:24]!r})")
                else:
                    print(f"    OBSERVED  chose {first!r}; read the reply above and judge")

            # 3. **The one that decides whether this is liveable.**
            plain = await section(
                client, "an ordinary question", "What is the capital of Australia?"
            )
            if plain["questions"]:
                failures.append("she asked a multiple-choice question about Canberra")
            else:
                print("    PASS  no question — she just answered")

            # 4. Only one question set per turn, whatever she tries.
            many = await section(
                client,
                "one set per turn",
                "Plan a birthday party for me. Ask me about the venue, then the "
                "food, then the music, then the budget — one at a time.",
            )
            if len(many["questions"]) > 1:
                failures.append(f"{len(many['questions'])} question sets in one turn")
            else:
                print(f"    PASS  {len(many['questions'])} question set for the whole turn")
        finally:
            await client.close()

    print("\n" + "=" * 66)
    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}")
        return 1
    print("GATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
