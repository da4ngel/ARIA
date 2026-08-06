/**
 * Past conversations, for the history panel.
 *
 * A pure mirror of SQLite (CLAUDE.md rule 1). Nothing here is the source of
 * truth; the list is refetched after any change rather than patched locally, so
 * a title generated in the background shows up on the next open without the
 * renderer having to know it happened.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import type { SessionSummary } from '@/types/bridge'

/** Long enough that typing does not fire a query per keystroke, short enough
 *  that the list feels live. */
const SEARCH_DEBOUNCE_MS = 180

export interface DeletePreview {
  session_id: string
  title: string
  message_count: number
}

export interface UseSessions {
  sessions: SessionSummary[]
  query: string
  setQuery: (q: string) => void
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  rename: (id: string, title: string) => Promise<void>
  /** Asks the sidecar what would be deleted. Deletes nothing. */
  confirmDelete: (id: string) => Promise<DeletePreview | null>
  remove: (id: string) => Promise<void>
}

export function useSessions(enabled: boolean): UseSessions {
  const [sessions, setSessions] = useState<SessionSummary[]>([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const latest = useRef(0)

  const fetchList = useCallback(async (search: string) => {
    const ticket = ++latest.current
    setLoading(true)
    try {
      const result = await window.aria.call<{ sessions: SessionSummary[] }>('chat.sessions', {
        query: search || undefined,
      })
      // A slower earlier request must not overwrite a newer one's results.
      if (ticket !== latest.current) return
      setSessions(result.sessions)
      setError(null)
    } catch (cause) {
      if (ticket !== latest.current) return
      setError(cause instanceof Error ? cause.message : String(cause))
    } finally {
      if (ticket === latest.current) setLoading(false)
    }
  }, [])

  const refresh = useCallback(() => fetchList(query), [fetchList, query])

  useEffect(() => {
    if (!enabled) return
    const timer = setTimeout(() => void fetchList(query), query ? SEARCH_DEBOUNCE_MS : 0)
    return () => clearTimeout(timer)
  }, [enabled, query, fetchList])

  const rename = useCallback(
    async (id: string, title: string) => {
      await window.aria.call('chat.rename', { session_id: id, title })
      await fetchList(query)
    },
    [fetchList, query],
  )

  const confirmDelete = useCallback(async (id: string) => {
    // Rule 5: destructive operations confirm first. The sidecar refuses the
    // delete without `confirm` and reports what would go instead.
    const result = await window.aria.call<{
      confirm_required?: boolean
      session_id: string
      title: string
      message_count: number
    }>('chat.delete', { session_id: id })
    return result.confirm_required ? result : null
  }, [])

  const remove = useCallback(
    async (id: string) => {
      await window.aria.call('chat.delete', { session_id: id, confirm: true })
      await fetchList(query)
    },
    [fetchList, query],
  )

  return { sessions, query, setQuery, loading, error, refresh, rename, confirmDelete, remove }
}
