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

/** A 16×16 dot, tinted by connection state. Avoids shipping icon assets in Phase 0. */
function statusIcon(status: BrainStatus): Electron.NativeImage {
  const color =
    status === 'connected' ? '#4ade80' : status === 'disconnected' ? '#f87171' : '#fbbf24'
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"><circle cx="8" cy="8" r="6" fill="${color}"/></svg>`
  return nativeImage.createFromDataURL(`data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`)
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
