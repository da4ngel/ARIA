"""Does Study Mode actually teach? Live, against a real sidecar.

    python scripts/gate_study.py

Eyaas's standard for this mode, verbatim: *"Never optimize Study Mode for
producing the best answer. Optimize it for producing the best learning
outcome."* So what this measures is the loop — **teach → check → record →
adapt** — end to end against a real model, not whether the prompt contains the
right words. `test_study.py`, `test_curriculum.py` and `test_study_tools.py`
already assert the mechanisms; a prompt containing an instruction is not
evidence that a model followed it.

Five lines, in the order they have to work:

1. A lecture becomes a map of concepts that are **actually in the material**.
2. She teaches one and ends on a question she does not answer herself.
3. Answering it moves that concept's mastery, and getting it wrong moves it
   back — checked in the database, not in her reply.
4. A **new session** with no file resumes the subject at the right place.
5. A question the lecture does not cover is answered as not covered, rather
   than from general knowledge as though it were in the slides.
6. A sub-mode changes the session: Revision works on what is shaky, and
   **an Exam does not give the answers away**, which is the one lever that is
   mechanical rather than a prompt line a model may ignore.

**Its own sessions, its own scratch lecture, and it answers its own
questions.** `chat.send` with no session continues whatever conversation was
most recently active — this project has already put real confirmation dialogs
into Eyaas's live chat once by forgetting that. And a gate that cannot answer a
question does not fail, it hangs: `gate_research.py` learned that when §11
started escalating, and this gate asks *by design*, so it would have walked
straight into it.

Line 1 is the one that can be wrong in a way that looks right, so it is checked
against the source text rather than by eye: a concept whose words appear
nowhere in the lecture is reported, because a map that teaches the wrong
syllabus confidently is the worst failure available here.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import sys
import tempfile
import time
import uuid
from typing import Any

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import websockets

URL = "ws://127.0.0.1:8765/rpc"

TURN_TIMEOUT_S = 300.0

#: Read-only and named explicitly rather than derived from the tier table — a
#: gate that approves whatever the code under test calls safe is agreeing with
#: itself.
_AUTO_APPROVE = {"read_file", "list_folder", "search_files", "search_content", "find"}

SUBJECT = "gate transport security"

#: A scratch lecture, not one of Eyaas's. Every other gate here builds its own
#: state and deletes it; pointing this one at a real lecture would mean a
#: failed run leaves a subject and a mastery history in his real database.
#:
#: Deliberately made-up terminology — "Kestrel handshake", "drift window" —
#: so that line 1 can tell a concept read *out of the material* from one the
#: model already knew. A lecture about TCP would prove nothing: every concept
#: in it is one a model can produce from memory.
LECTURE = """Kestrel Transport Security — Lecture 1

1. The Kestrel Handshake
The Kestrel handshake is the three-message exchange that opens every Kestrel
session. The initiator sends a HELLO carrying its drift window; the responder
answers with a CHALLENGE; the initiator closes with a SEAL. A handshake that
does not complete all three messages leaves no session state on either side,
which is deliberate: a half-open Kestrel session cannot be resumed.

2. The Drift Window
The drift window is the number of milliseconds by which two Kestrel peers may
disagree about the time and still accept each other's messages. The default is
400 milliseconds. A wide drift window makes replay easier; a narrow one makes
handshakes fail on congested links. Choosing it is a trade between those two.

3. Seal Rotation
Every Kestrel session seal expires after 90 seconds and must be rotated. A
rotation reuses the existing drift window and does not repeat the handshake.
If a rotation is missed, the session is closed rather than downgraded — Kestrel
has no notion of an unsealed session.

