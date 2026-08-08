/**
 * Minimize, resize, close.
 *
 * The window is frameless, so Windows draws none of these — and until now
 * neither did the app. There was no way to close it from its own window; only
 * the tray could. That is the gap this fills.
 *
 * "Close" hides to the tray rather than quitting, because she keeps listening
 * and the wake word keeps working. The label says so, since a close button
 * that does not close is worth being honest about.
 */

const HIT = 'interactive grid h-7 w-7 place-items-center rounded-lg text-aria-muted'

export function WindowControls({
  expanded,
  onToggleExpanded,
}: {
  expanded: boolean
  onToggleExpanded: () => void
}): JSX.Element {
  return (
    <div className="ml-1 flex shrink-0 items-center gap-0.5">
      <button
        type="button"
        aria-label="Minimize"
        title="Minimize"
        onClick={() => window.aria.minimize()}
        className={`${HIT} hover:text-aria-text`}
      >
        <svg {...stroke} aria-hidden>
          <path d="M3 7h8" />
        </svg>
      </button>

      <button
        type="button"
        aria-label={expanded ? 'Shrink' : 'Expand'}
        title={expanded ? 'Shrink (Ctrl+E)' : 'Expand (Ctrl+E)'}
        onClick={onToggleExpanded}
        className={`${HIT} hover:text-aria-text`}
      >
        {expanded ? (
          <svg {...stroke} aria-hidden>
            <path d="M11.2 5.6h-3v-3M2.8 8.4h3v3M8.2 5.8 11.4 2.6M5.8 8.2 2.6 11.4" />
          </svg>
        ) : (
          <svg {...stroke} aria-hidden>
            <path d="M8.4 2.6h3v3M5.6 11.4h-3v-3M11.4 2.6 8 6M2.6 11.4 6 8" />
          </svg>
        )}
      </button>

      <button
        type="button"
        aria-label="Close to tray"
        title="Close to tray — she keeps listening"
        onClick={() => window.aria.hide()}
        // The one red hover in the chrome. It is the standard place for it and
        // the only control here that makes the window go away.
        className={`${HIT} hover:bg-aria-bad/80 hover:text-white`}
      >
        <svg {...stroke} aria-hidden>
          <path d="M3.6 3.6l6.8 6.8M10.4 3.6l-6.8 6.8" />
        </svg>
      </button>
    </div>
  )
}

const stroke = {
  width: 14,
  height: 14,
  viewBox: '0 0 14 14',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.4,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
}
