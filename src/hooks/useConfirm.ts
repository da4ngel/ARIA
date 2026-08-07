/**
 * Confirmation requests, and the answers that release the sidecar.
 *
 * The agent loop is genuinely blocked while one of these is open, so the queue
 * matters: a second request arriving must not overwrite the first and leave a
 * `Future` waiting for an answer that can no longer be given. They are shown
 * one at a time, in order.
 */

import { useCallback, useEffect, useState } from 'react'

import type { ConfirmRequest } from '@/components/ConfirmDialog'
import type { SidecarEvent } from '@/types/bridge'

export interface UseConfirm {
  /** The one being asked about now, or null. */
  current: ConfirmRequest | null
  respond: (requestId: string, approved: boolean, remember: boolean) => void
}

export function useConfirm(): UseConfirm {
  const [queue, setQueue] = useState<ConfirmRequest[]>([])

  useEffect(() => {
    return window.aria.onEvent((event: SidecarEvent) => {
      if (event.method !== 'confirm.request') return
      setQueue((previous) => [...previous, event.params as unknown as ConfirmRequest])
    })
  }, [])

  const respond = useCallback((requestId: string, approved: boolean, remember: boolean) => {
    // Dropped from the queue first: the dialog must close on the click rather
    // than when the round-trip lands, or a slow sidecar reads as a dead button.
    setQueue((previous) => previous.filter((r) => r.request_id !== requestId))
    void window.aria
      .call('confirm.respond', { request_id: requestId, approved, remember })
      .catch(() => {
        /* the 120s timeout already denied it — nothing left to do */
      })
  }, [])

  return { current: queue[0] ?? null, respond }
}
