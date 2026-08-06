/**
 * Animated state indicator (BUILD_SPEC §5, §9 Phase 1).
 *
 * Reflects `state.change` from the sidecar. Phase 2 replaces the listening and
 * speaking variants with real waveform and amplitude animations; Phase 1 just
 * needs idle / thinking to read differently at a glance.
 */

import { motion } from 'framer-motion'

import type { AssistantState } from '@/types/bridge'

const RING: Record<AssistantState, string> = {
  idle: 'bg-aria-muted/40',
  listening: 'bg-sky-400/70',
  thinking: 'bg-violet-400/70',
  speaking: 'bg-emerald-400/70',
  acting: 'bg-amber-400/70',
}

/** Per-state motion. Idle breathes slowly; thinking pulses with intent. */
const ANIMATION: Record<AssistantState, { scale: number[]; duration: number }> = {
  idle: { scale: [1, 1.06, 1], duration: 4 },
  listening: { scale: [1, 1.18, 1], duration: 1.1 },
  thinking: { scale: [1, 1.12, 1], duration: 0.9 },
  speaking: { scale: [1, 1.14, 1], duration: 0.7 },
  acting: { scale: [1, 1.1, 1], duration: 1.4 },
}

export function Orb({ state }: { state: AssistantState }): JSX.Element {
  const anim = ANIMATION[state]
  return (
    <div className="relative h-6 w-6 shrink-0" title={`Aria is ${state}`}>
      <motion.span
        className={`absolute inset-0 rounded-full blur-[6px] ${RING[state]}`}
        animate={{ scale: anim.scale, opacity: [0.55, 0.9, 0.55] }}
        transition={{ duration: anim.duration, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.span
        className={`absolute inset-1 rounded-full ${RING[state]}`}
        animate={{ scale: anim.scale }}
        transition={{ duration: anim.duration, repeat: Infinity, ease: 'easeInOut' }}
      />
      <span className="sr-only">{state}</span>
    </div>
  )
}
