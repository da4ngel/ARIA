# Graph Report - ARIA  (2026-08-29)

## Corpus Check
- 305 files · ~442,845 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 6262 nodes · 14336 edges · 332 communities (250 shown, 82 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1142 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4183eb44`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_permissions.py
- test_listener.py
- main.ts
- for_provider
- test_rpc.py
- test_reflection.py
- test_attachments.py
- undo.py
- Database
- test_scheduler.py
- EventStreamDecoder
- test_discovery.py
- EventBus
- state
- finder.py
- apps.py
- Indexer
- OpenWakeWord
- test_modes.py
- ConversationStore
- memory/study.py
- HealthTracker
- SemanticMemory
- test_screen.py
- main.py
- test_ollama_supervisor.py
- test_router.py
- test_extract.py
- handlers.py
- test_study_tools.py
- RoutingLog
- test_organize.py
- Router
- assemble
- catalog.py
- Tier
- conversation.py
- test_openrouter.py
- Listener
- test_db.py
- AdoptionService
- test_focus.py
- test_sigv4.py
- ARIA — Project Instructions
- test_reminders.py
- ConversationService
- ToolContext
- test_proactivity.py
- test_questions.py
- test_study_export.py
- ChatMessage
- test_text.py
- proactivity.py
- test_bedrock.py
- compilerOptions
- test_clipboard_history.py
- Connectivity
- test_conversation.py
- OpenAIProvider
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- test_episodic.py
- compilerOptions
- test_browser_setup.py
- retrieved_block
- OllamaEmbeddings
- test_tools.py
- test_vectors.py
- test_context.py
- BrowserUnavailable
- ModelInfo
- test_affect.py
- VoiceActivity
- test_research.py
- test_spoken_answers.py
- .upsert
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- FakeProvider
- test_adoption.py
- test_study_modes.py
- discovery.py
- configure_logging
- FilesPanel.tsx
- Sidecar
- Client
- test_ask.py
- Client
- WhisperSTT
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- test_retrieval.py
- soak_conversation.py
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- FakeLocator
- Runtime
- PermissionEngine
- ProviderUnavailable
- FilesPanel.test.tsx
- protocol.py
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- test_browser.py
- spawn
- render
- gate_organize.py
- Question
- HistoryPanel.tsx
- CLAUDE.md — ARIA Project Instructions (Claude Code-facing)
- Router — local vs cloud, then which provider
- gate_affect.py
- Utterance
- AffectState
- usePermissionMode.ts
- GenerationOptions
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- gate_research.py
- OllamaProvider
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
- rpc.ts
- useAskQuestion.ts
- probes.py
- gate_agent.py
- extract.py
- MemoryPanel.tsx
- She holds a conversation now (2026-08-07)
- Measuring answer quality
- Smart mode: it was the tool, and then it was the router (2026-08-12)
- test_the_system_prompt_leaves_the_conversation
- is_casual
- App.tsx
- ModelPicker.test.tsx
- ToolCallCard.tsx
- VoiceAura.tsx
- ScreenRim.tsx
- Phase 8 — she has moods, and does not go quiet forever (2026-08-14)
- Phase 2 — Voice
- FakeSettings
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
- search.py
- electron-vite
- framer-motion
- EpisodicMemory
- QuestionBroker
- remark-gfm
- files_rename
- @testing-library/react
- test_probes.py
- @types/react
- @types/react-dom
- OpenRouterProvider
- WebSearch
- vite
- @vitejs/plugin-react
- vitest
- sidecar/__init__.py
- persona/__init__.py
- Retriever
- test_tts.py
- PersonaLevel
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
- system.py
- test_usage.py
- StreamDelta
- describe
- strip_wake_word
- tokens.js
- auth_headers
- RateLimitState
- email.py
- useConversation.test.ts
- make_app_icon.py
- set_discovered
- memory.py
- estimate
- test_curriculum.py
- snapshot
- _locate
- eval/__init__.py
- postcss
- broker
- rehype-highlight
- @types/ws
- Client
- browser.py
- ProactivityScheduler
- files_browse
- StudyPanel.test.tsx
- _cloud_model
- test_half_an_aws_key_pair_is_not_a_credential
- StudyPanel.tsx
- _parse_yes_no
- code_only
- useStudy.ts
- _port_is_free
- .record
- _looks_like_checkout
- .reset
- _json_type
- ActivityPanel.tsx
- _body_of
- @types/node
- Any
- SubModeSelector.tsx
- _Semantic
- .prune
- routing_log.py
- Sidebar.test.tsx
- .add_message
- clipboard_copy
- _no_real_credentials
- ActivityPanel.test.tsx
- _suppress_close_errors
- context.py
- ClipboardPanel.tsx
- datetime
- payload
- Any
- useActivity.ts
- _reset_connection
- SubModeSelector.test.tsx
- electron-builder
- icon.test.ts
- _fence
- autoprefixer
- test_the_gate_is_the_same_probes_the_scripts_use
- EmailUnavailable
- zustand
- test_a_tool_result_with_no_output_still_says_something
- test_the_registry_schema_becomes_a_tool_spec
- test_read_is_named_as_an_untrusted_source
- react-dom
- probe.py
- useClipboard.ts
- .clear_rating
- test_a_model_is_classified_by_whole_tokens_not_substrings
- .as_dict
- test_consecutive_tool_results_merge_into_one_turn
- pcm16_to_float32
- test_an_id_is_split_on_every_separator_bedrock_uses

## God Nodes (most connected - your core abstractions)
1. `Database` - 431 edges
2. `ConversationStore` - 173 edges
3. `ConversationService` - 124 edges
4. `ToolContext` - 119 edges
5. `ChatMessage` - 115 edges
6. `HealthTracker` - 106 edges
7. `ToolResult` - 102 edges
8. `SemanticMemory` - 92 edges
9. `GenerationOptions` - 81 edges
10. `Role` - 69 edges

## Surprising Connections (you probably didn't know these)
- `AGENTS.md — ARIA Project Instructions (Codex-facing)` --semantically_similar_to--> `CLAUDE.md — ARIA Project Instructions (Claude Code-facing)`  [INFERRED] [semantically similar]
  AGENTS.md → CLAUDE.md
- `Overlay page paints no background of its own` --semantically_similar_to--> `No CSP meta tag; main.ts sets the header per-environment`  [INFERRED] [semantically similar]
  overlay.html → index.html
- `Result` --uses--> `Probe`  [INFERRED]
  scripts/eval_quality.py → sidecar/eval/probes.py
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

## Communities (332 total, 82 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (110): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+102 more)

### Community 1 - "test_listener.py"
Cohesion: 0.06
Nodes (69): drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on… (+61 more)

### Community 2 - "main.ts"
Cohesion: 0.14
Nodes (23): animateBounds(), APP_ICON, bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt (+15 more)

### Community 3 - "for_provider"
Cohesion: 0.20
Nodes (11): build_all(), for_provider(), A client for one provider. Raises on anything unrecognised. **Never a…, Every provider, keyed by name — the shape `ProviderRegistry` wants. Built by…, Adding a provider obliges five other places to learn about it. CLAUDE.md…, `for_provider` raises rather than defaulting, deliberately — a fall-through…, `ModelPicker.tsx` maps over `PROVIDER_ORDER` to draw its groups, and its own…, test_an_unknown_provider_is_an_error_not_a_default() (+3 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.08
Nodes (57): method_names(), _auth(), _call(), client(), fixture, MonkeyPatch, parametrize, Path (+49 more)

### Community 5 - "test_reflection.py"
Cohesion: 0.08
Nodes (40): build_prompt(), choose_model(), _extract_json(), Any, §8.3's prompt, with the two slots filled., §8.3: cloud if a key is present, local otherwise. Walks SMART then BALANCED,…, Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio (+32 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.05
Nodes (69): IO, Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, image / document / unsupported. Documents use `extract.ATTACHABLE`, which is…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,… (+61 more)

### Community 7 - "undo.py"
Cohesion: 0.08
Nodes (49): apply(), _claim(), last_undoable(), prune_backups(), Any, Path, One timeline of things that can be taken back. `organize_folder` has had a real…, The most recent thing that can still be taken back. (+41 more)

### Community 8 - "Database"
Cohesion: 0.08
Nodes (50): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+42 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "EventStreamDecoder"
Cohesion: 0.08
Nodes (32): encode_event(), Event, EventStreamDecoder, EventStreamError, _parse_headers(), Any, AWS's binary event-stream framing, which is what Bedrock streams. Every other…, Bytes in, whole frames out. Holds the partial frame between reads.… (+24 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.09
Nodes (33): _openai_label(), parse_openai(), Whether this id is a dated snapshot of something already in the list. Only when…, `gpt-5.6-luna` -> `GPT-5.6 Luna`, `gpt-4o` -> `GPT-4o`. Cosmetic and never…, Chat models from a `GET /v1/models` body., _undated(), gemini_ids(), _load() (+25 more)

### Community 12 - "EventBus"
Cohesion: 0.05
Nodes (47): Case, Bus, Conv, main(), Event, ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the… (+39 more)

### Community 13 - "state"
Cohesion: 0.10
Nodes (40): Write the fact and its vector in one transaction. One transaction is not…, add_concepts(), ensure_subject(), _next_level(), Find or create a subject by name, returning its id. `source_path` is filled in…, Add `(name, summary)` pairs to a subject's map, in order. **Additive, never a…, The whole map with its mastery, in one read., One answer's effect on a level. **A level is a running score, not a verdict on… (+32 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (71): _pack(), sqlite-vec takes raw little-endian float32., Nearest chunks to `query`, as (path, text, distance)., search_chunks(), _counting_scan(), f(), MonkeyPatch, parametrize (+63 more)

### Community 15 - "apps.py"
Cohesion: 0.04
Nodes (79): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, `normalise("notepad++")` is `"notepad"`, which scored an exact 1.00 against the…, Asking for "notepad" may well mean Notepad++; the ranking can decide. Asking…, Only `+` and `#` name a different product. The 7-Zip cases depend on everything…, test_a_shared_symbol_still_matches(), test_hyphens_and_dots_are_still_noise(), test_punctuation_that_names_a_different_product_is_not_folded_away() (+71 more)

### Community 16 - "Indexer"
Cohesion: 0.09
Nodes (31): chunk(), _digest(), Indexer, IndexStats, Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, Whether this file is worth reading at all., Cheap identity: re-reading a 10MB PDF to decide whether to re-read it would… (+23 more)

### Community 17 - "OpenWakeWord"
Cohesion: 0.07
Nodes (20): main(), Download the wake word weights into data/models/openwakeword. python…, _build_listener(), Hands-free listening. Built eagerly rather than warmed in a task: the VAD loads…, missing_models(), OpenWakeWord, Any, ndarray (+12 more)

### Community 18 - "test_modes.py"
Cohesion: 0.05
Nodes (52): policy_for(), ConversationMode, The policy, or Normal's. Never raises. A mode arriving from a stale client is a…, A mode this turn would be better served by, or None. None is the answer for the…, Whether this turn reads like it wanted a study chat rather than this one. The…, suggest(), suggests_study_chat(), ConversationMode (+44 more)

### Community 19 - "ConversationStore"
Cohesion: 0.06
Nodes (44): The message store, for callers that need to resolve a session id., ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, When anything was last said, in any session. The whole precondition for §9's…, A fresh id with no row behind it yet. `ensure_session` creates a row for any id… (+36 more)

### Community 20 - "memory/study.py"
Cohesion: 0.07
Nodes (33): StrEnum, How a study session is being run right now, as opposed to what it is about.…, Which concepts a sub-mode works over. Read by `study.render` to pick what the…, One way of running a study session., Scope, SubModePolicy, Concept, concept_by_name() (+25 more)

### Community 21 - "HealthTracker"
Cohesion: 0.06
Nodes (39): HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture (+31 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.07
Nodes (49): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:… (+41 more)

### Community 23 - "test_screen.py"
Cohesion: 0.09
Nodes (47): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+39 more)

### Community 24 - "main.py"
Cohesion: 0.04
Nodes (73): BaseSettings, FastAPI, get, Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly. (+65 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.06
Nodes (45): find_ollama(), OllamaSupervisor, Path, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was…, The `ollama` executable, or None if it is not installed. PATH first, because… (+37 more)

### Community 26 - "test_router.py"
Cohesion: 0.08
Nodes (46): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort. (+38 more)

### Community 27 - "test_extract.py"
Cohesion: 0.12
Nodes (32): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+24 more)

### Community 28 - "handlers.py"
Cohesion: 0.04
Nodes (117): build_health(), chat_cancel(), chat_delete(), chat_history(), chat_new(), chat_rename(), chat_send(), chat_sessions() (+109 more)

### Community 29 - "test_study_tools.py"
Cohesion: 0.06
Nodes (69): _mapped(), Any, asyncio, parametrize, quiz(), `study_begin` and `study_check`, and the state she is handed without asking.…, **The reason `QuizQuestion` is not `core.questions.Question`.** The broker…, Only `summary` reaches the model (§7.2), so the grade has to be in it — and the… (+61 more)

### Community 30 - "RoutingLog"
Cohesion: 0.12
Nodes (23): Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Every rating in one conversation, so the panel can render them., Writes and reads `routing_log`. Never raises into the turn path., RoutingLog, Connection, fixture, §9.7's labelled dataset: what the router decided, and what the user thought.…, Reopening a conversation has to show the thumbs again, or they look like they… (+15 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (65): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+57 more)

### Community 32 - "Router"
Cohesion: 0.08
Nodes (30): Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, is_tool_shaped(), needs_deep_model(), BaseModel, ModelInfo, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, A request to act on the machine rather than to talk about something., Reasoning, code, or a multi-step request: the `smart` class earns its cost. (+22 more)

### Community 33 - "assemble"
Cohesion: 0.29
Nodes (7): assemble(), Build the final message list, stable content first., The KV-cache bargain, asserted directly. CLAUDE.md's measured rule: an…, test_memory_never_touches_the_stable_prefix(), test_assemble_puts_stable_content_first(), Every conversation that is not a study session must be byte-identical to what…, test_no_study_block_leaves_the_prompt_exactly_as_it_was()

### Community 34 - "catalog.py"
Cohesion: 0.04
Nodes (69): adopted(), all_models(), Cost, default_local(), discovered(), get(), local_models(), ModelAvailability (+61 more)

### Community 35 - "Tier"
Cohesion: 0.06
Nodes (42): EscalateFn, PreviewFn, RefuseFn, Launch, StrEnum, How an entry has to be started. Three sources, three launchers., Bus, Denied (+34 more)

### Community 36 - "conversation.py"
Cohesion: 0.04
Nodes (64): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Mark one step as run. `local_only` is unknown, not False, for a tool the…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through… (+56 more)

### Community 37 - "test_openrouter.py"
Cohesion: 0.09
Nodes (31): _openrouter_class(), _openrouter_expired(), parse_openrouter(), date, Free models come and go, and OpenRouter says when. An expired id 404s mid-turn,…, Prefer the number; fall back to what the vendor called it. The other two…, Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, OpenRouter: the provider, and the filters that decide what is even offered. The… (+23 more)

### Community 38 - "Listener"
Cohesion: 0.08
Nodes (20): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+12 more)

