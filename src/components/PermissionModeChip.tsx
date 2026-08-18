/**
 * What she is allowed to do without asking, visible without opening a panel.
 *
 * The gap this fills: the mode selector shipped inside `ToolsPanel` and
 * nowhere else. In Full access **nothing ever prompts**, so the loudest state
 * in the app was also the quietest one — the only way to notice was that
 * confirmations had stopped appearing, which reads as a bug rather than a
 * setting. Meanwhile hands-free, far less consequential, has had a persistent
 * dot on the rail since Phase 2.
 *
 * A button, not a label: seeing the mode and being unable to do anything
 * about it from here would just move the problem. It opens the Tools panel,
 * where the selector and its explanation already live.
 */

import type { PermissionMode } from '@/hooks/usePermissionMode'
import { MODE_LABEL } from '@/hooks/usePermissionMode'

/** Auto is the default and the quiet one, so it is styled as ordinary chrome.
 *  Manual is a deliberate tightening and reads as active. Full access is the
 *  one real departure from "every destructive operation asks" and carries the
 *  same warning colour DANGER tools do. */
const MODE_STYLE: Record<PermissionMode, string> = {
  manual: 'text-aria-muted',
  auto: 'text-aria-faint',
  full_access: 'text-aria-bad',
}

const MODE_TITLE: Record<PermissionMode, string> = {
  manual: 'Manual — everything asks first. Click to change.',
  auto: 'Auto — trusted folders run silently, everything else asks. Click to change.',
  full_access: 'Full access — nothing asks, including checkout pages. Click to change.',
}

export function PermissionModeChip({
  mode,
  disabled,
  onOpen,
}: {
  mode: PermissionMode
  disabled: boolean
  onOpen: () => void
}): JSX.Element {
  return (
    <button
      type="button"
      onClick={onOpen}
      disabled={disabled}
      aria-label={`Permission mode: ${MODE_LABEL[mode]}`}
      title={MODE_TITLE[mode]}
      className={[
        'interactive flex shrink-0 items-center gap-1.5 rounded-lg px-2 py-1 text-micro',
        disabled ? 'cursor-not-allowed opacity-40' : '',
        MODE_STYLE[mode],
      ].join(' ')}
    >
      <span
        className={`h-1.5 w-1.5 shrink-0 rounded-full ${
          mode === 'full_access' ? 'bg-aria-bad' : 'bg-current opacity-60'
        }`}
        aria-hidden
      />
      {MODE_LABEL[mode]}
    </button>
  )
}
