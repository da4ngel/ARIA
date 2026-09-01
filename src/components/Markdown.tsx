/**
 * Assistant replies, rendered as a transcript rather than a document.
 *
 * Eyaas: *"when its gonna give code or cmd command or any kinda those stuffs,
 * it should be in a nice kinda snippet box, like how things are in chatgpt and
 * claude."*
 *
 * **The thing that makes this file non-obvious is streaming.** Tokens arrive
 * one at a time and `useConversation` appends each to a growing string, so the
 * naive rendering — hand the whole buffer to `react-markdown` — re-parses the
 * entire document on every token. Measured over one 8,000-character reply:
 * **10.3 seconds of parse CPU, a 29.5ms worst frame**, on a machine also
 * running Whisper, Kokoro and a 7B model. `memo` cannot help, because the text
 * really is new every time.
 *
 * So the buffer is split into blocks (`Markdown.blocks.ts`) and each block is
 * memoised on its own text. Every block but the last is finished and will
 * never change, so its memo bails out — and because `react-markdown` parses
 * *during render*, a bail-out is a skipped parse. Only the trailing block
 * re-parses per token: **0.91s, 3.5ms worst frame** on the same reply.
 *
 * Typography lives in `src/styles/prose.ts`, not here. Nothing in this file
 * may name a colour.
 */

import { memo, useMemo, useState, type ReactNode } from 'react'
import ReactMarkdown, { type Options } from 'react-markdown'
import remarkGfm from 'remark-gfm'

import { closeOpenFence, splitBlocks } from '@/components/Markdown.blocks'
import { rehypeHighlight } from '@/components/Markdown.highlight'
import { CODE_FOLD_LINES, PROSE, PROSE_BODY, PROSE_MEASURE } from '@/styles/prose'

/** How a language is spelled in the header, where it differs from its tag. */
const LABELS: Record<string, string> = {
  javascript: 'JavaScript',
  js: 'JavaScript',
  typescript: 'TypeScript',
  ts: 'TypeScript',
  powershell: 'PowerShell',
  ps1: 'PowerShell',
  python: 'Python',
  py: 'Python',
  json: 'JSON',
  sql: 'SQL',
  css: 'CSS',
  html: 'HTML',
  xml: 'HTML',
  yaml: 'YAML',
  yml: 'YAML',
  cpp: 'C++',
  c: 'C',
  go: 'Go',
  rust: 'Rust',
  bash: 'bash',
  shell: 'shell',
  markdown: 'Markdown',
  diff: 'diff',
}

/**
 * Only ever `http`, `https` and `mailto`.
 *
 * react-markdown's own default also permits `irc`, `ircs` and `xmpp`, which
 * this app has no handler for and no reason to hand to the OS. Anything else
 * comes back empty, and the `a` renderer below turns an empty href into plain
 * text — so a `javascript:` URL is not a dead link, it is not a link.
 */
const SAFE_SCHEME = /^(?:https?|mailto):/i
const HAS_SCHEME = /^[a-z][a-z0-9+.-]*:/i

