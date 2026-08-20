/**
 * Compact companion or expanded working window.
 *
 * Electron main owns the real bounds, so this mirrors rather than decides: it
 * asks for the current mode on mount and listens for changes, including ones
 * main initiates. Keeping a local boolean as the source of truth would drift
 * the moment anything resized the window without going through here.
 */

import { useCallback, useEffect, useState } from 'react'

export interface UseWindowMode {
  expanded: boolean
  toggle: () => void
  setExpanded: (expanded: boolean) => void
  /** Filling the screen. Implies `expanded`. */
  maximized: boolean
  toggleMaximized: () => void
}

export function useWindowMode(): UseWindowMode {
  const [expanded, setLocal] = useState(false)
  const [maximized, setMaximizedLocal] = useState(false)

  useEffect(() => {
    let cancelled = false
    void window.aria.isExpanded().then((value) => {
      if (!cancelled) setLocal(value)
    })
    void window.aria.isMaximized().then((value) => {
      if (!cancelled) setMaximizedLocal(value)
    })
    const off = window.aria.onWindowMode(setLocal)
    // The OS maximises too, so this is a subscription rather than only a
    // reply to our own call — Win+Up would otherwise leave the button lying.
    const offMax = window.aria.onWindowMaximized(setMaximizedLocal)
    return () => {
      cancelled = true
      off()
      offMax()
    }
  }, [])

  const setExpanded = useCallback((next: boolean) => {
    // Optimistic: the window starts moving immediately, and main confirms via
    // onWindowMode. Waiting for the round-trip makes the button feel broken.
    setLocal(next)
    void window.aria.setExpanded(next).then(setLocal)
  }, [])

  const toggleMaximized = useCallback(() => {
    const next = !maximized
    setMaximizedLocal(next)
    // Maximising implies expanding, and main is what actually applies that —
    // mirrored here so the rail and the controls do not disagree for a frame.
    if (next) setLocal(true)
    void window.aria.setMaximized(next).then(setMaximizedLocal)
  }, [maximized])

  const toggle = useCallback(() => setExpanded(!expanded), [expanded, setExpanded])

  return { expanded, toggle, setExpanded, maximized, toggleMaximized }
}
