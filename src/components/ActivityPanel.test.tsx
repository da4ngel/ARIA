/**
 * The activity panel.
 *
 * The assertions that matter are about honesty rather than layout: an unpriced
 * model must not read as free, an uncounted turn must not read as zero tokens,
 * and the cost must never be presented as anything but an estimate with a date
 * on it.
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ActivityPanel } from '@/components/ActivityPanel'
import { explainStage } from '@/hooks/useActivity'
import type { Reminder, ToolRecord, TurnRecord, UsageReport } from '@/types/bridge'

function usage(overrides: Partial<UsageReport> = {}): UsageReport {
  return {
    since: '2026-08-24T00:00:00Z',
    days: 1,
    turns: 12,
    local_turns: 8,
    cloud_turns: 4,
    models: [],
    prompt_tokens: 4200,
    completion_tokens: 900,
    uncounted: 0,
    estimated_usd: 0.0123,
    unpriced_turns: 0,
    prices_as_of: '2026-08-24',
    ...overrides,
  }
}

function turn(overrides: Partial<TurnRecord> = {}): TurnRecord {
  return {
    id: 1,
    message_id: 10,
    model: 'gpt-5.4-nano',
    provider: 'openai',
    local: 0,
    stage: 'quality',
    detail: '',
    bias: 'quality',
    spoken: 0,
    tool_shaped: 0,
    chars: 40,
    latency_ms: 2400,
    tool_called: null,
    tool_ok: null,
    prompt_tokens: 800,
    completion_tokens: 120,
    rating: null,
    created_at: '2026-08-24T09:00:00Z',
    ...overrides,
  }
}

function reminder(overrides: Partial<Reminder> = {}): Reminder {
  return {
    id: 1,
    text: 'call the bank',
    due_at: '2026-08-24T12:00:00Z',
    created_at: '2026-08-24T09:00:00Z',
    overdue: false,
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

function defaults(
  report: UsageReport,
  turns: TurnRecord[] = [],
  reminders: Reminder[] = [],
  tools: ToolRecord[] = [],
) {
  return (method: string): unknown => {
    if (method === 'usage.today') return report
    if (method === 'usage.recent') return { turns, tools }
    if (method === 'reminders.list') return { reminders }
    return { ok: true }
  }
}

const noop = (): void => {}

describe('ActivityPanel', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('shows the local and cloud split', async () => {
    mockBridge(defaults(usage()))
    render(<ActivityPanel onClose={noop} />)
    expect(await screen.findByText('12')).toBeTruthy()
    expect(await screen.findByText(/8 local · 4 cloud/)).toBeTruthy()
  })

  it('always dates the cost and calls it estimated', async () => {
    mockBridge(defaults(usage()))
    render(<ActivityPanel onClose={noop} />)
    expect(await screen.findByText(/Estimated cost/i)).toBeTruthy()
    expect(await screen.findByText(/rates as of 2026-08-24/)).toBeTruthy()
  })

  it('says how many turns the price table does not cover', async () => {
    // **The number that stops a short total reading as complete.**
    mockBridge(defaults(usage({ unpriced_turns: 4 })))
    render(<ActivityPanel onClose={noop} />)
    expect(await screen.findByText(/4 turns unpriced/)).toBeTruthy()
    expect(await screen.findByText(/providers\/pricing\.py/)).toBeTruthy()
  })

  it('reports uncounted turns rather than folding them into the token total', async () => {
    mockBridge(defaults(usage({ uncounted: 3 })))
    render(<ActivityPanel onClose={noop} />)
    expect(await screen.findByText(/3 turns uncounted/)).toBeTruthy()
  })

  it('shows an unpriced model as unpriced, never as zero', async () => {
    mockBridge(
      defaults(
        usage({
          models: [
            {
              model: 'some/free-model',
              provider: 'openrouter',
              local: false,
              turns: 2,
              prompt_tokens: 100,
              completion_tokens: 50,
              uncounted: 0,
              avg_latency_ms: 900,
              estimated_usd: null,
            },
          ],
        }),
      ),
    )
    render(<ActivityPanel onClose={noop} />)
    expect(await screen.findByText(/unpriced/)).toBeTruthy()
  })

  it('expands a turn to say why that model was chosen', async () => {
    mockBridge(defaults(usage(), [turn({ stage: 'private' })]))
    render(<ActivityPanel onClose={noop} />)

    const row = await screen.findByText('gpt-5.4-nano')
    expect(screen.getByText(/looked private/)).toBeTruthy()
    fireEvent.click(row)
    expect(await screen.findByText('800 in / 120 out')).toBeTruthy()
    expect(await screen.findByText('2.4s')).toBeTruthy()
  })

  it('says "not counted" for a turn whose provider reported no usage', async () => {
    mockBridge(defaults(usage(), [turn({ prompt_tokens: null, completion_tokens: null })]))
    render(<ActivityPanel onClose={noop} />)
    fireEvent.click(await screen.findByText('gpt-5.4-nano'))
    expect(await screen.findByText('not counted')).toBeTruthy()
  })

  it('cancels a reminder with no confirmation', async () => {
    const call = mockBridge(defaults(usage(), [], [reminder({ id: 9 })]))
    render(<ActivityPanel onClose={noop} />)

    fireEvent.click(await screen.findByText('cancel'))
    await waitFor(() => expect(call).toHaveBeenCalledWith('reminders.cancel', { id: 9 }))
  })

  it('marks an overdue reminder as overdue', async () => {
    mockBridge(defaults(usage(), [], [reminder({ overdue: true })]))
    render(<ActivityPanel onClose={noop} />)
    expect(await screen.findByText(/overdue/)).toBeTruthy()
  })

  it('survives a payload missing every list', async () => {
    mockBridge((method) => (method === 'usage.today' ? usage() : { ok: true }))
    render(<ActivityPanel onClose={noop} />)
    expect(await screen.findByText(/Nothing recorded yet/i)).toBeTruthy()
  })
})

describe('explainStage', () => {
  it('translates the router stages it knows', () => {
    expect(explainStage(turn({ stage: 'private' }))).toMatch(/private/)
    expect(explainStage(turn({ stage: 'explicit' }))).toMatch(/you picked/)
  })

  it('falls back to the detail the router wrote for a stage added later', () => {
    // `stage`/`detail` are the router's own RouteReason, so a row explains
    // itself even when this table has not learned the vocabulary.
    expect(explainStage(turn({ stage: 'brand-new', detail: 'a rule added later' }))).toBe(
      'a rule added later',
    )
  })
})

describe('the undo timeline', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  function withTimeline(entries: unknown[]) {
    return mockBridge((method) => {
      if (method === 'usage.today') return usage()
      if (method === 'usage.recent') return { turns: [], tools: [] }
      if (method === 'reminders.list') return { reminders: [] }
      if (method === 'undo.list') return { entries }
      return { ok: true, message: 'Put notes.txt back where it was.' }
    })
  }

  const reversible = {
    id: 4,
    tool: 'move_file',
    kind: 'move',
    summary: 'Moved notes.txt to Documents',
    created_at: '2026-08-24T09:00:00Z',
    undone_at: null,
    blocked: null,
    undoable: true,
  }

  it('lists what can be taken back', async () => {
    withTimeline([reversible])
    render(<ActivityPanel onClose={noop} />)
    expect(await screen.findByText('Moved notes.txt to Documents')).toBeTruthy()
  })

  it('reverses without a confirmation, and says what happened', async () => {
    // No dialog: the button *is* the decision. The *tool* path is CONFIRM,
    // because there a model chose the entry rather than a person.
    const call = withTimeline([reversible])
    render(<ActivityPanel onClose={noop} />)

    fireEvent.click(await screen.findByText('undo'))
    await waitFor(() => expect(call).toHaveBeenCalledWith('undo.apply', { id: 4 }))
    expect(await screen.findByText('Put notes.txt back where it was.')).toBeTruthy()
  })

  it('shows a reason instead of a dead button when it cannot be reversed', async () => {
    withTimeline([
      { ...reversible, undoable: false, blocked: 'notes.txt is not there any more' },
    ])
    render(<ActivityPanel onClose={noop} />)

    expect(await screen.findByText('notes.txt is not there any more')).toBeTruthy()
    expect(screen.queryByText('undo')).toBeNull()
  })

  it('survives a payload with no timeline at all', async () => {
    mockBridge((method) => (method === 'usage.today' ? usage() : { ok: true }))
    render(<ActivityPanel onClose={noop} />)
    expect(await screen.findByText(/Nothing recorded yet/i)).toBeTruthy()
  })
})
