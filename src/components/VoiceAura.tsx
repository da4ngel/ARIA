/**
 * The room reacting while she listens or speaks (BUILD_SPEC §5, §9 Phase 2).
 *
 * A full-bleed canvas behind everything, drawn only while there is a voice in
 * the room. Two states, and **the direction of travel is what tells them
 * apart**: listening draws inward from the edges, speaking radiates outward
 * from her. Colour alone would not survive a glance, and it is the same
 * information the orb is already carrying in hue.
 *
 * Real amplitude, not a timer. Both hooks hand over a `getLevel()` read at
 * frame rate rather than React state — sixty renders a second to move a
 * waveform costs more than the waveform.
 *
 * Cheap on purpose: this runs alongside Whisper, Kokoro and a 7B model. One
 * canvas, no per-frame allocation, and the loop is not merely hidden when
 * nothing is happening — it is cancelled.
 */

import { useEffect, useRef } from 'react'

import { RGB } from '@/styles/tokens'

export type AuraMode = 'listening' | 'speaking' | null

interface Props {
  mode: AuraMode
  /** Live amplitude, 0..1, sampled per frame. */
  getLevel: () => number
}

/** The orb's own hues as triples, **derived rather than typed**.
 *
 *  Hand-converting the hex is exactly how this drifted from the config: a
 *  recolour changed the palette and left the aura painting the old one, in a
 *  frame loop where only sampling pixels would have shown it. */
const HUE = RGB as Record<'listening' | 'speaking', [number, number, number]>

const WAVES = 3
/** Clear of the composer, which is ~56px of input plus its margin. Drawn any
 *  lower and the whole ribbon hides behind the text field. */
const RIBBON_BOTTOM = 78
/** Horizontal sample spacing. 3px is smooth at this width and a third of the
 *  points of a per-pixel curve. */
const STEP = 3
/** How fast the envelope chases the signal. Low enough to smooth a plosive,
 *  high enough that a syllable still reads as a syllable. */
const ATTACK = 0.28
const RELEASE = 0.08

