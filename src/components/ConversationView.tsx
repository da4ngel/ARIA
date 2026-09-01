/**
 * The transcript. Token-by-token while streaming (BUILD_SPEC §9 Phase 1).
 *
 * Assistant replies sit directly on the glass and user messages are raised.
 * That asymmetry does the work borders used to: you can tell who said what
 * without a line anywhere, and the reply — the thing you are actually here to
 * read — is the least decorated element on screen.
 */

import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import type { ReactNode } from 'react'

import { SPRING, TWEEN, still as stillMotion } from '@/styles/motion'
import { useCallback, useEffect, useRef, useState } from 'react'

import { Markdown } from '@/components/Markdown'
import { ToolCallCard } from '@/components/ToolCallCard'
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

function SpeakTurn({ text }: { text: string }): JSX.Element {
  const [state, setState] = useState<'idle' | 'speaking' | 'unavailable'>('idle')
  return (
    <button
      type="button"
      aria-label="Read this reply aloud"
      title={state === 'unavailable' ? 'No voice model installed' : 'Read aloud'}
      disabled={state !== 'idle'}
      onClick={() => {
        setState('speaking')
        void window.aria
          .call<{ ok: boolean }>('voice.speak', { text })
          .then((result) => setState(result.ok ? 'idle' : 'unavailable'))
          // The audio is already playing by the time this resolves — the call
          // returns when synthesis finishes, not when playback does — so a
          // failure here is about reaching the sidecar, not about the sound.
          .catch(() => setState('idle'))
      }}
      className="interactive rounded px-1.5 py-0.5 text-micro text-aria-faint hover:text-aria-text disabled:opacity-40"
    >
      {state === 'unavailable' ? 'no voice' : state === 'speaking' ? 'speaking…' : 'speak'}
    </button>
  )
}

function UserTurn({ turn }: { turn: Turn }): JSX.Element {
  const failed = (turn.attachments ?? []).filter((a) => !a.ok)
  return (
    <div className="flex flex-col items-end gap-1">
      <div className="raised rim max-w-[85%] rounded-2xl rounded-br-md px-3 py-2 text-small">
        <p className="whitespace-pre-wrap break-words">{turn.content}</p>
      </div>
      {/* A file she could not read, said where he is looking.
          Before this it went to `turn.attachments unreadable=[...]` in the
          sidecar log and nowhere else, so a skipped `.ppt` lecture showed up
          only as a vague answer. In the transcript rather than a toast, so a
          week later the history still explains why she never mentioned it —
          and the sidecar's message names the fix, not just the failure. */}
      {failed.map((attachment) => (
        <p key={attachment.name} className="max-w-[85%] text-right text-micro text-aria-warn">
          {attachment.summary}
        </p>
      ))}
    </div>
  )
}

/** Thumbs up/down on one answer — §9.7's label half.
 *
 *  The spec's upgrade path is a labelled dataset, not a bigger model: "log
 *  every routing decision with the provider, the resulting turn's latency and a
 *  user thumbs-up/down. After a few weeks you'll have a labelled dataset to
 *  tune the rules against." Nothing collected one until now.
 *
 *  Hidden until hover, like `CopyTurn` — an always-visible pair of buttons
 *  under every answer turns a conversation into a survey. A chosen thumb stays
 *  visible, or there would be no way to see what you had already said. */
