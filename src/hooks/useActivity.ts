/**
 * Today's usage, recent turns, and the reminders that are set.
 *
 * A pure mirror of what the sidecar records (CLAUDE.md rule 1), following
 * `useMemory`/`useStudy`: the out-of-order ticket guard, and **every mutation
 * refetches rather than patching locally** — cancelling a reminder can be
 * refused if it fired in between, so the shape after a write is not something
 * the renderer can guess at.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import type {
  Reminder,
  ToolRecord,
  TurnRecord,
  UndoEntry,
  UsageReport,
} from '@/types/bridge'

export interface UseActivity {
  usage: UsageReport | null
  turns: TurnRecord[]
  tools: ToolRecord[]
  reminders: Reminder[]
  undoable: UndoEntry[]
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  cancelReminder: (id: number) => Promise<void>
  /** Reverse one operation. Returns what happened, for display. */
  undo: (id: number) => Promise<string>
}

/** Turns a router stage into the sentence the panel shows.
 *
 * Mirrors `tools/introspect._STAGE_WORDS`, and restated here for the same
 * reason `useStudy` restates `WEAK_AT_OR_BELOW`: this decides *layout*. The
 * sidecar remains the only thing that decides what she is told; an unknown
 * stage falls through to the router's own `detail`, so a stage added later
 * still explains itself rather than rendering blank.
 */
export const STAGE_WORDS: Record<string, string> = {
  explicit: 'you picked this model',
  private: 'looked private — kept local',
  attachment: 'carried one of your files',
  offline: 'nothing else was reachable',
  local_only: 'a tool result had to stay local',
  spoken: 'spoken turn',
  tool: 'looked like it wanted a tool',
  quality: 'substantive question',
  fastest: 'speed first',
  balanced: 'balanced',
  fallback: 'first choice had failed',
  proactive: 'she started this one',
  step: 'a later step of the turn',
}

export function explainStage(turn: TurnRecord): string {
  return STAGE_WORDS[turn.stage] ?? turn.detail ?? turn.stage
}

export function useActivity(enabled: boolean): UseActivity {
  const [usage, setUsage] = useState<UsageReport | null>(null)
  const [turns, setTurns] = useState<TurnRecord[]>([])
  const [tools, setTools] = useState<ToolRecord[]>([])
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [undoable, setUndoable] = useState<UndoEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // The out-of-order guard `useMemory` uses: a slow first fetch must not
  // overwrite a fast second one.
  const latest = useRef(0)

  const fetchAll = useCallback(async () => {
    const ticket = ++latest.current
    setLoading(true)
    try {
      const report = await window.aria.call<UsageReport>('usage.today', {})
      if (ticket !== latest.current) return
      setUsage(report)

      const recent = await window.aria.call<{ turns: TurnRecord[]; tools: ToolRecord[] }>(
        'usage.recent',
        { limit: 20 },
      )
      if (ticket !== latest.current) return
      // `?? []` on every list: an unexpected payload must not take the whole
      // rail section down with it.
      setTurns(recent.turns ?? [])
      setTools(recent.tools ?? [])

      const pending = await window.aria.call<{ reminders: Reminder[] }>('reminders.list', {})
      if (ticket !== latest.current) return
      setReminders(pending.reminders ?? [])

      const timeline = await window.aria.call<{ entries: UndoEntry[] }>('undo.list', {
        limit: 15,
      })
      if (ticket !== latest.current) return
      setUndoable(timeline.entries ?? [])
      setError(null)
    } catch (cause) {
      if (ticket === latest.current) {
        setError(cause instanceof Error ? cause.message : String(cause))
      }
    } finally {
      if (ticket === latest.current) setLoading(false)
    }
  }, [])

  const cancelReminder = useCallback(
    async (id: number) => {
      try {
        await window.aria.call('reminders.cancel', { id })
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause))
      }
      await fetchAll()
    },
    [fetchAll],
  )

  useEffect(() => {
    if (!enabled) return
    void fetchAll()
  }, [enabled, fetchAll])

  const undo = useCallback(
    async (id: number): Promise<string> => {
      let message = ''
      try {
        const result = await window.aria.call<{ ok: boolean; message: string }>(
          'undo.apply',
          { id },
        )
        // **A refusal is a `message`, not an exception.** A file that moved
        // again, or a backup past its keep-window, is something the person
        // needs told — not an error toast with no detail.
        message = result.message ?? ''
      } catch (cause) {
        message = cause instanceof Error ? cause.message : String(cause)
        setError(message)
      }
      await fetchAll()
      return message
    },
    [fetchAll],
  )

  return {
    usage,
    turns,
    tools,
    reminders,
    undoable,
    loading,
    error,
    refresh: fetchAll,
    cancelReminder,
    undo,
  }
}
