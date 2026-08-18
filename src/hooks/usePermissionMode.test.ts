/**
 * The permission mode's read, write and rollback.
 *
 * These moved here from `ToolsPanel.test.tsx` when the header chip and
 * Settings started sharing the same hook — the behaviour did not change, but
 * the thing responsible for it did, and a test that keeps asserting against
 * the old owner stops meaning anything.
 */

import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { usePermissionMode } from '@/hooks/usePermissionMode'

function mockBridge(handler: (method: string, params: Record<string, unknown>) => unknown) {
  const call = vi.fn((method: string, params: Record<string, unknown> = {}) =>
    Promise.resolve(handler(method, params)),
  )
  // @ts-expect-error — the test only needs `call`.
  window.aria = { call }
  return call
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('usePermissionMode', () => {
  it('shows the mode the sidecar reports, not a hardcoded default', async () => {
    mockBridge(() => ({ mode: 'manual', tools: [] }))

    const { result } = renderHook(() => usePermissionMode(true))

    await waitFor(() => expect(result.current.mode).toBe('manual'))
  })

  it('switches through permissions.mode', async () => {
    const call = mockBridge((method, params) =>
      method === 'permissions.mode'
        ? { mode: params.mode ?? 'auto' }
        : { mode: 'auto', tools: [] },
    )

    const { result } = renderHook(() => usePermissionMode(true))
    await waitFor(() => expect(result.current.mode).toBe('auto'))
    await act(async () => {
      await result.current.setMode('full_access')
    })

    expect(call).toHaveBeenCalledWith('permissions.mode', { mode: 'full_access' })
    expect(result.current.mode).toBe('full_access')
  })

  it('reverts and reports when the switch fails', async () => {
    // A selector left showing a mode that never took is worse than one that
    // visibly fails: it would tell the user nothing asks, while everything
    // still does — or, far worse, the reverse.
    mockBridge((method) => {
      if (method === 'permissions.mode') throw new Error('sidecar unreachable')
      return { mode: 'auto', tools: [] }
    })

    const { result } = renderHook(() => usePermissionMode(true))
    await waitFor(() => expect(result.current.mode).toBe('auto'))
    await act(async () => {
      await result.current.setMode('manual')
    })

    expect(result.current.mode).toBe('auto')
    expect(result.current.error).toBe('sidecar unreachable')
  })

  it('does not ask the sidecar anything while it is down', async () => {
    const call = mockBridge(() => ({ mode: 'manual', tools: [] }))

    renderHook(() => usePermissionMode(false))

    expect(call).not.toHaveBeenCalled()
  })
})
