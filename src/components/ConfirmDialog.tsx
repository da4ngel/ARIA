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

/** A batch of file moves, worked out before the user is asked about it.
 *
 *  BUILD_SPEC §7.2: "if the agent wants to move 30 files, emit one
 *  confirm.request describing the batch, not 30. Include the full file list."
 *  `args` alone cannot do that — for `organize_folder` it is `{path,
 *  strategy}`, which says nothing about what is about to happen. */
export interface MovePlan {
  kind: 'move_plan'
  folder: string
  strategy: string
  count: number
  skipped: number
  folders: string[]
  moves: Array<{ from: string; to: string }>
  truncated: number
}

/** A screenshot, taken before the user is even asked, so the dialog shows a
 *  real frame rather than a promise of one — `capture_screen`'s `preview`.
 *  `thumbnail_b64` is a small, separately-downscaled copy for a fast
 *  round-trip through RPC; the full frame that actually reaches the vision
 *  model never travels over this channel at all. */
export interface ImagePreview {
  kind: 'image_preview'
  thumbnail_b64: string
  provider: string
}

/** `type_text`'s preview — **which window**, and how much text.
 *
 *  The window is the part being approved and the part that used to be
 *  missing. `type_text` chose its target by reading the foreground window at
 *  execution time, i.e. *after* this dialog, so the text could land wherever
 *  the user happened to be looking when they clicked Allow. It now claims
 *  the window here, at preview time, and `window` is that claim — the same
 *  "the plan you approve is the plan that runs" guarantee `move_plan` makes
 *  about a file list.
 *
 *  It also retires the wall of raw argument text: an essay rendered into the
 *  fallback `<dl>` is what once pushed Allow and Deny off the bottom of the
 *  dialog and left Escape — which denies — as the only reachable answer. */
export interface TypeTarget {
  kind: 'type_target'
  window: string
  chars: number
  method: 'paste' | 'keystrokes'
  excerpt: string
  truncated: boolean
  is_aria: boolean
}

export type ToolPreview = MovePlan | ImagePreview | TypeTarget

export interface ConfirmRequest {
  request_id: string
  tool: string
  args: Record<string, unknown>
  tier: number
  rationale?: string
  /** True for DANGER: a click is not enough. */
  typed: boolean
  /** What the tool worked out it would do. Absent for tools that have no
   *  preview, and null when computing one failed — the dialog still appears
   *  either way, showing the raw arguments as it always did. */
  preview?: ToolPreview | null
  /** True only when this call would not normally have asked at all — this
   *  tool is AUTO or SAFE, and it is here because §11 escalated it: the step
   *  before it in the agent loop read something from outside the machine
   *  (a search result, a fetched page), and the very next call is treated as
   *  CONFIRM regardless of its own tier. Without this the dialog looks like a
   *  bug — "why is opening an app suddenly asking me?" */
  escalated?: boolean
}

/** Just the file name, for a column of paths that all share a folder. */
function leaf(path: string): string {
  const parts = path.split(/[\\/]/)
  return parts[parts.length - 1] || path
}

/** The last two segments — "Images/holiday.png" — which is the part that is
 *  actually new information about where a file is going. */
function tail(path: string): string {
  const parts = path.split(/[\\/]/).filter(Boolean)
  return parts.slice(-2).join('/')
}

function MovePlanView({ plan }: { plan: MovePlan }): JSX.Element {
  return (
    <div className="mt-3 rounded-lg bg-black/25 p-2.5">
      <p className="text-micro text-aria-muted">
        <span className="text-aria-text">{plan.count}</span>{' '}
        {plan.count === 1 ? 'file' : 'files'} into{' '}
        <span className="text-aria-text">{plan.folders.length || 'their original'}</span>{' '}
        {plan.folders.length === 1 ? 'folder' : 'folders'}
        {plan.skipped > 0 && <span className="text-aria-faint"> · {plan.skipped} left alone</span>}
      </p>

      {plan.folders.length > 0 && (
        <p className="mt-1 text-micro text-aria-faint">{plan.folders.join(' · ')}</p>
      )}

      {/* Scrolls rather than growing: the dialog must stay a dialog, and a
          plan taller than the window is one nobody reads before clicking. */}
      <ul className="mt-2 max-h-40 space-y-0.5 overflow-y-auto font-mono text-micro">
        {plan.moves.map((move) => (
          <li key={move.from} className="flex items-baseline gap-1.5">
            <span className="min-w-0 flex-1 truncate text-aria-text" title={move.from}>
              {leaf(move.from)}
            </span>
            <span aria-hidden className="text-aria-faint">
              →
            </span>
            <span className="min-w-0 flex-1 truncate text-aria-muted" title={move.to}>
              {tail(move.to)}
            </span>
          </li>
        ))}
      </ul>

      {plan.truncated > 0 && (
        <p className="mt-1.5 text-micro text-aria-faint">and {plan.truncated} more</p>
      )}
    </div>
  )
}

