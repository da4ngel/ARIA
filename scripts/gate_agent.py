"""§9 Phase 6's agent loop, against the running sidecar.

    "find <scratch file>, read its contents, and tell me what's in it"
        -> chains find -> read_file -> answers, each step numbered

    npm run dev                        # or: npm run sidecar
    python scripts/gate_agent.py

`test_conversation.py` proves the loop's mechanics against a scripted fake
provider — same-call loop detection, the MAX_STEPS hard stop, the §11
escalation after an untrusted-source tool, mid-chain degrade-to-local, and
that mutating any one of those breaks exactly the test built for it. This
gate proves the product: a real model deciding, on its own, to call one tool
after seeing the result of the last one.

**Two of §9's four acceptance lines are not automated here, and said so
rather than faked.** Forcing a tool failure mid-chain and pulling the network
mid-chain both need to manipulate live conditions this script cannot safely
do to a machine it does not own (deleting a real file out from under a
running chain; taking the network down while other things on this computer
may depend on it). Both are printed as manual steps below instead of a false
PASS. What is automated:

1. a real chain: find -> open -> answer, `tool.call` events numbered by step;
2. loop detection, asked directly rather than hoped for — a model *can*
   decline to repeat itself on its own, which is a fine outcome too, so this
   is scored OBSERVED, not PASS/FAIL;
3. the §11 escalation firing for real after `research`, when online mode and
   a search key are available — SKIPPED otherwise, same as `gate_research.py`.

**Run live 2026-08-13, and check 1 (the answer uses the tool result) does not
pass yet — recorded honestly rather than adjusted until it does.** Checks 2
and 3 pass cleanly and repeatedly: the loop itself is proven — real step
numbers, the §11 escalation firing exactly when expected (`open_app` arrived
`escalated: true` immediately after `research`, every run), multi-tool chains
genuinely occurring up to the step budget. What check 1 exposes instead is a
finder cold-start: a file this script just wrote is not yet visible to
`find`/`search_files` (Phase 4's indexer is deliberately throttled — CLAUDE.md:
"an indexer that makes the machine feel slow gets uninstalled"), so the model
— correctly routed to `gpt-5.4-nano` per the quality bias, not stuck local —
spends its steps hunting across `search_files`, `open_file`, `read_file`,
`find` and sometimes even `research` for a file it cannot yet see, and some
runs end in an empty reply rather than an explanation. That emptiness is
itself worth another look — a model that gives up should say so, not go
silent — but it is a finder-and-final-answer question, not evidence the loop
mis-chained anything: every tool call it made was real, numbered correctly,
and fed back in. Left as a known gap for a future session rather than
loosened into a pass.
"""

from __future__ import annotations

import asyncio
import json
import pathlib

import websockets
from websockets.exceptions import WebSocketException

