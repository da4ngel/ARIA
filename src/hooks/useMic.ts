/**
 * Microphone capture for push-to-talk (BUILD_SPEC §9 Phase 2).
 *
 * The stream is opened when you start talking and **closed when you stop** —
 * not opened once and left running. On Windows that difference is visible: the
 * OS shows a microphone indicator while a stream is live, and an assistant that
 * keeps one open when it is not listening looks like it is always listening.
 * Stage 3's wake word will hold a stream open, and it will say so.
 *
 * Capture is 16kHz mono because that is what Whisper wants. Chromium usually
 * honours the requested `sampleRate`; when it does not, the sidecar resamples,
 * which is why the real rate is sent alongside the audio.
 */

import { useCallback, useRef, useState } from 'react'

const TARGET_SAMPLE_RATE = 16_000
/** Small enough to keep memory flat on a long hold, large enough not to thrash. */
const BUFFER_SIZE = 4096

function encodePcm16(chunks: Float32Array[], total: number): string {
  const view = new DataView(new ArrayBuffer(total * 2))
  let offset = 0
  for (const chunk of chunks) {
    for (let i = 0; i < chunk.length; i += 1) {
      const clamped = Math.max(-1, Math.min(1, chunk[i]))
      view.setInt16(offset, clamped * 32767, true)
      offset += 2
    }
  }

  // Chunked so a long recording cannot blow the argument limit of
  // String.fromCharCode, which a single spread over ~500k samples would.
  const bytes = new Uint8Array(view.buffer)
  let binary = ''
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000))
  }
  return btoa(binary)
}

export interface Recording {
  pcm: string
  sampleRate: number
  durationMs: number
}

export interface UseMic {
  listening: boolean
  /** Non-null when the microphone could not be opened, in words worth showing. */
  error: string | null
  start: () => Promise<void>
  /** Stops, releases the device, and returns what was captured. */
  stop: () => Promise<Recording | null>
}

export function useMic(): UseMic {
  const [listening, setListening] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const stream = useRef<MediaStream | null>(null)
  const context = useRef<AudioContext | null>(null)
  const processor = useRef<ScriptProcessorNode | null>(null)
  const chunks = useRef<Float32Array[]>([])
  const total = useRef(0)

  const teardown = useCallback(() => {
    processor.current?.disconnect()
    processor.current = null
    // Stopping every track is what actually turns the indicator off.
    stream.current?.getTracks().forEach((track) => track.stop())
    stream.current = null
    void context.current?.close()
    context.current = null
  }, [])

  const start = useCallback(async () => {
    if (stream.current) return
    setError(null)
    chunks.current = []
    total.current = 0

    try {
      const media = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: TARGET_SAMPLE_RATE,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })
      stream.current = media

      const ctx = new AudioContext({ sampleRate: TARGET_SAMPLE_RATE })
      context.current = ctx
      const source = ctx.createMediaStreamSource(media)

      // ScriptProcessor is deprecated in favour of AudioWorklet, which needs a
      // separate module file loaded over a URL — awkward under a strict CSP,
      // and this runs for a few seconds at a time on one channel.
      const node = ctx.createScriptProcessor(BUFFER_SIZE, 1, 1)
      node.onaudioprocess = (event) => {
        const input = event.inputBuffer.getChannelData(0)
        chunks.current.push(new Float32Array(input))
        total.current += input.length
      }
      source.connect(node)
      node.connect(ctx.destination)
      processor.current = node

      setListening(true)
    } catch (cause) {
      teardown()
      setListening(false)
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

  const stop = useCallback(async (): Promise<Recording | null> => {
    if (!stream.current) return null
    const sampleRate = context.current?.sampleRate ?? TARGET_SAMPLE_RATE
    const captured = chunks.current
    const length = total.current

    teardown()
    setListening(false)
    chunks.current = []
    total.current = 0

    if (length === 0) return null
    return {
      pcm: encodePcm16(captured, length),
      sampleRate,
      durationMs: (length / sampleRate) * 1000,
    }
  }, [teardown])

  return { listening, error, start, stop }
}
