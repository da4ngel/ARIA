/**
 * Past conversations — open, search, rename, delete.
 *
 * A full-panel overlay rather than a sidebar: the window is 420x600 and not
 * resizable, so a persistent list would take a third of the conversation.
 */

import { useEffect, useRef, useState } from 'react'

import { Panel } from '@/components/Panel'
import { type DeletePreview, useSessions } from '@/hooks/useSessions'
import type { SessionSummary } from '@/types/bridge'

/** Day buckets, so a long list stays scannable without showing 12 dates. */
function dayGroup(iso: string): string {
  const then = new Date(iso)
  if (Number.isNaN(then.getTime())) return 'Earlier'

  const startOfDay = (d: Date): number =>
    new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime()
  const days = Math.round((startOfDay(new Date()) - startOfDay(then)) / 86_400_000)

  if (days <= 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return 'This week'
  return then.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })
}

function clockTime(iso: string): string {
  const d = new Date(iso)
  return Number.isNaN(d.getTime())
    ? ''
    : d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}

function label(session: SessionSummary): string {
  return session.title || session.preview || 'Untitled conversation'
}

interface RowProps {
  session: SessionSummary
  active: boolean
  onOpen: () => void
  onRename: (title: string) => Promise<void>
  onAskDelete: () => Promise<DeletePreview | null>
  onDelete: () => Promise<void>
}

function Row({ session, active, onOpen, onRename, onAskDelete, onDelete }: RowProps): JSX.Element {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(label(session))
  const [pending, setPending] = useState<DeletePreview | null>(null)
  const [busy, setBusy] = useState(false)

  const commitRename = async (): Promise<void> => {
    const next = draft.trim()
    setEditing(false)
    if (next && next !== label(session)) await onRename(next)
  }

  if (editing) {
    return (
      <div className="rounded-md bg-white/5 px-2 py-2">
        <input
          autoFocus
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={() => void commitRename()}
          onKeyDown={(e) => {
            if (e.key === 'Enter') void commitRename()
            if (e.key === 'Escape') {
              setDraft(label(session))
              setEditing(false)
            }
          }}
          className="w-full rounded rim bg-aria-sunk px-2 py-1 text-tiny text-aria-text outline-none focus:rim-strong"
        />
      </div>
    )
  }

  if (pending) {
    return (
      <div className="rounded-md border border-aria-bad/40 bg-aria-bad/10 px-2 py-2">
        <p className="text-tiny text-aria-text">
          Delete “{pending.title}” and its {pending.message_count} messages?
        </p>
        <p className="mt-0.5 text-micro text-aria-muted">This cannot be undone.</p>
        <div className="mt-1.5 flex gap-1">
          <button
            type="button"
            disabled={busy}
            onClick={() => {
              setBusy(true)
              void onDelete().finally(() => {
                setBusy(false)
                setPending(null)
              })
            }}
            className="rounded border border-aria-bad/60 px-2 py-0.5 text-micro text-aria-bad hover:bg-aria-bad/20 disabled:opacity-50"
          >
            Delete
          </button>
          <button
            type="button"
            onClick={() => setPending(null)}
            className="rounded rim px-2 py-0.5 text-micro text-aria-muted hover:text-aria-text"
          >
            Keep
          </button>
        </div>
      </div>
    )
  }

  return (
    <div
      className={`group flex items-start gap-2 rounded-md px-2 py-1.5 hover:bg-white/5 ${
        active ? 'bg-white/10' : ''
      }`}
    >
      <button type="button" onClick={onOpen} className="min-w-0 flex-1 text-left">
        <span className="block truncate text-tiny text-aria-text">{label(session)}</span>
        <span className="mt-0.5 flex flex-wrap items-center gap-x-1.5 text-micro text-aria-faint">
          <span className="font-mono">{clockTime(session.last_activity)}</span>
          <span aria-hidden>·</span>
          <span>{session.message_count} messages</span>
          {/* A study chat is a different kind of conversation, not one with a
              setting on it, and the list you look through for "that thing I
              was learning" should say so. Not a filter — `chat.delete` looks a
              session up through this same list, so narrowing it would 404 its
              own delete. */}
          {session.kind === 'study' && (
            <span className="text-aria-accent" title="A study chat">
              · study
            </span>
          )}
          {active && <span className="text-aria-ok">· open</span>}
        </span>
      </button>
      <span className="flex shrink-0 gap-0.5 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
        <button
          type="button"
          aria-label="Rename"
          onClick={() => {
            setDraft(label(session))
            setEditing(true)
          }}
          className="rounded px-1.5 py-0.5 text-micro text-aria-muted hover:text-aria-text"
        >
          Rename
        </button>
        <button
          type="button"
          aria-label="Delete"
          onClick={() => void onAskDelete().then(setPending)}
          className="rounded px-1.5 py-0.5 text-micro text-aria-muted hover:text-aria-bad"
        >
          Delete
        </button>
      </span>
    </div>
  )
}

