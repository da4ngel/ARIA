/**
 * The window: one pane of glass, everything else a layer inside it.
 *
 * A pure view (BUILD_SPEC §3). Every turn shown here is already in SQLite and
 * the model selection lives in the sidecar's `settings` table, so this whole
 * tree can be destroyed and rebuilt without losing anything.
 *
 * Two layout states, one component tree: empty puts the orb in the middle and
 * asks for a first message; conversation docks the orb into the header and
 * gives the room to the messages.
 */

import { AnimatePresence, motion } from 'framer-motion'
import { useCallback, useEffect, useState } from 'react'

import { ComposerBar } from '@/components/ComposerBar'
import { ConnectionStatus } from '@/components/ConnectionStatus'
import { ConversationView } from '@/components/ConversationView'
import { EmptyState } from '@/components/EmptyState'
import { HandsFreeToggle } from '@/components/HandsFreeToggle'
import { VoiceAura, type AuraMode } from '@/components/VoiceAura'
import { HistoryPanel } from '@/components/HistoryPanel'
import { ModelPicker } from '@/components/ModelPicker'
import { Orb } from '@/components/Orb'
import { SettingsPanel } from '@/components/SettingsPanel'
import { Shortcuts } from '@/components/Shortcuts'
import { useAudio } from '@/hooks/useAudio'
import { useConversation } from '@/hooks/useConversation'
import { useModels } from '@/hooks/useModels'
import { useHandsFree } from '@/hooks/useHandsFree'
import { usePublishVoiceLevel } from '@/hooks/usePublishVoiceLevel'
import { useWakeChime } from '@/hooks/useWakeChime'
import { usePushToTalk } from '@/hooks/usePushToTalk'
import { useRpc } from '@/hooks/useRpc'
import { useWindowMode } from '@/hooks/useWindowMode'

const drag = { WebkitAppRegion: 'drag' } as React.CSSProperties
const noDrag = { WebkitAppRegion: 'no-drag' } as React.CSSProperties

type Overlay = 'history' | 'settings' | 'shortcuts' | null

