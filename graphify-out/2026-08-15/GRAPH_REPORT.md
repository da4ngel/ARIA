# Graph Report - .  (2026-08-14)

## Corpus Check
- 50 files · ~228,626 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4040 nodes · 8773 edges · 245 communities (170 shown, 75 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 656 edges (avg confidence: 0.52)
- Token cost: 146,228 input · 0 output

## Community Hubs (Navigation)
- test_procedures.py
- test_focus.py
- test_tools.py
- test_listener.py
- main.ts
- test_organize.py
- test_context.py
- apps.py
- catalog.py
- Role
- test_conversation.py
- KokoroTTS
- test_permissions.py
- test_scheduler.py
- test_discovery.py
- Tier
- SemanticMemory
- gate_wakeword.py
- Event
- HealthTracker
- Listener
- test_browser_setup.py
- listener.py
- SettingsStore
- probes.py
- _start_conversation
- ChatMessage
- Database
- ConversationStore
- test_episodic.py
- RoutingLog
- credentials.py
- method
- OpenEngine
- test_router.py
- Router
- test_text.py
- ToolContext
- GenerationOptions
- GeminiProvider
- Connectivity
- compilerOptions
- ConversationService
- Tool contract — decorator, ToolResult, derived schemas
- test_rpc.py
- test_research.py
- compilerOptions
- RecordingBus
- soak_conversation.py
- gate_tool_selection.py
- test_vectors.py
- EpisodicMemory
- Utterance
- test_proactivity.py
- HealthReport
- ProviderUnavailable
- test_screen.py
- Indexer
- OllamaProvider
- FakeProvider
- browser.py
- _looks_like_a_commit_action
- bridge.d.ts
- Electron main + Python sidecar architecture
- test_db.py
- RpcMethodError
- proactivity.py
- Source
- gate_agent.py
- MonkeyPatch
- CredentialKey
- StubSearch
- _Reader
- main.py
- Phase 2 — Voice
- FakePage
- test_catalog.py
- Sidebar.tsx
- memory.py
- test_affect.py
- Non-negotiable rules (1-10)
- CATALOG (curated, measured models)
- devDependencies
- get_settings
- Rule 5: destructive ops require T2+ and confirmation round-trip
- Phase 3 — the tool contract
- Phase 5 — she remembers
- discovery.py
- browser_read
- handlers.py
- useConversation.ts
- Barge-in: duck first, decide after (AssistantState.SPEAKING bug)
- package.json
- jsdom
- registry.py
- HistoryPanel.tsx
- open_app tool (T1)
- spawn
- conversation.py
- test_finder.py
- _cloud_model
- ModelPicker.tsx
- core/context.py (stable/volatile prefix, machine_context)
- Phase 4 — the finder
- browser_navigate
- system.py
- ConfirmDialog.tsx
- preload.ts
- gate_organize.py
- make_tray_icons.py
- Fact
- online
- SettingsPanel.tsx
- UI must be visually inspected; typecheck/tests miss layout bugs
- ._insert
- SpeechToText
- AvailabilityService
- MemoryPanel.test.tsx
- Orb.tsx
- scripts
- gate_research.py
- test_browser.py
- ConversationView.tsx
- MemoryPanel.tsx
- Torch-free Python sidecar
- affect.py
- App.tsx
- ModelPicker.test.tsx
- ToolCallCard.tsx
- ToolsPanel.tsx
- VoiceAura.tsx
- ScreenRim.tsx
- gate_memory.py
- Settings
- drain_text
- ConnectionStatus.tsx
- Markdown.tsx
- useAudio.ts
- useMic.ts
- Persona boundaries — capacity to push back
- Nightly reflection prompt (reflect.j2)
- gate_delete.py
- parametrize
- migrate
- FakeTTS
- ComposerBar.tsx
- ConfirmDialog.test.tsx
- EmptyState.tsx
- HandsFreeToggle.tsx
- HandsFreeToggle.test.tsx
- Shortcuts.tsx
- VoicePanel.tsx
- WindowControls.tsx
- useHandsFree.ts
- useModels.ts
- usePublishVoiceLevel.ts
- useSessions.ts
- useWakeChime.ts
- Caption.tsx
- _suppress_close_errors
- scripts/gate_conversation.py
- electron-builder
- electron-vite
- framer-motion
- rpc
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
- render
- gate_affect.py
- AffectState
- test_tts.py
- database
- ProactivityScheduler
- gate_browser.py
- StreamDelta
- tts.py
- _repeated_failures
- to_pcm16
- default_local
- Panel.tsx
- useConfirm.ts
- useMemory.ts
- usePushToTalk.ts
- useRpc.ts
- useRpc.test.tsx
- useWindowMode.ts
- src/main.tsx
- overlay/main.tsx
- OverlayApp.tsx
- create_folder tool (T1)
- list_folder tool (T0)
- rename_file tool (T2)
- electron.vite.config.ts
- aria-sidecar
- postcss.config.js
- core/__init__.py
- providers/__init__.py
- rpc/__init__.py
- tests/__init__.py
- ConnectionStatus.test.tsx
- .scrollIntoView
- EmptyState.test.tsx
- tailwind.config.js
- @types/ws
- Runtime
- discovered
- test_a_command_is_not_slowed_down_for_a_difference_that_is_noise
- is_casual
- .run
- persona/__init__.py
- test_ordinary_questions_do_not_get_the_expensive_tier
- test_a_spoken_command_is_no_longer_forced_onto_the_local_model
- RPC Handler Dispatch
- anyio Test Runner
- Tool Call Data Model
- Tool Tier Enum

## God Nodes (most connected - your core abstractions)
1. `Database` - 245 edges
2. `ConversationStore` - 154 edges
3. `HealthTracker` - 88 edges
4. `ToolContext` - 88 edges
5. `ConversationService` - 84 edges
6. `ToolResult` - 82 edges
7. `SemanticMemory` - 79 edges
8. `Listener` - 58 edges
9. `EpisodicMemory` - 54 edges
10. `RecordingBus` - 52 edges

## Surprising Connections (you probably didn't know these)
- `Overlay page paints no background of its own` --semantically_similar_to--> `No CSP meta tag; main.ts sets the header per-environment`  [INFERRED] [semantically similar]
  overlay.html → index.html
- `Result` --uses--> `ChatMessage`  [INFERRED]
  scripts/eval_quality.py → sidecar/providers/base.py
- `Result` --uses--> `GenerationOptions`  [INFERRED]
  scripts/eval_quality.py → sidecar/providers/base.py
- `Result` --uses--> `LLMProvider`  [INFERRED]
  scripts/eval_quality.py → sidecar/providers/base.py
- `Result` --uses--> `ProviderError`  [INFERRED]
  scripts/eval_quality.py → sidecar/providers/base.py

## Import Cycles
- 3-file cycle: `sidecar/core/conversation.py -> sidecar/state.py -> sidecar/core/listener.py -> sidecar/core/conversation.py`

## Hyperedges (group relationships)
- **Tool Tier, Permission Engine and Confirmation Rule form ARIA's safety net** — claude_md_rule_confirmation_required, claude_md_tool_tier_system, claude_md_permission_engine, sidecar_tools_registry_file [INFERRED 0.85]
- **Stable-first prompt ordering for KV cache reuse governs prompt and tool-schema design** — claude_md_kv_cache_stable_prefix, sidecar_core_context_file, claude_md_relevance_tool_selection_closed [INFERRED 0.85]
- **Six-cause memory recall failure and its fix, verified by the memory gate** — claude_md_phase5_memory, claude_md_phase5_memory_bug_fix, scripts_gate_memory_file [EXTRACTED 1.00]
- **KV-cache latency discipline across prompt assembly** — build_spec_stable_prefix_ordering, build_spec_prefill_cost [INFERRED 0.85]

## Communities (245 total, 75 thin omitted)

### Community 0 - "test_procedures.py"
Cohesion: 0.04
Nodes (95): anyio, HealthTracker, Router, _drain(), FakeProvider, make_service(), OpenEngine, _proactivity_service() (+87 more)

### Community 1 - "test_focus.py"
Cohesion: 0.06
Nodes (90): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+82 more)

