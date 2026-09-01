# Graph Report - ARIA  (2026-09-01)

## Corpus Check
- 329 files · ~486,276 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 6591 nodes · 14922 edges · 353 communities (273 shown, 80 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1177 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d91bf87e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_permissions.py
- test_listener.py
- main.ts
- KokoroTTS
- test_rpc.py
- test_conversation.py
- ConversationService
- undo.py
- Database
- test_scheduler.py
- EventStreamDecoder
- discovery.py
- AssistantState
- RecordingBus
- finder.py
- apps.py
- Indexer
- FakeProvider
- context.py
- test_episodic.py
- MonkeyPatch
- HealthTracker
- SemanticMemory
- test_screen.py
- WakeMode
- test_ollama_supervisor.py
- AvailabilityService
- test_extract.py
- Any
- test_study_tools.py
- RoutingLog
- test_organize.py
- Router
- test_router.py
- _clean_overlay
- Tier
- test_curriculum.py
- test_retrieval.py
- Listener
- test_catalog.py
- AdoptionService
- test_focus.py
- test_sigv4.py
- ARIA — Project Instructions
- attachments.py
- test_modes.py
- speech_text
- test_proactivity.py
- Question
- test_study_export.py
- eval_quality.py
- test_text.py
- test_reminders.py
- test_bedrock.py
- compilerOptions
- test_clipboard_history.py
- Connectivity
- ProviderUnavailable
- Event
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- system.py
- compilerOptions
- RpcMethodError
- diagnostics.py
- OllamaEmbeddings
- test_tools.py
- test_vectors.py
- test_attachments.py
- setup.py
- test_diagnostics.py
- test_affect.py
- ScriptedSTT
- FakePage
- EventBus
- semantic.py
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- extract.py
- test_adoption.py
- memory/study.py
- MonkeyPatch
- OpenAIProvider
- FilesPanel.tsx
- Sidecar
- Client
- test_ask.py
- Client
- gate_name.py
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- SpeechStream
- Utterance
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- test_research.py
- GenerationOptions
- PermissionEngine
- browser.py
- FilesPanel.test.tsx
- AppEntry
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- ProviderRegistry
- bedrock.py
- render
- gate_organize.py
- ConversationStore
- HistoryPanel.tsx
- CLAUDE.md — ARIA Project Instructions (Claude Code-facing)
- Router — local vs cloud, then which provider
- gate_affect.py
- test_openrouter.py
- AffectState
- usePermissionMode.ts
- test_spoken_answers.py
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- gate_research.py
- _cloud_model
- SettingsPanel.tsx
- Updater
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
- rpc.ts
- useAskQuestion.ts
- probes.py
- gate_agent.py
- conversation.py
- MemoryPanel.tsx
- She holds a conversation now (2026-08-07)
- Measuring answer quality
- Smart mode: it was the tool, and then it was the router (2026-08-12)
- EpisodicMemory
- is_casual
- App.tsx
- ModelPicker.test.tsx
- ToolCallCard.tsx
- VoiceAura.tsx
- ScreenRim.tsx
- Phase 8 — she has moods, and does not go quiet forever (2026-08-14)
- Phase 2 — Voice
- test_context.py
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
- StreamDelta
- test_reflection.py
- Settings
- ChatMessage
- HealthReport
- TranscriptionUnavailable
- files_browse
- test_usage.py
- packaging.test.ts
- @types/react
- @types/react-dom
- main.py
- soak_conversation.py
- schemas
- @vitejs/plugin-react
- Retriever
- sidecar/__init__.py
- persona/__init__.py
- overhead_tokens
- test_tts.py
- ModelInfo
- test_email.py
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
- WebSearch
- react
- PersonaLevel
- CredentialKey
- OpenRouterProvider
- tokens.js
- test_browser_setup.py
- parametrize
- email.py
- useConversation.test.ts
- make_app_icon.py
- spawn
- _proactivity_service
- _attached_this_turn
- rpc
- test_browser.py
- configure_logging
- eval/__init__.py
- RateLimitState
- _require_memory
- study_begin
- @types/ws
- Client
- sidecar.test.ts
- _start_conversation
- ARIA — Assistant Message Rendering Layer
- StudyPanel.test.tsx
- database
- BedrockCredentials
- StudyPanel.tsx
- BrowserUnavailable
- code_only
- useStudy.ts
- _looks_like_a_commit_action
- IO
- MonkeyPatch
- default_app
- FirstRun.tsx
- ActivityPanel.tsx
- _body_of
- @types/node
- useFirstRun.ts
- SubModeSelector.tsx
- ToolContext
- useFirstRun.test.ts
- test_version.py
- Sidebar.test.tsx
- test_a_study_chat_is_study_from_the_moment_it_is_opened
- _study_id
- StudySubMode
- ActivityPanel.test.tsx
- _suppress_close_errors
- _bedrock_class
- ClipboardPanel.tsx
- handlers.py
- ._resolve_procedure_reply
- to_triple
- useActivity.ts
- datetime
- SubModeSelector.test.tsx
- .prune
- icon.test.ts
- _fence
- state.py
- test_a_study_submode_does_not_outlive_its_conversation
- EmailUnavailable
- test_learn_is_stored_as_an_absence
- test_a_study_chat_refuses_to_stop_being_one
- _state
- prose.ts
- postcss
- probe.py
- useClipboard.ts
- .answer_from_speech
- @testing-library/react
- .as_dict
- snapshot
- zustand
- .__init__
- grade
- client
- _send_chord
- _Semantic
- useUpdates.ts
- PanelBoundary
- Markdown.blocks.ts
- prose.test.ts
- electron-builder
- electron-vite
- look_at_the_ui.py
- framer-motion
- highlight.js
- lowlight
- remark-gfm
- unist-util-visit
- vite
- test_an_ordinary_chat_can_still_change_mode
- test_the_gate_is_the_same_probes_the_scripts_use

## God Nodes (most connected - your core abstractions)
1. `Database` - 434 edges
2. `ConversationStore` - 174 edges
3. `ConversationService` - 124 edges
4. `ToolContext` - 120 edges
5. `ChatMessage` - 116 edges
6. `HealthTracker` - 106 edges
7. `ToolResult` - 102 edges
8. `SemanticMemory` - 92 edges
9. `GenerationOptions` - 82 edges
10. `method()` - 71 edges

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

## Communities (353 total, 80 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.07
Nodes (89): engine(), Any, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has…, Rule 6, and the entry most worth having., Models get argument names wrong. That is a thing to say, not to crash on. (+81 more)

### Community 1 - "test_listener.py"
Cohesion: 0.06
Nodes (70): drain(), frame(), interrupt(), Any, Listener, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it. (+62 more)

### Community 2 - "main.ts"
Cohesion: 0.10
Nodes (29): animateBounds(), APP_ICON, applyPermissions(), bottomRightPosition(), centredExpandedBounds(), createWindow(), DATA_DIR, exportDiagnostics() (+21 more)

### Community 3 - "KokoroTTS"
Cohesion: 0.06
Nodes (34): Case, Bus, Conv, main(), Event, Listener, ndarray, Can she hold a conversation? Measured, not assumed. python… (+26 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.09
Nodes (54): _auth(), _call(), Path, The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The id is reserved, not written — so the list stays empty., CLAUDE.md rule 5: destructive operations need a confirmation round-trip., An unregistered method returns -32601, so this proves they exist., This machine's `client` fixture runs the real lifespan against a real Ollama… (+46 more)

### Community 5 - "test_conversation.py"
Cohesion: 0.06
Nodes (75): A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, _drain(), OpenEngine, Event, Path, ToolCall, Turn orchestration, cancellation, persistence and context roll-up. (+67 more)

### Community 6 - "ConversationService"
Cohesion: 0.04
Nodes (33): SessionSummary, ConversationService, ConversationMode, RoutingBias, Name the conversation once it has enough content to name. Deliberately fire-…, Hold until no turn is in flight. False if the user never stops., Ask the local model for a short label. Never raises., Persist whatever was generated — a half reply is still conversation. (+25 more)

### Community 7 - "undo.py"
Cohesion: 0.08
Nodes (49): apply(), _claim(), last_undoable(), prune_backups(), Any, Path, One timeline of things that can be taken back. `organize_folder` has had a real…, The most recent thing that can still be taken back. (+41 more)

### Community 8 - "Database"
Cohesion: 0.07
Nodes (57): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+49 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "EventStreamDecoder"
Cohesion: 0.08
Nodes (33): encode_event(), Event, EventStreamDecoder, EventStreamError, _parse_headers(), Any, AWS's binary event-stream framing, which is what Bedrock streams. Every other…, Bytes in, whole frames out. Holds the partial frame between reads.… (+25 more)

### Community 11 - "discovery.py"
Cohesion: 0.06
Nodes (64): Amazon Bedrock, end to end, against the real endpoint. python…, Cost, StrEnum, discover_all(), discover_bedrock(), discover_gemini(), discover_openai(), discover_openrouter() (+56 more)

### Community 12 - "AssistantState"
Cohesion: 0.10
Nodes (18): frames(), main(), NullConversation, NullSTT, Event, ndarray, Stage 3 gate, for the parts a machine can check. python…, say() (+10 more)

### Community 13 - "RecordingBus"
Cohesion: 0.06
Nodes (33): RuntimeError, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, Voice could not start. Never fatal — she still types., SpeechUnavailable, asyncio, The pure function above is not the fix; wiring it in is. Both mutation checks…, Feed a reply through a real stream the way tokens actually arrive., TestTheStreamActuallyUsesIt (+25 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (67): _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The…, Make `find_files` deterministic and count how often it really walks., The reason the cache exists at all — two questions in a row must not walk three… (+59 more)

### Community 15 - "apps.py"
Cohesion: 0.07
Nodes (48): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, test_type_text_refuses_empty_text(), test_type_text_refuses_when_nothing_has_focus(), _bring_to_front(), clear_type_targets(), close_app(), _closest_ratio() (+40 more)

### Community 16 - "Indexer"
Cohesion: 0.08
Nodes (34): chunk(), _digest(), Indexer, _pack(), Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, Whether this file is worth reading at all., Cheap identity: re-reading a 10MB PDF to decide whether to re-read it would… (+26 more)

### Community 17 - "FakeProvider"
Cohesion: 0.07
Nodes (48): MemoryServices, Everything Phase 5 hands to the conversation, as one argument.…, ProviderRateLimited, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, chat_mode(), Read or set a conversation's mode. Omit `mode` to read. The read-or-write shape…, FakeProvider, make_service() (+40 more)

### Community 18 - "context.py"
Cohesion: 0.11
Nodes (21): clean_title(), ConversationMode, _mode_block(), mode_done_when(), mode_label(), _persona(), datetime, StoredMessage (+13 more)

### Community 19 - "test_episodic.py"
Cohesion: 0.10
Nodes (41): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., _conversation(), _episodic(), anyio, Connection (+33 more)

### Community 20 - "MonkeyPatch"
Cohesion: 0.06
Nodes (46): _focused(), MonkeyPatch, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V…, Below the threshold, nothing touches the clipboard — it belongs to the user,…, `read_text()` returns None when the clipboard held an image or a file list.…, The last gate. Between the claim and the send sit the dialog and… (+38 more)

### Community 21 - "HealthTracker"
Cohesion: 0.06
Nodes (38): HealthTracker, ModelHealth, BaseModel, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture, Observed latency and the circuit breaker. A 429 is treated as a routing input… (+30 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.07
Nodes (49): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:… (+41 more)

### Community 23 - "test_screen.py"
Cohesion: 0.09
Nodes (47): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+39 more)

### Community 24 - "WakeMode"
Cohesion: 0.06
Nodes (22): ListenerState, StrEnum, Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3). The renderer opens the…, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, The wake model, or None in PHRASE mode - which is the default. Exposed so the…, WakeMode, _build_listener() (+14 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.07
Nodes (40): OllamaSupervisor, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was…, FakeOllama, Any, Path (+32 more)

### Community 26 - "AvailabilityService"
Cohesion: 0.11
Nodes (10): ModelAvailability, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+2 more)

### Community 27 - "test_extract.py"
Cohesion: 0.12
Nodes (32): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+24 more)

### Community 28 - "Any"
Cohesion: 0.06
Nodes (53): chat_history(), chat_send(), clipboard_history(), confirm_respond(), method(), models_adoption(), models_bedrock(), models_refresh() (+45 more)

### Community 29 - "test_study_tools.py"
Cohesion: 0.08
Nodes (56): _mapped(), Any, asyncio, quiz(), `study_begin` and `study_check`, and the state she is handed without asking.…, Study's own `ToolPolicy.READ_ONLY` caps schemas at `Tier.SAFE`. Both tools sit…, **The reason `QuizQuestion` is not `core.questions.Question`.** The broker…, Only `summary` reaches the model (§7.2), so the grade has to be in it — and the… (+48 more)

### Community 30 - "RoutingLog"
Cohesion: 0.06
Nodes (37): ModelVerdict, Any, BaseModel, What the router decided, and what the user made of it (§9.7). §9.7's closing…, Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Per-model tallies. The dataset §9.7 wants, as far as it has grown. (+29 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (73): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+65 more)

### Community 32 - "Router"
Cohesion: 0.09
Nodes (27): is_tool_shaped(), BaseModel, ModelInfo, StrEnum, A request to act on the machine rather than to talk about something., Chooses a model for a turn., Pick a model. `selected` is the user's choice — a model id, or "smart" to…, How much latency the user will trade for a better answer. (+19 more)

### Community 33 - "test_router.py"
Cohesion: 0.08
Nodes (48): is_trivial(), needs_deep_model(), A greeting or acknowledgement — nothing a 4B model can get wrong., Reasoning, code, or a multi-step request: the `smart` class earns its cost., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router… (+40 more)

### Community 35 - "Tier"
Cohesion: 0.06
Nodes (42): EscalateFn, PreviewFn, RefuseFn, test_each_tool_sits_at_its_declared_tier(), Bus, Denied, Journal, paths_in() (+34 more)

### Community 36 - "test_curriculum.py"
Cohesion: 0.11
Nodes (36): The indexed text of one file, in order, or `""` if it was never indexed. The…, source_text(), _builder(), asyncio, Turning a lecture into a concept map, and surviving what a model returns. The…, A scanned PDF or an image-only deck is a normal thing to be handed, and "no…, A subject with no concepts would render as "0 of 0 covered" forever and win…, `reflection` records why this matters: reporting the model that was *tried*… (+28 more)

### Community 37 - "test_retrieval.py"
Cohesion: 0.12
Nodes (32): FactSource, Who asserted this. Decides whether a pin can block it., anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice., `_build_context` runs once per attempt inside the failover loop, so without… (+24 more)

### Community 38 - "Listener"
Cohesion: 0.08
Nodes (21): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, Report wake scores on the bus for the next `seconds`. **Self-disarming, and…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly. (+13 more)

### Community 39 - "test_catalog.py"
Cohesion: 0.06
Nodes (47): persona_for(), Persona level for a model; unknown ids get the safe, minimal prompt., Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from., resolve_availability(), usable_ids(), adopted(), discovered() (+39 more)

### Community 40 - "AdoptionService"
Cohesion: 0.10
Nodes (23): Probe, AdoptionService, AdoptionState, _probes_by_id(), Any, BaseModel, date, datetime (+15 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "test_sigv4.py"
Cohesion: 0.08
Nodes (38): canonical_path(), canonical_request(), datetime, AWS Signature Version 4, in stdlib only (Eyaas's Bedrock key, 2026-08-23).…, Return `headers` plus `Authorization`, `X-Amz-Date` and the payload hash.…, The four nested HMACs. Derived per day, per region, per service., The path as it appears in the **canonical request**, which is not the same…, `(canonical request, signed header list)`, as plain text. `headers` must… (+30 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "attachments.py"
Cohesion: 0.13
Nodes (22): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, image / document / unsupported. Documents use `extract.ATTACHABLE`, which is…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no… (+14 more)

### Community 45 - "test_modes.py"
Cohesion: 0.05
Nodes (51): ConversationMode, StrEnum, What a mode actually *does*, as opposed to what it says. Eyaas, after using the…, A mode this turn would be better served by, or None. None is the answer for the…, Whether this turn reads like it wanted a study chat rather than this one. The…, How much of the registry a mode lets the model see. **Narrowing, never…, The highest tier this policy will show, or None for no tools., suggest() (+43 more)

### Community 46 - "speech_text"
Cohesion: 0.10
Nodes (18): _incomplete_link_start(), _open_fence_start(), Markdown, said out loud. **Nothing stripped markdown from the speech path, in…, Where an unterminated fence begins, if one does., Where a half-written inline marker begins, if one does., Where a link that has not finished arriving begins. **A link has two halves and…, Split raw model text into (safe to speak now, hold for later). **This is what…, Turn one piece of a reply into something worth hearing. Safe to call on a… (+10 more)

### Community 47 - "test_proactivity.py"
Cohesion: 0.06
Nodes (66): Candidate, default_candidates(), idle_intention_candidate(), is_stated_intention(), ProactivityScheduler, procedure_offer_candidate(), datetime, Path (+58 more)

### Community 48 - "Question"
Cohesion: 0.07
Nodes (51): Answer, Asked, normalise(), Option, Pending, BaseModel, Question, QuestionBroker (+43 more)

### Community 49 - "test_study_export.py"
Cohesion: 0.09
Nodes (39): StrEnum, Which concepts a sub-mode works over. Read by `study.render` to pick what the…, Scope, Concept, dots(), StudyState, A knowledge map as something you can keep — Markdown, or a page you print. **No…, A self-contained page. Ctrl+P is the PDF export. (+31 more)

### Community 50 - "eval_quality.py"
Cohesion: 0.10
Nodes (28): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+20 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "test_reminders.py"
Cohesion: 0.06
Nodes (54): compose(), describe_delay(), datetime, timedelta, Deliver reminders when they come due, and do not let anything stop them. **This…, How overdue a reminder is, in words, or "" when it is on time. **Said out loud…, Fires due reminders. Clock and sleep injected; no test sleeps., One pass. Returns how many were delivered. Never raises. (+46 more)

### Community 53 - "test_bedrock.py"
Cohesion: 0.13
Nodes (41): auth_headers(), Headers for one Bedrock request, by whichever credential is stored. A module…, _collect(), _event(), _no_real_credentials(), _provider(), asyncio, fixture (+33 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "test_clipboard_history.py"
Cohesion: 0.05
Nodes (54): ClipboardWatcher, _entropy(), looks_like_a_secret(), Any, Watch the clipboard, and refuse to remember the things that look like keys.…, The clipboard's change counter, or None if the call is unavailable., Records what is copied. Everything is injected so a test drives it., One pass. Never raises — a watcher that can die is worse than none. (+46 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "ProviderUnavailable"
Cohesion: 0.07
Nodes (31): HTTPError, ProviderUnavailable, The backend could not be reached — offline, not running, DNS, refused. Distinct…, OllamaProvider, _parse_pull_line(), PullProgress, Any, NamedTuple (+23 more)

### Community 58 - "Event"
Cohesion: 0.09
Nodes (28): Event, Server -> client push notifications and the set of live connections (§7.1).…, Server -> client notification methods (§7.1 events table). Only the members…, Server -> client push. No ``id``, no reply expected (§7.1 events table)., RpcNotification, _Bus, _FakeVad, _FakeWake (+20 more)

### Community 59 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (27): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+19 more)

### Community 60 - "ARIA Sidecar Runtime Dependencies (requirements.txt)"
Cohesion: 0.07
Nodes (27): ARIA Sidecar Runtime Dependencies (requirements.txt), anthropic==0.39.* (NOT adopted, Anthropic excluded), apscheduler==3.10.* (deferred, Phase 5), fastapi==0.115.*, faster-whisper==1.0.3, httpx==0.27.*, keyring==25.7.* (Windows Credential Manager), kokoro-onnx==0.4.* (+19 more)

### Community 61 - "system.py"
Cohesion: 0.14
Nodes (22): _endpoint_volume(), _facts(), get_system_info(), kill_process(), list_processes(), Any, tool, Facts about the machine, and the one knob she can turn on it. `get_system_info`… (+14 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "RpcMethodError"
Cohesion: 0.06
Nodes (33): chat_delete(), chat_rename(), clipboard_copy(), clipboard_forget(), memory_reflect(), models_bias(), models_select(), permissions_mode() (+25 more)

### Community 64 - "diagnostics.py"
Cohesion: 0.12
Nodes (24): build_report(), _credential_presence(), _environment(), export(), _health(), Any, Path, Export diagnostics — one zip a person can attach to a bug report. BUILD_SPEC §9… (+16 more)

### Community 65 - "OllamaEmbeddings"
Cohesion: 0.06
Nodes (39): Episode, BaseModel, Row, A row from `episodes`, as the panel and retrieval see it., IndexStats, _age_days(), _percentile(), datetime (+31 more)

### Community 66 - "test_tools.py"
Cohesion: 0.04
Nodes (71): parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, Overwriting is a different destructive act from moving, and the user approved a…, It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, `read_file` did a plain UTF-8 read of whatever it was given, so "what does this…, A scanned PDF with no text layer is a normal thing to be handed. Saying so…, §7.2's second failure mode: the model gets one line, the UI gets the lot. (+63 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "test_attachments.py"
Cohesion: 0.09
Nodes (39): One attachment, understood. Never raises. `budget` is how many characters of it…, The block that goes into the prompt. **Fenced as untrusted content**, exactly…, read_one(), render(), MonkeyPatch, Path, Files the user hands her. Eyaas: *"i should be also be able to file uploads…, There is no local vision model (rule 2), so no key is a real state with an… (+31 more)

### Community 69 - "setup.py"
Cohesion: 0.08
Nodes (35): main(), Download the wake word weights into data/models/openwakeword. python…, _download(), fetch_voice(), fetch_wake_word(), FetchProgress, Any, AsyncClient (+27 more)

### Community 70 - "test_diagnostics.py"
Cohesion: 0.16
Nodes (18): CredentialStatus, BaseModel, Safe-to-display description of a stored key., archive(), fixture, MonkeyPatch, Path, Export diagnostics — and the one thing it must never contain. An export exists… (+10 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "ScriptedSTT"
Cohesion: 0.09
Nodes (16): Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout., build(), _drain_windows(), FakeConversation, parts(), phrase(), Event (+8 more)

### Community 73 - "FakePage"
Cohesion: 0.08
Nodes (14): FakeLocator, FakePage, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, Refusing to act on an ambiguous-but-real description is worse than picking the…, Implements exactly the `Page` surface `browser.py` calls., test_click_risk_escalates_on_the_elements_own_wording() (+6 more)

### Community 74 - "EventBus"
Cohesion: 0.16
Nodes (9): EventBus, Any, Protocol, Minimal transport surface — a Starlette WebSocket satisfies this., Tracks connected clients and broadcasts notifications to them., Send the current state to one client, unconditionally. A reconnecting renderer…, Send a notification to every live client, dropping dead ones., Update the assistant state and notify clients if it actually changed. (+1 more)

### Community 75 - "semantic.py"
Cohesion: 0.06
Nodes (27): _now(), Return an existing session id, or create one. `kind` is only ever applied at…, Fact, MergeOutcome, normalise_triple(), _now(), Row, StrEnum (+19 more)

### Community 76 - "bridge.d.ts"
Cohesion: 0.06
Nodes (32): AriaApi, AssistantState, BrainStatus, ClipboardHistory, ClipEntry, CredentialStatus, LogLine, MemoryEpisode (+24 more)

### Community 77 - "Electron main + Python sidecar architecture"
Cohesion: 0.11
Nodes (19): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation (+11 more)

### Community 78 - "affect.py"
Cohesion: 0.17
Nodes (18): _clamp(), _drift(), _energy_delta(), _format_hour(), _hours_since_last_interaction(), datetime, Four floats that make the same question read differently at 2am than at 2pm…, Roughly `[-1, 1]` from the last few user messages. Zero — the common case —… (+10 more)

### Community 79 - "extract.py"
Cohesion: 0.10
Nodes (26): _extract_bytes(), extract_text(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as… (+18 more)

### Community 80 - "test_adoption.py"
Cohesion: 0.10
Nodes (51): ProviderQuotaExhausted, The **account's** allowance is gone, not this model's. A 429 usually means…, by_class(), The router's pool: **measured only** — curated, or adopted after passing. The…, a_model(), Asker, Clock, perfect_reply() (+43 more)

### Community 81 - "memory/study.py"
Cohesion: 0.04
Nodes (102): policy_for(), Never raises, and `None` means Learn — `modes.policy_for`'s contract., One way of running a study session., SubModePolicy, add_concepts(), delete_subject(), ensure_subject(), find_subject() (+94 more)

### Community 82 - "MonkeyPatch"
Cohesion: 0.18
Nodes (20): MonkeyPatch, _returning(), test_click_names_what_it_could_not_find(), test_click_runs_the_match_it_finds(), test_current_page_escalation_checks_the_live_page(), test_current_page_escalation_is_quiet_on_an_ordinary_page(), test_fill_risk_escalates_on_a_payment_shaped_field(), test_fill_risk_is_quiet_for_an_ordinary_field() (+12 more)

### Community 83 - "OpenAIProvider"
Cohesion: 0.10
Nodes (16): _assemble(), OpenAIProvider, Any, Headers, Response, ToolCall, No-op: cloud models have no local load step to pay for., Per-request fields this vendor accepts and OpenAI does not. A hook rather than… (+8 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "Sidecar"
Cohesion: 0.18
Nodes (3): HealthBody, Sidecar, SidecarOptions

### Community 86 - "Client"
Cohesion: 0.29
Nodes (7): Client, main(), Any, Does she ask well, and — more importantly — does she stop asking? python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Send, answer anything she waits on, and return the completed turn. `pick` is…, section()

### Community 87 - "test_ask.py"
Cohesion: 0.07
Nodes (39): a_question(), ask_tool(), broker(), fixture, MonkeyPatch, `ask_user`: the registry entry, and the schema the model has to produce. The…, **The first restriction overshot, and Eyaas caught it on screen.** Asked "can u…, Pydantic hoists nested models into `$defs` and points at them with `$ref`.… (+31 more)

### Community 88 - "Client"
Cohesion: 0.21
Nodes (12): Client, concepts_in(), main(), Any, Does Study Mode actually teach? Live, against a real sidecar. python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Answer a `question.ask` the way a student would — one pick each. **This gate…, **The payload key is `tool`, not `name`.** This read `name` and defaulted to… (+4 more)

### Community 89 - "gate_name.py"
Cohesion: 0.11
Nodes (23): clips(), main(), ndarray, Can she hear her own name? Across many voices, because one is not a test.…, score(), is_stop_word(), _near_the_name(), Is this whole utterance just a request to stop talking? (+15 more)

### Community 90 - "Sidebar.tsx"
Cohesion: 0.11
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 92 - "SpeechStream"
Cohesion: 0.10
Nodes (18): Any, ModelInfo, ToolCall, Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, What the model is allowed to know exists. None rather than an empty list when…, Run steps until a text answer, loop detection, or the step budget ends it…, Which model gets to see the tool's result. `router._PRIVATE` already keeps a…, Evict the previous local model before loading a different one. CLAUDE.md rule… (+10 more)

### Community 93 - "Utterance"
Cohesion: 0.11
Nodes (8): ndarray, Protocol, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance, VoiceActivity

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.12
Nodes (17): autoprefixer, electron, jsdom, devDependencies, autoprefixer, electron, jsdom, react-dom (+9 more)

### Community 96 - "test_research.py"
Cohesion: 0.08
Nodes (38): One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, online(), Exception, fixture, MonkeyPatch, `research(query)`, the untrusted-content boundary, and the online gate. Two… (+30 more)

### Community 97 - "GenerationOptions"
Cohesion: 0.04
Nodes (69): Measurement, Measure a discovered model well enough to let Smart route to it.…, A recommendation, not a decision. Somebody still reads the replies., build_prompt(), choose_model(), CurriculumBuilder, CurriculumOutput, CurriculumReport (+61 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "browser.py"
Cohesion: 0.12
Nodes (26): Page, test_fill_types_the_value_into_the_match(), test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), test_navigate_adds_a_scheme_when_none_was_given(), test_read_returns_cleaned_text_with_the_url(), test_screenshot_returns_a_base64_image(), browser_fill() (+18 more)

### Community 101 - "AppEntry"
Cohesion: 0.08
Nodes (29): app(), 7 zip" matched "7-Zip Help" purely because it is the shorter name., The demotion must not make the entry unreachable., Opening the wrong app is worse than opening nothing., This is what stops "open youtube" launching the YouTube Music app: the website…, `normalise("notepad++")` is `"notepad"`, which scored an exact 1.00 against the…, Asking for "notepad" may well mean Notepad++; the ranking can decide. Asking…, Only `+` and `#` name a different product. The 7-Zip cases depend on everything… (+21 more)

### Community 102 - "ConfirmDialog.tsx"
Cohesion: 0.16
Nodes (10): ConfirmRequest, ImagePreview, leaf(), MovePlan, MovePlanView(), Props, tail(), TIER_LABEL (+2 more)

### Community 103 - "useConversation.ts"
Cohesion: 0.27
Nodes (12): appendToStreaming(), AttachmentStatus, clearStreaming(), finalise(), loadRatings(), ToolCall, toTurns(), Turn (+4 more)

### Community 104 - "package.json"
Cohesion: 0.15
Nodes (12): author, dependencies, electron-updater, ws, description, electron-updater, license, main (+4 more)

### Community 105 - "ProviderRegistry"
Cohesion: 0.09
Nodes (20): ConversationHistory, ProviderRegistry, BaseModel, `chat.send` result (§7.1)., Providers keyed by name, so the service can follow the router's choice., `chat.history` result. Typed at the boundary per CLAUDE.md rule 7., TurnStarted, BaseModel (+12 more)

### Community 106 - "bedrock.py"
Cohesion: 0.05
Nodes (52): main(), BedrockProvider, control_url(), current_region(), fetch_control(), load_credentials(), _merge_adjacent(), Any (+44 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "ConversationStore"
Cohesion: 0.06
Nodes (43): ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, When anything was last said, in any session. The whole precondition for §9's…, A fresh id with no row behind it yet. `ensure_session` creates a row for any id…, Name a conversation. The `with conn:` is load-bearing. Python's sqlite3 opens… (+35 more)

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

### Community 114 - "test_openrouter.py"
Cohesion: 0.07
Nodes (40): _openrouter_class(), _openrouter_expired(), parse_openrouter(), date, Free models come and go, and OpenRouter says when. An expired id 404s mid-turn,…, Prefer the number; fall back to what the vendor called it. The other two…, Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, payload() (+32 more)

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "test_spoken_answers.py"
Cohesion: 0.15
Nodes (27): match_spoken(), One spoken utterance into an answer, or None if it is not one. Tried in order…, The question and its options, phrased to be heard rather than read. The "Other"…, speakable(), parametrize, _question(), Answering a question out loud. The property that makes this safe to run on…, **"I don't know" is a real answer to a quiz.** Left to the fuzzy path it would… (+19 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 121 - "_cloud_model"
Cohesion: 0.10
Nodes (21): _cloud_model(), free_model(), health(), fixture, ModelInfo, 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement… (+13 more)

### Community 122 - "SettingsPanel.tsx"
Cohesion: 0.20
Nodes (10): BEDROCK_REGIONS, BedrockState, BrowserState, KEY_HELP, KEY_LABEL, OnlineState, RowProps, SEARCH_KEYS (+2 more)

### Community 123 - "Updater"
Cohesion: 0.13
Nodes (9): api, AriaApi, BrainStatus, LogLine, SidecarEvent, Unsubscribe, Updater, UpdaterOptions (+1 more)

### Community 124 - "Client"
Cohesion: 0.15
Nodes (15): Client, main(), Any, ConversationMode, Do the six modes actually behave differently? Live, against a real sidecar.…, Send, then wait for this turn's own completion., **One reader task, everything else off a queue.** The first version called…, report() (+7 more)

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
Cohesion: 0.25
Nodes (8): scripts, build, dev, dist, dist:sidecar, sidecar, test, typecheck

### Community 137 - "core/router.py — model Router"
Cohesion: 0.33
Nodes (6): Model catalog discovery is a filtering problem, not a fetching one, routing_log table + thumbs rating implements §9.7 route auditing, _TOOL_SHAPED narrows which spoken turns route by bias vs stay local/fast, Per-model tool scoreboard: run-to-run spread exceeds inter-model gaps; TOOL_SCORE_MARGIN band added, TTFT does not scale with conversation length once KV cache prefix is byte-identical, core/router.py — model Router

### Community 138 - "rpc.ts"
Cohesion: 0.13
Nodes (14): BrainStatus, Pending, RpcEnvelope, RpcError, RpcErrorShape, RpcNotification, createTray(), ICON_PNG (+6 more)

### Community 139 - "useAskQuestion.ts"
Cohesion: 0.33
Nodes (5): AskedQuestion, GivenAnswer, PendingAsk, QuestionOption, useAskQuestion

### Community 141 - "probes.py"
Cohesion: 0.07
Nodes (42): admits_ignorance(), answers_flatly(), contains(), contains_any(), denies_capability(), exact(), excludes(), hedged() (+34 more)

### Community 142 - "gate_agent.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 6's agent loop, against the running sidecar. "find <scratch file>,…

### Community 143 - "conversation.py"
Cohesion: 0.09
Nodes (21): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Mark one step as run. `local_only` is unknown, not False, for a tool the…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through… (+13 more)

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

### Community 149 - "EpisodicMemory"
Cohesion: 0.10
Nodes (14): EpisodicMemory, _now(), datetime, StoredMessage, Writes and reads `episodes`. Never raises into the turn path., Summarize every conversation that has gone quiet. Returns how many., Summarize one session into an episode. Idempotent; never raises. `ended_at` is…, Stamp `ended_at` without writing an episode. (+6 more)

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

### Community 158 - "test_context.py"
Cohesion: 0.08
Nodes (46): machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, volatile_prefix(), full(), Machine context: the clock, the model, and what it costs to carry them. (+38 more)

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
Cohesion: 0.14
Nodes (15): CodeBlock(), COMPONENTS, classesOf(), languageFrom(), lowlight, OPT_OUT, rehypeHighlight(), textOf() (+7 more)

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

### Community 191 - "StreamDelta"
Cohesion: 0.10
Nodes (13): BaseModel, One chunk of a streaming response. `text` carries *content only*. Reasoning…, StreamDelta, _function_call_part(), GeminiProvider, Any, Response, ToolCall (+5 more)

### Community 192 - "test_reflection.py"
Cohesion: 0.08
Nodes (38): build_prompt(), _extract_json(), Any, §8.3's prompt, with the two slots filled., Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio, parametrize, The nightly §8.3 pass. Two things are load-bearing and both are about a local… (+30 more)

### Community 193 - "Settings"
Cohesion: 0.11
Nodes (16): BaseSettings, _default_data_dir(), Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly., Where her database, models and logs live. **Beside the repo in development, in… (+8 more)

### Community 194 - "ChatMessage"
Cohesion: 0.11
Nodes (21): measure_latency(), TTFT over several turns, ignoring the first., assemble(), episode_request(), Prompt asking the model to compress a whole session into an episode. Distinct…, Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, Build the final message list, stable content first., Prompt asking the model to name a conversation for the history list. (+13 more)

### Community 195 - "HealthReport"
Cohesion: 0.16
Nodes (20): dispatch(), HealthReport, _invoke(), BaseModel, Rich health snapshot for the UI (§7.1 ``system.health``, §9.6)., Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., err() (+12 more)

### Community 196 - "TranscriptionUnavailable"
Cohesion: 0.22
Nodes (8): pcm16_to_float32(), ndarray, RuntimeError, Load and warm. First use downloads ~150MB, which must not happen while someone…, One utterance to text. Empty string when nothing was said., Speech input could not start. Never fatal — she still reads typing., Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., TranscriptionUnavailable

### Community 197 - "files_browse"
Cohesion: 0.13
Nodes (17): _enumerate_drives(), files_browse(), files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, One folder's contents, for the panel. Deliberately not `list_folder`: that tool… (+9 more)

### Community 198 - "test_usage.py"
Cohesion: 0.06
Nodes (48): estimate(), for_model(), is_priced(), Rate, What a turn cost, estimated — and the word *estimated* is load-bearing.…, US dollars per million tokens., The rate for a model, or None when nobody has priced it. `local` comes from…, Cost for one turn, or None if it cannot be known. **Missing token counts are… (+40 more)

### Community 199 - "packaging.test.ts"
Cohesion: 0.29
Nodes (7): BUILDER, code(), CONFIG_PY, MAIN, PACKAGE, read(), SIDECAR

### Community 202 - "main.py"
Cohesion: 0.12
Nodes (24): FastAPI, get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds…, Use the token Electron supplied, or mint one for standalone runs. (+16 more)

### Community 203 - "soak_conversation.py"
Cohesion: 0.19
Nodes (11): concrete_tokens(), main(), novel_tokens(), Any, Event, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet. (+3 more)

### Community 204 - "schemas"
Cohesion: 0.09
Nodes (23): Collection, §7.2: "off by default" means the model is not told they exist, which is…, test_a_required_argument_is_marked_required(), test_danger_tools_are_hidden_from_the_model_by_default(), test_raising_the_ceiling_offers_them(), test_the_schema_comes_from_the_signature(), A `list[QuizQuestion]` that came out as `{"type": "object"}` with no properties…, test_the_quiz_schema_describes_the_nested_shape() (+15 more)

### Community 206 - "Retriever"
Cohesion: 0.13
Nodes (11): Task, What one turn recalled, plus what it cost., Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache. (+3 more)

### Community 209 - "overhead_tokens"
Cohesion: 0.09
Nodes (29): estimate_tokens(), fit_to_budget(), overhead_tokens(), Render remembered facts and episodes into one system message. Returns None when…, Tokens spent before the conversation even starts. Roll-up decisions must…, Drop oldest turns until the assembled prompt fits. Backstop, not policy.…, _render_memory(), retrieved_block() (+21 more)

### Community 210 - "test_tts.py"
Cohesion: 0.08
Nodes (39): ndarray, Speech synthesis — kokoro-onnx on CPU (BUILD_SPEC §9 Phase 2). CPU only, per…, Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, Load and warm. The first synthesis is ~5x slower than the rest, and the user…, shorten_for_speech(), split_for_speech() (+31 more)

### Community 211 - "ModelInfo"
Cohesion: 0.04
Nodes (69): main(), Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, Whether this endpoint may train on what is sent to it. Unknown ids read as…, _trains_on_data(), Which models are usable right now. One object answers this for both…, adopt(), adopted(), all_models() (+61 more)

### Community 212 - "test_email.py"
Cohesion: 0.11
Nodes (9): Read-only IMAP. Two properties carry this feature and both are negative: it…, Subjects arrive like this more often than not, and a summariser fed the raw…, **Email is the canonical case for §11.** A web page has to be navigated to; an…, **The subtle destructive edit.** A plain `RFC822` fetch sets `\\Seen`, so a…, Not a whitelist — somebody's own mail server has to work., test_a_mime_encoded_subject_is_decoded(), test_a_real_hostname_passes_straight_through(), test_email_is_treated_as_an_untrusted_source() (+1 more)

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.29
Nodes (5): DURATION, EASE, SPRING, stagger, TWEEN

### Community 244 - "WebSearch"
Cohesion: 0.09
Nodes (19): HTMLParser, Any, AsyncClient, Response, RuntimeError, Readable text from a page, truncated on a word boundary., Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix. (+11 more)

### Community 246 - "PersonaLevel"
Cohesion: 0.12
Nodes (23): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+15 more)

### Community 247 - "CredentialKey"
Cohesion: 0.16
Nodes (18): CredentialKey, delete_key(), get_key(), StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Credential Manager entry names under the ARIA service., Read a key, or None if unset. Never logs the value., Store a key. Callers must never log `value`. (+10 more)

### Community 248 - "OpenRouterProvider"
Cohesion: 0.14
Nodes (12): _as_int(), OpenRouterProvider, Any, Headers, OpenAI's wire format, someone else's models. Subclassing rather than copying is…, Reachability, and a free chance to read the quota headers., OpenRouter's 429 says more than OpenAI's, and it is routine here. The free tier…, The raw catalogue OpenRouter offers today. Unauthenticated on purpose —… (+4 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 255 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): _default_browser(), A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, (exe path, profile dir) for the user's actual default browser., _write_browser_launcher(), MonkeyPatch, Path, `browser.setup`'s launcher detection. The bug this guards against was real, not…, Firefox is a real default browser some people have, and CDP does not work with… (+9 more)

### Community 256 - "parametrize"
Cohesion: 0.20
Nodes (14): ConversationMode, parametrize, The guard above only ever measured NORMAL, and a mode block is part of the…, Resolved once at import, so the same configuration always yields the same bytes…, `_INSTRUCTION_PRIORITY` exists because "reply with only the number 7" once…, `_FULL` says "Short sentences; you are often spoken aloud" — which Study and…, ~150 tokens is the ceiling, raised from 130 on 2026-08-19. Eyaas asked for…, The `has_tools` bug and the `online` bug, pre-empted for the new axis: a budget… (+6 more)

### Community 257 - "email.py"
Cohesion: 0.24
Nodes (12): IMAP4_SSL, _decode(), fetch(), _fetch_one(), MailHeader, Read-only IMAP, in stdlib. `imaplib` and `email` both ship with Python, so this…, An IMAP SEARCH command. Quoted, so a query cannot inject a command., Newest first. **Blocking** — callers put it on a thread. Raises… (+4 more)

### Community 259 - "make_app_icon.py"
Cohesion: 0.17
Nodes (13): _chunk(), _geometry(), ico_bytes(), main(), _pixel(), png_bytes(), Generate resources/icon.ico — the orb, as the app icon.…, Colour and alpha at a point, in 0..1 icon coordinates. Returns straight (non-… (+5 more)

### Community 260 - "spawn"
Cohesion: 0.13
Nodes (11): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, Deliver a message with no preceding question. Called by…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, Any, Task (+3 more)

### Community 261 - "_proactivity_service"
Cohesion: 0.18
Nodes (13): _proactivity_service(), Connection, A proactive message needs somewhere to live even before the user has ever said…, A pending offer must never swallow an unrelated message as if it were a decline…, Only the very next `send()` after the offer can resolve it — a second "yes"…, _seed_procedure(), test_a_no_reply_discards_the_pending_offer(), test_a_yes_reply_confirms_the_pending_offer_without_a_model_call() (+5 more)

### Community 262 - "_attached_this_turn"
Cohesion: 0.12
Nodes (13): parametrize, The import in `tools/__init__.py` is load-bearing: the decorator runs on…, Grading matches on the option text, so a label the broker altered would make…, **The indexer cannot be a precondition for reading what he just gave.**…, test_material_matches_a_file_attached_this_turn(), test_option_labels_are_carried_through_verbatim(), test_the_tools_are_registered(), _attached_this_turn() (+5 more)

### Community 263 - "rpc"
Cohesion: 0.18
Nodes (12): bearer_from_header(), Constant-time comparison of a presented Bearer token., Extract the token from an ``Authorization: Bearer <token>`` header., token_matches(), Token-gated JSON-RPC endpoint (§7.1). The port is reachable by any browser tab…, Read/dispatch/reply until the client goes away., rpc(), _serve() (+4 more)

### Community 264 - "test_browser.py"
Cohesion: 0.08
Nodes (34): Exception, fixture, parametrize, _raising(), Browser control: the checkout/banking hard block, password refusal, and element…, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, The URL check catches the common case; a card-number field on an unlisted…, No page has loaded yet at this point — only the URL being navigated *to* is… (+26 more)

### Community 265 - "configure_logging"
Cohesion: 0.31
Nodes (8): configure_logging(), _console_handler(), _file_handler(), Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file., Install the structlog + stdlib logging bridge. Idempotent.

### Community 267 - "RateLimitState"
Cohesion: 0.17
Nodes (7): RateLimitState, Turn reasoning off where the endpoint allows it, and count the call. This is…, How much of the free daily allowance ARIA has spent, and it is a count. **The…, **Checked live on 2026-08-19, and the first version was wrong.** OpenRouter…, The header reader is kept because a 429 is documented to carry them. If a real…, test_a_stated_figure_beats_the_local_count(), test_the_free_allowance_is_counted_here_because_the_api_does_not_say()

### Community 268 - "_require_memory"
Cohesion: 0.17
Nodes (12): memory_forget(), memory_list(), memory_search(), memory_stats(), memory_update(), The memory services, or a message saying how to turn them on., Everything she has learned, for MemoryPanel. Superseded facts are excluded by…, §7.1: search what she remembers. The same path a turn uses. (+4 more)

### Community 270 - "study_begin"
Cohesion: 0.17
Nodes (12): His own answer: show it, then check. A roadmap is a claim about what he should…, The exact shape of the bug, named in the instruction that replaces it — a tool…, Provenance reaches the model, not just the database. A roadmap presented as…, A dead end is what caused this whole bug once. Naming a file she cannot find…, A subject row is not a map, and saying otherwise wastes a whole session.…, test_a_map_with_no_concepts_is_reported_as_a_failure(), test_a_named_file_that_is_missing_offers_to_plan_instead(), test_a_planned_roadmap_forbids_writing_the_options_as_letters() (+4 more)

### Community 272 - "Client"
Cohesion: 0.25
Nodes (7): Client, _copy(), main(), Any, Clipboard history, reminders, usage and explain-last-action — live. npm run dev…, Put something on the real clipboard, so the watcher sees a real change., One reader task, everything else off a queue — `gate_modes.py`'s shape.…

### Community 274 - "_start_conversation"
Cohesion: 0.08
Nodes (25): get, _build_indexer(), _build_stt(), _discover_local_models(), health(), _probe_embeddings(), Any, RoutingBias (+17 more)

### Community 275 - "ARIA — Assistant Message Rendering Layer"
Cohesion: 0.18
Nodes (10): ARIA — Assistant Message Rendering Layer, Deliverables, Design direction, Element specification, First: read the codebase before proposing anything, Hard constraints, Library direction, Out of scope (+2 more)

### Community 276 - "StudyPanel.test.tsx"
Cohesion: 0.32
Nodes (3): defaults(), state(), subject()

### Community 277 - "database"
Cohesion: 0.29
Nodes (9): conn(), database(), db_path(), Connection, fixture, Path, Shared fixtures. Every test gets a throwaway data dir — never the real data/., A migrated database on a temp path. (+1 more)

### Community 278 - "BedrockCredentials"
Cohesion: 0.25
Nodes (5): BedrockCredentials, Whichever of the two credential shapes is stored. Read once per request rather…, A signer with no secret produces a signature nobody can verify, and the failure…, test_either_credential_shape_is_usable(), test_half_an_aws_key_pair_is_not_a_credential()

### Community 281 - "BrowserUnavailable"
Cohesion: 0.22
Nodes (8): Browser, `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, test_no_user_facing_browser_error_names_chrome(), BrowserUnavailable, _connect(), RuntimeError, The browser is not reachable over CDP. Carries the fix, same shape as…, The live `Browser`, connecting on first use. Raises `BrowserUnavailable`.

### Community 282 - "code_only"
Cohesion: 0.29
Nodes (7): ModuleType, code_only(), A module's source with every comment and string literal removed. **A plain…, Rule 5 names sending as destructive. There is no SMTP to guard., `STORE` sets flags and `EXPUNGE` deletes. Neither appears., test_nothing_here_can_change_a_mailbox(), test_nothing_here_can_send()

### Community 284 - "_looks_like_a_commit_action"
Cohesion: 0.22
Nodes (9): Locator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught(), test_commit_wording_in_the_visible_text_is_caught(), _looks_like_a_commit_action() (+1 more)

### Community 285 - "IO"
Cohesion: 0.20
Nodes (8): IO, Import every optional subsystem and say plainly which ones are broken. **This…, Run every check. Returns the process exit code., The Silero weights faster-whisper ships as package data. Nothing imports this…, Loading the extension, not merely importing the wrapper — the wrapper is pure…, run(), _sqlite_vec(), _vad_asset()

### Community 286 - "MonkeyPatch"
Cohesion: 0.31
Nodes (9): broker(), exam(), planner(), fixture, MonkeyPatch, Stands in for `runtime.questions`, recording exactly what was shown., Put the session into Exam, through the real `ConversationService` API rather…, Stand in for the model call, so this tests the tool rather than a 7B. (+1 more)

### Community 287 - "default_app"
Cohesion: 0.22
Nodes (9): test_a_real_name_is_not_treated_as_a_category(), default_app(), _entry_for_prog_id(), The ProgId the user picked for this association, if they picked one., Turn a ProgId into something launchable. Three shapes, in the order they are…, The user's chosen handler for a category word, or None if not a category.…, Give a resolved default the name the Start menu already has for it. Some…, _readable() (+1 more)

### Community 290 - "ActivityPanel.tsx"
Cohesion: 0.29
Nodes (7): clock(), Reminders(), thousands(), Timeline(), Today(), TurnRow(), whenever()

### Community 291 - "_body_of"
Cohesion: 0.40
Nodes (5): Message, _body_of(), The plain-text part, or the HTML stripped down to something readable., Tags out, entities in. The same trade `providers/search.py` already made: a…, _strip_html()

### Community 293 - "useFirstRun.ts"
Cohesion: 0.22
Nodes (8): CALIBRATE_FOR_S, DEFAULT_MODEL, MicState, SetupProgress, SetupState, useFirstRun, WakeScore, WakeState

### Community 295 - "ToolContext"
Cohesion: 0.04
Nodes (93): test_with_no_mailbox_configured_it_says_what_to_add(), _paste_text(), Put `text` on the clipboard, send one Ctrl+V, then put the clipboard back.…, `ask_user` — put the choice on screen instead of describing it. The mechanism,…, tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, Read what was copied recently. Args: count: How many entries to look back over,… (+85 more)

### Community 296 - "useFirstRun.test.ts"
Cohesion: 0.40
Nodes (3): EMPTY_STATE, Listener, listeners

### Community 297 - "test_version.py"
Cohesion: 0.21
Nodes (14): _detect_version(), The version this build is part of, from whichever source can know it. **Three…, _package_version(), MonkeyPatch, Path, One version, reported by two processes that cannot see each other.…, **Derived, not restated.** The first version of this asserted the *literal*…, `--selftest` on the bundled exe is exactly this: frozen, no Electron, and no… (+6 more)

### Community 300 - "_study_id"
Cohesion: 0.25
Nodes (8): A row id off the wire. The panel always sends one; anything else is a caller…, Rename a subject. Not cosmetic — the name is what resuming matches on. `ok:…, Delete a subject, its map, and every answer recorded against it. **The…, Put one concept back to never-introduced. One click, where deleting a subject…, study_forget(), _study_id(), study_rename(), study_reset()

### Community 301 - "StudySubMode"
Cohesion: 0.25
Nodes (8): parse(), How a study session is being run right now, as opposed to what it is about.…, A sub-mode name off the wire, or `None` for anything unrecognised. Lenient…, The six. `LEARN` is the default and behaves exactly as Study did before sub-…, StudySubMode, parametrize, A sub-mode with no opener is a button that sends nothing., test_every_sub_mode_has_a_policy_and_an_opener()

### Community 302 - "ActivityPanel.test.tsx"
Cohesion: 0.32
Nodes (3): mockBridge(), usage(), withTimeline()

### Community 303 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 304 - "_bedrock_class"
Cohesion: 0.29
Nodes (7): _bedrock_class(), _bedrock_tokens(), A model id split into the words a name is actually made of.…, parametrize, Dots, dashes and colons all at once, in one id., test_a_model_is_classified_by_whole_tokens_not_substrings(), test_an_id_is_split_on_every_separator_bedrock_uses()

### Community 305 - "ClipboardPanel.tsx"
Cohesion: 0.60
Nodes (3): clock(), Entry(), preview()

### Community 307 - "handlers.py"
Cohesion: 0.10
Nodes (24): browser_setup(), build_health(), _cdp_reachable(), chat_cancel(), chat_new(), chat_sessions(), models_list(), JSON-RPC method registry and dispatch (BUILD_SPEC §7.1). Phase 0 registers only… (+16 more)

### Community 308 - "._resolve_procedure_reply"
Cohesion: 0.33
Nodes (5): _parse_yes_no(), True/False for a clearly affirmative/negative one-line reply, else None — an…, The other half of "offer once, wait for a yes" (Part 2). Returns a completed…, parametrize, test_parse_yes_no()

### Community 309 - "to_triple"
Cohesion: 0.29
Nodes (7): People say "remember that ..." to a thing whose job is remembering., The fallback is not a failure: the fact stays retrievable and the panel can fix…, test_a_lead_in_is_stripped(), test_an_unrecognised_phrasing_is_still_kept(), test_common_phrasings_become_real_predicates(), Parse a plain sentence into (subject, predicate, object). The fallback is…, to_triple()

### Community 313 - ".prune"
Cohesion: 0.40
Nodes (3): datetime, Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days.

### Community 314 - "icon.test.ts"
Cohesion: 0.29
Nodes (3): Entry, EXPECTED_SIZES, ICON

### Community 315 - "_fence"
Cohesion: 0.50
Nodes (4): test_the_mail_is_fenced_as_data_before_and_after(), test_the_unread_state_is_shown_per_message(), _fence(), The mail, labelled as data. §11, and here it earns its keep. Before *and* after…

### Community 316 - "state.py"
Cohesion: 0.04
Nodes (60): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Apply one migration file atomically and stamp `user_version`. The vec0 virtual… (+52 more)

### Community 318 - "EmailUnavailable"
Cohesion: 0.67
Nodes (3): EmailUnavailable, RuntimeError, Could not reach or sign in to the mailbox. Carries what to do next.

### Community 321 - "_state"
Cohesion: 0.33
Nodes (6): StudyState, **Observed live, and it is the worst failure this project has.** Asked "how…, The two cases are not the same falsehood. A planned roadmap has no file behind…, _state(), test_a_planned_roadmap_says_there_is_no_document_to_quote(), test_the_block_says_the_map_is_the_boundary_of_the_material()

### Community 322 - "prose.ts"
Cohesion: 0.40
Nodes (4): CODE_FOLD_LINES, PROSE, PROSE_BODY, PROSE_MEASURE

### Community 324 - "probe.py"
Cohesion: 0.67
Nodes (3): main(), Diagnose the frozen-only "cannot load module more than once per process". **Not…, show()

### Community 329 - "snapshot"
Cohesion: 0.25
Nodes (9): fixture, A registry with one tool per tier, put back exactly as found. The snapshot…, _tools(), clear(), A copy of the registry, for tests that install their own tools. Paired with…, Put back what `snapshot` took. For tests only., Empty the registry. For tests only, and only with `restore` after it., restore() (+1 more)

### Community 331 - ".__init__"
Cohesion: 0.50
Nodes (3): Path, Start `ollama serve` as its own process, with no console window. Detached on…, _spawn_detached()

### Community 332 - "grade"
Cohesion: 0.25
Nodes (8): Rules every reply obeys, regardless of what was asked., universal_failures(), grade(), Why this reply fails, or an empty list. The same two-part judgement…, The fixture the whole file rests on, checked against the real probes. Without…, `universal_failures` applies here as it does in every other category. Running…, test_a_reply_that_leaks_the_prompt_fails_even_when_correct(), test_the_perfect_model_answers_every_probe()

### Community 333 - "client"
Cohesion: 0.50
Nodes (4): client(), fixture, MonkeyPatch, App wired to a temp data dir and a known token, via the real env path.

### Community 334 - "_send_chord"
Cohesion: 0.50
Nodes (4): _key_sender(), Build the one-keystroke `SendInput` wrapper. A factory rather than module-level…, One modified keypress — modifier down, key down, key up, modifier up. Only…, _send_chord()

### Community 337 - "PanelBoundary"
Cohesion: 0.25
Nodes (3): PanelBoundary, Props, State

### Community 339 - "prose.test.ts"
Cohesion: 0.50
Nodes (3): code, SOURCE, values

### Community 342 - "look_at_the_ui.py"
Cohesion: 0.38
Nodes (6): _chromium(), main(), Look at the UI, without taking over anybody's screen. npm run dev # in another…, Stream `text` into the open turn and report what the frames did., Playwright's own Chromium, whichever build is installed. Its Python package…, _replay()

## Knowledge Gaps
- **416 isolated node(s):** `DATA_DIR`, `startHidden`, `APP_ICON`, `sidecar`, `updater` (+411 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **80 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_conversation.py`, `ConversationService`, `undo.py`, `_proactivity_service`, `_attached_this_turn`, `RecordingBus`, `study_begin`, `conversation.py`, `Indexer`, `FakeProvider`, `test_episodic.py`, `EpisodicMemory`, `SemanticMemory`, `database`, `test_study_tools.py`, `RoutingLog`, `MonkeyPatch`, `test_curriculum.py`, `test_retrieval.py`, `test_proactivity.py`, `test_study_export.py`, `test_reminders.py`, `test_clipboard_history.py`, `state.py`, `test_reflection.py`, `OllamaEmbeddings`, `test_usage.py`, `test_affect.py`, `main.py`, `soak_conversation.py`, `semantic.py`, `affect.py`, `memory/study.py`, `test_tts.py`, `SpeechStream`, `GenerationOptions`, `ProviderRegistry`, `ConversationStore`, `AffectState`, `_repeated_failures`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `ConversationService`, `test_browser.py`, `finder.py`, `conversation.py`, `apps.py`, `study_begin`, `test_screen.py`, `BrowserUnavailable`, `test_study_tools.py`, `test_organize.py`, `Tier`, `_suppress_close_errors`, `system.py`, `test_tools.py`, `FakePage`, `_Semantic`, `memory/study.py`, `MonkeyPatch`, `test_email.py`, `test_ask.py`, `SpeechStream`, `test_research.py`, `browser.py`, `AppEntry`, `ProviderRegistry`, `test_browser_setup.py`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `spawn`, `test_conversation.py`, `_proactivity_service`, `Database`, `AssistantState`, `RecordingBus`, `conversation.py`, `FakeProvider`, `_start_conversation`, `HealthTracker`, `WakeMode`, `RoutingLog`, `Router`, `Tier`, `Listener`, `ToolContext`, `StudySubMode`, `test_modes.py`, `._resolve_procedure_reply`, `ProviderUnavailable`, `Event`, `state.py`, `ChatMessage`, `EventBus`, `soak_conversation.py`, `main.py`, `Retriever`, `test_tts.py`, `ModelInfo`, `test_ask.py`, `SpeechStream`, `GenerationOptions`, `ProviderRegistry`, `ConversationStore`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `ToolContext` (e.g. with `ConversationHistory` and `ConversationService`) actually correct?**
  _`ToolContext` has 29 INFERRED edges - model-reasoned connections that need verification._