export function HistoryPanel({
  activeSessionId,
  onOpen,
  onClose,
  variant = 'overlay',
}: {
  activeSessionId: string | null
  onOpen: (id: string) => void
  onClose: () => void
  /** `rail` is the permanent column in the expanded window; `overlay` covers
   *  the compact one. One component either way — two implementations of the
   *  same list is how they drift apart. */
  variant?: 'overlay' | 'rail'
}): JSX.Element {
  const store = useSessions(true)
  const inputRef = useRef<HTMLInputElement>(null)
  const isRail = variant === 'rail'

  useEffect(() => {
    // The rail is always present, so stealing focus would fight the composer.
    if (!isRail) inputRef.current?.focus()
    if (isRail) return
    const onKey = (e: KeyboardEvent): void => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose, isRail])

  // Grouped in list order, which the sidecar already sorted by last activity.
  const groups: [string, SessionSummary[]][] = []
  for (const session of store.sessions) {
    const key = dayGroup(session.last_activity)
    const last = groups[groups.length - 1]
    if (last && last[0] === key) last[1].push(session)
    else groups.push([key, [session]])
  }

  // Same list either way — two implementations is how they drift apart. Only
  // the frame differs: a column docked to the rail, or a floating sheet.
  const body = (
    <>
      <input
        ref={inputRef}
        value={store.query}
        placeholder="Search what you said…"
        onChange={(e) => store.setQuery(e.target.value)}
        className="mt-3 w-full rounded-lg rim bg-aria-sunk px-2.5 py-1.5 text-tiny text-aria-text outline-none placeholder:text-aria-faint focus:rim-strong"
      />

      <div className="mt-2 flex-1 overflow-y-auto pr-0.5">
        {store.error && <p className="px-2 py-3 text-tiny text-aria-bad">{store.error}</p>}

        {!store.error && store.sessions.length === 0 && (
          <p className="px-2 py-6 text-center text-tiny text-aria-muted">
            {store.loading
              ? 'Loading…'
              : store.query
                ? `Nothing matches “${store.query}”.`
                : 'No conversations yet. Say something and it will appear here.'}
          </p>
        )}

        {groups.map(([day, items]) => (
          <div key={day} className="mb-2">
            <p className="px-2 pb-1 pt-1.5 text-micro uppercase tracking-wide text-aria-muted">
              {day}
            </p>
            {items.map((session) => (
              <Row
                key={session.id}
                session={session}
                active={session.id === activeSessionId}
                onOpen={() => onOpen(session.id)}
                onRename={(title) => store.rename(session.id, title)}
                onAskDelete={() => store.confirmDelete(session.id)}
                onDelete={() => store.remove(session.id)}
              />
            ))}
          </div>
        ))}
      </div>
    </>
  )

  if (isRail) {
    return (
      <div className="flex h-full flex-col p-3">
        <h2 className="px-0.5 text-small font-strong text-aria-text">Chats</h2>
        {body}
      </div>
    )
  }

  return (
    <Panel title="Chats" onClose={onClose} width="max-w-sm">
      {body}
    </Panel>
  )
}