### Community 2 - "test_tools.py"
Cohesion: 0.04
Nodes (66): ndarray, Phase 8 voice polish's affect-driven nudge to `KokoroTTS.synthesize`. Same…, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, SpeechStream, RuntimeError (+58 more)

### Community 3 - "test_listener.py"
Cohesion: 0.05
Nodes (53): HTTPError, provider_for(), main(), measure_honesty(), measure_latency(), Measurement, ModelInfo, Measure a discovered model well enough to let Smart route to it.… (+45 more)

### Community 4 - "main.ts"
Cohesion: 0.05
Nodes (53): Case, FastAPI, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the… (+45 more)

### Community 5 - "test_organize.py"
Cohesion: 0.06
Nodes (76): get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., main(), Console entrypoint for ``python -m sidecar.main``., messy(), fixture, MonkeyPatch (+68 more)

### Community 6 - "test_context.py"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 7 - "apps.py"
Cohesion: 0.04
Nodes (74): app(), parametrize, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, 7 zip" matched "7-Zip Help" purely because it is the shorter name., The demotion must not make the entry unreachable., Opening the wrong app is worse than opening nothing., This is what stops "open youtube" launching the YouTube Music app: the website…, OneDrive relocates Documents and Desktop by default, so joining onto… (+66 more)

### Community 8 - "catalog.py"
Cohesion: 0.05
Nodes (69): all_models(), by_class(), default_local(), discovered(), get(), local_models(), ModelAvailability, ModelInfo (+61 more)

### Community 9 - "Role"
Cohesion: 0.04
Nodes (48): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, §11: the call immediately after reading untrusted content is forced through…, Told to the model, not just logged — it should know why it stopped., A hashable fingerprint of one tool call, for loop detection. Sorted so argument… (+40 more)

### Community 10 - "test_conversation.py"
Cohesion: 0.04
Nodes (34): ModelInfo, Retrieved, RouteDecision, ConversationService, Any, ChatMessage, RoutingBias, Which model gets to see the tool's result. `router._PRIVATE` already keeps a… (+26 more)

### Community 11 - "KokoroTTS"
Cohesion: 0.05
Nodes (64): bearer_from_header(), clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds…, Use the token Electron supplied, or mint one for standalone runs., Publish the token for a client that did not supply one. Written after the…, Remove the token file on clean shutdown so no stale token survives. **Only if…, Constant-time comparison of a presented Bearer token. (+56 more)

### Community 12 - "test_permissions.py"
Cohesion: 0.06
Nodes (60): Check, Namespace, build_messages(), _is_reasoning(), main(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+52 more)

### Community 13 - "test_scheduler.py"
Cohesion: 0.07
Nodes (55): Database, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard() (+47 more)

### Community 14 - "test_discovery.py"
Cohesion: 0.06
Nodes (41): Episode, _now(), BaseModel, Row, Episodes — what happened, compressed and kept (BUILD_SPEC §7.3 tier 2). One…, A row from `episodes`, as the panel and retrieval see it., Nearest episodes to a vector, as (episode, cosine)., Mark episodes as recalled. Feeds the access_count term in scoring. Called off… (+33 more)

### Community 15 - "Tier"
Cohesion: 0.06
Nodes (52): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), f(), parametrize, Finding files by name: the ranking, and the words people wrap around it. The…, if I say open cv … fetch the latest cv" — this is that, with an old draft and a…, budget_2026 is newer than every CV, and must not answer "cv"., Recency is a tiebreaker, never the whole answer. (+44 more)

### Community 16 - "SemanticMemory"
Cohesion: 0.06
Nodes (44): Role, ConversationStore, _now(), CRUD over `sessions` and `messages`., Return an existing session id, or create one., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing… (+36 more)

