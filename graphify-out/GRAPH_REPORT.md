# Graph Report - ARIA  (2026-08-20)

## Corpus Check
- 248 files · ~358,128 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 5084 nodes · 11581 edges · 289 communities (219 shown, 70 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1021 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `410e11ad`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_permissions.py
- test_listener.py
- main.ts
- test_catalog.py
- test_rpc.py
- test_reflection.py
- test_attachments.py
- test_tts.py
- Database
- test_scheduler.py
- test_proactivity.py
- test_discovery.py
- KokoroTTS
- ModelInfo
- finder.py
- apps.py
- indexer.py
- SileroVAD
- test_modes.py
- ConversationStore
- Role
- HealthTracker
- SemanticMemory
- test_screen.py
- ChatMessage
- test_ollama_supervisor.py
- test_router.py
- test_extract.py
- handlers.py
- OpenEngine
- RoutingLog
- test_organize.py
- Router
- semantic.py
- test_retrieval.py
- Tier
- EpisodicMemory
- listener.py
- Listener
- test_db.py
- AdoptionService
- test_focus.py
- test_episodic.py
- ARIA — Project Instructions
- ToolContext
- ConversationService
- OpenAIProvider
- .close_session
- test_questions.py
- EventBus
- PersonaLevel
- test_text.py
- StreamDelta
- LoopState
- compilerOptions
- Event
- Connectivity
- test_conversation.py
- snapshot
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- main.py
- compilerOptions
- stable_prefix
- context.py
- SpeechStream
- test_tools.py
- test_vectors.py
- test_context.py
- test_browser_setup.py
- for_model
- test_affect.py
- Utterance
- StubSearch
- extract.py
- Episode
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- _cloud_model
- test_adoption.py
- registry.py
- discovery.py
- system.py
- FilesPanel.tsx
- Sidecar
- Client
- test_ask.py
- test_a_spoken_command_is_no_longer_forced_onto_the_local_model
- Indexer
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- ToolResult
- free_model
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- SettingsStore
- AvailabilityService
- PermissionEngine
- FakeLocator
- FilesPanel.test.tsx
- HealthReport
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- FakePage
- spawn
- render
- gate_organize.py
- _start_conversation
- HistoryPanel.tsx
- CLAUDE.md — ARIA Project Instructions (Claude Code-facing)
- Router — local vs cloud, then which provider
- gate_affect.py
- Retriever
- AffectState
- usePermissionMode.ts
- ProviderUnavailable
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- gate_research.py
- Question
- SettingsPanel.tsx
- preload.ts
- Client
- make_tray_icons.py
- PermissionModeChip.tsx
- _repeated_failures
- ToolsPanel.tsx
- Phase 8 — moods, procedural learning, proactivity, voice polish
- Query: QA assessment against BUILD_SPEC
- Phase 2 stage 3 — hands free (wake word, VAD, endpointing)
- RpcClient
- MemoryPanel.test.tsx
- Orb.tsx
- scripts
- core/router.py — model Router
- tray.ts
- useAskQuestion.ts
- probes.py
- gate_agent.py
- WebSearch
- MemoryPanel.tsx
- She holds a conversation now (2026-08-07)
- Measuring answer quality
- Smart mode: it was the tool, and then it was the router (2026-08-12)
- _escalate_current_page
- is_casual
- App.tsx
- ModelPicker.test.tsx
- ToolCallCard.tsx
- VoiceAura.tsx
- ScreenRim.tsx
- Phase 8 — she has moods, and does not go quiet forever (2026-08-14)
- Phase 2 — Voice
- datetime
- gate_browser.py
- gate_memory.py
- tokens.test.ts
- ConnectionStatus.tsx
- Markdown.tsx
- ToolsPanel.test.tsx
- useAudio.ts
- useMic.ts
- Online mode: she can reach the web now (2026-08-13)
- Persona boundaries — capacity to push back
- Nightly reflection prompt (reflect.j2)
- Tool.preview channel: one confirmation shows a whole batch plan (organize_folder)
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
- Phase 2 stage 3 — hands free (2026-08-07)
- Phase 3 finished — the rest of the tools, and a flag that never worked (2026-08-09)
- She forgot a conversation she had just had (2026-08-12)
- Phase 9 — Packaging
- db.py
- electron-vite
- framer-motion
- jsdom
- Source
- remark-gfm
- files_rename
- @testing-library/react
- @types/node
- @types/react
- @types/react-dom
- parse_openrouter
- _Reader
- vite
- @vitejs/plugin-react
- vitest
- sidecar/__init__.py
- persona/__init__.py
- ask_user
- test_the_gate_is_the_same_probes_the_scripts_use
- test_browser.py
- questions.py
- useConversationMode.ts
- motion.ts
- acrylic.test.ts
- ModeSelector.test.tsx
- useConfirm.ts
- useMemory.ts
- usePushToTalk.ts
- useRpc.ts
- useWindowMode.ts
- src/main.tsx
- overlay/main.tsx
- One phase per session execution model
- Always send think:false to qwen3.x reasoning models
- overlay.html entry (#overlay → src/overlay/main.tsx)
- aria-sidecar
- Warm persona embeds its own anti-invention clause against fabricated shared memory
- tokens.d.ts
- clipboard.py
- test_research.py
- conversation.py
- WakeWord
- catalog.py
- tokens.js
- rpc.ts
- ._resolve_procedure_reply
- database
- useConversation.test.ts
- pcm16_to_float32
- table_names
- parse_gemini
- Any
- ollama_supervisor.py
- _Semantic
- _reset_connection
- eval/__init__.py
- postcss
- react-dom
- rehype-highlight
- @types/ws
- online
- ModelListing
- test_the_perfect_model_answers_every_probe
- electron-builder
- _escalate_click_risk
- _locate
- .record_access
- .refresh_discovered
- zustand
- test_the_filter_is_not_simply_rejecting_everything
- test_archives_are_attachable_but_never_indexed
- test_a_short_code_request_is_not_answered_locally_to_save_time
- test_ordinary_questions_do_not_get_the_expensive_tier
- test_a_command_is_not_slowed_down_for_a_difference_that_is_noise
- test_an_ordinary_question_still_takes_the_fast_class

## God Nodes (most connected - your core abstractions)
1. `Database` - 266 edges
2. `ConversationStore` - 168 edges
3. `ConversationService` - 118 edges
4. `HealthTracker` - 106 edges
5. `ToolContext` - 97 edges
6. `SemanticMemory` - 92 edges
7. `ChatMessage` - 87 edges
8. `ToolResult` - 86 edges
9. `GenerationOptions` - 65 edges
10. `Router` - 63 edges

## Surprising Connections (you probably didn't know these)
- `AGENTS.md — ARIA Project Instructions (Codex-facing)` --semantically_similar_to--> `CLAUDE.md — ARIA Project Instructions (Claude Code-facing)`  [INFERRED] [semantically similar]
  AGENTS.md → CLAUDE.md
- `Overlay page paints no background of its own` --semantically_similar_to--> `No CSP meta tag; main.ts sets the header per-environment`  [INFERRED] [semantically similar]
  overlay.html → index.html
- `Result` --uses--> `Probe`  [INFERRED]
  scripts/eval_quality.py → sidecar/eval/probes.py
- `Result` --uses--> `ChatMessage`  [INFERRED]
  scripts/eval_quality.py → sidecar/providers/base.py
- `Result` --uses--> `GenerationOptions`  [INFERRED]
  scripts/eval_quality.py → sidecar/providers/base.py

## Import Cycles
- 3-file cycle: `sidecar/core/conversation.py -> sidecar/state.py -> sidecar/core/listener.py -> sidecar/core/conversation.py`

## Hyperedges (group relationships)
- **ARIA's layered safety/confirmation system** — permission_engine, rule_destructive_confirmation, rationale_untrusted_source_escalation, rationale_checkout_escalation, rationale_confirm_timeout_denied [INFERRED 0.85]
- **Memory repair: six-cause conversation-forgetting investigation and fix** — bug_she_forgot_conversation, rationale_memory_high_water_mark, rationale_salience_computed_not_asked, memory_system, phase_5_memory [EXTRACTED 1.00]
- **Phase 6 agent loop design: step-aware routing, privacy stickiness, escalation** — agent_loop, rationale_sticky_local, rationale_untrusted_source_escalation, phase_6_agent_loop, router_core [EXTRACTED 1.00]
- **KV-cache latency discipline across prompt assembly** — build_spec_stable_prefix_ordering, build_spec_prefill_cost [INFERRED 0.85]

## Communities (289 total, 70 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (106): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+98 more)

### Community 1 - "test_listener.py"
Cohesion: 0.06
Nodes (71): Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout., drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device… (+63 more)

### Community 2 - "main.ts"
Cohesion: 0.15
Nodes (22): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+14 more)

### Community 3 - "test_catalog.py"
Cohesion: 0.08
Nodes (38): default_local(), local_models(), persona_for(), The local fallback. Prefers the instruction-tuned 7B. `pulled` is what Ollama…, Persona level for a model; unknown ids get the safe, minimal prompt., Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from., resolve_availability() (+30 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.09
Nodes (45): _port_is_free(), Whether we can actually have the port, checked before anything else. **A second…, files_browse(), method_names(), One folder's contents, for the panel. Deliberately not `list_folder`: that tool…, _auth(), _call(), client() (+37 more)

### Community 5 - "test_reflection.py"
Cohesion: 0.09
Nodes (38): build_prompt(), choose_model(), _extract_json(), Any, §8.3's prompt, with the two slots filled., §8.3: cloud if a key is present, local otherwise. Walks SMART then BALANCED,…, Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio (+30 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.07
Nodes (59): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no…, One attachment, understood. Never raises. (+51 more)

### Community 7 - "test_tts.py"
Cohesion: 0.04
Nodes (63): ndarray, RuntimeError, Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, Voice could not start. Never fatal — she still types., shorten_for_speech() (+55 more)

### Community 8 - "Database"
Cohesion: 0.09
Nodes (48): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), Procedural learning — tier 4 of memory (BUILD_SPEC §9 Phase 8). `procedures`… (+40 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.05
Nodes (77): Unprompted messages (Phase 8). Off entirely when the switch is off — the same…, _start_proactivity_scheduler(), pending_offers(), Row, Detected, not yet confirmed or declined — what the proactivity engine has to…, Candidate, default_candidates(), default_self_check() (+69 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.13
Nodes (25): parse_openai(), Chat models from a `GET /v1/models` body., gemini_ids(), _load(), openai_ids(), Any, fixture, parametrize (+17 more)

### Community 12 - "KokoroTTS"
Cohesion: 0.06
Nodes (38): Case, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance., run() (+30 more)

### Community 13 - "ModelInfo"
Cohesion: 0.07
Nodes (34): adopt(), adopted(), all_models(), clear_adopted(), discovered(), ModelInfo, Record a model as measured-and-passed, making it routable. Curated ids still…, Tests only. The overlay is process-global, like `_DISCOVERED`. (+26 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (69): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The… (+61 more)

### Community 15 - "apps.py"
Cohesion: 0.05
Nodes (70): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, AppEntry, _AppIndex, _bring_to_front(), _build_index(), clear_type_targets(), close_app() (+62 more)

### Community 16 - "indexer.py"
Cohesion: 0.12
Nodes (24): chunk(), _pack(), The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, Whether this file is worth reading at all., sqlite-vec takes raw little-endian float32., Overlapping windows, so a sentence spanning a boundary stays findable., should_index(), parametrize (+16 more)

### Community 17 - "SileroVAD"
Cohesion: 0.06
Nodes (28): main(), Download the wake word weights into data/models/openwakeword. python…, frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python… (+20 more)

### Community 18 - "test_modes.py"
Cohesion: 0.06
Nodes (45): policy_for(), ConversationMode, The policy, or Normal's. Never raises. A mode arriving from a stale client is a…, A mode this turn would be better served by, or None. None is the answer for the…, suggest(), ConversationMode, parametrize, Modes as operating systems, not tones. Eyaas's own framing after using the… (+37 more)

### Community 19 - "ConversationStore"
Cohesion: 0.07
Nodes (41): ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, When anything was last said, in any session. The whole precondition for §9's…, A fresh id with no row behind it yet. `ensure_session` creates a row for any id…, Name a conversation. The `with conn:` is load-bearing. Python's sqlite3 opens… (+33 more)

### Community 20 - "Role"
Cohesion: 0.07
Nodes (29): cosine(), main(), measure_choice(), measure_recall(), Should tool schemas be filtered by relevance before the model sees them? §7.2…, Would a selector keep the right tool? The question that decides it., Does a shorter list make the model choose better? Measured, not assumed., _clamp_summary() (+21 more)

### Community 21 - "HealthTracker"
Cohesion: 0.08
Nodes (30): HealthTracker, ModelHealth, BaseModel, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture, Observed latency and the circuit breaker. A 429 is treated as a routing input… (+22 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.07
Nodes (49): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:… (+41 more)

### Community 23 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 24 - "ChatMessage"
Cohesion: 0.11
Nodes (21): choose_with(), measure_per_model(), Score each model's tool choice, for `ModelInfo.tool_score`. **There was no such…, Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, split_for_rollup(), Compress the oldest turns. Folds in any earlier note so it compounds., Free-model measurement, and putting past adoptions back in the pool.…, _start_adoption() (+13 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.07
Nodes (40): OllamaSupervisor, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was…, FakeOllama, Any, Path (+32 more)

### Community 26 - "test_router.py"
Cohesion: 0.08
Nodes (48): is_trivial(), needs_deep_model(), A greeting or acknowledgement — nothing a 4B model can get wrong., Reasoning, code, or a multi-step request: the `smart` class earns its cost., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router… (+40 more)

### Community 27 - "test_extract.py"
Cohesion: 0.13
Nodes (30): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+22 more)

### Community 28 - "handlers.py"
Cohesion: 0.05
Nodes (86): delete_key(), build_health(), chat_cancel(), chat_delete(), chat_history(), chat_mode(), chat_new(), chat_rename() (+78 more)

### Community 29 - "OpenEngine"
Cohesion: 0.07
Nodes (60): A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, _drain(), OpenEngine, Path, ToolCall, §11 escalates the step after *reading* untrusted content. A `research` that was…, Decided with Eyaas (2026-08-18): §11 guards against untrusted content reaching… (+52 more)

### Community 30 - "RoutingLog"
Cohesion: 0.07
Nodes (33): ModelVerdict, BaseModel, What the router decided, and what the user made of it (§9.7). §9.7's closing…, Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Per-model tallies. The dataset §9.7 wants, as far as it has grown., One turn's routing decision, as it is written down. (+25 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (71): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+63 more)

### Community 32 - "Router"
Cohesion: 0.13
Nodes (18): BaseModel, ModelInfo, Whether this endpoint may train on what is sent to it. Unknown ids read as…, Chooses a model for a turn., Pick a model. `selected` is the user's choice — a model id, or "smart" to…, `bias` overrides the instance setting for this call only. **A parameter, not a…, Cloud unless the turn is trivial. The default. `_DEEP_VERBS` is checked here…, Cloud for real work, local for conversation. (+10 more)

### Community 33 - "semantic.py"
Cohesion: 0.06
Nodes (28): _now(), Return an existing session id, or create one., Fact, normalise_triple(), _now(), datetime, Row, Facts — what she has LEARNED about you (BUILD_SPEC §7.3 tier 3, §8.3). A fact… (+20 more)

### Community 34 - "test_retrieval.py"
Cohesion: 0.11
Nodes (33): 1.0 today, 0.5 after a month, never quite zero., recency_decay(), anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice., `_build_context` runs once per attempt inside the failover loop, so without… (+25 more)

### Community 35 - "Tier"
Cohesion: 0.05
Nodes (55): EscalateFn, PreviewFn, RefuseFn, StrEnum, How much of the registry a mode lets the model see. **Narrowing, never…, The highest tier this policy will show, or None for no tools., ToolPolicy, The tier says she may run it; this says the answer stays here. A clipboard… (+47 more)

### Community 36 - "EpisodicMemory"
Cohesion: 0.06
Nodes (40): EpisodicMemory, Writes and reads `episodes`. Never raises into the turn path., Stamp `ended_at` without writing an episode., Drop a session's episodes, so the session itself can be deleted.…, ExtractedEpisode, ExtractedFact, BaseModel, datetime (+32 more)

### Community 37 - "listener.py"
Cohesion: 0.11
Nodes (24): clips(), main(), ndarray, Can she hear her own name? Across many voices, because one is not a test.…, score(), is_stop_word(), _near_the_name(), Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3). The renderer opens the… (+16 more)

### Community 38 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 39 - "test_db.py"
Cohesion: 0.18
Nodes (17): current_version(), Connection, Path, Phase 0 acceptance gate: the database is created and migrated from schema.sql., The schema declares float[768]; prove it round-trips., test_affect_state_singleton_is_seeded(), test_all_schema_tables_exist(), test_db_file_is_created() (+9 more)

### Community 40 - "AdoptionService"
Cohesion: 0.08
Nodes (31): Probe, Rules every reply obeys, regardless of what was asked., universal_failures(), AdoptionService, AdoptionState, grade(), _probes_by_id(), Any (+23 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "test_episodic.py"
Cohesion: 0.09
Nodes (45): _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, FactHit, BaseModel, A fact with its retrieval scoring, for the panel and the prompt., EmbeddingsUnavailable, RuntimeError, Ollama could not embed. Never fatal — the name search still works. (+37 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "ToolContext"
Cohesion: 0.13
Nodes (34): OneDrive relocates Documents and Desktop by default, so joining onto…, test_it_uses_the_real_location_not_a_guess(), create_folder(), delete_file(), delete_folder(), _GUID, known_folder(), list_folder() (+26 more)

### Community 45 - "ConversationService"
Cohesion: 0.04
Nodes (29): SessionSummary, ConversationService, ConversationMode, RoutingBias, Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, Name the conversation once it has enough content to name. Deliberately fire-…, Hold until no turn is in flight. False if the user never stops., Ask the local model for a short label. Never raises. (+21 more)

### Community 46 - "OpenAIProvider"
Cohesion: 0.10
Nodes (15): _assemble(), OpenAIProvider, Any, Headers, Response, ToolCall, No-op: cloud models have no local load step to pay for., Per-request fields this vendor accepts and OpenAI does not. A hook rather than… (+7 more)

### Community 47 - ".close_session"
Cohesion: 0.14
Nodes (7): datetime, StoredMessage, Summarize every conversation that has gone quiet. Returns how many., Summarize one session into an episode. Idempotent; never raises. `ended_at` is…, How much this conversation deserves to be remembered, computed. **The model was…, One model call for the summary and a salience hint. ("", 0.5) on failure., Embed episodes written while Ollama was down.

### Community 48 - "test_questions.py"
Cohesion: 0.11
Nodes (22): Answer, QuestionBroker, What came back for one question., Puts a question on screen and waits for the answer., Resolve a waiting question. False if it already went., Release every waiter as unanswered. Wired to shutdown, unlike…, FakeBus, Any (+14 more)

### Community 49 - "EventBus"
Cohesion: 0.14
Nodes (12): EventBus, Any, Protocol, Server -> client push notifications and the set of live connections (§7.1).…, Minimal transport surface — a Starlette WebSocket satisfies this., Tracks connected clients and broadcasts notifications to them., Send the current state to one client, unconditionally. A reconnecting renderer…, Send a notification to every live client, dropping dead ones. (+4 more)

### Community 50 - "PersonaLevel"
Cohesion: 0.08
Nodes (36): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+28 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "StreamDelta"
Cohesion: 0.07
Nodes (32): ProviderRateLimited, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, One chunk of a streaming response. `text` carries *content only*. Reasoning…, StreamDelta, all_status(), CredentialKey, CredentialStatus, get_key() (+24 more)

### Community 53 - "LoopState"
Cohesion: 0.11
Nodes (15): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Mark one step as run. `local_only` is unknown, not False, for a tool the…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through… (+7 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "Event"
Cohesion: 0.07
Nodes (25): Bus, Any, ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, AssistantState (+17 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "test_conversation.py"
Cohesion: 0.07
Nodes (59): FakeProvider, make_service(), _proactivity_service(), anyio, Connection, fixture, MonkeyPatch, Turn orchestration, cancellation, persistence and context roll-up. (+51 more)

### Community 58 - "snapshot"
Cohesion: 0.18
Nodes (11): BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM unconditionally.…, §9:943 says "regardless of tool tier" — that only means something if *every*…, test_every_browser_tool_carries_the_checkout_escalation(), test_only_fill_carries_the_password_refusal(), test_tiers_deviate_from_build_specs_blanket_confirm_by_design(), T1. It reads and changes nothing; the consent that matters is the online…, test_research_needs_no_confirmation(), BUILD_SPEC's own tier table (§9:474) lists this AUTO — that line is about the… (+3 more)

### Community 59 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (27): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+19 more)

### Community 60 - "ARIA Sidecar Runtime Dependencies (requirements.txt)"
Cohesion: 0.07
Nodes (27): ARIA Sidecar Runtime Dependencies (requirements.txt), anthropic==0.39.* (NOT adopted, Anthropic excluded), apscheduler==3.10.* (deferred, Phase 5), fastapi==0.115.*, faster-whisper==1.0.3, httpx==0.27.*, keyring==25.7.* (Windows Credential Manager), kokoro-onnx==0.4.* (+19 more)

### Community 61 - "main.py"
Cohesion: 0.06
Nodes (44): FastAPI, get, get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., bearer_from_header(), clear_handshake(), Path (+36 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "stable_prefix"
Cohesion: 0.11
Nodes (25): assemble(), Content identical across turns. Everything here is KV-cached. Changing `level`…, Build the final message list, stable content first., stable_prefix(), ConversationMode, parametrize, The KV-cache bargain, asserted directly. CLAUDE.md's measured rule: an…, `overhead_tokens` must equal what `assemble` actually produces, for every flag,… (+17 more)

### Community 64 - "context.py"
Cohesion: 0.09
Nodes (25): clean_title(), ConversationMode, episode_request(), _mode_block(), mode_done_when(), mode_label(), _persona(), datetime (+17 more)

### Community 65 - "SpeechStream"
Cohesion: 0.10
Nodes (17): Any, ModelInfo, ToolCall, Run steps until a text answer, loop detection, or the step budget ends it…, Which model gets to see the tool's result. `router._PRIVATE` already keeps a…, Evict the previous local model before loading a different one. CLAUDE.md rule…, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Say a reply aloud, on request. False when there is no voice engine. The other… (+9 more)

### Community 66 - "test_tools.py"
Cohesion: 0.03
Nodes (124): app(), _focused(), MonkeyPatch, parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and… (+116 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "test_context.py"
Cohesion: 0.05
Nodes (72): estimate_tokens(), fit_to_budget(), machine_context(), MachineContext, overhead_tokens(), Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase… (+64 more)

### Community 69 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+9 more)

### Community 70 - "for_model"
Cohesion: 0.33
Nodes (6): provider_for(), ModelInfo, One line, because the hand-written version here was a trap. It mapped Ollama…, for_model(), ModelInfo, The client that answers for this model.

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "Utterance"
Cohesion: 0.10
Nodes (9): ndarray, Protocol, Voice activity detection — streaming Silero (BUILD_SPEC §9 Phase 2 stage 3).…, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance (+1 more)

### Community 73 - "StubSearch"
Cohesion: 0.15
Nodes (14): Exception, Stripping is a losing game — there are unlimited phrasings. The content is…, It has a title, a URL and a snippet. Citing it beats pretending the search did…, A model that asks for fifty pages would blow the context budget §8.2 exists to…, Stands in for the network. Returns whatever it was handed., StubSearch, test_a_source_that_would_not_load_is_still_cited(), test_an_empty_query_asks_rather_than_searching() (+6 more)

### Community 74 - "extract.py"
Cohesion: 0.10
Nodes (26): _extract_bytes(), extract_text(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as… (+18 more)

### Community 75 - "Episode"
Cohesion: 0.10
Nodes (20): Episode, BaseModel, Row, A row from `episodes`, as the panel and retrieval see it., Nearest episodes to a vector, as (episode, cosine)., _age_days(), datetime, §9 Phase 5: 0.6·cosine + 0.25·recency + 0.15·salience, boosted by access. Two… (+12 more)

### Community 76 - "bridge.d.ts"
Cohesion: 0.10
Nodes (19): AriaApi, AssistantState, BrainStatus, CredentialStatus, LogLine, MemoryEpisode, MemoryFact, MemoryStats (+11 more)

### Community 77 - "Electron main + Python sidecar architecture"
Cohesion: 0.11
Nodes (19): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation (+11 more)

### Community 78 - "affect.py"
Cohesion: 0.17
Nodes (18): _clamp(), _drift(), _energy_delta(), _format_hour(), _hours_since_last_interaction(), datetime, Four floats that make the same question read differently at 2am than at 2pm…, Roughly `[-1, 1]` from the last few user messages. Zero — the common case —… (+10 more)

### Community 79 - "_cloud_model"
Cohesion: 0.22
Nodes (9): _cloud_model(), 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement…, The mechanism has to keep working, or banding would just be a way of ignoring…, test_a_measured_tool_score_outranks_latency_on_a_command(), test_a_model_that_is_visibly_worse_still_loses(), test_an_unmeasured_model_is_neither_promoted_nor_punished() (+1 more)

### Community 80 - "test_adoption.py"
Cohesion: 0.11
Nodes (49): by_class(), The router's pool: **measured only** — curated, or adopted after passing. The…, a_model(), Asker, Clock, perfect_reply(), Any, ModelInfo (+41 more)

### Community 81 - "registry.py"
Cohesion: 0.10
Nodes (21): It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, It is a strong constraint — it overrides the router — so it should be…, test_a_wrapped_argument_description_survives_the_line_break(), test_no_registered_tool_documents_an_argument_it_then_truncates(), test_nothing_else_claims_local_only(), all_tools(), _arg_docs(), build_parameters() (+13 more)

### Community 82 - "discovery.py"
Cohesion: 0.17
Nodes (17): Cost, StrEnum, discover_all(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch(), _openai_class() (+9 more)

### Community 83 - "system.py"
Cohesion: 0.13
Nodes (23): test_system_info_reports_this_machine(), _endpoint_volume(), _facts(), get_system_info(), kill_process(), list_processes(), Any, tool (+15 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "Sidecar"
Cohesion: 0.19
Nodes (3): HealthBody, Sidecar, SidecarOptions

### Community 86 - "Client"
Cohesion: 0.29
Nodes (7): Client, main(), Any, Does she ask well, and — more importantly — does she stop asking? python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Send, answer anything she waits on, and return the completed turn. `pick` is…, section()

### Community 87 - "test_ask.py"
Cohesion: 0.11
Nodes (22): ask_tool(), `ask_user`: the registry entry, and the schema the model has to produce. The…, **The first restriction overshot, and Eyaas caught it on screen.** Asked "can u…, Pydantic hoists nested models into `$defs` and points at them with `$ref`.…, The first version only reached the top level. Pydantic emits a title per class…, The schema change is a capability, not a special case for this tool., **There was a one-question-per-turn cap here, and it was wrong.** Asked to…, `registry.get` is `Tool | None`, and a missing tool here means the import in… (+14 more)

### Community 88 - "test_a_spoken_command_is_no_longer_forced_onto_the_local_model"
Cohesion: 0.20
Nodes (6): The signal is hand-written, so this is what keeps it honest. One deliberate…, The reported failure. "increase the volume" said aloud could only ever reach…, Nobody is waiting on the prosody of "Volume 40% to 55%", but they are waiting…, test_a_spoken_command_is_no_longer_forced_onto_the_local_model(), test_a_spoken_conversational_turn_still_stays_local(), test_every_tool_probe_is_recognised_as_a_command()

### Community 89 - "Indexer"
Cohesion: 0.19
Nodes (9): _digest(), Indexer, IndexStats, Path, Cheap identity: re-reading a 10MB PDF to decide whether to re-read it would…, Walks, reads, embeds and stores — slowly, and out of the way., Hold here while the machine is busy or she is answering., One pass over everything, at the throttled rate. (+1 more)

### Community 90 - "Sidebar.tsx"
Cohesion: 0.13
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.25
Nodes (8): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, Phase 7 — a real, logged-in browser (CDP), Online mode — research(query) over search API, Tool.escalate/Tool.refuse hooks: checkout/banking pages force CONFIRM, password fields refused, _default_browser() detects the real default (Brave) via UserChoice registry rather than assuming Chrome, §11 untrusted_content boundary: fetched text is data, labelled and unfiltered, §11 force_confirm: next tool call after research/browser_read is force-escalated to T2

### Community 92 - "ToolResult"
Cohesion: 0.06
Nodes (50): Browser, Launch, StrEnum, How an entry has to be started. Three sources, three launchers., `ask_user` — put the choice on screen instead of describing it. The mechanism,…, aclose(), browser_click(), browser_fill() (+42 more)

### Community 93 - "free_model"
Cohesion: 0.17
Nodes (12): free_model(), health(), fixture, ModelInfo, A free OpenRouter model, adopted so the router can actually reach it.…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make…, Stage 1 already works this way for privacy, and this sits after it. Overriding… (+4 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): autoprefixer, electron, devDependencies, autoprefixer, electron, react, react-markdown, tailwindcss (+5 more)

### Community 96 - "SettingsStore"
Cohesion: 0.13
Nodes (15): Any, SettingsStore, Fill the overlay from cache. Returns whether it is still fresh. A stale cache…, fixture, parametrize, Durable settings and the v1 -> v2 migration. The migration matters more than…, Values are JSON so a new setting never needs another migration., store() (+7 more)

### Community 97 - "AvailabilityService"
Cohesion: 0.10
Nodes (12): ModelAvailability, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, AvailabilityService, Which models are usable right now. One object answers this for both…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+4 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "FakeLocator"
Cohesion: 0.10
Nodes (10): Locator, FakeLocator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught(), test_commit_wording_in_the_visible_text_is_caught() (+2 more)

### Community 101 - "HealthReport"
Cohesion: 0.16
Nodes (20): dispatch(), HealthReport, _invoke(), BaseModel, Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., Rich health snapshot for the UI (§7.1 ``system.health``, §9.6)., err() (+12 more)

### Community 102 - "ConfirmDialog.tsx"
Cohesion: 0.16
Nodes (10): ConfirmRequest, ImagePreview, leaf(), MovePlan, MovePlanView(), Props, tail(), TIER_LABEL (+2 more)

### Community 103 - "useConversation.ts"
Cohesion: 0.27
Nodes (12): appendToStreaming(), AttachmentStatus, clearStreaming(), finalise(), loadRatings(), ToolCall, toTurns(), Turn (+4 more)

### Community 104 - "package.json"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 105 - "FakePage"
Cohesion: 0.15
Nodes (22): FakePage, MonkeyPatch, The page-level check runs first, and an ordinary-looking "OK" button on a…, Implements exactly the `Page` surface `browser.py` calls., _returning(), test_click_names_what_it_could_not_find(), test_click_risk_still_escalates_on_a_checkout_page(), test_click_runs_the_match_it_finds() (+14 more)

### Community 106 - "spawn"
Cohesion: 0.13
Nodes (11): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, Deliver a message with no preceding question. Called by…, Collect what `send()` started. None when memory is off or it failed. Retrieval…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, Any, Task (+3 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "_start_conversation"
Cohesion: 0.08
Nodes (27): BaseSettings, _default_data_dir(), Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly., Where her database, models and logs live. **Beside the repo in development, in… (+19 more)

### Community 110 - "HistoryPanel.tsx"
Cohesion: 0.24
Nodes (7): clockTime(), dayGroup(), HistoryPanel(), label(), Row(), RowProps, session()

### Community 111 - "CLAUDE.md — ARIA Project Instructions (Claude Code-facing)"
Cohesion: 0.22
Nodes (9): AGENTS.md — ARIA Project Instructions (Codex-facing), CLAUDE.md — ARIA Project Instructions (Claude Code-facing), graphify-out/ knowledge graph, Rule 2: never load a second model onto the GPU (6GB VRAM ceiling), Rule 10: do not refactor prior phases unless the current phase says to, Rule 3: never add torch as a dependency, Rule 7: full type hints, pydantic models, async by default, Rule 6: all tool calls logged to tool_log with args and result (+1 more)

### Community 112 - "Router — local vs cloud, then which provider"
Cohesion: 0.20
Nodes (10): Health monitoring and degradation warnings, Local by default, cloud opt-in per turn, num_ctx capped at 8192, Offline is a first-class path, not an error path, Phase 0 — Foundation, Phase 6 — Agent loop + cloud routing, providers/base.py LLMProvider interface, Router — local vs cloud, then which provider (+2 more)

### Community 113 - "gate_affect.py"
Cohesion: 0.33
Nodes (9): main(), _mechanism_checks(), _ok(), Row, §9 Phase 8's affect-model acceptance gate. the same question at a 2am-shaped…, Section 1: pure functions, no sidecar needed. Mirrors `test_affect.py` but as a…, _read_affect_row(), _restore_affect() (+1 more)

### Community 114 - "Retriever"
Cohesion: 0.16
Nodes (9): Task, Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache., Cancel any embed still running past its deadline. Without this, shutting down… (+1 more)

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "ProviderUnavailable"
Cohesion: 0.07
Nodes (31): HTTPError, concrete_tokens(), main(), novel_tokens(), Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+23 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 121 - "Question"
Cohesion: 0.15
Nodes (16): normalise(), Option, Pending, BaseModel, Question, Trim to the caps and give every question its escape hatch. Done here rather…, Broadcast, then wait. Never raises for an ordinary outcome., One answer the user can pick. (+8 more)

### Community 122 - "SettingsPanel.tsx"
Cohesion: 0.25
Nodes (7): BrowserState, KEY_HELP, KEY_LABEL, OnlineState, RowProps, SEARCH_KEYS, SettingsPanel()

### Community 123 - "preload.ts"
Cohesion: 0.25
Nodes (6): api, AriaApi, BrainStatus, LogLine, SidecarEvent, Unsubscribe

### Community 124 - "Client"
Cohesion: 0.22
Nodes (9): Client, main(), Any, ConversationMode, Do the six modes actually behave differently? Live, against a real sidecar.…, Send, then wait for this turn's own completion., **One reader task, everything else off a queue.** The first version called…, report() (+1 more)

### Community 125 - "make_tray_icons.py"
Cohesion: 0.31
Nodes (7): _chunk(), coverage(), main(), png_bytes(), Generate the tray icon PNGs embedded in electron/tray.ts. Electron's…, Fraction of one pixel covered by the circle, by supersampling., An 8-bit RGBA PNG of a filled circle on transparency.

### Community 127 - "_repeated_failures"
Cohesion: 0.32
Nodes (8): Two or more failed tool calls in this session, recently — 'repeated', not 'a…, _repeated_failures(), _log_failure(), Connection, _seed_session(), test_a_failure_outside_the_recent_window_does_not_count(), test_refresh_loads_updates_and_saves_in_one_call(), test_repeated_failures_reads_recent_tool_log()

### Community 129 - "ToolsPanel.tsx"
Cohesion: 0.40
Nodes (3): TIER_LABEL, TIER_STYLE, ToolSummary

### Community 130 - "Phase 8 — moods, procedural learning, proactivity, voice polish"
Cohesion: 0.29
Nodes (7): AffectState (warmth/energy/playfulness/concern), Nothing turned a yes/no reply into procedures.confirm/discard, resolved via _resolve_procedure_reply, record_new_offers() was dead code; procedural learning never actually detected offers in production, Phase 8 — moods, procedural learning, proactivity, voice polish, Proactivity scheduler (tick/triggers), Procedural learning (procedures table, detect/offer/confirm), Rule 4: every tool goes through the registry with an explicit permission tier

### Community 131 - "Query: QA assessment against BUILD_SPEC"
Cohesion: 0.15
Nodes (13): ARIA (local-first Windows AI assistant), Electron UI (renderer), QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+5 more)

### Community 132 - "Phase 2 stage 3 — hands free (wake word, VAD, endpointing)"
Cohesion: 0.33
Nodes (7): Barge-in never worked: AssistantState.SPEAKING was written nowhere in the sidecar, Phase 2 stage 1 — she speaks (kokoro-onnx TTS), Phase 2 stage 3 — hands free (wake word, VAD, endpointing), Barge-in: duck audio to 20% first, decide (stop/resume) after transcription, Fuzzy first-word name matching plus ARMED listener state for 'aria', src/overlay/ScreenRim.tsx — screen overlay, Voice pipeline (wake word, VAD, STT, TTS)

### Community 134 - "MemoryPanel.test.tsx"
Cohesion: 0.43
Nodes (4): defaults(), episode(), fact(), stats()

### Community 135 - "Orb.tsx"
Cohesion: 0.33
Nodes (6): BREATH, HUE, Orb(), ORB_LAYOUT_ID, OrbProps, SPINS

### Community 136 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, sidecar, test, typecheck

### Community 137 - "core/router.py — model Router"
Cohesion: 0.33
Nodes (6): Model catalog discovery is a filtering problem, not a fetching one, routing_log table + thumbs rating implements §9.7 route auditing, _TOOL_SHAPED narrows which spoken turns route by bias vs stay local/fast, Per-model tool scoreboard: run-to-run spread exceeds inter-model gaps; TOOL_SCORE_MARGIN band added, TTFT does not scale with conversation length once KV cache prefix is byte-identical, core/router.py — model Router

### Community 138 - "tray.ts"
Cohesion: 0.21
Nodes (9): BrainStatus, createTray(), ICON_PNG, STATUS_LABEL, statusIcon(), TrayCallbacks, TrayHandle, icons() (+1 more)

### Community 139 - "useAskQuestion.ts"
Cohesion: 0.33
Nodes (5): AskedQuestion, GivenAnswer, PendingAsk, QuestionOption, useAskQuestion

### Community 141 - "probes.py"
Cohesion: 0.07
Nodes (44): Check, Answered something that has no answer, or claimed an action it cannot perform.…, admits_ignorance(), answers_flatly(), claimed_action(), contains(), contains_any(), denies_capability() (+36 more)

### Community 142 - "gate_agent.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 6's agent loop, against the running sidecar. "find <scratch file>,…

### Community 143 - "WebSearch"
Cohesion: 0.23
Nodes (8): Any, Response, RuntimeError, Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix., No usable search key, or the provider refused. Carries the fix., SearchUnavailable, WebSearch

### Community 145 - "MemoryPanel.tsx"
Cohesion: 0.53
Nodes (5): confidenceStyle(), FactRow(), MemoryPanel(), summarise(), whenever()

### Community 146 - "She holds a conversation now (2026-08-07)"
Cohesion: 0.40
Nodes (5): Interrupting her, and the bug I reported as passing, Latency, measured and cut (2026-08-07), She could not hear her own name (2026-08-07), She holds a conversation now (2026-08-07), Two silence thresholds, not one

### Community 147 - "Measuring answer quality"
Cohesion: 0.40
Nodes (5): Measured baseline (2026-08-06, 117 probes), Measuring answer quality, She has a clock, and "no tool" is not "offline", The battery picked the wrong model; transcripts caught it, Writing probes: the checks lie before the model does

### Community 148 - "Smart mode: it was the tool, and then it was the router (2026-08-12)"
Cohesion: 0.40
Nodes (5): Routing is recorded now, and rateable (§9.7), Smart mode: it was the tool, and then it was the router (2026-08-12), The first per-model tool scoreboard — and what one run of it was worth, Two things that made the gates unrunnable, both found by running them, Wrapped argument docs were being truncated for the model

### Community 149 - "_escalate_current_page"
Cohesion: 0.25
Nodes (8): Page, The URL check catches the common case; a card-number field on an unlisted…, test_a_generic_domain_can_still_be_caught_by_its_dom(), test_no_checkout_fields_means_no_dom_match(), _dom_confirms_checkout(), _escalate_current_page(), A light scan, not a crawl: does the page carry a payment field? Checked in…, §11's checkout gate for the tools with no URL argument of their own —…

### Community 150 - "is_casual"
Cohesion: 0.50
Nodes (5): is_casual(), A rough stand-in for BUILD_SPEC's own undefined `conversation_is_casual` —…, parametrize, test_short_conversational_messages_are_casual(), test_task_shaped_messages_are_not_casual()

### Community 151 - "App.tsx"
Cohesion: 0.40
Nodes (3): drag, noDrag, Overlay

### Community 152 - "ModelPicker.test.tsx"
Cohesion: 0.60
Nodes (3): entry(), model(), models()

### Community 153 - "ToolCallCard.tsx"
Cohesion: 0.43
Nodes (4): formatDuration(), inline(), readable(), ToolCallCard()

### Community 154 - "VoiceAura.tsx"
Cohesion: 0.40
Nodes (3): AuraMode, HUE, Props

### Community 155 - "ScreenRim.tsx"
Cohesion: 0.40
Nodes (3): HUE, Props, RimMode

### Community 156 - "Phase 8 — she has moods, and does not go quiet forever (2026-08-14)"
Cohesion: 0.50
Nodes (4): Mutation-checked, both against the plan's own named targets, Phase 8 — she has moods, and does not go quiet forever (2026-08-14), The live gate, run twice, both honest, Two real bugs, both found by running the thing, not by reading the diff

### Community 157 - "Phase 2 — Voice"
Cohesion: 0.50
Nodes (4): Barge-in — interrupt playback on speech, Phase 2 — Voice, Sentence-level TTS streaming, openWakeWord hey_jarvis wake detection

### Community 159 - "gate_browser.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 7's browser half, against a real, CDP-attached Chrome. "open…

### Community 160 - "gate_memory.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 5's acceptance gate, against the running sidecar. "I usually work on…

### Community 161 - "tokens.test.ts"
Cohesion: 0.33
Nodes (3): contrast(), luminance(), SURFACE

### Community 163 - "Markdown.tsx"
Cohesion: 0.29
Nodes (3): DETECTABLE, LABELS, Markdown

### Community 165 - "useAudio.ts"
Cohesion: 0.67
Nodes (3): AudioChunk, decodePcm16(), useAudio

### Community 166 - "useMic.ts"
Cohesion: 0.67
Nodes (3): encodePcm16(), Recording, useMic

### Community 167 - "Online mode: she can reach the web now (2026-08-13)"
Cohesion: 0.67
Nodes (3): §11: fetched text is data, and is labelled as such, Online mode: she can reach the web now (2026-08-13), The gate — PARTIAL, then PASSED once a key existed

### Community 168 - "Persona boundaries — capacity to push back"
Cohesion: 0.67
Nodes (3): Persona boundaries — capacity to push back, Character, not sycophancy, aria.yaml persona configuration

### Community 169 - "Nightly reflection prompt (reflect.j2)"
Cohesion: 0.67
Nodes (3): Fact merge and supersession logic, Phase 5 — Memory, Nightly reflection prompt (reflect.j2)

### Community 170 - "Tool.preview channel: one confirmation shows a whole batch plan (organize_folder)"
Cohesion: 0.67
Nodes (3): Phase 4 closed — organize_folder / undo_organize, Phase 6 finished — capture_screen + cloud vision, Tool.preview channel: one confirmation shows a whole batch plan (organize_folder)

### Community 172 - "ComposerBar.tsx"
Cohesion: 0.67
Nodes (3): basename(), ComposerBar(), Props

### Community 191 - "db.py"
Cohesion: 0.18
Nodes (11): _apply_sql(), connect(), migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Run ``fn`` against the connection off the event loop, serialised., Open the database with sqlite-vec loaded and the required pragmas set. (+3 more)

### Community 195 - "Source"
Cohesion: 0.18
Nodes (12): Fetch and strip anything that arrived without text. Concurrently, and failures…, One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, A model that has just read 6,000 characters of someone else's writing has…, Returns real, correct URLs" is the acceptance line, and only `summary` reaches…, test_a_source_is_truncated_rather_than_dropped(), test_every_source_carries_its_url() (+4 more)

### Community 197 - "files_rename"
Cohesion: 0.20
Nodes (12): files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, Show it in Explorer. The escape hatch for anything this panel does not do., Rename in place, from a click in the panel. Reuses `tools/files.py`'s own…, **To the Recycle Bin, not gone.** This is the one place in the codebase that… (+4 more)

### Community 202 - "parse_openrouter"
Cohesion: 0.07
Nodes (27): _openrouter_class(), parse_openrouter(), Prefer the number; fall back to what the vendor called it. The other two…, Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, `openrouter/free` forwards to whichever free model it likes. Measuring it would…, An expired id 404s mid-turn, which reads as ARIA being broken., Fail towards keeping it: a bad date string is not evidence of anything., The rule the whole discovery module is built on. `Cost.FREE` is the one… (+19 more)

### Community 203 - "_Reader"
Cohesion: 0.20
Nodes (4): AsyncClient, HTMLParser, Strip a page to its readable text. Not readability, not an article extractor,…, _Reader

### Community 209 - "ask_user"
Cohesion: 0.15
Nodes (15): a_question(), broker(), fixture, MonkeyPatch, `summary` is the only field the model sees., **`ok=False` would make her apologise for his silence.** Nothing went wrong; he…, Unreachable in the app, but a tool that raises fails the whole turn and this…, A stand-in for `runtime.questions`, recording what it was asked. (+7 more)

### Community 211 - "test_browser.py"
Cohesion: 0.13
Nodes (23): Exception, parametrize, _raising(), Browser control: the checkout/banking hard block, password refusal, and element…, No page has loaded yet at this point — only the URL being navigated *to* is…, `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, §11: the *next* tool call after this one is force-escalated by the agent loop —…, test_known_checkout_and_banking_urls_are_recognised() (+15 more)

### Community 212 - "questions.py"
Cohesion: 0.26
Nodes (11): Asked, Asking the user something and waiting for the answer. Eyaas: *"if u are gonna…, The result of one `ask_user` call., The one-line-per-question summary that goes back to the model. **`summary` is…, render(), a_question(), `summary` is the only field the model ever sees, so it has to carry the answers…, Otherwise the next step asks the same thing, which is how a question becomes a… (+3 more)

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.29
Nodes (5): DURATION, EASE, SPRING, stagger, TWEEN

### Community 244 - "clipboard.py"
Cohesion: 0.24
Nodes (10): tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, The clipboard's text, or None when it holds something else. An image, a file…, Replace the clipboard's contents. Public for the same reason as `read_text`…, Read the clipboard's text., read_clipboard(), read_text() (+2 more)

### Community 245 - "test_research.py"
Cohesion: 0.27
Nodes (9): Readable text from a page, truncated on a word boundary., to_text(), `research(query)`, the untrusted-content boundary, and the online gate. Two…, The normal case on the open web, and returning nothing would read as "research…, Stronger than asking it not to use one: §7.2's own reasoning for hiding DANGER,…, test_extraction_is_capped(), test_malformed_html_still_yields_something(), test_scripts_and_navigation_are_dropped() (+1 more)

### Community 246 - "conversation.py"
Cohesion: 0.06
Nodes (40): ConversationHistory, ProviderRegistry, BaseModel, datetime, StoredMessage, Turn orchestration (BUILD_SPEC §9 Phase 1). One turn: persist the user message,…, `chat.send` result (§7.1)., Providers keyed by name, so the service can follow the router's choice. (+32 more)

### Community 247 - "WakeWord"
Cohesion: 0.12
Nodes (7): Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, ndarray, Protocol, What the listener depends on, so it never imports openwakeword., WakeWord

### Community 248 - "catalog.py"
Cohesion: 0.05
Nodes (45): ProviderName, The model catalog — one structure behind the picker, the tooltips, and routing.…, Replace what the providers said they offer. A curated id always wins: `gpt-5`…, Drop an adoption — used when a free model expires or disappears., Why a model can or cannot be used, in words the picker can show., set_discovered(), unadopt(), _verdict() (+37 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 255 - "rpc.ts"
Cohesion: 0.29
Nodes (5): Pending, RpcEnvelope, RpcError, RpcErrorShape, RpcNotification

### Community 256 - "._resolve_procedure_reply"
Cohesion: 0.33
Nodes (5): _parse_yes_no(), True/False for a clearly affirmative/negative one-line reply, else None — an…, The other half of "offer once, wait for a yes" (Part 2). Returns a completed…, parametrize, test_parse_yes_no()

### Community 257 - "database"
Cohesion: 0.29
Nodes (9): conn(), database(), db_path(), Connection, fixture, Path, Shared fixtures. Every test gets a throwaway data dir — never the real data/., A migrated database on a temp path. (+1 more)

### Community 259 - "pcm16_to_float32"
Cohesion: 0.50
Nodes (4): pcm16_to_float32(), Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., One 80ms frame of base64 int16 PCM from the open microphone. Sent as a…, voice_frame()

### Community 260 - "table_names"
Cohesion: 0.25
Nodes (8): Every table in the database, including vec0 virtual tables., table_names(), Connection, Path, The realistic case: a Phase 1 database already holding a conversation., test_fresh_database_lands_on_the_current_version(), test_selected_model_is_seeded_to_smart(), test_upgrades_a_v1_database_without_losing_messages()

### Community 261 - "parse_gemini"
Cohesion: 0.25
Nodes (8): _gemini_class(), _gemini_is_chat(), _gemini_is_duplicate(), parse_gemini(), A pinned or preview alias of something already listed plainly. Only when the…, Chat models from a `GET /v1beta/models` body., A provider changing shape should empty the discovered list, not take the picker…, test_a_malformed_payload_yields_nothing_rather_than_raising()

### Community 262 - "Any"
Cohesion: 0.25
Nodes (8): _openrouter_benchmark(), _openrouter_expired(), _openrouter_is_free(), Any, date, Free on **both** sides of the meter. `pricing.prompt == "0"` alone would admit…, Artificial Analysis' published intelligence index, if OpenRouter has one. A…, Free models come and go, and OpenRouter says when. An expired id 404s mid-turn,…

### Community 263 - "ollama_supervisor.py"
Cohesion: 0.29
Nodes (6): find_ollama(), Path, Keep Ollama running, and notice when it comes back. Eyaas: *"sometimes when…, The `ollama` executable, or None if it is not installed. PATH first, because…, Start `ollama serve` as its own process, with no console window. Detached on…, _spawn_detached()

### Community 265 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 272 - "online"
Cohesion: 0.25
Nodes (8): online(), fixture, MonkeyPatch, The whole point of `SearchUnavailable` carrying a message., Online mode on, with a stubbed search behind it., Belt to `_tool_schemas`' braces. `allow_danger_tools` was dead for a whole…, test_it_refuses_when_online_mode_is_off(), test_no_key_says_which_key_and_where()

### Community 273 - "ModelListing"
Cohesion: 0.29
Nodes (7): ModelListing, BaseModel, `models.list` result., models_list(), models_refresh(), Catalog plus live availability. Drives the picker and its tooltips. Re-probes…, Ask the cloud providers what they offer today, and re-list. Deliberately…

### Community 276 - "_escalate_click_risk"
Cohesion: 0.29
Nodes (7): The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, test_click_risk_escalates_on_the_elements_own_wording(), test_click_risk_is_quiet_for_an_ordinary_click(), test_click_risk_is_quiet_when_nothing_resolved(), _escalate_click_risk(), `browser_click`'s escalate hook: the checkout/banking page check, plus whether…

### Community 277 - "_locate"
Cohesion: 0.33
Nodes (6): Refusing to act on an ambiguous-but-real description is worse than picking the…, test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), test_locate_takes_the_first_of_several_ambiguous_matches(), _locate(), Best-effort resolution of a natural-language description, tried in the order a…

## Knowledge Gaps
- **339 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+334 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **70 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConversationService` connect `ConversationService` to `._resolve_procedure_reply`, `test_permissions.py`, `test_tts.py`, `Database`, `ModelInfo`, `test_modes.py`, `ConversationStore`, `Role`, `HealthTracker`, `ChatMessage`, `OpenEngine`, `RoutingLog`, `Router`, `Tier`, `EpisodicMemory`, `listener.py`, `Listener`, `ToolContext`, `EventBus`, `StreamDelta`, `LoopState`, `Event`, `test_conversation.py`, `main.py`, `SpeechStream`, `test_ask.py`, `spawn`, `_start_conversation`, `ProviderUnavailable`, `conversation.py`, `WakeWord`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `database`, `table_names`, `test_reflection.py`, `test_tts.py`, `test_proactivity.py`, `finder.py`, `indexer.py`, `ConversationStore`, `Role`, `SemanticMemory`, `OpenEngine`, `RoutingLog`, `semantic.py`, `test_retrieval.py`, `EpisodicMemory`, `test_db.py`, `test_episodic.py`, `ConversationService`, `test_conversation.py`, `main.py`, `db.py`, `SpeechStream`, `test_affect.py`, `Episode`, `affect.py`, `Indexer`, `SettingsStore`, `AvailabilityService`, `AffectState`, `ProviderUnavailable`, `conversation.py`, `_repeated_failures`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `_Semantic`, `finder.py`, `apps.py`, `test_screen.py`, `test_organize.py`, `Tier`, `ConversationService`, `SpeechStream`, `test_tools.py`, `StubSearch`, `ask_user`, `registry.py`, `test_browser.py`, `system.py`, `test_ask.py`, `ToolResult`, `FakeLocator`, `FakePage`, `clipboard.py`, `test_research.py`, `conversation.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 51 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._