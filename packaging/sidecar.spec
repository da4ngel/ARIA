# PyInstaller spec for the sidecar (BUILD_SPEC §9 Phase 9).
#
#     npm run dist:sidecar
#
# which is:
#
#     pyinstaller packaging/sidecar.spec --noconfirm
#         --distpath packaging/dist --workpath packaging/build
#
# **The paths are not optional.** PyInstaller defaults to `./dist` and
# `./build` relative to the working directory, and `./dist` is where
# electron-builder puts the installer — two different things under one
# name. `npm run dist:sidecar` passes them; run it that way.
#
# **`--onedir`, not `--onefile`**, which §9 already specifies and which is not
# a preference: a onefile build unpacks itself to a temp directory on every
# launch, and this bundle carries onnxruntime, ctranslate2 and the Kokoro
# weights. That is hundreds of megabytes of extraction in front of a process
# Electron expects to answer within seconds.
#
# **The hidden imports are the whole difficulty.** PyInstaller finds imports by
# reading source; every one listed below is reached in a way static analysis
# cannot see — a C extension loaded by name, a plugin registry, or a lazy
# import inside a function. Each has been added because it was *missing*, not
# on principle.
#
# `torch` is absent and must stay absent (CLAUDE.md rule 3): it adds ~2.5GB
# and DLL hell on Windows, and every library choice in §4 exists to avoid it.

from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
)

# The spec is executed with `SPECPATH` set to its own directory; the repo is
# one level up. `__file__` is not defined in a spec file.
ROOT = Path(SPECPATH).parent  # noqa: F821 — injected by PyInstaller

hidden = [
    # sqlite-vec is a loadable SQLite extension: `sqlite_vec.load(conn)` hands
    # SQLite a path to a .dll. Nothing imports the binary itself, so only the
    # data-file collection below actually ships it.
    "sqlite_vec",
    # onnxruntime is reached through kokoro-onnx and openwakeword, both of
    # which construct sessions from strings rather than importing providers.
    "onnxruntime",
    "onnxruntime.capi",
    "onnxruntime.capi._pybind_state",
    # **The bundle's speech failure was numpy, not ctranslate2.**
    #
    # For weeks this bundle raised `cannot load module more than once per
    # process` and the blame sat on ctranslate2. It never belonged there. That
    # string is compiled into `numpy/_core/_multiarray_umath.pyd` and re-raised
    # verbatim by `numpy/_core/__init__.py`; it is numpy's own guard against a
    # C extension being initialised twice.
    #
    # What actually happened: PyInstaller 6.10's numpy hook does not understand
    # numpy 2.4's layout and left `numpy._core._exceptions` out of the bundle
    # entirely. The *first* `import numpy` therefore died with
    # `ModuleNotFoundError: No module named 'numpy._core._exceptions'` — after
    # the C extension had already initialised — and numpy was evicted from
    # `sys.modules`. Every later import was a *second* initialisation, which
    # numpy refuses. **The famous error was the symptom of the second attempt;
    # nobody ever saw the first, because `main.py` logged `str(exc)` without a
    # traceback and the shipped exe has no console.**
    #
    # `collect_submodules` rather than naming `_exceptions` alone: the hook is
    # simply older than the library, so the next missing submodule would fail
    # the same way. Same for scipy, which is reached through sklearn from
    # openwakeword and was missing `scipy._cyutility`.
    *collect_submodules("numpy"),
    *collect_submodules("scipy"),
    # Reached by name from `providers/tts.py` and `providers/wakeword.py`.
    "kokoro_onnx",
    "openwakeword",
    # Windows shell APIs used by `rpc/handlers.py`'s recycle-bin delete and by
    # `tools/apps.py` — pywin32 submodules are imported inside functions, so
    # the analyser never sees them.
    "win32com.shell.shell",
    "win32com.shell.shellcon",
    "win32timezone",  # pywin32 pulls this at runtime, never in source
    # Document parsers, all imported inside `memory/indexer.py`'s readers.
    "pypdf",
    "docx",
    "openpyxl",
    # Vision and screen capture, imported inside functions in `tools/screen.py`
    # and `core/attachments.py`.
    "PIL.Image",
    "mss",
    # Playwright's sync/async facade is imported lazily by `tools/browser.py`.
    "playwright.async_api",
    # keyring picks its backend at runtime from entry points.
    "keyring.backends.Windows",
]

