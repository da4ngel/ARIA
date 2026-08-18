# Graph Report - ARIA  (2026-08-13)

## Corpus Check
- 186 files · ~211,692 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3723 nodes · 8438 edges · 210 communities (155 shown, 55 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 845 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8e4993c4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Retriever
- ToolResult
- test_tools.py
- test_listener.py
- main.ts
- test_organize.py
- test_context.py
- apps.py
- catalog.py
- Reflector
- EpisodicMemory
- KokoroTTS
- test_permissions.py
- test_scheduler.py
- discovery.py
- Tier
- test_semantic.py
- gate_wakeword.py
- Event
- HealthTracker
- Listener
- test_browser_setup.py
- listener.py
- Database
- probes.py
- call_key
- ChatMessage
- SemanticMemory
- ConversationStore
- test_episodic.py
- RoutingLog
- CredentialKey
- method
- OpenEngine
- test_router.py
- Router
- test_text.py
- finder.py
- eval_quality.py
- GeminiProvider
- Connectivity
- compilerOptions
- ConversationService
- Tool contract — decorator, ToolResult, derived schemas
- test_rpc.py
- snapshot
- compilerOptions
- test_tts.py
- soak_conversation.py
- gate_tool_selection.py
- test_vectors.py
- OllamaEmbeddings
- Utterance
- EventBus
- HealthReport
- OpenAIProvider
- test_screen.py
- Indexer
- GenerationOptions
- test_conversation.py
- browser.py
- _looks_like_a_commit_action
- bridge.d.ts
- Electron main + Python sidecar architecture
- test_db.py
- RpcMethodError
- ModelVerdict
- test_research.py
- gate_agent.py
- MonkeyPatch
- WebSearch
- StubSearch
- search.py
- main.py
- Phase 2 — Voice
- FakePage
- handlers.py
- Sidebar.tsx
- ToolContext
- ProviderUnavailable
- Non-negotiable rules (1-10)
- CATALOG (curated, measured models)
- devDependencies
- configure_logging
- Rule 5: destructive ops require T2+ and confirmation round-trip
- Phase 3 — the tool contract
- Phase 5 — she remembers
- SpeechStream
- browser_read
- _require_memory
- useConversation.ts
- Barge-in: duck first, decide after (AssistantState.SPEAKING bug)
- package.json
- jsdom
- registry.py
- HistoryPanel.tsx
- open_app tool (T1)
- spawn
- conversation.py
- Role
- _cloud_model
- ModelPicker.tsx
- core/context.py (stable/volatile prefix, machine_context)
- Phase 4 — the finder
- browser_navigate
- _parse_episode
- ConfirmDialog.tsx
- preload.ts
- gate_organize.py
- make_tray_icons.py
- Fact
- online
- SettingsPanel.tsx
- UI must be visually inspected; typecheck/tests miss layout bugs
- .add_message
- WakeWord
- AvailabilityService
- MemoryPanel.test.tsx
- Orb.tsx
- scripts
- gate_research.py
- test_browser.py
- MemoryPanel.tsx
- Torch-free Python sidecar
- App.tsx
- ModelPicker.test.tsx
- ToolCallCard.tsx
- ToolsPanel.tsx
- VoiceAura.tsx
- ScreenRim.tsx
- kokoro-onnx (CPU TTS)
- gate_memory.py
- ConnectionStatus.tsx
- Markdown.tsx
- useAudio.ts
- useMic.ts
- Persona boundaries — capacity to push back
- Nightly reflection prompt (reflect.j2)
- gate_delete.py
- ComposerBar.tsx
- ConfirmDialog.test.tsx
- EmptyState.tsx
- HandsFreeToggle.tsx
- Shortcuts.tsx
- WindowControls.tsx
- useHandsFree.ts
- useModels.ts
- usePublishVoiceLevel.ts
- useSessions.ts
- useWakeChime.ts
- Caption.tsx
- tsconfig.json
- _suppress_close_errors
- One phase per session execution model
- scripts/gate_conversation.py
- electron-builder
- electron-vite
- framer-motion
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
- .delete_session
- .latest_session_id
- .reserve_session_id
- .set_title
- store
- gate_browser.py
- _reset_connection
- useConfirm.ts
- useMemory.ts
- usePushToTalk.ts
- useRpc.ts
- useWindowMode.ts
- src/main.tsx
- overlay/main.tsx
- Always send think:false to qwen3.x reasoning models
- create_folder tool (T1)
- list_folder tool (T0)
- rename_file tool (T2)
- overlay.html entry (#overlay → src/overlay/main.tsx)
- aria-sidecar
- @types/ws

## God Nodes (most connected - your core abstractions)
1. `Database` - 164 edges
2. `ConversationStore` - 124 edges
3. `HealthTracker` - 106 edges
4. `ConversationService` - 94 edges
5. `SemanticMemory` - 88 edges
6. `ToolContext` - 88 edges
7. `ToolResult` - 82 edges
8. `ChatMessage` - 77 edges
9. `EpisodicMemory` - 63 edges
10. `Listener` - 62 edges

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
- 3-file cycle: `sidecar/core/conversation.py -> sidecar/state.py -> sidecar/core/listener.py -> sidecar/core/conversation.py`

## Hyperedges (group relationships)
- **KV-cache latency discipline across prompt assembly** — build_spec_stable_prefix_ordering, build_spec_prefill_cost [INFERRED 0.85]
- **Tools spanning permission tiers T0-T3 governed by registry.py** — claude_tools_registry_py, claude_permission_tiers, claude_read_file_tool, claude_write_file_tool, claude_delete_file_tool, claude_move_file_tool, claude_run_powershell_tool, claude_kill_process_tool [INFERRED 0.85]
- **Hands-free voice pipeline: wake, VAD, barge-in, conversation state** — claude_openwakeword, claude_silero_vad, claude_wake_mode_concept, claude_listenerstate_armed, claude_barge_in_rationale, claude_assistantstate_speaking, claude_kokoro_onnx [INFERRED 0.85]
- **Memory retrieval pipeline feeding the turn prompt** — claude_memory_retrieval_py, claude_ollama_embeddings_class, claude_volatile_prefix, claude_fit_to_budget_func, claude_memory_reflection_py, claude_remember_tool [INFERRED 0.85]

## Communities (210 total, 55 thin omitted)

### Community 0 - "Retriever"
Cohesion: 0.16
Nodes (9): Task, Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache., Cancel any embed still running past its deadline. Without this, shutting down… (+1 more)

### Community 1 - "ToolResult"
Cohesion: 0.09
Nodes (45): Path, Overwriting is a different destructive act from moving, and the user approved a…, The whole point: when it cannot be done she must say so, not claim it., A folder is a much larger promise than a file, and this tool says file., test_a_missing_file_is_said_plainly(), test_a_path_is_not_a_named_folder(), test_it_deletes_a_file_it_was_pointed_at(), test_it_moves_a_file() (+37 more)

### Community 2 - "test_tools.py"
Cohesion: 0.04
Nodes (74): app(), parametrize, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, §7.2's second failure mode: the model gets one line, the UI gets the lot., 7 zip" matched "7-Zip Help" purely because it is the shorter name., The demotion must not make the entry unreachable., Opening the wrong app is worse than opening nothing., This is what stops "open youtube" launching the YouTube Music app: the website… (+66 more)

### Community 3 - "test_listener.py"
Cohesion: 0.06
Nodes (69): drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on… (+61 more)

### Community 4 - "main.ts"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 5 - "test_organize.py"
Cohesion: 0.06
Nodes (71): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+63 more)

### Community 6 - "test_context.py"
Cohesion: 0.06
Nodes (63): estimate_tokens(), fit_to_budget(), machine_context(), MachineContext, overhead_tokens(), Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase… (+55 more)

### Community 7 - "apps.py"
Cohesion: 0.06
Nodes (53): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, AppEntry, _AppIndex, _bring_to_front(), _build_index(), close_app(), _closest_ratio() (+45 more)

### Community 8 - "catalog.py"
Cohesion: 0.05
Nodes (71): Which models are usable right now. One object answers this for both…, all_models(), by_class(), default_local(), discovered(), get(), local_models(), ModelAvailability (+63 more)

### Community 9 - "Reflector"
Cohesion: 0.08
Nodes (34): choose_model(), ExtractedEpisode, ExtractedFact, BaseModel, datetime, ModelInfo, Reflection — where "learns on its own" actually lives (BUILD_SPEC §8.3). Once a…, What the model returned, once it survives validation. (+26 more)

### Community 10 - "EpisodicMemory"
Cohesion: 0.06
Nodes (21): EpisodicMemory, _now(), datetime, Row, StoredMessage, Writes and reads `episodes`. Never raises into the turn path., Summarize every conversation that has gone quiet. Returns how many., Summarize one session into an episode. Idempotent; never raises. `ended_at` is… (+13 more)

### Community 11 - "KokoroTTS"
Cohesion: 0.07
Nodes (32): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+24 more)

