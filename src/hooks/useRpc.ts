/**
 * Bridge subscription hook.
 *
 * Holds connection status and the last event only — transport concerns, not
 * domain state. Conversation, memory, and task state live in the sidecar
 * (CLAUDE.md rule 1); nothing here may ever accumulate them.
 */

import { useCallback, useEffect, useState } from 'react'

import type { BrainStatus, LogLine, SidecarEvent } from '@/types/bridge'

export interface UseRpc {
  status: BrainStatus
  /** Most recent sidecar notification, for debugging the wire in Phase 0. */
  lastEvent: SidecarEvent | null
  /** Most recent supervisor problem, if any. */
  lastLog: LogLine | null
  call: <T = unknown>(method: string, params?: Record<string, unknown>) => Promise<T>
  restartBrain: () => void
}

export function useRpc(): UseRpc {
  const [status, setStatus] = useState<BrainStatus>('starting')
  const [lastEvent, setLastEvent] = useState<SidecarEvent | null>(null)
  const [lastLog, setLastLog] = useState<LogLine | null>(null)

  useEffect(() => {
    void window.aria.getStatus().then(setStatus)
    const offStatus = window.aria.onStatus(setStatus)
    const offEvent = window.aria.onEvent(setLastEvent)
    const offLog = window.aria.onLog(setLastLog)
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

  return { status, lastEvent, lastLog, call, restartBrain }
}
