/**
 * The mode control.
 *
 * What matters here is not that a popover opens — it is that Normal does not
 * look like a setting, and that Research with the web switched off says so
 * rather than quietly behaving like Normal and leaving her to explain it in a
 * refusal.
 */

import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { ModeSelector } from '@/components/ModeSelector'

const BASE = {
  mode: 'normal' as const,
  label: 'Normal',
  needsOnline: false,
  disabled: false,
  onSelect: () => {},
  onEnableOnline: () => {},
}

describe('ModeSelector', () => {
  it('names the current mode without opening anything', () => {
    render(<ModeSelector {...BASE} mode="study" label="Study" />)

    expect(screen.getByRole('button', { name: 'Answer mode: Study' })).toBeDefined()
  })

  it('describes each mode rather than just listing names', () => {
    // "Study" alone does not tell you it will ask you questions back.
    render(<ModeSelector {...BASE} />)
    fireEvent.click(screen.getByRole('button', { name: 'Answer mode: Normal' }))

    expect(screen.getByText(/asks? a question back|question back/i)).toBeDefined()
    expect(screen.getByText(/cites them/i)).toBeDefined()
  })

  it('reports the mode chosen and closes', () => {
    const onSelect = vi.fn()
    render(<ModeSelector {...BASE} onSelect={onSelect} />)
    fireEvent.click(screen.getByRole('button', { name: 'Answer mode: Normal' }))

    fireEvent.click(screen.getByText('Quick'))

    expect(onSelect).toHaveBeenCalledWith('quick')
    expect(screen.queryByText(/One line where/)).toBeNull()
  })

  it('says when Research cannot actually reach the web', () => {
    // "On" is not the same as "working" — the distinction `settings.online`
    // already draws. Without this the mode silently behaves like Normal.
    render(<ModeSelector {...BASE} mode="research" label="Research" needsOnline />)

    expect(screen.getByText(/needs online mode/i)).toBeDefined()
  })

  it('offers the fix rather than only the complaint', () => {
    const onEnableOnline = vi.fn()
    render(
      <ModeSelector
        {...BASE}
        mode="research"
        label="Research"
        needsOnline
        onEnableOnline={onEnableOnline}
      />,
    )

    fireEvent.click(screen.getByText(/needs online mode/i))

    expect(onEnableOnline).toHaveBeenCalled()
  })

  it('does not mark Normal as if it were a setting', () => {
    // Normal is the absence of a mode. A dot beside it would make the default
    // read as something switched on.
    const { container } = render(<ModeSelector {...BASE} />)
    const dots = container.querySelectorAll('span.rounded-full')

    expect(dots.length).toBe(0)
  })
})