### Community 17 - "gate_wakeword.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 18 - "Event"
Cohesion: 0.09
Nodes (45): Candidate, default_candidates(), default_self_check(), idle_intention_candidate(), is_stated_intention(), ProactivityScheduler, procedure_offer_candidate(), datetime (+37 more)

### Community 19 - "HealthTracker"
Cohesion: 0.06
Nodes (31): main(), Download the wake word weights into data/models/openwakeword. python…, frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python… (+23 more)

### Community 20 - "Listener"
Cohesion: 0.06
Nodes (38): EscalateFn, IntEnum, PreviewFn, RefuseFn, Launch, StrEnum, How an entry has to be started. Three sources, three launchers., Holds the pieces the content search needs. A module-level holder rather than… (+30 more)

### Community 21 - "test_browser_setup.py"
Cohesion: 0.06
Nodes (46): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, §7.2's second failure mode: the model gets one line, the UI gets the lot., A dead end is useless; naming the closest lets the model retry., test_listing_windows_summarises_rather_than_dumps(), test_ranking_offers_the_near_misses(), _AppIndex, _bring_to_front() (+38 more)

### Community 22 - "listener.py"
Cohesion: 0.08
Nodes (38): chunk(), _digest(), extract_text(), Indexer, IndexStats, _pack(), Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks… (+30 more)

### Community 23 - "SettingsStore"
Cohesion: 0.08
Nodes (44): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:… (+36 more)

### Community 24 - "probes.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 25 - "_start_conversation"
Cohesion: 0.09
Nodes (33): ExtractedEpisode, ExtractedFact, BaseModel, datetime, ModelInfo, Reflection — where "learns on its own" actually lives (BUILD_SPEC §8.3). Once a…, What the model returned, once it survives validation., What one run did. Shown in MemoryPanel and asserted by the gate. (+25 more)

### Community 26 - "ChatMessage"
Cohesion: 0.09
Nodes (47): Path, Overwriting is a different destructive act from moving, and the user approved a…, The whole point: when it cannot be done she must say so, not claim it., A folder is a much larger promise than a file, and this tool says file., test_a_missing_file_is_said_plainly(), test_it_deletes_a_file_it_was_pointed_at(), test_it_moves_a_file(), test_it_refuses_a_folder() (+39 more)

### Community 27 - "Database"
Cohesion: 0.06
Nodes (37): BaseSettings, OllamaProvider, RoutingLog, SettingsStore, Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In… (+29 more)

### Community 28 - "ConversationStore"
Cohesion: 0.09
Nodes (41): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., _conversation(), _episodic(), anyio, Connection (+33 more)

### Community 29 - "test_episodic.py"
Cohesion: 0.06
Nodes (28): Fact, FactHit, normalise_triple(), _now(), BaseModel, datetime, Row, Facts — what she has LEARNED about you (BUILD_SPEC §7.3 tier 3, §8.3). A fact… (+20 more)

### Community 30 - "RoutingLog"
Cohesion: 0.06
Nodes (45): chat_history(), chat_new(), chat_rename(), chat_send(), chat_sessions(), confirm_respond(), memory_reflect(), method() (+37 more)

### Community 31 - "credentials.py"
Cohesion: 0.09
Nodes (37): One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, online(), Exception, fixture, MonkeyPatch, `research(query)`, the untrusted-content boundary, and the online gate. Two… (+29 more)

### Community 32 - "method"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 33 - "OpenEngine"
Cohesion: 0.07
Nodes (32): ModelVerdict, BaseModel, Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Per-model tallies. The dataset §9.7 wants, as far as it has grown., One turn's routing decision, as it is written down., How a model has actually been received, per `routing_log`. (+24 more)

### Community 34 - "test_router.py"
Cohesion: 0.08
Nodes (30): HealthTracker, ModelHealth, BaseModel, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture, Observed latency and the circuit breaker. A 429 is treated as a routing input… (+22 more)

### Community 35 - "Router"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 36 - "test_text.py"
Cohesion: 0.09
Nodes (36): build_prompt(), choose_model(), _extract_json(), Any, §8.3's prompt, with the two slots filled., §8.3: cloud if a key is present, local otherwise. Walks SMART then BALANCED,…, Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio (+28 more)

### Community 37 - "ToolContext"
Cohesion: 0.13
Nodes (30): anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice., `_build_context` runs once per attempt inside the failover loop, so without…, Below MIN_SCORE nothing is injected, so the prompt stays byte-identical to a…, The KV-cache invariant, asserted from the retrieval side too. (+22 more)

### Community 38 - "GenerationOptions"
Cohesion: 0.11
Nodes (33): is_local(), RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort., Observed latency overrides the seeded table as turns land., The router must always answer. A turn with no candidates is a crash., Local models are multi-GB downloads that may not have finished. (+25 more)

### Community 39 - "GeminiProvider"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 40 - "Connectivity"
Cohesion: 0.15
Nodes (19): is_tool_shaped(), needs_deep_model(), BaseModel, ModelInfo, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, A request to act on the machine rather than to talk about something., Reasoning, code, or a multi-step request: the `smart` class earns its cost., Chooses a model for a turn. (+11 more)

### Community 41 - "compilerOptions"
Cohesion: 0.09
Nodes (12): FakeLocator, FakePage, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, Refusing to act on an ambiguous-but-real description is worse than picking the…, Implements exactly the `Page` surface `browser.py` calls., test_click_risk_escalates_on_the_elements_own_wording(), test_click_risk_is_quiet_for_an_ordinary_click() (+4 more)

### Community 42 - "ConversationService"
Cohesion: 0.11
Nodes (29): drain(), frame(), Any, ndarray, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on…, Under MIN_SPEECH_MS of speech is a door or a chair, not a question., Without a wake word, silence is just silence — no capture, no turn. (+21 more)

