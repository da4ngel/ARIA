# Graph Report - ARIA  (2026-08-09)

## Corpus Check
- 146 files · ~129,634 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2515 nodes · 5298 edges · 172 communities (123 shown, 49 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 526 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2c9f4581`
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
- Database
- Event
- GenerationOptions
- test_permissions.py
- test_tts.py
- ConversationStore
- listener.py
- Listener
- KokoroTTS
- AvailabilityService
- apps.py
- test_router.py
- test_tools.py
- PermissionEngine
- Router
- test_conversation.py
- ToolContext
- OpenWakeWord
- test_catalog.py
- HealthTracker
- discovery.py
- test_listener.py
- Connectivity
- WakeMode
- compilerOptions
- catalog.py
- registry.py
- Tool contract — decorator, ToolResult, derived schemas
- compilerOptions
- method
- main.py
- OllamaProvider
- test_rpc.py
- protocol.py
- LLMProvider
- VoiceActivity
- Semantic file index (nomic-embed-text)
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
- The screen overlay window
- strip_wake_word
- Tier
- devDependencies
- SpeechStream
- handlers.py
- _start_conversation
- rpc
- App.tsx
- ListenerState.ARMED
- open_app's ordered match bands
- package.json
- eval_quality.py
- HistoryPanel.tsx
- _GROUNDING_TEMPLATE / stable_prefix(has_tools=...)
- configure_logging
- db.py
- ModelPicker.tsx
- WakeWord
- Sidebar.tsx
- RecordingBus
- preload.ts
- make_tray_icons.py
- gate_tool_selection.py
- useConversation.ts
- Barge-in
- FakeTTS
- ToolJournal
- Orb.tsx
- scripts
- SettingsPanel.tsx
- Torch-free Python sidecar
- list_windows
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
- autoprefixer
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
- ModelListing
- discovered
- ToolsPanel.tsx
- ._free_vram_for
- _Cache
- _Semantic
- .run
- Launch
- WindowControls.tsx
- .new_session
- .set_selected_model
- test_stable_prefix_is_byte_identical_across_calls

## God Nodes (most connected - your core abstractions)
1. `HealthTracker` - 96 edges
2. `ConversationService` - 78 edges
3. `Database` - 73 edges
4. `ConversationStore` - 71 edges
5. `ChatMessage` - 64 edges
6. `Listener` - 62 edges
7. `Router` - 49 edges
8. `ToolResult` - 49 edges
9. `ToolContext` - 49 edges
10. `Event` - 48 edges

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

## Communities (172 total, 49 thin omitted)

### Community 0 - "main.ts"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 1 - "test_context.py"
Cohesion: 0.11
Nodes (38): assemble(), estimate_tokens(), fit_to_budget(), machine_context(), MachineContext, overhead_tokens(), Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,… (+30 more)

### Community 2 - "probes.py"
Cohesion: 0.08
Nodes (36): Check, Answered something that has no answer, or claimed an action it cannot perform.…, admits_ignorance(), answers_flatly(), claimed_action(), contains(), contains_any(), denies_capability() (+28 more)

### Community 3 - "Indexer"
Cohesion: 0.06
Nodes (46): chunk(), _digest(), extract_text(), Indexer, IndexStats, _pack(), Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks… (+38 more)

### Community 4 - "conversation.py"
Cohesion: 0.08
Nodes (35): datetime, Row, clean_title(), _persona(), Prompt assembly and the rolling context window (BUILD_SPEC §8.2, §9 Phase 1).…, Fill in what she can reach. Everything else is identical., Strip what models add despite being told not to. Even with an explicit…, _relative_age() (+27 more)

### Community 5 - "finder.py"
Cohesion: 0.07
Nodes (48): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), f(), parametrize, Finding files by name: the ranking, and the words people wrap around it. The…, if I say open cv … fetch the latest cv" — this is that, with an old draft and a…, budget_2026 is newer than every CV, and must not answer "cv"., Recency is a tiebreaker, never the whole answer. (+40 more)

### Community 6 - "ConversationService"
Cohesion: 0.08
Nodes (17): SessionSummary, ConversationService, ModelInfo, RoutingBias, StoredMessage, Owns in-flight turns. All durable state goes to SQLite., Whether a turn is in flight. Read by the file indexer, which stops entirely…, The history list, plus a nudge to name anything still unnamed. Conversations… (+9 more)

### Community 7 - "Database"
Cohesion: 0.11
Nodes (20): Database, Async-safe wrapper around the single sqlite connection., Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, Connection, fixture, parametrize (+12 more)

### Community 8 - "Event"
Cohesion: 0.08
Nodes (23): frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python…, say(), SilentBus (+15 more)

### Community 9 - "GenerationOptions"
Cohesion: 0.07
Nodes (29): GenerationOptions, BaseModel, A model asking for a tool to be run. `id` is the provider's handle for the call…, One chunk of a streaming response. `text` carries *content only*. Reasoning…, Provider-neutral knobs. Providers map these onto their own APIs., StreamDelta, ToolCall, get_key() (+21 more)

### Community 10 - "test_permissions.py"
Cohesion: 0.14
Nodes (40): engine(), Any, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has…, Rule 6, and the entry most worth having., Models get argument names wrong. That is a thing to say, not to crash on. (+32 more)

### Community 11 - "test_tts.py"
Cohesion: 0.11
Nodes (23): ndarray, Speech synthesis — kokoro-onnx on CPU (BUILD_SPEC §9 Phase 2). CPU only, per…, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, Load and warm. The first synthesis is ~5x slower than the rest, and the user…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, split_for_speech(), to_pcm16(), drain_text() (+15 more)

### Community 12 - "ConversationStore"
Cohesion: 0.09
Nodes (34): ConversationStore, _now(), Sessions and messages — the durable conversation (BUILD_SPEC §7.3). This is…, Most recently started session, for reload-on-launch., A fresh id with no row behind it yet. `ensure_session` creates a row for any id…, Name a conversation. The `with conn:` is load-bearing. Python's sqlite3 opens…, Remove a conversation and everything in it. Returns messages deleted. Both…, CRUD over `sessions` and `messages`. (+26 more)

### Community 13 - "listener.py"
Cohesion: 0.07
Nodes (33): main(), measure(), missing_words(), normalise(), ndarray, Where the time goes between you stopping and her starting. python…, Words that actually went missing, ignoring differences nothing downstream cares…, clips() (+25 more)

### Community 14 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 15 - "KokoroTTS"
Cohesion: 0.09
Nodes (21): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+13 more)

### Community 16 - "AvailabilityService"
Cohesion: 0.09
Nodes (12): ModelAvailability, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+4 more)

### Community 17 - "apps.py"
Cohesion: 0.07
Nodes (48): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, `normalise("notepad++")` is `"notepad"`, which scored an exact 1.00 against the…, Asking for "notepad" may well mean Notepad++; the ranking can decide. Asking…, Only `+` and `#` name a different product. The 7-Zip cases depend on everything…, test_a_real_name_is_not_treated_as_a_category(), test_a_shared_symbol_still_matches(), test_hyphens_and_dots_are_still_noise() (+40 more)

### Community 18 - "test_router.py"
Cohesion: 0.09
Nodes (43): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort. (+35 more)

### Community 19 - "test_tools.py"
Cohesion: 0.07
Nodes (37): parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, Overwriting is a different destructive act from moving, and the user approved a…, 7 zip" matched "7-Zip Help" purely because it is the shorter name., The demotion must not make the entry unreachable., Opening the wrong app is worse than opening nothing., This is what stops "open youtube" launching the YouTube Music app: the website… (+29 more)

### Community 20 - "PermissionEngine"
Cohesion: 0.12
Nodes (15): paths_in(), PermissionEngine, Any, Path, Decides whether a tool may run, and records that it was asked., Replace the trusted set. Resolved once here rather than per call, and silently…, Whether every path in this call is somewhere she is trusted. **Every** path: a…, Gate a tool call, run it if allowed, and log it either way. (+7 more)

### Community 21 - "Router"
Cohesion: 0.12
Nodes (22): needs_deep_model(), BaseModel, ModelInfo, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, Reasoning, code, or a multi-step request: the `smart` class earns its cost., Chooses a model for a turn., Pick a model. `selected` is the user's choice — a model id, or "smart" to…, Cloud unless the turn is trivial. The default. `_DEEP_VERBS` is checked here… (+14 more)

### Community 22 - "test_conversation.py"
Cohesion: 0.06
Nodes (57): _drain(), FakeProvider, make_service(), OpenEngine, fixture, Turn orchestration, cancellation, persistence and context roll-up., Wait for all in-flight turns., The Phase 1 gate: kill the window, conversation reloads from SQLite. (+49 more)

### Community 23 - "ToolContext"
Cohesion: 0.13
Nodes (34): test_it_refuses_a_drive_root(), create_folder(), delete_file(), delete_folder(), _GUID, known_folder(), list_folder(), move_file() (+26 more)

### Community 24 - "OpenWakeWord"
Cohesion: 0.10
Nodes (15): main(), Download the wake word weights into data/models/openwakeword. python…, missing_models(), OpenWakeWord, Any, ndarray, Path, RuntimeError (+7 more)

### Community 25 - "test_catalog.py"
Cohesion: 0.10
Nodes (29): persona_for(), Persona level for a model; unknown ids get the safe, minimal prompt., Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from., resolve_availability(), usable_ids(), entry_for(), parametrize (+21 more)

### Community 26 - "HealthTracker"
Cohesion: 0.08
Nodes (31): HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture (+23 more)

### Community 27 - "discovery.py"
Cohesion: 0.07
Nodes (53): Cost, ModelClass, StrEnum, What a model is *for*. The router picks a class, then a model in it., discover_all(), discover_gemini(), discover_openai(), _fetch() (+45 more)

### Community 28 - "test_listener.py"
Cohesion: 0.06
Nodes (69): drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on… (+61 more)

### Community 29 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 30 - "WakeMode"
Cohesion: 0.07
Nodes (22): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Endpoint, Accumulates frames and decides when the speaker has finished. Deliberately not…, Why capture stopped, so the caller can tell an utterance from a timeout. (+14 more)

### Community 31 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 32 - "catalog.py"
Cohesion: 0.09
Nodes (33): Which models are usable right now. One object answers this for both…, all_models(), by_class(), default_local(), discovered(), get(), local_models(), ModelAvailability (+25 more)

### Community 33 - "registry.py"
Cohesion: 0.09
Nodes (29): fixture, A registry with one tool per tier, put back exactly as found. The snapshot…, test_a_required_argument_is_marked_required(), test_the_schema_comes_from_the_signature(), _tools(), DANGER is off by default, and a tool the model cannot see is one it cannot be…, test_deleting_is_never_offered_to_the_model_by_default(), all_tools() (+21 more)

### Community 34 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (28): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+20 more)

### Community 35 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 36 - "method"
Cohesion: 0.11
Nodes (26): chat_history(), chat_new(), chat_rename(), chat_send(), chat_sessions(), confirm_respond(), method(), Any (+18 more)

### Community 37 - "main.py"
Cohesion: 0.16
Nodes (18): FastAPI, get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds…, Use the token Electron supplied, or mint one for standalone runs. (+10 more)

### Community 38 - "OllamaProvider"
Cohesion: 0.11
Nodes (13): HTTPError, OllamaProvider, Any, Response, Ollama provider — the local brain, and the offline fallback (BUILD_SPEC §9.7).…, Reachability only — does not check whether any model is loaded., Load `model` with a 1-token request so the user never hits cold start., One NDJSON chunk into a StreamDelta. Unparseable lines are skipped. (+5 more)

### Community 39 - "test_rpc.py"
Cohesion: 0.16
Nodes (27): _auth(), _call(), client(), fixture, MonkeyPatch, Path, The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The id is reserved, not written — so the list stays empty. (+19 more)

### Community 40 - "protocol.py"
Cohesion: 0.17
Nodes (19): dispatch(), _invoke(), Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., err(), ErrorCode, ok(), Any (+11 more)

### Community 41 - "LLMProvider"
Cohesion: 0.10
Nodes (11): LLMProvider, Protocol, What `core/conversation.py` and, later, `core/router.py` depend on., Stable identifier used in logs, the `route` column, and the UI., Cheap reachability check. Must not raise., Load the model and return how long it took, in ms. Cold start is 8-15s (§12);…, Protocol, What `core/conversation.py` depends on, so it never imports onnxruntime. Same… (+3 more)

### Community 42 - "VoiceActivity"
Cohesion: 0.15
Nodes (6): ndarray, Protocol, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., VoiceActivity

### Community 43 - "Semantic file index (nomic-embed-text)"
Cohesion: 0.12
Nodes (19): AppData in the skip list hides %TEMP%, Tests must set ARIA_INDEX_FILES=false, ARIA — local-first Windows AI assistant, ARIA_TOKEN handshake, Bounded scan instead of Everything, BUILD_SPEC.md, Electron renderer (pure view), graphify check-update . (+11 more)

### Community 44 - "ChatMessage"
Cohesion: 0.10
Nodes (21): StoredMessage, Drop rows the model should not see back (tool rows arrive in Phase 3)., Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, Prompt asking the model to compress the oldest turns into a note., Prompt asking the model to name a conversation for the history list., split_for_rollup(), summarization_request(), title_request() (+13 more)

### Community 45 - "RoutingBias"
Cohesion: 0.13
Nodes (13): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+5 more)

