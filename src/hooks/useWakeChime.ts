/**
 * The blip that says she is listening.
 *
 * Synthesised rather than played from a file: two short sine tones cost a few
 * lines of WebAudio, and an asset would need bundling, a path that survives
 * packaging, and a decode on first use.
 *
 * It exists because the glow alone is not feedback. You say her name while
 * looking at whatever you were already doing, and a light at the edge of the
 * screen you are not watching is the same as nothing. Sixty-four utterances
 * were dropped in one measured session with no sign at all that she had heard
 * anything — that silence is the bug this closes.
 */

import { useEffect, useRef } from 'react'

/** Two notes, rising — the shape of a question rather than an alert. */
const NOTES: ReadonlyArray<{ hz: number; at: number; for: number }> = [
  { hz: 784, at: 0, for: 0.07 }, // G5
  { hz: 1047, at: 0.075, for: 0.09 }, // C6
]
/** Quiet on purpose. This plays over whatever you are listening to. */
const GAIN = 0.055

export function useWakeChime(enabled = true): void {
  // One context for the life of the window; creating one per chime leaks
  // hardware handles and costs a few ms of setup each time.
  const context = useRef<AudioContext | null>(null)

  useEffect(() => {
    if (!enabled) return

    return window.aria.onEvent((event) => {
      if (event.method !== 'wake') return

      context.current ??= new AudioContext()
      const ctx = context.current
      void ctx.resume()

      const start = ctx.currentTime + 0.01
      for (const note of NOTES) {
        const osc = ctx.createOscillator()
        const gain = ctx.createGain()
        osc.type = 'sine'
        osc.frequency.value = note.hz

        // Ramped, never switched: a square-edged gain change is an audible
        // click, and a click is what a cheap notification sounds like.
        const from = start + note.at
        const to = from + note.for
        gain.gain.setValueAtTime(0, from)
        gain.gain.linearRampToValueAtTime(GAIN, from + 0.012)
        gain.gain.exponentialRampToValueAtTime(0.0001, to)

        osc.connect(gain)
        gain.connect(ctx.destination)
        osc.start(from)
        osc.stop(to + 0.02)
      }
    })
  }, [enabled])

  useEffect(() => {
    return () => {
      void context.current?.close()
      context.current = null
    }
  }, [])
}
