/**
 * Conversation view-model.
 *
 * Mirrors sidecar state for rendering; it is not the source of truth. Every
 * turn here also exists in SQLite, which is why killing the window loses
 * nothing (BUILD_SPEC §3, CLAUDE.md rule 1). On mount it reloads from
 * `chat.history` rather than trusting anything kept in the renderer.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import type { SidecarEvent, StoredMessage } from '@/types/bridge'

export interface Turn {
  id: string
  role: 'user' | 'assistant'
  content: string
  streaming?: boolean
  cancelled?: boolean
  error?: string
  /** Which model actually answered — never what was merely chosen. */
  modelLabel?: string
  /** Why the router picked it, so routing is never a black box. */
  routeReason?: string
  /** Set when a provider failed and another one answered instead. */
  note?: string
}

interface TurnCompletePayload {
  turn_id: string
  full_text: string
  route?: string
  model?: string
  model_label?: string
  route_reason?: string
  note?: string | null
  cancelled?: boolean
  error?: string
  first_token_ms?: number | null
}

export interface UseConversation {
  turns: Turn[]
  busy: boolean
  send: (text: string) => Promise<void>
  cancel: () => Promise<void>
  /** Clear the view and start a new session in the sidecar. */
  newChat: () => Promise<void>
  /** Load a past conversation and keep talking in it. */
  openSession: (sessionId: string) => Promise<void>
  /** Which conversation is on screen, so the history panel can mark it. */
  sessionId: string | null
  /** First-token latency of the last turn — the Phase 1 gate, visible in the UI. */
  lastFirstTokenMs: number | null
}

/** StoredMessage rows -> the shape the transcript renders. */
function toTurns(messages: StoredMessage[]): Turn[] {
  return messages
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .map((m) => ({ id: `m${m.id}`, role: m.role as 'user' | 'assistant', content: m.content }))
}

export function useConversation(connected: boolean): UseConversation {
  const [turns, setTurns] = useState<Turn[]>([])
  const [busy, setBusy] = useState(false)
  const [lastFirstTokenMs, setLastFirstTokenMs] = useState<number | null>(null)
  // Mirrored into state as well as a ref: the ref keeps event handlers correct
  // without re-subscribing, the state lets the history panel mark what's open.
  const [activeSession, setActiveSession] = useState<string | null>(null)
  const sessionId = useRef<string | null>(null)
  const activeTurnId = useRef<string | null>(null)

  // Reload from the sidecar whenever the connection is (re)established.
  useEffect(() => {
    if (!connected) return
    let cancelled = false

    void window.aria
      .call<{ session_id: string | null; messages: StoredMessage[] }>('chat.history', {})
      .then((history) => {
        if (cancelled) return
        sessionId.current = history.session_id
        setActiveSession(history.session_id)
        setTurns(toTurns(history.messages))
      })
      .catch(() => {
        /* the status line already tells the user the brain is down */
      })

    return () => {
      cancelled = true
    }
  }, [connected])

  // Streaming deltas.
  useEffect(() => {
    return window.aria.onEvent((event: SidecarEvent) => {
      if (event.method === 'token') {
        const { turn_id: turnId, text } = event.params as { turn_id: string; text: string }
        if (turnId !== activeTurnId.current) return
        setTurns((prev) => appendToStreaming(prev, text))
        return
      }

      // A provider died after streaming part of a reply. What is on screen
      // belongs to a model that will not finish it, so drop it before the
      // replacement starts — otherwise the two answers concatenate.
      if (event.method === 'turn.reset') {
        const { turn_id: turnId } = event.params as { turn_id: string }
        if (turnId !== activeTurnId.current) return
        setTurns((prev) => clearStreaming(prev))
        return
      }

      if (event.method === 'turn.complete') {
        const payload = event.params as unknown as TurnCompletePayload
        if (payload.turn_id !== activeTurnId.current) return
        activeTurnId.current = null
        setBusy(false)
        setLastFirstTokenMs(payload.first_token_ms ?? null)
        setTurns((prev) => finalise(prev, payload))
      }
    })
  }, [])

  const send = useCallback(async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed) return

    setBusy(true)
    setTurns((prev) => [
      ...prev,
      { id: `u${Date.now()}`, role: 'user', content: trimmed },
      { id: `a${Date.now()}`, role: 'assistant', content: '', streaming: true },
    ])

    try {
      const started = await window.aria.call<{ turn_id: string; session_id: string }>(
        'chat.send',
        { text: trimmed, session_id: sessionId.current ?? undefined },
      )
      activeTurnId.current = started.turn_id
      sessionId.current = started.session_id
      setActiveSession(started.session_id)
    } catch (cause) {
      activeTurnId.current = null
      setBusy(false)
      const message = cause instanceof Error ? cause.message : String(cause)
      setTurns((prev) => finalise(prev, { turn_id: '', full_text: '', error: message }))
    }
  }, [])

  const cancel = useCallback(async () => {
    const turnId = activeTurnId.current
    if (!turnId) return
    try {
      await window.aria.call('chat.cancel', { turn_id: turnId })
    } catch {
      /* the turn.complete event still resolves the UI */
    }
  }, [])

  const newChat = useCallback(async () => {
    // The id is reserved, not created — no row exists behind it until the first
    // message, so opening a new chat and walking away leaves nothing behind.
    const started = await window.aria.call<{ session_id: string }>('chat.new', {})
    sessionId.current = started.session_id
    setActiveSession(null) // nothing to mark as open in the history list yet
    activeTurnId.current = null
    setBusy(false)
    setLastFirstTokenMs(null)
    setTurns([])
  }, [])

  const openSession = useCallback(async (id: string) => {
    const history = await window.aria.call<{
      session_id: string | null
      messages: StoredMessage[]
    }>('chat.history', { session_id: id })

    sessionId.current = history.session_id ?? id
    setActiveSession(history.session_id ?? id)
    activeTurnId.current = null
    setBusy(false)
    setLastFirstTokenMs(null)
    setTurns(toTurns(history.messages))
  }, [])

  return {
    turns,
    busy,
    send,
    cancel,
    newChat,
    openSession,
    sessionId: activeSession,
    lastFirstTokenMs,
  }
}

// ── reducers ──────────────────────────────────────────────────────────

function appendToStreaming(turns: Turn[], text: string): Turn[] {
  const index = turns.findIndex((t) => t.streaming)
  if (index === -1) return turns
  const next = [...turns]
  next[index] = { ...next[index], content: next[index].content + text }
  return next
}

function clearStreaming(turns: Turn[]): Turn[] {
  const index = turns.findIndex((t) => t.streaming)
  if (index === -1) return turns
  const next = [...turns]
  next[index] = { ...next[index], content: '' }
  return next
}

function finalise(turns: Turn[], payload: TurnCompletePayload): Turn[] {
  const index = turns.findIndex((t) => t.streaming)
  if (index === -1) return turns
  const next = [...turns]
  next[index] = {
    ...next[index],
    // Trust the accumulated stream: full_text is empty on error and identical
    // otherwise, and using it would blank a partial reply on cancel.
    content: next[index].content || payload.full_text,
    streaming: false,
    cancelled: payload.cancelled,
    error: payload.error,
    modelLabel: payload.model_label,
    routeReason: payload.route_reason,
    note: payload.note ?? undefined,
  }
  return next
}