function urlTransform(url: string): string {
  const trimmed = url.trim()
  if (!HAS_SCHEME.test(trimmed)) return trimmed // relative links and #anchors
  return SAFE_SCHEME.test(trimmed) ? trimmed : ''
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

/**
 * Extract raw text from a code block's children, for the copy button.
 *
 * Reads the rendered children, so it never sees the virtual closing fence
 * `closeOpenFence` adds while streaming — what is copied is what the model
 * actually wrote.
 */
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
 * none — it is a claim about the code.
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
    const match = /language-([\w+#-]+)/.exec(className)
    if (match) return match[1]
  }
  return null
}

function CodeBlock({ children }: { children: ReactNode }): JSX.Element {
  const [open, setOpen] = useState(false)
  const language = languageOf(children)
  const source = textOf(children)
  // A fenced block's text always ends with a newline, so counting naively
  // advertises "show all 41 lines" for a forty-line block. The number is
  // on screen, so it has to be the number a person would actually count.
  const lines = source.replace(/\n$/, '').split('\n').length
  const folded = lines > CODE_FOLD_LINES && !open

  return (
    <div className={PROSE.codeWrap}>
      <div className={PROSE.codeHeader}>
        <span className="truncate font-mono text-micro text-aria-faint">
          {language ? (LABELS[language] ?? language) : ''}
        </span>
        <CopyButton value={source} />
      </div>
      <pre
        className={PROSE.codeBody}
        // Derived from the same constant as the decision to fold, so the cap
        // and the threshold cannot drift apart.
        style={folded ? { maxHeight: `${CODE_FOLD_LINES * 1.7}em` } : undefined}
      >
        {children}
      </pre>
      {lines > CODE_FOLD_LINES && (
        <button
          type="button"
          onClick={() => setOpen((was) => !was)}
          className="interactive w-full border-t border-aria-rim px-2 py-1 text-micro text-aria-faint hover:text-aria-text"
        >
          {open ? 'show less' : `show all ${lines} lines`}
        </button>
      )}
    </div>
  )
}

/**
 * Module scope, so every memoised block shares one identity.
 *
 * `rehype-sanitize` is deliberately **not** here. react-markdown 9 does not
 * render raw HTML at all unless `rehype-raw` is added, which it is not, so
 * `<script>` in a reply arrives as text. Adding a sanitiser would be a
 * dependency guarding a hole that does not exist — there is a test asserting
 * the hole stays shut instead.
 */
const REMARK_PLUGINS: Options['remarkPlugins'] = [remarkGfm]
const REHYPE_PLUGINS: Options['rehypePlugins'] = [rehypeHighlight]

const COMPONENTS: Options['components'] = {
  p: ({ children }) => <p className={PROSE.p}>{children}</p>,
  // h1 and h2 share a step on purpose: a heading in a reply is a section
  // marker, not a title, and nothing in a transcript deserves display size.
  h1: ({ children }) => <h2 className={PROSE.h1}>{children}</h2>,
  h2: ({ children }) => <h2 className={PROSE.h2}>{children}</h2>,
  h3: ({ children }) => <h3 className={PROSE.h3}>{children}</h3>,
  h4: ({ children }) => <h4 className={PROSE.h4}>{children}</h4>,
  h5: ({ children }) => <h5 className={PROSE.h4}>{children}</h5>,
  h6: ({ children }) => <h6 className={PROSE.h4}>{children}</h6>,

  strong: ({ children }) => <strong className={PROSE.strong}>{children}</strong>,
  em: ({ children }) => <em className={PROSE.em}>{children}</em>,

  a: ({ href, children }) =>
    href ? (
      // **`_blank` is load-bearing, not a habit.** A plain anchor fires
      // `will-navigate` in the main process, which blocks it and logs a warning
      // nobody sees — so links in replies did nothing at all when clicked.
      // With a target, `setWindowOpenHandler` fires instead and calls
      // `shell.openExternal`, which is what "opens in the real browser" means.
      <a className={PROSE.a} href={href} target="_blank" rel="noreferrer">
        {children}
      </a>
    ) : (
      // `urlTransform` emptied it, so it was not a scheme we hand to the OS.
      // Show the words; never offer something that cannot be followed.
      <>{children}</>
    ),

  ul: ({ children }) => <ul className={PROSE.ul}>{children}</ul>,
  ol: ({ children }) => <ol className={PROSE.ol}>{children}</ol>,
  li: ({ children }) => <li className={PROSE.li}>{children}</li>,

  blockquote: ({ children }) => <blockquote className={PROSE.blockquote}>{children}</blockquote>,
  hr: () => <hr className={PROSE.hr} />,

  // A table cannot scroll itself, so it travels with its own scroller. The
  // right-edge fade only shows where there is content under it, which is
  // exactly when the table is overflowing — no measurement needed.
  table: ({ children }) => (
    <div
      className={PROSE.tableWrap}
      style={{
        maskImage: 'linear-gradient(to right, #000 calc(100% - 20px), transparent)',
        WebkitMaskImage: 'linear-gradient(to right, #000 calc(100% - 20px), transparent)',
      }}
    >
      <table className={PROSE.table}>{children}</table>
    </div>
  ),
  th: ({ children }) => <th className={PROSE.th}>{children}</th>,
  td: ({ children }) => <td className={PROSE.td}>{children}</td>,

  pre: ({ children }) => <CodeBlock>{children}</CodeBlock>,
  code: ({ className, children }) => {
    // Inline code only — block code is wrapped by `pre` above, and arrives
    // here carrying the `language-*` class the highlighter needs.
    if (className) return <code className={className}>{children}</code>
    return <code className={PROSE.codeInline}>{children}</code>
  },
}

/**
 * One block, parsed once.
 *
 * The memo is the entire optimisation: for every block but the last, `source`
 * is finished text that never changes, so this never re-renders — and because
 * parsing happens during render, never re-rendering means never re-parsing.
 */
const MarkdownBlock = memo(function MarkdownBlock({ source }: { source: string }): JSX.Element {
  return (
    <ReactMarkdown
      remarkPlugins={REMARK_PLUGINS}
      rehypePlugins={REHYPE_PLUGINS}
      components={COMPONENTS}
      urlTransform={urlTransform}
    >
      {source}
    </ReactMarkdown>
  )
})

export const Markdown = memo(function Markdown({
  text,
  streaming = false,
}: {
  text: string
  /** Still arriving. Closes a half-written fence and shows the caret. */
  streaming?: boolean
}): JSX.Element {
  const blocks = useMemo(() => splitBlocks(text), [text])

  return (
    // `react-markdown` renders a Fragment rather than a wrapper element, so
    // every block's output lands as siblings here. That is what lets
    // `first:mt-0` / `last:mb-0` work across the whole reply, and what lets the
    // caret attach to its genuine last element rather than to a wrapper.
    <div className={`${PROSE_BODY} ${PROSE_MEASURE}${streaming ? ' is-streaming' : ''}`}>
      {blocks.map((block, index) => (
        <MarkdownBlock
          key={index}
          source={streaming && index === blocks.length - 1 ? closeOpenFence(block) : block}
        />
      ))}
    </div>
  )
})
