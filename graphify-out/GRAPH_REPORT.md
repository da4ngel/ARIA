# Graph Report - ARIA  (2026-09-01)

## Corpus Check
- 321 files · ~472,658 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 6501 nodes · 14769 edges · 343 communities (263 shown, 80 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1161 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e63e70fc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_permissions.py
- test_listener.py
- main.ts
- KokoroTTS
- TestClient
- SettingsStore
- test_attachments.py
- undo.py
- test_procedures.py
- test_scheduler.py
- EventStreamDecoder
- test_discovery.py
- gate_wakeword.py
- state
- finder.py
- apps.py
- indexer.py
- ConversationStore
- context.py
- test_episodic.py
- study_check
- HealthTracker
- SemanticMemory
- test_screen.py
- Runtime
- test_ollama_supervisor.py
- AvailabilityService
- test_extract.py
- handlers.py
- test_study_tools.py
- conversation.py
- test_organize.py
- Router
- test_router.py
- clear_adopted
- PermissionEngine
- files.py
- test_openrouter.py
- Listener
- test_catalog.py
- AdoptionService
- test_focus.py
- test_sigv4.py
- ARIA — Project Instructions
- attachments.py
- ConversationService
- discovery.py
- test_proactivity.py
- QuestionBroker
- test_study_export.py
- eval_quality.py
- test_text.py
- test_reminders.py
- test_bedrock.py
- compilerOptions
- test_clipboard_history.py
- Connectivity
- ChatMessage
- WakeMode
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- ModelVerdict
- compilerOptions
- test_browser_setup.py
- diagnostics.py
- EpisodicMemory
- test_tools.py
- test_vectors.py
- _drain_windows
- get_settings
- test_diagnostics.py
- test_affect.py
- Utterance
- FakeLocator
- Question
- Fact
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- extract.py
- test_adoption.py
- memory/study.py
- test_browser.py
- OpenAIProvider
- FilesPanel.tsx
- Sidecar
- Client
- test_ask.py
- Client
- listener.py
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- test_retrieval.py
- test_rpc.py
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- StubSearch
- main.py
- PermissionEngine
- browser.py
- FilesPanel.test.tsx
- MachineContext
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- _escalate_click_risk
- ProviderRateLimited
- render
- gate_organize.py
- test_messages.py
- HistoryPanel.tsx
- CLAUDE.md — ARIA Project Instructions (Claude Code-facing)
- Router — local vs cloud, then which provider
- gate_affect.py
- OpenRouterProvider
- AffectState
- usePermissionMode.ts
- Indexer
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- gate_research.py
- test_the_registry_schema_becomes_a_tool_spec
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
- call_key
- MemoryPanel.tsx
- She holds a conversation now (2026-08-07)
- Measuring answer quality
- Smart mode: it was the tool, and then it was the router (2026-08-12)
- test_setup.py
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
- search.py
- test_reflection.py
- Settings
- PersonaLevel
- protocol.py
- _startup
- files_browse
- estimate
- packaging.test.ts
- @types/react
- @types/react-dom
- gate_tool_selection.py
- .broadcast
- test_research.py
- @vitejs/plugin-react
- vitest
- sidecar/__init__.py
- persona/__init__.py
- retrieved_block
- test_tts.py
- ProviderName
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
- overhead_tokens
- _reflector
- typescript
- tokens.js
- ._insert
- parametrize
- email.py
- useConversation.test.ts
- make_app_icon.py
- gate_permission_modes.py
- EventStreamError
- test_usage.py
- Database
- _looks_like_checkout
- configure_logging
- eval/__init__.py
- _cloud_model
- to_pcm16
- rehype-highlight
- @types/ws
- Client
- sidecar.test.ts
- rpc
- ModelHealth
- StudyPanel.test.tsx
- _reset_connection
- test_half_an_aws_key_pair_is_not_a_credential
- StudyPanel.tsx
- RateLimitState
- code_only
- useStudy.ts
- test_read_is_named_as_an_untrusted_source
- IO
- MonkeyPatch
- _locate
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
- auth_headers
- _stream_setup
- online
- ActivityPanel.test.tsx
- _suppress_close_errors
- Any
- ClipboardPanel.tsx
- ModelListing
- _state
- dependencies
- useActivity.ts
- datetime
- SubModeSelector.test.tsx
- .prune
- icon.test.ts
- _fence
- db.py
- WakeWord
- EmailUnavailable
- _no_real_credentials
- payload
- _vector
- autoprefixer
- postcss
- probe.py
- useClipboard.ts
- react-dom
- @testing-library/react
- .as_dict
- snapshot
- zustand
- .forget
- test_the_perfect_model_answers_every_probe
- test_a_model_is_classified_by_whole_tokens_not_substrings
- test_an_id_is_split_on_every_separator_bedrock_uses
- test_smart_never_routes_to_a_discovered_model
- useUpdates.ts
- PanelBoundary
- jsdom
- look_at_the_ui.py
- react-markdown
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

## Communities (343 total, 80 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (106): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+98 more)

### Community 1 - "test_listener.py"
Cohesion: 0.05
Nodes (74): build(), drain(), frame(), interrupt(), Any, Event, Listener, ndarray (+66 more)

### Community 2 - "main.ts"
Cohesion: 0.10
Nodes (29): animateBounds(), APP_ICON, applyPermissions(), bottomRightPosition(), centredExpandedBounds(), createWindow(), DATA_DIR, exportDiagnostics() (+21 more)

### Community 3 - "KokoroTTS"
Cohesion: 0.05
Nodes (38): Case, Bus, Conv, main(), Event, Listener, ndarray, Can she hold a conversation? Measured, not assumed. python… (+30 more)

### Community 4 - "TestClient"
Cohesion: 0.10
Nodes (42): _auth(), _call(), The id is reserved, not written — so the list stays empty., CLAUDE.md rule 5: destructive operations need a confirmation round-trip., An unregistered method returns -32601, so this proves they exist., This machine's `client` fixture runs the real lifespan against a real Ollama…, `None`, not an error. A fresh install has never studied anything, and a read…, The read `scripts/gate_study.py` asserts on instead of on her prose — a model… (+34 more)

### Community 5 - "SettingsStore"
Cohesion: 0.12
Nodes (18): Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, Connection, fixture, parametrize, Durable settings and the v1 -> v2 migration. The migration matters more than…, Values are JSON so a new setting never needs another migration. (+10 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.09
Nodes (45): One attachment, understood. Never raises. `budget` is how many characters of it…, Every attachment on one message, in the order they were given. Sequential…, The block that goes into the prompt. **Fenced as untrusted content**, exactly…, read_all(), read_one(), render(), MonkeyPatch, Path (+37 more)

### Community 7 - "undo.py"
Cohesion: 0.08
Nodes (49): apply(), _claim(), last_undoable(), prune_backups(), Any, Path, One timeline of things that can be taken back. `organize_folder` has had a real…, The most recent thing that can still be taken back. (+41 more)

### Community 8 - "test_procedures.py"
Cohesion: 0.08
Nodes (48): confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers(), Row, Procedural learning — tier 4 of memory (BUILD_SPEC §9 Phase 8). `procedures`… (+40 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "EventStreamDecoder"
Cohesion: 0.14
Nodes (23): encode_event(), EventStreamDecoder, AWS's binary event-stream framing, which is what Bedrock streams. Every other…, Bytes in, whole frames out. Holds the partial frame between reads.…, What is buffered but not yet a whole frame. For tests and logs., Build one frame. **Tests only** — nothing here ever sends this framing. It…, _frame(), The `vnd.amazon.eventstream` decoder. Frames are built with `encode_event`,… (+15 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.08
Nodes (37): Cost, StrEnum, _openai_class(), _openai_is_chat(), _openai_label(), parse_openai(), Whether this id is a dated snapshot of something already in the list. Only when…, `gpt-5.6-luna` -> `GPT-5.6 Luna`, `gpt-4o` -> `GPT-4o`. Cosmetic and never… (+29 more)

### Community 12 - "gate_wakeword.py"
Cohesion: 0.06
Nodes (31): frames(), main(), NullConversation, NullSTT, Event, ndarray, Stage 3 gate, for the parts a machine can check. python…, say() (+23 more)

### Community 13 - "state"
Cohesion: 0.12
Nodes (33): mark_taught(), _next_level(), The whole map with its mastery, in one read., One answer's effect on a level. **A level is a running score, not a verdict on…, Record one answer and return the concept's new level., Introduce a concept without asking anything about it. Level 1 means "he has met…, record_answer(), state() (+25 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (69): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The… (+61 more)

### Community 15 - "apps.py"
Cohesion: 0.03
Nodes (94): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, main(), Console entrypoint for ``python -m sidecar.main``., app(), §7.2's second failure mode: the model gets one line, the UI gets the lot., 7 zip" matched "7-Zip Help" purely because it is the shorter name., The demotion must not make the entry unreachable. (+86 more)

### Community 16 - "indexer.py"
Cohesion: 0.13
Nodes (23): chunk(), _pack(), The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, Whether this file is worth reading at all., sqlite-vec takes raw little-endian float32., Overlapping windows, so a sentence spanning a boundary stays findable., should_index(), parametrize (+15 more)

### Community 17 - "ConversationStore"
Cohesion: 0.03
Nodes (108): The six. `LEARN` is the default and behaves exactly as Study did before sub-…, StudySubMode, ConversationStore, _now(), CRUD over `sessions` and `messages`., Return an existing session id, or create one. `kind` is only ever applied at…, Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's… (+100 more)

### Community 18 - "context.py"
Cohesion: 0.03
Nodes (85): Do the six modes actually behave differently? Live, against a real sidecar.…, report(), clean_title(), ConversationMode, episode_request(), _mode_block(), mode_done_when(), mode_label() (+77 more)

### Community 19 - "test_episodic.py"
Cohesion: 0.09
Nodes (41): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., _conversation(), _episodic(), anyio, Connection (+33 more)

### Community 20 - "study_check"
Cohesion: 0.09
Nodes (31): concept_by_name(), The concept a question was about. Exact, then substring., Which subject *this* chat got to, or None if it has touched none.…, session_subject_id(), **The indexer cannot be a precondition for reading what he just gave.**…, test_a_question_with_one_option_is_not_a_question(), test_material_matches_a_file_attached_this_turn(), _attached_this_turn() (+23 more)

### Community 21 - "HealthTracker"
Cohesion: 0.07
Nodes (38): HealthTracker, In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture, Observed latency and the circuit breaker. A 429 is treated as a routing input…, An unmeasured model must not win a latency ranking by default., A fresh process re-probes rather than assuming the worst., A stale seed must self-correct rather than misroute forever., A 429 is not transient the way a dropped connection is. (+30 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.08
Nodes (46): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:…, §8.3 caps at 0.95. Repetition is evidence, not proof. (+38 more)

### Community 23 - "test_screen.py"
Cohesion: 0.09
Nodes (47): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+39 more)

### Community 24 - "Runtime"
Cohesion: 0.14
Nodes (7): Any, Writes `tool_log`, and — since 2026-08-24 — reads it. **It was write-only for…, The most recent call, optionally within one session. Ordered by `id`, not…, The last few calls, newest first., ToolJournal, Handles owned by the app lifespan., Runtime

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.06
Nodes (43): OllamaSupervisor, Path, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was…, Start `ollama serve` as its own process, with no console window. Detached on…, _spawn_detached() (+35 more)

### Community 26 - "AvailabilityService"
Cohesion: 0.12
Nodes (10): ModelAvailability, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+2 more)

### Community 27 - "test_extract.py"
Cohesion: 0.12
Nodes (32): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+24 more)

### Community 28 - "handlers.py"
Cohesion: 0.04
Nodes (113): build_health(), chat_cancel(), chat_delete(), chat_history(), chat_new(), chat_rename(), chat_send(), chat_sessions() (+105 more)

### Community 29 - "test_study_tools.py"
Cohesion: 0.06
Nodes (63): _mapped(), Any, asyncio, parametrize, quiz(), `study_begin` and `study_check`, and the state she is handed without asking.…, The import in `tools/__init__.py` is load-bearing: the decorator runs on…, Study's own `ToolPolicy.READ_ONLY` caps schemas at `Tier.SAFE`. Both tools sit… (+55 more)

### Community 30 - "conversation.py"
Cohesion: 0.03
Nodes (92): exhausted_note(), LoopState, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through…, Told to the model, not just logged — it should know why it stopped., The budget is per-turn now, so the number has to be passed in. It reads as a…, What the user sees when the model produced no words at all. A real, observed… (+84 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (71): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+63 more)

### Community 32 - "Router"
Cohesion: 0.07
Nodes (35): concrete_tokens(), main(), novel_tokens(), Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket., Recorder (+27 more)

### Community 33 - "test_router.py"
Cohesion: 0.07
Nodes (52): is_trivial(), needs_deep_model(), A greeting or acknowledgement — nothing a 4B model can get wrong., Reasoning, code, or a multi-step request: the `smart` class earns its cost., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router… (+44 more)

### Community 34 - "clear_adopted"
Cohesion: 0.09
Nodes (24): adopt(), clear_adopted(), Record a model as measured-and-passed, making it routable. Curated ids still…, Tests only. The overlay is process-global, like `_DISCOVERED`., _clean_overlay(), fixture, adopted(), discovered() (+16 more)

### Community 35 - "PermissionEngine"
Cohesion: 0.05
Nodes (48): EscalateFn, PreviewFn, RefuseFn, The tier says she may run it; this says the answer stays here. A clipboard…, SAFE, not CONFIRM. A dialog in front of "remember that I prefer short answers"…, Rule 5: destructive operations are T2+ with a confirmation round-trip., AUTO, as BUILD_SPEC:474 lists it. Reading her own memory is not an act on the…, The schema is what the model has to fill in blind. One string. (+40 more)

### Community 36 - "files.py"
Cohesion: 0.06
Nodes (56): Path, Overwriting is a different destructive act from moving, and the user approved a…, `read_file` did a plain UTF-8 read of whatever it was given, so "what does this…, A scanned PDF with no text layer is a normal thing to be handed. Saying so…, OneDrive relocates Documents and Desktop by default, so joining onto…, The whole point: when it cannot be done she must say so, not claim it., A folder is a much larger promise than a file, and this tool says file., test_a_missing_file_is_said_plainly() (+48 more)

### Community 37 - "test_openrouter.py"
Cohesion: 0.09
Nodes (31): _openrouter_class(), _openrouter_expired(), parse_openrouter(), date, Free models come and go, and OpenRouter says when. An expired id 404s mid-turn,…, Prefer the number; fall back to what the vendor called it. The other two…, Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, OpenRouter: the provider, and the filters that decide what is even offered. The… (+23 more)

### Community 38 - "Listener"
Cohesion: 0.08
Nodes (21): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, Report wake scores on the bus for the next `seconds`. **Self-disarming, and…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly. (+13 more)

### Community 39 - "test_catalog.py"
Cohesion: 0.07
Nodes (41): get(), ModelAvailability, persona_for(), A catalog entry plus whether it can actually be used right now., Curated first, then adopted, then discovered. So an explicit choice always…, Persona level for a model; unknown ids get the safe, minimal prompt., Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from. (+33 more)

### Community 40 - "AdoptionService"
Cohesion: 0.09
Nodes (29): Probe, Rules every reply obeys, regardless of what was asked., universal_failures(), AdoptionService, AdoptionState, grade(), _probes_by_id(), Any (+21 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "test_sigv4.py"
Cohesion: 0.08
Nodes (40): canonical_path(), canonical_request(), encode_path_segment(), datetime, AWS Signature Version 4, in stdlib only (Eyaas's Bedrock key, 2026-08-23).…, Return `headers` plus `Authorization`, `X-Amz-Date` and the payload hash.…, The four nested HMACs. Derived per day, per region, per service., One path segment as it appears in the **request URL**. Bedrock model ids carry… (+32 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "attachments.py"
Cohesion: 0.16
Nodes (16): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, image / document / unsupported. Documents use `extract.ATTACHABLE`, which is…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no… (+8 more)

### Community 45 - "ConversationService"
Cohesion: 0.03
Nodes (47): SessionSummary, ConversationService, Any, ConversationMode, datetime, RoutingBias, StoredMessage, What the model is allowed to know exists. None rather than an empty list when… (+39 more)

### Community 46 - "discovery.py"
Cohesion: 0.13
Nodes (29): _bedrock_class(), _bedrock_tokens(), discover_all(), discover_bedrock(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch() (+21 more)

### Community 47 - "test_proactivity.py"
Cohesion: 0.06
Nodes (73): Unprompted messages (Phase 8). Off entirely when the switch is off — the same…, _start_proactivity_scheduler(), Candidate, default_candidates(), idle_intention_candidate(), is_stated_intention(), ProactivityScheduler, procedure_offer_candidate() (+65 more)

### Community 48 - "QuestionBroker"
Cohesion: 0.06
Nodes (50): Answer, Asked, normalise(), Option, Pending, BaseModel, QuestionBroker, Asking the user something and waiting for the answer. Eyaas: *"if u are gonna… (+42 more)

### Community 49 - "test_study_export.py"
Cohesion: 0.14
Nodes (30): dots(), StudyState, A knowledge map as something you can keep — Markdown, or a page you print. **No…, A self-contained page. Ctrl+P is the PDF export., `(text, extension)` for the requested format., The map as Markdown. Plain enough to paste anywhere., render(), _stamp() (+22 more)

### Community 50 - "eval_quality.py"
Cohesion: 0.09
Nodes (31): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+23 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "test_reminders.py"
Cohesion: 0.06
Nodes (54): compose(), describe_delay(), datetime, timedelta, Deliver reminders when they come due, and do not let anything stop them. **This…, How overdue a reminder is, in words, or "" when it is on time. **Said out loud…, Fires due reminders. Clock and sleep injected; no test sleeps., One pass. Returns how many were delivered. Never raises. (+46 more)

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
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "ChatMessage"
Cohesion: 0.03
Nodes (115): HTTPError, Measurement, A recommendation, not a decision. Somebody still reads the replies., Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, split_for_rollup(), Compress the oldest turns. Folds in any earlier note so it compounds., Free-model measurement, and putting past adoptions back in the pool.…, _start_adoption() (+107 more)

### Community 58 - "WakeMode"
Cohesion: 0.10
Nodes (27): How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, _build_listener(), Hands-free listening. Built eagerly rather than warmed in a task: the VAD loads…, _Bus, _FakeVad, _FakeWake, _listener() (+19 more)

### Community 59 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (27): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+19 more)

### Community 60 - "ARIA Sidecar Runtime Dependencies (requirements.txt)"
Cohesion: 0.07
Nodes (27): ARIA Sidecar Runtime Dependencies (requirements.txt), anthropic==0.39.* (NOT adopted, Anthropic excluded), apscheduler==3.10.* (deferred, Phase 5), fastapi==0.115.*, faster-whisper==1.0.3, httpx==0.27.*, keyring==25.7.* (Windows Credential Manager), kokoro-onnx==0.4.* (+19 more)

### Community 61 - "ModelVerdict"
Cohesion: 0.29
Nodes (5): ModelVerdict, BaseModel, Per-model tallies. The dataset §9.7 wants, as far as it has grown., How a model has actually been received, per `routing_log`., Liked as a fraction of rated, or None while it would be noise.

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+9 more)

### Community 64 - "diagnostics.py"
Cohesion: 0.17
Nodes (18): build_report(), _credential_presence(), _environment(), export(), _health(), Any, Path, Export diagnostics — one zip a person can attach to a bug report. BUILD_SPEC §9… (+10 more)

### Community 65 - "EpisodicMemory"
Cohesion: 0.04
Nodes (57): _build_memory(), Facts, episodes and retrieval, as one handle for the conversation., Episode, EpisodicMemory, _now(), BaseModel, datetime, Row (+49 more)

### Community 66 - "test_tools.py"
Cohesion: 0.04
Nodes (92): _focused(), MonkeyPatch, parametrize, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V…, Below the threshold, nothing touches the clipboard — it belongs to the user,… (+84 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "_drain_windows"
Cohesion: 0.25
Nodes (7): _drain_windows(), parts(), phrase(), fixture, Cancel every listening window a test left open. Not optional: ARMED and OPEN…, openWakeWord gating — `hey jarvis` opens capture., The default: any speech is captured, and the transcript decides.

### Community 69 - "get_settings"
Cohesion: 0.09
Nodes (32): main(), Download the wake word weights into data/models/openwakeword. python…, get_settings(), Process-wide settings singleton., _download(), fetch_voice(), fetch_wake_word(), FetchProgress (+24 more)

### Community 70 - "test_diagnostics.py"
Cohesion: 0.16
Nodes (18): CredentialStatus, BaseModel, Safe-to-display description of a stored key., archive(), fixture, MonkeyPatch, Path, Export diagnostics — and the one thing it must never contain. An export exists… (+10 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "Utterance"
Cohesion: 0.06
Nodes (17): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, Endpoint, ndarray, Protocol, Voice activity detection — streaming Silero (BUILD_SPEC §9 Phase 2 stage 3).…, Accumulates frames and decides when the speaker has finished. Deliberately not… (+9 more)

### Community 73 - "FakeLocator"
Cohesion: 0.09
Nodes (10): Locator, FakeLocator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught(), test_commit_wording_in_the_visible_text_is_caught() (+2 more)

### Community 74 - "Question"
Cohesion: 0.13
Nodes (30): match_spoken(), Question, Say the questions. A failure here is not a failure of the ask. If speech is…, One spoken utterance into an answer, or None if it is not one. Tried in order…, The question and its options, phrased to be heard rather than read. The "Other"…, One question, with the options that answer it., speakable(), parametrize (+22 more)

### Community 75 - "Fact"
Cohesion: 0.12
Nodes (13): Fact, FactHit, BaseModel, Row, The form that gets embedded and shown in the prompt., A fact with its retrieval scoring, for the panel and the prompt., A stored `fact_vec` row back into floats, or None if it has no vector., Edit a fact from the panel. Returns None if it is gone. (+5 more)

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
Cohesion: 0.05
Nodes (75): parse(), policy_for(), StrEnum, How a study session is being run right now, as opposed to what it is about.…, Never raises, and `None` means Learn — `modes.policy_for`'s contract., A sub-mode name off the wire, or `None` for anything unrecognised. Lenient…, Which concepts a sub-mode works over. Read by `study.render` to pick what the…, One way of running a study session. (+67 more)

### Community 82 - "test_browser.py"
Cohesion: 0.16
Nodes (28): FakePage, MonkeyPatch, Browser control: the checkout/banking hard block, password refusal, and element…, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, Implements exactly the `Page` surface `browser.py` calls., _returning() (+20 more)

### Community 83 - "OpenAIProvider"
Cohesion: 0.08
Nodes (20): _assemble(), OpenAIProvider, Any, Headers, Response, ToolCall, No-op: cloud models have no local load step to pay for., Per-request fields this vendor accepts and OpenAI does not. A hook rather than… (+12 more)

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

### Community 89 - "listener.py"
Cohesion: 0.11
Nodes (24): clips(), main(), ndarray, Can she hear her own name? Across many voices, because one is not a test.…, score(), is_stop_word(), _near_the_name(), Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3). The renderer opens the… (+16 more)

### Community 90 - "Sidebar.tsx"
Cohesion: 0.11
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 92 - "test_retrieval.py"
Cohesion: 0.09
Nodes (39): 1.0 today, 0.5 after a month, never quite zero., recency_decay(), anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A memory that keeps coming up is worth surfacing, but not enough to outrank…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice. (+31 more)

### Community 93 - "test_rpc.py"
Cohesion: 0.14
Nodes (19): _port_is_free(), Whether we can actually have the port, checked before anything else. **A second…, client(), fixture, MonkeyPatch, Path, The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The `client` fixture above leaves `proactivity_enabled` at its default (True)… (+11 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.13
Nodes (15): electron, electron-builder, electron-vite, framer-motion, devDependencies, electron, electron-builder, electron-vite (+7 more)

### Community 96 - "StubSearch"
Cohesion: 0.15
Nodes (14): Exception, Stripping is a losing game — there are unlimited phrasings. The content is…, It has a title, a URL and a snippet. Citing it beats pretending the search did…, A model that asks for fifty pages would blow the context budget §8.2 exists to…, Stands in for the network. Returns whatever it was handed., StubSearch, test_a_source_that_would_not_load_is_still_cited(), test_an_empty_query_asks_rather_than_searching() (+6 more)

### Community 97 - "main.py"
Cohesion: 0.03
Nodes (102): Amazon Bedrock, end to end, against the real endpoint. python…, Measure a discovered model well enough to let Smart route to it.…, _build_indexer(), _build_stt(), _build_tts(), _discover_local_models(), _probe_embeddings(), RoutingBias (+94 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "browser.py"
Cohesion: 0.10
Nodes (29): Browser, Page, Exception, _raising(), `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, test_navigate_reports_browser_unavailable_plainly(), test_no_user_facing_browser_error_names_chrome(), browser_click() (+21 more)

### Community 101 - "MachineContext"
Cohesion: 0.15
Nodes (21): machine_context(), MachineContext, datetime, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, _relative_age(), volatile_prefix() (+13 more)

### Community 102 - "ConfirmDialog.tsx"
Cohesion: 0.16
Nodes (10): ConfirmRequest, ImagePreview, leaf(), MovePlan, MovePlanView(), Props, tail(), TIER_LABEL (+2 more)

### Community 103 - "useConversation.ts"
Cohesion: 0.27
Nodes (12): appendToStreaming(), AttachmentStatus, clearStreaming(), finalise(), loadRatings(), ToolCall, toTurns(), Turn (+4 more)

### Community 104 - "package.json"
Cohesion: 0.25
Nodes (7): author, description, license, main, name, private, version

### Community 105 - "_escalate_click_risk"
Cohesion: 0.22
Nodes (9): The URL check catches the common case; a card-number field on an unlisted…, test_a_generic_domain_can_still_be_caught_by_its_dom(), test_no_checkout_fields_means_no_dom_match(), _dom_confirms_checkout(), _escalate_click_risk(), _escalate_current_page(), A light scan, not a crawl: does the page carry a payment field? Checked in…, §11's checkout gate for the tools with no URL argument of their own —… (+1 more)

### Community 106 - "ProviderRateLimited"
Cohesion: 0.04
Nodes (62): main(), ProviderRateLimited, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, BedrockCredentials, BedrockProvider, control_url(), current_region(), fetch_control() (+54 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "test_messages.py"
Cohesion: 0.10
Nodes (32): make_session(), fixture, Session listing, search, titles and deletion — what the history panel reads., The bug this catches: `set_title` opened an implicit transaction and never…, The exact failure, reproduced at the layer that fixes it. He asked one question…, The model can already see this chat. Returning it as a discovery would make her…, Before IDF weighting, a question about jobs returned "Discussed the capitals of…, New Chat must not litter the database with empty conversations. (+24 more)

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

### Community 114 - "OpenRouterProvider"
Cohesion: 0.08
Nodes (24): Replace what the providers said they offer. A curated id always wins: `gpt-5`…, set_discovered(), _as_int(), OpenRouterProvider, Any, Headers, OpenAI's wire format, someone else's models. Subclassing rather than copying is…, Reachability, and a free chance to read the quota headers. (+16 more)

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "Indexer"
Cohesion: 0.17
Nodes (10): _digest(), Indexer, IndexStats, Path, Cheap identity: re-reading a 10MB PDF to decide whether to re-read it would…, Walks, reads, embeds and stores — slowly, and out of the way., Hold here while the machine is busy or she is answering., One pass over everything, at the throttled rate. (+2 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 122 - "SettingsPanel.tsx"
Cohesion: 0.20
Nodes (10): BEDROCK_REGIONS, BedrockState, BrowserState, KEY_HELP, KEY_LABEL, OnlineState, RowProps, SEARCH_KEYS (+2 more)

### Community 123 - "Updater"
Cohesion: 0.13
Nodes (9): api, AriaApi, BrainStatus, LogLine, SidecarEvent, Unsubscribe, Updater, UpdaterOptions (+1 more)

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

### Community 143 - "call_key"
Cohesion: 0.47
Nodes (4): call_key(), Any, Mark one step as run. `local_only` is unknown, not False, for a tool the…, A hashable fingerprint of one tool call, for loop detection. Sorted so argument…

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

### Community 149 - "test_setup.py"
Cohesion: 0.13
Nodes (22): _parse_pull_line(), One NDJSON line, or None for keep-alive blanks and unparseable noise., MonkeyPatch, Path, First run: the pull parser, the download, and the two things it must not do.…, The whole reason for the `.part`. `tts.py` decides speech is available by…, Opening the wizard twice must not cost 310MB twice., Same rule as the diagnostics export, for the same reason. `hint` is the last… (+14 more)

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
Cohesion: 0.09
Nodes (28): full(), Machine context: the clock, the model, and what it costs to carry them., CLAUDE.md: keep the pre-conversation budget near 800 tokens **on local**. It…, Roll-up decisions subtract this; if it were uncounted, a conversation could…, The sentence that made her deny a conversation she had just had. "You know…, `recall` is a tool, so the instruction to search only makes sense when tools…, The anti-invention force is what took the 7B from 57% fabrication to 27%.…, `universal_failures` fails *every* probe in *every* category on either of… (+20 more)

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
Nodes (13): HTMLParser, available(), AsyncClient, Web search, and turning a page into something a model can read. BUILD_SPEC §9…, Readable text from a page, truncated on a word boundary., Which search backend can run, or None. Never raises, never blocks., Strip a page to its readable text. Not readability, not an article extractor,…, _Reader (+5 more)

### Community 192 - "test_reflection.py"
Cohesion: 0.14
Nodes (19): build_prompt(), _extract_json(), Any, §8.3's prompt, with the two slots filled., Find the JSON object in whatever the model actually returned. A local 7B wraps…, parametrize, The nightly §8.3 pass. Two things are load-bearing and both are about a local…, §8.3: reflection is the highest-leverage inference in the system. (+11 more)

### Community 193 - "Settings"
Cohesion: 0.14
Nodes (11): BaseSettings, _default_data_dir(), Path, Sidecar configuration. Single source of truth for paths, port, and auth token.…, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly. (+3 more)

### Community 194 - "PersonaLevel"
Cohesion: 0.17
Nodes (15): assemble(), PersonaLevel, StrEnum, Content identical across turns. Everything here is KV-cached. Changing `level`…, How much character a model can carry without falling apart. Measured on…, Build the final message list, stable content first., stable_prefix(), The KV-cache bargain, asserted directly. CLAUDE.md's measured rule: an… (+7 more)

### Community 195 - "protocol.py"
Cohesion: 0.19
Nodes (17): dispatch(), _invoke(), Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., err(), ErrorCode, ok(), Any (+9 more)

### Community 196 - "_startup"
Cohesion: 0.12
Nodes (18): FastAPI, clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds…, Use the token Electron supplied, or mint one for standalone runs., Publish the token for a client that did not supply one. **Not written after the…, Remove the token file on clean shutdown so no stale token survives. **Only if…, Constant-time comparison of a presented Bearer token. (+10 more)

### Community 197 - "files_browse"
Cohesion: 0.13
Nodes (17): _enumerate_drives(), files_browse(), files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, One folder's contents, for the panel. Deliberately not `list_folder`: that tool… (+9 more)

### Community 198 - "estimate"
Cohesion: 0.15
Nodes (17): estimate(), for_model(), is_priced(), Rate, What a turn cost, estimated — and the word *estimated* is load-bearing.…, US dollars per million tokens., The rate for a model, or None when nobody has priced it. `local` comes from…, Cost for one turn, or None if it cannot be known. **Missing token counts are… (+9 more)

### Community 199 - "packaging.test.ts"
Cohesion: 0.29
Nodes (7): BUILDER, code(), CONFIG_PY, MAIN, PACKAGE, read(), SIDECAR

### Community 202 - "gate_tool_selection.py"
Cohesion: 0.17
Nodes (16): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+8 more)

### Community 204 - "test_research.py"
Cohesion: 0.16
Nodes (17): One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, `research(query)`, the untrusted-content boundary, and the online gate. Two…, T1. It reads and changes nothing; the consent that matters is the online…, A model that has just read 6,000 characters of someone else's writing has…, Returns real, correct URLs" is the acceptance line, and only `summary` reaches…, Stronger than asking it not to use one: §7.2's own reasoning for hiding DANGER,… (+9 more)

### Community 209 - "retrieved_block"
Cohesion: 0.13
Nodes (16): estimate_tokens(), Render remembered facts and episodes into one system message. Returns None when…, _render_memory(), retrieved_block(), A turn about something she has no memory of must leave the prompt byte-…, A fact is a standing truth; an episode is one conversation., A clipped fact beats silence — the cap is a prefill guard, not a correctness…, §8.2's order: temporal, then facts. Memory sits nearest the turns because that… (+8 more)

### Community 210 - "test_tts.py"
Cohesion: 0.04
Nodes (63): ToolCall, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Say a reply aloud, on request. False when there is no voice engine. The other…, Phase 8 voice polish's affect-driven nudge to `KokoroTTS.synthesize`. Same…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, SpeechStream (+55 more)

### Community 211 - "ProviderName"
Cohesion: 0.16
Nodes (17): ProviderName, Why a model can or cannot be used, in words the picker can show., _verdict(), parametrize, Adding a provider obliges five other places to learn about it. CLAUDE.md…, `_verdict` indexes this directly to say why a model is unavailable., `for_provider` raises rather than defaulting, deliberately — a fall-through…, Omitting this greys out every one of that provider's models forever, and the… (+9 more)

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
Cohesion: 0.18
Nodes (9): Any, Response, RuntimeError, Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix., Fetch and strip anything that arrived without text. Concurrently, and failures…, No usable search key, or the provider refused. Carries the fix., SearchUnavailable (+1 more)

### Community 246 - "overhead_tokens"
Cohesion: 0.24
Nodes (11): fit_to_budget(), overhead_tokens(), Tokens spent before the conversation even starts. Roll-up decisions must…, Drop oldest turns until the assembled prompt fits. Backstop, not policy.…, It used to omit them, so it trimmed against a budget ~1650 tokens too generous.…, The regression for the live bug: with online mode on, the real prefix is 73…, The third flag on the same axis, guarded before it could be the third bug.…, test_fit_to_budget_accounts_for_the_online_paragraph() (+3 more)

### Community 247 - "_reflector"
Cohesion: 0.17
Nodes (17): anyio, A key can be present while the account is dead, which is exactly this machine's…, The gate's fourth line, from the reflection side., This assertion used to be the other way round, and it cost real learning. The…, A timestamp says an attempt happened; the mark says it was understood.…, The permanent-loss regression. With a wall-clock window, a conversation is…, The table exists but nothing reads it until Phase 6's agent loop., _reflector() (+9 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 255 - "._insert"
Cohesion: 0.13
Nodes (11): normalise_triple(), _now(), Fold a triple to its stored form. The UNIQUE index is on the raw columns, so…, Merge one observation into the store, per §8.3. Order matters: 1. **Exact…, §8.3: exact triple → evidence_count += 1, confidence += 0.1 (cap 0.95)., Write the fact and its vector in one transaction. One transaction is not…, Embed, or None. Never raises — a fact without a vector still counts., The closest fact about the same subject, above the §8.3 threshold. Same subject… (+3 more)

### Community 256 - "parametrize"
Cohesion: 0.20
Nodes (14): ConversationMode, parametrize, The guard above only ever measured NORMAL, and a mode block is part of the…, Resolved once at import, so the same configuration always yields the same bytes…, `_INSTRUCTION_PRIORITY` exists because "reply with only the number 7" once…, `_FULL` says "Short sentences; you are often spoken aloud" — which Study and…, ~150 tokens is the ceiling, raised from 130 on 2026-08-19. Eyaas asked for…, The `has_tools` bug and the `online` bug, pre-empted for the new axis: a budget… (+6 more)

### Community 257 - "email.py"
Cohesion: 0.24
Nodes (12): IMAP4_SSL, _decode(), fetch(), _fetch_one(), MailHeader, Read-only IMAP, in stdlib. `imaplib` and `email` both ship with Python, so this…, An IMAP SEARCH command. Quoted, so a query cannot inject a command., Newest first. **Blocking** — callers put it on a thread. Raises… (+4 more)

### Community 259 - "make_app_icon.py"
Cohesion: 0.17
Nodes (13): _chunk(), _geometry(), ico_bytes(), main(), _pixel(), png_bytes(), Generate resources/icon.ico — the orb, as the app icon.…, Colour and alpha at a point, in 0..1 icon coordinates. Returns straight (non-… (+5 more)

### Community 260 - "gate_permission_modes.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…

### Community 261 - "EventStreamError"
Cohesion: 0.15
Nodes (9): Event, EventStreamError, _parse_headers(), Any, Add bytes; return every frame that is now complete., A frame that cannot be trusted — bad CRC, or a length that does not fit., `messageStart`, `contentBlockDelta`, `metadata`, and so on., `event`, or `exception` when the service is reporting a failure. (+1 more)

### Community 262 - "test_usage.py"
Cohesion: 0.10
Nodes (27): Usage accounting, pricing, and reading an action back in plain language. The…, I have no record of that" is a true answer; an invented one is not., `stage`/`detail` are the router's own RouteReason, so a row explains itself…, `approved_by` was added precisely so an audit trail could tell them apart; an…, `type_text`'s argument is an entire essay., Gemini's stream ends by ending — `done` is hard-coded False. A collector that…, They are not discoverable at runtime and they will drift — the same treatment…, **Not folded into the token sum as zero.** OpenRouter sends no usage, and a… (+19 more)

### Community 263 - "Database"
Cohesion: 0.10
Nodes (40): The indexed text of one file, in order, or `""` if it was never indexed. The…, source_text(), Database, Async-safe wrapper around the single sqlite connection., latest_subject_id(), The subject most recently studied, for resuming without being named., _builder(), asyncio (+32 more)

### Community 264 - "_looks_like_checkout"
Cohesion: 0.15
Nodes (15): parametrize, No page has loaded yet at this point — only the URL being navigated *to* is…, test_known_checkout_and_banking_urls_are_recognised(), test_navigate_escalates_on_the_target_url_before_loading_it(), test_ordinary_targets_are_not_refused(), test_ordinary_urls_are_not_flagged(), test_password_shaped_targets_are_refused(), test_role_name_strips_the_leading_article_and_trailing_noun() (+7 more)

### Community 265 - "configure_logging"
Cohesion: 0.31
Nodes (8): configure_logging(), _console_handler(), _file_handler(), Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file., Install the structlog + stdlib logging bridge. Idempotent.

### Community 267 - "_cloud_model"
Cohesion: 0.12
Nodes (17): _cloud_model(), ModelInfo, 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement…, The mechanism has to keep working, or banding would just be a way of ignoring…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make… (+9 more)

### Community 268 - "to_pcm16"
Cohesion: 0.25
Nodes (7): ndarray, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, to_pcm16(), Wrapping turns a loud sample into a click at the opposite polarity., test_pcm16_clips_rather_than_wrapping(), test_pcm16_is_little_endian_and_half_the_size_of_float32()

### Community 272 - "Client"
Cohesion: 0.25
Nodes (7): Client, _copy(), main(), Any, Clipboard history, reminders, usage and explain-last-action — live. npm run dev…, Put something on the real clipboard, so the watcher sees a real change., One reader task, everything else off a queue — `gate_modes.py`'s shape.…

### Community 274 - "rpc"
Cohesion: 0.17
Nodes (13): get, bearer_from_header(), Extract the token from an ``Authorization: Bearer <token>`` header., health(), Any, Liveness probe for Electron's supervisor. Deliberately cheap and dependency-…, Token-gated JSON-RPC endpoint (§7.1). The port is reachable by any browser tab…, Read/dispatch/reply until the client goes away. (+5 more)

### Community 275 - "ModelHealth"
Cohesion: 0.18
Nodes (4): ModelHealth, BaseModel, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id.

### Community 276 - "StudyPanel.test.tsx"
Cohesion: 0.32
Nodes (3): defaults(), state(), subject()

### Community 277 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 281 - "RateLimitState"
Cohesion: 0.17
Nodes (7): RateLimitState, Turn reasoning off where the endpoint allows it, and count the call. This is…, How much of the free daily allowance ARIA has spent, and it is a count. **The…, **Checked live on 2026-08-19, and the first version was wrong.** OpenRouter…, The header reader is kept because a 429 is documented to carry them. If a real…, test_a_stated_figure_beats_the_local_count(), test_the_free_allowance_is_counted_here_because_the_api_does_not_say()

### Community 282 - "code_only"
Cohesion: 0.29
Nodes (7): ModuleType, code_only(), A module's source with every comment and string literal removed. **A plain…, Rule 5 names sending as destructive. There is no SMTP to guard., `STORE` sets flags and `EXPUNGE` deletes. Neither appears., test_nothing_here_can_change_a_mailbox(), test_nothing_here_can_send()

### Community 285 - "IO"
Cohesion: 0.20
Nodes (8): IO, Import every optional subsystem and say plainly which ones are broken. **This…, Run every check. Returns the process exit code., The Silero weights faster-whisper ships as package data. Nothing imports this…, Loading the extension, not merely importing the wrapper — the wrapper is pure…, run(), _sqlite_vec(), _vad_asset()

### Community 286 - "MonkeyPatch"
Cohesion: 0.24
Nodes (11): broker(), exam(), planner(), fixture, MonkeyPatch, Stands in for `runtime.questions`, recording exactly what was shown., Put the session into Exam, through the real `ConversationService` API rather…, Stand in for the model call, so this tests the tool rather than a 7B. (+3 more)

### Community 287 - "_locate"
Cohesion: 0.22
Nodes (10): Refusing to act on an ambiguous-but-real description is worse than picking the…, test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), test_locate_takes_the_first_of_several_ambiguous_matches(), _locate(), _preview_click(), _preview_fill(), Any (+2 more)

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
Nodes (97): test_with_no_mailbox_configured_it_says_what_to_add(), Launch, _paste_text(), StrEnum, Put `text` on the clipboard, send one Ctrl+V, then put the clipboard back.…, How an entry has to be started. Three sources, three launchers., `ask_user` — put the choice on screen instead of describing it. The mechanism,…, tool (+89 more)

### Community 296 - "useFirstRun.test.ts"
Cohesion: 0.40
Nodes (3): EMPTY_STATE, Listener, listeners

### Community 297 - "test_version.py"
Cohesion: 0.24
Nodes (9): _package_version(), MonkeyPatch, One version, reported by two processes that cannot see each other.…, **The drift guard.** Bump `package.json` and this fails until the fallback…, An installed app is whatever electron-updater last installed, and the sidecar…, `ARIA_APP_VERSION=` is what a shell gives you for an unset variable it still…, test_an_empty_value_falls_back_rather_than_reporting_nothing(), test_electron_wins_when_it_says_anything() (+1 more)

### Community 299 - "auth_headers"
Cohesion: 0.29
Nodes (8): auth_headers(), Headers for one Bedrock request, by whichever credential is stored. A module…, It is scoped to Bedrock alone, so preferring it means the general-purpose AWS…, test_a_bearer_token_is_sent_unsigned(), test_an_access_key_is_signed(), test_no_credential_says_what_to_add_and_where(), test_the_bedrock_api_key_wins_over_the_broader_iam_key(), _with_key()

### Community 300 - "_stream_setup"
Cohesion: 0.25
Nodes (8): Drain a progress generator onto the event bus and report the outcome. **The RPC…, Pull an Ollama model, reporting progress on the event bus. **The first caller…, Download the Kokoro weights, ~330MB. Progress on the event bus., Download the wake-word weights, ~3.5MB. Progress on the event bus., setup_fetch_voice(), setup_fetch_wake_word(), setup_pull_model(), _stream_setup()

### Community 301 - "online"
Cohesion: 0.25
Nodes (8): online(), fixture, MonkeyPatch, The whole point of `SearchUnavailable` carrying a message., Online mode on, with a stubbed search behind it., Belt to `_tool_schemas`' braces. `allow_danger_tools` was dead for a whole…, test_it_refuses_when_online_mode_is_off(), test_no_key_says_which_key_and_where()

### Community 302 - "ActivityPanel.test.tsx"
Cohesion: 0.32
Nodes (3): mockBridge(), usage(), withTimeline()

### Community 303 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 304 - "Any"
Cohesion: 0.29
Nodes (4): Any, What has been spent since `since` (an ISO-8601 UTC stamp). **Aggregates in SQL…, The last few routing decisions, for "why did it pick that". Everything needed…, The routing row that produced one message.

### Community 305 - "ClipboardPanel.tsx"
Cohesion: 0.60
Nodes (3): clock(), Entry(), preview()

### Community 307 - "ModelListing"
Cohesion: 0.29
Nodes (7): ModelListing, BaseModel, `models.list` result., models_list(), models_refresh(), Catalog plus live availability. Drives the picker and its tooltips. Re-probes…, Ask the cloud providers what they offer today, and re-list. Deliberately…

### Community 308 - "_state"
Cohesion: 0.33
Nodes (6): StudyState, **Observed live, and it is the worst failure this project has.** Asked "how…, The two cases are not the same falsehood. A planned roadmap has no file behind…, _state(), test_a_planned_roadmap_says_there_is_no_document_to_quote(), test_the_block_says_the_map_is_the_boundary_of_the_material()

### Community 309 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, electron-updater, ws, electron-updater, ws

### Community 313 - ".prune"
Cohesion: 0.40
Nodes (3): datetime, Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days.

### Community 314 - "icon.test.ts"
Cohesion: 0.29
Nodes (3): Entry, EXPECTED_SIZES, ICON

### Community 315 - "_fence"
Cohesion: 0.50
Nodes (4): test_the_mail_is_fenced_as_data_before_and_after(), test_the_unread_state_is_shown_per_message(), _fence(), The mail, labelled as data. §11, and here it earns its keep. Before *and* after…

### Community 316 - "db.py"
Cohesion: 0.06
Nodes (43): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Apply one migration file atomically and stamp `user_version`. The vec0 virtual… (+35 more)

### Community 317 - "WakeWord"
Cohesion: 0.11
Nodes (8): The wake model, or None in PHRASE mode - which is the default. Exposed so the…, Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, ndarray, Protocol, What the listener depends on, so it never imports openwakeword., WakeWord

### Community 318 - "EmailUnavailable"
Cohesion: 0.67
Nodes (3): EmailUnavailable, RuntimeError, Could not reach or sign in to the mailbox. Carries what to do next.

### Community 319 - "_no_real_credentials"
Cohesion: 0.67
Nodes (3): _no_real_credentials(), fixture, Never read the developer's actual Credential Manager.

### Community 320 - "payload"
Cohesion: 0.67
Nodes (3): payload(), Any, fixture

### Community 324 - "probe.py"
Cohesion: 0.67
Nodes (3): main(), Diagnose the frozen-only "cannot load module more than once per process". **Not…, show()

### Community 329 - "snapshot"
Cohesion: 0.29
Nodes (7): BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM unconditionally.…, §9:943 says "regardless of tool tier" — that only means something if *every*…, test_every_browser_tool_carries_the_checkout_escalation(), test_only_fill_carries_the_password_refusal(), test_tiers_deviate_from_build_specs_blanket_confirm_by_design(), A copy of the registry, for tests that install their own tools. Paired with…, snapshot()

### Community 337 - "PanelBoundary"
Cohesion: 0.25
Nodes (3): PanelBoundary, Props, State

### Community 342 - "look_at_the_ui.py"
Cohesion: 0.50
Nodes (4): _chromium(), main(), Look at the UI, without taking over anybody's screen. npm run dev # in another…, Playwright's own Chromium, whichever build is installed. Its Python package…

## Knowledge Gaps
- **394 isolated node(s):** `DATA_DIR`, `startHidden`, `APP_ICON`, `sidecar`, `updater` (+389 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **80 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `SettingsStore`, `test_usage.py`, `undo.py`, `test_procedures.py`, `state`, `finder.py`, `indexer.py`, `ConversationStore`, `test_episodic.py`, `study_check`, `SemanticMemory`, `Runtime`, `test_study_tools.py`, `conversation.py`, `MonkeyPatch`, `Router`, `ConversationService`, `test_proactivity.py`, `test_reminders.py`, `test_clipboard_history.py`, `ChatMessage`, `db.py`, `ModelVerdict`, `test_reflection.py`, `EpisodicMemory`, `_startup`, `test_affect.py`, `Fact`, `affect.py`, `memory/study.py`, `test_tts.py`, `test_retrieval.py`, `main.py`, `test_messages.py`, `AffectState`, `Indexer`, `_reflector`, `_repeated_failures`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `finder.py`, `apps.py`, `study_check`, `test_screen.py`, `test_study_tools.py`, `conversation.py`, `test_organize.py`, `PermissionEngine`, `files.py`, `ConversationService`, `_suppress_close_errors`, `test_tools.py`, `FakeLocator`, `test_research.py`, `test_tts.py`, `test_browser.py`, `test_email.py`, `test_ask.py`, `StubSearch`, `browser.py`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `Database`, `ConversationStore`, `context.py`, `HealthTracker`, `Runtime`, `conversation.py`, `Router`, `PermissionEngine`, `Listener`, `ToolContext`, `ChatMessage`, `WakeMode`, `WakeWord`, `EpisodicMemory`, `Utterance`, `test_tts.py`, `test_ask.py`, `listener.py`, `main.py`, `ProviderRateLimited`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `ToolContext` (e.g. with `ConversationHistory` and `ConversationService`) actually correct?**
  _`ToolContext` has 29 INFERRED edges - model-reasoned connections that need verification._