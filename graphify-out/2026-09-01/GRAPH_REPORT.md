# Graph Report - ARIA  (2026-09-01)

## Corpus Check
- 318 files · ~466,861 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 6464 nodes · 14709 edges · 338 communities (258 shown, 80 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1161 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4183eb44`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_permissions.py
- test_listener.py
- main.ts
- EpisodicMemory
- test_rpc.py
- test_reflection.py
- test_attachments.py
- undo.py
- test_procedures.py
- test_scheduler.py
- EventStreamDecoder
- test_discovery.py
- KokoroTTS
- state
- finder.py
- apps.py
- Indexer
- test_conversation.py
- test_modes.py
- ConversationStore
- memory/study.py
- HealthTracker
- SemanticMemory
- test_screen.py
- main.py
- test_ollama_supervisor.py
- _start_conversation
- test_extract.py
- handlers.py
- test_study_tools.py
- conversation.py
- test_organize.py
- RouteDecision
- test_router.py
- ModelInfo
- PermissionEngine
- Router
- test_openrouter.py
- Listener
- test_db.py
- AdoptionService
- test_focus.py
- test_sigv4.py
- ARIA — Project Instructions
- files.py
- ConversationService
- discovery.py
- test_proactivity.py
- test_ask.py
- test_study_export.py
- eval_quality.py
- test_text.py
- test_reminders.py
- test_bedrock.py
- compilerOptions
- test_clipboard_history.py
- Connectivity
- StreamDelta
- EventBus
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- Database
- compilerOptions
- test_browser_setup.py
- diagnostics.py
- OllamaEmbeddings
- test_tools.py
- test_vectors.py
- RpcMethodError
- setup.py
- test_diagnostics.py
- test_affect.py
- Utterance
- FakePage
- test_spoken_answers.py
- Fact
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- extract.py
- test_adoption.py
- test_study_modes.py
- MonkeyPatch
- OpenAIProvider
- FilesPanel.tsx
- Sidecar
- Client
- schemas
- Client
- strip_wake_word
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- test_retrieval.py
- soak_conversation.py
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- test_research.py
- GenerationOptions
- PermissionEngine
- browser.py
- FilesPanel.test.tsx
- proactivity.py
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- test_browser.py
- BedrockProvider
- render
- gate_organize.py
- BrowserUnavailable
- HistoryPanel.tsx
- CLAUDE.md — ARIA Project Instructions (Claude Code-facing)
- Router — local vs cloud, then which provider
- gate_affect.py
- _looks_like_a_commit_action
- AffectState
- usePermissionMode.ts
- _cloud_model
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- gate_research.py
- bedrock.py
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
- rpc.ts
- useAskQuestion.ts
- probes.py
- gate_agent.py
- .prune
- MemoryPanel.tsx
- She holds a conversation now (2026-08-07)
- Measuring answer quality
- Smart mode: it was the tool, and then it was the router (2026-08-12)
- ProviderUnavailable
- is_casual
- App.tsx
- ModelPicker.test.tsx
- ToolCallCard.tsx
- VoiceAura.tsx
- ScreenRim.tsx
- Phase 8 — she has moods, and does not go quiet forever (2026-08-14)
- Phase 2 — Voice
- ChatMessage
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
- WebSearch
- electron-vite
- Settings
- _clean_overlay
- HealthReport
- remark-gfm
- files_browse
- browser_read
- packaging.test.ts
- @types/react
- @types/react-dom
- _parse_yes_no
- OllamaProvider
- CredentialKey
- @vitejs/plugin-react
- vitest
- sidecar/__init__.py
- persona/__init__.py
- StoredMessage
- test_tts.py
- Retrieved
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
- GeminiProvider
- react
- gate_tool_selection.py
- tailwindcss
- typescript
- tokens.js
- estimate
- FakeSettings
- email.py
- useConversation.test.ts
- make_app_icon.py
- gate_permission_modes.py
- state.py
- test_usage.py
- test_curriculum.py
- ProactivityScheduler
- configure_logging
- eval/__init__.py
- Any
- _require_memory
- rehype-highlight
- @types/ws
- Client
- sidecar.test.ts
- test_the_perfect_model_answers_every_probe
- test_a_reply_that_leaks_the_prompt_fails_even_when_correct
- StudyPanel.test.tsx
- test_a_verdict_records_why_not_just_what
- BedrockCredentials
- StudyPanel.tsx
- screen.py
- code_only
- useStudy.ts
- test_an_already_present_weight_is_not_downloaded_again
- IO
- ._raise_for_detail
- _study_id
- FirstRun.tsx
- ActivityPanel.tsx
- _body_of
- @types/node
- useFirstRun.ts
- SubModeSelector.tsx
- ToolContext
- useFirstRun.test.ts
- .tick
- Sidebar.test.tsx
- .backfill_vectors
- find_subject
- extract_text
- ActivityPanel.test.tsx
- _suppress_close_errors
- ._parse_sse
- ClipboardPanel.tsx
- _clean_stash
- normalise_triple
- .__init__
- useActivity.ts
- datetime
- SubModeSelector.test.tsx
- electron-builder
- icon.test.ts
- _fence
- db.py
- WakeWord
- EmailUnavailable
- _resolve_bias
- .record_access
- test_legacy_office_names_the_fix_rather_than_the_failure
- autoprefixer
- test_archives_are_attachable_but_never_indexed
- probe.py
- useClipboard.ts
- _next_level
- .__init__
- .as_dict
- test_it_sits_at_confirm_not_the_spec_tables_auto
- PanelBoundary
- jsdom
- look_at_the_ui.py
- test_every_sub_mode_has_a_policy_and_an_opener
- study_export_rpc
- react-markdown
- test_the_gate_is_the_same_probes_the_scripts_use

## God Nodes (most connected - your core abstractions)
1. `Database` - 432 edges
2. `ConversationStore` - 173 edges
3. `ConversationService` - 124 edges
4. `ToolContext` - 119 edges
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

## Communities (338 total, 80 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.07
Nodes (93): engine(), Any, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has…, Rule 6, and the entry most worth having., Models get argument names wrong. That is a thing to say, not to crash on. (+85 more)

### Community 1 - "test_listener.py"
Cohesion: 0.04
Nodes (85): Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout., build(), drain(), _drain_windows(), FakeConversation, frame(), interrupt() (+77 more)

### Community 2 - "main.ts"
Cohesion: 0.12
Nodes (27): animateBounds(), APP_ICON, applyPermissions(), bottomRightPosition(), centredExpandedBounds(), createWindow(), DATA_DIR, exportDiagnostics() (+19 more)

### Community 3 - "EpisodicMemory"
Cohesion: 0.09
Nodes (17): _build_memory(), Facts, episodes and retrieval, as one handle for the conversation., EpisodicMemory, datetime, StoredMessage, Writes and reads `episodes`. Never raises into the turn path., Summarize every conversation that has gone quiet. Returns how many., Summarize one session into an episode. Idempotent; never raises. `ended_at` is… (+9 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.08
Nodes (58): _auth(), _call(), client(), fixture, MonkeyPatch, Path, The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The id is reserved, not written — so the list stays empty. (+50 more)

### Community 5 - "test_reflection.py"
Cohesion: 0.09
Nodes (34): build_prompt(), _extract_json(), Any, §8.3's prompt, with the two slots filled., Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio, parametrize, The nightly §8.3 pass. Two things are load-bearing and both are about a local… (+26 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.06
Nodes (61): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, image / document / unsupported. Documents use `extract.ATTACHABLE`, which is…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no… (+53 more)

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
Cohesion: 0.08
Nodes (33): encode_event(), Event, EventStreamDecoder, EventStreamError, _parse_headers(), Any, AWS's binary event-stream framing, which is what Bedrock streams. Every other…, Bytes in, whole frames out. Holds the partial frame between reads.… (+25 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.08
Nodes (39): _gemini_class(), _gemini_is_chat(), _gemini_is_duplicate(), _openai_class(), _openai_is_chat(), _openai_label(), parse_gemini(), parse_openai() (+31 more)

### Community 12 - "KokoroTTS"
Cohesion: 0.03
Nodes (76): Case, Bus, Conv, main(), Event, Listener, ndarray, Can she hold a conversation? Measured, not assumed. python… (+68 more)

### Community 13 - "state"
Cohesion: 0.17
Nodes (29): add_concepts(), ensure_subject(), Find or create a subject by name, returning its id. `source_path` is filled in…, Add `(name, summary)` pairs to a subject's map, in order. **Additive, never a…, The whole map with its mastery, in one read., Record one answer and return the concept's new level., record_answer(), state() (+21 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (71): _pack(), sqlite-vec takes raw little-endian float32., Nearest chunks to `query`, as (path, text, distance)., search_chunks(), _counting_scan(), f(), MonkeyPatch, parametrize (+63 more)

### Community 15 - "apps.py"
Cohesion: 0.04
Nodes (85): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, 7 zip" matched "7-Zip Help" purely because it is the shorter name., Opening the wrong app is worse than opening nothing., A dead end is useless; naming the closest lets the model retry., `normalise("notepad++")` is `"notepad"`, which scored an exact 1.00 against the…, Asking for "notepad" may well mean Notepad++; the ranking can decide. Asking…, Only `+` and `#` name a different product. The 7-Zip cases depend on everything… (+77 more)

### Community 16 - "Indexer"
Cohesion: 0.08
Nodes (33): _build_indexer(), Start reading documents in the background, if that is wanted. Deliberately last…, chunk(), _digest(), Indexer, IndexStats, Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks… (+25 more)

### Community 17 - "test_conversation.py"
Cohesion: 0.04
Nodes (98): chat_mode(), Read or set a conversation's mode. Omit `mode` to read. The read-or-write shape…, _drain(), FakeProvider, make_service(), _proactivity_service(), anyio, Connection (+90 more)

### Community 18 - "test_modes.py"
Cohesion: 0.04
Nodes (64): Do the six modes actually behave differently? Live, against a real sidecar.…, report(), mode_done_when(), This mode's standard for a finished answer. Public because `core/modes.py`…, ModePolicy, policy_for(), ConversationMode, StrEnum (+56 more)

### Community 19 - "ConversationStore"
Cohesion: 0.05
Nodes (50): The message store, for callers that need to resolve a session id., ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, When anything was last said, in any session. The whole precondition for §9's…, A fresh id with no row behind it yet. `ensure_session` creates a row for any id… (+42 more)

### Community 20 - "memory/study.py"
Cohesion: 0.08
Nodes (26): StrEnum, Which concepts a sub-mode works over. Read by `study.render` to pick what the…, One way of running a study session., Scope, SubModePolicy, Concept, concept_by_name(), list_subjects() (+18 more)

### Community 21 - "HealthTracker"
Cohesion: 0.08
Nodes (29): HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture (+21 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.07
Nodes (49): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:… (+41 more)

### Community 23 - "test_screen.py"
Cohesion: 0.17
Nodes (28): _fake_capture(), _fake_thumbnail(), MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, The load-bearing guarantee. Mutation-checked below: recomputing at execution…, The trusted / always-allow / direct-call path: preview never ran, so there is…, Longer than the 120s confirmation timeout would ever take, but not forever — a…, A capture left behind after being used would answer a *later*, unrelated call… (+20 more)

### Community 24 - "main.py"
Cohesion: 0.07
Nodes (41): FastAPI, get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., bearer_from_header(), clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds… (+33 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.07
Nodes (39): OllamaSupervisor, Keep Ollama running, and notice when it comes back. Eyaas: *"sometimes when…, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., FakeOllama, Any, Path, Starting Ollama, and noticing when it comes back. Eyaas: *"sometimes when… (+31 more)

### Community 26 - "_start_conversation"
Cohesion: 0.06
Nodes (34): get, ModelAvailability, Wire every provider, the router, and the conversation service. §12: a model…, Free-model measurement, and putting past adoptions back in the pool.…, Idle sweeps always; the nightly §8.3 pass only if it is wanted., _start_adoption(), _start_conversation(), _start_memory_scheduler() (+26 more)

### Community 27 - "test_extract.py"
Cohesion: 0.16
Nodes (25): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing…, This is the one path that unpacks untrusted input, and a zip bomb is a… (+17 more)

### Community 28 - "handlers.py"
Cohesion: 0.05
Nodes (70): build_health(), chat_delete(), chat_history(), chat_new(), chat_send(), chat_sessions(), clipboard_forget(), clipboard_history() (+62 more)

### Community 29 - "test_study_tools.py"
Cohesion: 0.05
Nodes (84): broker(), exam(), _mapped(), planner(), Any, asyncio, fixture, MonkeyPatch (+76 more)

### Community 30 - "conversation.py"
Cohesion: 0.03
Nodes (82): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Mark one step as run. `local_only` is unknown, not False, for a tool the…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through… (+74 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (70): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+62 more)

### Community 32 - "RouteDecision"
Cohesion: 0.12
Nodes (20): Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, is_tool_shaped(), needs_deep_model(), BaseModel, ModelInfo, A request to act on the machine rather than to talk about something., Reasoning, code, or a multi-step request: the `smart` class earns its cost., Pick a model. `selected` is the user's choice — a model id, or "smart" to… (+12 more)

### Community 33 - "test_router.py"
Cohesion: 0.11
Nodes (33): is_local(), RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort., Observed latency overrides the seeded table as turns land., The router must always answer. A turn with no candidates is a crash., Local models are multi-GB downloads that may not have finished. (+25 more)

### Community 34 - "ModelInfo"
Cohesion: 0.03
Nodes (113): main(), Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, Whether this endpoint may train on what is sent to it. Unknown ids read as…, _trains_on_data(), adopt(), adopted(), all_models(), by_class() (+105 more)

### Community 35 - "PermissionEngine"
Cohesion: 0.06
Nodes (33): EscalateFn, PreviewFn, RefuseFn, fixture, A registry with one tool per tier, put back exactly as found. The snapshot…, _tools(), paths_in(), PermissionEngine (+25 more)

### Community 36 - "Router"
Cohesion: 0.07
Nodes (30): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., Chooses a model for a turn., Router, parametrize, The line that was missing. Without it these went to the FAST class., Even in the latency-first bias. Fast and wrong is not the trade., The control. Widening the detector must not make everything SMART. (+22 more)

### Community 37 - "test_openrouter.py"
Cohesion: 0.05
Nodes (50): parse_openrouter(), Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, OpenRouterProvider, Any, RateLimitState, OpenAI's wire format, someone else's models. Subclassing rather than copying is…, Turn reasoning off where the endpoint allows it, and count the call. This is…, The raw catalogue OpenRouter offers today. Unauthenticated on purpose —… (+42 more)

### Community 38 - "Listener"
Cohesion: 0.08
Nodes (21): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, Report wake scores on the bus for the next `seconds`. **Self-disarming, and…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly. (+13 more)

### Community 39 - "test_db.py"
Cohesion: 0.17
Nodes (18): Every table in the database, including vec0 virtual tables., table_names(), Connection, Path, Phase 0 acceptance gate: the database is created and migrated from schema.sql., The schema declares float[768]; prove it round-trips., test_affect_state_singleton_is_seeded(), test_all_schema_tables_exist() (+10 more)

### Community 40 - "AdoptionService"
Cohesion: 0.09
Nodes (27): Probe, Rules every reply obeys, regardless of what was asked., universal_failures(), AdoptionService, AdoptionState, grade(), _probes_by_id(), Any (+19 more)

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
Cohesion: 0.06
Nodes (56): Path, Overwriting is a different destructive act from moving, and the user approved a…, `read_file` did a plain UTF-8 read of whatever it was given, so "what does this…, A scanned PDF with no text layer is a normal thing to be handed. Saying so…, OneDrive relocates Documents and Desktop by default, so joining onto…, The whole point: when it cannot be done she must say so, not claim it., A folder is a much larger promise than a file, and this tool says file., test_a_missing_file_is_said_plainly() (+48 more)

### Community 45 - "ConversationService"
Cohesion: 0.03
Nodes (54): SessionSummary, ConversationService, Any, ConversationMode, datetime, ModelInfo, RoutingBias, StoredMessage (+46 more)

### Community 46 - "discovery.py"
Cohesion: 0.09
Nodes (34): _bedrock_class(), _bedrock_tokens(), discover_all(), discover_bedrock(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch() (+26 more)

### Community 47 - "test_proactivity.py"
Cohesion: 0.17
Nodes (30): You have not been around in a while" — at most once, and only when that is…, scheduled_check_in_candidate(), _candidate(), FakeStore, Connection, datetime, The proactivity engine (BUILD_SPEC §9 Phase 8). `ProactivityScheduler.tick()`…, Stands in for `find_candidates`/`self_check`/`deliver`. (+22 more)

### Community 48 - "test_ask.py"
Cohesion: 0.04
Nodes (87): Answer, Asked, normalise(), Option, Pending, BaseModel, Question, QuestionBroker (+79 more)

### Community 49 - "test_study_export.py"
Cohesion: 0.14
Nodes (30): dots(), StudyState, A knowledge map as something you can keep — Markdown, or a page you print. **No…, A self-contained page. Ctrl+P is the PDF export., `(text, extension)` for the requested format., The map as Markdown. Plain enough to paste anywhere., render(), _stamp() (+22 more)

### Community 50 - "eval_quality.py"
Cohesion: 0.09
Nodes (30): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+22 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "test_reminders.py"
Cohesion: 0.06
Nodes (56): compose(), describe_delay(), datetime, timedelta, Deliver reminders when they come due, and do not let anything stop them. **This…, How overdue a reminder is, in words, or "" when it is on time. **Said out loud…, Fires due reminders. Clock and sleep injected; no test sleeps., One pass. Returns how many were delivered. Never raises. (+48 more)

### Community 53 - "test_bedrock.py"
Cohesion: 0.16
Nodes (34): _collect(), _event(), _no_real_credentials(), _provider(), asyncio, fixture, MonkeyPatch, Bedrock: the Converse mapping, the streaming loop, and the errors. **The… (+26 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "test_clipboard_history.py"
Cohesion: 0.05
Nodes (56): ClipboardWatcher, _entropy(), looks_like_a_secret(), Any, Watch the clipboard, and refuse to remember the things that look like keys.…, The clipboard's change counter, or None if the call is unavailable., Records what is copied. Everything is injected so a test drives it., One pass. Never raises — a watcher that can die is worse than none. (+48 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "StreamDelta"
Cohesion: 0.08
Nodes (49): BaseModel, A model asking for a tool to be run. `id` is the provider's handle for the call…, One chunk of a streaming response. `text` carries *content only*. Reasoning…, StreamDelta, ToolCall, OpenEngine, Any, ToolCall (+41 more)

### Community 58 - "EventBus"
Cohesion: 0.05
Nodes (46): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, AssistantState, Event, EventBus (+38 more)

### Community 59 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (27): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+19 more)

### Community 60 - "ARIA Sidecar Runtime Dependencies (requirements.txt)"
Cohesion: 0.07
Nodes (27): ARIA Sidecar Runtime Dependencies (requirements.txt), anthropic==0.39.* (NOT adopted, Anthropic excluded), apscheduler==3.10.* (deferred, Phase 5), fastapi==0.115.*, faster-whisper==1.0.3, httpx==0.27.*, keyring==25.7.* (Windows Credential Manager), kokoro-onnx==0.4.* (+19 more)

### Community 61 - "Database"
Cohesion: 0.10
Nodes (41): Database, Async-safe wrapper around the single sqlite connection., _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, _conversation(), _episodic(), anyio, Connection (+33 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+9 more)

### Community 64 - "diagnostics.py"
Cohesion: 0.12
Nodes (24): build_report(), _credential_presence(), _environment(), export(), _health(), Any, Path, Export diagnostics — one zip a person can attach to a bug report. BUILD_SPEC §9… (+16 more)

### Community 65 - "OllamaEmbeddings"
Cohesion: 0.08
Nodes (30): Episode, BaseModel, A row from `episodes`, as the panel and retrieval see it., Nearest episodes to a vector, as (episode, cosine)., _age_days(), _percentile(), datetime, Retrieval — putting the right memory in front of the model (§9 Phase 5). **The… (+22 more)

### Community 66 - "test_tools.py"
Cohesion: 0.03
Nodes (109): parametrize, A `list[QuizQuestion]` that came out as `{"type": "object"}` with no properties…, The import in `tools/__init__.py` is load-bearing: the decorator runs on…, test_the_quiz_schema_describes_the_nested_shape(), test_the_tools_are_registered(), app(), _focused(), MonkeyPatch (+101 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "RpcMethodError"
Cohesion: 0.06
Nodes (31): chat_cancel(), chat_rename(), clipboard_copy(), memory_reflect(), models_bias(), models_select(), permissions_mode(), proactivity_trigger() (+23 more)

### Community 69 - "setup.py"
Cohesion: 0.11
Nodes (24): main(), Download the wake word weights into data/models/openwakeword. python…, _download(), fetch_voice(), fetch_wake_word(), FetchProgress, Any, AsyncClient (+16 more)

### Community 70 - "test_diagnostics.py"
Cohesion: 0.16
Nodes (18): CredentialStatus, BaseModel, Safe-to-display description of a stored key., archive(), fixture, MonkeyPatch, Path, Export diagnostics — and the one thing it must never contain. An export exists… (+10 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "Utterance"
Cohesion: 0.11
Nodes (8): ndarray, Protocol, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance, VoiceActivity

### Community 73 - "FakePage"
Cohesion: 0.10
Nodes (7): FakeLocator, FakePage, The page-level check runs first, and an ordinary-looking "OK" button on a…, Refusing to act on an ambiguous-but-real description is worse than picking the…, Implements exactly the `Page` surface `browser.py` calls., test_click_risk_still_escalates_on_a_checkout_page(), test_locate_takes_the_first_of_several_ambiguous_matches()

### Community 74 - "test_spoken_answers.py"
Cohesion: 0.15
Nodes (27): match_spoken(), One spoken utterance into an answer, or None if it is not one. Tried in order…, The question and its options, phrased to be heard rather than read. The "Other"…, speakable(), parametrize, _question(), Answering a question out loud. The property that makes this safe to run on…, **"I don't know" is a real answer to a quiz.** Left to the fuzzy path it would… (+19 more)

### Community 75 - "Fact"
Cohesion: 0.08
Nodes (19): _now(), Return an existing session id, or create one. `kind` is only ever applied at…, Fact, _now(), Row, The form that gets embedded and shown in the prompt., A stored `fact_vec` row back into floats, or None if it has no vector., Merge one observation into the store, per §8.3. Order matters: 1. **Exact… (+11 more)

### Community 76 - "bridge.d.ts"
Cohesion: 0.06
Nodes (31): AriaApi, AssistantState, BrainStatus, ClipboardHistory, ClipEntry, CredentialStatus, LogLine, MemoryEpisode (+23 more)

### Community 77 - "Electron main + Python sidecar architecture"
Cohesion: 0.11
Nodes (19): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation (+11 more)

### Community 78 - "affect.py"
Cohesion: 0.17
Nodes (18): _clamp(), _drift(), _energy_delta(), _format_hour(), _hours_since_last_interaction(), datetime, Four floats that make the same question read differently at 2am than at 2pm…, Roughly `[-1, 1]` from the last few user messages. Zero — the common case —… (+10 more)

### Community 79 - "extract.py"
Cohesion: 0.11
Nodes (23): _extract_bytes(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as…, Slide text and speaker notes, straight out of the OOXML. `python-pptx` would do… (+15 more)

### Community 80 - "test_adoption.py"
Cohesion: 0.12
Nodes (46): a_model(), Asker, Clock, perfect_reply(), ModelInfo, Measuring a free model, and the line it has to cross to be routed to.…, A scripted model, and a count of what it cost to ask it., What a model that should be adopted says to any probe. (+38 more)

### Community 81 - "test_study_modes.py"
Cohesion: 0.10
Nodes (39): parse(), policy_for(), How a study session is being run right now, as opposed to what it is about.…, Never raises, and `None` means Learn — `modes.policy_for`'s contract., A sub-mode name off the wire, or `None` for anything unrecognised. Lenient…, delete_subject(), The block that goes in the volatile prefix. Bounded by construction, and the…, Delete a subject, its map, and every answer recorded against it. **This is the… (+31 more)

### Community 82 - "MonkeyPatch"
Cohesion: 0.16
Nodes (23): MonkeyPatch, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, _returning(), test_click_risk_escalates_on_the_elements_own_wording(), test_click_risk_is_quiet_for_an_ordinary_click(), test_click_risk_is_quiet_when_nothing_resolved(), test_current_page_escalation_checks_the_live_page() (+15 more)

### Community 83 - "OpenAIProvider"
Cohesion: 0.11
Nodes (14): _assemble(), OpenAIProvider, Any, Headers, Response, ToolCall, No-op: cloud models have no local load step to pay for., Per-request fields this vendor accepts and OpenAI does not. A hook rather than… (+6 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "Sidecar"
Cohesion: 0.19
Nodes (3): HealthBody, Sidecar, SidecarOptions

### Community 86 - "Client"
Cohesion: 0.29
Nodes (7): Client, main(), Any, Does she ask well, and — more importantly — does she stop asking? python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Send, answer anything she waits on, and return the completed turn. `pick` is…, section()

### Community 87 - "schemas"
Cohesion: 0.06
Nodes (36): Collection, The schema change is a capability, not a special case for this tool., `tools/__init__.py`'s own docstring records `finder` being silently…, Four options on screen are no use to someone across the room, and that is the…, test_a_plain_model_argument_also_works(), test_it_is_hidden_on_a_spoken_turn(), test_it_is_registered_at_import(), §7.2: "off by default" means the model is not told they exist, which is… (+28 more)

### Community 88 - "Client"
Cohesion: 0.21
Nodes (12): Client, concepts_in(), main(), Any, Does Study Mode actually teach? Live, against a real sidecar. python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Answer a `question.ask` the way a student would — one pick each. **This gate…, **The payload key is `tool`, not `name`.** This read `name` and defaulted to… (+4 more)

### Community 89 - "strip_wake_word"
Cohesion: 0.16
Nodes (14): is_stop_word(), Is this whole utterance just a request to stop talking?, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said., The name has to be first. Anywhere else it is just a word., Matched whole, never as a prefix. (+6 more)

### Community 90 - "Sidebar.tsx"
Cohesion: 0.11
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 92 - "test_retrieval.py"
Cohesion: 0.10
Nodes (38): 1.0 today, 0.5 after a month, never quite zero., recency_decay(), anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A memory that keeps coming up is worth surfacing, but not enough to outrank…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice. (+30 more)

### Community 93 - "soak_conversation.py"
Cohesion: 0.19
Nodes (11): concrete_tokens(), main(), novel_tokens(), Any, Event, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet. (+3 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.13
Nodes (15): electron, framer-motion, devDependencies, electron, framer-motion, postcss, react-dom, @testing-library/react (+7 more)

### Community 96 - "test_research.py"
Cohesion: 0.08
Nodes (38): One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, online(), Exception, fixture, MonkeyPatch, `research(query)`, the untrusted-content boundary, and the online gate. Two… (+30 more)

### Community 97 - "GenerationOptions"
Cohesion: 0.04
Nodes (78): Amazon Bedrock, end to end, against the real endpoint. python…, Measurement, Measure a discovered model well enough to let Smart route to it.…, A recommendation, not a decision. Somebody still reads the replies., Compress the oldest turns. Folds in any earlier note so it compounds., build_prompt(), choose_model(), CurriculumBuilder (+70 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "browser.py"
Cohesion: 0.15
Nodes (19): Page, test_fill_types_the_value_into_the_match(), test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), test_role_name_strips_the_leading_article_and_trailing_noun(), browser_fill(), _get_page(), _locate() (+11 more)

### Community 101 - "proactivity.py"
Cohesion: 0.15
Nodes (21): Candidate, default_candidates(), idle_intention_candidate(), is_stated_intention(), procedure_offer_candidate(), datetime, Path, timedelta (+13 more)

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
Cohesion: 0.09
Nodes (32): fixture, parametrize, Browser control: the checkout/banking hard block, password refusal, and element…, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, The URL check catches the common case; a card-number field on an unlisted…, No page has loaded yet at this point — only the URL being navigated *to* is…, BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM unconditionally.…, §9:943 says "regardless of tool tier" — that only means something if *every*… (+24 more)

### Community 106 - "BedrockProvider"
Cohesion: 0.09
Nodes (19): main(), BedrockProvider, current_region(), Response, ToolCall, Streamed `toolUse` fragments into finished calls. Bedrock fragments a tool call…, Implements `LLMProvider` against `bedrock-runtime` ConverseStream., No-op: a cloud model has no local load step to pay for. (+11 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "BrowserUnavailable"
Cohesion: 0.13
Nodes (14): Browser, Exception, _raising(), `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, test_navigate_adds_a_scheme_when_none_was_given(), test_navigate_reports_browser_unavailable_plainly(), test_no_user_facing_browser_error_names_chrome(), browser_navigate() (+6 more)

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

### Community 114 - "_looks_like_a_commit_action"
Cohesion: 0.22
Nodes (9): Locator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught(), test_commit_wording_in_the_visible_text_is_caught(), _looks_like_a_commit_action() (+1 more)

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "_cloud_model"
Cohesion: 0.10
Nodes (21): _cloud_model(), free_model(), health(), fixture, ModelInfo, 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement… (+13 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 121 - "bedrock.py"
Cohesion: 0.08
Nodes (30): control_url(), fetch_control(), _merge_adjacent(), Any, Amazon Bedrock, over the Converse API (Eyaas, 2026-08-23). He has a Bedrock key…, One GET against the Bedrock **control plane** — listing, not running. A…, A text block, or none at all. Converse rejects an empty `text` block outright,…, `(system, messages)` in the shape Converse accepts. Four rules, all of them… (+22 more)

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

### Community 143 - ".prune"
Cohesion: 0.40
Nodes (3): datetime, Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days.

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

### Community 149 - "ProviderUnavailable"
Cohesion: 0.14
Nodes (18): ProviderUnavailable, The backend could not be reached — offline, not running, DNS, refused. Distinct…, _parse_pull_line(), PullProgress, NamedTuple, Response, Ollama provider — the local brain, and the offline fallback (BUILD_SPEC §9.7).…, One NDJSON line, or None for keep-alive blanks and unparseable noise. (+10 more)

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

### Community 158 - "ChatMessage"
Cohesion: 0.03
Nodes (135): assemble(), clean_title(), ConversationMode, episode_request(), estimate_tokens(), fit_to_budget(), machine_context(), MachineContext (+127 more)

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

### Community 191 - "WebSearch"
Cohesion: 0.08
Nodes (22): HTMLParser, available(), Any, AsyncClient, Response, RuntimeError, Web search, and turning a page into something a model can read. BUILD_SPEC §9…, Readable text from a page, truncated on a word boundary. (+14 more)

### Community 193 - "Settings"
Cohesion: 0.12
Nodes (14): BaseSettings, _default_data_dir(), Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly., Where her database, models and logs live. **Beside the repo in development, in… (+6 more)

### Community 195 - "HealthReport"
Cohesion: 0.16
Nodes (20): dispatch(), HealthReport, _invoke(), BaseModel, Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., Rich health snapshot for the UI (§7.1 ``system.health``, §9.6)., err() (+12 more)

### Community 197 - "files_browse"
Cohesion: 0.13
Nodes (17): _enumerate_drives(), files_browse(), files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, One folder's contents, for the panel. Deliberately not `list_folder`: that tool… (+9 more)

### Community 198 - "browser_read"
Cohesion: 0.29
Nodes (7): test_read_returns_cleaned_text_with_the_url(), test_screenshot_returns_a_base64_image(), browser_read(), browser_screenshot(), tool, Read the current page as text., Screenshot the current tab. Ephemeral — never written to disk (§11), the same…

### Community 199 - "packaging.test.ts"
Cohesion: 0.29
Nodes (7): BUILDER, code(), CONFIG_PY, MAIN, PACKAGE, read(), SIDECAR

### Community 202 - "_parse_yes_no"
Cohesion: 0.50
Nodes (4): _parse_yes_no(), True/False for a clearly affirmative/negative one-line reply, else None — an…, parametrize, test_parse_yes_no()

### Community 203 - "OllamaProvider"
Cohesion: 0.09
Nodes (16): HTTPError, _discover_local_models(), Ask Ollama what is actually pulled. Never fatal — Ollama may be down., OllamaProvider, Any, ToolCall, Implements `LLMProvider` against a local Ollama daemon., Reachability only — does not check whether any model is loaded. (+8 more)

### Community 204 - "CredentialKey"
Cohesion: 0.19
Nodes (15): Which models are usable right now. One object answers this for both…, CredentialKey, delete_key(), get_key(), StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Credential Manager entry names under the ARIA service., Read a key, or None if unset. Never logs the value. (+7 more)

### Community 209 - "StoredMessage"
Cohesion: 0.20
Nodes (8): MessageHit, BaseModel, Row, Oldest-first turns for a session., Find past turns that mention what `query` is about. **This is the layer that…, A row from `messages`, as the UI and context assembly see it., One past turn that matched a `recall` query., StoredMessage

### Community 210 - "test_tts.py"
Cohesion: 0.04
Nodes (65): ndarray, RuntimeError, Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, Voice could not start. Never fatal — she still types., shorten_for_speech() (+57 more)

### Community 211 - "Retrieved"
Cohesion: 0.12
Nodes (8): Task, What one turn recalled, plus what it cost., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache., Retrieved

### Community 212 - "test_email.py"
Cohesion: 0.11
Nodes (9): Read-only IMAP. Two properties carry this feature and both are negative: it…, Subjects arrive like this more often than not, and a summariser fed the raw…, **Email is the canonical case for §11.** A web page has to be navigated to; an…, **The subtle destructive edit.** A plain `RFC822` fetch sets `\\Seen`, so a…, Not a whitelist — somebody's own mail server has to work., test_a_mime_encoded_subject_is_decoded(), test_a_real_hostname_passes_straight_through(), test_email_is_treated_as_an_untrusted_source() (+1 more)

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.29
Nodes (5): DURATION, EASE, SPRING, stagger, TWEEN

### Community 244 - "GeminiProvider"
Cohesion: 0.15
Nodes (9): _function_call_part(), GeminiProvider, Any, Response, ToolCall, Split system messages out; map assistant -> model. **Tool turns are not text.**…, Replay a tool call in the shape Gemini demands back. The signature is not…, Implements `LLMProvider` against the Gemini generateContent API. (+1 more)

### Community 246 - "gate_tool_selection.py"
Cohesion: 0.17
Nodes (16): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+8 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 255 - "estimate"
Cohesion: 0.15
Nodes (17): estimate(), for_model(), is_priced(), Rate, What a turn cost, estimated — and the word *estimated* is load-bearing.…, US dollars per million tokens., The rate for a model, or None when nobody has priced it. `local` comes from…, Cost for one turn, or None if it cannot be known. **Missing token counts are… (+9 more)

### Community 256 - "FakeSettings"
Cohesion: 0.17
Nodes (13): FakeSettings, Path, Empty by default is what keeps this one honest — on a machine that never opted…, I see you are working on X" after one keystroke is precisely the noise §9 warns…, The window is what makes this "right now" rather than "at some point". Without…, Someone renames or deletes a project. That must cost this trigger, not the tick…, It reuses the finder's own skip list rather than inventing a second one. A…, test_a_burst_of_changes_in_a_watched_folder_is_noticed() (+5 more)

### Community 257 - "email.py"
Cohesion: 0.24
Nodes (12): IMAP4_SSL, _decode(), fetch(), _fetch_one(), MailHeader, Read-only IMAP, in stdlib. `imaplib` and `email` both ship with Python, so this…, An IMAP SEARCH command. Quoted, so a query cannot inject a command., Newest first. **Blocking** — callers put it on a thread. Raises… (+4 more)

### Community 259 - "make_app_icon.py"
Cohesion: 0.17
Nodes (13): _chunk(), _geometry(), ico_bytes(), main(), _pixel(), png_bytes(), Generate resources/icon.ico — the orb, as the app icon.…, Colour and alpha at a point, in 0..1 icon coordinates. Returns straight (non-… (+5 more)

### Community 260 - "gate_permission_modes.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…

### Community 261 - "state.py"
Cohesion: 0.13
Nodes (9): Any, Where every tool call is recorded (BUILD_SPEC §7.3, CLAUDE.md rule 6). Append-…, Writes `tool_log`, and — since 2026-08-24 — reads it. **It was write-only for…, The most recent call, optionally within one session. Ordered by `id`, not…, The last few calls, newest first., ToolJournal, Process-wide runtime handles. Not in BUILD_SPEC §5. Added because RPC handlers…, Handles owned by the app lifespan. (+1 more)

### Community 262 - "test_usage.py"
Cohesion: 0.09
Nodes (29): Usage accounting, pricing, and reading an action back in plain language. The…, I have no record of that" is a true answer; an invented one is not., `stage`/`detail` are the router's own RouteReason, so a row explains itself…, `approved_by` was added precisely so an audit trail could tell them apart; an…, `type_text`'s argument is an entire essay., **The ordering that defeated the first two fixes.** OpenAI sends…, Gemini's stream ends by ending — `done` is hard-coded False. A collector that…, They are not discoverable at runtime and they will drift — the same treatment… (+21 more)

### Community 263 - "test_curriculum.py"
Cohesion: 0.11
Nodes (36): The indexed text of one file, in order, or `""` if it was never indexed. The…, source_text(), _builder(), asyncio, Turning a lecture into a concept map, and surviving what a model returns. The…, A scanned PDF or an image-only deck is a normal thing to be handed, and "no…, A subject with no concepts would render as "0 of 0 covered" forever and win…, `reflection` records why this matters: reporting the model that was *tried*… (+28 more)

### Community 264 - "ProactivityScheduler"
Cohesion: 0.23
Nodes (5): Unprompted messages (Phase 8). Off entirely when the switch is off — the same…, _start_proactivity_scheduler(), ProactivityScheduler, One pass. Never raises — a scheduler that dies stops everything, the same…, Sweeps for something worth saying, at most once per tick, and only when nothing…

### Community 265 - "configure_logging"
Cohesion: 0.31
Nodes (8): configure_logging(), _console_handler(), _file_handler(), Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file., Install the structlog + stdlib logging bridge. Idempotent.

### Community 268 - "_require_memory"
Cohesion: 0.17
Nodes (12): memory_forget(), memory_list(), memory_search(), memory_stats(), memory_update(), The memory services, or a message saying how to turn them on., Everything she has learned, for MemoryPanel. Superseded facts are excluded by…, §7.1: search what she remembers. The same path a turn uses. (+4 more)

### Community 272 - "Client"
Cohesion: 0.25
Nodes (7): Client, _copy(), main(), Any, Clipboard history, reminders, usage and explain-last-action — live. npm run dev…, Put something on the real clipboard, so the watcher sees a real change., One reader task, everything else off a queue — `gate_modes.py`'s shape.…

### Community 276 - "StudyPanel.test.tsx"
Cohesion: 0.32
Nodes (3): defaults(), state(), subject()

### Community 278 - "BedrockCredentials"
Cohesion: 0.12
Nodes (15): auth_headers(), BedrockCredentials, load_credentials(), Whichever of the two credential shapes is stored. Read once per request rather…, What is in the Credential Manager, in the order of preference. **The bearer…, Headers for one Bedrock request, by whichever credential is stored. A module…, Reachability. Must not raise (`LLMProvider`). **403 counts as reachable.** A…, A signer with no secret produces a signature nobody can verify, and the failure… (+7 more)

### Community 281 - "screen.py"
Cohesion: 0.23
Nodes (11): Never raises — losing the thumbnail is far better than losing the confirmation…, test_a_failed_capture_falls_back_to_no_preview(), _capture_jpeg(), _key(), preview_capture_screen(), Any, `capture_screen(question)` — let her see what's on screen (§9 Phase 6).…, Take the screenshot *now*, before the user is even asked — the dialog has to… (+3 more)

### Community 282 - "code_only"
Cohesion: 0.29
Nodes (7): ModuleType, code_only(), A module's source with every comment and string literal removed. **A plain…, Rule 5 names sending as destructive. There is no SMTP to guard., `STORE` sets flags and `EXPUNGE` deletes. Neither appears., test_nothing_here_can_change_a_mailbox(), test_nothing_here_can_send()

### Community 284 - "test_an_already_present_weight_is_not_downloaded_again"
Cohesion: 0.20
Nodes (11): MonkeyPatch, Path, The whole reason for the `.part`. `tts.py` decides speech is available by…, Opening the wizard twice must not cost 310MB twice., Same rule as the diagnostics export, for the same reason. `hint` is the last…, A wizard whose job is to report absence cannot fail because of it., test_a_download_lands_and_reports_a_total(), test_an_already_present_weight_is_not_downloaded_again() (+3 more)

### Community 285 - "IO"
Cohesion: 0.20
Nodes (8): IO, Import every optional subsystem and say plainly which ones are broken. **This…, Run every check. Returns the process exit code., The Silero weights faster-whisper ships as package data. Nothing imports this…, Loading the extension, not merely importing the wrapper — the wrapper is pure…, run(), _sqlite_vec(), _vad_asset()

### Community 286 - "._raise_for_detail"
Cohesion: 0.31
Nodes (4): _as_int(), Headers, Reachability, and a free chance to read the quota headers., OpenRouter's 429 says more than OpenAI's, and it is routine here. The free tier…

### Community 287 - "_study_id"
Cohesion: 0.25
Nodes (8): A row id off the wire. The panel always sends one; anything else is a caller…, Rename a subject. Not cosmetic — the name is what resuming matches on. `ok:…, Delete a subject, its map, and every answer recorded against it. **The…, Put one concept back to never-introduced. One click, where deleting a subject…, study_forget(), _study_id(), study_rename(), study_reset()

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
Nodes (98): test_with_no_mailbox_configured_it_says_what_to_add(), Launch, _paste_text(), StrEnum, Put `text` on the clipboard, send one Ctrl+V, then put the clipboard back.…, How an entry has to be started. Three sources, three launchers., tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,… (+90 more)

### Community 296 - "useFirstRun.test.ts"
Cohesion: 0.40
Nodes (3): EMPTY_STATE, Listener, listeners

### Community 300 - "find_subject"
Cohesion: 0.15
Nodes (15): find_subject(), latest_subject_id(), The subject most recently studied, for resuming without being named., Resolve a spoken subject name to an id, loosely. Exact first, then substring in…, Which subject *this* chat got to, or None if it has touched none.…, Rename a subject. False if the new name is taken or empty. The name is what…, rename_subject(), session_subject_id() (+7 more)

### Community 301 - "extract_text"
Cohesion: 0.40
Nodes (5): extract_text(), Whatever text this file has, or "" if it has none worth having. **Never…, _read_pdf(), The two entry points differ on purpose. One corrupt PDF in Downloads must not…, test_extract_text_never_raises_for_the_background_sweep()

### Community 302 - "ActivityPanel.test.tsx"
Cohesion: 0.32
Nodes (3): mockBridge(), usage(), withTimeline()

### Community 303 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 304 - "._parse_sse"
Cohesion: 0.40
Nodes (4): One `data:` frame into a StreamDelta. Non-data lines are ignored. `partial`…, **OpenAI reports usage in a frame with no `choices` at all.** `_parse_sse`…, test_a_chunk_with_neither_choices_nor_usage_is_still_nothing(), test_an_empty_choices_chunk_carrying_usage_is_not_discarded()

### Community 305 - "ClipboardPanel.tsx"
Cohesion: 0.60
Nodes (3): clock(), Entry(), preview()

### Community 307 - "_clean_stash"
Cohesion: 0.40
Nodes (5): _clean_stash(), fixture, Every test starts and ends with an empty stash — one test's leftover capture…, clear_captures(), Forget every previewed capture. For tests, and for a fresh session.

### Community 308 - "normalise_triple"
Cohesion: 0.50
Nodes (4): normalise_triple(), Fold a triple to its stored form. The UNIQUE index is on the raw columns, so…, The UNIQUE index is on raw columns, so "Prefers" and "prefers" would otherwise…, test_triples_are_folded_before_storage()

### Community 309 - ".__init__"
Cohesion: 0.50
Nodes (3): Path, Start `ollama serve` as its own process, with no console window. Detached on…, _spawn_detached()

### Community 314 - "icon.test.ts"
Cohesion: 0.29
Nodes (3): Entry, EXPECTED_SIZES, ICON

### Community 315 - "_fence"
Cohesion: 0.50
Nodes (4): test_the_mail_is_fenced_as_data_before_and_after(), test_the_unread_state_is_shown_per_message(), _fence(), The mail, labelled as data. §11, and here it earns its keep. Before *and* after…

### Community 316 - "db.py"
Cohesion: 0.09
Nodes (25): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Apply one migration file atomically and stamp `user_version`. The vec0 virtual… (+17 more)

### Community 317 - "WakeWord"
Cohesion: 0.08
Nodes (12): The wake model, or None in PHRASE mode - which is the default. Exposed so the…, Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, ndarray, Protocol, RuntimeError, Score one frame of int16 audio. Returns 0.0 while debounced. Callers must await… (+4 more)

### Community 318 - "EmailUnavailable"
Cohesion: 0.67
Nodes (3): EmailUnavailable, RuntimeError, Could not reach or sign in to the mailbox. Carries what to do next.

### Community 319 - "_resolve_bias"
Cohesion: 0.67
Nodes (3): RoutingBias, A hand-edited settings row must not stop the sidecar booting., _resolve_bias()

### Community 321 - "test_legacy_office_names_the_fix_rather_than_the_failure"
Cohesion: 0.67
Nodes (3): parametrize, The actual incident: a lecture `.ppt` was skipped and the only record was a log…, test_legacy_office_names_the_fix_rather_than_the_failure()

### Community 324 - "probe.py"
Cohesion: 0.67
Nodes (3): main(), Diagnose the frozen-only "cannot load module more than once per process". **Not…, show()

### Community 326 - "_next_level"
Cohesion: 0.33
Nodes (6): _next_level(), One answer's effect on a level. **A level is a running score, not a verdict on…, **The load-bearing rule.** One correct pick from four options is a 25% coin…, 0 means "never seen", and that stops being true once it is taught. Collapsing…, test_a_wrong_answer_never_takes_a_concept_back_to_never_introduced(), test_mastery_cannot_be_reached_in_one_answer()

### Community 337 - "PanelBoundary"
Cohesion: 0.25
Nodes (3): PanelBoundary, Props, State

### Community 342 - "look_at_the_ui.py"
Cohesion: 0.50
Nodes (4): _chromium(), main(), Look at the UI, without taking over anybody's screen. npm run dev # in another…, Playwright's own Chromium, whichever build is installed. Its Python package…

### Community 348 - "test_every_sub_mode_has_a_policy_and_an_opener"
Cohesion: 0.67
Nodes (3): parametrize, A sub-mode with no opener is a button that sends nothing., test_every_sub_mode_has_a_policy_and_an_opener()

### Community 351 - "study_export_rpc"
Cohesion: 0.40
Nodes (5): Save a subject's map to Documents/ARIA Study, and say where it went. The panel…, study_export_rpc(), Path, Write it, never over anything. Blocking, so callers use a thread., _write_export()

## Knowledge Gaps
- **390 isolated node(s):** `DATA_DIR`, `startHidden`, `APP_ICON`, `sidecar`, `rpc` (+385 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **80 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `FakeSettings`, `EpisodicMemory`, `state.py`, `test_reflection.py`, `test_curriculum.py`, `test_procedures.py`, `undo.py`, `ProactivityScheduler`, `test_usage.py`, `state`, `finder.py`, `Indexer`, `test_conversation.py`, `ConversationStore`, `memory/study.py`, `SemanticMemory`, `main.py`, `_start_conversation`, `test_study_tools.py`, `conversation.py`, `test_db.py`, `find_subject`, `ConversationService`, `test_proactivity.py`, `test_reminders.py`, `test_clipboard_history.py`, `StreamDelta`, `db.py`, `OllamaEmbeddings`, `test_affect.py`, `Fact`, `affect.py`, `StoredMessage`, `test_study_modes.py`, `test_tts.py`, `test_retrieval.py`, `soak_conversation.py`, `GenerationOptions`, `proactivity.py`, `AffectState`, `_repeated_failures`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `finder.py`, `apps.py`, `test_screen.py`, `screen.py`, `test_study_tools.py`, `conversation.py`, `test_organize.py`, `PermissionEngine`, `files.py`, `ConversationService`, `find_subject`, `_suppress_close_errors`, `test_ask.py`, `test_tools.py`, `browser_read`, `FakePage`, `MonkeyPatch`, `test_email.py`, `test_research.py`, `browser.py`, `test_browser.py`, `BrowserUnavailable`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `state.py`, `KokoroTTS`, `test_conversation.py`, `test_modes.py`, `ConversationStore`, `ProviderUnavailable`, `HealthTracker`, `main.py`, `_start_conversation`, `ChatMessage`, `conversation.py`, `RouteDecision`, `ModelInfo`, `PermissionEngine`, `Router`, `Listener`, `ToolContext`, `test_ask.py`, `test_reminders.py`, `StreamDelta`, `EventBus`, `Database`, `WakeWord`, `StoredMessage`, `test_tts.py`, `Retrieved`, `soak_conversation.py`, `GenerationOptions`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `ToolContext` (e.g. with `ConversationHistory` and `ConversationService`) actually correct?**
  _`ToolContext` has 29 INFERRED edges - model-reasoned connections that need verification._