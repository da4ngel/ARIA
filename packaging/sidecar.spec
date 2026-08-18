# PyInstaller spec for the sidecar (BUILD_SPEC §9 Phase 9).
#
#     pyinstaller packaging/sidecar.spec --noconfirm
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

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

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
    # **`ctranslate2` is deliberately NOT listed.** Naming it here makes
    # PyInstaller register the frozen module *and* leave the on-disk
    # `_ext.cp311-win_amd64.pyd` reachable, so the extension is loaded twice
    # under two names and Python raises `cannot load module more than once
    # per process` — which killed speech recognition and the wake word in an
    # otherwise working bundle. PyInstaller ships its own ctranslate2 hook;
    # letting it do the work is the fix. Found by running the bundle.
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

# **`ctranslate2` is deliberately not collected here.** Adding it produced a
# bundle that built cleanly and then failed at runtime with
# `cannot load module more than once per process` — faster-whisper could not
# start, so speech recognition and the wake word were both dead in the
# packaged app while everything else worked. PyInstaller already ships a hook
# for it; collecting the DLLs a second time puts the same native module at two
# paths and loading it twice is what that error is. Found by running the
# bundle, not by building it.
binaries = collect_dynamic_libs("onnxruntime")

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

coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="aria-sidecar",
)