### Community 12 - "test_permissions.py"
Cohesion: 0.06
Nodes (90): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+82 more)

### Community 13 - "test_scheduler.py"
Cohesion: 0.09
Nodes (42): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday., Sweeps idle sessions, and runs reflection once per day. (+34 more)

### Community 14 - "discovery.py"
Cohesion: 0.07
Nodes (50): Cost, discover_all(), discover_gemini(), discover_openai(), _fetch(), _gemini_class(), _gemini_is_chat(), _gemini_is_duplicate() (+42 more)

### Community 15 - "Tier"
Cohesion: 0.06
Nodes (38): EscalateFn, PreviewFn, RefuseFn, Launch, StrEnum, How an entry has to be started. Three sources, three launchers., Holds the pieces the content search needs. A module-level holder rather than…, _Semantic (+30 more)

### Community 16 - "test_semantic.py"
Cohesion: 0.06
Nodes (45): normalise_triple(), Fold a triple to its stored form. The UNIQUE index is on the raw columns, so…, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:…, §8.3 caps at 0.95. Repetition is evidence, not proof. (+37 more)

### Community 17 - "gate_wakeword.py"
Cohesion: 0.07
Nodes (24): main(), Download the wake word weights into data/models/openwakeword. python…, frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python… (+16 more)

