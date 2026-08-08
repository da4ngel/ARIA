"""Can she find the app you meant? Resolves only — nothing is launched.

    python scripts/gate_apps.py

Every name here is written the way a person says it out loud, including the
two typos that turned up in real use. **Nothing is started**, so this can run
as often as you like without burying the screen in windows.

The number to beat is 20 of the 24 installed names, which is what the previous
three-pass matcher managed.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sidecar.tools.apps import _INDEX, _resolve, rank

# (said, expected label or None if it should be a website, note)
Case = tuple[str, str | None, str]

CASES: list[Case] = [
    # Ordinary names, the easy majority.
    ("photoshop", "Photoshop", "the registry entry, which is the real exe"),
    ("capcut", "CapCut", ""),
    ("brave", "Brave", ""),
    ("word", "Word", ""),
    ("excel", "Excel", ""),
    ("powerpoint", "PowerPoint", ""),
    ("task manager", "Task Manager", ""),
    ("control panel", "Control Panel", ""),
    ("settings", "Settings", ""),
    ("paint", "Paint", ""),
    ("snipping tool", "Snipping Tool", ""),
    ("claude", "Claude", ""),
    ("steam", "Steam", ""),
    ("file explorer", "File Explorer", ""),
    ("camera", "Camera", ""),
    ("clock", "Clock", ""),
    ("character map", "Character Map", ""),
    ("zoom", "Zoom Workplace", ""),
    ("notion", "Notion", ""),
    ("calculator", "Calculator", ""),
    # The four that used to fail.
    ("7 zip", "7-Zip File Manager", "punctuation"),
    ("seven zip", "7-Zip File Manager", "number word"),
    ("photoshp", "Photoshop", "typo"),
    ("youtbe music", "YouTube Music", "typo; the app is installed"),
    # Regressions that already bit once each.
    ("youtube", None, "the site, NOT the YouTube Music app"),
    ("youtube music", "YouTube Music", "the installed app, not the site"),
    ("spotify", "Spotify", "the app, not the web player"),
    ("calendar", "Calendar", "not Calendar (Microsoft 365)"),
    # A kind of program, not a name. Answered by whatever the user set as
    # their default — "browser" used to score 0.88 against LockDown Browser.
    ("browser", "Brave", "the default browser, not a name that contains it"),
    ("the browser", "Brave", "filler words stripped"),
    ("my email", "Outlook", "the default mail handler"),
    ("music", "Media Player", "the default .mp3 handler, not YouTube Music"),
    ("chrome", "chrome", "a real name still beats the category"),
    # Must not resolve to anything.
    ("qwertyuiop nonsense", "", "must miss"),
    # Punctuation that names a different product. Notepad++ is not installed
    # here, and `normalise` folded it to "notepad", which matched Notepad
    # exactly — so asking for one opened the other on every model tested.
    ("notepad++", "", "must miss; it is not Notepad"),
    ("notepad plus plus", "", "same, said out loud"),
    ("notepad", "Notepad", "and the real one still opens"),
]


async def main() -> int:
    entries = await _INDEX.entries()
    print(f"indexed {len(entries)} apps\n")

    right = wrong = 0
    for said, expected, note in CASES:
        entry = _resolve(said, entries)
        got = entry.label if entry else None
        kind = str(entry.launch) if entry else "-"

        if expected == "":
            ok = entry is None
        elif expected is None:
            ok = entry is not None and kind == "browser"
        else:
            ok = got == expected

        right += ok
        wrong += not ok
        mark = "ok " if ok else "BAD"
        shown = f"{got} [{kind}]" if entry else "(not found)"
        print(f"  {mark} {said:22} -> {shown:38} {note}")
        if not ok:
            near = ", ".join(f"{s:.2f} {e.label}" for s, e in rank(said, entries)[:3])
            print(f"      wanted {expected!r}; closest were {near}")

    print(f"\n{right}/{len(CASES)} correct   (previous matcher: 20/24 installed)")
    return 0 if wrong == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
