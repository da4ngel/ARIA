/**
 * The screen-edge overlay: her presence when the window is put away.
 *
 * A second window covering the whole primary display, drawing only at the
 * edges. Everything about it is arranged so it is *seen and never felt* —
 * clicks pass through, focus is never taken, and it stays out of the taskbar
 * and out of Alt+Tab. If any of that stops being true it becomes an obstacle
 * sitting permanently on top of the user's work, which is much worse than
 * having no overlay at all.
 *
 * It exists only while she is listening or speaking *and* the main window is
 * hidden. With the window open, `VoiceAura` inside it already says the same
 * thing, and two indicators saying one thing is a bug.
 *
 * Like the main window it disables background throttling, but for the opposite
 * reason: this one animates, and a throttled rAF turns the glow into a
 * slideshow the moment focus goes elsewhere — which is always, since it never
 * takes focus.
 */

import { join } from 'node:path'

import { BrowserWindow, screen } from 'electron'

export interface OverlayHandle {
  /** Show or hide, driven by assistant state. Cheap to call repeatedly. */
  setVisible: (visible: boolean) => void
  /** Push a payload to the overlay renderer. */
  send: (channel: string, payload: unknown) => void
  window: () => BrowserWindow | null
  destroy: () => void
}

export function createOverlay(options: { isDev: boolean }): OverlayHandle {
  let win: BrowserWindow | null = null
  let visible = false

  const build = (): BrowserWindow => {
    // `bounds`, not `workArea`: the glow traces the physical edge of the
    // display, so it must sit under the taskbar rather than stop above it.
    const { bounds } = screen.getPrimaryDisplay()

    const overlay = new BrowserWindow({
      ...bounds,
      show: false,
      frame: false,
      transparent: true,
      // No `backgroundMaterial` here. CLAUDE.md records that acrylic requires
      // `transparent: false`; this window needs the opposite, and a real
      // alpha channel is the entire point.
      backgroundColor: '#00000000',
      hasShadow: false,
      resizable: false,
      movable: false,
      minimizable: false,
      maximizable: false,
      fullscreenable: false,
      skipTaskbar: true,
      // Never steal the caret from whatever the user is typing in.
      focusable: false,
      // Keeps it out of Alt+Tab on Windows.
      type: 'toolbar',
      webPreferences: {
        preload: join(__dirname, '../preload/index.js'),
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: true,
        webSecurity: true,
        backgroundThrottling: false,
      },
    })

    // Above full-screen apps, not merely above normal windows.
    overlay.setAlwaysOnTop(true, 'screen-saver')
    // `forward: true` keeps hover events flowing to the page while every click
    // lands on whatever is underneath.
    overlay.setIgnoreMouseEvents(true, { forward: true })
    overlay.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true })

    if (options.isDev && process.env.ELECTRON_RENDERER_URL) {
      void overlay.loadURL(`${process.env.ELECTRON_RENDERER_URL}/overlay.html`)
    } else {
      void overlay.loadFile(join(__dirname, '../renderer/overlay.html'))
    }

    overlay.on('closed', () => {
      win = null
      visible = false
    })

    return overlay
  }

  const ensure = (): BrowserWindow => {
    if (!win || win.isDestroyed()) win = build()
    return win
  }

  // Built now and kept, never on first use: constructing a window and loading
  // a page does not fit inside the 300ms budget between the wake word and a
  // visible reaction. It sits hidden until there is something to show.
  ensure()

  // A display change moves the edges. Re-home rather than glowing around where
  // the screen used to be.
  screen.on('display-metrics-changed', () => {
    if (win && !win.isDestroyed()) win.setBounds(screen.getPrimaryDisplay().bounds)
  })

  return {
    setVisible(next: boolean): void {
      if (next === visible) return
      visible = next
      const overlay = ensure()
      if (next) {
        // `showInactive`, never `show`: showing would activate it, and a
        // window that cannot be focused being activated drops the user's
        // caret on the floor.
        overlay.showInactive()
        overlay.setAlwaysOnTop(true, 'screen-saver')
      } else {
        overlay.hide()
      }
    },

    send(channel: string, payload: unknown): void {
      if (win && !win.isDestroyed()) win.webContents.send(channel, payload)
    },

    window: () => win,

    destroy(): void {
      if (win && !win.isDestroyed()) win.destroy()
      win = null
      visible = false
    },
  }
}
