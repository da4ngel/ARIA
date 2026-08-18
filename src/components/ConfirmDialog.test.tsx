import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import {
  ConfirmDialog,
  type ConfirmRequest,
  type MovePlan,
} from '@/components/ConfirmDialog'

function request(overrides: Partial<ConfirmRequest> = {}): ConfirmRequest {
  return {
    request_id: 'cr_1',
    tool: 'move_file',
    args: { source: 'C:/a.txt', destination: 'C:/b.txt' },
    tier: 2,
    typed: false,
    ...overrides,
  }
}

const danger = (): ConfirmRequest =>
  request({ tool: 'delete_file', tier: 3, typed: true, args: { path: 'C:/notes.txt' } })

describe('ConfirmDialog', () => {
  it('shows nothing when nothing is pending', () => {
    const { container } = render(<ConfirmDialog request={null} onRespond={() => {}} />)
    expect(container.innerHTML).toBe('')
  })

  it('shows the arguments, because approving without them is not consent', () => {
    render(<ConfirmDialog request={danger()} onRespond={() => {}} />)
    expect(screen.getByText('C:/notes.txt')).toBeDefined()
  })

  it('will not allow a danger tool until its name is typed', () => {
    const onRespond = vi.fn()
    render(<ConfirmDialog request={danger()} onRespond={onRespond} />)

    const allow = screen.getByRole('button', { name: 'Delete' })
    fireEvent.click(allow)
    expect(onRespond).not.toHaveBeenCalled()

    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'delete_file' } })
    fireEvent.click(allow)
    expect(onRespond).toHaveBeenCalledWith('cr_1', true, false)
  })

  it('does not demand typing below the danger tier', () => {
    const onRespond = vi.fn()
    render(<ConfirmDialog request={request()} onRespond={onRespond} />)

    expect(screen.queryByRole('textbox')).toBeNull()
    fireEvent.click(screen.getByRole('button', { name: 'Allow' }))
    expect(onRespond).toHaveBeenCalledWith('cr_1', true, false)
  })

  it('denies on Escape, so the safe answer is the reflex one', () => {
    const onRespond = vi.fn()
    render(<ConfirmDialog request={danger()} onRespond={onRespond} />)

    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onRespond).toHaveBeenCalledWith('cr_1', false, false)
  })

  it('caps and scrolls a long argument instead of growing the dialog off screen', () => {
    // Real failure: `type_text` asked to type an essay rendered the whole
    // essay with no height cap, pushing Allow/Deny below the visible
    // window — the only reachable answer was Escape, which denies. This
    // asserts the argument list itself is bounded and scrollable, the same
    // treatment `MovePlanView`'s own list already gets.
    const essay = 'Essay: The Value of Small Habits\n\n' + 'word '.repeat(400)
    render(
      <ConfirmDialog
        request={request({ tool: 'type_text', args: { text: essay } })}
        onRespond={() => {}}
      />,
    )

    const value = screen.getByText(/Essay: The Value of Small Habits/)
    expect(value.className).toContain('whitespace-pre-wrap')
    // The scrolling container is the arguments list itself, not the value.
    const list = value.closest('dl')
    expect(list?.className).toContain('overflow-y-auto')
    expect(list?.className).toContain('max-h-48')

    // And Allow/Deny are still reachable and still work.
    expect(screen.getByRole('button', { name: 'Allow' })).toBeDefined()
    expect(screen.getByRole('button', { name: 'Deny' })).toBeDefined()
  })

  it('offers "always allow" only where the action can be undone', () => {
    const { rerender } = render(<ConfirmDialog request={request()} onRespond={() => {}} />)
    expect(screen.queryByText('Always allow this')).not.toBeNull()

    rerender(<ConfirmDialog request={danger()} onRespond={() => {}} />)
    expect(screen.queryByText('Always allow this')).toBeNull()
  })

  it('does not carry typed text from one request to the next', () => {
    const onRespond = vi.fn()
    const { rerender } = render(<ConfirmDialog request={danger()} onRespond={onRespond} />)
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'delete_file' } })

    rerender(
      <ConfirmDialog
        request={{ ...danger(), request_id: 'cr_2', args: { path: 'C:/other.txt' } }}
        onRespond={onRespond}
      />,
    )

    // Armed for the previous request must not mean armed for this one.
    fireEvent.click(screen.getByRole('button', { name: 'Delete' }))
    expect(onRespond).not.toHaveBeenCalled()
  })

  // ── the batch preview (§7.2) ────────────────────────────────────────

  const plan = (over: Partial<MovePlan> = {}): ConfirmRequest =>
    request({
      tool: 'organize_folder',
      args: { path: 'downloads', strategy: 'by_type' },
      preview: {
        kind: 'move_plan',
        folder: 'C:/Users/me/Downloads',
        strategy: 'by_type',
        count: 30,
        skipped: 4,
        folders: ['Documents', 'Images'],
        moves: [
          { from: 'C:/Users/me/Downloads/invoice.pdf', to: 'C:/Users/me/Downloads/Documents/invoice.pdf' },
          { from: 'C:/Users/me/Downloads/holiday.png', to: 'C:/Users/me/Downloads/Images/holiday.png' },
        ],
        truncated: 28,
        ...over,
      },
    })

  it('shows the batch rather than the arguments', () => {
    // §7.2: "if the agent wants to move 30 files, emit one confirm.request
    // describing the batch, not 30. Include the full file list." `args` is
    // {path, strategy} and says nothing about what is about to happen.
    render(<ConfirmDialog request={plan()} onRespond={() => {}} />)

    expect(screen.getByText('30')).toBeDefined()
    expect(screen.getByText('invoice.pdf')).toBeDefined()
    expect(screen.getByText('Documents/invoice.pdf')).toBeDefined()
    expect(screen.getByText('Documents · Images')).toBeDefined()
    // The raw arguments are replaced, not stacked underneath.
    expect(screen.queryByText('by_type')).toBeNull()
  })

  it('says how many files it is leaving alone', () => {
    render(<ConfirmDialog request={plan()} onRespond={() => {}} />)
    expect(screen.getByText(/4 left alone/)).toBeDefined()
  })

  it('admits when the list it is showing is not the whole list', () => {
    render(<ConfirmDialog request={plan()} onRespond={() => {}} />)
    expect(screen.getByText('and 28 more')).toBeDefined()
  })

  it('falls back to the arguments when a preview could not be computed', () => {
    // Losing the confirmation because the detail failed would be backwards.
    render(<ConfirmDialog request={request({ preview: null })} onRespond={() => {}} />)
    expect(screen.getByText('C:/a.txt')).toBeDefined()
  })

  it('still asks, and still takes an answer, with a plan on screen', () => {
    const onRespond = vi.fn()
    render(<ConfirmDialog request={plan()} onRespond={onRespond} />)

    fireEvent.click(screen.getByRole('button', { name: 'Allow' }))
    expect(onRespond).toHaveBeenCalledWith('cr_1', true, false)
  })

  // ── the typing target (type_text) ──────────────────────
  //
  // Eyaas asked for an essay, ARIA opened Notepad and began typing, he
  // switched to VS Code, and the rest of the essay went there. The window is
  // now claimed before this dialog appears, and naming it here is what makes
  // that claim something he can actually check before clicking Allow.

  const typing = (): ConfirmRequest =>
    request({
      tool: 'type_text',
      args: { text: 'e'.repeat(5000) },
      preview: {
        kind: 'type_target',
        window: 'Untitled - Notepad',
        chars: 5000,
        method: 'paste',
        excerpt: 'e'.repeat(600),
        truncated: true,
        is_aria: false,
      },
    })

  it('names the window the text is going into, and how much of it', () => {
    render(<ConfirmDialog request={typing()} onRespond={() => {}} />)

    expect(screen.getByText('Untitled - Notepad')).toBeDefined()
    expect(screen.getByText(/5,000 characters/)).toBeDefined()
    expect(screen.getByText(/pasted in one go/)).toBeDefined()
  })

  it('does not render the essay as a raw argument list', () => {
    render(<ConfirmDialog request={typing()} onRespond={() => {}} />)

    // The whole reason the args fallback grew a height cap: an essay in a
    // `<dd>` pushed Allow and Deny off the bottom, leaving Escape — which
    // denies — as the only reachable answer. A preview avoids it entirely.
    expect(screen.queryByText('text')).toBeNull()
    expect(screen.getByRole('button', { name: 'Allow' })).toBeDefined()
    expect(screen.getByRole('button', { name: 'Deny' })).toBeDefined()
  })

  it('says so when the target is her own window', () => {
    const own = typing()
    const preview = own.preview as { window: string; is_aria: boolean }
    preview.window = 'Aria'
    preview.is_aria = true

    render(<ConfirmDialog request={own} onRespond={() => {}} />)

    expect(screen.getByText(/my own window/)).toBeDefined()
  })

  // ── the screenshot preview (capture_screen, Phase 6) ────────────────

  const screenshot = (): ConfirmRequest =>
    request({
      tool: 'capture_screen',
      args: { question: "what's on screen" },
      preview: {
        kind: 'image_preview',
        thumbnail_b64: 'ZmFrZS1qcGVn',
        provider: 'GPT-4o',
      },
    })

  it('shows the thumbnail and names who it is going to, not the raw args', () => {
    render(<ConfirmDialog request={screenshot()} onRespond={() => {}} />)

    const image = screen.getByAltText('Screen preview') as HTMLImageElement
    expect(image.src).toContain('ZmFrZS1qcGVn')
    expect(screen.getByText('GPT-4o')).toBeDefined()
    // Same principle as the move plan: the preview replaces the argument
    // list, it does not sit above it.
    expect(screen.queryByText("what's on screen")).toBeNull()
  })

  it('still asks, and still takes an answer, with a screenshot on screen', () => {
    const onRespond = vi.fn()
    render(<ConfirmDialog request={screenshot()} onRespond={onRespond} />)

    fireEvent.click(screen.getByRole('button', { name: 'Allow' }))
    expect(onRespond).toHaveBeenCalledWith('cr_1', true, false)
  })
})
