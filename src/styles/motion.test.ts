/**
 * The motion tokens, and the helper that was written and never called.
 *
 * `still()` sat unused for two days while every framer call site inlined its
 * own numbers — and its signature is the likely reason: it took `boolean`,
 * while `useReducedMotion()` returns `boolean | null`, so every call site
 * would have been a type error. A helper nothing can call is the same shape as
 * a table nothing writes to, which this project keeps finding.
 */

import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

import { DURATION, SPRING, TWEEN, stagger, still } from '@/styles/motion'

describe('still()', () => {
  it('means still, not merely faster', () => {
    // Someone who asked for less movement did not ask for the same movement
    // in a hurry.
    expect(still(TWEEN.base, true)).toEqual({ duration: 0 })
  })

  it('passes the transition through untouched otherwise', () => {
    expect(still(TWEEN.base, false)).toBe(TWEEN.base)
  })

  it('accepts what useReducedMotion actually returns', () => {
    // `null` until the media query has been read. Typing this `boolean` is why
    // the helper was uncallable and therefore unused.
    expect(still(TWEEN.base, null)).toBe(TWEEN.base)
  })

  it('is actually wired up', () => {
    // The point of the whole exercise. Counted rather than spot-checked,
    // because one call site would satisfy a `toContain` and prove nothing.
    const sources = [
      'src/components/Panel.tsx',
      'src/components/ConfirmDialog.tsx',
      'src/components/ToolCallCard.tsx',
      'src/components/QuestionCard.tsx',
      'src/components/ModeSelector.tsx',
      'src/components/ModelPicker.tsx',
      'src/components/ComposerBar.tsx',
      'src/components/HandsFreeToggle.tsx',
      'src/components/Orb.tsx',
      'src/overlay/Caption.tsx',
    ]
    for (const path of sources) {
      const code = readFileSync(join(process.cwd(), path), 'utf8')
      expect(code, `${path} should route its transitions through still()`).toMatch(
        /still(Motion)?\(/,
      )
    }
  })
})

describe('the token set', () => {
  it('covers the durations the app actually uses', () => {
    // Each of these was a number written out at a call site before it had a
    // name: 120ms hover in the CSS, 160ms `animate-rise`, 300ms orb colour.
    expect(DURATION.hover).toBe(120)
    expect(DURATION.rise).toBe(160)
    expect(DURATION.colour).toBe(300)
  })

  it('names the two springs that were duplicated inline', () => {
    // `Orb` and `HandsFreeToggle` both carried 700/30; `ConversationView`
    // carried 420/34.
    expect(SPRING.reactive).toMatchObject({ stiffness: 700, damping: 30 })
    expect(SPRING.arrive).toMatchObject({ stiffness: 420, damping: 34 })
  })

  it('staggers from a scale rather than hand-written delays', () => {
    expect(stagger(0)).toBeCloseTo(0.12)
    expect(stagger(2)).toBeGreaterThan(stagger(1))
  })
})
