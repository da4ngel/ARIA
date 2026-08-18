# Graph Report - ARIA  (2026-08-11)

## Corpus Check
- 166 files · ~160,745 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3075 nodes · 6822 edges · 197 communities (146 shown, 51 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 755 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8e4993c4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.ts
- test_context.py
- probes.py
- Indexer
- conversation.py
- test_finder.py
- ConversationService
- SettingsStore
- SileroVAD
- ProviderUnavailable
- test_permissions.py
- SpeechStream
- test_episodic.py
- test_semantic.py
- Listener
- state.py
- AvailabilityService
- apps.py
- test_router.py
- test_tools.py
- Tier
- Router
- test_conversation.py
- ToolResult
- test_scheduler.py
- test_catalog.py
- HealthTracker
- test_discovery.py
- test_listener.py
- Connectivity
- Event
- compilerOptions
- catalog.py
- OllamaEmbeddings
- Tool contract — decorator, ToolResult, derived schemas
- compilerOptions
- method
- main.py
- Database
- test_rpc.py
- HealthReport
- test_reflection.py
- Utterance
- Semantic file index (nomic-embed-text)
- ChatMessage
- RoutingBias
- scripts/eval_quality.py
- Phase 3 — the tool contract
- test_db.py
- Phase 2 — Voice
- CredentialKey
- ToolContext
- open_app's ordered match bands
- RpcMethodError
- bridge.d.ts
- Electron main + Python sidecar architecture
- The screen overlay window
- listener.py
- parametrize
- devDependencies
- ._stream_one
- _require_memory
- LLMProvider
- GenerationOptions
- App.tsx
- ListenerState.ARMED
- _GROUNDING_TEMPLATE / stable_prefix(has_tools=...)
- package.json
- ProviderError
- HistoryPanel.tsx
- _start_conversation
- configure_logging
- score
- ModelPicker.tsx
- ConversationStore
- Sidebar.tsx
- Fact
- preload.ts
- make_tray_icons.py
- PersonaLevel
- useConversation.ts
- Barge-in
- WakeWord
- db.py
- Orb.tsx
- scripts
- SettingsPanel.tsx
- Torch-free Python sidecar
- GeminiProvider
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
- EpisodicMemory
- discovered
- ToolsPanel.tsx
- StreamDelta
- ModelHealth
- eval_quality.py
- test_vectors.py
- EventBus
- WindowControls.tsx
- discovery.py
- context.py
- retrieved_block
- .run
- migrate
- overhead_tokens
- ToolCallCard.tsx
- database
- gate_delete.py
- MemoryPanel.test.tsx
- Provider strategy — OpenAI and Gemini, not Anthropic
- MemoryPanel.tsx
- normalise
- gate_memory.py
- useMemory.ts
- handlers.py
- default_local
- Runtime
- ._finish
- ._generate_title
- ._run_turn
- persona_for
- Expect
- .refresh_discovered
- autoprefixer
- test_a_short_code_request_is_not_answered_locally_to_save_time
- test_ordinary_questions_do_not_get_the_expensive_tier
- test_a_spoken_turn_still_stays_local

## God Nodes (most connected - your core abstractions)
1. `Database` - 145 edges
2. `ConversationStore` - 102 edges
3. `HealthTracker` - 97 edges
4. `ConversationService` - 89 edges
5. `SemanticMemory` - 87 edges
6. `ChatMessage` - 75 edges
7. `Listener` - 62 edges
8. `ToolResult` - 61 edges
9. `ToolContext` - 61 edges
10. `EpisodicMemory` - 58 edges

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
- **KV-cache latency discipline across prompt assembly** — build_spec_stable_prefix_ordering, build_spec_prefill_cost [INFERRED 0.85]

## Communities (197 total, 51 thin omitted)

### Community 0 - "main.ts"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 1 - "test_context.py"
Cohesion: 0.16
Nodes (28): machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, volatile_prefix(), full(), Machine context: the clock, the model, and what it costs to carry them. (+20 more)

### Community 2 - "probes.py"
Cohesion: 0.12
Nodes (25): Check, admits_ignorance(), answers_flatly(), contains(), contains_any(), denies_capability(), exact(), excludes() (+17 more)

### Community 3 - "Indexer"
Cohesion: 0.08
Nodes (38): chunk(), _digest(), extract_text(), Indexer, IndexStats, _pack(), Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks… (+30 more)

### Community 4 - "conversation.py"
Cohesion: 0.09
Nodes (26): ConversationHistory, ProviderRegistry, BaseModel, Turn orchestration (BUILD_SPEC §9 Phase 1). One turn: persist the user message,…, `chat.send` result (§7.1)., Providers keyed by name, so the service can follow the router's choice., `chat.history` result. Typed at the boundary per CLAUDE.md rule 7., TurnStarted (+18 more)

### Community 5 - "test_finder.py"
Cohesion: 0.06
Nodes (49): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), f(), parametrize, Finding files by name: the ranking, and the words people wrap around it. The…, if I say open cv … fetch the latest cv" — this is that, with an old draft and a…, budget_2026 is newer than every CV, and must not answer "cv"., Recency is a tiebreaker, never the whole answer. (+41 more)

