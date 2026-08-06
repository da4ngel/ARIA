/**
 * Phase 1.5 shell: a conversation over any of the configured models.
 *
 * A pure view (BUILD_SPEC §3). Every turn shown here is already in SQLite, and
 * the model selection lives in the sidecar's `settings` table — this component
 * can be destroyed and rebuilt without losing anything.
 */

import { useState } from 'react'

import { ComposerBar } from '@/components/ComposerBar'
import { ConnectionStatus } from '@/components/ConnectionStatus'
import { ConversationView } from '@/components/ConversationView'
import { ModelPicker } from '@/components/ModelPicker'
import { Orb } from '@/components/Orb'
import { SettingsPanel } from '@/components/SettingsPanel'
import { useConversation } from '@/hooks/useConversation'
import { useModels } from '@/hooks/useModels'
import { useRpc } from '@/hooks/useRpc'

export default function App(): JSX.Element {
  const { status, assistantState, lastLog, restartBrain } = useRpc()
  const connected = status === 'connected'
  const { turns, busy, send, cancel, newChat, lastFirstTokenMs } = useConversation(connected)
  const models = useModels(connected)
  const [settingsOpen, setSettingsOpen] = useState(false)

  return (
    <div className="relative flex h-screen flex-col gap-3 rounded-2xl border border-aria-edge bg-aria-bg/95 p-4 text-aria-text backdrop-blur">
      <header
        className="flex items-center justify-between gap-2"
        style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}
      >
        <div className="flex items-center gap-2">
          <Orb state={assistantState} />
          <h1 className="text-base font-semibold tracking-tight">Aria</h1>
        </div>
        <div
          className="flex items-center gap-1.5"
          style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
        >
          <button
            type="button"
            disabled={!connected || turns.length === 0}
            onClick={() => void newChat()}
            className="rounded-lg border border-aria-edge px-2 py-1 text-xs text-aria-muted hover:text-aria-text disabled:opacity-40"
          >
            New chat
          </button>
          <ModelPicker models={models} />
          <button
            type="button"
            onClick={() => setSettingsOpen(true)}
            aria-label="Settings"
            className="rounded-lg border border-aria-edge px-2 py-1 text-xs text-aria-muted hover:text-aria-text"
          >
            ⚙
          </button>
        </div>
      </header>

      <div style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}>
        <ConnectionStatus status={status} />
      </div>

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

      {settingsOpen && (
        <SettingsPanel onClose={() => setSettingsOpen(false)} onKeysChanged={models.refresh} />
      )}
    </div>
  )
}
