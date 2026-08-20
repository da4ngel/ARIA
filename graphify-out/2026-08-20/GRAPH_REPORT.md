# Graph Report - ARIA  (2026-08-20)

## Corpus Check
- 247 files · ~356,449 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 5081 nodes · 11577 edges · 280 communities (212 shown, 68 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1021 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3ac3132d`
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
- Indexer
- OpenWakeWord
- test_modes.py
- ConversationStore
- OllamaEmbeddings
- HealthTracker
- SemanticMemory
- test_screen.py
- soak_conversation.py
- test_ollama_supervisor.py
- test_router.py
- test_extract.py
- handlers.py
- OpenEngine
- RoutingLog
- test_organize.py
- RouteDecision
- Fact
- test_retrieval.py
- Tier
- Reflector
- strip_wake_word
- Listener
- db.py
- AdoptionService
- test_focus.py
- test_episodic.py
- ARIA — Project Instructions
- ToolContext
- ConversationService
- ProviderUnavailable
- EpisodicMemory
- test_ask.py
- EventBus
- eval_quality.py
- test_text.py
- ChatMessage
- conversation.py
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
- Role
- SpeechStream
- test_tools.py
- test_vectors.py
- test_context.py
- test_browser_setup.py
- gate_tool_selection.py
- test_affect.py
- VoiceActivity
- test_research.py
- extract.py
- attachments.py
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- _cloud_model
- test_adoption.py
- proactivity.py
- discovery.py
- CredentialKey
- FilesPanel.tsx
- Sidecar
- Client
- ToolJournal
- Router
- _suppress_close_errors
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- browser.py
- free_model
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- state.py
- Runtime
- PermissionEngine
- FakeLocator
- FilesPanel.test.tsx
- HealthReport
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- test_browser.py
- spawn
- render
- gate_organize.py
- Settings
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
- FakeSettings
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
- BrowserUnavailable
- electron-vite
- framer-motion
- jsdom
- ProactivityScheduler
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
- _build_listener
- test_the_gate_is_the_same_probes_the_scripts_use
- parametrize
- adopted
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
- test_an_unrelated_reply_falls_through_to_a_normal_turn
- persona_for
- ProviderRegistry
- WakeWord
- base.py
- tokens.js
- rpc.ts
- ._resolve_procedure_reply
- is_trivial
- useConversation.test.ts
- pcm16_to_float32
- build_health
- tools_trust_all_drives
- Any
- autoprefixer
- _Semantic
- _reset_connection
- eval/__init__.py
- postcss
- react-dom
- rehype-highlight
- @types/ws
- ModelInfo
- _clean_overlay
- test_the_perfect_model_answers_every_probe
- electron-builder
- test_a_reply_that_leaks_the_prompt_fails_even_when_correct
- test_a_verdict_records_why_not_just_what
- test_read_is_named_as_an_untrusted_source

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

## Communities (280 total, 68 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (108): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+100 more)

### Community 1 - "test_listener.py"
Cohesion: 0.06
Nodes (69): drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on… (+61 more)

### Community 2 - "main.ts"
Cohesion: 0.15
Nodes (21): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+13 more)

### Community 3 - "test_catalog.py"
Cohesion: 0.08
Nodes (33): ModelAvailability, A catalog entry plus whether it can actually be used right now., Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from., resolve_availability(), usable_ids(), entry_for(), parametrize (+25 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.09
Nodes (45): _port_is_free(), Whether we can actually have the port, checked before anything else. **A second…, files_browse(), method_names(), One folder's contents, for the panel. Deliberately not `list_folder`: that tool…, _auth(), _call(), client() (+37 more)

### Community 5 - "test_reflection.py"
Cohesion: 0.08
Nodes (38): build_prompt(), _extract_json(), Any, §8.3's prompt, with the two slots filled., Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio, parametrize, The nightly §8.3 pass. Two things are load-bearing and both are about a local… (+30 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.09
Nodes (39): One attachment, understood. Never raises., The block that goes into the prompt. **Fenced as untrusted content**, exactly…, read_one(), render(), MonkeyPatch, Path, Files the user hands her. Eyaas: *"i should be also be able to file uploads…, There is no local vision model (rule 2), so no key is a real state with an… (+31 more)

### Community 7 - "test_tts.py"
Cohesion: 0.04
Nodes (66): ndarray, RuntimeError, Speech synthesis — kokoro-onnx on CPU (BUILD_SPEC §9 Phase 2). CPU only, per…, Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, Load and warm. The first synthesis is ~5x slower than the rest, and the user…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,… (+58 more)

### Community 8 - "Database"
Cohesion: 0.09
Nodes (50): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+42 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.17
Nodes (30): You have not been around in a while" — at most once, and only when that is…, scheduled_check_in_candidate(), _candidate(), FakeStore, Connection, datetime, The proactivity engine (BUILD_SPEC §9 Phase 8). `ProactivityScheduler.tick()`…, Stands in for `find_candidates`/`self_check`/`deliver`. (+22 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.11
Nodes (31): parse_gemini(), parse_openai(), Chat models from a `GET /v1/models` body., Chat models from a `GET /v1beta/models` body., gemini_ids(), _load(), openai_ids(), Any (+23 more)

### Community 12 - "KokoroTTS"
Cohesion: 0.04
Nodes (59): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+51 more)

### Community 13 - "ModelInfo"
Cohesion: 0.08
Nodes (36): adopt(), adopted(), all_models(), clear_adopted(), default_local(), discovered(), get(), local_models() (+28 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (67): _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The…, Make `find_files` deterministic and count how often it really walks., The reason the cache exists at all — two questions in a row must not walk three… (+59 more)

### Community 15 - "apps.py"
Cohesion: 0.05
Nodes (70): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, AppEntry, _AppIndex, _bring_to_front(), _build_index(), clear_type_targets(), close_app() (+62 more)

### Community 16 - "Indexer"
Cohesion: 0.09
Nodes (29): chunk(), _digest(), Indexer, Path, Whether this file is worth reading at all., Cheap identity: re-reading a 10MB PDF to decide whether to re-read it would…, Walks, reads, embeds and stores — slowly, and out of the way., Hold here while the machine is busy or she is answering. (+21 more)

### Community 17 - "OpenWakeWord"
Cohesion: 0.10
Nodes (10): NullConversation, OpenWakeWord, Any, ndarray, RuntimeError, Score one frame of int16 audio. Returns 0.0 while debounced. Callers must await…, Drop the rolling buffer. Called when capture stops, so audio from before a…, The wake word could not start. Never fatal — typing and push-to-talk both still… (+2 more)

### Community 18 - "test_modes.py"
Cohesion: 0.06
Nodes (45): policy_for(), ConversationMode, The policy, or Normal's. Never raises. A mode arriving from a stale client is a…, A mode this turn would be better served by, or None. None is the answer for the…, suggest(), ConversationMode, parametrize, Modes as operating systems, not tones. Eyaas's own framing after using the… (+37 more)

### Community 19 - "ConversationStore"
Cohesion: 0.07
Nodes (42): The message store, for callers that need to resolve a session id., ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, When anything was last said, in any session. The whole precondition for §9's…, A fresh id with no row behind it yet. `ensure_session` creates a row for any id… (+34 more)

### Community 20 - "OllamaEmbeddings"
Cohesion: 0.05
Nodes (46): Episode, BaseModel, Episodes — what happened, compressed and kept (BUILD_SPEC §7.3 tier 2). One…, A row from `episodes`, as the panel and retrieval see it., IndexStats, _pack(), The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, sqlite-vec takes raw little-endian float32. (+38 more)

### Community 21 - "HealthTracker"
Cohesion: 0.08
Nodes (29): HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture (+21 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.06
Nodes (56): normalise_triple(), datetime, Fold a triple to its stored form. The UNIQUE index is on the raw columns, so…, Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days., SemanticMemory (+48 more)

### Community 23 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 24 - "soak_conversation.py"
Cohesion: 0.22
Nodes (11): concrete_tokens(), main(), novel_tokens(), Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket., Recorder (+3 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.06
Nodes (46): find_ollama(), OllamaSupervisor, Path, Keep Ollama running, and notice when it comes back. Eyaas: *"sometimes when…, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was… (+38 more)

### Community 26 - "test_router.py"
Cohesion: 0.11
Nodes (33): is_local(), RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort., Observed latency overrides the seeded table as turns land., The router must always answer. A turn with no candidates is a crash., Local models are multi-GB downloads that may not have finished. (+25 more)

### Community 27 - "test_extract.py"
Cohesion: 0.12
Nodes (32): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+24 more)

### Community 28 - "handlers.py"
Cohesion: 0.05
Nodes (82): delete_key(), chat_cancel(), chat_delete(), chat_history(), chat_mode(), chat_new(), chat_rename(), chat_send() (+74 more)

### Community 29 - "OpenEngine"
Cohesion: 0.11
Nodes (41): A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, OpenEngine, ToolCall, §11 escalates the step after *reading* untrusted content. A `research` that was…, Decided with Eyaas (2026-08-18): §11 guards against untrusted content reaching…, The half that did not move, asserted beside the half that did — the narrowing…, Test with set of mcqs one after the other" is a real request, and a one-per-… (+33 more)

### Community 30 - "RoutingLog"
Cohesion: 0.07
Nodes (33): ModelVerdict, BaseModel, What the router decided, and what the user made of it (§9.7). §9.7's closing…, Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Per-model tallies. The dataset §9.7 wants, as far as it has grown., One turn's routing decision, as it is written down. (+25 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (71): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+63 more)

### Community 32 - "RouteDecision"
Cohesion: 0.12
Nodes (21): is_tool_shaped(), needs_deep_model(), BaseModel, ModelInfo, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, A request to act on the machine rather than to talk about something., Reasoning, code, or a multi-step request: the `smart` class earns its cost., Whether this endpoint may train on what is sent to it. Unknown ids read as… (+13 more)

### Community 33 - "Fact"
Cohesion: 0.07
Nodes (22): _now(), Return an existing session id, or create one., Fact, FactHit, _now(), BaseModel, Row, The form that gets embedded and shown in the prompt. (+14 more)

### Community 34 - "test_retrieval.py"
Cohesion: 0.09
Nodes (39): 1.0 today, 0.5 after a month, never quite zero., recency_decay(), anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A memory that keeps coming up is worth surfacing, but not enough to outrank…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice. (+31 more)

### Community 35 - "Tier"
Cohesion: 0.05
Nodes (54): EscalateFn, PreviewFn, RefuseFn, SAFE, not CONFIRM. A dialog in front of "remember that I prefer short answers"…, Rule 5: destructive operations are T2+ with a confirmation round-trip., AUTO, as BUILD_SPEC:474 lists it. Reading her own memory is not an act on the…, The schema is what the model has to fill in blind. One string., The schema has to permit the relative form, or the description is a lie about… (+46 more)

### Community 36 - "Reflector"
Cohesion: 0.09
Nodes (27): choose_model(), ExtractedEpisode, ExtractedFact, BaseModel, datetime, ModelInfo, Reflection — where "learns on its own" actually lives (BUILD_SPEC §8.3). Once a…, What the model returned, once it survives validation. (+19 more)

### Community 37 - "strip_wake_word"
Cohesion: 0.16
Nodes (14): is_stop_word(), Is this whole utterance just a request to stop talking?, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said., The name has to be first. Anywhere else it is just a word., Matched whole, never as a prefix. (+6 more)

### Community 38 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 39 - "db.py"
Cohesion: 0.07
Nodes (42): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Run ``fn`` against the connection off the event loop, serialised. (+34 more)

### Community 40 - "AdoptionService"
Cohesion: 0.11
Nodes (20): AdoptionService, AdoptionState, _probes_by_id(), Any, BaseModel, date, datetime, ModelInfo (+12 more)

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
Cohesion: 0.05
Nodes (85): test_system_info_reports_this_machine(), `ask_user` — put the choice on screen instead of describing it. The mechanism,…, tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, The clipboard's text, or None when it holds something else. An image, a file…, Replace the clipboard's contents. Public for the same reason as `read_text`…, Read the clipboard's text. (+77 more)

### Community 45 - "ConversationService"
Cohesion: 0.04
Nodes (32): SessionSummary, ConversationService, Any, ConversationMode, ModelInfo, RoutingBias, Which model gets to see the tool's result. `router._PRIVATE` already keeps a…, Evict the previous local model before loading a different one. CLAUDE.md rule… (+24 more)

### Community 46 - "ProviderUnavailable"
Cohesion: 0.09
Nodes (19): ProviderUnavailable, The backend could not be reached — offline, not running, DNS, refused. Distinct…, _assemble(), OpenAIProvider, Any, Headers, Response, ToolCall (+11 more)

### Community 47 - "EpisodicMemory"
Cohesion: 0.06
Nodes (23): _build_memory(), Facts, episodes and retrieval, as one handle for the conversation., EpisodicMemory, _now(), datetime, Row, StoredMessage, Writes and reads `episodes`. Never raises into the turn path. (+15 more)

### Community 48 - "test_ask.py"
Cohesion: 0.04
Nodes (88): Answer, Asked, normalise(), Option, Pending, BaseModel, Question, QuestionBroker (+80 more)

### Community 49 - "EventBus"
Cohesion: 0.14
Nodes (11): EventBus, Any, Protocol, Minimal transport surface — a Starlette WebSocket satisfies this., Tracks connected clients and broadcasts notifications to them., Send the current state to one client, unconditionally. A reconnecting renderer…, Send a notification to every live client, dropping dead ones., Update the assistant state and notify clients if it actually changed. (+3 more)

### Community 50 - "eval_quality.py"
Cohesion: 0.07
Nodes (42): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+34 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "ChatMessage"
Cohesion: 0.08
Nodes (26): Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, split_for_rollup(), Compress the oldest turns. Folds in any earlier note so it compounds., ChatMessage, GenerationOptions, Any, BaseModel, Stream a completion. Cancellation is cooperative: cancelling the consuming task… (+18 more)

### Community 53 - "conversation.py"
Cohesion: 0.09
Nodes (22): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Mark one step as run. `local_only` is unknown, not False, for a tool the…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through… (+14 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "Event"
Cohesion: 0.06
Nodes (29): SilentBus, Any, ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Endpoint (+21 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "FakeProvider"
Cohesion: 0.09
Nodes (36): FakeProvider, make_service(), fixture, MonkeyPatch, The whole point of writing a `routing_log` row for it: the *existing*…, The whole reason this is per-conversation rather than a setting: a mode chosen…, The Phase 1 gate: kill the window, conversation reloads from SQLite., A cloud model that dies mid-chain must never swap silently (§9.7 stage 7). (+28 more)

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
Nodes (49): FastAPI, get, bearer_from_header(), clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds…, Use the token Electron supplied, or mint one for standalone runs., Publish the token for a client that did not supply one. **Not written after the… (+41 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "test_conversation.py"
Cohesion: 0.08
Nodes (37): _drain(), _proactivity_service(), anyio, parametrize, Path, Turn orchestration, cancellation, persistence and context roll-up., A proactive message needs somewhere to live even before the user has ever said…, Wait for all in-flight turns. (+29 more)

### Community 64 - "Role"
Cohesion: 0.07
Nodes (35): clean_title(), ConversationMode, episode_request(), _mode_block(), mode_done_when(), mode_label(), _persona(), datetime (+27 more)

### Community 65 - "SpeechStream"
Cohesion: 0.10
Nodes (15): ToolCall, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Say a reply aloud, on request. False when there is no voice engine. The other…, Phase 8 voice polish's affect-driven nudge to `KokoroTTS.synthesize`. Same…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, SpeechStream (+7 more)

### Community 66 - "test_tools.py"
Cohesion: 0.02
Nodes (138): _focused(), MonkeyPatch, parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V… (+130 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (23): cosine(), cosine_from_l2(), normalise(), pack(), Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for…, Cosine similarity of two vectors, normalised or not. Used by the merge step,… (+15 more)

### Community 68 - "test_context.py"
Cohesion: 0.04
Nodes (95): assemble(), estimate_tokens(), fit_to_budget(), machine_context(), MachineContext, overhead_tokens(), PersonaLevel, Content identical across turns. Everything here is KV-cached. Changing `level`… (+87 more)

### Community 69 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+9 more)

### Community 70 - "gate_tool_selection.py"
Cohesion: 0.17
Nodes (16): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+8 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "VoiceActivity"
Cohesion: 0.15
Nodes (6): ndarray, Protocol, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., VoiceActivity

### Community 73 - "test_research.py"
Cohesion: 0.06
Nodes (46): An epub is a zip of XHTML. Tags are stripped rather than parsed — the same call…, _read_epub(), Web search, and turning a page into something a model can read. BUILD_SPEC §9…, Readable text from a page, truncated on a word boundary., Fetch and strip anything that arrived without text. Concurrently, and failures…, One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source (+38 more)

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
Cohesion: 0.13
Nodes (47): by_class(), The router's pool: **measured only** — curated, or adopted after passing. The…, a_model(), Asker, Clock, perfect_reply(), Measuring a free model, and the line it has to cross to be routed to.…, A scripted model, and a count of what it cost to ask it. (+39 more)

### Community 81 - "proactivity.py"
Cohesion: 0.11
Nodes (27): Candidate, default_candidates(), default_self_check(), idle_intention_candidate(), is_stated_intention(), procedure_offer_candidate(), datetime, Path (+19 more)

### Community 82 - "discovery.py"
Cohesion: 0.11
Nodes (26): Cost, ModelClass, ProviderName, StrEnum, What a model is *for*. The router picks a class, then a model in it., discover_all(), discover_gemini(), discover_openai() (+18 more)

### Community 83 - "CredentialKey"
Cohesion: 0.18
Nodes (15): Which models are usable right now. One object answers this for both…, all_status(), CredentialKey, CredentialStatus, get_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,… (+7 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "Sidecar"
Cohesion: 0.19
Nodes (3): HealthBody, Sidecar, SidecarOptions

### Community 86 - "Client"
Cohesion: 0.29
Nodes (7): Client, main(), Any, Does she ask well, and — more importantly — does she stop asking? python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Send, answer anything she waits on, and return the completed turn. `pick` is…, section()

### Community 87 - "ToolJournal"
Cohesion: 0.29
Nodes (4): Any, Where every tool call is recorded (BUILD_SPEC §7.3, CLAUDE.md rule 6). Append-…, Writes to `tool_log`. Satisfies `tools.permissions.Journal`., ToolJournal

### Community 88 - "Router"
Cohesion: 0.07
Nodes (27): Chooses a model for a turn., Router, parametrize, The line that was missing. Without it these went to the FAST class., Even in the latency-first bias. Fast and wrong is not the trade., The control. Widening the detector must not make everything SMART., §10 budgets ~1000ms end to end; a network hop does not fit in it., A false positive costs a spoken turn its ~800ms head start, which is the thing… (+19 more)

### Community 89 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 90 - "Sidebar.tsx"
Cohesion: 0.13
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 92 - "browser.py"
Cohesion: 0.13
Nodes (26): Page, test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), browser_click(), browser_fill(), browser_navigate(), browser_read(), browser_screenshot() (+18 more)

### Community 93 - "free_model"
Cohesion: 0.17
Nodes (12): free_model(), health(), fixture, ModelInfo, A free OpenRouter model, adopted so the router can actually reach it.…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make…, Stage 1 already works this way for privacy, and this sits after it. Overriding… (+4 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): electron, devDependencies, electron, react, react-markdown, tailwindcss, typescript, zustand (+5 more)

### Community 96 - "state.py"
Cohesion: 0.11
Nodes (19): Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, Process-wide runtime handles. Not in BUILD_SPEC §5. Added because RPC handlers…, Connection, fixture, parametrize, Durable settings and the v1 -> v2 migration. The migration matters more than… (+11 more)

### Community 97 - "Runtime"
Cohesion: 0.09
Nodes (12): ModelAvailability, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+4 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "FakeLocator"
Cohesion: 0.09
Nodes (12): Locator, FakeLocator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, Refusing to act on an ambiguous-but-real description is worse than picking the…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught() (+4 more)

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

### Community 105 - "test_browser.py"
Cohesion: 0.14
Nodes (30): FakePage, MonkeyPatch, Browser control: the checkout/banking hard block, password refusal, and element…, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, Implements exactly the `Page` surface `browser.py` calls., _returning() (+22 more)

### Community 106 - "spawn"
Cohesion: 0.15
Nodes (10): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, Deliver a message with no preceding question. Called by…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, Any, Task, Fire-and-forget work that must not take the process down with it. Two rules,… (+2 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "Settings"
Cohesion: 0.14
Nodes (11): BaseSettings, _default_data_dir(), Path, Sidecar configuration. Single source of truth for paths, port, and auth token.…, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly. (+3 more)

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

### Community 117 - "OllamaProvider"
Cohesion: 0.10
Nodes (14): HTTPError, OllamaProvider, Any, Response, ToolCall, Reachability only — does not check whether any model is loaded., Load `model` with a 1-token request so the user never hits cold start., Evict `model` from VRAM now, instead of after `keep_alive`. CLAUDE.md rule 2:… (+6 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 121 - "FakeSettings"
Cohesion: 0.17
Nodes (13): FakeSettings, Path, Empty by default is what keeps this one honest — on a machine that never opted…, I see you are working on X" after one keystroke is precisely the noise §9 warns…, The window is what makes this "right now" rather than "at some point". Without…, Someone renames or deletes a project. That must cost this trigger, not the tick…, It reuses the finder's own skip list rather than inventing a second one. A…, test_a_burst_of_changes_in_a_watched_folder_is_noticed() (+5 more)

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

### Community 191 - "BrowserUnavailable"
Cohesion: 0.17
Nodes (11): Browser, Exception, _raising(), `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, test_navigate_reports_browser_unavailable_plainly(), test_no_user_facing_browser_error_names_chrome(), BrowserUnavailable, _connect() (+3 more)

### Community 195 - "ProactivityScheduler"
Cohesion: 0.23
Nodes (5): Unprompted messages (Phase 8). Off entirely when the switch is off — the same…, _start_proactivity_scheduler(), ProactivityScheduler, One pass. Never raises — a scheduler that dies stops everything, the same…, Sweeps for something worth saying, at most once per tick, and only when nothing…

### Community 197 - "files_rename"
Cohesion: 0.20
Nodes (12): files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, Show it in Explorer. The escape hatch for anything this panel does not do., Rename in place, from a click in the panel. Reuses `tools/files.py`'s own…, **To the Recycle Bin, not gone.** This is the one place in the codebase that… (+4 more)

### Community 202 - "parse_openrouter"
Cohesion: 0.07
Nodes (33): _openrouter_benchmark(), _openrouter_expired(), _openrouter_is_free(), parse_openrouter(), Any, date, Free on **both** sides of the meter. `pricing.prompt == "0"` alone would admit…, Artificial Analysis' published intelligence index, if OpenRouter has one. A… (+25 more)

### Community 203 - "_Reader"
Cohesion: 0.20
Nodes (4): AsyncClient, HTMLParser, Strip a page to its readable text. Not readability, not an article extractor,…, _Reader

### Community 209 - "_build_listener"
Cohesion: 0.25
Nodes (7): main(), Download the wake word weights into data/models/openwakeword. python…, _build_listener(), Hands-free listening. Built eagerly rather than warmed in a task: the VAD loads…, missing_models(), Path, Which weights are absent, named so the log can say what to download.

### Community 211 - "parametrize"
Cohesion: 0.25
Nodes (9): parametrize, test_ordinary_targets_are_not_refused(), test_ordinary_urls_are_not_flagged(), test_password_shaped_targets_are_refused(), test_role_name_strips_the_leading_article_and_trailing_noun(), A hard block, not a dialog — see the module docstring. Reads only the call's…, the Send button" -> "Send" — a role lookup wants the label, not the description…, _refuse_password_field() (+1 more)

### Community 212 - "adopted"
Cohesion: 0.29
Nodes (8): adopted(), discovered(), fixture, ModelInfo, None means "send nothing and let the provider decide" — the only safe default,…, One discovered model, removed again afterwards. The overlay is module state, so…, A model this machine measured itself, and which passed. Built exactly the way…, test_temperature_defaults_to_none()

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.29
Nodes (5): DURATION, EASE, SPRING, stagger, TWEEN

### Community 244 - "test_an_unrelated_reply_falls_through_to_a_normal_turn"
Cohesion: 0.32
Nodes (7): Connection, A pending offer must never swallow an unrelated message as if it were a decline…, Only the very next `send()` after the offer can resolve it — a second "yes"…, _seed_procedure(), test_a_no_reply_discards_the_pending_offer(), test_an_unrelated_reply_falls_through_to_a_normal_turn(), test_the_pending_offer_window_is_one_shot()

### Community 245 - "persona_for"
Cohesion: 0.40
Nodes (5): persona_for(), Persona level for a model; unknown ids get the safe, minimal prompt., Nothing is known about how it behaves, so it gets the safe prompt., test_persona_for_a_discovered_model_is_minimal(), test_persona_for_unknown_model_is_the_safe_minimal_prompt()

### Community 246 - "ProviderRegistry"
Cohesion: 0.08
Nodes (27): ConversationHistory, ProviderRegistry, BaseModel, `chat.send` result (§7.1)., Providers keyed by name, so the service can follow the router's choice., `chat.history` result. Typed at the boundary per CLAUDE.md rule 7., TurnStarted, ModePolicy (+19 more)

### Community 247 - "WakeWord"
Cohesion: 0.13
Nodes (6): Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, Protocol, What the listener depends on, so it never imports openwakeword., WakeWord

### Community 248 - "base.py"
Cohesion: 0.05
Nodes (49): ProviderQuotaExhausted, ProviderRateLimited, The interface every LLM backend implements. Phase 1 only ships the Ollama…, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, The **account's** allowance is gone, not this model's. A 429 usually means…, Common `[{role, content}]` shape most chat APIs accept. Tool fields are only…, to_wire(), Replace what the providers said they offer. A curated id always wins: `gpt-5`… (+41 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 255 - "rpc.ts"
Cohesion: 0.29
Nodes (5): Pending, RpcEnvelope, RpcError, RpcErrorShape, RpcNotification

### Community 256 - "._resolve_procedure_reply"
Cohesion: 0.50
Nodes (3): _parse_yes_no(), True/False for a clearly affirmative/negative one-line reply, else None — an…, The other half of "offer once, wait for a yes" (Part 2). Returns a completed…

### Community 257 - "is_trivial"
Cohesion: 0.50
Nodes (4): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., test_is_trivial_accepts_greetings(), test_is_trivial_rejects_real_questions()

### Community 259 - "pcm16_to_float32"
Cohesion: 0.50
Nodes (4): pcm16_to_float32(), Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., One 80ms frame of base64 int16 PCM from the open microphone. Sent as a…, voice_frame()

### Community 260 - "build_health"
Cohesion: 0.50
Nodes (4): build_health(), Return the health snapshot. Never raises — the UI polls this., system_health(), uptime_seconds()

### Community 261 - "tools_trust_all_drives"
Cohesion: 0.50
Nodes (4): _enumerate_drives(), Every fixed drive letter Windows reports, as root paths ("C:\\").…, Trust every drive letter on the machine, in one call. The direct answer to…, tools_trust_all_drives()

### Community 265 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

## Knowledge Gaps
- **339 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+334 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **68 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConversationService` connect `ConversationService` to `._resolve_procedure_reply`, `test_permissions.py`, `test_tts.py`, `Database`, `KokoroTTS`, `ModelInfo`, `test_modes.py`, `ConversationStore`, `OllamaEmbeddings`, `HealthTracker`, `soak_conversation.py`, `OpenEngine`, `RoutingLog`, `RouteDecision`, `Tier`, `Listener`, `ToolContext`, `ProviderUnavailable`, `EpisodicMemory`, `test_ask.py`, `EventBus`, `eval_quality.py`, `ChatMessage`, `conversation.py`, `Event`, `FakeProvider`, `main.py`, `test_conversation.py`, `Role`, `SpeechStream`, `Router`, `state.py`, `Runtime`, `spawn`, `ProviderRegistry`, `WakeWord`, `base.py`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `test_reflection.py`, `test_tts.py`, `test_proactivity.py`, `Indexer`, `ConversationStore`, `OllamaEmbeddings`, `SemanticMemory`, `soak_conversation.py`, `OpenEngine`, `RoutingLog`, `Fact`, `test_retrieval.py`, `Reflector`, `db.py`, `test_episodic.py`, `ConversationService`, `EpisodicMemory`, `conversation.py`, `FakeProvider`, `main.py`, `test_conversation.py`, `Role`, `SpeechStream`, `ProactivityScheduler`, `test_affect.py`, `affect.py`, `proactivity.py`, `ToolJournal`, `state.py`, `Runtime`, `AffectState`, `test_an_unrelated_reply_falls_through_to_a_normal_turn`, `ProviderRegistry`, `FakeSettings`, `_repeated_failures`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `_Semantic`, `finder.py`, `apps.py`, `test_screen.py`, `test_organize.py`, `Tier`, `ConversationService`, `test_ask.py`, `conversation.py`, `BrowserUnavailable`, `SpeechStream`, `test_tools.py`, `test_research.py`, `_suppress_close_errors`, `browser.py`, `FakeLocator`, `test_browser.py`, `ProviderRegistry`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 51 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._