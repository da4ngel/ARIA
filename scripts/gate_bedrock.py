"""Amazon Bedrock, end to end, against the real endpoint.

    python scripts/gate_bedrock.py
    python scripts/gate_bedrock.py --region eu-west-2
    python scripts/gate_bedrock.py --model anthropic.claude-3-5-haiku-20241022-v1:0

**Needs no sidecar and no Electron.** It drives `BedrockProvider` directly,
because everything it is checking sits below the RPC layer — and because the
three things most likely to be wrong cannot be reached from a conversation:

1. **The signature.** `providers/sigv4.py` is hand-written stdlib. Its unit
   tests check the canonical request against AWS's published specification,
   which proves the string is built correctly and proves nothing whatever about
   whether AWS agrees. **Only a real request can do that**, and a signing bug
   is indistinguishable from a mistyped key.
2. **The framing.** Bedrock is the only provider here that answers in binary
   (`vnd.amazon.eventstream`) rather than SSE. The decoder is tested against
   frames this project builds itself, which is better than nothing and is not
   the same as a frame AWS actually sent.
3. **The Converse mapping.** System prompts leave the conversation, tool
   results arrive as *user* turns, and roles must alternate. Getting any of it
   wrong returns `ValidationException` with a message that names none of it.

Nothing here is scored out of ten and nothing is asserted about the *content*
of a reply — a model saying something sensible is not what is under test. What
is under test is whether the bytes go out correctly and come back parseable.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# A gate that dies two thirds of the way through on a cp1252 console still
# prints something that looks like a result. `eval_quality.py` lost a whole
# hallucination-suite run to exactly that.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

from sidecar.providers import bedrock
from sidecar.providers.base import (
    ChatMessage,
    GenerationOptions,
    ProviderError,
    Role,
)
from sidecar.providers.discovery import parse_bedrock

RULE = "=" * 72

#: Small, cheap, and it calls tools. Overridable, because which models an
#: account has been granted differs per account and per region.
#:
#: **The `us.` prefix is an inference profile, not a typo.** The bare
#: `anthropic.claude-*` id has no on-demand throughput and returns a 404 or
#: an inference-profile error. The first version of this constant named a
#: bare id and a model that had since reached end of life — both found by
#: running it.
DEFAULT_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name."}},
            "required": ["city"],
        },
    },
}


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default=None, help="AWS region to test against.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Bedrock model id.")
    args = parser.parse_args()

    if args.region:
        bedrock.set_region(args.region)

    failures: list[str] = []
    observed: list[str] = []

    credentials = bedrock.load_credentials()
    print(RULE)
    print("0. WHAT IS CONFIGURED")
    print(RULE)
    print(f"    region:     {bedrock.current_region()}")
    print(f"    credential: {credentials.kind}")
    print(f"    model:      {args.model}")

    if not credentials.usable:
        # Not a failure. There is nothing to test, and saying "FAILED" about an
        # absent key would send someone hunting a bug that is not there.
        print()
        print("    SKIPPED  no Bedrock credential is stored.")
        print("    Add one in Settings, or from a Python shell:")
        print("        from sidecar.providers.credentials import CredentialKey, set_key")
        print('        set_key(CredentialKey.BEDROCK, "<your Bedrock API key>")')
        print()
        print("GATE SKIPPED")
        return 0

    provider = bedrock.BedrockProvider()
    try:
        # ── 1. the signature, against the control plane ──────────────
        print()
        print(RULE)
        print("1. THE SIGNATURE IS ACCEPTED (ListFoundationModels)")
        print(RULE)
        models: dict = {}
        try:
            models = await bedrock.fetch_control("/foundation-models")
            count = len(models.get("modelSummaries", []))
            print(f"    PASS  AWS accepted the credential — {count} models listed")
        except Exception as exc:  # noqa: BLE001 — the whole point is to report it
            # A 403 here can mean the credential is fine and merely not allowed
            # to *list*. That is a real and common configuration, so it is
            # reported rather than scored, and step 2 is what settles it.
            if "403" in str(exc):
                observed.append("1. listing is not permitted for this credential")
                print(f"    OBSERVED  403 on listing — {exc}")
                print("    Not necessarily wrong: a key scoped to running models")
                print("    may not be allowed to enumerate them. Step 2 decides.")
            else:
                failures.append(f"1. control plane refused the request: {exc}")
                print(f"    FAIL  {exc}")

        # ── 2. discovery's filters, on the real payload ──────────────
        if models:
            print()
            print(RULE)
            print("2. THE FILTERS KEEP SOMETHING USABLE")
            print(RULE)
            try:
                profiles = await bedrock.fetch_control("/inference-profiles")
            except Exception as exc:  # noqa: BLE001
                profiles = {}
                print(f"    (no inference profiles: {exc})")
            found = parse_bedrock(models, profiles)
            print(f"    {len(found)} streamable text models after filtering")
            for info in found[:8]:
                print(f"      {info.id}  —  {info.label}")
            if len(found) > 8:
                print(f"      ... and {len(found) - 8} more")
            if not found:
                failures.append("2. every model was filtered out")
                print("    FAIL  nothing survived the filters")
            else:
                print("    PASS  the picker would have something in it")

        # ── 3. a real streamed reply ─────────────────────────────────
        print()
        print(RULE)
        print("3. A REAL CONVERSE STREAM (signing + framing + mapping)")
        print(RULE)
        print("    This is the line that matters. It proves SigV4 against a")
        print("    POST body, the binary event-stream decoder, and the")
        print("    Converse message mapping, all at once.")
        reply: list[str] = []
        try:
            async for delta in provider.stream_chat(
                [
                    ChatMessage(role=Role.SYSTEM, content="Answer in one short sentence."),
                    ChatMessage(role=Role.USER, content="What is the capital of Australia?"),
                ],
                model=args.model,
                options=GenerationOptions(max_tokens=100),
            ):
                if delta.text:
                    reply.append(delta.text)
            answer = "".join(reply).strip()
            print(f"    reply: {answer!r}")
            if answer:
                print("    PASS  a real reply streamed back and decoded")
            else:
                failures.append("3. the stream decoded but produced no text")
                print("    FAIL  no text came back")
        except ProviderError as exc:
            failures.append(f"3. streaming failed: {exc}")
            print(f"    FAIL  {exc}")

        # ── 4. tools ─────────────────────────────────────────────────
        print()
        print(RULE)
        print("4. A TOOL CALL SURVIVES THE ROUND TRIP")
        print(RULE)
        print("    Converse renames every field of a tool schema and streams")
        print("    the arguments back as JSON fragments. ARIA offers 42 tools,")
        print("    so a provider that cannot do this is of little use here.")
        try:
            calls = []
            async for delta in provider.stream_chat(
                [ChatMessage(role=Role.USER, content="What is the weather in Colombo?")],
                model=args.model,
                options=GenerationOptions(max_tokens=300),
                tools=[WEATHER_TOOL],
            ):
                calls.extend(delta.tool_calls)
            if calls:
                call = calls[0]
                print(f"    tool: {call.name}  args: {call.arguments}")
                if call.name == "get_weather" and call.arguments.get("city"):
                    print("    PASS  the call reassembled with its arguments intact")
                else:
                    failures.append("4. the tool call came back malformed")
                    print("    FAIL  the arguments did not reassemble")
            else:
                # Not scored as a failure: a model choosing not to call a tool
                # is a model behaviour, and this gate measures transport.
                observed.append("4. the model answered without calling the tool")
                print("    OBSERVED  no tool call — the transport is untested here.")
                print("    Re-run, or try --model with a stronger one.")
        except ProviderError as exc:
            failures.append(f"4. the tool round trip failed: {exc}")
            print(f"    FAIL  {exc}")
    finally:
        await provider.aclose()

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
