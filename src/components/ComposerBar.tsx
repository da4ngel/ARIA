/** Text input. Enter sends, Shift+Enter newlines, Esc cancels a live turn. */

import { useEffect, useRef, useState, type KeyboardEvent } from 'react'

interface Props {
  busy: boolean
  disabled: boolean
  onSend: (text: string) => void
  onCancel: () => void
}

const MAX_ROWS = 5

export function ComposerBar({ busy, disabled, onSend, onCancel }: Props): JSX.Element {
  const [value, setValue] = useState('')
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
    const lineHeight = 20
    el.style.height = `${Math.min(el.scrollHeight, lineHeight * MAX_ROWS)}px`
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

  return (
    <div
      className="flex items-end gap-2 rounded-xl border border-aria-edge bg-aria-panel p-2"
      style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
    >
      <textarea
        ref={textarea}
        rows={1}
        value={value}
        disabled={disabled}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder={disabled ? 'Waiting for the brain…' : 'Message Aria…'}
        className="flex-1 resize-none bg-transparent text-sm text-aria-text placeholder:text-aria-muted focus:outline-none disabled:opacity-50"
      />
      {busy ? (
        <button
          type="button"
          onClick={onCancel}
          title="Stop generating (Esc)"
          className="rounded-lg border border-aria-edge px-2.5 py-1 text-xs text-aria-muted hover:text-aria-text"
        >
          Stop
        </button>
      ) : (
        <button
          type="button"
          onClick={submit}
          disabled={disabled || !value.trim()}
          className="rounded-lg border border-aria-edge px-2.5 py-1 text-xs text-aria-muted hover:text-aria-text disabled:opacity-30"
        >
          Send
        </button>
      )}
    </div>
  )
}
