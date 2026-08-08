/**
 * The keyboard map, on demand.
 *
 * It used to live permanently in the footer, which is a row spent on something
 * you stop reading after the first day. Behind '?' it stays discoverable and
 * stops costing space.
 */

import { Panel } from '@/components/Panel'

const KEYS: [string, string][] = [
  ['Ctrl + Space', 'Show or hide Aria'],
  ['Enter', 'Send'],
  ['Shift + Enter', 'New line'],
  ['Esc', 'Stop generating, or close this'],
  ['Ctrl + K', 'Show or hide your chats'],
  ['Ctrl + N', 'New chat'],
  ['Ctrl + E', 'Expand or shrink the window'],
  ['?', 'This list'],
]

export function Shortcuts({ onClose }: { onClose: () => void }): JSX.Element {
  return (
    <Panel title="Shortcuts" onClose={onClose} width="max-w-sm">
      <dl className="flex flex-col gap-0.5">
        {KEYS.map(([key, what]) => (
          <div
            key={key}
            className="flex items-center justify-between gap-3 rounded-md px-1.5 py-1.5"
          >
            <dt className="shrink-0 font-mono text-micro text-aria-text">{key}</dt>
            <dd className="truncate text-right text-tiny text-aria-muted">{what}</dd>
          </div>
        ))}
      </dl>
    </Panel>
  )
}
