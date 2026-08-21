/**
 * The Study console.
 *
 * What is worth asserting here is not that it renders — it is the three things
 * that would look fine and be wrong: a button that starts a session must
 * actually send its opener, a button with nothing to work on must say so
 * instead of spending a turn finding out, and deleting a subject must take two
 * clicks because it is not recoverable.
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { StudyPanel } from '@/components/StudyPanel'
import type { StudyConcept, StudyState, StudySubject } from '@/types/bridge'

function concept(overrides: Partial<StudyConcept> = {}): StudyConcept {
  return {
    id: 1,
    name: 'CIA Triad',
    summary: 'Confidentiality, integrity, availability.',
    level: 4,
    asked: 5,
    correct: 4,
    ...overrides,
  }
}

function subject(overrides: Partial<StudySubject> = {}): StudySubject {
  return {
    id: 7,
    name: 'Information Security',
    source_path: 'C:/lectures/infosec.pptx',
    last_studied_at: '2026-08-20T10:00:00Z',
    total: 3,
    covered: 2,
    ...overrides,
  }
}

function state(concepts: StudyConcept[]): StudyState {
  return {
    subject_id: 7,
    subject: 'Information Security',
    source_path: 'C:/lectures/infosec.pptx',
    covered: concepts.filter((c) => c.level > 0).length,
    next: null,
    concepts,
  }
}

/** Stub the bridge; `call` is what every hook goes through. */
function mockBridge(handler: (method: string, params: Record<string, unknown>) => unknown) {
  const call = vi.fn((method: string, params: Record<string, unknown> = {}) =>
    Promise.resolve(handler(method, params)),
  )
  // @ts-expect-error — the test only needs `call`.
  window.aria = { call }
  return call
}

function defaults(concepts: StudyConcept[], overrides: Record<string, unknown> = {}) {
  return (method: string): unknown => {
    if (method === 'study.subjects') return { subjects: [subject()] }
    if (method === 'study.sessions') return { sessions: [] }
    if (method === 'study.state') return state(concepts)
    if (method === 'study.start') {
      return { session_id: 's_1', sub_mode: 'learn', label: 'Learn', opener: 'Teach me.' }
    }
    return (overrides[method] as unknown) ?? { ok: true }
  }
}

const noop = (): void => {}

