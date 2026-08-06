"""Long-conversation contamination soak — the Phase 1 regression, restated.

The battery in `eval_quality.py` is single-turn or short-history. The bug that
started all of this was neither: `qwen3.5:4b` invented a leaking roof and mold,
and then referenced that fiction for 25 straight turns, because its own reply
re-entered the prompt as history and became something to be consistent with.

A fixture cannot reproduce that. It needs a real conversation where the model's
output feeds back, which is what this drives — through the actual
`ConversationService`, roll-up and all.

    python scripts/soak_conversation.py                       # default local model
    python scripts/soak_conversation.py --model qwen3.5:4b
    python scripts/soak_conversation.py --turns 40

After each turn, every capitalised noun and number in the reply is checked
against everything the *user* has said. A token that appears in no user turn and
in no earlier assistant turn is newly introduced by the model; if it then
reappears in a later reply, the model is building on its own invention. That
second event is the actual Phase 1 failure, and it is reported separately.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("ARIA_WARM_ON_STARTUP", "false")
os.environ.setdefault("ARIA_DATA_DIR", tempfile.mkdtemp(prefix="aria-soak-"))

from sidecar.core.conversation import ConversationService
from sidecar.core.router import Router, RoutingBias
from sidecar.memory.db import Database
from sidecar.memory.messages import ConversationStore
from sidecar.providers import catalog
from sidecar.providers.health import HealthTracker
from sidecar.providers.ollama import OllamaProvider
from sidecar.rpc.events import Event, EventBus

# Ordinary chat with no factual anchors, which is the point: nothing here
# licenses the model to introduce a specific place, person, object or number.
# The Phase 1 transcript looked exactly like this before it went wrong.
SCRIPT: list[str] = [
    "hey",
    "not much, just settling in for the evening",
    "what do you think about working late?",
    "yeah I've been doing that a lot lately",
    "name a colour",
    "why that one?",
    "do you like music?",
    "what kind of thing would you listen to",
    "I've been tired this week",
    "any advice?",
    "that's fair",
    "tell me something interesting",
    "huh, I didn't know that",
    "what else",
    "do you ever get bored?",
    "what would you do if you did",
    "say hello",
    "how are things on your end?",
    "I might go for a walk later",
    "it's been raining though",
    "what's your favourite season",
    "mine too",
    "anything you want to ask me?",
    "sure, go ahead",
    "that's a good question",
    "I'd say probably not",
    "what were we talking about?",
    "before that",
    "okay, last one",
    "goodnight",
]

# The first word of a sentence is capitalised by grammar, not because it names
# anything. Counting those made the detector report "Make", "Did", "Enjoy" and
# "Have" as invented facts — 11 false alarms in a 30-turn run, which is worse
# than no detector at all, because it buries the real ones.
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
_PROPER_NOUN = re.compile(r"\b[A-Z][a-z]{2,}\b")
_NUMBER = re.compile(r"\b\d[\d,.]*\b")

# Capitalised mid-sentence but not naming anything specific.
_STOPWORDS = {
    "i", "aria", "eyaas", "windows", "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday", "january", "february", "march", "april", "may",
    "june", "july", "august", "september", "october", "november", "december",
}


def concrete_tokens(text: str) -> set[str]:
    """Proper nouns and numbers, ignoring words capitalised only by position."""
    found: set[str] = set()
    for sentence in _SENTENCE_SPLIT.split(text):
        words = sentence.split()
        if not words:
            continue
        # Skip the first word: its capital carries no information.
        body = " ".join(words[1:])
        for raw in _PROPER_NOUN.findall(body):
            token = raw.lower()
            if token not in _STOPWORDS:
                found.add(token)
        found.update(_NUMBER.findall(sentence))
    return found


def novel_tokens(reply: str, said_before: set[str]) -> list[str]:
    """Concrete tokens in `reply` that nobody has grounded yet."""
    return sorted(concrete_tokens(reply) - said_before)


class Recorder(EventBus):
    """Collects turn completions without needing a socket."""

    def __init__(self) -> None:
        super().__init__()
        self.completed: list[dict[str, Any]] = []

    async def broadcast(self, method: Event | str, params: dict[str, Any]) -> None:
        if str(method) == Event.TURN_COMPLETE:
            self.completed.append(params)


async def run(model_id: str, turns: int) -> int:
    from sidecar.config import get_settings

    settings = get_settings()
    settings.ensure_dirs()
    db = Database(settings.db_path)
    db.migrate()

    provider = OllamaProvider(settings.ollama_url)
    bus = Recorder()
    health = HealthTracker()
    service = ConversationService(
        store=ConversationStore(db),
        provider=provider,
        bus=bus,
        model=model_id,
        num_ctx=settings.num_ctx,
        context_token_budget=settings.context_token_budget,
        providers={str(catalog.ProviderName.OLLAMA): provider},
        # FASTEST keeps every turn local: this is a test of one model's
        # behaviour over a long conversation, not of the router.
        router=Router(health, RoutingBias.FASTEST),
        health=health,
        selected_model=model_id,
    )

    print(f"=== soak: {model_id}, {turns} turns ===\n")

    said: set[str] = set()          # everything the user has written
    introduced: dict[str, int] = {}  # model invention -> turn it first appeared
    carried: list[tuple[int, str, int]] = []  # (turn, token, first_seen_turn)
    session: str | None = None

    for index, message in enumerate(SCRIPT[:turns], start=1):
        # Everything the user wrote is grounded, however they capitalised it.
        said.update(w.strip(".,?!'\"").lower() for w in message.split())

        started = await service.send(message, session)
        session = started.session_id
        for _ in range(2400):
            if bus.completed:
                break
            await asyncio.sleep(0.05)
        if not bus.completed:
            print(f"  turn {index}: no reply, aborting")
            break

        reply = bus.completed.pop()["full_text"]
        flat = reply.replace("\n", " ⏎ ")

        # Anything the model already said is fair game to repeat; only tokens
        # nobody has ever grounded are inventions.
        novel = novel_tokens(reply, said | set(introduced))
        repeats = [t for t in introduced if re.search(rf"\b{re.escape(t)}\b", reply, re.I)]

        print(f"[{index:>2}] > {message}")
        print(f"     < {flat[:150]}")
        if novel:
            print(f"     ** introduced: {', '.join(novel)}")
        for token in repeats:
            carried.append((index, token, introduced[token]))
            print(f"     !! CARRIED FORWARD: {token!r} (invented at turn {introduced[token]})")
        for token in novel:
            introduced.setdefault(token, index)
        print()

    print("=" * 70)
    print(f"tokens the model introduced : {len(introduced)}")
    print(f"of those, reused later      : {len(carried)}")
    print(
        "\nThese are candidates for review, NOT a verdict. The script cannot\n"
        "tell an invention about Eyaas ('your leaking roof') from a fact the\n"
        "model was asked for and then correctly recalled ('the Great Barrier\n"
        "Reef', after 'tell me something interesting'). Only the first is the\n"
        "Phase 1 bug. Read the transcript above and judge which you are seeing."
    )
    for turn, token, first in carried:
        print(f"  turn {turn:>2}: {token!r} — introduced at turn {first}")

    await service.shutdown()
    await provider.aclose()
    db.close()
    return len(carried)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=None, help="Catalog id. Defaults to the local default.")
    parser.add_argument("--turns", type=int, default=len(SCRIPT))
    args = parser.parse_args()

    model_id = args.model
    if model_id is None:
        probe = OllamaProvider()
        try:
            pulled = await probe.list_models()
        finally:
            await probe.aclose()
        model_id = catalog.default_local(pulled).id

    # Always exits 0: the reuse count is a review aid, not a pass/fail signal,
    # and wiring it to an exit code would invite someone to "fix" the model by
    # making it stop remembering things.
    await run(model_id, args.turns)


if __name__ == "__main__":
    asyncio.run(main())
