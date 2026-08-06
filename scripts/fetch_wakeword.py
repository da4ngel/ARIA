"""Download the wake word weights into data/models/openwakeword.

    python scripts/fetch_wakeword.py

About 3.5MB of ONNX: the `hey_jarvis` model plus the melspectrogram and
embedding frontends it shares. Not vendored — same rule as the kokoro voice.

openWakeWord fetches the tflite copies alongside the ONNX ones and there is no
flag to stop it. They are removed afterwards rather than left to confuse anyone
reading the directory, since `providers/wakeword.py` only ever loads ONNX.
"""

from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "data" / "models" / "openwakeword"


def main() -> int:
    try:
        from openwakeword.utils import download_models
    except ImportError:
        print(
            "openwakeword is not installed. Run:\n"
            "  .venv\\Scripts\\pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    TARGET.mkdir(parents=True, exist_ok=True)
    download_models(model_names=["hey_jarvis"], target_directory=str(TARGET))

    for stale in TARGET.glob("*.tflite"):
        stale.unlink()

    from sidecar.providers.wakeword import missing_models

    absent = missing_models(TARGET)
    if absent:
        print(f"Still missing after download: {', '.join(absent)}", file=sys.stderr)
        return 1

    print(f"Wake word ready in {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
