# Diagnostic bundle for the frozen-only numpy re-initialisation failure.
#
# **Not shipped, and not part of the build.** Mirrors `sidecar.spec`'s
# collection decisions as closely as a single-file entry point can, so that
# whatever it reproduces is the same thing the real bundle does.
#
#     pyinstaller packaging/probe.spec --noconfirm
#     packaging/dist/aria-probe/aria-probe.exe

from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
)

ROOT = Path(SPECPATH).parent  # noqa: F821

hidden = [
    "onnxruntime",
    "onnxruntime.capi",
    "onnxruntime.capi._pybind_state",
    "openwakeword",
    "faster_whisper",
    # The fix under test: PyInstaller 6.10's numpy hook does not understand
    # numpy 2.4's layout and leaves `numpy._core._exceptions` (and most of
    # `numpy/_core`) out entirely.
    *collect_submodules("numpy"),
]

datas = collect_data_files("sqlite_vec")
binaries = collect_dynamic_libs("onnxruntime")

a = Analysis(  # noqa: F821
    [str(ROOT / "packaging" / "probe.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=["torch", "pytest", "mypy", "ruff", "IPython", "tkinter", "matplotlib"],
    noarchive=False,
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="aria-probe",
    debug=False,
    strip=False,
    upx=False,
    # A console, unlike the real bundle — the whole point is to read stdout.
    console=True,
)

coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="aria-probe",
)
