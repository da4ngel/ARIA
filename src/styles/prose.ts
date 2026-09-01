/**
 * Every typographic decision in an assistant reply, in one place.
 *
 * The brief asked for "a separate tokens file holding all colors, type, and
 * spacing values. No hardcoded hex outside it." **This is that file, and it
 * deliberately holds no colour of its own** — every value here is an `aria-*`
 * class resolving through `src/styles/tokens.js`, and every size is a step of
 * the scale in `tailwind.config.mjs`.
 *
 * A second palette would be the bug this project has now recorded eight times:
 * the tray icons sat a whole retheme behind because their colours were a
 * hand-typed copy, and `Markdown.tsx` itself carried a raw `text-sky-400`
 * through the green recolour. `prose.test.ts` fails on any raw hex or any raw
 * Tailwind colour appearing here.
 *
 * **Read the message area as a transcript, not a document.** The type is
 * quieter than a blog post but keeps real hierarchy: h1 and h2 land on the
 * same step because nothing in a running conversation deserves display size,
 * and the difference below that is carried by weight rather than by another
 * size.
 */

/**
 * Body is `dim`, emphasis is `text`.
 *
 * Bold at weight alone reads weakly at small sizes on a dark surface, so it is
 * paired with a brighter foreground — which is exactly what the four-step
 * neutral ramp was cut for. `text` is the top of that ramp, so body has to sit
 * one step below it for emphasis to have anywhere to go.
 *
 * Weight stays `font-strong` (620) rather than the 600 the brief suggests:
 * CLAUDE.md records that 600 blooms on near-black glass, measured on this
 * palette, and that finding still holds.
 */
export const PROSE_BODY = 'text-body text-aria-dim'

/**
 * How wide a line of prose is allowed to get — see `--prose` in `index.css`.
 *
 * Separate from `--reading` (46rem), which the transcript column and the
 * composer share and which must keep agreeing with each other. At body size
 * `--reading` is around 98 characters, well past the comfortable range; this
 * caps the prose alone and leaves the column, the composer and the user
 * bubbles exactly where they were.
 */
export const PROSE_MEASURE = 'max-w-[var(--prose)]'

/**
 * Per-element classes.
 *
 * Vertical rhythm is `margin-block` with the first and last margins zeroed, so
 * a reply has no dead space at its edges. Headings take more space above than
 * below, which is what binds one visually to the content it introduces rather
 * than letting it float between two paragraphs.
 */
export const PROSE = {
  /** `overflow-wrap: anywhere` so an unbroken URL cannot widen the column. */
  p: 'my-3 first:mt-0 last:mb-0 [overflow-wrap:anywhere]',

  h1: 'mt-6 mb-2 first:mt-0 text-head font-strong text-aria-text tracking-tight',
  h2: 'mt-6 mb-2 first:mt-0 text-head font-strong text-aria-text tracking-tight',
  h3: 'mt-5 mb-2 first:mt-0 text-subhead font-strong text-aria-text',
  /** Body size. At this depth the difference is weight, not another step. */
  h4: 'mt-4 mb-1 first:mt-0 text-body font-strong text-aria-text',

  strong: 'font-strong text-aria-text',
  em: 'italic',

  /** `_blank` is what routes this through `shell.openExternal` — see Markdown.tsx. */
  a: 'text-aria-accent underline underline-offset-2 decoration-aria-accent/40 hover:decoration-aria-accent',

  /**
   * `list-outside` is the hanging indent: the marker sits outside the content
   * box, so a wrapped line aligns to the text above it rather than to the
   * bullet. `pl-5` is the indent itself, and it is the *only* thing that
   * changes when a list nests — never the size.
   */
  ul: 'my-3 first:mt-0 last:mb-0 list-disc list-outside pl-5 marker:text-aria-faint',
  ol: 'my-3 first:mt-0 last:mb-0 list-decimal list-outside pl-5 marker:text-aria-faint',
  /** Tight between items; the list's own margin is what spaces it from prose. */
  li: 'my-1 [overflow-wrap:anywhere]',

  /** A rule and a quieter voice. Not italic-everything, which is unreadable
   *  for anything longer than a line. */
  blockquote: 'my-4 first:mt-0 last:mb-0 border-l-2 border-aria-rim-strong pl-3 text-aria-muted',

  hr: 'my-6 border-0 border-t border-aria-rim',

  /** The scroller, not the table — a table cannot scroll itself. */
  tableWrap: 'my-4 first:mt-0 last:mb-0 overflow-x-auto',
  table: 'w-full border-collapse text-left',
  /** Weight and a rule, never a filled background: a header band would be the
   *  heaviest thing in the reply and it is not the point of the table. */
  th: 'border-b border-aria-rim-strong px-2 py-1.5 font-strong text-aria-text',
  td: 'border-b border-aria-rim px-2 py-1.5 align-top',

  /** Optically matched to the prose around it — a monospace face at the same
   *  nominal size reads a step larger. */
  codeInline: 'rounded bg-aria-sunk px-1 py-0.5 font-mono text-[0.9em] text-aria-text',

  codeWrap: 'rim my-4 first:mt-0 last:mb-0 overflow-hidden rounded-lg bg-aria-sunk',
  /** A lid, not a second block: `raised` is a white wash, so it reads as the
   *  same object catching more light. */
  codeHeader: 'flex items-center justify-between gap-2 bg-aria-raised px-2 py-1',
  /** `pt-3` clears the header chrome. Scrolls rather than wraps — a broken
   *  line in PowerShell is a different command. */
  codeBody: 'overflow-x-auto px-3 pb-3 pt-3 text-tiny leading-relaxed',
} as const

/** Past this many lines a block collapses behind "show more". */
export const CODE_FOLD_LINES = 18