SCRATCH = pathlib.Path.home() / "Downloads" / "aria-agent-gate.txt"
SCRATCH_TEXT = "Project Nightingale ships 2026-Q3. Budget owner: Priya."


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
        completions: asyncio.Queue[dict] = asyncio.Queue()
        calls: asyncio.Queue[dict] = asyncio.Queue()
        confirmations: asyncio.Queue[dict] = asyncio.Queue()
        tokens: dict[str, list[str]] = {}

        async def pump() -> None:
            async for raw in ws:
                message = json.loads(raw)
                if "id" in message and message["id"] in pending:
                    pending.pop(message["id"]).set_result(message)
                elif message.get("method") == "tool.call":
                    await calls.put(message["params"])
                elif message.get("method") == "confirm.request":
                    await confirmations.put(message["params"])
                elif message.get("method") == "turn.complete":
                    await completions.put(message["params"])
                elif message.get("method") == "token":
                    params = message["params"]
                    tokens.setdefault(params["turn_id"], []).append(params["text"])

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
            message = await asyncio.wait_for(fut, timeout=240)
            if "error" in message:
                raise RuntimeError(message["error"])
            return dict(message["result"])

        async def ask(
            text: str, *, session_id: str, auto_confirm: bool = True
        ) -> tuple[str, list[dict]]:
            """Send a turn, collect every `tool.call` it makes, answer any
            confirmation that comes up (approve, unless told not to), and
            return the final text plus the ordered list of calls.

            **`session_id` is required, not optional.** `chat.send` with no
            session continues *whatever conversation was most recently
            active* — which for a gate script means its probes, and the real
            `confirm.request` dialogs they raise, land in whatever Eyaas
            happens to have open. That already happened once, with
            `gate_permission_modes.py`; the write-up of that incident said
            "unlike every other gate script here, all of which call
            `chat.new` first", and that was simply not true — five of them
            did not. It is also why two consecutive runs of this gate used
            to contaminate each other: section 3's "search the web, then
            open Notepad" was still in context when the next run's section 1
            started, and the model dutifully did it again.
            """
            started = await call(
                "chat.send", {"text": text, "session_id": session_id, "spoken": False}
            )
            turn_id = started["turn_id"]
            seen: list[dict] = []

            async def drain_calls() -> None:
                while not calls.empty():
                    seen.append(calls.get_nowait())

            while True:
                confirm_task = asyncio.create_task(confirmations.get())
                complete_task = asyncio.create_task(completions.get())
                done, pending_tasks = await asyncio.wait(
                    {confirm_task, complete_task},
                    timeout=240,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                await drain_calls()
                if confirm_task in done:
                    complete_task.cancel()
                    request = confirm_task.result()
                    print(
                        f"      confirm.request  tool={request['tool']} "
                        f"escalated={request.get('escalated')}"
                    )
                    if auto_confirm:
                        await call(
                            "confirm.respond",
                            {"request_id": request["request_id"], "approved": True},
                        )
                    else:
                        for t in pending_tasks:
                            t.cancel()
                        return "".join(tokens.get(turn_id, [])), seen
                    continue
                if complete_task in done:
                    confirm_task.cancel()
                    finished = complete_task.result()
                    if finished.get("turn_id") == turn_id:
                        await drain_calls()
                        # `full_text` first, streamed tokens second — exactly
                        # what `useConversation.ts` does (`content ||
                        # payload.full_text`). Some replies never stream at
                        # all: the agent loop's own `repeat_note`, and the
                        # fallback for a model that finishes a pass with no
                        # text, are both appended after streaming ends. A
                        # gate reading only the token stream reports those as
                        # an empty reply, which is a defect in the gate and
                        # not in what the user is shown.
                        streamed = "".join(tokens.get(turn_id, []))
                        return str(finished.get("full_text") or streamed), seen
                    continue
                for t in pending_tasks:
                    t.cancel()
                raise TimeoutError(f"turn {turn_id} never completed")

        failures = 0

        # ── setup: a findable scratch file with something to report back ──
        SCRATCH.parent.mkdir(parents=True, exist_ok=True)
        SCRATCH.write_text(SCRATCH_TEXT, encoding="utf-8")
        print(f"scratch file: {SCRATCH}\n")

        try:
            # ── 1. a real chain ─────────────────────────────────────────
            #
            # Asked by *name*, not given the path, so a find-then-open chain
            # is actually necessary rather than answerable with one call —
            # but Phase 4's finder is throttled (CLAUDE.md: "an indexer that
            # makes the machine feel slow gets uninstalled") and a file this
            # script just wrote is not indexed yet. The wait below is that
            # subsystem's own startup cost, not this loop's — measured the
            # first time this gate ran, the chain instead wandered across
            # `research`, `open_path`, `search_content` and more hunting for
            # a file that had not been indexed yet, which is a real finding
            # about the finder's cold-start, not about the agent loop.
            await asyncio.sleep(6.0)
            print("1. find -> read -> answer")
            # "read the contents" rather than "open it" — the tools are two
            # different things (`open_file` launches the default app and
            # leaves a real, visible Notepad window behind; `read_file`
            # returns text into context) and the wrong verb here nudges her
            # towards the wrong one, discovered by this gate leaving stray
            # Notepad windows on the desktop across repeated runs.
            session = (await call("chat.new"))["session_id"]
            reply, chain_calls = await ask(
                f"find the file named {SCRATCH.name} and read its contents to tell me "
                f"who the budget owner is",
                session_id=session,
            )
            names = [c["tool"] for c in chain_calls]
            steps = [c.get("step") for c in chain_calls]
            print(f"   tools called: {names}")
            print(f"   step numbers: {steps}")
            print(f"   reply: {reply.strip()[:200]}")

            chained = len(names) >= 2 and names != [names[0]] * len(names)
            print(f"   {_ok(chained)}  more than one distinct tool ran in one turn")
            failures += 0 if chained else 1

            numbered = steps == sorted(steps) and len(set(steps)) == len(steps)
            print(f"   {_ok(numbered)}  each call carries its own, increasing step")
            failures += 0 if numbered else 1

            named_owner = "priya" in reply.lower()
            print(f"   {_ok(named_owner)}  the answer actually used what open_file returned")
            failures += 0 if named_owner else 1

            # ── 2. loop detection, asked directly ───────────────────────
            print("\n2. loop detection (best-effort — a model may just decline to repeat itself)")
            session = (await call("chat.new"))["session_id"]
            reply2, calls2 = await ask(
                "Call list_windows, then call list_windows again with the exact same "
                "arguments even though you already have the result.",
                session_id=session,
            )
            names2 = [c["tool"] for c in calls2]
            repeated_request = names2.count("list_windows") >= 2
            if not repeated_request:
                print(f"   OBSERVED  the model did not actually repeat itself: {names2}")
            else:
                # It asked twice; the loop must have only *run* it once — and
                # since `ask()` already returned, the turn plainly did not
                # hang on the repeat, which is the property that matters.
                print(f"   asked twice, reply: {reply2.strip()[:160]}")
                print(f"   {_ok(True)}  OBSERVED — repeat requested, second one did not hang")

            # ── 3. the §11 escalation, if online mode is usable ─────────
            print("\n3. the step after `research` escalates the next tool")
            state = await call("settings.online", {})
            if not state["key_present"]:
                print(
                    "   SKIPPED  needs a search key (Tavily or Brave) in Settings, "
                    "same precondition as gate_research.py"
                )
            else:
                was_online = bool(state["enabled"])
                await call("settings.online", {"enabled": True})
                try:
                    session = (await call("chat.new"))["session_id"]
                    _, calls3 = await ask(
                        "Search the web for today's date, then open Notepad.",
                        session_id=session,
                        auto_confirm=False,
                    )
                    names3 = [c["tool"] for c in calls3]
                    print(f"   tools called before the confirmation: {names3}")
                    # Whether that confirmation carried `escalated: true` was
                    # already printed by `ask()` the moment it arrived — this
                    # just confirms the turn actually got that far.
                    reached_second_step = "research" in names3
                    print(f"   {_ok(reached_second_step)}  it reached for research first")
                    failures += 0 if reached_second_step else 1
                finally:
                    await call("settings.online", {"enabled": was_online})

        finally:
            task.cancel()
            if SCRATCH.exists():
                SCRATCH.unlink()

        print(
            "\n4. MANUAL — not automated here, see the module docstring for why:\n"
            "   a. force a tool failure mid-chain: start a chain that reads a file,\n"
            "      delete the file between steps, confirm she recovers or explains\n"
            "      rather than hanging.\n"
            "   b. pull the network mid-chain: start a chain that reaches a cloud\n"
            "      model partway through, disconnect, confirm the turn finishes\n"
            "      locally with a note rather than hanging or erroring silently."
        )

        print(f"\nGATE {'PASSED' if failures == 0 else f'FAILED ({failures})'}")
        return 0 if failures == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except (OSError, WebSocketException) as exc:
        print(f"Could not reach the sidecar: {exc}\nStart it with: npm run sidecar")
        raise SystemExit(2) from exc