### Community 6 - "ConversationService"
Cohesion: 0.11
Nodes (12): ConversationService, RoutingBias, Compress the oldest turns. Folds in any earlier note so it compounds., Owns in-flight turns. All durable state goes to SQLite., Persisted choice: a catalog id, or "smart" to let the router decide., Whether a turn is in flight. Read by the file indexer, which stops entirely…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, The control. Forcing every continuation local would throw away the cloud model… (+4 more)

### Community 7 - "SettingsStore"
Cohesion: 0.12
Nodes (18): Any, SettingsStore, Fill the overlay from cache. Returns whether it is still fresh. A stale cache…, Connection, fixture, parametrize, Durable settings and the v1 -> v2 migration. The migration matters more than…, Values are JSON so a new setting never needs another migration. (+10 more)

### Community 8 - "SileroVAD"
Cohesion: 0.09
Nodes (18): frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python…, say(), SilentBus (+10 more)

### Community 9 - "ProviderUnavailable"
Cohesion: 0.11
Nodes (17): ProviderRateLimited, ProviderUnavailable, The interface every LLM backend implements. Phase 1 only ships the Ollama…, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, The backend could not be reached — offline, not running, DNS, refused. Distinct…, _assemble(), OpenAIProvider, Any (+9 more)

### Community 10 - "test_permissions.py"
Cohesion: 0.08
Nodes (58): engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has…, Rule 6, and the entry most worth having. (+50 more)

### Community 11 - "SpeechStream"
Cohesion: 0.06
Nodes (42): Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., SpeechStream, ndarray, RuntimeError, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, Load and warm. The first synthesis is ~5x slower than the rest, and the user… (+34 more)

### Community 12 - "test_episodic.py"
Cohesion: 0.10
Nodes (37): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., _conversation(), _episodic(), anyio, Connection (+29 more)

### Community 13 - "test_semantic.py"
Cohesion: 0.06
Nodes (45): normalise_triple(), Fold a triple to its stored form. The UNIQUE index is on the raw columns, so…, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:…, §8.3 caps at 0.95. Repetition is evidence, not proof. (+37 more)

### Community 14 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 15 - "state.py"
Cohesion: 0.06
Nodes (39): Case, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance., run() (+31 more)

### Community 16 - "AvailabilityService"
Cohesion: 0.12
Nodes (13): ModelAvailability, AvailabilityService, Which models are usable right now. One object answers this for both…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand., Re-read the Credential Manager. Call after any key change. (+5 more)

### Community 17 - "apps.py"
Cohesion: 0.06
Nodes (53): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, AppEntry, _AppIndex, _bring_to_front(), _build_index(), close_app(), _closest_ratio() (+45 more)

### Community 18 - "test_router.py"
Cohesion: 0.11
Nodes (33): is_local(), RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort., Observed latency overrides the seeded table as turns land., The router must always answer. A turn with no candidates is a crash., Local models are multi-GB downloads that may not have finished. (+25 more)

### Community 19 - "test_tools.py"
Cohesion: 0.05
Nodes (58): parametrize, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, §7.2's second failure mode: the model gets one line, the UI gets the lot., 7 zip" matched "7-Zip Help" purely because it is the shorter name., The demotion must not make the entry unreachable., Opening the wrong app is worse than opening nothing., This is what stops "open youtube" launching the YouTube Music app: the website…, A dead end is useless; naming the closest lets the model retry. (+50 more)

### Community 20 - "Tier"
Cohesion: 0.07
Nodes (38): It is a strong constraint — it overrides the router — so it should be…, test_nothing_else_claims_local_only(), Launch, StrEnum, How an entry has to be started. Three sources, three launchers., Holds the pieces the content search needs. A module-level holder rather than…, _Semantic, Bus (+30 more)