### Community 46 - "scripts/eval_quality.py"
Cohesion: 0.14
Nodes (17): Chunks carry an index; renderer plays by index, num_gpu: 0 on every embedding call, scripts/eval_quality.py, Read fabricated and over-refused together, kokoro-onnx TTS on CPU, Never set temperature on a reasoning model, Switching local models evicts the old one first, Persona is per model; MINIMAL is not a downgrade (+9 more)

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
Cohesion: 0.20
Nodes (15): all_status(), CredentialKey, CredentialStatus, delete_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Credential Manager entry names under the ARIA service. (+7 more)

### Community 51 - "system.py"
Cohesion: 0.18
Nodes (14): test_system_info_reports_this_machine(), Everything she can do to the machine, and what it costs to do it. Importing…, _endpoint_volume(), _facts(), get_system_info(), Any, tool, Facts about the machine, and the one knob she can turn on it. `get_system_info`… (+6 more)

### Community 52 - "Provider strategy — OpenAI and Gemini, not Anthropic"
Cohesion: 0.29
Nodes (8): Cloud providers call tools too, Keys in Windows Credential Manager via keyring, Provider strategy — OpenAI and Gemini, not Anthropic, core/router.py, Rule 10 — do not refactor prior phases, Smart-mode bias is a persisted setting, Gemini requires thoughtSignature echoed back, A tool turn is not a text turn