### Community 18 - "Event"
Cohesion: 0.08
Nodes (25): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout., AssistantState (+17 more)

### Community 19 - "HealthTracker"
Cohesion: 0.06
Nodes (39): HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture (+31 more)

### Community 20 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 21 - "test_browser_setup.py"
Cohesion: 0.17
Nodes (18): browser_setup(), _cdp_reachable(), _default_browser(), Path, (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher() (+10 more)

### Community 22 - "listener.py"
Cohesion: 0.08
Nodes (33): clips(), main(), ndarray, Can she hear her own name? Across many voices, because one is not a test.…, score(), is_stop_word(), _near_the_name(), Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3). The renderer opens the… (+25 more)

### Community 23 - "Database"
Cohesion: 0.05
Nodes (63): Database, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Async-safe wrapper around the single sqlite connection., Sessions and messages — the durable conversation (BUILD_SPEC §7.3). This is…, build_prompt(), _extract_json(), Any, §8.3's prompt, with the two slots filled. (+55 more)

### Community 24 - "probes.py"
Cohesion: 0.10
Nodes (31): Check, admits_ignorance(), answers_flatly(), contains(), contains_any(), denies_capability(), exact(), excludes() (+23 more)

### Community 25 - "call_key"
Cohesion: 0.47
Nodes (4): call_key(), Any, A hashable fingerprint of one tool call, for loop detection. Sorted so argument…, Mark one step as run. `local_only` is unknown, not False, for a tool the…

### Community 26 - "ChatMessage"
Cohesion: 0.08
Nodes (36): assemble(), clean_title(), episode_request(), _persona(), PersonaLevel, datetime, StoredMessage, StrEnum (+28 more)

### Community 27 - "SemanticMemory"
Cohesion: 0.13
Nodes (33): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice. (+25 more)

### Community 28 - "ConversationStore"
Cohesion: 0.11
Nodes (34): ConversationStore, CRUD over `sessions` and `messages`., make_session(), fixture, Session listing, search, titles and deletion — what the history panel reads., The bug this catches: `set_title` opened an implicit transaction and never…, The exact failure, reproduced at the layer that fixes it. He asked one question…, The model can already see this chat. Returning it as a discovery would make her… (+26 more)

### Community 29 - "test_episodic.py"
Cohesion: 0.14
Nodes (30): _conversation(), _episodic(), anyio, Connection, Closing a conversation into an episode, and the foreign key that bites. The…, `ended_at` is the guard as well as the record, so an idle sweep racing a New…, The regression test for the whole bug. Eyaas asked one question about data…, Still too short to summarise — but it must be stamped anyway. Skipping without… (+22 more)

### Community 30 - "RoutingLog"
Cohesion: 0.11
Nodes (24): Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Writes and reads `routing_log`. Never raises into the turn path., RoutingLog, Connection, fixture, §9.7's labelled dataset: what the router decided, and what the user thought.… (+16 more)

### Community 31 - "CredentialKey"
Cohesion: 0.17
Nodes (17): all_status(), CredentialKey, CredentialStatus, delete_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Credential Manager entry names under the ARIA service. (+9 more)

### Community 32 - "method"
Cohesion: 0.08
Nodes (34): chat_cancel(), chat_delete(), chat_history(), chat_new(), chat_send(), chat_sessions(), method(), models_list() (+26 more)

### Community 33 - "OpenEngine"
Cohesion: 0.16
Nodes (17): A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, OpenEngine, ToolCall, Asks for a tool on the first pass, then answers on the second. The two-pass…, One entry per pass: a list of `ToolCall`s to ask for, or `None` to answer in…, A permission engine that always allows, recording what it ran., §7.2's second failure mode: never paste the payload into the context. (+9 more)

### Community 34 - "test_router.py"
Cohesion: 0.08
Nodes (46): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort. (+38 more)

### Community 35 - "Router"
Cohesion: 0.10
Nodes (28): is_tool_shaped(), needs_deep_model(), BaseModel, ModelInfo, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, A request to act on the machine rather than to talk about something., Reasoning, code, or a multi-step request: the `smart` class earns its cost., Chooses a model for a turn. (+20 more)

### Community 36 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 37 - "finder.py"
Cohesion: 0.07
Nodes (48): f(), parametrize, Finding files by name: the ranking, and the words people wrap around it. The…, if I say open cv … fetch the latest cv" — this is that, with an old draft and a…, budget_2026 is newer than every CV, and must not answer "cv"., Recency is a tiebreaker, never the whole answer., Opening the wrong document is worse than opening none., Stripping everything would search for the empty string, which matches the… (+40 more)

### Community 38 - "eval_quality.py"
Cohesion: 0.08
Nodes (36): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+28 more)

### Community 39 - "GeminiProvider"
Cohesion: 0.17
Nodes (8): _function_call_part(), GeminiProvider, Any, ToolCall, Split system messages out; map assistant -> model. **Tool turns are not text.**…, Replay a tool call in the shape Gemini demands back. The signature is not…, Implements `LLMProvider` against the Gemini generateContent API., No-op: cloud models have no local load step to pay for.

