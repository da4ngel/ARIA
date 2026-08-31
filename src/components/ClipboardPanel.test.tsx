/**
 * The clipboard panel.
 *
 * The warning about what is stored is asserted as content, not styling: it is
 * the only place a person is told that their clipboard history lives in a
 * database file, and a redesign that quietly drops it should fail here.
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ClipboardPanel } from '@/components/ClipboardPanel'
import type { ClipEntry } from '@/types/bridge'

function entry(overrides: Partial<ClipEntry> = {}): ClipEntry {
  return {
    id: 1,
    content: 'https://example.com/a-link',
    chars: 26,
    copied_at: '2026-08-24T09:00:00Z',
    source: 'Firefox',
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

function defaults(entries: ClipEntry[], extra: Record<string, unknown> = {}) {
  return (method: string): unknown => {
    if (method === 'clipboard.history') {
      return { entries, watching: true, skipped_secrets: 0, ...extra }
    }
    return { ok: true }
  }
}

const noop = (): void => {}

describe('ClipboardPanel', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('lists what was copied', async () => {
    mockBridge(defaults([entry(), entry({ id: 2, content: 'a second thing' })]))
    render(<ClipboardPanel onClose={noop} />)

    expect(await screen.findByText('https://example.com/a-link')).toBeTruthy()
    expect(await screen.findByText('a second thing')).toBeTruthy()
  })

  it('always says the history is stored on the machine', async () => {
    mockBridge(defaults([entry()]))
    render(<ClipboardPanel onClose={noop} />)

    expect(await screen.findByText(/stored on this machine/i)).toBeTruthy()
    // And it does not overclaim: the filter is described as partial.
    expect(await screen.findByText(/cannot be told from a sentence/i)).toBeTruthy()
  })

  it('reports how many secrets the filter caught', async () => {
    mockBridge(defaults([entry()], { skipped_secrets: 3 }))
    render(<ClipboardPanel onClose={noop} />)
    expect(await screen.findByText(/3 skipped so far/i)).toBeTruthy()
  })

  it('says when nothing is recording, which is not the same as nothing copied', async () => {
    mockBridge(defaults([], { watching: false }))
    render(<ClipboardPanel onClose={noop} />)
    expect(await screen.findByText(/Not recording/i)).toBeTruthy()
  })

  it('copies an entry back without a confirmation', async () => {
    const call = mockBridge(defaults([entry({ id: 7 })]))
    render(<ClipboardPanel onClose={noop} />)

    fireEvent.click(await screen.findByText('https://example.com/a-link'))
    await waitFor(() => expect(call).toHaveBeenCalledWith('clipboard.copy', { id: 7 }))
  })

  it('forgets one entry, and can forget everything', async () => {
    const call = mockBridge(defaults([entry({ id: 4 })]))
    render(<ClipboardPanel onClose={noop} />)

    fireEvent.click(await screen.findByText('forget'))
    await waitFor(() => expect(call).toHaveBeenCalledWith('clipboard.forget', { id: 4 }))

    fireEvent.click(await screen.findByText('Forget everything'))
    await waitFor(() => expect(call).toHaveBeenCalledWith('clipboard.forget', { all: true }))
  })

  it('collapses whitespace so a copied file reads as one line', async () => {
    mockBridge(defaults([entry({ content: 'line one\n\n   line two\tline three' })]))
    render(<ClipboardPanel onClose={noop} />)
    expect(await screen.findByText('line one line two line three')).toBeTruthy()
  })

  it('survives a payload with no entries array at all', async () => {
    // A panel that throws on an unexpected shape takes the whole rail section
    // down — the gap `useStudy` found the hard way.
    mockBridge(() => ({ ok: true }))
    render(<ClipboardPanel onClose={noop} />)
    expect(await screen.findByText(/Nothing copied yet/i)).toBeTruthy()
  })
})

describe('the copy button', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('is visible without hovering, and copies', async () => {
    // The row was already clickable; nothing said so. A clipboard write
    // changes nothing on screen, so the affordance has to be explicit.
    const call = mockBridge(defaults([entry({ id: 3 })]))
    render(<ClipboardPanel onClose={noop} />)

    fireEvent.click(await screen.findByText('copy'))
    await waitFor(() => expect(call).toHaveBeenCalledWith('clipboard.copy', { id: 3 }))
  })

  it('confirms, because a clipboard write is otherwise invisible', async () => {
    mockBridge(defaults([entry({ id: 3 })]))
    render(<ClipboardPanel onClose={noop} />)

    fireEvent.click(await screen.findByText('copy'))
    expect(await screen.findByText('copied')).toBeTruthy()
  })

  it('labels itself for a screen reader with what it will copy', async () => {
    mockBridge(defaults([entry({ content: 'a memorable line' })]))
    render(<ClipboardPanel onClose={noop} />)
    expect(await screen.findByLabelText('Copy a memorable line')).toBeTruthy()
  })
})