### Community 53 - "RpcMethodError"
Cohesion: 0.12
Nodes (17): chat_cancel(), chat_delete(), models_bias(), models_select(), Abort an in-flight turn mid-stream., Persist the model choice: a catalog id, or "smart"., Read or set what Smart mode optimises for. Phase 2 flips this to "fastest" for…, Turn a held-button recording into text. Takes base64 int16 PCM from the… (+9 more)

### Community 54 - "bridge.d.ts"
Cohesion: 0.13
Nodes (14): AriaApi, AssistantState, BrainStatus, CredentialStatus, LogLine, ModelAvailability, ModelInfo, ModelListing (+6 more)

### Community 55 - "Electron main + Python sidecar architecture"
Cohesion: 0.09
Nodes (22): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation (+14 more)

### Community 56 - "The screen overlay window"
Cohesion: 0.16
Nodes (14): backgroundThrottling: false is not sufficient, Audio frames go over a JSON-RPC notification, Hands-free is on by default, The indexer throttle is the feature, listener.frame_rate, @method("name") in rpc/handlers.py, The screen overlay window, sendToRenderer broadcasts to both windows (+6 more)

### Community 57 - "strip_wake_word"
Cohesion: 0.16
Nodes (14): is_stop_word(), Is this whole utterance just a request to stop talking?, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said., The name has to be first. Anywhere else it is just a word., Matched whole, never as a prefix. (+6 more)

