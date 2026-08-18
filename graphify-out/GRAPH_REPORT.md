# Graph Report - ARIA  (2026-08-18)

## Corpus Check
- 213 files · ~291,353 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4421 nodes · 10093 edges · 241 communities (177 shown, 64 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 915 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `78c1ab61`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- RecordingBus
- test_listener.py
- main.ts
- catalog.py
- test_rpc.py
- ConversationService
- read_one
- test_tts.py
- Database
- test_scheduler.py
- test_proactivity.py
- discovery.py
- KokoroTTS
- AvailabilityService
- finder.py
- test_tools.py
- Indexer
- gate_wakeword.py
- Event
- ConversationStore
- ModelInfo
- HealthTracker
- SemanticMemory
- test_screen.py
- Settings
- test_ollama_supervisor.py
- test_router.py
- eval_quality.py
- handlers.py
- OpenAIProvider
- state.py
- test_organize.py
- Router
- Fact
- test_retrieval.py
- Tier
- main.py
- listener.py
- Listener
- test_db.py
- test_conversation.py
- test_focus.py
- test_reflection.py
- ARIA — Project Instructions
- ToolContext
- measure_models.py
- apps.py
- Reflector
- conversation.py
- Retriever
- probes.py
- test_text.py
- ChatMessage
- parametrize
- compilerOptions
- memory.py
- Connectivity
- test_permissions.py
- MachineContext
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- rpc
- compilerOptions
- EventBus
- overhead_tokens
- test_browser.py
- Path
- test_vectors.py
- WakeWord
- RecordingJournal
- test_context.py
- test_affect.py
- Utterance
- StubSearch
- WebSearch
- _Reader
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- soak_conversation.py
- GeminiProvider
- test_research.py
- test_a_call_spanning_in_and_out_still_asks
- CredentialKey
- FilesPanel.tsx
- Source
- _reset_connection
- fit_to_budget
- OllamaProvider
- _suppress_close_errors
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- online
- datetime
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- context.py
- SettingsStore
- PermissionEngine
- PermissionEngine
- FilesPanel.test.tsx
- ModelListing
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- call_key
- ToolJournal
- render
- snapshot
- _port_is_free
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
- PersonaLevel
- _vector
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
- HealthReport
- MemoryPanel.test.tsx
- Orb.tsx
- scripts
- core/router.py — model Router
- spawn
- gate_research.py
- .forget
- test_a_short_code_request_is_not_answered_locally_to_save_time
- test_ordinary_questions_do_not_get_the_expensive_tier
- MemoryPanel.tsx
- She holds a conversation now (2026-08-07)
- Measuring answer quality
- Smart mode: it was the tool, and then it was the router (2026-08-12)
- test_a_spoken_turn_still_stays_local
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
- test_every_tool_probe_is_recognised_as_a_command
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
- @types/ws
- typescript
- vite
- @vitejs/plugin-react
- vitest
- sidecar/__init__.py
- persona/__init__.py
- test_a_spoken_command_is_no_longer_forced_onto_the_local_model
- test_a_spoken_conversational_turn_still_stays_local
- test_a_command_is_not_slowed_down_for_a_difference_that_is_noise
- test_an_ordinary_question_still_takes_the_fast_class
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

## God Nodes (most connected - your core abstractions)
1. `Database` - 253 edges
2. `ConversationStore` - 159 edges
3. `HealthTracker` - 106 edges
4. `ConversationService` - 102 edges
5. `ToolContext` - 94 edges
6. `SemanticMemory` - 92 edges
7. `ToolResult` - 84 edges
8. `ChatMessage` - 81 edges
9. `EpisodicMemory` - 63 edges
10. `RecordingBus` - 63 edges

## Surprising Connections (you probably didn't know these)
- `Tool Call Log: "write me an essay on space in notepad"` --references--> `open_app()`  [INFERRED]
  image.png → sidecar/tools/apps.py
- `AGENTS.md — ARIA Project Instructions (Codex-facing)` --semantically_similar_to--> `CLAUDE.md — ARIA Project Instructions (Claude Code-facing)`  [INFERRED] [semantically similar]
  AGENTS.md → CLAUDE.md
- `Tool Call Log: "write me an essay on space in notepad"` --references--> `open_path()`  [INFERRED]
  image.png → sidecar/tools/files.py
- `Tool Call Log: "write me an essay on space in notepad"` --references--> `write_file()`  [INFERRED]
  image.png → sidecar/tools/files.py
- `Overlay page paints no background of its own` --semantically_similar_to--> `No CSP meta tag; main.ts sets the header per-environment`  [INFERRED] [semantically similar]
  overlay.html → index.html

## Import Cycles
- 3-file cycle: `sidecar/core/conversation.py -> sidecar/state.py -> sidecar/core/listener.py -> sidecar/core/conversation.py`

## Hyperedges (group relationships)
- **ARIA's layered safety/confirmation system** — permission_engine, rule_destructive_confirmation, rationale_untrusted_source_escalation, rationale_checkout_escalation, rationale_confirm_timeout_denied [INFERRED 0.85]
- **Memory repair: six-cause conversation-forgetting investigation and fix** — bug_she_forgot_conversation, rationale_memory_high_water_mark, rationale_salience_computed_not_asked, memory_system, phase_5_memory [EXTRACTED 1.00]
- **Phase 6 agent loop design: step-aware routing, privacy stickiness, escalation** — agent_loop, rationale_sticky_local, rationale_untrusted_source_escalation, phase_6_agent_loop, router_core [EXTRACTED 1.00]
- **KV-cache latency discipline across prompt assembly** — build_spec_stable_prefix_ordering, build_spec_prefill_cost [INFERRED 0.85]

## Communities (241 total, 64 thin omitted)

### Community 0 - "RecordingBus"
Cohesion: 0.09
Nodes (43): engine(), The property §9 Phase 3 names., `allow_danger` stays False on the engine itself — FULL_ACCESS grants the same…, §7.2: "if the agent wants to move 30 files, emit one confirm.request describing…, Detail on top of a confirmation. Losing the confirmation because the detail…, It describes what *would* happen. A preview computed after the fact would be…, The control. force_confirm is opt-in per call, never a default., The whole point: a tool that never asks, asking because the step before it read… (+35 more)

### Community 1 - "test_listener.py"
Cohesion: 0.06
Nodes (69): drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on… (+61 more)

### Community 2 - "main.ts"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 3 - "catalog.py"
Cohesion: 0.05
Nodes (62): Which models are usable right now. One object answers this for both…, all_models(), by_class(), default_local(), local_models(), ModelAvailability, persona_for(), ProviderName (+54 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.12
Nodes (37): _auth(), _call(), client(), fixture, MonkeyPatch, Path, The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The id is reserved, not written — so the list stays empty. (+29 more)

### Community 5 - "ConversationService"
Cohesion: 0.04
Nodes (42): SessionSummary, ConversationService, _parse_yes_no(), Any, datetime, ModelInfo, RoutingBias, StoredMessage (+34 more)

### Community 6 - "read_one"
Cohesion: 0.09
Nodes (45): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, Images need a model, and there is no local one (rule 2). So an image with no…, One attachment, understood. Never raises., Every attachment on one message, in the order they were given. Sequential…, The block that goes into the prompt. **Fenced as untrusted content**, exactly… (+37 more)

### Community 7 - "test_tts.py"
Cohesion: 0.06
Nodes (49): ToolCall, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, SpeechStream, Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is… (+41 more)

### Community 8 - "Database"
Cohesion: 0.09
Nodes (50): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+42 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.06
Nodes (73): Unprompted messages (Phase 8). Off entirely when the switch is off — the same…, _start_proactivity_scheduler(), Candidate, default_candidates(), idle_intention_candidate(), is_stated_intention(), ProactivityScheduler, procedure_offer_candidate() (+65 more)

### Community 11 - "discovery.py"
Cohesion: 0.07
Nodes (51): Cost, StrEnum, discover_all(), discover_gemini(), discover_openai(), _fetch(), _gemini_class(), _gemini_is_chat() (+43 more)

### Community 12 - "KokoroTTS"
Cohesion: 0.05
Nodes (46): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+38 more)

### Community 13 - "AvailabilityService"
Cohesion: 0.11
Nodes (10): ModelAvailability, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+2 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (69): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The… (+61 more)

### Community 15 - "test_tools.py"
Cohesion: 0.03
Nodes (96): _focused(), MonkeyPatch, parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V… (+88 more)

### Community 16 - "Indexer"
Cohesion: 0.05
Nodes (46): datetime, StoredMessage, Summarize every conversation that has gone quiet. Returns how many., Summarize one session into an episode. Idempotent; never raises. `ended_at` is…, Stamp `ended_at` without writing an episode., How much this conversation deserves to be remembered, computed. **The model was…, One model call for the summary and a salience hint. ("", 0.5) on failure., Embed episodes written while Ollama was down. (+38 more)

### Community 17 - "gate_wakeword.py"
Cohesion: 0.05
Nodes (32): main(), Download the wake word weights into data/models/openwakeword. python…, frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python… (+24 more)

### Community 18 - "Event"
Cohesion: 0.07
Nodes (26): SilentBus, ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout. (+18 more)

### Community 19 - "ConversationStore"
Cohesion: 0.05
Nodes (80): _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, When anything was last said, in any session. The whole precondition for §9's… (+72 more)

### Community 20 - "ModelInfo"
Cohesion: 0.12
Nodes (25): ExtractedEpisode, ExtractedFact, BaseModel, Reflection — where "learns on its own" actually lives (BUILD_SPEC §8.3). Once a…, What the model returned, once it survives validation., What one run did. Shown in MemoryPanel and asserted by the gate., ReflectionOutput, ReflectionReport (+17 more)

### Community 21 - "HealthTracker"
Cohesion: 0.07
Nodes (31): HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture (+23 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.08
Nodes (46): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:…, §8.3 caps at 0.95. Repetition is evidence, not proof. (+38 more)

### Community 23 - "test_screen.py"
Cohesion: 0.09
Nodes (47): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+39 more)

### Community 24 - "Settings"
Cohesion: 0.14
Nodes (11): BaseSettings, _default_data_dir(), Path, Sidecar configuration. Single source of truth for paths, port, and auth token.…, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly. (+3 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.06
Nodes (46): find_ollama(), OllamaSupervisor, Path, Keep Ollama running, and notice when it comes back. Eyaas: *"sometimes when…, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was… (+38 more)

### Community 26 - "test_router.py"
Cohesion: 0.11
Nodes (33): is_local(), RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort., Observed latency overrides the seeded table as turns land., The router must always answer. A turn with no candidates is a crash., Local models are multi-GB downloads that may not have finished. (+25 more)

### Community 27 - "eval_quality.py"
Cohesion: 0.13
Nodes (18): Namespace, main(), _pulled_models(), Answer-quality and hallucination battery. Run it, change something, run again.…, Answered something that has no answer, or claimed an action it cannot perform.…, Declined or hedged a solid fact. The counter-metric — a hallucination fix that…, The individual failures worth a human reading. A rate tells you there is a…, report() (+10 more)

### Community 28 - "handlers.py"
Cohesion: 0.04
Nodes (96): pcm16_to_float32(), Little-endian int16 -> float32 in [-1, 1], which is what whisper wants., browser_setup(), build_health(), _cdp_reachable(), chat_cancel(), chat_delete(), chat_history() (+88 more)

### Community 29 - "OpenAIProvider"
Cohesion: 0.11
Nodes (13): _assemble(), OpenAIProvider, Any, Response, ToolCall, No-op: cloud models have no local load step to pay for., One vision call: an image in, a description out. Not `stream_chat`.…, One `data:` frame into a StreamDelta. Non-data lines are ignored. `partial`… (+5 more)

### Community 30 - "state.py"
Cohesion: 0.05
Nodes (42): Deliver a message with no preceding question. Called by…, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, _now(), Sessions and messages — the durable conversation (BUILD_SPEC §7.3). This is…, Return an existing session id, or create one., ModelVerdict, BaseModel, What the router decided, and what the user made of it (§9.7). §9.7's closing… (+34 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (71): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+63 more)

### Community 32 - "Router"
Cohesion: 0.12
Nodes (22): Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, is_tool_shaped(), needs_deep_model(), BaseModel, ModelInfo, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, A request to act on the machine rather than to talk about something., Reasoning, code, or a multi-step request: the `smart` class earns its cost. (+14 more)

### Community 33 - "Fact"
Cohesion: 0.10
Nodes (15): Fact, FactHit, BaseModel, Row, The form that gets embedded and shown in the prompt., A fact with its retrieval scoring, for the panel and the prompt., A stored `fact_vec` row back into floats, or None if it has no vector., Edit a fact from the panel. Returns None if it is gone. (+7 more)

### Community 34 - "test_retrieval.py"
Cohesion: 0.11
Nodes (33): 1.0 today, 0.5 after a month, never quite zero., recency_decay(), anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice., `_build_context` runs once per attempt inside the failover loop, so without… (+25 more)

### Community 35 - "Tier"
Cohesion: 0.04
Nodes (67): EscalateFn, PreviewFn, RefuseFn, It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, The tier says she may run it; this says the answer stays here. A clipboard…, It is a strong constraint — it overrides the router — so it should be…, SAFE, not CONFIRM. A dialog in front of "remember that I prefer short answers"…, Rule 5: destructive operations are T2+ with a confirmation round-trip. (+59 more)

### Community 36 - "main.py"
Cohesion: 0.09
Nodes (34): FastAPI, clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds…, Use the token Electron supplied, or mint one for standalone runs., Publish the token for a client that did not supply one. **Not written after the…, Remove the token file on clean shutdown so no stale token survives. **Only if…, resolve_token() (+26 more)

### Community 37 - "listener.py"
Cohesion: 0.11
Nodes (24): clips(), main(), ndarray, Can she hear her own name? Across many voices, because one is not a test.…, score(), is_stop_word(), _near_the_name(), Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3). The renderer opens the… (+16 more)

### Community 38 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 39 - "test_db.py"
Cohesion: 0.07
Nodes (41): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, Run ``fn`` against the connection off the event loop, serialised., Every table in the database, including vec0 virtual tables. (+33 more)

### Community 40 - "test_conversation.py"
Cohesion: 0.04
Nodes (108): StrEnum, How much latency the user will trade for a better answer., RoutingBias, A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, _drain(), FakeProvider, make_service() (+100 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "test_reflection.py"
Cohesion: 0.09
Nodes (36): build_prompt(), choose_model(), _extract_json(), Any, §8.3's prompt, with the two slots filled., §8.3: cloud if a key is present, local otherwise. Walks SMART then BALANCED,…, Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio (+28 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "ToolContext"
Cohesion: 0.05
Nodes (78): Tool Call Log: "write me an essay on space in notepad", test_system_info_reports_this_machine(), close_app(), focus_window(), list_windows(), tool, List open application windows., Bring an open window to the front. Args: name: Part of the window's title, e.g.… (+70 more)

### Community 45 - "measure_models.py"
Cohesion: 0.19
Nodes (16): build_messages(), _is_reasoning(), provider_for(), ModelInfo, Exactly what the app would send: stable prefix first, then the turns., run_probe(), main(), measure_honesty() (+8 more)

### Community 46 - "apps.py"
Cohesion: 0.03
Nodes (105): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, main(), Console entrypoint for ``python -m sidecar.main``., _default_browser(), (exe path, profile dir) for the user's actual default browser., A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher() (+97 more)

### Community 47 - "Reflector"
Cohesion: 0.14
Nodes (10): datetime, ModelInfo, One nightly pass: read the day, extract facts, merge, prune., Read the window, extract, merge, prune. Never raises., Ask the chosen model, falling back to local on any provider failure., Fold extracted facts in, one at a time. **Sequentially, deliberately.** The…, How many messages have arrived since the last successful reflection. Cheap…, The oldest unread messages, with the id to mark on success. **Oldest first, and… (+2 more)

### Community 48 - "conversation.py"
Cohesion: 0.03
Nodes (83): exhausted_note(), LoopState, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through…, Told to the model, not just logged — it should know why it stopped., What the user sees when the model produced no words at all. A real, observed…, What one turn's agent loop is tracking, across its steps. Deliberately not… (+75 more)

### Community 49 - "Retriever"
Cohesion: 0.08
Nodes (21): _age_days(), _percentile(), Task, §9 Phase 5: 0.6·cosine + 0.25·recency + 0.15·salience, boosted by access. Two…, Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two… (+13 more)

### Community 50 - "probes.py"
Cohesion: 0.10
Nodes (33): Check, admits_ignorance(), answers_flatly(), contains(), contains_any(), denies_capability(), exact(), excludes() (+25 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "ChatMessage"
Cohesion: 0.06
Nodes (44): Headers, Compress the oldest turns. Folds in any earlier note so it compounds., default_self_check(), Off the interactive path entirely — background, local-only, the same shape…, ChatMessage, GenerationOptions, ProviderRateLimited, ProviderUnavailable (+36 more)

### Community 53 - "parametrize"
Cohesion: 0.18
Nodes (12): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., parametrize, The line that was missing. Without it these went to the FAST class., A false positive costs a spoken turn its ~800ms head start, which is the thing…, test_clipboard_questions_stay_on_this_machine(), test_code_requests_reach_a_reasoning_model(), test_conversation_is_not_mistaken_for_a_command() (+4 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "memory.py"
Cohesion: 0.13
Nodes (18): People say "remember that ..." to a thing whose job is remembering., The fallback is not a failure: the fact stays retrievable and the panel can fix…, test_a_lead_in_is_stripped(), test_an_unrecognised_phrasing_is_still_kept(), test_common_phrasings_become_real_predicates(), _clip(), forget(), tool (+10 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "test_permissions.py"
Cohesion: 0.11
Nodes (20): Collection, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, **Never default to approved on timeout** (§7.1). Somebody who walked away has…, `visit`'s checkout-page escalation would normally force a SAFE tool to CONFIRM.…, §7.2: "off by default" means the model is not told they exist, which is…, The half that was missing. `_tool_schemas` always asked for the CONFIRM…, `escalate` reaches the same CONFIRM floor `force_confirm` does — it must not be…, test_a_required_argument_is_marked_required() (+12 more)

### Community 58 - "MachineContext"
Cohesion: 0.18
Nodes (17): machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, The whole design rests on this. This block sits before the conversation, so a…, These are different things to tell someone., 4 days ago' is not worth the tokens, and the date already says when., Silence beats a wrong claim: unknown facts are simply not mentioned. (+9 more)

### Community 59 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (27): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+19 more)

### Community 60 - "ARIA Sidecar Runtime Dependencies (requirements.txt)"
Cohesion: 0.07
Nodes (27): ARIA Sidecar Runtime Dependencies (requirements.txt), anthropic==0.39.* (NOT adopted, Anthropic excluded), apscheduler==3.10.* (deferred, Phase 5), fastapi==0.115.*, faster-whisper==1.0.3, httpx==0.27.*, keyring==25.7.* (Windows Credential Manager), kokoro-onnx==0.4.* (+19 more)

### Community 61 - "rpc"
Cohesion: 0.13
Nodes (16): get, bearer_from_header(), Constant-time comparison of a presented Bearer token., Extract the token from an ``Authorization: Bearer <token>`` header., token_matches(), health(), Any, Liveness probe for Electron's supervisor. Deliberately cheap and dependency-… (+8 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "EventBus"
Cohesion: 0.14
Nodes (12): EventBus, Any, Protocol, Server -> client push notifications and the set of live connections (§7.1).…, Send the current state to one client, unconditionally. A reconnecting renderer…, Send a notification to every live client, dropping dead ones., Update the assistant state and notify clients if it actually changed., Minimal transport surface — a Starlette WebSocket satisfies this. (+4 more)

### Community 64 - "overhead_tokens"
Cohesion: 0.15
Nodes (17): overhead_tokens(), Content that changes per turn. Everything after this point re-prefills. Phase…, Tokens spent before the conversation even starts. Roll-up decisions must…, volatile_prefix(), full(), CLAUDE.md: keep the pre-conversation budget near 800 tokens on local., Roll-up decisions subtract this; if it were uncounted, a conversation could…, §8.2's order: temporal, then facts. Memory sits nearest the turns because that… (+9 more)

### Community 65 - "test_browser.py"
Cohesion: 0.04
Nodes (103): Browser, Locator, Page, FakeLocator, FakePage, Exception, MonkeyPatch, parametrize (+95 more)

### Community 66 - "Path"
Cohesion: 0.12
Nodes (21): Path, Trusting a folder means trusting what is nested in it., `allow_danger` decides whether the tool exists; trust only decides whether it…, The choice made: trust covers deletion too., The engine you get with no mode set behaves exactly as it always has — every…, Switching to MANUAL and back must not have silently cleared what was configured…, The one thing mode never touches: `Tool.refuse`'s password-field block runs…, test_a_trusted_delete_runs_without_asking() (+13 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "WakeWord"
Cohesion: 0.12
Nodes (7): Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText, ndarray, Protocol, What the listener depends on, so it never imports openwakeword., WakeWord

### Community 69 - "RecordingJournal"
Cohesion: 0.17
Nodes (13): Any, Rule 6, and the entry most worth having., Models get argument names wrong. That is a thing to say, not to crash on., An audit trail that cannot tell "you approved this" from "the folder was…, Same reasoning as trust's own audit-trail test: `approved_by` must say *why*…, RecordingJournal, test_a_denial_is_still_written_to_the_log(), test_a_failing_tool_is_reported_not_raised() (+5 more)

### Community 70 - "test_context.py"
Cohesion: 0.09
Nodes (28): estimate_tokens(), Render remembered facts and episodes into one system message. Returns None when…, _render_memory(), retrieved_block(), Machine context: the clock, the model, and what it costs to carry them., A turn about something she has no memory of must leave the prompt byte-…, A fact is a standing truth; an episode is one conversation., A clipped fact beats silence — the cap is a prefill guard, not a correctness… (+20 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "Utterance"
Cohesion: 0.10
Nodes (9): ndarray, Protocol, Voice activity detection — streaming Silero (BUILD_SPEC §9 Phase 2 stage 3).…, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance (+1 more)

### Community 73 - "StubSearch"
Cohesion: 0.15
Nodes (14): Exception, Stripping is a losing game — there are unlimited phrasings. The content is…, It has a title, a URL and a snippet. Citing it beats pretending the search did…, A model that asks for fifty pages would blow the context budget §8.2 exists to…, Stands in for the network. Returns whatever it was handed., StubSearch, test_a_source_that_would_not_load_is_still_cited(), test_an_empty_query_asks_rather_than_searching() (+6 more)

### Community 74 - "WebSearch"
Cohesion: 0.23
Nodes (8): Any, Response, RuntimeError, Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix., No usable search key, or the provider refused. Carries the fix., SearchUnavailable, WebSearch

### Community 75 - "_Reader"
Cohesion: 0.22
Nodes (4): AsyncClient, HTMLParser, Strip a page to its readable text. Not readability, not an article extractor,…, _Reader

### Community 76 - "bridge.d.ts"
Cohesion: 0.10
Nodes (19): AriaApi, AssistantState, BrainStatus, CredentialStatus, LogLine, MemoryEpisode, MemoryFact, MemoryStats (+11 more)

### Community 77 - "Electron main + Python sidecar architecture"
Cohesion: 0.11
Nodes (19): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation (+11 more)

### Community 78 - "affect.py"
Cohesion: 0.17
Nodes (18): _clamp(), _drift(), _energy_delta(), _format_hour(), _hours_since_last_interaction(), datetime, Four floats that make the same question read differently at 2am than at 2pm…, Roughly `[-1, 1]` from the last few user messages. Zero — the common case —… (+10 more)

### Community 79 - "soak_conversation.py"
Cohesion: 0.18
Nodes (12): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+4 more)

### Community 80 - "GeminiProvider"
Cohesion: 0.25
Nodes (3): GeminiProvider, Implements `LLMProvider` against the Gemini generateContent API., No-op: cloud models have no local load step to pay for.

### Community 81 - "test_research.py"
Cohesion: 0.21
Nodes (11): Readable text from a page, truncated on a word boundary., to_text(), `research(query)`, the untrusted-content boundary, and the online gate. Two…, T1. It reads and changes nothing; the consent that matters is the online…, The normal case on the open web, and returning nothing would read as "research…, Stronger than asking it not to use one: §7.2's own reasoning for hiding DANGER,…, test_extraction_is_capped(), test_malformed_html_still_yields_something() (+3 more)

### Community 82 - "test_a_call_spanning_in_and_out_still_asks"
Cohesion: 0.22
Nodes (9): fixture, Moving a file *out* of a trusted folder is not covered by trusting it — the…, Trust is about places. A tool that names none is not in one., A registry with one tool per tier, put back exactly as found. The snapshot…, test_a_call_spanning_in_and_out_still_asks(), test_a_tool_naming_no_path_is_never_trusted(), _tools(), clear() (+1 more)

### Community 83 - "CredentialKey"
Cohesion: 0.15
Nodes (20): all_status(), CredentialKey, CredentialStatus, delete_key(), get_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,… (+12 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "Source"
Cohesion: 0.18
Nodes (12): Fetch and strip anything that arrived without text. Concurrently, and failures…, One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, A model that has just read 6,000 characters of someone else's writing has…, Returns real, correct URLs" is the acceptance line, and only `summary` reaches…, test_a_source_is_truncated_rather_than_dropped(), test_every_source_carries_its_url() (+4 more)

### Community 86 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 87 - "fit_to_budget"
Cohesion: 0.40
Nodes (5): fit_to_budget(), Drop oldest turns until the assembled prompt fits. Backstop, not policy.…, It used to omit them, so it trimmed against a budget ~1650 tokens too generous.…, test_fit_to_budget_reserves_room_for_memory(), test_fit_to_budget_reserves_room_for_the_tool_schemas()

### Community 88 - "OllamaProvider"
Cohesion: 0.10
Nodes (19): HTTPError, choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for() (+11 more)

### Community 89 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 90 - "Sidebar.tsx"
Cohesion: 0.13
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 92 - "online"
Cohesion: 0.25
Nodes (8): online(), fixture, MonkeyPatch, The whole point of `SearchUnavailable` carrying a message., Online mode on, with a stubbed search behind it., Belt to `_tool_schemas`' braces. `allow_danger_tools` was dead for a whole…, test_it_refuses_when_online_mode_is_off(), test_no_key_says_which_key_and_where()

### Community 93 - "datetime"
Cohesion: 0.40
Nodes (3): datetime, Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days.

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): autoprefixer, electron, devDependencies, autoprefixer, electron, postcss, react, react-dom (+5 more)

### Community 96 - "context.py"
Cohesion: 0.11
Nodes (18): clean_title(), episode_request(), _persona(), datetime, StoredMessage, Prompt assembly and the rolling context window (BUILD_SPEC §8.2, §9 Phase 1).…, Fill in what she can reach and what she remembers. The rest is identical., Prompt asking the model to compress a whole session into an episode. Distinct… (+10 more)

### Community 97 - "SettingsStore"
Cohesion: 0.13
Nodes (17): Any, SettingsStore, Connection, fixture, parametrize, Durable settings and the v1 -> v2 migration. The migration matters more than…, Values are JSON so a new setting never needs another migration., store() (+9 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "PermissionEngine"
Cohesion: 0.25
Nodes (4): PermissionEngine, Decides whether a tool may run, and records that it was asked., Answer a pending confirmation. Returns whether one was waiting., Deny everything outstanding. Used when a turn is cancelled.

### Community 101 - "ModelListing"
Cohesion: 0.29
Nodes (7): ModelListing, BaseModel, `models.list` result., models_list(), models_refresh(), Catalog plus live availability. Drives the picker and its tooltips. Re-probes…, Ask the cloud providers what they offer today, and re-list. Deliberately…

### Community 102 - "ConfirmDialog.tsx"
Cohesion: 0.16
Nodes (10): ConfirmRequest, ImagePreview, leaf(), MovePlan, MovePlanView(), Props, tail(), TIER_LABEL (+2 more)

### Community 103 - "useConversation.ts"
Cohesion: 0.30
Nodes (11): appendToStreaming(), clearStreaming(), finalise(), loadRatings(), ToolCall, toTurns(), Turn, TurnCompletePayload (+3 more)

### Community 104 - "package.json"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 105 - "call_key"
Cohesion: 0.47
Nodes (4): call_key(), Any, A hashable fingerprint of one tool call, for loop detection. Sorted so argument…, Mark one step as run. `local_only` is unknown, not False, for a tool the…

### Community 106 - "ToolJournal"
Cohesion: 0.40
Nodes (3): Any, Writes to `tool_log`. Satisfies `tools.permissions.Journal`., ToolJournal

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "snapshot"
Cohesion: 0.29
Nodes (7): BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM unconditionally.…, §9:943 says "regardless of tool tier" — that only means something if *every*…, test_every_browser_tool_carries_the_checkout_escalation(), test_only_fill_carries_the_password_refusal(), test_tiers_deviate_from_build_specs_blanket_confirm_by_design(), A copy of the registry, for tests that install their own tools. Paired with…, snapshot()

### Community 109 - "_port_is_free"
Cohesion: 0.50
Nodes (4): _port_is_free(), Whether we can actually have the port, checked before anything else. **A second…, The incident, in one assertion. uvicorn runs the lifespan *before* it binds, so…, test_a_taken_port_is_detected_before_anything_starts()

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
Cohesion: 0.29
Nodes (9): configure_logging(), _console_handler(), _file_handler(), Handler, Path, structlog configuration. JSON to file, pretty to console in dev. CLAUDE.md rule…, JSON lines to ``data/logs/sidecar.log``. Electron tails this file., Pretty in dev, JSON in production — stdout is piped into the same log file. (+1 more)

### Community 115 - "AffectState"
Cohesion: 0.27
Nodes (10): AffectState, load(), BaseModel, The one row. Falls back to the schema's own defaults if it is somehow missing —…, save(), `schema.sql`'s own seed insert (migration 1) means Phase 8 never has to…, `affect_state.id` is `CHECK (id = 1)` — a second row is structurally…, test_load_returns_the_seeded_defaults() (+2 more)

### Community 116 - "usePermissionMode.ts"
Cohesion: 0.33
Nodes (5): MODE_COPY, MODE_LABEL, MODE_OPTIONS, PermissionMode, usePermissionMode

### Community 117 - "_cloud_model"
Cohesion: 0.20
Nodes (10): _cloud_model(), ModelInfo, 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement…, The mechanism has to keep working, or banding would just be a way of ignoring…, test_a_measured_tool_score_outranks_latency_on_a_command(), test_a_model_that_is_visibly_worse_still_loses() (+2 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "PersonaLevel"
Cohesion: 0.20
Nodes (12): assemble(), PersonaLevel, StrEnum, Content identical across turns. Everything here is KV-cached. Changing `level`…, How much character a model can carry without falling apart. Measured on…, Build the final message list, stable content first., stable_prefix(), The KV-cache bargain, asserted directly. CLAUDE.md's measured rule: an… (+4 more)

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

### Community 138 - "spawn"
Cohesion: 0.18
Nodes (9): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, Start a fresh conversation, without writing anything yet. Returns a *reserved*…, Any, Task, Fire-and-forget work that must not take the process down with it. Two rules,…, Run `coro` detached. Failures are logged against `name`, never raised. (+1 more)

### Community 139 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

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

## Knowledge Gaps
- **312 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+307 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **64 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `ConversationService`, `test_tts.py`, `test_proactivity.py`, `finder.py`, `Indexer`, `ConversationStore`, `ModelInfo`, `SemanticMemory`, `state.py`, `Fact`, `test_retrieval.py`, `main.py`, `test_db.py`, `test_conversation.py`, `test_reflection.py`, `Reflector`, `conversation.py`, `test_affect.py`, `affect.py`, `soak_conversation.py`, `SettingsStore`, `ToolJournal`, `AffectState`, `_repeated_failures`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `ConversationService` to `RecordingBus`, `test_tts.py`, `Database`, `spawn`, `Event`, `ConversationStore`, `ModelInfo`, `HealthTracker`, `state.py`, `Router`, `Tier`, `main.py`, `listener.py`, `Listener`, `test_conversation.py`, `ToolContext`, `conversation.py`, `ChatMessage`, `test_permissions.py`, `EventBus`, `WakeWord`, `RecordingJournal`, `soak_conversation.py`, `PermissionEngine`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `RecordingBus`, `ConversationService`, `test_tts.py`, `finder.py`, `test_tools.py`, `test_screen.py`, `test_organize.py`, `Tier`, `test_conversation.py`, `apps.py`, `conversation.py`, `memory.py`, `test_permissions.py`, `test_browser.py`, `RecordingJournal`, `StubSearch`, `test_research.py`, `_suppress_close_errors`, `PermissionEngine`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 44 INFERRED edges - model-reasoned connections that need verification._