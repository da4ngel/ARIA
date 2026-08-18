/**
 * The file panel.
 *
 * The behaviour worth pinning down is not the listing — it is the two places
 * this panel deliberately differs from the model-facing tools: clicking a
 * file hands it to the conversation rather than opening it, and deleting
 * goes to the Recycle Bin with no modal, because the bin *is* the undo.
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { FilesPanel } from '@/components/FilesPanel'

function mockBridge(handler: (method: string, params: Record<string, unknown>) => unknown) {
  const call = vi.fn((method: string, params: Record<string, unknown> = {}) =>
    Promise.resolve(handler(method, params)),
  )
  // @ts-expect-error — the test only needs `call`.
  window.aria = { call }
  return call
}

const ROOTS = {
  path: '',
  parent: null,
  entries: [
    { name: 'Downloads', path: 'C:\\Users\\x\\Downloads', kind: 'folder' },
    { name: 'C:\\', path: 'C:\\', kind: 'drive' },
  ],
}

const DOWNLOADS = {
  path: 'C:\\Users\\x\\Downloads',
  parent: 'C:\\Users\\x',
  entries: [
    {
      name: 'lease.pdf',
      path: 'C:\\Users\\x\\Downloads\\lease.pdf',
      kind: 'file',
      size: 2048,
      modified: Date.now() / 1000,
    },
  ],
}

function defaults(overrides: Record<string, unknown> = {}) {
  return (method: string, params: Record<string, unknown> = {}): unknown => {
    if (overrides[method] !== undefined) return overrides[method]
    if (method === 'files.browse') return params.path ? DOWNLOADS : ROOTS
    return { ok: true }
  }
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('FilesPanel', () => {
  it('starts at the places a person keeps things, plus every drive', async () => {
    mockBridge(defaults())
    render(<FilesPanel onClose={() => {}} />)

    expect(await screen.findByText('Downloads')).toBeDefined()
    expect(screen.getByText('C:\\')).toBeDefined()
  })

  it('walks into a folder and back out again', async () => {
    const call = mockBridge(defaults())
    render(<FilesPanel onClose={() => {}} />)

    fireEvent.click(await screen.findByText('Downloads'))

    expect(await screen.findByText('lease.pdf')).toBeDefined()
    await waitFor(() =>
      expect(call).toHaveBeenCalledWith('files.browse', { path: 'C:\\Users\\x\\Downloads' }),
    )

    fireEvent.click(screen.getByRole('button', { name: /Up/ }))
    await waitFor(() =>
      expect(call).toHaveBeenCalledWith('files.browse', { path: 'C:\\Users\\x' }),
    )
  })

  it('hands a clicked file to the conversation rather than opening it', async () => {
    // The point of having a browser inside her at all: finding a file and
    // asking about it should be one click, not a trip through the OS picker.
    const onAttach = vi.fn()
    mockBridge(defaults())
    render(<FilesPanel onClose={() => {}} onAttach={onAttach} />)

    fireEvent.click(await screen.findByText('Downloads'))
    fireEvent.click(await screen.findByText('lease.pdf'))

    expect(onAttach).toHaveBeenCalledWith('C:\\Users\\x\\Downloads\\lease.pdf')
  })

  it('deletes without a modal, because the Recycle Bin is the undo', async () => {
    // The one delete in the app with no confirmation round-trip. It is
    // allowed to be because it does not destroy anything — the same bargain
    // Explorer itself makes.
    const call = mockBridge(defaults())
    render(<FilesPanel onClose={() => {}} />)
    fireEvent.click(await screen.findByText('Downloads'))

    fireEvent.click(await screen.findByRole('button', { name: 'Delete lease.pdf' }))

    await waitFor(() =>
      expect(call).toHaveBeenCalledWith('files.delete', {
        path: 'C:\\Users\\x\\Downloads\\lease.pdf',
      }),
    )
    expect(screen.getByText(/Recycle Bin/)).toBeDefined()
  })

  it('renames in place, on Enter', async () => {
    const call = mockBridge(defaults())
    render(<FilesPanel onClose={() => {}} />)
    fireEvent.click(await screen.findByText('Downloads'))

    fireEvent.click(await screen.findByRole('button', { name: 'Rename lease.pdf' }))
    const input = screen.getByLabelText('New name for lease.pdf')
    fireEvent.change(input, { target: { value: 'tenancy.pdf' } })
    fireEvent.keyDown(input, { key: 'Enter' })

    await waitFor(() =>
      expect(call).toHaveBeenCalledWith('files.rename', {
        path: 'C:\\Users\\x\\Downloads\\lease.pdf',
        name: 'tenancy.pdf',
      }),
    )
  })

  it('shows what the sidecar refused rather than failing silently', async () => {
    // `tools/files.py`'s hard refusals still apply to a click — Windows and
    // Program Files were never confirmation mechanisms, and a panel is not a
    // reason to relax them. The user has to be told why nothing happened.
    mockBridge((method, params) => {
      if (method === 'files.browse') return params.path ? DOWNLOADS : ROOTS
      throw new Error('I will not delete C:\\Windows: it is a system folder.')
    })
    render(<FilesPanel onClose={() => {}} />)
    fireEvent.click(await screen.findByText('Downloads'))

    fireEvent.click(await screen.findByRole('button', { name: 'Delete lease.pdf' }))

    expect(await screen.findByText(/system folder/)).toBeDefined()
  })
})
