/**
 * What has been happening — today's usage, why each turn went where it did,
 * and the reminders that are waiting.
 *
 * Every number here comes from `routing_log` and `tool_log`, which have been
 * recording since Phase 5 and Phase 1 with no way to look at them. The one
 * genuinely new piece of data is the token counts, which every provider has
 * been reporting all along and which nothing read until now.
 *
 * **The cost figure says "estimated" everywhere and that is not a hedge.** The
 * tokens are real; the rates are a hand-maintained table in
 * `providers/pricing.py` carrying the date it was true. Turns the table does
 * not cover are counted and shown rather than absorbed into the total.
 */

import { useState } from 'react'

import { Panel } from '@/components/Panel'
import { explainStage, useActivity } from '@/hooks/useActivity'
import type {
  Reminder,
  ToolRecord,
  TurnRecord,
  UndoEntry,
  UsageReport,
} from '@/types/bridge'

function whenever(iso: string): string {
  const at = new Date(iso.endsWith('Z') ? iso : `${iso}Z`)
  if (Number.isNaN(at.getTime())) return iso
  return at.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

function clock(iso: string): string {
  const at = new Date(iso.endsWith('Z') ? iso : `${iso}Z`)
  if (Number.isNaN(at.getTime())) return iso
  return at.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}

function thousands(n: number): string {
  return n.toLocaleString()
}

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }): JSX.Element {
  return (
    <div className="rim raised rounded-xl px-3 py-2">
      <span className="block text-micro text-aria-muted">{label}</span>
      <span className="block text-body font-strong text-aria-text">{value}</span>
      {hint && <span className="block text-micro text-aria-faint">{hint}</span>}
    </div>
  )
}

