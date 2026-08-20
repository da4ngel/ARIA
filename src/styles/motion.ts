/**
 * One motion language, instead of a number invented at every call site.
 *
 * Before this, durations and easings were inline everywhere: 120ms hover in
 * the CSS, 140ms and 180ms sheets on two different curves, springs anywhere
 * between 260 and 700 stiffness, 200ms and 220ms size changes. Each was
 * reasonable alone; together they are why the app moved like several
 * programs rather than one.
 *
 * **Reduced motion is honoured through `still()` rather than at each call
 * site.** Branching on `useReducedMotion()` by hand is five chances to
 * forget, and the CSS blanket in `index.css` only covers the CSS half.
 */

import type { Transition } from 'framer-motion'

/** Milliseconds. Shared with `electron/main.ts`, which animates the window
 *  itself — but only the *numbers* cross that boundary: a CSS cubic-bezier
 *  string is no use to `animateBounds`, which needs a JS easing function. */
export const DURATION = {
  instant: 90,
  /** Pointer feedback. `.interactive`'s hover transition in `index.css`. */
  hover: 120,
  fast: 140,
  /** Popover entrance — `animate-rise` in `tailwind.config.mjs`. */
  rise: 160,
  base: 200,
  /** A colour crossfade. `Orb`'s state change is the documented case: §9
   *  Phase 2 budgets 300ms from wake word to visible response. */
  colour: 300,
  slow: 320,
  /** Window resize, matched by hand in `electron/main.ts`. */
  window: 220,
} as const

/** Cubic-bezier control points, in the form Framer wants them. */
export const EASE = {
  /** Entrances. Fast out of the gate, settles gently. */
  standard: [0.2, 0.8, 0.2, 1],
  /** Sheets and anything large. A longer tail reads as weight. */
  emphasis: [0.16, 1, 0.3, 1],
  /** Exits should not linger — a thing being dismissed should look dismissed. */
  exit: [0.4, 0, 1, 1],
} as const

export const SPRING = {
  /** Chips, popovers, small state. */
  snappy: { type: 'spring', stiffness: 520, damping: 32, mass: 0.9 },
  /** Sheets, captions — anything with area. */
  settle: { type: 'spring', stiffness: 320, damping: 30 },
  /** Shared-element travel, e.g. the orb between hero and header. */
  shared: { type: 'spring', stiffness: 260, damping: 28 },
  /** A message arriving. Firmer than `settle` — a turn should land, not drift. */
  arrive: { type: 'spring', stiffness: 420, damping: 34 },
  /**
   * Anything tracking a live audio envelope.
   *
   * Stiff and lightly damped on purpose, and the reason is in `Orb`: a voice's
   * envelope moves in tens of milliseconds, and a slower spring smears
   * syllables into a hum. `HandsFreeToggle` had the same numbers inline.
   */
  reactive: { type: 'spring', stiffness: 700, damping: 30 },
} as const

export const TWEEN = {
  fast: { duration: DURATION.fast / 1000, ease: EASE.standard },
  base: { duration: DURATION.base / 1000, ease: EASE.standard },
  emphasis: { duration: DURATION.base / 1000, ease: EASE.emphasis },
  exit: { duration: DURATION.instant / 1000, ease: EASE.exit },
  rise: { duration: DURATION.rise / 1000, ease: EASE.standard },
} as const

/**
 * How far apart a list's children start.
 *
 * `EmptyState` hand-wrote `0.12` and `0.2`, which is a stagger with the
 * arithmetic already done and no name on it. Framer wants seconds.
 */
export const STAGGER = { step: 0.06, lead: 0.12 } as const

/** `STAGGER.lead` then one `STAGGER.step` per item, as a delay in seconds. */
export function stagger(index: number): number {
  return STAGGER.lead + index * STAGGER.step
}

/**
 * The same transition, or none at all.
 *
 * Reduced motion means **still**, not merely faster — someone who asked for
 * less movement did not ask for the same movement in a hurry.
 *
 * `reduced` is `boolean | null` because that is what `useReducedMotion()`
 * returns — null until the media query has been read. It was typed `boolean`
 * for two days and this function was never called once in that time, which is
 * unlikely to be a coincidence: every call site would have been a type error.
 */
export function still(transition: Transition, reduced: boolean | null): Transition {
  return reduced ? { duration: 0 } : transition
}