### Community 40 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 41 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 42 - "ConversationService"
Cohesion: 0.05
Nodes (28): SessionSummary, ConversationService, Any, ModelInfo, RoutingBias, StoredMessage, Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, Name the conversation once it has enough content to name. Deliberately fire-… (+20 more)

### Community 43 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (28): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+20 more)

### Community 44 - "test_rpc.py"
Cohesion: 0.14
Nodes (30): method_names(), _auth(), _call(), client(), fixture, MonkeyPatch, parametrize, Path (+22 more)

### Community 45 - "snapshot"
Cohesion: 0.18
Nodes (11): BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM unconditionally.…, §9:943 says "regardless of tool tier" — that only means something if *every*…, test_every_browser_tool_carries_the_checkout_escalation(), test_only_fill_carries_the_password_refusal(), test_tiers_deviate_from_build_specs_blanket_confirm_by_design(), T1. It reads and changes nothing; the consent that matters is the online…, test_research_needs_no_confirmation(), BUILD_SPEC's own tier table (§9:474) lists this AUTO — that line is about the… (+3 more)

### Community 46 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 47 - "test_tts.py"
Cohesion: 0.06
Nodes (38): ndarray, RuntimeError, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, Load and warm. The first synthesis is ~5x slower than the rest, and the user…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, Voice could not start. Never fatal — she still types., Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, SpeechUnavailable (+30 more)

### Community 48 - "soak_conversation.py"
Cohesion: 0.18
Nodes (12): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+4 more)

### Community 49 - "gate_tool_selection.py"
Cohesion: 0.24
Nodes (12): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+4 more)

### Community 50 - "test_vectors.py"
Cohesion: 0.11
Nodes (23): cosine(), cosine_from_l2(), normalise(), pack(), Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for…, Cosine similarity of two vectors, normalised or not. Used by the merge step,… (+15 more)

### Community 51 - "OllamaEmbeddings"
Cohesion: 0.06
Nodes (41): Episode, BaseModel, Episodes — what happened, compressed and kept (BUILD_SPEC §7.3 tier 2). One…, A row from `episodes`, as the panel and retrieval see it., IndexStats, _pack(), The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, sqlite-vec takes raw little-endian float32. (+33 more)

### Community 52 - "Utterance"
Cohesion: 0.10
Nodes (9): ndarray, Protocol, Voice activity detection — streaming Silero (BUILD_SPEC §9 Phase 2 stage 3).…, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance (+1 more)

### Community 53 - "EventBus"
Cohesion: 0.14
Nodes (12): EventBus, Any, Protocol, Server -> client push notifications and the set of live connections (§7.1).…, Send the current state to one client, unconditionally. A reconnecting renderer…, Send a notification to every live client, dropping dead ones., Update the assistant state and notify clients if it actually changed., Minimal transport surface — a Starlette WebSocket satisfies this. (+4 more)

### Community 54 - "HealthReport"
Cohesion: 0.16
Nodes (20): dispatch(), HealthReport, _invoke(), BaseModel, Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., Rich health snapshot for the UI (§7.1 ``system.health``, §9.6)., err() (+12 more)

### Community 55 - "OpenAIProvider"
Cohesion: 0.10
Nodes (16): get_key(), Read a key, or None if unset. Never logs the value., _assemble(), OpenAIProvider, Any, Response, ToolCall, OpenAI provider (BUILD_SPEC §4, §9.7). Raw HTTP against `/v1/chat/completions`… (+8 more)

### Community 56 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 57 - "Indexer"
Cohesion: 0.08
Nodes (34): chunk(), _digest(), extract_text(), Indexer, Path, Whatever text this file has, or "" if it has none worth having. Never raises: a…, Overlapping windows, so a sentence spanning a boundary stays findable., Whether this file is worth reading at all. (+26 more)

### Community 58 - "GenerationOptions"
Cohesion: 0.07
Nodes (29): HTTPError, Compress the oldest turns. Folds in any earlier note so it compounds., GenerationOptions, Any, BaseModel, The interface every LLM backend implements. Phase 1 only ships the Ollama…, Stream a completion. Cancellation is cooperative: cancelling the consuming task…, Common `[{role, content}]` shape most chat APIs accept. Tool fields are only… (+21 more)

### Community 59 - "test_conversation.py"
Cohesion: 0.07
Nodes (58): _drain(), FakeProvider, make_service(), anyio, fixture, Turn orchestration, cancellation, persistence and context roll-up., Every memory call site is a no-op when `memory` is None — Phase 4's behaviour,…, Wait for all in-flight turns. (+50 more)

### Community 60 - "browser.py"
Cohesion: 0.13
Nodes (22): Browser, Page, test_fill_types_the_value_into_the_match(), test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), browser_fill(), BrowserUnavailable, _connect() (+14 more)

### Community 61 - "_looks_like_a_commit_action"
Cohesion: 0.22
Nodes (9): Locator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught(), test_commit_wording_in_the_visible_text_is_caught(), _looks_like_a_commit_action() (+1 more)

### Community 62 - "bridge.d.ts"
Cohesion: 0.10
Nodes (19): AriaApi, AssistantState, BrainStatus, CredentialStatus, LogLine, MemoryEpisode, MemoryFact, MemoryStats (+11 more)

### Community 63 - "Electron main + Python sidecar architecture"
Cohesion: 0.11
Nodes (19): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation (+11 more)

