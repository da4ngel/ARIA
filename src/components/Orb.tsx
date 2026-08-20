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
import { SPRING, still } from '@/styles/motion'
import { COLORS, HUES } from '@/styles/tokens'

export const ORB_LAYOUT_ID = 'aria-orb'

/** Per-state colour, from the one place they are defined.
 *
 *  This used to be a literal copy of `tailwind.config.js`'s values, and the
 *  two canvases carried a third and fourth copy as hand-derived RGB triples.
 *  Four copies of five colours is four chances for a recolour to half-apply. */
const HUE = HUES as Record<AssistantState, string>

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
  /** Live audio level, 0..1. Drives a small swell on top of the breath so the
   *  orb reacts to a voice rather than to a timer. Ignored when idle: a
   *  microphone that is open but not being spoken to should look calm. */
  level?: number
}

export function Orb({
  state,
  size = 20,
  connected = true,
  shared = true,
  level = 0,
}: OrbProps): JSX.Element {
  const reduced = useReducedMotion()
  const hue = connected ? HUE[state] : COLORS.faint
  const breath = BREATH[state]
  const spin = SPINS.has(state) && connected && !reduced

  // Capped well below the breath's own swell: this is a voice showing through
  // the animation, not a level meter competing with it.
  const reactive = reduced || !connected ? 0 : Math.min(1, Math.max(0, level))
  const voiced = state === 'listening' || state === 'speaking'
  const swell = voiced ? 1 + reactive * 0.18 : 1

  return (
    <motion.div
      {...(shared ? { layoutId: ORB_LAYOUT_ID } : {})}
      className="relative shrink-0"
      style={{ width: size, height: size, color: hue }}
      // The size change is the shared-element transition; a spring reads as the
      // orb moving into place rather than the layout jumping.
      transition={SPRING.shared}
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
          reduced
            ? { opacity: 0.5 }
            : { scale: [1, breath.swell, 1], opacity: [0.35, 0.72, 0.35] }
        }
        transition={{ duration: breath.period, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Core — off-centre highlight, so it reads as a sphere and not a disc.
          The colour **fades** between states rather than cutting. This is the
          app's signature element and it used to snap: idle to thinking was an
          instant swap from grey-blue to violet, which reads as a glitch
          rather than as a change of mind. */}
      <motion.span
        aria-hidden
        className="absolute inset-0 rounded-full transition-[background,box-shadow] duration-300 ease-out"
        style={{
          background: `radial-gradient(circle at 32% 28%, ${
            connected ? '#ffffffcc' : '#ffffff55'
          } 0%, ${hue} 46%, ${hue}bb 100%)`,
          boxShadow: `0 0 ${Math.round(size * 0.6)}px ${hue}66`,
        }}
        // Retargets the instant `state` changes — this is the 300ms path.
        initial={false}
        animate={{ opacity: connected ? 1 : 0.45, scale: swell }}
        // Stiff and lightly damped: a voice's envelope moves in tens of
        // milliseconds, and a slow spring would smear syllables into a hum.
        transition={still(SPRING.reactive, reduced)}
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
