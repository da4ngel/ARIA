/**
 * The transcript. Token-by-token while streaming (BUILD_SPEC §9 Phase 1).
 *
 * Assistant replies sit directly on the glass and user messages are raised.
 * That asymmetry does the work borders used to: you can tell who said what
 * without a line anywhere, and the reply — the thing you are actually here to
 * read — is the least decorated element on screen.
 */

import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import { useCallback, useEffect, useRef, useState } from 'react'

import { Markdown } from '@/components/Markdown'
import type { Turn } from '@/hooks/useConversation'
import type { AssistantState } from '@/types/bridge'

/** How close to the bottom still counts as "following along", in px. */
const FOLLOW_THRESHOLD = 64

function CopyTurn({ text }: { text: string }): JSX.Element {
  const [copied, setCopied] = useState(false)
  return (
    <button
      type="button"
      aria-label="Copy reply"
      onClick={() => {
        void navigator.clipboard
          .writeText(text)
          .then(() => {
            setCopied(true)
            setTimeout(() => setCopied(false), 1200)
          })
          .catch(() => setCopied(false))
      }}
      className="interactive rounded px-1.5 py-0.5 text-micro text-aria-faint hover:text-aria-text"
    >
      {copied ? 'copied' : 'copy'}
    </button>
  )
}

function UserTurn({ turn }: { turn: Turn }): JSX.Element {
  return (
    <div className="flex justify-end">
      <div className="raised rim max-w-[85%] rounded-2xl rounded-br-md px-3 py-2 text-small">
        <p className="whitespace-pre-wrap break-words">{turn.content}</p>
      </div>
    </div>
  )
}

function AssistantTurn({ turn, state }: { turn: Turn; state: AssistantState }): JSX.Element {
  const thinking = turn.streaming && !turn.content
  return (
    <div className="group flex flex-col gap-1">
      {thinking ? (
        // Something has to occupy the gap between send and first token, or the
        // window looks broken for the ~400ms it takes.
        <p className="text-small text-aria-faint">
          {state === 'thinking' ? 'Thinking…' : 'Working…'}
        </p>
      ) : (
        <div className="text-body">
          <Markdown text={turn.content} />
          {turn.streaming && (
            <span
              aria-hidden
              className="ml-0.5 inline-block h-[1em] w-[2px] translate-y-[0.15em] animate-caret bg-aria-accent align-middle"
            />
          )}
        </div>
      )}

      {turn.error && <p className="text-tiny text-aria-bad">{turn.error}</p>}
      {turn.cancelled && <p className="text-tiny text-aria-faint">stopped</p>}
      {/* A failover is never silent: say who actually answered. */}
      {turn.note && <p className="text-tiny text-aria-warn">{turn.note}</p>}

      <div className="flex h-4 items-center gap-1.5">
        {turn.modelLabel && (
          <span
            className="font-mono text-micro text-aria-faint"
            title={turn.routeReason}
          >
            {turn.modelLabel}
          </span>
        )}
        {!turn.streaming && turn.content && (
          <span className="opacity-0 transition-opacity focus-within:opacity-100 group-hover:opacity-100">
            <CopyTurn text={turn.content} />
          </span>
        )}
      </div>
    </div>
  )
}

export function ConversationView({
  turns,
  state = 'idle',
}: {
  turns: Turn[]
  state?: AssistantState
}): JSX.Element {
  const still = useReducedMotion()
  const scroller = useRef<HTMLDivElement>(null)
  const [following, setFollowing] = useState(true)
  const lastContent = turns[turns.length - 1]?.content

  const atBottom = useCallback((): boolean => {
    const el = scroller.current
    if (!el) return true
    return el.scrollHeight - el.scrollTop - el.clientHeight < FOLLOW_THRESHOLD
  }, [])

  /** jsdom has no `Element.scrollTo`, and a missing scroll API is never worth
   *  throwing over — the transcript still renders, it just does not follow. */
  const scrollToEnd = useCallback((): void => {
    const el = scroller.current
    if (typeof el?.scrollTo !== 'function') return
    el.scrollTo({ top: el.scrollHeight, behavior: still ? 'auto' : 'smooth' })
  }, [still])

  // Follow the stream, but only while the reader is already at the bottom.
  // Scrolling up to re-read an earlier answer used to be yanked back on the
  // next token, which made a long reply impossible to read while it arrived.
  useEffect(() => {
    if (!following) return
    scrollToEnd()
  }, [turns.length, lastContent, following, scrollToEnd])

  return (
    <div className="relative min-h-0 flex-1">
      {/* Messages scroll under the header, and a hard cut there reads as a
          rendering bug — a half-line of text sliced by the title bar. The mask
          fades the first 20px instead, which is also what makes the panel feel
          like one continuous surface rather than stacked boxes. */}
      <div
        ref={scroller}
        onScroll={() => setFollowing(atBottom())}
        className="flex h-full flex-col gap-4 overflow-y-auto px-3 pb-2"
        style={{
          maskImage: 'linear-gradient(to bottom, transparent 0, #000 20px)',
          WebkitMaskImage: 'linear-gradient(to bottom, transparent 0, #000 20px)',
        }}
      >
        {turns.map((turn) =>
          turn.role === 'user' ? (
            <motion.div
              key={turn.id}
              initial={still ? false : { opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ type: 'spring', stiffness: 420, damping: 34 }}
            >
              <UserTurn turn={turn} />
            </motion.div>
          ) : (
            <div key={turn.id}>
              <AssistantTurn turn={turn} state={state} />
            </div>
          ),
        )}
      </div>

      <AnimatePresence>
        {!following && (
          <motion.button
            type="button"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            onClick={() => {
              setFollowing(true)
              scrollToEnd()
            }}
            className="raised rim-strong absolute bottom-2 left-1/2 -translate-x-1/2 rounded-full px-2.5 py-1 text-micro text-aria-muted backdrop-blur hover:text-aria-text"
          >
            Jump to latest
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  )
}
