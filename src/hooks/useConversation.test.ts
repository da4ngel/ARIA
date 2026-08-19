/**
 * Stop, and the two ways it used to do nothing.
 *
 * Eyaas: *"im trying to click the stop, but when its still processing, i cant
 * stop it."* The sidecar was never at fault — measured live against the real
 * one, `chat.send` returns in 4ms, `chat.cancel` in 2ms, and not a single
 * token arrives after it. Both bugs were in this hook, and both come from the
 * same shape: it knows a turn is running before it knows *which* turn, and
 * treated knowing which as a precondition for stopping it and for noticing it
 * had ended.
 *
 * There was no test file for this hook at all before now, which is how a
 * button that silently does nothing survived.
 */

import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useConversation } from '@/hooks/useConversation'

type Handler = (event: { method: string; params: Record<string, unknown> }) => void

let emit: Handler = () => {}

function mockBridge(
  handler: (method: string, params: Record<string, unknown>) => unknown,
): ReturnType<typeof vi.fn> {
  const call = vi.fn((method: string, params: Record<string, unknown> = {}) =>
    Promise.resolve(handler(method, params)),
  )
  window.aria = {
    // The generic on the real `call` is what a test double cannot satisfy;
    // the hook only reaches for these three members.
    call: call as unknown as typeof window.aria.call,
    onEvent: (h: Handler) => {
      emit = h
      return () => {}
    },
    onLog: () => () => {},
  } as unknown as typeof window.aria
  return call
}

beforeEach(() => {
  vi.restoreAllMocks()
  emit = () => {}
})

describe('stopping a turn', () => {
  it('cancels the turn that is actually running', async () => {
    const call = mockBridge((method) =>
      method === 'chat.send' ? { turn_id: 't_1', session_id: 's_1' } : { ok: true },
    )
    const { result } = renderHook(() => useConversation(true))

    await act(async () => {
      await result.current.send('write me an essay')
    })
    await waitFor(() => expect(result.current.busy).toBe(true))

    await act(async () => {
      await result.current.cancel()
    })

    expect(call).toHaveBeenCalledWith('chat.cancel', { turn_id: 't_1' })
  })

  it('honours a stop pressed before the turn id has come back', async () => {
    // **The window nobody could see.** `setBusy(true)` runs before the
    // `chat.send` await, so the button says Stop while `activeTurnId` is still
    // null. The click used to return silently, and the only feedback was that
    // nothing happened.
    let release: (value: unknown) => void = () => {}
    const pending = new Promise((resolve) => {
      release = resolve
    })
    const call = mockBridge((method) => {
      if (method === 'chat.send') return pending
      return { ok: true }
    })

    const { result } = renderHook(() => useConversation(true))
    let sending: Promise<void>
    act(() => {
      sending = result.current.send('write me an essay')
    })
    await waitFor(() => expect(result.current.busy).toBe(true))

    // Stop, while the send is still in flight.
    await act(async () => {
      await result.current.cancel()
    })
    expect(call).not.toHaveBeenCalledWith('chat.cancel', expect.anything())

    await act(async () => {
      release({ turn_id: 't_2', session_id: 's_1' })
      await sending
    })

    expect(call).toHaveBeenCalledWith('chat.cancel', { turn_id: 't_2' })
  })

  it('does not leave the composer stuck on Stop when a completion arrives unmatched', async () => {
    // **The bug that made it look permanently broken.** `setBusy(false)` sat
    // inside the `payload.turn_id !== activeTurnId.current` guard, so a
    // completion the hook could not match left `busy` true forever — the
    // button showing Stop with nothing left to cancel.
    //
    // The ids can legitimately disagree: the RPC reply and the event stream
    // are separate Electron IPC channels with no ordering between them, so a
    // fast turn can complete before `chat.send` resolves.
    mockBridge(() => new Promise(() => {}))
    const { result } = renderHook(() => useConversation(true))

    act(() => {
      void result.current.send('hi')
    })
    await waitFor(() => expect(result.current.busy).toBe(true))

    act(() => {
      emit({
        method: 'turn.complete',
        params: { turn_id: 't_unknown', full_text: 'done', first_token_ms: 12 },
      })
    })

    await waitFor(() => expect(result.current.busy).toBe(false))
  })

  it('still ignores a completion belonging to a different, known turn', async () => {
    // The guard is narrowed, not removed. Once the hook knows which turn is
    // running, a stale completion from another one must not end it.
    mockBridge((method) =>
      method === 'chat.send' ? { turn_id: 't_3', session_id: 's_1' } : { ok: true },
    )
    const { result } = renderHook(() => useConversation(true))

    await act(async () => {
      await result.current.send('hello')
    })
    await waitFor(() => expect(result.current.busy).toBe(true))

    act(() => {
      emit({
        method: 'turn.complete',
        params: { turn_id: 't_somethingelse', full_text: 'not mine', first_token_ms: 5 },
      })
    })

    expect(result.current.busy).toBe(true)
  })

  it('does not carry a stop across to the next turn', async () => {
    // A stop that arrived too late for one turn must not silently kill the
    // next one the moment it starts.
    const call = mockBridge((method) =>
      method === 'chat.send' ? { turn_id: 't_4', session_id: 's_1' } : { ok: true },
    )
    const { result } = renderHook(() => useConversation(true))

    // Stop with nothing running at all: remembered, then discarded by `send`.
    await act(async () => {
      await result.current.cancel()
    })
    await act(async () => {
      await result.current.send('a fresh question')
    })

    expect(call).not.toHaveBeenCalledWith('chat.cancel', expect.anything())
  })
})
