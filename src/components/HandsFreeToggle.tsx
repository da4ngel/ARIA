/**
 * The always-listening switch, and the fact that it is on.
 *
 * Deliberately not a quiet icon among other quiet icons. While this is on the
 * microphone is open continuously and Windows shows its own indicator; the app
 * saying so too is the honest thing, and it makes turning it off a single
 * obvious click rather than a hunt through settings.
 */

import { motion } from 'framer-motion'

interface Props {
  available: boolean
  active: boolean
  /** 0..1, for the pulse. Decorative — the decision is the sidecar's. */
  level: number
  disabled: boolean
  onToggle: () => void
}

export function HandsFreeToggle({
  available,
  active,
  level,
  disabled,
  onToggle,
}: Props): JSX.Element | null {
  // Absent weights: no control at all rather than one that cannot work. The
  // sidecar logs what to run, and push-to-talk is unaffected.
  if (!available) return null

  return (
    <button
      type="button"
      role="switch"
      aria-checked={active}
      aria-label="Listen for hey Jarvis"
      title={
        active
          ? 'Listening for "hey Jarvis" — the microphone is open. Click to stop.'
          : 'Listen for "hey Jarvis" (keeps the microphone open)'
      }
      disabled={disabled}
      onClick={onToggle}
      className={`interactive flex h-7 shrink-0 items-center gap-1.5 rounded-full px-2 text-micro transition-colors disabled:cursor-not-allowed disabled:opacity-30 ${
        active ? 'bg-aria-listening/15 text-aria-listening' : 'text-aria-faint hover:text-aria-text'
      }`}
    >
      <span className="relative grid h-3 w-3 place-items-center">
        {active && (
          <motion.span
            aria-hidden
            className="absolute inset-0 rounded-full bg-aria-listening/40"
            animate={{ scale: 1 + Math.min(1, level) * 1.4, opacity: 0.55 - level * 0.3 }}
            transition={{ type: 'spring', stiffness: 700, damping: 30 }}
          />
        )}
        <svg
          width="11"
          height="11"
          viewBox="0 0 14 14"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.4"
          strokeLinecap="round"
          aria-hidden
          className="relative"
        >
          <rect x="5" y="1.6" width="4" height="7" rx="2" />
          <path d="M2.8 6.6a4.2 4.2 0 0 0 8.4 0M7 10.8v1.6" />
        </svg>
      </span>
      {active && <span className="font-medium">Listening</span>}
    </button>
  )
}
