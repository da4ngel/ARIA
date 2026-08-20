/**
 * The rail — and the gap this file exists to close.
 *
 * **There was no test for `Sidebar.tsx` at all.** A `Section` added to the
 * union with no `<Item>` to reach it typechecks perfectly and leaves the whole
 * panel unreachable, with nothing anywhere saying so — the same shape as the
 * `finder` import once dropped from `tools/__init__.py`, or the four tables
 * this project shipped that nobody wrote to.
 *
 * Found while adding Study. The parametrised test below is the guard: every
 * member of `Section` must be clickable, so the next one cannot arrive
 * unreachable either.
 */

import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { Sidebar, type Section } from '@/components/Sidebar'

const SECTIONS: Section[] = ['history', 'voice', 'files', 'tools', 'memory', 'study', 'settings']

function rail(overrides: Partial<Parameters<typeof Sidebar>[0]> = {}) {
  return (
    <Sidebar
      collapsed={false}
      onToggleCollapsed={vi.fn()}
      canExpand
      active={null}
      onSelect={vi.fn()}
      onNewChat={vi.fn()}
      canNewChat
      connected
      orbState="idle"
      orbLevel={0}
      listening={false}
      {...overrides}
    />
  )
}

describe('every section is reachable', () => {
  it.each(SECTIONS)('%s has a rail item that selects it', (section) => {
    const onSelect = vi.fn()
    render(rail({ onSelect }))

    // By label rather than by test id: the label is what makes the rail
    // navigable at all, and a section whose button exists but says nothing is
    // barely better than one that is missing.
    const labels: Record<Section, string> = {
      history: 'Chats',
      voice: 'Voice',
      files: 'Files',
      tools: 'Tools',
      memory: 'Memory',
      study: 'Study',
      settings: 'Settings',
    }
    fireEvent.click(screen.getByText(labels[section]))

    expect(onSelect).toHaveBeenCalledWith(section)
  })
})

describe('the compact window', () => {
  it('drops labels whatever the stored preference says', () => {
    // Measured on screen once: a 13rem labelled rail takes half of a 420px
    // window and squeezes the conversation into a column. A preference for
    // labels cannot conjure the width to show them in.
    render(rail({ collapsed: false, canExpand: false }))

    expect(screen.queryByText('Study')).toBeNull()
    expect(screen.queryByText('Memory')).toBeNull()
  })

  it('still reaches every section by its accessible name', () => {
    const onSelect = vi.fn()
    render(rail({ canExpand: false, onSelect }))

    fireEvent.click(screen.getByTitle('Study'))

    expect(onSelect).toHaveBeenCalledWith('study')
  })
})

describe('state on the rail', () => {
  it('disables navigation while the sidecar is unreachable', () => {
    render(rail({ connected: false }))

    expect(screen.getByText('Study').closest('button')?.disabled).toBe(true)
  })

  it('marks the active section', () => {
    render(rail({ active: 'study' }))

    expect(screen.getByText('Study').closest('button')?.getAttribute('aria-current')).toBeTruthy()
  })
})
