# Graph Report - .  (2026-08-08)

## Corpus Check
- 2 files · ~117,210 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2367 nodes · 4969 edges · 155 communities (114 shown, 41 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 526 edges (avg confidence: 0.53)
- Token cost: 170,439 input · 0 output

## Community Hubs (Navigation)
- Electron Main Process & Windows
- Prompt Context Assembly
- Quality Probe Checks
- File Semantic Indexer
- Conversation History Store
- File Finder Tool
- Conversation Service Core
- Database Layer & Settings Store
- Wake Word Gate Script
- Provider Wire Format & Ollama
- Permission Engine Tests
- TTS Speech Synthesis
- Conversation Store Sessions
- Latency Gate & Whisper STT
- Listener Capture Loop
- Conversation Gate Script
- Model Availability Service
- App Launcher & Matching
- Router Tests
- Tool Behaviour Tests
- Permission Engine & Semantic Finder
- Model Router Decision
- Conversation Service Tests
- File CRUD Tools
- Wake Word Gate Harness
- Model Catalog Tests
- Provider Health Tracking
- Conversation Test Fakes
- Listener Tests
- Connectivity Probe
- Listener State & VAD Utterance
- Web TypeScript Config
- Listener Test Helpers
- Tool Registry & Schemas
- Spec: Phases & Feature Scope
- Node TypeScript Config
- JSON-RPC Chat Handlers
- Sidecar Startup & Handshake
- Contamination Soak & Provider Errors
- RPC Integration Tests
- RPC Dispatch & Protocol
- Sentence Speech Stream
- Silero VAD Feed
- ARIA Project & Indexing Lessons
- Sidecar Service Builders
- Cloud Provider Clients
- Evaluation & Measurement Lessons
- Tool Contract Lessons
- Database Tests
- Spec: Core Constraints
- Credential Manager Keys
- System Info & Volume Tools
- Graph Maintenance Rules
- RPC Chat & Model Methods
- Renderer Bridge Types
- Spec: Architecture & State Rule
- Always-On Runtime Lessons
- Wake Phrase Matching
- Listener VAD Test Doubles
- Electron Build Dev Deps
- Screenshot: Graphify CLI Commands
- Health Report Handler
- Sidecar Settings Config
- Bearer Token Auth
- Renderer App Shell
- Wake & Arming Lessons
- Dependency & Wake Word Choices
- Package Manifest
- LLM Provider Interface
- History Panel UI
- Prompt & Latency Lessons
- Structured Logging Setup
- Test Fixtures Conftest
- Model Picker UI
- Spec: IPC & Confirmation Safety
- Model Health State
- App Matching Lessons
- Electron Preload Bridge
- Tray Icon Generator
- Silero VAD Lifecycle
- Conversation Hook
- Barge-in & Ducking
- Wake Word Model Fetch
- Tool Log Journal
- Orb Component
- NPM Scripts
- Settings Panel UI
- Spec: Security & Packaging
- RPC Test Fixtures
- Confirm Dialog UI
- Model Picker Tests
- Voice Aura Canvas
- Overlay Screen Rim
- Connection Status UI
- Markdown Renderer
- Audio Playback Hook
- Microphone Capture Hook
- Spec: Persona & Boundaries
- Spec: Memory & Reflection
- Composer Bar UI
- Confirm Dialog Tests
- Empty State UI
- Hands-Free Toggle UI
- Shortcuts Overlay UI
- Hands-Free Hook
- Models Hook
- Voice Level Publisher
- Sessions Hook
- Wake Chime Hook
- Overlay Caption
- Root TypeScript Config
- Autoprefixer Dependency
- Spec: Router & Offline Design
- Electron Builder Dependency
- Electron Vite Dependency
- Framer Motion Dependency
- JSDOM Dependency
- React Markdown Dependency
- Remark GFM Dependency
- Tailwind CSS Dependency
- Testing Library Dependency
- Node Types Dependency
- React Types Dependency
- React DOM Types Dependency
- TypeScript Dependency
- Vite Dependency
- Vite React Plugin
- Vitest Dependency
- Sidecar Package Init
- Confirm Hook
- Push To Talk Hook
- RPC Hook
- Window Mode Hook
- Renderer Entry Point
- Overlay Entry Point
- Reasoning Suppression
- Relative Path Resolution
- Sidecar Package Metadata

## God Nodes (most connected - your core abstractions)
1. `HealthTracker` - 90 edges
2. `ConversationService` - 78 edges
3. `Database` - 73 edges
4. `ConversationStore` - 71 edges
5. `Listener` - 62 edges
6. `ChatMessage` - 59 edges
7. `ToolResult` - 49 edges
8. `ToolContext` - 49 edges
9. `Event` - 48 edges
10. `EventBus` - 48 edges

## Surprising Connections (you probably didn't know these)
- `Model weights not vendored; missing weights degrade, never fail` --semantically_similar_to--> `Offline is a first-class path, not an error path`  [INFERRED] [semantically similar]
  requirements.txt → BUILD_SPEC.md
- `Overlay page paints no background of its own` --semantically_similar_to--> `No CSP meta tag; main.ts sets the header per-environment`  [INFERRED] [semantically similar]
  overlay.html → index.html
- `Result` --uses--> `ChatMessage`  [INFERRED]
  scripts/eval_quality.py → sidecar/providers/base.py
- `Result` --uses--> `GenerationOptions`  [INFERRED]
  scripts/eval_quality.py → sidecar/providers/base.py
- `Result` --uses--> `LLMProvider`  [INFERRED]
  scripts/eval_quality.py → sidecar/providers/base.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Keeping the knowledge graph current** — claude_keep_graph_current, claude_graphify_update, claude_graphify_semantic_reextraction, claude_graphify_shrink_guard, claude_graphify_check_update, claude_graphify_out [EXTRACTED 1.00]
- **Speech to turn: VAD, recognition, name check, arming** — claude_silero_vad, claude_wake_phrase_from_transcript, claude_fuzzy_name_matching, claude_armed_state, claude_strip_wake_word, claude_two_silence_thresholds, claude_whisper_serialisation [EXTRACTED 1.00]
- **The safety chain around a destructive tool call** — claude_rule_tool_registry, claude_tool_tiers, claude_confirmation_timeout_denied, claude_trusted_folders, claude_tool_log_approved_by, claude_approval_never_by_voice, claude_danger_off_by_default [EXTRACTED 1.00]
- **Incremental maintenance loop: watch detects, check-update decides, update re-extracts, cluster-only re-clusters** — image_graphify_watch, image_graphify_check_update, image_graphify_update, image_graphify_cluster_only, image_graph_json_artifact [INFERRED 0.85]
- **Cheap re-run paths that avoid a full LLM extraction** — image_graphify_update, image_graphify_cluster_only, image_llm_free_reextraction, image_semantic_reextraction_pending [INFERRED 0.75]
- **KV-cache latency discipline across prompt assembly** — build_spec_stable_prefix_ordering, build_spec_prefill_cost [INFERRED 0.85]

## Communities (155 total, 41 thin omitted)

### Community 0 - "Electron Main Process & Windows"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 1 - "Prompt Context Assembly"
Cohesion: 0.06
Nodes (64): datetime, assemble(), clean_title(), estimate_tokens(), fit_to_budget(), machine_context(), MachineContext, overhead_tokens() (+56 more)

### Community 2 - "Quality Probe Checks"
Cohesion: 0.06
Nodes (58): Check, Namespace, build_messages(), _is_reasoning(), main(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+50 more)

### Community 3 - "File Semantic Indexer"
Cohesion: 0.06
Nodes (46): chunk(), _digest(), extract_text(), Indexer, IndexStats, _pack(), Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks… (+38 more)

### Community 4 - "Conversation History Store"
Cohesion: 0.07
Nodes (41): Row, ConversationHistory, ProviderRegistry, BaseModel, Turn orchestration (BUILD_SPEC §9 Phase 1). One turn: persist the user message,…, `chat.send` result (§7.1)., Providers keyed by name, so the service can follow the router's choice., `chat.history` result. Typed at the boundary per CLAUDE.md rule 7. (+33 more)

### Community 5 - "File Finder Tool"
Cohesion: 0.07
Nodes (50): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), f(), parametrize, Finding files by name: the ranking, and the words people wrap around it. The…, if I say open cv … fetch the latest cv" — this is that, with an old draft and a…, budget_2026 is newer than every CV, and must not answer "cv"., Recency is a tiebreaker, never the whole answer. (+42 more)

