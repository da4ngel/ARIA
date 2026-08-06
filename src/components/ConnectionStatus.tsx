/**
 * The Phase 0 acceptance gate's visible signal: "Brain: connected".
 *
 * Renders for any status, but `App` only mounts it when something is wrong —
 * a permanent row saying everything is fine is a row spent on nothing. The
 * component does not decide its own visibility, so the gate can still be
 * checked directly and the orb carries the healthy case.
 */

import type { BrainStatus } from '@/types/bridge'

const LABEL: Record<BrainStatus, string> = {
  starting: 'starting…',
  connecting: 'connecting…',
  connected: 'connected',
  reconnecting: 'reconnecting…',
  disconnected: 'disconnected',
}

const DOT: Record<BrainStatus, string> = {
  starting: 'bg-aria-warn',
  connecting: 'bg-aria-warn',
  connected: 'bg-aria-ok',
  reconnecting: 'bg-aria-warn animate-pulse',
  disconnected: 'bg-aria-bad',
}

export function ConnectionStatus({ status }: { status: BrainStatus }): JSX.Element {
  return (
    <div className="flex items-center gap-2 text-tiny">
      <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${DOT[status]}`} aria-hidden />
      <span className="text-aria-faint">Brain:</span>
      <span className="text-aria-muted">{LABEL[status]}</span>
    </div>
  )
}
