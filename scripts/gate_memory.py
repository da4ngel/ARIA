"""§9 Phase 5's acceptance gate, against the running sidecar.

    "I usually work on Sillara pricing before 10am"
      -> after reflection, a matching fact exists with the right predicate
    contradict it  -> the old fact gets superseded_by, the new one is active
    pin it, reflect over contradicting evidence -> the pinned fact survives
    a two-message chat, then a new one -> she still remembers it (step 5b)
    retrieval adds  < 80ms to turn latency

`test_semantic.py` and `test_retrieval.py` prove the logic against stubs. This
proves the product: a real conversation, a real model extracting real facts,
and the real retrieval path timed on real turns.

    npm run dev                              # or: npm run sidecar
    python scripts/gate_memory.py            # the whole gate
    python scripts/gate_memory.py --latency  # the timing alone

**The pin test must not speak.** §9 words step 4 as "pin a fact, run reflection
with contradicting evidence". Saying the contradiction out loud makes her call
the `remember` tool, which writes as `FactSource.USER` — and §8.3 is explicit
that a pinned fact may be superseded "only by the user". That path *correctly*
overrides the pin, so a gate built on it tests the opposite of what it claims.
Step 4 therefore re-reflects over the window that already holds the
contradiction, and never sends a turn.

**Two things this cannot check, and says so rather than reporting a pass:**

- *"Next day, ask at 9am and she references it unprompted."* The clock cannot
  be moved without lying about it, and whether a 7B volunteers a remembered
  fact is a property of the model, not of memory. Step 5 runs it and reports
  what happened as OBSERVED.
- *The prefill cost of the injected block.* The gate measures the retrieval
  step, which is what "<80ms" can mean; ~220 tokens of injected memory costs a
  further ~105ms of prefill at the measured 480ms/1000. That is printed beside
  the gate and deliberately excluded — it is the cost §8.2 already accepted for
  the volatile section.

It cleans up after itself, so re-running it does not leave "Sillara pricing" in
the real database.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import sys

import websockets
from websockets.exceptions import WebSocketException

LEARN = "I usually work on Sillara pricing before 10am"
CONTRADICT = "Actually I work on Sillara pricing in the evenings now"

#: What "with the right predicate" is checked *by*.
#:
#: §9 asks for "a matching fact with the right predicate". An earlier version of
#: this script enumerated acceptable predicates and failed on `has_a_habit_of`,
#: which is a perfectly good answer — the model invents relation names freely
#: (`habitually`, `prefers`, `works`, `has_a_habit_of` across four runs) and no
#: list survives contact with that.
#:
#: So the assertion is what a predicate is *for*: the fact has to come back when
#: you ask about the thing. A garbled relation fails that; `has_a_habit_of`
#: passes it. The triple is printed either way so a human can still judge it.
RECALL_PROBE = "when do I work on Sillara pricing?"

#: Varied on purpose: some trivial, some topical. A run where none are skipped
#: means the trivial-message filter has regressed, which is most of the budget.
LATENCY_TURNS = [
    "ok",
    "what am I working on at the moment?",
    "thanks",
    "remind me about the Sillara pricing schedule",
    "yes",
    "what do you know about my mornings?",
    "go on",
    "what is the capital of Australia?",
    "sure",
    "tell me about my pricing work",
    "no",
    "when do I usually start?",
]

GATE_P90_MS = 80.0
PREFILL_MS_PER_1000 = 480.0


def _ok(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


async def main(latency_only: bool = False) -> int:
    handshake = pathlib.Path("data/.handshake").read_text().strip()
    try:
        token = str(json.loads(handshake)["token"])
    except (json.JSONDecodeError, KeyError, TypeError):
        token = handshake

    async with websockets.connect(
        "ws://127.0.0.1:8765/rpc",
        additional_headers={"Authorization": f"Bearer {token}"},
        # She speaks, and synthesised audio goes to every connected client.
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
                    # Deny anything that asks, immediately. A gate script must
                    # never approve a T2+ operation on someone's machine, and
                    # leaving it unanswered stalls the turn for the full 120s
                    # timeout — which is how the first run of this script hung.
                    params = message["params"]
                    print(f"   (denied an unexpected confirm: {params.get('tool')})")
                    counter[0] += 1
                    await ws.send(
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": counter[0],
                                "method": "confirm.respond",
                                "params": {
                                    "request_id": params["request_id"],
                                    "approved": False,
                                },
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
            """One turn, start to finish. Returns the reply."""
            started = await call("chat.send", {"text": text, "spoken": False})
            turn_id = started["turn_id"]
            while True:
                done = await asyncio.wait_for(completions.get(), timeout=300)
                if done.get("turn_id") == turn_id:
                    break
            return "".join(tokens.get(turn_id, []))

        async def active_facts() -> list[dict]:
            listing = await call("memory.list", {})
            return [f for f in listing["facts"] if f["superseded_by"] is None]

        try:
            failures = 0
            created_sessions: list[str] = []

            stats = await call("memory.stats", {})
            print(
                f"embeddings_ready={stats['embeddings_ready']}  "
                f"facts={stats['facts']}  episodes={stats['episodes']}\n"
            )
            if stats["embeddings_ready"] is False:
                print(
                    "NOTE  Embeddings are unavailable, so retrieval is running on word\n"
                    "      matching. The latency figure below is NOT the semantic path.\n"
                    "      Run: ollama pull nomic-embed-text\n"
                )

            if not latency_only:
                # ── 1-2. she learns, and the fact is the right shape ──────
                print("1. Learning")
                session = await call("chat.new", {})
                created_sessions.append(session["session_id"])
                await say(LEARN)
                report = await call("memory.reflect", {"window_hours": 1})
                print(
                    f"   reflect  model={report['model']} read={report['messages_read']} "
                    f"+{report['inserted']} learned  {report['reinforced']} reinforced  "
                    f"{report['superseded']} replaced  {report['blocked_by_pin']} pinned kept"
                )
                if report["error"]:
                    print(f"   error: {report['error']}")

                facts = await active_facts()
                matches = [
                    f
                    for f in facts
                    if f["subject"] == "user"
                    and "sillara" in f["object"].lower()
                    and ("10" in f["object"] or "morning" in f["object"].lower())
                ]
                print("2. A fact exists, and it comes back when asked")
                for fact in facts:
                    print(
                        f"   [{fact['id']}] {fact['subject']} | {fact['predicate']} | "
                        f"{fact['object']}  ({fact['confidence']:.2f})"
                    )
                learned = matches[0] if matches else None

                found = await call("memory.search", {"query": RECALL_PROBE})
                recalled = [
                    hit["fact"]
                    for hit in found["facts"]
                    if "sillara" in hit["fact"]["object"].lower()
                ]
                print(
                    f'   probe "{RECALL_PROBE}" -> {len(recalled)} match(es) '
                    f'in {found["took_ms"]}ms'
                    f'{"  (degraded to word matching)" if found["degraded"] else ""}'
                )
                passed = bool(learned) and bool(recalled)
                print(f"   {_ok(passed)}  a Sillara/morning fact exists and is recallable")
                failures += 0 if passed else 1

                # ── 3. a contradiction supersedes ─────────────────────────
                print("3. Contradicting it")
                if learned is None:
                    print("   SKIP  nothing was learned to contradict")
                    failures += 1
                else:
                    morning_ids = {
                        f["id"]
                        for f in matches
                        if "10" in f["object"] or "morning" in f["object"].lower()
                    }
                    await say(CONTRADICT)
                    await call("memory.reflect", {"window_hours": 1})

                    listing = await call("memory.list", {"include_superseded": True})
                    by_id = {f["id"]: f for f in listing["facts"]}
                    still_active_morning = [
                        f
                        for f in listing["facts"]
                        if f["id"] in morning_ids and f["superseded_by"] is None
                    ]
                    # Follow the pointer rather than grepping the object for
                    # "evening". The replacement is whatever `superseded_by`
                    # names — exact by construction — and the model phrases the
                    # new fact however it likes ("in the evenings", "evening
                    # hours", "after work"), so a keyword check turns a passing
                    # run into a failing one for no reason.
                    replacements = [
                        by_id[f["superseded_by"]]
                        for f in listing["facts"]
                        if f["id"] in morning_ids
                        and f["superseded_by"] is not None
                        and f["superseded_by"] in by_id
                    ]
                    active_replacements = [
                        f for f in replacements if f["superseded_by"] is None
                    ]
                    for fact in listing["facts"]:
                        if fact["id"] in morning_ids:
                            print(
                                f"   was [{fact['id']}] {fact['predicate']} | "
                                f"{fact['object']}  superseded_by={fact['superseded_by']}"
                            )
                    for fact in active_replacements:
                        print(
                            f"   active now: [{fact['id']}] {fact['predicate']} | "
                            f"{fact['object']}"
                        )

                    # The property §9 asks for is that the *old belief* stops
                    # being active and a replacement takes over — not that one
                    # particular row was the casualty, and not that it used any
                    # particular words.
                    passed = not still_active_morning and bool(active_replacements)
                    print(f"   {_ok(passed)}  the old belief was replaced, not duplicated")
                    failures += 0 if passed else 1
                    if active_replacements:
                        learned = active_replacements[0]

                # ── 4. a pin survives ─────────────────────────────────────
                print("4. Pinning, then reflecting over contradicting evidence")
                if learned is None:
                    print("   SKIP  no fact to pin")
                    failures += 1
                else:
                    await call("memory.update", {"fact_id": learned["id"], "user_locked": True})
                    # Reflect again over the window already holding both the
                    # "before 10am" and "in the evenings" statements, rather
                    # than sending another turn.
                    #
                    # Saying it out loud makes her call the `remember` tool,
                    # which writes as FactSource.USER — and §8.3 is explicit
                    # that a pinned fact may be superseded "only by the user".
                    # So that path legitimately overrides the pin, and a gate
                    # that used it would be testing the opposite of what §9
                    # asks. What must not overwrite a pin is *reflection*.
                    report = await call("memory.reflect", {"window_hours": 1})
                    survivor = next(
                        (f for f in await active_facts() if f["id"] == learned["id"]), None
                    )
                    intact = bool(survivor) and survivor["object"] == learned["object"]
                    print(
                        f"   pinned fact {learned['id']} "
                        f"{'survived unchanged' if intact else 'was changed or removed'}; "
                        f"blocked_by_pin={report['blocked_by_pin']}"
                    )
                    print(f"   {_ok(intact)}  reflection did not overwrite a pinned fact")
                    failures += 0 if intact else 1

                # ── 5. unprompted recall — OBSERVED, not asserted ─────────
                print("5. Referencing it unprompted")
                session = await call("chat.new", {})
                created_sessions.append(session["session_id"])
                reply = await say("what should I be doing?")
                mentioned = "sillara" in reply.lower() or "pricing" in reply.lower()
                print(f"   reply: {reply.strip()[:200]}")
                print(
                    f"   OBSERVED  memory mentioned: {mentioned}  "
                    "(model-dependent, and the spec's 'next day at 9am' cannot be "
                    "produced without lying about the clock — not counted)"
                )

                # ── 5b. the reported bug, end to end ──────────────────────
                #
                # Eyaas asked about data science job skills, opened a new chat,
                # asked "did we have any conversation regarding any job kind of
                # things?" and was told no. Six separate causes, and this step
                # is the only thing that proves all six at once — every other
                # test here proves a mechanism.
                #
                # It asserts she *finds* it, not that she phrases it any
                # particular way. `recall` returning the exchange is the
                # product working; whether a 7B then opens with "yes" is the
                # model's business, and step 5 already covers that ground.
                print("5b. A short conversation, remembered in the next one")
                session = await call("chat.new", {})
                created_sessions.append(session["session_id"])
                await say(
                    "If I'm going to apply for a data science job, what skills "
                    "matter most?"
                )
                # New Chat closes the previous session, which is what writes the
                # episode. Two messages — the exact length that used to be
                # silently discarded.
                session = await call("chat.new", {})
                created_sessions.append(session["session_id"])

                found = await call(
                    "memory.search", {"query": "data science jobs", "limit": 5}
                )
                summaries = [
                    str(e["episode"]["summary"]) for e in found.get("episodes", [])
                ]
                remembered = any(
                    "job" in s.lower() or "data science" in s.lower() for s in summaries
                )
                if summaries:
                    print(f"   episode: {summaries[0][:110]}")
                else:
                    print("   nothing came back for 'data science jobs'")
                print(f"   {_ok(remembered)}  a two-message chat became a memory")
                failures += 0 if remembered else 1

                reply = await say("did we have any conversation regarding any jobs?")
                denied = any(
                    phrase in reply.lower()
                    for phrase in (
                        "no record",
                        "don't have any record",
                        "no conversation",
                        "outside this chat",
                        "we haven't discussed",
                        "have not discussed",
                    )
                )
                print(f"   reply: {reply.strip()[:200]}")
                print(
                    f"   {_ok(not denied)}  she did not deny a conversation that happened"
                )
                failures += 1 if denied else 0

            # ── 6. the latency gate ───────────────────────────────────────
            print("6. Retrieval latency")
            before = (await call("memory.stats", {}))["retrieval"]["count"]
            session = await call("chat.new", {})
            created_sessions.append(session["session_id"])
            for text in LATENCY_TURNS:
                await say(text)
            retrieval = (await call("memory.stats", {}))["retrieval"]

            # Every figure below is over the sidecar's rolling sample window,
            # so they are all in the same units. Reporting `n` as a delta while
            # p50/degraded/empty came from the window produced "n=12, empty=15",
            # which is the sort of nonsense that makes a measurement worthless
            # six months later. The delta is printed alongside instead.
            added = retrieval["count"] - before
            block_ms = 220 * PREFILL_MS_PER_1000 / 1000
            print(
                f"   retrieval   window={retrieval['count']} (+{added} this run)  "
                f"p50 {retrieval['p50_ms']}ms  p90 {retrieval['p90_ms']}ms  "
                f"max {retrieval['max_ms']}ms  degraded {retrieval['degraded']}  "
                f"empty {retrieval['empty']}"
            )
            print(
                f"   embed only  n={retrieval['embed_count']}  "
                f"p50 {retrieval['embed_p50_ms']}ms  p90 {retrieval['embed_p90_ms']}ms"
            )
            print(
                f"   block cost  <=220 tok ~= {block_ms:.0f}ms prefill "
                "(not part of the gate; §8.2 already accepts it)"
            )
            if retrieval["empty"] == 0:
                print(
                    "   WARN  no turn skipped retrieval. The trivial-message filter "
                    "is most of the budget — check it has not regressed."
                )
            within = retrieval["p90_ms"] < GATE_P90_MS
            print(
                f"   {_ok(within)}  GATE  p90 {retrieval['p90_ms']}ms < {GATE_P90_MS:.0f}ms"
            )
            failures += 0 if within else 1

            # ── 7. leave the database as we found it ──────────────────────
            print("7. Cleanup")
            removed = 0
            # `include_superseded`, not `active_facts()`: a run leaves behind a
            # chain of replaced facts, and listing only the active ones left
            # every superseded "Sillara pricing" row in the real database.
            # `memory.forget` releases inbound pointers itself, so order here
            # does not matter. Unpin first — a pinned fact is still test data.
            listing = await call("memory.list", {"include_superseded": True})
            for fact in listing["facts"]:
                if "sillara" in fact["object"].lower():
                    await call("memory.update", {"fact_id": fact["id"], "user_locked": False})
                    await call("memory.forget", {"fact_id": fact["id"]})
                    removed += 1
            for session_id in created_sessions:
                await call("chat.delete", {"session_id": session_id, "confirm": True})
            print(f"   removed {removed} facts and {len(created_sessions)} sessions")

            print(f"\n{'GATE PASSED' if failures == 0 else f'GATE FAILED ({failures})'}")
            return 0 if failures == 0 else 1
        finally:
            task.cancel()


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main("--latency" in sys.argv)))
    except (OSError, WebSocketException) as exc:
        # `websockets.exceptions` is a lazy submodule and resolving it through
        # the package raises `AttributeError` — so the handler for "the sidecar
        # is not reachable" was itself the thing that crashed, burying the real
        # error under a traceback about the websockets package. Imported at the
        # top now, where it fails loudly at import time if it ever moves.
        print(f"Could not reach the sidecar: {exc}\nStart it with: npm run sidecar")
        raise SystemExit(2) from exc
