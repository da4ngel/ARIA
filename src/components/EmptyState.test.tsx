import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { EmptyState } from '@/components/EmptyState'

// The empty case used to live inside ConversationView as the string
// "Say something." It moved here when the orb became the hero of a blank
// screen, which is why that assertion is no longer in ConversationView's tests.

describe('EmptyState', () => {
  it('introduces her and says where she is running', () => {
    render(<EmptyState state="idle" connected onPick={() => {}} />)
    expect(screen.getByText('Aria')).toBeDefined()
    expect(screen.getByText('Running on this machine')).toBeDefined()
  })

  it('says what it is waiting for when the brain is down', () => {
    render(<EmptyState state="idle" connected={false} onPick={() => {}} />)
    expect(screen.getByText('Waiting for the brain to start')).toBeDefined()
  })

  it('sends a suggestion when one is clicked', () => {
    const onPick = vi.fn()
    render(<EmptyState state="idle" connected onPick={onPick} />)
    fireEvent.click(screen.getByText('What can you do?'))
    expect(onPick).toHaveBeenCalledWith('What can you do?')
  })

  it('does not offer suggestions while disconnected', () => {
    render(<EmptyState state="idle" connected={false} onPick={() => {}} />)
    const button = screen.getByText('What can you do?').closest('button')
    expect(button?.hasAttribute('disabled')).toBe(true)
  })

  it('reports the assistant state for screen readers', () => {
    render(<EmptyState state="thinking" connected onPick={() => {}} />)
    expect(screen.getByText('thinking')).toBeDefined()
  })
})
