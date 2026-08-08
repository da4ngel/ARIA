import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { ModelPicker } from '@/components/ModelPicker'
import type { UseModels } from '@/hooks/useModels'
import type { ModelAvailability, ModelInfo } from '@/types/bridge'

function model(overrides: Partial<ModelInfo> = {}): ModelInfo {
  return {
    id: 'gpt-5',
    provider: 'openai',
    label: 'GPT-5',
    klass: 'smart',
    persona: 'full',
    cost: '$$$',
    best_for: 'Hardest reasoning, multi-step planning, and code.',
    ttft_ms_seed: 2434,
    caveat: null,
    local: false,
    context_tokens: 32768,
    discovered: false,
    ...overrides,
  }
}

function entry(overrides: Partial<ModelAvailability> = {}): ModelAvailability {
  return { model: model(), available: true, reason: null, observed_ttft_ms: null, ...overrides }
}

function models(overrides: Partial<UseModels> = {}): UseModels {
  return {
    models: [entry()],
    selected: 'smart',
    bias: 'quality',
    loading: false,
    select: vi.fn().mockResolvedValue(undefined),
    setBias: vi.fn().mockResolvedValue(undefined),
    refresh: vi.fn().mockResolvedValue(undefined),
    rediscover: vi.fn().mockResolvedValue(undefined),
    rediscovering: false,
    ...overrides,
  }
}

function open(props: UseModels): void {
  render(<ModelPicker models={props} />)
  fireEvent.click(screen.getByText('Smart'))
}

describe('ModelPicker', () => {
  it('shows Smart as the button label when nothing specific is picked', () => {
    render(<ModelPicker models={models()} />)
    expect(screen.getByText('Smart')).toBeDefined()
  })

  it('names the chosen model on the button instead', () => {
    render(<ModelPicker models={models({ selected: 'gpt-5' })} />)
    expect(screen.getByText('GPT-5')).toBeDefined()
  })

  it('groups models under their provider', () => {
    open(
      models({
        models: [
          entry(),
          entry({ model: model({ id: 'qwen2.5:7b', provider: 'ollama', label: 'Qwen', local: true }) }),
        ],
      }),
    )
    expect(screen.getByText('OpenAI')).toBeDefined()
    expect(screen.getByText('On this machine')).toBeDefined()
  })

  it('disables an unavailable model and keeps its reason for the tooltip', () => {
    open(
      models({
        models: [entry({ available: false, reason: 'No OpenAI API key stored. Add one in Settings.' })],
      }),
    )
    const row = screen.getByText('GPT-5').closest('button')
    expect(row?.hasAttribute('disabled')).toBe(true)
  })

  it('reveals best-for and the measured speed on hover', () => {
    open(models())
    fireEvent.mouseEnter(screen.getByText('GPT-5').closest('div')!)
    expect(screen.getByText(/Hardest reasoning/)).toBeDefined()
    // The label shows on the row and again in the tooltip.
    expect(screen.getAllByText('2.4s measured').length).toBeGreaterThan(0)
  })

  it('prefers observed latency over the catalog seed', () => {
    open(models({ models: [entry({ observed_ttft_ms: 800 })] }))
    fireEvent.mouseEnter(screen.getByText('GPT-5').closest('div')!)
    expect(screen.getAllByText('800ms observed').length).toBeGreaterThan(0)
    expect(screen.queryByText('2.4s measured')).toBeNull()
  })

  it('selects a model when its row is clicked', () => {
    const props = models()
    open(props)
    fireEvent.click(screen.getByText('GPT-5'))
    expect(props.select).toHaveBeenCalledWith('gpt-5')
  })

  it('offers the routing bias only while Smart is selected', () => {
    open(models())
    expect(screen.getByText('Best answer')).toBeDefined()
  })

  it('hides the routing bias once a specific model is picked', () => {
    render(<ModelPicker models={models({ selected: 'gpt-5' })} />)
    fireEvent.click(screen.getByText('GPT-5'))
    expect(screen.queryByText('Best answer')).toBeNull()
  })

  it('changes the bias', () => {
    const props = models()
    open(props)
    fireEvent.click(screen.getByText('Fastest'))
    expect(props.setBias).toHaveBeenCalledWith('fastest')
  })

  // ── discovered models ───────────────────────────────────────────────
  // Found by asking the provider rather than measured here. The picker's job
  // is to keep that distinction visible: these are selectable, but nothing is
  // known about them and it must not pretend otherwise.

  const found = (id: string, label: string): ModelAvailability =>
    entry({
      model: model({
        id,
        label,
        discovered: true,
        best_for: '',
        ttft_ms_seed: null,
        caveat: null,
        cost: '?',
        context_tokens: 400000,
      }),
    })

  it('folds discovered models away behind a count', () => {
    open(models({ models: [entry(), found('gpt-5.6-luna', 'GPT-5.6 Luna')] }))
    // The measured one is listed; the offered one is not, until asked for.
    expect(screen.getByText('GPT-5')).toBeDefined()
    expect(screen.queryByText('GPT-5.6 Luna')).toBeNull()
    expect(screen.getByText('1 more offered, not measured here')).toBeDefined()
  })

  it('reveals and selects a discovered model', () => {
    const props = models({ models: [entry(), found('gpt-5.6-luna', 'GPT-5.6 Luna')] })
    open(props)
    fireEvent.click(screen.getByText('1 more offered, not measured here'))
    fireEvent.click(screen.getByText('GPT-5.6 Luna'))
    expect(props.select).toHaveBeenCalledWith('gpt-5.6-luna')
  })

  it('states that a discovered model is unmeasured rather than inventing a blurb', () => {
    const luna = found('gpt-5.6-luna', 'GPT-5.6 Luna')
    render(<ModelPicker models={models({ models: [luna], selected: 'gpt-5.6-luna' })} />)
    fireEvent.click(screen.getByText('GPT-5.6 Luna'))
    expect(screen.getByText(/Nothing about its speed, cost or accuracy/)).toBeDefined()
  })

  it('shows no latency and no cost for a model nobody has measured', () => {
    const luna = found('gpt-5.6-luna', 'GPT-5.6 Luna')
    render(<ModelPicker models={models({ models: [luna], selected: 'gpt-5.6-luna' })} />)
    fireEvent.click(screen.getByText('GPT-5.6 Luna'))
    // A fabricated "$$" here would be worse than saying nothing, which is the
    // same rule discovery follows on the Python side.
    expect(screen.queryByText(/measured$/)).toBeNull()
    expect(screen.queryByText(/^cost /)).toBeNull()
    expect(screen.getByText('400k context')).toBeDefined()
  })

  it('leaves the row blank rather than printing a bare question mark', () => {
    // The fallback used to end at `cost`, so every discovered row showed "?"
    // in the column where a measured one shows its latency.
    open(models({ models: [entry(), found('gpt-5.6-luna', 'GPT-5.6 Luna')] }))
    fireEvent.click(screen.getByText('1 more offered, not measured here'))
    expect(screen.queryByText('?')).toBeNull()
  })

  it('asks the providers for new models on demand', () => {
    const props = models()
    open(props)
    fireEvent.click(screen.getByText('Check the providers for new models'))
    expect(props.rediscover).toHaveBeenCalled()
  })
})
