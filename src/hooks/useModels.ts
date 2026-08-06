/**
 * Model catalog, availability and the current selection.
 *
 * A pure mirror of the sidecar (CLAUDE.md rule 1): the selection lives in the
 * `settings` table, not here. This hook only caches what `models.list` last
 * said so the picker can render without a round-trip per keystroke.
 */

import { useCallback, useEffect, useState } from 'react'

import type { ModelAvailability, ModelListing, RoutingBias } from '@/types/bridge'

export const SMART_ID = 'smart'

export interface UseModels {
  models: ModelAvailability[]
  selected: string
  bias: RoutingBias
  loading: boolean
  select: (modelId: string) => Promise<void>
  setBias: (bias: RoutingBias) => Promise<void>
  refresh: () => Promise<void>
}

export function useModels(connected: boolean): UseModels {
  const [models, setModels] = useState<ModelAvailability[]>([])
  const [selected, setSelected] = useState<string>(SMART_ID)
  const [bias, setBiasState] = useState<RoutingBias>('quality')
  const [loading, setLoading] = useState(false)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      const listing = await window.aria.call<ModelListing>('models.list', {})
      setModels(listing.models)
      setSelected(listing.selected)
      setBiasState(listing.bias)
    } catch {
      /* the status line already reports that the brain is down */
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!connected) return
    void refresh()
  }, [connected, refresh])

  const select = useCallback(
    async (modelId: string) => {
      const previous = selected
      setSelected(modelId) // optimistic; the picker should not feel laggy
      try {
        await window.aria.call('models.select', { model: modelId })
      } catch {
        setSelected(previous)
      }
    },
    [selected],
  )

  const setBias = useCallback(
    async (next: RoutingBias) => {
      const previous = bias
      setBiasState(next)
      try {
        await window.aria.call('models.bias', { bias: next })
      } catch {
        setBiasState(previous)
      }
    },
    [bias],
  )

  return { models, selected, bias, loading, select, setBias, refresh }
}
