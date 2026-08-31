/**
 * The wizard's gate, and the two states that are easy to get wrong.
 *
 * A first-run screen has exactly two ways of being annoying rather than
 * useful: showing itself to somebody who has already set the machine up, and
 * flashing for a frame on the way to deciding not to. Both come from the same
 * mistake — treating "I have not asked yet" as "no".
 */

import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useFirstRun, type SetupProgress } from '@/hooks/useFirstRun'

type Listener = (event: { method: string; params: Record<string, unknown> }) => void

let listeners: Listener[] = []

function mockBridge(handler: (method: string, params: Record<string, unknown>) => unknown) {
  const call = vi.fn((method: string, params: Record<string, unknown> = {}) =>
    Promise.resolve(handler(method, params)),
  )
  window.aria = {
    // The hook only touches `call` and `onEvent`; the rest of the bridge is
    // not what these tests are about.
    call,
    onEvent: (handler_: Listener) => {
      listeners.push(handler_)
      return () => {
        listeners = listeners.filter((l) => l !== handler_)
      }
    },
  } as unknown as typeof window.aria
  return call
}

const EMPTY_STATE = {
  ollama: { installed: false, running: false, models: [] },
  everything: { present: false },
  voice: { present: false, missing: ['kokoro-v1.0.onnx'], approx_bytes: 353_746_785 },
  wake_word: { present: false, missing: ['hey_jarvis_v0.1.onnx'], approx_bytes: 3_500_000 },
  keys: [],
  models_dir: 'C:/data/models',
}

beforeEach(() => {
  listeners = []
  vi.restoreAllMocks()
})

describe('whether the wizard shows at all', () => {
  it('is undecided until the sidecar answers, so it cannot flash', () => {
    mockBridge(() => new Promise(() => {})) // never resolves
    const { result } = renderHook(() => useFirstRun(true))
    // Not `false` — App.tsx renders on `=== true`, and a boolean default
    // would either show the wizard to everybody for a frame or hide it from
    // the one person who needs it.
    expect(result.current.needed).toBeNull()
  })

  it('opens when the settings row says it has never run', async () => {
    mockBridge((method) => (method === 'setup.done' ? { done: false } : EMPTY_STATE))
    const { result } = renderHook(() => useFirstRun(true))
    await waitFor(() => expect(result.current.needed).toBe(true))
  })

  it('stays shut for a machine that has been through it', async () => {
    mockBridge((method) => (method === 'setup.done' ? { done: true } : EMPTY_STATE))
    const { result } = renderHook(() => useFirstRun(true))
    await waitFor(() => expect(result.current.needed).toBe(false))
  })

  it('does not read the state of a machine it is not going to ask about', async () => {
    const call = mockBridge((method) => (method === 'setup.done' ? { done: true } : EMPTY_STATE))
    const { result } = renderHook(() => useFirstRun(true))
    await waitFor(() => expect(result.current.needed).toBe(false))
    expect(call.mock.calls.map(([method]) => method)).not.toContain('setup.state')
  })

  it('treats an unreachable brain as not a first run', async () => {
    // The status line already says the brain is down. A setup wizard on top
    // of that is a second, less accurate explanation of the same thing.
    mockBridge(() => {
      throw new Error('disconnected')
    })
    const { result } = renderHook(() => useFirstRun(true))
    await waitFor(() => expect(result.current.needed).toBe(false))
  })

  it('closes for good, and says so to the sidecar rather than to storage', async () => {
    const call = mockBridge((method) => (method === 'setup.done' ? { done: false } : EMPTY_STATE))
    const { result } = renderHook(() => useFirstRun(true))
    await waitFor(() => expect(result.current.needed).toBe(true))

    await act(async () => {
      await result.current.finish()
    })
    expect(result.current.needed).toBe(false)
    expect(call).toHaveBeenCalledWith('setup.done', { done: true })
  })

  it('reopens from Settings without clearing the row', async () => {
    const call = mockBridge((method) => (method === 'setup.done' ? { done: true } : EMPTY_STATE))
    const { result } = renderHook(() => useFirstRun(true))
    await waitFor(() => expect(result.current.needed).toBe(false))

    act(() => result.current.reopen())
    expect(result.current.needed).toBe(true)
    // Reopening is a view decision. Writing `done: false` would mean the
    // wizard came back on its own at the next launch.
    expect(call).not.toHaveBeenCalledWith('setup.done', { done: false })
  })
})

describe('progress', () => {
  it('follows setup.progress events while a download runs', async () => {
    mockBridge((method) => (method === 'setup.done' ? { done: false } : EMPTY_STATE))
    const { result } = renderHook(() => useFirstRun(true))
    await waitFor(() => expect(result.current.state).not.toBeNull())

    const params: SetupProgress = {
      kind: 'model',
      what: 'pulling ab12',
      received: 512,
      total: 1024,
      percent: 50,
      done: false,
      note: null,
    }
    act(() => {
      for (const listener of listeners) {
        listener({ method: 'setup.progress', params: params as unknown as Record<string, unknown> })
      }
    })
    expect(result.current.progress?.percent).toBe(50)
  })

  it('shows a returned error under the step instead of throwing it away', async () => {
    // The sidecar returns its failures rather than raising them, precisely so
    // this can happen — the user is looking at a step, and that is where
    // "could not reach Ollama" belongs.
    mockBridge((method) => {
      if (method === 'setup.done') return { done: false }
      if (method === 'setup.pull_model') return { ok: false, error: 'model not found' }
      return EMPTY_STATE
    })
    const { result } = renderHook(() => useFirstRun(true))
    await waitFor(() => expect(result.current.state).not.toBeNull())

    await act(async () => {
      await result.current.pullModel('nope:latest')
    })
    expect(result.current.error).toBe('model not found')
    expect(result.current.busy).toBeNull()
  })
})