### Community 58 - "Tier"
Cohesion: 0.17
Nodes (14): Bus, Denied, Journal, Pending, Protocol, RuntimeError, The tier engine and the confirmation round-trip (BUILD_SPEC §7.1, §7.2). This…, A confirmation the user has not answered yet. (+6 more)

### Community 59 - "devDependencies"
Cohesion: 0.15
Nodes (13): electron, devDependencies, electron, postcss, react, react-dom, @types/ws, zustand (+5 more)

### Community 60 - "SpeechStream"
Cohesion: 0.19
Nodes (7): Any, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, What the model is allowed to know exists. None rather than an empty list when…, SpeechStream

### Community 61 - "handlers.py"
Cohesion: 0.31
Nodes (8): build_health(), HealthReport, BaseModel, JSON-RPC method registry and dispatch (BUILD_SPEC §7.1). Phase 0 registers only…, Rich health snapshot for the UI (§7.1 ``system.health``, §9.6)., Return the health snapshot. Never raises — the UI polls this., system_health(), uptime_seconds()

### Community 62 - "_start_conversation"
Cohesion: 0.08
Nodes (25): BaseSettings, get, Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Create the runtime directory tree. Safe to call repeatedly., Sidecar settings, loaded once per process., Settings, _build_indexer() (+17 more)

