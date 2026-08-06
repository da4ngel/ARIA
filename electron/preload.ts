/**
 * The entire surface the renderer is allowed to touch (BUILD_SPEC §3).
 *
 * Deliberately narrow: no Node, no filesystem, no socket, no auth token, not
 * even the sidecar's port. The renderer asks main to make calls on its behalf
 * and listens for pushed events — nothing more.
 */

import { contextBridge, ipcRenderer, type IpcRendererEvent } from 'electron'

export type BrainStatus =
  | 'starting'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'disconnected'

export interface SidecarEvent {
  method: string
  params: Record<string, unknown>
}

export interface LogLine {
  level: 'warn' | 'error'
  message: string
}

/** Returned by every subscribe helper; call it to detach. */
type Unsubscribe = () => void

function subscribe<T>(channel: string, handler: (payload: T) => void): Unsubscribe {
  const listener = (_event: IpcRendererEvent, payload: T): void => handler(payload)
  ipcRenderer.on(channel, listener)
  return () => ipcRenderer.removeListener(channel, listener)
}

const api = {
  /** Current brain connection status, for the initial render. */
  getStatus: (): Promise<BrainStatus> => ipcRenderer.invoke('aria:status'),

  /** Connection status changes. */
  onStatus: (handler: (status: BrainStatus) => void): Unsubscribe =>
    subscribe('aria:status', handler),

  /** Server-pushed notifications from the sidecar (§7.1 events). */
  onEvent: (handler: (event: SidecarEvent) => void): Unsubscribe =>
    subscribe('aria:event', handler),

  /** Supervisor messages worth surfacing (spawn failures, restarts). */
  onLog: (handler: (line: LogLine) => void): Unsubscribe => subscribe('aria:log', handler),

  /** Invoke a JSON-RPC method on the sidecar. */
  call: <T = unknown>(method: string, params: Record<string, unknown> = {}): Promise<T> =>
    ipcRenderer.invoke('aria:call', method, params) as Promise<T>,

  restartBrain: (): void => ipcRenderer.send('aria:restart-brain'),

  hide: (): void => ipcRenderer.send('aria:hide'),
} as const

export type AriaApi = typeof api

contextBridge.exposeInMainWorld('aria', api)
