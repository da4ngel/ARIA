"""§9 Phase 7's research half, against the running sidecar.

    "research X and summarize with sources" returns real, correct URLs

    npm run dev                        # or: npm run sidecar
    python scripts/gate_research.py

**Scope, stated up front.** §9 Phase 7 is a browser phase: Playwright over a
real logged-in Chrome, `browser_click`, `browser_fill`, a checkout hard-block,
and *"check my email and summarize anything urgent"*. This gate covers the one
composite that does not need any of that — `research(query)` over a search API —
which is what Eyaas chose and what is built. **The other three acceptance lines
of Phase 7 are not tested here because the code they test does not exist**, and
CLAUDE.md says so rather than letting a green gate imply a finished phase.

What it does check:

1. she reaches for `research` when asked something live, unprompted;
2. the URLs she cites are **real** — every one is fetched and must respond;
3. the switch actually gates it, both halves: off, the model is not even told
   the tool exists, and the tool refuses if called anyway.

Point 2 is the one worth having. A model asked to "cite your sources" will
happily produce plausible URLs that 404, and every earlier phase of this project
has a story about a measurement that passed while the thing was broken.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import re

import httpx
import websockets
from websockets.exceptions import WebSocketException

#: Something she cannot know and cannot guess: it changes, and it is specific
#: enough that a fabricated URL is obvious.
QUESTION = "What is the latest stable version of Python? Search the web and cite your sources."

URL_PATTERN = re.compile(r"https?://[^\s<>\"'\)\]]+")


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
        results: asyncio.Queue[dict] = asyncio.Queue()
        confirmations: asyncio.Queue[dict] = asyncio.Queue()
        tokens: dict[str, list[str]] = {}

        async def pump() -> None:
            async for raw in ws:
                message = json.loads(raw)
                if "id" in message and message["id"] in pending:
                    pending.pop(message["id"]).set_result(message)
                elif message.get("method") == "tool.result":
                    await results.put(message["params"])
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

        async def ask(text: str) -> tuple[str, dict | None]:
            """One probe, in its own session.

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
                "chat.send", {"text": text, "session_id": session, "spoken": False}
            )
            turn_id = started["turn_id"]
            used: dict | None = None
            # **A gate that cannot answer a dialog is a gate that hangs.**
            # `research` is T1 and asks for nothing on its own, so this
            # script never needed confirmation handling — until Phase 6's
            # agent loop made a second step possible and §11 began escalating
            # the call after an untrusted read. A research-then-research
            # chain then stalled here for the full 120s confirmation timeout,
            # twice, and the run died with "Could not reach the sidecar".
            while True:
                confirm_task = asyncio.create_task(confirmations.get())
                complete_task = asyncio.create_task(completions.get())
                done_set, pending_set = await asyncio.wait(
                    {confirm_task, complete_task},
                    timeout=240,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if confirm_task in done_set:
                    complete_task.cancel()
                    request = confirm_task.result()
                    print(
                        f"      confirm.request  tool={request['tool']} "
                        f"escalated={request.get('escalated')}"
                    )
                    await call(
                        "confirm.respond",
                        {"request_id": request["request_id"], "approved": True},
                    )
                    continue
                if complete_task in done_set:
                    confirm_task.cancel()
                    if complete_task.result().get("turn_id") == turn_id:
                        break
                    continue
                for t in pending_set:
                    t.cancel()
                raise TimeoutError(f"turn {turn_id} never completed")
            while not results.empty():
                used = results.get_nowait()
            return ("".join(tokens.get(turn_id, [])), used)

        failures = 0
        was_online: bool | None = None
        try:
            state = await call("settings.online", {})
            was_online = bool(state["enabled"])
            print(
                f"online mode: {state['enabled']}  backend: {state['backend']}  "
                f"key present: {state['key_present']}\n"
            )
            # ── 1. off means off, in both places ─────────────────────────
            #
            # Checked first and checked always: it needs no key, and it is the
            # half that matters when something goes wrong. A gate that refuses
            # to test the part it *can* test is a worse gate.
            print("1. With online mode off")
            await call("settings.online", {"enabled": False})
            reply, used = await ask("What is the latest stable version of Python?")
            offered = used is not None and used.get("tool") == "research"
            print(f"   she called research: {offered}")
            print(f"   {_ok(not offered)}  the tool is not even offered when off")
            failures += 1 if offered else 0

            if not state["key_present"]:
                print(
                    "\nSKIPPED  the rest needs a search key. Add a free Tavily key\n"
                    "         (tavily.com) or Brave key (brave.com/search/api) in\n"
                    "         Settings, then run this again.\n"
                )
                print(f"GATE {'PARTIAL' if failures == 0 else f'FAILED ({failures})'}")
                return 0 if failures == 0 else 1

            # ── 2. on, and she reaches for it unprompted ─────────────────
            print("\n2. With online mode on")
            await call("settings.online", {"enabled": True})
            reply, used = await ask(QUESTION)
            called = used is not None and used.get("tool") == "research"
            print(f"   she called: {used.get('tool') if used else None}")
            print(f"   {_ok(called)}  she reached for research")
            failures += 0 if called else 1

            # ── 3. the URLs are real ─────────────────────────────────────
            cited = list(dict.fromkeys(URL_PATTERN.findall(reply)))
            print(f"   reply: {reply.strip()[:220]}")
            print(f"   cited {len(cited)} URL(s)")
            if not cited:
                print("   FAIL  no sources cited")
                failures += 1
            else:
                reachable = await _check(cited)
                for url, status in reachable:
                    print(f"        {status:>6}  {url[:96]}")
                good = sum(1 for _, s in reachable if s == "ok")
                real = good == len(reachable)
                print(
                    f"   {_ok(real)}  every cited URL resolves "
                    f"({good}/{len(reachable)}) — a model will happily invent "
                    f"plausible ones"
                )
                failures += 0 if real else 1

            print(f"\nGATE {'PASSED' if failures == 0 else f'FAILED ({failures})'}")
            return 0 if failures == 0 else 1
        finally:
            # Leave the switch as it was found. A gate that silently turns on
            # network access and walks away is its own kind of bug.
            if was_online is not None:
                await call("settings.online", {"enabled": was_online})
            task.cancel()


async def _check(urls: list[str]) -> list[tuple[str, str]]:
    """Does each cited URL actually exist? The whole point of this gate."""
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=15.0,
        headers={"User-Agent": "Mozilla/5.0 ARIA-gate"},
    ) as client:

        async def one(url: str) -> tuple[str, str]:
            cleaned = url.rstrip(".,;:)]}")
            try:
                response = await client.get(cleaned)
            except httpx.HTTPError as exc:
                return (cleaned, type(exc).__name__)
            return (cleaned, "ok" if response.status_code < 400 else str(response.status_code))

        return list(await asyncio.gather(*(one(u) for u in urls)))


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except (OSError, WebSocketException) as exc:
        print(f"Could not reach the sidecar: {exc}\nStart it with: npm run sidecar")
        raise SystemExit(2) from exc
