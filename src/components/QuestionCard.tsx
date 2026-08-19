/**
 * One question, with its answers as things you click.
 *
 * Eyaas: *"if u are gonna ask a question and give 4 answers more like an MCQ …
 * i should be able to select what i want, and one by one it moves to next."*
 *
 * **In the transcript, not a modal.** `ConfirmDialog`'s scrim exists because a
 * permission lock is being held and nothing else should happen until it is
 * answered. A question is part of the conversation: it belongs in the flow,
 * scrolling with the reply it interrupts.
 *
 * The button shape is `EmptyState`'s stacked choices, which are already the
 * "here are your options" idiom in this app. Only the selected option takes
 * `accent` — in this palette saturation means something, and four accent-filled
 * buttons would mean nothing.
 */

import { AnimatePresence, motion } from 'framer-motion'
import { useCallback, useState } from 'react'

import type { AskedQuestion, GivenAnswer, PendingAsk } from '@/hooks/useAskQuestion'

const OTHER = 'Other'

function Choice({
  option,
  picked,
  onPick,
}: {
  option: { label: string; description: string }
  picked: boolean
  onPick: () => void
}): JSX.Element {
  return (
    <button
      type="button"
      onClick={onPick}
      aria-pressed={picked}
      className={`raised rim interactive w-full rounded-xl px-3 py-2 text-left ${
        picked ? 'bg-aria-accent/90 text-aria-void' : 'text-aria-muted hover:text-aria-text'
      }`}
    >
      <span className="block text-tiny">{option.label}</span>
      {option.description && (
        <span
          className={`mt-0.5 block text-micro leading-relaxed ${
            picked ? 'text-aria-void/70' : 'text-aria-faint'
          }`}
        >
          {option.description}
        </span>
      )}
    </button>
  )
}

export function QuestionCard({
  pending,
  index,
  onAnswer,
  onDismiss,
}: {
  pending: PendingAsk
  index: number
  onAnswer: (given: GivenAnswer) => void
  onDismiss: () => void
}): JSX.Element | null {
  const [multi, setMulti] = useState<string[]>([])
  const [other, setOther] = useState('')
  const [typing, setTyping] = useState(false)

  const question: AskedQuestion | undefined = pending.questions[index]

  const reset = useCallback(() => {
    setMulti([])
    setOther('')
    setTyping(false)
  }, [])

  const give = useCallback(
    (given: GivenAnswer) => {
      reset()
      onAnswer(given)
    },
    [onAnswer, reset],
  )

  if (!question) return null

  const total = pending.questions.length
  const pick = (label: string): void => {
    if (label === OTHER) {
      setTyping(true)
      return
    }
    if (question.multi_select) {
      setMulti((current) =>
        current.includes(label) ? current.filter((l) => l !== label) : [...current, label],
      )
      return
    }
    give({ question: question.question, chosen: [label], other: '' })
  }

  return (
    <motion.div
      key={`${pending.request_id}:${index}`}
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.16, ease: [0.2, 0.8, 0.2, 1] }}
      className="raised rim my-1.5 rounded-xl p-2.5"
    >
      <div className="mb-1.5 flex items-baseline justify-between gap-2">
        <p className="text-tiny text-aria-text">{question.question}</p>
        {/* Only when there is more than one — "1 of 1" is noise. */}
        {total > 1 && (
          <span className="shrink-0 font-mono text-micro text-aria-faint">
            {index + 1} of {total}
          </span>
        )}
      </div>

      <div className="flex flex-col gap-1.5">
        {question.options.map((option) => (
          <Choice
            key={option.label}
            option={option}
            picked={multi.includes(option.label) || (typing && option.label === OTHER)}
            onPick={() => pick(option.label)}
          />
        ))}
      </div>

      <AnimatePresence>
        {typing && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <input
              autoFocus
              value={other}
              onChange={(e) => setOther(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && other.trim()) {
                  give({ question: question.question, chosen: [], other: other.trim() })
                }
                if (e.key === 'Escape') setTyping(false)
              }}
              placeholder="Say what you want instead…"
              aria-label="Your own answer"
              className="mt-1.5 w-full rounded-lg bg-aria-sunk px-2.5 py-1.5 text-tiny text-aria-text outline-none placeholder:text-aria-faint"
            />
          </motion.div>
        )}
      </AnimatePresence>

      <div className="mt-2 flex items-center justify-end gap-2 text-micro">
        <button
          type="button"
          onClick={onDismiss}
          className="interactive mr-auto rounded px-1 py-0.5 text-aria-faint hover:text-aria-muted"
        >
          Skip
        </button>
        {/* Multi-select has no natural "done" moment, so it needs a button.
            A single-select one commits on click and must not have a second
            step — that would be two actions for one decision. */}
        {question.multi_select && (
          <button
            type="button"
            disabled={multi.length === 0}
            onClick={() => give({ question: question.question, chosen: multi, other: '' })}
            className="interactive rounded-lg bg-aria-accent/90 px-2 py-1 text-aria-void disabled:cursor-not-allowed disabled:opacity-40"
          >
            Confirm
          </button>
        )}
        {typing && (
          <button
            type="button"
            disabled={!other.trim()}
            onClick={() => give({ question: question.question, chosen: [], other: other.trim() })}
            className="interactive rounded-lg bg-aria-accent/90 px-2 py-1 text-aria-void disabled:cursor-not-allowed disabled:opacity-40"
          >
            Send
          </button>
        )}
      </div>
    </motion.div>
  )
}
