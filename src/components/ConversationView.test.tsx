import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ConversationView } from '@/components/ConversationView'
import type { ToolCall, Turn } from '@/hooks/useConversation'

// jsdom has no layout engine, so neither scroll API is implemented there.
Element.prototype.scrollIntoView = () => {}

describe('ConversationView', () => {
  it('renders user text and assistant markdown', () => {
    const turns: Turn[] = [
      { id: 'u1', role: 'user', content: 'hello' },
      { id: 'a1', role: 'assistant', content: 'Here is **bold** text' },
    ]
    render(<ConversationView turns={turns} />)
    expect(screen.getByText('hello')).toBeDefined()
    expect(screen.getByText('bold').tagName).toBe('STRONG')
  })

  it('marks a cancelled turn as stopped', () => {
    const turns: Turn[] = [{ id: 'a1', role: 'assistant', content: 'partial', cancelled: true }]
    render(<ConversationView turns={turns} />)
    expect(screen.getByText('stopped')).toBeDefined()
    expect(screen.getByText('partial')).toBeDefined()
  })

  it('surfaces an error on the turn it belongs to', () => {
    const turns: Turn[] = [
      { id: 'a1', role: 'assistant', content: '', error: "Ollama isn't running." },
    ]
    render(<ConversationView turns={turns} />)
    expect(screen.getByText("Ollama isn't running.")).toBeDefined()
  })

  it('names the model that answered', () => {
    const turns: Turn[] = [
      { id: 'a1', role: 'assistant', content: 'Canberra', modelLabel: 'Qwen2.5 7B (local)' },
    ]
    render(<ConversationView turns={turns} />)
    expect(screen.getByText('Qwen2.5 7B (local)')).toBeDefined()
  })

  it('says a failover happened rather than swapping silently', () => {
    const turns: Turn[] = [
      {
        id: 'a1',
        role: 'assistant',
        content: 'Recovered.',
        note: 'GPT-5 was unavailable, so Gemini answered instead.',
      },
    ]
    render(<ConversationView turns={turns} />)
    expect(screen.getByText(/GPT-5 was unavailable/)).toBeDefined()
  })

  it('shows a placeholder between send and first token', () => {
    // The window would otherwise look broken for the ~400ms before a reply.
    const turns: Turn[] = [{ id: 'a1', role: 'assistant', content: '', streaming: true }]
    render(<ConversationView turns={turns} state="thinking" />)
    expect(screen.getByText('Thinking…')).toBeDefined()
  })
})

describe('tool calls', () => {
  const call = (over: Partial<ToolCall> = {}): ToolCall => ({
    id: 'c1',
    tool: 'open_app',
    args: { name: 'chrome' },
    state: 'ok',
    summary: 'Opened Chrome.',
    startedAt: 0,
    durationMs: 213,
    ...over,
  })

  it('shows what she did, not just what she said about it', () => {
    render(
      <ConversationView
        turns={[{ id: 'a', role: 'assistant', content: 'Opened it.', toolCalls: [call()] }]}
      />,
    )
    expect(screen.getByText('open_app')).toBeDefined()
    expect(screen.getByText('chrome')).toBeDefined()
    expect(screen.getByText('213ms')).toBeDefined()
  })

  it('reveals the arguments and the result on click', () => {
    render(
      <ConversationView
        turns={[{ id: 'a', role: 'assistant', content: 'done', toolCalls: [call()] }]}
      />,
    )
    expect(screen.queryByText('Opened Chrome.')).toBeNull()
    fireEvent.click(screen.getByText('open_app'))
    expect(screen.getByText('Opened Chrome.')).toBeDefined()
  })

  it('marks a running call rather than showing a duration it does not have', () => {
    render(
      <ConversationView
        turns={[
          {
            id: 'a',
            role: 'assistant',
            content: '',
            streaming: true,
            toolCalls: [call({ state: 'running', summary: undefined, durationMs: undefined })],
          },
        ]}
      />,
    )
    expect(screen.getByText('running…')).toBeDefined()
    // The card already says she is busy; saying "Thinking…" too says it twice.
    expect(screen.queryByText('Thinking…')).toBeNull()
  })

  it('still shows a placeholder when nothing has run yet', () => {
    render(
      <ConversationView
        turns={[{ id: 'a', role: 'assistant', content: '', streaming: true }]}
        state="thinking"
      />,
    )
    expect(screen.getByText('Thinking…')).toBeDefined()
  })

  it('colours a failure differently from a success', () => {
    render(
      <ConversationView
        turns={[
          {
            id: 'a',
            role: 'assistant',
            content: 'I could not.',
            toolCalls: [call({ state: 'failed', summary: 'I could not find it.' })],
          },
        ]}
      />,
    )
    expect(screen.getByLabelText('Failed')).toBeDefined()
  })
})