/** `capture_screen`'s preview — what's about to be sent, and to whom. The
 *  thumbnail is the point: approving "let her see the screen" without
 *  seeing what the screen currently shows is not really consent to it. */
function ImagePreviewView({ preview }: { preview: ImagePreview }): JSX.Element {
  return (
    <div className="mt-3 rounded-lg bg-black/25 p-2.5">
      <img
        src={`data:image/jpeg;base64,${preview.thumbnail_b64}`}
        alt="Screen preview"
        className="w-full rounded-md ring-1 ring-white/10"
      />
      <p className="mt-1.5 text-micro text-aria-faint">
        Sent to <span className="text-aria-muted">{preview.provider}</span> to describe it.
      </p>
    </div>
  )
}

/** Where the text is going, then what it is. Window first and in the
 *  heading position, because that is the question this dialog exists to
 *  answer — reading the essay tells you nothing about which app receives it. */
function TypeTargetView({ preview }: { preview: TypeTarget }): JSX.Element {
  return (
    <div className="mt-3 rounded-lg bg-black/25 p-2.5">
      <p className="text-tiny text-aria-text">
        Into <span className="font-strong">{preview.window}</span>
      </p>
      <p className="mt-0.5 text-micro text-aria-faint">
        {preview.chars.toLocaleString()} characters,{' '}
        {preview.method === 'paste' ? 'pasted in one go' : 'typed out'}
      </p>
      {preview.is_aria && (
        <p className="mt-1.5 text-micro text-aria-bad">
          That is my own window — open or focus the app you want this in first.
        </p>
      )}
      <pre className="mt-2 max-h-40 overflow-y-auto whitespace-pre-wrap break-words font-mono text-micro text-aria-muted">
        {preview.excerpt}
        {preview.truncated ? '…' : ''}
      </pre>
    </div>
  )
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
          // A heavier scrim than the panels use, and deliberately so: this one
          // holds a lock in the sidecar, and everything behind it is not
          // merely covered but genuinely unreachable until it is answered.
          className="absolute inset-0 z-50 flex items-center justify-center bg-black/55 px-4 backdrop-blur-[3px]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            role="alertdialog"
            aria-modal
            aria-label={`Confirm ${request.tool}`}
            className="glass-pop sheen relative w-full max-w-sm rounded-2xl p-4"
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

            {request.escalated && (
              <p className="mt-1.5 rounded-lg bg-aria-warn/10 px-2.5 py-1.5 text-micro leading-relaxed text-aria-warn">
                This wouldn&apos;t normally ask — it&apos;s asking because the
                step before it read something from outside this machine.
              </p>
            )}

            {request.rationale && (
              <p className="mt-1.5 text-small leading-relaxed text-aria-muted">
                {request.rationale}
              </p>
            )}

            {/* A preview replaces the argument list rather than sitting
                beside it: `{path: "downloads", strategy: "by_type"}` under a
                list of the actual moves is noise, and it is the moves (or
                the screen) that are being agreed to. Dispatched on `.kind`
                because a dialog can be asked to approve either shape. */}
            {request.preview?.kind === 'move_plan' && <MovePlanView plan={request.preview} />}
            {request.preview?.kind === 'image_preview' && (
              <ImagePreviewView preview={request.preview} />
            )}
            {request.preview?.kind === 'type_target' && (
              <TypeTargetView preview={request.preview} />
            )}
            {/* Approving "delete a file" without seeing which file is not
               consent to anything. */}
            {/* Scrolls rather than growing — the same reason `MovePlanView`
                caps its own list. `type_text` surfaced this: a long string
                argument (an essay) with no cap pushed Allow/Deny off the
                bottom of the dialog, so the only reachable answer was
                Escape — which denies. `whitespace-pre-wrap`, not `break-all`
                alone, so a multi-line value reads as its own lines rather
                than one run-on wall of text. */}
            {!request.preview && Object.keys(request.args).length > 0 && (
              <dl className="mt-3 max-h-48 space-y-1 overflow-y-auto rounded-lg bg-black/25 p-2.5 text-micro">
                {Object.entries(request.args).map(([key, value]) => (
                  <div key={key} className="flex gap-2">
                    <dt className="shrink-0 text-aria-faint">{key}</dt>
                    <dd className="min-w-0 whitespace-pre-wrap break-all font-mono text-aria-text">
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
