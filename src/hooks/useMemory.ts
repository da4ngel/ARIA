/**
 * What she has learned, for MemoryPanel.
 *
 * A pure mirror of SQLite (CLAUDE.md rule 1). Every mutation refetches rather
 * than patching locally — a fact edited here can be superseded by the same
 * write, and guessing at the new shape in the renderer is how the two drift.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import type { MemoryEpisode, MemoryFact, MemoryStats, ReflectionReport } from '@/types/bridge'

/** Long enough that typing does not fire a query per keystroke, short enough
 *  that the list feels live. Same figure as useSessions, deliberately. */
const SEARCH_DEBOUNCE_MS = 180

export interface UseMemory {
  facts: MemoryFact[]
  episodes: MemoryEpisode[]
  stats: MemoryStats | null
  query: string
  setQuery: (q: string) => void
  loading: boolean
  reflecting: boolean
  error: string | null
  refresh: () => Promise<void>
  pin: (id: number, locked: boolean) => Promise<void>
  edit: (id: number, object: string) => Promise<void>
  forget: (id: number) => Promise<void>
  reflect: () => Promise<ReflectionReport | null>
}

export function useMemory(enabled: boolean): UseMemory {
  const [facts, setFacts] = useState<MemoryFact[]>([])
  const [episodes, setEpisodes] = useState<MemoryEpisode[]>([])
  const [stats, setStats] = useState<MemoryStats | null>(null)
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [reflecting, setReflecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const latest = useRef(0)

  const fetchAll = useCallback(async (search: string) => {
    const ticket = ++latest.current
    setLoading(true)
    try {
      if (search.trim()) {
        const found = await window.aria.call<{
          facts: { fact: MemoryFact }[]
          episodes: { episode: MemoryEpisode }[]
        }>('memory.search', { query: search })
        // A slower earlier request must not overwrite a newer one's results.
        if (ticket !== latest.current) return
        setFacts(found.facts.map((f) => f.fact))
        setEpisodes(found.episodes.map((e) => e.episode))
      } else {
        const all = await window.aria.call<{
          facts: MemoryFact[]
          episodes: MemoryEpisode[]
        }>('memory.list', {})
        if (ticket !== latest.current) return
        setFacts(all.facts)
        setEpisodes(all.episodes)
      }
      const counts = await window.aria.call<MemoryStats>('memory.stats', {})
      if (ticket !== latest.current) return
      setStats(counts)
      setError(null)
    } catch (cause) {
      if (ticket !== latest.current) return
      setError(cause instanceof Error ? cause.message : String(cause))
    } finally {
      if (ticket === latest.current) setLoading(false)
    }
  }, [])

  const refresh = useCallback(() => fetchAll(query), [fetchAll, query])

  useEffect(() => {
    if (!enabled) return
    const timer = setTimeout(() => void fetchAll(query), query ? SEARCH_DEBOUNCE_MS : 0)
    return () => clearTimeout(timer)
  }, [enabled, query, fetchAll])

  const mutate = useCallback(
    async (run: () => Promise<unknown>) => {
      setError(null)
      try {
        await run()
        await fetchAll(query)
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause))
      }
    },
    [fetchAll, query],
  )

  const pin = useCallback(
    (id: number, locked: boolean) =>
      mutate(() => window.aria.call('memory.update', { fact_id: id, user_locked: locked })),
    [mutate],
  )

  const edit = useCallback(
    (id: number, object: string) =>
      mutate(() => window.aria.call('memory.update', { fact_id: id, object })),
    [mutate],
  )

  const forget = useCallback(
    (id: number) => mutate(() => window.aria.call('memory.forget', { fact_id: id })),
    [mutate],
  )

  const reflect = useCallback(async () => {
    setReflecting(true)
    setError(null)
    try {
      // Synchronous by design — the caller wants the report, not an ack.
      const report = await window.aria.call<ReflectionReport>('memory.reflect', {})
      await fetchAll(query)
      return report
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
      return null
    } finally {
      setReflecting(false)
    }
  }, [fetchAll, query])

  return {
    facts,
    episodes,
    stats,
    query,
    setQuery,
    loading,
    reflecting,
    error,
    refresh,
    pin,
    edit,
    forget,
    reflect,
  }
}