### Community 43 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 44 - "test_rpc.py"
Cohesion: 0.11
Nodes (29): parse_openai(), Chat models from a `GET /v1/models` body., gemini_ids(), _load(), openai_ids(), Any, fixture, parametrize (+21 more)

### Community 45 - "test_research.py"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 46 - "compilerOptions"
Cohesion: 0.11
Nodes (16): Headers, Response, _assemble(), OpenAIProvider, Any, ChatMessage, GenerationOptions, StreamDelta (+8 more)

### Community 47 - "RecordingBus"
Cohesion: 0.07
Nodes (27): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+19 more)

### Community 48 - "soak_conversation.py"
Cohesion: 0.11
Nodes (26): overhead_tokens(), Tokens spent before the conversation even starts. Roll-up decisions must…, full(), Machine context: the clock, the model, and what it costs to carry them., CLAUDE.md: keep the pre-conversation budget near 800 tokens on local., Roll-up decisions subtract this; if it were uncounted, a conversation could…, Uncounted, a roll-up could 'succeed' and still overflow the context — the same…, The sentence that made her deny a conversation she had just had. "You know… (+18 more)

### Community 49 - "gate_tool_selection.py"
Cohesion: 0.12
Nodes (25): Which models are usable right now. One object answers this for both…, Cost, StrEnum, get_key(), Read a key, or None if unset. Never logs the value., discover_all(), discover_gemini(), discover_openai() (+17 more)

### Community 50 - "test_vectors.py"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 51 - "EpisodicMemory"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 52 - "Utterance"
Cohesion: 0.12
Nodes (25): Phase 0: foundation, Phase 1.5: multi-provider cloud client, Phase 3 finished: remaining tools, allow_danger_tools fix, app matching, Phase 3: the tool contract, Phase 4: the finder (find, search_files, search_content), ARIA Sidecar Runtime Dependencies (requirements.txt), fastapi==0.115.*, httpx==0.27.* (+17 more)

### Community 53 - "test_proactivity.py"
Cohesion: 0.11
Nodes (13): EpisodicMemory, datetime, StoredMessage, Writes and reads `episodes`. Never raises into the turn path., Summarize every conversation that has gone quiet. Returns how many., Summarize one session into an episode. Idempotent; never raises. `ended_at` is…, Stamp `ended_at` without writing an episode., Drop a session's episodes, so the session itself can be deleted.… (+5 more)

### Community 54 - "HealthReport"
Cohesion: 0.13
Nodes (22): Browser, Page, test_fill_types_the_value_into_the_match(), test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), browser_fill(), BrowserUnavailable, _connect() (+14 more)

### Community 55 - "ProviderUnavailable"
Cohesion: 0.13
Nodes (11): Task, What one turn recalled, plus what it cost., Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache. (+3 more)

### Community 56 - "test_screen.py"
Cohesion: 0.13
Nodes (23): parametrize, Browser control: the checkout/banking hard block, password refusal, and element…, The URL check catches the common case; a card-number field on an unlisted…, No page has loaded yet at this point — only the URL being navigated *to* is…, §11: the *next* tool call after this one is force-escalated by the agent loop —…, test_a_generic_domain_can_still_be_caught_by_its_dom(), test_known_checkout_and_banking_urls_are_recognised(), test_navigate_escalates_on_the_target_url_before_loading_it() (+15 more)

### Community 57 - "Indexer"
Cohesion: 0.12
Nodes (18): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+10 more)

### Community 58 - "OllamaProvider"
Cohesion: 0.13
Nodes (21): Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, One utterance: speech, then enough silence to end it. The silence has to clear…, The whole bug: "Aria" strips to an empty string, and the first build threw it…, The opposite of what this file asserted an hour ago, on purpose. A 12s window…, The old form must not regress just because a new one exists., Otherwise one "aria" leaves the microphone answering the room forever., 64 silent drops in one session were indistinguishable from a dead app., Otherwise "stop" said to someone else in the room is a command to her. (+13 more)

### Community 59 - "FakeProvider"
Cohesion: 0.11
Nodes (11): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText (+3 more)

### Community 60 - "browser.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 61 - "_looks_like_a_commit_action"
Cohesion: 0.16
Nodes (22): MonkeyPatch, A target that does not exist is the tool's "not found" to report, not a reason…, _returning(), test_click_names_what_it_could_not_find(), test_click_risk_is_quiet_when_nothing_resolved(), test_click_runs_the_match_it_finds(), test_current_page_escalation_checks_the_live_page(), test_current_page_escalation_is_quiet_on_an_ordinary_page() (+14 more)

### Community 62 - "bridge.d.ts"
Cohesion: 0.15
Nodes (21): test_system_info_reports_this_machine(), _endpoint_volume(), _facts(), get_system_info(), kill_process(), Any, tool, Facts about the machine, and the one knob she can turn on it. `get_system_info`… (+13 more)

### Community 63 - "Electron main + Python sidecar architecture"
Cohesion: 0.14
Nodes (15): Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, fixture, parametrize, Durable settings and the v1 -> v2 migration. The migration matters more than…, Values are JSON so a new setting never needs another migration., store() (+7 more)

### Community 64 - "test_db.py"
Cohesion: 0.11
Nodes (18): It is a strong constraint — it overrides the router — so it should be…, It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, test_a_wrapped_argument_description_survives_the_line_break(), test_no_registered_tool_documents_an_argument_it_then_truncates(), test_nothing_else_claims_local_only(), all_tools(), _arg_docs(), build_parameters() (+10 more)

### Community 65 - "RpcMethodError"
Cohesion: 0.11
Nodes (13): AsyncClient, HTMLParser, available(), Web search, and turning a page into something a model can read. BUILD_SPEC §9…, Readable text from a page, truncated on a word boundary., Which search backend can run, or None. Never raises, never blocks., Strip a page to its readable text. Not readability, not an article extractor,…, _Reader (+5 more)

### Community 66 - "proactivity.py"
Cohesion: 0.12
Nodes (10): ModelAvailability, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+2 more)