### Community 64 - "test_db.py"
Cohesion: 0.07
Nodes (40): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, Run ``fn`` against the connection off the event loop, serialised., Every table in the database, including vec0 virtual tables. (+32 more)

### Community 65 - "RpcMethodError"
Cohesion: 0.11
Nodes (19): chat_rename(), confirm_respond(), memory_reflect(), models_bias(), Read or set what Smart mode optimises for. Phase 2 flips this to "fastest" for…, Turn a held-button recording into text. Takes base64 int16 PCM from the…, Read or set whether the sidecar accepts a continuous audio stream. Turning this…, Answer a pending confirmation (§7.1). The agent loop is suspended on an… (+11 more)

### Community 66 - "ModelVerdict"
Cohesion: 0.29
Nodes (5): ModelVerdict, BaseModel, Per-model tallies. The dataset §9.7 wants, as far as it has grown., How a model has actually been received, per `routing_log`., Liked as a fraction of rated, or None while it would be noise.

### Community 67 - "test_research.py"
Cohesion: 0.18
Nodes (15): One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, `research(query)`, the untrusted-content boundary, and the online gate. Two…, A model that has just read 6,000 characters of someone else's writing has…, Returns real, correct URLs" is the acceptance line, and only `summary` reaches…, Stronger than asking it not to use one: §7.2's own reasoning for hiding DANGER,…, test_a_source_is_truncated_rather_than_dropped() (+7 more)

### Community 68 - "gate_agent.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 6's agent loop, against the running sidecar. "find <scratch file>,…

### Community 69 - "MonkeyPatch"
Cohesion: 0.16
Nodes (22): MonkeyPatch, A target that does not exist is the tool's "not found" to report, not a reason…, _returning(), test_click_names_what_it_could_not_find(), test_click_risk_is_quiet_when_nothing_resolved(), test_click_runs_the_match_it_finds(), test_current_page_escalation_checks_the_live_page(), test_current_page_escalation_is_quiet_on_an_ordinary_page() (+14 more)

### Community 70 - "WebSearch"
Cohesion: 0.18
Nodes (9): Any, Response, RuntimeError, Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix., Fetch and strip anything that arrived without text. Concurrently, and failures…, No usable search key, or the provider refused. Carries the fix., SearchUnavailable (+1 more)

### Community 71 - "StubSearch"
Cohesion: 0.15
Nodes (14): Exception, Stripping is a losing game — there are unlimited phrasings. The content is…, It has a title, a URL and a snippet. Citing it beats pretending the search did…, A model that asks for fifty pages would blow the context budget §8.2 exists to…, Stands in for the network. Returns whatever it was handed., StubSearch, test_a_source_that_would_not_load_is_still_cited(), test_an_empty_query_asks_rather_than_searching() (+6 more)

### Community 72 - "search.py"
Cohesion: 0.12
Nodes (11): AsyncClient, HTMLParser, Web search, and turning a page into something a model can read. BUILD_SPEC §9…, Readable text from a page, truncated on a word boundary., Strip a page to its readable text. Not readability, not an article extractor,…, _Reader, to_text(), The normal case on the open web, and returning nothing would read as "research… (+3 more)

### Community 73 - "main.py"
Cohesion: 0.04
Nodes (62): BaseSettings, FastAPI, get, Path, Sidecar configuration. Single source of truth for paths, port, and auth token.…, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In… (+54 more)

### Community 74 - "Phase 2 — Voice"
Cohesion: 0.12
Nodes (16): Barge-in — interrupt playback on speech, Health monitoring and degradation warnings, Local by default, cloud opt-in per turn, num_ctx capped at 8192, Offline is a first-class path, not an error path, Phase 0 — Foundation, Phase 2 — Voice, Phase 6 — Agent loop + cloud routing (+8 more)

### Community 75 - "FakePage"
Cohesion: 0.09
Nodes (12): FakeLocator, FakePage, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, Refusing to act on an ambiguous-but-real description is worse than picking the…, Implements exactly the `Page` surface `browser.py` calls., test_click_risk_escalates_on_the_elements_own_wording(), test_click_risk_is_quiet_for_an_ordinary_click() (+4 more)

### Community 76 - "handlers.py"
Cohesion: 0.27
Nodes (9): pcm16_to_float32(), Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., build_health(), JSON-RPC method registry and dispatch (BUILD_SPEC §7.1). Phase 0 registers only…, One 80ms frame of base64 int16 PCM from the open microphone. Sent as a…, Return the health snapshot. Never raises — the UI polls this., system_health(), uptime_seconds() (+1 more)

### Community 77 - "Sidebar.tsx"
Cohesion: 0.14
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 78 - "ToolContext"
Cohesion: 0.07
Nodes (46): test_system_info_reports_this_machine(), tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, The clipboard's text, or None when it holds something else. An image, a file…, Read the clipboard's text., _read(), read_clipboard() (+38 more)

### Community 79 - "ProviderUnavailable"
Cohesion: 0.22
Nodes (7): Headers, ProviderRateLimited, ProviderUnavailable, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, The backend could not be reached — offline, not running, DNS, refused. Distinct…, Response, Response

