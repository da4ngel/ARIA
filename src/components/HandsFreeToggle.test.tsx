import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { HandsFreeToggle } from '@/components/HandsFreeToggle'

const noop = (): void => {}

function toggle(props: Partial<Parameters<typeof HandsFreeToggle>[0]> = {}) {
  return render(
    <HandsFreeToggle
      available
      active={false}
      level={0}
      disabled={false}
      onToggle={noop}
      {...props}
    />,
  )
}

describe('HandsFreeToggle', () => {
  it('renders nothing when the wake word is unavailable', () => {
    const { container } = toggle({ available: false })
    expect(container.innerHTML).toBe('')
  })

  it('reports its state to assistive tech', () => {
    toggle({ active: true })
    expect(screen.getByRole('switch').getAttribute('aria-checked')).toBe('true')
  })

  it('says the microphone is open while it is', () => {
    // The point of the label: an always-on microphone must be visible without
    // hovering anything.
    toggle({ active: true })
    expect(screen.getByText('Listening')).toBeDefined()
    expect(screen.getByRole('switch').title).toMatch(/microphone is open/i)
  })

  it('says nothing about listening while it is off', () => {
    toggle({ active: false })
    expect(screen.queryByText('Listening')).toBeNull()
  })

  it('toggles on click', () => {
    const onToggle = vi.fn()
    toggle({ onToggle })
    fireEvent.click(screen.getByRole('switch'))
    expect(onToggle).toHaveBeenCalledOnce()
  })

  it('cannot be switched on while the brain is down', () => {
    const onToggle = vi.fn()
    toggle({ disabled: true, onToggle })
    fireEvent.click(screen.getByRole('switch'))
    expect(onToggle).not.toHaveBeenCalled()
  })
})