### Community 21 - "Router"
Cohesion: 0.16
Nodes (13): BaseModel, ModelInfo, Chooses a model for a turn., Pick a model. `selected` is the user's choice — a model id, or "smart" to…, Cloud unless the turn is trivial. The default. `_DEEP_VERBS` is checked here…, Cloud for real work, local for conversation., Local unless the turn clearly needs more. What voice will want., Fastest observed first — the ranking self-corrects as turns land. (+5 more)

### Community 22 - "test_conversation.py"
Cohesion: 0.07
Nodes (54): MemoryServices, Everything Phase 5 hands to the conversation, as one argument.…, _drain(), FakeProvider, make_service(), anyio, fixture, Turn orchestration, cancellation, persistence and context roll-up. (+46 more)

### Community 23 - "ToolResult"
Cohesion: 0.08
Nodes (47): Path, Overwriting is a different destructive act from moving, and the user approved a…, The whole point: when it cannot be done she must say so, not claim it., A folder is a much larger promise than a file, and this tool says file., test_a_missing_file_is_said_plainly(), test_a_path_is_not_a_named_folder(), test_it_deletes_a_file_it_was_pointed_at(), test_it_moves_a_file() (+39 more)

### Community 24 - "test_scheduler.py"
Cohesion: 0.10
Nodes (34): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, The last time the clock passed `hour`:00, today or yesterday., Sweeps idle sessions, and runs reflection once per day., One pass. Never raises — a scheduler that dies stops everything. (+26 more)

### Community 25 - "test_catalog.py"
Cohesion: 0.15
Nodes (20): Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from., resolve_availability(), usable_ids(), entry_for(), Model availability — the one resolver behind both the picker and the router. If…, The picker builds its tooltip from these — an empty one is a blank box., `str.capitalize()` would render these 'Openai' — they are user-facing. (+12 more)

### Community 26 - "HealthTracker"
Cohesion: 0.11
Nodes (26): HealthTracker, In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture, Observed latency and the circuit breaker. A 429 is treated as a routing input…, An unmeasured model must not win a latency ranking by default., A fresh process re-probes rather than assuming the worst., A stale seed must self-correct rather than misroute forever., A 429 is not transient the way a dropped connection is. (+18 more)

### Community 27 - "test_discovery.py"
Cohesion: 0.11
Nodes (29): parse_openai(), Chat models from a `GET /v1/models` body., gemini_ids(), _load(), openai_ids(), Any, fixture, parametrize (+21 more)

### Community 28 - "test_listener.py"
Cohesion: 0.06
Nodes (69): drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on… (+61 more)

### Community 29 - "Connectivity"
Cohesion: 0.13
Nodes (20): Connectivity, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception, MonkeyPatch (+12 more)

### Community 30 - "Event"
Cohesion: 0.07
Nodes (26): Bus, ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout. (+18 more)

### Community 31 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 32 - "catalog.py"
Cohesion: 0.11
Nodes (28): all_models(), by_class(), discovered(), get(), local_models(), ModelInfo, ModelListing, BaseModel (+20 more)

### Community 33 - "OllamaEmbeddings"
Cohesion: 0.06
Nodes (40): Episode, BaseModel, A row from `episodes`, as the panel and retrieval see it., _age_days(), _content_words(), _overlap(), _percentile(), datetime (+32 more)

### Community 34 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (28): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+20 more)

### Community 35 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 36 - "method"
Cohesion: 0.10
Nodes (28): chat_cancel(), chat_history(), chat_new(), chat_send(), chat_sessions(), confirm_respond(), method(), models_list() (+20 more)

### Community 37 - "main.py"
Cohesion: 0.10
Nodes (29): FastAPI, get, bearer_from_header(), clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds…, Use the token Electron supplied, or mint one for standalone runs., Publish the token for a client that did not supply one. Written after the… (+21 more)

### Community 38 - "Database"
Cohesion: 0.11
Nodes (35): Database, Async-safe wrapper around the single sqlite connection., Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are… (+27 more)

### Community 39 - "test_rpc.py"
Cohesion: 0.12
Nodes (32): Run ``fn`` against the connection off the event loop, serialised., method_names(), _auth(), _call(), client(), fixture, MonkeyPatch, parametrize (+24 more)

### Community 40 - "HealthReport"
Cohesion: 0.16
Nodes (20): dispatch(), HealthReport, _invoke(), BaseModel, Rich health snapshot for the UI (§7.1 ``system.health``, §9.6)., Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., err() (+12 more)

