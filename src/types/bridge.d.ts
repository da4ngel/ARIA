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

/** What Smart mode trades latency for. Mirrors `core.router.RoutingBias`. */
export type RoutingBias = 'fastest' | 'balanced' | 'quality'

/** One entry from `providers/catalog.py`. Everything the tooltip shows. */
export interface ModelInfo {
  id: string
  provider: 'ollama' | 'openai' | 'gemini'
  label: string
  klass: 'fast' | 'balanced' | 'smart' | 'vision'
  persona: 'minimal' | 'full'
  cost: 'free' | '$' | '$$' | '$$$'
  best_for: string
  ttft_ms_seed: number | null
  caveat: string | null
  local: boolean
  context_tokens: number
}

/** A catalog entry plus whether it can be used right now (`models.list`). */
export interface ModelAvailability {
  model: ModelInfo
  available: boolean
  /** Why not, in words fit to display. Null when available. */
  reason: string | null
  observed_ttft_ms: number | null
}

export interface ModelListing {
  /** A catalog id, or "smart" to let the router choose. */
  selected: string
  bias: RoutingBias
  models: ModelAvailability[]
}

/** `settings.keys` — presence and last four characters only, never a value. */
export interface CredentialStatus {
  key: 'openai_api_key' | 'gemini_api_key'
  present: boolean
  hint: string | null
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
