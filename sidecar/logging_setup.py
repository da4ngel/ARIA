"""structlog configuration. JSON to file, pretty to console in dev.

CLAUDE.md rule 9: structured logging only, never ``print()``. Module is named
``logging_setup`` rather than ``logging`` so it cannot shadow the stdlib.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import structlog

_SHARED_PROCESSORS: list[structlog.typing.Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.UnicodeDecoder(),
]


def _file_handler(log_path: Path, level: int) -> logging.Handler:
    """JSON lines to ``data/logs/sidecar.log``. Electron tails this file."""
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=_SHARED_PROCESSORS,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
        )
    )
    return handler


def _console_handler(dev: bool, level: int) -> logging.Handler:
    """Pretty in dev, JSON in production — stdout is piped into the same log file."""
    renderer: structlog.typing.Processor = (
        structlog.dev.ConsoleRenderer(colors=False)
        if dev
        else structlog.processors.JSONRenderer()
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=_SHARED_PROCESSORS,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.format_exc_info,
                renderer,
            ],
        )
    )
    return handler


def configure_logging(log_path: Path, *, dev: bool = False, level: str = "INFO") -> None:
    """Install the structlog + stdlib logging bridge. Idempotent."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    structlog.configure(
        processors=[
            *_SHARED_PROCESSORS,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    root = logging.getLogger()
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(_file_handler(log_path, numeric_level))
    root.addHandler(_console_handler(dev, numeric_level))
    root.setLevel(numeric_level)

    # uvicorn installs its own handlers; force everything through ours.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True