### Community 39 - "test_db.py"
Cohesion: 0.07
Nodes (41): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, Apply one migration file atomically and stamp `user_version`. The vec0 virtual…, Run ``fn`` against the connection off the event loop, serialised. (+33 more)

### Community 40 - "AdoptionService"
Cohesion: 0.10
Nodes (22): AdoptionService, AdoptionState, Any, BaseModel, date, datetime, ModelInfo, Everything the scheduler needs to resume, and nothing else. (+14 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "test_sigv4.py"
Cohesion: 0.08
Nodes (40): canonical_path(), canonical_request(), encode_path_segment(), datetime, AWS Signature Version 4, in stdlib only (Eyaas's Bedrock key, 2026-08-23).…, Return `headers` plus `Authorization`, `X-Amz-Date` and the payload hash.…, The four nested HMACs. Derived per day, per region, per service., One path segment as it appears in the **request URL**. Bedrock model ids carry… (+32 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "test_reminders.py"
Cohesion: 0.06
Nodes (54): compose(), describe_delay(), datetime, timedelta, Deliver reminders when they come due, and do not let anything stop them. **This…, How overdue a reminder is, in words, or "" when it is on time. **Said out loud…, Fires due reminders. Clock and sleep injected; no test sleeps., One pass. Returns how many were delivered. Never raises. (+46 more)

### Community 45 - "ConversationService"
Cohesion: 0.04
Nodes (40): SessionSummary, ConversationService, Any, ConversationMode, datetime, RoutingBias, StoredMessage, What the model is allowed to know exists. None rather than an empty list when… (+32 more)

### Community 46 - "ToolContext"
Cohesion: 0.04
Nodes (94): _default_data_dir(), get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Where her database, models and logs live. **Beside the repo in development, in…, Process-wide settings singleton., test_with_no_mailbox_configured_it_says_what_to_add(), tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,… (+86 more)

### Community 47 - "test_proactivity.py"
Cohesion: 0.17
Nodes (30): You have not been around in a while" — at most once, and only when that is…, scheduled_check_in_candidate(), _candidate(), FakeStore, Connection, datetime, The proactivity engine (BUILD_SPEC §9 Phase 8). `ProactivityScheduler.tick()`…, Stands in for `find_candidates`/`self_check`/`deliver`. (+22 more)

### Community 48 - "test_questions.py"
Cohesion: 0.11
Nodes (31): Answer, Asked, What came back for one question., The result of one `ask_user` call., The one-line-per-question summary that goes back to the model. **`summary` is…, render(), a_question(), FakeBus (+23 more)

### Community 49 - "test_study_export.py"
Cohesion: 0.14
Nodes (30): dots(), StudyState, A knowledge map as something you can keep — Markdown, or a page you print. **No…, A self-contained page. Ctrl+P is the PDF export., `(text, extension)` for the requested format., The map as Markdown. Plain enough to paste anywhere., render(), _stamp() (+22 more)

### Community 50 - "ChatMessage"
Cohesion: 0.06
Nodes (44): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+36 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "proactivity.py"
Cohesion: 0.11
Nodes (25): Candidate, default_candidates(), idle_intention_candidate(), is_stated_intention(), procedure_offer_candidate(), datetime, Path, timedelta (+17 more)

### Community 53 - "test_bedrock.py"
Cohesion: 0.19
Nodes (31): _collect(), _event(), _provider(), asyncio, MonkeyPatch, Bedrock: the Converse mapping, the streaming loop, and the errors. **The…, `base.py`'s rule, and CLAUDE.md's "always send think: false", on a fourth…, Bedrock streams the argument JSON a piece at a time. A half-parsed argument… (+23 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "test_clipboard_history.py"
Cohesion: 0.05
Nodes (54): ClipboardWatcher, _entropy(), looks_like_a_secret(), Any, Watch the clipboard, and refuse to remember the things that look like keys.…, The clipboard's change counter, or None if the call is unavailable., Records what is copied. Everything is injected so a test drives it., One pass. Never raises — a watcher that can die is worse than none. (+46 more)

### Community 56 - "Connectivity"
Cohesion: 0.13
Nodes (20): Connectivity, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception, MonkeyPatch (+12 more)

### Community 57 - "test_conversation.py"
Cohesion: 0.05
Nodes (91): The six. `LEARN` is the default and behaves exactly as Study did before sub-…, StudySubMode, A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, _drain(), OpenEngine, Path, ToolCall (+83 more)

### Community 58 - "OpenAIProvider"
Cohesion: 0.10
Nodes (14): _assemble(), OpenAIProvider, Any, Response, ToolCall, No-op: cloud models have no local load step to pay for., Per-request fields this vendor accepts and OpenAI does not. A hook rather than…, One vision call: an image in, a description out. Not `stream_chat`.… (+6 more)

### Community 59 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (27): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+19 more)

### Community 60 - "ARIA Sidecar Runtime Dependencies (requirements.txt)"
Cohesion: 0.07
Nodes (27): ARIA Sidecar Runtime Dependencies (requirements.txt), anthropic==0.39.* (NOT adopted, Anthropic excluded), apscheduler==3.10.* (deferred, Phase 5), fastapi==0.115.*, faster-whisper==1.0.3, httpx==0.27.*, keyring==25.7.* (Windows Credential Manager), kokoro-onnx==0.4.* (+19 more)

### Community 61 - "test_episodic.py"
Cohesion: 0.09
Nodes (41): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., _conversation(), _episodic(), anyio, Connection (+33 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+9 more)

### Community 64 - "retrieved_block"
Cohesion: 0.14
Nodes (14): Render remembered facts and episodes into one system message. Returns None when…, _render_memory(), retrieved_block(), A turn about something she has no memory of must leave the prompt byte-…, A fact is a standing truth; an episode is one conversation., A clipped fact beats silence — the cap is a prefill guard, not a correctness…, Uncounted, a roll-up could 'succeed' and still overflow the context — the same…, test_episodes_are_dropped_before_facts() (+6 more)

### Community 65 - "OllamaEmbeddings"
Cohesion: 0.07
Nodes (34): Episode, BaseModel, Row, A row from `episodes`, as the panel and retrieval see it., Nearest episodes to a vector, as (episode, cosine)., _age_days(), _percentile(), datetime (+26 more)

### Community 66 - "test_tools.py"
Cohesion: 0.02
Nodes (137): main(), Console entrypoint for ``python -m sidecar.main``., app(), _focused(), MonkeyPatch, parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested… (+129 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "test_context.py"
Cohesion: 0.07
Nodes (49): machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, volatile_prefix(), full(), Machine context: the clock, the model, and what it costs to carry them. (+41 more)

### Community 69 - "BrowserUnavailable"
Cohesion: 0.22
Nodes (8): Exception, _raising(), `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, test_navigate_reports_browser_unavailable_plainly(), test_no_user_facing_browser_error_names_chrome(), BrowserUnavailable, RuntimeError, The browser is not reachable over CDP. Carries the fix, same shape as…

### Community 70 - "ModelInfo"
Cohesion: 0.06
Nodes (46): SQLite connection, sqlite-vec loading, and the migration runner. One connection…, ExtractedEpisode, ExtractedFact, BaseModel, datetime, ModelInfo, Reflection — where "learns on its own" actually lives (BUILD_SPEC §8.3). Once a…, What the model returned, once it survives validation. (+38 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "VoiceActivity"
Cohesion: 0.15
Nodes (6): ndarray, Protocol, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., VoiceActivity

### Community 73 - "test_research.py"
Cohesion: 0.08
Nodes (38): One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, online(), Exception, fixture, MonkeyPatch, `research(query)`, the untrusted-content boundary, and the online gate. Two… (+30 more)

### Community 74 - "test_spoken_answers.py"
Cohesion: 0.15
Nodes (27): match_spoken(), One spoken utterance into an answer, or None if it is not one. Tried in order…, The question and its options, phrased to be heard rather than read. The "Other"…, speakable(), parametrize, _question(), Answering a question out loud. The property that makes this safe to run on…, **"I don't know" is a real answer to a quiz.** Left to the fuzzy path it would… (+19 more)

### Community 75 - ".upsert"
Cohesion: 0.08
Nodes (17): normalise_triple(), _now(), Row, The form that gets embedded and shown in the prompt., Fold a triple to its stored form. The UNIQUE index is on the raw columns, so…, A stored `fact_vec` row back into floats, or None if it has no vector., Merge one observation into the store, per §8.3. Order matters: 1. **Exact…, §8.3: exact triple → evidence_count += 1, confidence += 0.1 (cap 0.95). (+9 more)

### Community 76 - "bridge.d.ts"
Cohesion: 0.06
Nodes (31): AriaApi, AssistantState, BrainStatus, ClipboardHistory, ClipEntry, CredentialStatus, LogLine, MemoryEpisode (+23 more)

### Community 77 - "Electron main + Python sidecar architecture"
Cohesion: 0.11
Nodes (19): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation (+11 more)

### Community 78 - "affect.py"
Cohesion: 0.17
Nodes (18): _clamp(), _drift(), _energy_delta(), _format_hour(), _hours_since_last_interaction(), datetime, Four floats that make the same question read differently at 2am than at 2pm…, Roughly `[-1, 1]` from the last few user messages. Zero — the common case —… (+10 more)

### Community 79 - "FakeProvider"
Cohesion: 0.06
Nodes (54): chat_mode(), Read or set a conversation's mode. Omit `mode` to read. The read-or-write shape…, FakeProvider, make_service(), _proactivity_service(), anyio, Connection, Event (+46 more)

### Community 80 - "test_adoption.py"
Cohesion: 0.12
Nodes (48): by_class(), The router's pool: **measured only** — curated, or adopted after passing. The…, a_model(), Asker, Clock, perfect_reply(), ModelInfo, Measuring a free model, and the line it has to cross to be routed to.… (+40 more)

### Community 81 - "test_study_modes.py"
Cohesion: 0.08
Nodes (48): parse(), policy_for(), Never raises, and `None` means Learn — `modes.policy_for`'s contract., A sub-mode name off the wire, or `None` for anything unrecognised. Lenient…, delete_subject(), find_subject(), Resolve a spoken subject name to an id, loosely. Exact first, then substring in…, The block that goes in the volatile prefix. Bounded by construction, and the… (+40 more)

### Community 82 - "discovery.py"
Cohesion: 0.11
Nodes (31): _bedrock_class(), _bedrock_tokens(), discover_all(), discover_bedrock(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch() (+23 more)

### Community 83 - "configure_logging"
Cohesion: 0.31
Nodes (8): configure_logging(), _console_handler(), _file_handler(), Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file., Install the structlog + stdlib logging bridge. Idempotent.

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
Cohesion: 0.07
Nodes (39): a_question(), ask_tool(), broker(), fixture, MonkeyPatch, `ask_user`: the registry entry, and the schema the model has to produce. The…, **The first restriction overshot, and Eyaas caught it on screen.** Asked "can u…, Pydantic hoists nested models into `$defs` and points at them with `$ref`.… (+31 more)

### Community 88 - "Client"
Cohesion: 0.23
Nodes (11): Client, concepts_in(), main(), Any, Does Study Mode actually teach? Live, against a real sidecar. python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Answer a `question.ask` the way a student would — one pick each. **This gate…, Open a study chat. **Created, not switched into.** Study stopped being a mode… (+3 more)

### Community 89 - "WhisperSTT"
Cohesion: 0.07
Nodes (30): main(), measure(), missing_words(), normalise(), ndarray, Where the time goes between you stopping and her starting. python…, Words that actually went missing, ignoring differences nothing downstream cares…, clips() (+22 more)

### Community 90 - "Sidebar.tsx"
Cohesion: 0.11
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.25
Nodes (8): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, Phase 7 — a real, logged-in browser (CDP), Online mode — research(query) over search API, Tool.escalate/Tool.refuse hooks: checkout/banking pages force CONFIRM, password fields refused, _default_browser() detects the real default (Brave) via UserChoice registry rather than assuming Chrome, §11 untrusted_content boundary: fetched text is data, labelled and unfiltered, §11 force_confirm: next tool call after research/browser_read is force-escalated to T2

### Community 92 - "test_retrieval.py"
Cohesion: 0.09
Nodes (39): 1.0 today, 0.5 after a month, never quite zero., recency_decay(), anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A memory that keeps coming up is worth surfacing, but not enough to outrank…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice. (+31 more)

### Community 93 - "soak_conversation.py"
Cohesion: 0.19
Nodes (11): concrete_tokens(), main(), novel_tokens(), Any, Event, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet. (+3 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): electron, jsdom, devDependencies, electron, jsdom, react, react-markdown, tailwindcss (+5 more)

### Community 96 - "FakeLocator"
Cohesion: 0.09
Nodes (10): Locator, FakeLocator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught(), test_commit_wording_in_the_visible_text_is_caught() (+2 more)

### Community 97 - "Runtime"
Cohesion: 0.09
Nodes (12): ModelAvailability, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+4 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "ProviderUnavailable"
Cohesion: 0.03
Nodes (72): main(), ProviderRateLimited, ProviderUnavailable, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, The backend could not be reached — offline, not running, DNS, refused. Distinct…, BedrockCredentials, BedrockProvider, control_url() (+64 more)

### Community 101 - "protocol.py"
Cohesion: 0.25
Nodes (14): dispatch(), _invoke(), Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., err(), ok(), Any, BaseModel (+6 more)

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
Cohesion: 0.16
Nodes (28): FakePage, MonkeyPatch, Browser control: the checkout/banking hard block, password refusal, and element…, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, Implements exactly the `Page` surface `browser.py` calls., _returning() (+20 more)

### Community 106 - "spawn"
Cohesion: 0.12
Nodes (14): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, Deliver a message with no preceding question. Called by…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, Any, Task, Run `coro` detached. Failures are logged against `name`, never raised. (+6 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "Question"
Cohesion: 0.15
Nodes (16): normalise(), Option, Pending, BaseModel, Question, Asking the user something and waiting for the answer. Eyaas: *"if u are gonna…, Trim to the caps and give every question its escape hatch. Done here rather…, Broadcast, then wait. Never raises for an ordinary outcome. `spoken`… (+8 more)

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

### Community 114 - "Utterance"
Cohesion: 0.07
Nodes (21): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, Endpoint, Accumulates frames and decides when the speaker has finished. Deliberately not…, Why capture stopped, so the caller can tell an utterance from a timeout., Utterance, build() (+13 more)

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "GenerationOptions"
Cohesion: 0.05
Nodes (56): Amazon Bedrock, end to end, against the real endpoint. python…, choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for() (+48 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 121 - "OllamaProvider"
Cohesion: 0.10
Nodes (14): HTTPError, OllamaProvider, Any, ToolCall, Ollama provider — the local brain, and the offline fallback (BUILD_SPEC §9.7).…, Reachability only — does not check whether any model is loaded., Load `model` with a 1-token request so the user never hits cold start., Evict `model` from VRAM now, instead of after `keep_alive`. CLAUDE.md rule 2:… (+6 more)

### Community 122 - "SettingsPanel.tsx"
Cohesion: 0.20
Nodes (9): BEDROCK_REGIONS, BedrockState, BrowserState, KEY_HELP, KEY_LABEL, OnlineState, RowProps, SEARCH_KEYS (+1 more)

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

### Community 138 - "rpc.ts"
Cohesion: 0.13
Nodes (14): BrainStatus, Pending, RpcEnvelope, RpcError, RpcErrorShape, RpcNotification, createTray(), ICON_PNG (+6 more)

### Community 139 - "useAskQuestion.ts"
Cohesion: 0.33
Nodes (5): AskedQuestion, GivenAnswer, PendingAsk, QuestionOption, useAskQuestion

### Community 141 - "probes.py"
Cohesion: 0.07
Nodes (42): Answered something that has no answer, or claimed an action it cannot perform.…, admits_ignorance(), answers_flatly(), claimed_action(), contains(), contains_any(), denies_capability(), exact() (+34 more)

### Community 142 - "gate_agent.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 6's agent loop, against the running sidecar. "find <scratch file>,…

### Community 143 - "extract.py"
Cohesion: 0.11
Nodes (24): _extract_bytes(), extract_text(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as… (+16 more)

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

### Community 158 - "FakeSettings"
Cohesion: 0.17
Nodes (13): FakeSettings, Path, Empty by default is what keeps this one honest — on a machine that never opted…, I see you are working on X" after one keystroke is precisely the noise §9 warns…, The window is what makes this "right now" rather than "at some point". Without…, Someone renames or deletes a project. That must cost this trigger, not the tick…, It reuses the finder's own skip list rather than inventing a second one. A…, test_a_burst_of_changes_in_a_watched_folder_is_noticed() (+5 more)

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

### Community 191 - "search.py"
Cohesion: 0.11
Nodes (13): AsyncClient, HTMLParser, An epub is a zip of XHTML. Tags are stripped rather than parsed — the same call…, _read_epub(), Web search, and turning a page into something a model can read. BUILD_SPEC §9…, Readable text from a page, truncated on a word boundary., Strip a page to its readable text. Not readability, not an article extractor,…, _Reader (+5 more)

### Community 194 - "EpisodicMemory"
Cohesion: 0.10
Nodes (13): EpisodicMemory, _now(), datetime, StoredMessage, Writes and reads `episodes`. Never raises into the turn path., Summarize every conversation that has gone quiet. Returns how many., Summarize one session into an episode. Idempotent; never raises. `ended_at` is…, Stamp `ended_at` without writing an episode. (+5 more)

### Community 195 - "QuestionBroker"
Cohesion: 0.15
Nodes (7): QuestionBroker, Puts a question on screen and waits for the answer., Give the broker a way to read a question out., Whether an utterance right now should be read as an answer., Try to resolve the pending spoken question from one utterance. Returns whether…, Resolve a waiting question. False if it already went., Release every waiter as unanswered. Wired to shutdown, unlike…

### Community 197 - "files_rename"
Cohesion: 0.16
Nodes (14): files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, Show it in Explorer. The escape hatch for anything this panel does not do., Rename in place, from a click in the panel. Reuses `tools/files.py`'s own…, **To the Recycle Bin, not gone.** This is the one place in the codebase that… (+6 more)

### Community 199 - "test_probes.py"
Cohesion: 0.16
Nodes (13): hedges(), Answers, but signals the answer might be wrong. The middle of the three kinds:…, parametrize, The checks, checked. **They lie before the model does.** CLAUDE.md's own rule,…, `GROUNDED_PROBES` is the adoption gate. What is in it decides which free models…, The check has to keep working, or splitting the pattern would just be a way of…, The other half of the split, and the reason it is a split at all.…, A `\\b` written through a shell heredoc arrives as a backspace (0x08). It… (+5 more)

### Community 202 - "OpenRouterProvider"
Cohesion: 0.08
Nodes (22): _as_int(), OpenRouterProvider, Any, Headers, OpenAI's wire format, someone else's models. Subclassing rather than copying is…, Reachability, and a free chance to read the quota headers., OpenRouter's 429 says more than OpenAI's, and it is routine here. The free tier…, The raw catalogue OpenRouter offers today. Unauthenticated on purpose —… (+14 more)

### Community 203 - "WebSearch"
Cohesion: 0.18
Nodes (9): Any, Response, RuntimeError, Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix., Fetch and strip anything that arrived without text. Concurrently, and failures…, No usable search key, or the provider refused. Carries the fix., SearchUnavailable (+1 more)

### Community 209 - "Retriever"
Cohesion: 0.13
Nodes (11): Task, What one turn recalled, plus what it cost., Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache. (+3 more)

### Community 210 - "test_tts.py"
Cohesion: 0.05
Nodes (48): Any, ndarray, Path, RuntimeError, Speech synthesis — kokoro-onnx on CPU (BUILD_SPEC §9 Phase 2). CPU only, per…, Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half… (+40 more)

### Community 211 - "PersonaLevel"
Cohesion: 0.09
Nodes (37): estimate_tokens(), fit_to_budget(), overhead_tokens(), PersonaLevel, Content identical across turns. Everything here is KV-cached. Changing `level`…, How much character a model can carry without falling apart. Measured on…, Tokens spent before the conversation even starts. Roll-up decisions must…, Drop oldest turns until the assembled prompt fits. Backstop, not policy.… (+29 more)

### Community 212 - "test_email.py"
Cohesion: 0.11
Nodes (9): Read-only IMAP. Two properties carry this feature and both are negative: it…, Subjects arrive like this more often than not, and a summariser fed the raw…, **Email is the canonical case for §11.** A web page has to be navigated to; an…, **The subtle destructive edit.** A plain `RFC822` fetch sets `\\Seen`, so a…, Not a whitelist — somebody's own mail server has to work., test_a_mime_encoded_subject_is_decoded(), test_a_real_hostname_passes_straight_through(), test_email_is_treated_as_an_untrusted_source() (+1 more)

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.29
Nodes (5): DURATION, EASE, SPRING, stagger, TWEEN

### Community 244 - "system.py"
Cohesion: 0.15
Nodes (21): test_system_info_reports_this_machine(), _endpoint_volume(), _facts(), get_system_info(), kill_process(), Any, tool, Facts about the machine, and the one knob she can turn on it. `get_system_info`… (+13 more)

### Community 245 - "test_usage.py"
Cohesion: 0.15
Nodes (16): Usage accounting, pricing, and reading an action back in plain language. The…, **OpenAI reports usage in a frame with no `choices` at all.** `_parse_sse`…, **The ordering that defeated the first two fixes.** OpenAI sends…, Gemini's stream ends by ending — `done` is hard-coded False. A collector that…, They are not discoverable at runtime and they will drift — the same treatment…, **Not folded into the token sum as zero.** OpenRouter sends no usage, and a…, _record(), test_a_chunk_with_neither_choices_nor_usage_is_still_nothing() (+8 more)

### Community 246 - "StreamDelta"
Cohesion: 0.08
Nodes (25): BaseModel, One chunk of a streaming response. `text` carries *content only*. Reasoning…, StreamDelta, Any, EchoProvider, FakeTTS, Event, qwen3.5 streams reasoning into a separate channel. Speaking it aloud would be… (+17 more)

### Community 247 - "describe"
Cohesion: 0.13
Nodes (16): I have no record of that" is a true answer; an invented one is not., `stage`/`detail` are the router's own RouteReason, so a row explains itself…, `approved_by` was added precisely so an audit trail could tell them apart; an…, `type_text`'s argument is an entire essay., test_a_failed_call_says_so_with_its_error(), test_a_long_argument_is_clipped_rather_than_read_back_whole(), test_a_tool_call_names_what_ran_and_who_approved_it(), test_an_unknown_stage_falls_back_to_the_detail_the_router_wrote() (+8 more)

### Community 248 - "strip_wake_word"
Cohesion: 0.14
Nodes (16): is_stop_word(), _near_the_name(), Is this whole utterance just a request to stop talking?, Is this first word a plausible mishearing of her name? `base.en` on a single…, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said. (+8 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 255 - "auth_headers"
Cohesion: 0.18
Nodes (13): auth_headers(), fetch_control(), load_credentials(), What is in the Credential Manager, in the order of preference. **The bearer…, Headers for one Bedrock request, by whichever credential is stored. A module…, One GET against the Bedrock **control plane** — listing, not running. A…, Reachability. Must not raise (`LLMProvider`). **403 counts as reachable.** A…, It is scoped to Bedrock alone, so preferring it means the general-purpose AWS… (+5 more)

### Community 256 - "RateLimitState"
Cohesion: 0.17
Nodes (7): RateLimitState, Turn reasoning off where the endpoint allows it, and count the call. This is…, How much of the free daily allowance ARIA has spent, and it is a count. **The…, **Checked live on 2026-08-19, and the first version was wrong.** OpenRouter…, The header reader is kept because a 429 is documented to carry them. If a real…, test_a_stated_figure_beats_the_local_count(), test_the_free_allowance_is_counted_here_because_the_api_does_not_say()

### Community 257 - "email.py"
Cohesion: 0.24
Nodes (12): IMAP4_SSL, _decode(), fetch(), _fetch_one(), MailHeader, Read-only IMAP, in stdlib. `imaplib` and `email` both ship with Python, so this…, An IMAP SEARCH command. Quoted, so a query cannot inject a command., Newest first. **Blocking** — callers put it on a thread. Raises… (+4 more)

### Community 259 - "make_app_icon.py"
Cohesion: 0.17
Nodes (13): _chunk(), _geometry(), ico_bytes(), main(), _pixel(), png_bytes(), Generate resources/icon.ico — the orb, as the app icon.…, Colour and alpha at a point, in 0..1 icon coordinates. Returns straight (non-… (+5 more)

### Community 260 - "set_discovered"
Cohesion: 0.09
Nodes (26): adopt(), clear_adopted(), Replace what the providers said they offer. A curated id always wins: `gpt-5`…, Record a model as measured-and-passed, making it routable. Curated ids still…, Tests only. The overlay is process-global, like `_DISCOVERED`., set_discovered(), _clean_overlay(), fixture (+18 more)

### Community 261 - "memory.py"
Cohesion: 0.23
Nodes (11): _clip(), forget(), tool, Teaching her directly: `remember` and `forget` (§9 Phase 5). Reflection learns…, Look through past conversations, remembered facts and episodes. Args: query:…, `2026-08-12T10:50:12Z` -> `on 12 Aug`. The date is what makes it a memory., Delete remembered facts matching a description. Args: query: What to forget,…, Keep something about the user for later conversations. Args: fact: The thing to… (+3 more)

### Community 262 - "estimate"
Cohesion: 0.15
Nodes (17): estimate(), for_model(), is_priced(), Rate, What a turn cost, estimated — and the word *estimated* is load-bearing.…, US dollars per million tokens., The rate for a model, or None when nobody has priced it. `local` comes from…, Cost for one turn, or None if it cannot be known. **Missing token counts are… (+9 more)

### Community 263 - "test_curriculum.py"
Cohesion: 0.12
Nodes (34): The indexed text of one file, in order, or `""` if it was never indexed. The…, source_text(), _builder(), asyncio, Turning a lecture into a concept map, and surviving what a model returns. The…, A scanned PDF or an image-only deck is a normal thing to be handed, and "no…, A subject with no concepts would render as "0 of 0 covered" forever and win…, `reflection` records why this matters: reporting the model that was *tried*… (+26 more)

### Community 264 - "snapshot"
Cohesion: 0.29
Nodes (7): BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM unconditionally.…, §9:943 says "regardless of tool tier" — that only means something if *every*…, test_every_browser_tool_carries_the_checkout_escalation(), test_only_fill_carries_the_password_refusal(), test_tiers_deviate_from_build_specs_blanket_confirm_by_design(), A copy of the registry, for tests that install their own tools. Paired with…, snapshot()

### Community 265 - "_locate"
Cohesion: 0.22
Nodes (10): Refusing to act on an ambiguous-but-real description is worse than picking the…, test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), test_locate_takes_the_first_of_several_ambiguous_matches(), _locate(), _preview_click(), _preview_fill(), Any (+2 more)

### Community 268 - "broker"
Cohesion: 0.31
Nodes (9): broker(), exam(), planner(), fixture, MonkeyPatch, Stands in for `runtime.questions`, recording exactly what was shown., Put the session into Exam, through the real `ConversationService` API rather…, Stand in for the model call, so this tests the tool rather than a 7B. (+1 more)

### Community 272 - "Client"
Cohesion: 0.25
Nodes (7): Client, _copy(), main(), Any, Clipboard history, reminders, usage and explain-last-action — live. npm run dev…, Put something on the real clipboard, so the watcher sees a real change., One reader task, everything else off a queue — `gate_modes.py`'s shape.…

### Community 273 - "browser.py"
Cohesion: 0.12
Nodes (28): Browser, Page, test_no_checkout_fields_means_no_dom_match(), browser_click(), browser_fill(), browser_navigate(), browser_read(), browser_screenshot() (+20 more)

### Community 274 - "ProactivityScheduler"
Cohesion: 0.33
Nodes (3): ProactivityScheduler, One pass. Never raises — a scheduler that dies stops everything, the same…, Sweeps for something worth saying, at most once per tick, and only when nothing…

### Community 275 - "files_browse"
Cohesion: 0.29
Nodes (7): _enumerate_drives(), files_browse(), One folder's contents, for the panel. Deliberately not `list_folder`: that tool…, Every fixed drive letter Windows reports, as root paths ("C:\\").…, Trust every drive letter on the machine, in one call. The direct answer to…, tools_trust_all_drives(), test_browse_with_no_path_offers_somewhere_to_start()

### Community 276 - "StudyPanel.test.tsx"
Cohesion: 0.32
Nodes (3): defaults(), state(), subject()

### Community 277 - "_cloud_model"
Cohesion: 0.12
Nodes (17): _cloud_model(), ModelInfo, 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement…, The mechanism has to keep working, or banding would just be a way of ignoring…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make… (+9 more)

### Community 281 - "_parse_yes_no"
Cohesion: 0.50
Nodes (4): _parse_yes_no(), True/False for a clearly affirmative/negative one-line reply, else None — an…, parametrize, test_parse_yes_no()

### Community 282 - "code_only"
Cohesion: 0.29
Nodes (7): ModuleType, code_only(), A module's source with every comment and string literal removed. **A plain…, Rule 5 names sending as destructive. There is no SMTP to guard., `STORE` sets flags and `EXPUNGE` deletes. Neither appears., test_nothing_here_can_change_a_mailbox(), test_nothing_here_can_send()

### Community 284 - "_port_is_free"
Cohesion: 0.50
Nodes (4): _port_is_free(), Whether we can actually have the port, checked before anything else. **A second…, The incident, in one assertion. uvicorn runs the lifespan *before* it binds, so…, test_a_taken_port_is_detected_before_anything_starts()

### Community 286 - "_looks_like_checkout"
Cohesion: 0.13
Nodes (17): parametrize, The URL check catches the common case; a card-number field on an unlisted…, No page has loaded yet at this point — only the URL being navigated *to* is…, test_a_generic_domain_can_still_be_caught_by_its_dom(), test_known_checkout_and_banking_urls_are_recognised(), test_navigate_escalates_on_the_target_url_before_loading_it(), test_ordinary_targets_are_not_refused(), test_ordinary_urls_are_not_flagged() (+9 more)

### Community 289 - "_json_type"
Cohesion: 0.15
Nodes (14): It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, test_a_wrapped_argument_description_survives_the_line_break(), _arg_docs(), build_parameters(), _json_type(), _model_schema(), Any, BaseModel (+6 more)

### Community 290 - "ActivityPanel.tsx"
Cohesion: 0.29
Nodes (7): clock(), Reminders(), thousands(), Timeline(), Today(), TurnRow(), whenever()

### Community 291 - "_body_of"
Cohesion: 0.40
Nodes (5): Message, _body_of(), The plain-text part, or the HTML stripped down to something readable., Tags out, entities in. The same trade `providers/search.py` already made: a…, _strip_html()

### Community 293 - "Any"
Cohesion: 0.29
Nodes (4): Any, What has been spent since `since` (an ISO-8601 UTC stamp). **Aggregates in SQL…, The last few routing decisions, for "why did it pick that". Everything needed…, The routing row that produced one message.

### Community 296 - ".prune"
Cohesion: 0.40
Nodes (3): datetime, Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days.

### Community 297 - "routing_log.py"
Cohesion: 0.25
Nodes (5): ModelVerdict, BaseModel, What the router decided, and what the user made of it (§9.7). §9.7's closing…, How a model has actually been received, per `routing_log`., Liked as a fraction of rated, or None while it would be noise.

### Community 300 - "clipboard_copy"
Cohesion: 0.50
Nodes (4): clipboard_copy(), Put a history entry back on the clipboard., Replace the clipboard's contents. Public for the same reason as `read_text`…, write_text()

### Community 301 - "_no_real_credentials"
Cohesion: 0.67
Nodes (3): _no_real_credentials(), fixture, Never read the developer's actual Credential Manager.

### Community 302 - "ActivityPanel.test.tsx"
Cohesion: 0.32
Nodes (3): mockBridge(), usage(), withTimeline()

### Community 303 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 304 - "context.py"
Cohesion: 0.08
Nodes (28): clean_title(), ConversationMode, _mode_block(), mode_done_when(), mode_label(), _persona(), datetime, StoredMessage (+20 more)

### Community 305 - "ClipboardPanel.tsx"
Cohesion: 0.60
Nodes (3): clock(), Entry(), preview()

### Community 308 - "payload"
Cohesion: 0.67
Nodes (3): payload(), Any, fixture

### Community 311 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 314 - "icon.test.ts"
Cohesion: 0.29
Nodes (3): Entry, EXPECTED_SIZES, ICON

### Community 315 - "_fence"
Cohesion: 0.50
Nodes (4): test_the_mail_is_fenced_as_data_before_and_after(), test_the_unread_state_is_shown_per_message(), _fence(), The mail, labelled as data. §11, and here it earns its keep. Before *and* after…

### Community 318 - "EmailUnavailable"
Cohesion: 0.67
Nodes (3): EmailUnavailable, RuntimeError, Could not reach or sign in to the mailbox. Carries what to do next.

### Community 324 - "probe.py"
Cohesion: 0.67
Nodes (3): main(), Diagnose the frozen-only "cannot load module more than once per process". **Not…, show()

### Community 330 - "pcm16_to_float32"
Cohesion: 0.50
Nodes (4): pcm16_to_float32(), Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., One 80ms frame of base64 int16 PCM from the open microphone. Sent as a…, voice_frame()

## Knowledge Gaps
- **367 isolated node(s):** `APP_ICON`, `sidecar`, `rpc`, `launchedAt`, `singleInstance` (+362 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **82 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_reflection.py`, `test_curriculum.py`, `undo.py`, `broker`, `state`, `finder.py`, `Indexer`, `ProactivityScheduler`, `ConversationStore`, `memory/study.py`, `SemanticMemory`, `main.py`, `test_study_tools.py`, `RoutingLog`, `FakeSettings`, `conversation.py`, `test_db.py`, `routing_log.py`, `test_reminders.py`, `ConversationService`, `test_proactivity.py`, `proactivity.py`, `test_clipboard_history.py`, `test_conversation.py`, `test_episodic.py`, `OllamaEmbeddings`, `EpisodicMemory`, `ModelInfo`, `test_affect.py`, `affect.py`, `FakeProvider`, `test_study_modes.py`, `test_tts.py`, `test_retrieval.py`, `soak_conversation.py`, `Runtime`, `AffectState`, `GenerationOptions`, `StreamDelta`, `test_usage.py`, `_repeated_failures`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `memory.py`, `finder.py`, `apps.py`, `browser.py`, `memory/study.py`, `test_screen.py`, `test_study_tools.py`, `test_organize.py`, `Tier`, `conversation.py`, `_Semantic`, `ConversationService`, `_suppress_close_errors`, `test_conversation.py`, `test_tools.py`, `BrowserUnavailable`, `test_research.py`, `test_email.py`, `test_ask.py`, `FakeLocator`, `test_browser.py`, `Question`, `system.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `Database`, `EventBus`, `test_modes.py`, `ConversationStore`, `HealthTracker`, `main.py`, `RoutingLog`, `Router`, `Tier`, `conversation.py`, `Listener`, `ToolContext`, `ChatMessage`, `test_conversation.py`, `ModelInfo`, `FakeProvider`, `Retriever`, `test_tts.py`, `test_ask.py`, `soak_conversation.py`, `Runtime`, `ProviderUnavailable`, `spawn`, `Utterance`, `GenerationOptions`, `StreamDelta`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `ToolContext` (e.g. with `ConversationHistory` and `ConversationService`) actually correct?**
  _`ToolContext` has 29 INFERRED edges - model-reasoned connections that need verification._