### Community 67 - "Source"
Cohesion: 0.11
Nodes (8): ndarray, Protocol, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance, VoiceActivity

### Community 68 - "gate_agent.py"
Cohesion: 0.10
Nodes (19): AriaApi, AssistantState, BrainStatus, CredentialStatus, LogLine, MemoryEpisode, MemoryFact, MemoryStats (+11 more)

### Community 69 - "MonkeyPatch"
Cohesion: 0.11
Nodes (19): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation (+11 more)

### Community 70 - "CredentialKey"
Cohesion: 0.17
Nodes (18): Every table in the database, including vec0 virtual tables., table_names(), Connection, Path, Phase 0 acceptance gate: the database is created and migrated from schema.sql., The schema declares float[768]; prove it round-trips., test_affect_state_singleton_is_seeded(), test_all_schema_tables_exist() (+10 more)

### Community 71 - "StubSearch"
Cohesion: 0.17
Nodes (18): _clamp(), _drift(), _energy_delta(), _format_hour(), _hours_since_last_interaction(), datetime, Four floats that make the same question read differently at 2am than at 2pm…, Roughly `[-1, 1]` from the last few user messages. Zero — the common case —… (+10 more)

### Community 72 - "_Reader"
Cohesion: 0.17
Nodes (18): browser_setup(), _cdp_reachable(), _default_browser(), Path, (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher() (+10 more)

### Community 73 - "main.py"
Cohesion: 0.13
Nodes (18): People say "remember that ..." to a thing whose job is remembering., The fallback is not a failure: the fact stays retrievable and the panel can fix…, test_a_lead_in_is_stripped(), test_an_unrecognised_phrasing_is_still_kept(), test_common_phrasings_become_real_predicates(), _clip(), forget(), tool (+10 more)

### Community 74 - "Phase 2 — Voice"
Cohesion: 0.14
Nodes (17): clean_title(), episode_request(), _persona(), ChatMessage, datetime, Prompt assembly and the rolling context window (BUILD_SPEC §8.2, §9 Phase 1).…, Fill in what she can reach and what she remembers. The rest is identical., Prompt asking the model to compress a whole session into an episode. Distinct… (+9 more)

### Community 75 - "FakePage"
Cohesion: 0.13
Nodes (17): health(), Any, Liveness probe for Electron's supervisor. Deliberately cheap and dependency-…, build_health(), HealthReport, models_refresh(), BaseModel, JSON-RPC method registry and dispatch (BUILD_SPEC §7.1). Phase 0 registers only… (+9 more)

### Community 76 - "test_catalog.py"
Cohesion: 0.14
Nodes (9): Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout., FakeConversation, Silero's seat, answering from a list instead of a model., The default path must work with nothing downloaded — that is the whole reason…, ScriptedSTT, ScriptedVAD, test_model_mode_without_a_model_is_refused_loudly() (+1 more)

### Community 77 - "Sidebar.tsx"
Cohesion: 0.16
Nodes (9): EventBus, Any, Protocol, Send the current state to one client, unconditionally. A reconnecting renderer…, Send a notification to every live client, dropping dead ones., Update the assistant state and notify clients if it actually changed., Minimal transport surface — a Starlette WebSocket satisfies this., Tracks connected clients and broadcasts notifications to them. (+1 more)

### Community 78 - "memory.py"
Cohesion: 0.18
Nodes (17): machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, The whole design rests on this. This block sits before the conversation, so a…, These are different things to tell someone., 4 days ago' is not worth the tokens, and the date already says when., Silence beats a wrong claim: unknown facts are simply not mentioned. (+9 more)

### Community 79 - "test_affect.py"
Cohesion: 0.15
Nodes (14): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, Run ``fn`` against the connection off the event loop, serialised., Open the database with sqlite-vec loaded and the required pragmas set. (+6 more)

### Community 80 - "Non-negotiable rules (1-10)"
Cohesion: 0.18
Nodes (9): Any, Response, RuntimeError, Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix., Fetch and strip anything that arrived without text. Concurrently, and failures…, No usable search key, or the provider refused. Carries the fix., SearchUnavailable (+1 more)

### Community 81 - "CATALOG (curated, measured models)"
Cohesion: 0.14
Nodes (16): estimate_tokens(), fit_to_budget(), Render remembered facts and episodes into one system message. Returns None when…, Drop oldest turns until the assembled prompt fits. Backstop, not policy.…, retrieved_block(), A turn about something she has no memory of must leave the prompt byte-…, A fact is a standing truth; an episode is one conversation., A clipped fact beats silence — the cap is a prefill guard, not a correctness… (+8 more)

### Community 82 - "devDependencies"
Cohesion: 0.14
Nodes (15): interrupt(), It cannot stop her yet: whether this is an interruption depends on what was…, One frame is a cough or her own voice leaking past echo cancellation., Talk over her, long enough to trip the sustained-speech guard., A cough, someone else in the room, or her own voice through the speakers. The…, The bug this whole section exists for: the guard read a state that nothing ever…, 13 ducks and 0 resumes in one log. She ducked, finished the sentence on her…, test_a_single_frame_of_noise_does_not_interrupt_her() (+7 more)

### Community 83 - "get_settings"
Cohesion: 0.17
Nodes (11): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+3 more)

### Community 84 - "Rule 5: destructive ops require T2+ and confirmation round-trip"
Cohesion: 0.14
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 85 - "Phase 3 — the tool contract"
Cohesion: 0.18
Nodes (14): Checkout/banking page hard-escalation to CONFIRM, PermissionEngine confirmation flow, Files and trusted folders (write/rename/move/delete tools), browser_click/browser_fill: SAFE tier with risk-based escalation, Phase 7 finished: real logged-in browser control over CDP, Browser launcher fix: detect real default browser (Brave, not Chrome), Rule 5: Every destructive operation requires T2+ and a confirmation round-trip, Rule 6: All tool calls are logged to the tool_log table (+6 more)

