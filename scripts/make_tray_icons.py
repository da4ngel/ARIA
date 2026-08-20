"""Generate the tray icon PNGs embedded in electron/tray.ts.

Electron's nativeImage cannot decode SVG, so the tray needs real bitmaps. They
are embedded as base64 in tray.ts rather than loaded from resources/ so the icon
behaves identically in dev and in the packaged app.

Run when the palette in tailwind.config.js changes, then paste the output over
the ICON_PNG map in electron/tray.ts:

    .venv\\Scripts\\python.exe scripts/make_tray_icons.py

Stdlib only (zlib + struct). Deliberately no Pillow — nothing here belongs in
requirements.txt.
"""

from __future__ import annotations

import base64
import re
import struct
import zlib
from pathlib import Path

SIZE = 32
RADIUS = 12.0
SAMPLES = 4  # supersampling per axis, for a smooth edge

# **Read from `src/styles/tokens.js`, not typed out again.**
#
# This was a hand-written copy pointing at `tailwind.config.js` — a file that
# no longer exists — and it sat a whole retheme behind: `#4ade80/#fbbf24/
# #f87171`, the Tailwind 400s from before the palette moved to measured values.
# The tray had been the wrong colour ever since, and nothing said so, because
# it is the one surface no test and no screenshot covers.
#
# That is the same "the palette was restated in six places" bug this project
# already fixed once, still live in a seventh. Parsing the token file is ugly
# and it is the only thing that cannot drift.
_TOKENS = Path(__file__).resolve().parent.parent / "src" / "styles" / "tokens.js"


def _palette() -> dict[str, tuple[int, int, int]]:
    source = _TOKENS.read_text(encoding="utf-8")
    found: dict[str, tuple[int, int, int]] = {}
    for name in ("ok", "warn", "bad"):
        match = re.search(rf"^\s+{name}:\s*'#([0-9a-fA-F]{{6}})'", source, re.MULTILINE)
        if match is None:
            raise SystemExit(f"No {name!r} in {_TOKENS} — has the palette moved?")
        value = match.group(1)
        found[name] = (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))
    return found


COLORS: dict[str, tuple[int, int, int]] = _palette()


def coverage(px: int, py: int) -> float:
    """Fraction of one pixel covered by the circle, by supersampling."""
    centre = SIZE / 2.0
    hits = 0
    for sy in range(SAMPLES):
        for sx in range(SAMPLES):
            x = px + (sx + 0.5) / SAMPLES - centre
            y = py + (sy + 0.5) / SAMPLES - centre
            if x * x + y * y <= RADIUS * RADIUS:
                hits += 1
    return hits / (SAMPLES * SAMPLES)


def _chunk(tag: bytes, data: bytes) -> bytes:
    body = tag + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))


def png_bytes(rgb: tuple[int, int, int]) -> bytes:
    """An 8-bit RGBA PNG of a filled circle on transparency."""
    raw = bytearray()
    for y in range(SIZE):
        raw.append(0)  # filter type 0 (None) per scanline
        for x in range(SIZE):
            raw += bytes((*rgb, round(coverage(x, y) * 255)))

    ihdr = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )


def main() -> None:
    lines = [
        f"  {name}: '{base64.b64encode(png_bytes(rgb)).decode()}',"
        for name, rgb in COLORS.items()
    ]
    # This script's whole job is to print source for pasting, so stdout is the
    # product here rather than logging (CLAUDE.md rule 9 governs the sidecar).
    import sys

    sys.stdout.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
