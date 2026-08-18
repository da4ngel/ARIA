/**
 * Electron main: window, global hotkey, lifecycle, and the bridge to the sidecar.
 *
 * ZERO business logic (BUILD_SPEC §3). This process owns the window and the
 * supervised child; every decision about conversation, memory, or tasks belongs
 * to Python.
 */

import { join } from 'node:path'
import {
  app,
  BrowserWindow,
  dialog,
  globalShortcut,
  ipcMain,
  screen,
  session,
  shell,
} from 'electron'

import { type BrainStatus, RpcClient, type RpcNotification } from './rpc'
import { createOverlay, type OverlayHandle } from './overlay'
import { Sidecar } from './sidecar'
import { createTray, type TrayHandle } from './tray'

const WINDOW_WIDTH = 420
const WINDOW_HEIGHT = 600
// Expanded is for reading a long answer and browsing history side by side.
const EXPANDED_WIDTH = 900
const EXPANDED_HEIGHT = 700
const MIN_EXPANDED_WIDTH = 640
const MIN_EXPANDED_HEIGHT = 480
const SCREEN_MARGIN = 24
const FADE_STEP = 0.12
const FADE_INTERVAL_MS = 12
const RESIZE_MS = 220
const HOTKEY = 'Control+Space'
// Claimed only while she is talking, and released the moment she stops.
//
// Esc rather than Space, which was the first ask: a global Space would be
// swallowed mid-word in whatever the user is typing in. Esc costs nothing if
// it is caught by mistake, and the whole point of a key is that it beats
// saying "stop" — which cannot land in under ~1.3s, because it has to wait for
// silence and then a transcription.
const INTERRUPT_KEY = 'Escape'

// Chromium suspends renderers it believes nobody is looking at, and hiding the
// window is exactly that. She is *meant* to keep listening while dismissed, so
// the backgrounding has to be off at the process level as well as per-window
// (`backgroundThrottling` in createWindow) — the per-window flag alone does not
// stop the renderer-process backgrounder on Windows.
//
// Must be set before `whenReady`; appended later they are simply ignored.
app.commandLine.appendSwitch('disable-renderer-backgrounding')
app.commandLine.appendSwitch('disable-background-timer-throttling')
app.commandLine.appendSwitch('disable-backgrounding-occluded-windows')

const isDev = !app.isPackaged
// In dev the sources live next to out/; packaged, resources sit beside the exe.
const repoRoot = isDev ? join(app.getAppPath()) : process.resourcesPath

let window: BrowserWindow | null = null
let tray: TrayHandle | null = null
let overlay: OverlayHandle | null = null
let fadeTimer: NodeJS.Timeout | null = null
let resizeTimer: NodeJS.Timeout | null = null
let brainStatus: BrainStatus = 'starting'
let hotkeyRegistered = false
let interruptRegistered = false
// Last reported voice state, from the renderer that owns the audio.
let voiceMode: 'listening' | 'speaking' | null = null

const sidecar = new Sidecar({
  repoRoot,
  host: '127.0.0.1',
  port: 8765,
  dev: isDev,
  onReady: () => {
    // Fires on every healthy poll, not just the first. Only reconnect when the
    // token actually changed — i.e. the sidecar was respawned.
    rpc.syncToken(sidecar.getToken())
  },
  onDown: (reason) => {
    publishStatus('reconnecting')
    sendToRenderer('aria:log', { level: 'warn', message: reason })
  },
})

const rpc = new RpcClient({
  url: sidecar.rpcUrl,
  getToken: () => sidecar.getToken(),
  onStatus: publishStatus,
  onNotification: (notification: RpcNotification) => {
    // Approval is deliberately never by voice: a misheard "yes" is the only
    // thing that would stand between a file and deletion. That makes the
    // dialog the *only* way to answer, so it has to be reachable — hidden,
    // hands-free use would otherwise dead-end at a prompt nobody can see and
    // the sidecar's 120s timeout would deny it.
    if (notification.method === 'confirm.request') showWindow()
    sendToRenderer('aria:event', notification)
  },
})

// ── renderer plumbing ─────────────────────────────────────────────────

function sendToRenderer(channel: string, payload: unknown): void {
  if (window && !window.isDestroyed()) {
    window.webContents.send(channel, payload)
  }
  // The overlay reads the same event stream. It is a second view of one
  // conversation, not a second conversation.
  overlay?.send(channel, payload)
}

const launchedAt = Date.now()
let lastStatusAt = launchedAt