### Community 6 - "Conversation Service Core"
Cohesion: 0.05
Nodes (26): SessionSummary, ConversationService, Any, ModelInfo, RoutingBias, StoredMessage, Owns in-flight turns. All durable state goes to SQLite., Persisted choice: a catalog id, or "smart" to let the router decide. (+18 more)

### Community 7 - "Database Layer & Settings Store"
Cohesion: 0.07
Nodes (37): _apply_sql(), connect(), current_version(), Database, migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection… (+29 more)

### Community 8 - "Wake Word Gate Script"
Cohesion: 0.06
Nodes (25): ListenerState, StrEnum, Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3). The renderer opens the…, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Protocol, What the RPC layer depends on, so it never imports ctranslate2. (+17 more)

### Community 9 - "Provider Wire Format & Ollama"
Cohesion: 0.07
Nodes (30): Compress the oldest turns without the current turn waiting for it. One at a…, Compress the oldest turns. Folds in any earlier note so it compounds., ChatMessage, GenerationOptions, Any, BaseModel, Stream a completion. Cancellation is cooperative: cancelling the consuming task…, Common `[{role, content}]` shape most chat APIs accept. Tool fields are only… (+22 more)

### Community 10 - "Permission Engine Tests"
Cohesion: 0.14
Nodes (40): engine(), Any, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has…, Rule 6, and the entry most worth having., Models get argument names wrong. That is a thing to say, not to crash on. (+32 more)