### Community 63 - "rpc"
Cohesion: 0.18
Nodes (12): bearer_from_header(), Constant-time comparison of a presented Bearer token., Extract the token from an ``Authorization: Bearer <token>`` header., token_matches(), Token-gated JSON-RPC endpoint (§7.1). The port is reachable by any browser tab…, Read/dispatch/reply until the client goes away., rpc(), _serve() (+4 more)

### Community 64 - "App.tsx"
Cohesion: 0.40
Nodes (3): drag, noDrag, Overlay

### Community 65 - "ListenerState.ARMED"
Cohesion: 0.16
Nodes (14): ListenerState.ARMED, Blue means she is listening to you, The follow-up window was removed, Fuzzy name matching on the first word, hotwords="Aria" makes it worse, measured, listener.heard logs the words, not chars=42, listener.not_addressed logs the transcript, _rearm() — a false start must not disarm her (+6 more)

### Community 66 - "open_app's ordered match bands"
Cohesion: 0.13
Nodes (16): _ALIASES is a fallback, never a rewrite, App index: Get-StartApps + App Paths + PATH, open_app's ordered match bands, Filename ranking reuses tools/apps.score, Filler words are stripped first, A refusal names the limit once, then points somewhere, Cloud vendors reached over httpx, not their SDKs, MATCH_FLOOR (+8 more)

### Community 67 - "package.json"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 68 - "eval_quality.py"
Cohesion: 0.09
Nodes (34): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+26 more)

### Community 69 - "HistoryPanel.tsx"
Cohesion: 0.24
Nodes (7): clockTime(), dayGroup(), HistoryPanel(), label(), Row(), RowProps, session()

### Community 70 - "_GROUNDING_TEMPLATE / stable_prefix(has_tools=...)"
Cohesion: 0.24
Nodes (10): providers/connectivity.py, FIRST_CHUNK_MAX_CHARS = 32, _GROUNDING_TEMPLATE / stable_prefix(has_tools=...), Stable-first prompt assembly and the KV cache, context.machine_context(), Being reached over the internet is not having internet, Roll-up (_summarize / _maybe_roll_up) runs in the background, scripts/soak_conversation.py (30-turn soak) (+2 more)

### Community 71 - "configure_logging"
Cohesion: 0.21
Nodes (12): configure_logging(), _console_handler(), _file_handler(), Handler, Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file. (+4 more)

### Community 72 - "db.py"
Cohesion: 0.12
Nodes (22): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Open the database with sqlite-vec loaded and the required pragmas set. (+14 more)

### Community 73 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 74 - "WakeWord"
Cohesion: 0.13
Nodes (6): Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, Protocol, What the listener depends on, so it never imports openwakeword., WakeWord

### Community 75 - "Sidebar.tsx"
Cohesion: 0.15
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 76 - "RecordingBus"
Cohesion: 0.17
Nodes (10): RuntimeError, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, Voice could not start. Never fatal — she still types., SpeechUnavailable, Voice is additive. No engine must not mean no reply., Audio already queued would otherwise keep talking after the stop button., RecordingBus, test_a_failing_synthesiser_does_not_break_the_turn() (+2 more)

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
Cohesion: 0.39
Nodes (7): appendToStreaming(), clearStreaming(), finalise(), toTurns(), Turn, TurnCompletePayload, useConversation

