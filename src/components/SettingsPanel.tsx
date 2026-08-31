/**
 * API key management.
 *
 * Keys live in Windows Credential Manager (BUILD_SPEC §11). The sidecar returns
 * presence and the last four characters only — a key value never travels back
 * over the bridge, so this panel can show which key is stored without ever
 * being able to display it.
 */

import { useCallback, useEffect, useState } from 'react'

import { useUpdates } from '@/hooks/useUpdates'

import type { PermissionMode } from '@/hooks/usePermissionMode'
import { MODE_COPY, MODE_OPTIONS } from '@/hooks/usePermissionMode'

import { Panel } from '@/components/Panel'
import type { CredentialStatus, UpdateStatus } from '@/types/bridge'

const KEY_LABEL: Record<string, string> = {
  openai_api_key: 'OpenAI',
  gemini_api_key: 'Gemini',
  openrouter_api_key: 'OpenRouter',
  bedrock_api_key: 'Amazon Bedrock',
  aws_access_key_id: 'AWS access key ID',
  aws_secret_access_key: 'AWS secret access key',
  aws_session_token: 'AWS session token',
  imap_host: 'Mail server',
  imap_user: 'Mail address',
  imap_password: 'Mail app password',
  brave_api_key: 'Brave Search',
  tavily_api_key: 'Tavily',
}

const KEY_HELP: Record<string, string> = {
  openai_api_key: 'platform.openai.com → API keys',
  gemini_api_key: 'aistudio.google.com/apikey',
  openrouter_api_key: 'openrouter.ai/keys — free models, 50 requests a day',
  bedrock_api_key: 'console.aws.amazon.com/bedrock → API keys. This alone is enough.',
  aws_access_key_id: 'Only if you have no Bedrock API key — an IAM key, signed instead.',
  aws_secret_access_key: 'The secret half of the access key above. Both or neither.',
  aws_session_token: 'Temporary credentials only. Leave empty for a normal IAM key.',
  imap_host: "'gmail', 'outlook', or your own IMAP server's hostname",
  imap_user: 'The address to sign in with',
  imap_password: 'An APP password, not your account password. Read-only; she cannot send.',
  brave_api_key: 'brave.com/search/api — free tier',
  tavily_api_key: 'tavily.com — free tier, built for this',
}

// Where Bedrock offers text models today. Not exhaustive on purpose — a
// complete list is thirty entries of noise, and these are the regions with
// the widest model selection. `models.bedrock` accepts any string, so
// nothing here limits what the sidecar can be pointed at.
const BEDROCK_REGIONS = [
  'us-east-1',
  'us-east-2',
  'us-west-2',
  'eu-west-1',
  'eu-west-2',
  'eu-central-1',
  'ap-south-1',
  'ap-southeast-1',
  'ap-southeast-2',
  'ap-northeast-1',
]

/** Which keys are for reaching the web rather than for answering. */
const SEARCH_KEYS = new Set(['brave_api_key', 'tavily_api_key'])

interface OnlineState {
  enabled: boolean
  backend: string | null
  key_present: boolean
}