### Community 11 - "TTS Speech Synthesis"
Cohesion: 0.07
Nodes (37): ndarray, RuntimeError, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, Voice could not start. Never fatal — she still types., Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, SpeechUnavailable, split_for_speech() (+29 more)

### Community 12 - "Conversation Store Sessions"
Cohesion: 0.09
Nodes (33): ConversationStore, _now(), Most recently started session, for reload-on-launch., A fresh id with no row behind it yet. `ensure_session` creates a row for any id…, Name a conversation. The `with conn:` is load-bearing. Python's sqlite3 opens…, Remove a conversation and everything in it. Returns messages deleted. Both…, CRUD over `sessions` and `messages`., Return an existing session id, or create one. (+25 more)

### Community 13 - "Latency Gate & Whisper STT"
Cohesion: 0.08
Nodes (30): main(), measure(), missing_words(), normalise(), ndarray, Where the time goes between you stopping and her starting. python…, Words that actually went missing, ignoring differences nothing downstream cares…, clips() (+22 more)

### Community 14 - "Listener Capture Loop"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 15 - "Conversation Gate Script"
Cohesion: 0.09
Nodes (22): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+14 more)

### Community 16 - "Model Availability Service"
Cohesion: 0.07
Nodes (26): ModelAvailability, AvailabilityService, Which models are usable right now. One object answers this for both…, Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand., Re-read the Credential Manager. Call after any key change., Every catalog model with a verdict and a displayable reason., The ids the router may choose from. (+18 more)

### Community 17 - "App Launcher & Matching"
Cohesion: 0.09
Nodes (35): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, AppEntry, _AppIndex, best(), _build_index(), _closest_ratio(), list_windows() (+27 more)

### Community 18 - "Router Tests"
Cohesion: 0.10
Nodes (39): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort. (+31 more)

### Community 19 - "Tool Behaviour Tests"
Cohesion: 0.07
Nodes (39): app(), parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, Overwriting is a different destructive act from moving, and the user approved a…, §7.2's second failure mode: the model gets one line, the UI gets the lot., 7 zip" matched "7-Zip Help" purely because it is the shorter name., The demotion must not make the entry unreachable. (+31 more)

### Community 20 - "Permission Engine & Semantic Finder"
Cohesion: 0.08
Nodes (29): Holds the pieces the content search needs. A module-level holder rather than…, _Semantic, Bus, Denied, Journal, paths_in(), Pending, Any (+21 more)

### Community 21 - "Model Router Decision"
Cohesion: 0.12
Nodes (24): needs_deep_model(), BaseModel, ModelInfo, StrEnum, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, Reasoning, code, or a multi-step request: the `smart` class earns its cost., Chooses a model for a turn., Pick a model. `selected` is the user's choice — a model id, or "smart" to… (+16 more)

### Community 22 - "Conversation Service Tests"
Cohesion: 0.09
Nodes (33): _drain(), OpenEngine, Turn orchestration, cancellation, persistence and context roll-up., Wait for all in-flight turns., A client that forgets to echo the id back must not silently lose context., New Chat then closing the window must leave nothing behind., The sharp edge: `send` with no id continues the most recent conversation, so…, Deleting what you are looking at must not wedge the assistant. (+25 more)

