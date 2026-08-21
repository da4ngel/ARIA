# Graph Report - ARIA  (2026-08-21)

## Corpus Check
- 261 files · ~380,027 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 5394 nodes · 12448 edges · 293 communities (224 shown, 69 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1083 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8261a279`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_permissions.py
- test_listener.py
- main.ts
- catalog.py
- test_rpc.py
- test_reflection.py
- test_attachments.py
- test_tts.py
- Database
- test_scheduler.py
- test_proactivity.py
- test_discovery.py
- KokoroTTS
- clear_adopted
- finder.py
- apps.py
- Indexer
- SileroVAD
- conversation.py
- ConversationStore
- SettingsStore
- HealthTracker
- SemanticMemory
- test_screen.py
- test_study_modes.py
- test_ollama_supervisor.py
- test_router.py
- test_extract.py
- handlers.py
- test_study_tools.py
- RoutingLog
- test_organize.py
- Router
- FakeProvider
- test_retrieval.py
- Tool
- GenerationOptions
- strip_wake_word
- Listener
- test_db.py
- AdoptionService
- test_focus.py
- proactivity.py
- ARIA — Project Instructions
- files.py
- ConversationService
- test_episodic.py
- watched_project_candidate
- test_questions.py
- test_curriculum.py
- eval_quality.py
- test_text.py
- settings_set_key
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
- ChatMessage
- EpisodicMemory
- test_tools.py
- test_vectors.py
- test_context.py
- test_browser_setup.py
- ProviderUnavailable
- test_affect.py
- VoiceActivity
- Retriever
- extract.py
- OllamaEmbeddings
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- _cloud_model
- test_adoption.py
- memory/study.py
- discovery.py
- StudyState
- FilesPanel.tsx
- Sidecar
- Client
- test_ask.py
- Client
- Fact
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- ToolContext
- attachments.py
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- EventBus
- Runtime
- PermissionEngine
- FakePage
- FilesPanel.test.tsx
- HealthReport
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- MonkeyPatch
- gate_permission_modes.py
- render
- gate_organize.py
- system.py
- HistoryPanel.tsx
- CLAUDE.md — ARIA Project Instructions (Claude Code-facing)
- Router — local vs cloud, then which provider
- gate_affect.py
- ProactivityScheduler
- AffectState
- usePermissionMode.ts
- OllamaProvider
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- gate_research.py
- MachineContext
- SettingsPanel.tsx
- preload.ts
- Client
- make_tray_icons.py
- PermissionModeChip.tsx
- _repeated_failures
- ToolsPanel.tsx
- Phase 8 — moods, procedural learning, proactivity, voice polish
- Electron UI (renderer)
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
- test_browser.py
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
- get
- electron-vite
- framer-motion
- jsdom
- WakeWord
- remark-gfm
- files_browse
- @testing-library/react
- @types/node
- @types/react
- @types/react-dom
- test_openrouter.py
- test_research.py
- vite
- @vitejs/plugin-react
- vitest
- sidecar/__init__.py
- persona/__init__.py
- migrate
- test_the_gate_is_the_same_probes_the_scripts_use
- retrieved_block
- PersonaLevel
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
- parametrize
- _json_type
- ProviderRegistry
- broker
- OpenRouterProvider
- tokens.js
- rpc.ts
- gate_tool_selection.py
- Question
- useConversation.test.ts
- pcm16_to_float32
- RateLimitState
- free_model
- database
- _looks_like_a_commit_action
- _escalate_click_risk
- _reset_connection
- eval/__init__.py
- postcss
- react-dom
- rehype-highlight
- @types/ws
- study_begin
- to_pcm16
- _drain_windows
- electron-builder
- StudyPanel.test.tsx
- assemble
- choose_model
- StudyPanel.tsx
- zustand
- build_prompt
- useStudy.ts
- test_the_tools_are_registered
- test_a_short_code_request_is_not_answered_locally_to_save_time
- test_ordinary_questions_do_not_get_the_expensive_tier
- test_a_spoken_turn_still_stays_local
- test_a_spoken_command_is_no_longer_forced_onto_the_local_model
- test_a_spoken_conversational_turn_still_stays_local
- test_a_command_is_not_slowed_down_for_a_difference_that_is_noise
- test_an_ordinary_question_still_takes_the_fast_class

## God Nodes (most connected - your core abstractions)
1. `Database` - 348 edges
2. `ConversationStore` - 168 edges
3. `ConversationService` - 122 edges
4. `HealthTracker` - 106 edges
5. `ToolContext` - 102 edges
6. `ChatMessage` - 94 edges
7. `SemanticMemory` - 92 edges
8. `ToolResult` - 90 edges
9. `GenerationOptions` - 71 edges
10. `Router` - 63 edges

## Surprising Connections (you probably didn't know these)
- `AGENTS.md — ARIA Project Instructions (Codex-facing)` --semantically_similar_to--> `CLAUDE.md — ARIA Project Instructions (Claude Code-facing)`  [INFERRED] [semantically similar]
  AGENTS.md → CLAUDE.md
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
- **ARIA's layered safety/confirmation system** — permission_engine, rule_destructive_confirmation, rationale_untrusted_source_escalation, rationale_checkout_escalation, rationale_confirm_timeout_denied [INFERRED 0.85]
- **Memory repair: six-cause conversation-forgetting investigation and fix** — bug_she_forgot_conversation, rationale_memory_high_water_mark, rationale_salience_computed_not_asked, memory_system, phase_5_memory [EXTRACTED 1.00]
- **Phase 6 agent loop design: step-aware routing, privacy stickiness, escalation** — agent_loop, rationale_sticky_local, rationale_untrusted_source_escalation, phase_6_agent_loop, router_core [EXTRACTED 1.00]
- **KV-cache latency discipline across prompt assembly** — build_spec_stable_prefix_ordering, build_spec_prefill_cost [INFERRED 0.85]

## Communities (293 total, 69 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (106): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+98 more)

### Community 1 - "test_listener.py"
Cohesion: 0.06
Nodes (67): drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on… (+59 more)

### Community 2 - "main.ts"
Cohesion: 0.15
Nodes (22): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+14 more)

### Community 3 - "catalog.py"
Cohesion: 0.06
Nodes (46): adopted(), Cost, default_local(), discovered(), local_models(), ModelAvailability, ModelListing, ProviderName (+38 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.10
Nodes (47): Constant-time comparison of a presented Bearer token., token_matches(), method_names(), _auth(), _call(), parametrize, The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The id is reserved, not written — so the list stays empty. (+39 more)

### Community 5 - "test_reflection.py"
Cohesion: 0.13
Nodes (27): _extract_json(), Any, Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio, parametrize, The nightly §8.3 pass. Two things are load-bearing and both are about a local…, A key can be present while the account is dead, which is exactly this machine's…, The gate's fourth line, from the reflection side. (+19 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.09
Nodes (39): One attachment, understood. Never raises., The block that goes into the prompt. **Fenced as untrusted content**, exactly…, read_one(), render(), MonkeyPatch, Path, Files the user hands her. Eyaas: *"i should be also be able to file uploads…, There is no local vision model (rule 2), so no key is a real state with an… (+31 more)

### Community 7 - "test_tts.py"
Cohesion: 0.05
Nodes (61): Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Say a reply aloud, on request. False when there is no voice engine. The other…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., SpeechStream, RuntimeError, Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is… (+53 more)

### Community 8 - "Database"
Cohesion: 0.08
Nodes (50): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+42 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.17
Nodes (30): You have not been around in a while" — at most once, and only when that is…, scheduled_check_in_candidate(), _candidate(), FakeStore, Connection, datetime, The proactivity engine (BUILD_SPEC §9 Phase 8). `ProactivityScheduler.tick()`…, Stands in for `find_candidates`/`self_check`/`deliver`. (+22 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.11
Nodes (29): parse_openai(), Chat models from a `GET /v1/models` body., gemini_ids(), _load(), openai_ids(), Any, fixture, parametrize (+21 more)

### Community 12 - "KokoroTTS"
Cohesion: 0.05
Nodes (46): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+38 more)

### Community 13 - "clear_adopted"
Cohesion: 0.10
Nodes (22): adopt(), all_models(), clear_adopted(), Record a model as measured-and-passed, making it routable. Curated ids still…, Tests only. The overlay is process-global, like `_DISCOVERED`., Everything selectable: measured first, then adopted, then found., _clean_overlay(), fixture (+14 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (69): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The… (+61 more)

### Community 15 - "apps.py"
Cohesion: 0.04
Nodes (79): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, `normalise("notepad++")` is `"notepad"`, which scored an exact 1.00 against the…, Asking for "notepad" may well mean Notepad++; the ranking can decide. Asking…, Only `+` and `#` name a different product. The 7-Zip cases depend on everything…, test_a_shared_symbol_still_matches(), test_hyphens_and_dots_are_still_noise(), test_punctuation_that_names_a_different_product_is_not_folded_away() (+71 more)

### Community 16 - "Indexer"
Cohesion: 0.08
Nodes (33): chunk(), _digest(), Indexer, IndexStats, _pack(), Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, Whether this file is worth reading at all. (+25 more)

### Community 17 - "SileroVAD"
Cohesion: 0.06
Nodes (28): main(), Download the wake word weights into data/models/openwakeword. python…, frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python… (+20 more)

### Community 18 - "conversation.py"
Cohesion: 0.04
Nodes (74): clean_title(), ConversationMode, _mode_block(), mode_done_when(), mode_label(), _persona(), datetime, Prompt assembly and the rolling context window (BUILD_SPEC §8.2, §9 Phase 1).… (+66 more)

### Community 19 - "ConversationStore"
Cohesion: 0.07
Nodes (42): The message store, for callers that need to resolve a session id., ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, When anything was last said, in any session. The whole precondition for §9's…, A fresh id with no row behind it yet. `ensure_session` creates a row for any id… (+34 more)

### Community 20 - "SettingsStore"
Cohesion: 0.10
Nodes (20): Any, SettingsStore, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Fill the overlay from cache. Returns whether it is still fresh. A stale cache…, Connection, fixture, parametrize (+12 more)

### Community 21 - "HealthTracker"
Cohesion: 0.08
Nodes (28): HealthTracker, ModelHealth, BaseModel, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture, Observed latency and the circuit breaker. A 429 is treated as a routing input… (+20 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.07
Nodes (49): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:… (+41 more)

### Community 23 - "test_screen.py"
Cohesion: 0.09
Nodes (47): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+39 more)

### Community 24 - "test_study_modes.py"
Cohesion: 0.06
Nodes (55): Set how this study session runs. LEARN is stored as an absence., parse(), policy_for(), StrEnum, How a study session is being run right now, as opposed to what it is about.…, Never raises, and `None` means Learn — `modes.policy_for`'s contract., A sub-mode name off the wire, or `None` for anything unrecognised. Lenient…, The six. `LEARN` is the default and behaves exactly as Study did before sub-… (+47 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.06
Nodes (45): find_ollama(), OllamaSupervisor, Path, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was…, The `ollama` executable, or None if it is not installed. PATH first, because… (+37 more)

### Community 26 - "test_router.py"
Cohesion: 0.11
Nodes (33): is_local(), RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort., Observed latency overrides the seeded table as turns land., The router must always answer. A turn with no candidates is a crash., Local models are multi-GB downloads that may not have finished. (+25 more)

### Community 27 - "test_extract.py"
Cohesion: 0.12
Nodes (32): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+24 more)

