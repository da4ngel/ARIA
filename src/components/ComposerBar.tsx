/** Text input. Enter sends, Shift+Enter newlines, Esc cancels a live turn. */

import { useEffect, useRef, useState, type KeyboardEvent } from 'react'

interface Props {
  busy: boolean
  disabled: boolean
  onSend: (text: string) => void
  onCancel: () => void
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

export function ComposerBar({ busy, disabled, onSend, onCancel, voice }: Props): JSX.Element {
  const [value, setValue] = useState('')
  const [focused, setFocused] = useState(false)
  const textarea = useRef<HTMLTextAreaElement>(null)

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
    if (busy || disabled || !value.trim()) return
    onSend(value)
    setValue('')
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

  const canSend = !disabled && value.trim().length > 0

  return (
    <div
      className={`raised flex items-end gap-1.5 rounded-2xl p-1.5 pl-3 transition-shadow ${
        focused ? 'rim-strong' : 'rim'
      }`}
    >
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
  )
}
