/**
 * The keyboard map, on demand.
 *
 * It used to live permanently in the footer, which is a row spent on something
 * you stop reading after the first day. Behind '?' it stays discoverable and
 * stops costing space.
 */

import { motion } from 'framer-motion'
import { useEffect } from 'react'

const KEYS: [string, string][] = [
  ['Ctrl + Space', 'Show or hide Aria'],
  ['Enter', 'Send'],
  ['Shift + Enter', 'New line'],
  ['Esc', 'Stop generating, or close this'],
  ['Ctrl + K', 'History'],
  ['Ctrl + N', 'New chat'],
  ['Ctrl + E', 'Expand or shrink the window'],
  ['?', 'This list'],
]

export function Shortcuts({ onClose }: { onClose: () => void }): JSX.Element {
  useEffect(() => {
    const onKey = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <motion.div
      className="absolute inset-0 z-30 flex flex-col bg-aria-void/80 p-4 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.14 }}
    >
      <div className="flex items-center justify-between">
        <h2 className="text-small font-semibold">Shortcuts</h2>
        <button
          type="button"
          onClick={onClose}
          className="interactive rounded px-2 py-0.5 text-tiny text-aria-muted hover:text-aria-text"
        >
          Close
        </button>
      </div>

      <dl className="mt-3 flex flex-col gap-0.5 overflow-y-auto">
        {KEYS.map(([key, what]) => (
          <div
            key={key}
            className="flex items-center justify-between gap-3 rounded-md px-1.5 py-1.5"
          >
            <dt className="shrink-0 font-mono text-micro text-aria-text">{key}</dt>
            <dd className="truncate text-right text-tiny text-aria-muted">{what}</dd>
          </div>
        ))}
      </dl>
    </motion.div>
  )
}