### Community 28 - "handlers.py"
Cohesion: 0.05
Nodes (95): build_health(), chat_cancel(), chat_delete(), chat_history(), chat_new(), chat_rename(), chat_send(), chat_sessions() (+87 more)

### Community 29 - "test_study_tools.py"
Cohesion: 0.13
Nodes (37): _mapped(), Any, asyncio, quiz(), `study_begin` and `study_check`, and the state she is handed without asking.…, A `list[QuizQuestion]` that came out as `{"type": "object"}` with no properties…, **The reason `QuizQuestion` is not `core.questions.Question`.** The broker…, Only `summary` reaches the model (§7.2), so the grade has to be in it — and the… (+29 more)

### Community 30 - "RoutingLog"
Cohesion: 0.07
Nodes (33): ModelVerdict, BaseModel, What the router decided, and what the user made of it (§9.7). §9.7's closing…, Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Per-model tallies. The dataset §9.7 wants, as far as it has grown., One turn's routing decision, as it is written down. (+25 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (71): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+63 more)

### Community 32 - "Router"
Cohesion: 0.12
Nodes (20): is_tool_shaped(), BaseModel, ModelInfo, A request to act on the machine rather than to talk about something., Chooses a model for a turn., Pick a model. `selected` is the user's choice — a model id, or "smart" to…, `bias` overrides the instance setting for this call only. **A parameter, not a…, Cloud unless the turn is trivial. The default. `_DEEP_VERBS` is checked here… (+12 more)

