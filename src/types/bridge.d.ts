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
  /** `'?'` is a discovered model nobody has priced — shown blank, never guessed. */
  cost: 'free' | '$' | '$$' | '$$$' | '?'
  best_for: string
  ttft_ms_seed: number | null
  caveat: string | null
  local: boolean
  context_tokens: number
  /** Found by asking the provider, rather than measured and written down. */
  discovered: boolean
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

/** One past conversation, as `chat.sessions` returns it. */
export interface SessionSummary {
  id: string
  started_at: string
  /** Generated in the background; null until then. */
  title: string | null
  /** First thing you said — the fallback label. */
  preview: string
  message_count: number
  last_activity: string
}

/** One thing she has learned, as `memory.list` returns it (BUILD_SPEC §7.3). */
export interface MemoryFact {
  id: number
  subject: string
  predicate: string
  object: string
  confidence: number
  evidence_count: number
  /** You asserted it. Reflection may not overwrite it — only you may. */
  user_locked: boolean
  source_episode: number | null
  created_at: string
  updated_at: string
  /** Set when a newer fact replaced this one. Kept as an audit trail. */
  superseded_by: number | null
}

/** One past conversation, compressed. */
export interface MemoryEpisode {
  id: number
  session_id: string | null
  summary: string
  started_at: string
  ended_at: string
  salience: number
  access_count: number
  last_accessed: string | null
}

/** `memory.stats` — the retrieval latency §9 Phase 5's gate is measured on. */
export interface RetrievalStats {
  count: number
  p50_ms: number
  p90_ms: number
  max_ms: number
  embed_count: number
  embed_p50_ms: number
  embed_p90_ms: number
  degraded: number
  /** Turns that skipped retrieval entirely — the mechanism, not a shortfall. */
  empty: number
}

export interface MemoryStats {
  facts: number
  episodes: number
  retrieval: RetrievalStats
  last_reflection: string | null
  reflecting: boolean
  /** null until probed; false means word matching, not failure. */
  embeddings_ready: boolean | null
}

/** What one §8.3 reflection pass did. */
export interface ReflectionReport {
  model: string
  local: boolean
  window_hours: number
  messages_read: number
  inserted: number
  reinforced: number
  superseded: number
  blocked_by_pin: number
  pruned: number
  took_ms: number
  error: string | null
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
  /** Fire-and-forget JSON-RPC notification. No reply; dropped if the socket
   *  is closed, which is correct for audio frames. */
  notify: (method: string, params?: Record<string, unknown>) => void
  /** Publish the live voice level, for the screen overlay to animate to. */
  publishVoiceLevel: (level: number, mode: 'listening' | 'speaking' | null) => void
  /** Subscribe to it. Only the overlay window does. */
  onVoiceLevel: (
    handler: (payload: { level: number; mode: 'listening' | 'speaking' | null }) => void,
  ) => Unsubscribe
  restartBrain: () => void
  /** Put the window away. She keeps listening — this is close-to-tray. */
  hide: () => void
  /** Down to the taskbar, the way any other window does it. */
  minimize: () => void
  /** Grow into a working window, or shrink back to the corner companion. */
  setExpanded: (expanded: boolean) => Promise<boolean>
  isExpanded: () => Promise<boolean>
  onWindowMode: (handler: (expanded: boolean) => void) => Unsubscribe
}

declare global {
  interface Window {
    aria: AriaApi
  }
}
