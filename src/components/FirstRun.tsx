/**
 * The first-run wizard (BUILD_SPEC §9 Phase 9).
 *
 * **Not a panel.** Every other surface here is a sheet over the conversation,
 * dismissed with Escape and a backdrop click. This one covers the shell
 * instead: on a genuine first run there is no conversation behind it to see,
 * and half the steps decide whether the app can do anything at all.
 *
 * **Opaque, not 95%.** The first version let the rail ghost through at 5%,
 * which read as a rendering fault rather than as depth — visible only by
 * actually looking at it. A takeover screen is a takeover screen.
 *
 * Five steps plus the microphone, in the order §9 names them. Each says what
 * is missing, what it costs, and offers exactly one button — and **every one
 * of them is skippable**, because none of this is required to type a question
 * to a cloud model, and a setup screen that will not let you past it is how
 * an app gets closed before it is ever used.
 */

import { motion, useReducedMotion } from 'framer-motion'
import { useState } from 'react'

import { DEFAULT_MODEL, type UseFirstRun } from '@/hooks/useFirstRun'
import { TWEEN, still } from '@/styles/motion'

/** Bytes as something a person can weigh a download against. */
function size(bytes: number): string {
  if (bytes >= 1 << 30) return `${(bytes / (1 << 30)).toFixed(1)}GB`
  return `${Math.round(bytes / (1 << 20))}MB`
}

function Step({
  n,
  title,
  done,
  optional,
  children,
}: {
  n: number
  title: string
  done: boolean
  optional?: boolean
  children: React.ReactNode
}): JSX.Element {
  return (
    <section className="rim raised rounded-xl px-3 py-2.5">
      <header className="flex items-baseline gap-2">
        <span
          aria-hidden
          className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-micro ${
            done ? 'bg-aria-ok/20 text-aria-ok' : 'bg-white/10 text-aria-muted'
          }`}
        >
          {done ? '✓' : n}
        </span>
        <h3 className="text-small font-medium text-aria-text">{title}</h3>
        {optional && <span className="text-micro text-aria-faint">optional</span>}
      </header>
      <div className="mt-1 pl-7 text-micro leading-relaxed text-aria-muted">{children}</div>
    </section>
  )
}

function Action({
  label,
  onClick,
  busy,
  disabled,
}: {
  label: string
  onClick: () => void
  busy?: boolean
  disabled?: boolean
}): JSX.Element {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy || disabled}
      className="rim interactive mt-2 block rounded-lg px-2 py-1 text-micro text-aria-text disabled:opacity-40"
    >
      {busy ? 'Working…' : label}
    </button>
  )
}

/** One bar, shared by all three downloads.
 *
 *  A null percentage is a real state, not zero: "pulling manifest" and
 *  "verifying sha256 digest" carry no totals, and a bar that read them as
 *  zero would snap back to the start between every layer. */
function Progress({
  percent,
  what,
  note,
}: {
  percent: number | null
  what: string
  note: string | null
}): JSX.Element {
  return (
    <div className="mt-1.5">
      <div className="h-1 overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full bg-aria-accent transition-all ${percent === null ? 'w-1/3 opacity-50' : ''}`}
          style={percent === null ? undefined : { width: `${percent}%` }}
        />
      </div>
      <p className="mt-1 truncate text-micro text-aria-faint">
        {what}
        {percent !== null && ` — ${percent}%`}
        {note && ` (${note})`}
      </p>
    </div>
  )
}

