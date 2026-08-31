"""Generate resources/icon.ico — the orb, as the app icon.

    .venv\\Scripts\\python.exe scripts/make_app_icon.py

**The orb is already ARIA's identity.** It is on screen constantly — the hero
on an empty conversation, a small dot in the header afterwards — so the app
icon is that same object rather than a letterform ARIA uses nowhere else. What
is drawn here is what `src/components/Orb.tsx` draws in CSS: a bloom behind, a
sphere lit from the upper left, and an outer glow.

**Stdlib only (zlib + struct), the same discipline as `make_tray_icons.py`.**
Pillow is a runtime dependency but a *build* script's dependencies do not
belong in `requirements.txt`, and an .ico is a container of PNGs — a six-byte
header, one sixteen-byte directory entry per size, and the PNG payloads this
project already knows how to write.

The palette is read from `src/styles/tokens.js`, never retyped. That file's own
history is the argument: the tray icons sat a whole retheme behind because
their colours had been copied by hand.

**This does not replace the tray icons.** Those are status — ok, warn, bad —
and are the only always-visible signal that the brain is alive. The orb is the
*app*; the dots are its *state*.
"""

from __future__ import annotations

import re
import struct
import zlib
from pathlib import Path

#: Every size Windows picks between: 16 in the taskbar and title bar, 256 in
#: the installer and on the desktop. electron-builder requires the 256.
SIZES = (16, 24, 32, 48, 64, 128, 256)

#: Supersampling per axis. The sphere is a gradient rather than a flat disc, so
#: the edge needs more help than the tray dots do.
SAMPLES = 4

#: Fractions of the icon's width, and **they change with the size**.
#:
#: At 256 the bloom is most of the charm and the sphere can sit small with air
#: around it. At 16 that same layout is a five-pixel dot adrift in a mostly
#: empty square — the glow is below the resolution that can express it, so it
#: only steals room. Small sizes therefore get a bigger core and a tighter
#: halo. Verified by rendering each size and looking at it, which is the only
#: way this is checkable.
def _geometry(size: int) -> tuple[float, float, float]:
    """`(sphere radius, bloom radius, bloom alpha)` for one size."""
    if size <= 24:
        return 0.40, 0.48, 0.26
    if size <= 48:
        return 0.35, 0.49, 0.36
    return 0.30, 0.50, 0.45

#: Where the light comes from, as a fraction of the sphere's own box. Straight
#: from `Orb.tsx`'s `radial-gradient(circle at 32% 28%, …)` — it is what makes
#: the mark read as a lit object rather than a coloured circle.
LIGHT_X, LIGHT_Y = 0.32, 0.28

_TOKENS = Path(__file__).resolve().parent.parent / "src" / "styles" / "tokens.js"
_OUT = Path(__file__).resolve().parent.parent / "resources" / "icon.ico"


def _colour(name: str) -> tuple[int, int, int]:
    source = _TOKENS.read_text(encoding="utf-8")
    match = re.search(rf"^\s+'?{name}'?:\s*'#([0-9a-fA-F]{{6}})'", source, re.MULTILINE)
    if match is None:
        raise SystemExit(f"No {name!r} in {_TOKENS} — has the palette moved?")
    value = match.group(1)
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


#: **`accent`, and this was `idle` first.** The reasoning for `idle` was that a
#: static icon is at rest, and that `tokens.js` reserves `accent` for focus
#: rings. Rendered at 256 and looked at, it was a grey ball — elegant in the
#: app, invisible on a taskbar beside everything else competing for attention.
#:
#: The palette rule governs *in-app semantics*: it exists so a saturated colour
#: on screen always means something, and so the accent is never confused with
#: "listening" or "speaking". An icon in the Windows shell is outside that
#: system entirely — nobody checks the taskbar to find out whether she is
#: listening — so the rule it must obey is a different one: be recognisable at
#: 16 pixels. Indigo is the app's own colour and it is that.
HUE = _colour("accent")

#: The specular highlight — the sphere's own colour lifted toward white rather
#: than white itself, which would look like a hole punched in it.
def _lift(rgb: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(c + (255 - c) * amount) for c in rgb)  # type: ignore[return-value]