### Community 86 - "Phase 5 — she remembers"
Cohesion: 0.16
Nodes (14): is_stop_word(), Is this whole utterance just a request to stop talking?, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said., The name has to be first. Anywhere else it is just a word., Matched whole, never as a prefix. (+6 more)

### Community 87 - "discovery.py"
Cohesion: 0.21
Nodes (13): all_status(), CredentialKey, CredentialStatus, delete_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Credential Manager entry names under the ARIA service. (+5 more)

### Community 88 - "browser_read"
Cohesion: 0.15
Nodes (9): build(), _drain_windows(), parts(), phrase(), fixture, Cancel every listening window a test left open. Not optional: ARMED and OPEN…, openWakeWord gating — `hey jarvis` opens capture., The default: any speech is captured, and the transcript decides. (+1 more)

### Community 89 - "handlers.py"
Cohesion: 0.18
Nodes (13): Stable-first prompt ordering for Ollama KV cache reuse, Phase 5: she remembers (facts, episodes, reflection, MemoryPanel), Memory bug: she forgot a conversation she had just had (six causes), Phase 8: affect, procedural learning, proactivity, voice polish, Relevance-based tool selection: closed, measured, rejected, Rule 10: Do not refactor prior phases unless the current phase says to, nomic-embed-text (embedding model), apscheduler==3.10.* (deferred, Phase 5) (+5 more)

### Community 90 - "useConversation.ts"
Cohesion: 0.18
Nodes (13): Online mode: research(query) over search API and httpx, Overlay gets a direction of travel (ScreenRim inward/outward pulses), Phase 6: the agent loop (multi-step tool chaining), Rule 1: All state lives in the Python sidecar, sticky_local: local-only routing persists across agent loop steps, §11 untrusted_content boundary and force-escalation, scripts/gate_agent.py, scripts/gate_research.py (+5 more)

### Community 91 - "Barge-in: duck first, decide after (AssistantState.SPEAKING bug)"
Cohesion: 0.15
Nodes (13): electron, devDependencies, electron, postcss, react, react-dom, @types/ws, zustand (+5 more)

### Community 92 - "package.json"
Cohesion: 0.18
Nodes (11): ARIA Project Instructions (CLAUDE.md), Knowledge graph maintenance via graphify update, Phase 2 stage 1: she speaks (kokoro-onnx TTS), Rule 2: Never load a second model onto the GPU (6GB VRAM ceiling), Rule 3: Never add torch as a dependency, Rule 4: Every tool goes through the registry with an explicit permission tier, Rule 7: Python full type hints, pydantic models, async by default, Rule 8: TypeScript strict mode, no any (+3 more)

### Community 93 - "jsdom"
Cohesion: 0.20
Nodes (12): Handler, RpcRequest, RpcResponse, Token-gated JSON-RPC endpoint (§7.1). The port is reachable by any browser tab…, Read/dispatch/reply until the client goes away., rpc(), _serve(), dispatch() (+4 more)

### Community 94 - "registry.py"
Cohesion: 0.27
Nodes (9): Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, split_for_rollup(), Any, ChatMessage, GenerationOptions, StreamDelta, test_assemble_puts_stable_content_first(), test_no_rollup_under_budget() (+1 more)

### Community 95 - "HistoryPanel.tsx"
Cohesion: 0.18
Nodes (12): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., parametrize, The line that was missing. Without it these went to the FAST class., A false positive costs a spoken turn its ~800ms head start, which is the thing…, test_clipboard_questions_stay_on_this_machine(), test_code_requests_reach_a_reasoning_model(), test_conversation_is_not_mistaken_for_a_command() (+4 more)

### Community 96 - "open_app tool (T1)"
Cohesion: 0.17
Nodes (12): memory_forget(), memory_list(), memory_search(), memory_stats(), memory_update(), The memory services, or a message saying how to turn them on., Everything she has learned, for MemoryPanel. Superseded facts are excluded by…, §7.1: search what she remembers. The same path a turn uses. (+4 more)

### Community 97 - "spawn"
Cohesion: 0.21
Nodes (10): tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, The clipboard's text, or None when it holds something else. An image, a file…, Read the clipboard's text., _read(), read_clipboard(), _write() (+2 more)

### Community 98 - "conversation.py"
Cohesion: 0.20
Nodes (9): ConfirmRequest, ImagePreview, leaf(), MovePlan, MovePlanView(), Props, tail(), TIER_LABEL (+1 more)

### Community 99 - "test_finder.py"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 100 - "_cloud_model"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 101 - "ModelPicker.tsx"
Cohesion: 0.22
Nodes (8): pcm16_to_float32(), ndarray, RuntimeError, Load and warm. First use downloads ~150MB, which must not happen while someone…, One utterance to text. Empty string when nothing was said., Speech input could not start. Never fatal — she still reads typing., Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., TranscriptionUnavailable

### Community 102 - "core/context.py (stable/volatile prefix, machine_context)"
Cohesion: 0.18
Nodes (11): BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM unconditionally.…, §9:943 says "regardless of tool tier" — that only means something if *every*…, test_every_browser_tool_carries_the_checkout_escalation(), test_only_fill_carries_the_password_refusal(), test_tiers_deviate_from_build_specs_blanket_confirm_by_design(), T1. It reads and changes nothing; the consent that matters is the online…, test_research_needs_no_confirmation(), BUILD_SPEC's own tier table (§9:474) lists this AUTO — that line is about the… (+3 more)

### Community 103 - "Phase 4 — the finder"
Cohesion: 0.24
Nodes (7): clockTime(), dayGroup(), HistoryPanel(), label(), Row(), RowProps, session()

### Community 104 - "browser_navigate"
Cohesion: 0.35
Nodes (10): appendToStreaming(), clearStreaming(), finalise(), loadRatings(), toTurns(), Turn, TurnCompletePayload, UseConversation (+2 more)

