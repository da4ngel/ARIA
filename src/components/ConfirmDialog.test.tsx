import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { ConfirmDialog, type ConfirmRequest } from '@/components/ConfirmDialog'

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
})
