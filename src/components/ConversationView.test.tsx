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

  // ── step numbering (Phase 6's agent loop) ───────────────────────────

  it('does not number a single-tool turn — there is nothing to count', () => {
    render(
      <ConversationView
        turns={[{ id: 'a', role: 'assistant', content: 'done', toolCalls: [call({ step: 0 })] }]}
      />,
    )
    expect(screen.queryByTitle('Step 1')).toBeNull()
  })

  it('numbers each step of a real chain, one-indexed for a human to read', () => {
    render(
      <ConversationView
        turns={[
          {
            id: 'a',
            role: 'assistant',
            content: 'done',
            toolCalls: [
              call({ id: 'c1', tool: 'search_files', step: 0 }),
              call({ id: 'c2', tool: 'read_file', step: 1 }),
            ],
          },
        ]}
      />,
    )
    expect(screen.getByTitle('Step 1')).toBeDefined()
    expect(screen.getByTitle('Step 2')).toBeDefined()
  })

  // ── rating (§9.7's labelled dataset) ────────────────────────────────

  const rated = (over: Partial<Turn> = {}): Turn => ({
    id: 'a1',
    role: 'assistant',
    content: 'Volume 40% to 55%.',
    messageId: 42,
    ...over,
  })

  it('offers a thumbs up and down on a finished answer', () => {
    render(<ConversationView turns={[rated()]} onRate={() => {}} />)
    expect(screen.getByLabelText('Good answer')).toBeDefined()
    expect(screen.getByLabelText('Bad answer')).toBeDefined()
  })

  it('reports which thumb was pressed', () => {
    const calls: Array<[number, number]> = []
    render(
      <ConversationView
        turns={[rated()]}
        onRate={(id, rating) => calls.push([id, rating])}
      />,
    )
    fireEvent.click(screen.getByLabelText('Bad answer'))
    expect(calls).toEqual([[42, -1]])
  })

  it('shows an existing rating as pressed', () => {
    render(<ConversationView turns={[rated({ rating: 1 })]} onRate={() => {}} />)
    expect(screen.getByLabelText('Good answer').getAttribute('aria-pressed')).toBe('true')
    expect(screen.getByLabelText('Bad answer').getAttribute('aria-pressed')).toBe('false')
  })

  it('does not offer a rating while the answer is still streaming', () => {
    render(
      <ConversationView
        turns={[rated({ streaming: true })]}
        onRate={() => {}}
      />,
    )
    expect(screen.queryByLabelText('Good answer')).toBeNull()
  })

  it('does not offer a rating on a turn with no message row behind it', () => {
    // A turn that failed before it was persisted has nothing to key a rating on.
    render(<ConversationView turns={[rated({ messageId: undefined })]} onRate={() => {}} />)
    expect(screen.queryByLabelText('Good answer')).toBeNull()
  })

  // ── attachments that could not be read ──────────────────────────────

  it('shows why a file was skipped, in the transcript', () => {
    // The bug: a lecture .ppt was attached, could not be parsed, and the only
    // record was a log line — so the first he knew of it was a vague answer.
    render(
      <ConversationView
        turns={[
          {
            id: 'u1',
            role: 'user',
            content: 'summarise this',
            attachments: [
              {
                name: 'lecture.ppt',
                ok: false,
                summary:
                  'lecture.ppt — .ppt is the old binary PowerPoint format. Save as .pptx.',
              },
            ],
          },
        ]}
      />,
    )

    expect(screen.getByText(/old binary PowerPoint format/)).toBeDefined()
  })

  it('says nothing about files that read fine', () => {
    render(
      <ConversationView
        turns={[
          {
            id: 'u1',
            role: 'user',
            content: 'summarise this',
            attachments: [{ name: 'lease.pdf', ok: true, summary: 'lease.pdf — a document.' }],
          },
        ]}
      />,
    )

    expect(screen.queryByText(/lease.pdf/)).toBeNull()
  })
})
