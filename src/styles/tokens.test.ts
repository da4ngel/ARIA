/**
 * The palette, enforced.
 *
 * Two recorded incidents are what this file is for. The colours were restated
 * in five places, three of them inside canvas frame loops where only sampling
 * pixels would show a mismatch. And the 0.62 glass alpha was chosen by
 * looking at a white document through the window — a number that can be
 * "tidied" by anyone who does not know that, and whose failure mode is text
 * you cannot read.
 */

import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

import { COLORS, HUES, RGB, hexToRgb } from '@/styles/tokens'

/** Composite `rgba(...)` over an opaque backdrop, so contrast is measured
 *  against what is actually on screen rather than against the tint alone. */
function over(rgba: string, backdrop: [number, number, number]): [number, number, number] {
  const [r, g, b, a] = rgba
    .replace(/rgba?\(|\)/g, '')
    .split(',')
    .map((n) => Number(n.trim()))
  return [
    Math.round(r * a + backdrop[0] * (1 - a)),
    Math.round(g * a + backdrop[1] * (1 - a)),
    Math.round(b * a + backdrop[2] * (1 - a)),
  ]
}

function luminance([r, g, b]: [number, number, number]): number {
  const channel = (v: number): number => {
    const s = v / 255
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4
  }
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)
}

function contrast(a: [number, number, number], b: [number, number, number]): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return (hi + 0.05) / (lo + 0.05)
}

/** Hue in degrees. Used to ask whether two colours are *confusable*, which
 *  luminance contrast cannot answer. */
function hueOf([r, g, b]: [number, number, number]): number {
  const [rn, gn, bn] = [r / 255, g / 255, b / 255]
  const max = Math.max(rn, gn, bn)
  const min = Math.min(rn, gn, bn)
  const delta = max - min
  if (delta === 0) return 0
  const h =
    max === rn ? ((gn - bn) / delta) % 6 : max === gn ? (bn - rn) / delta + 2 : (rn - gn) / delta + 4
  return (h * 60 + 360) % 360
}

function saturationOf([r, g, b]: [number, number, number]): number {
  const [rn, gn, bn] = [r / 255, g / 255, b / 255]
  const max = Math.max(rn, gn, bn)
  const min = Math.min(rn, gn, bn)
  const lightness = (max + min) / 2
  return max === min ? 0 : (max - min) / (1 - Math.abs(2 * lightness - 1))
}

const SURFACE = over(COLORS.glass, hexToRgb(COLORS.void))

describe('the palette', () => {
  it('derives the canvas triples rather than restating them', () => {
    // The exact drift this file exists to stop: `VoiceAura` and `ScreenRim`
    // draw with rgba triples that used to be hand-converted from the hex.
    for (const key of Object.keys(HUES) as Array<keyof typeof HUES>) {
      expect(RGB[key]).toEqual(hexToRgb(HUES[key]))
    }
  })

  it('keeps the accent clear of every saturated assistant state', () => {
    // The single most defensible change in the retheme. The old accent
    // (#6fd3e0, hue 187) sat **seven degrees** from `listening` (#5ec8e8,
    // hue 194), so a focus ring and "she is listening" were the same colour
    // — in a palette whose entire rule is that saturated colour means
    // something.
    //
    // Measured on hue, not on contrast: two colours can have identical
    // luminance and be plainly different (blue and green do), and it was the
    // hue that collided. `idle` is exempt because it is 21% saturated — a
    // grey, by design, since it means "nothing is happening" — and
    // saturation separates it from a 100% accent regardless of hue.
    const accent = hueOf(hexToRgb(COLORS.accent))
    for (const [name, hex] of Object.entries(HUES)) {
      const rgb = hexToRgb(hex)
      if (saturationOf(rgb) < 0.5) continue
      const gap = Math.abs(accent - hueOf(rgb))
      expect(Math.min(gap, 360 - gap), name).toBeGreaterThanOrEqual(20)
    }
  })

  it('stays readable against the composited glass', () => {
    // Readability wins the tiebreak — the config has pre-committed to that
    // since the alpha was first measured over a bright editor.
    expect(contrast(hexToRgb(COLORS.text), SURFACE)).toBeGreaterThanOrEqual(7)
    expect(contrast(hexToRgb(COLORS.dim), SURFACE)).toBeGreaterThanOrEqual(4.5)
    expect(contrast(hexToRgb(COLORS.muted), SURFACE)).toBeGreaterThanOrEqual(4.5)
    expect(contrast(hexToRgb(COLORS.faint), SURFACE)).toBeGreaterThanOrEqual(3)
  })

  it('gives the accent enough contrast to work as a focus ring', () => {
    // WCAG 1.4.11: a non-text UI component needs 3:1, and a focus ring is the
    // one component that is useless if it cannot be seen.
    expect(contrast(hexToRgb(COLORS.accent), SURFACE)).toBeGreaterThanOrEqual(3)
  })

  it('holds the glass alpha at the measured value', () => {
    // 0.86 came from the era before DWM acrylic, when the window was
    // `transparent: true` and the alpha did all the work. 0.62 was measured
    // on screen once the compositor supplied the blur. Neither number is a
    // preference, and a recolour is not a reason to move it.
    expect(COLORS.glass).toContain('0.62')
  })

  it('keeps the state colours that are meant to match, matching', () => {
    // Speaking is a good outcome and acting is a caution — the overlap with
    // `ok`/`warn` is deliberate, not a copy-paste to be tidied away.
    expect(COLORS.speaking).toBe(COLORS.ok)
    expect(COLORS.acting).toBe(COLORS.warn)
  })

  it('still has every token the components ask for by name', () => {
    // Tests elsewhere assert on token *names* (`bg-aria-accent`,
    // `text-aria-bad`), which is what makes a recolour cheap — and what makes
    // deleting a name expensive.
    for (const name of [
      'void', 'glass', 'panel', 'pop', 'raised', 'sunk', 'rim', 'rim-strong',
      'text', 'dim', 'muted', 'faint', 'accent', 'ok', 'warn', 'bad',
      'idle', 'listening', 'thinking', 'speaking', 'acting',
    ]) {
      expect(COLORS[name], name).toBeDefined()
    }
  })

  it('is an ES module, because the renderer imports it', () => {
    // This file shipped as CommonJS once. Vite treats `.js` under `src/` as
    // ESM, so `HUES` resolved to nothing, `Orb` failed to evaluate, and the
    // window came up **completely blank** — while `npm run typecheck` and
    // `npm test` both stayed green, because tsc reads the `.d.ts` beside this
    // file and vitest runs in Node where CJS interop is transparent.
    //
    // A grep, because the honest guard is `npm run build` and this is the
    // cheap half of it that runs in the normal loop.
    const source = readFileSync(join(process.cwd(), 'src/styles/tokens.js'), 'utf8')

    // Comments mention both words; strip them before looking.
    const code = source.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\/\/.*/g, '')

    expect(code).not.toContain('module.exports')
    expect(code).not.toContain('require(')
    expect(code).toContain('export const COLORS')
  })
})

