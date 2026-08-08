/**
 * What she can do, and where she may do it without asking.
 *
 * The trusted-folder list existed in the sidecar (`tools.trusted`) with no way
 * to reach it, so the feature shipped unusable. This is that control.
 *
 * Trust is a large thing to hand over — inside a trusted folder she writes,
 * moves and deletes with no confirmation, recursively — so the panel says so
 * plainly rather than presenting it as a convenience toggle.
 */

import { useCallback, useEffect, useState } from 'react'

import { Panel } from '@/components/Panel'

interface ToolSummary {
  name: string
  tier: number
  description: string
}

const TIER_LABEL = ['Runs silently', 'Runs, and tells you', 'Asks first', 'Asks, and needs typing']
const TIER_STYLE = [
  'text-aria-faint',
  'text-aria-muted',
  'text-aria-warn',
  'text-aria-bad',
]

export function ToolsPanel({ onClose }: { onClose: () => void }): JSX.Element {
  const [tools, setTools] = useState<ToolSummary[]>([])
  const [trusted, setTrusted] = useState<string[]>([])
  const [draft, setDraft] = useState('')
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const [list, trust] = await Promise.all([
        window.aria.call<{ tools: ToolSummary[] }>('tools.list', {}),
        window.aria.call<{ paths: string[] }>('tools.trusted', {}),
      ])
      setTools(list.tools)
      setTrusted(trust.paths)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  // Whole-list replacement, matching the RPC: two half-applied edits racing is
  // a worse failure than re-sending four strings.
  const replace = useCallback(async (paths: string[]) => {
    setError(null)
    try {
      const result = await window.aria.call<{ paths: string[] }>('tools.trusted', { paths })
      setTrusted(result.paths)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    }
  }, [])

  const add = useCallback(() => {
    const value = draft.trim().replace(/^"|"$/g, '')
    if (!value || trusted.includes(value)) return
    setDraft('')
    void replace([...trusted, value])
  }, [draft, trusted, replace])

  return (
    <Panel title="Tools" onClose={onClose}>
      <section>
        <h3 className="text-tiny font-semibold text-aria-text">Trusted folders</h3>
        <p className="mt-1 text-micro leading-relaxed text-aria-muted">
          Inside these she writes, moves and deletes without asking — including everything nested
          inside them. Everywhere else she still asks. A folder that reaches outside, like moving a
          file out of one of these, is asked about too.
        </p>

        <div className="mt-2 flex gap-1">
          <input
            value={draft}
            spellCheck={false}
            placeholder="C:\Users\you\Projects\scratch"
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') add()
            }}
            className="rim min-w-0 flex-1 rounded bg-aria-sunk px-2 py-1 font-mono text-micro text-aria-text outline-none placeholder:text-aria-faint focus:rim-strong"
          />
          <button
            type="button"
            disabled={!draft.trim()}
            onClick={add}
            className="rim interactive rounded px-2 py-1 text-micro text-aria-muted hover:text-aria-text disabled:opacity-40"
          >
            Trust
          </button>
        </div>

        <ul className="mt-2 space-y-1">
          {trusted.length === 0 && (
            <li className="text-micro text-aria-faint">
              Nothing is trusted yet, so she asks before every write.
            </li>
          )}
          {trusted.map((path) => (
            <li
              key={path}
              className="raised rim flex items-center gap-2 rounded px-2 py-1 text-micro"
            >
              <span className="min-w-0 flex-1 truncate font-mono text-aria-text" title={path}>
                {path}
              </span>
              <button
                type="button"
                onClick={() => void replace(trusted.filter((p) => p !== path))}
                className="interactive shrink-0 rounded px-1 text-aria-muted hover:text-aria-bad"
              >
                Remove
              </button>
            </li>
          ))}
        </ul>

        <p className="mt-2 text-micro leading-relaxed text-aria-faint">
          Trusting a folder never widens what she is allowed to touch. System folders stay refused
          whatever is listed here, and approval is never given by voice.
        </p>
      </section>

      <section className="mt-5">
        <h3 className="text-tiny font-semibold text-aria-text">
          Registered tools{tools.length > 0 && ` (${tools.length})`}
        </h3>
        <ul className="mt-1.5 space-y-0.5">
          {tools.map((tool) => (
            <li key={tool.name} className="flex items-baseline gap-2 py-0.5 text-micro">
              <span className="w-28 shrink-0 truncate font-mono text-aria-text">{tool.name}</span>
              <span className={`w-32 shrink-0 ${TIER_STYLE[tool.tier] ?? 'text-aria-muted'}`}>
                {TIER_LABEL[tool.tier] ?? `Tier ${tool.tier}`}
              </span>
              <span className="min-w-0 flex-1 truncate text-aria-faint" title={tool.description}>
                {tool.description}
              </span>
            </li>
          ))}
        </ul>
      </section>

      {error && <p className="mt-3 text-tiny text-aria-bad">{error}</p>}
    </Panel>
  )
}
