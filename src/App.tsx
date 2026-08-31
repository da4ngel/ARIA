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
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { FirstRun } from '@/components/FirstRun'
import { PanelBoundary } from '@/components/PanelBoundary'
import { HandsFreeToggle } from '@/components/HandsFreeToggle'
import { VoiceAura, type AuraMode } from '@/components/VoiceAura'
import { HistoryPanel } from '@/components/HistoryPanel'
import { ModelPicker } from '@/components/ModelPicker'
import { SettingsPanel } from '@/components/SettingsPanel'
import { Shortcuts } from '@/components/Shortcuts'
import { Sidebar, useSidebar, type Section } from '@/components/Sidebar'
import { ActivityPanel } from '@/components/ActivityPanel'
import { ClipboardPanel } from '@/components/ClipboardPanel'
import { MemoryPanel } from '@/components/MemoryPanel'
import { StudyPanel } from '@/components/StudyPanel'
import { FilesPanel } from '@/components/FilesPanel'
import { ModeSelector } from '@/components/ModeSelector'
import { SubModeSelector, type SubMode } from '@/components/SubModeSelector'
import { QuestionCard } from '@/components/QuestionCard'
import { PermissionModeChip } from '@/components/PermissionModeChip'
import { ToolsPanel } from '@/components/ToolsPanel'
import { VoicePanel } from '@/components/VoicePanel'
import { WindowControls } from '@/components/WindowControls'
import { useAudio } from '@/hooks/useAudio'
import { useConfirm } from '@/hooks/useConfirm'
import { useConversation } from '@/hooks/useConversation'
import { useModels } from '@/hooks/useModels'
import { useAskQuestion } from '@/hooks/useAskQuestion'
import { useConversationMode } from '@/hooks/useConversationMode'
import { usePermissionMode } from '@/hooks/usePermissionMode'
import { useFirstRun } from '@/hooks/useFirstRun'
import { useHandsFree } from '@/hooks/useHandsFree'
import { usePublishVoiceLevel } from '@/hooks/usePublishVoiceLevel'
import { useWakeChime } from '@/hooks/useWakeChime'
import { usePushToTalk } from '@/hooks/usePushToTalk'
import { useRpc } from '@/hooks/useRpc'
import { useWindowMode } from '@/hooks/useWindowMode'

const drag = { WebkitAppRegion: 'drag' } as React.CSSProperties
const noDrag = { WebkitAppRegion: 'no-drag' } as React.CSSProperties

/** What is open over the conversation. `Section` comes from the rail;
 *  `shortcuts` has no rail entry because it is reached by pressing `?`. */
type Overlay = Section | 'shortcuts' | null

