/**
 * Markdown rendering, and code that looks like code (BUILD_SPEC §9 Phase 1).
 *
 * Eyaas: *"when its gonna give code or cmd command or any kinda those stuffs,
 * it should be in a nice kinda snippet box, like how things are in chatgpt and
 * claude."*
 *
 * There was already a box — a `rim bg-aria-sunk` `<pre>` with a copy button —
 * and it read as an undifferentiated grey slab. Three things were missing, and
 * they are what the header strip below is for: **which language this is**,
 * **a copy control you can see without hunting for it**, and highlighting.
 *
 * The copy button used to appear on hover, floating over the code's first
 * line. At 420px that covers the thing you are trying to read, and a control
 * you have to discover by hovering is one most people never find.
 */

import { memo, useState, type ReactNode } from 'react'
import ReactMarkdown from 'react-markdown'
import rehypeHighlight from 'rehype-highlight'
import remarkGfm from 'remark-gfm'

/** What auto-detection is allowed to guess at, for a fence with no tag.
 *
 * **This is a `subset`, and a subset narrows *detection*, not the bundle.**
 * `rehype-highlight` does `import {common} from 'lowlight'` at module scope,
 * so all thirty-seven of its languages are compiled in whatever is passed
 * here — measured, that is the whole of the +363KB this feature cost, and no
 * option available on this plugin changes it. Getting it back would mean
 * writing the plugin against `createLowlight` directly and owning its edge
 * cases (`no-highlight`, nested code, prefixes), which is not a trade worth
 * making for a bundle that is read off local disk.
 *
 * What it *does* buy is predictable guessing. An untagged fence of prose or a
 * stack trace will not be confidently coloured as Perl. A fence that names any
 * of the thirty-seven still highlights, which is a bonus rather than a leak.
 */
const DETECTABLE = [
  'python',
  'javascript',
  'typescript',
  'bash',
  'shell',
  'powershell',
  'json',
  'sql',
  'css',
  'xml', // covers HTML
  'yaml',
  'markdown',
  'diff',
] as const

/** How a language is spelled in the header, where it differs from its tag. */
const LABELS: Record<string, string> = {
  javascript: 'JavaScript',
  typescript: 'TypeScript',
  powershell: 'PowerShell',
  bash: 'bash',
  shell: 'shell',
  python: 'Python',
  json: 'JSON',
  sql: 'SQL',
  css: 'CSS',
  xml: 'HTML',
  yaml: 'YAML',
  markdown: 'Markdown',
  diff: 'diff',
}

function CopyButton({ value }: { value: string }): JSX.Element {
  const [copied, setCopied] = useState(false)

  const copy = async (): Promise<void> => {
    try {
      await navigator.clipboard.writeText(value)
      setCopied(true)
      setTimeout(() => setCopied(false), 1200)
    } catch {
      // Clipboard can be denied; a dead button is better than a thrown error.
      setCopied(false)
    }
  }

  return (
    <button
      type="button"
      aria-label="Copy code"
      onClick={() => void copy()}
      className="interactive shrink-0 rounded px-1.5 py-0.5 text-micro text-aria-faint hover:text-aria-text"
    >
      {copied ? 'copied' : 'copy'}
    </button>
  )
}

/** Extract raw text from a code block's children, for the copy button. */
function textOf(node: ReactNode): string {
  if (typeof node === 'string') return node
  if (Array.isArray(node)) return node.map(textOf).join('')
  if (node && typeof node === 'object' && 'props' in node) {
    const props = (node as { props?: { children?: ReactNode } }).props
    return textOf(props?.children)
  }
  return ''
}

/**
 * The `language-x` class react-markdown puts on the inner `<code>`.
 *
 * Read off the child rather than guessed from the content: an unlabelled fence
 * gets no name at all, because a wrong language in the header is worse than
 * none — it is a claim about the code, and highlighting will already have
 * declined to colour it.
 */
function languageOf(node: ReactNode): string | null {
  if (Array.isArray(node)) {
    for (const child of node) {
      const found = languageOf(child)
      if (found) return found
    }
    return null
  }
  if (node && typeof node === 'object' && 'props' in node) {
    const className = (node as { props?: { className?: string } }).props?.className ?? ''
    const match = /language-([\w-]+)/.exec(className)
    if (match) return match[1]
  }
  return null
}

export const Markdown = memo(function Markdown({ text }: { text: string }): JSX.Element {
  return (
    <div className="space-y-2 text-small leading-relaxed [&_a]:text-aria-accent [&_a]:underline [&_li]:ml-4 [&_li]:list-disc [&_p]:m-0 [&_strong]:font-strong">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[[rehypeHighlight, { subset: DETECTABLE, ignoreMissing: true }]]}
        components={{
          pre({ children }) {
            const language = languageOf(children)
            return (
              <div className="rim my-2 overflow-hidden rounded-lg bg-aria-sunk">
                {/* A lid, not a second block: `raised` is a white wash, so it
                    reads as the same object catching more light. */}
                <div className="flex items-center justify-between gap-2 bg-aria-raised px-2 py-1">
                  <span className="truncate font-mono text-micro text-aria-faint">
                    {language ? (LABELS[language] ?? language) : ''}
                  </span>
                  <CopyButton value={textOf(children)} />
                </div>
                {/* Scrolls rather than wraps. Wrapping code changes what it
                    means — a broken line in PowerShell is a different command. */}
                <pre className="overflow-x-auto p-3 text-tiny">{children}</pre>
              </div>
            )
          },
          code({ className, children }) {
            // Inline code only — block code is wrapped by `pre` above, and
            // arrives here with the `language-*` class the highlighter needs.
            if (className) return <code className={className}>{children}</code>
            return (
              <code className="rounded bg-aria-sunk px-1 py-0.5 font-mono text-[0.9em] text-aria-dim">
                {children}
              </code>
            )
          },
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  )
})
