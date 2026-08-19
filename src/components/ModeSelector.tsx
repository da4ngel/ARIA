/**
 * Picking how she answers this conversation.
 *
 * Sits in the composer rather than the header, deliberately: it belongs to
 * the message you are about to send, and the header is already carrying four
 * controls in a 420px window. Same popover recipe as `ModelPicker` — click
 * away or Escape to close, `glass-pop` sheet, `animate-rise`.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import type { ConversationMode } from '@/hooks/useConversationMode'
import { MODE_OPTIONS } from '@/hooks/useConversationMode'

export function ModeSelector({
  mode,
  label,
  needsOnline,
  disabled,
  suggestion,
  onSelect,
  onEnableOnline,
  onDismissSuggestion,
}: {
  mode: ConversationMode
  label: string
  /** Research chosen while online mode is off. */
  needsOnline: boolean
  disabled: boolean
  /** A mode this turn would suit better. **An offer, never applied** — modes
   *  reset to Normal per conversation precisely so one cannot silently shape
   *  an answer, and a mode ARIA switched to itself is that same invisible
   *  shaping arriving faster. */
  suggestion: { mode: ConversationMode; label: string } | null
  onSelect: (next: ConversationMode) => void
  onEnableOnline: () => void
  onDismissSuggestion: () => void
}): JSX.Element {
  const [open, setOpen] = useState(false)
  const root = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const away = (event: MouseEvent): void => {
      if (!root.current?.contains(event.target as Node)) setOpen(false)
    }
    const escape = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', away)
    document.addEventListener('keydown', escape)
    return () => {
      document.removeEventListener('mousedown', away)
      document.removeEventListener('keydown', escape)
    }
  }, [open])

  const choose = useCallback(
    (next: ConversationMode) => {
      setOpen(false)
      onSelect(next)
    },
    [onSelect],
  )

  return (
    <div ref={root} className="relative">
      <button
        type="button"
        disabled={disabled}
        aria-label={`Answer mode: ${label}`}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className={`interactive flex items-center gap-1 rounded-lg px-1.5 py-0.5 text-micro disabled:cursor-not-allowed disabled:opacity-40 ${
          mode === 'normal' ? 'text-aria-faint' : 'text-aria-muted'
        }`}
      >
        {/* A dot only when a mode is actually on. Normal is the absence of a
            mode, and marking it would make the default look like a setting. */}
        {mode !== 'normal' && (
          <span className="h-1 w-1 shrink-0 rounded-full bg-current" aria-hidden />
        )}
        {label}
        <span aria-hidden>▾</span>
      </button>

      {open && (
        <div className="glass-pop absolute bottom-full left-0 z-20 mb-1.5 w-64 overflow-hidden rounded-xl p-1.5 animate-rise">
          {MODE_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => choose(option.value)}
              className={`interactive block w-full rounded-lg px-2 py-1.5 text-left ${
                option.value === mode ? 'bg-white/10' : ''
              }`}
            >
              <span className="block text-tiny text-aria-text">{option.label}</span>
              <span className="block text-micro leading-relaxed text-aria-faint">
                {option.hint}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* "On" is not the same as "working" — the same distinction
          `settings.online` already draws. Research with the web switched off
          would otherwise behave like Normal and leave her to explain why in a
          refusal, which is how the user ends up debugging by asking. */}
      {/* One offer at a time, and the online warning outranks it: a mode that
          cannot work yet is a more urgent thing to say than a mode that might
          suit better. */}
      {suggestion && !needsOnline && !open && (
        <div className="absolute bottom-full left-0 mb-1 flex items-center gap-1 whitespace-nowrap rounded-md bg-aria-sunk px-1.5 py-0.5 text-micro">
          <button
            type="button"
            onClick={() => {
              onDismissSuggestion()
              choose(suggestion.mode)
            }}
            className="interactive text-aria-accent"
          >
            Switch to {suggestion.label}?
          </button>
          <button
            type="button"
            aria-label="Dismiss mode suggestion"
            onClick={onDismissSuggestion}
            className="interactive text-aria-faint hover:text-aria-muted"
          >
            ✕
          </button>
        </div>
      )}

      {needsOnline && !open && (
        <button
          type="button"
          onClick={onEnableOnline}
          className="interactive absolute bottom-full left-0 mb-1 whitespace-nowrap rounded-md bg-aria-sunk px-1.5 py-0.5 text-micro text-aria-warn"
        >
          Research needs online mode — turn it on
        </button>
      )}
    </div>
  )
}
