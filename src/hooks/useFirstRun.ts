/**
 * The first-run wizard's state — what is missing, and what is downloading.
 *
 * **Gated on a settings row, not `localStorage`** (rule 1). A wizard that
 * reappears because somebody cleared their storage is worse than no wizard,
 * and "have I set this machine up" is exactly the kind of thing the sidecar
 * is supposed to be the only owner of.
 *
 * The steps are a *report*, never a decision. Nothing here starts a download
 * on its own: a first launch that quietly pulls 4.7GB is the behaviour this
 * whole screen exists to replace.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

/** The default local model. Matches `catalog.PREFERRED_LOCAL` — named here
 *  because the wizard has to offer *something* concrete, and "pick a model"
 *  is not a question a first run should be asking. */
export const DEFAULT_MODEL = 'qwen2.5:7b'

export interface SetupState {
  ollama: { installed: boolean; running: boolean; models: string[] }
  everything: { present: boolean }
  voice: { present: boolean; missing: string[]; approx_bytes: number }
  wake_word: { present: boolean; missing: string[]; approx_bytes: number }
  keys: Array<{ key: string; present: boolean }>
  models_dir: string
}

/** Mirrors the `setup.progress` event. `percent` is null on the lines that
 *  carry no total — "pulling manifest", "verifying sha256 digest" — and a
 *  bar that read those as zero would jump back to the start each time. */
export interface SetupProgress {
  kind: 'model' | 'voice' | 'wake_word'
  what: string
  received: number | null
  total: number | null
  percent: number | null
  done: boolean
  note: string | null
}

export type MicState = 'unknown' | 'granted' | 'denied'

/** `voice.wake_threshold`. `available` is false in phrase mode, which is the
 *  default and has no model to threshold — a real state, not a failure, and
 *  one a single number could not express. */
export interface WakeState {
  available: boolean
  threshold: number
  default: number
  mode: string | null
}

/** The peak the wake model scored while calibration was armed.
 *  A threshold is unpickable without seeing what your own voice in your own
 *  room actually scores. */
export interface WakeScore {
  score: number
  threshold: number
  fired: boolean
}

/** How long a calibration arm lasts, in seconds. Self-expiring: it
 *  broadcasts on every frame, 12.5 a second, beside Whisper and a 7B. */
export const CALIBRATE_FOR_S = 30

export interface UseFirstRun {
  /** null until the sidecar has answered — the wizard must not flash. */
  needed: boolean | null
  state: SetupState | null
  progress: SetupProgress | null
  busy: null | 'model' | 'voice' | 'wake_word'
  error: string | null
  mic: MicState
  refresh: () => Promise<void>
  pullModel: (model: string) => Promise<void>
  fetchVoice: () => Promise<void>
  fetchWakeWord: () => Promise<void>
  askForMic: () => Promise<void>
  wake: WakeState | null
  /** The loudest frame since calibration was armed, or null. */
  wakePeak: WakeScore | null
  calibrating: boolean
  startCalibration: () => Promise<void>
  stopCalibration: () => Promise<void>
  setWakeThreshold: (value: number) => Promise<void>
  finish: () => Promise<void>
  /** Open it again from Settings, without clearing the row. */
  reopen: () => void
}

