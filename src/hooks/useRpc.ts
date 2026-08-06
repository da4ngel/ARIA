/**
 * Bridge subscription hook.
 *
 * Holds connection status, assistant state, and the last supervisor log —
 * transport concerns, not domain state. Conversation, memory, and task state
 * live in the sidecar (CLAUDE.md rule 1); nothing here may ever accumulate them.
 */

import { useCallback, useEffect, useState } from 'react'

import type { AssistantState, BrainStatus, LogLine, SidecarEvent } from '@/types/bridge'

export interface UseRpc {
  status: BrainStatus
  /** Mirrors `state.change`; drives the Orb. */
  assistantState: AssistantState
  /** Most recent supervisor problem, if any. */
  lastLog: LogLine | null
  call: <T = unknown>(method: string, params?: Record<string, unknown>) => Promise<T>
  restartBrain: () => void
}

export function useRpc(): UseRpc {
  const [status, setStatus] = useState<BrainStatus>('starting')
  const [assistantState, setAssistantState] = useState<AssistantState>('idle')
  const [lastLog, setLastLog] = useState<LogLine | null>(null)

  useEffect(() => {
    // The initial read is a round-trip over IPC, so a pushed status can land
    // first. Applying the reply unconditionally would then put a stale value
    // back — "starting" over a brain that already said "connected".
    let pushed = false
    void window.aria.getStatus().then((initial) => {
      if (!pushed) setStatus(initial)
    })

    // A supervisor warning describes a problem happening now. Once the brain is
    // connected again there is no problem, and leaving "Sidecar exited" on
    // screen over a working app reports a fault that has already healed.
    // The log file keeps the history; this line is a status, not a record.
    const offStatus = window.aria.onStatus((next) => {
      pushed = true
      setStatus(next)
      if (next === 'connected') setLastLog(null)
    })
    const offLog = window.aria.onLog(setLastLog)
    const offEvent = window.aria.onEvent((event: SidecarEvent) => {
      if (event.method === 'state.change') {
        setAssistantState(event.params.state as AssistantState)
      }
    })
    return () => {
      offStatus()
      offEvent()
      offLog()
    }
  }, [])

  const call = useCallback(
    <T,>(method: string, params: Record<string, unknown> = {}): Promise<T> =>
      window.aria.call<T>(method, params),
    [],
  )

  const restartBrain = useCallback(() => window.aria.restartBrain(), [])

  return { status, assistantState, lastLog, call, restartBrain }
}
