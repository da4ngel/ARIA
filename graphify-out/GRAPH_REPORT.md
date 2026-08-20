# Graph Report - ARIA  (2026-08-20)

## Corpus Check
- 256 files · ~370,256 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 5276 nodes · 12140 edges · 280 communities (215 shown, 65 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1067 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `01b37287`
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
- test_procedures.py
- test_scheduler.py
- test_proactivity.py
- discovery.py
- KokoroTTS
- ModelInfo
- finder.py
- apps.py
- test_indexer.py
- gate_wakeword.py
- test_modes.py
- ConversationStore
- main.py
- HealthTracker
- SemanticMemory
- test_screen.py
- MonkeyPatch
- test_ollama_supervisor.py
- test_router.py
- test_extract.py
- handlers.py
- test_study_tools.py
- RoutingLog
- test_organize.py
- Router
- .prune
- Database
- Tier
- GenerationOptions
- strip_wake_word
- Listener
- test_db.py
- AdoptionService
- test_focus.py
- _seed
- ARIA — Project Instructions
- ToolContext
- ConversationService
- OpenAIProvider
- Candidate
- test_questions.py
- test_curriculum.py
- eval_quality.py
- test_text.py
- CredentialKey
- LoopState
- compilerOptions
- Event
- Connectivity
- test_conversation.py
- snapshot
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- Settings
- compilerOptions
- PersonaLevel
- ChatMessage
- SpeechStream
- test_tools.py
- test_vectors.py
- test_context.py
- test_browser_setup.py
- ProviderRateLimited
- test_affect.py
- Utterance
- StubSearch
- extract.py
- EpisodicMemory
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- _cloud_model
- test_adoption.py
- memory/study.py
- memory.py
- study_begin
- FilesPanel.tsx
- Sidecar
- Client
- registry.py
- Client
- Indexer
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- browser.py
- rpc
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- soak_conversation.py
- AvailabilityService
- PermissionEngine
- FakeLocator
- FilesPanel.test.tsx
- protocol.py
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- test_browser.py
- _start_conversation
- render
- gate_organize.py
- BrowserUnavailable
- HistoryPanel.tsx
- CLAUDE.md — ARIA Project Instructions (Claude Code-facing)
- Router — local vs cloud, then which provider
- gate_affect.py
- ProactivityScheduler
- AffectState
- usePermissionMode.ts
- ProviderUnavailable
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- gate_research.py
- ModelVerdict
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
- _next_level
- electron-vite
- framer-motion
- jsdom
- test_research.py
- remark-gfm
- files_rename
- @testing-library/react
- @types/node
- @types/react
- @types/react-dom
- test_openrouter.py
- to_text
- vite
- @vitejs/plugin-react
- vitest
- sidecar/__init__.py
- persona/__init__.py
- ask_user
- test_the_gate_is_the_same_probes_the_scripts_use
- parametrize
- _suppress_close_errors
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
- extract_text
- conversation.py
- broker
- OpenRouterProvider
- tokens.js
- rpc.ts
- _parse_yes_no
- is_stated_intention
- useConversation.test.ts
- TranscriptionUnavailable
- tools_trust_all_drives
- Any
- Launch
- test_a_verdict_records_why_not_just_what
- _Semantic
- _reset_connection
- eval/__init__.py
- postcss
- react-dom
- rehype-highlight
- @types/ws
- online
- test_read_is_named_as_an_untrusted_source
- grade
- electron-builder
- zustand
- test_archives_are_attachable_but_never_indexed

## God Nodes (most connected - your core abstractions)
1. `Database` - 326 edges
2. `ConversationStore` - 168 edges
3. `ConversationService` - 119 edges
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

## Communities (280 total, 65 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (110): Collection, Four options on screen are no use to someone across the room, and that is the…, test_it_is_hidden_on_a_spoken_turn(), engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this… (+102 more)

### Community 1 - "test_listener.py"
Cohesion: 0.06
Nodes (71): Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout., drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device… (+63 more)

### Community 2 - "main.ts"
Cohesion: 0.15
Nodes (22): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+14 more)

