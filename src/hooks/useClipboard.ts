/**
 * The clipboard ring, for ClipboardPanel.
 *
 * Same rules as `useMemory`: the ticket guard, and every write refetches. The
 * one thing worth reading twice is `watching` — "nothing has been copied yet"
 * and "nothing is recording" look identical on screen, and only the sidecar
 * knows which it is.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import type { ClipboardHistory, ClipEntry } from '@/types/bridge'

export interface UseClipboard {
  entries: ClipEntry[]
  watching: boolean
  /** How many copies the credential filter refused. Shown in the panel so the
   *  filter is visible rather than a claim in a docstring. */
  skippedSecrets: number
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  copy: (id: number) => Promise<void>
  forget: (id: number) => Promise<void>
  forgetAll: () => Promise<void>
}

export function useClipboard(enabled: boolean): UseClipboard {
  const [entries, setEntries] = useState<ClipEntry[]>([])
  const [watching, setWatching] = useState(false)
  const [skippedSecrets, setSkippedSecrets] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const latest = useRef(0)

  const fetchAll = useCallback(async () => {
    const ticket = ++latest.current
    setLoading(true)
    try {
      const result = await window.aria.call<ClipboardHistory>('clipboard.history', {
        limit: 100,
      })
      if (ticket !== latest.current) return
      setEntries(result.entries ?? [])
      setWatching(result.watching ?? false)
      setSkippedSecrets(result.skipped_secrets ?? 0)
      setError(null)
    } catch (cause) {
      if (ticket === latest.current) {
        setError(cause instanceof Error ? cause.message : String(cause))
      }
    } finally {
      if (ticket === latest.current) setLoading(false)
    }
  }, [])

  const mutate = useCallback(
    async (run: () => Promise<unknown>) => {
      try {
        await run()
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause))
      }
      await fetchAll()
    },
    [fetchAll],
  )

  const copy = useCallback(
    async (id: number) => {
      // Deliberately does *not* refetch: putting an entry back on the
      // clipboard changes the sequence number, so the watcher records it and
      // moves it to the front. Refetching here would reorder the list under
      // the cursor of somebody who just clicked it.
      try {
        await window.aria.call('clipboard.copy', { id })
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause))
      }
    },
    [],
  )

  const forget = useCallback(
    (id: number) => mutate(() => window.aria.call('clipboard.forget', { id })),
    [mutate],
  )

  const forgetAll = useCallback(
    () => mutate(() => window.aria.call('clipboard.forget', { all: true })),
    [mutate],
  )

  useEffect(() => {
    if (!enabled) return
    void fetchAll()
  }, [enabled, fetchAll])

  return { entries, watching, skippedSecrets, loading, error, refresh: fetchAll, copy, forget, forgetAll }
}
