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
  openrouter: 'OpenRouter (free tier)',
}

// Rendering maps over this array, so a provider missing from it is **invisible**
// — there is no fallback that lists the leftovers. OpenRouter goes last: it is
// the fallback tier, 50 requests a day, and nothing in it is routed to until it
// has passed measurement.
const PROVIDER_ORDER = ['ollama', 'openai', 'gemini', 'openrouter']

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

/**
 * Details for whichever model is under the pointer.
 *
 * A sheet pinned to the bottom of the panel rather than a floating tooltip: the
 * old one was 256px wide and positioned to the *left* of a 288px menu inside a
 * 420px window, so it ran off the screen edge every time. Fixed position also
 * means it no longer flickers as the pointer crosses between rows.
 */
function DetailSheet({ entry }: { entry: ModelAvailability }): JSX.Element {
  const speed = speedLabel(entry)
  const { model } = entry
  return (
    <div className="border-t border-white/5 bg-aria-sunk px-3 py-2.5">
      <p className="text-tiny font-strong text-aria-text">{model.label}</p>

      {model.best_for ? (
        <p className="mt-0.5 text-micro leading-relaxed text-aria-muted">{model.best_for}</p>
      ) : (
        // Blank, not filler. Nobody has measured this model here, and writing
        // a plausible sentence would be inventing the thing the catalog exists
        // to record.
        <p className="mt-0.5 text-micro leading-relaxed text-aria-faint">
          Offered by {PROVIDER_LABEL[model.provider] ?? model.provider}. Nothing about its speed,
          cost or accuracy has been measured here.
        </p>
      )}

      <div className="mt-1.5 flex flex-wrap gap-x-3 gap-y-0.5 font-mono text-micro text-aria-faint">
        {speed && <span>{speed}</span>}
        {model.cost !== '?' && (
          <span>{model.cost === 'free' ? 'free' : `cost ${model.cost}`}</span>
        )}
        <span>{model.local ? 'private' : 'leaves this machine'}</span>
        {model.discovered && <span>{(model.context_tokens / 1000).toFixed(0)}k context</span>}
      </div>

      {/* Stated plainly rather than implied by the word "free". Smart mode
          keeps files away from these on its own (router stage 2b), but which
          tier answered should never be a surprise. */}
      {model.trains_on_data && (
        <p className="mt-1.5 text-micro text-aria-warn">
          Free tier: this endpoint may train on what is sent to it. Files you attach are never
          routed here.
        </p>
      )}

      {model.caveat && <p className="mt-1.5 text-micro text-aria-warn">{model.caveat}</p>}
      {!entry.available && entry.reason && (
        <p className="mt-1.5 text-micro text-aria-bad">{entry.reason}</p>
      )}
    </div>
  )
}

interface RowProps {
  entry: ModelAvailability
  selected: boolean
  onSelect: () => void
  onHover: (id: string | null) => void
}

function Row({ entry, selected, onSelect, onHover }: RowProps): JSX.Element {
  const speed = speedLabel(entry)
  return (
    <div onMouseEnter={() => onHover(entry.model.id)} onFocus={() => onHover(entry.model.id)}>
      <button
        type="button"
        disabled={!entry.available}
        onClick={onSelect}
        className={[
          'flex w-full items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-left text-tiny',
          entry.available ? 'interactive' : 'cursor-not-allowed opacity-40',
          selected ? 'bg-white/10' : '',
        ].join(' ')}
      >
        <span className="flex min-w-0 items-center gap-1.5">
          <span
            className={`h-1 w-1 shrink-0 rounded-full ${
              selected ? 'bg-aria-ok' : entry.available ? 'bg-white/20' : 'bg-transparent'
            }`}
            aria-hidden
          />
          <span className="truncate text-aria-text">{entry.model.label}</span>
        </span>
        {/* Latency if it was measured, else price if it is known, else nothing.
            The fallback used to end at `cost`, which rendered a bare "?" on
            every discovered row — a column of question marks that says less
            than an empty column does. */}
        <span className="shrink-0 font-mono text-micro text-aria-faint">
          {!entry.available
            ? 'unavailable'
            : (speed ?? (entry.model.cost === '?' ? '' : entry.model.cost))}
        </span>
      </button>
    </div>
  )
}

