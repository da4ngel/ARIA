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
import struct
import zlib

SIZE = 32
RADIUS = 12.0
SAMPLES = 4  # supersampling per axis, for a smooth edge

# Must match theme.extend.colors.aria in tailwind.config.js.
COLORS: dict[str, tuple[int, int, int]] = {
    "ok": (0x4A, 0xDE, 0x80),
    "warn": (0xFB, 0xBF, 0x24),
    "bad": (0xF8, 0x71, 0x71),
}


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
