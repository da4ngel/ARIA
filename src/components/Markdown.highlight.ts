/**
 * Syntax highlighting, with only the grammars this app actually wants.
 *
 * **Why this is not `rehype-highlight`.** That plugin does
 * `import {common} from 'lowlight'` at module scope, so all thirty-seven of
 * lowlight's common grammars are compiled into the bundle no matter what
 * `subset` is passed — `subset` narrows *detection*, never the bundle.
 * CLAUDE.md measured that at **+363KB** and declined to fix it, on the
 * reasoning that it is a bundle read off local disk.
 *
 * What changed the answer is a second measurement: those grammars are also the
 * dominant *parse* cost. One pass over an 8,000-character reply is 13.25ms
 * with highlighting and 6.30ms without — more than half — and the trailing
 * block re-parses on every token while a reply streams. So this is not only
 * bundle bytes; it is the thing standing between a streaming reply and the
 * frame budget.
 *
 * The cost of owning it is three behaviours the plugin handled, each of which
 * has a test in `Markdown.test.tsx`: opting out with `no-highlight`, an
 * unknown language falling through to plain text rather than throwing, and
 * emitting `hljs-*` class names so `index.css` keeps working untouched.
 */

import { createLowlight } from 'lowlight'
import { visit } from 'unist-util-visit'
import type { Element, Root } from 'hast'

import bash from 'highlight.js/lib/languages/bash'
import c from 'highlight.js/lib/languages/c'
import cpp from 'highlight.js/lib/languages/cpp'
import css from 'highlight.js/lib/languages/css'
import diff from 'highlight.js/lib/languages/diff'
import go from 'highlight.js/lib/languages/go'
import javascript from 'highlight.js/lib/languages/javascript'
import json from 'highlight.js/lib/languages/json'
import markdown from 'highlight.js/lib/languages/markdown'
import powershell from 'highlight.js/lib/languages/powershell'
import python from 'highlight.js/lib/languages/python'
import rust from 'highlight.js/lib/languages/rust'
import shell from 'highlight.js/lib/languages/shell'
import sql from 'highlight.js/lib/languages/sql'
import typescript from 'highlight.js/lib/languages/typescript'
import xml from 'highlight.js/lib/languages/xml'
import yaml from 'highlight.js/lib/languages/yaml'

/**
 * The languages worth carrying, and nothing else.
 *
 * `xml` covers HTML. Each grammar registers its own aliases with highlight.js,
 * so `js`, `ts`, `py`, `sh`, `yml` and `ps1` all resolve without being listed.
 */
export const lowlight = createLowlight({
  bash,
  c,
  cpp,
  css,
  diff,
  go,
  javascript,
  json,
  markdown,
  powershell,
  python,
  rust,
  shell,
  sql,
  typescript,
  xml,
  yaml,
})

/** Ways of saying "leave this one alone". */
const OPT_OUT = new Set(['no-highlight', 'nohighlight', 'plaintext', 'text', 'plain'])

/** The language named on a `<code>`, or null for untagged and opted-out. */
export function languageFrom(classes: readonly string[]): string | null {
  for (const name of classes) {
    if (OPT_OUT.has(name)) return null
  }
  for (const name of classes) {
    const match = /^lang(?:uage)?-([\w+#-]+)$/.exec(name)
    if (match) return OPT_OUT.has(match[1]) ? null : match[1]
  }
  return null
}

function classesOf(node: Element): string[] {
  // hast types `className` as an array, but a plugin upstream is free to have
  // left a bare string there, so both are handled rather than assumed.
  const raw: unknown = node.properties?.className
  if (Array.isArray(raw)) return raw.map(String)
  if (typeof raw === 'string') return raw.split(/\s+/).filter(Boolean)
  return []
}

function textOf(node: Element): string {
  let out = ''
  visit(node, 'text', (child) => {
    out += child.value
  })
  return out
}

/**
 * Highlight fenced code blocks.
 *
 * **An untagged fence is left plain, and that is a deliberate change from
 * `rehype-highlight`'s behaviour here.** It used to auto-detect within a
 * subset. Two reasons not to: auto-detection runs every registered grammar
 * against the text and picks a winner, which on the streaming path is
 * seventeen parses per token while a fence is open; and colouring a fence the
 * model did not label is a guess about what the code *is*. This file's own
 * header already declines to print a guessed language for exactly that reason
 * — *"a wrong language in the header is worse than none — it is a claim about
 * the code"* — and doing it in colour instead of in words is the same claim.
 */
export function rehypeHighlight() {
  return (tree: Root): void => {
    visit(tree, 'element', (node: Element, _index, parent) => {
      if (node.tagName !== 'code') return
      if (!parent || parent.type !== 'element' || parent.tagName !== 'pre') return

      const language = languageFrom(classesOf(node))
      if (!language) return
      // An unknown language is a normal thing for a model to write. Plain text
      // is the answer; throwing would take down the whole reply.
      if (!lowlight.registered(language)) return

      const result = lowlight.highlight(language, textOf(node))
      node.children = result.children as Element['children']
      node.properties = {
        ...node.properties,
        className: [...classesOf(node).filter((n) => n !== 'hljs'), 'hljs'],
      }
    })
  }
}