### Community 41 - "test_reflection.py"
Cohesion: 0.08
Nodes (36): build_prompt(), choose_model(), _extract_json(), Any, §8.3's prompt, with the two slots filled., §8.3: cloud if a key is present, local otherwise. Walks SMART then BALANCED,…, Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio (+28 more)

### Community 42 - "Utterance"
Cohesion: 0.10
Nodes (9): ndarray, Protocol, Voice activity detection — streaming Silero (BUILD_SPEC §9 Phase 2 stage 3).…, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance (+1 more)

### Community 43 - "Semantic file index (nomic-embed-text)"
Cohesion: 0.12
Nodes (19): AppData in the skip list hides %TEMP%, Tests must set ARIA_INDEX_FILES=false, ARIA — local-first Windows AI assistant, ARIA_TOKEN handshake, Bounded scan instead of Everything, BUILD_SPEC.md, Electron renderer (pure view), graphify check-update . (+11 more)

### Community 44 - "ChatMessage"
Cohesion: 0.20
Nodes (14): assemble(), Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, Build the final message list, stable content first., split_for_rollup(), ChatMessage, One turn on the wire to a provider., The KV-cache bargain, asserted directly. CLAUDE.md's measured rule: an…, test_machine_context_sits_after_identity_and_before_the_turns() (+6 more)

### Community 45 - "RoutingBias"
Cohesion: 0.10
Nodes (21): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+13 more)

### Community 46 - "scripts/eval_quality.py"
Cohesion: 0.13
Nodes (18): Chunks carry an index; renderer plays by index, num_gpu: 0 on every embedding call, scripts/eval_quality.py, Read fabricated and over-refused together, A gate that supplies the precondition tests the mechanism, not the feature, kokoro-onnx TTS on CPU, Never set temperature on a reasoning model, Switching local models evicts the old one first (+10 more)

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
Cohesion: 0.17
Nodes (17): all_status(), CredentialKey, CredentialStatus, delete_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Credential Manager entry names under the ARIA service. (+9 more)

### Community 51 - "ToolContext"
Cohesion: 0.08
Nodes (40): test_system_info_reports_this_machine(), tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, The clipboard's text, or None when it holds something else. An image, a file…, Read the clipboard's text., _read(), read_clipboard() (+32 more)

### Community 52 - "open_app's ordered match bands"
Cohesion: 0.13
Nodes (16): _ALIASES is a fallback, never a rewrite, App index: Get-StartApps + App Paths + PATH, open_app's ordered match bands, Filename ranking reuses tools/apps.score, Filler words are stripped first, A refusal names the limit once, then points somewhere, Cloud vendors reached over httpx, not their SDKs, MATCH_FLOOR (+8 more)

### Community 53 - "RpcMethodError"
Cohesion: 0.12
Nodes (17): chat_delete(), chat_rename(), memory_reflect(), models_bias(), models_select(), Persist the model choice: a catalog id, or "smart"., Read or set what Smart mode optimises for. Phase 2 flips this to "fastest" for…, Read or set whether the sidecar accepts a continuous audio stream. Turning this… (+9 more)

### Community 54 - "bridge.d.ts"
Cohesion: 0.10
Nodes (19): AriaApi, AssistantState, BrainStatus, CredentialStatus, LogLine, MemoryEpisode, MemoryFact, MemoryStats (+11 more)

### Community 55 - "Electron main + Python sidecar architecture"
Cohesion: 0.09
Nodes (22): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation (+14 more)

### Community 56 - "The screen overlay window"
Cohesion: 0.16
Nodes (14): backgroundThrottling: false is not sufficient, Audio frames go over a JSON-RPC notification, Hands-free is on by default, The indexer throttle is the feature, listener.frame_rate, @method("name") in rpc/handlers.py, The screen overlay window, sendToRenderer broadcasts to both windows (+6 more)

### Community 57 - "listener.py"
Cohesion: 0.11
Nodes (24): clips(), main(), ndarray, Can she hear her own name? Across many voices, because one is not a test.…, score(), is_stop_word(), _near_the_name(), Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3). The renderer opens the… (+16 more)

### Community 58 - "parametrize"
Cohesion: 0.17
Nodes (13): is_trivial(), needs_deep_model(), A greeting or acknowledgement — nothing a 4B model can get wrong., Reasoning, code, or a multi-step request: the `smart` class earns its cost., parametrize, The line that was missing. Without it these went to the FAST class., test_clipboard_questions_stay_on_this_machine(), test_code_requests_reach_a_reasoning_model() (+5 more)

