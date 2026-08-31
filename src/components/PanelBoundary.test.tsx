/**
 * One panel failing must not blank the window.
 *
 * **Found by feeding `ClipboardPanel` a payload with one field renamed** while
 * looking at the UI for the first time: it threw on `entry.content.replace`,
 * React unmounted the entire tree, and the app became an empty rectangle —
 * the same symptom as the retheme's blank window, from a completely different
 * cause. There was no error boundary anywhere in this app.
 */

import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { PanelBoundary } from '@/components/PanelBoundary'

function Boom(): JSX.Element {
  throw new Error("Cannot read properties of undefined (reading 'content')")
}

function Fine(): JSX.Element {
  return <p>the panel</p>
}

describe('PanelBoundary', () => {
  it('is invisible when nothing goes wrong', () => {
    render(
      <PanelBoundary name="clipboard" onClose={() => {}}>
        <Fine />
      </PanelBoundary>,
    )
    expect(screen.getByText('the panel')).toBeTruthy()
    expect(screen.queryByText(/failed/)).toBeNull()
  })

  it('names the panel and shows the message rather than disappearing', () => {
    // React logs the caught error itself; silenced so a passing run is quiet.
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
    render(
      <PanelBoundary name="clipboard" onClose={() => {}}>
        <Boom />
      </PanelBoundary>,
    )
    expect(screen.getByText(/The clipboard panel failed/)).toBeTruthy()
    // The message, because "something went wrong" is not diagnosable and a
    // stack belongs in the log the diagnostics export collects.
    expect(screen.getByText(/reading 'content'/)).toBeTruthy()
    // The half that matters: everything else still works, said out loud.
    expect(screen.getByText(/Everything else still works/)).toBeTruthy()
    spy.mockRestore()
  })

  it('does not hold one panel’s failure against the next one', () => {
    // A different panel is a different subtree. Without the reset, opening
    // anything after a failure would show the first one's error forever —
    // which is a worse bug than the one this component exists to fix.
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const { rerender } = render(
      <PanelBoundary name="clipboard" onClose={() => {}}>
        <Boom />
      </PanelBoundary>,
    )
    expect(screen.getByText(/The clipboard panel failed/)).toBeTruthy()

    rerender(
      <PanelBoundary name="settings" onClose={() => {}}>
        <Fine />
      </PanelBoundary>,
    )
    expect(screen.getByText('the panel')).toBeTruthy()
    expect(screen.queryByText(/failed/)).toBeNull()
    spy.mockRestore()
  })
})
