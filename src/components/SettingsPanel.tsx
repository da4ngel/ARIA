/**
 * API key management.
 *
 * Keys live in Windows Credential Manager (BUILD_SPEC §11). The sidecar returns
 * presence and the last four characters only — a key value never travels back
 * over the bridge, so this panel can show which key is stored without ever
 * being able to display it.
 */

import { useCallback, useEffect, useState } from 'react'

import type { PermissionMode } from '@/hooks/usePermissionMode'
import { MODE_COPY, MODE_OPTIONS } from '@/hooks/usePermissionMode'

import { Panel } from '@/components/Panel'
import type { CredentialStatus } from '@/types/bridge'

const KEY_LABEL: Record<string, string> = {
  openai_api_key: 'OpenAI',
  gemini_api_key: 'Gemini',
  brave_api_key: 'Brave Search',
  tavily_api_key: 'Tavily',
}

const KEY_HELP: Record<string, string> = {
  openai_api_key: 'platform.openai.com → API keys',
  gemini_api_key: 'aistudio.google.com/apikey',
  brave_api_key: 'brave.com/search/api — free tier',
  tavily_api_key: 'tavily.com — free tier, built for this',
}

/** Which keys are for reaching the web rather than for answering. */
const SEARCH_KEYS = new Set(['brave_api_key', 'tavily_api_key'])

interface OnlineState {
  enabled: boolean
  backend: string | null
  key_present: boolean
}