describe('the streaming shimmer', () => {
  const CSS = readFileSync(join(process.cwd(), 'src/styles/index.css'), 'utf8')

  it('does not reach code', () => {
    // **A real bug for an hour.** `.streaming` sets `background-clip: text`
    // with a transparent colour, and every descendant inherits it — so a
    // fenced block inside a streaming reply rendered transparent, clipped to
    // the *container's* gradient rather than drawn.
    //
    // Invisible unless you happened to watch a reply containing code arrive,
    // which is exactly the kind of thing that needs a test rather than an eye.
    const exemption = CSS.slice(CSS.indexOf('.streaming pre'))

    expect(CSS).toContain('.streaming pre')
    expect(CSS).toContain('.streaming code')
    expect(exemption.slice(0, 400)).toContain('background-clip: border-box')
    expect(exemption.slice(0, 400)).toContain('color: inherit')
  })

  it('still applies to ordinary prose', () => {
    // The exemption must not have turned the whole effect off.
    const rule = CSS.slice(CSS.indexOf('.streaming {'), CSS.indexOf('.streaming pre'))
    expect(rule).toContain('background-clip: text')
    expect(rule).toContain('color: transparent')
  })
})

describe('syntax highlighting', () => {
  const CSS = readFileSync(join(process.cwd(), 'src/styles/index.css'), 'utf8')

  it('is coloured from the palette, not a stock theme', () => {
    // `highlight.js` themes ship a full colour scheme and assume their own
    // background. Dropping one in would put eight hues in the one place where
    // colour is otherwise load-bearing.
    const block = CSS.slice(CSS.indexOf('.hljs {'), CSS.indexOf('.interactive {'))

    expect(block).toContain('.hljs')
    expect(block).not.toMatch(/#[0-9a-fA-F]{6}/)
    expect(block).toContain("theme('colors.aria")
  })

  it('keeps saturation meaning something', () => {
    // The palette's own stated rule. Three things carry colour — keywords,
    // strings, a deletion — and the rest is the neutral ramp.
    const block = CSS.slice(CSS.indexOf('.hljs {'), CSS.indexOf('.interactive {'))
    const hues = new Set(
      [...block.matchAll(/theme\('colors\.aria\.([a-z-]+)'\)/g)].map((m) => m[1]),
    )
    const saturated = [...hues].filter((h) => ['accent', 'ok', 'warn', 'bad'].includes(h))

    expect(saturated.length).toBeLessThanOrEqual(3)
  })
})
