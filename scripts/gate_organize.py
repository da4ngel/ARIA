"""§9 Phase 4c's acceptance gate, against the running sidecar.

    organize_folder on a messy Downloads folder:
      plan is sane, one confirmation, undo restores exactly

    npm run dev                          # or: npm run sidecar
    python scripts/gate_organize.py

**It builds its own Downloads.** Pointing the gate at the real one and hoping
would be a poor trade: the acceptance line ends in "undo restores exactly", and
proving that on somebody's actual downloads folder means a failure costs them
their files rather than costing the gate a red line. A scratch folder with the
same shape — a `.crdownload` mid-write, an existing `Documents/`, a name
collision — exercises every branch that a real one would.

`test_organize.py` proves the logic against a temp directory. This proves the
*product*: the tool reached through the registry, the tier engine raising one
real confirmation, the dialog payload the renderer would draw, and the undo
manifest on disk under `data/undo/`.

**The three things it checks are the three clauses of the acceptance line**,
and the middle one is the reason `Tool.preview` exists at all — a batch
confirmation nobody can read is not a confirmation.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import shutil

import websockets
from websockets.exceptions import WebSocketException

#: A Downloads folder as they actually look, including the two awkward cases.
MESSY = [
    "invoice_march.pdf",
    "contract_final.docx",
    "notes.txt",
    "holiday.png",
    "screenshot.PNG",
    "diagram.svg",
    "budget_2026.xlsx",
    "expenses.csv",
    "setup_installer.exe",
    "backup.zip",
    "presentation.pptx",
    "script.py",
    "song.mp3",
    "clip.mp4",
    "mystery.qqq",
]
#: Skipped, and each for its own reason: a browser is mid-write, Windows owns
#: it, and the third is already where it belongs.
AWKWARD = ["big_video.mkv.crdownload", "desktop.ini"]

SCRATCH = pathlib.Path("data/gate-organize")


def _ok(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def build_scratch() -> pathlib.Path:
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    for name in [*MESSY, *AWKWARD]:
        (SCRATCH / name).write_text(f"contents of {name}", encoding="utf-8")
    # An existing folder with something in it: organising must not re-sort
    # what it sorted last time, and undo must not disturb this.
    (SCRATCH / "Documents").mkdir()
    (SCRATCH / "Documents" / "invoice_march.pdf").write_text("older", encoding="utf-8")
    return SCRATCH.resolve()


def snapshot(root: pathlib.Path) -> dict[str, str]:
    """Every file under `root`, by path relative to it, with its contents."""
    return {
        str(p.relative_to(root)): p.read_text(encoding="utf-8", errors="replace")
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


async def main() -> int:
    handshake = pathlib.Path("data/.handshake").read_text().strip()
    try:
        token = str(json.loads(handshake)["token"])
    except (json.JSONDecodeError, KeyError, TypeError):
        token = handshake

    root = build_scratch()
    before = snapshot(root)
    print(f"scratch folder: {root}")
    print(f"  {len(before)} files, including {len(AWKWARD)} that must not move\n")

    async with websockets.connect(
        "ws://127.0.0.1:8765/rpc",
        additional_headers={"Authorization": f"Bearer {token}"},
        max_size=None,
    ) as ws:
        counter = [0]
        pending: dict[int, asyncio.Future[dict]] = {}
        confirms: asyncio.Queue[dict] = asyncio.Queue()
        completions: asyncio.Queue[dict] = asyncio.Queue()
        results: asyncio.Queue[dict] = asyncio.Queue()

        async def pump() -> None:
            async for raw in ws:
                message = json.loads(raw)
                if "id" in message and message["id"] in pending:
                    pending.pop(message["id"]).set_result(message)
                elif message.get("method") == "confirm.request":
                    await confirms.put(message["params"])
                elif message.get("method") == "tool.result":
                    await results.put(message["params"])
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

        async def ask(text: str) -> tuple[dict, dict]:
            """Say it, approve the one dialog, wait for the turn to finish.

            Through `chat.send` rather than a direct tool call, the way
            `gate_delete.py` does it — there is no RPC that runs a tool, and
            adding one for a gate would be testing a path the product does not
            have. The model choosing `organize_folder` from the description is
            part of what is being accepted.

            Its own session, never the user's — `chat.send` with no
            `session_id` continues whatever conversation was most recently
            active, which is how `gate_permission_modes.py` once put real
            confirmation dialogs in front of Eyaas mid-task.
            """
            session = (await call("chat.new"))["session_id"]
            started = await call(
                "chat.send", {"text": text, "session_id": session, "spoken": False}
            )
            turn_id = started["turn_id"]

            request = await asyncio.wait_for(confirms.get(), timeout=120)
            await call(
                "confirm.respond",
                {"request_id": request["request_id"], "approved": True},
            )
            outcome = await asyncio.wait_for(results.get(), timeout=180)
            while True:
                done = await asyncio.wait_for(completions.get(), timeout=180)
                if done.get("turn_id") == turn_id:
                    break
            return (outcome, request)

        failures = 0
        try:
            # ── 1. the plan is sane, and it is one confirmation ───────────
            print("1. Organising")
            result, request = await ask(
                f"organise the folder {root} by type"
            )
            print(f"   she called: {result['tool']}")
            if result["tool"] != "organize_folder":
                print("   FAIL  she reached for the wrong tool")
                return 1
            preview = request.get("preview") or {}
            print("   confirmations raised: 1")
            print(f"   preview: {preview.get('count')} moves into {preview.get('folders')}")
            print(f"   {result['summary']}")

            extra = 0
            while not confirms.empty():
                confirms.get_nowait()
                extra += 1
            one_dialog = extra == 0
            print(f"   {_ok(one_dialog)}  one confirmation, not one per file")
            failures += 0 if one_dialog else 1

            described = (
                preview.get("kind") == "move_plan"
                and preview.get("count") == len(MESSY)
                and bool(preview.get("moves"))
            )
            print(
                f"   {_ok(described)}  the confirmation described the batch "
                f"(§7.2: include the full file list)"
            )
            failures += 0 if described else 1

            after = snapshot(root)
            sane = (
                (root / "Documents" / "invoice_march (1).pdf").exists()
                and (root / "Images" / "holiday.png").exists()
                and (root / "Archives" / "backup.zip").exists()
                and (root / "big_video.mkv.crdownload").exists()
                and (root / "desktop.ini").exists()
                and (root / "Documents" / "invoice_march.pdf").read_text(
                    encoding="utf-8"
                ) == "older"
            )
            print(f"   files now: {len(after)} (was {len(before)})")
            print(
                f"   {_ok(sane)}  plan is sane: kinds grouped, part-file and "
                f"desktop.ini untouched, nothing overwritten"
            )
            failures += 0 if sane else 1

            # ── 2. undo restores exactly ──────────────────────────────────
            print("\n2. Undoing")
            undo_result, _ = await ask("undo that, put the files back")
            print(f"   she called: {undo_result['tool']}")
            print(f"   {undo_result['summary']}")

            restored = snapshot(root)
            exact = restored == before
            print(f"   {_ok(exact)}  undo restores exactly")
            if not exact:
                missing = sorted(set(before) - set(restored))
                added = sorted(set(restored) - set(before))
                changed = sorted(
                    k for k in set(before) & set(restored) if before[k] != restored[k]
                )
                for label, items in (
                    ("missing", missing),
                    ("unexpected", added),
                    ("altered", changed),
                ):
                    if items:
                        print(f"        {label}: {items[:6]}")
            failures += 0 if exact else 1

            print(f"\nGATE {'PASSED' if failures == 0 else f'FAILED ({failures})'}")
            return 0 if failures == 0 else 1
        finally:
            task.cancel()
            shutil.rmtree(SCRATCH, ignore_errors=True)


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except (OSError, WebSocketException) as exc:
        print(f"Could not reach the sidecar: {exc}\nStart it with: npm run sidecar")
        raise SystemExit(2) from exc
