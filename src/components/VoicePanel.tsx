/**
 * Hands-free, with room to say what it actually does.
 *
 * The header toggle stays — it is a one-click thing used constantly — but a
 * switch that opens the microphone permanently deserves more than a tooltip.
 * This is where the wake phrase, the shortcuts and the current state are
 * written down.
 */

import { Panel } from '@/components/Panel'
import type { UseHandsFree } from '@/hooks/useHandsFree'

export function VoicePanel({
  handsFree,
  onClose,
}: {
  handsFree: UseHandsFree
  onClose: () => void
}): JSX.Element {
  const { available, phrase, active, error, toggle } = handsFree

  return (
    <Panel title="Voice" onClose={onClose}>
      {!available ? (
        <p className="text-tiny leading-relaxed text-aria-muted">
          Voice is off. The speech model could not be loaded, so she cannot listen or speak — the
          sidecar log names the file that is missing. Typing still works, and so does push-to-talk
          if a microphone is available.
        </p>
      ) : (
        <>
          <button
            type="button"
            role="switch"
            aria-checked={active}
            onClick={toggle}
            className={`rim interactive flex w-full items-center justify-between gap-3 rounded-xl px-3 py-2.5 text-left ${
              active ? 'bg-aria-listening/10' : 'raised'
            }`}
          >
            <span className="min-w-0">
              <span
                className={`block text-small font-medium ${
                  active ? 'text-aria-listening' : 'text-aria-text'
                }`}
              >
                {active ? 'Listening' : 'Hands-free is off'}
              </span>
              <span className="mt-0.5 block text-micro text-aria-muted">
                {active ? (
                  <>
                    Say <span className="text-aria-text">“{phrase}”</span> and then your question.
                  </>
                ) : (
                  'The microphone stays closed until you turn this on.'
                )}
              </span>
            </span>
            <span
              aria-hidden
              className={`relative h-5 w-9 shrink-0 rounded-full transition-colors ${
                active ? 'bg-aria-listening/50' : 'bg-white/10'
              }`}
            >
              <span
                className={`absolute top-0.5 h-4 w-4 rounded-full bg-aria-text transition-all ${
                  active ? 'left-[1.125rem]' : 'left-0.5'
                }`}
              />
            </span>
          </button>

          {/* Said plainly, because Windows shows its own microphone indicator
              and the app staying quiet about why would be the dishonest half. */}
          <p className="mt-2 text-micro leading-relaxed text-aria-muted">
            While this is on the microphone is open continuously. Audio is only sent to the sidecar
            on this machine, and only a turn that starts with her name is answered.
          </p>

          <dl className="mt-4 space-y-1.5 text-micro">
            <Row term="Wake phrase" detail={`“${phrase}”`} />
            <Row term="Interrupt her" detail="Esc, or just start talking" />
            <Row term="Push to talk" detail="Ctrl+Space, without hands-free" />
            <Row term="Approving an action" detail="Always by hand — never by voice" />
          </dl>
        </>
      )}

      {error && <p className="mt-3 text-tiny text-aria-bad">{error}</p>}
    </Panel>
  )
}

function Row({ term, detail }: { term: string; detail: string }): JSX.Element {
  return (
    <div className="flex items-baseline gap-3">
      <dt className="w-32 shrink-0 text-aria-faint">{term}</dt>
      <dd className="min-w-0 flex-1 text-aria-muted">{detail}</dd>
    </div>
  )
}
