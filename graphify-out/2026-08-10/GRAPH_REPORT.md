# Graph Report - ARIA  (2026-08-09)

## Corpus Check
- 149 files · ~135,740 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2582 nodes · 5438 edges · 183 communities (131 shown, 52 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 542 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4f5c9c61`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.ts
- test_context.py
- probes.py
- Indexer
- conversation.py
- finder.py
- ConversationService
- SettingsStore
- Event
- GenerationOptions
- test_permissions.py
- test_tts.py
- ConversationStore
- TranscriptionUnavailable
- Listener
- KokoroTTS
- AvailabilityService
- AppEntry
- test_router.py
- test_tools.py
- Tier
- Router
- test_conversation.py
- ToolContext
- missing_models
- test_catalog.py
- HealthTracker
- test_discovery.py
- test_listener.py
- Connectivity
- EventBus
- compilerOptions
- catalog.py
- FakeProvider
- Tool contract — decorator, ToolResult, derived schemas
- compilerOptions
- method
- main.py
- Database
- test_rpc.py
- events.py
- discovery.py
- VoiceActivity
- /graphify --update (semantic re-extraction)
- ChatMessage
- RoutingBias
- scripts/eval_quality.py
- Phase 3 — the tool contract
- test_db.py
- Phase 2 — Voice
- CredentialKey
- system.py
- Provider strategy — OpenAI and Gemini, not Anthropic
- RpcMethodError
- bridge.d.ts
- Electron main + Python sidecar architecture
- Semantic file index (nomic-embed-text)
- strip_wake_word
- parametrize
- devDependencies
- ._stream_one
- handlers.py
- _start_conversation
- rpc
- App.tsx
- ListenerState.ARMED
- open_app's ordered match bands
- package.json
- eval_quality.py
- HistoryPanel.tsx
- Settings
- configure_logging
- db.py
- ModelPicker.tsx
- WakeWord
- Sidebar.tsx
- database
- preload.ts
- make_tray_icons.py
- gate_tool_selection.py
- useConversation.ts
- Barge-in
- WebSocket JSON-RPC 2.0 IPC contract
- ToolJournal
- Orb.tsx
- scripts
- SettingsPanel.tsx
- Torch-free Python sidecar
- apps.py
- ConfirmDialog.tsx
- ModelPicker.test.tsx
- VoiceAura.tsx
- ScreenRim.tsx
- ConnectionStatus.tsx
- Markdown.tsx
- useAudio.ts
- useMic.ts
- Persona boundaries — capacity to push back
- Nightly reflection prompt (reflect.j2)
- ComposerBar.tsx
- ConfirmDialog.test.tsx
- EmptyState.tsx
- HandsFreeToggle.tsx
- Shortcuts.tsx
- useHandsFree.ts
- useModels.ts
- usePublishVoiceLevel.ts
- useSessions.ts
- useWakeChime.ts
- Caption.tsx
- tsconfig.json
- ._build_context
- One phase per session execution model
- electron-builder
- electron-vite
- framer-motion
- jsdom
- react-markdown
- remark-gfm
- tailwindcss
- @testing-library/react
- @types/node
- @types/react
- @types/react-dom
- typescript
- vite
- @vitejs/plugin-react
- vitest
- sidecar/__init__.py
- useConfirm.ts
- usePushToTalk.ts
- useRpc.ts
- useWindowMode.ts
- src/main.tsx
- overlay/main.tsx
- Always send think:false to qwen3.x reasoning models
- Relative paths resolve against the named folder
- aria-sidecar
- graphify update . (AST-only refresh)
- .cancel
- spawn
- _drain_windows
- set_discovered
- ToolsPanel.tsx
- ._free_vram_for
- ModelHealth
- _Semantic
- .run
- Sender
- WindowControls.tsx
- Runtime
- ._finish
- ._generate_title
- by_class
- kokoro-onnx TTS on CPU
- persona_for
- ToolCallCard.tsx
- .add_message
- gate_delete.py
- test_fresh_database_lands_on_the_current_version
- @types/ws
- test_a_short_code_request_is_not_answered_locally_to_save_time
- test_ordinary_questions_do_not_get_the_expensive_tier
- test_a_spoken_turn_still_stays_local

## God Nodes (most connected - your core abstractions)
1. `HealthTracker` - 97 edges
2. `ConversationService` - 86 edges
3. `Database` - 73 edges
4. `ConversationStore` - 71 edges
5. `ChatMessage` - 64 edges
6. `Listener` - 62 edges
7. `ToolResult` - 58 edges
8. `ToolContext` - 58 edges
9. `Router` - 50 edges
10. `Event` - 48 edges

## Surprising Connections (you probably didn't know these)
- `Overlay page paints no background of its own` --semantically_similar_to--> `No CSP meta tag; main.ts sets the header per-environment`  [INFERRED] [semantically similar]
  overlay.html → index.html
- `Model weights not vendored; missing weights degrade, never fail` --semantically_similar_to--> `Offline is a first-class path, not an error path`  [INFERRED] [semantically similar]
  requirements.txt → BUILD_SPEC.md
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
- **KV-cache latency discipline across prompt assembly** — build_spec_stable_prefix_ordering, build_spec_prefill_cost [INFERRED 0.85]

## Communities (183 total, 52 thin omitted)

### Community 0 - "main.ts"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 1 - "test_context.py"
Cohesion: 0.11
Nodes (41): assemble(), estimate_tokens(), fit_to_budget(), machine_context(), MachineContext, overhead_tokens(), PersonaLevel, StrEnum (+33 more)

### Community 2 - "probes.py"
Cohesion: 0.10
Nodes (31): Check, admits_ignorance(), answers_flatly(), contains(), contains_any(), denies_capability(), exact(), excludes() (+23 more)

### Community 3 - "Indexer"
Cohesion: 0.06
Nodes (47): chunk(), _digest(), extract_text(), Indexer, IndexStats, _pack(), Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks… (+39 more)

### Community 4 - "conversation.py"
Cohesion: 0.05
Nodes (42): datetime, Row, clean_title(), _persona(), Prompt assembly and the rolling context window (BUILD_SPEC §8.2, §9 Phase 1).…, Fill in what she can reach. Everything else is identical., Strip what models add despite being told not to. Even with an explicit…, _relative_age() (+34 more)

### Community 5 - "finder.py"
Cohesion: 0.07
Nodes (50): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), f(), parametrize, Finding files by name: the ranking, and the words people wrap around it. The…, if I say open cv … fetch the latest cv" — this is that, with an old draft and a…, budget_2026 is newer than every CV, and must not answer "cv"., Recency is a tiebreaker, never the whole answer. (+42 more)

### Community 6 - "ConversationService"
Cohesion: 0.12
Nodes (11): ConversationService, RoutingBias, Owns in-flight turns. All durable state goes to SQLite., Persisted choice: a catalog id, or "smart" to let the router decide., Whether a turn is in flight. Read by the file indexer, which stops entirely…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, The control. Forcing every continuation local would throw away the cloud model…, test_a_local_only_tool_forces_the_continuation_local() (+3 more)

### Community 7 - "SettingsStore"
Cohesion: 0.11
Nodes (18): Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Fill the overlay from cache. Returns whether it is still fresh. A stale cache…, fixture, parametrize (+10 more)

### Community 8 - "Event"
Cohesion: 0.08
Nodes (19): frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python…, say(), SilentBus (+11 more)

### Community 9 - "GenerationOptions"
Cohesion: 0.05
Nodes (51): HTTPError, GenerationOptions, ProviderRateLimited, ProviderUnavailable, BaseModel, The interface every LLM backend implements. Phase 1 only ships the Ollama…, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, Common `[{role, content}]` shape most chat APIs accept. Tool fields are only… (+43 more)

### Community 10 - "test_permissions.py"
Cohesion: 0.09
Nodes (54): engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has…, Rule 6, and the entry most worth having. (+46 more)

### Community 11 - "test_tts.py"
Cohesion: 0.06
Nodes (38): ndarray, RuntimeError, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, Load and warm. The first synthesis is ~5x slower than the rest, and the user…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, Voice could not start. Never fatal — she still types., Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, SpeechUnavailable (+30 more)

### Community 12 - "ConversationStore"
Cohesion: 0.10
Nodes (31): ConversationStore, Most recently started session, for reload-on-launch., A fresh id with no row behind it yet. `ensure_session` creates a row for any id…, Name a conversation. The `with conn:` is load-bearing. Python's sqlite3 opens…, Remove a conversation and everything in it. Returns messages deleted. Both…, CRUD over `sessions` and `messages`., make_session(), fixture (+23 more)

### Community 13 - "TranscriptionUnavailable"
Cohesion: 0.22
Nodes (8): pcm16_to_float32(), ndarray, RuntimeError, Load and warm. First use downloads ~150MB, which must not happen while someone…, One utterance to text. Empty string when nothing was said., Speech input could not start. Never fatal — she still reads typing., Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., TranscriptionUnavailable

### Community 14 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 15 - "KokoroTTS"
Cohesion: 0.05
Nodes (47): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+39 more)

### Community 16 - "AvailabilityService"
Cohesion: 0.15
Nodes (9): ModelAvailability, AvailabilityService, Which models are usable right now. One object answers this for both…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand., Re-read the Credential Manager. Call after any key change. (+1 more)

### Community 17 - "AppEntry"
Cohesion: 0.06
Nodes (41): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, app(), 7 zip" matched "7-Zip Help" purely because it is the shorter name., The demotion must not make the entry unreachable., Opening the wrong app is worse than opening nothing., This is what stops "open youtube" launching the YouTube Music app: the website…, A dead end is useless; naming the closest lets the model retry. (+33 more)

### Community 18 - "test_router.py"
Cohesion: 0.11
Nodes (33): is_local(), RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort., Observed latency overrides the seeded table as turns land., The router must always answer. A turn with no candidates is a crash., Local models are multi-GB downloads that may not have finished. (+25 more)

### Community 19 - "test_tools.py"
Cohesion: 0.07
Nodes (39): parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, Overwriting is a different destructive act from moving, and the user approved a…, OneDrive relocates Documents and Desktop by default, so joining onto…, The whole point: when it cannot be done she must say so, not claim it., browser" scored 0.88 against LockDown Browser and won. A category is not a…, The control. A guard that refuses everything passes every test above. (+31 more)

### Community 20 - "Tier"
Cohesion: 0.05
Nodes (49): It is a strong constraint — it overrides the router — so it should be…, test_nothing_else_claims_local_only(), Bus, Denied, Journal, paths_in(), Pending, PermissionEngine (+41 more)

### Community 21 - "Router"
Cohesion: 0.20
Nodes (13): BaseModel, ModelInfo, Chooses a model for a turn., Pick a model. `selected` is the user's choice — a model id, or "smart" to…, Cloud unless the turn is trivial. The default. `_DEEP_VERBS` is checked here…, Cloud for real work, local for conversation., Local unless the turn clearly needs more. What voice will want., Fastest observed first — the ranking self-corrects as turns land. (+5 more)

### Community 22 - "test_conversation.py"
Cohesion: 0.11
Nodes (27): _drain(), Turn orchestration, cancellation, persistence and context roll-up., Wait for all in-flight turns., A client that forgets to echo the id back must not silently lose context., New Chat then closing the window must leave nothing behind., The sharp edge: `send` with no id continues the most recent conversation, so…, Deleting what you are looking at must not wedge the assistant., Measured: firing a title straight after a turn pushed the *next* turn to 924ms… (+19 more)

### Community 23 - "ToolContext"
Cohesion: 0.10
Nodes (43): tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, The clipboard's text, or None when it holds something else. An image, a file…, Read the clipboard's text., _read(), read_clipboard(), write_clipboard() (+35 more)

### Community 24 - "missing_models"
Cohesion: 0.33
Nodes (5): main(), Download the wake word weights into data/models/openwakeword. python…, missing_models(), Path, Which weights are absent, named so the log can say what to download.

### Community 25 - "test_catalog.py"
Cohesion: 0.12
Nodes (21): default_local(), The local fallback. Prefers the instruction-tuned 7B. `pulled` is what Ollama…, entry_for(), Model availability — the one resolver behind both the picker and the router. If…, Callers use this as a last resort; it must not raise., The picker builds its tooltip from these — an empty one is a blank box., `str.capitalize()` would render these 'Openai' — they are user-facing., The free-tier quota may have reset — show the warning, allow the pick. (+13 more)

### Community 26 - "HealthTracker"
Cohesion: 0.10
Nodes (27): HealthTracker, Observed latency if we have it, else the catalog seed, else pessimistic.…, In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture, Observed latency and the circuit breaker. A 429 is treated as a routing input…, An unmeasured model must not win a latency ranking by default., A fresh process re-probes rather than assuming the worst., A stale seed must self-correct rather than misroute forever. (+19 more)

### Community 27 - "test_discovery.py"
Cohesion: 0.10
Nodes (32): parse_gemini(), parse_openai(), Any, Chat models from a `GET /v1/models` body., Chat models from a `GET /v1beta/models` body., gemini_ids(), _load(), openai_ids() (+24 more)

### Community 28 - "test_listener.py"
Cohesion: 0.07
Nodes (59): drain(), frame(), interrupt(), ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on…, Under MIN_SPEECH_MS of speech is a door or a chair, not a question. (+51 more)

### Community 29 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 30 - "EventBus"
Cohesion: 0.06
Nodes (33): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Endpoint, Accumulates frames and decides when the speaker has finished. Deliberately not…, Why capture stopped, so the caller can tell an utterance from a timeout. (+25 more)

### Community 31 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 32 - "catalog.py"
Cohesion: 0.12
Nodes (26): all_models(), discovered(), get(), ModelAvailability, ModelInfo, ModelListing, BaseModel, The model catalog — one structure behind the picker, the tooltips, and routing.… (+18 more)

### Community 33 - "FakeProvider"
Cohesion: 0.12
Nodes (20): FakeProvider, make_service(), fixture, The Phase 1 gate: kill the window, conversation reloads from SQLite., Scriptable stand-in for Ollama., A cloud model that dies mid-chain must never swap silently (§9.7 stage 7)., 30-turn coherence gate: stays under budget, no overflow., Roll-up is a second model call. Awaiting it put a whole generation in front of… (+12 more)

### Community 34 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (28): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+20 more)

### Community 35 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 36 - "method"
Cohesion: 0.09
Nodes (30): chat_history(), chat_new(), chat_send(), chat_sessions(), confirm_respond(), method(), models_list(), models_refresh() (+22 more)

### Community 37 - "main.py"
Cohesion: 0.12
Nodes (24): FastAPI, get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., bearer_from_header(), clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds… (+16 more)

### Community 38 - "Database"
Cohesion: 0.15
Nodes (15): Database, Async-safe wrapper around the single sqlite connection., OpenEngine, ToolCall, Asks for a tool on the first pass, then answers on the second. The two-pass…, A permission engine that always allows, recording what it ran., §7.2's second failure mode: never paste the payload into the context., Otherwise a model loops: use a tool, see the tools, use one again. (+7 more)

### Community 39 - "test_rpc.py"
Cohesion: 0.16
Nodes (27): _auth(), _call(), client(), fixture, MonkeyPatch, Path, The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The id is reserved, not written — so the list stays empty. (+19 more)

### Community 40 - "events.py"
Cohesion: 0.15
Nodes (20): Server -> client push notifications and the set of live connections (§7.1).…, dispatch(), _invoke(), Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., err(), ErrorCode, ok() (+12 more)

### Community 41 - "discovery.py"
Cohesion: 0.13
Nodes (21): Cost, ModelClass, StrEnum, What a model is *for*. The router picks a class, then a model in it., discover_all(), discover_gemini(), discover_openai(), _fetch() (+13 more)

### Community 42 - "VoiceActivity"
Cohesion: 0.15
Nodes (6): ndarray, Protocol, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., VoiceActivity

### Community 43 - "/graphify --update (semantic re-extraction)"
Cohesion: 0.16
Nodes (14): ARIA — local-first Windows AI assistant, ARIA_TOKEN handshake, BUILD_SPEC.md, Electron renderer (pure view), graphify check-update ., /graphify --update (semantic re-extraction), update is code-only, by design, Prefill costs ~480ms per 1000 tokens here (+6 more)

### Community 44 - "ChatMessage"
Cohesion: 0.10
Nodes (19): StoredMessage, Drop rows the model should not see back (tool rows arrive in Phase 3)., Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, Prompt asking the model to compress the oldest turns into a note., Prompt asking the model to name a conversation for the history list., split_for_rollup(), summarization_request(), title_request() (+11 more)

### Community 45 - "RoutingBias"
Cohesion: 0.11
Nodes (15): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+7 more)

### Community 46 - "scripts/eval_quality.py"
Cohesion: 0.14
Nodes (18): num_gpu: 0 on every embedding call, scripts/eval_quality.py, Read fabricated and over-refused together, FIRST_CHUNK_MAX_CHARS = 32, A gate that supplies the precondition tests the mechanism, not the feature, Never set temperature on a reasoning model, Switching local models evicts the old one first, Persona is per model; MINIMAL is not a downgrade (+10 more)

### Community 47 - "Phase 3 — the tool contract"
Cohesion: 0.12
Nodes (17): Approval is never by voice, A confirmation timeout resolves to DENIED, The continuation pass is not offered tools again, DANGER tools are off by default and absent from schemas(), Phase 3 — the tool contract, pycaw's GetSpeakers() API changed, registry.clear() needs snapshot/restore in tests, Rule 5 — destructive ops need T2+ and confirmation (+9 more)

### Community 48 - "test_db.py"
Cohesion: 0.17
Nodes (18): Every table in the database, including vec0 virtual tables., table_names(), Connection, Path, Phase 0 acceptance gate: the database is created and migrated from schema.sql., The schema declares float[768]; prove it round-trips., test_affect_state_singleton_is_seeded(), test_all_schema_tables_exist() (+10 more)

### Community 49 - "Phase 2 — Voice"
Cohesion: 0.12
Nodes (16): Barge-in — interrupt playback on speech, Health monitoring and degradation warnings, Local by default, cloud opt-in per turn, num_ctx capped at 8192, Offline is a first-class path, not an error path, Phase 0 — Foundation, Phase 2 — Voice, Phase 6 — Agent loop + cloud routing (+8 more)

### Community 50 - "CredentialKey"
Cohesion: 0.18
Nodes (17): all_status(), CredentialKey, CredentialStatus, delete_key(), get_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,… (+9 more)

### Community 51 - "system.py"
Cohesion: 0.12
Nodes (22): test_system_info_reports_this_machine(), Everything she can do to the machine, and what it costs to do it. Importing…, _endpoint_volume(), _facts(), get_system_info(), kill_process(), list_processes(), Any (+14 more)

### Community 52 - "Provider strategy — OpenAI and Gemini, not Anthropic"
Cohesion: 0.13
Nodes (16): Cloud providers call tools too, Filler words are stripped first, Cloud vendors reached over httpx, not their SDKs, Keys in Windows Credential Manager via keyring, openWakeWord (ONNX), Provider strategy — OpenAI and Gemini, not Anthropic, core/router.py, Rule 10 — do not refactor prior phases (+8 more)

### Community 53 - "RpcMethodError"
Cohesion: 0.12
Nodes (17): chat_cancel(), chat_delete(), chat_rename(), models_bias(), models_select(), Abort an in-flight turn mid-stream., Persist the model choice: a catalog id, or "smart"., Read or set what Smart mode optimises for. Phase 2 flips this to "fastest" for… (+9 more)

### Community 54 - "bridge.d.ts"
Cohesion: 0.13
Nodes (14): AriaApi, AssistantState, BrainStatus, CredentialStatus, LogLine, ModelAvailability, ModelInfo, ModelListing (+6 more)

### Community 55 - "Electron main + Python sidecar architecture"
Cohesion: 0.20
Nodes (10): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Renderer isolation via contextBridge preload, All state lives in Python; renderer is a view, sidecar.log and sidecar.out.log, No CSP meta tag; main.ts sets the header per-environment, index.html renderer entry (#root → src/main.tsx), README layout — electron / src / sidecar / data (+2 more)

### Community 56 - "Semantic file index (nomic-embed-text)"
Cohesion: 0.10
Nodes (22): AppData in the skip list hides %TEMP%, Tests must set ARIA_INDEX_FILES=false, backgroundThrottling: false is not sufficient, Bounded scan instead of Everything, Audio frames go over a JSON-RPC notification, Hands-free is on by default, The indexer throttle is the feature, listener.frame_rate (+14 more)

### Community 57 - "strip_wake_word"
Cohesion: 0.16
Nodes (14): is_stop_word(), Is this whole utterance just a request to stop talking?, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said., The name has to be first. Anywhere else it is just a word., Matched whole, never as a prefix. (+6 more)

### Community 58 - "parametrize"
Cohesion: 0.17
Nodes (13): is_trivial(), needs_deep_model(), A greeting or acknowledgement — nothing a 4B model can get wrong., Reasoning, code, or a multi-step request: the `smart` class earns its cost., parametrize, The line that was missing. Without it these went to the FAST class., test_clipboard_questions_stay_on_this_machine(), test_code_requests_reach_a_reasoning_model() (+5 more)

### Community 59 - "devDependencies"
Cohesion: 0.15
Nodes (13): autoprefixer, electron, devDependencies, autoprefixer, electron, postcss, react, react-dom (+5 more)

### Community 60 - "._stream_one"
Cohesion: 0.17
Nodes (7): ModelInfo, ToolCall, Start a turn. Returns immediately; the reply streams as events. Omitting…, Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, Run the first requested tool, then let the model answer with it. **One tool,…, Which model gets to see the tool's result. `router._PRIVATE` already keeps a…, Persist whatever was generated — a half reply is still conversation.

### Community 61 - "handlers.py"
Cohesion: 0.31
Nodes (8): build_health(), HealthReport, BaseModel, JSON-RPC method registry and dispatch (BUILD_SPEC §7.1). Phase 0 registers only…, Rich health snapshot for the UI (§7.1 ``system.health``, §9.6)., Return the health snapshot. Never raises — the UI polls this., system_health(), uptime_seconds()

### Community 62 - "_start_conversation"
Cohesion: 0.11
Nodes (19): get, _build_indexer(), _build_listener(), _build_stt(), _build_tts(), _discover_local_models(), health(), Any (+11 more)

### Community 63 - "rpc"
Cohesion: 0.29
Nodes (8): Constant-time comparison of a presented Bearer token., token_matches(), Token-gated JSON-RPC endpoint (§7.1). The port is reachable by any browser tab…, Read/dispatch/reply until the client goes away., rpc(), _serve(), test_token_comparison_rejects_empty(), websocket

### Community 64 - "App.tsx"
Cohesion: 0.40
Nodes (3): drag, noDrag, Overlay

### Community 65 - "ListenerState.ARMED"
Cohesion: 0.16
Nodes (14): ListenerState.ARMED, Blue means she is listening to you, The follow-up window was removed, Fuzzy name matching on the first word, hotwords="Aria" makes it worse, measured, listener.heard logs the words, not chars=42, listener.not_addressed logs the transcript, _rearm() — a false start must not disarm her (+6 more)

### Community 66 - "open_app's ordered match bands"
Cohesion: 0.18
Nodes (13): _ALIASES is a fallback, never a rewrite, App index: Get-StartApps + App Paths + PATH, open_app's ordered match bands, providers/connectivity.py, Filename ranking reuses tools/apps.score, _GROUNDING_TEMPLATE / stable_prefix(has_tools=...), A refusal names the limit once, then points somewhere, Stable-first prompt assembly and the KV cache (+5 more)

### Community 67 - "package.json"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 68 - "eval_quality.py"
Cohesion: 0.08
Nodes (39): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+31 more)

### Community 69 - "HistoryPanel.tsx"
Cohesion: 0.24
Nodes (7): clockTime(), dayGroup(), HistoryPanel(), label(), Row(), RowProps, session()

### Community 70 - "Settings"
Cohesion: 0.23
Nodes (6): BaseSettings, Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Create the runtime directory tree. Safe to call repeatedly., Sidecar settings, loaded once per process., Settings

### Community 71 - "configure_logging"
Cohesion: 0.29
Nodes (9): configure_logging(), _console_handler(), _file_handler(), Handler, Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file. (+1 more)

### Community 72 - "db.py"
Cohesion: 0.19
Nodes (13): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Open the database with sqlite-vec loaded and the required pragmas set. (+5 more)

### Community 73 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 74 - "WakeWord"
Cohesion: 0.12
Nodes (7): Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, ndarray, Protocol, What the listener depends on, so it never imports openwakeword., WakeWord

### Community 75 - "Sidebar.tsx"
Cohesion: 0.15
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 76 - "database"
Cohesion: 0.29
Nodes (9): conn(), database(), db_path(), Connection, fixture, Path, Shared fixtures. Every test gets a throwaway data dir — never the real data/., A migrated database on a temp path. (+1 more)

### Community 77 - "preload.ts"
Cohesion: 0.25
Nodes (6): api, AriaApi, BrainStatus, LogLine, SidecarEvent, Unsubscribe

### Community 78 - "make_tray_icons.py"
Cohesion: 0.36
Nodes (7): _chunk(), coverage(), main(), png_bytes(), Generate the tray icon PNGs embedded in electron/tray.ts. Electron's…, Fraction of one pixel covered by the circle, by supersampling., An 8-bit RGBA PNG of a filled circle on transparency.

### Community 79 - "gate_tool_selection.py"
Cohesion: 0.27
Nodes (10): choose_with(), cosine(), main(), measure_choice(), measure_recall(), Should tool schemas be filtered by relevance before the model sees them? §7.2…, Does a shorter list make the model choose better? Measured, not assumed., Would a selector keep the right tool? The question that decides it. (+2 more)

### Community 80 - "useConversation.ts"
Cohesion: 0.36
Nodes (9): appendToStreaming(), clearStreaming(), finalise(), ToolCall, toTurns(), Turn, TurnCompletePayload, useConversation (+1 more)

### Community 81 - "Barge-in"
Cohesion: 0.33
Nodes (7): Cancel emits audio.stop, Barge-in, Duck first, decide after, A duck must always resume (_unduck), Esc stops her, claimed only while she speaks, Only her name or a stop word cuts her off, voice.playing (renderer reports playback)

### Community 82 - "WebSocket JSON-RPC 2.0 IPC contract"
Cohesion: 0.22
Nodes (9): Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation, Security model — localhost, keyring, path allowlist, Bearer token handshake on the WS upgrade (+1 more)

### Community 83 - "ToolJournal"
Cohesion: 0.29
Nodes (4): Any, Where every tool call is recorded (BUILD_SPEC §7.3, CLAUDE.md rule 6). Append-…, Writes to `tool_log`. Satisfies `tools.permissions.Journal`., ToolJournal

### Community 84 - "Orb.tsx"
Cohesion: 0.33
Nodes (6): BREATH, HUE, Orb(), ORB_LAYOUT_ID, OrbProps, SPINS

### Community 85 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, sidecar, test, typecheck

### Community 86 - "SettingsPanel.tsx"
Cohesion: 0.33
Nodes (3): KEY_HELP, KEY_LABEL, RowProps

### Community 87 - "Torch-free Python sidecar"
Cohesion: 0.40
Nodes (5): Phase 9 — Packaging, Torch-free Python sidecar, requests pinned explicitly — undeclared faster-whisper dep, kokoro-onnx conflicts with §4's onnxruntime/numpy pins, openai and google-genai deliberately absent; httpx instead

### Community 88 - "apps.py"
Cohesion: 0.07
Nodes (37): §7.2's second failure mode: the model gets one line, the UI gets the lot., test_a_real_name_is_not_treated_as_a_category(), test_listing_windows_summarises_rather_than_dumps(), _bring_to_front(), close_app(), _closest_ratio(), default_app(), _entry_for_prog_id() (+29 more)

### Community 89 - "ConfirmDialog.tsx"
Cohesion: 0.40
Nodes (3): ConfirmRequest, Props, TIER_LABEL

### Community 91 - "ModelPicker.test.tsx"
Cohesion: 0.60
Nodes (3): entry(), model(), models()

### Community 92 - "VoiceAura.tsx"
Cohesion: 0.40
Nodes (3): AuraMode, HUE, Props

### Community 93 - "ScreenRim.tsx"
Cohesion: 0.40
Nodes (3): HUE, Props, RimMode

### Community 96 - "useAudio.ts"
Cohesion: 0.67
Nodes (3): AudioChunk, decodePcm16(), useAudio

### Community 97 - "useMic.ts"
Cohesion: 0.67
Nodes (3): encodePcm16(), Recording, useMic

### Community 98 - "Persona boundaries — capacity to push back"
Cohesion: 0.67
Nodes (3): Persona boundaries — capacity to push back, Character, not sycophancy, aria.yaml persona configuration

### Community 99 - "Nightly reflection prompt (reflect.j2)"
Cohesion: 0.67
Nodes (3): Fact merge and supersession logic, Phase 5 — Memory, Nightly reflection prompt (reflect.j2)

### Community 113 - "._build_context"
Cohesion: 0.22
Nodes (5): Any, StoredMessage, What the model is allowed to know exists. None rather than an empty list when…, Facts already in hand — no query, no probe, nothing on the hot path. The…, Compress the oldest turns without the current turn waiting for it. One at a…

### Community 155 - "graphify update . (AST-only refresh)"
Cohesion: 0.38
Nodes (7): graphify cluster-only ., graphify update . --force, Two benign extractor gaps, graphify-out/ (graph.json, graph.html, GRAPH_REPORT.md), Graph shrink guard, graphify update . (AST-only refresh), Keep the knowledge graph current

### Community 156 - ".cancel"
Cohesion: 0.29
Nodes (3): Remove a conversation. Cancels it first if it is the one in flight., Abort an in-flight turn. Returns False if it was already finished., Cancel every in-flight turn. Returns how many there were. Barge-in has no turn…

### Community 157 - "spawn"
Cohesion: 0.33
Nodes (5): Any, Fire-and-forget work that must not take the process down with it. Two rules,…, Run `coro` detached. Failures are logged against `name`, never raised., spawn(), Task

### Community 158 - "_drain_windows"
Cohesion: 0.25
Nodes (7): _drain_windows(), parts(), phrase(), fixture, Cancel every listening window a test left open. Not optional: ARMED and OPEN…, openWakeWord gating — `hey jarvis` opens capture., The default: any speech is captured, and the transcript decides.

### Community 159 - "set_discovered"
Cohesion: 0.22
Nodes (10): Replace what the providers said they offer. A curated id always wins: `gpt-5`…, set_discovered(), discovered(), fixture, ModelInfo, None means "send nothing and let the provider decide" — the only safe default,…, One discovered model, removed again afterwards. The overlay is module state, so…, `gpt-5` comes back from the API as a bare id with no caveat and no latency.… (+2 more)

### Community 160 - "ToolsPanel.tsx"
Cohesion: 0.40
Nodes (3): TIER_LABEL, TIER_STYLE, ToolSummary

### Community 162 - "ModelHealth"
Cohesion: 0.29
Nodes (3): ModelHealth, BaseModel, Rolling health for one model id.

### Community 165 - "Sender"
Cohesion: 0.33
Nodes (4): Protocol, Send the current state to one client, unconditionally. A reconnecting renderer…, Minimal transport surface — a Starlette WebSocket satisfies this., Sender

### Community 169 - "._finish"
Cohesion: 0.33
Nodes (3): SessionSummary, The history list, plus a nudge to name anything still unnamed. Conversations…, Name the conversation once it has enough content to name. Deliberately fire-…

### Community 170 - "._generate_title"
Cohesion: 0.33
Nodes (3): Reload the conversation — the Phase 1 gate's relaunch requirement., Hold until no turn is in flight. False if the user never stops., Ask the local model for a short label. Never raises.

### Community 172 - "by_class"
Cohesion: 0.33
Nodes (6): by_class(), local_models(), The router's pool, and **curated only**. Reading `all_models()` here would let…, **The load-bearing test of the whole feature.** `by_class` is the router's only…, test_each_class_has_a_cloud_model_so_routing_can_resolve(), test_smart_never_routes_to_a_discovered_model()

### Community 173 - "kokoro-onnx TTS on CPU"
Cohesion: 0.40
Nodes (5): Chunks carry an index; renderer plays by index, kokoro-onnx TTS on CPU, Reasoning is never spoken, SpeechStream, Always send "think": false to Ollama

### Community 174 - "persona_for"
Cohesion: 0.40
Nodes (5): persona_for(), Persona level for a model; unknown ids get the safe, minimal prompt., Nothing is known about how it behaves, so it gets the safe prompt., test_persona_for_a_discovered_model_is_minimal(), test_persona_for_unknown_model_is_the_safe_minimal_prompt()

### Community 178 - "test_fresh_database_lands_on_the_current_version"
Cohesion: 0.67
Nodes (3): Connection, test_fresh_database_lands_on_the_current_version(), test_selected_model_is_seeded_to_smart()

## Knowledge Gaps
- **197 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+192 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **52 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConversationService` connect `ConversationService` to `conversation.py`, `Event`, `GenerationOptions`, `test_permissions.py`, `test_tts.py`, `ConversationStore`, `Listener`, `KokoroTTS`, `Tier`, `Router`, `test_conversation.py`, `ToolContext`, `HealthTracker`, `.cancel`, `EventBus`, `catalog.py`, `._free_vram_for`, `FakeProvider`, `main.py`, `Database`, `Runtime`, `._finish`, `._generate_title`, `ChatMessage`, `RoutingBias`, `._stream_one`, `_start_conversation`, `eval_quality.py`, `WakeWord`, `._build_context`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `HealthTracker` connect `HealthTracker` to `catalog.py`, `FakeProvider`, `ModelHealth`, `conversation.py`, `ConversationService`, `Database`, `discovery.py`, `RoutingBias`, `AvailabilityService`, `test_router.py`, `test_a_short_code_request_is_not_answered_locally_to_save_time`, `Router`, `test_conversation.py`, `test_a_spoken_turn_still_stays_local`, `test_ordinary_questions_do_not_get_the_expensive_tier`, `test_catalog.py`, `parametrize`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `FakeProvider`, `Indexer`, `.run`, `main.py`, `finder.py`, `conversation.py`, `db.py`, `SettingsStore`, `Runtime`, `test_tts.py`, `ConversationStore`, `RoutingBias`, `database`, `KokoroTTS`, `test_db.py`, `test_fresh_database_lands_on_the_current_version`, `ToolJournal`, `test_conversation.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `RouteDecision`) actually correct?**
  _`ConversationService` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Database` (e.g. with `Recorder` and `Indexer`) actually correct?**
  _`Database` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 14 INFERRED edges - model-reasoned connections that need verification._