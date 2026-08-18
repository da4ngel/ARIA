/**
 * The chip exists so Full access is never silent.
 *
 * In that mode nothing prompts — no confirmation, no checkout warning — so
 * before this the only evidence of the most permissive state in the app was
 * the *absence* of dialogs, which reads as a bug rather than a setting.
 */

import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { PermissionModeChip } from '@/components/PermissionModeChip'

describe('PermissionModeChip', () => {
  it('names the mode in the header, without opening a panel', () => {
    render(<PermissionModeChip mode="manual" disabled={false} onOpen={() => {}} />)

    expect(screen.getByRole('button', { name: 'Permission mode: Manual' })).toBeDefined()
  })

  it('shows Full access in the warning color it deserves', () => {
    // The same treatment DANGER tools get. CLAUDE.md rule 5 is what this
    // mode sets aside, and it should look like it.
    render(<PermissionModeChip mode="full_access" disabled={false} onOpen={() => {}} />)

    const chip = screen.getByRole('button', { name: 'Permission mode: Full access' })
    expect(chip.className).toContain('text-aria-bad')
  })

  it('does not shout about Auto, which is the default', () => {
    render(<PermissionModeChip mode="auto" disabled={false} onOpen={() => {}} />)

    const chip = screen.getByRole('button', { name: 'Permission mode: Auto' })
    expect(chip.className).not.toContain('text-aria-bad')
  })

  it('opens the panel where the mode can actually be changed', () => {
    // Seeing the mode and being unable to do anything about it from here
    // would just move the problem one click further away.
    const onOpen = vi.fn()
    render(<PermissionModeChip mode="auto" disabled={false} onOpen={onOpen} />)

    fireEvent.click(screen.getByRole('button', { name: 'Permission mode: Auto' }))

    expect(onOpen).toHaveBeenCalled()
  })

  it('is inert while the sidecar is down', () => {
    const onOpen = vi.fn()
    render(<PermissionModeChip mode="auto" disabled onOpen={onOpen} />)

    fireEvent.click(screen.getByRole('button', { name: 'Permission mode: Auto' }))

    expect(onOpen).not.toHaveBeenCalled()
  })
})