### Community 81 - "Barge-in"
Cohesion: 0.29
Nodes (8): Cancel emits audio.stop, Barge-in, Duck first, decide after, A duck must always resume (_unduck), Esc stops her, claimed only while she speaks, A gate that supplies the precondition tests the mechanism, not the feature, Only her name or a stop word cuts her off, voice.playing (renderer reports playback)

### Community 82 - "FakeTTS"
Cohesion: 0.20
Nodes (6): FakeTTS, qwen3.5 streams reasoning into a separate channel. Speaking it aloud would be…, Synthesis is dispatched per fragment, so a short chunk can finish before a…, Records what it was asked to say, without loading onnxruntime., test_chunks_carry_an_index_so_playback_can_order_them(), test_reasoning_is_never_spoken()

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

### Community 88 - "list_windows"
Cohesion: 0.25
Nodes (8): §7.2's second failure mode: the model gets one line, the UI gets the lot., test_listing_windows_summarises_rather_than_dumps(), list_windows(), Any, tool, List open application windows., Top-level windows with a title, which is as close to "what is running" as a…, _visible_windows()

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

### Community 155 - "graphify update . (AST-only refresh)"
Cohesion: 0.38
Nodes (7): graphify cluster-only ., graphify update . --force, Two benign extractor gaps, graphify-out/ (graph.json, graph.html, GRAPH_REPORT.md), Graph shrink guard, graphify update . (AST-only refresh), Keep the knowledge graph current

### Community 156 - ".cancel"
Cohesion: 0.29
Nodes (3): Remove a conversation. Cancels it first if it is the one in flight., Abort an in-flight turn. Returns False if it was already finished., Cancel every in-flight turn. Returns how many there were. Barge-in has no turn…

### Community 157 - "spawn"
Cohesion: 0.33
Nodes (5): Any, Fire-and-forget work that must not take the process down with it. Two rules,…, Run `coro` detached. Failures are logged against `name`, never raised., spawn(), Task

### Community 158 - "ModelListing"
Cohesion: 0.33
Nodes (6): ModelListing, `models.list` result., models_list(), models_refresh(), Catalog plus live availability. Drives the picker and its tooltips. Re-probes…, Ask the cloud providers what they offer today, and re-list. Deliberately…

### Community 159 - "discovered"
Cohesion: 0.33
Nodes (6): discovered(), fixture, ModelInfo, None means "send nothing and let the provider decide" — the only safe default,…, One discovered model, removed again afterwards. The overlay is module state, so…, test_temperature_defaults_to_none()

### Community 160 - "ToolsPanel.tsx"
Cohesion: 0.40
Nodes (3): TIER_LABEL, TIER_STYLE, ToolSummary

### Community 165 - "Launch"
Cohesion: 0.67
Nodes (3): Launch, StrEnum, How an entry has to be started. Three sources, three launchers.

## Knowledge Gaps
- **196 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+191 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **49 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConversationService` connect `ConversationService` to `conversation.py`, `Event`, `GenerationOptions`, `test_tts.py`, `ConversationStore`, `listener.py`, `Listener`, `AvailabilityService`, `PermissionEngine`, `Router`, `test_conversation.py`, `ToolContext`, `HealthTracker`, `.cancel`, `WakeMode`, `catalog.py`, `._free_vram_for`, `main.py`, `.new_session`, `LLMProvider`, `.set_selected_model`, `ChatMessage`, `RoutingBias`, `SpeechStream`, `_start_conversation`, `WakeWord`, `RecordingBus`, `FakeTTS`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `Listener` connect `Listener` to `main.py`, `ConversationService`, `Event`, `WakeWord`, `listener.py`, `KokoroTTS`, `AvailabilityService`, `_start_conversation`, `test_listener.py`, `WakeMode`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `HealthTracker` connect `HealthTracker` to `catalog.py`, `conversation.py`, `ConversationService`, `LLMProvider`, `RoutingBias`, `AvailabilityService`, `test_router.py`, `Router`, `test_conversation.py`, `test_catalog.py`, `discovery.py`, `SpeechStream`, `ModelListing`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `RouteDecision`) actually correct?**
  _`ConversationService` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Database` (e.g. with `Recorder` and `Indexer`) actually correct?**
  _`Database` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 14 INFERRED edges - model-reasoned connections that need verification._