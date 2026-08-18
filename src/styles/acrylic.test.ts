/**
 * The acrylic incident, turned into a test.
 *
 * Recorded in CLAUDE.md: `backgroundMaterial: 'acrylic'` was set *together
 * with* an opaque `backgroundColor`, which composites straight over the DWM
 * material and hides it on every frame. The acrylic was being applied and
 * then painted out, and the symptom — "I asked for glass everywhere and I
 * can't see it" — pointed at the CSS rather than at the window.
 *
 * The three window options are load-bearing and easy to "tidy": an opaque
 * brand colour on `backgroundColor` looks like an improvement and silently
 * re-breaks the whole effect. These read the source rather than mocking
 * Electron, because what needs guarding is the literal configuration.
 */

import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

const MAIN = readFileSync(join(process.cwd(), 'electron/main.ts'), 'utf8')
const CSS = readFileSync(join(process.cwd(), 'src/styles/index.css'), 'utf8')

describe('the acrylic window', () => {
  it('keeps the three settings that make DWM acrylic visible', () => {
    // All three together, or none of it works: `transparent: false` is
    // required *for* acrylic, and the transparent backgroundColor is what
    // stops the window painting over it.
    expect(MAIN).toContain("backgroundMaterial: 'acrylic'")
    expect(MAIN).toContain('transparent: false')
    expect(MAIN).toContain("backgroundColor: '#00000000'")
  })

  it('never gives the main window an opaque background', () => {
    // The exact regression. `#00000000` is the only acceptable value.
    const colours = [...MAIN.matchAll(/backgroundColor:\s*'([^']+)'/g)].map((m) => m[1])
    expect(colours.length).toBeGreaterThan(0)
    for (const colour of colours) {
      expect(colour, 'an opaque window background hides the acrylic').toBe('#00000000')
    }
  })

  it('paints the fallback in CSS, under the tint rather than over the material', () => {
    // Where acrylic applies this sits behind it and is never seen; where it
    // does not — Windows 10, or transparency effects off — it is what keeps
    // the panel readable. On the window it would be the bug above.
    expect(CSS).toContain('prefers-reduced-transparency')
    const block = CSS.slice(CSS.indexOf('prefers-reduced-transparency'))
    expect(block.slice(0, 200)).toContain("theme('colors.aria.void')")
  })

  it('leaves the page itself transparent', () => {
    // A background on html/body/#root is the same mistake one layer in.
    const base = CSS.slice(0, CSS.indexOf('@media'))
    expect(base).toContain('background: transparent')
  })
})
