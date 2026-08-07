/**
 * The dialog that stands between her and something you cannot undo.
 *
 * The sidecar's agent loop is genuinely suspended while this is open — an
 * `asyncio.Future` waiting on the answer — and it denies itself after 120s.
 * So this is not a notification with buttons; it is the thing holding the
 * lock, and every decision below follows from that:
 *
 * - **Nothing is pre-selected and nothing is focused by default.** A stray
 *   Enter must not approve a deletion.
 * - **Escape denies**, because the safe answer should be the reflex one.
 * - **DANGER needs the tool's name typed.** A click is muscle memory; typing
 *   "delete_file" is not something you do by accident.
 * - **The arguments are shown in full**, because approving "delete a file"
 *   without seeing which file is not consent to anything.
 */

import { AnimatePresence, motion } from 'framer-motion'
import { useEffect, useState } from 'react'

export interface ConfirmRequest {
  request_id: string
  tool: string
  args: Record<string, unknown>
  tier: number
  rationale?: string
  /** True for DANGER: a click is not enough. */
  typed: boolean
}

interface Props {
  request: ConfirmRequest | null
  onRespond: (requestId: string, approved: boolean, remember: boolean) => void
}

const TIER_LABEL: Record<number, string> = {
  2: 'Changes your files',
  3: 'Cannot be undone',
}

export function ConfirmDialog({ request, onRespond }: Props): JSX.Element {
  const [confirmation, setConfirmation] = useState('')

  // A fresh request must never inherit the last one's typing.
  useEffect(() => setConfirmation(''), [request?.request_id])

  useEffect(() => {
    if (!request) return
    const onKey = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') {
        event.preventDefault()
        onRespond(request.request_id, false, false)
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [request, onRespond])

  const armed = !request?.typed || confirmation.trim() === request.tool

  return (
    <AnimatePresence>
      {request && (
        <motion.div
          className="absolute inset-0 z-50 flex items-center justify-center bg-black/55 px-4 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            role="alertdialog"
            aria-modal
            aria-label={`Confirm ${request.tool}`}
            className="raised rim w-full max-w-sm rounded-2xl p-4"
            initial={{ opacity: 0, y: 12, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.99 }}
            transition={{ type: 'spring', stiffness: 320, damping: 28 }}
          >
            <div className="flex items-center gap-2">
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  request.tier >= 3 ? 'bg-aria-bad' : 'bg-aria-warn'
                }`}
                aria-hidden
              />
              <span className="text-micro uppercase tracking-wide text-aria-muted">
                {TIER_LABEL[request.tier] ?? 'Needs permission'}
              </span>
            </div>

            <p className="mt-2 text-body font-medium">
              Let her run <span className="font-mono">{request.tool}</span>?
            </p>

            {request.rationale && (
              <p className="mt-1.5 text-small leading-relaxed text-aria-muted">
                {request.rationale}
              </p>
            )}

            {/* Approving "delete a file" without seeing which file is not
                consent to anything. */}
            {Object.keys(request.args).length > 0 && (
              <dl className="mt-3 space-y-1 rounded-lg bg-black/25 p-2.5 text-micro">
                {Object.entries(request.args).map(([key, value]) => (
                  <div key={key} className="flex gap-2">
                    <dt className="shrink-0 text-aria-faint">{key}</dt>
                    <dd className="min-w-0 break-all font-mono text-aria-text">
                      {typeof value === 'string' ? value : JSON.stringify(value)}
                    </dd>
                  </div>
                ))}
              </dl>
            )}

            {request.typed && (
              <label className="mt-3 block">
                <span className="text-micro text-aria-muted">
                  Type <span className="font-mono text-aria-text">{request.tool}</span> to allow it
                </span>
                <input
                  value={confirmation}
                  onChange={(e) => setConfirmation(e.target.value)}
                  spellCheck={false}
                  autoComplete="off"
                  className="mt-1 w-full rounded-lg bg-black/30 px-2.5 py-1.5 font-mono text-small text-aria-text ring-1 ring-white/10 focus:outline-none focus:ring-aria-accent/60"
                />
              </label>
            )}

            <div className="mt-4 flex items-center justify-end gap-2">
              {/* Only for the tier you can undo. "Always allow" on something
                  irreversible would defeat the point of asking. */}
              {request.tier < 3 && (
                <button
                  type="button"
                  onClick={() => onRespond(request.request_id, true, true)}
                  className="interactive mr-auto rounded-lg px-2 py-1.5 text-micro text-aria-faint hover:text-aria-text"
                >
                  Always allow this
                </button>
              )}
              <button
                type="button"
                onClick={() => onRespond(request.request_id, false, false)}
                className="interactive rounded-lg px-3 py-1.5 text-small text-aria-muted hover:text-aria-text"
              >
                Deny
              </button>
              <button
                type="button"
                disabled={!armed}
                onClick={() => onRespond(request.request_id, true, false)}
                className={`interactive rounded-lg px-3 py-1.5 text-small font-medium transition-colors ${
                  armed
                    ? request.tier >= 3
                      ? 'bg-aria-bad/90 text-white hover:bg-aria-bad'
                      : 'bg-aria-accent/90 text-aria-void hover:bg-aria-accent'
                    : 'cursor-not-allowed bg-white/5 text-aria-faint'
                }`}
              >
                {request.tier >= 3 ? 'Delete' : 'Allow'}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
