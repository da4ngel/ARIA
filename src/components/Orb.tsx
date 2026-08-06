/**
 * Aria's state, made visible (BUILD_SPEC §5, §9 Phase 1–2).
 *
 * The same orb appears large on an empty screen and small in the header once a
 * conversation starts. It is one element in both places, not two that crossfade
 * — `layoutId` lets Framer Motion tween position and size between the two mount
 * points, so it visibly travels into the header on the first message.
 *
 * **The reaction to a state change must be immediate.** Phase 2 budgets 300ms
 * from wake word to visible response, and an animation that had to finish its
 * current keyframe loop before acknowledging the change would spend most of
 * that on nothing. So state drives a spring that retargets instantly, and the
 * looping breath is a separate, purely decorative layer underneath.
 */

import { motion, useReducedMotion } from 'framer-motion'

import type { AssistantState } from '@/types/bridge'

export const ORB_LAYOUT_ID = 'aria-orb'

/** Per-state colour. The app's only saturated hues besides the semantic three. */
const HUE: Record<AssistantState, string> = {
  idle: '#9fb0c9',
  listening: '#5ec8e8',
  thinking: '#a78bfa',
  speaking: '#4ade80',
  acting: '#fbbf24',
}

/** Breathing: period in seconds, and how far the bloom swells. */
const BREATH: Record<AssistantState, { period: number; swell: number }> = {
  idle: { period: 5.5, swell: 1.06 },
  listening: { period: 1.4, swell: 1.22 },
  thinking: { period: 1.0, swell: 1.16 },
  speaking: { period: 0.8, swell: 1.2 },
  acting: { period: 1.6, swell: 1.12 },
}

/** Only states that represent work in progress get a moving rim. */
const SPINS: ReadonlySet<AssistantState> = new Set<AssistantState>(['thinking', 'acting'])

export interface OrbProps {
  state: AssistantState
  /** Diameter in px. 88+ reads as the hero; ~20 sits in the header. */
  size?: number
  /** False while the brain is down — the orb dims rather than lying. */
  connected?: boolean
  /** Opt out of the shared-element tween (tests, or a second orb on screen). */
  shared?: boolean
}

export function Orb({
  state,
  size = 20,
  connected = true,
  shared = true,
}: OrbProps): JSX.Element {
  const still = useReducedMotion()
  const hue = connected ? HUE[state] : '#5d6478'
  const breath = BREATH[state]
  const spin = SPINS.has(state) && connected && !still

  return (
    <motion.div
      {...(shared ? { layoutId: ORB_LAYOUT_ID } : {})}
      className="relative shrink-0"
      style={{ width: size, height: size, color: hue }}
      // The size change is the shared-element transition; a spring reads as the
      // orb moving into place rather than the layout jumping.
      transition={{ type: 'spring', stiffness: 260, damping: 30 }}
      title={connected ? `Aria is ${state}` : 'Aria is not connected'}
    >
      {/* Bloom — the soft light that makes it feel lit rather than drawn. */}
      <motion.span
        aria-hidden
        className="absolute rounded-full"
        style={{
          inset: `-${Math.round(size * 0.28)}px`,
          background: `radial-gradient(circle, ${hue}55 0%, ${hue}00 68%)`,
        }}
        animate={
          still
            ? { opacity: 0.5 }
            : { scale: [1, breath.swell, 1], opacity: [0.35, 0.72, 0.35] }
        }
        transition={{ duration: breath.period, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Core — off-centre highlight, so it reads as a sphere and not a disc. */}
      <motion.span
        aria-hidden
        className="absolute inset-0 rounded-full"
        style={{
          background: `radial-gradient(circle at 32% 28%, ${
            connected ? '#ffffffcc' : '#ffffff55'
          } 0%, ${hue} 46%, ${hue}bb 100%)`,
          boxShadow: `0 0 ${Math.round(size * 0.6)}px ${hue}66`,
        }}
        // Retargets the instant `state` changes — this is the 300ms path.
        initial={false}
        animate={{ opacity: connected ? 1 : 0.45 }}
        transition={{ type: 'spring', stiffness: 420, damping: 24 }}
      />

      {/* Rim — a thin arc that turns only while she is working, which is the
          difference between reading as "alive" and reading as "busy". */}
      {spin && (
        <motion.span
          aria-hidden
          className="absolute rounded-full"
          style={{
            inset: -Math.max(2, Math.round(size * 0.14)),
            border: `${size > 48 ? 2 : 1}px solid transparent`,
            borderTopColor: hue,
            borderRightColor: `${hue}66`,
          }}
          animate={{ rotate: 360 }}
          transition={{
            duration: state === 'thinking' ? 1.6 : 2.6,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      )}

      <span className="sr-only">{connected ? state : 'disconnected'}</span>
    </motion.div>
  )
}