function panel(props: Partial<Parameters<typeof StudyPanel>[0]> = {}) {
  return (
    <StudyPanel
      onClose={noop}
      onStudy={noop}
      onNewStudyChat={() => Promise.resolve('s_new')}
      onOpenSession={noop}
      {...props}
    />
  )
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('the map', () => {
  it('shows the subject and its concepts', async () => {
    // Both solid, so each name appears once — a shaky concept is listed twice
    // on purpose and that is its own test below.
    mockBridge(defaults([concept(), concept({ id: 2, name: 'Access Control', level: 4 })]))

    render(panel())

    expect(await screen.findByText('Information Security')).toBeDefined()
    expect(await screen.findByText('Access Control')).toBeDefined()
    expect(screen.queryByText('Needs revision')).toBeNull()
  })

  it('says what to do when nothing has been studied', async () => {
    // An empty panel that only says "nothing here" is a dead end; this one
    // names the two things that produce a map.
    mockBridge((method) => {
      if (method === 'study.subjects') return { subjects: [] }
      if (method === 'study.sessions') return { sessions: [] }
      if (method === 'study.state') return { subject: null, concepts: [] }
      return { ok: true }
    })

    render(panel())

    expect(await screen.findByText(/Start a study chat/i)).toBeDefined()
  })

  it('separates what is shaky from the rest of the map', async () => {
    // "Due" is weakest-first, derived from level — there is no schedule, and
    // this is the surface that decision was made for.
    mockBridge(defaults([concept(), concept({ id: 2, name: 'Replay Attacks', level: 1 })]))

    render(panel())

    expect(await screen.findByText('Needs revision')).toBeDefined()
    // Once under "Needs revision" and once in the full map.
    expect(await screen.findAllByText('Replay Attacks')).toHaveLength(2)
  })

  it('reports the score from the concepts rather than a stored total', async () => {
    mockBridge(defaults([concept({ asked: 5, correct: 4 }), concept({ id: 2, asked: 5, correct: 1 })]))

    render(panel())

    expect(await screen.findByText(/10 answered · 5 right · 50%/)).toBeDefined()
  })
})

describe('starting a session', () => {
  it('opens a new study chat and starts it in that sub-mode', async () => {
    // **A new chat every time, not the one that happens to be open.** A study
    // session is a conversation; starting one inside yesterday's exam buries
    // it. The sub-mode lands on the chat the button just created.
    const call = mockBridge(defaults([concept()]))
    const onStudy = vi.fn()
    const onNewStudyChat = vi.fn(() => Promise.resolve('s_new'))
    render(panel({ onStudy, onNewStudyChat }))
    await screen.findByText('Information Security')

    fireEvent.click(screen.getByText('Exam'))

    await waitFor(() => expect(onNewStudyChat).toHaveBeenCalled())
    await waitFor(() =>
      expect(call).toHaveBeenCalledWith('study.start', { sub_mode: 'exam', session_id: 's_new' }),
    )
    // The opener the sidecar returned, not one invented here — the panel and
    // `study_modes.py` must not each have their own idea of what Exam says.
    await waitFor(() => expect(onStudy).toHaveBeenCalledWith('Teach me.'))
  })

  it('closes the panel, because the reply lands behind it', async () => {
    mockBridge(defaults([concept()]))
    const onClose = vi.fn()
    render(panel({ onClose }))
    await screen.findByText('Information Security')

    fireEvent.click(screen.getByText('Learn'))

    await waitFor(() => expect(onClose).toHaveBeenCalled())
  })

  it('disables a sub-mode that has nothing to work on', async () => {
    // A button that produces "there is nothing to revise" is a button that
    // should have said so itself rather than spending a turn.
    mockBridge(defaults([concept({ level: 4 })]))

    render(panel())
    await screen.findByText('Information Security')

    expect(screen.getByText('Revision').closest('button')?.disabled).toBe(true)
    expect(screen.getByText('Practice').closest('button')?.disabled).toBe(false)
  })

  it('disables everything that needs covered ground when nothing is covered', async () => {
    mockBridge(defaults([concept({ level: 0, asked: 0, correct: 0 })]))

    render(panel())
    await screen.findByText('Information Security')

    for (const label of ['Practice', 'Rapid review', 'Exam']) {
      expect(screen.getByText(label).closest('button')?.disabled).toBe(true)
    }
    expect(screen.getByText('Learn').closest('button')?.disabled).toBe(false)
  })
})

describe('editing', () => {
  it('takes two clicks to delete a subject', async () => {
    // It cascades through `concepts` into `concept_mastery`, so it takes every
    // answer he ever gave with it. `MemoryPanel`'s forget, for a bigger reason.
    const call = mockBridge(defaults([concept()]))
    render(panel())
    await screen.findByText('Information Security')

    fireEvent.click(screen.getByText('Delete'))

    expect(call).not.toHaveBeenCalledWith('study.forget', expect.anything())
    fireEvent.click(screen.getByText('Sure?'))
    await waitFor(() => expect(call).toHaveBeenCalledWith('study.forget', { subject_id: 7 }))
  })

  it('takes one click to reset a concept, which is re-earnable', async () => {
    const call = mockBridge(defaults([concept()]))
    render(panel())
    await screen.findByText('Information Security')

    fireEvent.click(screen.getByLabelText('Reset CIA Triad'))

    await waitFor(() => expect(call).toHaveBeenCalledWith('study.reset', { concept_id: 1 }))
  })

  it('renames a subject on Enter and abandons it on Escape', async () => {
    const call = mockBridge(defaults([concept()]))
    render(panel())
    fireEvent.click(await screen.findByLabelText('Rename subject'))

    const input = screen.getByLabelText('Subject name')
    fireEvent.change(input, { target: { value: 'Infosec' } })
    fireEvent.keyDown(input, { key: 'Escape' })
    expect(call).not.toHaveBeenCalledWith('study.rename', expect.anything())

    fireEvent.click(screen.getByLabelText('Rename subject'))
    const again = screen.getByLabelText('Subject name')
    fireEvent.change(again, { target: { value: 'Infosec' } })
    fireEvent.keyDown(again, { key: 'Enter' })

    await waitFor(() =>
      expect(call).toHaveBeenCalledWith('study.rename', { subject_id: 7, name: 'Infosec' }),
    )
  })

  it('shows a refused rename rather than swallowing it', async () => {
    // Two subjects with one name makes resuming a coin flip, so the sidecar
    // refuses — and a panel that says nothing looks like a click that missed.
    mockBridge(
      defaults([concept()], {
        'study.rename': { ok: false, reason: 'There is already a subject with that name.' },
      }),
    )
    render(panel())
    fireEvent.click(await screen.findByLabelText('Rename subject'))

    const input = screen.getByLabelText('Subject name')
    fireEvent.change(input, { target: { value: 'Networking' } })
    fireEvent.keyDown(input, { key: 'Enter' })

    expect(await screen.findByText(/already a subject with that name/i)).toBeDefined()
  })
})
