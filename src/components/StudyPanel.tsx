/**
 * Study — the map, what is shaky, and the six ways to run a session.
 *
 * Eyaas asked for this as a rail section beside Chats, Voice, Files, Tools and
 * Memory rather than as something you have to ask her about. It is a console,
 * not a viewer.
 *
 * **A sub-mode button opens a study chat.** Study stopped being a mode you
 * switch on and became a kind of conversation you open — *"another type of
 * chat, dedicated fully for studies purpose"* — so pressing Exam here starts a
 * study chat in Exam rather than reaching into whatever conversation happens
 * to be in front of you. Switching sub-mode *within* a session is the
 * composer's picker; this is how a session begins.
 *
 * **And it sends a visible message.** It could set the state and say nothing,
 * which would be less code — but then the thing that started an exam would be
 * invisible in the transcript, and pressing "Exam" *is* asking to be examined.
 * It belongs there in his own words.
 *
 * **Clicks are not tool calls.** Rename, reset and delete go through
 * `study.*` RPCs, not the registry: the `files.browse` distinction this project
 * already drew. A confirmation dialog in front of the button somebody just
 * pressed is asking them to confirm the thing they just did. Deleting a subject
 * is unrecoverable, so it arms in two clicks instead — `MemoryPanel`'s forget,
 * for a bigger reason.
 */

import { useState } from 'react'

import { Panel } from '@/components/Panel'
import { needsRevision, useStudy } from '@/hooks/useStudy'
import type { StudyConcept, StudySubject } from '@/types/bridge'

/** The six, in the order they are used rather than alphabetically: learn it,
 *  practise it, fix what broke, skim it, sit the exam, explain it back. */
const SUB_MODES = [
  { id: 'learn', label: 'Learn', hint: 'Teach me the next thing, in layers.' },
  { id: 'practice', label: 'Practice', hint: 'Questions on what I have covered, with feedback.' },
  { id: 'revision', label: 'Revision', hint: 'Only the things I keep getting wrong.' },
  { id: 'rapid', label: 'Rapid review', hint: 'One line per concept. A skim, not a lesson.' },
  { id: 'exam', label: 'Exam', hint: 'Four questions, no feedback until the end.' },
  { id: 'teach_back', label: 'Teach-back', hint: 'I explain, she says what was missing.' },
] as const

const MAX_LEVEL = 5

/** Dots, not a number. `level` is an integer 0-5 and `MemoryPanel`'s
 *  `0.00-1.00` ramp does not carry over — five positions read as a scale at a
 *  glance where "3" has to be compared against something. */
function Mastery({ level }: { level: number }): JSX.Element {
  const tone = level >= 4 ? 'text-aria-ok' : level >= 3 ? 'text-aria-muted' : 'text-aria-warn'
  return (
    <span className={`shrink-0 font-mono tracking-tight ${level === 0 ? 'text-aria-faint' : tone}`}>
      {'●'.repeat(level)}
      {'○'.repeat(MAX_LEVEL - level)}
    </span>
  )
}

function ConceptRow({
  concept,
  onReset,
}: {
  concept: StudyConcept
  onReset: () => void
}): JSX.Element {
  return (
    <li className="raised rim flex items-center gap-2 rounded px-2 py-1 text-micro">
      <span className="min-w-0 flex-1 truncate text-aria-text" title={concept.summary}>
        {concept.name}
      </span>
      <Mastery level={concept.level} />
      <span
        className="shrink-0 tabular-nums text-aria-faint"
        title={
          concept.asked === 0
            ? 'Never asked about'
            : `${concept.correct} right of ${concept.asked} asked`
        }
      >
        {concept.asked > 0 ? `${concept.correct}/${concept.asked}` : '—'}
      </span>
      {/* One click, where deleting a subject takes two: a reset destroys
          nothing that cannot be earned again by answering a question. */}
      <button
        type="button"
        aria-label={`Reset ${concept.name}`}
        title="Back to unlearned. You can earn it again by answering."
        onClick={onReset}
        disabled={concept.level === 0 && concept.asked === 0}
        className="interactive shrink-0 rounded px-1 text-aria-faint hover:text-aria-text disabled:opacity-25"
      >
        ↺
      </button>
    </li>
  )
}

