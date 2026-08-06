/**
 * API key management.
 *
 * Keys live in Windows Credential Manager (BUILD_SPEC §11). The sidecar returns
 * presence and the last four characters only — a key value never travels back
 * over the bridge, so this panel can show which key is stored without ever
 * being able to display it.
 */

import { useCallback, useEffect, useState } from 'react'

import type { CredentialStatus } from '@/types/bridge'

const KEY_LABEL: Record<string, string> = {
  openai_api_key: 'OpenAI',
  gemini_api_key: 'Gemini',
}

const KEY_HELP: Record<string, string> = {
  openai_api_key: 'platform.openai.com → API keys',
  gemini_api_key: 'aistudio.google.com/apikey',
}

interface RowProps {
  status: CredentialStatus
  onSave: (key: string, value: string | null) => Promise<void>
}

function KeyRow({ status, onSave }: RowProps): JSX.Element {
  const [editing, setEditing] = useState(false)
  const [value, setValue] = useState('')
  const [busy, setBusy] = useState(false)

  const commit = async (next: string | null): Promise<void> => {
    setBusy(true)
    try {
      await onSave(status.key, next)
      setEditing(false)
      setValue('')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="border-b border-white/5 py-2 last:border-0">
      <div className="flex items-center justify-between gap-2">
        <span className="flex items-center gap-2 text-tiny">
          <span
            className={`h-1.5 w-1.5 rounded-full ${status.present ? 'bg-aria-ok' : 'bg-aria-muted'}`}
            aria-hidden
          />
          <span className="text-aria-text">{KEY_LABEL[status.key] ?? status.key}</span>
          <span className="text-aria-muted">{status.present ? status.hint : 'not set'}</span>
        </span>
        <span className="flex gap-1">
          <button
            type="button"
            onClick={() => setEditing(!editing)}
            className="rounded px-1.5 py-0.5 text-micro text-aria-muted hover:text-aria-text"
          >
            {status.present ? 'Replace' : 'Add'}
          </button>
          {status.present && (
            <button
              type="button"
              disabled={busy}
              onClick={() => void commit(null)}
              className="rounded px-1.5 py-0.5 text-micro text-aria-muted hover:text-aria-bad"
            >
              Clear
            </button>
          )}
        </span>
      </div>

      {editing && (
        <div className="mt-1.5 flex gap-1">
          <input
            type="password"
            autoFocus
            value={value}
            spellCheck={false}
            placeholder={KEY_HELP[status.key]}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && value.trim()) void commit(value.trim())
              if (event.key === 'Escape') setEditing(false)
            }}
            className="min-w-0 flex-1 rounded rim bg-aria-sunk px-2 py-1 text-tiny text-aria-text outline-none placeholder:text-aria-faint focus:rim-strong"
          />
          <button
            type="button"
            disabled={busy || !value.trim()}
            onClick={() => void commit(value.trim())}
            className="rounded rim px-2 py-1 text-micro text-aria-muted hover:text-aria-text disabled:opacity-40"
          >
            Save
          </button>
        </div>
      )}
    </div>
  )
}

export function SettingsPanel({
  onClose,
  onKeysChanged,
}: {
  onClose: () => void
  onKeysChanged: () => void
}): JSX.Element {
  const [keys, setKeys] = useState<CredentialStatus[]>([])
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const result = await window.aria.call<{ keys: CredentialStatus[] }>('settings.keys', {})
      setKeys(result.keys)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const save = useCallback(
    async (key: string, value: string | null) => {
      setError(null)
      try {
        await window.aria.call('settings.set_key', { key, value })
        await load()
        onKeysChanged() // a new key changes which models the picker offers
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause))
      }
    },
    [load, onKeysChanged],
  )

  return (
    <div className="absolute inset-0 z-30 flex flex-col bg-aria-void/85 p-4 backdrop-blur-md animate-rise">
      <div className="flex items-center justify-between">
        <h2 className="text-small font-semibold text-aria-text">API keys</h2>
        <button
          type="button"
          onClick={onClose}
          className="interactive rounded px-2 py-0.5 text-tiny text-aria-muted hover:text-aria-text"
        >
          Close
        </button>
      </div>

      <div className="mt-3">
        {keys.map((status) => (
          <KeyRow key={status.key} status={status} onSave={save} />
        ))}
      </div>

      {error && <p className="mt-2 text-tiny text-aria-bad">{error}</p>}

      <p className="mt-auto text-micro leading-relaxed text-aria-muted">
        Stored in Windows Credential Manager, never in the repo or a .env file. Only the last four
        characters are ever shown. Rotate a key at the address above, then Replace it here.
      </p>
    </div>
  )
}
