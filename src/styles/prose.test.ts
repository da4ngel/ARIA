/**
 * The prose tokens must never become a second palette.
 *
 * `Markdown.tsx` carried a raw `text-sky-400` through an entire retheme and
 * nothing failed, because there was no test for that file at all. Moving every
 * typographic decision into `prose.ts` concentrates the risk in one place —
 * which is only an improvement if that one place is watched.
 */

import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

import { CODE_FOLD_LINES, PROSE, PROSE_BODY, PROSE_MEASURE } from '@/styles/prose'
import { COLORS } from '@/styles/tokens'

const SOURCE = readFileSync(join(process.cwd(), 'src/styles/prose.ts'), 'utf8')

/** Source with its comments removed.
 *
 *  **A negative assertion has to be made against code, not prose.** This
 *  project has now been caught by that in three files and two languages —
 *  `test_email.py` grew `code_only()` after a scan for "SMTP" matched the
 *  docstring saying there is none, and `tokens.test.ts` grew the CSS version
 *  after a comment explaining a removed gradient matched the rule forbidding
 *  it. The comments here name colours; the code must not. */
const code = SOURCE.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\/\/.*$/gm, '')

const values = [PROSE_BODY, PROSE_MEASURE, ...Object.values(PROSE)].join(' ')

describe('the prose tokens', () => {
  it('names no colour of its own', () => {
    expect(code).not.toMatch(/#[0-9a-fA-F]{3,8}\b/)
    expect(code).not.toMatch(/\b(rgb|rgba|hsl|hsla)\(/)
  })

  it('uses the palette rather than raw Tailwind colours', () => {
    // A raw Tailwind colour is the specific failure that happened before: it
    // survives a recolour untouched and drifts silently off-palette.
    expect(values).not.toMatch(
      /\b(?:text|bg|border|decoration|marker:text)-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}\b/,
    )
  })

  it('takes every colour it does use from an aria token', () => {
    // Two ways a colour can be off-palette. One is a Tailwind palette entry,
    // covered above. The other is a bare keyword — `text-white`, `bg-black` —
    // which no recolour would ever touch. Checked by name rather than by
    // shape, because a suffix rule cannot tell `border-l-2` (a width) from
    // `border-white` (a colour) without knowing every utility Tailwind has.
    expect(values).not.toMatch(
      /(?:text|bg|border|decoration)-(?:white|black|current|inherit)/,
    )

    // And every token that *is* referenced has to be one that exists.
    const referenced = values.match(/-aria-[a-z-]+/g) ?? []
    expect(referenced.length).toBeGreaterThan(0)
    for (const token of referenced) {
      expect(Object.keys(COLORS)).toContain(token.replace('-aria-', ''))
    }
  })
})

describe('the type scale', () => {
  it('sets body at the reading size rather than the label size', () => {
    // Replies rendered at 13px for months: `Markdown` set `text-small` and the
    // `text-body` its parent applied was silently overridden.
    expect(PROSE_BODY).toContain('text-body')
    expect(PROSE_BODY).not.toContain('text-small')
  })

  it('gives h1 and h2 the same step', () => {
    // A heading in a reply is a section marker, not a title. The difference
    // below that is carried by weight, not by another size.
    expect(PROSE.h1).toContain('text-head')
    expect(PROSE.h2).toContain('text-head')
    expect(PROSE.h4).toContain('text-body')
    expect(PROSE.h4).toContain('font-strong')
  })

  it('pairs bold with a brighter foreground than body', () => {
    // Weight alone reads weakly at small sizes on a dark surface, which is
    // what the four-step neutral ramp was cut for. Body has to sit one step
    // below the top for emphasis to have anywhere to go.
    expect(PROSE_BODY).toContain('text-aria-dim')
    expect(PROSE.strong).toContain('text-aria-text')
  })

  it('zeroes the first and last margins so a reply has no dead edges', () => {
    expect(PROSE.p).toContain('first:mt-0')
    expect(PROSE.p).toContain('last:mb-0')
  })

  it('gives a heading more space above than below', () => {
    // What binds a heading to the content it introduces, rather than letting
    // it float between two paragraphs.
    const above = Number(/mt-(\d+)/.exec(PROSE.h2)?.[1])
    const below = Number(/mb-(\d+)/.exec(PROSE.h2)?.[1])

    expect(above).toBeGreaterThan(below)
  })
})

describe('the measure', () => {
  it('caps prose separately from the transcript column', () => {
    // `--reading` is where the *column* ends and the composer shares it, so
    // they keep agreeing with each other. At body size that column is around
    // 98 characters — far past where the eye reliably finds the next line.
    expect(PROSE_MEASURE).toContain('--prose')
    expect(PROSE_MEASURE).not.toContain('--reading')
  })

  it('is declared in rem so it scales with the roomy class', () => {
    // Both the type and the measure hang off the root font size, so the line
    // stays the same number of *characters* when the window is maximised
    // rather than simply becoming a longer one.
    const css = readFileSync(join(process.cwd(), 'src/styles/index.css'), 'utf8')

    expect(css).toMatch(/--prose:\s*[\d.]+rem/)
  })
})

describe('code folding', () => {
  it('folds past a threshold both the cap and the control derive from', () => {
    expect(CODE_FOLD_LINES).toBeGreaterThan(0)
    expect(Number.isInteger(CODE_FOLD_LINES)).toBe(true)
  })
})
