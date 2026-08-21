/**
 * What he is learning, for StudyPanel.
 *
 * A pure mirror of SQLite (CLAUDE.md rule 1), and `useMemory`'s rules kept
 * deliberately: **every mutation refetches rather than patching locally.**
 * Deleting a subject cascades through `concepts` into `concept_mastery` and
 * renaming one can be refused for a clash, so the shape after a write is not
 * something the renderer can guess at — guessing is how the two drift.
 *
 * The subject is selected here rather than in the panel because two of the
 * three writes can change which subject exists: after deleting the selected
 * one, *something* has to decide what is now on screen, and it should be the
 * thing that knows the new list.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import type {
  SessionSummary,
  StudyConcept,
  StudyStart,
  StudyState,
  StudySubject,
} from '@/types/bridge'

export interface UseStudy {
  subjects: StudySubject[]
  /** Study chats, most recently active first. Grouped in the panel by the
   *  subject each last worked on — a record of where a chat got to, not a
   *  binding, since a study chat may roam. */
  sessions: SessionSummary[]
  /** The subject currently shown, or null when nothing has ever been studied. */
  state: StudyState | null
  selected: number | null
  select: (subjectId: number) => void
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  rename: (subjectId: number, name: string) => Promise<void>
  forget: (subjectId: number) => Promise<void>
  reset: (conceptId: number) => Promise<void>
  /** Sets the conversation to Study with this sub-mode and returns the message
   *  the caller should send. Null when the sidecar refused. */
  start: (subMode: string, sessionId: string | null) => Promise<StudyStart | null>
}

/** Weak or recently wrong — "due", as Eyaas defined it. Derived from what is
 *  already stored rather than from a review schedule that does not exist.
 *
 *  Mirrors `study.WEAK_AT_OR_BELOW`. It is restated here rather than fetched
 *  because it decides layout, not behaviour: the sidecar is still the only
 *  thing that decides what she is told, and this only decides what is drawn
 *  under "Needs revision". */
export const WEAK_AT_OR_BELOW = 2

export function needsRevision(concepts: StudyConcept[]): StudyConcept[] {
  return concepts.filter((c) => c.level > 0 && c.level <= WEAK_AT_OR_BELOW)
}

export function useStudy(enabled: boolean): UseStudy {
  const [subjects, setSubjects] = useState<StudySubject[]>([])
  const [sessions, setSessions] = useState<SessionSummary[]>([])
  const [state, setState] = useState<StudyState | null>(null)
  const [selected, setSelected] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // The out-of-order guard `useMemory` uses: a slow first response must not
  // overwrite a fast second one.
  const latest = useRef(0)

  const fetchAll = useCallback(async (subjectId: number | null) => {
    const ticket = ++latest.current
    setLoading(true)
    try {
      const [list, chats] = await Promise.all([
        window.aria.call<{ subjects: StudySubject[] }>('study.subjects', {}),
        window.aria.call<{ sessions: SessionSummary[] }>('study.sessions', {}),
      ])
      if (ticket !== latest.current) return

      // A selected subject that no longer exists means it was just deleted.
      // Falling back to the head of the list rather than to nothing keeps the
      // panel showing something after a delete.
      const known = list.subjects.some((s) => s.id === subjectId)
      const wanted = known ? subjectId : (list.subjects[0]?.id ?? null)
      const found = list.subjects.find((s) => s.id === wanted)

      const next = await window.aria.call<StudyState>('study.state', {
        ...(found ? { subject: found.name } : {}),
      })
      if (ticket !== latest.current) return

      setSubjects(list.subjects ?? [])
      // `?? []` rather than trusting the shape: a panel that throws on an
      // unexpected payload takes the whole rail section down, and an empty
      // list is the honest fallback for "nothing came back".
      setSessions(chats.sessions ?? [])
      setSelected(wanted)
      setState(next.subject ? next : null)
    } catch (cause) {
      if (ticket === latest.current) {
        setError(cause instanceof Error ? cause.message : String(cause))
      }
    } finally {
      if (ticket === latest.current) setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!enabled) return
    void fetchAll(null)
  }, [enabled, fetchAll])

  const refresh = useCallback(() => fetchAll(selected), [fetchAll, selected])

  const select = useCallback(
    (subjectId: number) => {
      setSelected(subjectId)
      void fetchAll(subjectId)
    },
    [fetchAll],
  )

  /** Run a write, then refetch. Never patches local state — see the header. */
  const mutate = useCallback(
    async (run: () => Promise<{ ok?: boolean; reason?: string | null }>, after: number | null) => {
      setError(null)
      try {
        const result = await run()
        // A refusal is not an exception: renaming onto a name that is taken is
        // a thing the user can fix, and it comes back as a reason to show.
        if (result?.ok === false && result.reason) setError(result.reason)
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause))
      }
      await fetchAll(after)
    },
    [fetchAll],
  )

  const rename = useCallback(
    (subjectId: number, name: string) =>
      mutate(
        () =>
          window.aria.call<{ ok: boolean; reason: string | null }>('study.rename', {
            subject_id: subjectId,
            name,
          }),
        subjectId,
      ),
    [mutate],
  )

  const forget = useCallback(
    // `null` afterwards, not `subjectId` — it has just been deleted, and
    // asking for it back would resolve to whatever the fallback picks anyway.
    (subjectId: number) =>
      mutate(() => window.aria.call('study.forget', { subject_id: subjectId }), null),
    [mutate],
  )

  const reset = useCallback(
    (conceptId: number) =>
      mutate(() => window.aria.call('study.reset', { concept_id: conceptId }), selected),
    [mutate, selected],
  )

  const start = useCallback(async (subMode: string, sessionId: string | null) => {
    try {
      return await window.aria.call<StudyStart>('study.start', {
        sub_mode: subMode,
        ...(sessionId ? { session_id: sessionId } : {}),
      })
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
      return null
    }
  }, [])

  return {
    subjects,
    sessions,
    state,
    selected,
    select,
    loading,
    error,
    refresh,
    rename,
    forget,
    reset,
    start,
  }
}
