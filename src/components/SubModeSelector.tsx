/**
 * Picking how you are studying, in a study chat.
 *
 * **This takes the mode picker's slot, and that is the point.** Eyaas asked
 * for Study to be *"another type of chat, dedicated fully for studies
 * purpose"* — so in a study chat the control you reach for in the composer is
 * not Normal / Quick / Research / Code / Critic, which are ways of answering an
 * ordinary question. It is Learn / Practice / Revision / Rapid review / Exam /
 * Teach-back, which are ways of running a lesson.
 *
 * Same popover recipe as `ModeSelector` and `ModelPicker` — click away or
 * Escape to close, `glass-pop` sheet, an exit animation so it does not vanish
 * between frames. Deliberately not a shared component with `ModeSelector`:
 * that one carries an online warning, a suggestion chip and a "Normal is the
 * absence of a mode" rule that none of this has, and folding two controls into
 * one with three flags is how both become hard to change.
 */

import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import { useCallback, useEffect, useRef, useState } from 'react'

import { TWEEN, still } from '@/styles/motion'

/** The six, in the order they are used rather than alphabetically: learn it,
 *  practise it, fix what broke, skim it, sit the exam, explain it back.
 *
 *  Mirrors `sidecar/core/study_modes.py`. The *labels* live in both places
 *  because a popover cannot wait on a round trip to draw itself; the openers
 *  do not, and come back from `study.start` — so what she is actually asked
 *  has one definition. */
export const SUB_MODES = [
  { value: 'learn', label: 'Learn', hint: 'Teach me the next thing, in layers.' },
  { value: 'practice', label: 'Practice', hint: 'Questions on what I have covered, with feedback.' },
  { value: 'revision', label: 'Revision', hint: 'Only the things I keep getting wrong.' },
  { value: 'rapid', label: 'Rapid review', hint: 'One line per concept. A skim, not a lesson.' },
  { value: 'exam', label: 'Exam', hint: 'Four questions, no feedback until the end.' },
  { value: 'teach_back', label: 'Teach-back', hint: 'I explain, she says what was missing.' },
] as const

export type SubMode = (typeof SUB_MODES)[number]['value']

export function SubModeSelector({
  subMode,
  disabled,
  onSelect,
}: {
  subMode: SubMode
  disabled: boolean
  onSelect: (next: SubMode) => void
}): JSX.Element {
  const [open, setOpen] = useState(false)
  const reduced = useReducedMotion()
  const root = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const away = (event: MouseEvent): void => {
      if (!root.current?.contains(event.target as Node)) setOpen(false)
    }
    const escape = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', away)
    document.addEventListener('keydown', escape)
    return () => {
      document.removeEventListener('mousedown', away)
      document.removeEventListener('keydown', escape)
    }
  }, [open])

  const choose = useCallback(
    (next: SubMode) => {
      setOpen(false)
      onSelect(next)
    },
    [onSelect],
  )

  const current = SUB_MODES.find((option) => option.value === subMode) ?? SUB_MODES[0]

  return (
    <div ref={root} className="relative">
      <button
        type="button"
        disabled={disabled}
        aria-label={`Study: ${current.label}`}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className="interactive flex items-center gap-1 rounded-lg px-1.5 py-0.5 text-micro text-aria-muted disabled:cursor-not-allowed disabled:opacity-40"
      >
        {/* Always dotted, unlike the mode picker. There is no "absence of a
            sub-mode" to avoid marking — you are always studying somehow, and
            which way is the most useful thing this strip can say. */}
        <span className="h-1 w-1 shrink-0 rounded-full bg-current" aria-hidden />
        {current.label}
        <span aria-hidden>▾</span>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 4, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 2, scale: 0.99 }}
            transition={still(TWEEN.rise, reduced)}
            className="glass-pop absolute bottom-full left-0 z-20 mb-1.5 w-64 overflow-hidden rounded-xl p-1.5"
          >
            {SUB_MODES.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => choose(option.value)}
                className={`interactive block w-full rounded-lg px-2 py-1.5 text-left ${
                  option.value === subMode ? 'bg-white/10' : ''
                }`}
              >
                <span className="block text-tiny text-aria-text">{option.label}</span>
                <span className="block text-micro leading-relaxed text-aria-faint">
                  {option.hint}
                </span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
