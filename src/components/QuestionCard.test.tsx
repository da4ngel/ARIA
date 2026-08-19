/**
 * The question card: pick one, and it moves to the next.
 *
 * Eyaas asked for exactly this — *"i should be able to select what i want, and
 * one by one it moves to next"* — so the tests are about the clicking, not
 * about the wording.
 */

import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { QuestionCard } from '@/components/QuestionCard'
import type { PendingAsk } from '@/hooks/useAskQuestion'

function pending(overrides: Partial<PendingAsk> = {}): PendingAsk {
  return {
    request_id: 'q_1',
    turn_id: 't_1',
    questions: [
      {
        question: 'Which database?',
        header: 'Storage',
        multi_select: false,
        options: [
          { label: 'SQLite', description: 'One file, no server.' },
          { label: 'Postgres', description: 'A server to run.' },
          { label: 'Other', description: 'Something else — type it.' },
        ],
      },
    ],
    ...overrides,
  }
}

const noop = (): void => {}

describe('QuestionCard', () => {
  it('shows the question and what each answer would mean', () => {
    render(
      <QuestionCard pending={pending()} index={0} onAnswer={noop} onDismiss={noop} />,
    )

    expect(screen.getByText('Which database?')).toBeDefined()
    expect(screen.getByText('SQLite')).toBeDefined()
    // The description is what makes an option a decision rather than a label.
    expect(screen.getByText('One file, no server.')).toBeDefined()
  })

  it('answers on a single click, with no second step to confirm', () => {
    // Two actions for one decision is exactly the friction this replaces.
    const onAnswer = vi.fn()
    render(
      <QuestionCard pending={pending()} index={0} onAnswer={onAnswer} onDismiss={noop} />,
    )

    fireEvent.click(screen.getByText('SQLite'))

    expect(onAnswer).toHaveBeenCalledWith({
      question: 'Which database?',
      chosen: ['SQLite'],
      other: '',
    })
  })

  it('counts through a set, and does not count a set of one', () => {
    const two = pending({
      questions: [pending().questions[0], { ...pending().questions[0], question: 'Which host?' }],
    })

    const { rerender } = render(
      <QuestionCard pending={two} index={0} onAnswer={noop} onDismiss={noop} />,
    )
    expect(screen.getByText('1 of 2')).toBeDefined()

    rerender(<QuestionCard pending={two} index={1} onAnswer={noop} onDismiss={noop} />)
    expect(screen.getByText('Which host?')).toBeDefined()
    expect(screen.getByText('2 of 2')).toBeDefined()

    // "1 of 1" is noise, not information.
    rerender(<QuestionCard pending={pending()} index={0} onAnswer={noop} onDismiss={noop} />)
    expect(screen.queryByText('1 of 1')).toBeNull()
  })

  it('lets you say something the options did not offer', () => {
    // **The escape hatch that stops a badly-framed question being a trap.**
    // The sidecar appends "Other" to every question for this reason.
    const onAnswer = vi.fn()
    render(
      <QuestionCard pending={pending()} index={0} onAnswer={onAnswer} onDismiss={noop} />,
    )

    fireEvent.click(screen.getByText('Other'))
    const box = screen.getByLabelText('Your own answer')
    fireEvent.change(box, { target: { value: 'neither, use DuckDB' } })
    fireEvent.click(screen.getByText('Send'))

    expect(onAnswer).toHaveBeenCalledWith({
      question: 'Which database?',
      chosen: [],
      other: 'neither, use DuckDB',
    })
  })

  it('does not answer with an empty free-text box', () => {
    const onAnswer = vi.fn()
    render(
      <QuestionCard pending={pending()} index={0} onAnswer={onAnswer} onDismiss={noop} />,
    )

    fireEvent.click(screen.getByText('Other'))
    fireEvent.click(screen.getByText('Send'))

    expect(onAnswer).not.toHaveBeenCalled()
  })

  it('waits for Confirm when more than one option can apply', () => {
    // Multi-select has no natural "done" moment; single-select does, and must
    // not grow a second step.
    const onAnswer = vi.fn()
    const multi = pending()
    multi.questions[0].multi_select = true
    render(<QuestionCard pending={multi} index={0} onAnswer={onAnswer} onDismiss={noop} />)

    fireEvent.click(screen.getByText('SQLite'))
    expect(onAnswer).not.toHaveBeenCalled()

    fireEvent.click(screen.getByText('Postgres'))
    fireEvent.click(screen.getByText('Confirm'))

    expect(onAnswer).toHaveBeenCalledWith({
      question: 'Which database?',
      chosen: ['SQLite', 'Postgres'],
      other: '',
    })
  })

  it('can be skipped', () => {
    // She is told what was answered so far and to assume a default for the
    // rest — being stuck behind a question you do not want to answer would be
    // worse than the prose it replaced.
    const onDismiss = vi.fn()
    render(
      <QuestionCard pending={pending()} index={0} onAnswer={noop} onDismiss={onDismiss} />,
    )

    fireEvent.click(screen.getByText('Skip'))

    expect(onDismiss).toHaveBeenCalled()
  })
})
