/**
 * Phase 0 shell. A pure view over sidecar state (BUILD_SPEC §3).
 *
 * Everything here exists to prove the transport works; Phase 1 replaces the
 * body with ConversationView + ComposerBar.
 */

import { useState } from 'react'

import { ConnectionStatus } from '@/components/ConnectionStatus'
import { useRpc } from '@/hooks/useRpc'

interface Health {
  status: string
  version: string
  uptime_s: number
  db: boolean
  pending_probes: string[]
}

export default function App(): JSX.Element {
  const { status, lastEvent, lastLog, call, restartBrain } = useRpc()
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  const checkHealth = async (): Promise<void> => {
    try {
      setError(null)
      setHealth(await call<Health>('system.health'))
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    }
  }

  return (
    <div className="flex h-screen flex-col gap-4 rounded-2xl border border-aria-edge bg-aria-bg/95 p-5 text-aria-text backdrop-blur">
      <header className="flex items-center justify-between" style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}>
        <h1 className="text-lg font-semibold tracking-tight">Aria</h1>
        <span className="text-xs text-aria-muted">Phase 0</span>
      </header>

      <ConnectionStatus status={status} />

      <div className="flex gap-2" style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}>
        <button
          type="button"
          onClick={() => void checkHealth()}
          disabled={status !== 'connected'}
          className="rounded-lg border border-aria-edge px-3 py-1.5 text-sm hover:bg-aria-panel disabled:opacity-40"
        >
          system.health
        </button>
        <button
          type="button"
          onClick={restartBrain}
          className="rounded-lg border border-aria-edge px-3 py-1.5 text-sm hover:bg-aria-panel"
        >
          Restart brain
        </button>
      </div>

      {error && <p className="text-sm text-aria-bad">{error}</p>}

      {health && (
        <dl className="rounded-lg border border-aria-edge bg-aria-panel p-3 text-xs">
          <Row label="status" value={health.status} />
          <Row label="version" value={health.version} />
          <Row label="uptime" value={`${health.uptime_s.toFixed(1)}s`} />
          <Row label="db" value={String(health.db)} />
          <Row label="pending probes" value={health.pending_probes.join(', ') || 'none'} />
        </dl>
      )}

      <div className="mt-auto space-y-1 text-xs text-aria-muted">
        {lastEvent && (
          <p>
            last event: <span className="text-aria-text">{lastEvent.method}</span>{' '}
            {JSON.stringify(lastEvent.params)}
          </p>
        )}
        {lastLog && <p className="text-aria-warn">{lastLog.message}</p>}
        <p>Ctrl+Space toggles this window.</p>
      </div>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }): JSX.Element {
  return (
    <div className="flex justify-between gap-4 py-0.5">
      <dt className="text-aria-muted">{label}</dt>
      <dd className="truncate">{value}</dd>
    </div>
  )
}