### Community 23 - "File CRUD Tools"
Cohesion: 0.12
Nodes (36): Launch, StrEnum, How an entry has to be started. Three sources, three launchers., create_folder(), delete_file(), delete_folder(), _GUID, known_folder() (+28 more)

### Community 24 - "Wake Word Gate Harness"
Cohesion: 0.08
Nodes (18): frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python…, say(), SilentBus (+10 more)

### Community 25 - "Model Catalog Tests"
Cohesion: 0.09
Nodes (30): default_local(), The local fallback. Prefers the instruction-tuned 7B. `pulled` is what Ollama…, Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from., resolve_availability(), usable_ids(), entry_for(), parametrize (+22 more)

### Community 26 - "Provider Health Tracking"
Cohesion: 0.10
Nodes (27): HealthTracker, Observed latency if we have it, else the catalog seed, else pessimistic.…, In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture, Observed latency and the circuit breaker. A 429 is treated as a routing input…, An unmeasured model must not win a latency ranking by default., A fresh process re-probes rather than assuming the worst., A stale seed must self-correct rather than misroute forever. (+19 more)

### Community 27 - "Conversation Test Fakes"
Cohesion: 0.11
Nodes (24): FakeProvider, make_service(), fixture, The Phase 1 gate: kill the window, conversation reloads from SQLite., Scriptable stand-in for Ollama., A cloud model that dies mid-chain must never swap silently (§9.7 stage 7)., Otherwise the replacement reply appends to half a sentence from a model that…, Roll-up is a second model call. Awaiting it put a whole generation in front of… (+16 more)

### Community 28 - "Listener Tests"
Cohesion: 0.10
Nodes (29): interrupt(), Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, It cannot stop her yet: whether this is an interruption depends on what was…, One utterance: speech, then enough silence to end it. The silence has to clear…, The whole bug: "Aria" strips to an empty string, and the first build threw it…, The opposite of what this file asserted an hour ago, on purpose. A 12s window…, The old form must not regress just because a new one exists., Otherwise one "aria" leaves the microphone answering the room forever. (+21 more)

### Community 29 - "Connectivity Probe"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 30 - "Listener State & VAD Utterance"
Cohesion: 0.09
Nodes (17): Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout., build(), _drain_windows(), FakeConversation, parts(), phrase(), fixture (+9 more)

### Community 31 - "Web TypeScript Config"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 32 - "Listener Test Helpers"
Cohesion: 0.12
Nodes (28): drain(), frame(), ndarray, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on…, Under MIN_SPEECH_MS of speech is a door or a chair, not a question., Without a wake word, silence is just silence — no capture, no turn., One frame is a cough or her own voice leaking past echo cancellation. (+20 more)

### Community 33 - "Tool Registry & Schemas"
Cohesion: 0.09
Nodes (26): fixture, A registry with one tool per tier, put back exactly as found. The snapshot…, test_a_required_argument_is_marked_required(), test_the_schema_comes_from_the_signature(), _tools(), DANGER is off by default, and a tool the model cannot see is one it cannot be…, test_deleting_is_never_offered_to_the_model_by_default(), all_tools() (+18 more)

### Community 34 - "Spec: Phases & Feature Scope"
Cohesion: 0.07
Nodes (28): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+20 more)

### Community 35 - "Node TypeScript Config"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 36 - "JSON-RPC Chat Handlers"
Cohesion: 0.11
Nodes (26): chat_history(), chat_new(), chat_send(), chat_sessions(), method(), models_list(), models_select(), Any (+18 more)

### Community 37 - "Sidecar Startup & Handshake"
Cohesion: 0.14
Nodes (20): FastAPI, get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds…, Use the token Electron supplied, or mint one for standalone runs. (+12 more)

### Community 38 - "Contamination Soak & Provider Errors"
Cohesion: 0.12
Nodes (14): HTTPError, concrete_tokens(), main(), novel_tokens(), Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+6 more)

### Community 39 - "RPC Integration Tests"
Cohesion: 0.21
Nodes (22): _auth(), _call(), The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The id is reserved, not written — so the list stays empty., CLAUDE.md rule 5: destructive operations need a confirmation round-trip., An unregistered method returns -32601, so this proves they exist., Send a request and skip past any notifications until the reply arrives., test_chat_delete_refuses_without_confirmation() (+14 more)

