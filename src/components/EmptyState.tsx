/**
 * What you see before you have said anything.
 *
 * The orb is the subject here, not decoration: this is the screen you speak to
 * once Phase 2 lands, so it gets the centre and the size. The suggestions are
 * chosen to show what she is actually good at — a local fact, something that
 * routes to cloud, and something she will decline — rather than to flatter.
 */

import { motion, useReducedMotion } from 'framer-motion'

import { Orb } from '@/components/Orb'
import type { AssistantState } from '@/types/bridge'

const SUGGESTIONS = [
  'What can you do?',
  'Explain what a KV cache is',
  'Draft a short reply declining a meeting',
] as const

export function EmptyState({
  state,
  connected,
  onPick,
  level = 0,
}: {
  state: AssistantState
  connected: boolean
  onPick: (text: string) => void
  /** Live audio level, 0..1. The hero orb is 92px, where a voice reacting to
   *  the room is the whole point of an always-listening mode. */
  level?: number
}): JSX.Element {
  const still = useReducedMotion()

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 px-6 pb-4">
      <Orb state={state} size={92} connected={connected} level={level} />

      <motion.div
        className="flex flex-col items-center gap-1.5 text-center"
        initial={still ? false : { opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.12, duration: 0.3 }}
      >
        {/* `text-hero` existed in the scale with zero uses. A 28px display line
            is exactly what a clean empty state wants, and `font-display` is the
            optical size Segoe UI Variable draws for that size — the reason large
            type here used to look soft. */}
        <h1 className="font-display text-hero font-strong tracking-tightest text-aria-text">
          Aria
        </h1>
        <p className="text-tiny text-aria-muted">
          {connected ? 'Running on this machine' : 'Waiting for the brain to start'}
        </p>
      </motion.div>

      <motion.div
        className="flex w-full max-w-xs flex-col gap-1.5"
        initial={still ? false : { opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.3 }}
      >
        {SUGGESTIONS.map((text) => (
          <button
            key={text}
            type="button"
            disabled={!connected}
            onClick={() => onPick(text)}
            className="raised rim interactive rounded-xl px-3 py-2 text-left text-tiny text-aria-muted hover:text-aria-text disabled:cursor-not-allowed disabled:opacity-40"
          >
            {text}
          </button>
        ))}
      </motion.div>
    </div>
  )
}