export function VoiceAura({ mode, getLevel }: Props): JSX.Element {
  const canvas = useRef<HTMLCanvasElement>(null)
  const running = useRef(0)
  const tick = useRef<(() => void) | null>(null)
  // Read inside the loop rather than captured, so changing mode does not
  // restart the animation and lose the envelope mid-word.
  const modeRef = useRef<AuraMode>(mode)
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
      const ratio = Math.min(window.devicePixelRatio || 1, 2)
      const box = element.getBoundingClientRect()
      width = box.width
      height = box.height
      element.width = Math.round(width * ratio)
      element.height = Math.round(height * ratio)
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0)
    }
    resize()
    const observer = new ResizeObserver(resize)
    observer.observe(element)

    let phase = 0
    let envelope = 0
    let fade = 0

    const draw = (): void => {
      const active = modeRef.current

      // Fade covers the gap between states, so listening handing over to
      // speaking is a crossfade rather than a blink.
      const target = active ? 1 : 0
      fade += (target - fade) * (target > fade ? 0.12 : 0.06)

      // Idle and faded out: stop scheduling entirely rather than burning a
      // frame every 16ms drawing nothing. The effect below restarts it.
      if (!active && fade < 0.004) {
        ctx.clearRect(0, 0, width, height)
        running.current = 0
        return
      }
      running.current = requestAnimationFrame(draw)

      const raw = active ? Math.min(1, levelRef.current()) : 0
      envelope += (raw - envelope) * (raw > envelope ? ATTACK : RELEASE)
      if (!still) phase += 0.016 + envelope * 0.03

      const [r, g, b] = HUE[active ?? 'listening']
      ctx.clearRect(0, 0, width, height)

      // ── the wash ──────────────────────────────────────────────────
      // A glow rising from below the bottom edge, where the composer is and
      // where the conversation is happening. Grows with the voice.
      const reach = height * (0.42 + envelope * 0.26)
      const originY = height + reach * 0.25
      const wash = ctx.createRadialGradient(width / 2, originY, 0, width / 2, originY, reach * 1.25)
      wash.addColorStop(0, `rgba(${r},${g},${b},${(0.2 + envelope * 0.26) * fade})`)
      wash.addColorStop(0.55, `rgba(${r},${g},${b},${(0.07 + envelope * 0.1) * fade})`)
      wash.addColorStop(1, `rgba(${r},${g},${b},0)`)
      ctx.fillStyle = wash
      ctx.fillRect(0, height - reach * 1.4, width, reach * 1.4)

      if (still) return

      // ── the ribbon ────────────────────────────────────────────────
      // Sits clear above the composer rather than behind it: drawn at the very
      // bottom the whole thing hides under the input and reads as a tint.
      //
      // Three sines at different rates, so the crests drift apart instead of
      // marching in lockstep — that is the difference between a voice and a
      // graphic of a voice.
      const base = height - RIBBON_BOTTOM
      const swing = 5 + envelope * 42
      const centre = width / 2
      // Listening pulls toward her; speaking pushes away. Direction is what
      // separates the two states at a glance, not just hue.
      const direction = active === 'speaking' ? 1 : -1

      const shape = (index: number): number[] => {
        const depth = 1 - index * 0.24
        const speed = (0.9 + index * 0.5) * direction
        const length = 0.01 + index * 0.0045
        const ys: number[] = []
        for (let x = 0; x <= width; x += STEP) {
          // Tapered at the edges so the ribbon dissolves into the window
          // rather than being sliced off by it.
          const edge = Math.sin((x / width) * Math.PI) ** 1.3
          const fromCentre = (x - centre) * length
          ys.push(
            base -
              Math.sin(fromCentre + phase * speed) * swing * depth * edge -
              Math.sin(fromCentre * 2.3 - phase * speed * 0.62) * swing * 0.38 * depth * edge,
          )
        }
        return ys
      }

      // Body under the front wave, so it reads as a mass of light and not a
      // wireframe, fading downward into the wash.
      const front = shape(0)
      ctx.beginPath()
      ctx.moveTo(0, height)
      front.forEach((y, i) => ctx.lineTo(i * STEP, y))
      ctx.lineTo(width, height)
      ctx.closePath()
      const body = ctx.createLinearGradient(0, base - swing, 0, height)
      body.addColorStop(0, `rgba(${r},${g},${b},${(0.16 + envelope * 0.18) * fade})`)
      body.addColorStop(1, `rgba(${r},${g},${b},0)`)
      ctx.fillStyle = body
      ctx.fill()

      ctx.lineCap = 'round'
      // Back to front, so the brightest line is not dimmed by the ones behind.
      for (let w = WAVES - 1; w >= 0; w -= 1) {
        const ys = w === 0 ? front : shape(w)
        ctx.beginPath()
        ys.forEach((y, i) => (i ? ctx.lineTo(i * STEP, y) : ctx.moveTo(0, y)))
        ctx.strokeStyle = `rgba(${r},${g},${b},${(0.85 - w * 0.24) * fade})`
        ctx.lineWidth = 2 - w * 0.5
        // The glow is what makes it read as light rather than ink.
        ctx.shadowColor = `rgba(${r},${g},${b},${0.75 * fade})`
        ctx.shadowBlur = 10 + envelope * 16
        ctx.stroke()
      }
      ctx.shadowBlur = 0
    }

    tick.current = draw
    if (modeRef.current && running.current === 0) running.current = requestAnimationFrame(draw)

    return () => {
      cancelAnimationFrame(running.current)
      running.current = 0
      tick.current = null
      observer.disconnect()
    }
  }, [])

  // Restart the loop when a voice appears. Kept out of the effect above so a
  // state change never rebuilds the canvas or resets the envelope mid-word.
  useEffect(() => {
    if (mode && running.current === 0 && tick.current) {
      running.current = requestAnimationFrame(tick.current)
    }
  }, [mode])

  return (
    <canvas
      ref={canvas}
      aria-hidden
      className="pointer-events-none absolute inset-0 h-full w-full"
    />
  )
}