/**
 * Status transitions are logged with elapsed time because two Phase 0 gate
 * criteria are timing claims ("connected within 3s", "recovers within 15s").
 * Appendix B: measured, not assumed.
 */
function publishStatus(status: BrainStatus): void {
  if (status !== brainStatus) {
    const now = Date.now()
    process.stdout.write(
      `[brain] ${brainStatus} -> ${status} ` +
        `(+${now - lastStatusAt}ms, ${now - launchedAt}ms since launch)\n`,
    )
    lastStatusAt = now
  }
  brainStatus = status
  tray?.setStatus(status)
  sendToRenderer('aria:status', status)
}

// ── window ────────────────────────────────────────────────────────────

function bottomRightPosition(): { x: number; y: number } {
  const { workArea } = screen.getPrimaryDisplay()
  return {
    x: workArea.x + workArea.width - WINDOW_WIDTH - SCREEN_MARGIN,
    y: workArea.y + workArea.height - WINDOW_HEIGHT - SCREEN_MARGIN,
  }
}

// ── compact / expanded ────────────────────────────────────────────────
// Compact is the companion: small, pinned bottom-right, always on top.
// Expanded is a real working window: bigger, centred, resizable, and *not*
// floating — something you are reading in should not sit over your other work.

let expanded = false

function centredExpandedBounds(): { x: number; y: number; width: number; height: number } {
  const { workArea } = screen.getPrimaryDisplay()
  const width = Math.min(EXPANDED_WIDTH, workArea.width - SCREEN_MARGIN * 2)
  const height = Math.min(EXPANDED_HEIGHT, workArea.height - SCREEN_MARGIN * 2)
  return {
    width,
    height,
    x: workArea.x + Math.round((workArea.width - width) / 2),
    y: workArea.y + Math.round((workArea.height - height) / 2),
  }
}

/** Animate bounds over `RESIZE_MS`. `setBounds(..., true)` animates on macOS
 *  only, so Windows needs this done by hand or the window teleports. */
function animateBounds(
  win: BrowserWindow,
  to: { x: number; y: number; width: number; height: number },
): void {
  if (resizeTimer) clearInterval(resizeTimer)
  const from = win.getBounds()
  const started = Date.now()

  resizeTimer = setInterval(() => {
    if (!window || window.isDestroyed()) {
      if (resizeTimer) clearInterval(resizeTimer)
      resizeTimer = null
      return
    }
    const t = Math.min(1, (Date.now() - started) / RESIZE_MS)
    // Same easing as the fade, so growing and appearing feel like one system.
    const eased = 1 - Math.pow(1 - t, 3)
    window.setBounds({
      x: Math.round(from.x + (to.x - from.x) * eased),
      y: Math.round(from.y + (to.y - from.y) * eased),
      width: Math.round(from.width + (to.width - from.width) * eased),
      height: Math.round(from.height + (to.height - from.height) * eased),
    })
    if (t >= 1) {
      if (resizeTimer) clearInterval(resizeTimer)
      resizeTimer = null
    }
  }, FADE_INTERVAL_MS)
}

function setExpanded(next: boolean): boolean {
  const win = window
  if (!win || win.isDestroyed()) return expanded
  if (next === expanded) return expanded
  expanded = next

  // Resizable must be set before the animation, or the manual setBounds calls
  // are clamped to the old fixed size and the window never grows.
  win.setResizable(next)
  win.setMaximizable(next)
  win.setAlwaysOnTop(!next, 'floating')
  win.setSkipTaskbar(!next)

  if (next) {
    win.setMinimumSize(MIN_EXPANDED_WIDTH, MIN_EXPANDED_HEIGHT)
    animateBounds(win, centredExpandedBounds())
  } else {
    win.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    animateBounds(win, { ...bottomRightPosition(), width: WINDOW_WIDTH, height: WINDOW_HEIGHT })
  }

  sendToRenderer('aria:window-mode', next)
  return expanded
}

