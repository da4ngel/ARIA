/**
 * Hold to talk: capture, transcribe, send.
 *
 * **Not the spacebar.** The plan said hold Space, which is wrong here — the
 * composer is focused by default and Space is a character you type. The hold
 * key is `Ctrl+Shift+Space`, and the microphone button in the composer does the
 * same thing with the mouse.
 *
 * A held key repeats while it is down, so `start` has to be idempotent; `useMic`
 * returns early when a stream is already open.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import { useMic } from '@/hooks/useMic'

/** Shorter than this is a mis-hit, not an utterance. */
const MIN_HOLD_MS = 250

export interface UsePushToTalk {
  listening: boolean
  /** True between release and the transcript coming back. */
  transcribing: boolean
  error: string | null
  start: () => void
  stop: () => void
}

export function usePushToTalk(
  onTranscript: (text: string) => void,
  enabled: boolean,
): UsePushToTalk {
  const mic = useMic()
  const [transcribing, setTranscribing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const startedAt = useRef(0)

  const start = useCallback(() => {
    if (!enabled || mic.listening) return
    startedAt.current = Date.now()
    setError(null)
    void mic.start()
  }, [enabled, mic])

  const stop = useCallback(() => {
    if (!mic.listening) return
    const held = Date.now() - startedAt.current

    void mic.stop().then(async (recording) => {
      if (!recording || held < MIN_HOLD_MS) return

      setTranscribing(true)
      try {
        const result = await window.aria.call<{ text: string; took_ms: number }>(
          'voice.transcribe',
          { pcm: recording.pcm, sample_rate: recording.sampleRate },
        )
        const text = result.text.trim()
        // Whisper returns nothing for silence, and sending an empty turn would
        // be worse than saying nothing happened.
        if (text) onTranscript(text)
        else setError('Nothing was heard.')
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause))
      } finally {
        setTranscribing(false)
      }
    })
  }, [mic, onTranscript])

  // Ctrl+Shift+Space, held. `repeat` is ignored so the auto-repeat of a held
  // key does not restart the capture on every tick.
  useEffect(() => {
    if (!enabled) return

    const down = (event: KeyboardEvent): void => {
      if (event.code !== 'Space' || !event.ctrlKey || !event.shiftKey) return
      if (event.repeat) return
      event.preventDefault()
      start()
    }
    const up = (event: KeyboardEvent): void => {
      // Releasing Ctrl or Shift first also ends the hold, which is what
      // actually happens when a hand comes off three keys at once.
      if (event.code === 'Space' || event.key === 'Control' || event.key === 'Shift') {
        stop()
      }
    }
    // A lost window while holding must not leave the microphone open.
    const blur = (): void => stop()

    document.addEventListener('keydown', down)
    document.addEventListener('keyup', up)
    window.addEventListener('blur', blur)
    return () => {
      document.removeEventListener('keydown', down)
      document.removeEventListener('keyup', up)
      window.removeEventListener('blur', blur)
    }
  }, [enabled, start, stop])

  return {
    listening: mic.listening,
    transcribing,
    error: error ?? mic.error,
    start,
    stop,
  }
}