### Community 80 - "Non-negotiable rules (1-10)"
Cohesion: 0.15
Nodes (13): ARIA (local-first Windows AI assistant), BUILD_SPEC.md, Electron UI (renderer), graphify-out/ (graph.json, graph.html, GRAPH_REPORT.md), graphify (knowledge graph tool), Rule 10: do not refactor prior phases unless current phase says to, Rule 3: never add torch (breaks PyInstaller packaging), Non-negotiable rules (1-10) (+5 more)

### Community 81 - "CATALOG (curated, measured models)"
Cohesion: 0.18
Nodes (13): by_class() (Smart mode routing, hand-pick-only), CATALOG (curated, measured models), core/router.py (Smart mode bias), scripts/eval_quality.py, scripts/gate_memory.py, scripts/measure_models.py, memory/retrieval.py, providers/discovery.py (+5 more)

### Community 82 - "devDependencies"
Cohesion: 0.15
Nodes (13): autoprefixer, electron, devDependencies, autoprefixer, electron, postcss, react, react-dom (+5 more)

### Community 83 - "configure_logging"
Cohesion: 0.23
Nodes (11): configure_logging(), _console_handler(), _file_handler(), Handler, Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file. (+3 more)

### Community 84 - "Rule 5: destructive ops require T2+ and confirmation round-trip"
Cohesion: 0.18
Nodes (12): allow_danger_tools flag (was dead code, fixed), confirm.request event (window must come forward), delete_file tool (T3), delete_folder tool (T3), Rule 5: destructive ops require T2+ and confirmation round-trip, files.py (drive-root / Windows / Program Files refusals), forget tool (T2), scripts/gate_delete.py (+4 more)

### Community 85 - "Phase 3 — the tool contract"
Cohesion: 0.17
Nodes (12): close_app tool (T2), focus_window tool (T1), get_system_info tool (T0), kill_process tool (T2), list_processes tool (T0), list_windows tool (T0), Phase 3 — the tool contract, read_clipboard tool (T0, local_only) (+4 more)

### Community 86 - "Phase 5 — she remembers"
Cohesion: 0.18
Nodes (12): ConversationService (ordering guard: forget_session before delete), ConversationStore.delete_session, memory/episodic.py, memory/reflection.py, memory/scheduler.py, memory/semantic.py, memory/vectors.py, MemoryPanel (renderer component) (+4 more)

### Community 87 - "SpeechStream"
Cohesion: 0.11
Nodes (11): ToolCall, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, SpeechStream, Protocol, What `core/conversation.py` depends on, so it never imports onnxruntime. Same… (+3 more)

### Community 88 - "browser_read"
Cohesion: 0.29
Nodes (7): test_read_returns_cleaned_text_with_the_url(), test_screenshot_returns_a_base64_image(), browser_read(), browser_screenshot(), tool, Read the current page as text., Screenshot the current tab. Ephemeral — never written to disk (§11), the same…

### Community 89 - "_require_memory"
Cohesion: 0.17
Nodes (12): memory_forget(), memory_list(), memory_search(), memory_stats(), memory_update(), The memory services, or a message saying how to turn them on., Everything she has learned, for MemoryPanel. Superseded facts are excluded by…, §7.1: search what she remembers. The same path a turn uses. (+4 more)

### Community 90 - "useConversation.ts"
Cohesion: 0.30
Nodes (11): appendToStreaming(), clearStreaming(), finalise(), loadRatings(), ToolCall, toTurns(), Turn, TurnCompletePayload (+3 more)

### Community 91 - "Barge-in: duck first, decide after (AssistantState.SPEAKING bug)"
Cohesion: 0.18
Nodes (11): AssistantState.SPEAKING, Barge-in: duck first, decide after (AssistantState.SPEAKING bug), scripts/gate_latency.py, scripts/gate_wakeword.py, openWakeWord (ONNX, hey_jarvis pretrained), Phase 2 stage 3 — hands free, providers/vad.py, Silero VAD (via faster-whisper vad_filter) (+3 more)

### Community 92 - "package.json"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 94 - "registry.py"
Cohesion: 0.11
Nodes (18): It is a strong constraint — it overrides the router — so it should be…, It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, test_a_wrapped_argument_description_survives_the_line_break(), test_no_registered_tool_documents_an_argument_it_then_truncates(), test_nothing_else_claims_local_only(), all_tools(), _arg_docs(), build_parameters() (+10 more)

### Community 95 - "HistoryPanel.tsx"
Cohesion: 0.24
Nodes (7): clockTime(), dayGroup(), HistoryPanel(), label(), Row(), RowProps, session()

### Community 96 - "open_app tool (T1)"
Cohesion: 0.22
Nodes (10): scripts/gate_apps.py, Rule 2: never load a second model onto the GPU (6GB VRAM ceiling), Indexer throttle: 20 files/min, paused while busy/CPU>60%, MATCH_FLOOR (wrong app worse than no app), OllamaEmbeddings (shared pool with indexer), open_app tool (T1), search_files tool, ToolCallCard (renderer component) (+2 more)

### Community 97 - "spawn"
Cohesion: 0.25
Nodes (6): Start a fresh conversation, without writing anything yet. Returns a *reserved*…, Any, Task, Fire-and-forget work that must not take the process down with it. Two rules,…, Run `coro` detached. Failures are logged against `name`, never raised., spawn()

