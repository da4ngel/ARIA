/**
 * The reply renderer, and the snippet box.
 *
 * **There was no test for this file at all**, which is how a hardcoded
 * `text-sky-400` sat in it through an entire retheme — the eighth place the
 * palette had been restated, and the one nothing was watching.
 */

import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { Markdown } from '@/components/Markdown'

/** Written this way so a fence below can never terminate anything. */
const F = '```'

beforeEach(() => {
  Object.assign(navigator, { clipboard: { writeText: vi.fn(() => Promise.resolve()) } })
})

describe('a fenced code block', () => {
  it('names the language it was tagged with', () => {
    render(<Markdown text={`Here:\n\n${F}python\nprint("hi")\n${F}`} />)

    expect(screen.getByText('Python')).toBeDefined()
  })

  it('names nothing when the fence was not tagged', () => {
    // A wrong language in the header is worse than none — it is a claim about
    // the code, not decoration.
    const { container } = render(<Markdown text={`${F}\nsome text\n${F}`} />)

    expect(container.querySelector('pre')).toBeTruthy()
    expect(screen.queryByText('Python')).toBeNull()
    expect(screen.queryByText('bash')).toBeNull()
  })

  it('offers copy without having to be hovered first', () => {
    // It used to appear only on hover, floating over the code's first line —
    // at 420px that covers what you are reading, and a control you discover by
    // hovering is one most people never find.
    render(<Markdown text={`${F}bash\nnpm run dev\n${F}`} />)

    expect(screen.getByLabelText('Copy code')).toBeDefined()
  })

  it('copies the code and not the prose around it', () => {
    render(<Markdown text={`Run this now:\n\n${F}bash\nnpm run dev\n${F}\n\nThen wait.`} />)

    fireEvent.click(screen.getByLabelText('Copy code'))

    const copied = (navigator.clipboard.writeText as ReturnType<typeof vi.fn>).mock.calls[0][0]
    expect(copied).toContain('npm run dev')
    expect(copied).not.toContain('Run this now')
    expect(copied).not.toContain('Then wait')
  })

  it('scrolls a long line rather than wrapping it', () => {
    // A broken line in PowerShell is a different command.
    const { container } = render(
      <Markdown text={`${F}powershell\nGet-Process | Sort-Object CPU\n${F}`} />,
    )

    expect(container.querySelector('pre')?.className).toContain('overflow-x-auto')
  })

  it('folds a long block behind a control that says how long it is', () => {
    const long = Array.from({ length: 40 }, (_, i) => `line ${i}`).join('\n')
    render(<Markdown text={`${F}python\n${long}\n${F}`} />)

    fireEvent.click(screen.getByText(/show all 40 lines/))

    expect(screen.getByText('show less')).toBeDefined()
  })

  it('leaves a short block alone', () => {
    render(<Markdown text={`${F}python\na = 1\n${F}`} />)

    expect(screen.queryByText(/show all/)).toBeNull()
  })
})

describe('highlighting', () => {
  it('colours a tagged fence with hljs class names', () => {
    // The class prefix is the contract with `index.css`, which maps `hljs-*`
    // onto the palette. Replacing the highlighter must not change these.
    const { container } = render(<Markdown text={`${F}python\ndef f():\n    pass\n${F}`} />)

    expect(container.querySelector('code.hljs')).toBeTruthy()
    expect(container.querySelector('.hljs-keyword')).toBeTruthy()
  })

  it('resolves an alias like js', () => {
    const { container } = render(<Markdown text={`${F}js\nconst a = 1\n${F}`} />)

    expect(container.querySelector('.hljs-keyword')).toBeTruthy()
  })

  it('leaves an untagged fence uncoloured', () => {
    // **A deliberate change from `rehype-highlight`, which auto-detected.**
    // Detection runs every registered grammar and picks a winner, which on the
    // streaming path is seventeen parses per token while a fence is open — and
    // colouring a fence the model did not label is a guess about what the code
    // is. The header already declines to print a guessed language for exactly
    // that reason; doing it in colour is the same claim.
    const { container } = render(<Markdown text={`${F}\nplain text here\n${F}`} />)

    expect(container.querySelector('pre')).toBeTruthy()
    expect(container.querySelector('.hljs-keyword')).toBeNull()
  })

  it('honours no-highlight', () => {
    const { container } = render(<Markdown text={`${F}no-highlight\ndef f():\n    pass\n${F}`} />)

    expect(container.querySelector('.hljs-keyword')).toBeNull()
  })

  it('falls through to plain text for a language it does not know', () => {
    // A model writing an unusual fence tag is normal. Throwing here would take
    // down the whole reply — this is what `ignoreMissing` used to buy.
    expect(() => render(<Markdown text={`${F}brainfuck\n+++[->+++<]\n${F}`} />)).not.toThrow()
  })
})

describe('inline code', () => {
  it('stays inline and does not become a block', () => {
    const { container } = render(<Markdown text={'Use `npm run dev` to start.'} />)

    expect(container.querySelector('pre')).toBeNull()
    const code = container.querySelector('code')
    expect(code).toBeTruthy()
    expect(code?.textContent).toBe('npm run dev')
  })
})

