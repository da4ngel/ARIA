/**
 * Minimize, expand, fill the screen, close.
 *
 * Eyaas: *"i should be able to full expand the window as well which fits the
 * entire desktop screen."* There were two sizes — a 420px companion pinned
 * bottom-right, and a centred 900x700 working window — and no way to go
 * further.
 */

import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { WindowControls } from '@/components/WindowControls'

function controls(overrides: Partial<Parameters<typeof WindowControls>[0]> = {}) {
  return {
    expanded: true,
    onToggleExpanded: vi.fn(),
    maximized: false,
    onToggleMaximized: vi.fn(),
    ...overrides,
  }
}

describe('filling the screen', () => {
  it('is offered once the window is expanded', () => {
    render(<WindowControls {...controls()} />)

    expect(screen.getByLabelText('Fill the screen')).toBeDefined()
  })

  it('is not offered while compact', () => {
    // **The reason is not tidiness.** Compact is `resizable: false` and pinned
    // bottom-right with `alwaysOnTop` and no taskbar entry — maximising it
    // would either do nothing or produce a full-screen window you cannot get
    // behind or away from.
    render(<WindowControls {...controls({ expanded: false })} />)

    expect(screen.queryByLabelText('Fill the screen')).toBeNull()
  })

  it('offers the way back once it is filling the screen', () => {
    render(<WindowControls {...controls({ maximized: true })} />)

    expect(screen.getByLabelText('Restore')).toBeDefined()
    expect(screen.queryByLabelText('Fill the screen')).toBeNull()
  })

  it('asks for the change rather than assuming it happened', () => {
    const onToggleMaximized = vi.fn()
    render(<WindowControls {...controls({ onToggleMaximized })} />)

    fireEvent.click(screen.getByLabelText('Fill the screen'))

    expect(onToggleMaximized).toHaveBeenCalled()
  })
})

describe('the other three', () => {
  it('still minimizes and closes to tray', () => {
    // Close hides to the tray because she keeps listening — the label says so,
    // since a close button that does not close is worth being honest about.
    render(<WindowControls {...controls()} />)

    expect(screen.getByLabelText('Minimize')).toBeDefined()
    expect(screen.getByLabelText('Close to tray')).toBeDefined()
  })

  it('expands and shrinks independently of filling the screen', () => {
    const onToggleExpanded = vi.fn()
    const onToggleMaximized = vi.fn()
    render(<WindowControls {...controls({ onToggleExpanded, onToggleMaximized })} />)

    fireEvent.click(screen.getByLabelText('Shrink'))

    expect(onToggleExpanded).toHaveBeenCalled()
    expect(onToggleMaximized).not.toHaveBeenCalled()
  })
})