### Community 59 - "devDependencies"
Cohesion: 0.15
Nodes (13): electron, devDependencies, electron, postcss, react, react-dom, @types/ws, zustand (+5 more)

### Community 60 - "._stream_one"
Cohesion: 0.20
Nodes (7): ModelInfo, ToolCall, Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, Run the first requested tool, then let the model answer with it. **One tool,…, Which model gets to see the tool's result. `router._PRIVATE` already keeps a…, Evict the previous local model before loading a different one. CLAUDE.md rule…, Evict `model` from VRAM now, instead of after `keep_alive`. CLAUDE.md rule 2:…

### Community 61 - "_require_memory"
Cohesion: 0.17
Nodes (12): memory_forget(), memory_list(), memory_search(), memory_stats(), memory_update(), The memory services, or a message saying how to turn them on., Everything she has learned, for MemoryPanel. Superseded facts are excluded by…, §7.1: search what she remembers. The same path a turn uses. (+4 more)

### Community 62 - "LLMProvider"
Cohesion: 0.07
Nodes (33): Idle sweeps always; the nightly §8.3 pass only if it is wanted., _start_memory_scheduler(), ExtractedEpisode, ExtractedFact, BaseModel, datetime, ModelInfo, Reflection — where "learns on its own" actually lives (BUILD_SPEC §8.3). Once a… (+25 more)

### Community 63 - "GenerationOptions"
Cohesion: 0.09
Nodes (20): HTTPError, GenerationOptions, Any, Stream a completion. Cancellation is cooperative: cancelling the consuming task…, Common `[{role, content}]` shape most chat APIs accept. Tool fields are only…, Provider-neutral knobs. Providers map these onto their own APIs., to_wire(), OllamaProvider (+12 more)

### Community 64 - "App.tsx"
Cohesion: 0.40
Nodes (3): drag, noDrag, Overlay

### Community 65 - "ListenerState.ARMED"
Cohesion: 0.16
Nodes (14): ListenerState.ARMED, Blue means she is listening to you, The follow-up window was removed, Fuzzy name matching on the first word, hotwords="Aria" makes it worse, measured, listener.heard logs the words, not chars=42, listener.not_addressed logs the transcript, _rearm() — a false start must not disarm her (+6 more)

### Community 66 - "_GROUNDING_TEMPLATE / stable_prefix(has_tools=...)"
Cohesion: 0.24
Nodes (10): providers/connectivity.py, FIRST_CHUNK_MAX_CHARS = 32, _GROUNDING_TEMPLATE / stable_prefix(has_tools=...), Stable-first prompt assembly and the KV cache, context.machine_context(), Being reached over the internet is not having internet, Roll-up (_summarize / _maybe_roll_up) runs in the background, scripts/soak_conversation.py (30-turn soak) (+2 more)

### Community 67 - "package.json"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 68 - "ProviderError"
Cohesion: 0.16
Nodes (19): build_messages(), _is_reasoning(), provider_for(), ModelInfo, Exactly what the app would send: stable prefix first, then the turns., run_probe(), main(), measure_honesty() (+11 more)

### Community 69 - "HistoryPanel.tsx"
Cohesion: 0.24
Nodes (7): clockTime(), dayGroup(), HistoryPanel(), label(), Row(), RowProps, session()

### Community 70 - "_start_conversation"
Cohesion: 0.10
Nodes (20): BaseSettings, Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Create the runtime directory tree. Safe to call repeatedly., Sidecar settings, loaded once per process., Settings, _build_indexer(), _build_memory() (+12 more)

### Community 71 - "configure_logging"
Cohesion: 0.21
Nodes (12): configure_logging(), _console_handler(), _file_handler(), Handler, Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file. (+4 more)

### Community 72 - "score"
Cohesion: 0.18
Nodes (11): 1.0 today, 0.5 after a month, never quite zero., §9 Phase 5: 0.6·cosine + 0.25·recency + 0.15·salience, boosted by access. Two…, recency_decay(), score(), A memory that keeps coming up is worth surfacing, but not enough to outrank…, 0.6·cosine + 0.25·recency + 0.15·salience, plus the access nudge., 0.6 against 0.25 — an old fact about the question beats a new one about…, test_recency_halves_over_a_month() (+3 more)

### Community 73 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 74 - "ConversationStore"
Cohesion: 0.10
Nodes (31): ConversationStore, Most recently started session, for reload-on-launch., A fresh id with no row behind it yet. `ensure_session` creates a row for any id…, Name a conversation. The `with conn:` is load-bearing. Python's sqlite3 opens…, Remove a conversation and everything in it. Returns messages deleted. Both…, CRUD over `sessions` and `messages`., make_session(), fixture (+23 more)

