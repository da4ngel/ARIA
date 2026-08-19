"""Everything she can do to the machine, and what it costs to do it.

Importing this package registers every tool. `main.py` imports it once at
startup; nothing else should need to, because `registry.get` is the only
supported way to reach a tool (CLAUDE.md rule 4).

The imports below look unused and are not: the `@tool` decorator runs on
import, and dropping one silently removes that tool from the registry — which
is exactly what happened to `finder` once, leaving the model unable to search
for files while every test still passed.
"""

from sidecar.tools import apps as apps
from sidecar.tools import ask as ask
from sidecar.tools import browser as browser
from sidecar.tools import clipboard as clipboard
from sidecar.tools import files as files
from sidecar.tools import finder as finder
from sidecar.tools import memory as memory
from sidecar.tools import organize as organize
from sidecar.tools import research as research
from sidecar.tools import screen as screen
from sidecar.tools import system as system

__all__ = [
    "apps",
    "ask",
    "browser",
    "clipboard",
    "files",
    "finder",
    "memory",
    "organize",
    "research",
    "screen",
    "system",
]
