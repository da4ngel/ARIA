/** The transcript. Token-by-token while streaming (BUILD_SPEC §9 Phase 1). */

import { useEffect, useRef } from 'react'

import { Markdown } from '@/components/Markdown'
import type { Turn } from '@/hooks/useConversation'

function Bubble({ turn }: { turn: Turn }): JSX.Element {
  const isUser = turn.role === 'user'
  return (
    <div className={isUser ? 'flex justify-end' : 'flex justify-start'}>
      <div
        className={
          isUser
            ? 'max-w-[85%] rounded-2xl rounded-br-sm bg-white/10 px-3 py-2 text-sm'
            : 'max-w-[92%] rounded-2xl rounded-bl-sm bg-aria-panel px-3 py-2'
        }
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{turn.content}</p>
        ) : (
          <>
            <Markdown text={turn.content} />
            {turn.streaming && (
              <span className="ml-0.5 inline-block h-3 w-1.5 animate-pulse bg-aria-text align-middle" />
            )}
            {turn.error && <p className="mt-1 text-xs text-aria-bad">{turn.error}</p>}
            {turn.cancelled && <p className="mt-1 text-xs text-aria-muted">stopped</p>}
            {/* A failover is never silent: say who actually answered. */}
            {turn.note && <p className="mt-1 text-xs text-aria-warn">{turn.note}</p>}
            {turn.modelLabel && !turn.streaming && (
              <p className="mt-1 text-[10px] text-aria-muted" title={turn.routeReason}>
                {turn.modelLabel}
              </p>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export function ConversationView({ turns }: { turns: Turn[] }): JSX.Element {
  const endRef = useRef<HTMLDivElement>(null)
  const lastContent = turns[turns.length - 1]?.content

  // Follow the stream. Depends on the last turn's content so it scrolls as
  // tokens land, not only when a turn is added.
  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'end' })
  }, [turns.length, lastContent])

  if (turns.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-aria-muted">
        Say something.
      </div>
    )
  }

  return (
    <div className="flex-1 space-y-3 overflow-y-auto pr-1">
      {turns.map((turn) => (
        <Bubble key={turn.id} turn={turn} />
      ))}
      <div ref={endRef} />
    </div>
  )
}
