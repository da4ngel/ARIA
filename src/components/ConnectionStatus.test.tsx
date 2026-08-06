import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ConnectionStatus } from '@/components/ConnectionStatus'

describe('ConnectionStatus', () => {
  it('renders the Phase 0 gate string when connected', () => {
    render(<ConnectionStatus status="connected" />)
    expect(screen.getByText('Brain:')).toBeDefined()
    expect(screen.getByText('connected')).toBeDefined()
  })

  it('distinguishes reconnecting from connected', () => {
    render(<ConnectionStatus status="reconnecting" />)
    expect(screen.getByText('reconnecting…')).toBeDefined()
  })
})
