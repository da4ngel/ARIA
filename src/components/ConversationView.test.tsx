import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ConversationView } from '@/components/ConversationView'
import type { Turn } from '@/hooks/useConversation'

// jsdom has no layout engine; scrollIntoView is not implemented there.
Element.prototype.scrollIntoView = () => {}

describe('ConversationView', () => {
  it('prompts when there is nothing yet', () => {
    render(<ConversationView turns={[]} />)
    expect(screen.getByText('Say something.')).toBeDefined()
  })

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
    const turns: Turn[] = [
      { id: 'a1', role: 'assistant', content: 'partial', cancelled: true },
    ]
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
})
