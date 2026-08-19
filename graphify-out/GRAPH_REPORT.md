# Graph Report - ARIA  (2026-08-19)

## Corpus Check
- 233 files · ~335,414 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4890 nodes · 11142 edges · 260 communities (194 shown, 66 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 983 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `42597eb1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_permissions.py
- test_listener.py
- main.ts
- catalog.py
- test_rpc.py
- ConversationService
- test_attachments.py
- test_tts.py
- Database
- test_scheduler.py
- test_proactivity.py
- discovery.py
- state.py
- AvailabilityService
- finder.py
- test_tools.py
- indexer.py
- Event
- RoutingBias
- ConversationStore
- retrieval.py
- HealthTracker
- SemanticMemory
- test_screen.py
- main.py
- test_ollama_supervisor.py
- test_router.py
- test_extract.py
- method
- OpenEngine
- RoutingLog
- test_organize.py
- RouteDecision
- Fact
- test_retrieval.py
- Tier
- WakeMode
- strip_wake_word
- Listener
- db.py
- AdoptionService
- test_focus.py
- Reflector
- ARIA — Project Instructions
- ToolContext
- conversation.py
- handlers.py
- extract.py
- LLMProvider
- Retriever
- GenerationOptions
- test_text.py
- ProviderUnavailable
- FakeProvider
- compilerOptions
- SpeechStream
- Connectivity
- test_episodic.py
- snapshot
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- _start_conversation
- compilerOptions
- RpcMethodError
- Settings
- test_browser.py
- Indexer
- test_vectors.py
- test_context.py
- test_browser_setup.py
- retrieved_block
- test_affect.py
- VoiceActivity
- StubSearch
- WebSearch
- CredentialKey
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- Router
- test_adoption.py
- get_key
- WakeWord
- credentials.py
- FilesPanel.tsx
- ModelInfo
- _require_memory
- files_rename
- OpenAIProvider
- _suppress_close_errors
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- Source
- test_research.py
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- context.py
- SettingsStore
- PermissionEngine
- OpenWakeWord
- FilesPanel.test.tsx
- rpc
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- test_reflection.py
- spawn
- render
- ModelListing
- EpisodicMemory
- HistoryPanel.tsx
- CLAUDE.md — ARIA Project Instructions (Claude Code-facing)
- Router — local vs cloud, then which provider
- gate_affect.py
- configure_logging
- AffectState
- usePermissionMode.ts
- _cloud_model
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- test_every_attachment_is_reported_to_the_renderer
- .prune
- SettingsPanel.tsx
- preload.ts
- gate_organize.py
- make_tray_icons.py
- PermissionModeChip.tsx
- _repeated_failures
- ToolsPanel.tsx
- Phase 8 — moods, procedural learning, proactivity, voice polish
- Electron UI (renderer)
- Phase 2 stage 3 — hands free (wake word, VAD, endpointing)
- protocol.py
- MemoryPanel.test.tsx
- Orb.tsx
- scripts
- core/router.py — model Router
- files_browse
- gate_research.py
- probes.py
- online
- gate_tool_selection.py
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
- gate_agent.py
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
- electron-builder
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
- free_model
- ChatMessage
- database
- _clean_overlay
- useConversationMode.ts
- motion.ts
- Any
- test_warmth_did_not_displace_the_capacity_to_disagree
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
- test_a_verdict_records_why_not_just_what
- test_the_warm_voice_carries_no_emoji_or_filler_opener
- test_she_is_pointed_at_type_text_for_a_native_app
- datetime
- tokens.js
- test_no_placeholder_survives_in_any_resolved_prompt
- test_archives_are_attachable_but_never_indexed
- test_the_gate_is_the_same_probes_the_scripts_use
- test_conversation.py
- eval/__init__.py

## God Nodes (most connected - your core abstractions)
1. `Database` - 260 edges
2. `ConversationStore` - 164 edges
3. `ConversationService` - 111 edges
4. `HealthTracker` - 106 edges
5. `ToolContext` - 94 edges
6. `SemanticMemory` - 92 edges
7. `ChatMessage` - 85 edges
8. `ToolResult` - 84 edges
9. `Router` - 63 edges
10. `EpisodicMemory` - 63 edges

## Surprising Connections (you probably didn't know these)
- `AGENTS.md — ARIA Project Instructions (Codex-facing)` --semantically_similar_to--> `CLAUDE.md — ARIA Project Instructions (Claude Code-facing)`  [INFERRED] [semantically similar]
  AGENTS.md → CLAUDE.md
- `Overlay page paints no background of its own` --semantically_similar_to--> `No CSP meta tag; main.ts sets the header per-environment`  [INFERRED] [semantically similar]
  overlay.html → index.html
- `Result` --uses--> `Expect`  [INFERRED]
  scripts/eval_quality.py → sidecar/eval/probes.py
- `Result` --uses--> `ChatMessage`  [INFERRED]
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

## Communities (260 total, 66 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (109): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+101 more)

### Community 1 - "test_listener.py"
Cohesion: 0.07
Nodes (57): drain(), frame(), interrupt(), ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on…, Under MIN_SPEECH_MS of speech is a door or a chair, not a question. (+49 more)

### Community 2 - "main.ts"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 3 - "catalog.py"
Cohesion: 0.04
Nodes (79): adopt(), all_models(), clear_adopted(), default_local(), get(), local_models(), ModelAvailability, persona_for() (+71 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.12
Nodes (37): _auth(), _call(), client(), fixture, MonkeyPatch, Path, The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The id is reserved, not written — so the list stays empty. (+29 more)

### Community 5 - "ConversationService"
Cohesion: 0.05
Nodes (34): SessionSummary, ConversationService, ConversationMode, ModelInfo, RoutingBias, StoredMessage, Which model gets to see the tool's result. `router._PRIVATE` already keeps a…, Record the decision for §9.7's labelled dataset. Off the turn path. Spawned… (+26 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.07
Nodes (59): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no…, One attachment, understood. Never raises. (+51 more)

### Community 7 - "test_tts.py"
Cohesion: 0.05
Nodes (57): ndarray, RuntimeError, Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, Voice could not start. Never fatal — she still types., shorten_for_speech() (+49 more)

### Community 8 - "Database"
Cohesion: 0.06
Nodes (66): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+58 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (42): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday., Sweeps idle sessions, and runs reflection once per day. (+34 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.06
Nodes (68): Candidate, default_candidates(), default_self_check(), idle_intention_candidate(), is_stated_intention(), ProactivityScheduler, procedure_offer_candidate(), datetime (+60 more)

### Community 11 - "discovery.py"
Cohesion: 0.06
Nodes (62): Cost, StrEnum, discover_all(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch(), _gemini_class() (+54 more)

### Community 12 - "state.py"
Cohesion: 0.05
Nodes (54): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+46 more)

### Community 13 - "AvailabilityService"
Cohesion: 0.10
Nodes (12): ModelAvailability, Idle sweeps always; the nightly §8.3 pass only if it is wanted., _start_memory_scheduler(), AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from. (+4 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (67): _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The…, Make `find_files` deterministic and count how often it really walks., The reason the cache exists at all — two questions in a row must not walk three… (+59 more)

### Community 15 - "test_tools.py"
Cohesion: 0.02
Nodes (170): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, _focused(), MonkeyPatch, parametrize, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and… (+162 more)

### Community 16 - "indexer.py"
Cohesion: 0.11
Nodes (26): chunk(), _pack(), The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, Whether this file is worth reading at all., sqlite-vec takes raw little-endian float32., Nearest chunks to `query`, as (path, text, distance)., Overlapping windows, so a sentence spanning a boundary stays findable., search_chunks() (+18 more)

### Community 17 - "Event"
Cohesion: 0.08
Nodes (25): frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python…, say(), SilentBus (+17 more)

### Community 18 - "RoutingBias"
Cohesion: 0.05
Nodes (53): policy_for(), ConversationMode, StrEnum, What a mode actually *does*, as opposed to what it says. Eyaas, after using the…, The policy, or Normal's. Never raises. A mode arriving from a stale client is a…, A mode this turn would be better served by, or None. None is the answer for the…, How much of the registry a mode lets the model see. **Narrowing, never…, The highest tier this policy will show, or None for no tools. (+45 more)

### Community 19 - "ConversationStore"
Cohesion: 0.05
Nodes (48): The message store, for callers that need to resolve a session id., ConversationStore, MessageHit, _now(), Sessions and messages — the durable conversation (BUILD_SPEC §7.3). This is…, CRUD over `sessions` and `messages`., Return an existing session id, or create one., Most recently started session, for reload-on-launch. (+40 more)

### Community 20 - "retrieval.py"
Cohesion: 0.14
Nodes (19): _age_days(), datetime, Retrieval — putting the right memory in front of the model (§9 Phase 5). **The…, 1.0 today, 0.5 after a month, never quite zero., §9 Phase 5: 0.6·cosine + 0.25·recency + 0.15·salience, boosted by access. Two…, Word overlap in place of cosine. Sub-millisecond, and honest about it. Not a…, Best `limit` above the floor. Below it, nothing goes in the prompt. **A zero…, recency_decay() (+11 more)

### Community 21 - "HealthTracker"
Cohesion: 0.08
Nodes (30): Which models are usable right now. One object answers this for both…, HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process… (+22 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.07
Nodes (49): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:… (+41 more)

### Community 23 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 24 - "main.py"
Cohesion: 0.13
Nodes (22): FastAPI, get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., bearer_from_header(), clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds… (+14 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.06
Nodes (46): find_ollama(), OllamaSupervisor, Path, Keep Ollama running, and notice when it comes back. Eyaas: *"sometimes when…, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was… (+38 more)

### Community 26 - "test_router.py"
Cohesion: 0.08
Nodes (46): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort. (+38 more)

### Community 27 - "test_extract.py"
Cohesion: 0.13
Nodes (30): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+22 more)

### Community 28 - "method"
Cohesion: 0.08
Nodes (34): chat_history(), chat_new(), chat_send(), chat_sessions(), confirm_respond(), memory_reflect(), method(), models_adoption() (+26 more)

### Community 29 - "OpenEngine"
Cohesion: 0.12
Nodes (37): A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, OpenEngine, ToolCall, §11 escalates the step after *reading* untrusted content. A `research` that was…, Decided with Eyaas (2026-08-18): §11 guards against untrusted content reaching…, The half that did not move, asserted beside the half that did — the narrowing…, Asks for a tool on the first pass, then answers on the second. The two-pass… (+29 more)

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
Nodes (22): Fact, normalise_triple(), _now(), Row, The form that gets embedded and shown in the prompt., Fold a triple to its stored form. The UNIQUE index is on the raw columns, so…, A stored `fact_vec` row back into floats, or None if it has no vector., Merge one observation into the store, per §8.3. Order matters: 1. **Exact… (+14 more)

### Community 34 - "test_retrieval.py"
Cohesion: 0.13
Nodes (30): anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice., `_build_context` runs once per attempt inside the failover loop, so without…, Below MIN_SCORE nothing is injected, so the prompt stays byte-identical to a…, The KV-cache invariant, asserted from the retrieval side too. (+22 more)

### Community 35 - "Tier"
Cohesion: 0.04
Nodes (67): EscalateFn, PreviewFn, RefuseFn, It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, The tier says she may run it; this says the answer stays here. A clipboard…, It is a strong constraint — it overrides the router — so it should be…, SAFE, not CONFIRM. A dialog in front of "remember that I prefer short answers"…, Rule 5: destructive operations are T2+ with a confirmation round-trip. (+59 more)

### Community 36 - "WakeMode"
Cohesion: 0.05
Nodes (35): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Endpoint, Voice activity detection — streaming Silero (BUILD_SPEC §9 Phase 2 stage 3).…, Accumulates frames and decides when the speaker has finished. Deliberately not… (+27 more)

### Community 37 - "strip_wake_word"
Cohesion: 0.16
Nodes (14): is_stop_word(), Is this whole utterance just a request to stop talking?, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said., The name has to be first. Anywhere else it is just a word., Matched whole, never as a prefix. (+6 more)

### Community 38 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 39 - "db.py"
Cohesion: 0.09
Nodes (33): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Run ``fn`` against the connection off the event loop, serialised. (+25 more)

### Community 40 - "AdoptionService"
Cohesion: 0.12
Nodes (16): AdoptionService, AdoptionState, BaseModel, date, ModelInfo, Everything the scheduler needs to resume, and nothing else., Works through free candidates, a few probes at a time, and decides. Injected…, Put previously adopted models back into the routing pool. Called at startup.… (+8 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "Reflector"
Cohesion: 0.07
Nodes (38): build_prompt(), choose_model(), ExtractedEpisode, ExtractedFact, BaseModel, datetime, ModelInfo, Reflection — where "learns on its own" actually lives (BUILD_SPEC §8.3). Once a… (+30 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "ToolContext"
Cohesion: 0.04
Nodes (107): Path, Overwriting is a different destructive act from moving, and the user approved a…, `read_file` did a plain UTF-8 read of whatever it was given, so "what does this…, A scanned PDF with no text layer is a normal thing to be handed. Saying so…, OneDrive relocates Documents and Desktop by default, so joining onto…, The whole point: when it cannot be done she must say so, not claim it., A folder is a much larger promise than a file, and this tool says file., test_a_missing_file_is_said_plainly() (+99 more)

### Community 45 - "conversation.py"
Cohesion: 0.10
Nodes (19): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through…, Told to the model, not just logged — it should know why it stopped. (+11 more)

### Community 46 - "handlers.py"
Cohesion: 0.15
Nodes (17): pcm16_to_float32(), Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., browser_setup(), build_health(), _cdp_reachable(), HealthReport, BaseModel, JSON-RPC method registry and dispatch (BUILD_SPEC §7.1). Phase 0 registers only… (+9 more)

### Community 47 - "extract.py"
Cohesion: 0.10
Nodes (26): _extract_bytes(), extract_text(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as… (+18 more)

### Community 48 - "LLMProvider"
Cohesion: 0.06
Nodes (30): ConversationHistory, ProviderRegistry, BaseModel, `chat.send` result (§7.1)., Providers keyed by name, so the service can follow the router's choice., `chat.history` result. Typed at the boundary per CLAUDE.md rule 7., TurnStarted, BaseModel (+22 more)

### Community 49 - "Retriever"
Cohesion: 0.11
Nodes (13): _percentile(), Task, What one turn recalled, plus what it cost., Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is… (+5 more)

### Community 50 - "GenerationOptions"
Cohesion: 0.06
Nodes (52): Namespace, _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.…, Declined or hedged a solid fact. The counter-metric — a hallucination fix that… (+44 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "ProviderUnavailable"
Cohesion: 0.10
Nodes (17): HTTPError, ProviderUnavailable, The backend could not be reached — offline, not running, DNS, refused. Distinct…, OllamaProvider, Any, Response, ToolCall, Reachability only — does not check whether any model is loaded. (+9 more)

### Community 53 - "FakeProvider"
Cohesion: 0.07
Nodes (43): chat_mode(), Read or set a conversation's mode. Omit `mode` to read. The read-or-write shape…, FakeProvider, make_service(), anyio, fixture, MonkeyPatch, The whole point of writing a `routing_log` row for it: the *existing*… (+35 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "SpeechStream"
Cohesion: 0.11
Nodes (13): Any, ToolCall, Evict the previous local model before loading a different one. CLAUDE.md rule…, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Phase 8 voice polish's affect-driven nudge to `KokoroTTS.synthesize`. Same…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`… (+5 more)

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

### Community 61 - "_start_conversation"
Cohesion: 0.09
Nodes (23): get, _build_indexer(), _build_stt(), _build_tts(), _discover_local_models(), health(), _probe_embeddings(), Any (+15 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "RpcMethodError"
Cohesion: 0.10
Nodes (21): chat_cancel(), chat_delete(), chat_rename(), models_select(), permissions_mode(), proactivity_trigger(), Run one sweep now, rather than waiting for the next five-minute tick. Same…, Abort an in-flight turn mid-stream. (+13 more)

### Community 64 - "Settings"
Cohesion: 0.13
Nodes (12): BaseSettings, _default_data_dir(), Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly., Where her database, models and logs live. **Beside the repo in development, in… (+4 more)

### Community 65 - "test_browser.py"
Cohesion: 0.04
Nodes (103): Browser, Locator, Page, FakeLocator, FakePage, Exception, MonkeyPatch, parametrize (+95 more)

### Community 66 - "Indexer"
Cohesion: 0.19
Nodes (9): _digest(), Indexer, IndexStats, Path, Cheap identity: re-reading a 10MB PDF to decide whether to re-read it would…, Walks, reads, embeds and stores — slowly, and out of the way., Hold here while the machine is busy or she is answering., One pass over everything, at the throttled rate. (+1 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "test_context.py"
Cohesion: 0.10
Nodes (38): machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, volatile_prefix(), full(), Machine context: the clock, the model, and what it costs to carry them. (+30 more)

### Community 69 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): _default_browser(), (exe path, profile dir) for the user's actual default browser., A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch, Path, `browser.setup`'s launcher detection. The bug this guards against was real, not…, Firefox is a real default browser some people have, and CDP does not work with… (+9 more)

### Community 70 - "retrieved_block"
Cohesion: 0.11
Nodes (21): estimate_tokens(), fit_to_budget(), Render remembered facts and episodes into one system message. Returns None when…, Drop oldest turns until the assembled prompt fits. Backstop, not policy.…, _render_memory(), retrieved_block(), A turn about something she has no memory of must leave the prompt byte-…, A fact is a standing truth; an episode is one conversation. (+13 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "VoiceActivity"
Cohesion: 0.15
Nodes (6): ndarray, Protocol, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., VoiceActivity

### Community 73 - "StubSearch"
Cohesion: 0.15
Nodes (15): Stripping is a losing game — there are unlimited phrasings. The content is…, It has a title, a URL and a snippet. Citing it beats pretending the search did…, The whole point of `SearchUnavailable` carrying a message., A model that asks for fifty pages would blow the context budget §8.2 exists to…, Stands in for the network. Returns whatever it was handed., StubSearch, test_a_source_that_would_not_load_is_still_cited(), test_an_empty_query_asks_rather_than_searching() (+7 more)

### Community 74 - "WebSearch"
Cohesion: 0.18
Nodes (9): Any, Response, RuntimeError, Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix., Fetch and strip anything that arrived without text. Concurrently, and failures…, No usable search key, or the provider refused. Carries the fix., SearchUnavailable (+1 more)

### Community 75 - "CredentialKey"
Cohesion: 0.13
Nodes (10): AsyncClient, HTMLParser, CredentialKey, StrEnum, Credential Manager entry names under the ARIA service., available(), Web search, and turning a page into something a model can read. BUILD_SPEC §9…, Which search backend can run, or None. Never raises, never blocks. (+2 more)

### Community 76 - "bridge.d.ts"
Cohesion: 0.10
Nodes (19): AriaApi, AssistantState, BrainStatus, CredentialStatus, LogLine, MemoryEpisode, MemoryFact, MemoryStats (+11 more)

### Community 77 - "Electron main + Python sidecar architecture"
Cohesion: 0.11
Nodes (19): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation (+11 more)

### Community 78 - "affect.py"
Cohesion: 0.17
Nodes (18): _clamp(), _drift(), _energy_delta(), _format_hour(), _hours_since_last_interaction(), datetime, Four floats that make the same question read differently at 2am than at 2pm…, Roughly `[-1, 1]` from the last few user messages. Zero — the common case —… (+10 more)

### Community 79 - "Router"
Cohesion: 0.07
Nodes (28): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+20 more)

### Community 80 - "test_adoption.py"
Cohesion: 0.12
Nodes (46): by_class(), The router's pool: **measured only** — curated, or adopted after passing. The…, a_model(), Asker, Clock, perfect_reply(), ModelInfo, Measuring a free model, and the line it has to cross to be routed to.… (+38 more)

### Community 81 - "get_key"
Cohesion: 0.14
Nodes (11): get_key(), Read a key, or None if unset. Never logs the value., _function_call_part(), GeminiProvider, Any, Response, ToolCall, Split system messages out; map assistant -> model. **Tool turns are not text.**… (+3 more)

### Community 82 - "WakeWord"
Cohesion: 0.12
Nodes (7): Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, ndarray, Protocol, What the listener depends on, so it never imports openwakeword., WakeWord

### Community 83 - "credentials.py"
Cohesion: 0.18
Nodes (14): all_status(), CredentialStatus, delete_key(), BaseModel, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Safe-to-display description of a stored key., Store a key. Callers must never log `value`., For Settings and `system.health`. Contains no secrets. (+6 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "ModelInfo"
Cohesion: 0.13
Nodes (14): grade(), _probes_by_id(), Any, datetime, Measuring a free model before Smart mode is allowed to use it. Eyaas asked for…, Why this reply fails, or an empty list. The same two-part judgement…, adopted(), discovered() (+6 more)

### Community 86 - "_require_memory"
Cohesion: 0.17
Nodes (12): memory_forget(), memory_list(), memory_search(), memory_stats(), memory_update(), §7.1: search what she remembers. The same path a turn uses., §7.1: delete one fact by id., Edit a fact, including pinning it. Pinning rides here rather than on its own… (+4 more)

### Community 87 - "files_rename"
Cohesion: 0.22
Nodes (11): files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, Show it in Explorer. The escape hatch for anything this panel does not do., Rename in place, from a click in the panel. Reuses `tools/files.py`'s own…, **To the Recycle Bin, not gone.** This is the one place in the codebase that… (+3 more)

### Community 88 - "OpenAIProvider"
Cohesion: 0.10
Nodes (15): _assemble(), OpenAIProvider, Any, Headers, Response, ToolCall, No-op: cloud models have no local load step to pay for., Per-request fields this vendor accepts and OpenAI does not. A hook rather than… (+7 more)

### Community 89 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 90 - "Sidebar.tsx"
Cohesion: 0.13
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 92 - "Source"
Cohesion: 0.17
Nodes (13): One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, Exception, A model that has just read 6,000 characters of someone else's writing has…, Returns real, correct URLs" is the acceptance line, and only `summary` reaches…, test_a_source_is_truncated_rather_than_dropped(), test_every_source_carries_its_url() (+5 more)

### Community 93 - "test_research.py"
Cohesion: 0.27
Nodes (9): Readable text from a page, truncated on a word boundary., to_text(), `research(query)`, the untrusted-content boundary, and the online gate. Two…, The normal case on the open web, and returning nothing would read as "research…, Stronger than asking it not to use one: §7.2's own reasoning for hiding DANGER,…, test_extraction_is_capped(), test_malformed_html_still_yields_something(), test_scripts_and_navigation_are_dropped() (+1 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): autoprefixer, electron, devDependencies, autoprefixer, electron, postcss, react, react-dom (+5 more)

### Community 96 - "context.py"
Cohesion: 0.11
Nodes (22): clean_title(), ConversationMode, episode_request(), _mode_block(), mode_done_when(), mode_label(), _persona(), datetime (+14 more)

### Community 97 - "SettingsStore"
Cohesion: 0.12
Nodes (18): Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, Connection, fixture, parametrize, Durable settings and the v1 -> v2 migration. The migration matters more than…, Values are JSON so a new setting never needs another migration. (+10 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "OpenWakeWord"
Cohesion: 0.10
Nodes (16): main(), Download the wake word weights into data/models/openwakeword. python…, _build_listener(), Hands-free listening. Built eagerly rather than warmed in a task: the VAD loads…, missing_models(), OpenWakeWord, Any, Path (+8 more)

### Community 101 - "rpc"
Cohesion: 0.29
Nodes (8): Constant-time comparison of a presented Bearer token., token_matches(), Token-gated JSON-RPC endpoint (§7.1). The port is reachable by any browser tab…, Read/dispatch/reply until the client goes away., rpc(), _serve(), test_token_comparison_rejects_empty(), websocket

### Community 102 - "ConfirmDialog.tsx"
Cohesion: 0.16
Nodes (10): ConfirmRequest, ImagePreview, leaf(), MovePlan, MovePlanView(), Props, tail(), TIER_LABEL (+2 more)

### Community 103 - "useConversation.ts"
Cohesion: 0.27
Nodes (12): appendToStreaming(), AttachmentStatus, clearStreaming(), finalise(), loadRatings(), ToolCall, toTurns(), Turn (+4 more)

### Community 104 - "package.json"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 105 - "test_reflection.py"
Cohesion: 0.11
Nodes (29): _extract_json(), Any, Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio, parametrize, The nightly §8.3 pass. Two things are load-bearing and both are about a local…, A key can be present while the account is dead, which is exactly this machine's…, The gate's fourth line, from the reflection side. (+21 more)

### Community 106 - "spawn"
Cohesion: 0.15
Nodes (10): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, Deliver a message with no preceding question. Called by…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, Any, Task, Fire-and-forget work that must not take the process down with it. Two rules,… (+2 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "ModelListing"
Cohesion: 0.29
Nodes (7): ModelListing, BaseModel, `models.list` result., models_list(), models_refresh(), Catalog plus live availability. Drives the picker and its tooltips. Re-probes…, Ask the cloud providers what they offer today, and re-list. Deliberately…

### Community 109 - "EpisodicMemory"
Cohesion: 0.05
Nodes (32): Episode, EpisodicMemory, _now(), BaseModel, datetime, Row, StoredMessage, Episodes — what happened, compressed and kept (BUILD_SPEC §7.3 tier 2). One… (+24 more)

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
Nodes (16): configure_logging(), _console_handler(), _file_handler(), Handler, Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file. (+8 more)

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "_cloud_model"
Cohesion: 0.22
Nodes (9): _cloud_model(), 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement…, The mechanism has to keep working, or banding would just be a way of ignoring…, test_a_measured_tool_score_outranks_latency_on_a_command(), test_a_model_that_is_visibly_worse_still_loses(), test_an_unmeasured_model_is_neither_promoted_nor_punished() (+1 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "test_every_attachment_is_reported_to_the_renderer"
Cohesion: 0.29
Nodes (7): Path, The divergent-state bug: reading is sequential and every image is a cloud round…, The actual bug. An unreadable file was recorded in a log line and nowhere a…, The guarantee the non-blocking move must not break., test_a_readable_attachment_still_reaches_the_first_pass(), test_every_attachment_is_reported_to_the_renderer(), test_send_returns_before_the_files_are_read()

### Community 121 - ".prune"
Cohesion: 0.40
Nodes (3): datetime, Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days.

### Community 122 - "SettingsPanel.tsx"
Cohesion: 0.25
Nodes (7): BrowserState, KEY_HELP, KEY_LABEL, OnlineState, RowProps, SEARCH_KEYS, SettingsPanel()

### Community 123 - "preload.ts"
Cohesion: 0.25
Nodes (6): api, AriaApi, BrainStatus, LogLine, SidecarEvent, Unsubscribe

### Community 124 - "gate_organize.py"
Cohesion: 0.43
Nodes (7): build_scratch(), main(), _ok(), Path, §9 Phase 4c's acceptance gate, against the running sidecar. organize_folder on…, Every file under `root`, by path relative to it, with its contents., snapshot()

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

### Community 133 - "protocol.py"
Cohesion: 0.19
Nodes (17): dispatch(), _invoke(), Parse and execute one client message. Returns None for notifications., Run a handler, mapping exceptions onto JSON-RPC errors., err(), ErrorCode, ok(), Any (+9 more)

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

### Community 139 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 141 - "probes.py"
Cohesion: 0.06
Nodes (47): Check, Answered something that has no answer, or claimed an action it cannot perform.…, admits_ignorance(), answers_flatly(), claimed_action(), contains(), contains_any(), denies_capability() (+39 more)

### Community 142 - "online"
Cohesion: 0.33
Nodes (6): online(), fixture, MonkeyPatch, Online mode on, with a stubbed search behind it., Belt to `_tool_schemas`' braces. `allow_danger_tools` was dead for a whole…, test_it_refuses_when_online_mode_is_off()

### Community 143 - "gate_tool_selection.py"
Cohesion: 0.17
Nodes (15): cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo, Should tool schemas be filtered by relevance before the model sees them? §7.2… (+7 more)

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

### Community 158 - "gate_agent.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), §9 Phase 6's agent loop, against the running sidecar. "find <scratch file>,…

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
Cohesion: 0.04
Nodes (58): Replace what the providers said they offer. A curated id always wins: `gpt-5`…, set_discovered(), parse_openrouter(), Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, _as_int(), OpenRouterProvider, Headers, RateLimitState (+50 more)

### Community 209 - "free_model"
Cohesion: 0.17
Nodes (12): free_model(), health(), fixture, ModelInfo, A free OpenRouter model, adopted so the router can actually reach it.…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make…, Stage 1 already works this way for privacy, and this sits after it. Overriding… (+4 more)

### Community 210 - "ChatMessage"
Cohesion: 0.14
Nodes (18): build_messages(), Exactly what the app would send: stable prefix first, then the turns.…, assemble(), StoredMessage, Drop rows the model should not see back (tool rows arrive in Phase 3)., Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, Build the final message list, stable content first., split_for_rollup() (+10 more)

### Community 211 - "database"
Cohesion: 0.29
Nodes (9): conn(), database(), db_path(), Connection, fixture, Path, Shared fixtures. Every test gets a throwaway data dir — never the real data/., A migrated database on a temp path. (+1 more)

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.33
Nodes (4): DURATION, EASE, SPRING, TWEEN

### Community 216 - "test_warmth_did_not_displace_the_capacity_to_disagree"
Cohesion: 0.33
Nodes (4): `recall` is a tool, so the instruction to search only makes sense when tools…, BUILD_SPEC §8.1's boundary, and the thing that keeps her from being a mirror:…, test_warmth_did_not_displace_the_capacity_to_disagree(), test_with_tools_she_is_told_to_look_before_denying()

### Community 241 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 244 - "PersonaLevel"
Cohesion: 0.13
Nodes (25): choose_with(), overhead_tokens(), PersonaLevel, Content identical across turns. Everything here is KV-cached. Changing `level`…, How much character a model can carry without falling apart. Measured on…, Tokens spent before the conversation even starts. Roll-up decisions must…, stable_prefix(), ConversationMode (+17 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 258 - "test_conversation.py"
Cohesion: 0.10
Nodes (28): _parse_yes_no(), True/False for a clearly affirmative/negative one-line reply, else None — an…, _drain(), _proactivity_service(), parametrize, Turn orchestration, cancellation, persistence and context roll-up., The control. Forcing every continuation local would throw away the cloud model…, A proactive message needs somewhere to live even before the user has ever said… (+20 more)

## Knowledge Gaps
- **329 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+324 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **66 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `test_conversation.py`, `test_tts.py`, `Database`, `state.py`, `Event`, `RoutingBias`, `ConversationStore`, `HealthTracker`, `main.py`, `OpenEngine`, `RoutingLog`, `RouteDecision`, `Tier`, `WakeMode`, `Listener`, `ToolContext`, `conversation.py`, `LLMProvider`, `Retriever`, `GenerationOptions`, `ProviderUnavailable`, `FakeProvider`, `SpeechStream`, `_start_conversation`, `Router`, `ChatMessage`, `WakeWord`, `ModelInfo`, `spawn`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `test_browser.py`, `Tier`, `ConversationService`, `test_browser_setup.py`, `StubSearch`, `conversation.py`, `finder.py`, `test_tools.py`, `LLMProvider`, `test_screen.py`, `SpeechStream`, `_suppress_close_errors`, `Source`, `test_research.py`, `test_organize.py`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `test_conversation.py`, `ConversationService`, `test_tts.py`, `test_proactivity.py`, `state.py`, `indexer.py`, `ConversationStore`, `SemanticMemory`, `main.py`, `OpenEngine`, `RoutingLog`, `Fact`, `test_retrieval.py`, `db.py`, `Reflector`, `conversation.py`, `LLMProvider`, `FakeProvider`, `SpeechStream`, `test_episodic.py`, `Indexer`, `test_affect.py`, `affect.py`, `Router`, `database`, `SettingsStore`, `test_reflection.py`, `EpisodicMemory`, `AffectState`, `test_every_attachment_is_reported_to_the_renderer`, `_repeated_failures`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._