export function ModelPicker({ models }: { models: UseModels }): JSX.Element {
  const [open, setOpen] = useState(false)
  const [hovered, setHovered] = useState<string | null>(null)
  // Folded by default, per provider. The measured models are the answer to
  // "which should I use"; the rest is a catalogue.
  const [expandedProviders, setExpandedProviders] = useState<string[]>([])
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
  // The sheet shows whatever is under the pointer, falling back to the current
  // selection so it never collapses to nothing and jumps the panel's height.
  const detail = models.models.find((m) => m.model.id === (hovered ?? models.selected))

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={() => {
          if (!open) void models.refresh()
          setOpen(!open)
        }}
        className="flex items-center gap-1 rounded-lg rim px-2 py-1 text-tiny text-aria-muted hover:text-aria-text"
      >
        <span className="max-w-[10rem] truncate">{buttonLabel}</span>
        <span aria-hidden>▾</span>
      </button>

      {open && (
        <div
          onMouseLeave={() => setHovered(null)}
          // Taller than it was. Measured on screen with the catalog listing 50
          // models: at 24rem the Smart block and the detail sheet left about
          // 100px for the list itself, which is four rows of fifty. Capped
          // against the viewport so the compact window cannot overflow.
          className="glass-pop absolute right-0 z-20 mt-1.5 flex max-h-[min(32rem,78vh)] w-72 flex-col overflow-hidden rounded-xl animate-rise"
        >
          <div className="min-h-0 flex-1 overflow-y-auto p-2">
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
            <span className="flex items-center gap-1.5 text-tiny text-aria-text">
              {smartSelected && <span className="text-aria-ok">✓</span>}
              Smart
            </span>
            <span className="mt-0.5 block text-micro text-aria-muted">
              Picks a model per task. Private turns always stay local.
            </span>
          </button>

          {/* The bias only affects Smart, so it lives with it. */}
          {smartSelected && (
            <div className="mt-1 rounded-md bg-aria-sunk p-2">
              <div className="flex gap-1">
                {(Object.keys(BIAS_LABEL) as RoutingBias[]).map((bias) => (
                  <button
                    key={bias}
                    type="button"
                    onClick={() => void models.setBias(bias)}
                    className={[
                      'flex-1 rounded px-1.5 py-1 text-micro',
                      models.bias === bias
                        ? 'bg-white/15 text-aria-text'
                        : 'text-aria-muted hover:text-aria-text',
                    ].join(' ')}
                  >
                    {BIAS_LABEL[bias]}
                  </button>
                ))}
              </div>
              <p className="mt-1.5 text-micro text-aria-muted">{BIAS_HINT[models.bias]}</p>
            </div>
          )}

          {PROVIDER_ORDER.map((provider) => {
            const group = models.models.filter((m) => m.model.provider === provider)
            if (group.length === 0) return null

            // Measured models are the ones with notes, latency and a known
            // cost — and the only ones Smart will route to. Everything the
            // provider merely *offers* goes below, folded away: this account
            // lists 32 OpenAI chat models, and a flat list of them buries the
            // three that were actually measured.
            const measured = group.filter((m) => !m.model.discovered)
            const found = group.filter((m) => m.model.discovered)
            const showFound = expandedProviders.includes(provider)

            const pick = (id: string) => () => {
              void models.select(id)
              setOpen(false)
            }

            return (
              <div key={provider} className="mt-2">
                <p className="px-2 pb-1 text-micro uppercase tracking-wide text-aria-muted">
                  {PROVIDER_LABEL[provider] ?? provider}
                </p>
                {measured.map((entry) => (
                  <Row
                    key={entry.model.id}
                    entry={entry}
                    selected={entry.model.id === models.selected}
                    onHover={setHovered}
                    onSelect={pick(entry.model.id)}
                  />
                ))}

                {found.length > 0 && (
                  <>
                    <button
                      type="button"
                      aria-expanded={showFound}
                      onClick={() =>
                        setExpandedProviders((current) =>
                          current.includes(provider)
                            ? current.filter((p) => p !== provider)
                            : [...current, provider],
                        )
                      }
                      className="interactive mt-0.5 flex w-full items-center gap-1 rounded-md px-2 py-1 text-micro text-aria-faint hover:text-aria-muted"
                    >
                      <span aria-hidden>{showFound ? '▾' : '▸'}</span>
                      {found.length} more offered, not measured here
                    </button>
                    {showFound &&
                      found.map((entry) => (
                        <Row
                          key={entry.model.id}
                          entry={entry}
                          selected={entry.model.id === models.selected}
                          onHover={setHovered}
                          onSelect={pick(entry.model.id)}
                        />
                      ))}
                  </>
                )}
              </div>
            )
          })}

          {models.models.length === 0 && (
            <p className="px-2 py-3 text-tiny text-aria-muted">
              {models.loading ? 'Loading models…' : 'No models reported. Is the brain connected?'}
            </p>
          )}

          <button
            type="button"
            disabled={models.rediscovering}
            onClick={() => void models.rediscover()}
            className="interactive mt-2 w-full rounded-md px-2 py-1.5 text-left text-micro text-aria-faint hover:text-aria-muted disabled:opacity-50"
          >
            {models.rediscovering
              ? 'Asking the providers…'
              : 'Check the providers for new models'}
          </button>
          </div>

          {detail && <DetailSheet entry={detail} />}
        </div>
      )}
    </div>
  )
}
