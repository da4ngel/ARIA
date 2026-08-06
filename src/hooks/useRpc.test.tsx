import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useRpc } from '@/hooks/useRpc'
import type { BrainStatus, LogLine } from '@/types/bridge'

/** Stub the bridge and hand back the callbacks it registered, so a test can
 *  drive status and log lines the way the supervisor does. */
function mockBridge() {
  let onStatus: (status: BrainStatus) => void = () => {}
  let onLog: (line: LogLine) => void = () => {}

  // @ts-expect-error — the hook only touches these four.
  window.aria = {
    getStatus: () => Promise.resolve('starting' as BrainStatus),
    onStatus: (fn: (status: BrainStatus) => void) => {
      onStatus = fn
      return () => {}
    },
    onLog: (fn: (line: LogLine) => void) => {
      onLog = fn
      return () => {}
    },
    onEvent: () => () => {},
  }

  return {
    status: (next: BrainStatus) => act(() => onStatus(next)),
    log: (message: string) => act(() => onLog({ level: 'warn', message })),
  }
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('useRpc', () => {
  it('shows the last supervisor warning', async () => {
    const bridge = mockBridge()
    const { result } = renderHook(() => useRpc())

    bridge.log('Sidecar exited (code 1, signal none).')
    await waitFor(() => expect(result.current.lastLog?.message).toContain('Sidecar exited'))
  })

  it('clears the warning once the brain is connected again', async () => {
    const bridge = mockBridge()
    const { result } = renderHook(() => useRpc())

    bridge.status('reconnecting')
    bridge.log('Sidecar exited (code 1, signal none).')
    expect(result.current.lastLog).not.toBeNull()

    // The sidecar restarts itself, so this arrives on its own a second later.
    // Leaving the warning up would report a fault over a working app.
    bridge.status('connected')
    await waitFor(() => expect(result.current.lastLog).toBeNull())
    expect(result.current.status).toBe('connected')
  })

  it('keeps the warning while the brain is still down', async () => {
    const bridge = mockBridge()
    const { result } = renderHook(() => useRpc())

    bridge.log('Sidecar exited (code 1, signal none).')
    bridge.status('reconnecting')
    bridge.status('disconnected')

    expect(result.current.lastLog?.message).toContain('Sidecar exited')
  })
})
