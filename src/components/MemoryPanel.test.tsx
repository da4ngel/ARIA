import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { MemoryPanel } from '@/components/MemoryPanel'
import type { MemoryEpisode, MemoryFact, MemoryStats } from '@/types/bridge'

function fact(overrides: Partial<MemoryFact> = {}): MemoryFact {
  return {
    id: 1,
    subject: 'user',
    predicate: 'works_on',
    object: 'Sillara pricing before 10am',
    confidence: 0.8,
    evidence_count: 2,
    user_locked: false,
    source_episode: null,
    created_at: '2026-08-09T10:00:00Z',
    updated_at: '2026-08-09T10:00:00Z',
    superseded_by: null,
    ...overrides,
  }
}

function episode(overrides: Partial<MemoryEpisode> = {}): MemoryEpisode {
  return {
    id: 1,
    session_id: 's_aaa',
    summary: 'They settled on £2,400 for the banquet hall.',
    started_at: '2026-08-09T10:00:00Z',
    ended_at: '2026-08-09T10:30:00Z',
    salience: 0.9,
    access_count: 0,
    last_accessed: null,
    ...overrides,
  }
}

function stats(overrides: Partial<MemoryStats> = {}): MemoryStats {
  return {
    facts: 1,
    episodes: 1,
    retrieval: {
      count: 12,
      p50_ms: 34,
      p90_ms: 61,
      max_ms: 88,
      embed_count: 7,
      embed_p50_ms: 29,
      embed_p90_ms: 52,
      degraded: 0,
      empty: 5,
    },
    last_reflection: '2026-08-10T03:00:00Z',
    reflecting: false,
    embeddings_ready: true,
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

function defaults(overrides: Record<string, unknown> = {}) {
  return (method: string): unknown => {
    if (method === 'memory.list') return { facts: [fact()], episodes: [episode()] }
    if (method === 'memory.stats') return stats()
    return (overrides[method] as unknown) ?? { ok: true }
  }
}

const noop = (): void => {}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('MemoryPanel', () => {
  it('lists what she has learned', async () => {
    mockBridge(defaults())
    render(<MemoryPanel onClose={noop} />)

    expect(await screen.findByText('Sillara pricing before 10am')).toBeDefined()
    expect(screen.getByText('works_on')).toBeDefined()
    expect(screen.getByText(/They settled on £2,400/)).toBeDefined()
  })

  it('pins a fact, which is what stops reflection overwriting it', async () => {
    const call = mockBridge(defaults())
    render(<MemoryPanel onClose={noop} />)

    fireEvent.click(await screen.findByRole('button', { name: 'Pin this fact' }))

    await waitFor(() =>
      expect(call).toHaveBeenCalledWith('memory.update', { fact_id: 1, user_locked: true }),
    )
  })

  it('takes two clicks to forget, because forgetting is irreversible', async () => {
    const call = mockBridge(defaults())
    render(<MemoryPanel onClose={noop} />)

    const button = await screen.findByRole('button', { name: 'Forget' })
    fireEvent.click(button)
    expect(call).not.toHaveBeenCalledWith('memory.forget', expect.anything())

    fireEvent.click(screen.getByRole('button', { name: 'Sure?' }))
    await waitFor(() => expect(call).toHaveBeenCalledWith('memory.forget', { fact_id: 1 }))
  })

  it('reports what a reflection did', async () => {
    mockBridge(
      defaults({
        'memory.reflect': {
          model: 'qwen2.5:7b',
          local: true,
          window_hours: 24,
          messages_read: 40,
          inserted: 3,
          reinforced: 1,
          superseded: 1,
          blocked_by_pin: 1,
          pruned: 0,
          took_ms: 4200,
          error: null,
        },
      }),
    )
    render(<MemoryPanel onClose={noop} />)

    fireEvent.click(await screen.findByRole('button', { name: 'Reflect now' }))

    expect(await screen.findByText(/\+3 learned/)).toBeDefined()
    expect(screen.getByText(/1 pinned kept/)).toBeDefined()
  })

  it('says what to run when embeddings are missing, rather than failing quietly', async () => {
    mockBridge((method: string) => {
      if (method === 'memory.list') return { facts: [], episodes: [] }
      if (method === 'memory.stats') return stats({ embeddings_ready: false, facts: 0 })
      return { ok: true }
    })
    render(<MemoryPanel onClose={noop} />)

    expect(await screen.findByText(/ollama pull nomic-embed-text/)).toBeDefined()
  })

  it('searches rather than listing once you type', async () => {
    const call = mockBridge((method: string) => {
      if (method === 'memory.search') {
        return { facts: [{ fact: fact({ object: 'a matching fact' }) }], episodes: [] }
      }
      if (method === 'memory.stats') return stats()
      return { facts: [fact()], episodes: [episode()] }
    })
    render(<MemoryPanel onClose={noop} />)
    await screen.findByText('Sillara pricing before 10am')

    fireEvent.change(screen.getByPlaceholderText('Search what she remembers'), {
      target: { value: 'pricing' },
    })

    await waitFor(() =>
      expect(call).toHaveBeenCalledWith('memory.search', { query: 'pricing' }),
    )
    expect(await screen.findByText('a matching fact')).toBeDefined()
  })

  it('says how much recall is costing', async () => {
    mockBridge(defaults())
    render(<MemoryPanel onClose={noop} />)

    expect(await screen.findByText(/61ms at p90/)).toBeDefined()
  })
})