describe('links', () => {
  it('opens in the real browser rather than in the window', () => {
    // **`_blank` is what makes a link work at all here.** A plain anchor fires
    // `will-navigate` in the main process, which blocks it and logs a warning
    // nobody sees — so clicking a link in a reply did nothing whatsoever. With
    // a target, `setWindowOpenHandler` fires and calls `shell.openExternal`.
    const { container } = render(<Markdown text={'[docs](https://example.com)'} />)
    const link = container.querySelector('a')

    expect(link?.getAttribute('target')).toBe('_blank')
    expect(link?.getAttribute('rel')).toContain('noreferrer')
  })

  it('allows mailto', () => {
    const { container } = render(<Markdown text={'[write](mailto:a@b.com)'} />)

    expect(container.querySelector('a')?.getAttribute('href')).toBe('mailto:a@b.com')
  })

  it('renders an unsafe scheme as text, not as a dead link', () => {
    const { container } = render(<Markdown text={'[click](javascript:alert(1))'} />)

    expect(container.querySelector('a')).toBeNull()
    expect(container.textContent).toContain('click')
  })

  it('does not offer irc or xmpp, which react-markdown permits by default', () => {
    const { container } = render(<Markdown text={'[chat](xmpp:someone@example.com)'} />)

    expect(container.querySelector('a')).toBeNull()
  })
})

describe('untrusted model output', () => {
  it('shows HTML as text rather than mounting it', () => {
    // No `rehype-sanitize` is installed and none is needed: react-markdown 9
    // does not render raw HTML without `rehype-raw`, which is absent. This is
    // the test that keeps that true, in place of a dependency.
    const { container } = render(
      <Markdown text={'<script>alert(1)</script> and <img src=x onerror=alert(1)>'} />,
    )

    expect(container.querySelector('script')).toBeNull()
    expect(container.querySelector('img')).toBeNull()
    expect(container.textContent).toContain('alert(1)')
  })
})

describe('structure', () => {
  it('keeps an ordered list numbered', () => {
    // The old blanket `[&_li]:list-disc` forced a bullet onto every item,
    // numbered ones included.
    const { container } = render(<Markdown text={'1. first\n2. second'} />)

    expect(container.querySelector('ol')?.className).toContain('list-decimal')
    expect(container.querySelector('ol')?.className).not.toContain('list-disc')
  })

  it('hangs the indent so a wrapped line aligns to the text', () => {
    const { container } = render(<Markdown text={'- a\n- b'} />)

    expect(container.querySelector('ul')?.className).toContain('list-outside')
  })

  it('gives a table its own scroller', () => {
    // A table cannot scroll itself, and an overflowing one would otherwise
    // widen the whole transcript.
    const { container } = render(<Markdown text={'| a | b |\n| - | - |\n| 1 | 2 |'} />)
    const table = container.querySelector('table')

    expect(table).toBeTruthy()
    expect(table?.parentElement?.className).toContain('overflow-x-auto')
  })

  it('renders h1 and h2 at the same step', () => {
    // A heading in a reply is a section marker, not a title.
    const { container } = render(<Markdown text={'# One\n\n## Two'} />)
    const headings = Array.from(container.querySelectorAll('h2'))

    expect(headings).toHaveLength(2)
    for (const heading of headings) expect(heading.className).toContain('text-head')
  })
})

describe('streaming', () => {
  it('renders a half-written fence as a code block from the first line', () => {
    // Without the virtual close this is a paragraph of raw source until the
    // closing fence arrives, and then it snaps into a `<pre>` — a visible
    // reflow on every code block in every reply.
    const { container } = render(<Markdown text={`${F}python\nprint(`} streaming />)

    expect(container.querySelector('pre')).toBeTruthy()
  })

  it('does not move when the real fence lands', () => {
    const { container, rerender } = render(<Markdown text={`${F}python\nprint(1)`} streaming />)
    const before = container.querySelectorAll('pre').length

    rerender(<Markdown text={`${F}python\nprint(1)\n${F}`} streaming={false} />)

    expect(container.querySelectorAll('pre').length).toBe(before)
  })

  it('marks the reply so the caret can attach to its last element', () => {
    const { container, rerender } = render(<Markdown text={'still going'} streaming />)
    expect(container.firstElementChild?.className).toContain('is-streaming')

    rerender(<Markdown text={'still going'} streaming={false} />)
    expect(container.firstElementChild?.className).not.toContain('is-streaming')
  })

  it('arrives at the same DOM whether streamed or rendered at once', () => {
    // The whole optimisation is that finished blocks are parsed once and their
    // memo reused. If block splitting ever dropped or mangled one, this is
    // where it shows — a reply that renders differently depending on how it
    // got there is the failure mode that actually matters.
    const full = `Intro.\n\n- a\n- b\n\n${F}python\nx = 1\n${F}\n\nOutro.`

    const streamed = render(<Markdown text={full.slice(0, 12)} streaming />)
    streamed.rerender(<Markdown text={full.slice(0, 40)} streaming />)
    streamed.rerender(<Markdown text={full} streaming={false} />)

    const atOnce = render(<Markdown text={full} />)

    expect(streamed.container.innerHTML).toBe(atOnce.container.innerHTML)
  })
})

describe('the palette', () => {
  it('takes its colours from tokens rather than raw Tailwind', () => {
    // `text-sky-400` lived here through a whole retheme. After the palette
    // went green it was both off-palette and sitting near the accent's hue,
    // and nothing failed.
    //
    // Asserted against the rendered link rather than the root container's
    // class list: colours moved into `prose.ts` per element, so a root-level
    // check would now pass by looking at the wrong thing.
    const { container } = render(<Markdown text={'[a link](https://example.com)'} />)

    expect(container.querySelector('a')?.className).toContain('text-aria-accent')
    expect(container.innerHTML).not.toMatch(/text-(sky|blue|indigo|violet|emerald|green)-\d/)
  })

  it('uses a token surface for inline code', () => {
    const { container } = render(<Markdown text={'a `thing` here'} />)

    expect(container.querySelector('code')?.className).toContain('bg-aria-sunk')
  })
})
