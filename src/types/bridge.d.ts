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
  provider: 'ollama' | 'openai' | 'gemini' | 'openrouter'
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
  /**
   * A third party's published score (Artificial Analysis' intelligence index),
   * carried verbatim. **Never a measurement made here** — it decides which
   * candidate is measured first and nothing else.
   */
  benchmark_index: number | null
  /**
   * Whether the endpoint may train on what is sent to it. A property of the
   * endpoint, not the model: OpenRouter's free tier can route to providers
   * that do, and the opt-out is the account holder's to set.
   */
  trains_on_data: boolean
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
  /** "chat" or "study". A study chat is a kind of conversation rather than a
   *  mode switched on, so this is a field on every row rather than a filter —
   *  `chat.delete` looks a session up through this same list. */
  kind?: string
  /** The subject this study chat last worked on. A record of where it got to,
   *  not a binding: a study chat may roam between subjects. */
  study_subject_id?: number | null
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

/** One concept on a subject's map, with whatever mastery it has earned.
 *
 * `level` is an integer 0-5, not a 0..1 confidence — 0 never seen, 1
 * introduced, 2-3 shaky, 4 solid, 5 he could teach it. `asked`/`correct` are
 * the evidence behind it, the way `evidence_count` is for a fact. */
export interface StudyConcept {
  id: number
  name: string
  summary: string
  level: number
  asked: number
  correct: number
}

/** One subject's whole map, as `study.state` returns it. */
export interface StudyState {
  subject_id?: number
  /** null when nothing has ever been studied. */
  subject: string | null
  source_path?: string | null
  covered?: number
  /** What she would teach next, or null when the map is finished. */
  next?: string | null
  concepts: StudyConcept[]
}

/** A row in the subject switcher — progress without fetching every concept. */
export interface StudySubject {
  id: number
  name: string
  source_path: string | null
  last_studied_at: string | null
  total: number
  covered: number
}

/** What `study.start` hands back: the message the panel should then send. */
export interface StudyStart {
  session_id: string
  sub_mode: string
  label: string
  opener: string
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
  /** Fill the screen. Maximising implies expanding — compact is not
   *  resizable, and a full-screen always-on-top window with no taskbar
   *  entry is one you cannot get behind. */
  setMaximized: (maximized: boolean) => Promise<boolean>
  isMaximized: () => Promise<boolean>
  /** Including when the OS did it — Win+Up, snap, a double click. */
  onWindowMaximized: (handler: (maximized: boolean) => void) => Unsubscribe
  /** Write a diagnostics zip (logs, health, versions — never a credential
   *  value) and resolve with its path, or null if the sidecar is down. */
  exportDiagnostics: () => Promise<string | null>
  /** Whether Windows launches her at login. Read from the OS every time —
   *  a stored copy could disagree with what the registry actually says. */
  getAutoStart: () => Promise<boolean>
  setAutoStart: (enabled: boolean) => Promise<boolean>
  /** Absolute paths the user chose in the OS picker. Paths only — the
   *  renderer never reads a file; the sidecar opens them. */
  pickFiles: () => Promise<string[]>
}

declare global {
  interface Window {
    aria: AriaApi
  }
}

/** One thing that was copied, from `clipboard.history`. */
export interface ClipEntry {
  id: number
  content: string
  chars: number
  copied_at: string
  source: string | null
}

export interface ClipboardHistory {
  entries: ClipEntry[]
  /** False when the watcher is not running — "nothing copied yet" and "not
   *  recording" look identical on screen otherwise. */
  watching: boolean
  /** How many copies the credential filter refused this session. Counted so
   *  the filter is observable rather than assumed. */
  skipped_secrets: number
}

/** A reminder that has been set and not yet fired, from `reminders.list`. */
export interface Reminder {
  id: number
  text: string
  due_at: string
  created_at: string
  overdue: boolean
}

/** One model's share of a day, from `usage.today`. */
export interface UsageModel {
  model: string
  provider: string
  local: boolean
  turns: number
  prompt_tokens: number
  completion_tokens: number
  /** Turns where the provider reported no usage at all. Not the same as zero. */
  uncounted: number
  avg_latency_ms: number
  /** Null when no rate covers this model — never silently 0. */
  estimated_usd: number | null
}

export interface UsageReport {
  since: string
  days: number
  turns: number
  local_turns: number
  cloud_turns: number
  models: UsageModel[]
  prompt_tokens: number
  completion_tokens: number
  uncounted: number
  estimated_usd: number
  /** Turns the price table does not cover. Shown, because a total that hides
   *  them is knowingly short. */
  unpriced_turns: number
  prices_as_of: string
}

/** A routing decision, from `usage.recent`. */
export interface TurnRecord {
  id: number
  message_id: number | null
  model: string
  provider: string
  local: number
  stage: string
  detail: string | null
  bias: string
  spoken: number
  tool_shaped: number
  chars: number
  latency_ms: number | null
  tool_called: string | null
  tool_ok: number | null
  prompt_tokens: number | null
  completion_tokens: number | null
  rating: number | null
  created_at: string
}

/** A tool call, from `usage.recent`. */
export interface ToolRecord {
  id: number
  call_id: string
  session_id: string | null
  tool: string
  args: string
  tier: number
  approved: number | null
  ok: number | null
  error: string | null
  duration_ms: number | null
  approved_by: string | null
  created_at: string
}

/** One reversible operation, from `undo.list`. */
export interface UndoEntry {
  id: number
  tool: string
  kind: string
  summary: string
  created_at: string
  undone_at: string | null
  /** Why it can no longer be reversed — shown instead of a dead button. */
  blocked: string | null
  undoable: boolean
}
