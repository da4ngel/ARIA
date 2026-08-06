/**
 * Always-on listening (BUILD_SPEC §9 Phase 2 stage 3).
 *
 * The microphone stays open and every 80ms frame is forwarded to the sidecar,
 * which owns the wake phrase, the endpointing and the state machine (CLAUDE.md
 * rule 1). Nothing here decides that her name was said, or even knows what the
 * name is — `phrase` comes back from `voice.listen`, so the label can never
 * name something the sidecar is not listening for.
 *
 * **Frames go out as notifications, not calls.** Twelve requests a second each
 * awaiting a reply would be twelve round-trips a second to hear "received".
 *
 * **It opens on launch**, so talking to her needs no keypress and no click —
 * that is the whole point of hands-free. The stream is still a visible thing
 * rather than a hidden one: Windows shows a microphone indicator for as long
 * as it is open, the header switch says "Listening" in words, and switching
 * it off persists so the answer is not re-asked every launch.
 *
 * `useMic` remains the push-to-talk path and is untouched — holding
 * Ctrl+Shift+Space still works, and is the way to talk with this off.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

const SAMPLE_RATE = 16_000
/** openWakeWord's frame size, kept in both modes. The sidecar re-chunks to
 *  the 512 samples Silero wants. */
const FRAME_SAMPLES = 1280
/** ScriptProcessor's quantum; frames are cut out of it. */
const BUFFER_SIZE = 4096

function encodeFrame(frame: Float32Array): string {
  const view = new DataView(new ArrayBuffer(frame.length * 2))
  for (let i = 0; i < frame.length; i += 1) {
    view.setInt16(i * 2, Math.max(-1, Math.min(1, frame[i])) * 32767, true)
  }
  const bytes = new Uint8Array(view.buffer)
  let binary = ''
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000))
  }
  return btoa(binary)
}

export interface UseHandsFree {
  /** The sidecar can listen. False means voice is off or speech failed to load. */
  available: boolean
  /** What to actually say, from the sidecar — never guessed here, or the UI
   *  could print a phrase it is not listening for. */
  phrase: string
  /** The microphone is open and frames are going out. */
  active: boolean
  /** Loudest recent sample, 0..1 — drives the orb, never a decision. */
  level: number
  /** The same figure, without a render behind it. See `useAudio.getLevel`. */
  getLevel: () => number
  error: string | null
  toggle: () => void
}

export function useHandsFree(connected: boolean): UseHandsFree {
  const [available, setAvailable] = useState(false)
  const [phrase, setPhrase] = useState('aria')
  const [active, setActive] = useState(false)
  const [level, setLevel] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const stream = useRef<MediaStream | null>(null)
  const context = useRef<AudioContext | null>(null)
  const processor = useRef<ScriptProcessorNode | null>(null)
  const carry = useRef<Float32Array>(new Float32Array(0))
  // Set once the persisted setting has been honoured, so a reconnect does
  // not re-open a microphone the user switched off in the meantime.
  const autoStarted = useRef(false)
  const levelRef = useRef(0)

  const teardown = useCallback(() => {
    processor.current?.disconnect()
    processor.current = null
    stream.current?.getTracks().forEach((track) => track.stop())
    stream.current = null
    void context.current?.close()
    context.current = null
    carry.current = new Float32Array(0)
    levelRef.current = 0
    setLevel(0)
  }, [])

  // Ask the sidecar what it can do, and whether it should already be on —
  // then actually open the device if so. The sidecar persists the answer but
  // owns no microphone, so without this the setting was remembered and then
  // quietly ignored, and hands-free needed a click on every launch.
  useEffect(() => {
    if (!connected) {
      setAvailable(false)
      return
    }
    let cancelled = false

    void window.aria
      .call<{ available: boolean; enabled: boolean; phrase: string | null }>('voice.listen', {})
      .then((state) => {
        if (cancelled) return
        setAvailable(state.available)
        if (state.phrase) setPhrase(state.phrase)
        // `autoStarted` guards a reconnect: dropping and re-attaching the
        // socket must not re-open a device the user has since switched off.
        if (state.available && state.enabled && !autoStarted.current) {
          autoStarted.current = true
          void start()
        }
      })
      .catch(() => setAvailable(false))

    return () => {
      cancelled = true
    }
    // `start` is stable; listing it would re-run this on every render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connected])

  // Close the device if the brain goes away — frames would go nowhere, and a
  // microphone open for no listener is exactly what must not happen.
  useEffect(() => {
    if (!connected && active) {
      teardown()
      setActive(false)
    }
  }, [connected, active, teardown])

  useEffect(() => teardown, [teardown])

  const start = useCallback(async () => {
    if (stream.current) return
    setError(null)

    try {
      await window.aria.call('voice.listen', { enabled: true })
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
      return
    }

    try {
      const media = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: SAMPLE_RATE,
          // Barge-in depends on this: without it the microphone hears her own
          // voice out of the speakers and interrupts her mid-sentence.
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })
      stream.current = media

      const ctx = new AudioContext({ sampleRate: SAMPLE_RATE })
      context.current = ctx
      const source = ctx.createMediaStreamSource(media)
      const node = ctx.createScriptProcessor(BUFFER_SIZE, 1, 1)

      node.onaudioprocess = (event) => {
        const input = event.inputBuffer.getChannelData(0)

        let peak = 0
        for (let i = 0; i < input.length; i += 1) {
          const magnitude = Math.abs(input[i])
          if (magnitude > peak) peak = magnitude
        }
        levelRef.current = peak
        setLevel(peak)

        // Cut exact 80ms frames, carrying the remainder: the sidecar's models
        // are stateful and a ragged frame would shift their whole history.
        const buffer = new Float32Array(carry.current.length + input.length)
        buffer.set(carry.current)
        buffer.set(input, carry.current.length)

        let offset = 0
        while (offset + FRAME_SAMPLES <= buffer.length) {
          window.aria.notify('voice.frame', {
            pcm: encodeFrame(buffer.subarray(offset, offset + FRAME_SAMPLES)),
            sample_rate: ctx.sampleRate,
          })
          offset += FRAME_SAMPLES
        }
        carry.current = buffer.slice(offset)
      }

      source.connect(node)
      node.connect(ctx.destination)
      processor.current = node
      setActive(true)
    } catch (cause) {
      teardown()
      void window.aria.call('voice.listen', { enabled: false }).catch(() => {})
      const name = cause instanceof Error ? cause.name : ''
      setError(
        name === 'NotAllowedError'
          ? 'Microphone access was refused. Allow it in Windows privacy settings, then try again.'
          : name === 'NotFoundError'
            ? 'No microphone was found.'
            : `Could not open the microphone: ${cause instanceof Error ? cause.message : cause}`,
      )
    }
  }, [teardown])

  const stop = useCallback(() => {
    teardown()
    setActive(false)
    void window.aria.call('voice.listen', { enabled: false }).catch(() => {})
  }, [teardown])

  const toggle = useCallback(() => {
    if (active) stop()
    else void start()
  }, [active, start, stop])

  const getLevel = useCallback(() => levelRef.current, [])

  return { available, phrase, active, level, getLevel, error, toggle }
}