### Community 40 - "RPC Dispatch & Protocol"
Cohesion: 0.17
Nodes (19): dispatch(), _invoke(), Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., err(), ErrorCode, ok(), Any (+11 more)

### Community 41 - "Sentence Speech Stream"
Cohesion: 0.12
Nodes (9): Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., SpeechStream, Protocol, What `core/conversation.py` depends on, so it never imports onnxruntime. Same…, False until warmed. The turn loop stays silent rather than blocking., int16 PCM and its sample rate. (+1 more)

### Community 42 - "Silero VAD Feed"
Cohesion: 0.11
Nodes (8): ndarray, Protocol, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance, VoiceActivity

### Community 43 - "ARIA Project & Indexing Lessons"
Cohesion: 0.12
Nodes (19): AppData in the skip list hides %TEMP%, Tests must set ARIA_INDEX_FILES=false, ARIA — local-first Windows AI assistant, ARIA_TOKEN handshake, Bounded scan instead of Everything, BUILD_SPEC.md, Electron renderer (pure view), graphify check-update . (+11 more)

### Community 44 - "Sidecar Service Builders"
Cohesion: 0.11
Nodes (19): get, _build_indexer(), _build_listener(), _build_stt(), _build_tts(), _discover_local_models(), health(), Any (+11 more)

### Community 45 - "Cloud Provider Clients"
Cohesion: 0.14
Nodes (9): get_key(), Read a key, or None if unset. Never logs the value., OpenAIProvider, Any, No-op: cloud models have no local load step to pay for., One `data:` frame into a StreamDelta. Non-data lines are ignored. `partial`…, Messages in the shape OpenAI actually accepts. Not `to_wire`: OpenAI needs…, Implements `LLMProvider` against the OpenAI chat completions API. (+1 more)

### Community 46 - "Evaluation & Measurement Lessons"
Cohesion: 0.13
Nodes (18): Chunks carry an index; renderer plays by index, num_gpu: 0 on every embedding call, scripts/eval_quality.py, Read fabricated and over-refused together, A gate that supplies the precondition tests the mechanism, not the feature, kokoro-onnx TTS on CPU, Never set temperature on a reasoning model, Switching local models evicts the old one first (+10 more)

### Community 47 - "Tool Contract Lessons"
Cohesion: 0.12
Nodes (17): Approval is never by voice, A confirmation timeout resolves to DENIED, The continuation pass is not offered tools again, DANGER tools are off by default and absent from schemas(), Phase 3 — the tool contract, pycaw's GetSpeakers() API changed, registry.clear() needs snapshot/restore in tests, Rule 5 — destructive ops need T2+ and confirmation (+9 more)

### Community 48 - "Database Tests"
Cohesion: 0.18
Nodes (16): Connection, Path, Phase 0 acceptance gate: the database is created and migrated from schema.sql., The schema declares float[768]; prove it round-trips., test_affect_state_singleton_is_seeded(), test_all_schema_tables_exist(), test_db_file_is_created(), test_foreign_keys_enforced() (+8 more)

### Community 49 - "Spec: Core Constraints"
Cohesion: 0.12
Nodes (16): Barge-in — interrupt playback on speech, Health monitoring and degradation warnings, Local by default, cloud opt-in per turn, num_ctx capped at 8192, Offline is a first-class path, not an error path, Phase 0 — Foundation, Phase 2 — Voice, Phase 6 — Agent loop + cloud routing (+8 more)

### Community 50 - "Credential Manager Keys"
Cohesion: 0.20
Nodes (15): all_status(), CredentialKey, CredentialStatus, delete_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Credential Manager entry names under the ARIA service. (+7 more)

### Community 51 - "System Info & Volume Tools"
Cohesion: 0.18
Nodes (14): test_system_info_reports_this_machine(), Everything she can do to the machine, and what it costs to do it. Importing…, _endpoint_volume(), _facts(), get_system_info(), Any, tool, Facts about the machine, and the one knob she can turn on it. `get_system_info`… (+6 more)

### Community 52 - "Graph Maintenance Rules"
Cohesion: 0.16
Nodes (15): Cloud providers call tools too, graphify cluster-only ., graphify update . --force, Two benign extractor gaps, graphify-out/ (graph.json, graph.html, GRAPH_REPORT.md), Graph shrink guard, graphify update . (AST-only refresh), Keep the knowledge graph current (+7 more)

