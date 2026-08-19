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
  /** What she did during this turn, in the order she did it. The sidecar has
   *  broadcast `tool.call`/`tool.result` since Phase 3 and nothing consumed
   *  them, so a turn that opened an app looked identical to one that talked
   *  about opening it. */
  toolCalls?: ToolCall[]
  /** The `messages` row this answer was written to. Ratings key on it, because
   *  the renderer never sees `routing_log`. */
  messageId?: number
  /** 1, -1, or undefined for un-rated. §9.7's label. */
  rating?: 1 | -1
  /** Files attached to *this* turn, and how reading each one went.
   *
   *  On the user turn, not the assistant's: it is his message that carried
   *  them. A file that could not be read used to be recorded only in the
   *  sidecar log, so a skipped `.ppt` lecture surfaced as a vague answer and
   *  nothing else — the whole point of this field is that the failure is
   *  visible where he is already looking, and stays in the transcript. */
  attachments?: AttachmentStatus[]
}

export interface AttachmentStatus {
  name: string
  ok: boolean
  /** Why, when `ok` is false — and it names the fix, not just the failure. */
  summary: string
}

export interface ToolCall {
  id: string
  tool: string
  args: Record<string, unknown>
  /** `running` until the result arrives — which includes the whole time a
   *  tier-2 call is waiting on the confirmation dialog. */
  state: 'running' | 'ok' | 'failed'
  summary?: string
  display?: Record<string, unknown> | null
  startedAt: number
  durationMs?: number
  /** Which step of the agent loop this was (Phase 6), zero-indexed. Undefined
   *  on events from a sidecar build that predates step numbering — treated
   *  the same as a single-tool turn, not as an error. */
  step?: number
}

interface TurnCompletePayload {
  turn_id: string
  message_id?: number
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
  send: (text: string, options?: { spoken?: boolean; attachments?: string[] }) => Promise<void>
  cancel: () => Promise<void>
  /** Clear the view and start a new session in the sidecar. */
  newChat: () => Promise<void>
  /** Load a past conversation and keep talking in it. */
  openSession: (sessionId: string) => Promise<void>
  /** Thumbs up or down on an answer. The same value again clears it. */
  rate: (messageId: number, rating: 1 | -1) => Promise<void>
  /** Which conversation is on screen, so the history panel can mark it. */
  sessionId: string | null
  /** First-token latency of the last turn — the Phase 1 gate, visible in the UI. */
  lastFirstTokenMs: number | null
}

/** StoredMessage rows -> the shape the transcript renders. */
function toTurns(messages: StoredMessage[]): Turn[] {
  return messages
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .map((m) => ({
      id: `m${m.id}`,
      role: m.role as 'user' | 'assistant',
      content: m.content,
      messageId: m.id,
    }))
}

/** Reattach saved ratings to reloaded turns.
 *
 *  Without this a thumb vanishes the moment the conversation is reopened,
 *  which reads as "it was not saved" and stops people rating anything. */
