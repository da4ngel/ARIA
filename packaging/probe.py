"""Diagnose the frozen-only "cannot load module more than once per process".

**Not shipped.** A throwaway entry point, frozen with `probe.spec`, that does
what the sidecar does — import numpy, then onnxruntime, then faster-whisper —
and prints the full traceback the real code swallows into a `log.warning`.

The message turns out to come from **numpy**, not from ctranslate2: the string
is compiled into `numpy/_core/_multiarray_umath.pyd`, and `numpy/_core/__init__.py`
re-raises it verbatim. So the question is not "why does ctranslate2 load twice"
but "what initialises numpy's C extension a second time".
"""

from __future__ import annotations

import sys
import traceback


def show(label: str, fn) -> None:  # noqa: ANN001
    print(f"\n=== {label} ===", flush=True)
    try:
        fn()
        print("  ok", flush=True)
    except BaseException:  # noqa: BLE001 — the traceback is the whole point
        traceback.print_exc()
        sys.stdout.flush()


def main() -> None:
    print("frozen:", getattr(sys, "frozen", False), flush=True)
    print("_MEIPASS:", getattr(sys, "_MEIPASS", None), flush=True)
    print("sys.path:", flush=True)
    for entry in sys.path:
        print("   ", entry, flush=True)

    def numpy_first() -> None:
        import numpy

        print("  numpy", numpy.__version__, "from", numpy.__file__, flush=True)

    show("1. import numpy", numpy_first)

    def numpy_modules() -> None:
        hits = sorted(n for n in sys.modules if n.startswith("numpy") and "multiarray" in n)
        print("  numpy multiarray modules in sys.modules:", hits, flush=True)

    show("2. what numpy registered", numpy_modules)

    show("3. import onnxruntime", lambda: __import__("onnxruntime"))
    show("4. import ctranslate2", lambda: __import__("ctranslate2"))
    show("5. import faster_whisper", lambda: __import__("faster_whisper"))
    show("6. import openwakeword", lambda: __import__("openwakeword"))
    show("7. import sklearn", lambda: __import__("sklearn"))
    show("8. import scipy", lambda: __import__("scipy"))
    show("9. import av", lambda: __import__("av"))

    def reimport() -> None:
        # The suspicion: something drops numpy from sys.modules and re-imports
        # it, which numpy 2.x refuses outright.
        import numpy  # noqa: F401

        for name in [n for n in list(sys.modules) if n.startswith("numpy")]:
            del sys.modules[name]
        import numpy  # noqa: F401, F811

    show("10. deliberately re-import numpy (expected to fail)", reimport)

    print("\ndone", flush=True)


if __name__ == "__main__":
    main()
