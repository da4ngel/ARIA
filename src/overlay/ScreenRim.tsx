/**
 * The glow around the edge of the screen.
 *
 * Same idea as `VoiceAura` and deliberately the same envelope constants, so
 * she moves at one speed whether you are looking at the window or at the
 * desktop. What differs is the canvas: this one is the whole display, so it
 * costs more per frame and earns it back by drawing almost nothing — a single
 * rounded rectangle at the edge, and a blur.
 *
 * **Device pixel ratio is pinned to 1 here.** A 2560-wide canvas at ratio 2 is
 * four times the fill for a band of soft light nobody will inspect, on a
 * machine already running Whisper, Kokoro and a 7B model.
 */

import { useEffect, useRef } from 'react'

export type RimMode = 'listening' | 'speaking' | null

interface Props {
  mode: RimMode
  /** Live amplitude, 0..1, sampled once a frame. */
  getLevel: () => number
}

/** The orb's hues, so every surface agrees about what state she is in. */
const HUE: Record<'listening' | 'speaking', [number, number, number]> = {
  listening: [94, 200, 232],
  speaking: [74, 222, 128],
}

const ATTACK = 0.28
const RELEASE = 0.08
/** Corner radius of the traced rectangle — near Windows 11's own. */
const RADIUS = 12
/** Band thickness at silence and at full voice. */
const THICKNESS_MIN = 5
const THICKNESS_MAX = 26

export function ScreenRim({ mode, getLevel }: Props): JSX.Element {
  const canvas = useRef<HTMLCanvasElement>(null)
  const running = useRef(0)
  const tick = useRef<(() => void) | null>(null)
  const modeRef = useRef<RimMode>(mode)
  const levelRef = useRef(getLevel)
  modeRef.current = mode
  levelRef.current = getLevel

  useEffect(() => {
    const element = canvas.current
    if (!element) return
    const ctx = element.getContext('2d')
    if (!ctx) return

    const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    let width = 0
    let height = 0
    const resize = (): void => {
      width = window.innerWidth
      height = window.innerHeight
      element.width = width
      element.height = height
    }
    resize()
    window.addEventListener('resize', resize)

    let envelope = 0
    let fade = 0
    let pulse = 0

    const draw = (): void => {
      const active = modeRef.current
      const target = active ? 1 : 0
      fade += (target - fade) * (target > fade ? 0.14 : 0.07)

      if (!active && fade < 0.004) {
        ctx.clearRect(0, 0, width, height)
        running.current = 0
        return
      }
      running.current = requestAnimationFrame(draw)

      const raw = active ? Math.min(1, levelRef.current()) : 0
      envelope += (raw - envelope) * (raw > envelope ? ATTACK : RELEASE)
      if (!still) pulse += 0.02

      const [r, g, b] = HUE[active ?? 'listening']
      ctx.clearRect(0, 0, width, height)

      // A slow breath under the voice, so a silent moment still looks alive
      // rather than switched off mid-conversation.
      const breath = still ? 0 : (Math.sin(pulse) + 1) * 0.5 * 0.12
      const strength = Math.min(1, envelope + breath)
      const thickness = THICKNESS_MIN + strength * (THICKNESS_MAX - THICKNESS_MIN)

      // Inset by half the line width so the stroke sits fully on screen; half
      // of it would otherwise be clipped by the edge and the glow would look
      // thinner at the corners than along the sides.
      const inset = thickness / 2
      ctx.save()
      ctx.beginPath()
      ctx.roundRect(inset, inset, width - thickness, height - thickness, RADIUS)
      ctx.strokeStyle = `rgba(${r},${g},${b},${(0.34 + strength * 0.5) * fade})`
      ctx.lineWidth = thickness
      // The blur is what makes it read as light bleeding in from off-screen
      // rather than a coloured border drawn around the desktop.
      ctx.shadowColor = `rgba(${r},${g},${b},${(0.8 + strength * 0.2) * fade})`
      ctx.shadowBlur = 26 + strength * 54
      ctx.stroke()
      // Stroked twice: one pass cannot be both a tight bright edge and a wide
      // soft halo, and layering them is cheaper than a gradient per frame.
      ctx.shadowBlur = 10 + strength * 20
      ctx.strokeStyle = `rgba(${r},${g},${b},${(0.18 + strength * 0.34) * fade})`
      ctx.lineWidth = thickness * 0.45
      ctx.stroke()
      ctx.restore()
    }

    tick.current = draw
    if (modeRef.current) running.current = requestAnimationFrame(draw)

    return () => {
      cancelAnimationFrame(running.current)
      running.current = 0
      tick.current = null
      window.removeEventListener('resize', resize)
    }
  }, [])

  useEffect(() => {
    if (mode && running.current === 0 && tick.current) {
      running.current = requestAnimationFrame(tick.current)
    }
  }, [mode])

  return <canvas ref={canvas} aria-hidden className="pointer-events-none fixed inset-0" />
}
