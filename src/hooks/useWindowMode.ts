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
}

export function useWindowMode(): UseWindowMode {
  const [expanded, setLocal] = useState(false)

  useEffect(() => {
    let cancelled = false
    void window.aria.isExpanded().then((value) => {
      if (!cancelled) setLocal(value)
    })
    const off = window.aria.onWindowMode(setLocal)
    return () => {
      cancelled = true
      off()
    }
  }, [])

  const setExpanded = useCallback((next: boolean) => {
    // Optimistic: the window starts moving immediately, and main confirms via
    // onWindowMode. Waiting for the round-trip makes the button feel broken.
    setLocal(next)
    void window.aria.setExpanded(next).then(setLocal)
  }, [])

  const toggle = useCallback(() => setExpanded(!expanded), [expanded, setExpanded])

  return { expanded, toggle, setExpanded }
}