### Community 105 - "system.py"
Cohesion: 0.20
Nodes (10): Health monitoring and degradation warnings, Local by default, cloud opt-in per turn, num_ctx capped at 8192, Offline is a first-class path, not an error path, Phase 0 — Foundation, Phase 6 — Agent loop + cloud routing, providers/base.py LLMProvider interface, Router — local vs cloud, then which provider (+2 more)

### Community 106 - "ConfirmDialog.tsx"
Cohesion: 0.22
Nodes (10): Model catalog discovery (measured overlay, hand-pick-only routing), Phase 4 closed: organize_folder, undo_organize, Tool.preview channel, Provider strategy: OpenAI + Gemini via API keys, Ollama offline fallback, Smart mode: set_volume direction fix and spoken-turn router fix, gemini-flash-lite (Smart mode fastest pick), anthropic==0.39.* (NOT adopted, Anthropic excluded), scripts/gate_organize.py, scripts/measure_models.py (+2 more)

### Community 107 - "preload.ts"
Cohesion: 0.33
Nodes (9): main(), _mechanism_checks(), _ok(), Row, §9 Phase 8's affect-model acceptance gate. the same question at a 2am-shaped…, Section 1: pure functions, no sidecar needed. Mirrors `test_affect.py` but as a…, _read_affect_row(), _restore_affect() (+1 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.29
Nodes (9): configure_logging(), _console_handler(), _file_handler(), Handler, Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file. (+1 more)

### Community 109 - "make_tray_icons.py"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 110 - "Fact"
Cohesion: 0.29
Nodes (9): conn(), database(), db_path(), Connection, fixture, Path, Shared fixtures. Every test gets a throwaway data dir — never the real data/., A migrated database on a temp path. (+1 more)

### Community 111 - "online"
Cohesion: 0.20
Nodes (10): _cloud_model(), ModelInfo, 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement…, The mechanism has to keep working, or banding would just be a way of ignoring…, test_a_measured_tool_score_outranks_latency_on_a_command(), test_a_model_that_is_visibly_worse_still_loses() (+2 more)

### Community 112 - "SettingsPanel.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 113 - "UI must be visually inspected; typecheck/tests miss layout bugs"
Cohesion: 0.22
Nodes (9): Phase 2 stage 2: speech in (faster-whisper), Phase 2 stage 3: hands free (wake word, VAD, endpointing, barge-in), faster-whisper (tiny.en/base.en STT), openWakeWord (ONNX wake-word model), faster-whisper==1.0.3, openwakeword==0.6.0, webrtcvad (deliberately absent, needs MSVC to build), scripts/gate_wakeword.py (+1 more)

### Community 114 - "._insert"
Cohesion: 0.22
Nodes (9): Locator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught(), test_commit_wording_in_the_visible_text_is_caught(), _looks_like_a_commit_action() (+1 more)

### Community 115 - "SpeechToText"
Cohesion: 0.25
Nodes (7): BrowserState, KEY_HELP, KEY_LABEL, OnlineState, RowProps, SEARCH_KEYS, SettingsPanel()

### Community 116 - "AvailabilityService"
Cohesion: 0.25
Nodes (6): api, AriaApi, BrainStatus, LogLine, SidecarEvent, Unsubscribe

### Community 117 - "MemoryPanel.test.tsx"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 118 - "Orb.tsx"
Cohesion: 0.36
Nodes (7): _chunk(), coverage(), main(), png_bytes(), Generate the tray icon PNGs embedded in electron/tray.ts. Electron's…, Fraction of one pixel covered by the circle, by supersampling., An 8-bit RGBA PNG of a filled circle on transparency.

### Community 119 - "scripts"
Cohesion: 0.29
Nodes (8): assemble(), Content identical across turns. Everything here is KV-cached. Changing `level`…, Build the final message list, stable content first., stable_prefix(), The KV-cache bargain, asserted directly. CLAUDE.md's measured rule: an…, test_memory_never_touches_the_stable_prefix(), The KV cache only holds if this never varies (§8.2)., test_stable_prefix_is_byte_identical_across_calls()

### Community 120 - "gate_research.py"
Cohesion: 0.32
Nodes (8): Two or more failed tool calls in this session, recently — 'repeated', not 'a…, _repeated_failures(), _log_failure(), Connection, _seed_session(), test_a_failure_outside_the_recent_window_does_not_count(), test_refresh_loads_updates_and_saves_in_one_call(), test_repeated_failures_reads_recent_tool_log()

### Community 121 - "test_browser.py"
Cohesion: 0.25
Nodes (3): AvailabilityService, Handles owned by the app lifespan., Runtime

### Community 122 - "ConversationView.tsx"
Cohesion: 0.29
Nodes (7): Local model decision: qwen2.5:7b default, qwen3.5:9b banned, routing_log table + thumbs rating (§9.7, migration 005), Per-model tool selection scoreboard (gate_tool_selection.py), gpt-5.4-mini (adopted cloud model), gpt-5.4-nano (adopted cloud model), qwen2.5:7b (local default model), qwen3.5:4b (rejected local model)

### Community 123 - "MemoryPanel.tsx"
Cohesion: 0.29
Nodes (7): test_read_returns_cleaned_text_with_the_url(), test_screenshot_returns_a_base64_image(), browser_read(), browser_screenshot(), tool, Read the current page as text., Screenshot the current tab. Ephemeral — never written to disk (§11), the same…

### Community 124 - "Torch-free Python sidecar"
Cohesion: 0.43
Nodes (4): defaults(), episode(), fact(), stats()

### Community 125 - "affect.py"
Cohesion: 0.33
Nodes (6): BREATH, HUE, Orb(), ORB_LAYOUT_ID, OrbProps, SPINS

### Community 126 - "App.tsx"
Cohesion: 0.33
Nodes (6): scripts, build, dev, sidecar, test, typecheck

### Community 127 - "ModelPicker.test.tsx"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 128 - "ToolCallCard.tsx"
Cohesion: 0.33
Nodes (3): StrEnum, How much latency the user will trade for a better answer., RoutingBias