export function useFirstRun(connected: boolean): UseFirstRun {
  const [needed, setNeeded] = useState<boolean | null>(null)
  const [state, setState] = useState<SetupState | null>(null)
  const [progress, setProgress] = useState<SetupProgress | null>(null)
  const [busy, setBusy] = useState<null | 'model' | 'voice' | 'wake_word'>(null)
  const [error, setError] = useState<string | null>(null)
  const [mic, setMic] = useState<MicState>('unknown')
  const [wake, setWake] = useState<WakeState | null>(null)
  const [wakePeak, setWakePeak] = useState<WakeScore | null>(null)
  const [calibrating, setCalibrating] = useState(false)
  // A later answer must not be overwritten by an earlier one still in flight.
  // `MemoryPanel`'s ticket guard, which every panel here uses.
  const latest = useRef(0)

  const refresh = useCallback(async () => {
    if (!connected) return
    const ticket = ++latest.current
    try {
      const next = await window.aria.call<SetupState>('setup.state', {})
      if (ticket === latest.current) setState(next)
    } catch (cause) {
      if (ticket === latest.current) setError(cause instanceof Error ? cause.message : String(cause))
    }
  }, [connected])

  // Whether to show it at all. Separate from `refresh` because it decides
  // what is on screen, and re-reading it on every refresh would let a step
  // that marks itself done close the wizard out from under the user.
  useEffect(() => {
    if (!connected) return
    void (async () => {
      try {
        const result = await window.aria.call<{ done: boolean }>('setup.done', {})
        setNeeded(!result.done)
      } catch {
        // An unreachable brain is not a first run — the status line already
        // says the brain is down, and a setup wizard on top of that is a
        // second, less accurate explanation of the same thing. `try/catch`
        // rather than `.catch()`: a bridge that throws *synchronously* (a
        // stale preload, which this project has shipped before) would
        // otherwise take the whole effect down.
        setNeeded(false)
      }
    })()
  }, [connected])

  useEffect(() => {
    if (needed) void refresh()
  }, [needed, refresh])

  useEffect(
    () =>
      window.aria.onEvent((event) => {
        if (event.method === 'setup.progress') {
          setProgress(event.params as unknown as SetupProgress)
          return
        }
        if (event.method !== 'wake.score') return
        const next = event.params as unknown as WakeScore
        // **The peak, not the latest.** A phrase spans several frames and
        // most of them are the quiet either side of it; showing the last one
        // would report near-silence a moment after a perfect detection.
        setWakePeak((best) => (best && best.score > next.score && !next.fired ? best : next))
      }),
    [],
  )

  const run = useCallback(
    async (kind: 'model' | 'voice' | 'wake_word', method: string, params: Record<string, unknown> = {}) => {
      setBusy(kind)
      setError(null)
      setProgress(null)
      try {
        // The sidecar returns its failures rather than raising them: at this
        // point the user is looking at a step, and the error belongs under
        // that step rather than in a toast beside a spinner still turning.
        const result = await window.aria.call<{ ok: boolean; error?: string }>(method, params)
        if (!result.ok && result.error) setError(result.error)
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause))
      } finally {
        setBusy(null)
        setProgress(null)
        await refresh()
      }
    },
    [refresh],
  )

  const pullModel = useCallback(
    (model: string) => run('model', 'setup.pull_model', { model }),
    [run],
  )
  const fetchVoice = useCallback(() => run('voice', 'setup.fetch_voice'), [run])
  const fetchWakeWord = useCallback(() => run('wake_word', 'setup.fetch_wake_word'), [run])

  const askForMic = useCallback(async () => {
    // **The renderer owns the device, so the renderer has to be what asks.**
    // The sidecar can say hands-free is available and still never hear a
    // thing; only `getUserMedia` raises the Windows prompt.
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      // Released immediately: this step is consent, not a session. Holding it
      // open would light the recording indicator for the rest of the wizard.
      for (const track of stream.getTracks()) track.stop()
      setMic('granted')
    } catch {
      setMic('denied')
    }
  }, [])

  const readWake = useCallback(async () => {
    try {
      setWake(await window.aria.call<WakeState>('voice.wake_threshold', {}))
    } catch {
      /* phrase mode, or no listener; the step says so from `available` */
    }
  }, [])

  useEffect(() => {
    if (needed) void readWake()
  }, [needed, readWake])

  const startCalibration = useCallback(async () => {
    setWakePeak(null)
    setCalibrating(true)
    await window.aria.call('voice.wake_threshold', { calibrate_for: CALIBRATE_FOR_S })
    // The sidecar disarms itself; this only stops the UI claiming to listen
    // for longer than it is. Two clocks, and the sidecar's is the real one.
    window.setTimeout(() => setCalibrating(false), CALIBRATE_FOR_S * 1000)
  }, [])

  const stopCalibration = useCallback(async () => {
    setCalibrating(false)
    try {
      await window.aria.call('voice.wake_threshold', { calibrate_for: 0 })
    } catch {
      /* it expires on its own regardless */
    }
  }, [])

  const setWakeThreshold = useCallback(
    async (value: number) => {
      setError(null)
      try {
        setWake(await window.aria.call<WakeState>('voice.wake_threshold', { threshold: value }))
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause))
        await readWake() // never leave a slider showing a value that was refused
      }
    },
    [readWake],
  )

  const finish = useCallback(async () => {
    try {
      await window.aria.call('setup.done', { done: true })
    } catch {
      /* closing the wizard must not be the thing that fails */
    }
    setNeeded(false)
  }, [])

  const reopen = useCallback(() => setNeeded(true), [])

  return {
    needed,
    state,
    progress,
    busy,
    error,
    mic,
    refresh,
    pullModel,
    fetchVoice,
    fetchWakeWord,
    askForMic,
    wake,
    wakePeak,
    calibrating,
    startCalibration,
    stopCalibration,
    setWakeThreshold,
    finish,
    reopen,
  }
}
