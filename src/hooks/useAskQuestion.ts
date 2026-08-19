/**
 * The question she is waiting on, and stepping through it one at a time.
 *
 * Its own hook with its own `onEvent`, which is the established pattern here —
 * `useConfirm`, `useConversationMode` and `useAudio` each own one subscription
 * rather than adding a branch to `useConversation`.
 *
 * **She is genuinely blocked while this is on screen.** That is what separates
 * it from `mode.suggested`, which is an offer nobody has to answer. The turn is
 * suspended on a future in `core/questions.py` until `question.answer` lands or
 * ten minutes pass — and unlike a confirmation, running out of time is not a
 * "no", it just means she carries on with a stated assumption.
 */

import { useCallback, useEffect, useState } from 'react'

export interface QuestionOption {
  label: string
  description: string
}

export interface AskedQuestion {
  question: string
  header: string
  options: QuestionOption[]
  multi_select: boolean
}

export interface PendingAsk {
  request_id: string
  turn_id: string | null
  questions: AskedQuestion[]
}

/** One answered question, in the shape `question.answer` expects. */
export interface GivenAnswer {
  question: string
  chosen: string[]
  other: string
}

export interface UseAskQuestion {
  /** The question set on screen, or null. */
  pending: PendingAsk | null
  /** Which one of them is showing — 0-based. */
  index: number
  /** What has been answered so far, in order. */
  answers: GivenAnswer[]
  /** Record an answer and advance; sends everything once the last one lands. */
  answer: (given: GivenAnswer) => void
  /** Give up on the whole set. She is told nothing was chosen. */
  dismiss: () => void
}

export function useAskQuestion(): UseAskQuestion {
  const [pending, setPending] = useState<PendingAsk | null>(null)
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState<GivenAnswer[]>([])

  useEffect(() => {
    return window.aria.onEvent((event) => {
      if (event.method !== 'question.ask') return
      const params = event.params as unknown as PendingAsk
      // A new question set replaces whatever was there. Only one turn runs at
      // a time, so a second set means the first is already gone.
      setPending(params)
      setIndex(0)
      setAnswers([])
    })
  }, [])

  const send = useCallback((requestId: string, given: GivenAnswer[]) => {
    setPending(null)
    setIndex(0)
    setAnswers([])
    // Cleared before the call, not after, so the card goes the moment it is
    // clicked — `useConfirm` drops from its queue first for the same reason.
    void window.aria
      .call('question.answer', { request_id: requestId, answers: given })
      .catch(() => {
        /* the turn ends on its own timeout; nothing here can rescue it */
      })
  }, [])

  const answer = useCallback(
    (given: GivenAnswer) => {
      if (!pending) return
      const next = [...answers, given]
      if (index + 1 >= pending.questions.length) {
        send(pending.request_id, next)
        return
      }
      setAnswers(next)
      setIndex(index + 1)
    },
    [pending, answers, index, send],
  )

  const dismiss = useCallback(() => {
    if (!pending) return
    // Deliberately sends what was answered so far rather than nothing: two of
    // four answers is more use to her than none, and `render()` counts the
    // rest as unanswered and tells her to assume a default.
    send(pending.request_id, answers)
  }, [pending, answers, send])

  return { pending, index, answers, answer, dismiss }
}
