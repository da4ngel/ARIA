/**
 * Sends the live voice level to the main process, for the screen overlay.
 *
 * The overlay owns no audio — it cannot, since the microphone and the playback
 * graph both live here. So this window, which does own them, reports what it
 * hears and what it is saying, and main relays it.
 *
 * **Throttled to ~30Hz and silent when idle.** Sixty IPC messages a second to
 * animate a glow would cost more than the glow; thirty is past the point where
 * the envelope smoothing in `ScreenRim` can tell the difference. When there is
 * no voice it sends one final zero and then stops entirely, so an idle machine
 * carries no traffic at all.
 */

import { useEffect, useRef } from 'react'

const INTERVAL_MS = 33

export type VoiceMode = 'listening' | 'speaking' | null

export function usePublishVoiceLevel(mode: VoiceMode, getLevel: () => number): void {
  // Held in refs so a changing mode never restarts the timer mid-sentence.
  const modeRef = useRef(mode)
  const levelRef = useRef(getLevel)
  modeRef.current = mode
  levelRef.current = getLevel

  useEffect(() => {
    let sentIdle = true

    const timer = window.setInterval(() => {
      const active = modeRef.current
      if (!active) {
        // One zero on the way down, so the overlay fades rather than freezing
        // at whatever level it last heard.
        if (!sentIdle) {
          sentIdle = true
          window.aria.publishVoiceLevel(0, null)
        }
        return
      }
      sentIdle = false
      window.aria.publishVoiceLevel(Math.min(1, Math.max(0, levelRef.current())), active)
    }, INTERVAL_MS)

    return () => {
      window.clearInterval(timer)
      window.aria.publishVoiceLevel(0, null)
    }
  }, [])
}
