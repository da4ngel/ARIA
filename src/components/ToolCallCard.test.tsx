/**
 * The tool card, and the arguments it cannot just stringify.
 *
 * `ask_user` was the first tool whose argument is a list of objects, and it
 * put `ask_user [object Object]` in the header and a five-line wall of escaped
 * JSON in the body. Both are what these pin.
 */

import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ToolCallCard } from '@/components/ToolCallCard'

describe('an argument that is not a scalar', () => {
  const questions = [
    {
      question: 'Which of the following is a valid IPv4 address?',
      options: [{ label: '192.168.0.1' }, { label: '2001::85a3' }],
    },
    { question: 'What is a public IP for?', options: [{ label: 'The wider internet' }] },
  ]

  it('never renders [object Object]', () => {
    // What `ask_user` put on screen: the header read `ask_user [object
    // Object]`, because `String(value)` on an array of questions does exactly
    // that.
    render(
      <ToolCallCard
        call={{
          id: 'c1',
          tool: 'ask_user',
          args: { questions },
          state: 'ok',
          startedAt: 0,
        }}
      />,
    )

    expect(screen.queryByText(/\[object Object\]/)).toBeNull()
    // The first question says more than "2 items" does.
    expect(screen.getByText(/Which of the following is a valid IPv4 address\?/)).toBeDefined()
  })

  it('lays the detail out as lines rather than a wall of JSON', () => {
    render(
      <ToolCallCard
        call={{
          id: 'c1',
          tool: 'ask_user',
          args: { questions },
          state: 'ok',
          startedAt: 0,
        }}
      />,
    )

    fireEvent.click(screen.getByRole('button'))

    // Five lines of escaped quotes in a break-all column is what this replaces.
    expect(screen.queryByText(/\{"question":/)).toBeNull()
    expect(screen.getByText(/192\.168\.0\.1/)).toBeDefined()
  })
})