### Community 129 - "ToolsPanel.tsx"
Cohesion: 0.33
Nodes (5): Any, Task, Fire-and-forget work that must not take the process down with it. Two rules,…, Run `coro` detached. Failures are logged against `name`, never raised., spawn()

### Community 130 - "VoiceAura.tsx"
Cohesion: 0.33
Nodes (6): Exception, _raising(), test_navigate_adds_a_scheme_when_none_was_given(), test_navigate_reports_browser_unavailable_plainly(), browser_navigate(), Open a URL in the current tab. Args: url: The address to go to, including…

### Community 131 - "ScreenRim.tsx"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 133 - "gate_memory.py"
Cohesion: 0.53
Nodes (5): confidenceStyle(), FactRow(), MemoryPanel(), summarise(), whenever()

### Community 134 - "Settings"
Cohesion: 0.50
Nodes (5): is_casual(), A rough stand-in for BUILD_SPEC's own undefined `conversation_is_casual` —…, parametrize, test_short_conversational_messages_are_casual(), test_task_shaped_messages_are_not_casual()

### Community 135 - "drain_text"
Cohesion: 0.40
Nodes (3): drag, noDrag, Overlay

### Community 136 - "ConnectionStatus.tsx"
Cohesion: 0.60
Nodes (3): entry(), model(), models()

### Community 138 - "useAudio.ts"
Cohesion: 0.40
Nodes (3): TIER_LABEL, TIER_STYLE, ToolSummary

### Community 139 - "useMic.ts"
Cohesion: 0.40
Nodes (3): AuraMode, HUE, Props

### Community 140 - "Persona boundaries — capacity to push back"
Cohesion: 0.40
Nodes (3): HUE, Props, RimMode

### Community 141 - "Nightly reflection prompt (reflect.j2)"
Cohesion: 0.50
Nodes (4): Barge-in — interrupt playback on speech, Phase 2 — Voice, Sentence-level TTS streaming, openWakeWord hey_jarvis wake detection

### Community 142 - "gate_delete.py"
Cohesion: 0.50
Nodes (4): Phase 6 finished: capture_screen + cloud vision, mss==9.0.*, pillow>=10.4,<11, sidecar/tools/screen.py

### Community 143 - "parametrize"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 6's agent loop, against the running sidecar. "find <scratch file>,…

### Community 144 - "migrate"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 7's browser half, against a real, CDP-attached Chrome. "open…

### Community 145 - "FakeTTS"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 5's acceptance gate, against the running sidecar. "I usually work on…

### Community 146 - "ComposerBar.tsx"
Cohesion: 0.50
Nodes (4): Content that changes per turn. Everything after this point re-prefills. Phase…, volatile_prefix(), §8.2's order: temporal, then facts. Memory sits nearest the turns because that…, test_retrieved_memory_sits_after_the_clock()

### Community 149 - "HandsFreeToggle.tsx"
Cohesion: 0.67
Nodes (3): AudioChunk, decodePcm16(), useAudio

### Community 150 - "HandsFreeToggle.test.tsx"
Cohesion: 0.67
Nodes (3): encodePcm16(), Recording, useMic

### Community 151 - "Shortcuts.tsx"
Cohesion: 0.67
Nodes (3): Persona boundaries — capacity to push back, Character, not sycophancy, aria.yaml persona configuration

### Community 152 - "VoicePanel.tsx"
Cohesion: 0.67
Nodes (3): Fact merge and supersession logic, Phase 5 — Memory, Nightly reflection prompt (reflect.j2)

### Community 154 - "useHandsFree.ts"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 155 - "useModels.ts"
Cohesion: 0.67
Nodes (3): Connection, test_fresh_database_lands_on_the_current_version(), test_selected_model_is_seeded_to_smart()

## Ambiguous Edges - Review These
- `Phase 8: affect, procedural learning, proactivity, voice polish` → `apscheduler==3.10.* (deferred, Phase 5)`  [AMBIGUOUS]
  requirements.txt · relation: references

## Knowledge Gaps
- **234 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+229 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **75 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Phase 8: affect, procedural learning, proactivity, voice polish` and `apscheduler==3.10.* (deferred, Phase 5)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `Database` connect `test_scheduler.py` to `test_procedures.py`, `test_tools.py`, `main.ts`, `Role`, `test_conversation.py`, `test_discovery.py`, `Tier`, `SemanticMemory`, `Event`, `listener.py`, `SettingsStore`, `_start_conversation`, `useModels.ts`, `ConversationStore`, `test_episodic.py`, `OpenEngine`, `test_text.py`, `ToolContext`, `test_proactivity.py`, `browser.py`, `Electron main + Python sidecar architecture`, `CredentialKey`, `StubSearch`, `test_affect.py`, `get_settings`, `make_tray_icons.py`, `Fact`, `gate_research.py`, `test_browser.py`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `test_conversation.py` to `method`, `test_procedures.py`, `test_tools.py`, `test_focus.py`, `main.ts`, `Database`, `Role`, `test_scheduler.py`, `Sidebar.tsx`, `SemanticMemory`, `get_settings`, `HealthTracker`, `Listener`, `test_browser.py`, `ChatMessage`, `FakeProvider`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ChatMessage` to `test_focus.py`, `test_tools.py`, `VoiceAura.tsx`, `ScreenRim.tsx`, `test_organize.py`, `apps.py`, `Role`, `test_conversation.py`, `Tier`, `Listener`, `test_browser_setup.py`, `probes.py`, `credentials.py`, `compilerOptions`, `HealthReport`, `test_screen.py`, `_looks_like_a_commit_action`, `bridge.d.ts`, `test_db.py`, `main.py`, `spawn`, `MemoryPanel.tsx`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 48 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `RouteDecision`) actually correct?**
  _`HealthTracker` has 12 INFERRED edges - model-reasoned connections that need verification._