/** `models.bedrock` — the region, and which credential shape is stored. */
interface BedrockState {
  region: string
  credential: 'api_key' | 'sigv4' | 'none'
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

/** One line per state, so the card never shows two things at once. */
function updateLine(status: UpdateStatus | null): string {
  if (!status) return 'Reading the current version…'
  switch (status.state) {
    case 'checking':
      return 'Looking for a newer version…'
    case 'available':
      return `Version ${status.next} found. Downloading it now.`
    case 'downloading':
      return `Downloading version ${status.next ?? ''} — ${status.percent ?? 0}%`
    case 'ready':
      return `Version ${status.next} is ready. It installs when you next quit, or restart now.`
    case 'none':
      return 'Up to date.'
    case 'error':
      // Named rather than hidden: "no network" and "the release is broken"
      // are different problems and only the message tells them apart.
      return status.message ?? 'The check did not complete.'
    default:
      return 'Checked automatically, and whenever you ask.'
  }
}

export function SettingsPanel({
  onClose,
  onKeysChanged,
  mode,
  setMode,
  onReopenSetup,
}: {
  onClose: () => void
  onKeysChanged: () => void
  mode: PermissionMode
  setMode: (next: PermissionMode) => Promise<void>
  /** Reopen the first-run wizard. It is the only place that offers the
   *  model pull and the weight downloads, so it has to be reachable after
   *  somebody has clicked past it once. */
  onReopenSetup: () => void
}): JSX.Element {
  const [keys, setKeys] = useState<CredentialStatus[]>([])
  const [online, setOnline] = useState<OnlineState | null>(null)
  const [browser, setBrowser] = useState<BrowserState | null>(null)
  const [bedrock, setBedrock] = useState<BedrockState | null>(null)
  const [browserBusy, setBrowserBusy] = useState(false)
  // **Read from the OS, never stored.** Auto-start lives in the registry's
  // Run key; a copy kept here would still read as on after somebody turned
  // it off in Task Manager. `null` until the first read answers.
  const [autoStart, setAutoStart] = useState<boolean | null>(null)
  const updates = useUpdates()
  const [diagnostics, setDiagnostics] = useState<string | null>(null)
  const [diagnosticsBusy, setDiagnosticsBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const result = await window.aria.call<{ keys: CredentialStatus[] }>('settings.keys', {})
      setKeys(result.keys)
      setOnline(await window.aria.call<OnlineState>('settings.online', {}))
      setBrowser(await window.aria.call<BrowserState>('browser.setup', {}))
      setBedrock(await window.aria.call<BedrockState>('models.bedrock', {}))
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    }
  }, [])

  const setRegion = useCallback(async (region: string) => {
    try {
      // The reply is authoritative: the sidecar normalises and stores it,
      // and re-lists the models, because which models exist is a property
      // of the region.
      setBedrock(await window.aria.call<BedrockState>('models.bedrock', { region }))
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

  useEffect(() => {
    void window.aria.getAutoStart().then(setAutoStart)
  }, [])

  const toggleAutoStart = useCallback(async () => {
    if (autoStart === null) return
    // Take what the OS reports back rather than what was asked for: the write
    // can fail (a policy, a locked registry) and a switch that shows the
    // request instead of the result is a switch that lies.
    setAutoStart(await window.aria.setAutoStart(!autoStart))
  }, [autoStart])

  const exportDiagnostics = useCallback(async () => {
    setDiagnosticsBusy(true)
    try {
      // Naming the file is the whole point: an export whose location you have
      // to go hunting for is one nobody attaches to the bug report.
      setDiagnostics(await window.aria.exportDiagnostics())
    } finally {
      setDiagnosticsBusy(false)
    }
  }, [])

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

      {/* Start with Windows. Off by default — an assistant that installs
          itself into your login without asking is one people uninstall. */}
      {autoStart !== null && (
        <button
          type="button"
          role="switch"
          aria-checked={autoStart}
          aria-label="Start with Windows"
          onClick={() => void toggleAutoStart()}
          className={`rim interactive mb-4 flex w-full items-center justify-between gap-3 rounded-xl px-3 py-2.5 text-left ${
            autoStart ? 'bg-aria-accent/10' : 'raised'
          }`}
        >
          <span className="min-w-0">
            <span
              className={`block text-small font-medium ${
                autoStart ? 'text-aria-accent' : 'text-aria-text'
              }`}
            >
              Start with Windows
            </span>
            <span className="mt-0.5 block text-micro text-aria-muted">
              {autoStart
                ? 'She starts in the tray at login. No window until you ask for one.'
                : 'She only runs when you open her.'}
            </span>
          </span>
          <span
            aria-hidden
            className={`relative h-5 w-9 shrink-0 rounded-full transition-colors ${
              autoStart ? 'bg-aria-accent/50' : 'bg-white/10'
            }`}
          >
            <span
              className={`absolute top-0.5 h-4 w-4 rounded-full bg-aria-text transition-all ${
                autoStart ? 'left-[1.125rem]' : 'left-0.5'
              }`}
            />
          </span>
        </button>
      )}

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
                ? 'She cannot reach the web. Nothing you say leaves this machine — though ARIA still checks GitHub for its own updates.'
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

      {/* **Only once a Bedrock credential exists.** For everyone else this is
          a region selector for a provider they do not use, and Settings is
          already long. But for someone whose key was issued outside us-east-1
          it is the difference between "every Bedrock model is greyed out" and
          a working provider — the region is in the hostname, and a key is
          refused outside the region that issued it. */}
      {bedrock && bedrock.credential !== 'none' && (
        <div className="rim raised mb-4 rounded-xl px-3 py-2.5">
          <span className="block text-small font-medium text-aria-text">Amazon Bedrock</span>
          <p className="mt-0.5 text-micro text-aria-muted">
            Using {bedrock.credential === 'api_key' ? 'a Bedrock API key' : 'an AWS access key'}.
            Models differ by region, and a key is refused outside the region that issued it.
          </p>
          <label className="mt-2 flex items-center gap-2 text-micro text-aria-dim">
            Region
            <select
              value={bedrock.region}
              onChange={(event) => void setRegion(event.target.value)}
              className="rim interactive rounded-lg bg-aria-sunk px-2 py-1 text-micro text-aria-text"
            >
              {BEDROCK_REGIONS.map((region) => (
                <option key={region} value={region}>
                  {region}
                </option>
              ))}
            </select>
          </label>
        </div>
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

      {/* Said plainly, and it stops at what can honestly be claimed. The
          account-level opt-out and Zero Data Retention are real, and they are
          Eyaas's to set — implying ARIA has done it for him would be worse
          than saying nothing. */}
      <p className="mt-2 text-micro leading-relaxed text-aria-muted">
        OpenRouter's free models may route to providers that train on what you send. Attachments
        are never routed to them, and a free model only enters Smart mode after passing the same
        honesty probes every other model here was measured on. Your training and retention
        settings live in your OpenRouter account, not here.
      </p>

      {error && <p className="mt-2 text-tiny text-aria-bad">{error}</p>}

      {/* Updates, above Setup: it is the one card here whose state changes on
          its own, and the running version is the first thing anybody looks
          for when something is behaving oddly. */}
      <div className="rim raised mt-4 rounded-xl px-3 py-2.5">
        <div className="flex items-baseline justify-between gap-2">
          <span className="text-small font-medium text-aria-text">Updates</span>
          <span className="text-micro text-aria-faint">
            {updates.status ? `v${updates.status.current}` : ''}
          </span>
        </div>
        <p className="mt-0.5 text-micro text-aria-muted">{updateLine(updates.status)}</p>
        <div className="mt-2 flex gap-2">
          <button
            type="button"
            disabled={updates.busy || updates.status?.state === 'downloading'}
            onClick={() => void updates.check()}
            className="rounded rim px-2 py-1 text-micro text-aria-muted hover:text-aria-text disabled:opacity-40"
          >
            {updates.busy ? 'Checking…' : 'Check for updates'}
          </button>
          {/* Only ever an offer. Quitting normally installs it anyway, so
              nobody has to click this to end up updated. */}
          {updates.status?.state === 'ready' && (
            <button
              type="button"
              onClick={() => void updates.install()}
              className="interactive rounded bg-aria-accent/90 px-2 py-1 text-micro text-white"
            >
              Restart now
            </button>
          )}
        </div>
      </div>

      {/* The wizard is the only place that offers the model pull and the
          weight downloads, and it is dismissible — so without this it would
          be reachable exactly once per install. */}
      <div className="rim raised mt-4 rounded-xl px-3 py-2.5">
        <span className="block text-small font-medium text-aria-text">Setup</span>
        <p className="mt-0.5 text-micro text-aria-muted">
          What this machine has, and the downloads for what it does not — a local model, her
          voice, the wake word.
        </p>
        <button
          type="button"
          onClick={() => {
            onReopenSetup()
            onClose()
          }}
          className="mt-2 rounded rim px-2 py-1 text-micro text-aria-muted hover:text-aria-text"
        >
          Open setup
        </button>
      </div>

      {/* Last, because it is the thing you reach for when something else on
          this page has already gone wrong. Also in the tray, for when the
          window itself is the thing that is not working. */}
      <div className="rim raised mt-4 rounded-xl px-3 py-2.5">
        <span className="block text-small font-medium text-aria-text">Diagnostics</span>
        <p className="mt-0.5 text-micro text-aria-muted">
          A zip with the logs, health and versions — no API key values, no conversation.
        </p>
        <button
          type="button"
          disabled={diagnosticsBusy}
          onClick={() => void exportDiagnostics()}
          className="mt-2 rounded rim px-2 py-1 text-micro text-aria-muted hover:text-aria-text disabled:opacity-40"
        >
          {diagnosticsBusy ? 'Exporting…' : 'Export diagnostics'}
        </button>
        {diagnostics && (
          <p className="mt-1.5 break-all text-micro text-aria-dim">Written to {diagnostics}</p>
        )}
      </div>

      <p className="mt-4 text-micro leading-relaxed text-aria-muted">
        Stored in Windows Credential Manager, never in the repo or a .env file. Only the last four
        characters are ever shown. Rotate a key at the address above, then Replace it here.
      </p>
    </Panel>
  )
}