function createWindow(): BrowserWindow {
  const { x, y } = bottomRightPosition()

  const win = new BrowserWindow({
    width: WINDOW_WIDTH,
    height: WINDOW_HEIGHT,
    x,
    y,
    show: false,
    frame: false,
    // Real Windows 11 acrylic, not a CSS approximation. `backdrop-filter` in the
    // renderer cannot blur the *desktop* behind a window — with `transparent`
    // it simply showed whatever was underneath, so text from the editor behind
    // read straight through the conversation. `backgroundMaterial` is composited
    // by DWM and actually blurs.
    //
    // It requires `transparent: false`, and it requires the window's own
    // background to be **transparent** — an opaque `backgroundColor`
    // composites straight over the DWM material and hides it completely.
    // That is why "glass everywhere" looked like a flat dark rectangle: the
    // acrylic was being applied and then painted over on every frame.
    //
    // The dark fallback for machines that will not apply acrylic (Windows 10,
    // or transparency effects switched off) moves into CSS, where it sits
    // *under* the tint instead of over the material.
    transparent: false,
    backgroundColor: '#00000000',
    backgroundMaterial: 'acrylic',
    alwaysOnTop: true,
    resizable: false,
    maximizable: false,
    fullscreenable: false,
    skipTaskbar: true,
    opacity: 0,
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
      // The microphone lives in this renderer, and `hideWindow` hides this
      // window. Throttled, the capture stalls and "aria" goes unheard while she
      // is dismissed — which is the state she spends most of her time in.
      backgroundThrottling: false,
    },
  })

  win.setAlwaysOnTop(true, 'floating')

  // External links open in the real browser, never inside the assistant window.
  win.webContents.setWindowOpenHandler(({ url }) => {
    void shell.openExternal(url)
    return { action: 'deny' }
  })

  if (isDev && process.env.ELECTRON_RENDERER_URL) {
    void win.loadURL(process.env.ELECTRON_RENDERER_URL)
  } else {
    void win.loadFile(join(__dirname, '../renderer/index.html'))
  }

  win.on('closed', () => {
    window = null
  })

  return win
}

/**
 * Content-Security-Policy, set here rather than in index.html so dev and
 * production can differ. Production pins connect-src to 'none': the renderer
 * must never open a socket of its own to the sidecar port.
 */
function applyCsp(): void {
  const policy = isDev
    ? "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; " +
      "style-src 'self' 'unsafe-inline'; img-src 'self' data:; " +
      'connect-src http://localhost:* ws://localhost:*'
    : "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; " +
      "img-src 'self' data:; connect-src 'none'"

  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [policy],
      },
    })
  })
}

// ── show / hide with a fade ───────────────────────────────────────────
// Driven from main via setOpacity rather than CSS, so the hotkey feels instant
// even before React has mounted.

function fadeTo(target: number, onDone?: () => void): void {
  const win = window
  if (!win) return
  if (fadeTimer) clearInterval(fadeTimer)

  fadeTimer = setInterval(() => {
    if (!window || window.isDestroyed()) {
      if (fadeTimer) clearInterval(fadeTimer)
      fadeTimer = null
      return
    }
    const current = window.getOpacity()
    const next = current < target ? Math.min(current + FADE_STEP, target) : Math.max(current - FADE_STEP, target)
    window.setOpacity(next)

    if (Math.abs(next - target) < 0.001) {
      if (fadeTimer) clearInterval(fadeTimer)
      fadeTimer = null
      onDone?.()
    }
  }, FADE_INTERVAL_MS)
}

function showWindow(): void {
  if (!window || window.isDestroyed()) window = createWindow()
  // Only the compact window re-homes itself to the corner. Expanded is a window
  // the user has placed and sized, and yanking it back would undo that.
  if (!expanded) {
    const { x, y } = bottomRightPosition()
    window.setPosition(x, y)
  }
  window.showInactive()
  window.focus()
  fadeTo(1)
  syncOverlay()
}

function hideWindow(): void {
  if (!window || window.isDestroyed()) return
  fadeTo(0, () => {
    window?.hide()
    // After the hide, not before: `syncOverlay` reads `isVisible()`.
    syncOverlay()
  })
}

/**
 * The overlay is her presence *instead of* the window, never alongside it.
 *
 * With the window open, `VoiceAura` inside it already shows the same state;
 * lighting the screen edge as well would be one thing said twice, and a glow
 * around a window you are looking at is just glare.
 */
/**
 * Own Esc for exactly as long as she is speaking.
 *
 * Registering it permanently would take Esc away from every other app on the
 * machine, which is far too high a price for a stop button.
 */
function syncInterruptKey(): void {
  const speaking = voiceMode === 'speaking'
  if (speaking === interruptRegistered) return

  if (speaking) {
    interruptRegistered = globalShortcut.register(INTERRUPT_KEY, () => {
      // The sidecar owns the stop, the cancel and the state change; this only
      // reports the key press (BUILD_SPEC §3).
      void rpc.call('voice.interrupt', {}).catch(() => {
        /* she may have finished on her own between press and dispatch */
      })
    })
  } else {
    globalShortcut.unregister(INTERRUPT_KEY)
    interruptRegistered = false
  }
}

