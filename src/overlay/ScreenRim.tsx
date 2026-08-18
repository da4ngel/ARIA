/**
 * The glow around the edge of the screen.
 *
 * Same idea as `VoiceAura` and deliberately the same envelope constants, so
 * she moves at one speed whether you are looking at the window or at the
 * desktop. What differs is the canvas: this one is the whole display, so it
 * costs more per frame and earns it back by drawing almost nothing — a
 * handful of rounded rectangles at the edge, and a blur.
 *
 * **Hue alone used to be the only thing telling listening and speaking
 * apart, and CLAUDE.md already recorded that as wrong** — VoiceAura's own
 * note is that colour does not survive a glance, which is exactly the
 * distance this overlay is read from. So it carries the same fix: **two thin
 * pulses travel the band**, inward for listening and outward for speaking —
 * "draws inward from the edges" and "radiates outward" are literally true of
 * a border, more so than they were of VoiceAura's ribbon. The base glow
 * (hue, thickness, the two-pass halo) is unchanged; the pulses are additive.
 *
 * **Device pixel ratio is pinned to 1 here.** A 2560-wide canvas at ratio 2 is
 * four times the fill for a band of soft light nobody will inspect, on a
 * machine already running Whisper, Kokoro and a 7B model. The pulses keep to
 * that budget: two extra thin strokes with a small, fixed blur ceiling, not
 * a second full pass over the perimeter.
 */

import { useEffect, useRef } from 'react'

import { RGB } from '@/styles/tokens'

export type RimMode = 'listening' | 'speaking' | null

interface Props {
  mode: RimMode
  /** Live amplitude, 0..1, sampled once a frame. */
  getLevel: () => number
}

/** The orb's hues as triples, from the one place they are defined — see
 *  `VoiceAura` for why these are derived rather than written out. */
const HUE = RGB as Record<'listening' | 'speaking', [number, number, number]>

const ATTACK = 0.28
const RELEASE = 0.08
/** Corner radius of the traced rectangle — near Windows 11's own. */
const RADIUS = 12
/** Band thickness at silence and at full voice. */
const THICKNESS_MIN = 5
const THICKNESS_MAX = 26

/** How many pulses travel the band at once. Two, offset by half a cycle, so
 *  there is always one somewhere between fading in and fading out — one
 *  alone leaves a visible dead moment each loop. */
const PULSE_COUNT = 2
/** Cycles per frame at rest; scales up slightly with voice, the same way
 *  VoiceAura's ribbon phase does. Slow enough to read as travel, not flicker. */
const PULSE_SPEED = 0.0034
/** Where in the band's own thickness a pulse sits at its start and end —
 *  fractions of `thickness`, kept off 0 and 1 so it never touches the hard
 *  edges of the two-pass halo underneath. */
const PULSE_INSET_NEAR = 0.14
const PULSE_INSET_FAR = 0.86

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
    let travel = 0

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
      // A little livelier when she is louder, same spirit as VoiceAura's
      // ribbon phase — but this loops (mod 1) rather than accumulating, since
      // it drives a position in the band, not a running waveform.
      if (!still) travel = (travel + PULSE_SPEED + envelope * 0.006) % 1

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

      // ── direction of travel ─────────────────────────────────────────
      // Two thin, brighter strokes sweep the width of the band. Listening
      // runs near -> far (the edge pulling inward, toward the room);
      // speaking runs far -> near (her voice pushing out past the edge).
      // Reduced motion drops this pass entirely and keeps only the static
      // halo above — the same choice VoiceAura makes for its ribbon.
      if (!still) {
        const direction = active === 'speaking' ? 1 : -1
        for (let p = 0; p < PULSE_COUNT; p += 1) {
          const t = (travel + p / PULSE_COUNT) % 1
          // t runs 0->1 every cycle regardless of direction; direction only
          // decides which physical end of the band t=0 corresponds to.
          const along = direction === 1 ? 1 - t : t
          const pulseInset =
            thickness * (PULSE_INSET_NEAR + along * (PULSE_INSET_FAR - PULSE_INSET_NEAR))
          // Fades in from one edge of its sweep and out at the other, so it
          // reads as a pulse passing through rather than an object that
          // pops in and out of existence.
          //
          // Not scaled by `strength` alone: at silence that would nearly
          // erase the direction cue right when it matters most — the moment
          // listening opens, before any voice has arrived. VoiceAura avoids
          // the same trap by giving its ribbon a swing floor regardless of
          // envelope; this is that floor, expressed as a base fraction.
          const pulseAlpha = Math.sin(t * Math.PI) * fade * (0.5 + strength * 0.5)
          if (pulseAlpha < 0.02) continue
          ctx.beginPath()
          ctx.roundRect(
            pulseInset,
            pulseInset,
            width - pulseInset * 2,
            height - pulseInset * 2,
            RADIUS,
          )
          // Additive, not source-over. Measured: at moderate-to-high
          // `strength` the halo underneath is already near-saturated at the
          // hue's own colour (r,g,b pinned close to `HUE` across the band),
          // so a same-hue stroke on top under normal compositing has no
          // headroom left to read as brighter — it is invisible exactly
          // when the glow is most awake. `lighter` adds light where it
          // overlaps instead of being capped by what is already there;
          // verified by sampling pixels before/after, ~150/765 point jump.
          ctx.globalCompositeOperation = 'lighter'
          ctx.strokeStyle = `rgba(${r},${g},${b},${Math.min(1, pulseAlpha * 0.9)})`
          ctx.lineWidth = 2
          ctx.shadowColor = `rgba(${r},${g},${b},${pulseAlpha})`
          ctx.shadowBlur = 4 + strength * 6
          ctx.stroke()
          ctx.globalCompositeOperation = 'source-over'
        }
      }
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