interface BrowserState {
  cdp_reachable: boolean
  launcher_path: string
  launcher_exists: boolean
  detected_browser: string | null
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
  mode,
  setMode,
}: {
  onClose: () => void
  onKeysChanged: () => void
  mode: PermissionMode
  setMode: (next: PermissionMode) => Promise<void>
}): JSX.Element {
  const [keys, setKeys] = useState<CredentialStatus[]>([])
  const [online, setOnline] = useState<OnlineState | null>(null)
  const [browser, setBrowser] = useState<BrowserState | null>(null)
  const [browserBusy, setBrowserBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const result = await window.aria.call<{ keys: CredentialStatus[] }>('settings.keys', {})
      setKeys(result.keys)
      setOnline(await window.aria.call<OnlineState>('settings.online', {}))
      setBrowser(await window.aria.call<BrowserState>('browser.setup', {}))
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    }
  }, [])

  const writeLauncher = useCallback(async () => {
    setBrowserBusy(true)
    try {
      setBrowser(await window.aria.call<BrowserState>('browser.setup', { write: true }))
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    } finally {
      setBrowserBusy(false)
    }
  }, [])

  const checkBrowser = useCallback(async () => {
    setBrowserBusy(true)
    try {
      setBrowser(await window.aria.call<BrowserState>('browser.setup', {}))
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    } finally {
      setBrowserBusy(false)
    }
  }, [])

  const toggleOnline = useCallback(async () => {
    if (!online) return
    // Optimistic, then reconciled: the reply also carries whether a search key
    // exists, which is the difference between "on" and "working".
    setOnline({ ...online, enabled: !online.enabled })
    try {
      setOnline(await window.aria.call<OnlineState>('settings.online', { enabled: !online.enabled }))
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
      await load()
    }
  }, [online, load])

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
    <Panel title="Settings" onClose={onClose}>
      {/* Permission mode leads, because it governs every other switch here.
          It is also mirrored in the Tools panel — deliberately, not by
          accident: it shipped there and only there, which meant the only way
          to see which mode you were in was to go looking for a wrench icon.
          In Full access nothing ever prompts, so the state with the largest
          consequences was the one with no evidence on screen at all. */}
      <div className="mb-4">
        <h3 className="text-tiny font-strong text-aria-text">Permission mode</h3>
        <div className="mt-1.5 flex gap-1 rounded-xl bg-aria-sunk p-1">
          {MODE_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              aria-pressed={mode === option.value}
              onClick={() => void setMode(option.value)}
              className={`interactive flex-1 rounded-lg px-2 py-1.5 text-tiny ${
                mode === option.value
                  ? option.value === 'full_access'
                    ? 'bg-aria-bad/90 text-white'
                    : 'bg-aria-accent/90 text-white'
                  : 'text-aria-muted'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
        <p
          className={`mt-1.5 text-micro leading-relaxed ${
            mode === 'full_access' ? 'text-aria-bad' : 'text-aria-faint'
          }`}
        >
          {MODE_COPY[mode]}
        </p>
      </div>

      {/* Online mode next, because it is the only other switch here that
          changes what she can do rather than which model answers. */}
      {online && (
        <button
          type="button"
          role="switch"
          aria-checked={online.enabled}
          aria-label="Online mode"
          onClick={() => void toggleOnline()}
          className={`rim interactive mb-4 flex w-full items-center justify-between gap-3 rounded-xl px-3 py-2.5 text-left ${
            online.enabled ? 'bg-aria-accent/10' : 'raised'
          }`}
        >
          <span className="min-w-0">
            <span
              className={`block text-small font-medium ${
                online.enabled ? 'text-aria-accent' : 'text-aria-text'
              }`}
            >
              {online.enabled ? 'Online mode is on' : 'Online mode is off'}
            </span>
            <span className="mt-0.5 block text-micro text-aria-muted">
              {/* On with no key is the one state a single label cannot
                  describe, and the one a user would otherwise debug by asking
                  her a question and reading the refusal. */}
              {!online.enabled
                ? 'She cannot reach the web. Nothing you say leaves this machine.'
                : online.key_present
                  ? `She can search the web and read pages. Using ${online.backend}.`
                  : 'Add a Tavily or Brave key below — the switch alone cannot search.'}
            </span>
          </span>
          <span
            aria-hidden
            className={`relative h-5 w-9 shrink-0 rounded-full transition-colors ${
              online.enabled ? 'bg-aria-accent/50' : 'bg-white/10'
            }`}
          >
            <span
              className={`absolute top-0.5 h-4 w-4 rounded-full bg-aria-text transition-all ${
                online.enabled ? 'left-[1.125rem]' : 'left-0.5'
              }`}
            />
          </span>
        </button>
      )}

      {/* browser_click/browser_fill/etc. connect to a browser that is
          already running with remote debugging on — they never launch one.
          Without this, the only sign anything is wrong is a raw ECONNREFUSED
          inside a tool card, which is what prompted adding this section. */}
      {browser && (
        <div
          className={`rim mb-4 rounded-xl px-3 py-2.5 ${
            browser.cdp_reachable ? 'bg-aria-accent/10' : 'raised'
          }`}
        >
          <span
            className={`block text-small font-medium ${
              browser.cdp_reachable ? 'text-aria-accent' : 'text-aria-text'
            }`}
          >
            {browser.cdp_reachable ? 'Browser control is connected' : 'Browser control is off'}
          </span>
          <p className="mt-0.5 text-micro text-aria-muted">
            {browser.cdp_reachable ? (
              'She can navigate, read, click and fill in your browser.'
            ) : browser.launcher_exists ? (
              <>
                Run <code className="text-aria-text">{browser.launcher_path}</code>, then check
                again.
              </>
            ) : (
              <>
                Needs {browser.detected_browser ?? 'your browser'} started with remote debugging
                on — write a launcher for it below.
              </>
            )}
          </p>
          <div className="mt-2 flex gap-2">
            {!browser.launcher_exists && (
              <button
                type="button"
                disabled={browserBusy}
                onClick={() => void writeLauncher()}
                className="rounded rim px-2 py-1 text-micro text-aria-muted hover:text-aria-text disabled:opacity-40"
              >
                Write launcher
              </button>
            )}
            <button
              type="button"
              disabled={browserBusy}
              onClick={() => void checkBrowser()}
              className="rounded rim px-2 py-1 text-micro text-aria-muted hover:text-aria-text disabled:opacity-40"
            >
              Check again
            </button>
          </div>
        </div>
      )}

      <p className="mb-1 text-micro uppercase tracking-wide text-aria-faint">Models</p>
      <div>
        {keys
          .filter((status) => !SEARCH_KEYS.has(status.key))
          .map((status) => (
            <KeyRow key={status.key} status={status} onSave={save} />
          ))}
      </div>

      <p className="mb-1 mt-4 text-micro uppercase tracking-wide text-aria-faint">
        Web search — either one is enough
      </p>
      <div>
        {keys
          .filter((status) => SEARCH_KEYS.has(status.key))
          .map((status) => (
            <KeyRow key={status.key} status={status} onSave={save} />
          ))}
      </div>

      {error && <p className="mt-2 text-tiny text-aria-bad">{error}</p>}

      <p className="mt-4 text-micro leading-relaxed text-aria-muted">
        Stored in Windows Credential Manager, never in the repo or a .env file. Only the last four
        characters are ever shown. Rotate a key at the address above, then Replace it here.
      </p>
    </Panel>
  )
}
