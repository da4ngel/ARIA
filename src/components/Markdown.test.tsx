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

beforeEach(() => {
  Object.assign(navigator, { clipboard: { writeText: vi.fn(() => Promise.resolve()) } })
})

describe('a fenced code block', () => {
  it('names the language it was tagged with', () => {
    render(<Markdown text={'Here:\n\n```python\nprint("hi")\n```'} />)

    expect(screen.getByText('Python')).toBeDefined()
  })

  it('names nothing when the fence was not tagged', () => {
    // A wrong language in the header is worse than none — it is a claim about
    // the code, not decoration.
    const { container } = render(<Markdown text={'```\nsome text\n```'} />)

    expect(container.querySelector('pre')).toBeTruthy()
    expect(screen.queryByText('Python')).toBeNull()
    expect(screen.queryByText('bash')).toBeNull()
  })

  it('offers copy without having to be hovered first', () => {
    // It used to appear only on hover, floating over the code's first line —
    // at 420px that covers what you are reading, and a control you discover by
    // hovering is one most people never find.
    render(<Markdown text={'```bash\nnpm run dev\n```'} />)

    expect(screen.getByLabelText('Copy code')).toBeDefined()
  })

  it('copies the code and not the prose around it', () => {
    render(<Markdown text={'Run this now:\n\n```bash\nnpm run dev\n```\n\nThen wait.'} />)

    fireEvent.click(screen.getByLabelText('Copy code'))

    const copied = (navigator.clipboard.writeText as ReturnType<typeof vi.fn>).mock.calls[0][0]
    expect(copied).toContain('npm run dev')
    expect(copied).not.toContain('Run this now')
    expect(copied).not.toContain('Then wait')
  })

  it('scrolls a long line rather than wrapping it', () => {
    // A broken line in PowerShell is a different command.
    const { container } = render(<Markdown text={'```powershell\nGet-Process | Sort-Object CPU\n```'} />)

    expect(container.querySelector('pre')?.className).toContain('overflow-x-auto')
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

describe('the palette', () => {
  it('takes its colours from tokens rather than raw Tailwind', () => {
    // `text-sky-400` lived here through a whole retheme. After the palette
    // went green it was both off-palette and sitting near the accent's hue,
    // and nothing failed.
    const { container } = render(<Markdown text={'[a link](https://example.com)'} />)
    const classes = container.firstElementChild?.className ?? ''

    expect(classes).not.toMatch(/text-(sky|blue|indigo|violet|emerald|green)-\d/)
    expect(classes).toContain('text-aria-accent')
  })

  it('uses a token surface for inline code', () => {
    const { container } = render(<Markdown text={'a `thing` here'} />)

    expect(container.querySelector('code')?.className).toContain('bg-aria-sunk')
  })
})