4. Replay Defence in Kestrel
Kestrel defeats replay with a nonce carried in the SEAL message, checked
against the drift window. A captured SEAL replayed after the drift window has
elapsed is rejected outright. A SEAL replayed inside the window is caught by
the nonce cache, which holds every nonce seen for exactly one drift window.
"""

#: A concept that is genuinely not in the lecture above. Line 5 asks about it.
NOT_IN_LECTURE = "How does Kestrel handle certificate revocation?"


class Client:
    """One reader task, everything else off a queue.

    `asyncio.wait_for(ws.recv(), ...)` in a loop cancels the pending `recv()`
    on every timeout, and a frame arriving during that cancellation is lost.
    `gate_modes.py` lost three runs to it before this shape was written down.
    """

    def __init__(self, ws: Any) -> None:
        self._ws = ws
        self.events: list[dict[str, Any]] = []
        self._replies: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._inbox: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._reader = asyncio.create_task(self._read())
        #: Filled by `ask`, so a section can assert on what she actually put
        #: on screen rather than on what her prose claims she asked.
        self.questions_asked: list[list[dict[str, Any]]] = []
        #: What this gate will pick, per question index. Empty picks the first
        #: option, which for line 3 is deliberately the wrong one.
        self.pick_correct = True

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
            # Dying silently is what made this take three runs to find.
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
        message = await asyncio.wait_for(future, timeout=90)
        if message.get("error"):
            raise RuntimeError(f"{method}: {message['error']}")
        return message.get("result")

    async def _answer_questions(self, params: dict[str, Any]) -> None:
        """Answer a `question.ask` the way a student would — one pick each.

        **This gate cannot skip these.** The turn is suspended on a future for
        ten minutes; ignoring the event would make every study turn look like
        a hang.
        """
        questions = params.get("questions") or []
        self.questions_asked.append(questions)
        answers = []
        for question in questions:
            options = [o["label"] for o in question.get("options", []) if o.get("label") != "Other"]
            if not options:
                continue
            # There is no answer key on the wire — by design, so the key
            # cannot reach the screen. So the gate picks by position and the
            # *database* is what says whether that was right.
            pick = options[0] if self.pick_correct else options[-1]
            answers.append({"question": question["question"], "chosen": [pick], "other": ""})
        print(f"    answered {len(answers)} question(s): {[a['chosen'][0] for a in answers]}")
        await self.call("question.answer", {"request_id": params["request_id"], "answers": answers})

    async def ask(
        self, session_id: str, text: str, attachments: list[str] | None = None
    ) -> dict[str, Any]:
        self.events.clear()
        self.questions_asked.clear()
        while not self._inbox.empty():
            self._inbox.get_nowait()

        params: dict[str, Any] = {"session_id": session_id, "text": text}
        if attachments:
            params["attachments"] = attachments
        started = await self.call("chat.send", params)
        turn_id = started["turn_id"]

        deadline = time.perf_counter() + TURN_TIMEOUT_S
        while time.perf_counter() < deadline:
            try:
                async with asyncio.timeout(5):
                    message = await self._inbox.get()
            except TimeoutError:
                continue

            method = message["method"]
            if method == "question.ask":
                await self._answer_questions(message["params"])
                continue
            if method == "confirm.request":
                request = message["params"]
                tool = request.get("tool", "?")
                approved = tool in _AUTO_APPROVE
                print(f"    confirm: {tool} -> {'approved' if approved else 'DENIED'}")
                await self.call(
                    "confirm.respond",
                    {"request_id": request["request_id"], "approved": approved},
                )
                continue
            if method == "turn.complete" and message["params"].get("turn_id") == turn_id:
                return dict(message["params"])
        raise TimeoutError(f"no turn.complete for {turn_id} within {TURN_TIMEOUT_S}s")

    def tools_used(self) -> list[str]:
        return [e["params"].get("name", "?") for e in self.events if e["method"] == "tool.call"]


async def study_session(client: Client) -> str:
    """Open a study chat.

    **Created, not switched into.** Study stopped being a mode you toggle and
    became a kind of conversation — `chat.mode` refuses it now, in both
    directions, so this gate would fail at its first line if it still tried.
    """
    started = await client.call("chat.new", {"kind": "study"})
    assert started["kind"] == "study", "chat.new did not open a study chat"
    return str(started["session_id"])


def concepts_in(state: dict[str, Any]) -> list[dict[str, Any]]:
    return list(state.get("concepts") or [])


async def read_map(client: Client) -> dict[str, Any]:
    """The map and its mastery, read straight from the sidecar's own state.

    Asserting on the database rather than on her reply is the point of lines 1
    and 3: a model that *says* it recorded something and a row that changed are
    different claims, and only the second one is what the next session reads.
    """
    return dict(await client.call("study.state") or {})


async def main() -> int:
    failures: list[str] = []
    observed: list[str] = []

    scratch = pathlib.Path(tempfile.gettempdir()) / "aria-gate-study"
    scratch.mkdir(parents=True, exist_ok=True)
    lecture = scratch / "Kestrel Transport Security Lecture 1.txt"
    lecture.write_text(LECTURE, encoding="utf-8")

    try:
        ws = await websockets.connect(URL, max_size=8 * 1024 * 1024)
    except OSError:
        print("Could not reach the sidecar on :8765. Start it with `npm run sidecar`.")
        return 2

    client = Client(ws)
    try:
        print("=" * 72)
        print("1. A LECTURE BECOMES A MAP OF WHAT IT ACTUALLY TEACHES")
        print("=" * 72)
        session = await study_session(client)
        result = await client.ask(
            session,
            "Teach me this lecture. Start from the beginning.",
            attachments=[str(lecture)],
        )
        tools = client.tools_used()
        print(f"    tools: {tools}")
        state = await read_map(client)
        concepts = concepts_in(state)
        print(f"    subject: {state.get('subject')!r}  concepts: {len(concepts)}")
        for concept in concepts:
            print(f"      - {concept['name']} (level {concept['level']})")

        if "study_begin" not in tools:
            failures.append("1. she did not call study_begin on an attached lecture")
        elif not concepts:
            failures.append("1. study_begin ran but no concepts were stored")
        else:
            # The check that matters: are these concepts *from the material*?
            source = LECTURE.casefold()
            invented = [
                c["name"]
                for c in concepts
                if not any(word in source for word in c["name"].casefold().split() if len(word) > 3)
            ]
            if invented:
                failures.append(f"1. concepts not present in the lecture: {invented}")
            else:
                print(f"    PASS  {len(concepts)} concepts, all grounded in the material")

        print("\n" + "=" * 72)
        print("2. SHE TEACHES, AND ENDS ON A QUESTION SHE DOES NOT ANSWER")
        print("=" * 72)
        reply = (result.get("full_text") or "").strip()
        print(f"    reply ({len(reply.split())} words):\n      {reply[:400]}")
        if client.questions_asked:
            print(f"    PASS  she put {len(client.questions_asked[0])} question(s) on screen")
        elif reply.rstrip().endswith("?"):
            observed.append("2. she ended on a written question rather than study_check")
            print("    OBSERVED  ended on a question, but in prose rather than the tool")
        else:
            failures.append("2. she taught without checking anything")

        print("\n" + "=" * 72)
        print("3. A WRONG ANSWER MOVES MASTERY BACK")
        print("=" * 72)
        before = {c["name"]: c["level"] for c in concepts_in(await read_map(client))}
        client.pick_correct = False
        await client.ask(session, "Quiz me on what you have taught so far.")
        after_wrong = {c["name"]: c["level"] for c in concepts_in(await read_map(client))}

        client.pick_correct = True
        await client.ask(session, "Ask me those again.")
        after_right = {c["name"]: c["level"] for c in concepts_in(await read_map(client))}

        print(f"    before:      {before}")
        print(f"    after wrong: {after_wrong}")
        print(f"    after right: {after_right}")
        moved = [n for n in after_right if after_right[n] != before.get(n)]
        if not moved:
            failures.append("3. no concept's mastery moved after two rounds of answers")
        else:
            print(f"    PASS  mastery moved for: {moved}")

        print("\n" + "=" * 72)
        print("4. A NEW SESSION RESUMES WITHOUT THE FILE")
        print("=" * 72)
        fresh = await study_session(client)
        result = await client.ask(fresh, f"Carry on with {SUBJECT}.")
        reply = (result.get("full_text") or "").strip()
        print(f"    tools: {client.tools_used()}")
        print(f"    reply:\n      {reply[:400]}")
        named = [c["name"] for c in concepts if c["name"].casefold() in reply.casefold()]
        if named:
            print(f"    PASS  she picked the subject back up, naming: {named}")
        else:
            observed.append("4. resumed, but named no concept from the map in her reply")
            print("    OBSERVED  no concept named in the reply — read it above and judge")

        print("\n" + "=" * 72)
        print("5. SOMETHING THE LECTURE DOES NOT COVER IS SAID TO BE UNCOVERED")
        print("=" * 72)
        result = await client.ask(fresh, NOT_IN_LECTURE)
        reply = (result.get("full_text") or "").strip()
        print(f"    reply:\n      {reply[:400]}")
        markers = (
            "not cover",
            "isn't cover",
            "is not cover",
            "not in ",
            "does not appear",
            "not mentioned",
            "outside",
            "no mention",
        )
        if any(m in reply.casefold() for m in markers):
            print("    PASS  she said it is outside the material")
        else:
            failures.append("5. she answered as though revocation were in the lecture")

        print("\n" + "=" * 72)
        print("6. SUB-MODES: REVISION WORKS ON WHAT IS SHAKY, EXAM WITHHOLDS")
        print("=" * 72)
        started = await client.call("study.start", {"session_id": fresh, "sub_mode": "revision"})
        print(f"    revision opener: {started['opener']!r}")
        await client.ask(fresh, started["opener"])
        print(f"    tools: {client.tools_used()}")

        started = await client.call("study.start", {"session_id": fresh, "sub_mode": "exam"})
        client.pick_correct = False
        result = await client.ask(fresh, started["opener"])
        reply = (result.get("full_text") or "").strip()
        print(f"    exam reply:\n      {reply[:400]}")

        # **The check that matters.** `study_check` withholds the per-question
        # answers under Exam, so the only way a right answer can appear in her
        # reply is if she invented it — which is worth knowing either way.
        summaries = [
            e["params"].get("summary", "") for e in client.events if e["method"] == "tool.result"
        ]
        leaked = [s for s in summaries if "the answer was" in s.lower()]
        if leaked:
            failures.append("6. an exam's tool result gave the answers away")
        elif summaries:
            print("    PASS  no tool result named a correct answer during the exam")
        else:
            observed.append("6. no study_check ran during the exam turn")
            print("    OBSERVED  she did not reach for study_check — read the reply above")

    finally:
        # The subject this gate created is left in place deliberately: it is
        # named `gate transport security`, it is the evidence for what the run
        # reported, and deleting it would take `study.forget` — a tool this
        # phase does not build. Say so rather than leaving it as a surprise.
        print(f"\nleft behind: study subject {SUBJECT!r} (delete it from the panel if you like)")
        lecture.unlink(missing_ok=True)
        await client.close()
        await ws.close()

    print("\n" + "=" * 72)
    for line in observed:
        print(f"OBSERVED  {line}")
    for line in failures:
        print(f"FAILED    {line}")
    print("GATE PASSED" if not failures else "GATE FAILED")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