function withRatings(turns: Turn[], ratings: Record<string, number>): Turn[] {
  if (Object.keys(ratings).length === 0) return turns
  return turns.map((turn) => {
    const rating = turn.messageId === undefined ? undefined : ratings[String(turn.messageId)]
    return rating === 1 || rating === -1 ? { ...turn, rating } : turn
  })
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
  //: Stop pressed during the window between `setBusy(true)` and `chat.send`
  //: returning the turn id. There is nothing to cancel yet, so the intent is
  //: remembered and applied the moment the id lands — otherwise the click is
  //: silently dropped and the only feedback is that nothing happens.
  const cancelWanted = useRef(false)

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
        if (history.session_id) void loadRatings(history.session_id, setTurns)
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
        const { turn_id: turnId, text } = event.params as {
          turn_id: string
          text: string
        }
        if (turnId !== activeTurnId.current) return
        setTurns((prev) => appendToStreaming(prev, text))
        return
      }

      // She is doing something. Attached to the streaming turn so the card
      // sits with the answer it belongs to rather than floating at the end.
      if (event.method === 'tool.call') {
        const {
          turn_id: turnId,
          call_id: callId,
          tool,
          args,
          step,
        } = event.params as {
          turn_id: string
          call_id: string
          tool: string
          args: Record<string, unknown>
          step?: number
        }
        if (turnId !== activeTurnId.current) return
        setTurns((prev) =>
          withStreaming(prev, (turn) => ({
            ...turn,
            toolCalls: [
              ...(turn.toolCalls ?? []),
              {
                id: callId,
                tool,
                args,
                state: 'running',
                startedAt: Date.now(),
                step,
              },
            ],
          })),
        )
        return
      }

      if (event.method === 'tool.result') {
        const {
          turn_id: turnId,
          call_id: callId,
          ok,
          summary,
          display,
        } = event.params as {
          turn_id: string
          call_id: string
          ok: boolean
          summary: string
          display: Record<string, unknown> | null
        }
        if (turnId !== activeTurnId.current) return
        setTurns((prev) =>
          withStreaming(prev, (turn) => ({
            ...turn,
            toolCalls: (turn.toolCalls ?? []).map((call) =>
              call.id === callId
                ? {
                    ...call,
                    state: ok ? ('ok' as const) : ('failed' as const),
                    summary,
                    display,
                    durationMs: Date.now() - call.startedAt,
                  }
                : call,
            ),
          })),
        )
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

      // One per attached file, as the sidecar finishes reading it. Attached
      // to the *user* turn, which is the one that carried the files.
      if (event.method === 'attachment.read') {
        const payload = event.params as unknown as {
          turn_id: string
          name: string
          ok: boolean
          summary: string
        }
        if (payload.turn_id !== activeTurnId.current) return
        setTurns((prev) => {
          const next = [...prev]
          for (let i = next.length - 1; i >= 0; i -= 1) {
            if (next[i].role !== 'user') continue
            const seen = next[i].attachments ?? []
            next[i] = {
              ...next[i],
              attachments: [
                ...seen.filter((a) => a.name !== payload.name),
                { name: payload.name, ok: payload.ok, summary: payload.summary },
              ],
            }
            break
          }
          return next
        })
        return
      }

      if (event.method === 'turn.complete') {
        const payload = event.params as unknown as TurnCompletePayload
        // **`busy` is cleared even when the id does not match**, and that is
        // the whole fix. It used to sit behind this guard, so any unmatched
        // completion left the composer showing Stop forever with nothing to
        // cancel — clicking it did nothing, which is exactly what Eyaas hit.
        //
        // The id can legitimately be unknown here: the RPC reply and the event
        // stream are two different Electron IPC channels with no ordering
        // between them, so a fast turn can complete before `chat.send`
        // resolves. Only one turn is ever in flight, so an unmatched
        // completion while busy is this turn's.
        if (activeTurnId.current !== null && payload.turn_id !== activeTurnId.current) return
        activeTurnId.current = null
        cancelWanted.current = false
        setBusy(false)
        setLastFirstTokenMs(payload.first_token_ms ?? null)
        setTurns((prev) => finalise(prev, payload))
        return
      }

      // Phase 8: a message with no preceding question. Only appended to
      // whatever is on screen if it landed in the conversation currently
      // open — one that happened in a session the user is not looking at
      // is not something to interrupt this one with.
      if (event.method === 'proactive') {
        const payload = event.params as {
          text: string
          message_id?: number
          session_id?: string
        }
        if (payload.session_id && payload.session_id !== sessionId.current) return
        setTurns((prev) => [
          ...prev,
          {
            id: `p${payload.message_id ?? Date.now()}`,
            role: 'assistant',
            content: payload.text,
            messageId: payload.message_id,
          },
        ])
      }
    })
  }, [])

  const send = useCallback(
    async (text: string, options?: { spoken?: boolean; attachments?: string[] }) => {
      const trimmed = text.trim()
      const attachments = options?.attachments ?? []
      // A message can be nothing but files — the sidecar allows that too.
      // Dragging a PDF in and pressing Enter is a complete request.
      if (!trimmed && attachments.length === 0) return

      // Shown with the file names in it, so the transcript reads sensibly.
      // A bare "summarise this" with no record of what "this" was looks like
      // a bug in the history rather than a message.
      const names = attachments.map((p) => p.split(/[\\/]/).pop()).filter(Boolean)
      const shown =
        names.length > 0
          ? [trimmed, `[attached: ${names.join(', ')}]`].filter(Boolean).join('\n\n')
          : trimmed

      setBusy(true)
      // Cleared per turn, not per click: a stop meant for the previous turn
      // must not cancel this one.
      activeTurnId.current = null
      cancelWanted.current = false
      setTurns((prev) => [
        ...prev,
        { id: `u${Date.now()}`, role: 'user', content: shown },
        {
          id: `a${Date.now()}`,
          role: 'assistant',
          content: '',
          streaming: true,
        },
      ])

      try {
        const started = await window.aria.call<{
          turn_id: string
          session_id: string
        }>('chat.send', {
          text: trimmed,
          session_id: sessionId.current ?? undefined,
          // Marks a turn that arrived by voice, so the sidecar answers it
          // locally and fast rather than following the Smart bias.
          spoken: options?.spoken ?? false,
          // Absolute paths, never contents: the renderer has no filesystem
          // access, and the sidecar is what opens them.
          ...(attachments.length > 0 ? { attachments } : {}),
        })
        activeTurnId.current = started.turn_id
        sessionId.current = started.session_id
        setActiveSession(started.session_id)
        // The stop that arrived too early, honoured now.
        if (cancelWanted.current) {
          cancelWanted.current = false
          await window.aria.call('chat.cancel', { turn_id: started.turn_id })
        }
      } catch (cause) {
        activeTurnId.current = null
        setBusy(false)
        const message = cause instanceof Error ? cause.message : String(cause)
        setTurns((prev) => finalise(prev, { turn_id: '', full_text: '', error: message }))
      }
    },
    [],
  )

  const cancel = useCallback(async () => {
    const turnId = activeTurnId.current
    if (!turnId) {
      // Pressed before the turn id came back. Remembered rather than dropped
      // — `send` applies it as soon as it knows what to cancel.
      cancelWanted.current = true
      return
    }
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
    void loadRatings(history.session_id ?? id, setTurns)
  }, [])

  /** Thumbs up or down on one answer (§9.7's label half).
   *
   *  Optimistic, and deliberately so: this is a two-state toggle against a
   *  table nothing else writes, and a thumb that waits for a round-trip before
   *  it moves feels broken. Pressing the same thumb twice clears it — a rating
   *  you cannot take back is one people stop giving. */
  const rate = useCallback(async (messageId: number, rating: 1 | -1) => {
    let next: 1 | -1 | undefined
    setTurns((prev) =>
      prev.map((turn) => {
        if (turn.messageId !== messageId) return turn
        next = turn.rating === rating ? undefined : rating
        return { ...turn, rating: next }
      }),
    )
    try {
      await window.aria.call('turn.rate', {
        message_id: messageId,
        rating: next ?? 0,
      })
    } catch {
      /* The label is a nicety; failing to store one must not disturb the view. */
    }
  }, [])

  return {
    turns,
    busy,
    send,
    cancel,
    newChat,
    openSession,
    rate,
    sessionId: activeSession,
    lastFirstTokenMs,
  }
}

async function loadRatings(
  id: string,
  setTurns: React.Dispatch<React.SetStateAction<Turn[]>>,
): Promise<void> {
  try {
    const result = await window.aria.call<{ ratings: Record<string, number> }>('turn.ratings', {
      session_id: id,
    })
    setTurns((prev) => withRatings(prev, result.ratings))
  } catch {
    /* Ratings are additive. Missing them must not empty the transcript. */
  }
}

// ── reducers ──────────────────────────────────────────────────────────

/** Replace the turn currently streaming, or return the list untouched. */
function withStreaming(turns: Turn[], change: (turn: Turn) => Turn): Turn[] {
  const index = turns.findIndex((t) => t.streaming)
  if (index === -1) return turns
  const next = [...turns]
  next[index] = change(next[index])
  return next
}

function appendToStreaming(turns: Turn[], text: string): Turn[] {
  return withStreaming(turns, (turn) => ({
    ...turn,
    content: turn.content + text,
  }))
}

function clearStreaming(turns: Turn[]): Turn[] {
  return withStreaming(turns, (turn) => ({ ...turn, content: '' }))
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
    messageId: payload.message_id,
  }
  return next
}