### Community 75 - "Sidebar.tsx"
Cohesion: 0.14
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 76 - "Fact"
Cohesion: 0.09
Nodes (16): Fact, _now(), Row, The form that gets embedded and shown in the prompt., A stored `fact_vec` row back into floats, or None if it has no vector., Merge one observation into the store, per §8.3. Order matters: 1. **Exact…, §8.3: exact triple → evidence_count += 1, confidence += 0.1 (cap 0.95)., Edit a fact from the panel. Returns None if it is gone. (+8 more)

### Community 77 - "preload.ts"
Cohesion: 0.25
Nodes (6): api, AriaApi, BrainStatus, LogLine, SidecarEvent, Unsubscribe

### Community 78 - "make_tray_icons.py"
Cohesion: 0.36
Nodes (7): _chunk(), coverage(), main(), png_bytes(), Generate the tray icon PNGs embedded in electron/tray.ts. Electron's…, Fraction of one pixel covered by the circle, by supersampling., An 8-bit RGBA PNG of a filled circle on transparency.

### Community 79 - "PersonaLevel"
Cohesion: 0.17
Nodes (15): choose_with(), cosine(), main(), measure_choice(), measure_recall(), Should tool schemas be filtered by relevance before the model sees them? §7.2…, Does a shorter list make the model choose better? Measured, not assumed., Would a selector keep the right tool? The question that decides it. (+7 more)

### Community 80 - "useConversation.ts"
Cohesion: 0.36
Nodes (9): appendToStreaming(), clearStreaming(), finalise(), ToolCall, toTurns(), Turn, TurnCompletePayload, useConversation (+1 more)

### Community 81 - "Barge-in"
Cohesion: 0.33
Nodes (7): Cancel emits audio.stop, Barge-in, Duck first, decide after, A duck must always resume (_unduck), Esc stops her, claimed only while she speaks, Only her name or a stop word cuts her off, voice.playing (renderer reports playback)

### Community 82 - "WakeWord"
Cohesion: 0.07
Nodes (17): main(), Download the wake word weights into data/models/openwakeword. python…, Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, missing_models(), ndarray, Path (+9 more)

### Community 83 - "db.py"
Cohesion: 0.13
Nodes (9): SQLite connection, sqlite-vec loading, and the migration runner. One connection…, _now(), Return an existing session id, or create one., Write the fact and its vector in one transaction. One transaction is not…, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, Any, Where every tool call is recorded (BUILD_SPEC §7.3, CLAUDE.md rule 6). Append-…, Writes to `tool_log`. Satisfies `tools.permissions.Journal`. (+1 more)

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

### Community 88 - "GeminiProvider"
Cohesion: 0.13
Nodes (12): get_key(), Read a key, or None if unset. Never logs the value., _function_call_part(), GeminiProvider, Any, Response, ToolCall, Google Gemini provider (BUILD_SPEC §4, §9.7). Raw HTTP against… (+4 more)

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
Cohesion: 0.18
Nodes (6): Any, StoredMessage, Facts already in hand — no query, no probe, nothing on the hot path. The…, Compress the oldest turns without the current turn waiting for it. One at a…, What the model is allowed to know exists. None rather than an empty list when…, Collect what `send()` started. None when memory is off or it failed. Retrieval…

### Community 155 - "graphify update . (AST-only refresh)"
Cohesion: 0.38
Nodes (7): graphify cluster-only ., graphify update . --force, Two benign extractor gaps, graphify-out/ (graph.json, graph.html, GRAPH_REPORT.md), Graph shrink guard, graphify update . (AST-only refresh), Keep the knowledge graph current

### Community 156 - ".cancel"
Cohesion: 0.29
Nodes (3): Remove a conversation. Cancels it first if it is the one in flight., Abort an in-flight turn. Returns False if it was already finished., Cancel every in-flight turn. Returns how many there were. Barge-in has no turn…

### Community 157 - "spawn"
Cohesion: 0.33
Nodes (5): Any, Task, Fire-and-forget work that must not take the process down with it. Two rules,…, Run `coro` detached. Failures are logged against `name`, never raised., spawn()

### Community 158 - "EpisodicMemory"
Cohesion: 0.10
Nodes (13): EpisodicMemory, _now(), datetime, Row, StoredMessage, Summarize every conversation that has gone quiet. Returns how many., Summarize one session into an episode. Idempotent; never raises. `ended_at` is…, Drop a session's episodes, so the session itself can be deleted.… (+5 more)

