/**
 * Browsing the machine, without leaving her.
 *
 * The last piece of the three Eyaas asked for alongside permission modes:
 * *"easy file navigation"*. Confirmed as a full Explorer replacement rather
 * than a read-only viewer — open, rename, delete, and hand a file straight
 * to the conversation.
 *
 * **These are clicks, not tool calls, and that is the whole distinction.**
 * `list_folder`/`rename_file`/`delete_file` are tools the *model* asks for,
 * so they go through `PermissionEngine` and its dialog. A modal in front of
 * "I clicked Rename" would be asking someone to confirm the thing they just
 * did. What does not change: the hard refusals in `tools/files.py` (drive
 * roots, Windows, Program Files) still apply, because those were never
 * confirmation mechanisms — and deleting goes to the Recycle Bin, which is
 * what makes a misclick survivable rather than final.
 */

import { useCallback, useEffect, useState } from 'react'

import { Panel } from '@/components/Panel'

interface Entry {
  name: string
  path: string
  kind: 'file' | 'folder' | 'drive'
  size?: number
  modified?: number
}

interface Listing {
  path: string
  parent: string | null
  entries: Entry[]
}

function humanSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
}

function humanDate(epochSeconds: number): string {
  const days = (Date.now() / 1000 - epochSeconds) / 86400
  if (days < 1) return 'today'
  if (days < 2) return 'yesterday'
  if (days < 60) return `${Math.floor(days)} days ago`
  return new Date(epochSeconds * 1000).toLocaleDateString(undefined, {
    month: 'short',
    year: 'numeric',
  })
}

export function FilesPanel({
  onClose,
  onAttach,
}: {
  onClose: () => void
  /** Hand a file to the composer. The panel is where you find it; the
   *  conversation is where you ask about it, and making that one click
   *  rather than a trip through the OS picker is most of the point. */
  onAttach?: (path: string) => void
}): JSX.Element {
  const [listing, setListing] = useState<Listing | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [renaming, setRenaming] = useState<string | null>(null)
  const [draft, setDraft] = useState('')

  const browse = useCallback(async (path: string) => {
    setError(null)
    try {
      setListing(await window.aria.call<Listing>('files.browse', { path }))
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    }
  }, [])

  useEffect(() => {
    void browse('')
  }, [browse])

  const act = useCallback(
    async (method: string, params: Record<string, unknown>) => {
      setError(null)
      try {
        await window.aria.call(method, params)
        await browse(listing?.path ?? '')
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause))
      }
    },
    [browse, listing],
  )

  const remove = useCallback(
    (entry: Entry) => {
      // No modal. The Recycle Bin *is* the confirmation — the same bargain
      // Explorer makes, and the reason this is the one delete in the app
      // without a round-trip.
      void act('files.delete', { path: entry.path })
    },
    [act],
  )

  const entries = listing?.entries ?? []

  return (
    <Panel title="Files" onClose={onClose} width="max-w-lg">
      {/* Where you are, and the way back. A breadcrumb of the full path
          would wrap to three lines on a deep folder; the parent hop plus the
          current folder's own name is what people actually use. */}
      <div className="mb-2 flex items-center gap-2">
        <button
          type="button"
          disabled={!listing?.path}
          onClick={() => void browse(listing?.parent ?? '')}
          className="interactive shrink-0 rounded-lg px-2 py-1 text-tiny text-aria-muted disabled:cursor-not-allowed disabled:opacity-30"
        >
          ← Up
        </button>
        <p className="min-w-0 flex-1 truncate font-mono text-micro text-aria-faint">
          {listing?.path || 'This computer'}
        </p>
      </div>

      <ul className="max-h-[26rem] space-y-0.5 overflow-y-auto pr-0.5">
        {entries.length === 0 && !error && (
          <li className="px-2 py-3 text-tiny text-aria-faint">Nothing in here.</li>
        )}
        {entries.map((entry) => (
          <li
            key={entry.path}
            className="group flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-white/5"
          >
            {renaming === entry.path ? (
              <input
                autoFocus
                value={draft}
                aria-label={`New name for ${entry.name}`}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    setRenaming(null)
                    void act('files.rename', { path: entry.path, name: draft })
                  }
                  if (e.key === 'Escape') setRenaming(null)
                }}
                onBlur={() => setRenaming(null)}
                className="min-w-0 flex-1 rounded bg-aria-sunk px-1.5 py-0.5 text-tiny text-aria-text focus:outline-none"
              />
            ) : (
              <button
                type="button"
                onClick={() =>
                  entry.kind === 'file' ? onAttach?.(entry.path) : void browse(entry.path)
                }
                className="interactive flex min-w-0 flex-1 items-center gap-2 text-left"
                title={entry.kind === 'file' ? 'Attach to the conversation' : entry.path}
              >
                <span className="shrink-0 text-aria-faint" aria-hidden>
                  {entry.kind === 'file' ? '▪' : '▸'}
                </span>
                <span className="truncate text-tiny text-aria-text">{entry.name}</span>
                {entry.kind === 'file' && entry.size !== undefined && (
                  <span className="shrink-0 font-mono text-micro text-aria-faint">
                    {humanSize(entry.size)}
                  </span>
                )}
                {entry.modified !== undefined && entry.kind !== 'drive' && (
                  <span className="shrink-0 font-mono text-micro text-aria-faint">
                    {humanDate(entry.modified)}
                  </span>
                )}
              </button>
            )}

            {/* Only on hover, and only for real entries: a row of four
                buttons against every drive letter is noise around the thing
                you came here to click. */}
            {entry.kind !== 'drive' && renaming !== entry.path && (
              <span className="flex shrink-0 items-center gap-0.5 opacity-0 transition-opacity group-hover:opacity-100">
                <button
                  type="button"
                  aria-label={`Rename ${entry.name}`}
                  onClick={() => {
                    setRenaming(entry.path)
                    setDraft(entry.name)
                  }}
                  className="interactive rounded px-1.5 py-0.5 text-micro text-aria-faint hover:text-aria-text"
                >
                  Rename
                </button>
                <button
                  type="button"
                  aria-label={`Show ${entry.name} in Explorer`}
                  onClick={() => void act('files.reveal', { path: entry.path })}
                  className="interactive rounded px-1.5 py-0.5 text-micro text-aria-faint hover:text-aria-text"
                >
                  Reveal
                </button>
                <button
                  type="button"
                  aria-label={`Delete ${entry.name}`}
                  onClick={() => remove(entry)}
                  className="interactive rounded px-1.5 py-0.5 text-micro text-aria-faint hover:text-aria-bad"
                >
                  Delete
                </button>
              </span>
            )}
          </li>
        ))}
      </ul>

      <p className="mt-2 text-micro leading-relaxed text-aria-faint">
        Clicking a file attaches it to the conversation. Deleting sends it to the Recycle Bin, so
        nothing here is permanent.
      </p>
      {error && <p className="mt-2 text-tiny text-aria-bad">{error}</p>}
    </Panel>
  )
}
