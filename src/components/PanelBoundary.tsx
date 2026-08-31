/**
 * One panel failing must not blank the whole window.
 *
 * **Found by feeding `ClipboardPanel` a payload with one field renamed.** It
 * threw on `entry.content.replace`, React unmounted the entire tree, and the
 * app became an empty rectangle — the same symptom as the retheme's blank
 * window, from a completely different cause. There was no error boundary
 * anywhere in this app; React's own console message said so.
 *
 * The panels are the right place for one. They are the surfaces that render
 * whatever the sidecar last returned, they are the ones that grow a field per
 * phase, and CLAUDE.md already has this lesson once — `useStudy` guards with
 * `?? []` because "a panel that throws takes the whole rail section down".
 * That fix was per-panel and per-field. This is the general form.
 *
 * It deliberately does **not** wrap the conversation. A boundary there would
 * turn a crash in the thing you are actually reading into a quiet placeholder,
 * and losing a reply silently is worse than losing it loudly.
 */

import { Component, type ReactNode } from 'react'

interface Props {
  /** Named so the message can say which panel, not just "a panel". */
  name: string
  onClose: () => void
  children: ReactNode
}

interface State {
  error: Error | null
}

export class PanelBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error): void {
    // The main process appends this to `data/logs/electron.log`, which
    // `system.diagnostics` collects — so a panel that failed once on
    // somebody's machine is still answerable afterwards.
    console.error(`[panel] ${this.props.name} failed`, error)
  }

  // A different panel is a different subtree; without this, one failure
  // would leave every later panel showing the first one's error.
  componentDidUpdate(previous: Props): void {
    if (previous.name !== this.props.name && this.state.error) {
      this.setState({ error: null })
    }
  }

  render(): ReactNode {
    if (!this.state.error) return this.props.children
    return (
      <div className="pop rim absolute right-4 top-16 z-40 max-w-sm rounded-xl px-3 py-2.5">
        <p className="text-small font-medium text-aria-bad">The {this.props.name} panel failed</p>
        <p className="mt-1 text-micro leading-relaxed text-aria-muted">
          {/* The message, not a stack: a stack is for the log, and a person
              reading this needs to know the rest of the app still works. */}
          {this.state.error.message}
        </p>
        <p className="mt-1 text-micro text-aria-faint">
          Everything else still works. Settings &rsaquo; Export diagnostics has the details.
        </p>
        <button
          type="button"
          onClick={this.props.onClose}
          className="rim interactive mt-2 rounded-lg px-2 py-1 text-micro text-aria-text"
        >
          Close
        </button>
      </div>
    )
  }
}