### Community 33 - "FakeProvider"
Cohesion: 0.07
Nodes (49): chat_mode(), Read or set a conversation's mode. Omit `mode` to read. The read-or-write shape…, FakeProvider, make_service(), _proactivity_service(), anyio, Connection, fixture (+41 more)

### Community 34 - "test_retrieval.py"
Cohesion: 0.13
Nodes (30): anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice., `_build_context` runs once per attempt inside the failover loop, so without…, Below MIN_SCORE nothing is injected, so the prompt stays byte-identical to a…, The KV-cache invariant, asserted from the retrieval side too. (+22 more)

### Community 35 - "Tool"
Cohesion: 0.08
Nodes (25): EscalateFn, PreviewFn, RefuseFn, It is a strong constraint — it overrides the router — so it should be…, test_no_registered_tool_documents_an_argument_it_then_truncates(), test_nothing_else_claims_local_only(), paths_in(), Any (+17 more)

### Community 36 - "GenerationOptions"
Cohesion: 0.05
Nodes (68): `chat.send` result (§7.1)., TurnStarted, build_prompt(), choose_model(), CurriculumBuilder, CurriculumOutput, CurriculumReport, ExtractedConcept (+60 more)

### Community 37 - "strip_wake_word"
Cohesion: 0.14
Nodes (16): is_stop_word(), _near_the_name(), Is this whole utterance just a request to stop talking?, Is this first word a plausible mishearing of her name? `base.en` on a single…, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said. (+8 more)

### Community 38 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 39 - "test_db.py"
Cohesion: 0.17
Nodes (18): Every table in the database, including vec0 virtual tables., table_names(), Connection, Path, Phase 0 acceptance gate: the database is created and migrated from schema.sql., The schema declares float[768]; prove it round-trips., test_affect_state_singleton_is_seeded(), test_all_schema_tables_exist() (+10 more)

