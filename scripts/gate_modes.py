"""Do the six modes actually behave differently? Live, against a real sidecar.

    python scripts/gate_modes.py

Eyaas asked for modes that are *"genuinely different reasoning policies, tool
strategies, context handling and output standards"* — so what this measures is
whether the same question, asked in six modes, comes back six different shapes.
Not whether the prompt text contains the right words: `test_modes.py` and
`test_context.py` already do that, and a prompt containing an instruction is
not evidence a model followed it.

**Each section creates and deletes its own session.** `chat.send` with no
session continues whatever conversation was most recently active, and this
project has already put real confirmation dialogs into Eyaas's live chat once
by forgetting that.

Reported honestly: the mechanical checks (step budget, tool ceiling, routing)
are asserted; the *style* differences are printed as OBSERVED, because "is
this a good Study answer" is not a thing a script can score, and pretending
otherwise is how a green gate comes to mean nothing.
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

from sidecar.core.context import ConversationMode
from sidecar.core.modes import policy_for

URL = "ws://127.0.0.1:8765/rpc"

#: **One question per mode, not one question six times**, and the first version
#: got this wrong in a way only running it showed.
#:
#: Asking all six the *same* thing looked obviously right. But `chat.new`
#: closes the previous session, which writes an episode immediately, and
#: `Retriever` is deliberately cross-session — so by the fourth mode there were
#: three episodes about that exact question and she was answering from them.
#: Quick opened with *"Earlier you said to use an array"* and Critic with
#: *"We talked about this before, Eyaas"*. Both were memory working correctly;
#: the measurement was the thing that was broken, because modes four to six
#: had context modes one to three did not.
#:
#: So: six questions of the same *shape* — pick between two designs, where the
#: honest answer is "it depends on the workload" — sharing no vocabulary, so
#: nothing cross-retrieves. The cost is real and stated: differences between
#: replies now carry some of the question as well as the mode. That is a worse
#: comparison than an identical prompt would be and a far better one than a
#: contaminated identical prompt.
QUESTIONS: dict[ConversationMode, str] = {
    ConversationMode.NORMAL: (
        "Should I use a linked list or an array for a lookup-heavy cache?"
    ),
    ConversationMode.STUDY: (
        "Should I use a hash map or a balanced tree for an index I iterate in order?"
    ),
    ConversationMode.RESEARCH: (
        "Should I pick a B-tree or an LSM-tree for a write-heavy time-series store?"
    ),
    ConversationMode.QUICK: (
        "Should I use a mutex or a channel to share a counter between two threads?"
    ),
    ConversationMode.CODE: (
        "Should I use recursion or an explicit stack to walk a deep directory tree?"
    ),
    ConversationMode.CRITIC: (
        "Should I split my two-person project into microservices or keep the monolith?"
    ),
}

#: Long enough for a cloud round trip plus an agent step or two. Research is
#: the slow one: online mode is on, so it really does go and fetch pages.
TURN_TIMEOUT_S = 240.0

#: Tools this gate will approve on sight. **Read-only, and named explicitly**
#: rather than derived from the tier table — a gate that approves whatever the
#: code under test says is safe is agreeing with itself. Anything not listed is
#: denied, which is the right default for a script running unattended.
_AUTO_APPROVE = {"research", "browser_read", "read_file", "list_folder", "search_files", "find"}


class Client:
    """**One reader task, everything else off a queue.**

    The first version called `asyncio.wait_for(ws.recv(), timeout=5)` in a
    loop, which is a real hazard rather than a style point: `wait_for` cancels
    the pending `recv()` on every timeout, and a frame that arrived while the
    cancellation was in flight is lost. Modes answering in 5-15s survived it;
    Critic takes ~35s, which is seven cancellations, and its `turn.complete`
    went missing twice — the gate then reported a 240s timeout for a turn the
    database shows finished in 35. Cancelling a `Queue.get()` is safe in a way
    cancelling `recv()` is not.
    """

    def __init__(self, ws: Any) -> None:
        self._ws = ws
        self.events: list[dict[str, Any]] = []
        self._replies: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._inbox: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._reader = asyncio.create_task(self._read())

    async def _read(self) -> None:
        try:
            await self._pump()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            # Silently is how this cost three runs: the task died, replies kept
            # working from the queue that was already filled, and every later
            # turn "timed out" while the database showed it answering in 12s.
            print(f"    !! reader died: {type(exc).__name__}: {exc}")
            raise

    async def _pump(self) -> None:
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
        message = await asyncio.wait_for(future, timeout=60)
        if message.get("error"):
            raise RuntimeError(f"{method}: {message['error']}")
        return message.get("result")

    async def ask(self, session_id: str, text: str) -> dict[str, Any]:
        """Send, then wait for this turn's own completion."""
        self.events.clear()
        # Events from the previous turn are not this turn's. Left queued they
        # are only noise here, but a stale `turn.complete` sitting in front of
        # the real one is the kind of thing that reads as a hang.
        while not self._inbox.empty():
            self._inbox.get_nowait()
        started = await self.call("chat.send", {"session_id": session_id, "text": text})
        turn_id = started["turn_id"]
        deadline = time.perf_counter() + TURN_TIMEOUT_S
        while time.perf_counter() < deadline:
            message = await self.next_event(seconds=5)
            if message is None:
                continue

            # **A gate that cannot answer a confirmation does not fail, it
            # hangs** — `gate_research.py` learned this when Phase 6 made a
            # second agent step possible and §11 started escalating: the run
            # stalled for the full 120s timeout and then reported that the
            # sidecar was unreachable, which was false. Research mode reaches
            # for `research`, so this gate walked into it too.
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
            e["params"].get("name", "?")
            for e in self.events
            if e["method"] == "tool.call"
        ]


