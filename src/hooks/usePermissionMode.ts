/**
 * The global permission mode, shared by everything that shows it.
 *
 * A pure mirror of the sidecar (CLAUDE.md rule 1): the mode lives in the
 * `settings` table and `PermissionEngine` is what enforces it. This hook only
 * caches the last answer so three surfaces can render it without three
 * independent fetches that could disagree.
 *
 * **It exists because the mode used to be invisible.** The selector shipped
 * inside `ToolsPanel` and nowhere else, so the only way to know which mode
 * you were in was to open the Tools panel and look — and in Full access
 * nothing ever prompts, which means the most consequential state in the app
 * was also the one with no representation on screen. Hands-free, far less
 * consequential, has had a persistent marker on the rail since Phase 2.
 */

import { useCallback, useEffect, useState } from 'react'

/** Matches `sidecar.tools.permissions.PermissionMode` — a string on the
 *  wire, one value per RPC round trip, never inferred client-side. */
export type PermissionMode = 'manual' | 'auto' | 'full_access'

export const MODE_OPTIONS: Array<{ value: PermissionMode; label: string }> = [
  { value: 'manual', label: 'Manual' },
  { value: 'auto', label: 'Auto' },
  { value: 'full_access', label: 'Full access' },
]

/** What each mode actually changes — shown under every selector so choosing
 *  Full access is never a moment of "and this means...?". Shared rather than
 *  duplicated: two surfaces describing the same switch in different words is
 *  how one of them ends up quietly wrong. */
export const MODE_COPY: Record<PermissionMode, string> = {
  manual:
    'Every action that changes or removes something asks first, every time — trusted folders and "always allow" are both set aside while this is on, not cleared.',
  auto: 'Today’s behavior. Trusted folders and "always allow" work as you’ve set them up; everything else still asks.',
  full_access:
    'Nothing asks — not a confirmation, not a checkout-page warning, not a DANGER action’s typed confirmation. Off by default for a reason.',
}

export const MODE_LABEL: Record<PermissionMode, string> = {
  manual: 'Manual',
  auto: 'Auto',
  full_access: 'Full access',
}

export interface UsePermissionMode {
  mode: PermissionMode
  setMode: (next: PermissionMode) => Promise<void>
  error: string | null
  refresh: () => Promise<void>
}

export function usePermissionMode(connected: boolean): UsePermissionMode {
  const [mode, setModeState] = useState<PermissionMode>('auto')
  const [error, setError] = useState<string | null>(null)

  // The mode rides along on `tools.list` rather than having a read of its
  // own — that is how ToolsPanel already got it, and adding a second RPC for
  // one enum would be a round trip for nothing.
  const refresh = useCallback(async () => {
    if (!connected) return
    try {
      const list = await window.aria.call<{ mode?: PermissionMode }>('tools.list', {})
      if (list.mode) setModeState(list.mode)
    } catch {
      /* the status line already reports that the brain is down */
    }
  }, [connected])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const setMode = useCallback(
    async (next: PermissionMode) => {
      setError(null)
      const previous = mode
      setModeState(next) // optimistic — a mode switch should feel instant
      try {
        const result = await window.aria.call<{ mode: PermissionMode }>('permissions.mode', {
          mode: next,
        })
        setModeState(result.mode)
      } catch (cause) {
        // Rolled back rather than left showing a mode that is not in force.
        // A selector that lies about this is worse than one that fails.
        setModeState(previous)
        setError(cause instanceof Error ? cause.message : String(cause))
      }
    },
    [mode],
  )

  return { mode, setMode, error, refresh }
}