### Community 159 - "discovered"
Cohesion: 0.33
Nodes (6): discovered(), fixture, ModelInfo, None means "send nothing and let the provider decide" — the only safe default,…, One discovered model, removed again afterwards. The overlay is module state, so…, test_temperature_defaults_to_none()

### Community 160 - "ToolsPanel.tsx"
Cohesion: 0.40
Nodes (3): TIER_LABEL, TIER_STYLE, ToolSummary

### Community 161 - "StreamDelta"
Cohesion: 0.15
Nodes (17): BaseModel, A model asking for a tool to be run. `id` is the provider's handle for the call…, One chunk of a streaming response. `text` carries *content only*. Reasoning…, StreamDelta, ToolCall, OpenEngine, Any, ToolCall (+9 more)

### Community 162 - "ModelHealth"
Cohesion: 0.18
Nodes (4): ModelHealth, BaseModel, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id.

### Community 163 - "eval_quality.py"
Cohesion: 0.16
Nodes (15): Namespace, main(), _pulled_models(), Answer-quality and hallucination battery. Run it, change something, run again.…, Declined or hedged a solid fact. The counter-metric — a hallucination fix that…, The individual failures worth a human reading. A rate tells you there is a…, Answered something that has no answer, or claimed an action it cannot perform.…, report() (+7 more)

### Community 164 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 165 - "EventBus"
Cohesion: 0.14
Nodes (12): EventBus, Any, Protocol, Server -> client push notifications and the set of live connections (§7.1).…, Send the current state to one client, unconditionally. A reconnecting renderer…, Send a notification to every live client, dropping dead ones., Update the assistant state and notify clients if it actually changed., Minimal transport surface — a Starlette WebSocket satisfies this. (+4 more)

### Community 168 - "discovery.py"
Cohesion: 0.15
Nodes (20): discover_all(), discover_gemini(), discover_openai(), _fetch(), _gemini_class(), _gemini_is_chat(), _gemini_is_duplicate(), _openai_class() (+12 more)

### Community 169 - "context.py"
Cohesion: 0.12
Nodes (16): clean_title(), episode_request(), _persona(), datetime, StoredMessage, Prompt assembly and the rolling context window (BUILD_SPEC §8.2, §9 Phase 1).…, Fill in what she can reach. Everything else is identical., Prompt asking the model to compress a whole session into an episode. Distinct… (+8 more)

### Community 170 - "retrieved_block"
Cohesion: 0.13
Nodes (17): estimate_tokens(), fit_to_budget(), Render remembered facts and episodes into one system message. Returns None when…, Drop oldest turns until the assembled prompt fits. Backstop, not policy.…, _render_memory(), retrieved_block(), A turn about something she has no memory of must leave the prompt byte-…, A fact is a standing truth; an episode is one conversation. (+9 more)

### Community 172 - ".run"
Cohesion: 0.16
Nodes (11): paths_in(), Any, Path, Replace the trusted set. Resolved once here rather than per call, and silently…, Whether every path in this call is somewhere she is trusted. **Every** path: a…, Gate a tool call, run it if allowed, and log it either way., Suspend until the user answers, or until the timeout denies for them., Rule 6: every call, with its args and result. Including refusals — a denial is… (+3 more)

### Community 173 - "migrate"
Cohesion: 0.20
Nodes (12): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, Open the database with sqlite-vec loaded and the required pragmas set., Bring the database up to :data:`SCHEMA_VERSION`. Returns the version applied.… (+4 more)

### Community 174 - "overhead_tokens"
Cohesion: 0.25
Nodes (8): overhead_tokens(), Tokens spent before the conversation even starts. Roll-up decisions must…, CLAUDE.md: keep the pre-conversation budget near 800 tokens on local., Roll-up decisions subtract this; if it were uncounted, a conversation could…, Uncounted, a roll-up could 'succeed' and still overflow the context — the same…, test_overhead_accounts_for_the_machine_block(), test_overhead_counts_the_retrieved_block(), test_the_whole_prefix_stays_within_the_local_budget()

### Community 176 - "database"
Cohesion: 0.29
Nodes (9): conn(), database(), db_path(), Connection, fixture, Path, Shared fixtures. Every test gets a throwaway data dir — never the real data/., A migrated database on a temp path. (+1 more)

### Community 178 - "MemoryPanel.test.tsx"
Cohesion: 0.43
Nodes (4): defaults(), episode(), fact(), stats()

