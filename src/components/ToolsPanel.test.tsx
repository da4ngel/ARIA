import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ToolsPanel } from '@/components/ToolsPanel'

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
  return (method: string, params: Record<string, unknown> = {}): unknown => {
    if (overrides[method] !== undefined) return overrides[method]
    if (method === 'tools.list') {
      return {
        mode: 'auto',
        tools: [{ name: 'open_app', tier: 1, description: 'Launch an app.' }],
      }
    }
    if (method === 'tools.trusted') return { paths: [] }
    // Echoes the requested mode back, matching the real RPC: setting a mode
    // returns that same mode as confirmation.
    if (method === 'permissions.mode') return { mode: params.mode ?? 'auto' }
    return { ok: true }
  }
}

const noop = (): void => {}

beforeEach(() => {
  vi.restoreAllMocks()
})

// The mode's own read, write and rollback moved into `usePermissionMode`
// when the header chip and Settings started sharing it — those behaviours
// are covered in `src/hooks/usePermissionMode.test.ts` now, against the hook
// that owns them. What is left here is what this panel is still responsible
// for: rendering the selection it is handed, and the trusted-folder list.

const MODE_PROPS = { mode: 'auto', setMode: async (): Promise<void> => {} } as const

describe('ToolsPanel', () => {
  it('shows the mode it is given, not a hardcoded default', async () => {
    mockBridge(defaults())
    render(<ToolsPanel onClose={noop} mode="manual" setMode={async () => {}} />)

    const manual = await screen.findByRole('button', { name: 'Manual' })
    expect(manual.className).toContain('bg-aria-accent')
  })

  it('asks to switch mode rather than deciding for itself', async () => {
    const setMode = vi.fn(async () => {})
    mockBridge(defaults())
    render(<ToolsPanel onClose={noop} mode="auto" setMode={setMode} />)

    fireEvent.click(await screen.findByRole('button', { name: 'Full access' }))

    await waitFor(() => expect(setMode).toHaveBeenCalledWith('full_access'))
  })

  it('names exactly what Full Access skips, in warning color', async () => {
    // Real risk this guards: a mode this permissive must never read as a
    // quiet convenience toggle — CLAUDE.md rule 5 is what it sets aside.
    mockBridge(defaults())
    render(<ToolsPanel onClose={noop} mode="full_access" setMode={async () => {}} />)

    const copy = await screen.findByText(/checkout-page warning/)
    expect(copy.className).toContain('text-aria-bad')
  })

  it('trusts every drive in one click, through tools.trust_all_drives', async () => {
    const call = mockBridge(defaults({ 'tools.trust_all_drives': { paths: ['C:\\', 'D:\\'] } }))
    render(<ToolsPanel onClose={noop} {...MODE_PROPS} />)

    fireEvent.click(await screen.findByRole('button', { name: 'Trust this entire computer' }))

    await waitFor(() => expect(call).toHaveBeenCalledWith('tools.trust_all_drives', {}))
    expect(await screen.findByText('C:\\')).toBeDefined()
    expect(await screen.findByText('D:\\')).toBeDefined()
  })
})