### Community 3 - "test_catalog.py"
Cohesion: 0.08
Nodes (38): default_local(), ModelAvailability, persona_for(), A catalog entry plus whether it can actually be used right now., The local fallback. Prefers the instruction-tuned 7B. `pulled` is what Ollama…, Persona level for a model; unknown ids get the safe, minimal prompt., Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from. (+30 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.09
Nodes (47): _port_is_free(), Whether we can actually have the port, checked before anything else. **A second…, files_browse(), method_names(), One folder's contents, for the panel. Deliberately not `list_folder`: that tool…, _auth(), _call(), client() (+39 more)

### Community 5 - "test_reflection.py"
Cohesion: 0.08
Nodes (40): build_prompt(), choose_model(), _extract_json(), Any, §8.3's prompt, with the two slots filled., §8.3: cloud if a key is present, local otherwise. Walks SMART then BALANCED,…, Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio (+32 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.07
Nodes (59): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no…, One attachment, understood. Never raises. (+51 more)

### Community 7 - "test_tts.py"
Cohesion: 0.04
Nodes (65): ndarray, RuntimeError, Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, Voice could not start. Never fatal — she still types., shorten_for_speech() (+57 more)

### Community 8 - "test_procedures.py"
Cohesion: 0.10
Nodes (26): detect(), DetectedSequence, discard(), Procedural learning — tier 4 of memory (BUILD_SPEC §9 Phase 8). `procedures`…, What the user said right before the first tool of a detected sequence, in the…, Declined — forgotten, not just hidden. If the same pattern keeps happening,…, The `procedures.name` key — `UNIQUE NOT NULL` in the schema, which is the…, Ordered `(tool)` per session, successful calls only — a sequence worth turning… (+18 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (42): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday., Sweeps idle sessions, and runs reflection once per day. (+34 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.18
Nodes (28): _candidate(), FakeStore, Connection, datetime, The proactivity engine (BUILD_SPEC §9 Phase 8). `ProactivityScheduler.tick()`…, Stands in for `find_candidates`/`self_check`/`deliver`., A check-in at 3am is not a check-in, it is being woken up — and `affect`…, Nothing has ever been said, so there is no silence to notice. Being messaged… (+20 more)

### Community 11 - "discovery.py"
Cohesion: 0.06
Nodes (57): Cost, StrEnum, discover_all(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch(), _gemini_class() (+49 more)

### Community 12 - "KokoroTTS"
Cohesion: 0.05
Nodes (53): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+45 more)

### Community 13 - "ModelInfo"
Cohesion: 0.05
Nodes (59): Which models are usable right now. One object answers this for both…, adopt(), adopted(), all_models(), by_class(), clear_adopted(), discovered(), get() (+51 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (67): _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The…, Make `find_files` deterministic and count how often it really walks., The reason the cache exists at all — two questions in a row must not walk three… (+59 more)

### Community 15 - "apps.py"
Cohesion: 0.05
Nodes (66): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, test_type_text_refuses_empty_text(), test_type_text_refuses_when_nothing_has_focus(), AppEntry, _AppIndex, _bring_to_front(), _build_index() (+58 more)

### Community 16 - "test_indexer.py"
Cohesion: 0.15
Nodes (21): chunk(), Whether this file is worth reading at all., Overlapping windows, so a sentence spanning a boundary stays findable., should_index(), parametrize, Path, Chunking, extraction and the rules that keep the indexer out of the way.…, §9: skip over 20MB. Extraction cost is otherwise unbounded. (+13 more)

### Community 17 - "gate_wakeword.py"
Cohesion: 0.06
Nodes (26): main(), Download the wake word weights into data/models/openwakeword. python…, frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python… (+18 more)

### Community 18 - "test_modes.py"
Cohesion: 0.05
Nodes (49): policy_for(), ConversationMode, StrEnum, The policy, or Normal's. Never raises. A mode arriving from a stale client is a…, A mode this turn would be better served by, or None. None is the answer for the…, How much of the registry a mode lets the model see. **Narrowing, never…, The highest tier this policy will show, or None for no tools., suggest() (+41 more)

### Community 19 - "ConversationStore"
Cohesion: 0.04
Nodes (83): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's… (+75 more)

### Community 20 - "main.py"
Cohesion: 0.05
Nodes (50): ARIA sidecar entrypoint — FastAPI app, /health, and the /rpc WebSocket. Run…, Free-model measurement, and putting past adoptions back in the pool.…, Idle sweeps always; the nightly §8.3 pass only if it is wanted., _start_adoption(), _start_memory_scheduler(), SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Episodes — what happened, compressed and kept (BUILD_SPEC §7.3 tier 2). One…, _pack() (+42 more)

### Community 21 - "HealthTracker"
Cohesion: 0.07
Nodes (32): HealthTracker, ModelHealth, BaseModel, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture, Observed latency and the circuit breaker. A 429 is treated as a routing input… (+24 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.04
Nodes (69): Fact, normalise_triple(), _now(), Row, The form that gets embedded and shown in the prompt., Fold a triple to its stored form. The UNIQUE index is on the raw columns, so…, A stored `fact_vec` row back into floats, or None if it has no vector., Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder. (+61 more)

### Community 23 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 24 - "MonkeyPatch"
Cohesion: 0.06
Nodes (46): _focused(), MonkeyPatch, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V…, Below the threshold, nothing touches the clipboard — it belongs to the user,…, `read_text()` returns None when the clipboard held an image or a file list.…, The last gate. Between the claim and the send sit the dialog and… (+38 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.06
Nodes (46): find_ollama(), OllamaSupervisor, Path, Keep Ollama running, and notice when it comes back. Eyaas: *"sometimes when…, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was… (+38 more)

### Community 26 - "test_router.py"
Cohesion: 0.07
Nodes (50): is_trivial(), needs_deep_model(), A greeting or acknowledgement — nothing a 4B model can get wrong., Reasoning, code, or a multi-step request: the `smart` class earns its cost., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router… (+42 more)

### Community 27 - "test_extract.py"
Cohesion: 0.14
Nodes (28): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+20 more)

### Community 28 - "handlers.py"
Cohesion: 0.05
Nodes (90): build_health(), chat_cancel(), chat_delete(), chat_history(), chat_mode(), chat_new(), chat_rename(), chat_send() (+82 more)

### Community 29 - "test_study_tools.py"
Cohesion: 0.12
Nodes (33): concept_by_name(), The concept a question was about. Exact, then substring., _mapped(), Any, asyncio, quiz(), `study_begin` and `study_check`, and the state she is handed without asking.…, **The reason `QuizQuestion` is not `core.questions.Question`.** The broker… (+25 more)

### Community 30 - "RoutingLog"
Cohesion: 0.08
Nodes (26): Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Writes and reads `routing_log`. Never raises into the turn path., RoutingLog, Handles owned by the app lifespan., Runtime, Connection (+18 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (71): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+63 more)

### Community 32 - "Router"
Cohesion: 0.08
Nodes (30): BaseModel, ModelInfo, Whether this endpoint may train on what is sent to it. Unknown ids read as…, Chooses a model for a turn., Pick a model. `selected` is the user's choice — a model id, or "smart" to…, `bias` overrides the instance setting for this call only. **A parameter, not a…, Cloud unless the turn is trivial. The default. `_DEEP_VERBS` is checked here…, Cloud for real work, local for conversation. (+22 more)

### Community 33 - ".prune"
Cohesion: 0.40
Nodes (3): datetime, Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days.

### Community 34 - "Database"
Cohesion: 0.13
Nodes (33): Database, Async-safe wrapper around the single sqlite connection., anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice., `_build_context` runs once per attempt inside the failover loop, so without… (+25 more)

### Community 35 - "Tier"
Cohesion: 0.06
Nodes (40): EscalateFn, PreviewFn, RefuseFn, Bus, Denied, Journal, paths_in(), Pending (+32 more)

### Community 36 - "GenerationOptions"
Cohesion: 0.05
Nodes (56): build_prompt(), choose_model(), CurriculumBuilder, CurriculumOutput, CurriculumReport, ExtractedConcept, BaseModel, ModelInfo (+48 more)

### Community 37 - "strip_wake_word"
Cohesion: 0.14
Nodes (16): is_stop_word(), _near_the_name(), Is this whole utterance just a request to stop talking?, Is this first word a plausible mishearing of her name? `base.en` on a single…, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said. (+8 more)

### Community 38 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 39 - "test_db.py"
Cohesion: 0.07
Nodes (41): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, Run ``fn`` against the connection off the event loop, serialised., Every table in the database, including vec0 virtual tables. (+33 more)

### Community 40 - "AdoptionService"
Cohesion: 0.10
Nodes (22): AdoptionService, AdoptionState, _probes_by_id(), Any, BaseModel, date, datetime, ModelInfo (+14 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "_seed"
Cohesion: 0.10
Nodes (32): confirm(), context_hint(), pending_offers(), Row, Detect, then insert exactly the sequences not already known. Returns the names…, Detected, not yet confirmed or declined — what the proactivity engine has to…, Accepted — becomes a context hint from now on., One line for the prompt when a confirmed procedure's trigger phrase is a close… (+24 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "ToolContext"
Cohesion: 0.08
Nodes (57): test_system_info_reports_this_machine(), create_folder(), delete_file(), delete_folder(), _GUID, known_folder(), list_folder(), move_file() (+49 more)

### Community 45 - "ConversationService"
Cohesion: 0.04
Nodes (32): SessionSummary, ConversationService, Any, ConversationMode, RoutingBias, Name the conversation once it has enough content to name. Deliberately fire-…, Hold until no turn is in flight. False if the user never stops., Ask the local model for a short label. Never raises. (+24 more)

### Community 46 - "OpenAIProvider"
Cohesion: 0.10
Nodes (15): _assemble(), OpenAIProvider, Any, Headers, Response, ToolCall, No-op: cloud models have no local load step to pay for., Per-request fields this vendor accepts and OpenAI does not. A hook rather than… (+7 more)

### Community 47 - "Candidate"
Cohesion: 0.12
Nodes (24): Candidate, idle_intention_candidate(), datetime, Path, timedelta, You have not been around in a while" — at most once, and only when that is…, Names of files under `root` modified inside `window`. Bounded, and never raises…, Notice that a watched folder is being worked in right now. Empty by default:… (+16 more)

### Community 48 - "test_questions.py"
Cohesion: 0.07
Nodes (49): Answer, Asked, normalise(), Option, Pending, BaseModel, Question, QuestionBroker (+41 more)

### Community 49 - "test_curriculum.py"
Cohesion: 0.15
Nodes (25): The indexed text of one file, in order, or `""` if it was never indexed. The…, source_text(), _builder(), asyncio, Turning a lecture into a concept map, and surviving what a model returns. The…, A scanned PDF or an image-only deck is a normal thing to be handed, and "no…, A subject with no concepts would render as "0 of 0 covered" forever and win…, `reflection` records why this matters: reporting the model that was *tried*… (+17 more)

### Community 50 - "eval_quality.py"
Cohesion: 0.08
Nodes (37): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+29 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (29): content_words(), coverage(), idf(), `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,…, Strip a plural or tense suffix. Crude on purpose, and guarded. Not a linguistic… (+21 more)

### Community 52 - "CredentialKey"
Cohesion: 0.12
Nodes (22): all_status(), CredentialKey, CredentialStatus, delete_key(), get_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,… (+14 more)

### Community 53 - "LoopState"
Cohesion: 0.11
Nodes (16): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Mark one step as run. `local_only` is unknown, not False, for a tool the…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through… (+8 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "Event"
Cohesion: 0.06
Nodes (33): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, AssistantState, Event, EventBus, Any, Protocol (+25 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "test_conversation.py"
Cohesion: 0.04
Nodes (121): MemoryServices, Everything Phase 5 hands to the conversation, as one argument.…, A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, _drain(), FakeProvider, make_service(), OpenEngine (+113 more)

### Community 58 - "snapshot"
Cohesion: 0.18
Nodes (11): BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM unconditionally.…, §9:943 says "regardless of tool tier" — that only means something if *every*…, test_every_browser_tool_carries_the_checkout_escalation(), test_only_fill_carries_the_password_refusal(), test_tiers_deviate_from_build_specs_blanket_confirm_by_design(), T1. It reads and changes nothing; the consent that matters is the online…, test_research_needs_no_confirmation(), BUILD_SPEC's own tier table (§9:474) lists this AUTO — that line is about the… (+3 more)

### Community 59 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (27): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+19 more)

### Community 60 - "ARIA Sidecar Runtime Dependencies (requirements.txt)"
Cohesion: 0.07
Nodes (27): ARIA Sidecar Runtime Dependencies (requirements.txt), anthropic==0.39.* (NOT adopted, Anthropic excluded), apscheduler==3.10.* (deferred, Phase 5), fastapi==0.115.*, faster-whisper==1.0.3, httpx==0.27.*, keyring==25.7.* (Windows Credential Manager), kokoro-onnx==0.4.* (+19 more)

### Community 61 - "Settings"
Cohesion: 0.06
Nodes (36): BaseSettings, FastAPI, _default_data_dir(), Path, Sidecar configuration. Single source of truth for paths, port, and auth token.…, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In… (+28 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "PersonaLevel"
Cohesion: 0.09
Nodes (35): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+27 more)

### Community 64 - "ChatMessage"
Cohesion: 0.05
Nodes (55): assemble(), clean_title(), ConversationMode, episode_request(), estimate_tokens(), fit_to_budget(), _mode_block(), mode_done_when() (+47 more)

### Community 65 - "SpeechStream"
Cohesion: 0.11
Nodes (13): ModelInfo, StoredMessage, ToolCall, Which model gets to see the tool's result. `router._PRIVATE` already keeps a…, Evict the previous local model before loading a different one. CLAUDE.md rule…, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Say a reply aloud, on request. False when there is no voice engine. The other…, Phase 8 voice polish's affect-driven nudge to `KokoroTTS.synthesize`. Same… (+5 more)

### Community 66 - "test_tools.py"
Cohesion: 0.03
Nodes (99): main(), Console entrypoint for ``python -m sidecar.main``., parametrize, The import in `tools/__init__.py` is load-bearing: the decorator runs on…, test_the_tools_are_registered(), app(), parametrize, Path (+91 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (23): cosine(), cosine_from_l2(), normalise(), pack(), Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for…, Cosine similarity of two vectors, normalised or not. Used by the merge step,… (+15 more)

### Community 68 - "test_context.py"
Cohesion: 0.06
Nodes (57): machine_context(), MachineContext, overhead_tokens(), Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, Tokens spent before the conversation even starts. Roll-up decisions must…, volatile_prefix() (+49 more)

### Community 69 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+9 more)

### Community 70 - "ProviderRateLimited"
Cohesion: 0.09
Nodes (20): ProviderRateLimited, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, build_all(), for_model(), for_provider(), ModelInfo, One place that knows how to build a provider from its name. **This exists…, A client for one provider. Raises on anything unrecognised. **Never a… (+12 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "Utterance"
Cohesion: 0.11
Nodes (8): ndarray, Protocol, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance, VoiceActivity

### Community 73 - "StubSearch"
Cohesion: 0.15
Nodes (14): Exception, Stripping is a losing game — there are unlimited phrasings. The content is…, It has a title, a URL and a snippet. Citing it beats pretending the search did…, A model that asks for fifty pages would blow the context budget §8.2 exists to…, Stands in for the network. Returns whatever it was handed., StubSearch, test_a_source_that_would_not_load_is_still_cited(), test_an_empty_query_asks_rather_than_searching() (+6 more)

### Community 74 - "extract.py"
Cohesion: 0.12
Nodes (21): _extract_bytes(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as…, Slide text and speaker notes, straight out of the OOXML. `python-pptx` would do… (+13 more)

### Community 75 - "EpisodicMemory"
Cohesion: 0.03
Nodes (62): _build_memory(), Facts, episodes and retrieval, as one handle for the conversation., Episode, EpisodicMemory, _now(), BaseModel, datetime, Row (+54 more)

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
Cohesion: 0.12
Nodes (17): _cloud_model(), ModelInfo, 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement…, The mechanism has to keep working, or banding would just be a way of ignoring…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make… (+9 more)

### Community 80 - "test_adoption.py"
Cohesion: 0.12
Nodes (46): a_model(), Asker, Clock, perfect_reply(), ModelInfo, Measuring a free model, and the line it has to cross to be routed to.…, A scripted model, and a count of what it cost to ask it., What a model that should be adopted says to any probe. (+38 more)

### Community 81 - "memory/study.py"
Cohesion: 0.10
Nodes (41): add_concepts(), ensure_subject(), latest_subject_id(), mark_taught(), _now(), Study Mode's state — the subject, its concept map, and what he has shown. Study…, Find or create a subject by name, returning its id. `source_path` is filled in…, Add `(name, summary)` pairs to a subject's map, in order. **Additive, never a… (+33 more)

### Community 82 - "memory.py"
Cohesion: 0.12
Nodes (19): People say "remember that ..." to a thing whose job is remembering., The fallback is not a failure: the fact stays retrievable and the panel can fix…, test_a_lead_in_is_stripped(), test_an_unrecognised_phrasing_is_still_kept(), test_common_phrasings_become_real_predicates(), Everything she can do to the machine, and what it costs to do it. Importing…, _clip(), forget() (+11 more)

### Community 83 - "study_begin"
Cohesion: 0.12
Nodes (16): Concept, find_subject(), What to teach next: the first weak one, else the first untouched one, else…, Resolve a spoken subject name to an id, loosely. Exact first, then substring in…, One node of the map, with whatever mastery it has accumulated., Everything the prompt block and the report are rendered from. Assembled in one…, Anything that has been taught, whether or not it stuck., StudyState (+8 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "Sidecar"
Cohesion: 0.19
Nodes (3): HealthBody, Sidecar, SidecarOptions

### Community 86 - "Client"
Cohesion: 0.29
Nodes (7): Client, main(), Any, Does she ask well, and — more importantly — does she stop asking? python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Send, answer anything she waits on, and return the completed turn. `pick` is…, section()

### Community 87 - "registry.py"
Cohesion: 0.07
Nodes (35): ask_tool(), `ask_user`: the registry entry, and the schema the model has to produce. The…, **The first restriction overshot, and Eyaas caught it on screen.** Asked "can u…, Pydantic hoists nested models into `$defs` and points at them with `$ref`.…, The first version only reached the top level. Pydantic emits a title per class…, The schema change is a capability, not a special case for this tool., **There was a one-question-per-turn cap here, and it was wrong.** Asked to…, `registry.get` is `Tool | None`, and a missing tool here means the import in… (+27 more)

### Community 88 - "Client"
Cohesion: 0.24
Nodes (10): Client, concepts_in(), main(), Any, Does Study Mode actually teach? Live, against a real sidecar. python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Answer a `question.ask` the way a student would — one pick each. **This gate…, The map and its mastery, read straight from the sidecar's own state. Asserting… (+2 more)

### Community 89 - "Indexer"
Cohesion: 0.09
Nodes (16): _build_indexer(), Start reading documents in the background, if that is wanted. Deliberately last…, _digest(), Indexer, IndexStats, Path, Cheap identity: re-reading a 10MB PDF to decide whether to re-read it would…, Walks, reads, embeds and stores — slowly, and out of the way. (+8 more)

### Community 90 - "Sidebar.tsx"
Cohesion: 0.13
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 92 - "browser.py"
Cohesion: 0.13
Nodes (26): Page, test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), browser_click(), browser_fill(), browser_navigate(), browser_read(), browser_screenshot() (+18 more)

### Community 93 - "rpc"
Cohesion: 0.13
Nodes (16): get, bearer_from_header(), Constant-time comparison of a presented Bearer token., Extract the token from an ``Authorization: Bearer <token>`` header., token_matches(), health(), Any, Liveness probe for Electron's supervisor. Deliberately cheap and dependency-… (+8 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): autoprefixer, electron, devDependencies, autoprefixer, electron, react, react-markdown, tailwindcss (+5 more)

### Community 96 - "soak_conversation.py"
Cohesion: 0.18
Nodes (12): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+4 more)

### Community 97 - "AvailabilityService"
Cohesion: 0.11
Nodes (10): ModelAvailability, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+2 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "FakeLocator"
Cohesion: 0.09
Nodes (12): Locator, FakeLocator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, Refusing to act on an ambiguous-but-real description is worse than picking the…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught() (+4 more)

### Community 101 - "protocol.py"
Cohesion: 0.19
Nodes (17): dispatch(), _invoke(), Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., err(), ErrorCode, ok(), Any (+9 more)

### Community 102 - "ConfirmDialog.tsx"
Cohesion: 0.16
Nodes (10): ConfirmRequest, ImagePreview, leaf(), MovePlan, MovePlanView(), Props, tail(), TIER_LABEL (+2 more)

### Community 103 - "useConversation.ts"
Cohesion: 0.27
Nodes (12): appendToStreaming(), AttachmentStatus, clearStreaming(), finalise(), loadRatings(), ToolCall, toTurns(), Turn (+4 more)

### Community 104 - "package.json"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 105 - "test_browser.py"
Cohesion: 0.14
Nodes (30): FakePage, MonkeyPatch, Browser control: the checkout/banking hard block, password refusal, and element…, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, Implements exactly the `Page` surface `browser.py` calls., _returning() (+22 more)

### Community 106 - "_start_conversation"
Cohesion: 0.09
Nodes (18): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, Deliver a message with no preceding question. Called by…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, Any, Task (+10 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "BrowserUnavailable"
Cohesion: 0.17
Nodes (11): Browser, Exception, _raising(), `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, test_navigate_reports_browser_unavailable_plainly(), test_no_user_facing_browser_error_names_chrome(), BrowserUnavailable, _connect() (+3 more)

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
Cohesion: 0.23
Nodes (5): Unprompted messages (Phase 8). Off entirely when the switch is off — the same…, _start_proactivity_scheduler(), ProactivityScheduler, One pass. Never raises — a scheduler that dies stops everything, the same…, Sweeps for something worth saying, at most once per tick, and only when nothing…

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "ProviderUnavailable"
Cohesion: 0.08
Nodes (22): HTTPError, _discover_local_models(), Ask Ollama what is actually pulled. Never fatal — Ollama may be down., ProviderUnavailable, Any, Common `[{role, content}]` shape most chat APIs accept. Tool fields are only…, The backend could not be reached — offline, not running, DNS, refused. Distinct…, to_wire() (+14 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 121 - "ModelVerdict"
Cohesion: 0.29
Nodes (5): ModelVerdict, BaseModel, Per-model tallies. The dataset §9.7 wants, as far as it has grown., How a model has actually been received, per `routing_log`., Liked as a fraction of rated, or None while it would be noise.

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
Cohesion: 0.18
Nodes (9): Any, Response, RuntimeError, Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix., Fetch and strip anything that arrived without text. Concurrently, and failures…, No usable search key, or the provider refused. Carries the fix., SearchUnavailable (+1 more)

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
Cohesion: 0.17
Nodes (13): The URL check catches the common case; a card-number field on an unlisted…, No page has loaded yet at this point — only the URL being navigated *to* is…, test_a_generic_domain_can_still_be_caught_by_its_dom(), test_known_checkout_and_banking_urls_are_recognised(), test_navigate_escalates_on_the_target_url_before_loading_it(), test_no_checkout_fields_means_no_dom_match(), _dom_confirms_checkout(), _escalate_current_page() (+5 more)

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

### Community 191 - "_next_level"
Cohesion: 0.33
Nodes (6): _next_level(), One answer's effect on a level. **A level is a running score, not a verdict on…, **The load-bearing rule.** One correct pick from four options is a 25% coin…, 0 means "never seen", and that stops being true once it is taught. Collapsing…, test_a_wrong_answer_never_takes_a_concept_back_to_never_introduced(), test_mastery_cannot_be_reached_in_one_answer()

### Community 195 - "test_research.py"
Cohesion: 0.18
Nodes (15): One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, `research(query)`, the untrusted-content boundary, and the online gate. Two…, A model that has just read 6,000 characters of someone else's writing has…, Returns real, correct URLs" is the acceptance line, and only `summary` reaches…, Stronger than asking it not to use one: §7.2's own reasoning for hiding DANGER,…, test_a_source_is_truncated_rather_than_dropped() (+7 more)

### Community 197 - "files_rename"
Cohesion: 0.20
Nodes (12): files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, Show it in Explorer. The escape hatch for anything this panel does not do., Rename in place, from a click in the panel. Reuses `tools/files.py`'s own…, **To the Recycle Bin, not gone.** This is the one place in the codebase that… (+4 more)

### Community 202 - "test_openrouter.py"
Cohesion: 0.08
Nodes (34): _openrouter_class(), _openrouter_expired(), parse_openrouter(), date, Free models come and go, and OpenRouter says when. An expired id 404s mid-turn,…, Prefer the number; fall back to what the vendor called it. The other two…, Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, payload() (+26 more)

### Community 203 - "to_text"
Cohesion: 0.12
Nodes (12): AsyncClient, HTMLParser, An epub is a zip of XHTML. Tags are stripped rather than parsed — the same call…, _read_epub(), Readable text from a page, truncated on a word boundary., Strip a page to its readable text. Not readability, not an article extractor,…, _Reader, to_text() (+4 more)

### Community 209 - "ask_user"
Cohesion: 0.15
Nodes (15): a_question(), broker(), fixture, MonkeyPatch, `summary` is the only field the model sees., **`ok=False` would make her apologise for his silence.** Nothing went wrong; he…, Unreachable in the app, but a tool that raises fails the whole turn and this…, A stand-in for `runtime.questions`, recording what it was asked. (+7 more)

### Community 211 - "parametrize"
Cohesion: 0.25
Nodes (9): parametrize, test_ordinary_targets_are_not_refused(), test_ordinary_urls_are_not_flagged(), test_password_shaped_targets_are_refused(), test_role_name_strips_the_leading_article_and_trailing_noun(), A hard block, not a dialog — see the module docstring. Reads only the call's…, the Send button" -> "Send" — a role lookup wants the label, not the description…, _refuse_password_field() (+1 more)

### Community 212 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.29
Nodes (5): DURATION, EASE, SPRING, stagger, TWEEN

### Community 244 - "clipboard.py"
Cohesion: 0.15
Nodes (16): _key_sender(), _paste_text(), Build the one-keystroke `SendInput` wrapper. A factory rather than module-level…, One modified keypress — modifier down, key down, key up, modifier up. Only…, Put `text` on the clipboard, send one Ctrl+V, then put the clipboard back.…, _send_chord(), tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,… (+8 more)

### Community 245 - "extract_text"
Cohesion: 0.40
Nodes (5): extract_text(), Whatever text this file has, or "" if it has none worth having. **Never…, _read_pdf(), The two entry points differ on purpose. One corrupt PDF in Downloads must not…, test_extract_text_never_raises_for_the_background_sweep()

### Community 246 - "conversation.py"
Cohesion: 0.06
Nodes (37): ConversationHistory, ProviderRegistry, BaseModel, datetime, Turn orchestration (BUILD_SPEC §9 Phase 1). One turn: persist the user message,…, `chat.send` result (§7.1)., Providers keyed by name, so the service can follow the router's choice., `chat.history` result. Typed at the boundary per CLAUDE.md rule 7. (+29 more)

### Community 247 - "broker"
Cohesion: 0.50
Nodes (5): broker(), fixture, MonkeyPatch, Stands in for `runtime.questions`, recording exactly what was shown., wired()

### Community 248 - "OpenRouterProvider"
Cohesion: 0.07
Nodes (25): _as_int(), OpenRouterProvider, Any, Headers, RateLimitState, OpenAI's wire format, someone else's models. Subclassing rather than copying is…, Turn reasoning off where the endpoint allows it, and count the call. This is…, Reachability, and a free chance to read the quota headers. (+17 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 255 - "rpc.ts"
Cohesion: 0.29
Nodes (5): Pending, RpcEnvelope, RpcError, RpcErrorShape, RpcNotification

### Community 256 - "_parse_yes_no"
Cohesion: 0.50
Nodes (4): _parse_yes_no(), True/False for a clearly affirmative/negative one-line reply, else None — an…, parametrize, test_parse_yes_no()

### Community 257 - "is_stated_intention"
Cohesion: 0.67
Nodes (4): is_stated_intention(), parametrize, test_intention_shaped_messages_are_recognised(), test_ordinary_messages_are_not_intentions()

### Community 259 - "TranscriptionUnavailable"
Cohesion: 0.22
Nodes (8): pcm16_to_float32(), ndarray, RuntimeError, Load and warm. First use downloads ~150MB, which must not happen while someone…, One utterance to text. Empty string when nothing was said., Speech input could not start. Never fatal — she still reads typing., Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., TranscriptionUnavailable

### Community 260 - "tools_trust_all_drives"
Cohesion: 0.50
Nodes (4): _enumerate_drives(), Every fixed drive letter Windows reports, as root paths ("C:\\").…, Trust every drive letter on the machine, in one call. The direct answer to…, tools_trust_all_drives()

### Community 262 - "Launch"
Cohesion: 0.67
Nodes (3): Launch, StrEnum, How an entry has to be started. Three sources, three launchers.

### Community 265 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 272 - "online"
Cohesion: 0.25
Nodes (8): online(), fixture, MonkeyPatch, The whole point of `SearchUnavailable` carrying a message., Online mode on, with a stubbed search behind it., Belt to `_tool_schemas`' braces. `allow_danger_tools` was dead for a whole…, test_it_refuses_when_online_mode_is_off(), test_no_key_says_which_key_and_where()

### Community 274 - "grade"
Cohesion: 0.33
Nodes (6): grade(), Why this reply fails, or an empty list. The same two-part judgement…, The fixture the whole file rests on, checked against the real probes. Without…, `universal_failures` applies here as it does in every other category. Running…, test_a_reply_that_leaks_the_prompt_fails_even_when_correct(), test_the_perfect_model_answers_every_probe()

## Knowledge Gaps
- **339 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+334 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **65 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_reflection.py`, `test_tts.py`, `test_procedures.py`, `test_proactivity.py`, `ConversationStore`, `main.py`, `SemanticMemory`, `test_study_tools.py`, `RoutingLog`, `GenerationOptions`, `test_db.py`, `_seed`, `ConversationService`, `Candidate`, `test_curriculum.py`, `test_conversation.py`, `Settings`, `SpeechStream`, `test_affect.py`, `EpisodicMemory`, `affect.py`, `memory/study.py`, `study_begin`, `Indexer`, `soak_conversation.py`, `ProactivityScheduler`, `AffectState`, `conversation.py`, `broker`, `ModelVerdict`, `_repeated_failures`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `test_tts.py`, `KokoroTTS`, `ModelInfo`, `test_modes.py`, `ConversationStore`, `main.py`, `HealthTracker`, `RoutingLog`, `Router`, `Database`, `Tier`, `GenerationOptions`, `Listener`, `ToolContext`, `LoopState`, `Event`, `test_conversation.py`, `ChatMessage`, `SpeechStream`, `ProviderRateLimited`, `registry.py`, `soak_conversation.py`, `_start_conversation`, `ProviderUnavailable`, `conversation.py`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `Launch`, `_Semantic`, `finder.py`, `apps.py`, `test_screen.py`, `test_study_tools.py`, `test_organize.py`, `Tier`, `ConversationService`, `LoopState`, `SpeechStream`, `test_tools.py`, `test_research.py`, `StubSearch`, `ask_user`, `memory.py`, `study_begin`, `_suppress_close_errors`, `registry.py`, `browser.py`, `FakeLocator`, `test_browser.py`, `BrowserUnavailable`, `clipboard.py`, `conversation.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 58 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 58 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._