"""Everything she can do to the machine, and what it costs to do it.

Importing this package registers every tool. `main.py` imports it once at
startup; nothing else should need to, because `registry.get` is the only
supported way to reach a tool (CLAUDE.md rule 4).
"""

from sidecar.tools import apps, files, system

__all__ = ["apps", "files", "system"]