### Community 53 - "RPC Chat & Model Methods"
Cohesion: 0.13
Nodes (15): chat_cancel(), chat_delete(), chat_rename(), confirm_respond(), models_bias(), Abort an in-flight turn mid-stream., Read or set what Smart mode optimises for. Phase 2 flips this to "fastest" for…, Read or set whether the sidecar accepts a continuous audio stream. Turning this… (+7 more)

### Community 54 - "Renderer Bridge Types"
Cohesion: 0.13
Nodes (14): AriaApi, AssistantState, BrainStatus, CredentialStatus, LogLine, ModelAvailability, ModelInfo, ModelListing (+6 more)

### Community 55 - "Spec: Architecture & State Rule"
Cohesion: 0.15
Nodes (13): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Renderer isolation via contextBridge preload, All state lives in Python; renderer is a view, Overlay window flags are the whole risk, showInactive, never show, sidecar.log and sidecar.out.log, No CSP meta tag; main.ts sets the header per-environment (+5 more)

### Community 56 - "Always-On Runtime Lessons"
Cohesion: 0.16
Nodes (14): backgroundThrottling: false is not sufficient, Audio frames go over a JSON-RPC notification, Hands-free is on by default, The indexer throttle is the feature, listener.frame_rate, @method("name") in rpc/handlers.py, The screen overlay window, sendToRenderer broadcasts to both windows (+6 more)

### Community 57 - "Wake Phrase Matching"
Cohesion: 0.16
Nodes (14): is_stop_word(), Is this whole utterance just a request to stop talking?, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said., The name has to be first. Anywhere else it is just a word., Matched whole, never as a prefix. (+6 more)

### Community 58 - "Listener VAD Test Doubles"
Cohesion: 0.19
Nodes (10): Any, Thinking for half a second in the middle of a question is not the end of the…, Silero's seat, answering from a list instead of a model., The trailing-silence clock starts at the first word. Otherwise a wake word…, ScriptedVAD, test_a_monologue_is_cut_off_at_the_cap(), test_a_pause_mid_sentence_does_not_end_the_turn(), test_endpoints_after_the_trailing_silence() (+2 more)

### Community 59 - "Electron Build Dev Deps"
Cohesion: 0.15
Nodes (13): electron, devDependencies, electron, postcss, react, react-dom, @types/ws, zustand (+5 more)

### Community 60 - "Screenshot: Graphify CLI Commands"
Cohesion: 0.29
Nodes (13): Cron-oriented staleness check (comment truncated at frame edge), Dark terminal layout: command column left, aligned # comments right, graph.json — the persisted graph artifact reused between runs, graphify check-update ./src — is semantic re-extraction pending, Graphify CLI maintenance command reference (terminal screenshot), graphify cluster-only ./my-project — rerun clustering on existing graph.json, graphify update ./src — re-extract code files, no LLM needed, graphify watch ./src — auto-rebuild on code changes (+5 more)

### Community 61 - "Health Report Handler"
Cohesion: 0.21
Nodes (12): pcm16_to_float32(), Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., build_health(), HealthReport, BaseModel, JSON-RPC method registry and dispatch (BUILD_SPEC §7.1). Phase 0 registers only…, One 80ms frame of base64 int16 PCM from the open microphone. Sent as a…, Rich health snapshot for the UI (§7.1 ``system.health``, §9.6). (+4 more)

### Community 62 - "Sidecar Settings Config"
Cohesion: 0.23
Nodes (6): BaseSettings, Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Create the runtime directory tree. Safe to call repeatedly., Sidecar settings, loaded once per process., Settings

### Community 63 - "Bearer Token Auth"
Cohesion: 0.18
Nodes (12): bearer_from_header(), Constant-time comparison of a presented Bearer token., Extract the token from an ``Authorization: Bearer <token>`` header., token_matches(), Token-gated JSON-RPC endpoint (§7.1). The port is reachable by any browser tab…, Read/dispatch/reply until the client goes away., rpc(), _serve() (+4 more)

### Community 64 - "Renderer App Shell"
Cohesion: 0.17
Nodes (4): drag, noDrag, Overlay, stroke

### Community 65 - "Wake & Arming Lessons"
Cohesion: 0.22
Nodes (11): ListenerState.ARMED, Blue means she is listening to you, The follow-up window was removed, Fuzzy name matching on the first word, hotwords="Aria" makes it worse, measured, listener.heard logs the words, not chars=42, listener.not_addressed logs the transcript, _rearm() — a false start must not disarm her (+3 more)

