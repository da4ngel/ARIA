/** Markdown rendering with copyable code blocks (BUILD_SPEC §9 Phase 1). */

import { memo, useState, type ReactNode } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

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
      onClick={() => void copy()}
      className="absolute right-2 top-2 rounded border border-aria-edge bg-aria-bg/80 px-2 py-0.5 text-[10px] text-aria-muted opacity-0 transition group-hover:opacity-100 hover:text-aria-text"
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

export const Markdown = memo(function Markdown({ text }: { text: string }): JSX.Element {
  return (
    <div className="space-y-2 text-sm leading-relaxed [&_a]:text-sky-400 [&_a]:underline [&_li]:ml-4 [&_li]:list-disc [&_p]:m-0 [&_strong]:font-semibold">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          pre({ children }) {
            return (
              <div className="group relative">
                <CopyButton value={textOf(children)} />
                <pre className="overflow-x-auto rounded-lg border border-aria-edge bg-black/40 p-3 text-xs">
                  {children}
                </pre>
              </div>
            )
          },
          code({ className, children }) {
            // Inline code only — block code is wrapped by `pre` above.
            if (className) return <code className={className}>{children}</code>
            return (
              <code className="rounded bg-white/10 px-1 py-0.5 text-[0.85em]">{children}</code>
            )
          },
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  )
})
