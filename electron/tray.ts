/**
 * System tray: Show, Settings, Restart Brain, Quit (BUILD_SPEC §9 Phase 0).
 *
 * The tray is how Aria stays reachable when the window is hidden, and it is the
 * fallback when the global hotkey could not be registered.
 */

import { Menu, nativeImage, Tray } from 'electron'

import type { BrainStatus } from './rpc'

export interface TrayCallbacks {
  onShow: () => void
  onSettings: () => void
  onRestartBrain: () => void
  onQuit: () => void
}

export interface TrayHandle {
  setStatus: (status: BrainStatus) => void
  setHotkeyError: (message: string) => void
  destroy: () => void
}

const STATUS_LABEL: Record<BrainStatus, string> = {
  starting: 'Brain: starting…',
  connecting: 'Brain: connecting…',
  connected: 'Brain: connected',
  reconnecting: 'Brain: reconnecting…',
  disconnected: 'Brain: disconnected',
}

/**
 * A 32×32 dot, tinted by connection state.
 *
 * These are real PNGs, embedded as base64. Electron's nativeImage cannot decode
 * SVG — createFromDataURL on an image/svg+xml URL silently returns an *empty*
 * image, which on Windows produces a tray entry that is present and clickable
 * but invisible. Embedding rather than loading from resources/ also keeps the
 * icon working identically in dev and in the packaged app, where that directory
 * moves.
 *
 * Regenerate with scripts/make_tray_icons.py if the palette changes — the
 * script reads `src/styles/tokens.js` itself now, and `tray.test.ts` decodes
 * these pixels back and fails if they have drifted. Both exist because this
 * file sat a whole retheme behind for days: the tray was the only surface
 * with no test and no screenshot, so nothing said so.
 */
const ICON_PNG: Record<'ok' | 'warn' | 'bad', string> = {
  ok: 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAsElEQVR42u2XwQ2AIAxFGYWtvDICc7gEozCEg3QExAQTQoI02KbVcHgXovxHqFDNduxGErMEviZgMz4TM5BJBShjvjxDLnBNGqrAEQErggl3zWqxQHn3lYCbCG5xswIU4UOJpz0HQgHo1URPIBCG14WJErAM4TcWI+AZBTxGIDIKRIwAMAoARiAxo19AfAvEi1D8MxQ/iMSPYhWXkfh1rKIhUdGSqWhKVbTl68/ovwInOZGSuRyanTgAAAAASUVORK5CYII=',
  warn: 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAsElEQVR42u2XwQ2AIAxFGYVBHIYR2IgdXIB1vHUExAQTQoI02KbVcHgXovxHqFDNsW9GErMEviZgMz4TM5BJBShjvjxDLnBNGqrAEQErggl3zWqxQHn3lYCbCG5xswIU4UOJpz0HQgHo1URPIBCG14WJErAM4TcWI+AZBTxGIDIKRIwAMAoARiAxo19AfAvEi1D8MxQ/iMSPYhWXkfh1rKIhUdGSqWhKVbTl68/ovwInugUayGF+IpYAAAAASUVORK5CYII=',
  bad: 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAArklEQVR42u2XYQqAIAxGPYpH8wQhdCCP4pHWDczAQARz2MZW+OP9kfJ74tJljn0zkpgl8DUBm/GZmIFMKkAZ8+UZcoFr0lAFjghYEUy4a1aLBcq7rwTcRHCLmxWgCB9KPO05EApAryZ6AoEwvC5MlIBlCL+xGAHPKOAxApFRIGIEgFEAMAKJGf0C4lsgXoTin6H4QSR+FKu4jMSvYxUNiYqWTEVTqqItX39G/xU4Ab6HBsixgmo0AAAAAElFTkSuQmCC',
}

function statusIcon(status: BrainStatus): Electron.NativeImage {
  const key = status === 'connected' ? 'ok' : status === 'disconnected' ? 'bad' : 'warn'
  const image = nativeImage.createFromBuffer(Buffer.from(ICON_PNG[key], 'base64'))
  // Windows draws the tray at 16pt; hand it a downscaled copy rather than
  // letting the shell nearest-neighbour a 32px bitmap.
  return image.resize({ width: 16, height: 16, quality: 'best' })
}

export function createTray(callbacks: TrayCallbacks): TrayHandle {
  const tray = new Tray(statusIcon('starting'))
  let status: BrainStatus = 'starting'
  let hotkeyError: string | null = null

  const render = (): void => {
    tray.setImage(statusIcon(status))
    tray.setToolTip(hotkeyError ? `Aria — ${STATUS_LABEL[status]}\n${hotkeyError}` : `Aria — ${STATUS_LABEL[status]}`)
    tray.setContextMenu(
      Menu.buildFromTemplate([
        { label: STATUS_LABEL[status], enabled: false },
        ...(hotkeyError ? [{ label: 'Ctrl+Space unavailable', enabled: false }] : []),
        { type: 'separator' },
        { label: 'Show', click: callbacks.onShow },
        { label: 'Settings', click: callbacks.onSettings },
        { label: 'Restart Brain', click: callbacks.onRestartBrain },
        { type: 'separator' },
        { label: 'Quit', click: callbacks.onQuit },
      ]),
    )
  }

  tray.on('click', callbacks.onShow)
  render()

  return {
    setStatus: (next) => {
      if (next === status) return
      status = next
      render()
    },
    setHotkeyError: (message) => {
      hotkeyError = message
      render()
    },
    destroy: () => tray.destroy(),
  }
}