### Community 66 - "Dependency & Wake Word Choices"
Cohesion: 0.18
Nodes (11): Filler words are stripped first, Cloud vendors reached over httpx, not their SDKs, openWakeWord (ONNX), Rule 3 — never add torch, Silero VAD via faster-whisper, strip_wake_word, Two trailing-silence thresholds, The wake check reads only the opening of long utterances (+3 more)

### Community 67 - "Package Manifest"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 68 - "LLM Provider Interface"
Cohesion: 0.18
Nodes (7): provider_for(), LLMProvider, Protocol, What `core/conversation.py` and, later, `core/router.py` depend on., Stable identifier used in logs, the `route` column, and the UI., Cheap reachability check. Must not raise., Load the model and return how long it took, in ms. Cold start is 8-15s (§12);…

### Community 69 - "History Panel UI"
Cohesion: 0.24
Nodes (7): clockTime(), dayGroup(), HistoryPanel(), label(), Row(), RowProps, session()

### Community 70 - "Prompt & Latency Lessons"
Cohesion: 0.24
Nodes (10): providers/connectivity.py, FIRST_CHUNK_MAX_CHARS = 32, _GROUNDING_TEMPLATE / stable_prefix(has_tools=...), Stable-first prompt assembly and the KV cache, context.machine_context(), Being reached over the internet is not having internet, Roll-up (_summarize / _maybe_roll_up) runs in the background, scripts/soak_conversation.py (30-turn soak) (+2 more)

### Community 71 - "Structured Logging Setup"
Cohesion: 0.29
Nodes (9): configure_logging(), _console_handler(), _file_handler(), Handler, Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file. (+1 more)

### Community 72 - "Test Fixtures Conftest"
Cohesion: 0.29
Nodes (9): conn(), database(), db_path(), Connection, fixture, Path, Shared fixtures. Every test gets a throwaway data dir — never the real data/., A migrated database on a temp path. (+1 more)

### Community 73 - "Model Picker UI"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 74 - "Spec: IPC & Confirmation Safety"
Cohesion: 0.22
Nodes (9): Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation, Security model — localhost, keyring, path allowlist, Bearer token handshake on the WS upgrade (+1 more)

### Community 75 - "Model Health State"
Cohesion: 0.22
Nodes (4): ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Rolling health for one model id.

### Community 76 - "App Matching Lessons"
Cohesion: 0.29
Nodes (8): _ALIASES is a fallback, never a rewrite, App index: Get-StartApps + App Paths + PATH, open_app's ordered match bands, Filename ranking reuses tools/apps.score, A refusal names the limit once, then points somewhere, MATCH_FLOOR, open_app, Style — explicit over clever

### Community 77 - "Electron Preload Bridge"
Cohesion: 0.25
Nodes (6): api, AriaApi, BrainStatus, LogLine, SidecarEvent, Unsubscribe

### Community 78 - "Tray Icon Generator"
Cohesion: 0.36
Nodes (7): _chunk(), coverage(), main(), png_bytes(), Generate the tray icon PNGs embedded in electron/tray.ts. Electron's…, Fraction of one pixel covered by the circle, by supersampling., An 8-bit RGBA PNG of a filled circle on transparency.

### Community 79 - "Silero VAD Lifecycle"
Cohesion: 0.29
Nodes (4): Forget the previous utterance. Without this the tail of the last one biases the…, Frame-by-frame speech probability with carried state., Load the ONNX graph. Synchronous and ~170ms, called at startup rather than on…, SileroVAD

### Community 80 - "Conversation Hook"
Cohesion: 0.39
Nodes (7): appendToStreaming(), clearStreaming(), finalise(), toTurns(), Turn, TurnCompletePayload, useConversation

### Community 81 - "Barge-in & Ducking"
Cohesion: 0.33
Nodes (7): Cancel emits audio.stop, Barge-in, Duck first, decide after, A duck must always resume (_unduck), Esc stops her, claimed only while she speaks, Only her name or a stop word cuts her off, voice.playing (renderer reports playback)

### Community 82 - "Wake Word Model Fetch"
Cohesion: 0.33
Nodes (5): main(), Download the wake word weights into data/models/openwakeword. python…, missing_models(), Path, Which weights are absent, named so the log can say what to download.