### Community 40 - "AdoptionService"
Cohesion: 0.08
Nodes (25): datetime, Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days., AdoptionService, AdoptionState, _probes_by_id(), Any, BaseModel (+17 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "proactivity.py"
Cohesion: 0.11
Nodes (21): Candidate, default_candidates(), default_self_check(), idle_intention_candidate(), is_stated_intention(), procedure_offer_candidate(), datetime, Unprompted messages — rate-limited, focus-aware, self-checked (BUILD_SPEC §9… (+13 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "files.py"
Cohesion: 0.07
Nodes (48): Path, Overwriting is a different destructive act from moving, and the user approved a…, `read_file` did a plain UTF-8 read of whatever it was given, so "what does this…, A scanned PDF with no text layer is a normal thing to be handed. Saying so…, OneDrive relocates Documents and Desktop by default, so joining onto…, The whole point: when it cannot be done she must say so, not claim it., A folder is a much larger promise than a file, and this tool says file., test_a_missing_file_is_said_plainly() (+40 more)

### Community 45 - "ConversationService"
Cohesion: 0.03
Nodes (50): SessionSummary, ConversationService, Any, ConversationMode, datetime, ModelInfo, RoutingBias, StoredMessage (+42 more)

### Community 46 - "test_episodic.py"
Cohesion: 0.09
Nodes (41): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., _conversation(), _episodic(), anyio, Connection (+33 more)

### Community 47 - "watched_project_candidate"
Cohesion: 0.15
Nodes (19): Path, timedelta, Names of files under `root` modified inside `window`. Bounded, and never raises…, Notice that a watched folder is being worked in right now. Empty by default:…, _recently_changed(), watched_project_candidate(), FakeSettings, Path (+11 more)

### Community 48 - "test_questions.py"
Cohesion: 0.09
Nodes (36): Answer, Asked, QuestionBroker, Asking the user something and waiting for the answer. Eyaas: *"if u are gonna…, What came back for one question., The result of one `ask_user` call., Puts a question on screen and waits for the answer., Resolve a waiting question. False if it already went. (+28 more)

### Community 49 - "test_curriculum.py"
Cohesion: 0.15
Nodes (25): The indexed text of one file, in order, or `""` if it was never indexed. The…, source_text(), _builder(), asyncio, Turning a lecture into a concept map, and surviving what a model returns. The…, A scanned PDF or an image-only deck is a normal thing to be handed, and "no…, A subject with no concepts would render as "0 of 0 covered" forever and win…, `reflection` records why this matters: reporting the model that was *tried*… (+17 more)

### Community 50 - "eval_quality.py"
Cohesion: 0.07
Nodes (41): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+33 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "settings_set_key"
Cohesion: 0.20
Nodes (11): all_status(), CredentialStatus, delete_key(), BaseModel, Safe-to-display description of a stored key., For Settings and `system.health`. Contains no secrets., status(), Which providers are configured. Contains no secrets. (+3 more)

### Community 53 - "LoopState"
Cohesion: 0.11
Nodes (15): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Mark one step as run. `local_only` is unknown, not False, for a tool the…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through… (+7 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "Event"
Cohesion: 0.08
Nodes (25): Any, ListenerState, StrEnum, Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3). The renderer opens the…, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Endpoint (+17 more)

### Community 56 - "Connectivity"
Cohesion: 0.13
Nodes (20): Connectivity, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception, MonkeyPatch (+12 more)

### Community 57 - "test_conversation.py"
Cohesion: 0.06
Nodes (78): A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, _drain(), OpenEngine, parametrize, Path, ToolCall, Turn orchestration, cancellation, persistence and context roll-up. (+70 more)

### Community 58 - "snapshot"
Cohesion: 0.29
Nodes (7): BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM unconditionally.…, §9:943 says "regardless of tool tier" — that only means something if *every*…, test_every_browser_tool_carries_the_checkout_escalation(), test_only_fill_carries_the_password_refusal(), test_tiers_deviate_from_build_specs_blanket_confirm_by_design(), A copy of the registry, for tests that install their own tools. Paired with…, snapshot()

### Community 59 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (27): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+19 more)

### Community 60 - "ARIA Sidecar Runtime Dependencies (requirements.txt)"
Cohesion: 0.07
Nodes (27): ARIA Sidecar Runtime Dependencies (requirements.txt), anthropic==0.39.* (NOT adopted, Anthropic excluded), apscheduler==3.10.* (deferred, Phase 5), fastapi==0.115.*, faster-whisper==1.0.3, httpx==0.27.*, keyring==25.7.* (Windows Credential Manager), kokoro-onnx==0.4.* (+19 more)

### Community 61 - "main.py"
Cohesion: 0.04
Nodes (77): BaseSettings, FastAPI, get, _default_data_dir(), Path, Sidecar configuration. Single source of truth for paths, port, and auth token.…, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch… (+69 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "stable_prefix"
Cohesion: 0.13
Nodes (22): Content identical across turns. Everything here is KV-cached. Changing `level`…, stable_prefix(), ConversationMode, parametrize, The guard above only ever measured NORMAL, and a mode block is part of the…, The property that makes modes free for anyone who never uses them. NORMAL…, Resolved once at import, so the same configuration always yields the same bytes…, `_INSTRUCTION_PRIORITY` exists because "reply with only the number 7" once… (+14 more)

### Community 64 - "ChatMessage"
Cohesion: 0.08
Nodes (25): episode_request(), StoredMessage, Prompt asking the model to compress a whole session into an episode. Distinct…, Drop rows the model should not see back (tool rows arrive in Phase 3)., Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, Prompt asking the model to compress the oldest turns into a note., Prompt asking the model to name a conversation for the history list., split_for_rollup() (+17 more)

### Community 65 - "EpisodicMemory"
Cohesion: 0.08
Nodes (18): Episode, EpisodicMemory, _now(), BaseModel, datetime, Row, StoredMessage, A row from `episodes`, as the panel and retrieval see it. (+10 more)

### Community 66 - "test_tools.py"
Cohesion: 0.03
Nodes (113): app(), _focused(), MonkeyPatch, parametrize, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V… (+105 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "test_context.py"
Cohesion: 0.09
Nodes (28): full(), Machine context: the clock, the model, and what it costs to carry them., CLAUDE.md: keep the pre-conversation budget near 800 tokens **on local**. It…, Roll-up decisions subtract this; if it were uncounted, a conversation could…, The sentence that made her deny a conversation she had just had. "You know…, `recall` is a tool, so the instruction to search only makes sense when tools…, The anti-invention force is what took the 7B from 57% fabrication to 27%.…, `universal_failures` fails *every* probe in *every* category on either of… (+20 more)

### Community 69 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+9 more)

### Community 70 - "ProviderUnavailable"
Cohesion: 0.04
Nodes (53): Which models are usable right now. One object answers this for both…, ProviderRateLimited, ProviderUnavailable, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, One chunk of a streaming response. `text` carries *content only*. Reasoning…, The backend could not be reached — offline, not running, DNS, refused. Distinct…, StreamDelta, CredentialKey (+45 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "VoiceActivity"
Cohesion: 0.15
Nodes (6): ndarray, Protocol, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., VoiceActivity

### Community 73 - "Retriever"
Cohesion: 0.13
Nodes (11): Task, What one turn recalled, plus what it cost., Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache. (+3 more)

### Community 74 - "extract.py"
Cohesion: 0.11
Nodes (24): _extract_bytes(), extract_text(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as… (+16 more)

### Community 75 - "OllamaEmbeddings"
Cohesion: 0.07
Nodes (33): _age_days(), _percentile(), datetime, Retrieval — putting the right memory in front of the model (§9 Phase 5). **The…, 1.0 today, 0.5 after a month, never quite zero., §9 Phase 5: 0.6·cosine + 0.25·recency + 0.15·salience, boosted by access. Two…, What `memory.stats` reports and `gate_memory.py` asserts against., Word overlap in place of cosine. Sub-millisecond, and honest about it. Not a… (+25 more)

### Community 76 - "bridge.d.ts"
Cohesion: 0.08
Nodes (23): AriaApi, AssistantState, BrainStatus, CredentialStatus, LogLine, MemoryEpisode, MemoryFact, MemoryStats (+15 more)

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
Cohesion: 0.10
Nodes (53): ProviderQuotaExhausted, The **account's** allowance is gone, not this model's. A 429 usually means…, by_class(), The router's pool: **measured only** — curated, or adopted after passing. The…, a_model(), Asker, Clock, perfect_reply() (+45 more)

### Community 81 - "memory/study.py"
Cohesion: 0.08
Nodes (50): add_concepts(), concept_by_name(), ensure_subject(), latest_subject_id(), list_subjects(), mark_taught(), _next_level(), _now() (+42 more)

### Community 82 - "discovery.py"
Cohesion: 0.13
Nodes (23): discover_all(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch(), _gemini_class(), _gemini_is_chat(), _gemini_is_duplicate() (+15 more)

### Community 83 - "StudyState"
Cohesion: 0.27
Nodes (6): Concept, Anything that has been taught, whether or not it stuck., What to teach next: the first weak one, else the first untouched one, else…, One node of the map, with whatever mastery it has accumulated., Everything the prompt block and the report are rendered from. Assembled in one…, StudyState

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
Cohesion: 0.06
Nodes (42): Option, One answer the user can pick., a_question(), ask_tool(), broker(), fixture, MonkeyPatch, `ask_user`: the registry entry, and the schema the model has to produce. The… (+34 more)

### Community 88 - "Client"
Cohesion: 0.25
Nodes (10): Client, concepts_in(), main(), Any, Does Study Mode actually teach? Live, against a real sidecar. python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Answer a `question.ask` the way a student would — one pick each. **This gate…, The map and its mastery, read straight from the sidecar's own state. Asserting… (+2 more)

### Community 89 - "Fact"
Cohesion: 0.06
Nodes (24): _now(), Return an existing session id, or create one., Fact, normalise_triple(), _now(), Row, The form that gets embedded and shown in the prompt., Fold a triple to its stored form. The UNIQUE index is on the raw columns, so… (+16 more)

### Community 90 - "Sidebar.tsx"
Cohesion: 0.12
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 92 - "ToolContext"
Cohesion: 0.04
Nodes (84): Browser, Page, The highest tier this policy will show, or None for no tools., Launch, StrEnum, How an entry has to be started. Three sources, three launchers., aclose(), browser_click() (+76 more)

### Community 93 - "attachments.py"
Cohesion: 0.14
Nodes (20): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no…, Every attachment on one message, in the order they were given. Sequential… (+12 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): autoprefixer, electron, devDependencies, autoprefixer, electron, react, react-markdown, tailwindcss (+5 more)

### Community 96 - "EventBus"
Cohesion: 0.14
Nodes (12): EventBus, Any, Protocol, Server -> client push notifications and the set of live connections (§7.1).…, Minimal transport surface — a Starlette WebSocket satisfies this., Tracks connected clients and broadcasts notifications to them., Send the current state to one client, unconditionally. A reconnecting renderer…, Send a notification to every live client, dropping dead ones. (+4 more)

### Community 97 - "Runtime"
Cohesion: 0.12
Nodes (9): ModelAvailability, AvailabilityService, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand., Re-read the Credential Manager. Call after any key change., Handles owned by the app lifespan. (+1 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "FakePage"
Cohesion: 0.10
Nodes (7): FakeLocator, FakePage, Refusing to act on an ambiguous-but-real description is worse than picking the…, Implements exactly the `Page` surface `browser.py` calls., test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), test_locate_takes_the_first_of_several_ambiguous_matches()

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

### Community 105 - "MonkeyPatch"
Cohesion: 0.19
Nodes (20): MonkeyPatch, _returning(), test_click_names_what_it_could_not_find(), test_click_runs_the_match_it_finds(), test_current_page_escalation_checks_the_live_page(), test_current_page_escalation_is_quiet_on_an_ordinary_page(), test_fill_risk_escalates_on_a_payment_shaped_field(), test_fill_risk_is_quiet_for_an_ordinary_field() (+12 more)

### Community 106 - "gate_permission_modes.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "system.py"
Cohesion: 0.15
Nodes (21): test_system_info_reports_this_machine(), _endpoint_volume(), _facts(), get_system_info(), kill_process(), Any, tool, Facts about the machine, and the one knob she can turn on it. `get_system_info`… (+13 more)

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

### Community 114 - "ProactivityScheduler"
Cohesion: 0.33
Nodes (3): ProactivityScheduler, One pass. Never raises — a scheduler that dies stops everything, the same…, Sweeps for something worth saying, at most once per tick, and only when nothing…

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "OllamaProvider"
Cohesion: 0.08
Nodes (24): HTTPError, concrete_tokens(), main(), novel_tokens(), Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+16 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 121 - "MachineContext"
Cohesion: 0.17
Nodes (19): machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, volatile_prefix(), Silence beats a wrong claim: unknown facts are simply not mentioned., The whole design rests on this. This block sits before the conversation, so a… (+11 more)

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

### Community 131 - "Electron UI (renderer)"
Cohesion: 0.29
Nodes (7): ARIA (local-first Windows AI assistant), Electron UI (renderer), Python sidecar (brain), Acrylic backgroundMaterial was covered by an opaque backgroundColor; fixed to #00000000, ConfirmDialog raw-argument fallback had no height cap; overflow hid Allow/Deny buttons, type_text SendInput struct-size bug: INPUT union undersized, all mocked tests passed anyway, Rule 1: all state lives in the Python sidecar

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
Nodes (42): Check, admits_ignorance(), answers_flatly(), contains(), contains_any(), denies_capability(), exact(), excludes() (+34 more)

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

### Community 149 - "test_browser.py"
Cohesion: 0.11
Nodes (28): Exception, parametrize, _raising(), Browser control: the checkout/banking hard block, password refusal, and element…, The URL check catches the common case; a card-number field on an unlisted…, No page has loaded yet at this point — only the URL being navigated *to* is…, `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, §11: the *next* tool call after this one is force-escalated by the agent loop —… (+20 more)

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

### Community 191 - "get"
Cohesion: 0.11
Nodes (19): Whether this endpoint may train on what is sent to it. Unknown ids read as…, _trains_on_data(), get(), persona_for(), Curated first, then adopted, then discovered. So an explicit choice always…, Persona level for a model; unknown ids get the safe, minimal prompt., require(), parametrize (+11 more)

### Community 195 - "WakeWord"
Cohesion: 0.12
Nodes (7): Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, ndarray, Protocol, What the listener depends on, so it never imports openwakeword., WakeWord

### Community 197 - "files_browse"
Cohesion: 0.09
Nodes (26): _enumerate_drives(), files_browse(), files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, One folder's contents, for the panel. Deliberately not `list_folder`: that tool… (+18 more)

### Community 202 - "test_openrouter.py"
Cohesion: 0.08
Nodes (37): _openrouter_benchmark(), _openrouter_expired(), _openrouter_is_free(), parse_openrouter(), Any, date, Free on **both** sides of the meter. `pricing.prompt == "0"` alone would admit…, Artificial Analysis' published intelligence index, if OpenRouter has one. A… (+29 more)

### Community 203 - "test_research.py"
Cohesion: 0.05
Nodes (51): AsyncClient, HTMLParser, An epub is a zip of XHTML. Tags are stripped rather than parsed — the same call…, _read_epub(), Readable text from a page, truncated on a word boundary., Fetch and strip anything that arrived without text. Concurrently, and failures…, One result, and whatever text could be got out of it., The best text available, preferring the fetched page. (+43 more)

### Community 209 - "migrate"
Cohesion: 0.15
Nodes (14): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, Run ``fn`` against the connection off the event loop, serialised., Open the database with sqlite-vec loaded and the required pragmas set. (+6 more)

### Community 211 - "retrieved_block"
Cohesion: 0.13
Nodes (16): estimate_tokens(), Render remembered facts and episodes into one system message. Returns None when…, _render_memory(), retrieved_block(), A turn about something she has no memory of must leave the prompt byte-…, A fact is a standing truth; an episode is one conversation., A clipped fact beats silence — the cap is a prefill guard, not a correctness…, §8.2's order: temporal, then facts. Memory sits nearest the turns because that… (+8 more)

### Community 212 - "PersonaLevel"
Cohesion: 0.17
Nodes (16): fit_to_budget(), overhead_tokens(), PersonaLevel, StrEnum, How much character a model can carry without falling apart. Measured on…, Tokens spent before the conversation even starts. Roll-up decisions must…, Drop oldest turns until the assembled prompt fits. Backstop, not policy.…, It used to omit them, so it trimmed against a budget ~1650 tokens too generous.… (+8 more)

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.29
Nodes (5): DURATION, EASE, SPRING, stagger, TWEEN

### Community 244 - "parametrize"
Cohesion: 0.14
Nodes (15): is_trivial(), needs_deep_model(), A greeting or acknowledgement — nothing a 4B model can get wrong., Reasoning, code, or a multi-step request: the `smart` class earns its cost., parametrize, The line that was missing. Without it these went to the FAST class., A false positive costs a spoken turn its ~800ms head start, which is the thing…, test_clipboard_questions_stay_on_this_machine() (+7 more)

### Community 245 - "_json_type"
Cohesion: 0.15
Nodes (14): It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, test_a_wrapped_argument_description_survives_the_line_break(), _arg_docs(), build_parameters(), _json_type(), _model_schema(), Any, BaseModel (+6 more)

### Community 246 - "ProviderRegistry"
Cohesion: 0.06
Nodes (30): ConversationHistory, ProviderRegistry, BaseModel, Providers keyed by name, so the service can follow the router's choice., `chat.history` result. Typed at the boundary per CLAUDE.md rule 7., MessageHit, BaseModel, Row (+22 more)

### Community 247 - "broker"
Cohesion: 0.38
Nodes (7): broker(), exam(), fixture, MonkeyPatch, Put the session into Exam, through the real `ConversationService` API rather…, Stands in for `runtime.questions`, recording exactly what was shown., wired()

### Community 248 - "OpenRouterProvider"
Cohesion: 0.08
Nodes (24): Replace what the providers said they offer. A curated id always wins: `gpt-5`…, set_discovered(), _as_int(), OpenRouterProvider, Any, Headers, OpenAI's wire format, someone else's models. Subclassing rather than copying is…, Reachability, and a free chance to read the quota headers. (+16 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 255 - "rpc.ts"
Cohesion: 0.29
Nodes (5): Pending, RpcEnvelope, RpcError, RpcErrorShape, RpcNotification

### Community 256 - "gate_tool_selection.py"
Cohesion: 0.22
Nodes (13): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+5 more)

### Community 257 - "Question"
Cohesion: 0.21
Nodes (11): normalise(), Pending, BaseModel, Question, Trim to the caps and give every question its escape hatch. Done here rather…, Broadcast, then wait. Never raises for an ordinary outcome., One question, with the options that answer it., Otherwise there would be two, and one of them would do nothing. (+3 more)

### Community 259 - "pcm16_to_float32"
Cohesion: 0.50
Nodes (4): pcm16_to_float32(), Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., One 80ms frame of base64 int16 PCM from the open microphone. Sent as a…, voice_frame()

### Community 260 - "RateLimitState"
Cohesion: 0.17
Nodes (7): RateLimitState, Turn reasoning off where the endpoint allows it, and count the call. This is…, How much of the free daily allowance ARIA has spent, and it is a count. **The…, **Checked live on 2026-08-19, and the first version was wrong.** OpenRouter…, The header reader is kept because a 429 is documented to carry them. If a real…, test_a_stated_figure_beats_the_local_count(), test_the_free_allowance_is_counted_here_because_the_api_does_not_say()

### Community 261 - "free_model"
Cohesion: 0.17
Nodes (12): free_model(), health(), fixture, ModelInfo, A free OpenRouter model, adopted so the router can actually reach it.…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make…, Stage 1 already works this way for privacy, and this sits after it. Overriding… (+4 more)

### Community 262 - "database"
Cohesion: 0.29
Nodes (9): conn(), database(), db_path(), Connection, fixture, Path, Shared fixtures. Every test gets a throwaway data dir — never the real data/., A migrated database on a temp path. (+1 more)

### Community 263 - "_looks_like_a_commit_action"
Cohesion: 0.22
Nodes (9): Locator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught(), test_commit_wording_in_the_visible_text_is_caught(), _looks_like_a_commit_action() (+1 more)

### Community 264 - "_escalate_click_risk"
Cohesion: 0.22
Nodes (9): The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, test_click_risk_escalates_on_the_elements_own_wording(), test_click_risk_is_quiet_for_an_ordinary_click(), test_click_risk_is_quiet_when_nothing_resolved(), test_click_risk_still_escalates_on_a_checkout_page(), _escalate_click_risk() (+1 more)

### Community 265 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 272 - "study_begin"
Cohesion: 0.22
Nodes (9): _describe(), Connection, StudyState, tool, What comes back to the model after a begin — the map and where he is., Build or resume a subject's concept map. Args: subject: What he is studying, in…, A file name or path as the model gave it, resolved to an indexed path. The…, _resolve_material() (+1 more)

### Community 273 - "to_pcm16"
Cohesion: 0.25
Nodes (7): ndarray, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, to_pcm16(), Wrapping turns a loud sample into a click at the opposite polarity., test_pcm16_clips_rather_than_wrapping(), test_pcm16_is_little_endian_and_half_the_size_of_float32()

### Community 274 - "_drain_windows"
Cohesion: 0.25
Nodes (7): _drain_windows(), parts(), phrase(), fixture, Cancel every listening window a test left open. Not optional: ARMED and OPEN…, openWakeWord gating — `hey jarvis` opens capture., The default: any speech is captured, and the transcript decides.

### Community 276 - "StudyPanel.test.tsx"
Cohesion: 0.32
Nodes (3): defaults(), state(), subject()

### Community 277 - "assemble"
Cohesion: 0.29
Nodes (7): assemble(), Build the final message list, stable content first., The KV-cache bargain, asserted directly. CLAUDE.md's measured rule: an…, test_memory_never_touches_the_stable_prefix(), test_assemble_puts_stable_content_first(), Every conversation that is not a study session must be byte-identical to what…, test_no_study_block_leaves_the_prompt_exactly_as_it_was()

### Community 278 - "choose_model"
Cohesion: 0.33
Nodes (6): choose_model(), §8.3: cloud if a key is present, local otherwise. Walks SMART then BALANCED,…, §8.3: reflection is the highest-leverage inference in the system., Which is the state this machine is actually in., test_a_usable_cloud_model_is_preferred(), test_it_falls_back_to_local_with_no_cloud_key()

### Community 282 - "build_prompt"
Cohesion: 0.40
Nodes (5): build_prompt(), §8.3's prompt, with the two slots filled., `str.format` would raise on the literal braces in the JSON example — hence the…, test_an_empty_fact_list_reads_as_none_yet(), test_the_prompt_carries_both_slots()

### Community 284 - "test_the_tools_are_registered"
Cohesion: 0.67
Nodes (3): parametrize, The import in `tools/__init__.py` is load-bearing: the decorator runs on…, test_the_tools_are_registered()

## Knowledge Gaps
- **346 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+341 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **69 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_reflection.py`, `database`, `test_tts.py`, `test_proactivity.py`, `finder.py`, `Indexer`, `conversation.py`, `ConversationStore`, `SettingsStore`, `SemanticMemory`, `test_study_modes.py`, `test_study_tools.py`, `RoutingLog`, `FakeProvider`, `test_retrieval.py`, `GenerationOptions`, `test_db.py`, `proactivity.py`, `ConversationService`, `test_episodic.py`, `watched_project_candidate`, `test_curriculum.py`, `test_conversation.py`, `main.py`, `EpisodicMemory`, `test_affect.py`, `OllamaEmbeddings`, `affect.py`, `migrate`, `memory/study.py`, `StudyState`, `test_ask.py`, `Fact`, `Runtime`, `ProactivityScheduler`, `AffectState`, `OllamaProvider`, `ProviderRegistry`, `broker`, `_repeated_failures`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `test_tts.py`, `Database`, `conversation.py`, `ConversationStore`, `HealthTracker`, `test_study_modes.py`, `RoutingLog`, `Router`, `FakeProvider`, `GenerationOptions`, `Listener`, `LoopState`, `Event`, `test_conversation.py`, `main.py`, `get`, `ChatMessage`, `WakeWord`, `ProviderUnavailable`, `Retriever`, `test_ask.py`, `ToolContext`, `EventBus`, `Runtime`, `OllamaProvider`, `ProviderRegistry`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `test_tts.py`, `finder.py`, `apps.py`, `study_begin`, `conversation.py`, `test_browser.py`, `test_screen.py`, `test_study_tools.py`, `test_organize.py`, `Tool`, `GenerationOptions`, `files.py`, `ConversationService`, `test_tools.py`, `test_research.py`, `test_ask.py`, `FakePage`, `system.py`, `ProviderRegistry`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 58 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 58 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._