### Community 179 - "Provider strategy — OpenAI and Gemini, not Anthropic"
Cohesion: 0.29
Nodes (8): Cloud providers call tools too, Keys in Windows Credential Manager via keyring, Provider strategy — OpenAI and Gemini, not Anthropic, core/router.py, Rule 10 — do not refactor prior phases, Smart-mode bias is a persisted setting, Gemini requires thoughtSignature echoed back, A tool turn is not a text turn

### Community 180 - "MemoryPanel.tsx"
Cohesion: 0.53
Nodes (5): confidenceStyle(), FactRow(), MemoryPanel(), summarise(), whenever()

### Community 181 - "normalise"
Cohesion: 0.25
Nodes (8): hedged(), leaks_prompt(), normalise(), Rules every reply obeys, regardless of what was asked., Did the reply decline to answer? Computed for every probe, so the over-refusal…, Fold typographic punctuation to ASCII so the patterns can match., refused(), universal_failures()

### Community 182 - "gate_memory.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 5's acceptance gate, against the running sidecar. "I usually work on…

### Community 184 - "handlers.py"
Cohesion: 0.32
Nodes (7): build_health(), JSON-RPC method registry and dispatch (BUILD_SPEC §7.1). Phase 0 registers only…, Every registered tool and the tier it runs at (rule 4, rule 6). Read-only, and…, Return the health snapshot. Never raises — the UI polls this., system_health(), tools_list(), uptime_seconds()

### Community 185 - "default_local"
Cohesion: 0.29
Nodes (7): default_local(), The local fallback. Prefers the instruction-tuned 7B. `pulled` is what Ollama…, Callers use this as a last resort; it must not raise., test_default_local_falls_back_to_what_is_actually_pulled(), test_default_local_prefers_the_instruction_tuned_7b(), test_default_local_with_nothing_pulled_still_returns_a_model(), test_default_local_without_argument_names_the_preferred_model()

### Community 187 - "._finish"
Cohesion: 0.33
Nodes (3): SessionSummary, The history list, plus a nudge to name anything still unnamed. Conversations…, Name the conversation once it has enough content to name. Deliberately fire-…

### Community 188 - "._generate_title"
Cohesion: 0.33
Nodes (3): Reload the conversation — the Phase 1 gate's relaunch requirement., Hold until no turn is in flight. False if the user never stops., Ask the local model for a short label. Never raises.

### Community 190 - "persona_for"
Cohesion: 0.40
Nodes (5): persona_for(), Persona level for a model; unknown ids get the safe, minimal prompt., Nothing is known about how it behaves, so it gets the safe prompt., test_persona_for_a_discovered_model_is_minimal(), test_persona_for_unknown_model_is_the_safe_minimal_prompt()

### Community 191 - "Expect"
Cohesion: 0.67
Nodes (3): Expect, StrEnum, What honest behaviour looks like for this probe. Drives the fabrication / over-…

## Knowledge Gaps
- **203 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+198 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConversationService` connect `ConversationService` to `conversation.py`, `ProviderUnavailable`, `test_permissions.py`, `SpeechStream`, `Listener`, `state.py`, `Tier`, `Router`, `test_conversation.py`, `HealthTracker`, `.cancel`, `Event`, `catalog.py`, `OllamaEmbeddings`, `StreamDelta`, `EventBus`, `main.py`, `ChatMessage`, `RoutingBias`, `ToolContext`, `listener.py`, `Runtime`, `._finish`, `._stream_one`, `._generate_title`, `._run_turn`, `LLMProvider`, `GenerationOptions`, `ProviderError`, `_start_conversation`, `ConversationStore`, `WakeWord`, `._build_context`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `Indexer`, `conversation.py`, `test_finder.py`, `SettingsStore`, `SpeechStream`, `test_episodic.py`, `test_semantic.py`, `state.py`, `test_conversation.py`, `EpisodicMemory`, `OllamaEmbeddings`, `StreamDelta`, `main.py`, `test_rpc.py`, `test_reflection.py`, `RoutingBias`, `migrate`, `database`, `test_db.py`, `Runtime`, `LLMProvider`, `ConversationStore`, `Fact`, `db.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `conversation.py`, `test_finder.py`, `ConversationService`, `test_permissions.py`, `SpeechStream`, `.run`, `apps.py`, `test_tools.py`, `Tier`, `ToolResult`, `._stream_one`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `Database` (e.g. with `Recorder` and `Episode`) actually correct?**
  _`Database` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `RouteDecision`) actually correct?**
  _`ConversationService` has 38 INFERRED edges - model-reasoned connections that need verification._