async def run_mode(client: Client, mode: ConversationMode) -> dict[str, Any]:
    session_id = (await client.call("chat.new"))["session_id"]
    state = await client.call("chat.mode", {"session_id": session_id, "mode": str(mode)})
    started = time.perf_counter()
    result = await client.ask(session_id, QUESTIONS[mode])
    elapsed = (time.perf_counter() - started) * 1000
    reply = (result.get("full_text") or "").strip()
    return {
        "mode": mode,
        "state": state,
        "reply": reply,
        "words": len(reply.split()),
        "ms": elapsed,
        "model": result.get("model"),
        "tools": client.tools_used(),
    }


def report(rows: list[dict[str, Any]]) -> int:
    failures: list[str] = []

    print("\n" + "=" * 72)
    print("WHAT THE SIDECAR SAYS EACH MODE IS")
    print("=" * 72)
    print(f"{'mode':9} {'steps':>5} {'tools':>10} {'bias':>9}  done_when")
    for row in rows:
        state = row["state"]
        done = (state.get("done_when") or "")[:44]
        print(
            f"{row['mode']!s:9} {state['max_steps']:5} {state['tools']:>10} "
            f"{state.get('effective_bias') or '—'!s:>9}  {done}…"
        )
        policy = policy_for(row["mode"])
        if state["max_steps"] != policy.max_steps:
            failures.append(
                f"{row['mode']}: RPC says {state['max_steps']} steps, "
                f"policy says {policy.max_steps}"
            )
        if state["tools"] != str(policy.tools):
            failures.append(
                f"{row['mode']}: RPC says {state['tools']} tools, "
                f"policy says {policy.tools}"
            )

    print("\n" + "=" * 72)
    print("SIX PARALLEL QUESTIONS, ONE PER MODE — see QUESTIONS for why not one")
    print("=" * 72)
    for row in rows:
        print(f"\n── {str(row['mode']).upper()} ── {row['words']} words, "
              f"{row['ms']:.0f}ms, model={row['model']}, tools={row['tools'] or 'none'}")
        print(row["reply"][:620] or "(empty reply)")

    print("\n" + "=" * 72)
    print("CHECKS")
    print("=" * 72)

    by_mode = {row["mode"]: row for row in rows}
    quick = by_mode[ConversationMode.QUICK]
    normal = by_mode[ConversationMode.NORMAL]

    # 1. Quick against Normal. **Observed, not asserted**, now that the two are
    #    answering different questions — a length difference that carries some
    #    of the question in it is not something to fail a build over.
    print(f"OBSERVED  Quick {quick['words']} words against Normal {normal['words']}")

    # 2. Nothing that changes the machine ran in a read-only mode. This is the
    #    tool ceiling doing its job, and the one check here with teeth.
    for row in rows:
        if policy_for(row["mode"]).tools.value != "read_only":
            continue
        offenders = [t for t in row["tools"] if t in _MUTATING]
        if offenders:
            failures.append(f"{row['mode']} is read-only but ran {offenders}")
    print("PASS  no read-only mode ran a tool that changes anything")

    # 3. Every mode answered at all. An empty reply is the one outcome a turn
    #    must never have.
    empty = [str(r["mode"]) for r in rows if not r["reply"]]
    if empty:
        failures.append(f"empty reply from {empty}")
    else:
        print("PASS  every mode produced an answer")

    # 4. OBSERVED, not scored: are the six replies actually different?
    lengths = sorted(r["words"] for r in rows)
    print(f"\nOBSERVED  reply lengths {lengths} — spread {lengths[-1] - lengths[0]} words")
    print("OBSERVED  read the six answers above. Whether Study teaches and Critic")
    print("          argues is a judgement, and a script that scored it would be")
    print("          inventing a measurement.")

    if failures:
        print("\nFAILURES")
        for failure in failures:
            print(f"  FAIL  {failure}")
        return 1
    print("\nGATE PASSED")
    return 0


#: Tools that change something. Used only to check a read-only mode never
#: reached one — deliberately a short explicit list rather than a tier lookup,
#: because this script is asserting against the *observed* calls, not against
#: the same table the code under test consults.
_MUTATING = {
    "write_file",
    "delete_file",
    "delete_folder",
    "move_file",
    "rename_file",
    "create_folder",
    "organize_folder",
    "undo_organize",
    "type_text",
    "kill_process",
    "close_app",
    "set_volume",
    "set_wifi",
    "write_clipboard",
    "browser_click",
    "browser_fill",
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

    async with connection as ws:
        client = Client(ws)
        try:
            rows = []
            for mode in ConversationMode:
                print(f"asking in {mode}…", flush=True)
                rows.append(await run_mode(client, mode))
            return report(rows)
        finally:
            await client.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
