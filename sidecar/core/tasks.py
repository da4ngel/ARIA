"""Fire-and-forget work that must not take the process down with it.

Two rules, both learned the hard way elsewhere in this codebase:

`asyncio.create_task` keeps only a **weak** reference to the task. A task
nobody holds can be collected mid-flight, and the symptom is work that
silently never happens. The set below is the strong reference.

And a background job that raises must log rather than propagate. These are
side errands — a model listing, a warm-up — and none of them is worth
interrupting a conversation for.
"""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any

import structlog

log = structlog.get_logger(__name__)

_RUNNING: set[asyncio.Task[Any]] = set()


def spawn(coro: Coroutine[Any, Any, Any], name: str) -> asyncio.Task[Any]:
    """Run `coro` detached. Failures are logged against `name`, never raised."""

    async def _guarded() -> None:
        try:
            await coro
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — an errand must not kill the caller
            log.warning("background.failed", task=name, error=str(exc))

    task = asyncio.create_task(_guarded(), name=name)
    _RUNNING.add(task)
    task.add_done_callback(_RUNNING.discard)
    return task
