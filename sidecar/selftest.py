"""Import every optional subsystem and say plainly which ones are broken.

**This exists because a packaging bug cost weeks that it should have cost
minutes.** The frozen bundle raised `cannot load module more than once per
process` and the blame sat on ctranslate2 for three attempts; the real cause
was a numpy submodule PyInstaller had left out, and the traceback naming it was
never once printed — `main.py` logged `str(exc)` with no `exc_info`, and the
shipped exe has no console to print to anyway.

So: one command that imports each thing the sidecar needs, in isolation, and
prints a **full traceback** for whatever fails.

    aria-sidecar-debug.exe --selftest      # the frozen bundle
    python -m sidecar.main --selftest      # the dev tree

It exits non-zero if anything required failed, which makes it usable as the
first line of the packaging acceptance gate. Optional subsystems (voice, the
browser) are reported but do not fail the run — a bundle without a microphone
is still a working assistant, and this must be able to say so rather than
refusing to distinguish.
"""

from __future__ import annotations

import importlib
import sys
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from typing import IO


@dataclass(frozen=True)
class Check:
    name: str
    run: Callable[[], object]
    #: A required check failing means the bundle is broken. An optional one
    #: failing means a feature is unavailable and should say so on screen.
    required: bool = True
    why: str = ""


def _import(module: str) -> Callable[[], object]:
    return lambda: importlib.import_module(module)


def _vad_asset() -> object:
    """The Silero weights faster-whisper ships as package data.

    Nothing imports this file, so PyInstaller cannot see it and the bundle
    shipped without it — hands-free was broken by this *independently* of the
    numpy fault, and would have stayed broken after that was fixed.
    """
    from pathlib import Path

    import faster_whisper

    asset = Path(faster_whisper.__file__).parent / "assets" / "silero_vad.onnx"
    if not asset.is_file():
        raise FileNotFoundError(
            f"{asset} is missing. The spec needs "
            f'`datas += collect_data_files("faster_whisper")`.'
        )
    return asset


def _sqlite_vec() -> object:
    """Loading the extension, not merely importing the wrapper — the wrapper is
    pure Python and imports fine without the .dll it exists to hand over."""
    import sqlite3

    import sqlite_vec

    conn = sqlite3.connect(":memory:")
    try:
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.execute("SELECT vec_version()").fetchone()
    finally:
        conn.close()
    return "loaded"


CHECKS: tuple[Check, ...] = (
    # The one that was actually broken. numpy first, because everything below
    # it imports numpy and a numpy failure disguises itself as their failure.
    Check("numpy", _import("numpy"), why="every audio path"),
    Check("sqlite-vec", _sqlite_vec, why="memory and file search"),
    Check("keyring", _import("keyring.backends.Windows"), why="API keys"),
    Check("pypdf", _import("pypdf"), why="reading PDFs"),
    Check("docx", _import("docx"), why="reading Word files"),
    Check("openpyxl", _import("openpyxl"), why="reading spreadsheets"),
    Check("PIL", _import("PIL.Image"), why="screenshots and image uploads"),
    Check("win32com.shell", _import("win32com.shell.shell"), why="recycle bin"),
    # Optional: a bundle missing these is degraded, not broken.
    Check("mss", _import("mss"), required=False, why="screen capture"),
    Check("onnxruntime", _import("onnxruntime"), required=False, why="wake word, voice"),
    Check("ctranslate2", _import("ctranslate2"), required=False, why="speech recognition"),
    Check("faster_whisper", _import("faster_whisper"), required=False, why="speech recognition"),
    Check("silero VAD asset", _vad_asset, required=False, why="hands-free"),
    Check("kokoro_onnx", _import("kokoro_onnx"), required=False, why="her voice"),
    Check("scipy", _import("scipy"), required=False, why="wake word (model mode)"),
    Check("openwakeword", _import("openwakeword"), required=False, why="wake word (model mode)"),
    Check("playwright", _import("playwright.async_api"), required=False, why="browser control"),
)


def run(out: IO[str] | None = None) -> int:
    """Run every check. Returns the process exit code."""
    stream: IO[str] = out or sys.stdout
    failures = 0
    degraded: list[str] = []

    print(f"python {sys.version.split()[0]}  frozen={getattr(sys, 'frozen', False)}", file=stream)
    if hasattr(sys, "_MEIPASS"):
        print(f"bundle  {sys._MEIPASS}", file=stream)  # noqa: SLF001
    print(file=stream)

    for check in CHECKS:
        tag = "     " if check.required else "opt  "
        try:
            check.run()
        except BaseException:  # noqa: BLE001 — the traceback is the deliverable
            mark = "FAIL" if check.required else "GONE"
            print(f"{tag}{mark}  {check.name} — {check.why}", file=stream)
            traceback.print_exc(file=stream)
            print(file=stream)
            if check.required:
                failures += 1
            else:
                degraded.append(check.name)
        else:
            print(f"{tag} ok   {check.name}", file=stream)

    print(file=stream)
    if failures:
        print(f"{failures} required subsystem(s) failed — this bundle is broken.", file=stream)
    elif degraded:
        print(
            f"Everything required works. Unavailable: {', '.join(degraded)}. "
            f"Typing, memory and tools are unaffected.",
            file=stream,
        )
    else:
        print("All subsystems present.", file=stream)
    return 1 if failures else 0
