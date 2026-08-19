# Graph Report - ARIA  (2026-08-19)

## Corpus Check
- 243 files · ~349,344 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 5046 nodes · 11505 edges · 263 communities (195 shown, 68 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1010 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e5fa387c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_permissions.py
- test_listener.py
- main.ts
- test_catalog.py
- test_rpc.py
- ConversationService
- test_attachments.py
- test_tts.py
- Database
- test_scheduler.py
- test_proactivity.py
- test_discovery.py
- Event
- apps.py
- finder.py
- test_tools.py
- Indexer
- SileroVAD
- test_modes.py
- ConversationStore
- OllamaEmbeddings
- HealthTracker
- SemanticMemory
- test_screen.py
- soak_conversation.py
- test_ollama_supervisor.py
- test_router.py
- extract.py
- handlers.py
- test_conversation.py
- RoutingLog
- test_organize.py
- Router
- Fact
- test_retrieval.py
- Tier
- WakeMode
- listener.py
- Listener
- test_db.py
- AdoptionService
- test_focus.py
- test_reflection.py
- ARIA — Project Instructions
- ToolContext
- conversation.py
- browser.py
- test_ask.py
- test_questions.py
- EventBus
- eval_quality.py
- test_text.py
- ProviderUnavailable
- FakeProvider
- compilerOptions
- search.py
- Connectivity
- test_episodic.py
- snapshot
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- main.py
- compilerOptions
- FakeLocator
- ConversationMode
- test_browser.py
- questions.py
- test_vectors.py
- test_context.py
- test_browser_setup.py
- test_research.py
- test_affect.py
- Utterance
- StubSearch
- registry.py
- WebSearch
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- _cloud_model
- test_adoption.py
- ChatMessage
- discovery.py
- credentials.py
- FilesPanel.tsx
- ModelInfo
- Client
- files_rename
- parametrize
- _suppress_close_errors
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- ModelHealth
- free_model
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- context.py
- state.py
- PermissionEngine
- TranscriptionUnavailable
- FilesPanel.test.tsx
- Asked
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- _escalate_current_page
- spawn
- render
- gate_organize.py
- EpisodicMemory
- HistoryPanel.tsx
- CLAUDE.md — ARIA Project Instructions (Claude Code-facing)
- Router — local vs cloud, then which provider
- gate_affect.py
- configure_logging
- AffectState
- usePermissionMode.ts
- BrowserUnavailable
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- gate_research.py
- .prune
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
- HealthReport
- MemoryPanel.test.tsx
- Orb.tsx
- scripts
- core/router.py — model Router
- tools_trust_all_drives
- useAskQuestion.ts
- probes.py
- gate_agent.py
- LLMProvider
- MemoryPanel.tsx
- She holds a conversation now (2026-08-07)
- Measuring answer quality
- Smart mode: it was the tool, and then it was the router (2026-08-12)
- @types/ws
- is_casual
- App.tsx
- ModelPicker.test.tsx
- ToolCallCard.tsx
- VoiceAura.tsx
- ScreenRim.tsx
- Phase 8 — she has moods, and does not go quiet forever (2026-08-14)
- Phase 2 — Voice
- parametrize
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
- Any
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
- clear_adopted
- persona_for
- broker
- _Semantic
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
- _reset_connection
- PersonaLevel
- autoprefixer
- .cancel_all
- test_a_verdict_records_why_not_just_what
- datetime
- tokens.js
- .broadcast
- test_ordinary_questions_do_not_get_the_expensive_tier
- test_the_gate_is_the_same_probes_the_scripts_use
- useConversation.test.ts
- test_a_spoken_conversational_turn_still_stays_local
- grade
- test_read_is_named_as_an_untrusted_source
- eval/__init__.py

## God Nodes (most connected - your core abstractions)
1. `Database` - 262 edges
2. `ConversationStore` - 164 edges
3. `ConversationService` - 113 edges
4. `HealthTracker` - 106 edges
5. `ToolContext` - 97 edges
6. `SemanticMemory` - 92 edges
7. `ToolResult` - 86 edges
8. `ChatMessage` - 85 edges
9. `Router` - 63 edges
10. `EpisodicMemory` - 63 edges

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

## Communities (263 total, 68 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (107): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+99 more)

### Community 1 - "test_listener.py"
Cohesion: 0.06
Nodes (67): drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on… (+59 more)

### Community 2 - "main.ts"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 3 - "test_catalog.py"
Cohesion: 0.08
Nodes (36): default_local(), ModelAvailability, A catalog entry plus whether it can actually be used right now., The local fallback. Prefers the instruction-tuned 7B. `pulled` is what Ollama…, Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from., resolve_availability(), usable_ids() (+28 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.09
Nodes (45): _port_is_free(), Whether we can actually have the port, checked before anything else. **A second…, files_browse(), method_names(), One folder's contents, for the panel. Deliberately not `list_folder`: that tool…, _auth(), _call(), client() (+37 more)

### Community 5 - "ConversationService"
Cohesion: 0.04
Nodes (33): SessionSummary, ConversationService, ConversationMode, ModelInfo, RoutingBias, StoredMessage, Run steps until a text answer, loop detection, or the step budget ends it…, Which model gets to see the tool's result. `router._PRIVATE` already keeps a… (+25 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.07
Nodes (59): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no…, One attachment, understood. Never raises. (+51 more)

### Community 7 - "test_tts.py"
Cohesion: 0.04
Nodes (68): Any, ToolCall, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Phase 8 voice polish's affect-driven nudge to `KokoroTTS.synthesize`. Same…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, What the model is allowed to know exists. None rather than an empty list when… (+60 more)

### Community 8 - "Database"
Cohesion: 0.08
Nodes (55): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+47 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (42): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday., Sweeps idle sessions, and runs reflection once per day. (+34 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.06
Nodes (70): Unprompted messages (Phase 8). Off entirely when the switch is off — the same…, _start_proactivity_scheduler(), Candidate, default_candidates(), default_self_check(), idle_intention_candidate(), is_stated_intention(), ProactivityScheduler (+62 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.11
Nodes (29): parse_openai(), Chat models from a `GET /v1/models` body., gemini_ids(), _load(), openai_ids(), Any, fixture, parametrize (+21 more)

### Community 12 - "Event"
Cohesion: 0.06
Nodes (33): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+25 more)

### Community 13 - "apps.py"
Cohesion: 0.05
Nodes (69): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, A dead end is useless; naming the closest lets the model retry., browser" scored 0.88 against LockDown Browser and won. A category is not a…, test_category_words_are_recognised_before_they_are_matched(), test_ranking_offers_the_near_misses(), test_type_text_refuses_empty_text(), test_type_text_refuses_when_nothing_has_focus() (+61 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (67): _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The…, Make `find_files` deterministic and count how often it really walks., The reason the cache exists at all — two questions in a row must not walk three… (+59 more)

### Community 15 - "test_tools.py"
Cohesion: 0.03
Nodes (122): _focused(), MonkeyPatch, parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V… (+114 more)

### Community 16 - "Indexer"
Cohesion: 0.08
Nodes (35): chunk(), _digest(), Indexer, IndexStats, _pack(), Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, Whether this file is worth reading at all. (+27 more)

### Community 17 - "SileroVAD"
Cohesion: 0.06
Nodes (31): main(), Download the wake word weights into data/models/openwakeword. python…, frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python… (+23 more)

### Community 18 - "test_modes.py"
Cohesion: 0.06
Nodes (43): policy_for(), ConversationMode, The policy, or Normal's. Never raises. A mode arriving from a stale client is a…, A mode this turn would be better served by, or None. None is the answer for the…, suggest(), ConversationMode, parametrize, Modes as operating systems, not tones. Eyaas's own framing after using the… (+35 more)

### Community 19 - "ConversationStore"
Cohesion: 0.06
Nodes (44): The message store, for callers that need to resolve a session id., ConversationStore, _now(), CRUD over `sessions` and `messages`., Return an existing session id, or create one., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing… (+36 more)

### Community 20 - "OllamaEmbeddings"
Cohesion: 0.06
Nodes (41): Episode, BaseModel, Episodes — what happened, compressed and kept (BUILD_SPEC §7.3 tier 2). One…, A row from `episodes`, as the panel and retrieval see it., _age_days(), MemoryServices, _percentile(), datetime (+33 more)

### Community 21 - "HealthTracker"
Cohesion: 0.08
Nodes (34): HealthTracker, In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture, Observed latency and the circuit breaker. A 429 is treated as a routing input…, An unmeasured model must not win a latency ranking by default., A fresh process re-probes rather than assuming the worst., A stale seed must self-correct rather than misroute forever., A 429 is not transient the way a dropped connection is. (+26 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.06
Nodes (53): normalise_triple(), Fold a triple to its stored form. The UNIQUE index is on the raw columns, so…, Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection (+45 more)

### Community 23 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 24 - "soak_conversation.py"
Cohesion: 0.11
Nodes (17): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+9 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.07
Nodes (40): OllamaSupervisor, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was…, FakeOllama, Any, Path (+32 more)

### Community 26 - "test_router.py"
Cohesion: 0.10
Nodes (37): is_local(), RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort., Observed latency overrides the seeded table as turns land., The router must always answer. A turn with no candidates is a crash., Local models are multi-GB downloads that may not have finished. (+29 more)

### Community 27 - "extract.py"
Cohesion: 0.06
Nodes (58): _extract_bytes(), extract_or_raise(), extract_text(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work. (+50 more)

### Community 28 - "handlers.py"
Cohesion: 0.05
Nodes (81): build_health(), chat_cancel(), chat_delete(), chat_history(), chat_mode(), chat_new(), chat_rename(), chat_send() (+73 more)

### Community 29 - "test_conversation.py"
Cohesion: 0.07
Nodes (74): A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, _drain(), OpenEngine, parametrize, Path, ToolCall, Turn orchestration, cancellation, persistence and context roll-up. (+66 more)

### Community 30 - "RoutingLog"
Cohesion: 0.07
Nodes (33): ModelVerdict, BaseModel, What the router decided, and what the user made of it (§9.7). §9.7's closing…, Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Per-model tallies. The dataset §9.7 wants, as far as it has grown., One turn's routing decision, as it is written down. (+25 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (74): get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance… (+66 more)

### Community 32 - "Router"
Cohesion: 0.12
Nodes (22): Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, is_tool_shaped(), BaseModel, ModelInfo, StrEnum, A request to act on the machine rather than to talk about something., Chooses a model for a turn., Pick a model. `selected` is the user's choice — a model id, or "smart" to… (+14 more)

### Community 33 - "Fact"
Cohesion: 0.08
Nodes (18): Fact, _now(), Row, The form that gets embedded and shown in the prompt., A stored `fact_vec` row back into floats, or None if it has no vector., Merge one observation into the store, per §8.3. Order matters: 1. **Exact…, §8.3: exact triple → evidence_count += 1, confidence += 0.1 (cap 0.95)., Write the fact and its vector in one transaction. One transaction is not… (+10 more)

### Community 34 - "test_retrieval.py"
Cohesion: 0.09
Nodes (39): 1.0 today, 0.5 after a month, never quite zero., recency_decay(), anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A memory that keeps coming up is worth surfacing, but not enough to outrank…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice. (+31 more)

### Community 35 - "Tier"
Cohesion: 0.07
Nodes (37): EscalateFn, PreviewFn, RefuseFn, Bus, Denied, Journal, paths_in(), Pending (+29 more)

### Community 36 - "WakeMode"
Cohesion: 0.05
Nodes (28): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText (+20 more)

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
Cohesion: 0.10
Nodes (22): AdoptionService, AdoptionState, _probes_by_id(), Any, BaseModel, date, datetime, ModelInfo (+14 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "test_reflection.py"
Cohesion: 0.05
Nodes (58): build_prompt(), choose_model(), _extract_json(), Any, datetime, ModelInfo, Reflection — where "learns on its own" actually lives (BUILD_SPEC §8.3). Once a…, What one run did. Shown in MemoryPanel and asserted by the gate. (+50 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "ToolContext"
Cohesion: 0.05
Nodes (85): close_app(), focus_window(), list_windows(), tool, List open application windows., Bring an open window to the front. Args: name: Part of the window's title, e.g.…, Close an open window. Args: name: Part of the window's title, e.g. "notepad",…, tool (+77 more)

### Community 45 - "conversation.py"
Cohesion: 0.04
Nodes (53): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Mark one step as run. `local_only` is unknown, not False, for a tool the…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through… (+45 more)

### Community 46 - "browser.py"
Cohesion: 0.13
Nodes (26): Page, test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), browser_click(), browser_fill(), browser_navigate(), browser_read(), browser_screenshot() (+18 more)

### Community 47 - "test_ask.py"
Cohesion: 0.09
Nodes (31): a_question(), ask_tool(), `ask_user`: the registry entry, and the schema the model has to produce. The…, Pydantic hoists nested models into `$defs` and points at them with `$ref`.…, The first version only reached the top level. Pydantic emits a title per class…, The schema change is a capability, not a special case for this tool., `summary` is the only field the model sees., **`ok=False` would make her apologise for his silence.** Nothing went wrong; he… (+23 more)

### Community 48 - "test_questions.py"
Cohesion: 0.14
Nodes (24): Answer, QuestionBroker, What came back for one question., Puts a question on screen and waits for the answer., Resolve a waiting question. False if it already went., a_question(), FakeBus, The ask-and-wait broker: what it guarantees, and what it refuses to assume. The… (+16 more)

### Community 49 - "EventBus"
Cohesion: 0.12
Nodes (15): AssistantState, EventBus, Any, Protocol, StrEnum, Server -> client push notifications and the set of live connections (§7.1).…, Minimal transport surface — a Starlette WebSocket satisfies this., Tracks connected clients and broadcasts notifications to them. (+7 more)

### Community 50 - "eval_quality.py"
Cohesion: 0.07
Nodes (40): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+32 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "ProviderUnavailable"
Cohesion: 0.04
Nodes (58): HTTPError, ProviderRateLimited, ProviderUnavailable, The interface every LLM backend implements. Phase 1 only ships the Ollama…, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, Common `[{role, content}]` shape most chat APIs accept. Tool fields are only…, The backend could not be reached — offline, not running, DNS, refused. Distinct…, to_wire() (+50 more)

### Community 53 - "FakeProvider"
Cohesion: 0.07
Nodes (47): FakeProvider, make_service(), _proactivity_service(), anyio, Connection, fixture, MonkeyPatch, A proactive message needs somewhere to live even before the user has ever said… (+39 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "search.py"
Cohesion: 0.12
Nodes (11): AsyncClient, HTMLParser, Web search, and turning a page into something a model can read. BUILD_SPEC §9…, Readable text from a page, truncated on a word boundary., Strip a page to its readable text. Not readability, not an article extractor,…, _Reader, to_text(), The normal case on the open web, and returning nothing would read as "research… (+3 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "test_episodic.py"
Cohesion: 0.09
Nodes (41): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., _conversation(), _episodic(), anyio, Connection (+33 more)

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
Nodes (62): BaseSettings, FastAPI, get, _default_data_dir(), Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In… (+54 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "FakeLocator"
Cohesion: 0.09
Nodes (12): Locator, FakeLocator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, Refusing to act on an ambiguous-but-real description is worse than picking the…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught() (+4 more)

### Community 64 - "ConversationMode"
Cohesion: 0.13
Nodes (15): ConversationMode, _mode_block(), mode_done_when(), mode_label(), _persona(), How she should answer this conversation — the ChatGPT-style modes. **Per…, This mode's standard for a finished answer. Public because `core/modes.py`…, The mode's own paragraph, with its definition of done last. **Last on… (+7 more)

### Community 65 - "test_browser.py"
Cohesion: 0.14
Nodes (30): FakePage, MonkeyPatch, Browser control: the checkout/banking hard block, password refusal, and element…, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, Implements exactly the `Page` surface `browser.py` calls., _returning() (+22 more)

### Community 66 - "questions.py"
Cohesion: 0.17
Nodes (15): normalise(), Option, Pending, BaseModel, Question, Asking the user something and waiting for the answer. Eyaas: *"if u are gonna…, Trim to the caps and give every question its escape hatch. Done here rather…, Broadcast, then wait. Never raises for an ordinary outcome. (+7 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (23): cosine(), cosine_from_l2(), normalise(), pack(), Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for…, Cosine similarity of two vectors, normalised or not. Used by the merge step,… (+15 more)

### Community 68 - "test_context.py"
Cohesion: 0.07
Nodes (49): machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, volatile_prefix(), full(), Machine context: the clock, the model, and what it costs to carry them. (+41 more)

### Community 69 - "test_browser_setup.py"
Cohesion: 0.15
Nodes (20): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+12 more)

### Community 70 - "test_research.py"
Cohesion: 0.18
Nodes (15): One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, `research(query)`, the untrusted-content boundary, and the online gate. Two…, A model that has just read 6,000 characters of someone else's writing has…, Returns real, correct URLs" is the acceptance line, and only `summary` reaches…, Stronger than asking it not to use one: §7.2's own reasoning for hiding DANGER,…, test_a_source_is_truncated_rather_than_dropped() (+7 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "Utterance"
Cohesion: 0.10
Nodes (9): ndarray, Protocol, Voice activity detection — streaming Silero (BUILD_SPEC §9 Phase 2 stage 3).…, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance (+1 more)

### Community 73 - "StubSearch"
Cohesion: 0.10
Nodes (22): online(), Exception, fixture, MonkeyPatch, Stripping is a losing game — there are unlimited phrasings. The content is…, It has a title, a URL and a snippet. Citing it beats pretending the search did…, The whole point of `SearchUnavailable` carrying a message., A model that asks for fifty pages would blow the context budget §8.2 exists to… (+14 more)

### Community 74 - "registry.py"
Cohesion: 0.06
Nodes (35): It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, The tier says she may run it; this says the answer stays here. A clipboard…, It is a strong constraint — it overrides the router — so it should be…, SAFE, not CONFIRM. A dialog in front of "remember that I prefer short answers"…, Rule 5: destructive operations are T2+ with a confirmation round-trip., AUTO, as BUILD_SPEC:474 lists it. Reading her own memory is not an act on the…, The schema is what the model has to fill in blind. One string., The schema has to permit the relative form, or the description is a lie about… (+27 more)

### Community 75 - "WebSearch"
Cohesion: 0.18
Nodes (9): Any, Response, RuntimeError, Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix., Fetch and strip anything that arrived without text. Concurrently, and failures…, No usable search key, or the provider refused. Carries the fix., SearchUnavailable (+1 more)

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
Cohesion: 0.12
Nodes (48): by_class(), The router's pool: **measured only** — curated, or adopted after passing. The…, a_model(), Asker, Clock, perfect_reply(), ModelInfo, Measuring a free model, and the line it has to cross to be routed to.… (+40 more)

### Community 81 - "ChatMessage"
Cohesion: 0.07
Nodes (32): Compress the oldest turns. Folds in any earlier note so it compounds., Free-model measurement, and putting past adoptions back in the pool.…, _start_adoption(), ChatMessage, GenerationOptions, Any, BaseModel, Stream a completion. Cancellation is cooperative: cancelling the consuming task… (+24 more)

### Community 82 - "discovery.py"
Cohesion: 0.10
Nodes (31): discover_all(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch(), _gemini_class(), _gemini_is_chat(), _gemini_is_duplicate() (+23 more)

### Community 83 - "credentials.py"
Cohesion: 0.18
Nodes (14): all_status(), CredentialStatus, delete_key(), BaseModel, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Safe-to-display description of a stored key., Store a key. Callers must never log `value`., For Settings and `system.health`. Contains no secrets. (+6 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "ModelInfo"
Cohesion: 0.08
Nodes (38): adopt(), adopted(), all_models(), Cost, discovered(), get(), local_models(), ModelInfo (+30 more)

### Community 86 - "Client"
Cohesion: 0.29
Nodes (7): Client, main(), Any, Does she ask well, and — more importantly — does she stop asking? python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Send, answer anything she waits on, and return the completed turn. `pick` is…, section()

### Community 87 - "files_rename"
Cohesion: 0.20
Nodes (12): files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, Show it in Explorer. The escape hatch for anything this panel does not do., Rename in place, from a click in the panel. Reuses `tools/files.py`'s own…, **To the Recycle Bin, not gone.** This is the one place in the codebase that… (+4 more)

### Community 88 - "parametrize"
Cohesion: 0.18
Nodes (12): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., parametrize, The line that was missing. Without it these went to the FAST class., A false positive costs a spoken turn its ~800ms head start, which is the thing…, test_clipboard_questions_stay_on_this_machine(), test_code_requests_reach_a_reasoning_model(), test_conversation_is_not_mistaken_for_a_command() (+4 more)

### Community 89 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 90 - "Sidebar.tsx"
Cohesion: 0.13
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.25
Nodes (8): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, Phase 7 — a real, logged-in browser (CDP), Online mode — research(query) over search API, Tool.escalate/Tool.refuse hooks: checkout/banking pages force CONFIRM, password fields refused, _default_browser() detects the real default (Brave) via UserChoice registry rather than assuming Chrome, §11 untrusted_content boundary: fetched text is data, labelled and unfiltered, §11 force_confirm: next tool call after research/browser_read is force-escalated to T2

### Community 92 - "ModelHealth"
Cohesion: 0.18
Nodes (4): ModelHealth, BaseModel, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id.

### Community 93 - "free_model"
Cohesion: 0.17
Nodes (12): free_model(), health(), fixture, ModelInfo, A free OpenRouter model, adopted so the router can actually reach it.…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make…, Stage 1 already works this way for privacy, and this sits after it. Overriding… (+4 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): electron, electron-builder, devDependencies, electron, electron-builder, postcss, react, react-dom (+5 more)

### Community 96 - "context.py"
Cohesion: 0.06
Nodes (41): clean_title(), episode_request(), estimate_tokens(), fit_to_budget(), overhead_tokens(), datetime, StoredMessage, Prompt assembly and the rolling context window (BUILD_SPEC §8.2, §9 Phase 1).… (+33 more)

### Community 97 - "state.py"
Cohesion: 0.05
Nodes (33): ModelAvailability, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, AvailabilityService, ModelInfo, Which models are usable right now. One object answers this for both… (+25 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "TranscriptionUnavailable"
Cohesion: 0.22
Nodes (8): pcm16_to_float32(), ndarray, RuntimeError, Load and warm. First use downloads ~150MB, which must not happen while someone…, One utterance to text. Empty string when nothing was said., Speech input could not start. Never fatal — she still reads typing., Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., TranscriptionUnavailable

### Community 101 - "Asked"
Cohesion: 0.31
Nodes (9): Asked, The result of one `ask_user` call., The one-line-per-question summary that goes back to the model. **`summary` is…, render(), `summary` is the only field the model ever sees, so it has to carry the answers…, Otherwise the next step asks the same thing, which is how a question becomes a…, test_a_timeout_tells_her_to_carry_on_rather_than_ask_again(), test_the_chosen_answer_reaches_the_model() (+1 more)

### Community 102 - "ConfirmDialog.tsx"
Cohesion: 0.16
Nodes (10): ConfirmRequest, ImagePreview, leaf(), MovePlan, MovePlanView(), Props, tail(), TIER_LABEL (+2 more)

### Community 103 - "useConversation.ts"
Cohesion: 0.27
Nodes (12): appendToStreaming(), AttachmentStatus, clearStreaming(), finalise(), loadRatings(), ToolCall, toTurns(), Turn (+4 more)

### Community 104 - "package.json"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 105 - "_escalate_current_page"
Cohesion: 0.17
Nodes (13): The URL check catches the common case; a card-number field on an unlisted…, No page has loaded yet at this point — only the URL being navigated *to* is…, test_a_generic_domain_can_still_be_caught_by_its_dom(), test_known_checkout_and_banking_urls_are_recognised(), test_navigate_escalates_on_the_target_url_before_loading_it(), test_no_checkout_fields_means_no_dom_match(), _dom_confirms_checkout(), _escalate_current_page() (+5 more)

### Community 106 - "spawn"
Cohesion: 0.15
Nodes (10): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, Deliver a message with no preceding question. Called by…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, Any, Task, Fire-and-forget work that must not take the process down with it. Two rules,… (+2 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "EpisodicMemory"
Cohesion: 0.09
Nodes (15): EpisodicMemory, _now(), datetime, Row, StoredMessage, Writes and reads `episodes`. Never raises into the turn path., Summarize every conversation that has gone quiet. Returns how many., Summarize one session into an episode. Idempotent; never raises. `ended_at` is… (+7 more)

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
Cohesion: 0.21
Nodes (11): configure_logging(), _console_handler(), _file_handler(), Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file., Install the structlog + stdlib logging bridge. Idempotent. (+3 more)

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "BrowserUnavailable"
Cohesion: 0.17
Nodes (11): Browser, Exception, _raising(), `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, test_navigate_reports_browser_unavailable_plainly(), test_no_user_facing_browser_error_names_chrome(), BrowserUnavailable, _connect() (+3 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 121 - ".prune"
Cohesion: 0.40
Nodes (3): datetime, Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days.

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
Cohesion: 0.36
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

### Community 133 - "HealthReport"
Cohesion: 0.16
Nodes (20): dispatch(), HealthReport, _invoke(), BaseModel, Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., Rich health snapshot for the UI (§7.1 ``system.health``, §9.6)., err() (+12 more)

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

### Community 138 - "tools_trust_all_drives"
Cohesion: 0.50
Nodes (4): _enumerate_drives(), Every fixed drive letter Windows reports, as root paths ("C:\\").…, Trust every drive letter on the machine, in one call. The direct answer to…, tools_trust_all_drives()

### Community 139 - "useAskQuestion.ts"
Cohesion: 0.33
Nodes (5): AskedQuestion, GivenAnswer, PendingAsk, QuestionOption, useAskQuestion

### Community 141 - "probes.py"
Cohesion: 0.07
Nodes (44): Check, Answered something that has no answer, or claimed an action it cannot perform.…, admits_ignorance(), answers_flatly(), claimed_action(), contains(), contains_any(), denies_capability() (+36 more)

### Community 142 - "gate_agent.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 6's agent loop, against the running sidecar. "find <scratch file>,…

### Community 143 - "LLMProvider"
Cohesion: 0.09
Nodes (27): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+19 more)

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

### Community 158 - "parametrize"
Cohesion: 0.25
Nodes (9): parametrize, test_ordinary_targets_are_not_refused(), test_ordinary_urls_are_not_flagged(), test_password_shaped_targets_are_refused(), test_role_name_strips_the_leading_article_and_trailing_noun(), A hard block, not a dialog — see the module docstring. Reads only the call's…, the Send button" -> "Send" — a role lookup wants the label, not the description…, _refuse_password_field() (+1 more)

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

### Community 202 - "test_openrouter.py"
Cohesion: 0.06
Nodes (43): parse_openrouter(), Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, payload(), Any, fixture, OpenRouter: the provider, and the filters that decide what is even offered. The…, `openrouter/free` forwards to whichever free model it likes. Measuring it would…, An expired id 404s mid-turn, which reads as ARIA being broken. (+35 more)

### Community 209 - "clear_adopted"
Cohesion: 0.15
Nodes (14): clear_adopted(), Tests only. The overlay is process-global, like `_DISCOVERED`., _clean_overlay(), fixture, adopted(), discovered(), fixture, ModelInfo (+6 more)

### Community 210 - "persona_for"
Cohesion: 0.40
Nodes (5): persona_for(), Persona level for a model; unknown ids get the safe, minimal prompt., Nothing is known about how it behaves, so it gets the safe prompt., test_persona_for_a_discovered_model_is_minimal(), test_persona_for_unknown_model_is_the_safe_minimal_prompt()

### Community 211 - "broker"
Cohesion: 0.50
Nodes (4): broker(), fixture, MonkeyPatch, A stand-in for `runtime.questions`, recording what it was asked.

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.33
Nodes (4): DURATION, EASE, SPRING, TWEEN

### Community 241 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 244 - "PersonaLevel"
Cohesion: 0.11
Nodes (28): assemble(), PersonaLevel, StrEnum, Content identical across turns. Everything here is KV-cached. Changing `level`…, How much character a model can carry without falling apart. Measured on…, Build the final message list, stable content first., stable_prefix(), ConversationMode (+20 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 261 - "grade"
Cohesion: 0.33
Nodes (6): grade(), Why this reply fails, or an empty list. The same two-part judgement…, The fixture the whole file rests on, checked against the real probes. Without…, `universal_failures` applies here as it does in every other category. Running…, test_a_reply_that_leaks_the_prompt_fails_even_when_correct(), test_the_perfect_model_answers_every_probe()

## Knowledge Gaps
- **335 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+330 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **68 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `test_tts.py`, `Database`, `Event`, `LLMProvider`, `test_modes.py`, `ConversationStore`, `OllamaEmbeddings`, `HealthTracker`, `soak_conversation.py`, `test_conversation.py`, `RoutingLog`, `Router`, `Tier`, `WakeMode`, `listener.py`, `Listener`, `ToolContext`, `conversation.py`, `test_ask.py`, `EventBus`, `eval_quality.py`, `ProviderUnavailable`, `FakeProvider`, `main.py`, `ChatMessage`, `ModelInfo`, `state.py`, `spawn`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `ConversationService`, `test_tts.py`, `test_proactivity.py`, `LLMProvider`, `Indexer`, `ConversationStore`, `OllamaEmbeddings`, `SemanticMemory`, `soak_conversation.py`, `test_conversation.py`, `RoutingLog`, `Fact`, `test_retrieval.py`, `test_db.py`, `test_reflection.py`, `conversation.py`, `eval_quality.py`, `FakeProvider`, `test_episodic.py`, `main.py`, `test_affect.py`, `affect.py`, `state.py`, `EpisodicMemory`, `AffectState`, `_repeated_failures`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `ConversationService`, `test_tts.py`, `apps.py`, `finder.py`, `test_tools.py`, `test_screen.py`, `test_organize.py`, `Tier`, `conversation.py`, `browser.py`, `test_ask.py`, `FakeLocator`, `test_browser.py`, `questions.py`, `test_browser_setup.py`, `test_research.py`, `StubSearch`, `registry.py`, `_Semantic`, `_suppress_close_errors`, `BrowserUnavailable`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._