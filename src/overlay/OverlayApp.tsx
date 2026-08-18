/**
 * The overlay's whole application: a rim and a caption, driven by events.
 *
 * It holds no conversation state and can start none — CLAUDE.md rule 1. Every
 * word here arrived over the same `aria:event` stream the main window reads,
 * and the moment a turn ends it is forgotten.
 */

import { useEffect, useRef, useState } from 'react'

import { Caption } from '@/overlay/Caption'
import { ScreenRim, type RimMode } from '@/overlay/ScreenRim'
import type { AssistantState, SidecarEvent } from '@/types/bridge'

/** How long the last exchange stays readable after she stops talking. */
const LINGER_MS = 4500
/** A miss is worth a glance, not a read. */
const MISHEARD_MS = 2200

export function OverlayApp(): JSX.Element {
  const [mode, setMode] = useState<RimMode>(null)
  const [asked, setAsked] = useState('')
  const [reply, setReply] = useState('')
  const [misheard, setMisheard] = useState('')
  // Read once a frame by the canvas, so it must never be React state.
  const level = useRef(0)
  const linger = useRef<number | undefined>(undefined)

  useEffect(() => {
    const clearLinger = (): void => {
      if (linger.current !== undefined) window.clearTimeout(linger.current)
      linger.current = undefined
    }

    const offLevel = window.aria.onVoiceLevel((payload) => {
      level.current = payload.level
      // The level carries the mode too. It arrives ~30 times a second from the
      // window that owns the audio, which knows whether sound is actually
      // coming out — `state.change` only knows a turn was started.
      setMode(payload.mode)
    })

    const offEvent = window.aria.onEvent((event: SidecarEvent) => {
      if (event.method === 'state.change') {
        const state = event.params.state as AssistantState
        // Only a floor: the level channel above wins, because it is the one
        // that knows about real playback.
        if (state === 'listening') setMode('listening')
        return
      }

      if (event.method === 'misheard') {
        // Shown so a run of silent drops is visibly a mishearing rather than
        // an app that has stopped responding.
        setMisheard(String(event.params.text ?? ''))
        window.setTimeout(() => setMisheard(''), MISHEARD_MS)
        return
      }

      if (event.method === 'heard') {
        setMisheard('')
        clearLinger()
        setAsked(String(event.params.text ?? ''))
        setReply('')
        return
      }

      if (event.method === 'token') {
        clearLinger()
        setReply((previous) => previous + String(event.params.text ?? ''))
        return
      }

      if (event.method === 'turn.complete') {
        // Kept up briefly rather than yanked away the instant she stops — the
        // last sentence is exactly the one you were still reading.
        clearLinger()
        linger.current = window.setTimeout(() => {
          setAsked('')
          setReply('')
        }, LINGER_MS)
      }

      if (event.method === 'proactive') {
        // No preceding question — `Caption` already renders `reply` alone
        // when `asked` is empty, so this reuses the exact same component
        // rather than a second caption style for the one case that has no
        // question in it.
        setMisheard('')
        clearLinger()
        setAsked('')
        setReply(String(event.params.text ?? ''))
        linger.current = window.setTimeout(() => {
          setAsked('')
          setReply('')
        }, LINGER_MS)
      }
    })

    return () => {
      offLevel()
      offEvent()
      clearLinger()
    }
  }, [])

  return (
    <>
      <ScreenRim mode={mode} getLevel={() => level.current} />
      <Caption asked={asked} reply={reply} misheard={misheard} />
    </>
  )
}
