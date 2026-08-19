# Graph Report - ARIA  (2026-08-19)

## Corpus Check
- 243 files · ~352,748 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 5067 nodes · 11566 edges · 281 communities (214 shown, 67 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1021 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d5e17981`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- RecordingBus
- test_listener.py
- main.ts
- ModelInfo
- test_rpc.py
- test_reflection.py
- test_attachments.py
- Event
- test_procedures.py
- test_scheduler.py
- test_proactivity.py
- test_discovery.py
- KokoroTTS
- apps.py
- finder.py
- test_tools.py
- Indexer
- gate_wakeword.py
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
- method
- Database
- RoutingLog
- Tier
- Router
- semantic.py
- test_retrieval.py
- registry.py
- WakeMode
- listener.py
- Listener
- db.py
- AdoptionService
- test_focus.py
- EpisodicMemory
- ARIA — Project Instructions
- ToolContext
- ConversationService
- browser.py
- test_ask.py
- test_questions.py
- EventBus
- PersonaLevel
- test_text.py
- ChatMessage
- extract.py
- compilerOptions
- to_text
- Connectivity
- test_episodic.py
- snapshot
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- Settings
- compilerOptions
- FakeLocator
- context.py
- test_browser.py
- Option
- test_vectors.py
- test_context.py
- test_browser_setup.py
- Role
- test_affect.py
- Utterance
- test_research.py
- proactivity.py
- get_key
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- _cloud_model
- test_adoption.py
- _start_conversation
- discovery.py
- CredentialKey
- FilesPanel.tsx
- Runtime
- Client
- files_rename
- parametrize
- _suppress_close_errors
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- RpcMethodError
- free_model
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- overhead_tokens
- state.py
- PermissionEngine
- attachments.py
- FilesPanel.test.tsx
- Asked
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- _escalate_current_page
- spawn
- render
- gate_organize.py
- test_permissions.py
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
- Electron UI (renderer)
- Phase 2 stage 3 — hands free (wake word, VAD, endpointing)
- HealthReport
- MemoryPanel.test.tsx
- Orb.tsx
- scripts
- core/router.py — model Router
- files_browse
- useAskQuestion.ts
- probes.py
- gate_agent.py
- gate_tool_selection.py
- MemoryPanel.tsx
- She holds a conversation now (2026-08-07)
- Measuring answer quality
- Smart mode: it was the tool, and then it was the router (2026-08-12)
- main.py
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
- Path
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
- system.py
- Retriever
- broker
- handlers.py
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
- stable_prefix
- autoprefixer
- .cancel_all
- WakeWord
- OpenRouterProvider
- tokens.js
- .broadcast
- test_ordinary_questions_do_not_get_the_expensive_tier
- RecordingJournal
- useConversation.test.ts
- FakeSettings
- ask_tool
- rpc
- test_read_is_named_as_an_untrusted_source
- scheduled_check_in_candidate
- RateLimitState
- database
- eval/__init__.py
- ProactivityScheduler
- test_a_call_spanning_in_and_out_still_asks
- to_pcm16
- PermissionEngine
- missing_models
- ToolJournal
- pending_offers
- payload
- electron-builder
- test_a_spoken_turn_still_stays_local
- test_every_tool_probe_is_recognised_as_a_command
- test_a_spoken_command_is_no_longer_forced_onto_the_local_model
- test_a_command_is_not_slowed_down_for_a_difference_that_is_noise
- test_an_ordinary_question_still_takes_the_fast_class

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

## Communities (281 total, 67 thin omitted)

### Community 0 - "RecordingBus"
Cohesion: 0.09
Nodes (43): engine(), The property §9 Phase 3 names., `allow_danger` stays False on the engine itself — FULL_ACCESS grants the same…, §7.2: "if the agent wants to move 30 files, emit one confirm.request describing…, Detail on top of a confirmation. Losing the confirmation because the detail…, It describes what *would* happen. A preview computed after the fact would be…, The control. force_confirm is opt-in per call, never a default., The whole point: a tool that never asks, asking because the step before it read… (+35 more)

### Community 1 - "test_listener.py"
Cohesion: 0.06
Nodes (69): drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on… (+61 more)

### Community 2 - "main.ts"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 3 - "ModelInfo"
Cohesion: 0.03
Nodes (99): adopt(), adopted(), all_models(), clear_adopted(), Cost, default_local(), discovered(), get() (+91 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.12
Nodes (37): _auth(), _call(), client(), fixture, MonkeyPatch, Path, The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The id is reserved, not written — so the list stays empty. (+29 more)

### Community 5 - "test_reflection.py"
Cohesion: 0.09
Nodes (34): build_prompt(), _extract_json(), Any, §8.3's prompt, with the two slots filled., Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio, parametrize, The nightly §8.3 pass. Two things are load-bearing and both are about a local… (+26 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.09
Nodes (39): One attachment, understood. Never raises., The block that goes into the prompt. **Fenced as untrusted content**, exactly…, read_one(), render(), MonkeyPatch, Path, Files the user hands her. Eyaas: *"i should be also be able to file uploads…, There is no local vision model (rule 2), so no key is a real state with an… (+31 more)

### Community 7 - "Event"
Cohesion: 0.04
Nodes (67): Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Say a reply aloud, on request. False when there is no voice engine. The other…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., SpeechStream, RuntimeError, Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is… (+59 more)

### Community 8 - "test_procedures.py"
Cohesion: 0.09
Nodes (44): confirm(), context_hint(), detect(), DetectedSequence, discard(), Procedural learning — tier 4 of memory (BUILD_SPEC §9 Phase 8). `procedures`…, What the user said right before the first tool of a detected sequence, in the…, Detect, then insert exactly the sequences not already known. Returns the names… (+36 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.23
Nodes (24): is_stated_intention(), _candidate(), Connection, datetime, parametrize, The proactivity engine (BUILD_SPEC §9 Phase 8). `ProactivityScheduler.tick()`…, Stands in for `find_candidates`/`self_check`/`deliver`., Recorder (+16 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.10
Nodes (31): parse_openai(), Whether this id is a dated snapshot of something already in the list. Only when…, Chat models from a `GET /v1/models` body., _undated(), gemini_ids(), _load(), openai_ids(), Any (+23 more)

### Community 12 - "KokoroTTS"
Cohesion: 0.06
Nodes (36): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+28 more)

### Community 13 - "apps.py"
Cohesion: 0.04
Nodes (76): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, §7.2's second failure mode: the model gets one line, the UI gets the lot., A dead end is useless; naming the closest lets the model retry., browser" scored 0.88 against LockDown Browser and won. A category is not a…, test_category_words_are_recognised_before_they_are_matched(), test_listing_windows_summarises_rather_than_dumps(), test_ranking_offers_the_near_misses() (+68 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (63): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The… (+55 more)

### Community 15 - "test_tools.py"
Cohesion: 0.03
Nodes (119): _focused(), MonkeyPatch, parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V… (+111 more)

### Community 16 - "Indexer"
Cohesion: 0.08
Nodes (33): chunk(), _digest(), Indexer, IndexStats, _pack(), Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, Whether this file is worth reading at all. (+25 more)

### Community 17 - "gate_wakeword.py"
Cohesion: 0.09
Nodes (17): frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python…, say(), SilentBus (+9 more)

### Community 18 - "test_modes.py"
Cohesion: 0.06
Nodes (41): ConversationMode, A mode this turn would be better served by, or None. None is the answer for the…, suggest(), ConversationMode, parametrize, Modes as operating systems, not tones. Eyaas's own framing after using the…, Leans on rule 5's own invariant rather than a second hand-written list. Every…, **The property that decides whether this is usable.** §9's own warning is that… (+33 more)

### Community 19 - "ConversationStore"
Cohesion: 0.06
Nodes (44): The message store, for callers that need to resolve a session id., ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, When anything was last said, in any session. The whole precondition for §9's…, A fresh id with no row behind it yet. `ensure_session` creates a row for any id… (+36 more)

### Community 20 - "OllamaEmbeddings"
Cohesion: 0.06
Nodes (39): Episode, _now(), BaseModel, Row, Episodes — what happened, compressed and kept (BUILD_SPEC §7.3 tier 2). One…, A row from `episodes`, as the panel and retrieval see it., Nearest episodes to a vector, as (episode, cosine)., Mark episodes as recalled. Feeds the access_count term in scoring. Called off… (+31 more)

### Community 21 - "HealthTracker"
Cohesion: 0.07
Nodes (33): HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture (+25 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.07
Nodes (49): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:… (+41 more)

### Community 23 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 24 - "soak_conversation.py"
Cohesion: 0.21
Nodes (10): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+2 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.06
Nodes (45): find_ollama(), OllamaSupervisor, Path, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was…, The `ollama` executable, or None if it is not installed. PATH first, because… (+37 more)

### Community 26 - "test_router.py"
Cohesion: 0.10
Nodes (35): is_local(), RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort., Observed latency overrides the seeded table as turns land., The router must always answer. A turn with no candidates is a crash., Local models are multi-GB downloads that may not have finished. (+27 more)

### Community 27 - "test_extract.py"
Cohesion: 0.12
Nodes (32): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+24 more)

### Community 28 - "method"
Cohesion: 0.07
Nodes (41): chat_cancel(), chat_history(), chat_new(), chat_rename(), chat_send(), chat_sessions(), method(), models_adoption() (+33 more)

### Community 29 - "Database"
Cohesion: 0.05
Nodes (123): Database, Async-safe wrapper around the single sqlite connection., A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, chat_mode(), Read or set a conversation's mode. Omit `mode` to read. The read-or-write shape…, _drain(), FakeProvider (+115 more)

### Community 30 - "RoutingLog"
Cohesion: 0.07
Nodes (34): Deliver a message with no preceding question. Called by…, ModelVerdict, BaseModel, What the router decided, and what the user made of it (§9.7). §9.7's closing…, Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Per-model tallies. The dataset §9.7 wants, as far as it has grown. (+26 more)

### Community 31 - "Tier"
Cohesion: 0.06
Nodes (74): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+66 more)

### Community 32 - "Router"
Cohesion: 0.11
Nodes (22): Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, is_tool_shaped(), needs_deep_model(), BaseModel, ModelInfo, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, A request to act on the machine rather than to talk about something., Reasoning, code, or a multi-step request: the `smart` class earns its cost. (+14 more)

### Community 33 - "semantic.py"
Cohesion: 0.07
Nodes (24): Fact, FactHit, normalise_triple(), _now(), BaseModel, Row, Facts — what she has LEARNED about you (BUILD_SPEC §7.3 tier 3, §8.3). A fact…, The form that gets embedded and shown in the prompt. (+16 more)

### Community 34 - "test_retrieval.py"
Cohesion: 0.13
Nodes (30): anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice., `_build_context` runs once per attempt inside the failover loop, so without…, Below MIN_SCORE nothing is injected, so the prompt stays byte-identical to a…, The KV-cache invariant, asserted from the retrieval side too. (+22 more)

### Community 35 - "registry.py"
Cohesion: 0.04
Nodes (65): EscalateFn, PreviewFn, RefuseFn, It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, The tier says she may run it; this says the answer stays here. A clipboard…, It is a strong constraint — it overrides the router — so it should be…, SAFE, not CONFIRM. A dialog in front of "remember that I prefer short answers"…, Rule 5: destructive operations are T2+ with a confirmation round-trip. (+57 more)

### Community 36 - "WakeMode"
Cohesion: 0.08
Nodes (20): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout., build() (+12 more)

### Community 37 - "listener.py"
Cohesion: 0.07
Nodes (35): clips(), main(), ndarray, Can she hear her own name? Across many voices, because one is not a test.…, score(), is_stop_word(), _near_the_name(), Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3). The renderer opens the… (+27 more)

### Community 38 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 39 - "db.py"
Cohesion: 0.09
Nodes (33): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Run ``fn`` against the connection off the event loop, serialised. (+25 more)

### Community 40 - "AdoptionService"
Cohesion: 0.09
Nodes (29): Probe, Rules every reply obeys, regardless of what was asked., universal_failures(), AdoptionService, AdoptionState, grade(), _probes_by_id(), Any (+21 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "EpisodicMemory"
Cohesion: 0.05
Nodes (51): EpisodicMemory, datetime, StoredMessage, Writes and reads `episodes`. Never raises into the turn path., Summarize every conversation that has gone quiet. Returns how many., Summarize one session into an episode. Idempotent; never raises. `ended_at` is…, Stamp `ended_at` without writing an episode., Drop a session's episodes, so the session itself can be deleted.… (+43 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "ToolContext"
Cohesion: 0.05
Nodes (72): Launch, StrEnum, How an entry has to be started. Three sources, three launchers., tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, The clipboard's text, or None when it holds something else. An image, a file…, Replace the clipboard's contents. Public for the same reason as `read_text`… (+64 more)

### Community 45 - "ConversationService"
Cohesion: 0.02
Nodes (95): SessionSummary, call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Mark one step as run. `local_only` is unknown, not False, for a tool the…, Whether the model should be handed tools on the next pass. False exactly on… (+87 more)

### Community 46 - "browser.py"
Cohesion: 0.13
Nodes (26): Page, test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), browser_click(), browser_fill(), browser_navigate(), browser_read(), browser_screenshot() (+18 more)

### Community 47 - "test_ask.py"
Cohesion: 0.11
Nodes (26): Question, Asking the user something and waiting for the answer. Eyaas: *"if u are gonna…, The one-line-per-question summary that goes back to the model. **`summary` is…, One question, with the options that answer it., render(), a_question(), `ask_user`: the registry entry, and the schema the model has to produce. The…, The schema change is a capability, not a special case for this tool. (+18 more)

### Community 48 - "test_questions.py"
Cohesion: 0.14
Nodes (25): Answer, QuestionBroker, What came back for one question., Puts a question on screen and waits for the answer., Resolve a waiting question. False if it already went., a_question(), FakeBus, The ask-and-wait broker: what it guarantees, and what it refuses to assume. The… (+17 more)

### Community 49 - "EventBus"
Cohesion: 0.14
Nodes (9): EventBus, Any, Protocol, Minimal transport surface — a Starlette WebSocket satisfies this., Tracks connected clients and broadcasts notifications to them., Send the current state to one client, unconditionally. A reconnecting renderer…, Send a notification to every live client, dropping dead ones., Update the assistant state and notify clients if it actually changed. (+1 more)

### Community 50 - "PersonaLevel"
Cohesion: 0.09
Nodes (31): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+23 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "ChatMessage"
Cohesion: 0.04
Nodes (67): HTTPError, Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, split_for_rollup(), Compress the oldest turns. Folds in any earlier note so it compounds., ChatMessage, GenerationOptions, ProviderRateLimited, ProviderUnavailable (+59 more)

### Community 53 - "extract.py"
Cohesion: 0.11
Nodes (24): _extract_bytes(), extract_text(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as… (+16 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "to_text"
Cohesion: 0.12
Nodes (12): AsyncClient, HTMLParser, An epub is a zip of XHTML. Tags are stripped rather than parsed — the same call…, _read_epub(), Readable text from a page, truncated on a word boundary., Strip a page to its readable text. Not readability, not an article extractor,…, _Reader, to_text() (+4 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "test_episodic.py"
Cohesion: 0.10
Nodes (39): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., _conversation(), _episodic(), anyio, Connection (+31 more)

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
Cohesion: 0.11
Nodes (16): BaseSettings, _default_data_dir(), Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly., Where her database, models and logs live. **Beside the repo in development, in… (+8 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "FakeLocator"
Cohesion: 0.09
Nodes (12): Locator, FakeLocator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, Refusing to act on an ambiguous-but-real description is worse than picking the…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught() (+4 more)

### Community 64 - "context.py"
Cohesion: 0.07
Nodes (31): Do the six modes actually behave differently? Live, against a real sidecar.…, clean_title(), ConversationMode, episode_request(), _mode_block(), mode_done_when(), mode_label(), _persona() (+23 more)

### Community 65 - "test_browser.py"
Cohesion: 0.14
Nodes (30): FakePage, MonkeyPatch, Browser control: the checkout/banking hard block, password refusal, and element…, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, Implements exactly the `Page` surface `browser.py` calls., _returning() (+22 more)

### Community 66 - "Option"
Cohesion: 0.20
Nodes (11): normalise(), Option, BaseModel, Trim to the caps and give every question its escape hatch. Done here rather…, One answer the user can pick., **The guarantee that keeps a badly-framed question from being a trap.** A…, Otherwise there would be two, and one of them would do nothing., The model got the shape wrong; the question is still real. Refusing the whole… (+3 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "test_context.py"
Cohesion: 0.07
Nodes (51): assemble(), machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, Build the final message list, stable content first., volatile_prefix() (+43 more)

### Community 69 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+9 more)

### Community 70 - "Role"
Cohesion: 0.11
Nodes (18): MessageHit, _now(), BaseModel, Row, Sessions and messages — the durable conversation (BUILD_SPEC §7.3). This is…, Return an existing session id, or create one., Oldest-first turns for a session., Find past turns that mention what `query` is about. **This is the layer that… (+10 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "Utterance"
Cohesion: 0.10
Nodes (9): ndarray, Protocol, Voice activity detection — streaming Silero (BUILD_SPEC §9 Phase 2 stage 3).…, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance (+1 more)

### Community 73 - "test_research.py"
Cohesion: 0.08
Nodes (37): Fetch and strip anything that arrived without text. Concurrently, and failures…, One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, online(), Exception, fixture, MonkeyPatch (+29 more)

### Community 74 - "proactivity.py"
Cohesion: 0.13
Nodes (21): Candidate, default_candidates(), default_self_check(), idle_intention_candidate(), datetime, Path, timedelta, Unprompted messages — rate-limited, focus-aware, self-checked (BUILD_SPEC §9… (+13 more)

### Community 75 - "get_key"
Cohesion: 0.17
Nodes (13): get_key(), Read a key, or None if unset. Never logs the value., available(), Any, Response, RuntimeError, Web search, and turning a page into something a model can read. BUILD_SPEC §9…, Which search backend can run, or None. Never raises, never blocks. (+5 more)

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
Cohesion: 0.09
Nodes (57): ProviderQuotaExhausted, The **account's** allowance is gone, not this model's. A 429 usually means…, by_class(), The router's pool: **measured only** — curated, or adopted after passing. The…, a_model(), Asker, Clock, perfect_reply() (+49 more)

### Community 81 - "_start_conversation"
Cohesion: 0.09
Nodes (23): get, _build_listener(), _build_memory(), _discover_local_models(), health(), _probe_embeddings(), Any, RoutingBias (+15 more)

### Community 82 - "discovery.py"
Cohesion: 0.12
Nodes (27): discover_all(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch(), _gemini_class(), _gemini_is_chat(), _gemini_is_duplicate() (+19 more)

### Community 83 - "CredentialKey"
Cohesion: 0.17
Nodes (17): all_status(), CredentialKey, CredentialStatus, delete_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Credential Manager entry names under the ARIA service. (+9 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "Runtime"
Cohesion: 0.09
Nodes (12): ModelAvailability, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+4 more)

### Community 86 - "Client"
Cohesion: 0.29
Nodes (7): Client, main(), Any, Does she ask well, and — more importantly — does she stop asking? python…, One reader task, everything else off a queue. `asyncio.wait_for(ws.recv(),…, Send, answer anything she waits on, and return the completed turn. `pick` is…, section()

### Community 87 - "files_rename"
Cohesion: 0.22
Nodes (11): files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, Show it in Explorer. The escape hatch for anything this panel does not do., Rename in place, from a click in the panel. Reuses `tools/files.py`'s own…, **To the Recycle Bin, not gone.** This is the one place in the codebase that… (+3 more)

### Community 88 - "parametrize"
Cohesion: 0.17
Nodes (13): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., parametrize, The line that was missing. Without it these went to the FAST class., A false positive costs a spoken turn its ~800ms head start, which is the thing…, test_clipboard_questions_stay_on_this_machine(), test_code_requests_reach_a_reasoning_model(), test_conversation_is_not_mistaken_for_a_command() (+5 more)

### Community 89 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 90 - "Sidebar.tsx"
Cohesion: 0.13
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 92 - "RpcMethodError"
Cohesion: 0.09
Nodes (23): chat_delete(), confirm_respond(), memory_reflect(), models_bias(), permissions_mode(), proactivity_trigger(), question_answer(), Run the §8.3 pass now, rather than waiting for 3am. Synchronous, like… (+15 more)

### Community 93 - "free_model"
Cohesion: 0.17
Nodes (12): free_model(), health(), fixture, ModelInfo, A free OpenRouter model, adopted so the router can actually reach it.…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make…, Stage 1 already works this way for privacy, and this sits after it. Overriding… (+4 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): electron, devDependencies, electron, postcss, react, react-dom, @types/ws, zustand (+5 more)

### Community 96 - "overhead_tokens"
Cohesion: 0.10
Nodes (27): estimate_tokens(), fit_to_budget(), overhead_tokens(), Render remembered facts and episodes into one system message. Returns None when…, Tokens spent before the conversation even starts. Roll-up decisions must…, Drop oldest turns until the assembled prompt fits. Backstop, not policy.…, _render_memory(), retrieved_block() (+19 more)

### Community 97 - "state.py"
Cohesion: 0.11
Nodes (20): Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, Which models are usable right now. One object answers this for both…, Process-wide runtime handles. Not in BUILD_SPEC §5. Added because RPC handlers…, Connection, fixture, parametrize (+12 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "attachments.py"
Cohesion: 0.14
Nodes (20): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no…, Every attachment on one message, in the order they were given. Sequential… (+12 more)

### Community 101 - "Asked"
Cohesion: 0.29
Nodes (6): Asked, Pending, The result of one `ask_user` call., Broadcast, then wait. Never raises for an ordinary outcome., Otherwise the next step asks the same thing, which is how a question becomes a…, test_a_timeout_tells_her_to_carry_on_rather_than_ask_again()

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
Cohesion: 0.18
Nodes (9): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, Any, Task, Fire-and-forget work that must not take the process down with it. Two rules,…, Run `coro` detached. Failures are logged against `name`, never raised. (+1 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

### Community 109 - "test_permissions.py"
Cohesion: 0.11
Nodes (20): Collection, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, **Never default to approved on timeout** (§7.1). Somebody who walked away has…, `visit`'s checkout-page escalation would normally force a SAFE tool to CONFIRM.…, §7.2: "off by default" means the model is not told they exist, which is…, The half that was missing. `_tool_schemas` always asked for the CONFIRM…, `escalate` reaches the same CONFIRM floor `force_confirm` does — it must not be…, test_a_required_argument_is_marked_required() (+12 more)

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
Cohesion: 0.24
Nodes (8): Client, main(), Any, ConversationMode, Send, then wait for this turn's own completion., **One reader task, everything else off a queue.** The first version called…, report(), run_mode()

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

### Community 131 - "Electron UI (renderer)"
Cohesion: 0.29
Nodes (7): ARIA (local-first Windows AI assistant), Electron UI (renderer), Python sidecar (brain), Acrylic backgroundMaterial was covered by an opaque backgroundColor; fixed to #00000000, ConfirmDialog raw-argument fallback had no height cap; overflow hid Allow/Deny buttons, type_text SendInput struct-size bug: INPUT union undersized, all mocked tests passed anyway, Rule 1: all state lives in the Python sidecar

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

### Community 138 - "files_browse"
Cohesion: 0.33
Nodes (6): _enumerate_drives(), files_browse(), One folder's contents, for the panel. Deliberately not `list_folder`: that tool…, Every fixed drive letter Windows reports, as root paths ("C:\\").…, Trust every drive letter on the machine, in one call. The direct answer to…, tools_trust_all_drives()

### Community 139 - "useAskQuestion.ts"
Cohesion: 0.33
Nodes (5): AskedQuestion, GivenAnswer, PendingAsk, QuestionOption, useAskQuestion

### Community 141 - "probes.py"
Cohesion: 0.07
Nodes (44): Check, Answered something that has no answer, or claimed an action it cannot perform.…, admits_ignorance(), answers_flatly(), claimed_action(), contains(), contains_any(), denies_capability() (+36 more)

### Community 142 - "gate_agent.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 6's agent loop, against the running sidecar. "find <scratch file>,…

### Community 143 - "gate_tool_selection.py"
Cohesion: 0.22
Nodes (13): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+5 more)

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

### Community 149 - "main.py"
Cohesion: 0.16
Nodes (18): FastAPI, get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds…, Use the token Electron supplied, or mint one for standalone runs. (+10 more)

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

### Community 191 - "Path"
Cohesion: 0.12
Nodes (21): Path, Trusting a folder means trusting what is nested in it., `allow_danger` decides whether the tool exists; trust only decides whether it…, The choice made: trust covers deletion too., The engine you get with no mode set behaves exactly as it always has — every…, Switching to MANUAL and back must not have silently cleared what was configured…, The one thing mode never touches: `Tool.refuse`'s password-field block runs…, test_a_trusted_delete_runs_without_asking() (+13 more)

### Community 202 - "test_openrouter.py"
Cohesion: 0.07
Nodes (36): _openrouter_class(), parse_openrouter(), Prefer the number; fall back to what the vendor called it. The other two…, Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, OpenRouter: the provider, and the filters that decide what is even offered. The…, `openrouter/free` forwards to whichever free model it likes. Measuring it would…, An expired id 404s mid-turn, which reads as ARIA being broken., Fail towards keeping it: a bad date string is not evidence of anything. (+28 more)

### Community 209 - "system.py"
Cohesion: 0.16
Nodes (19): test_system_info_reports_this_machine(), _endpoint_volume(), _facts(), get_system_info(), kill_process(), Any, tool, Facts about the machine, and the one knob she can turn on it. `get_system_info`… (+11 more)

### Community 210 - "Retriever"
Cohesion: 0.16
Nodes (9): Task, Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache., Cancel any embed still running past its deadline. Without this, shutting down… (+1 more)

### Community 211 - "broker"
Cohesion: 0.50
Nodes (4): broker(), fixture, MonkeyPatch, A stand-in for `runtime.questions`, recording what it was asked.

### Community 212 - "handlers.py"
Cohesion: 0.16
Nodes (17): build_health(), memory_forget(), memory_list(), memory_search(), memory_stats(), memory_update(), JSON-RPC method registry and dispatch (BUILD_SPEC §7.1). Phase 0 registers only…, The memory services, or a message saying how to turn them on. (+9 more)

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.33
Nodes (4): DURATION, EASE, SPRING, TWEEN

### Community 241 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 244 - "stable_prefix"
Cohesion: 0.13
Nodes (21): measure_latency(), ModelInfo, TTFT over several turns, ignoring the first., Content identical across turns. Everything here is KV-cached. Changing `level`…, stable_prefix(), ConversationMode, parametrize, The property that makes modes free for anyone who never uses them. NORMAL… (+13 more)

### Community 247 - "WakeWord"
Cohesion: 0.12
Nodes (7): Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, ndarray, Protocol, What the listener depends on, so it never imports openwakeword., WakeWord

### Community 248 - "OpenRouterProvider"
Cohesion: 0.16
Nodes (10): _as_int(), OpenRouterProvider, Any, Headers, OpenAI's wire format, someone else's models. Subclassing rather than copying is…, Reachability, and a free chance to read the quota headers., OpenRouter's 429 says more than OpenAI's, and it is routine here. The free tier…, The raw catalogue OpenRouter offers today. Unauthenticated on purpose —… (+2 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 257 - "RecordingJournal"
Cohesion: 0.17
Nodes (13): Any, Rule 6, and the entry most worth having., Models get argument names wrong. That is a thing to say, not to crash on., An audit trail that cannot tell "you approved this" from "the folder was…, Same reasoning as trust's own audit-trail test: `approved_by` must say *why*…, RecordingJournal, test_a_denial_is_still_written_to_the_log(), test_a_failing_tool_is_reported_not_raised() (+5 more)

### Community 259 - "FakeSettings"
Cohesion: 0.17
Nodes (13): FakeSettings, Path, Empty by default is what keeps this one honest — on a machine that never opted…, I see you are working on X" after one keystroke is precisely the noise §9 warns…, The window is what makes this "right now" rather than "at some point". Without…, Someone renames or deletes a project. That must cost this trigger, not the tick…, It reuses the finder's own skip list rather than inventing a second one. A…, test_a_burst_of_changes_in_a_watched_folder_is_noticed() (+5 more)

### Community 260 - "ask_tool"
Cohesion: 0.15
Nodes (13): ask_tool(), **The first restriction overshot, and Eyaas caught it on screen.** Asked "can u…, Pydantic hoists nested models into `$defs` and points at them with `$ref`.…, The first version only reached the top level. Pydantic emits a title per class…, `registry.get` is `Tool | None`, and a missing tool here means the import in…, `Tier.AUTO`, because asking changes nothing on the machine. A confirmation…, **Most of whether this feature is liveable.** §9's warning about proactive…, test_asking_is_never_a_permission_question() (+5 more)

### Community 261 - "rpc"
Cohesion: 0.18
Nodes (12): bearer_from_header(), Constant-time comparison of a presented Bearer token., Extract the token from an ``Authorization: Bearer <token>`` header., token_matches(), Token-gated JSON-RPC endpoint (§7.1). The port is reachable by any browser tab…, Read/dispatch/reply until the client goes away., rpc(), _serve() (+4 more)

### Community 263 - "scheduled_check_in_candidate"
Cohesion: 0.24
Nodes (10): You have not been around in a while" — at most once, and only when that is…, scheduled_check_in_candidate(), FakeStore, A check-in at 3am is not a check-in, it is being woken up — and `affect`…, Nothing has ever been said, so there is no silence to notice. Being messaged…, _stamp(), test_a_brand_new_install_is_not_greeted_unprompted(), test_a_check_in_fires_after_a_long_quiet() (+2 more)

### Community 264 - "RateLimitState"
Cohesion: 0.17
Nodes (7): RateLimitState, Turn reasoning off where the endpoint allows it, and count the call. This is…, How much of the free daily allowance ARIA has spent, and it is a count. **The…, **Checked live on 2026-08-19, and the first version was wrong.** OpenRouter…, The header reader is kept because a 429 is documented to carry them. If a real…, test_a_stated_figure_beats_the_local_count(), test_the_free_allowance_is_counted_here_because_the_api_does_not_say()

### Community 265 - "database"
Cohesion: 0.29
Nodes (9): conn(), database(), db_path(), Connection, fixture, Path, Shared fixtures. Every test gets a throwaway data dir — never the real data/., A migrated database on a temp path. (+1 more)

### Community 267 - "ProactivityScheduler"
Cohesion: 0.33
Nodes (3): ProactivityScheduler, One pass. Never raises — a scheduler that dies stops everything, the same…, Sweeps for something worth saying, at most once per tick, and only when nothing…

### Community 268 - "test_a_call_spanning_in_and_out_still_asks"
Cohesion: 0.22
Nodes (9): fixture, Moving a file *out* of a trusted folder is not covered by trusting it — the…, Trust is about places. A tool that names none is not in one., A registry with one tool per tier, put back exactly as found. The snapshot…, test_a_call_spanning_in_and_out_still_asks(), test_a_tool_naming_no_path_is_never_trusted(), _tools(), clear() (+1 more)

### Community 269 - "to_pcm16"
Cohesion: 0.25
Nodes (7): ndarray, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, to_pcm16(), Wrapping turns a loud sample into a click at the opposite polarity., test_pcm16_clips_rather_than_wrapping(), test_pcm16_is_little_endian_and_half_the_size_of_float32()

### Community 270 - "PermissionEngine"
Cohesion: 0.25
Nodes (4): PermissionEngine, Decides whether a tool may run, and records that it was asked., Answer a pending confirmation. Returns whether one was waiting., Deny everything outstanding. Used when a turn is cancelled.

### Community 271 - "missing_models"
Cohesion: 0.33
Nodes (5): main(), Download the wake word weights into data/models/openwakeword. python…, missing_models(), Path, Which weights are absent, named so the log can say what to download.

### Community 272 - "ToolJournal"
Cohesion: 0.29
Nodes (4): Any, Where every tool call is recorded (BUILD_SPEC §7.3, CLAUDE.md rule 6). Append-…, Writes to `tool_log`. Satisfies `tools.permissions.Journal`., ToolJournal

### Community 273 - "pending_offers"
Cohesion: 0.33
Nodes (6): pending_offers(), Row, Detected, not yet confirmed or declined — what the proactivity engine has to…, procedure_offer_candidate(), The most concrete, lowest-noise-risk trigger, and checked first for that…, test_procedure_offer_fires_for_a_pending_offer()

### Community 274 - "payload"
Cohesion: 0.67
Nodes (3): payload(), Any, fixture

## Knowledge Gaps
- **335 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+330 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **67 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConversationService` connect `ConversationService` to `RecordingBus`, `RecordingJournal`, `ModelInfo`, `Event`, `PermissionEngine`, `test_modes.py`, `ConversationStore`, `HealthTracker`, `main.py`, `soak_conversation.py`, `Database`, `RoutingLog`, `Tier`, `Router`, `WakeMode`, `listener.py`, `Listener`, `EpisodicMemory`, `ToolContext`, `test_ask.py`, `EventBus`, `ChatMessage`, `Role`, `_start_conversation`, `Runtime`, `state.py`, `spawn`, `test_permissions.py`, `WakeWord`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `FakeSettings`, `test_reflection.py`, `Event`, `test_procedures.py`, `database`, `test_proactivity.py`, `ProactivityScheduler`, `scheduled_check_in_candidate`, `finder.py`, `Indexer`, `pending_offers`, `ToolJournal`, `ConversationStore`, `OllamaEmbeddings`, `main.py`, `SemanticMemory`, `soak_conversation.py`, `RoutingLog`, `semantic.py`, `test_retrieval.py`, `db.py`, `EpisodicMemory`, `ConversationService`, `test_episodic.py`, `Role`, `test_affect.py`, `proactivity.py`, `affect.py`, `Runtime`, `state.py`, `AffectState`, `_repeated_failures`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `RecordingBus`, `RecordingJournal`, `Event`, `apps.py`, `finder.py`, `test_tools.py`, `PermissionEngine`, `test_screen.py`, `Tier`, `registry.py`, `ConversationService`, `browser.py`, `test_ask.py`, `FakeLocator`, `test_browser.py`, `test_research.py`, `system.py`, `_suppress_close_errors`, `test_permissions.py`, `BrowserUnavailable`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 51 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._