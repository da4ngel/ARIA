/**
 * What she actually did, shown where she did it.
 *
 * The sidecar has broadcast `tool.call` and `tool.result` since Phase 3 and
 * nothing consumed them, so a turn that opened an app looked exactly like a
 * turn that talked about opening one. That gap is also how "Opened Calculator"
 * followed by "I cannot run programs" went unnoticed for a whole phase.
 *
 * One line by default. This sits inside a conversation, and a JSON dump in the
 * middle of a reply is worse than no card at all — the arguments and the full
 * payload are a click away for when something looks wrong.
 */

import { useState } from 'react'

import type { ToolCall } from '@/hooks/useConversation'

export function ToolCallCard({
  call,
  chained = false,
}: {
  call: ToolCall
  /** True once a turn made more than one call — see `ConversationView`. Only
   *  then does a step number mean anything to look at. */
  chained?: boolean
}): JSX.Element {
  const [open, setOpen] = useState(false)
  const args = Object.entries(call.args)

  return (
    <div className="raised rim my-1 overflow-hidden rounded-lg text-micro">
      <button
        type="button"
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className="interactive flex w-full items-center gap-2 px-2 py-1.5 text-left"
      >
        <StateDot state={call.state} />
        {chained && call.step !== undefined && (
          <span
            className="shrink-0 rounded bg-white/5 px-1 font-mono tabular-nums text-aria-faint"
            title={`Step ${call.step + 1}`}
          >
            {call.step + 1}
          </span>
        )}
        <span className="shrink-0 font-mono text-aria-text">{call.tool}</span>

        {/* The most useful argument, inline. "open_app chrome" is the whole
            story for most calls and costs no extra row. */}
        {args.length > 0 && (
          <span className="min-w-0 flex-1 truncate text-aria-faint">
            {String(args[0][1])}
            {args.length > 1 && ` +${args.length - 1}`}
          </span>
        )}
        {args.length === 0 && <span className="flex-1" />}

        <span className="shrink-0 font-mono tabular-nums text-aria-faint">
          {call.state === 'running' ? <Waiting /> : formatDuration(call.durationMs)}
        </span>
        <span className="shrink-0 text-aria-faint" aria-hidden>
          {open ? '▾' : '▸'}
        </span>
      </button>

      {open && (
        <div className="border-t border-white/5 px-2 py-1.5">
          {args.length > 0 && (
            <dl className="space-y-0.5">
              {args.map(([key, value]) => (
                <div key={key} className="flex gap-2">
                  <dt className="shrink-0 text-aria-faint">{key}</dt>
                  <dd className="min-w-0 flex-1 break-all font-mono text-aria-muted">
                    {typeof value === 'string' ? value : JSON.stringify(value)}
                  </dd>
                </div>
              ))}
            </dl>
          )}
          {call.summary && (
            <p
              className={`mt-1.5 whitespace-pre-wrap ${
                call.state === 'failed' ? 'text-aria-bad' : 'text-aria-muted'
              }`}
            >
              {call.summary}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

/** Colour carries meaning here, so it is one of the few places saturation is
 *  allowed — and it is paired with a title, not left to colour alone. */
function StateDot({ state }: { state: ToolCall['state'] }): JSX.Element {
  const look = {
    running: ['bg-aria-acting', 'Running'],
    ok: ['bg-aria-ok', 'Done'],
    failed: ['bg-aria-bad', 'Failed'],
  }[state]
  return (
    <span
      className={`h-1.5 w-1.5 shrink-0 rounded-full ${look[0]} ${
        state === 'running' ? 'animate-pulse' : ''
      }`}
      title={look[1]}
      role="img"
      aria-label={look[1]}
    />
  )
}

/** A tier-2 call spends its whole "running" time waiting on the confirmation
 *  dialog, so this deliberately does not count seconds at the user. */
function Waiting(): JSX.Element {
  return <span className="text-aria-acting">running…</span>
}

function formatDuration(ms?: number): string {
  if (ms === undefined) return ''
  return ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${ms}ms`
}
