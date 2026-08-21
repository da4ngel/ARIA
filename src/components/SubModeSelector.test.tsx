/**
 * The composer control in a study chat.
 *
 * It occupies the mode picker's slot, and the thing worth asserting is that it
 * offers *ways of studying* rather than ways of answering — that is what makes
 * a study chat a different kind of chat rather than an ordinary one with a
 * badge on it.
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { SUB_MODES, SubModeSelector } from '@/components/SubModeSelector'

const BASE = {
  subMode: 'learn' as const,
  disabled: false,
  onSelect: () => {},
}

describe('SubModeSelector', () => {
  it('names the sub-mode in use without opening anything', () => {
    render(<SubModeSelector {...BASE} subMode="exam" />)

    expect(screen.getByRole('button', { name: 'Study: Exam' })).toBeDefined()
  })

  it('offers all six', () => {
    render(<SubModeSelector {...BASE} />)
    fireEvent.click(screen.getByRole('button', { name: 'Study: Learn' }))

    for (const option of SUB_MODES) {
      // `getAllBy`, because the current one also names itself on the trigger.
      expect(screen.getAllByText(option.label).length).toBeGreaterThan(0)
    }
  })

  it('offers no answer modes, because a study chat cannot leave Study', () => {
    // The sidecar refuses to move a study chat's mode; offering the switch
    // here would be a control whose only outcome is being ignored.
    render(<SubModeSelector {...BASE} />)
    fireEvent.click(screen.getByRole('button', { name: 'Study: Learn' }))

    for (const label of ['Normal', 'Quick', 'Research', 'Code', 'Critic']) {
      expect(screen.queryByText(label)).toBeNull()
    }
  })

  it('describes each one rather than just listing names', () => {
    render(<SubModeSelector {...BASE} />)
    fireEvent.click(screen.getByRole('button', { name: 'Study: Learn' }))

    expect(screen.getByText(/no feedback until the end/i)).toBeDefined()
    expect(screen.getByText(/A skim, not a lesson/i)).toBeDefined()
  })

  it('reports the choice', async () => {
    const onSelect = vi.fn()
    render(<SubModeSelector {...BASE} onSelect={onSelect} />)
    fireEvent.click(screen.getByRole('button', { name: 'Study: Learn' }))

    fireEvent.click(screen.getByText('Revision'))

    expect(onSelect).toHaveBeenCalledWith('revision')
    // The sheet has an exit animation — it leaves over a frame or two rather
    // than between them, which is the whole reason it has one.
    await waitFor(() => expect(screen.queryByText(/A skim, not a lesson/i)).toBeNull())
  })

  it('is disabled while the sidecar is unreachable', () => {
    render(<SubModeSelector {...BASE} disabled />)

    expect(screen.getByRole('button', { name: 'Study: Learn' }).getAttribute('disabled')).not.toBeNull()
  })
})
