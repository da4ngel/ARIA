/** The Phase 0 acceptance gate's visible signal: "Brain: connected". */

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
    <div className="flex items-center gap-2 text-sm">
      <span className={`h-2 w-2 rounded-full ${DOT[status]}`} aria-hidden />
      <span className="text-aria-muted">Brain:</span>
      <span className="text-aria-text">{LABEL[status]}</span>
    </div>
  )
}