export function FirstRun({ setup }: { setup: UseFirstRun }): JSX.Element {
  const reduced = useReducedMotion()
  const [model, setModel] = useState(DEFAULT_MODEL)
  const s = setup.state

  const hasModel = Boolean(s?.ollama.models.length)
  const anyKey = Boolean(s?.keys.some((k) => k.present))
  const bar = (kind: string): JSX.Element | null =>
    setup.progress && setup.progress.kind === kind ? (
      <Progress
        percent={setup.progress.percent}
        what={setup.progress.what}
        note={setup.progress.note}
      />
    ) : null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={still(TWEEN.base, reduced)}
      className="absolute inset-0 z-50 flex flex-col bg-aria-void"
    >
      <div className="mx-auto flex w-full max-w-[var(--reading)] flex-1 flex-col gap-2 overflow-y-auto px-4 py-5">
        <header className="mb-1">
          <h2 className="font-display text-hero text-aria-text">Set up ARIA</h2>
          <p className="mt-0.5 text-tiny text-aria-dim">
            Everything here is optional — she will answer questions without any of it. Each step
            says what it costs before it starts.
          </p>
        </header>

        {!s && <p className="text-micro text-aria-faint">Reading what this machine has…</p>}

        {s && (
          <>
            <Step n={1} title="Ollama" done={s.ollama.running}>
              {s.ollama.running ? (
                'Running. Local models answer without sending anything off this machine.'
              ) : s.ollama.installed ? (
                'Installed but not answering. ARIA starts it herself — give it a moment and refresh.'
              ) : (
                <>
                  Not installed. Without it she can still use a cloud model, but nothing runs
                  locally. Get it from <span className="text-aria-dim">ollama.com/download</span>.
                </>
              )}
              <Action label="Check again" onClick={() => void setup.refresh()} />
            </Step>

            <Step n={2} title="A local model" done={hasModel}>
              {hasModel ? (
                <>Pulled: {s.ollama.models.join(', ')}.</>
              ) : (
                <>
                  {/* Named rather than asked about: "which model" is not a
                      question a first run should be putting to anybody. */}
                  Nothing pulled yet. <span className="text-aria-dim">{DEFAULT_MODEL}</span> is the
                  default — about 4.7GB, and the download runs here rather than in a terminal.
                </>
              )}
              <input
                value={model}
                onChange={(event) => setModel(event.target.value)}
                aria-label="Model to pull"
                className="rim mt-1.5 block w-full rounded-lg bg-aria-sunk px-2 py-1 text-micro text-aria-text"
              />
              <Action
                label={hasModel ? 'Pull another' : 'Pull it'}
                busy={setup.busy === 'model'}
                disabled={!s.ollama.running || !model.trim()}
                onClick={() => void setup.pullModel(model.trim())}
              />
              {bar('model')}
            </Step>

            <Step n={3} title="Her voice" done={s.voice.present} optional>
              {s.voice.present
                ? 'The speech weights are here. She can read replies aloud.'
                : `Missing — about ${size(s.voice.approx_bytes)} of ONNX weights. She works silently without them.`}
              {!s.voice.present && (
                <Action
                  label={`Download (${size(s.voice.approx_bytes)})`}
                  busy={setup.busy === 'voice'}
                  onClick={() => void setup.fetchVoice()}
                />
              )}
              {bar('voice')}
            </Step>

            <Step n={4} title="The microphone" done={setup.mic === 'granted'} optional>
              {setup.mic === 'granted'
                ? 'Granted. Windows shows its own recording indicator whenever she is listening.'
                : setup.mic === 'denied'
                  ? 'Denied. Hands-free needs it; typing does not. Change it in Windows privacy settings.'
                  : 'Hands-free listening needs it. Nothing is recorded until you ask for it, and nothing leaves this machine.'}
              {setup.mic !== 'granted' && (
                <Action label="Ask for access" onClick={() => void setup.askForMic()} />
              )}
            </Step>

            <Step n={5} title="The wake word" done={s.wake_word.present} optional>
              {s.wake_word.present
                ? 'Ready. Say “Aria” to start a turn — she answers to her name, not to the room.'
                : `Missing — about ${size(s.wake_word.approx_bytes)}. Phrase mode still works without it; this is for “hey jarvis” detection.`}
              {!s.wake_word.present && (
                <Action
                  label={`Download (${size(s.wake_word.approx_bytes)})`}
                  busy={setup.busy === 'wake_word'}
                  onClick={() => void setup.fetchWakeWord()}
                />
              )}
              {bar('wake_word')}
            </Step>

            {/* **Only when there is a model to threshold.** Phrase mode,
                which is the default, gates on the transcript and has no
                score — a slider there would be a control over nothing. */}
            {setup.wake?.available && (
              <Step n={6} title="Calibrate the wake word" done={false} optional>
                Say the wake phrase a few times and watch what it scores. Lower catches more and
                false-fires more; the mark to beat is 20 wakes with under 2 misses, and an hour
                idle with none.
                <div className="mt-2 flex items-center gap-2">
                  <input
                    type="range"
                    min={0.05}
                    max={1}
                    step={0.05}
                    value={setup.wake.threshold}
                    aria-label="Wake word threshold"
                    onChange={(event) => void setup.setWakeThreshold(Number(event.target.value))}
                    className="flex-1 accent-aria-accent"
                  />
                  <span className="w-8 shrink-0 text-right text-micro text-aria-dim">
                    {setup.wake.threshold.toFixed(2)}
                  </span>
                </div>
                <Action
                  label={setup.calibrating ? 'Listening — say it' : 'Test it'}
                  onClick={() =>
                    void (setup.calibrating ? setup.stopCalibration() : setup.startCalibration())
                  }
                />
                {setup.calibrating && (
                  <p className="mt-1 text-micro text-aria-faint">
                    {setup.wakePeak
                      ? `Best so far: ${setup.wakePeak.score.toFixed(2)} — ${
                          setup.wakePeak.fired ? 'that would wake her' : 'below the threshold'
                        }`
                      : 'Nothing scored yet. Hands-free has to be on for this to hear anything.'}
                  </p>
                )}
              </Step>
            )}

            <Step
              n={setup.wake?.available ? 7 : 6}
              title="Search everything on this disk"
              done={s.everything.present}
              optional
            >
              {s.everything.present
                ? 'Everything is installed — name search covers the whole disk.'
                : 'Not installed. She searches Documents, Desktop and Downloads instead, which is slower and narrower but works.'}
            </Step>

            <Step n={setup.wake?.available ? 8 : 7} title="A cloud key" done={anyKey} optional>
              {anyKey
                ? 'Stored. Smart mode can reach a cloud model when a question is worth it.'
                : 'Local only for now. Add an OpenAI, Gemini, OpenRouter or Bedrock key in Settings whenever you want one — keys go to Windows Credential Manager, never to a file.'}
            </Step>

            {setup.error && (
              <p className="rim rounded-lg bg-aria-bad/10 px-3 py-2 text-micro text-aria-bad">
                {setup.error}
              </p>
            )}
          </>
        )}

        <footer className="mt-2 flex items-center justify-between gap-3">
          <p className="text-micro text-aria-faint">
            You can come back to this from Settings at any time.
          </p>
          <button
            type="button"
            onClick={() => void setup.finish()}
            disabled={setup.busy !== null}
            className="interactive shrink-0 rounded-lg bg-aria-accent/90 px-3 py-1.5 text-tiny text-white disabled:opacity-40"
          >
            {/* Disabled only while something is downloading — closing the
                window mid-pull is how you get a half-written file. */}
            Start using ARIA
          </button>
        </footer>
      </div>
    </motion.div>
  )
}
