/**
 * What she has learned, and the only way to correct it.
 *
 * §9 Phase 5 calls this "a requirement, not a nice-to-have", and the reason is
 * plain: reflection runs unattended overnight and can learn something wrong.
 * Without this you would be opening SQLite to fix it.
 *
 * Pinning is the important control. A pinned fact is one you asserted, and
 * §8.3 forbids reflection from superseding it — so the pin is what stops the
 * model quietly overwriting something you told it directly.
 */

import { useCallback, useState } from 'react'

import { Panel } from '@/components/Panel'
import { useMemory } from '@/hooks/useMemory'
import type { MemoryFact, ReflectionReport } from '@/types/bridge'

function confidenceStyle(confidence: number): string {
  if (confidence >= 0.75) return 'text-aria-ok'
  if (confidence >= 0.45) return 'text-aria-muted'
  return 'text-aria-faint'
}

function whenever(iso: string | null): string {
  if (!iso) return 'never'
  const at = new Date(iso.endsWith('Z') ? iso : `${iso}Z`)
  if (Number.isNaN(at.getTime())) return iso
  return at.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

function summarise(report: ReflectionReport): string {
  if (report.error) return report.error
  const parts = [
    report.inserted > 0 && `+${report.inserted} learned`,
    report.reinforced > 0 && `${report.reinforced} reinforced`,
    report.superseded > 0 && `${report.superseded} replaced`,
    report.blocked_by_pin > 0 && `${report.blocked_by_pin} pinned kept`,
    report.pruned > 0 && `${report.pruned} pruned`,
  ].filter(Boolean)
  if (parts.length === 0) return `Nothing new in ${report.messages_read} messages.`
  return `${parts.join(' · ')} — ${report.model}`
}

function FactRow({
  fact,
  onPin,
  onEdit,
  onForget,
}: {
  fact: MemoryFact
  onPin: (locked: boolean) => void
  onEdit: (object: string) => void
  onForget: () => void
}): JSX.Element {
  const [draft, setDraft] = useState<string | null>(null)
  // Rule 5's shape, scaled down: forgetting is destructive and irreversible,
  // so it takes two clicks rather than a dialog.
  const [armed, setArmed] = useState(false)

  const commit = useCallback(() => {
    const next = (draft ?? '').trim()
    setDraft(null)
    if (next && next !== fact.object) onEdit(next)
  }, [draft, fact.object, onEdit])

  return (
    <li className="raised rim flex items-baseline gap-2 rounded px-2 py-1 text-micro">
      <button
        type="button"
        title={fact.user_locked ? 'Pinned — reflection cannot change it' : 'Pin this'}
        aria-label={fact.user_locked ? 'Unpin this fact' : 'Pin this fact'}
        aria-pressed={fact.user_locked}
        onClick={() => onPin(!fact.user_locked)}
        className={`interactive shrink-0 rounded px-0.5 ${
          fact.user_locked ? 'text-aria-accent' : 'text-aria-faint hover:text-aria-muted'
        }`}
      >
        {fact.user_locked ? '★' : '☆'}
      </button>

      <span className="shrink-0 font-mono text-aria-muted">{fact.predicate}</span>

      {draft === null ? (
        <button
          type="button"
          onClick={() => setDraft(fact.object)}
          className="interactive min-w-0 flex-1 truncate text-left text-aria-text"
          title={`${fact.object} — click to edit`}
        >
          {fact.object}
        </button>
      ) : (
        <input
          autoFocus
          value={draft}
          spellCheck={false}
          onChange={(event) => setDraft(event.target.value)}
          onBlur={commit}
          onKeyDown={(event) => {
            if (event.key === 'Enter') commit()
            if (event.key === 'Escape') setDraft(null)
          }}
          className="rim min-w-0 flex-1 rounded bg-aria-sunk px-1 py-0.5 text-micro text-aria-text outline-none focus:rim-strong"
        />
      )}

      <span
        className={`shrink-0 tabular-nums ${confidenceStyle(fact.confidence)}`}
        title={`Confidence, from ${fact.evidence_count} observation${
          fact.evidence_count === 1 ? '' : 's'
        }`}
      >
        {fact.confidence.toFixed(2)}
        {fact.evidence_count > 1 && <span className="text-aria-faint">×{fact.evidence_count}</span>}
      </span>

      <button
        type="button"
        onClick={() => (armed ? onForget() : setArmed(true))}
        onBlur={() => setArmed(false)}
        className={`interactive shrink-0 rounded px-1 ${
          armed ? 'text-aria-bad' : 'text-aria-faint hover:text-aria-bad'
        }`}
      >
        {armed ? 'Sure?' : 'Forget'}
      </button>
    </li>
  )
}

export function MemoryPanel({ onClose }: { onClose: () => void }): JSX.Element {
  const memory = useMemory(true)
  const [report, setReport] = useState<ReflectionReport | null>(null)

  const runReflection = useCallback(async () => {
    setReport(await memory.reflect())
  }, [memory])

  const stats = memory.stats

  return (
    <Panel title="Memory" onClose={onClose} width="max-w-lg">
      {stats?.embeddings_ready === false && (
        <p className="rim mb-3 rounded bg-aria-sunk px-2 py-1.5 text-micro leading-relaxed text-aria-warn">
          Embeddings are unavailable, so she is matching on words rather than meaning. Run{' '}
          <span className="font-mono">ollama pull nomic-embed-text</span> to restore it. Nothing is
          lost in the meantime.
        </p>
      )}

      <div className="flex items-center gap-2">
        <input
          value={memory.query}
          spellCheck={false}
          placeholder="Search what she remembers"
          onChange={(event) => memory.setQuery(event.target.value)}
          className="rim min-w-0 flex-1 rounded bg-aria-sunk px-2 py-1 text-micro text-aria-text outline-none placeholder:text-aria-faint focus:rim-strong"
        />
        <button
          type="button"
          disabled={memory.reflecting}
          onClick={() => void runReflection()}
          title="Read the last day back and extract durable facts now"
          className="rim interactive shrink-0 rounded px-2 py-1 text-micro text-aria-muted hover:text-aria-text disabled:opacity-40"
        >
          {memory.reflecting ? 'Reflecting…' : 'Reflect now'}
        </button>
      </div>

      {report && (
        <p
          className={`mt-1.5 text-micro ${report.error ? 'text-aria-bad' : 'text-aria-muted'}`}
        >
          {summarise(report)}
        </p>
      )}

      <section className="mt-5">
        <h3 className="text-tiny font-semibold text-aria-text">
          Facts{stats && ` (${stats.facts})`}
        </h3>
        <ul className="mt-1.5 space-y-1">
          {memory.facts.length === 0 && !memory.loading && (
            <li className="text-micro text-aria-faint">
              Nothing learned yet. She picks things up as you talk, and reflection runs overnight —
              or press Reflect now.
            </li>
          )}
          {memory.facts.map((fact) => (
            <FactRow
              key={fact.id}
              fact={fact}
              onPin={(locked) => void memory.pin(fact.id, locked)}
              onEdit={(object) => void memory.edit(fact.id, object)}
              onForget={() => void memory.forget(fact.id)}
            />
          ))}
        </ul>
      </section>

      <section className="mt-5">
        <h3 className="text-tiny font-semibold text-aria-text">
          Conversations{stats && ` (${stats.episodes})`}
        </h3>
        <ul className="mt-1.5 space-y-1">
          {memory.episodes.length === 0 && !memory.loading && (
            <li className="text-micro text-aria-faint">
              No conversations summarised yet. One is written when a chat has been idle for half an
              hour, or when you start a new one.
            </li>
          )}
          {memory.episodes.map((episode) => (
            <li key={episode.id} className="raised rim rounded px-2 py-1.5 text-micro">
              <p className="leading-relaxed text-aria-text">{episode.summary}</p>
              <p className="mt-0.5 text-aria-faint">
                {whenever(episode.ended_at)} · worth {episode.salience.toFixed(2)}
                {episode.access_count > 0 && ` · recalled ${episode.access_count}×`}
              </p>
            </li>
          ))}
        </ul>
      </section>

      {stats && (
        <p className="mt-4 text-micro leading-relaxed text-aria-faint">
          Recall costs {stats.retrieval.p50_ms}ms typically, {stats.retrieval.p90_ms}ms at p90, over{' '}
          {stats.retrieval.count} turns — {stats.retrieval.empty} of which needed no memory at all.
          Last reflection {whenever(stats.last_reflection)}.
        </p>
      )}

      {memory.error && <p className="mt-3 text-tiny text-aria-bad">{memory.error}</p>}
    </Panel>
  )
}