export default function App(): JSX.Element {
  const { status, assistantState, lastLog, restartBrain } = useRpc()
  const connected = status === 'connected'
  const { turns, busy, send, cancel, newChat, openSession, sessionId, lastFirstTokenMs } =
    useConversation(connected)
  const models = useModels(connected)
  const audio = useAudio()
  // A spoken turn is marked as such: the sidecar answers it on this machine
  // whatever the Smart bias says, because the network hop alone costs more
  // than the whole voice budget.
  const voice = usePushToTalk((text) => void send(text, { spoken: true }), connected)
  // Hands-free is the sidecar's loop, not this one: the renderer streams
  // frames and the wake word, endpointing and turn all happen there.
  const handsFree = useHandsFree(connected)
  const { expanded, toggle: toggleExpanded } = useWindowMode()
  const [overlay, setOverlay] = useState<Overlay>(null)

  const started = turns.length > 0
  // Real playback beats the sidecar's own state here: `speaking` should mean
  // sound is coming out, not that a turn finished and audio may be queued.
  const orbState = voice.listening
    ? 'listening'
    : audio.speaking
      ? 'speaking'
      : assistantState
  // Only meaningful while the microphone is actually open; push-to-talk
  // does not sample levels, so it contributes nothing here.
  const orbLevel = handsFree.active ? handsFree.level : 0

  // Her voice wins over the room's: while she is speaking the microphone is
  // still open and still hearing her, and drawing that as "listening" would
  // show the wrong half of the conversation.
  const auraMode: AuraMode = audio.speaking
    ? 'speaking'
    : orbState === 'listening'
      ? 'listening'
      : null
  const auraLevel = audio.speaking ? audio.getLevel : handsFree.getLevel
  // The same two numbers drive the screen-edge overlay, which has no audio
  // of its own. Nothing is sent while she is idle.
  usePublishVoiceLevel(auraMode, auraLevel)
  // Audible, because the glow only helps if you are looking at it.
  useWakeChime()

  // One keyboard map, so Esc has a defined meaning at every moment: close what
  // is on top, and only cancel a turn when nothing is covering it.
  useEffect(() => {
    const onKey = (event: KeyboardEvent): void => {
      const ctrl = event.ctrlKey || event.metaKey
      if (ctrl && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        setOverlay((o) => (o === 'history' ? null : 'history'))
      } else if (ctrl && event.key.toLowerCase() === 'n') {
        event.preventDefault()
        void newChat()
      } else if (ctrl && event.key.toLowerCase() === 'e') {
        event.preventDefault()
        toggleExpanded()
      } else if (event.key === '?' && !event.ctrlKey) {
        const target = event.target as HTMLElement | null
        // Not while typing — '?' is a real character in a message.
        if (target?.tagName !== 'TEXTAREA' && target?.tagName !== 'INPUT') {
          event.preventDefault()
          setOverlay((o) => (o === 'shortcuts' ? null : 'shortcuts'))
        }
      } else if (event.key === 'Escape') {
        if (overlay) {
          event.preventDefault()
          setOverlay(null)
        }
        // Otherwise ComposerBar handles it and cancels the turn.
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [overlay, newChat, toggleExpanded])

  const openFromHistory = useCallback(
    (id: string) => {
      void openSession(id)
      if (!expanded) setOverlay(null)
    },
    [openSession, expanded],
  )

  return (
    // Edge to edge: the window is no longer transparent, so an inset panel
    // would just frame its own background colour. Windows 11 rounds frameless
    // windows at the compositor, which is also what clips the acrylic.
    <div className="h-screen text-aria-text">
      <div className="glass sheen relative flex h-full overflow-hidden">
        {/* Behind everything and inert: it must never take a click or push the
            layout, only tint the window while there is a voice in it. */}
        <VoiceAura mode={auraMode} getLevel={auraLevel} />

        {/* Expanded turns history from an overlay into a permanent rail.
            18rem wide, not 16: at the narrower width every title truncated and
            the time and message count wrapped onto two lines. */}
        {expanded && (
          <aside className="relative z-10 w-72 shrink-0 border-r border-white/5" style={noDrag}>
            <HistoryPanel
              variant="rail"
              activeSessionId={sessionId}
              onOpen={openFromHistory}
              onClose={() => undefined}
            />
          </aside>
        )}

        <div className="relative z-10 flex min-w-0 flex-1 flex-col">
          <header
            className="flex shrink-0 items-center justify-between gap-2 px-3 py-2.5"
            style={drag}
          >
            <div className="flex min-w-0 items-center gap-2">
              {started && (
                <Orb state={orbState} connected={connected} size={20} level={orbLevel} />
              )}
              {started && (
                <span className="truncate text-small font-medium tracking-tight">Aria</span>
              )}
            </div>

            <div className="flex shrink-0 items-center gap-1" style={noDrag}>
              <IconButton
                label="History"
                hint="History (Ctrl+K)"
                onClick={() => setOverlay((o) => (o === 'history' ? null : 'history'))}
                active={overlay === 'history'}
                disabled={!connected}
              >
                <IconHistory />
              </IconButton>
              <IconButton
                label="New chat"
                hint="New chat (Ctrl+N)"
                onClick={() => void newChat()}
                disabled={!connected || !started}
              >
                <IconPlus />
              </IconButton>
              <HandsFreeToggle
                available={handsFree.available}
                phrase={handsFree.phrase}
                active={handsFree.active}
                level={handsFree.level}
                disabled={!connected}
                onToggle={handsFree.toggle}
              />
              <ModelPicker models={models} />
              <IconButton
                label={expanded ? 'Shrink' : 'Expand'}
                hint={expanded ? 'Shrink (Ctrl+E)' : 'Expand (Ctrl+E)'}
                onClick={toggleExpanded}
              >
                {expanded ? <IconShrink /> : <IconExpand />}
              </IconButton>
              <IconButton
                label="Settings"
                hint="Settings"
                onClick={() => setOverlay((o) => (o === 'settings' ? null : 'settings'))}
                active={overlay === 'settings'}
              >
                <IconGear />
              </IconButton>
            </div>
          </header>

          {/* Only ever shown when something is actually wrong. */}
          <AnimatePresence>
            {!connected && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mx-3 mb-2 overflow-hidden"
                style={noDrag}
              >
                <div className="raised rim flex items-center justify-between gap-2 rounded-lg px-2.5 py-1.5">
                  <ConnectionStatus status={status} />
                  <button
                    type="button"
                    onClick={restartBrain}
                    className="interactive shrink-0 rounded px-2 py-0.5 text-micro text-aria-muted hover:text-aria-text"
                  >
                    Restart
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {started ? (
            <ConversationView turns={turns} state={orbState} />
          ) : (
            <EmptyState state={orbState} connected={connected} onPick={send} level={orbLevel} />
          )}

          {handsFree.error && (
            <p className="mx-3 mb-1 truncate text-micro text-aria-warn" title={handsFree.error}>
              {handsFree.error}
            </p>
          )}

          {voice.error && (
            <p className="mx-3 mb-1 truncate text-micro text-aria-warn" title={voice.error}>
              {voice.error}
            </p>
          )}

          {lastLog && (
            <p className="mx-3 mb-1 truncate text-micro text-aria-warn" title={lastLog.message}>
              {lastLog.message}
            </p>
          )}

          <div className="px-3 pb-3" style={noDrag}>
            <ComposerBar busy={busy} disabled={!connected} voice={voice} onSend={send} onCancel={() => {
              audio.stop()
              void cancel()
            }} />
            <footer className="mt-1.5 flex items-center justify-between px-0.5 text-micro text-aria-faint">
              <button
                type="button"
                onClick={() => setOverlay('shortcuts')}
                className="interactive rounded px-1 py-0.5 hover:text-aria-muted"
              >
                Shortcuts
              </button>
              {/* The Phase 1 gate is a latency number, so it stays visible. */}
              {lastFirstTokenMs !== null && (
                <span
                  className={`font-mono tabular-nums ${
                    lastFirstTokenMs < 700 ? 'text-aria-faint' : 'text-aria-warn'
                  }`}
                  title="Time to first token"
                >
                  {Math.round(lastFirstTokenMs)}ms
                </span>
              )}
            </footer>
          </div>

          <AnimatePresence>
            {overlay === 'history' && !expanded && (
              <HistoryPanel
                key="history"
                activeSessionId={sessionId}
                onOpen={openFromHistory}
                onClose={() => setOverlay(null)}
              />
            )}
            {overlay === 'settings' && (
              <SettingsPanel
                key="settings"
                onClose={() => setOverlay(null)}
                onKeysChanged={models.refresh}
              />
            )}
            {overlay === 'shortcuts' && (
              <Shortcuts key="shortcuts" onClose={() => setOverlay(null)} />
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

// ── header controls ───────────────────────────────────────────────────

function IconButton({
  label,
  hint,
  onClick,
  children,
  active = false,
  disabled = false,
}: {
  label: string
  hint?: string
  onClick: () => void
  children: React.ReactNode
  active?: boolean
  disabled?: boolean
}): JSX.Element {
  return (
    <button
      type="button"
      aria-label={label}
      title={hint ?? label}
      onClick={onClick}
      disabled={disabled}
      className={`interactive grid h-7 w-7 place-items-center rounded-lg text-aria-muted hover:text-aria-text disabled:cursor-not-allowed disabled:opacity-30 disabled:hover:bg-transparent ${
        active ? 'bg-white/10 text-aria-text' : ''
      }`}
    >
      {children}
    </button>
  )
}

/* 14px stroke icons, drawn rather than imported — five glyphs is not worth a
   dependency, and these match the hairline weight of the rest of the chrome. */
const stroke = {
  width: 14,
  height: 14,
  viewBox: '0 0 14 14',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.4,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
}

function IconHistory(): JSX.Element {
  return (
    <svg {...stroke} aria-hidden>
      <circle cx="7" cy="7" r="5.2" />
      <path d="M7 4.2V7l1.9 1.4" />
    </svg>
  )
}

function IconPlus(): JSX.Element {
  return (
    <svg {...stroke} aria-hidden>
      <path d="M7 2.8v8.4M2.8 7h8.4" />
    </svg>
  )
}

function IconExpand(): JSX.Element {
  return (
    <svg {...stroke} aria-hidden>
      <path d="M8.4 2.6h3v3M5.6 11.4h-3v-3M11.4 2.6 8 6M2.6 11.4 6 8" />
    </svg>
  )
}

function IconShrink(): JSX.Element {
  return (
    <svg {...stroke} aria-hidden>
      <path d="M11.2 5.6h-3v-3M2.8 8.4h3v3M8.2 5.8 11.4 2.6M5.8 8.2 2.6 11.4" />
    </svg>
  )
}

function IconGear(): JSX.Element {
  return (
    <svg {...stroke} aria-hidden>
      <circle cx="7" cy="7" r="2.1" />
      <path d="M7 1.6v1.3M7 11.1v1.3M12.4 7h-1.3M2.9 7H1.6M10.8 3.2l-.9.9M4.1 9.9l-.9.9M10.8 10.8l-.9-.9M4.1 4.1l-.9-.9" />
    </svg>
  )
}
