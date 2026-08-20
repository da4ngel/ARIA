# Graph Report - ARIA  (2026-08-20)

## Corpus Check
- 246 files · ~354,485 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 5075 nodes · 11572 edges · 274 communities (203 shown, 71 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1021 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0df05cbe`
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
- test_finder.py
- apps.py
- Indexer
- gate_wakeword.py
- test_modes.py
- ConversationStore
- EpisodicMemory
- HealthTracker
- SemanticMemory
- test_screen.py
- messages.py
- state.py
- test_router.py
- test_extract.py
- handlers.py
- OpenEngine
- RoutingLog
- test_organize.py
- Router
- Fact
- test_retrieval.py
- PermissionEngine
- Reflector
- listener.py
- Listener
- test_db.py
- AdoptionService
- test_focus.py
- test_episodic.py
- ARIA — Project Instructions
- ToolContext
- ConversationService
- ProviderUnavailable
- test_ask.py
- test_questions.py
- EventBus
- eval_quality.py
- test_text.py
- ChatMessage
- call_key
- compilerOptions
- Event
- Connectivity
- FakeProvider
- snapshot
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- main.py
- compilerOptions
- test_conversation.py
- context.py
- SpeechStream
- test_tools.py
- test_vectors.py
- test_context.py
- test_browser_setup.py
- LLMProvider
- test_affect.py
- Utterance
- test_research.py
- extract.py
- attachments.py
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- _cloud_model
- test_adoption.py
- system.py
- discovery.py
- CredentialKey
- FilesPanel.tsx
- Sidecar
- Client
- .upsert
- parametrize
- _suppress_close_errors
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- retrieved_block
- free_model
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- Retriever
- SettingsStore
- PermissionEngine
- routing_log.py
- FilesPanel.test.tsx
- Question
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- test_browser.py
- .new_session
- render
- gate_organize.py
- _json_type
- HistoryPanel.tsx
- CLAUDE.md — ARIA Project Instructions (Claude Code-facing)
- Router — local vs cloud, then which provider
- gate_affect.py
- configure_logging
- AffectState
- usePermissionMode.ts
- OllamaProvider
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- gate_research.py
- ask_user
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
- questions.py
- MemoryPanel.tsx
- She holds a conversation now (2026-08-07)
- Measuring answer quality
- Smart mode: it was the tool, and then it was the router (2026-08-12)
- RateLimitState
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
- by_class
- electron-vite
- framer-motion
- jsdom
- react-markdown
- remark-gfm
- tailwindcss
- @testing-library/react
- @types/node
- @types/react
- @types/react-dom
- test_openrouter.py
- typescript
- vite
- @vitejs/plugin-react
- vitest
- sidecar/__init__.py
- persona/__init__.py
- set_discovered
- test_the_gate_is_the_same_probes_the_scripts_use
- test_a_short_code_request_is_not_answered_locally_to_save_time
- test_a_spoken_conversational_turn_still_stays_local
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
- PersonaLevel
- Any
- RpcMethodError
- WakeWord
- OpenRouterProvider
- tokens.js
- rpc.ts
- test_ordinary_questions_do_not_get_the_expensive_tier
- MemoryServices
- useConversation.test.ts
- test_every_attachment_is_reported_to_the_renderer
- .prune
- payload
- _vector
- autoprefixer
- .cancel_all
- .forget
- eval/__init__.py
- test_the_prompt_never_claims_she_remembers_nothing
- test_an_ordinary_question_still_takes_the_fast_class
- electron-builder
- test_a_spoken_turn_still_stays_local
- test_a_spoken_command_is_no_longer_forced_onto_the_local_model
- test_a_command_is_not_slowed_down_for_a_difference_that_is_noise

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

## Communities (274 total, 71 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (108): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+100 more)

### Community 1 - "test_listener.py"
Cohesion: 0.06
Nodes (67): drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on… (+59 more)

### Community 2 - "main.ts"
Cohesion: 0.15
Nodes (21): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+13 more)

### Community 3 - "test_catalog.py"
Cohesion: 0.08
Nodes (36): default_local(), persona_for(), The local fallback. Prefers the instruction-tuned 7B. `pulled` is what Ollama…, Persona level for a model; unknown ids get the safe, minimal prompt., Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from., resolve_availability(), usable_ids() (+28 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.08
Nodes (52): files_browse(), files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, One folder's contents, for the panel. Deliberately not `list_folder`: that tool…, Show it in Explorer. The escape hatch for anything this panel does not do. (+44 more)

### Community 5 - "test_reflection.py"
Cohesion: 0.12
Nodes (28): _extract_json(), Any, Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio, parametrize, The nightly §8.3 pass. Two things are load-bearing and both are about a local…, A key can be present while the account is dead, which is exactly this machine's…, The gate's fourth line, from the reflection side. (+20 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.09
Nodes (39): One attachment, understood. Never raises., The block that goes into the prompt. **Fenced as untrusted content**, exactly…, read_one(), render(), MonkeyPatch, Path, Files the user hands her. Eyaas: *"i should be also be able to file uploads…, There is no local vision model (rule 2), so no key is a real state with an… (+31 more)

### Community 7 - "test_tts.py"
Cohesion: 0.04
Nodes (63): ndarray, RuntimeError, Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, Voice could not start. Never fatal — she still types., shorten_for_speech() (+55 more)

### Community 8 - "Database"
Cohesion: 0.07
Nodes (59): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+51 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.06
Nodes (65): Candidate, default_candidates(), idle_intention_candidate(), is_stated_intention(), ProactivityScheduler, datetime, Path, timedelta (+57 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.11
Nodes (29): parse_openai(), Chat models from a `GET /v1/models` body., gemini_ids(), _load(), openai_ids(), Any, fixture, parametrize (+21 more)

### Community 12 - "KokoroTTS"
Cohesion: 0.06
Nodes (35): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+27 more)

### Community 13 - "ModelInfo"
Cohesion: 0.07
Nodes (39): adopt(), adopted(), all_models(), clear_adopted(), Cost, discovered(), get(), local_models() (+31 more)

### Community 14 - "test_finder.py"
Cohesion: 0.07
Nodes (43): _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The…, Make `find_files` deterministic and count how often it really walks., The reason the cache exists at all — two questions in a row must not walk three… (+35 more)

### Community 15 - "apps.py"
Cohesion: 0.03
Nodes (93): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, §7.2's second failure mode: the model gets one line, the UI gets the lot., 7 zip" matched "7-Zip Help" purely because it is the shorter name., The demotion must not make the entry unreachable., Opening the wrong app is worse than opening nothing., This is what stops "open youtube" launching the YouTube Music app: the website…, A dead end is useless; naming the closest lets the model retry. (+85 more)

### Community 16 - "Indexer"
Cohesion: 0.09
Nodes (29): chunk(), _digest(), Indexer, Path, Whether this file is worth reading at all., Cheap identity: re-reading a 10MB PDF to decide whether to re-read it would…, Walks, reads, embeds and stores — slowly, and out of the way., Hold here while the machine is busy or she is answering. (+21 more)

### Community 17 - "gate_wakeword.py"
Cohesion: 0.07
Nodes (25): frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python…, say(), SilentBus (+17 more)

### Community 18 - "test_modes.py"
Cohesion: 0.06
Nodes (43): policy_for(), ConversationMode, The policy, or Normal's. Never raises. A mode arriving from a stale client is a…, A mode this turn would be better served by, or None. None is the answer for the…, suggest(), ConversationMode, parametrize, Modes as operating systems, not tones. Eyaas's own framing after using the… (+35 more)

### Community 19 - "ConversationStore"
Cohesion: 0.06
Nodes (43): ConversationStore, _now(), CRUD over `sessions` and `messages`., Return an existing session id, or create one., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, When anything was last said, in any session. The whole precondition for §9's… (+35 more)

### Community 20 - "EpisodicMemory"
Cohesion: 0.04
Nodes (53): SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Episode, EpisodicMemory, _now(), BaseModel, datetime, Row, StoredMessage (+45 more)

### Community 21 - "HealthTracker"
Cohesion: 0.08
Nodes (29): HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture (+21 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.08
Nodes (46): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:…, §8.3 caps at 0.95. Repetition is evidence, not proof. (+38 more)

### Community 23 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 24 - "messages.py"
Cohesion: 0.11
Nodes (17): concrete_tokens(), main(), novel_tokens(), Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket., Recorder (+9 more)

### Community 25 - "state.py"
Cohesion: 0.05
Nodes (47): find_ollama(), OllamaSupervisor, Path, Keep Ollama running, and notice when it comes back. Eyaas: *"sometimes when…, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was… (+39 more)

### Community 26 - "test_router.py"
Cohesion: 0.10
Nodes (37): is_local(), RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort., Observed latency overrides the seeded table as turns land., The router must always answer. A turn with no candidates is a crash., Local models are multi-GB downloads that may not have finished. (+29 more)

### Community 27 - "test_extract.py"
Cohesion: 0.12
Nodes (32): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+24 more)

### Community 28 - "handlers.py"
Cohesion: 0.04
Nodes (100): build_health(), chat_cancel(), chat_delete(), chat_history(), chat_new(), chat_rename(), chat_send(), chat_sessions() (+92 more)

### Community 29 - "OpenEngine"
Cohesion: 0.11
Nodes (41): A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, OpenEngine, ToolCall, §11 escalates the step after *reading* untrusted content. A `research` that was…, Decided with Eyaas (2026-08-18): §11 guards against untrusted content reaching…, The half that did not move, asserted beside the half that did — the narrowing…, Test with set of mcqs one after the other" is a real request, and a one-per-… (+33 more)

### Community 30 - "RoutingLog"
Cohesion: 0.11
Nodes (24): Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Writes and reads `routing_log`. Never raises into the turn path., RoutingLog, Connection, fixture, §9.7's labelled dataset: what the router decided, and what the user thought.… (+16 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (76): _default_data_dir(), get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Where her database, models and logs live. **Beside the repo in development, in…, Process-wide settings singleton., messy(), fixture, MonkeyPatch (+68 more)

### Community 32 - "Router"
Cohesion: 0.11
Nodes (24): is_tool_shaped(), BaseModel, ModelInfo, StrEnum, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, A request to act on the machine rather than to talk about something., Whether this endpoint may train on what is sent to it. Unknown ids read as…, Chooses a model for a turn. (+16 more)

### Community 33 - "Fact"
Cohesion: 0.14
Nodes (11): Fact, BaseModel, Row, The form that gets embedded and shown in the prompt., A stored `fact_vec` row back into floats, or None if it has no vector., Edit a fact from the panel. Returns None if it is gone., Nearest active facts to a vector, as (fact, cosine). Mirrors…, Embed facts written while Ollama was down. Chat must never wait on embeddings,… (+3 more)

### Community 34 - "test_retrieval.py"
Cohesion: 0.10
Nodes (38): 1.0 today, 0.5 after a month, never quite zero., recency_decay(), anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A memory that keeps coming up is worth surfacing, but not enough to outrank…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice. (+30 more)

### Community 35 - "PermissionEngine"
Cohesion: 0.07
Nodes (32): EscalateFn, PreviewFn, RefuseFn, It is a strong constraint — it overrides the router — so it should be…, test_no_registered_tool_documents_an_argument_it_then_truncates(), test_nothing_else_claims_local_only(), Bus, Journal (+24 more)

### Community 36 - "Reflector"
Cohesion: 0.11
Nodes (15): choose_model(), datetime, ModelInfo, §8.3: cloud if a key is present, local otherwise. Walks SMART then BALANCED,…, One nightly pass: read the day, extract facts, merge, prune., Read the window, extract, merge, prune. Never raises., Ask the chosen model, falling back to local on any provider failure., How many messages have arrived since the last successful reflection. Cheap… (+7 more)

### Community 37 - "listener.py"
Cohesion: 0.11
Nodes (24): clips(), main(), ndarray, Can she hear her own name? Across many voices, because one is not a test.…, score(), is_stop_word(), _near_the_name(), Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3). The renderer opens the… (+16 more)

### Community 38 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 39 - "test_db.py"
Cohesion: 0.07
Nodes (41): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, Run ``fn`` against the connection off the event loop, serialised., Every table in the database, including vec0 virtual tables. (+33 more)

### Community 40 - "AdoptionService"
Cohesion: 0.08
Nodes (29): Probe, AdoptionService, AdoptionState, grade(), _probes_by_id(), Any, BaseModel, date (+21 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "test_episodic.py"
Cohesion: 0.09
Nodes (41): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., _conversation(), _episodic(), anyio, Connection (+33 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "ToolContext"
Cohesion: 0.04
Nodes (99): Launch, StrEnum, How an entry has to be started. Three sources, three launchers., `ask_user` — put the choice on screen instead of describing it. The mechanism,…, tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, The clipboard's text, or None when it holds something else. An image, a file… (+91 more)

### Community 45 - "ConversationService"
Cohesion: 0.03
Nodes (73): SessionSummary, exhausted_note(), LoopState, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through…, Told to the model, not just logged — it should know why it stopped., The budget is per-turn now, so the number has to be passed in. It reads as a… (+65 more)

### Community 46 - "ProviderUnavailable"
Cohesion: 0.06
Nodes (27): ProviderUnavailable, The backend could not be reached — offline, not running, DNS, refused. Distinct…, build_all(), for_provider(), One place that knows how to build a provider from its name. **This exists…, A client for one provider. Raises on anything unrecognised. **Never a…, Every provider, keyed by name — the shape `ProviderRegistry` wants. Built by…, GeminiProvider (+19 more)

### Community 47 - "test_ask.py"
Cohesion: 0.12
Nodes (20): ask_tool(), `ask_user`: the registry entry, and the schema the model has to produce. The…, **The first restriction overshot, and Eyaas caught it on screen.** Asked "can u…, Pydantic hoists nested models into `$defs` and points at them with `$ref`.…, The first version only reached the top level. Pydantic emits a title per class…, **There was a one-question-per-turn cap here, and it was wrong.** Asked to…, `registry.get` is `Tool | None`, and a missing tool here means the import in…, `Tier.AUTO`, because asking changes nothing on the machine. A confirmation… (+12 more)

### Community 48 - "test_questions.py"
Cohesion: 0.13
Nodes (21): Answer, QuestionBroker, What came back for one question., Puts a question on screen and waits for the answer., Resolve a waiting question. False if it already went., FakeBus, Any, The ask-and-wait broker: what it guarantees, and what it refuses to assume. The… (+13 more)

### Community 49 - "EventBus"
Cohesion: 0.14
Nodes (12): EventBus, Any, Protocol, Server -> client push notifications and the set of live connections (§7.1).…, Minimal transport surface — a Starlette WebSocket satisfies this., Tracks connected clients and broadcasts notifications to them., Send the current state to one client, unconditionally. A reconnecting renderer…, Send a notification to every live client, dropping dead ones. (+4 more)

### Community 50 - "eval_quality.py"
Cohesion: 0.08
Nodes (35): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+27 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "ChatMessage"
Cohesion: 0.05
Nodes (61): Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, split_for_rollup(), Compress the oldest turns. Folds in any earlier note so it compounds., build_prompt(), ExtractedEpisode, ExtractedFact, BaseModel, Reflection — where "learns on its own" actually lives (BUILD_SPEC §8.3). Once a… (+53 more)

### Community 53 - "call_key"
Cohesion: 0.47
Nodes (4): call_key(), Any, Mark one step as run. `local_only` is unknown, not False, for a tool the…, A hashable fingerprint of one tool call, for loop detection. Sorted so argument…

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "Event"
Cohesion: 0.07
Nodes (28): Any, ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout. (+20 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "FakeProvider"
Cohesion: 0.09
Nodes (35): chat_mode(), Read or set a conversation's mode. Omit `mode` to read. The read-or-write shape…, FakeProvider, make_service(), fixture, MonkeyPatch, The whole reason this is per-conversation rather than a setting: a mode chosen…, The Phase 1 gate: kill the window, conversation reloads from SQLite. (+27 more)

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
Cohesion: 0.04
Nodes (67): BaseSettings, FastAPI, get, Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly. (+59 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "test_conversation.py"
Cohesion: 0.09
Nodes (35): _drain(), _proactivity_service(), Connection, parametrize, Turn orchestration, cancellation, persistence and context roll-up., A proactive message needs somewhere to live even before the user has ever said…, The whole point of writing a `routing_log` row for it: the *existing*…, Wait for all in-flight turns. (+27 more)

### Community 64 - "context.py"
Cohesion: 0.08
Nodes (29): clean_title(), ConversationMode, episode_request(), _mode_block(), mode_done_when(), mode_label(), _persona(), datetime (+21 more)

### Community 65 - "SpeechStream"
Cohesion: 0.10
Nodes (16): datetime, ModelInfo, StoredMessage, ToolCall, Which model gets to see the tool's result. `router._PRIVATE` already keeps a…, Evict the previous local model before loading a different one. CLAUDE.md rule…, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Say a reply aloud, on request. False when there is no voice engine. The other… (+8 more)

### Community 66 - "test_tools.py"
Cohesion: 0.03
Nodes (116): _focused(), MonkeyPatch, parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V… (+108 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (23): cosine(), cosine_from_l2(), normalise(), pack(), Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for…, Cosine similarity of two vectors, normalised or not. Used by the merge step,… (+15 more)

### Community 68 - "test_context.py"
Cohesion: 0.07
Nodes (53): machine_context(), MachineContext, overhead_tokens(), Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, Tokens spent before the conversation even starts. Roll-up decisions must…, volatile_prefix() (+45 more)

### Community 69 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+9 more)

### Community 70 - "LLMProvider"
Cohesion: 0.10
Nodes (22): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+14 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "Utterance"
Cohesion: 0.11
Nodes (8): ndarray, Protocol, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance, VoiceActivity

### Community 73 - "test_research.py"
Cohesion: 0.05
Nodes (57): AsyncClient, HTMLParser, An epub is a zip of XHTML. Tags are stripped rather than parsed — the same call…, _read_epub(), Any, Response, RuntimeError, Readable text from a page, truncated on a word boundary. (+49 more)

### Community 74 - "extract.py"
Cohesion: 0.11
Nodes (24): _extract_bytes(), extract_text(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as… (+16 more)

### Community 75 - "attachments.py"
Cohesion: 0.14
Nodes (20): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no…, Every attachment on one message, in the order they were given. Sequential… (+12 more)

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
Nodes (49): ProviderQuotaExhausted, The **account's** allowance is gone, not this model's. A 429 usually means…, a_model(), Asker, Clock, perfect_reply(), Any, ModelInfo (+41 more)

### Community 81 - "system.py"
Cohesion: 0.15
Nodes (21): test_system_info_reports_this_machine(), _endpoint_volume(), _facts(), get_system_info(), kill_process(), Any, tool, Facts about the machine, and the one knob she can turn on it. `get_system_info`… (+13 more)

### Community 82 - "discovery.py"
Cohesion: 0.13
Nodes (23): discover_all(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch(), _gemini_class(), _gemini_is_chat(), _gemini_is_duplicate() (+15 more)

### Community 83 - "CredentialKey"
Cohesion: 0.11
Nodes (26): Which models are usable right now. One object answers this for both…, ModelAvailability, ModelListing, BaseModel, A catalog entry plus whether it can actually be used right now., `models.list` result., all_status(), CredentialKey (+18 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "Sidecar"
Cohesion: 0.19
Nodes (3): HealthBody, Sidecar, SidecarOptions

### Community 86 - "Client"
Cohesion: 0.29
Nodes (7): Client, main(), Any, Does she ask well, and — more importantly — does she stop asking? python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Send, answer anything she waits on, and return the completed turn. `pick` is…, section()

### Community 87 - ".upsert"
Cohesion: 0.11
Nodes (13): Write one decision. Returns its id, or None if it could not be., normalise_triple(), _now(), Fold a triple to its stored form. The UNIQUE index is on the raw columns, so…, Merge one observation into the store, per §8.3. Order matters: 1. **Exact…, §8.3: exact triple → evidence_count += 1, confidence += 0.1 (cap 0.95)., Write the fact and its vector in one transaction. One transaction is not…, Embed, or None. Never raises — a fact without a vector still counts. (+5 more)

### Community 88 - "parametrize"
Cohesion: 0.14
Nodes (15): is_trivial(), needs_deep_model(), A greeting or acknowledgement — nothing a 4B model can get wrong., Reasoning, code, or a multi-step request: the `smart` class earns its cost., parametrize, The line that was missing. Without it these went to the FAST class., A false positive costs a spoken turn its ~800ms head start, which is the thing…, test_clipboard_questions_stay_on_this_machine() (+7 more)

### Community 89 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 90 - "Sidebar.tsx"
Cohesion: 0.13
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 92 - "retrieved_block"
Cohesion: 0.12
Nodes (19): estimate_tokens(), fit_to_budget(), Render remembered facts and episodes into one system message. Returns None when…, Drop oldest turns until the assembled prompt fits. Backstop, not policy.…, _render_memory(), retrieved_block(), A turn about something she has no memory of must leave the prompt byte-…, A fact is a standing truth; an episode is one conversation. (+11 more)

### Community 93 - "free_model"
Cohesion: 0.17
Nodes (12): free_model(), health(), fixture, ModelInfo, A free OpenRouter model, adopted so the router can actually reach it.…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make…, Stage 1 already works this way for privacy, and this sits after it. Overriding… (+4 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): electron, devDependencies, electron, postcss, react, react-dom, @types/ws, zustand (+5 more)

### Community 96 - "Retriever"
Cohesion: 0.16
Nodes (9): Task, Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache., Cancel any embed still running past its deadline. Without this, shutting down… (+1 more)

### Community 97 - "SettingsStore"
Cohesion: 0.06
Nodes (30): ModelAvailability, Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason. (+22 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "routing_log.py"
Cohesion: 0.20
Nodes (6): ModelVerdict, BaseModel, What the router decided, and what the user made of it (§9.7). §9.7's closing…, Per-model tallies. The dataset §9.7 wants, as far as it has grown., How a model has actually been received, per `routing_log`., Liked as a fraction of rated, or None while it would be noise.

### Community 101 - "Question"
Cohesion: 0.15
Nodes (16): normalise(), Option, Pending, BaseModel, Question, Trim to the caps and give every question its escape hatch. Done here rather…, Broadcast, then wait. Never raises for an ordinary outcome., One answer the user can pick. (+8 more)

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
Cohesion: 0.04
Nodes (106): Browser, Locator, Page, FakeLocator, FakePage, Exception, fixture, MonkeyPatch (+98 more)

### Community 106 - ".new_session"
Cohesion: 0.40
Nodes (4): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "_json_type"
Cohesion: 0.13
Nodes (16): The schema change is a capability, not a special case for this tool., test_a_plain_model_argument_also_works(), It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, test_a_wrapped_argument_description_survives_the_line_break(), _arg_docs(), build_parameters(), _json_type(), _model_schema() (+8 more)

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

### Community 114 - "configure_logging"
Cohesion: 0.15
Nodes (15): configure_logging(), _console_handler(), _file_handler(), Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file., Install the structlog + stdlib logging bridge. Idempotent. (+7 more)

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "OllamaProvider"
Cohesion: 0.14
Nodes (7): HTTPError, OllamaProvider, Response, Reachability only — does not check whether any model is loaded., Load `model` with a 1-token request so the user never hits cold start., Evict `model` from VRAM now, instead of after `keep_alive`. CLAUDE.md rule 2:…, Implements `LLMProvider` against a local Ollama daemon.

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 121 - "ask_user"
Cohesion: 0.15
Nodes (15): a_question(), broker(), fixture, MonkeyPatch, `summary` is the only field the model sees., **`ok=False` would make her apologise for his silence.** Nothing went wrong; he…, Unreachable in the app, but a tool that raises fails the whole turn and this…, A stand-in for `runtime.questions`, recording what it was asked. (+7 more)

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
Cohesion: 0.06
Nodes (46): Check, Answered something that has no answer, or claimed an action it cannot perform.…, admits_ignorance(), answers_flatly(), claimed_action(), contains(), contains_any(), denies_capability() (+38 more)

### Community 142 - "gate_agent.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 6's agent loop, against the running sidecar. "find <scratch file>,…

### Community 143 - "questions.py"
Cohesion: 0.26
Nodes (11): Asked, Asking the user something and waiting for the answer. Eyaas: *"if u are gonna…, The result of one `ask_user` call., The one-line-per-question summary that goes back to the model. **`summary` is…, render(), a_question(), `summary` is the only field the model ever sees, so it has to carry the answers…, Otherwise the next step asks the same thing, which is how a question becomes a… (+3 more)

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

### Community 149 - "RateLimitState"
Cohesion: 0.17
Nodes (7): RateLimitState, Turn reasoning off where the endpoint allows it, and count the call. This is…, How much of the free daily allowance ARIA has spent, and it is a count. **The…, **Checked live on 2026-08-19, and the first version was wrong.** OpenRouter…, The header reader is kept because a 429 is documented to carry them. If a real…, test_a_stated_figure_beats_the_local_count(), test_the_free_allowance_is_counted_here_because_the_api_does_not_say()

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

### Community 191 - "by_class"
Cohesion: 0.22
Nodes (9): by_class(), The router's pool: **measured only** — curated, or adopted after passing. The…, **The load-bearing test of the whole feature.** `by_class` is the router's only…, A **rejected** model is as unroutable as an unmeasured one. Adoption's whole…, The other direction, and the point of the whole feature. Without this,…, test_each_class_has_a_cloud_model_so_routing_can_resolve(), test_smart_does_route_to_a_model_that_passed(), test_smart_never_routes_to_a_discovered_model() (+1 more)

### Community 202 - "test_openrouter.py"
Cohesion: 0.11
Nodes (26): parse_openrouter(), Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, OpenRouter: the provider, and the filters that decide what is even offered. The…, `openrouter/free` forwards to whichever free model it likes. Measuring it would…, An expired id 404s mid-turn, which reads as ARIA being broken., Fail towards keeping it: a bad date string is not evidence of anything., The rule the whole discovery module is built on. `Cost.FREE` is the one…, A property of the endpoint, not of the model. OpenRouter's free tier can route… (+18 more)

### Community 209 - "set_discovered"
Cohesion: 0.25
Nodes (8): Replace what the providers said they offer. A curated id always wins: `gpt-5`…, set_discovered(), CLAUDE.md's *"always send `think: false` to Ollama"* rule, second provider. A…, **A hard 400, not a warning**, and it kills the whole turn. Measured live:…, The cost of not sending it is wasted tokens; the cost of sending it wrongly is…, test_an_unknown_model_fails_open(), test_it_is_never_sent_to_an_endpoint_that_requires_reasoning(), test_reasoning_is_turned_off_where_the_endpoint_allows_it()

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.29
Nodes (5): DURATION, EASE, SPRING, stagger, TWEEN

### Community 244 - "PersonaLevel"
Cohesion: 0.11
Nodes (26): assemble(), PersonaLevel, StrEnum, Content identical across turns. Everything here is KV-cached. Changing `level`…, How much character a model can carry without falling apart. Measured on…, Build the final message list, stable content first., stable_prefix(), ConversationMode (+18 more)

### Community 245 - "Any"
Cohesion: 0.25
Nodes (8): _openrouter_benchmark(), _openrouter_expired(), _openrouter_is_free(), Any, date, Free on **both** sides of the meter. `pricing.prompt == "0"` alone would admit…, Artificial Analysis' published intelligence index, if OpenRouter has one. A…, Free models come and go, and OpenRouter says when. An expired id 404s mid-turn,…

### Community 246 - "RpcMethodError"
Cohesion: 0.25
Nodes (8): permissions_mode(), Read or replace the global permission mode (manual / auto / full_access). Same…, Exception, Raised by a handler to return a specific JSON-RPC error to the client., RpcMethodError, PermissionMode, StrEnum, A global preset over the same machinery below — it never adds a new way to…

### Community 247 - "WakeWord"
Cohesion: 0.07
Nodes (17): main(), Download the wake word weights into data/models/openwakeword. python…, Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, missing_models(), ndarray, Path (+9 more)

### Community 248 - "OpenRouterProvider"
Cohesion: 0.11
Nodes (16): _as_int(), OpenRouterProvider, Any, Headers, OpenAI's wire format, someone else's models. Subclassing rather than copying is…, Reachability, and a free chance to read the quota headers., OpenRouter's 429 says more than OpenAI's, and it is routine here. The free tier…, The raw catalogue OpenRouter offers today. Unauthenticated on purpose —… (+8 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 255 - "rpc.ts"
Cohesion: 0.29
Nodes (5): Pending, RpcEnvelope, RpcError, RpcErrorShape, RpcNotification

### Community 257 - "MemoryServices"
Cohesion: 0.29
Nodes (7): MemoryServices, Everything Phase 5 hands to the conversation, as one argument.…, anyio, `episodes.session_id` is a foreign key, so the store's delete raises unless the…, Every memory call site is a no-op when `memory` is None — Phase 4's behaviour,…, test_a_turn_without_memory_behaves_exactly_as_before(), test_deleting_a_conversation_clears_its_episodes_first()

### Community 259 - "test_every_attachment_is_reported_to_the_renderer"
Cohesion: 0.29
Nodes (7): Path, The divergent-state bug: reading is sequential and every image is a cloud round…, The actual bug. An unreadable file was recorded in a log line and nowhere a…, The guarantee the non-blocking move must not break., test_a_readable_attachment_still_reaches_the_first_pass(), test_every_attachment_is_reported_to_the_renderer(), test_send_returns_before_the_files_are_read()

### Community 260 - ".prune"
Cohesion: 0.40
Nodes (3): datetime, Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days.

### Community 261 - "payload"
Cohesion: 0.67
Nodes (3): payload(), Any, fixture

## Knowledge Gaps
- **336 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+331 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **71 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `MemoryServices`, `test_tts.py`, `Database`, `ModelInfo`, `test_modes.py`, `ConversationStore`, `HealthTracker`, `messages.py`, `state.py`, `OpenEngine`, `RoutingLog`, `Router`, `PermissionEngine`, `listener.py`, `Listener`, `ToolContext`, `ProviderUnavailable`, `test_ask.py`, `EventBus`, `eval_quality.py`, `ChatMessage`, `Event`, `FakeProvider`, `main.py`, `test_conversation.py`, `SpeechStream`, `LLMProvider`, `SettingsStore`, `.new_session`, `RpcMethodError`, `WakeWord`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `MemoryServices`, `test_every_attachment_is_reported_to_the_renderer`, `test_reflection.py`, `test_tts.py`, `test_proactivity.py`, `Indexer`, `ConversationStore`, `EpisodicMemory`, `SemanticMemory`, `messages.py`, `state.py`, `OpenEngine`, `RoutingLog`, `Fact`, `test_retrieval.py`, `Reflector`, `test_db.py`, `test_episodic.py`, `ConversationService`, `ChatMessage`, `FakeProvider`, `main.py`, `test_conversation.py`, `SpeechStream`, `test_affect.py`, `affect.py`, `SettingsStore`, `routing_log.py`, `AffectState`, `_repeated_failures`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `SpeechStream`, `test_tools.py`, `_suppress_close_errors`, `PermissionEngine`, `test_browser.py`, `test_research.py`, `ConversationService`, `test_finder.py`, `test_ask.py`, `apps.py`, `system.py`, `RpcMethodError`, `test_screen.py`, `ask_user`, `test_organize.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 51 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._