/** Text input. Enter sends, Shift+Enter newlines, Esc cancels a live turn. */

import { useEffect, useRef, useState, type KeyboardEvent } from 'react'

interface Props {
  busy: boolean
  disabled: boolean
  onSend: (text: string, attachments?: string[]) => void
  onCancel: () => void
  /** A file picked in the Files panel, to be attached here. One-shot:
   *  cleared through `onAttachConsumed` so the same path arriving twice
   *  is two deliberate attachments rather than one stuck prop. */
  attachPath?: string | null
  onAttachConsumed?: () => void
  /** Push-to-talk, when speech is available. Held, not toggled. */
  voice?: {
    listening: boolean
    transcribing: boolean
    start: () => void
    stop: () => void
  }
}

const MAX_ROWS = 6
const LINE_HEIGHT = 21

export function ComposerBar({
  busy,
  disabled,
  onSend,
  onCancel,
  voice,
  attachPath,
  onAttachConsumed,
}: Props): JSX.Element {
  const [value, setValue] = useState('')
  const [focused, setFocused] = useState(false)
  // Absolute paths, never file contents. The renderer has no filesystem
  // access by design (see `electron/preload.ts`) — Electron's own picker
  // hands back where the files are, and the sidecar opens them.
  const [attached, setAttached] = useState<string[]>([])
  const [dragging, setDragging] = useState(false)
  const textarea = useRef<HTMLTextAreaElement>(null)

  const addPaths = (paths: string[]): void => {
    if (paths.length === 0) return
    setAttached((current) => [...current, ...paths.filter((p) => !current.includes(p))])
  }

  // Files chosen in the panel land here rather than through the OS picker.
  useEffect(() => {
    if (!attachPath) return
    addPaths([attachPath])
    onAttachConsumed?.()
  }, [attachPath, onAttachConsumed])

  const pick = async (): Promise<void> => {
    try {
      addPaths(await window.aria.pickFiles())
    } catch {
      /* the picker was dismissed, or main is gone — neither is worth a dialog */
    }
  }

  // Focus on mount and whenever a turn finishes — typing should never require
  // a click, since the window is summoned by hotkey.
  useEffect(() => {
    if (!busy && !disabled) textarea.current?.focus()
  }, [busy, disabled])

  // Grow with content, up to a cap.
  useEffect(() => {
    const el = textarea.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, LINE_HEIGHT * MAX_ROWS)}px`
  }, [value])

  const submit = (): void => {
    // A message can be nothing but files. Dragging a PDF in and pressing
    // Enter is a complete request — "what is this?" is implied by the act.
    if (busy || disabled || (!value.trim() && attached.length === 0)) return
    onSend(value, attached)
    setValue('')
    setAttached([])
  }

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>): void => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      submit()
      return
    }
    if (event.key === 'Escape' && busy) {
      event.preventDefault()
      onCancel()
    }
  }

  const canSend = !disabled && (value.trim().length > 0 || attached.length > 0)

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragging(false)
        // Electron puts the real path on a dropped File. This is the one
        // place the renderer learns a path without going through the picker,
        // and it is still the user's own deliberate act.
        addPaths(
          Array.from(e.dataTransfer.files)
            .map((file) => (file as File & { path?: string }).path ?? '')
            .filter(Boolean),
        )
      }}
      className={`raised flex flex-col gap-1.5 rounded-2xl p-1.5 pl-3 transition-shadow ${
        dragging ? 'rim-strong' : focused ? 'rim-strong' : 'rim'
      }`}
    >
      {/* Named, and removable one at a time. A count alone ("3 files") is
          not enough to notice you attached the wrong thing before sending
          it to a cloud vision model. */}
      {attached.length > 0 && (
        <ul className="flex flex-wrap gap-1 pr-1 pt-0.5">
          {attached.map((path) => (
            <li
              key={path}
              className="flex max-w-full items-center gap-1 rounded-md bg-aria-sunk px-1.5 py-0.5 text-micro text-aria-muted"
            >
              <span className="truncate" title={path}>
                {path.split(/[\/]/).pop()}
              </span>
              <button
                type="button"
                aria-label={`Remove ${path.split(/[\/]/).pop()}`}
                onClick={() => setAttached((c) => c.filter((p) => p !== path))}
                className="interactive shrink-0 rounded text-aria-faint hover:text-aria-text"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="flex items-end gap-1.5">
        <textarea
          ref={textarea}
          rows={1}
          value={value}
          disabled={disabled}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={onKeyDown}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={
            disabled
              ? 'Waiting for the brain…'
              : voice?.listening
                ? 'Listening…'
                : voice?.transcribing
                  ? 'Transcribing…'
                  : 'Message Aria…'
          }
          className="flex-1 resize-none self-center bg-transparent py-1.5 text-small leading-[21px] text-aria-text placeholder:text-aria-faint focus:outline-none disabled:opacity-50"
        />

        {/* Paperclip. Disabled while a turn runs, for the same reason Send
          becomes Stop: attaching to a message that is already gone does
          nothing anyone expects. */}
        <button
          type="button"
          aria-label="Attach files"
          title="Attach files"
          disabled={disabled || busy}
          onClick={() => void pick()}
          className="interactive grid h-8 w-8 shrink-0 place-items-center rounded-xl text-aria-faint transition-colors hover:text-aria-text disabled:cursor-not-allowed disabled:opacity-30"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.4"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden
          >
            <path d="M11.4 6.6 6.9 11a2.7 2.7 0 0 1-3.8-3.8l4.6-4.6a1.8 1.8 0 0 1 2.6 2.6L5.6 9.8a.9.9 0 0 1-1.3-1.3l4.2-4.2" />
          </svg>
        </button>

        {/* Held, not toggled — press and hold, exactly like the keyboard path.
          `pointerleave` matters: dragging off the button while held would
          otherwise leave the microphone open with nothing listening for the
          release. */}
        {voice && !busy && (
          <button
            type="button"
            aria-label="Hold to talk"
            title="Hold to talk (Ctrl+Shift+Space)"
            disabled={disabled}
            onPointerDown={voice.start}
            onPointerUp={voice.stop}
            onPointerLeave={() => voice.listening && voice.stop()}
            className={`interactive grid h-8 w-8 shrink-0 place-items-center rounded-xl transition-colors disabled:cursor-not-allowed disabled:opacity-30 ${
              voice.listening
                ? 'bg-aria-listening/20 text-aria-listening'
                : voice.transcribing
                  ? 'text-aria-accent'
                  : 'text-aria-faint hover:text-aria-text'
            }`}
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 14 14"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.4"
              strokeLinecap="round"
              aria-hidden
            >
              <rect x="5" y="1.6" width="4" height="7" rx="2" />
              <path d="M2.8 6.6a4.2 4.2 0 0 0 8.4 0M7 10.8v1.6" />
            </svg>
          </button>
        )}

        {/* One control in one place. A separate Stop button appearing beside Send
          moves the target mid-turn, exactly when you are reaching for it. */}
        <button
          type="button"
          aria-label={busy ? 'Stop generating' : 'Send'}
          title={busy ? 'Stop generating (Esc)' : 'Send (Enter)'}
          onClick={busy ? onCancel : submit}
          disabled={!busy && !canSend}
          className={`interactive grid h-8 w-8 shrink-0 place-items-center rounded-xl transition-colors ${
            busy
              ? 'bg-white/10 text-aria-text'
              : canSend
                ? 'bg-aria-accent/90 text-aria-void hover:bg-aria-accent'
                : 'text-aria-faint'
          } disabled:cursor-not-allowed`}
        >
          {busy ? (
            <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden>
              <rect x="2.5" y="2.5" width="7" height="7" rx="1.4" fill="currentColor" />
            </svg>
          ) : (
            <svg
              width="14"
              height="14"
              viewBox="0 0 14 14"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.7"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden
            >
              <path d="M7 11.5v-9M3.2 6.3 7 2.5l3.8 3.8" />
            </svg>
          )}
        </button>
      </div>
    </div>
  )
}