function Today({ usage }: { usage: UsageReport }): JSX.Element {
  const counted = usage.turns - usage.uncounted
  return (
    <section className="mb-4">
      <div className="grid grid-cols-2 gap-2">
        <Stat
          label="Turns today"
          value={String(usage.turns)}
          hint={`${usage.local_turns} local · ${usage.cloud_turns} cloud`}
        />
        <Stat
          label="Tokens"
          value={`${thousands(usage.prompt_tokens)} in`}
          hint={`${thousands(usage.completion_tokens)} out${
            usage.uncounted > 0 ? ` · ${usage.uncounted} turns uncounted` : ''
          }`}
        />
      </div>
      <div className="rim raised mt-2 rounded-xl px-3 py-2">
        <span className="block text-micro text-aria-muted">Estimated cost</span>
        <span className="block text-body font-strong text-aria-text">
          ${usage.estimated_usd.toFixed(4)}
        </span>
        {/* **The two numbers that stop this being a false total.** Turns no
            rate covers, and turns nobody counted tokens for. */}
        <span className="block text-micro text-aria-faint">
          rates as of {usage.prices_as_of}
          {usage.unpriced_turns > 0 && ` · ${usage.unpriced_turns} turns unpriced`}
        </span>
        {usage.unpriced_turns > 0 && (
          <p className="mt-1 text-micro text-aria-muted">
            Add rates for those models in <code className="text-aria-dim">providers/pricing.py</code>{' '}
            and this total stops being short.
          </p>
        )}
      </div>
      {counted > 0 && usage.models.length > 0 && (
        <ul className="mt-2 space-y-1">
          {usage.models.map((row) => (
            <li
              key={`${row.provider}/${row.model}`}
              className="flex items-baseline justify-between gap-2 text-micro"
            >
              <span className="truncate text-aria-dim">{row.model}</span>
              <span className="shrink-0 text-aria-faint">
                {row.turns} · {thousands(row.prompt_tokens + row.completion_tokens)} tok
                {row.estimated_usd === null ? ' · unpriced' : ` · $${row.estimated_usd.toFixed(4)}`}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function Reminders({
  reminders,
  onCancel,
}: {
  reminders: Reminder[]
  onCancel: (id: number) => void
}): JSX.Element | null {
  if (reminders.length === 0) return null
  return (
    <section className="mb-4">
      <h3 className="mb-1 text-micro font-medium text-aria-muted">Reminders</h3>
      <ul className="space-y-1">
        {reminders.map((reminder) => (
          <li
            key={reminder.id}
            className="rim raised flex items-baseline justify-between gap-2 rounded-lg px-3 py-2"
          >
            <span className="min-w-0">
              <span className="block truncate text-small text-aria-text">{reminder.text}</span>
              <span
                className={`block text-micro ${
                  reminder.overdue ? 'text-aria-warn' : 'text-aria-faint'
                }`}
              >
                {whenever(reminder.due_at)}
                {reminder.overdue && ' · overdue'}
              </span>
            </span>
            {/* No dialog: the button *is* the decision. `files.delete`'s rule. */}
            <button
              type="button"
              onClick={() => onCancel(reminder.id)}
              className="interactive shrink-0 rounded-md px-2 py-1 text-micro text-aria-muted hover:text-aria-bad"
            >
              cancel
            </button>
          </li>
        ))}
      </ul>
    </section>
  )
}

function Timeline({
  entries,
  onUndo,
}: {
  entries: UndoEntry[]
  onUndo: (id: number) => Promise<string>
}): JSX.Element | null {
  const [said, setSaid] = useState<string | null>(null)
  if (entries.length === 0) return null

  return (
    <section className="mb-4">
      <h3 className="mb-1 text-micro font-medium text-aria-muted">Undo</h3>
      {said && <p className="mb-1 text-micro text-aria-dim">{said}</p>}
      <ul className="space-y-1">
        {entries.map((entry) => (
          <li
            key={entry.id}
            className="rim raised flex items-baseline justify-between gap-2 rounded-lg px-3 py-2"
          >
            <span className="min-w-0">
              <span
                className={`block truncate text-small ${
                  entry.undoable ? 'text-aria-text' : 'text-aria-faint line-through'
                }`}
              >
                {entry.summary}
              </span>
              {/* **A reason, not a dead button.** A file that moved again or a
                  backup past its keep-window is something to be told. */}
              <span className="block truncate text-micro text-aria-faint">
                {entry.blocked ?? (entry.undone_at ? 'undone' : clock(entry.created_at))}
              </span>
            </span>
            {entry.undoable && (
              <button
                type="button"
                onClick={() => void onUndo(entry.id).then(setSaid)}
                className="interactive rim shrink-0 rounded-md px-2 py-1 text-micro text-aria-dim hover:text-aria-text"
              >
                undo
              </button>
            )}
          </li>
        ))}
      </ul>
    </section>
  )
}

function TurnRow({ turn, tool }: { turn: TurnRecord; tool: ToolRecord | null }): JSX.Element {
  const [open, setOpen] = useState(false)
  const tokens =
    turn.prompt_tokens === null && turn.completion_tokens === null
      ? 'not counted'
      : `${turn.prompt_tokens ?? 0} in / ${turn.completion_tokens ?? 0} out`
  return (
    <li className="rim raised rounded-lg">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="interactive flex w-full items-baseline justify-between gap-2 px-3 py-2 text-left"
      >
        <span className="min-w-0">
          <span className="block truncate text-small text-aria-text">{turn.model}</span>
          <span className="block truncate text-micro text-aria-faint">{explainStage(turn)}</span>
        </span>
        <span className="shrink-0 text-micro text-aria-faint">{clock(turn.created_at)}</span>
      </button>
      {open && (
        <dl className="border-t border-aria-rim px-3 py-2 text-micro">
          <div className="flex justify-between gap-2">
            <dt className="text-aria-muted">Where</dt>
            <dd className="text-aria-dim">{turn.local ? 'this machine' : turn.provider}</dd>
          </div>
          <div className="flex justify-between gap-2">
            <dt className="text-aria-muted">Tokens</dt>
            <dd className="text-aria-dim">{tokens}</dd>
          </div>
          {turn.latency_ms !== null && (
            <div className="flex justify-between gap-2">
              <dt className="text-aria-muted">Took</dt>
              <dd className="text-aria-dim">{(turn.latency_ms / 1000).toFixed(1)}s</dd>
            </div>
          )}
          {tool && (
            <div className="flex justify-between gap-2">
              <dt className="text-aria-muted">Tool</dt>
              <dd className="text-aria-dim">
                {tool.tool} — {tool.ok ? 'worked' : `failed (${tool.error ?? 'no reason'})`}
              </dd>
            </div>
          )}
        </dl>
      )}
    </li>
  )
}

export function ActivityPanel({ onClose }: { onClose: () => void }): JSX.Element {
  const { usage, turns, tools, reminders, undoable, loading, error, cancelReminder, undo } =
    useActivity(true)
  const toolFor = (turn: TurnRecord): ToolRecord | null =>
    tools.find((t) => t.tool === turn.tool_called) ?? null

  return (
    <Panel title="Activity" onClose={onClose} width="max-w-lg">
      {error && <p className="mb-3 text-small text-aria-bad">{error}</p>}
      {usage && <Today usage={usage} />}
      <Reminders reminders={reminders} onCancel={(id) => void cancelReminder(id)} />
      <Timeline entries={undoable} onUndo={undo} />

      <section>
        <h3 className="mb-1 text-micro font-medium text-aria-muted">Recent turns</h3>
        {turns.length === 0 ? (
          <p className="text-small text-aria-faint">
            {loading ? 'Reading the log…' : 'Nothing recorded yet.'}
          </p>
        ) : (
          <ul className="space-y-1">
            {turns.map((turn) => (
              <TurnRow key={turn.id} turn={turn} tool={toolFor(turn)} />
            ))}
          </ul>
        )}
      </section>
    </Panel>
  )
}
