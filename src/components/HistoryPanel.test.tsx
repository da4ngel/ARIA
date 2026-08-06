import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { HistoryPanel } from '@/components/HistoryPanel'
import type { SessionSummary } from '@/types/bridge'

function session(overrides: Partial<SessionSummary> = {}): SessionSummary {
  return {
    id: 's_aaa',
    started_at: new Date().toISOString(),
    title: null,
    preview: 'what did I eat for breakfast',
    message_count: 12,
    last_activity: new Date().toISOString(),
    ...overrides,
  }
}

/** Stub the bridge; `call` is what every hook goes through. */
function mockBridge(handler: (method: string, params: Record<string, unknown>) => unknown) {
  const call = vi.fn((method: string, params: Record<string, unknown> = {}) =>
    Promise.resolve(handler(method, params)),
  )
  // @ts-expect-error — the test only needs `call`.
  window.aria = { call }
  return call
}

const noop = (): void => {}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('HistoryPanel', () => {
  it('lists conversations under a day heading', async () => {
    mockBridge(() => ({ sessions: [session()] }))
    render(<HistoryPanel activeSessionId={null} onOpen={noop} onClose={noop} />)

    expect(await screen.findByText('what did I eat for breakfast')).toBeDefined()
    expect(screen.getByText('Today')).toBeDefined()
    expect(screen.getByText(/12 messages/)).toBeDefined()
  })

  it('prefers a generated title over the first message', async () => {
    mockBridge(() => ({ sessions: [session({ title: 'Breakfast and honesty' })] }))
    render(<HistoryPanel activeSessionId={null} onOpen={noop} onClose={noop} />)

    expect(await screen.findByText('Breakfast and honesty')).toBeDefined()
    expect(screen.queryByText('what did I eat for breakfast')).toBeNull()
  })

  it('marks the conversation that is currently open', async () => {
    mockBridge(() => ({ sessions: [session()] }))
    render(<HistoryPanel activeSessionId="s_aaa" onOpen={noop} onClose={noop} />)
    expect(await screen.findByText(/open/)).toBeDefined()
  })

  it('opens a conversation when its row is clicked', async () => {
    mockBridge(() => ({ sessions: [session()] }))
    const onOpen = vi.fn()
    render(<HistoryPanel activeSessionId={null} onOpen={onOpen} onClose={noop} />)

    fireEvent.click(await screen.findByText('what did I eat for breakfast'))
    expect(onOpen).toHaveBeenCalledWith('s_aaa')
  })

  it('passes the search text to the sidecar', async () => {
    const call = mockBridge(() => ({ sessions: [] }))
    render(<HistoryPanel activeSessionId={null} onOpen={noop} onClose={noop} />)

    fireEvent.change(screen.getByPlaceholderText(/Search/), { target: { value: 'breakfast' } })
    await waitFor(() =>
      expect(call).toHaveBeenCalledWith('chat.sessions', { query: 'breakfast' }),
    )
  })

  it('says so when a search matches nothing', async () => {
    mockBridge(() => ({ sessions: [] }))
    render(<HistoryPanel activeSessionId={null} onOpen={noop} onClose={noop} />)

    fireEvent.change(screen.getByPlaceholderText(/Search/), { target: { value: 'zzzznope' } })
    expect(await screen.findByText(/Nothing matches/)).toBeDefined()
  })

  it('invites a first conversation when there are none', async () => {
    mockBridge(() => ({ sessions: [] }))
    render(<HistoryPanel activeSessionId={null} onOpen={noop} onClose={noop} />)
    expect(await screen.findByText(/No conversations yet/)).toBeDefined()
  })

  it('asks before deleting, and deletes nothing until confirmed', async () => {
    const call = mockBridge((method, params) => {
      if (method === 'chat.sessions') return { sessions: [session()] }
      if (method === 'chat.delete' && params.confirm !== true) {
        return {
          confirm_required: true,
          session_id: 's_aaa',
          title: 'what did I eat for breakfast',
          message_count: 12,
        }
      }
      return { ok: true }
    })
    render(<HistoryPanel activeSessionId={null} onOpen={noop} onClose={noop} />)

    fireEvent.click(await screen.findByLabelText('Delete'))
    expect(await screen.findByText(/and its 12 messages/)).toBeDefined()

    // The confirm step has been shown, and no confirmed delete has gone out.
    expect(call).not.toHaveBeenCalledWith('chat.delete', { session_id: 's_aaa', confirm: true })

    fireEvent.click(screen.getByText('Delete', { selector: 'button' }))
    await waitFor(() =>
      expect(call).toHaveBeenCalledWith('chat.delete', { session_id: 's_aaa', confirm: true }),
    )
  })

  it('backs out of a delete without calling the sidecar', async () => {
    const call = mockBridge((method) =>
      method === 'chat.sessions'
        ? { sessions: [session()] }
        : { confirm_required: true, session_id: 's_aaa', title: 'x', message_count: 12 },
    )
    render(<HistoryPanel activeSessionId={null} onOpen={noop} onClose={noop} />)

    fireEvent.click(await screen.findByLabelText('Delete'))
    fireEvent.click(await screen.findByText('Keep'))

    expect(await screen.findByText('what did I eat for breakfast')).toBeDefined()
    expect(call).not.toHaveBeenCalledWith('chat.delete', { session_id: 's_aaa', confirm: true })
  })

  it('renames a conversation', async () => {
    const call = mockBridge((method) =>
      method === 'chat.sessions' ? { sessions: [session()] } : { ok: true },
    )
    render(<HistoryPanel activeSessionId={null} onOpen={noop} onClose={noop} />)

    fireEvent.click(await screen.findByLabelText('Rename'))
    const input = screen.getByDisplayValue('what did I eat for breakfast')
    fireEvent.change(input, { target: { value: 'Breakfast probe' } })
    fireEvent.keyDown(input, { key: 'Enter' })

    await waitFor(() =>
      expect(call).toHaveBeenCalledWith('chat.rename', {
        session_id: 's_aaa',
        title: 'Breakfast probe',
      }),
    )
  })
})