### Community 83 - "Tool Log Journal"
Cohesion: 0.29
Nodes (4): Any, Where every tool call is recorded (BUILD_SPEC §7.3, CLAUDE.md rule 6). Append-…, Writes to `tool_log`. Satisfies `tools.permissions.Journal`., ToolJournal

### Community 84 - "Orb Component"
Cohesion: 0.33
Nodes (6): BREATH, HUE, Orb(), ORB_LAYOUT_ID, OrbProps, SPINS

### Community 85 - "NPM Scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, sidecar, test, typecheck

### Community 86 - "Settings Panel UI"
Cohesion: 0.33
Nodes (3): KEY_HELP, KEY_LABEL, RowProps

### Community 87 - "Spec: Security & Packaging"
Cohesion: 0.40
Nodes (5): Phase 9 — Packaging, Torch-free Python sidecar, requests pinned explicitly — undeclared faster-whisper dep, kokoro-onnx conflicts with §4's onnxruntime/numpy pins, openai and google-genai deliberately absent; httpx instead

### Community 88 - "RPC Test Fixtures"
Cohesion: 0.40
Nodes (5): client(), fixture, MonkeyPatch, Path, App wired to a temp data dir and a known token, via the real env path.

### Community 89 - "Confirm Dialog UI"
Cohesion: 0.40
Nodes (3): ConfirmRequest, Props, TIER_LABEL

### Community 91 - "Model Picker Tests"
Cohesion: 0.60
Nodes (3): entry(), model(), models()

### Community 92 - "Voice Aura Canvas"
Cohesion: 0.40
Nodes (3): AuraMode, HUE, Props

### Community 93 - "Overlay Screen Rim"
Cohesion: 0.40
Nodes (3): HUE, Props, RimMode

### Community 96 - "Audio Playback Hook"
Cohesion: 0.67
Nodes (3): AudioChunk, decodePcm16(), useAudio

### Community 97 - "Microphone Capture Hook"
Cohesion: 0.67
Nodes (3): encodePcm16(), Recording, useMic

### Community 98 - "Spec: Persona & Boundaries"
Cohesion: 0.67
Nodes (3): Persona boundaries — capacity to push back, Character, not sycophancy, aria.yaml persona configuration

### Community 99 - "Spec: Memory & Reflection"
Cohesion: 0.67
Nodes (3): Fact merge and supersession logic, Phase 5 — Memory, Nightly reflection prompt (reflect.j2)

## Ambiguous Edges - Review These
- `Graphify CLI maintenance command reference (terminal screenshot)` → `Cron-oriented staleness check (comment truncated at frame edge)`  [AMBIGUOUS]
  image.png · relation: references

## Knowledge Gaps
- **191 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+186 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Graphify CLI maintenance command reference (terminal screenshot)` and `Cron-oriented staleness check (comment truncated at frame edge)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `ConversationService` connect `Conversation Service Core` to `Conversation History Store`, `LLM Provider Interface`, `Contamination Soak & Provider Errors`, `Sidecar Startup & Handshake`, `Wake Word Gate Script`, `Provider Wire Format & Ollama`, `Sentence Speech Stream`, `TTS Speech Synthesis`, `Conversation Store Sessions`, `Sidecar Service Builders`, `Listener Capture Loop`, `Conversation Gate Script`, `Model Availability Service`, `Model Router Decision`, `Conversation Service Tests`, `File CRUD Tools`, `Provider Health Tracking`, `Conversation Test Fakes`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `Database` connect `Database Layer & Settings Store` to `File Semantic Indexer`, `Conversation History Store`, `File Finder Tool`, `Sidecar Startup & Handshake`, `Contamination Soak & Provider Errors`, `Test Fixtures Conftest`, `TTS Speech Synthesis`, `Conversation Store Sessions`, `Conversation Gate Script`, `Model Availability Service`, `Database Tests`, `Tool Log Journal`, `Conversation Service Tests`, `Conversation Test Fakes`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `HealthTracker` connect `Provider Health Tracking` to `Conversation History Store`, `Contamination Soak & Provider Errors`, `Conversation Service Core`, `Sentence Speech Stream`, `Model Health State`, `Model Availability Service`, `Router Tests`, `Model Router Decision`, `Conversation Service Tests`, `Model Catalog Tests`, `Conversation Test Fakes`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `RouteDecision`) actually correct?**
  _`ConversationService` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Database` (e.g. with `Recorder` and `Indexer`) actually correct?**
  _`Database` has 15 INFERRED edges - model-reasoned connections that need verification._