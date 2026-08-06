/**
 * Model selection, grouped by provider, with Smart pinned at the top.
 *
 * Everything shown here comes from `providers/catalog.py` via `models.list` —
 * including why a model is unavailable. The renderer invents no copy of its
 * own, so the tooltip and the router can never disagree.
 */

import { useEffect, useRef, useState } from 'react'

import { SMART_ID, type UseModels } from '@/hooks/useModels'
import type { ModelAvailability, RoutingBias } from '@/types/bridge'

const PROVIDER_LABEL: Record<string, string> = {
  ollama: 'On this machine',
  openai: 'OpenAI',
  gemini: 'Gemini',
}

const PROVIDER_ORDER = ['ollama', 'openai', 'gemini']

const BIAS_LABEL: Record<RoutingBias, string> = {
  fastest: 'Fastest',
  balanced: 'Balanced',
  quality: 'Best answer',
}

const BIAS_HINT: Record<RoutingBias, string> = {
  fastest: 'Stays on this machine unless a turn clearly needs more. ~0.5s.',
  balanced: 'Cloud for real work, local for conversation.',
  quality: 'Cloud for anything beyond a greeting. Slower, and it costs API credit.',
}

/** Measured time-to-first-token, preferring what we have actually observed. */
function speedLabel(entry: ModelAvailability): string | null {
  const ms = entry.observed_ttft_ms ?? entry.model.ttft_ms_seed
  if (ms === null) return null
  const rendered = ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${Math.round(ms)}ms`
  return entry.observed_ttft_ms !== null ? `${rendered} observed` : `${rendered} measured`
}

function Tooltip({ entry }: { entry: ModelAvailability }): JSX.Element {
  const speed = speedLabel(entry)
  return (
    <div className="pointer-events-none absolute right-full top-0 mr-2 w-64 rounded-lg border border-aria-edge bg-aria-bg p-3 text-xs shadow-xl">
      <p className="font-semibold text-aria-text">{entry.model.label}</p>
      <p className="mt-1 text-aria-muted">{entry.model.best_for}</p>
      <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-aria-muted">
        {speed && <span>{speed}</span>}
        <span>{entry.model.cost === 'free' ? 'free' : `cost ${entry.model.cost}`}</span>
        <span>{entry.model.local ? 'private' : 'sends your message to the cloud'}</span>
      </div>
      {entry.model.caveat && <p className="mt-2 text-aria-warn">{entry.model.caveat}</p>}
      {!entry.available && entry.reason && <p className="mt-2 text-aria-bad">{entry.reason}</p>}
    </div>
  )
}

interface RowProps {
  entry: ModelAvailability
  selected: boolean
  onSelect: () => void
  onHover: (id: string | null) => void
  hovered: boolean
}

function Row({ entry, selected, onSelect, onHover, hovered }: RowProps): JSX.Element {
  const speed = speedLabel(entry)
  return (
    <div className="relative" onMouseEnter={() => onHover(entry.model.id)} onMouseLeave={() => onHover(null)}>
      <button
        type="button"
        disabled={!entry.available}
        onClick={onSelect}
        className={[
          'flex w-full items-center justify-between gap-2 rounded-md px-2 py-1.5 text-left text-xs',
          entry.available ? 'hover:bg-white/5' : 'cursor-not-allowed opacity-40',
          selected ? 'bg-white/10' : '',
        ].join(' ')}
      >
        <span className="flex min-w-0 items-center gap-1.5">
          {selected && <span className="text-aria-ok">✓</span>}
          <span className="truncate text-aria-text">{entry.model.label}</span>
        </span>
        <span className="shrink-0 text-[10px] text-aria-muted">
          {entry.available ? (speed ?? entry.model.cost) : 'unavailable'}
        </span>
      </button>
      {hovered && <Tooltip entry={entry} />}
    </div>
  )
}

export function ModelPicker({ models }: { models: UseModels }): JSX.Element {
  const [open, setOpen] = useState(false)
  const [hovered, setHovered] = useState<string | null>(null)
  const rootRef = useRef<HTMLDivElement>(null)

  // Click-away and Escape both close it.
  useEffect(() => {
    if (!open) return
    const onDown = (event: MouseEvent): void => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false)
    }
    const onKey = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', onDown)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDown)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  const smartSelected = models.selected === SMART_ID
  const current = models.models.find((m) => m.model.id === models.selected)
  const buttonLabel = smartSelected ? 'Smart' : (current?.model.label ?? models.selected)

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={() => {
          if (!open) void models.refresh()
          setOpen(!open)
        }}
        className="flex items-center gap-1 rounded-lg border border-aria-edge px-2 py-1 text-xs text-aria-muted hover:text-aria-text"
      >
        <span className="max-w-[10rem] truncate">{buttonLabel}</span>
        <span aria-hidden>▾</span>
      </button>

      {open && (
        <div className="absolute right-0 z-20 mt-1 max-h-[22rem] w-72 overflow-y-auto rounded-xl border border-aria-edge bg-aria-panel p-2 shadow-2xl">
          {/* Smart, pinned. */}
          <button
            type="button"
            onClick={() => {
              void models.select(SMART_ID)
              setOpen(false)
            }}
            className={[
              'w-full rounded-md px-2 py-1.5 text-left hover:bg-white/5',
              smartSelected ? 'bg-white/10' : '',
            ].join(' ')}
          >
            <span className="flex items-center gap-1.5 text-xs text-aria-text">
              {smartSelected && <span className="text-aria-ok">✓</span>}
              Smart
            </span>
            <span className="mt-0.5 block text-[10px] text-aria-muted">
              Picks a model per task. Private turns always stay local.
            </span>
          </button>

          {/* The bias only affects Smart, so it lives with it. */}
          {smartSelected && (
            <div className="mt-1 rounded-md bg-black/20 p-2">
              <div className="flex gap-1">
                {(Object.keys(BIAS_LABEL) as RoutingBias[]).map((bias) => (
                  <button
                    key={bias}
                    type="button"
                    onClick={() => void models.setBias(bias)}
                    className={[
                      'flex-1 rounded px-1.5 py-1 text-[10px]',
                      models.bias === bias
                        ? 'bg-white/15 text-aria-text'
                        : 'text-aria-muted hover:text-aria-text',
                    ].join(' ')}
                  >
                    {BIAS_LABEL[bias]}
                  </button>
                ))}
              </div>
              <p className="mt-1.5 text-[10px] text-aria-muted">{BIAS_HINT[models.bias]}</p>
            </div>
          )}

          {PROVIDER_ORDER.map((provider) => {
            const group = models.models.filter((m) => m.model.provider === provider)
            if (group.length === 0) return null
            return (
              <div key={provider} className="mt-2">
                <p className="px-2 pb-1 text-[10px] uppercase tracking-wide text-aria-muted">
                  {PROVIDER_LABEL[provider] ?? provider}
                </p>
                {group.map((entry) => (
                  <Row
                    key={entry.model.id}
                    entry={entry}
                    selected={entry.model.id === models.selected}
                    hovered={hovered === entry.model.id}
                    onHover={setHovered}
                    onSelect={() => {
                      void models.select(entry.model.id)
                      setOpen(false)
                    }}
                  />
                ))}
              </div>
            )
          })}

          {models.models.length === 0 && (
            <p className="px-2 py-3 text-xs text-aria-muted">
              {models.loading ? 'Loading models…' : 'No models reported. Is the brain connected?'}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
