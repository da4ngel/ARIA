/**
 * The app icon is a committed binary, so something has to notice when it drifts.
 *
 * `resources/icon.ico` must be in the repo — electron-builder needs it at pack
 * time and cannot regenerate it on a machine without Python. That makes it the
 * same hazard `electron/tray.ts`'s embedded PNGs were: a palette change lands
 * everywhere except the one surface nobody looks at. The tray sat a whole
 * retheme behind for exactly this reason.
 *
 * So this decodes the real file and checks the orb is still the accent colour,
 * and that every size Windows asks for is present.
 */

import { readFileSync } from 'node:fs'
import { inflateSync } from 'node:zlib'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import { COLORS } from '@/styles/tokens'

const ICON = resolve(__dirname, '../../resources/icon.ico')

/** Sizes Windows picks between. 16 is the taskbar; electron-builder demands 256. */
const EXPECTED_SIZES = [16, 24, 32, 48, 64, 128, 256]

interface Entry {
  size: number
  png: Buffer
}

function readIco(): Entry[] {
  const raw = readFileSync(ICON)
  expect(raw.readUInt16LE(0)).toBe(0) // reserved
  expect(raw.readUInt16LE(2)).toBe(1) // 1 = icon, 2 = cursor
  const count = raw.readUInt16LE(4)

  const entries: Entry[] = []
  for (let i = 0; i < count; i += 1) {
    const at = 6 + 16 * i
    // A 256px entry is stored as 0 — the format has one byte for the dimension.
    const size = raw.readUInt8(at) || 256
    const length = raw.readUInt32LE(at + 8)
    const offset = raw.readUInt32LE(at + 12)
    entries.push({ size, png: raw.subarray(offset, offset + length) })
  }
  return entries
}

/** One pixel of a PNG-encoded, non-interlaced RGBA image, by fraction. */
function pixelAt(
  png: Buffer,
  fx = 0.5,
  fy = 0.5,
): [number, number, number, number] {
  expect(png.subarray(0, 8).toString('hex')).toBe('89504e470d0a1a0a')

  let at = 8
  let width = 0
  let height = 0
  const idat: Buffer[] = []
  while (at < png.length) {
    const length = png.readUInt32BE(at)
    const tag = png.subarray(at + 4, at + 8).toString('ascii')
    if (tag === 'IHDR') {
      width = png.readUInt32BE(at + 8)
      height = png.readUInt32BE(at + 12)
      expect(png.readUInt8(at + 16)).toBe(8) // bit depth
      expect(png.readUInt8(at + 17)).toBe(6) // colour type 6 = RGBA
    }
    if (tag === 'IDAT') idat.push(png.subarray(at + 8, at + 8 + length))
    at += 12 + length
  }

  const pixels = inflateSync(Buffer.concat(idat))
  const stride = width * 4 + 1 // one filter byte per scanline
  const y = Math.min(height - 1, Math.floor(height * fy))
  const x = Math.min(width - 1, Math.floor(width * fx))
  // Filter type 0 (none) throughout — `make_app_icon.py` writes it that way.
  expect(pixels[y * stride]).toBe(0)
  const p = y * stride + 1 + x * 4
  return [pixels[p], pixels[p + 1], pixels[p + 2], pixels[p + 3]]
}

function hexToRgb(hex: string): [number, number, number] {
  return [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
  ]
}

describe('the app icon', () => {
  it('carries every size Windows asks for', () => {
    expect(readIco().map((e) => e.size)).toEqual(EXPECTED_SIZES)
  })

  it('includes the 256px entry electron-builder requires', () => {
    expect(readIco().some((e) => e.size === 256)).toBe(true)
  })

  it('is drawn in the accent colour, not a hand-typed copy of it', () => {
    // The centre sits inside the sphere, between the highlight and the shaded
    // rim — so it is the hue, darkened, not the raw token. Compared by *hue
    // proportion* rather than absolute value: what must not drift is which
    // colour it is, not how the gradient shades it.
    const [r, g, b, a] = pixelAt(readIco().find((e) => e.size === 256)!.png)
    expect(a).toBe(255)

    const [ar, , ab] = hexToRgb(COLORS.accent)
    // Blue dominates red in the accent, and green sits between them.
    expect(b).toBeGreaterThan(r)
    expect(g).toBeGreaterThan(r)
    expect(b).toBeGreaterThan(g)
    // And the ratios hold, which is what a recolour would break.
    expect(b / r).toBeGreaterThan((ab / ar) * 0.7)
    expect(b / r).toBeLessThan((ab / ar) * 1.4)
  })

  it('is transparent at the corners, so it sits on any taskbar colour', () => {
    // A Windows icon is composited over whatever the shell is painted in. An
    // icon with an opaque square background looks like a sticker.
    const png = readIco().find((e) => e.size === 256)!.png
    for (const [fx, fy] of [
      [0.02, 0.02],
      [0.98, 0.02],
      [0.02, 0.98],
      [0.98, 0.98],
    ]) {
      expect(pixelAt(png, fx, fy)[3]).toBe(0)
    }
    // And the centre is not, or there would be no orb.
    expect(pixelAt(png)[3]).toBe(255)
  })
})