export default function App(): JSX.Element {
  const { status, assistantState, lastLog, restartBrain } = useRpc()
  const connected = status === 'connected'
  const {
    turns,
    busy,
    send,
    cancel,
    newChat,
    openSession,
    rate,
    sessionId,
    sessionKind,
    lastFirstTokenMs,
  } =
    useConversation(connected)
  const models = useModels(connected)
  // Lifted so the header chip, the Tools panel and Settings all read one
  // value. Three independent fetches could disagree, and a selector that
  // disagrees with what is actually enforced is worse than none.
  const permissions = usePermissionMode(connected)
  const setup = useFirstRun(connected)
  // Per conversation, so it re-reads whenever the open chat changes.
  const answerMode = useConversationMode(sessionId, connected)
  const ask = useAskQuestion()
  // Handed from the Files panel to the composer. A one-shot value rather
  // than shared state: the composer owns its own attachment list, and two
  // places holding that would eventually disagree.
  const [pendingAttachment, setPendingAttachment] = useState<string | null>(null)
  // The sidecar's agent loop is suspended while one of these is open.
  const confirm = useConfirm()
  const audio = useAudio()
  // A spoken turn is marked as such: the sidecar answers it on this machine
  // whatever the Smart bias says, because the network hop alone costs more
  // than the whole voice budget.
  const voice = usePushToTalk((text) => void send(text, { spoken: true }), connected)
  // Hands-free is the sidecar's loop, not this one: the renderer streams
  // frames and the wake word, endpointing and turn all happen there.
  const handsFree = useHandsFree(connected)
  const { expanded, toggle: toggleExpanded, maximized, toggleMaximized } = useWindowMode()

  // Scale the whole interface with the window. Everything typographic is in
  // `rem`, so one class on `<html>` moves the type, the spacing and the
  // reading column together — see `html.roomy` in `index.css`. On the root
  // element and not `#root`, because that is what `rem` is measured against.
  useEffect(() => {
    document.documentElement.classList.toggle('roomy', maximized)
  }, [maximized])
  // Independent of the window mode above: how wide the rail is, versus how big
  // the window is. Conflating them meant a compact window could not show
  // labels and an expanded one could not hide them.
  const sidebar = useSidebar()
  const [overlay, setOverlay] = useState<Overlay>(null)
  //: How the open study chat is being run. Lifted here because two surfaces
  //: read it — the composer's picker and the Study panel's buttons — and two
  //: independent copies could disagree about what is running.
  const [subMode, setSubMode] = useState<SubMode>('learn')

  /** Open a fresh study chat and hand back its id.
   *
   *  `newChat` holds the reserved id in state, so reading it straight back is
   *  the same value the sidecar just minted — which is what the caller needs
   *  in order to name the session it means rather than letting the sidecar
   *  guess at "the latest one". */
  const openStudyChat = useCallback(async (): Promise<string | null> => {
    setSubMode('learn')
    return newChat('study')
  }, [newChat])

  /** Set the sub-mode on the open study chat and send its opener.
   *
   *  The opener comes back from the sidecar rather than being written here, so
   *  `study_modes.py` is the only place that decides what each one asks for. */
  const startStudy = useCallback(
    async (next: SubMode) => {
      if (!sessionId) return
      setSubMode(next)
      const started = await window.aria.call<{ opener: string }>('study.start', {
        session_id: sessionId,
        sub_mode: next,
      })
      if (started?.opener) void send(started.opener)
    },
    [sessionId, send],
  )

  const started = turns.length > 0
  // Real playback beats the sidecar's own state here: `speaking` should mean
  // sound is coming out, not that a turn finished and audio may be queued.
  const orbState = voice.listening ? 'listening' : audio.speaking ? 'speaking' : assistantState
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

  const selectSection = useCallback(
    (section: Section) => setOverlay((o) => (o === section ? null : section)),
    [],
  )

  // Chats live in the menu when there is room, and become a sheet when there
  // is not. One control either way — the previous split gave the menu a
  // collapse button and gave the chat list none. Room means the window is
  // expanded *and* the rail is not collapsed; either alone is not enough.
  const chatsInMenu = overlay === 'history' && expanded && !sidebar.collapsed

  // Collapsing the menu collapses what is inside it. Chats is part of the menu
  // now, so leaving it behind as a floating sheet would say the opposite.
  const toggleSidebar = useCallback(() => {
    if (chatsInMenu) setOverlay(null)
    sidebar.toggle()
  }, [chatsInMenu, sidebar])

  // **The whole window is a drop target, and a drop can never navigate.**
  //
  // Two problems, one handler. Chromium's default for a dropped file is to
  // navigate to it, so a drop that missed the composer replaced the entire UI
  // with `file:///C:/…` — and in compact mode the composer is a thin strip
  // across the bottom of a 420×600 window, so missing it is the normal
  // outcome rather than an edge case. Preventing the default fixes the crash;
  // accepting the file here fixes the thing that caused it.
  //
  // `electron/main.ts` still refuses the navigation as a backstop, because
  // this handler cannot run if the renderer has already been replaced.
  useEffect(() => {
    const over = (event: DragEvent): void => event.preventDefault()
    const drop = (event: DragEvent): void => {
      event.preventDefault()
      const paths = Array.from(event.dataTransfer?.files ?? [])
        .map((file) => (file as File & { path?: string }).path ?? '')
        .filter(Boolean)
      if (paths.length > 0) setPendingAttachment(paths[0])
    }
    window.addEventListener('dragover', over)
    window.addEventListener('drop', drop)
    return () => {
      window.removeEventListener('dragover', over)
      window.removeEventListener('drop', drop)
    }
  }, [])

  // One keyboard map, so Esc has a defined meaning at every moment: close what
  // is on top, and only cancel a turn when nothing is covering it.
  useEffect(() => {
    const onKey = (event: KeyboardEvent): void => {
      const ctrl = event.ctrlKey || event.metaKey
      if (ctrl && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        selectSection('history')
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
  }, [overlay, newChat, toggleExpanded, selectSection])

  const openFromHistory = useCallback(
    (id: string) => {
      void openSession(id)
      // The docked list stays open — it is the menu. A sheet is covering the
      // conversation the user just asked to see, so it goes.
      if (!chatsInMenu) setOverlay(null)
    },
    [openSession, chatsInMenu],
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

        {/* Above everything, including the history rail: it is holding a
            lock in the sidecar, so nothing else should be reachable. */}
        <ConfirmDialog request={confirm.current} onRespond={confirm.respond} />

        {/* **Over the shell, not inside the overlay stack.** On a real first
            run there is no conversation behind it worth seeing, and several
            of its steps decide whether the app can do anything at all.
            `needed` is null until the sidecar answers, so it never flashes
            on somebody who set this up months ago. */}
        {setup.needed === true && <FirstRun setup={setup} />}

        {/* The application menu, and the only place the parts of this app are
            named. Always present in both window modes. */}
        <Sidebar
          collapsed={sidebar.collapsed}
          onToggleCollapsed={toggleSidebar}
          canExpand={expanded}
          active={overlay === 'shortcuts' ? null : overlay}
          onSelect={selectSection}
          onNewChat={() => void newChat()}
          canNewChat={started}
          connected={connected}
          orbState={orbState}
          orbLevel={orbLevel}
          listening={handsFree.active}
        >
          {chatsInMenu && (
            <HistoryPanel
              variant="rail"
              activeSessionId={sessionId}
              onOpen={openFromHistory}
              onClose={() => setOverlay(null)}
            />
          )}
        </Sidebar>

        <div className="relative z-10 flex min-w-0 flex-1 flex-col">
          <header
            className="flex shrink-0 items-center justify-between gap-2 px-3 py-2"
            style={drag}
            // The Windows gesture. Costs nothing and is the first thing a lot
            // of people try on a title bar; without it the strip just ignores
            // them. Only meaningful once expanded — `toggleMaximized` handles
            // the compact case by expanding first.
            onDoubleClick={() => expanded && toggleMaximized()}
          >
            {/* Empty and draggable: the whole strip is the title bar, and the
                rail already carries the name and the orb. */}
            <div className="min-w-0 flex-1" />

            <div className="flex shrink-0 items-center gap-1" style={noDrag}>
              <HandsFreeToggle
                available={handsFree.available}
                phrase={handsFree.phrase}
                active={handsFree.active}
                level={handsFree.level}
                disabled={!connected}
                onToggle={handsFree.toggle}
              />
              <PermissionModeChip
                mode={permissions.mode}
                disabled={!connected}
                onOpen={() => setOverlay('tools')}
              />
              <ModelPicker models={models} />
              <WindowControls
                expanded={expanded}
                onToggleExpanded={toggleExpanded}
                maximized={maximized}
                onToggleMaximized={toggleMaximized}
              />
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
            <ConversationView
              turns={turns}
              state={orbState}
              onRate={rate}
              question={
                ask.pending ? (
                  <QuestionCard
                    pending={ask.pending}
                    index={ask.index}
                    onAnswer={ask.answer}
                    onDismiss={ask.dismiss}
                  />
                ) : null
              }
            />
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

          <div className="mx-auto w-full max-w-[var(--reading)] px-3 pb-3" style={noDrag}>
            <ComposerBar
              busy={busy}
              disabled={!connected}
              voice={voice}
              onSend={(text, attachments) => void send(text, { attachments })}
              attachPath={pendingAttachment}
              onAttachConsumed={() => setPendingAttachment(null)}
              onCancel={() => {
                audio.stop()
                void cancel()
              }}
            />
            <footer className="mt-1.5 flex items-center justify-between px-0.5 text-micro text-aria-faint">
              <div className="flex items-center gap-1">
                {/* In the composer, not the header: the mode belongs to the
                    message about to be sent, and the header already carries
                    four controls in a 420px window. */}
                {/* **The control changes with the kind of chat.** In a study
                    chat the useful question is not how she should answer but
                    how you are studying, so the same slot carries the six
                    sub-modes instead of the five modes. A study chat has no
                    mode to pick: it is Study, and the sidecar refuses to move
                    it. */}
                {sessionKind === 'study' ? (
                  <SubModeSelector
                    subMode={subMode}
                    disabled={!connected}
                    onSelect={(next) => void startStudy(next)}
                  />
                ) : (
                  <ModeSelector
                    mode={answerMode.mode}
                    label={answerMode.label}
                    needsOnline={answerMode.needsOnline}
                    disabled={!connected}
                    suggestion={answerMode.suggestion}
                    onSelect={(next) => void answerMode.setMode(next)}
                    onEnableOnline={() => setOverlay('settings')}
                    onDismissSuggestion={answerMode.dismissSuggestion}
                    onOpenStudyChat={() => void newChat('study')}
                  />
                )}
                <button
                  type="button"
                  onClick={() => setOverlay('shortcuts')}
                  className="interactive rounded px-1 py-0.5 hover:text-aria-muted"
                >
                  Shortcuts
                </button>
              </div>
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

          {/* Panels float over the conversation as glass sheets. History is
              the exception: when the window is expanded it is already a
              permanent column, so opening it again would be a sheet over a
              copy of itself. */}
          {/* `mode="wait"`: without it, switching panel A to B crossfades
              both at once and you briefly see two sheets stacked. One
              leaves, then the next arrives. */}
            {/* **A panel that throws must not blank the window.** There was
                no error boundary anywhere in this app until one bad payload
                unmounted the whole tree — the same symptom as the retheme's
                blank window, from an entirely different cause. Around the
                panels only: a boundary over the conversation would turn a
                crash in the thing you are reading into a quiet placeholder. */}
            <PanelBoundary name={overlay ?? 'panel'} onClose={() => setOverlay(null)}>
            <AnimatePresence mode="wait">
            {overlay === 'history' && !chatsInMenu && (
              <HistoryPanel
                key="history"
                activeSessionId={sessionId}
                onOpen={openFromHistory}
                onClose={() => setOverlay(null)}
              />
            )}
            {overlay === 'voice' && (
              <VoicePanel key="voice" handsFree={handsFree} onClose={() => setOverlay(null)} />
            )}
            {overlay === 'files' && (
              <FilesPanel
                key="files"
                onClose={() => setOverlay(null)}
                onAttach={(path) => {
                  // Close on pick. The panel is where you find a file; the
                  // conversation is where you ask about it, and leaving the
                  // sheet up over the composer you are about to type in
                  // helps nobody.
                  setOverlay(null)
                  setPendingAttachment(path)
                }}
              />
            )}
            {overlay === 'tools' && (
              <ToolsPanel
                key="tools"
                onClose={() => setOverlay(null)}
                mode={permissions.mode}
                setMode={permissions.setMode}
              />
            )}
            {overlay === 'memory' && <MemoryPanel key="memory" onClose={() => setOverlay(null)} />}
            {overlay === 'clipboard' && (
              <ClipboardPanel key="clipboard" onClose={() => setOverlay(null)} />
            )}
            {overlay === 'activity' && (
              <ActivityPanel key="activity" onClose={() => setOverlay(null)} />
            )}
            {overlay === 'study' && (
              <StudyPanel
                key="study"
                onClose={() => setOverlay(null)}
                onStudy={(text) => void send(text)}
                onNewStudyChat={openStudyChat}
                onOpenSession={(id) => void openSession(id)}
              />
            )}
            {overlay === 'settings' && (
              <SettingsPanel
                key="settings"
                onClose={() => setOverlay(null)}
                onKeysChanged={models.refresh}
                mode={permissions.mode}
                setMode={permissions.setMode}
                onReopenSetup={setup.reopen}
              />
            )}
            {overlay === 'shortcuts' && (
              <Shortcuts key="shortcuts" onClose={() => setOverlay(null)} />
            )}
          </AnimatePresence>
            </PanelBoundary>
        </div>
      </div>
    </div>
  )
}