### Community 98 - "conversation.py"
Cohesion: 0.06
Nodes (35): exhausted_note(), LoopState, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, §11: the call immediately after reading untrusted content is forced through…, Told to the model, not just logged — it should know why it stopped., What one turn's agent loop is tracking, across its steps. Deliberately not…, Whether the model should be handed tools on the next pass. False exactly on…, repeat_note() (+27 more)

### Community 99 - "Role"
Cohesion: 0.21
Nodes (10): MessageHit, BaseModel, Oldest-first turns for a session., Find past turns that mention what `query` is about. **This is the layer that…, A row from `messages`, as the UI and context assembly see it., One past turn that matched a `recall` query., StoredMessage, StrEnum (+2 more)

### Community 100 - "_cloud_model"
Cohesion: 0.20
Nodes (10): _cloud_model(), ModelInfo, 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement…, The mechanism has to keep working, or banding would just be a way of ignoring…, test_a_measured_tool_score_outranks_latency_on_a_command(), test_a_model_that_is_visibly_worse_still_loses() (+2 more)

### Community 101 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 102 - "core/context.py (stable/volatile prefix, machine_context)"
Cohesion: 0.22
Nodes (9): core/context.py (stable/volatile prefix, machine_context), fit_to_budget(has_tools, retrieved), _GROUNDING_TEMPLATE capability paragraph fix (57%->27% fabrication), Stable-first prompt ordering preserves Ollama KV cache (~480ms/1000 tok), Provider strategy: OpenAI + Gemini via API keys, Ollama offline fallback, providers/connectivity.py (60s reachability cache), providers/gemini.py (thoughtSignature echo), providers/openai.py (+1 more)

### Community 103 - "Phase 4 — the finder"
Cohesion: 0.25
Nodes (9): Everything (es.exe) integration, find tool, scripts/gate_tool_selection.py, open_file tool, open_path tool, organize_folder tool + undo manifest (planned, not built), Phase 4 — the finder, Relevance-based tool selection: closed, measured not worth building (+1 more)

### Community 104 - "browser_navigate"
Cohesion: 0.33
Nodes (6): Exception, _raising(), test_navigate_adds_a_scheme_when_none_was_given(), test_navigate_reports_browser_unavailable_plainly(), browser_navigate(), Open a URL in the current tab. Args: url: The address to go to, including…

### Community 105 - "_parse_episode"
Cohesion: 0.22
Nodes (9): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., A dropped episode is a lost conversation; a guessed salience is not., test_a_fenced_json_reply_parses(), test_an_empty_reply_produces_no_episode(), test_plain_prose_is_kept_as_the_summary() (+1 more)

### Community 106 - "ConfirmDialog.tsx"
Cohesion: 0.20
Nodes (9): ConfirmRequest, ImagePreview, leaf(), MovePlan, MovePlanView(), Props, tail(), TIER_LABEL (+1 more)

### Community 107 - "preload.ts"
Cohesion: 0.25
Nodes (6): api, AriaApi, BrainStatus, LogLine, SidecarEvent, Unsubscribe

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "make_tray_icons.py"
Cohesion: 0.36
Nodes (7): _chunk(), coverage(), main(), png_bytes(), Generate the tray icon PNGs embedded in electron/tray.ts. Electron's…, Fraction of one pixel covered by the circle, by supersampling., An 8-bit RGBA PNG of a filled circle on transparency.

### Community 110 - "Fact"
Cohesion: 0.07
Nodes (21): Write one decision. Returns its id, or None if it could not be., Fact, FactHit, _now(), BaseModel, Row, The form that gets embedded and shown in the prompt., A fact with its retrieval scoring, for the panel and the prompt. (+13 more)

### Community 111 - "online"
Cohesion: 0.25
Nodes (8): online(), fixture, MonkeyPatch, The whole point of `SearchUnavailable` carrying a message., Online mode on, with a stubbed search behind it., Belt to `_tool_schemas`' braces. `allow_danger_tools` was dead for a whole…, test_it_refuses_when_online_mode_is_off(), test_no_key_says_which_key_and_where()

### Community 112 - "SettingsPanel.tsx"
Cohesion: 0.25
Nodes (7): BrowserState, KEY_HELP, KEY_LABEL, OnlineState, RowProps, SEARCH_KEYS, SettingsPanel()

### Community 113 - "UI must be visually inspected; typecheck/tests miss layout bugs"
Cohesion: 0.29
Nodes (7): Acrylic backgroundMaterial fix (#00000000, tint 0.62), backgroundThrottling:false + disable-renderer-backgrounding flags, Screen overlay window (Ctrl+Space, WS_EX_TRANSPARENT), Sidebar rail (icons-only when compact), UI must be visually inspected; typecheck/tests miss layout bugs, useHandsFree (renderer hook, opens mic on persisted setting), VoiceAura (amplitude-driven canvas, getLevel())

### Community 115 - "WakeWord"
Cohesion: 0.12
Nodes (7): Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, ndarray, Protocol, What the listener depends on, so it never imports openwakeword., WakeWord

### Community 116 - "AvailabilityService"
Cohesion: 0.11
Nodes (10): ModelAvailability, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+2 more)

