/**
 * How she should answer this conversation — Study, Research, Quick, Code.
 *
 * A pure mirror of the sidecar (CLAUDE.md rule 1): `ConversationService` owns
 * the mode and `core/context.py` turns it into prompt text. This only caches
 * the last answer so the control can render without a round-trip.
 *
 * **Per conversation, and that is why this takes a session id.** A new chat
 * starts back at Normal, so a mode chosen last week cannot quietly shape
 * today's answers — unlike the permission mode and the routing bias, which
 * are deliberately sticky settings. It re-reads whenever the open
 * conversation changes, because the answer genuinely differs per session.
 */

import { useCallback, useEffect, useState } from 'react'

export type ConversationMode = 'normal' | 'study' | 'research' | 'quick' | 'code'

export interface ModeState {
  mode: ConversationMode
  label: string
  /** True for Research, which wants the web. */
  online_required: boolean
  online_enabled: boolean
  /** The routing bias this mode asks for, so the model picker can say its own
   *  control has been overridden rather than showing a setting that is not in
   *  force. */
  effective_bias: string | null
}

export const MODE_OPTIONS: Array<{
  value: ConversationMode
  label: string
  hint: string
}> = [
  { value: 'normal', label: 'Normal', hint: 'How she usually answers.' },
  {
    value: 'study',
    label: 'Study',
    hint: 'Teaches it: an example, then a question back. Not just the answer.',
  },
  {
    value: 'research',
    label: 'Research',
    hint: 'Reads several sources and cites them. Needs online mode.',
  },
  { value: 'quick', label: 'Quick', hint: 'One line where one line will do.' },
  { value: 'code', label: 'Code', hint: 'Runnable code first, explanation second.' },
]

export interface UseConversationMode {
  mode: ConversationMode
  label: string
  /** Research picked while online mode is off — a real state the UI has to be
   *  able to show, rather than leaving her to explain it in a refusal. */
  needsOnline: boolean
  effectiveBias: string | null
  setMode: (next: ConversationMode) => Promise<void>
  error: string | null
}

const NORMAL: ModeState = {
  mode: 'normal',
  label: 'Normal',
  online_required: false,
  online_enabled: false,
  effective_bias: null,
}

export function useConversationMode(
  sessionId: string | null,
  connected: boolean,
): UseConversationMode {
  const [state, setState] = useState<ModeState>(NORMAL)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!connected || !sessionId) {
      // No conversation yet means Normal, not a stale mode from the last one.
      setState(NORMAL)
      return
    }
    let cancelled = false
    void (async () => {
      try {
        const next = await window.aria.call<ModeState>('chat.mode', { session_id: sessionId })
        if (!cancelled) setState(next)
      } catch {
        /* the status line already reports that the brain is down */
      }
    })()
    return () => {
      cancelled = true
    }
  }, [sessionId, connected])

  const setMode = useCallback(
    async (next: ConversationMode) => {
      setError(null)
      const previous = state
      // Optimistic, with the label filled in locally so the chip does not
      // flicker through a stale name on the way to the real answer.
      setState({
        ...state,
        mode: next,
        label: MODE_OPTIONS.find((o) => o.value === next)?.label ?? next,
      })
      try {
        setState(
          await window.aria.call<ModeState>('chat.mode', {
            session_id: sessionId ?? undefined,
            mode: next,
          }),
        )
      } catch (cause) {
        // Rolled back rather than left showing a mode that is not in force.
        setState(previous)
        setError(cause instanceof Error ? cause.message : String(cause))
      }
    },
    [sessionId, state],
  )

  return {
    mode: state.mode,
    label: state.label,
    needsOnline: state.online_required && !state.online_enabled,
    effectiveBias: state.effective_bias,
    setMode,
    error,
  }
}
