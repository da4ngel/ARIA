/**
 * Auto-update from GitHub Releases (BUILD_SPEC §9 Phase 9, after the fact).
 *
 * Most of this was already in place before a line was written: electron-builder
 * infers `app-update.yml` from the git remote, so every build already ships
 * `provider: github, owner: da4ngel, repo: ARIA`, and writes `latest.yml` with
 * the version, size and sha512 beside the installer. **The repo is public**,
 * which is what makes this simple — release assets need no token, so nothing
 * secret has to ship inside the app.
 *
 * The flow, decided with Eyaas: download quietly, then *offer* a restart.
 * `autoInstallOnAppQuit` means somebody who never clicks anything still ends
 * up updated the next time they quit normally. Nothing ever interrupts a
 * conversation to install something.
 *
 * **Unsigned.** electron-updater checks a downloaded installer's publisher
 * name against the installed app's signature; with no certificate there is no
 * publisher name to check against, so that check does not apply. What is left
 * guarding the download is HTTPS plus the sha512 in `latest.yml` — which
 * means anyone who can push to the repo can ship code to every install. That
 * is the honest cost of not having a certificate, and it is stated here
 * rather than discovered.
 */

import { app } from 'electron'

/** What the UI renders. One shape, so the card never has to infer a state. */
export interface UpdateStatus {
  state: 'idle' | 'checking' | 'available' | 'downloading' | 'ready' | 'none' | 'error'
  /** The running version, always — the card leads with it. */
  current: string
  /** The version found, when there is one. */
  next?: string
  /** 0–100 while downloading. */
  percent?: number
  message?: string
}

export interface UpdaterOptions {
  onStatus: (status: UpdateStatus) => void
}

/** Six hours. Long enough to be invisible, short enough that a machine left
 *  running for a week is not a week behind. */
const CHECK_INTERVAL_MS = 6 * 60 * 60 * 1000

/** Give the app a moment to finish starting before spending bandwidth. */
const FIRST_CHECK_DELAY_MS = 20_000

export class Updater {
  private timer: NodeJS.Timeout | null = null
  private startTimer: NodeJS.Timeout | null = null
  private status: UpdateStatus
  // Loaded lazily so a dev run never imports it at all — see `start`.
  private updater: import('electron-updater').AppUpdater | null = null

  constructor(private readonly options: UpdaterOptions) {
    this.status = { state: 'idle', current: app.getVersion() }
  }

  get current(): UpdateStatus {
    return this.status
  }

  /** True in a packaged app only. Everything else is a no-op that says so. */
  get supported(): boolean {
    return app.isPackaged
  }

  start(): void {
    if (!this.supported) return
    // `require` rather than a top-level import: electron-updater reads
    // `app-update.yml` when the module loads, which does not exist in a dev
    // tree, and the throw would come out of the import rather than a call.
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { autoUpdater } = require('electron-updater') as typeof import('electron-updater')
    this.updater = autoUpdater

    autoUpdater.autoDownload = true
    // Somebody who never clicks the button still ends up updated, the next
    // time they quit for their own reasons.
    autoUpdater.autoInstallOnAppQuit = true
    autoUpdater.logger = null

    autoUpdater.on('checking-for-update', () => this.publish({ state: 'checking' }))
    autoUpdater.on('update-available', (info) =>
      this.publish({ state: 'available', next: info.version }),
    )
    autoUpdater.on('update-not-available', () => this.publish({ state: 'none' }))
    autoUpdater.on('download-progress', (progress) =>
      this.publish({ state: 'downloading', percent: Math.round(progress.percent) }),
    )
    autoUpdater.on('update-downloaded', (info) =>
      this.publish({ state: 'ready', next: info.version }),
    )
    autoUpdater.on('error', (error) =>
      // **Not an error the user has to act on.** This app is built to work
      // with no network at all; a failed check is the normal state of a
      // machine that is offline, and it belongs in the card rather than in a
      // dialog.
      this.publish({ state: 'error', message: error?.message ?? String(error) }),
    )

    this.startTimer = setTimeout(() => void this.check(), FIRST_CHECK_DELAY_MS)
    this.timer = setInterval(() => void this.check(), CHECK_INTERVAL_MS)
  }

  /** The button. Resolves with whatever the run ended on. */
  async check(): Promise<UpdateStatus> {
    if (!this.updater) {
      return this.publish({
        state: 'error',
        message: this.supported
          ? 'The updater has not started yet. Try again in a moment.'
          : 'Updates only apply to an installed ARIA — this is a development build.',
      })
    }
    try {
      await this.updater.checkForUpdates()
    } catch (error) {
      this.publish({ state: 'error', message: error instanceof Error ? error.message : String(error) })
    }
    return this.status
  }

  /**
   * Quit and install what was downloaded.
   *
   * **The caller must have stopped the sidecar and waited for it first.**
   * The installer overwrites `resources/sidecar/aria-sidecar.exe`, and
   * Windows will not overwrite a file a live process still holds open — so
   * this is deliberately not the thing that shuts anything down. See
   * `Sidecar.stopAndWait`.
   */
  quitAndInstall(): void {
    this.updater?.quitAndInstall()
  }

  stop(): void {
    if (this.timer) clearInterval(this.timer)
    if (this.startTimer) clearTimeout(this.startTimer)
    this.timer = null
    this.startTimer = null
  }

  private publish(next: Partial<UpdateStatus>): UpdateStatus {
    // `current` is re-read every time rather than captured once: after an
    // install the app restarts, and a stale number here would be the first
    // thing anybody noticed.
    this.status = { ...this.status, current: app.getVersion(), ...next }
    this.options.onStatus(this.status)
    return this.status
  }
}