datas = [
    # The SQL migrations are read from disk at startup, not embedded.
    (str(ROOT / "sidecar" / "memory" / "schema.sql"), "sidecar/memory"),
    *[
        (str(p), "sidecar/memory")
        for p in (ROOT / "sidecar" / "memory").glob("schema_*.sql")
    ],
]
# The .dll sqlite-vec loads by path, and onnxruntime's own native libraries.
datas += collect_data_files("sqlite_vec")

# **The Silero VAD weights faster-whisper ships as package data.**
# `providers/vad.py:92` calls `get_vad_model()`, which resolves
# `faster_whisper/assets/silero_vad.onnx` relative to its own `__file__`, and
# `stt.py:219` passes `vad_filter=True` for the same file. Nothing imports it,
# so static analysis cannot see it and the bundle shipped without it — which
# broke hands-free independently of the numpy fault below, and would have kept
# it broken after that was fixed.
datas += collect_data_files("faster_whisper")

# **Her voice drags in a whole text-processing stack, and all of it reads data
# files at import time.** `kokoro_onnx/config.json` was the first; behind it sit
# `csvw` -> `language_tags` -> `language_tags/data/json/index.json`, the espeak
# phonemiser and its DLLs, and Babel's locale tables. Every one of them fails as
# an *ImportError*, not a runtime error, so the whole of TTS is absent from the
# bundle if any single file is.
#
# Enumerated in one pass rather than discovered one rebuild at a time: import
# `kokoro_onnx` in the dev venv, diff `sys.modules`, and look for packages
# carrying non-.py files. That is worth remembering — each rebuild is five
# minutes, and this chain is five deep.
for _voice_package in (
    "kokoro_onnx",
    "espeakng_loader",  # 365 files, including the espeak-ng DLLs
    "phonemizer",
    "language_tags",
    "jsonschema",
    "jsonschema_specifications",
    "babel",  # locale tables, ~1000 .dat files
):
    datas += collect_data_files(_voice_package)

# `ctranslate2` needs no special handling. Two long comments used to stand here
# claiming it did — that naming it in `hiddenimports` or collecting its DLLs
# caused `cannot load module more than once per process`, and that PyInstaller
# ships a hook for it. **Both were wrong**, and they cost three separate
# attempts at the wrong library: there is no `hook-ctranslate2.py` in
# PyInstaller 6.10, and the error was never ctranslate2's. See `hidden` below.
# espeak-ng ships as DLLs beside its Python loader; `collect_data_files`
# takes the data but not the shared libraries.
binaries = collect_dynamic_libs("onnxruntime") + collect_dynamic_libs("espeakng_loader")

a = Analysis(  # noqa: F821
    [str(ROOT / "sidecar" / "main.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    # Never packaged. `torch` is rule 3; the rest are test and lint tooling
    # that would otherwise be pulled in through transitive imports.
    excludes=["torch", "pytest", "mypy", "ruff", "IPython", "tkinter", "matplotlib"],
    noarchive=False,
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="aria-sidecar",
    debug=False,
    strip=False,
    upx=False,  # UPX on onnxruntime's DLLs produces a bundle that will not load
    # **No console window.** §9's own `--noconsole`. The sidecar is a child of
    # Electron and its output already goes to `data/logs/sidecar.out.log`; a
    # terminal appearing behind the app on every launch is not a diagnostic,
    # it is a bug report waiting to happen.
    console=False,
)

# **A console twin, and it is the whole reason the numpy fault took weeks.**
#
# The shipped exe has no console, so a traceback raised before structlog is set
# up — or one swallowed into `log.warning(error=str(exc))` — goes nowhere at
# all. The *first* numpy failure, the one naming the actually-missing module,
# was never seen by anybody for exactly that reason.
#
# This shares every binary and data file with the real exe (COLLECT emits one
# `_internal/`), so it costs about a megabyte. Run it with `--selftest` to
# import every optional subsystem and print a full traceback per failure.
debug_exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="aria-sidecar-debug",
    debug=False,
    strip=False,
    upx=False,
    console=True,
)

coll = COLLECT(  # noqa: F821
    exe,
    debug_exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="aria-sidecar",
)
