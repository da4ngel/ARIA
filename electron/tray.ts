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
 * Regenerate with scripts/make_tray_icons.py if the palette changes.
 */
const ICON_PNG: Record<'ok' | 'warn' | 'bad', string> = {
  ok: 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAsUlEQVR42u2X0Q2AIAwFGYV5nIIRGMFNGIVNXKEjICaYEBKkwTatho/7Ico7QoVqtmM3kpgl8DUBm/GZmIFMKkAZ8+UZcoFr0lAFjghYEUy4a1aLBcq7rwTcRHCLmxWgCB9KPO05EApAryZ6AoEwvC5MlIBlCL+xGAHPKOAxApFRIGIEgFEAMAKJGf0C4lsgXoTin6H4QSR+FKu4jMSvYxUNiYqWTEVTqqItX39G/xU4Af7VYrmYWVqIAAAAAElFTkSuQmCC',
  warn: 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAArklEQVR42u2XwQ2AIAxFGYWDgzFCN2IURuoAHhATTAgJ0mCbVuPhXYjyH6FCdXvanCbuF3ibgC9AIRWwkCtYx6A+wy5wThqbwBmRKkIJD91qqWB995FAWAjuCasCHOFTibs9R0YBHNXESCAyhreFSRLwAuEXniIAggJAEUiCAokigIICSBHIwtgXUN8C9SJU/wzVDyL1o9jEZaR+HZtoSEy0ZCaaUhNt+f9n9F2BA4UyOsg+wFQsAAAAAElFTkSuQmCC',
  bad: 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAArUlEQVR42u2XwQ2AIAxFGYXRGAEmYhRG6tUbYoIJIUEabNNqOLwLUf4jVKjmCMFIYrbA1wRswRdSAQq5AnXM12fIBa5JYxM4I2JFMOGuWy0WqO++EnALwT1uVYAifCrxtOdAKACjmhgJRMLwtjBRApYh/MZiBDyjgMcIJEaBhBEARgHACGRm9AuIb4F4EYp/huIHkfhRrOIyEr+OVTQkKloyFU2pirZ8/xn9V+AENZQqyAFzoywAAAAASUVORK5CYII=',
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
