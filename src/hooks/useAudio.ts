/**
 * Plays the speech the sidecar streams back (BUILD_SPEC §9 Phase 2).
 *
 * Chunks arrive as base64 int16 PCM, one per spoken fragment, and they arrive
 * *out of order* — synthesis is dispatched per fragment and a short one can
 * finish before a long one sent earlier. Each carries an index, and playback
 * follows the index rather than arrival.
 *
 * Scheduling is absolute, not "play when the last one ends": WebAudio's clock
 * is sample-accurate, so queueing each buffer at the previous one's end time
 * gives gapless speech. Waiting for an `onended` callback leaves an audible
 * seam between every sentence.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import type { SidecarEvent } from '@/types/bridge'

interface AudioChunk {
  turn_id: string
  index: number
  sample_rate: number
  pcm: string
}

/** Small lead-in so the first buffer is scheduled slightly ahead of `currentTime`
 *  rather than racing it, which would clip the first few milliseconds. */
const SCHEDULE_LEAD_S = 0.02

/** How far playback drops while the sidecar works out whether the speech over
 *  her was an interruption. Quiet enough to talk across, loud enough that a
 *  false alarm reads as a dip rather than a dropout. */
const DUCKED_GAIN = 0.2

function decodePcm16(base64: string): Float32Array<ArrayBuffer> {
  const binary = atob(base64)
  const view = new DataView(new ArrayBuffer(binary.length))
  for (let i = 0; i < binary.length; i += 1) view.setUint8(i, binary.charCodeAt(i))

  const count = binary.length / 2
  // Backed by an explicit ArrayBuffer: `copyToChannel` will not accept a
  // Float32Array over ArrayBufferLike, which is what the bare constructor
  // infers under the current lib types.
  const samples = new Float32Array(new ArrayBuffer(count * 4))
  for (let i = 0; i < count; i += 1) {
    samples[i] = view.getInt16(i * 2, true) / 32768
  }
  return samples
}

export interface UseAudio {
  /** True while something is actually coming out of the speakers. */
  speaking: boolean
  /** Her live output amplitude, 0..1, read straight from the graph.
   *
   *  A getter rather than state on purpose: the visualiser wants this sixty
   *  times a second, and sixty React renders a second to move a waveform would
   *  cost more than the waveform. */
  getLevel: () => number
  /** Stop now and drop anything queued. */
  stop: () => void
}

export function useAudio(): UseAudio {
  const [speaking, setSpeaking] = useState(false)
  const context = useRef<AudioContext | null>(null)
  const analyser = useRef<AnalyserNode | null>(null)
  // Everything plays through this, so ducking is one ramp rather than a walk
  // over live source nodes.
  const volume = useRef<GainNode | null>(null)
  const scratch = useRef<Uint8Array<ArrayBuffer> | null>(null)
  const sources = useRef<AudioBufferSourceNode[]>([])
  const playHead = useRef(0)
  const announced = useRef(false)
  const nextIndex = useRef(0)
  const pending = useRef<Map<number, AudioChunk>>(new Map())
  const activeTurn = useRef<string | null>(null)

  /** Tell the sidecar whether sound is coming out. It has no other way to
   *  know: generation finishing is not playback finishing, and the gap between
   *  them is exactly when someone interrupts. */
  const announce = useCallback((playing: boolean) => {
    if (playing === announced.current) return
    announced.current = playing
    window.aria.notify('voice.playing', { playing })
  }, [])

  const setGain = useCallback((value: number, seconds = 0.08) => {
    const ctx = context.current
    const gain = volume.current
    if (!ctx || !gain) return
    gain.gain.cancelScheduledValues(ctx.currentTime)
    gain.gain.setValueAtTime(gain.gain.value, ctx.currentTime)
    // Ramped, not switched: an instant gain change is an audible click.
    gain.gain.linearRampToValueAtTime(value, ctx.currentTime + seconds)
  }, [])

  const stop = useCallback(() => {
    for (const source of sources.current) {
      try {
        source.stop()
      } catch {
        // Already finished; stopping twice is not an error worth surfacing.
      }
    }
    sources.current = []
    pending.current.clear()
    nextIndex.current = 0
    playHead.current = 0
    activeTurn.current = null
    setGain(1, 0.01)
    announce(false)
    setSpeaking(false)
  }, [announce, setGain])

  const play = useCallback((chunk: AudioChunk) => {
    context.current ??= new AudioContext()
    const ctx = context.current
    void ctx.resume()

    // One analyser for the whole graph, between every source and the speakers.
    // 512 bins is plenty for an envelope — this is not a spectrum display.
    if (!analyser.current) {
      const gain = ctx.createGain()
      gain.connect(ctx.destination)
      volume.current = gain

      const node = ctx.createAnalyser()
      node.fftSize = 512
      node.smoothingTimeConstant = 0.7
      node.connect(gain)
      analyser.current = node
      scratch.current = new Uint8Array(new ArrayBuffer(node.frequencyBinCount))
    }

    const samples = decodePcm16(chunk.pcm)
    const buffer = ctx.createBuffer(1, samples.length, chunk.sample_rate)
    buffer.copyToChannel(samples, 0)

    const source = ctx.createBufferSource()
    source.buffer = buffer
    source.connect(analyser.current)

    const startAt = Math.max(ctx.currentTime + SCHEDULE_LEAD_S, playHead.current)
    source.start(startAt)
    playHead.current = startAt + buffer.duration

    sources.current.push(source)
    announce(true)
    setSpeaking(true)
    source.onended = () => {
      sources.current = sources.current.filter((s) => s !== source)
      if (sources.current.length === 0) {
        announce(false)
        setSpeaking(false)
      }
    }
  }, [announce])

  useEffect(() => {
    return window.aria.onEvent((event: SidecarEvent) => {
      if (event.method === 'audio.stop') {
        stop()
        return
      }

      // Someone started talking over her. Drop the volume now; whether it was
      // really an interruption is not known until the sidecar has transcribed
      // what they said, which is over a second away.
      if (event.method === 'audio.duck') {
        setGain(DUCKED_GAIN)
        return
      }
      if (event.method === 'audio.resume') {
        setGain(1)
        return
      }
      if (event.method !== 'audio.out') return

      const chunk = event.params as unknown as AudioChunk

      // A new turn resets the ordering; the previous one's audio is stale.
      if (activeTurn.current !== chunk.turn_id) {
        stop()
        activeTurn.current = chunk.turn_id
      }

      pending.current.set(chunk.index, chunk)
      // Drain in index order, so an early-finishing short sentence waits for
      // the long one that was sent before it.
      while (pending.current.has(nextIndex.current)) {
        const next = pending.current.get(nextIndex.current)
        pending.current.delete(nextIndex.current)
        nextIndex.current += 1
        if (next) play(next)
      }
    })
  }, [play, stop, setGain])

  useEffect(() => {
    return () => {
      stop()
      void context.current?.close()
    }
  }, [stop])

  const getLevel = useCallback((): number => {
    const node = analyser.current
    const bins = scratch.current
    if (!node || !bins || sources.current.length === 0) return 0

    node.getByteTimeDomainData(bins)
    // Peak deviation from the 128 midpoint, which is silence in this encoding.
    let peak = 0
    for (let i = 0; i < bins.length; i += 1) {
      const magnitude = Math.abs(bins[i] - 128)
      if (magnitude > peak) peak = magnitude
    }
    return Math.min(1, peak / 128)
  }, [])

  return { speaking, getLevel, stop }
}
