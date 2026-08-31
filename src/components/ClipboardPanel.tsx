/**
 * What you copied, newest first, click to copy back.
 *
 * **The warning at the top is not boilerplate.** Everything copied on this
 * machine lands in `data/aria.db`. `core/clipboard_watcher.py` refuses what
 * looks like a credential first, and that filter is a reduction in exposure
 * rather than a guarantee — it cannot tell a word-based passphrase from a
 * sentence. Saying so here, where somebody is looking at their own clipboard
 * history, is the only place the caveat actually reaches them.
 */

import { useState } from 'react'

import { Panel } from '@/components/Panel'
import { useClipboard } from '@/hooks/useClipboard'
import type { ClipEntry } from '@/types/bridge'

/** How long the button says "copied". Long enough to read, short enough
 *  that it is back to "copy" before you look again. */
const COPIED_FOR_MS = 1200

function clock(iso: string): string {
  const at = new Date(iso.endsWith('Z') ? iso : `${iso}Z`)
  if (Number.isNaN(at.getTime())) return iso
  return at.toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })
}

/** One line, whitespace collapsed. A copied file is not a paragraph to read
 *  back — it is a thing to recognise and click. */
function preview(content: string): string {
  const flat = content.replace(/\s+/g, ' ').trim()
  return flat.length > 160 ? `${flat.slice(0, 160)}…` : flat
}

function Entry({
  entry,
  onCopy,
  onForget,
}: {
  entry: ClipEntry
  onCopy: () => Promise<void>
  onForget: () => void
}): JSX.Element {
  // **The whole point of the panel is putting something back on the clipboard,
  // and a clipboard write is invisible** — nothing on screen changes, and the
  // proof is in another application. So the button says so for a moment.
  const [copied, setCopied] = useState(false)

  const copy = async (): Promise<void> => {
    await onCopy()
    setCopied(true)
    window.setTimeout(() => setCopied(false), COPIED_FOR_MS)
  }

  return (
    <li className="rim raised group rounded-lg">
      <div className="flex items-start justify-between gap-2 px-3 py-2">
        {/* The row itself still copies — it is the obvious thing to click —
            but discovering that required hovering, so the button below is the
            one that is actually visible. */}
        <button
          type="button"
          onClick={() => void copy()}
          title="Copy this back to the clipboard"
          className="interactive min-w-0 flex-1 text-left"
        >
          <span className="block truncate text-small text-aria-text">{preview(entry.content)}</span>
          <span className="block text-micro text-aria-faint">
            {clock(entry.copied_at)} · {entry.chars} chars
            {entry.source && ` · ${entry.source}`}
          </span>
        </button>
        <div className="flex shrink-0 items-center gap-1">
          <button
            type="button"
            onClick={() => void copy()}
            aria-label={`Copy ${preview(entry.content)}`}
            className={`interactive rim rounded-md px-2 py-1 text-micro ${
              copied ? 'text-aria-ok' : 'text-aria-dim hover:text-aria-text'
            }`}
          >
            {copied ? 'copied' : 'copy'}
          </button>
          {/* No dialog — deleting one line of your own clipboard history is not
              a decision anyone needs confirming back at them. */}
          <button
            type="button"
            onClick={onForget}
            className="interactive rounded-md px-2 py-1 text-micro text-aria-muted hover:text-aria-bad"
          >
            forget
          </button>
        </div>
      </div>
    </li>
  )
}

export function ClipboardPanel({ onClose }: { onClose: () => void }): JSX.Element {
  const { entries, watching, skippedSecrets, loading, error, copy, forget, forgetAll } =
    useClipboard(true)

  return (
    <Panel title="Clipboard" onClose={onClose} width="max-w-lg">
      {error && <p className="mb-3 text-small text-aria-bad">{error}</p>}

      <p className="rim raised mb-3 rounded-lg px-3 py-2 text-micro text-aria-muted">
        Everything you copy is stored on this machine, in ARIA&apos;s database. Keys and
        passwords are filtered out where they can be recognised
        {skippedSecrets > 0 && ` — ${skippedSecrets} skipped so far`}, but a passphrase made
        of ordinary words cannot be told from a sentence. Clear the history if you have
        copied something you would rather was not kept.
      </p>

      {!watching && (
        <p className="mb-3 text-small text-aria-warn">
          Not recording — the clipboard watcher is not running in this session.
        </p>
      )}

      {entries.length === 0 ? (
        <p className="text-small text-aria-faint">
          {loading ? 'Reading…' : 'Nothing copied yet.'}
        </p>
      ) : (
        <>
          <ul className="space-y-1">
            {entries.map((entry) => (
              <Entry
                key={entry.id}
                entry={entry}
                onCopy={() => copy(entry.id)}
                onForget={() => void forget(entry.id)}
              />
            ))}
          </ul>
          <button
            type="button"
            onClick={() => void forgetAll()}
            className="interactive rim mt-3 w-full rounded-lg px-3 py-2 text-small text-aria-muted hover:text-aria-bad"
          >
            Forget everything
          </button>
        </>
      )}
    </Panel>
  )
}
