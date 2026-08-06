/**
 * The contextBridge surface, as the renderer sees it.
 *
 * Mirrors electron/preload.ts. Kept as a declaration rather than an import so
 * renderer code cannot accidentally pull main-process modules into the bundle.
 */

export type BrainStatus =
  | 'starting'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'disconnected'

/** `state.change` payload (BUILD_SPEC §7.1). */
export type AssistantState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'acting'

export interface SidecarEvent {
  method: string
  params: Record<string, unknown>
}

/** A row from the `messages` table, as `chat.history` returns it. */
export interface StoredMessage {
  id: number
  session_id: string
  role: 'user' | 'assistant' | 'tool' | 'system'
  content: string
  route: string | null
  latency_ms: number | null
  created_at: string
}

export interface LogLine {
  level: 'warn' | 'error'
  message: string
}

type Unsubscribe = () => void

export interface AriaApi {
  getStatus: () => Promise<BrainStatus>
  onStatus: (handler: (status: BrainStatus) => void) => Unsubscribe
  onEvent: (handler: (event: SidecarEvent) => void) => Unsubscribe
  onLog: (handler: (line: LogLine) => void) => Unsubscribe
  call: <T = unknown>(method: string, params?: Record<string, unknown>) => Promise<T>
  restartBrain: () => void
  hide: () => void
}

declare global {
  interface Window {
    aria: AriaApi
  }
}