function SubjectHeader({
  subject,
  subjects,
  onSelect,
  onRename,
  onForget,
  onExport,
}: {
  subject: StudySubject | undefined
  subjects: StudySubject[]
  onSelect: (id: number) => void
  onRename: (name: string) => void
  onForget: () => void
  onExport: (format: 'md' | 'html') => Promise<string | null>
}): JSX.Element | null {
  const [editing, setEditing] = useState<string | null>(null)
  const [armed, setArmed] = useState(false)
  const [saved, setSaved] = useState<string | null>(null)

  if (!subject) return null
  const pct = subject.total > 0 ? Math.round((subject.covered / subject.total) * 100) : 0

  return (
    <div className="rim raised rounded px-2 py-1.5">
      <div className="flex items-center gap-2">
        {editing === null ? (
          <button
            type="button"
            aria-label="Rename subject"
            title="Rename — this is the name resuming matches on"
            onClick={() => setEditing(subject.name)}
            className="interactive min-w-0 flex-1 truncate text-left text-tiny font-strong text-aria-text"
          >
            {subject.name}
          </button>
        ) : (
          <input
            autoFocus
            aria-label="Subject name"
            value={editing}
            onChange={(e) => setEditing(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                onRename(editing)
                setEditing(null)
              }
              if (e.key === 'Escape') setEditing(null)
            }}
            onBlur={() => setEditing(null)}
            className="min-w-0 flex-1 rounded bg-aria-sunk px-1 py-0.5 text-tiny text-aria-text outline-none"
          />
        )}
        <span className="shrink-0 tabular-nums text-micro text-aria-muted">
          {subject.covered}/{subject.total}
        </span>
        {/* Two formats and no PDF library. The HTML is styled for paper, so
            Ctrl+P in any browser produces one — see `memory/study_export.py`
            for why that beat adding reportlab or weasyprint. */}
        <button
          type="button"
          onClick={() => void onExport('md').then(setSaved)}
          title="Save the map as Markdown"
          className="interactive shrink-0 rounded px-1 text-micro text-aria-faint hover:text-aria-text"
        >
          .md
        </button>
        <button
          type="button"
          onClick={() => void onExport('html').then(setSaved)}
          title="Save as a page you can print to PDF with Ctrl+P"
          className="interactive shrink-0 rounded px-1 text-micro text-aria-faint hover:text-aria-text"
        >
          .html
        </button>
        <button
          type="button"
          onClick={() => (armed ? onForget() : setArmed(true))}
          onBlur={() => setArmed(false)}
          title="Deletes the map and every answer you have given. This cannot be undone."
          className={`interactive shrink-0 rounded px-1 text-micro ${
            armed ? 'text-aria-bad' : 'text-aria-faint hover:text-aria-bad'
          }`}
        >
          {armed ? 'Sure?' : 'Delete'}
        </button>
      </div>

      {/* Where it went, because a file saved somewhere you cannot find is a
          file you did not get. */}
      {saved && <p className="mt-1 truncate text-micro text-aria-ok">Saved to {saved}</p>}

      <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-aria-sunk">
        <div className="h-full rounded-full bg-aria-accent" style={{ width: `${pct}%` }} />
      </div>

      {subjects.length > 1 && (
        <div className="mt-1.5 flex flex-wrap gap-1">
          {subjects.map((other) => (
            <button
              key={other.id}
              type="button"
              onClick={() => onSelect(other.id)}
              className={`interactive rounded px-1.5 py-0.5 text-micro ${
                other.id === subject.id
                  ? 'bg-aria-sunk text-aria-text'
                  : 'text-aria-faint hover:text-aria-text'
              }`}
            >
              {other.name}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export function StudyPanel({
  onClose,
  onStudy,
  onNewStudyChat,
  onOpenSession,
}: {
  onClose: () => void
  /** Sends the sub-mode's opener as an ordinary message. */
  onStudy: (text: string) => void
  /** Opens a fresh study chat and returns its reserved id. */
  onNewStudyChat: () => Promise<string | null>
  onOpenSession: (sessionId: string) => void
}): JSX.Element {
  const study = useStudy(true)

  /** Save the map, and hand back where it landed. A refusal is a message
   *  rather than an exception — `useStudy`'s rule for `rename`. */
  async function exportMap(format: 'md' | 'html'): Promise<string | null> {
    if (study.selected === null) return null
    try {
      const result = await window.aria.call<{ path: string }>('study.export', {
        subject_id: study.selected,
        format,
      })
      return result.path ?? null
    } catch {
      return null
    }
  }
  const concepts = study.state?.concepts ?? []
  const shaky = needsRevision(concepts)
  const covered = concepts.filter((c) => c.level > 0)
  const subject = study.subjects.find((s) => s.id === study.selected)

  // Grouped by where each chat got to, not by what it is bound to — a study
  // chat may roam, and `study_subject_id` records rather than constrains.
  const chats = study.sessions.filter(
    (s) => study.selected === null || s.study_subject_id === study.selected,
  )

  const asked = concepts.reduce((sum, c) => sum + c.asked, 0)
  const right = concepts.reduce((sum, c) => sum + c.correct, 0)

  async function run(subMode: string): Promise<void> {
    // **A new chat every time, not the one that happens to be open.** A study
    // session is a conversation, and starting one inside yesterday's exam
    // would bury it. The id is reserved rather than created, so a button
    // pressed and abandoned leaves nothing behind.
    const fresh = await onNewStudyChat()
    if (!fresh) return
    const started = await study.start(subMode, fresh)
    if (!started) return
    // Closed before sending: a sheet over the reply you just asked for is in
    // the way of the thing you asked for.
    onClose()
    onStudy(started.opener)
  }

  /** A button that would produce "there is nothing to revise" should say so
   *  itself rather than spending a turn finding out. */
  function unavailable(id: string): string | null {
    if (id === 'revision' && shaky.length === 0) return 'Nothing shaky to go over yet'
    if ((id === 'rapid' || id === 'practice' || id === 'exam') && covered.length === 0) {
      return 'Nothing covered yet'
    }
    return null
  }

  return (
    <Panel title="Study" onClose={onClose} width="max-w-lg">
      <button
        type="button"
        onClick={() => {
          void onNewStudyChat().then((id) => {
            if (id) onClose()
          })
        }}
        className="rim interactive mt-1 w-full rounded px-2 py-1.5 text-micro text-aria-muted hover:text-aria-text"
      >
        + New study chat
      </button>

      {concepts.length === 0 && !study.loading ? (
        <p className="mt-4 text-micro text-aria-faint">
          Nothing on the map yet. Start a study chat, attach a lecture, slides or notes, and ask
          her to teach you it — she will break it into concepts and keep track of how each one is
          going.
        </p>
      ) : (
        <>
          <SubjectHeader
            subject={subject}
            subjects={study.subjects}
            onSelect={study.select}
            onRename={(name) => subject && void study.rename(subject.id, name)}
            onForget={() => subject && void study.forget(subject.id)}
          onExport={exportMap}
          />

          {shaky.length > 0 && (
            <section className="mt-4">
              <h3 className="text-tiny font-strong text-aria-text">Needs revision</h3>
              <ul className="mt-1.5 space-y-1">
                {shaky.map((concept) => (
                  <ConceptRow
                    key={concept.id}
                    concept={concept}
                    onReset={() => void study.reset(concept.id)}
                  />
                ))}
              </ul>
            </section>
          )}

          <section className="mt-4">
            <h3 className="text-tiny font-strong text-aria-text">Study</h3>
            <div className="mt-1.5 grid grid-cols-3 gap-1">
              {SUB_MODES.map((mode) => {
                const blocked = unavailable(mode.id)
                return (
                  <button
                    key={mode.id}
                    type="button"
                    disabled={blocked !== null}
                    title={blocked ?? mode.hint}
                    onClick={() => void run(mode.id)}
                    className="rim interactive rounded px-2 py-1.5 text-micro text-aria-muted hover:text-aria-text disabled:opacity-30"
                  >
                    {mode.label}
                  </button>
                )
              })}
            </div>
          </section>

          <section className="mt-4">
            <h3 className="text-tiny font-strong text-aria-text">
              The map{concepts.length > 0 && ` (${concepts.length})`}
            </h3>
            <ul className="mt-1.5 space-y-1">
              {concepts.map((concept) => (
                <ConceptRow
                  key={concept.id}
                  concept={concept}
                  onReset={() => void study.reset(concept.id)}
                />
              ))}
            </ul>
          </section>

          {chats.length > 0 && (
            <section className="mt-4">
              <h3 className="text-tiny font-strong text-aria-text">Sessions</h3>
              <ul className="mt-1.5 space-y-1">
                {chats.map((chat) => (
                  <li key={chat.id}>
                    <button
                      type="button"
                      onClick={() => {
                        onClose()
                        onOpenSession(chat.id)
                      }}
                      className="raised rim interactive flex w-full items-center gap-2 rounded px-2 py-1 text-left text-micro"
                    >
                      <span className="min-w-0 flex-1 truncate text-aria-text">
                        {chat.title || chat.preview || 'Untitled study chat'}
                      </span>
                      <span className="shrink-0 tabular-nums text-aria-faint">
                        {chat.message_count} msgs
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {asked > 0 && (
            <p className="mt-3 text-micro text-aria-faint">
              {asked} answered · {right} right · {Math.round((right / asked) * 100)}%
            </p>
          )}
        </>
      )}

      {study.error && <p className="mt-3 text-tiny text-aria-bad">{study.error}</p>}
    </Panel>
  )
}
