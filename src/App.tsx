/**
 * Phase 1 shell: a conversation over the local model.
 *
 * A pure view (BUILD_SPEC §3). Every turn shown here is already in SQLite;
 * this component can be destroyed and rebuilt without losing anything.
 */

import { ComposerBar } from '@/components/ComposerBar'
import { ConnectionStatus } from '@/components/ConnectionStatus'
import { ConversationView } from '@/components/ConversationView'
import { Orb } from '@/components/Orb'
import { useConversation } from '@/hooks/useConversation'
import { useRpc } from '@/hooks/useRpc'

export default function App(): JSX.Element {
  const { status, assistantState, lastLog, restartBrain } = useRpc()
  const connected = status === 'connected'
  const { turns, busy, send, cancel, lastFirstTokenMs } = useConversation(connected)

  return (
    <div className="flex h-screen flex-col gap-3 rounded-2xl border border-aria-edge bg-aria-bg/95 p-4 text-aria-text backdrop-blur">
      <header
        className="flex items-center justify-between"
        style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}
      >
        <div className="flex items-center gap-2">
          <Orb state={assistantState} />
          <h1 className="text-base font-semibold tracking-tight">Aria</h1>
        </div>
        <div style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}>
          <ConnectionStatus status={status} />
        </div>
      </header>

      <ConversationView turns={turns} />

      {lastLog && <p className="text-xs text-aria-warn">{lastLog.message}</p>}

      {!connected && (
        <button
          type="button"
          onClick={restartBrain}
          className="rounded-lg border border-aria-edge px-3 py-1.5 text-xs text-aria-muted hover:text-aria-text"
          style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
        >
          Restart brain
        </button>
      )}

      <ComposerBar busy={busy} disabled={!connected} onSend={send} onCancel={cancel} />

      <footer className="flex justify-between text-[10px] text-aria-muted">
        <span>Ctrl+Space toggles · Enter sends · Esc stops</span>
        {/* The Phase 1 gate is a latency number, so it stays visible. */}
        {lastFirstTokenMs !== null && (
          <span className={lastFirstTokenMs < 700 ? 'text-aria-ok' : 'text-aria-warn'}>
            first token {Math.round(lastFirstTokenMs)}ms
          </span>
        )}
      </footer>
    </div>
  )
}
