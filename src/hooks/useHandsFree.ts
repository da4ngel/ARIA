/**
 * Always-on listening (BUILD_SPEC §9 Phase 2 stage 3).
 *
 * The microphone stays open and every 80ms frame is forwarded to the sidecar,
 * which owns the wake word, the endpointing and the state machine (CLAUDE.md
 * rule 1). Nothing here decides that "hey jarvis" was said — this hook moves
 * audio and renders what it is told.
 *
 * **Frames go out as notifications, not calls.** Twelve requests a second each
 * awaiting a reply would be twelve round-trips a second to hear "received".
 *
 * The stream is a deliberate, visible thing: Windows shows a microphone
 * indicator for as long as it is open, and this hook is off until switched on.
 * `useMic` remains the push-to-talk path and is untouched.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

const SAMPLE_RATE = 16_000
/** openWakeWord's frame. The sidecar re-chunks to 512 for the VAD. */
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
  /** The sidecar has the wake word loaded. False means the weights are absent. */
  available: boolean
  /** The microphone is open and frames are going out. */
  active: boolean
  /** Loudest recent sample, 0..1 — drives the orb, never a decision. */
  level: number
  error: string | null
  toggle: () => void
}

export function useHandsFree(connected: boolean): UseHandsFree {
  const [available, setAvailable] = useState(false)
  const [active, setActive] = useState(false)
  const [level, setLevel] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const stream = useRef<MediaStream | null>(null)
  const context = useRef<AudioContext | null>(null)
  const processor = useRef<ScriptProcessorNode | null>(null)
  const carry = useRef<Float32Array>(new Float32Array(0))

  const teardown = useCallback(() => {
    processor.current?.disconnect()
    processor.current = null
    stream.current?.getTracks().forEach((track) => track.stop())
    stream.current = null
    void context.current?.close()
    context.current = null
    carry.current = new Float32Array(0)
    setLevel(0)
  }, [])

  // Ask the sidecar what it can do, and whether it was left on last time.
  useEffect(() => {
    if (!connected) {
      setAvailable(false)
      return
    }
    void window.aria
      .call<{ available: boolean; enabled: boolean }>('voice.listen', {})
      .then((state) => setAvailable(state.available))
      .catch(() => setAvailable(false))
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

  return { available, active, level, error, toggle }
}
