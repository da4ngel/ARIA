# Graph Report - ARIA  (2026-08-23)

## Corpus Check
- 273 files · ~403,986 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 5703 nodes · 13160 edges · 307 communities (233 shown, 74 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1119 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4183eb44`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_permissions.py
- test_listener.py
- main.ts
- ModelInfo
- test_rpc.py
- test_reflection.py
- test_attachments.py
- drain_text
- Database
- test_scheduler.py
- EventStreamDecoder
- test_discovery.py
- Listener
- state
- finder.py
- apps.py
- test_indexer.py
- missing_models
- test_modes.py
- ConversationStore
- study_modes.py
- HealthTracker
- SemanticMemory
- test_screen.py
- Settings
- test_ollama_supervisor.py
- test_router.py
- test_extract.py
- method
- test_study_tools.py
- conversation.py
- test_organize.py
- Router
- ChatMessage
- test_retrieval.py
- PermissionEngine
- GenerationOptions
- strip_wake_word
- ._transcribe_and_send
- db.py
- AdoptionService
- test_focus.py
- test_sigv4.py
- ARIA — Project Instructions
- files.py
- ConversationService
- test_episodic.py
- Candidate
- test_questions.py
- StreamDelta
- eval_quality.py
- test_text.py
- search.py
- test_bedrock.py
- compilerOptions
- RecordingBus
- Connectivity
- test_conversation.py
- snapshot
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- main.py
- compilerOptions
- test_browser_setup.py
- context.py
- OllamaEmbeddings
- test_tools.py
- test_vectors.py
- test_context.py
- ToolJournal
- ProviderUnavailable
- test_affect.py
- VoiceActivity
- StubSearch
- extract.py
- Fact
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- _cloud_model
- test_adoption.py
- test_study_modes.py
- discovery.py
- configure_logging
- FilesPanel.tsx
- Sidecar
- Client
- test_ask.py
- Client
- test_research.py
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- test_proactivity.py
- retrieved_block
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- EventBus
- AvailabilityService
- PermissionEngine
- BedrockProvider
- FilesPanel.test.tsx
- handlers.py
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
- messages.py
- AffectState
- usePermissionMode.ts
- OllamaProvider
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- gate_research.py
- SettingsStore
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
- online
- MemoryPanel.tsx
- She holds a conversation now (2026-08-07)
- Measuring answer quality
- Smart mode: it was the tool, and then it was the router (2026-08-12)
- ensure_subject
- is_casual
- App.tsx
- ModelPicker.test.tsx
- ToolCallCard.tsx
- VoiceAura.tsx
- ScreenRim.tsx
- Phase 8 — she has moods, and does not go quiet forever (2026-08-14)
- Phase 2 — Voice
- _to_converse
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
- test_every_sub_mode_has_a_policy_and_an_opener
- electron-vite
- framer-motion
- jsdom
- WakeWordUnavailable
- remark-gfm
- files_browse
- @testing-library/react
- zustand
- @types/react
- @types/react-dom
- test_openrouter.py
- WebSearch
- vite
- @vitejs/plugin-react
- vitest
- sidecar/__init__.py
- persona/__init__.py
- test_option_labels_are_carried_through_verbatim
- test_browser.py
- FakeLocator
- bedrock.py
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
- test_routing_log.py
- Indexer
- memory/study.py
- broker
- OpenRouterProvider
- tokens.js
- rpc.ts
- gate_tool_selection.py
- _next_level
- useConversation.test.ts
- GeminiProvider
- FakeTTS
- free_model
- test_tts.py
- parametrize
- OllamaSupervisor
- _reset_connection
- eval/__init__.py
- postcss
- react-dom
- rehype-highlight
- @types/ws
- study_begin
- EchoProvider
- StoredMessage
- electron-builder
- StudyPanel.test.tsx
- ProactivityScheduler
- _escalate_current_page
- StudyPanel.tsx
- to_pcm16
- _escalate_click_risk
- useStudy.ts
- test_the_tools_are_registered
- _locate
- extract_text
- ToolPolicy
- _parse_yes_no
- parse
- tools_trust_all_drives
- @types/node
- ToolContext
- SubModeSelector.tsx
- test_archives_are_attachable_but_never_indexed
- test_ordinary_questions_do_not_get_the_expensive_tier
- test_a_spoken_turn_still_stays_local
- Sidebar.test.tsx
- test_every_tool_probe_is_recognised_as_a_command
- .cancel_all
- test_a_spoken_command_is_no_longer_forced_onto_the_local_model
- test_a_command_is_not_slowed_down_for_a_difference_that_is_noise
- test_an_ordinary_question_still_takes_the_fast_class
- test_the_module_exposes_what_the_panel_needs
- .broadcast
- SubModeSelector.test.tsx

## God Nodes (most connected - your core abstractions)
1. `Database` - 359 edges
2. `ConversationStore` - 170 edges
3. `ConversationService` - 123 edges
4. `ChatMessage` - 113 edges
5. `HealthTracker` - 106 edges
6. `ToolContext` - 103 edges
7. `SemanticMemory` - 92 edges
8. `ToolResult` - 90 edges
9. `GenerationOptions` - 81 edges
10. `Role` - 68 edges

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

## Communities (307 total, 74 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (108): Collection, Four options on screen are no use to someone across the room, and that is the…, test_it_is_hidden_on_a_spoken_turn(), engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this… (+100 more)

### Community 1 - "test_listener.py"
Cohesion: 0.04
Nodes (87): Endpoint, Accumulates frames and decides when the speaker has finished. Deliberately not…, Why capture stopped, so the caller can tell an utterance from a timeout., Utterance, build(), drain(), _drain_windows(), FakeConversation (+79 more)

### Community 2 - "main.ts"
Cohesion: 0.15
Nodes (22): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+14 more)

### Community 3 - "ModelInfo"
Cohesion: 0.04
Nodes (89): adopt(), adopted(), all_models(), by_class(), clear_adopted(), default_local(), discovered(), get() (+81 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.11
Nodes (47): _auth(), _call(), The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The id is reserved, not written — so the list stays empty., CLAUDE.md rule 5: destructive operations need a confirmation round-trip., An unregistered method returns -32601, so this proves they exist., This machine's `client` fixture runs the real lifespan against a real Ollama…, The `client` fixture above leaves `proactivity_enabled` at its default (True)… (+39 more)

### Community 5 - "test_reflection.py"
Cohesion: 0.08
Nodes (38): build_prompt(), _extract_json(), Any, §8.3's prompt, with the two slots filled., Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio, parametrize, The nightly §8.3 pass. Two things are load-bearing and both are about a local… (+30 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.07
Nodes (59): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no…, One attachment, understood. Never raises. (+51 more)

### Community 7 - "drain_text"
Cohesion: 0.12
Nodes (17): drain_text(), parametrize, The common shape of a reply, and the worst case for silence., A clean, comma-free 24-word sentence sits well under CHUNK_MAX_CHARS, so only…, A comma inside the word budget is a more natural cut than a bare word count —…, No commas to cut on — falls back to a hard word-count cut rather than dropping…, Feed text through the splitter the way tokens actually arrive, then flush the…, The room is silent until the first chunk is synthesised, so the opening… (+9 more)

### Community 8 - "Database"
Cohesion: 0.08
Nodes (51): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+43 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "EventStreamDecoder"
Cohesion: 0.08
Nodes (32): encode_event(), Event, EventStreamDecoder, EventStreamError, _parse_headers(), Any, AWS's binary event-stream framing, which is what Bedrock streams. Every other…, Bytes in, whole frames out. Holds the partial frame between reads.… (+24 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.09
Nodes (36): _gemini_class(), _gemini_is_duplicate(), _openai_class(), _openai_is_chat(), parse_gemini(), parse_openai(), Chat models from a `GET /v1/models` body., A pinned or preview alias of something already listed plainly. Only when the… (+28 more)

### Community 12 - "Listener"
Cohesion: 0.03
Nodes (87): Case, Bus, Conv, main(), Event, ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the… (+79 more)

### Community 13 - "state"
Cohesion: 0.19
Nodes (25): add_concepts(), Add `(name, summary)` pairs to a subject's map, in order. **Additive, never a…, The whole map with its mastery, in one read., Record one answer and return the concept's new level., record_answer(), state(), asyncio, Study Mode's state: the map, the mastery rule, and the prompt line. The mastery… (+17 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (71): _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The…, Make `find_files` deterministic and count how often it really walks., The reason the cache exists at all — two questions in a row must not walk three… (+63 more)

### Community 15 - "apps.py"
Cohesion: 0.04
Nodes (81): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, app(), `normalise("notepad++")` is `"notepad"`, which scored an exact 1.00 against the…, Asking for "notepad" may well mean Notepad++; the ranking can decide. Asking…, Only `+` and `#` name a different product. The 7-Zip cases depend on everything…, test_a_real_name_is_not_treated_as_a_category(), test_a_shared_symbol_still_matches() (+73 more)

### Community 16 - "test_indexer.py"
Cohesion: 0.15
Nodes (21): chunk(), Whether this file is worth reading at all., Overlapping windows, so a sentence spanning a boundary stays findable., should_index(), parametrize, Path, Chunking, extraction and the rules that keep the indexer out of the way.…, §9: skip over 20MB. Extraction cost is otherwise unbounded. (+13 more)

### Community 17 - "missing_models"
Cohesion: 0.33
Nodes (5): main(), Download the wake word weights into data/models/openwakeword. python…, missing_models(), Path, Which weights are absent, named so the log can say what to download.

### Community 18 - "test_modes.py"
Cohesion: 0.05
Nodes (57): Do the six modes actually behave differently? Live, against a real sidecar.…, report(), ModePolicy, policy_for(), ConversationMode, What a mode actually *does*, as opposed to what it says. Eyaas, after using the…, The policy, or Normal's. Never raises. A mode arriving from a stale client is a…, A mode this turn would be better served by, or None. None is the answer for the… (+49 more)

### Community 19 - "ConversationStore"
Cohesion: 0.06
Nodes (44): The message store, for callers that need to resolve a session id., ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, When anything was last said, in any session. The whole precondition for §9's…, A fresh id with no row behind it yet. `ensure_session` creates a row for any id… (+36 more)

### Community 20 - "study_modes.py"
Cohesion: 0.16
Nodes (12): StrEnum, How a study session is being run right now, as opposed to what it is about.…, Which concepts a sub-mode works over. Read by `study.render` to pick what the…, One way of running a study session., Scope, SubModePolicy, Concept, Anything that has been taught, whether or not it stuck. (+4 more)

### Community 21 - "HealthTracker"
Cohesion: 0.07
Nodes (33): HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture (+25 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.06
Nodes (56): normalise_triple(), datetime, Fold a triple to its stored form. The UNIQUE index is on the raw columns, so…, Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days., SemanticMemory (+48 more)

### Community 23 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 24 - "Settings"
Cohesion: 0.11
Nodes (16): BaseSettings, _default_data_dir(), Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly., Where her database, models and logs live. **Beside the repo in development, in… (+8 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.09
Nodes (35): FakeOllama, Any, Path, Starting Ollama, and noticing when it comes back. Eyaas: *"sometimes when…, Somebody running Ollama on another machine, or keeping it off on purpose, still…, **The bug this whole file exists for.** Coming back up is worth nothing on its…, Ollama stays up for hours. Re-listing its models every 20 seconds would be a…, Killing Ollama mid-session and starting it again is exactly the case Eyaas hit.… (+27 more)

### Community 26 - "test_router.py"
Cohesion: 0.10
Nodes (35): is_local(), RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort., Observed latency overrides the seeded table as turns land., The router must always answer. A turn with no candidates is a crash., Local models are multi-GB downloads that may not have finished. (+27 more)

### Community 27 - "test_extract.py"
Cohesion: 0.14
Nodes (28): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+20 more)

### Community 28 - "method"
Cohesion: 0.04
Nodes (96): chat_cancel(), chat_delete(), chat_history(), chat_mode(), chat_new(), chat_rename(), chat_send(), chat_sessions() (+88 more)

### Community 29 - "test_study_tools.py"
Cohesion: 0.11
Nodes (42): _mapped(), Any, asyncio, quiz(), `study_begin` and `study_check`, and the state she is handed without asking.…, A `list[QuizQuestion]` that came out as `{"type": "object"}` with no properties…, **The reason `QuizQuestion` is not `core.questions.Question`.** The broker…, Only `summary` reaches the model (§7.2), so the grade has to be in it — and the… (+34 more)

### Community 30 - "conversation.py"
Cohesion: 0.04
Nodes (61): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Mark one step as run. `local_only` is unknown, not False, for a tool the…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through… (+53 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (71): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+63 more)

### Community 32 - "Router"
Cohesion: 0.11
Nodes (22): Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, is_tool_shaped(), needs_deep_model(), BaseModel, ModelInfo, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, A request to act on the machine rather than to talk about something., Reasoning, code, or a multi-step request: the `smart` class earns its cost. (+14 more)

### Community 33 - "ChatMessage"
Cohesion: 0.07
Nodes (48): choose_with(), assemble(), estimate_tokens(), fit_to_budget(), overhead_tokens(), PersonaLevel, Content identical across turns. Everything here is KV-cached. Changing `level`…, How much character a model can carry without falling apart. Measured on… (+40 more)

### Community 34 - "test_retrieval.py"
Cohesion: 0.10
Nodes (38): 1.0 today, 0.5 after a month, never quite zero., recency_decay(), anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A memory that keeps coming up is worth surfacing, but not enough to outrank…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice. (+30 more)

### Community 35 - "PermissionEngine"
Cohesion: 0.05
Nodes (48): EscalateFn, PreviewFn, RefuseFn, The tier says she may run it; this says the answer stays here. A clipboard…, SAFE, not CONFIRM. A dialog in front of "remember that I prefer short answers"…, Rule 5: destructive operations are T2+ with a confirmation round-trip., AUTO, as BUILD_SPEC:474 lists it. Reading her own memory is not an act on the…, The schema is what the model has to fill in blind. One string. (+40 more)

### Community 36 - "GenerationOptions"
Cohesion: 0.03
Nodes (85): main(), Amazon Bedrock, end to end, against the real endpoint. python…, Measurement, A recommendation, not a decision. Somebody still reads the replies., build_prompt(), choose_model(), CurriculumBuilder, CurriculumOutput (+77 more)

### Community 37 - "strip_wake_word"
Cohesion: 0.14
Nodes (16): is_stop_word(), _near_the_name(), Is this whole utterance just a request to stop talking?, Is this first word a plausible mishearing of her name? `base.en` on a single…, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said. (+8 more)

### Community 38 - "._transcribe_and_send"
Cohesion: 0.08
Nodes (16): ndarray, Told by the renderer when audio starts and stops coming out. Transitions only,…, Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as…, One frame of float32 audio at 16kHz from the renderer. Frames are handled one…, Waiting: decide whether this frame starts something worth hearing., Capturing: accumulate until the speaker stops or runs out of time. (+8 more)

### Community 39 - "db.py"
Cohesion: 0.07
Nodes (42): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Run ``fn`` against the connection off the event loop, serialised. (+34 more)

### Community 40 - "AdoptionService"
Cohesion: 0.10
Nodes (22): AdoptionService, AdoptionState, _probes_by_id(), Any, BaseModel, date, datetime, ModelInfo (+14 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "test_sigv4.py"
Cohesion: 0.08
Nodes (40): canonical_path(), canonical_request(), encode_path_segment(), datetime, AWS Signature Version 4, in stdlib only (Eyaas's Bedrock key, 2026-08-23).…, Return `headers` plus `Authorization`, `X-Amz-Date` and the payload hash.…, The four nested HMACs. Derived per day, per region, per service., One path segment as it appears in the **request URL**. Bedrock model ids carry… (+32 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "files.py"
Cohesion: 0.12
Nodes (32): OneDrive relocates Documents and Desktop by default, so joining onto…, test_it_uses_the_real_location_not_a_guess(), create_folder(), delete_file(), delete_folder(), _GUID, known_folder(), list_folder() (+24 more)

### Community 45 - "ConversationService"
Cohesion: 0.03
Nodes (47): SessionSummary, ConversationService, Any, ConversationMode, ModelInfo, RoutingBias, StoredMessage, ToolCall (+39 more)

### Community 46 - "test_episodic.py"
Cohesion: 0.10
Nodes (41): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., _conversation(), _episodic(), anyio, Connection (+33 more)

### Community 47 - "Candidate"
Cohesion: 0.08
Nodes (35): Candidate, default_candidates(), idle_intention_candidate(), procedure_offer_candidate(), datetime, Path, timedelta, The most concrete, lowest-noise-risk trigger, and checked first for that… (+27 more)

### Community 48 - "test_questions.py"
Cohesion: 0.08
Nodes (45): Answer, Asked, normalise(), Option, Pending, BaseModel, QuestionBroker, Asking the user something and waiting for the answer. Eyaas: *"if u are gonna… (+37 more)

### Community 49 - "StreamDelta"
Cohesion: 0.09
Nodes (38): The indexed text of one file, in order, or `""` if it was never indexed. The…, source_text(), BaseModel, One chunk of a streaming response. `text` carries *content only*. Reasoning…, StreamDelta, Any, _builder(), asyncio (+30 more)

### Community 50 - "eval_quality.py"
Cohesion: 0.08
Nodes (39): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+31 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "search.py"
Cohesion: 0.12
Nodes (11): AsyncClient, HTMLParser, Web search, and turning a page into something a model can read. BUILD_SPEC §9…, Readable text from a page, truncated on a word boundary., Strip a page to its readable text. Not readability, not an article extractor,…, _Reader, to_text(), The normal case on the open web, and returning nothing would read as "research… (+3 more)

### Community 53 - "test_bedrock.py"
Cohesion: 0.15
Nodes (38): _collect(), _event(), _no_real_credentials(), _provider(), asyncio, fixture, MonkeyPatch, Bedrock: the Converse mapping, the streaming loop, and the errors. **The… (+30 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "RecordingBus"
Cohesion: 0.18
Nodes (10): RuntimeError, Voice could not start. Never fatal — she still types., SpeechUnavailable, Event, Voice is additive. No engine must not mean no reply., Audio already queued would otherwise keep talking after the stop button., RecordingBus, test_a_failing_synthesiser_does_not_break_the_turn() (+2 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "test_conversation.py"
Cohesion: 0.03
Nodes (142): The six. `LEARN` is the default and behaves exactly as Study did before sub-…, StudySubMode, ProviderRateLimited, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, _drain(), FakeProvider (+134 more)

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
Cohesion: 0.08
Nodes (35): FastAPI, get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., bearer_from_header(), clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds… (+27 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+9 more)

### Community 64 - "context.py"
Cohesion: 0.09
Nodes (25): clean_title(), ConversationMode, episode_request(), _mode_block(), mode_done_when(), mode_label(), _persona(), datetime (+17 more)

### Community 65 - "OllamaEmbeddings"
Cohesion: 0.05
Nodes (44): Episode, BaseModel, Row, A row from `episodes`, as the panel and retrieval see it., Nearest episodes to a vector, as (episode, cosine)., IndexStats, _pack(), The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks… (+36 more)

### Community 66 - "test_tools.py"
Cohesion: 0.03
Nodes (118): _focused(), MonkeyPatch, parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V… (+110 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "test_context.py"
Cohesion: 0.07
Nodes (49): machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, volatile_prefix(), full(), Machine context: the clock, the model, and what it costs to carry them. (+41 more)

### Community 69 - "ToolJournal"
Cohesion: 0.29
Nodes (4): Any, Where every tool call is recorded (BUILD_SPEC §7.3, CLAUDE.md rule 6). Append-…, Writes to `tool_log`. Satisfies `tools.permissions.Journal`., ToolJournal

### Community 70 - "ProviderUnavailable"
Cohesion: 0.07
Nodes (33): ProviderUnavailable, The backend could not be reached — offline, not running, DNS, refused. Distinct…, all_status(), CredentialKey, CredentialStatus, delete_key(), get_key(), BaseModel (+25 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "VoiceActivity"
Cohesion: 0.15
Nodes (6): ndarray, Protocol, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., VoiceActivity

### Community 73 - "StubSearch"
Cohesion: 0.15
Nodes (14): Exception, Stripping is a losing game — there are unlimited phrasings. The content is…, It has a title, a URL and a snippet. Citing it beats pretending the search did…, A model that asks for fifty pages would blow the context budget §8.2 exists to…, Stands in for the network. Returns whatever it was handed., StubSearch, test_a_source_that_would_not_load_is_still_cited(), test_an_empty_query_asks_rather_than_searching() (+6 more)

### Community 74 - "extract.py"
Cohesion: 0.11
Nodes (23): _extract_bytes(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as…, Slide text and speaker notes, straight out of the OOXML. `python-pptx` would do… (+15 more)

### Community 75 - "Fact"
Cohesion: 0.07
Nodes (22): _now(), Return an existing session id, or create one. `kind` is only ever applied at…, Fact, FactHit, _now(), BaseModel, Row, The form that gets embedded and shown in the prompt. (+14 more)

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
Cohesion: 0.09
Nodes (55): ProviderQuotaExhausted, The **account's** allowance is gone, not this model's. A 429 usually means…, a_model(), Asker, Clock, perfect_reply(), Any, datetime (+47 more)

### Community 81 - "test_study_modes.py"
Cohesion: 0.13
Nodes (32): policy_for(), Never raises, and `None` means Learn — `modes.policy_for`'s contract., delete_subject(), The block that goes in the volatile prefix. Bounded by construction, and the…, Delete a subject, its map, and every answer recorded against it. **This is the…, render(), _mapped(), asyncio (+24 more)

### Community 82 - "discovery.py"
Cohesion: 0.12
Nodes (28): Cost, StrEnum, _bedrock_class(), discover_all(), discover_bedrock(), discover_gemini(), discover_openai(), discover_openrouter() (+20 more)

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
Cohesion: 0.08
Nodes (37): Question, One question, with the options that answer it., a_question(), ask_tool(), broker(), fixture, MonkeyPatch, `ask_user`: the registry entry, and the schema the model has to produce. The… (+29 more)

### Community 88 - "Client"
Cohesion: 0.23
Nodes (11): Client, concepts_in(), main(), Any, Does Study Mode actually teach? Live, against a real sidecar. python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Answer a `question.ask` the way a student would — one pick each. **This gate…, Open a study chat. **Created, not switched into.** Study stopped being a mode… (+3 more)

### Community 89 - "test_research.py"
Cohesion: 0.18
Nodes (15): One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, `research(query)`, the untrusted-content boundary, and the online gate. Two…, A model that has just read 6,000 characters of someone else's writing has…, Returns real, correct URLs" is the acceptance line, and only `summary` reaches…, Stronger than asking it not to use one: §7.2's own reasoning for hiding DANGER,…, test_a_source_is_truncated_rather_than_dropped() (+7 more)

### Community 90 - "Sidebar.tsx"
Cohesion: 0.12
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 92 - "test_proactivity.py"
Cohesion: 0.15
Nodes (32): is_stated_intention(), _candidate(), FakeStore, Connection, datetime, parametrize, The proactivity engine (BUILD_SPEC §9 Phase 8). `ProactivityScheduler.tick()`…, Stands in for `find_candidates`/`self_check`/`deliver`. (+24 more)

### Community 93 - "retrieved_block"
Cohesion: 0.14
Nodes (14): Render remembered facts and episodes into one system message. Returns None when…, _render_memory(), retrieved_block(), A turn about something she has no memory of must leave the prompt byte-…, A fact is a standing truth; an episode is one conversation., A clipped fact beats silence — the cap is a prefill guard, not a correctness…, Uncounted, a roll-up could 'succeed' and still overflow the context — the same…, test_episodes_are_dropped_before_facts() (+6 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): autoprefixer, electron, devDependencies, autoprefixer, electron, react, react-markdown, tailwindcss (+5 more)

### Community 96 - "EventBus"
Cohesion: 0.13
Nodes (12): EventBus, Any, Protocol, Server -> client push notifications and the set of live connections (§7.1).…, Minimal transport surface — a Starlette WebSocket satisfies this., Tracks connected clients and broadcasts notifications to them., Send the current state to one client, unconditionally. A reconnecting renderer…, Send a notification to every live client, dropping dead ones. (+4 more)

### Community 97 - "AvailabilityService"
Cohesion: 0.06
Nodes (34): ModelAvailability, AvailabilityService, ModelInfo, Which models are usable right now. One object answers this for both…, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn. (+26 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "BedrockProvider"
Cohesion: 0.10
Nodes (15): BedrockProvider, current_region(), Response, ToolCall, Streamed `toolUse` fragments into finished calls. Bedrock fragments a tool call…, Implements `LLMProvider` against `bedrock-runtime` ConverseStream., No-op: a cloud model has no local load step to pay for., One decoded frame into a delta, or None where there is nothing to say. (+7 more)

### Community 101 - "handlers.py"
Cohesion: 0.10
Nodes (34): Store a key. Callers must never log `value`., set_key(), pcm16_to_float32(), Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., build_health(), dispatch(), HealthReport, _invoke() (+26 more)

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
Cohesion: 0.18
Nodes (9): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, Any, Task, Fire-and-forget work that must not take the process down with it. Two rules,…, Run `coro` detached. Failures are logged against `name`, never raised. (+1 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "_start_conversation"
Cohesion: 0.09
Nodes (25): get, _build_indexer(), _build_listener(), _discover_local_models(), health(), _probe_embeddings(), Any, RoutingBias (+17 more)

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

### Community 114 - "messages.py"
Cohesion: 0.29
Nodes (5): MessageHit, BaseModel, Sessions and messages — the durable conversation (BUILD_SPEC §7.3). This is…, Find past turns that mention what `query` is about. **This is the layer that…, One past turn that matched a `recall` query.

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "OllamaProvider"
Cohesion: 0.06
Nodes (32): HTTPError, concrete_tokens(), main(), novel_tokens(), Any, Event, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position. (+24 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 121 - "SettingsStore"
Cohesion: 0.12
Nodes (18): Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, Connection, fixture, parametrize, Durable settings and the v1 -> v2 migration. The migration matters more than…, Values are JSON so a new setting never needs another migration. (+10 more)

### Community 122 - "SettingsPanel.tsx"
Cohesion: 0.20
Nodes (9): BEDROCK_REGIONS, BedrockState, BrowserState, KEY_HELP, KEY_LABEL, OnlineState, RowProps, SEARCH_KEYS (+1 more)

### Community 123 - "preload.ts"
Cohesion: 0.25
Nodes (6): api, AriaApi, BrainStatus, LogLine, SidecarEvent, Unsubscribe

### Community 124 - "Client"
Cohesion: 0.26
Nodes (7): Client, main(), Any, ConversationMode, Send, then wait for this turn's own completion., **One reader task, everything else off a queue.** The first version called…, run_mode()

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

### Community 143 - "online"
Cohesion: 0.25
Nodes (8): online(), fixture, MonkeyPatch, The whole point of `SearchUnavailable` carrying a message., Online mode on, with a stubbed search behind it., Belt to `_tool_schemas`' braces. `allow_danger_tools` was dead for a whole…, test_it_refuses_when_online_mode_is_off(), test_no_key_says_which_key_and_where()

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

### Community 149 - "ensure_subject"
Cohesion: 0.27
Nodes (10): ensure_subject(), find_subject(), Find or create a subject by name, returning its id. `source_path` is filled in…, Resolve a spoken subject name to an id, loosely. Exact first, then substring in…, Rename a subject. False if the new name is taken or empty. The name is what…, rename_subject(), Two subjects with one name makes `find_subject` a coin flip., test_a_rename_is_what_resuming_then_matches_on() (+2 more)

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

### Community 158 - "_to_converse"
Cohesion: 0.09
Nodes (24): _merge_adjacent(), Any, A text block, or none at all. Converse rejects an empty `text` block outright,…, `(system, messages)` in the shape Converse accepts. Four rules, all of them…, Fold consecutive same-role turns into one. Rule 3 above., `registry.schemas()` output as a Converse `toolConfig`. The registry emits the…, _text_blocks(), _to_converse() (+16 more)

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

### Community 191 - "test_every_sub_mode_has_a_policy_and_an_opener"
Cohesion: 0.67
Nodes (3): parametrize, A sub-mode with no opener is a button that sends nothing., test_every_sub_mode_has_a_policy_and_an_opener()

### Community 195 - "WakeWordUnavailable"
Cohesion: 0.25
Nodes (5): ndarray, RuntimeError, Score one frame of int16 audio. Returns 0.0 while debounced. Callers must await…, The wake word could not start. Never fatal — typing and push-to-talk both still…, WakeWordUnavailable

### Community 197 - "files_browse"
Cohesion: 0.10
Nodes (24): files_browse(), files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, One folder's contents, for the panel. Deliberately not `list_folder`: that tool…, Show it in Explorer. The escape hatch for anything this panel does not do. (+16 more)

### Community 202 - "test_openrouter.py"
Cohesion: 0.08
Nodes (34): _openrouter_class(), _openrouter_expired(), parse_openrouter(), date, Free models come and go, and OpenRouter says when. An expired id 404s mid-turn,…, Prefer the number; fall back to what the vendor called it. The other two…, Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, payload() (+26 more)

### Community 203 - "WebSearch"
Cohesion: 0.18
Nodes (9): Any, Response, RuntimeError, Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix., Fetch and strip anything that arrived without text. Concurrently, and failures…, No usable search key, or the provider refused. Carries the fix., SearchUnavailable (+1 more)

### Community 210 - "test_browser.py"
Cohesion: 0.13
Nodes (23): Exception, parametrize, _raising(), Browser control: the checkout/banking hard block, password refusal, and element…, No page has loaded yet at this point — only the URL being navigated *to* is…, `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, §11: the *next* tool call after this one is force-escalated by the agent loop —…, test_known_checkout_and_banking_urls_are_recognised() (+15 more)

### Community 211 - "FakeLocator"
Cohesion: 0.10
Nodes (10): Locator, FakeLocator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught(), test_commit_wording_in_the_visible_text_is_caught() (+2 more)

### Community 212 - "bedrock.py"
Cohesion: 0.11
Nodes (18): auth_headers(), BedrockCredentials, control_url(), fetch_control(), load_credentials(), Amazon Bedrock, over the Converse API (Eyaas, 2026-08-23). He has a Bedrock key…, Whichever of the two credential shapes is stored. Read once per request rather…, What is in the Credential Manager, in the order of preference. **The bearer… (+10 more)

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.29
Nodes (5): DURATION, EASE, SPRING, stagger, TWEEN

### Community 244 - "test_routing_log.py"
Cohesion: 0.15
Nodes (19): Connection, fixture, §9.7's labelled dataset: what the router decided, and what the user thought.…, Reopening a conversation has to show the thumbs again, or they look like they…, Three thumbs-down is one bad afternoon, not evidence about a model. A number…, `ON DELETE CASCADE` on message_id, with `foreign_keys` ON — the same foreign…, A row saying only which model answered cannot be used to tune anything. That is…, A routing log that can fail a turn is worse than no routing log. (+11 more)

### Community 245 - "Indexer"
Cohesion: 0.20
Nodes (8): _digest(), Indexer, Path, Cheap identity: re-reading a 10MB PDF to decide whether to re-read it would…, Walks, reads, embeds and stores — slowly, and out of the way., Hold here while the machine is busy or she is answering., One pass over everything, at the throttled rate., Index one file. Returns whether it did any work.

### Community 246 - "memory/study.py"
Cohesion: 0.12
Nodes (16): concept_by_name(), latest_subject_id(), list_subjects(), mark_taught(), _now(), Study Mode's state — the subject, its concept map, and what he has shown. Study…, The subject most recently studied, for resuming without being named., The concept a question was about. Exact, then substring. (+8 more)

### Community 247 - "broker"
Cohesion: 0.31
Nodes (9): broker(), exam(), planner(), fixture, MonkeyPatch, Put the session into Exam, through the real `ConversationService` API rather…, Stands in for `runtime.questions`, recording exactly what was shown., Stand in for the model call, so this tests the tool rather than a 7B. (+1 more)

### Community 248 - "OpenRouterProvider"
Cohesion: 0.07
Nodes (25): _as_int(), OpenRouterProvider, Any, Headers, RateLimitState, OpenAI's wire format, someone else's models. Subclassing rather than copying is…, Turn reasoning off where the endpoint allows it, and count the call. This is…, Reachability, and a free chance to read the quota headers. (+17 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 255 - "rpc.ts"
Cohesion: 0.29
Nodes (5): Pending, RpcEnvelope, RpcError, RpcErrorShape, RpcNotification

### Community 256 - "gate_tool_selection.py"
Cohesion: 0.22
Nodes (12): cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo, Should tool schemas be filtered by relevance before the model sees them? §7.2… (+4 more)

### Community 257 - "_next_level"
Cohesion: 0.33
Nodes (6): _next_level(), One answer's effect on a level. **A level is a running score, not a verdict on…, **The load-bearing rule.** One correct pick from four options is a 25% coin…, 0 means "never seen", and that stops being true once it is taught. Collapsing…, test_a_wrong_answer_never_takes_a_concept_back_to_never_introduced(), test_mastery_cannot_be_reached_in_one_answer()

### Community 259 - "GeminiProvider"
Cohesion: 0.16
Nodes (9): _function_call_part(), GeminiProvider, Any, Response, ToolCall, Split system messages out; map assistant -> model. **Tool turns are not text.**…, Replay a tool call in the shape Gemini demands back. The signature is not…, Implements `LLMProvider` against the Gemini generateContent API. (+1 more)

### Community 260 - "FakeTTS"
Cohesion: 0.13
Nodes (11): FakeTTS, qwen3.5 streams reasoning into a separate channel. Speaking it aloud would be…, Records what it was asked to say, without loading onnxruntime., Synthesis is dispatched per fragment, so a short chunk can finish before a…, Every pre-Phase-8 call site omits `speed` — the engine's own instance default…, Direct against `KokoroTTS`, not `FakeTTS` — proves the override reaches…, test_chunks_carry_an_index_so_playback_can_order_them(), test_kokoro_synthesize_uses_the_override_when_given() (+3 more)

### Community 261 - "free_model"
Cohesion: 0.17
Nodes (12): free_model(), health(), fixture, ModelInfo, A free OpenRouter model, adopted so the router can actually reach it.…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make…, Stage 1 already works this way for privacy, and this sits after it. Overriding… (+4 more)

### Community 262 - "test_tts.py"
Cohesion: 0.22
Nodes (13): Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, shorten_for_speech(), split_for_speech(), Speech chunking and the rule that reasoning is never spoken., Voice must not change what the model is asked for., test_blank_input_yields_nothing(), test_generation_options_are_untouched_by_speech() (+5 more)

### Community 263 - "parametrize"
Cohesion: 0.17
Nodes (13): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., parametrize, The line that was missing. Without it these went to the FAST class., A false positive costs a spoken turn its ~800ms head start, which is the thing…, test_clipboard_questions_stay_on_this_machine(), test_code_requests_reach_a_reasoning_model(), test_conversation_is_not_mistaken_for_a_command() (+5 more)

### Community 264 - "OllamaSupervisor"
Cohesion: 0.23
Nodes (5): OllamaSupervisor, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was…

### Community 265 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 272 - "study_begin"
Cohesion: 0.12
Nodes (17): **The reported bug.** "hey im preparing for a data science internship technical…, His own answer: show it, then check. A roadmap is a claim about what he should…, Provenance reaches the model, not just the database. A roadmap presented as…, A dead end is what caused this whole bug once. Naming a file she cannot find…, test_a_goal_with_no_file_plans_instead_of_refusing(), test_a_named_file_that_is_missing_offers_to_plan_instead(), test_a_planned_roadmap_is_shown_and_checked_before_teaching(), test_a_planned_roadmap_says_it_was_planned_not_read() (+9 more)

### Community 273 - "EchoProvider"
Cohesion: 0.18
Nodes (8): EchoProvider, A provider that answers immediately. The turns below are about whether speech…, Eyaas: *"when an output is generated, it starts to speak, i dont want that…, The button's half of the bargain — and it goes through `SpeechStream`, so a…, No weights is a real state with an honest answer — the button greys itself out…, test_a_typed_turn_does_not_read_itself_aloud(), test_asking_for_it_speaks_the_whole_reply(), test_asking_for_it_with_no_voice_says_so_rather_than_failing()

### Community 274 - "StoredMessage"
Cohesion: 0.25
Nodes (5): Row, Oldest-first turns for a session., Conversations for the history panel, most recently active first. Sessions with…, A row from `messages`, as the UI and context assembly see it., StoredMessage

### Community 276 - "StudyPanel.test.tsx"
Cohesion: 0.32
Nodes (3): defaults(), state(), subject()

### Community 277 - "ProactivityScheduler"
Cohesion: 0.33
Nodes (3): ProactivityScheduler, One pass. Never raises — a scheduler that dies stops everything, the same…, Sweeps for something worth saying, at most once per tick, and only when nothing…

### Community 278 - "_escalate_current_page"
Cohesion: 0.25
Nodes (8): Page, The URL check catches the common case; a card-number field on an unlisted…, test_a_generic_domain_can_still_be_caught_by_its_dom(), test_no_checkout_fields_means_no_dom_match(), _dom_confirms_checkout(), _escalate_current_page(), A light scan, not a crawl: does the page carry a payment field? Checked in…, §11's checkout gate for the tools with no URL argument of their own —…

### Community 281 - "to_pcm16"
Cohesion: 0.25
Nodes (7): ndarray, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, to_pcm16(), Wrapping turns a loud sample into a click at the opposite polarity., test_pcm16_clips_rather_than_wrapping(), test_pcm16_is_little_endian_and_half_the_size_of_float32()

### Community 282 - "_escalate_click_risk"
Cohesion: 0.29
Nodes (7): The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, test_click_risk_escalates_on_the_elements_own_wording(), test_click_risk_is_quiet_for_an_ordinary_click(), test_click_risk_is_quiet_when_nothing_resolved(), _escalate_click_risk(), `browser_click`'s escalate hook: the checkout/banking page check, plus whether…

### Community 284 - "test_the_tools_are_registered"
Cohesion: 0.67
Nodes (3): parametrize, The import in `tools/__init__.py` is load-bearing: the decorator runs on…, test_the_tools_are_registered()

### Community 285 - "_locate"
Cohesion: 0.33
Nodes (6): Refusing to act on an ambiguous-but-real description is worse than picking the…, test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), test_locate_takes_the_first_of_several_ambiguous_matches(), _locate(), Best-effort resolution of a natural-language description, tried in the order a…

### Community 286 - "extract_text"
Cohesion: 0.40
Nodes (5): extract_text(), Whatever text this file has, or "" if it has none worth having. **Never…, _read_pdf(), The two entry points differ on purpose. One corrupt PDF in Downloads must not…, test_extract_text_never_raises_for_the_background_sweep()

### Community 287 - "ToolPolicy"
Cohesion: 0.40
Nodes (4): StrEnum, How much of the registry a mode lets the model see. **Narrowing, never…, The highest tier this policy will show, or None for no tools., ToolPolicy

### Community 289 - "_parse_yes_no"
Cohesion: 0.50
Nodes (4): _parse_yes_no(), True/False for a clearly affirmative/negative one-line reply, else None — an…, parametrize, test_parse_yes_no()

### Community 290 - "parse"
Cohesion: 0.50
Nodes (4): parse(), A sub-mode name off the wire, or `None` for anything unrecognised. Lenient…, The caller is a panel button; an unrecognised string should not fail a click., test_an_unknown_sub_mode_lands_on_learn_rather_than_raising()

### Community 291 - "tools_trust_all_drives"
Cohesion: 0.50
Nodes (4): _enumerate_drives(), Every fixed drive letter Windows reports, as root paths ("C:\\").…, Trust every drive letter on the machine, in one call. The direct answer to…, tools_trust_all_drives()

### Community 293 - "ToolContext"
Cohesion: 0.03
Nodes (104): Browser, test_system_info_reports_this_machine(), Launch, StrEnum, How an entry has to be started. Three sources, three launchers., `ask_user` — put the choice on screen instead of describing it. The mechanism,…, aclose(), browser_click() (+96 more)

## Knowledge Gaps
- **352 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+347 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **74 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `FakeTTS`, `test_reflection.py`, `test_tts.py`, `Listener`, `state`, `study_begin`, `EchoProvider`, `StoredMessage`, `ConversationStore`, `study_modes.py`, `ensure_subject`, `SemanticMemory`, `ProactivityScheduler`, `test_study_tools.py`, `conversation.py`, `test_retrieval.py`, `GenerationOptions`, `db.py`, `ConversationService`, `test_episodic.py`, `Candidate`, `StreamDelta`, `RecordingBus`, `test_conversation.py`, `main.py`, `OllamaEmbeddings`, `ToolJournal`, `test_affect.py`, `Fact`, `affect.py`, `test_study_modes.py`, `test_option_labels_are_carried_through_verbatim`, `broker`, `test_proactivity.py`, `messages.py`, `AffectState`, `test_routing_log.py`, `OllamaProvider`, `Indexer`, `memory/study.py`, `SettingsStore`, `_repeated_failures`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `ModelInfo`, `FakeTTS`, `test_tts.py`, `Database`, `Listener`, `EchoProvider`, `test_modes.py`, `ConversationStore`, `StoredMessage`, `HealthTracker`, `conversation.py`, `Router`, `ChatMessage`, `PermissionEngine`, `GenerationOptions`, `ToolContext`, `RecordingBus`, `test_conversation.py`, `main.py`, `OllamaEmbeddings`, `ProviderUnavailable`, `test_ask.py`, `EventBus`, `spawn`, `_start_conversation`, `OllamaProvider`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `test_tools.py`, `PermissionEngine`, `FakePage`, `StubSearch`, `files.py`, `ConversationService`, `finder.py`, `apps.py`, `study_begin`, `test_browser.py`, `FakeLocator`, `test_screen.py`, `test_ask.py`, `test_research.py`, `test_study_tools.py`, `conversation.py`, `test_organize.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 58 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 58 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `ChatMessage` (e.g. with `Result` and `Measurement`) actually correct?**
  _`ChatMessage` has 35 INFERRED edges - model-reasoned connections that need verification._