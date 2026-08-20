/**
 * The sheet every panel sits on.
 *
 * Panels used to be `absolute inset-0 bg-aria-void/85` — a flat scrim painted
 * over the whole window, which is why nothing but the main pane read as glass.
 * This is a floating sheet instead: blurred, edged, shadowed, sized to its
 * content, with the conversation visible and out of focus behind it.
 *
 * One component so all four panels agree on the escape key, the backdrop
 * click, and where the close button is.
 */

import { motion, useReducedMotion } from 'framer-motion'

import { TWEEN, still } from '@/styles/motion'
import { useEffect, useRef } from 'react'

export function Panel({
  title,
  onClose,
  children,
  width = 'max-w-md',
}: {
  title: string
  onClose: () => void
  children: React.ReactNode
  width?: string
}): JSX.Element {
  const reduced = useReducedMotion()
  const sheet = useRef<HTMLDivElement>(null)

  // App.tsx owns Escape globally so it can decide what is on top; this only
  // handles focus. Nothing inside is focused on open — a panel that steals
  // focus into a text field swallows the next thing typed.
  useEffect(() => {
    sheet.current?.focus()
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={still(TWEEN.fast, reduced)}
      className="absolute inset-0 z-30 flex items-center justify-center p-4"
      // A click on the backdrop closes; a click on the sheet must not bubble
      // back out and close it again.
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div className="absolute inset-0 bg-black/35 backdrop-blur-[3px]" aria-hidden />

      <motion.div
        ref={sheet}
        role="dialog"
        aria-modal="false"
        aria-label={title}
        tabIndex={-1}
        initial={{ opacity: 0, y: 8, scale: 0.985 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 4, scale: 0.99 }}
        transition={still(TWEEN.emphasis, reduced)}
        className={`glass-pop sheen relative flex max-h-full w-full flex-col overflow-hidden rounded-2xl outline-none ${width}`}
      >
        <header className="flex shrink-0 items-center justify-between gap-2 px-4 pb-2 pt-3">
          <h2 className="truncate text-small font-strong text-aria-text">{title}</h2>
          <button
            type="button"
            aria-label="Close"
            title="Close (Esc)"
            onClick={onClose}
            className="interactive grid h-6 w-6 shrink-0 place-items-center rounded-md text-aria-muted hover:text-aria-text"
          >
            <svg
              width="12"
              height="12"
              viewBox="0 0 12 12"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.4"
              strokeLinecap="round"
              aria-hidden
            >
              <path d="M3 3l6 6M9 3l-6 6" />
            </svg>
          </button>
        </header>

        <div className="min-h-0 flex-1 overflow-y-auto px-4 pb-4">{children}</div>
      </motion.div>
    </motion.div>
  )
}
