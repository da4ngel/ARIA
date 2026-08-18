/**
 * What was said, while the window is put away.
 *
 * Without this the hidden conversation is audio only: fine for "what time is
 * it", useless the moment you mishear a name or a number. It is deliberately
 * *not* the transcript — one exchange, the current one, and then it goes away.
 * Anything more belongs in the window, which is one keypress away.
 */

import { AnimatePresence, motion } from 'framer-motion'

import { SPRING } from '@/styles/motion'

interface Props {
  /** What the sidecar heard. Empty until a turn starts. */
  asked: string
  /** Her reply, streaming in. */
  reply: string
  /** Speech she captured and then discarded because it did not name her.
   *  Shown dimly and briefly: not an answer, but not nothing either. */
  misheard?: string
}

export function Caption({ asked, reply, misheard }: Props): JSX.Element {
  const showing = Boolean(asked || reply || misheard)

  return (
    <AnimatePresence>
      {showing && (
        <motion.div
          // Bottom third rather than centre: the middle of the screen is where
          // the user's actual work is, and this is commentary on it.
          className="pointer-events-none fixed inset-x-0 bottom-[12vh] flex justify-center px-8"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={SPRING.settle}
        >
          {/* Text follows the palette; the background deliberately does not.
              This card floats over an arbitrary desktop, not over the app's
              glass, so its job is legibility against unknown pixels, and
              tokenising it would tie it to a palette tuned for a surface it
              never sits on. */}
          <div
            className={`max-w-[46rem] rounded-2xl px-5 py-3.5 text-center shadow-2xl backdrop-blur-xl ${
              misheard && !asked && !reply
                ? // A miss is information, not an answer. Dimmer, quieter,
                  // and gone in a couple of seconds.
                  'bg-black/45 ring-1 ring-white/5'
                : 'bg-black/65 ring-1 ring-white/10'
            }`}
          >
            {misheard && !asked && !reply && (
              <p className="text-small italic leading-relaxed text-aria-faint">
                heard {'“'}
                {misheard}
                {'”'}
              </p>
            )}
            {asked && (
              <p className="text-small leading-relaxed text-aria-dim">
                {'“'}
                {asked}
                {'”'}
              </p>
            )}
            {reply && (
              <p
                className={`text-body leading-relaxed text-aria-text ${asked ? 'mt-1.5' : ''}`}
                // Long answers are spoken, not read. Clamping keeps this a
                // caption instead of a wall of text over someone's screen.
                style={{
                  display: '-webkit-box',
                  WebkitLineClamp: 4,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                }}
              >
                {reply}
              </p>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