### Community 117 - "MemoryPanel.test.tsx"
Cohesion: 0.43
Nodes (4): defaults(), episode(), fact(), stats()

### Community 118 - "Orb.tsx"
Cohesion: 0.33
Nodes (6): BREATH, HUE, Orb(), ORB_LAYOUT_ID, OrbProps, SPINS

### Community 119 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, sidecar, test, typecheck

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 121 - "test_browser.py"
Cohesion: 0.13
Nodes (23): parametrize, Browser control: the checkout/banking hard block, password refusal, and element…, The URL check catches the common case; a card-number field on an unlisted…, No page has loaded yet at this point — only the URL being navigated *to* is…, §11: the *next* tool call after this one is force-escalated by the agent loop —…, test_a_generic_domain_can_still_be_caught_by_its_dom(), test_known_checkout_and_banking_urls_are_recognised(), test_navigate_escalates_on_the_target_url_before_loading_it() (+15 more)

### Community 123 - "MemoryPanel.tsx"
Cohesion: 0.53
Nodes (5): confidenceStyle(), FactRow(), MemoryPanel(), summarise(), whenever()

### Community 124 - "Torch-free Python sidecar"
Cohesion: 0.40
Nodes (5): Phase 9 — Packaging, Torch-free Python sidecar, requests pinned explicitly — undeclared faster-whisper dep, kokoro-onnx conflicts with §4's onnxruntime/numpy pins, openai and google-genai deliberately absent; httpx instead

### Community 126 - "App.tsx"
Cohesion: 0.40
Nodes (3): drag, noDrag, Overlay

### Community 127 - "ModelPicker.test.tsx"
Cohesion: 0.60
Nodes (3): entry(), model(), models()

### Community 129 - "ToolsPanel.tsx"
Cohesion: 0.40
Nodes (3): TIER_LABEL, TIER_STYLE, ToolSummary

### Community 130 - "VoiceAura.tsx"
Cohesion: 0.40
Nodes (3): AuraMode, HUE, Props

### Community 131 - "ScreenRim.tsx"
Cohesion: 0.40
Nodes (3): HUE, Props, RimMode

### Community 132 - "kokoro-onnx (CPU TTS)"
Cohesion: 0.50
Nodes (4): FIRST_CHUNK_MAX_CHARS=32 (900ms first-audio gate), kokoro-onnx (CPU TTS), Phase 2 stage 1 — she speaks, SpeechStream (reads delta.text, never delta.thinking)

### Community 133 - "gate_memory.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 5's acceptance gate, against the running sidecar. "I usually work on…

### Community 138 - "useAudio.ts"
Cohesion: 0.67
Nodes (3): AudioChunk, decodePcm16(), useAudio

### Community 139 - "useMic.ts"
Cohesion: 0.67
Nodes (3): encodePcm16(), Recording, useMic

### Community 140 - "Persona boundaries — capacity to push back"
Cohesion: 0.67
Nodes (3): Persona boundaries — capacity to push back, Character, not sycophancy, aria.yaml persona configuration

### Community 141 - "Nightly reflection prompt (reflect.j2)"
Cohesion: 0.67
Nodes (3): Fact merge and supersession logic, Phase 5 — Memory, Nightly reflection prompt (reflect.j2)

### Community 161 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 186 - "gate_browser.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 7's browser half, against a real, CDP-attached Chrome. "open…

### Community 187 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

## Knowledge Gaps
- **248 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+243 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolContext` connect `ToolContext` to `ToolResult`, `test_tools.py`, `test_organize.py`, `apps.py`, `test_permissions.py`, `Tier`, `_suppress_close_errors`, `finder.py`, `ConversationService`, `test_screen.py`, `browser.py`, `test_research.py`, `MonkeyPatch`, `StubSearch`, `FakePage`, `SpeechStream`, `browser_read`, `registry.py`, `conversation.py`, `browser_navigate`, `test_browser.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `ConversationService` to `catalog.py`, `Reflector`, `EpisodicMemory`, `test_permissions.py`, `Tier`, `Event`, `HealthTracker`, `Listener`, `listener.py`, `Database`, `ChatMessage`, `ConversationStore`, `RoutingLog`, `OpenEngine`, `Router`, `test_tts.py`, `soak_conversation.py`, `EventBus`, `GenerationOptions`, `test_conversation.py`, `main.py`, `ToolContext`, `ProviderUnavailable`, `SpeechStream`, `spawn`, `conversation.py`, `Role`, `WakeWord`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `ToolResult` connect `ToolResult` to `test_tools.py`, `test_organize.py`, `apps.py`, `test_permissions.py`, `Tier`, `OpenEngine`, `_suppress_close_errors`, `finder.py`, `test_screen.py`, `test_conversation.py`, `browser.py`, `test_research.py`, `MonkeyPatch`, `StubSearch`, `ToolContext`, `browser_read`, `registry.py`, `conversation.py`, `browser_navigate`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `Database` (e.g. with `Recorder` and `Episode`) actually correct?**
  _`Database` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 42 INFERRED edges - model-reasoned connections that need verification._