import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ConversationView } from '@/components/ConversationView'
import type { Turn } from '@/hooks/useConversation'

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
