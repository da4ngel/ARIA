/**
 * Where an update has got to.
 *
 * A pure mirror of the main process, which is where `electron-updater` lives.
 * The status is **pushed** as it happens rather than polled: a check runs on
 * launch and then every six hours, and a card that polled would either miss
 * the download entirely or ask a question nobody had an answer to.
 *
 * Not the sidecar's, and rule 1 is untouched: which version of the app is
 * installed is not conversation, memory or task state. Same argument as
 * auto-start, and for the same reason — the OS and the installer own it.
 */

import { useCallback, useEffect, useState } from 'react'

import type { UpdateStatus } from '@/types/bridge'

export interface UseUpdates {
  status: UpdateStatus | null
  busy: boolean
  check: () => Promise<void>
  install: () => Promise<void>
}

export function useUpdates(): UseUpdates {
  const [status, setStatus] = useState<UpdateStatus | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    // The current state first, so the card can show the running version
    // immediately rather than waiting six hours for something to happen.
    void window.aria
      .updateStatus()
      .then(setStatus)
      .catch(() => setStatus(null))
    return window.aria.onUpdateStatus(setStatus)
  }, [])

  const check = useCallback(async () => {
    setBusy(true)
    try {
      setStatus(await window.aria.checkForUpdates())
    } catch (cause) {
      // A failed check is the normal state of a machine with no network, not
      // an error worth a dialog — it belongs in the card like any other state.
      setStatus((previous) => ({
        state: 'error',
        current: previous?.current ?? '',
        message: cause instanceof Error ? cause.message : String(cause),
      }))
    } finally {
      setBusy(false)
    }
  }, [])

  const install = useCallback(async () => {
    setBusy(true)
    // No `finally`: this quits the app. Clearing `busy` afterwards would only
    // matter in the case where the install failed to start, and there the
    // status event says so.
    await window.aria.installUpdate()
  }, [])

  return { status, busy, check, install }
}