function RateTurn({
  rating,
  onRate,
}: {
  rating?: 1 | -1
  onRate: (rating: 1 | -1) => void
}): JSX.Element {
  return (
    <span className="flex items-center gap-0.5">
      {([1, -1] as const).map((value) => {
        const chosen = rating === value
        return (
          <button
            key={value}
            type="button"
            onClick={() => onRate(value)}
            aria-pressed={chosen}
            aria-label={value === 1 ? 'Good answer' : 'Bad answer'}
            title={
              value === 1
                ? 'Good answer — helps her learn which model to use'
                : 'Bad answer — helps her learn which model to use'
            }
            className={`rounded p-0.5 transition-colors hover:bg-white/10 ${
              chosen ? 'text-aria-accent' : 'text-aria-faint'
            }`}
          >
            <svg
              viewBox="0 0 16 16"
              className={`h-3 w-3 ${value === -1 ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              strokeWidth="1.4"
              strokeLinejoin="round"
              aria-hidden
            >
              <path d="M4.5 14V7l3.2-5a1.6 1.6 0 0 1 2.4 1.9L9.2 6.6h3.1a1.4 1.4 0 0 1 1.4 1.7l-.9 4.4a1.6 1.6 0 0 1-1.6 1.3H4.5Z" />
              <path d="M4.5 7H2.4v7h2.1" />
            </svg>
          </button>
        )
      })}
    </span>
  )
}

function AssistantTurn({
  turn,
  state,
  onRate,
}: {
  turn: Turn
  state: AssistantState
  onRate?: (messageId: number, rating: 1 | -1) => void
}): JSX.Element {
  const tools = turn.toolCalls ?? []
  const waiting = turn.streaming && !turn.content
  // Something has to occupy the gap between send and first token, or the window
  // looks broken for the ~400ms it takes — but a tool card already says she is
  // busy, and "Thinking…" stacked on top of it says it twice.
  const placeholder = waiting && tools.length === 0

  return (
    <div className="group flex flex-col gap-1">
      {/* Above the reply, because that is the order it happened in: she acts,
          then tells you about it. */}
      {tools.map((call) => (
        // The step badge only earns its place once there is more than one
        // call to number — on an ordinary single-tool turn "Step 1" is
        // noise, not information.
        <ToolCallCard key={call.id} call={call} chained={tools.length > 1} />
      ))}

      {placeholder ? (
        <p className="text-small text-aria-faint">
          {state === 'thinking' ? 'Thinking…' : 'Working…'}
        </p>
      ) : waiting ? null : (
        // Size and colour come from `prose.ts` now, not from here. The old
        // `text-body` on this div was dead — `Markdown` set `text-small` over
        // it, so every reply rendered at 13px rather than the 15 this line
        // believed it was asking for. The caret moved into the component too,
        // where it can attach to the last element instead of starting a new
        // line beneath it.
        <Markdown text={turn.content} streaming={turn.streaming} />
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
            <SpeakTurn text={turn.content} />
            <CopyTurn text={turn.content} />
          </span>
        )}
        {!turn.streaming && turn.content && onRate && turn.messageId !== undefined && (
          <span
            className={`transition-opacity focus-within:opacity-100 group-hover:opacity-100 ${
              turn.rating ? 'opacity-100' : 'opacity-0'
            }`}
          >
            <RateTurn
              rating={turn.rating}
              onRate={(value) => onRate(turn.messageId as number, value)}
            />
          </span>
        )}
      </div>
    </div>
  )
}

export function ConversationView({
  turns,
  state = 'idle',
  onRate,
  question,
}: {
  turns: Turn[]
  state?: AssistantState
  onRate?: (messageId: number, rating: 1 | -1) => void
  /**
   * A question she is blocked on, rendered at the end of the flow.
   *
   * A slot rather than the props themselves: this component has no business
   * knowing what a question is, and `QuestionCard` stays independently
   * testable. It sits *inside* the scroller so it scrolls with the reply it
   * interrupts — a modal would be the `ConfirmDialog` treatment, and that
   * scrim exists because a permission lock is held, which is not the case
   * here.
   */
  question?: ReactNode
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
        // The *scroller* stays full width so the scrollbar sits at the
        // window edge where it belongs; only the content is capped.
        className="flex h-full flex-col items-center overflow-y-auto px-3 pb-2"
        style={{
          maskImage: 'linear-gradient(to bottom, transparent 0, #000 20px)',
          WebkitMaskImage: 'linear-gradient(to bottom, transparent 0, #000 20px)',
        }}
      >
        <div className="flex w-full max-w-[var(--reading)] flex-col gap-4">
        {turns.map((turn) =>
          turn.role === 'user' ? (
            <motion.div
              key={turn.id}
              initial={still ? false : { opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={stillMotion(SPRING.arrive, still)}
            >
              <UserTurn turn={turn} />
            </motion.div>
          ) : (
            // It used to be a bare div: a user message sprang in and the reply
            // it belongs to just appeared. Softer than the user's spring — the
            // reply is the thing being read, not the thing being sent.
            <motion.div
              key={turn.id}
              initial={still ? false : { opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={stillMotion(TWEEN.base, still)}
            >
              <AssistantTurn turn={turn} state={state} onRate={onRate} />
            </motion.div>
          ),
        )}
        {question}
        </div>
      </div>

      <AnimatePresence>
        {!following && (
          <motion.button
            type="button"
            initial={still ? false : { opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            transition={stillMotion(TWEEN.fast, still)}
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