function syncOverlay(): void {
  const windowShown = Boolean(window && !window.isDestroyed() && window.isVisible())
  overlay?.setVisible(voiceMode !== null && !windowShown)
}

function toggleWindow(): void {
  if (window?.isVisible() && window.getOpacity() > 0.5) hideWindow()
  else showWindow()
}

// ── IPC surface (mirrors preload) ─────────────────────────────────────

function registerIpc(): void {
  // Notifications are `send`, not `handle`: nothing comes back, so there is
  // no promise for the renderer to await twelve times a second.
  ipcMain.on('aria:notify', (_event, method: string, params: Record<string, unknown>) => {
    rpc.notify(method, params)
  })

  ipcMain.handle('aria:call', async (_event, method: string, params: Record<string, unknown>) => {
    return rpc.call(method, params ?? {})
  })
  // ~30 a second while she is talking or being talked to, and nothing at all
  // otherwise. `send`, not `handle`, for the same reason audio frames are.
  ipcMain.on(
    'aria:voice-level',
    (_event, level: number, mode: 'listening' | 'speaking' | null) => {
      if (mode !== voiceMode) {
        voiceMode = mode
        syncOverlay()
        syncInterruptKey()
      }
      overlay?.send('aria:voice-level', { level, mode })
    },
  )

  ipcMain.handle('aria:status', () => brainStatus)
  ipcMain.on('aria:restart-brain', () => {
    publishStatus('reconnecting')
    sidecar.restart()
  })
  ipcMain.on('aria:hide', () => hideWindow())
  // Straight to the taskbar, no fade: minimize has its own animation and
  // fading first makes the window appear to stutter on the way down.
  ipcMain.on('aria:minimize', () => {
    if (window && !window.isDestroyed()) window.minimize()
  })
  ipcMain.handle('aria:set-expanded', (_event, next: boolean) => setExpanded(Boolean(next)))
  ipcMain.handle('aria:is-expanded', () => expanded)
  // The only filesystem-shaped channel in the preload, and it deliberately
  // returns *paths* rather than contents: the renderer never reads a file,
  // the sidecar does. The dialog is the consent — nothing here can open
  // anything the user did not pick in their own file browser.
  ipcMain.handle('aria:pick-files', async () => {
    if (!window || window.isDestroyed()) return []
    const result = await dialog.showOpenDialog(window, {
      title: 'Attach files',
      properties: ['openFile', 'multiSelections'],
    })
    return result.canceled ? [] : result.filePaths
  })
}

function registerHotkey(): void {
  hotkeyRegistered = globalShortcut.register(HOTKEY, toggleWindow)
  if (!hotkeyRegistered) {
    // Never fail silently — the user would just think the app is broken.
    const message =
      `Could not register the ${HOTKEY} hotkey; another app already owns it ` +
      `(common culprits: IME language switchers, launchers). ` +
      `Use the tray icon to show Aria, or free the shortcut and restart.`
    process.stderr.write(`${message}\n`)
    tray?.setHotkeyError(message)
  }
}

// ── lifecycle ─────────────────────────────────────────────────────────

const singleInstance = app.requestSingleInstanceLock()
if (!singleInstance) {
  app.quit()
} else {
  app.on('second-instance', showWindow)

  void app.whenReady().then(async () => {
    applyCsp()
    registerIpc()

    window = createWindow()
    // Built up front rather than on the first wake word: constructing a window
    // and loading a page does not fit inside the 300ms reaction budget.
    overlay = createOverlay({ isDev })
    tray = createTray({
      onShow: showWindow,
      onSettings: showWindow, // no Settings panel until Phase 9
      onRestartBrain: () => {
        publishStatus('reconnecting')
        sidecar.restart()
      },
      onQuit: () => app.quit(),
    })
    registerHotkey()

    publishStatus('starting')
    try {
      await sidecar.start()
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error)
      publishStatus('disconnected')
      sendToRenderer('aria:log', { level: 'error', message })
      process.stderr.write(`${message}\n`)
    }
    rpc.start()

    showWindow()
  })

  app.on('window-all-closed', () => {
    // The tray keeps her alive; closing the window is not quitting.
  })

  app.on('will-quit', () => {
    overlay?.destroy()
    globalShortcut.unregisterAll()
    rpc.stop()
    sidecar.stop()
  })
}