#: Tuned by rendering and looking. A 0.55 lift and a 0.42 shadow washed the
#: sphere out to near-white at the top; these keep it saturated enough to
#: read as blue while the gradient still describes a lit ball.
HIGHLIGHT = _lift(HUE, 0.30)
SHADOW = tuple(round(c * 0.24) for c in HUE)


def _sample(
    fx: float, fy: float, sphere: float, bloom: float, glow: float
) -> tuple[int, int, int, float]:
    """Colour and alpha at a point, in 0..1 icon coordinates.

    Returns straight (non-premultiplied) RGBA — the caller composites.
    """
    dx, dy = fx - 0.5, fy - 0.5
    distance = (dx * dx + dy * dy) ** 0.5

    if distance <= sphere:
        # Distance from the light source, normalised over the sphere's width.
        lx = fx - (0.5 - sphere + 2 * sphere * LIGHT_X)
        ly = fy - (0.5 - sphere + 2 * sphere * LIGHT_Y)
        lit = min(1.0, ((lx * lx + ly * ly) ** 0.5) / (sphere * 1.9))
        # Bright near the light, falling to a shaded rim. Squared so the
        # highlight stays tight instead of washing the whole sphere out.
        blend = lit * lit
        rgb = tuple(
            round(HIGHLIGHT[i] + (SHADOW[i] - HIGHLIGHT[i]) * blend) for i in range(3)
        )
        return rgb[0], rgb[1], rgb[2], 1.0  # type: ignore[return-value]

    if distance <= bloom:
        # `radial-gradient(circle, {hue}55 0%, {hue}00 68%)` — the glow, fading
        # to nothing well before the edge so the icon has breathing room.
        span = bloom - sphere
        fade = 1.0 - (distance - sphere) / span
        return HUE[0], HUE[1], HUE[2], glow * fade * fade

    return 0, 0, 0, 0.0


def _pixel(x: int, y: int, size: int) -> tuple[int, int, int, int]:
    """One pixel, supersampled."""
    sphere, bloom, glow = _geometry(size)
    r = g = b = a = 0.0
    for sy in range(SAMPLES):
        for sx in range(SAMPLES):
            fx = (x + (sx + 0.5) / SAMPLES) / size
            fy = (y + (sy + 0.5) / SAMPLES) / size
            pr, pg, pb, pa = _sample(fx, fy, sphere, bloom, glow)
            r += pr * pa
            g += pg * pa
            b += pb * pa
            a += pa
    total = SAMPLES * SAMPLES
    if a <= 0:
        return 0, 0, 0, 0
    # Un-premultiply: the colour is the average of what was actually there.
    return round(r / a), round(g / a), round(b / a), round(255 * a / total)


def _chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data))
    )


def png_bytes(size: int) -> bytes:
    """One RGBA PNG of the orb at `size`."""
    rows = bytearray()
    for y in range(size):
        rows.append(0)  # filter: none
        for x in range(size):
            rows.extend(_pixel(x, y, size))

    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + _chunk(b"IEND", b"")
    )


def ico_bytes(pngs: dict[int, bytes]) -> bytes:
    """An .ico wrapping PNG entries.

    ICONDIR: reserved, type 1 (icon), count. Then one 16-byte ICONDIRENTRY per
    image, then the payloads. A 256px entry is written as width/height 0, which
    is the format's way of saying "256" in one byte.
    """
    count = len(pngs)
    offset = 6 + 16 * count
    directory = bytearray(struct.pack("<HHH", 0, 1, count))
    payloads = bytearray()

    for size in sorted(pngs):
        data = pngs[size]
        directory.extend(
            struct.pack(
                "<BBBBHHII",
                0 if size >= 256 else size,  # width
                0 if size >= 256 else size,  # height
                0,  # palette entries; 0 for a truecolour image
                0,  # reserved
                1,  # colour planes
                32,  # bits per pixel
                len(data),
                offset + len(payloads),
            )
        )
        payloads.extend(data)

    return bytes(directory + payloads)


def main() -> None:
    pngs = {size: png_bytes(size) for size in SIZES}
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_bytes(ico_bytes(pngs))
    print(f"wrote {_OUT} — {_OUT.stat().st_size:,} bytes, sizes {', '.join(map(str, SIZES))}")
    print(f"hue #{HUE[0]:02x}{HUE[1]:02x}{HUE[2]:02x} (tokens.js `accent`)")


if __name__ == "__main__":
    main()
