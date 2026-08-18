# Graph Report - ARIA  (2026-08-18)

## Corpus Check
- 203 files · ~269,764 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4176 nodes · 9595 edges · 234 communities (173 shown, 61 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 892 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8e4993c4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_permissions.py
- test_listener.py
- main.ts
- catalog.py
- test_rpc.py
- ConversationService
- OllamaEmbeddings
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
- WakeWord
- ConversationStore
- Role
- HealthTracker
- SemanticMemory
- test_screen.py
- _start_conversation
- ProviderUnavailable
- test_router.py
- test_episodic.py
- method
- EpisodicMemory
- RoutingLog
- test_organize.py
- Router
- Fact
- test_retrieval.py
- Tier
- state.py
- strip_wake_word
- Listener
- test_db.py
- test_conversation.py
- test_focus.py
- test_reflection.py
- ARIA — Project Instructions
- ToolContext
- eval_quality.py
- apps.py
- _escalate_current_page
- conversation.py
- Retriever
- probes.py
- test_text.py
- ChatMessage
- CredentialKey
- compilerOptions
- main.py
- Connectivity
- migrate
- browser.py
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- rpc
- compilerOptions
- Event
- parametrize
- test_browser.py
- test_parse_yes_no
- test_vectors.py
- FakeLocator
- registry.py
- test_context.py
- test_affect.py
- Utterance
- test_research.py
- SpeechToText
- to_text
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- test_browser_setup.py
- _drain_windows
- ToolJournal
- context.py
- handlers.py
- _Semantic
- Source
- _reset_connection
- test_read_is_named_as_an_untrusted_source
- soak_conversation.py
- _suppress_close_errors
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- memory.py
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- retrieved_block
- SettingsStore
- PermissionEngine
- _require_memory
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- PersonaLevel
- FactSource
- render
- snapshot
- HistoryPanel.tsx
- CLAUDE.md — ARIA Project Instructions (Claude Code-facing)
- Router — local vs cloud, then which provider
- gate_affect.py
- configure_logging
- AffectState
- database
- _cloud_model
- ModelPicker.tsx
- memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py
- stable_prefix
- SettingsPanel.tsx
- preload.ts
- gate_organize.py
- make_tray_icons.py
- full
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
- gate_permission_modes.py
- gate_research.py
- BrowserUnavailable
- MemoryPanel.tsx
- She holds a conversation now (2026-08-07)
- Measuring answer quality
- Smart mode: it was the tool, and then it was the router (2026-08-12)
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
- ConnectionStatus.tsx
- Markdown.tsx
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
- RpcMethodError
- test_the_prompt_never_claims_she_remembers_nothing
- test_with_tools_she_is_told_to_look_before_denying
- test_both_levels_still_forbid_inventing_a_memory
- test_the_warm_voice_carries_no_emoji_or_filler_opener
- test_warmth_did_not_displace_the_capacity_to_disagree
- test_she_is_pointed_at_type_text_for_a_native_app
- test_she_is_told_to_use_relative_paths_not_a_guessed_account_name
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
1. `Database` - 251 edges
2. `ConversationStore` - 155 edges
3. `HealthTracker` - 106 edges
4. `ConversationService` - 102 edges
5. `ToolContext` - 94 edges
6. `SemanticMemory` - 88 edges
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

## Communities (234 total, 61 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (108): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+100 more)

### Community 1 - "test_listener.py"
Cohesion: 0.05
Nodes (76): Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout., build(), drain(), frame(), interrupt(), phrase(), Any (+68 more)

### Community 2 - "main.ts"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 3 - "catalog.py"
Cohesion: 0.05
Nodes (74): Which models are usable right now. One object answers this for both…, all_models(), by_class(), default_local(), discovered(), get(), local_models(), ModelAvailability (+66 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.14
Nodes (31): _auth(), _call(), client(), fixture, MonkeyPatch, Path, The /rpc token gate and JSON-RPC dispatch (BUILD_SPEC §7.1). Beyond the Phase 0…, The id is reserved, not written — so the list stays empty. (+23 more)

### Community 5 - "ConversationService"
Cohesion: 0.04
Nodes (39): SessionSummary, ConversationService, Any, ModelInfo, RoutingBias, StoredMessage, ToolCall, Which model gets to see the tool's result. `router._PRIVATE` already keeps a… (+31 more)

### Community 6 - "OllamaEmbeddings"
Cohesion: 0.07
Nodes (31): _age_days(), _percentile(), datetime, Retrieval — putting the right memory in front of the model (§9 Phase 5). **The…, 1.0 today, 0.5 after a month, never quite zero., §9 Phase 5: 0.6·cosine + 0.25·recency + 0.15·salience, boosted by access. Two…, What `memory.stats` reports and `gate_memory.py` asserts against., Word overlap in place of cosine. Sub-millisecond, and honest about it. Not a… (+23 more)

### Community 7 - "test_tts.py"
Cohesion: 0.04
Nodes (64): Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., SpeechStream, ndarray, Protocol, RuntimeError, Cap one spoken breath at `max_words`, pushing the rest back onto the front of… (+56 more)

### Community 8 - "Database"
Cohesion: 0.08
Nodes (57): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+49 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.11
Nodes (36): Candidate, default_candidates(), idle_intention_candidate(), is_stated_intention(), ProactivityScheduler, datetime, timedelta, Unprompted messages — rate-limited, focus-aware, self-checked (BUILD_SPEC §9… (+28 more)

### Community 11 - "discovery.py"
Cohesion: 0.07
Nodes (51): Cost, StrEnum, discover_all(), discover_gemini(), discover_openai(), _fetch(), _gemini_class(), _gemini_is_chat() (+43 more)

### Community 12 - "KokoroTTS"
Cohesion: 0.05
Nodes (49): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+41 more)

### Community 13 - "AvailabilityService"
Cohesion: 0.09
Nodes (12): ModelAvailability, AvailabilityService, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand. (+4 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (69): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The… (+61 more)

### Community 15 - "test_tools.py"
Cohesion: 0.04
Nodes (89): MonkeyPatch, parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, Overwriting is a different destructive act from moving, and the user approved a…, 7 zip" matched "7-Zip Help" purely because it is the shorter name., The demotion must not make the entry unreachable., Opening the wrong app is worse than opening nothing. (+81 more)

### Community 16 - "Indexer"
Cohesion: 0.08
Nodes (38): chunk(), _digest(), extract_text(), Indexer, IndexStats, _pack(), Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks… (+30 more)

### Community 17 - "gate_wakeword.py"
Cohesion: 0.05
Nodes (33): main(), Download the wake word weights into data/models/openwakeword. python…, frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python… (+25 more)

### Community 18 - "WakeWord"
Cohesion: 0.22
Nodes (4): ndarray, Protocol, What the listener depends on, so it never imports openwakeword., WakeWord

### Community 19 - "ConversationStore"
Cohesion: 0.08
Nodes (40): ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, A fresh id with no row behind it yet. `ensure_session` creates a row for any id…, Name a conversation. The `with conn:` is load-bearing. Python's sqlite3 opens…, Remove a conversation and everything in it. Returns messages deleted. Both… (+32 more)

### Community 20 - "Role"
Cohesion: 0.06
Nodes (43): Episodes — what happened, compressed and kept (BUILD_SPEC §7.3 tier 2). One…, MessageHit, BaseModel, Sessions and messages — the durable conversation (BUILD_SPEC §7.3). This is…, Find past turns that mention what `query` is about. **This is the layer that…, One past turn that matched a `recall` query., ExtractedEpisode, ExtractedFact (+35 more)

### Community 21 - "HealthTracker"
Cohesion: 0.05
Nodes (44): HealthTracker, ModelHealth, BaseModel, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture, Observed latency and the circuit breaker. A 429 is treated as a routing input… (+36 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.08
Nodes (44): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:… (+36 more)

### Community 23 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 24 - "_start_conversation"
Cohesion: 0.07
Nodes (29): BaseSettings, Path, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch…, A `.bat` that starts the user's real Chrome with CDP on (§9 Phase 7). In…, Create the runtime directory tree. Safe to call repeatedly., Sidecar settings, loaded once per process., Settings (+21 more)

### Community 25 - "ProviderUnavailable"
Cohesion: 0.08
Nodes (23): Headers, ProviderRateLimited, ProviderUnavailable, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input…, The backend could not be reached — offline, not running, DNS, refused. Distinct…, get_key(), Read a key, or None if unset. Never logs the value., Response (+15 more)

### Community 26 - "test_router.py"
Cohesion: 0.08
Nodes (46): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort. (+38 more)

### Community 27 - "test_episodic.py"
Cohesion: 0.09
Nodes (41): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., _conversation(), _episodic(), anyio, Connection (+33 more)

### Community 28 - "method"
Cohesion: 0.08
Nodes (36): chat_cancel(), chat_history(), chat_new(), chat_send(), confirm_respond(), method(), models_list(), models_refresh() (+28 more)

### Community 29 - "EpisodicMemory"
Cohesion: 0.08
Nodes (18): Episode, EpisodicMemory, _now(), BaseModel, datetime, Row, StoredMessage, A row from `episodes`, as the panel and retrieval see it. (+10 more)

### Community 30 - "RoutingLog"
Cohesion: 0.08
Nodes (30): ModelVerdict, BaseModel, What the router decided, and what the user made of it (§9.7). §9.7's closing…, Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Per-model tallies. The dataset §9.7 wants, as far as it has grown., How a model has actually been received, per `routing_log`. (+22 more)

### Community 31 - "test_organize.py"
Cohesion: 0.06
Nodes (69): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+61 more)

### Community 32 - "Router"
Cohesion: 0.10
Nodes (26): Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, is_tool_shaped(), needs_deep_model(), BaseModel, ModelInfo, StrEnum, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, A request to act on the machine rather than to talk about something. (+18 more)

### Community 33 - "Fact"
Cohesion: 0.17
Nodes (8): Fact, Row, The form that gets embedded and shown in the prompt., Edit a fact from the panel. Returns None if it is gone., Nearest active facts to a vector, as (fact, cosine). Mirrors…, Embed facts written while Ollama was down. Chat must never wait on embeddings,…, Every active fact about `subject`, each with its stored vector. One query…, A row from `facts`, as the UI, the prompt and the tools see it.

### Community 34 - "test_retrieval.py"
Cohesion: 0.13
Nodes (30): anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice., `_build_context` runs once per attempt inside the failover loop, so without…, Below MIN_SCORE nothing is injected, so the prompt stays byte-identical to a…, The KV-cache invariant, asserted from the retrieval side too. (+22 more)

### Community 35 - "Tier"
Cohesion: 0.07
Nodes (37): EscalateFn, PreviewFn, RefuseFn, Bus, Denied, Journal, paths_in(), Pending (+29 more)

### Community 36 - "state.py"
Cohesion: 0.11
Nodes (15): SQLite connection, sqlite-vec loading, and the migration runner. One connection…, FactHit, normalise_triple(), BaseModel, datetime, Facts — what she has LEARNED about you (BUILD_SPEC §7.3 tier 3, §8.3). A fact…, A fact with its retrieval scoring, for the panel and the prompt., Fold a triple to its stored form. The UNIQUE index is on the raw columns, so… (+7 more)

### Community 37 - "strip_wake_word"
Cohesion: 0.16
Nodes (14): is_stop_word(), Is this whole utterance just a request to stop talking?, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said., The name has to be first. Anywhere else it is just a word., Matched whole, never as a prefix. (+6 more)

### Community 38 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 39 - "test_db.py"
Cohesion: 0.17
Nodes (18): Every table in the database, including vec0 virtual tables., table_names(), Connection, Path, Phase 0 acceptance gate: the database is created and migrated from schema.sql., The schema declares float[768]; prove it round-trips., test_affect_state_singleton_is_seeded(), test_all_schema_tables_exist() (+10 more)

### Community 40 - "test_conversation.py"
Cohesion: 0.05
Nodes (102): A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, _drain(), FakeProvider, make_service(), OpenEngine, _proactivity_service(), anyio (+94 more)

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
Cohesion: 0.06
Nodes (71): Tool Call Log: "write me an essay on space in notepad", test_system_info_reports_this_machine(), tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, The clipboard's text, or None when it holds something else. An image, a file…, Read the clipboard's text., _read() (+63 more)

### Community 45 - "eval_quality.py"
Cohesion: 0.10
Nodes (31): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+23 more)

### Community 46 - "apps.py"
Cohesion: 0.06
Nodes (59): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, §7.2's second failure mode: the model gets one line, the UI gets the lot., A dead end is useless; naming the closest lets the model retry., browser" scored 0.88 against LockDown Browser and won. A category is not a…, test_category_words_are_recognised_before_they_are_matched(), test_listing_windows_summarises_rather_than_dumps(), test_ranking_offers_the_near_misses() (+51 more)

### Community 47 - "_escalate_current_page"
Cohesion: 0.17
Nodes (13): The URL check catches the common case; a card-number field on an unlisted…, No page has loaded yet at this point — only the URL being navigated *to* is…, test_a_generic_domain_can_still_be_caught_by_its_dom(), test_known_checkout_and_banking_urls_are_recognised(), test_navigate_escalates_on_the_target_url_before_loading_it(), test_no_checkout_fields_means_no_dom_match(), _dom_confirms_checkout(), _escalate_current_page() (+5 more)

### Community 48 - "conversation.py"
Cohesion: 0.06
Nodes (44): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through…, Told to the model, not just logged — it should know why it stopped. (+36 more)

### Community 49 - "Retriever"
Cohesion: 0.16
Nodes (9): Task, Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache., Cancel any embed still running past its deadline. Without this, shutting down… (+1 more)

### Community 50 - "probes.py"
Cohesion: 0.09
Nodes (36): Check, Answered something that has no answer, or claimed an action it cannot perform.…, admits_ignorance(), answers_flatly(), claimed_action(), contains(), contains_any(), denies_capability() (+28 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "ChatMessage"
Cohesion: 0.05
Nodes (51): HTTPError, choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for() (+43 more)

### Community 53 - "CredentialKey"
Cohesion: 0.17
Nodes (17): all_status(), CredentialKey, CredentialStatus, delete_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Credential Manager entry names under the ARIA service. (+9 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "main.py"
Cohesion: 0.11
Nodes (25): FastAPI, get_settings(), Sidecar configuration. Single source of truth for paths, port, and auth token.…, Process-wide settings singleton., bearer_from_header(), clear_handshake(), Path, WebSocket auth token lifecycle (BUILD_SPEC §7.1). The sidecar binds… (+17 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "migrate"
Cohesion: 0.15
Nodes (14): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, Run ``fn`` against the connection off the event loop, serialised., Open the database with sqlite-vec loaded and the required pragmas set. (+6 more)

### Community 58 - "browser.py"
Cohesion: 0.13
Nodes (26): Page, test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), browser_click(), browser_fill(), browser_navigate(), browser_read(), browser_screenshot() (+18 more)

### Community 59 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (27): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+19 more)

### Community 60 - "ARIA Sidecar Runtime Dependencies (requirements.txt)"
Cohesion: 0.07
Nodes (27): ARIA Sidecar Runtime Dependencies (requirements.txt), anthropic==0.39.* (NOT adopted, Anthropic excluded), apscheduler==3.10.* (deferred, Phase 5), fastapi==0.115.*, faster-whisper==1.0.3, httpx==0.27.*, keyring==25.7.* (Windows Credential Manager), kokoro-onnx==0.4.* (+19 more)

### Community 61 - "rpc"
Cohesion: 0.18
Nodes (12): get, Constant-time comparison of a presented Bearer token., token_matches(), health(), Any, Liveness probe for Electron's supervisor. Deliberately cheap and dependency-…, Token-gated JSON-RPC endpoint (§7.1). The port is reachable by any browser tab…, Read/dispatch/reply until the client goes away. (+4 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "Event"
Cohesion: 0.07
Nodes (23): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, AssistantState, Event, EventBus, Any, Protocol (+15 more)

### Community 64 - "parametrize"
Cohesion: 0.25
Nodes (9): parametrize, test_ordinary_targets_are_not_refused(), test_ordinary_urls_are_not_flagged(), test_password_shaped_targets_are_refused(), test_role_name_strips_the_leading_article_and_trailing_noun(), A hard block, not a dialog — see the module docstring. Reads only the call's…, the Send button" -> "Send" — a role lookup wants the label, not the description…, _refuse_password_field() (+1 more)

### Community 65 - "test_browser.py"
Cohesion: 0.14
Nodes (30): FakePage, MonkeyPatch, Browser control: the checkout/banking hard block, password refusal, and element…, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, Implements exactly the `Page` surface `browser.py` calls., _returning() (+22 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "FakeLocator"
Cohesion: 0.09
Nodes (12): Locator, FakeLocator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, Refusing to act on an ambiguous-but-real description is worse than picking the…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught() (+4 more)

### Community 69 - "registry.py"
Cohesion: 0.07
Nodes (32): The tier says she may run it; this says the answer stays here. A clipboard…, It is a strong constraint — it overrides the router — so it should be…, SAFE, not CONFIRM. A dialog in front of "remember that I prefer short answers"…, Rule 5: destructive operations are T2+ with a confirmation round-trip., AUTO, as BUILD_SPEC:474 lists it. Reading her own memory is not an act on the…, The schema is what the model has to fill in blind. One string., The schema has to permit the relative form, or the description is a lie about…, It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-… (+24 more)

### Community 70 - "test_context.py"
Cohesion: 0.19
Nodes (21): machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Machine context: the clock, the model, and what it costs to carry them., The whole design rests on this. This block sits before the conversation, so a…, These are different things to tell someone., 4 days ago' is not worth the tokens, and the date already says when. (+13 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "Utterance"
Cohesion: 0.11
Nodes (8): ndarray, Protocol, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance, VoiceActivity

### Community 73 - "test_research.py"
Cohesion: 0.12
Nodes (23): online(), fixture, MonkeyPatch, `research(query)`, the untrusted-content boundary, and the online gate. Two…, Stripping is a losing game — there are unlimited phrasings. The content is…, It has a title, a URL and a snippet. Citing it beats pretending the search did…, The whole point of `SearchUnavailable` carrying a message., A model that asks for fifty pages would blow the context budget §8.2 exists to… (+15 more)

### Community 74 - "SpeechToText"
Cohesion: 0.29
Nodes (3): Protocol, What the RPC layer depends on, so it never imports ctranslate2., SpeechToText

### Community 75 - "to_text"
Cohesion: 0.13
Nodes (10): AsyncClient, HTMLParser, Readable text from a page, truncated on a word boundary., Strip a page to its readable text. Not readability, not an article extractor,…, _Reader, to_text(), The normal case on the open web, and returning nothing would read as "research…, test_extraction_is_capped() (+2 more)

### Community 76 - "bridge.d.ts"
Cohesion: 0.10
Nodes (19): AriaApi, AssistantState, BrainStatus, CredentialStatus, LogLine, MemoryEpisode, MemoryFact, MemoryStats (+11 more)

### Community 77 - "Electron main + Python sidecar architecture"
Cohesion: 0.11
Nodes (19): Electron main + Python sidecar architecture, ARIA — local-first Windows AI assistant, Confirmation timeout resolves to denied, WebSocket JSON-RPC 2.0 IPC contract, API keys in Windows Credential Manager via keyring, Never silently destructive, Phase 7 — Browser, Untrusted content delimiters + forced T2 escalation (+11 more)

### Community 78 - "affect.py"
Cohesion: 0.17
Nodes (18): _clamp(), _drift(), _energy_delta(), _format_hour(), _hours_since_last_interaction(), datetime, Four floats that make the same question read differently at 2am than at 2pm…, Roughly `[-1, 1]` from the last few user messages. Zero — the common case —… (+10 more)

### Community 79 - "test_browser_setup.py"
Cohesion: 0.16
Nodes (18): _default_browser(), Path, (exe path, profile dir) for the user's actual default browser., A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch, Path, `browser.setup`'s launcher detection. The bug this guards against was real, not… (+10 more)

### Community 80 - "_drain_windows"
Cohesion: 0.33
Nodes (5): _drain_windows(), parts(), fixture, Cancel every listening window a test left open. Not optional: ARMED and OPEN…, openWakeWord gating — `hey jarvis` opens capture.

### Community 81 - "ToolJournal"
Cohesion: 0.40
Nodes (3): Where every tool call is recorded (BUILD_SPEC §7.3, CLAUDE.md rule 6). Append-…, Writes to `tool_log`. Satisfies `tools.permissions.Journal`., ToolJournal

### Community 82 - "context.py"
Cohesion: 0.12
Nodes (16): clean_title(), episode_request(), _persona(), datetime, StoredMessage, Prompt assembly and the rolling context window (BUILD_SPEC §8.2, §9 Phase 1).…, Fill in what she can reach and what she remembers. The rest is identical., Prompt asking the model to compress a whole session into an episode. Distinct… (+8 more)

### Community 83 - "handlers.py"
Cohesion: 0.17
Nodes (14): browser_setup(), build_health(), _cdp_reachable(), chat_sessions(), _enumerate_drives(), JSON-RPC method registry and dispatch (BUILD_SPEC §7.1). Phase 0 registers only…, Every fixed drive letter Windows reports, as root paths ("C:\\").…, Trust every drive letter on the machine, in one call. The direct answer to… (+6 more)

### Community 85 - "Source"
Cohesion: 0.09
Nodes (24): available(), Any, Response, RuntimeError, Web search, and turning a page into something a model can read. BUILD_SPEC §9…, Which search backend can run, or None. Never raises, never blocks., Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix. (+16 more)

### Community 86 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 88 - "soak_conversation.py"
Cohesion: 0.21
Nodes (10): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+2 more)

### Community 89 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 90 - "Sidebar.tsx"
Cohesion: 0.14
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.14
Nodes (14): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+6 more)

### Community 93 - "memory.py"
Cohesion: 0.23
Nodes (11): _clip(), forget(), tool, Teaching her directly: `remember` and `forget` (§9 Phase 5). Reflection learns…, Look through past conversations, remembered facts and episodes. Args: query:…, `2026-08-12T10:50:12Z` -> `on 12 Aug`. The date is what makes it a memory., Delete remembered facts matching a description. Args: query: What to forget,…, Keep something about the user for later conversations. Args: fact: The thing to… (+3 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): autoprefixer, electron, devDependencies, autoprefixer, electron, postcss, react, react-dom (+5 more)

### Community 96 - "retrieved_block"
Cohesion: 0.12
Nodes (17): estimate_tokens(), Render remembered facts and episodes into one system message. Returns None when…, Split turns into (to_summarize, to_keep). §9 Phase 1: once the conversation…, _render_memory(), retrieved_block(), split_for_rollup(), A turn about something she has no memory of must leave the prompt byte-…, A fact is a standing truth; an episode is one conversation. (+9 more)

### Community 97 - "SettingsStore"
Cohesion: 0.13
Nodes (17): Any, SettingsStore, Connection, fixture, parametrize, Durable settings and the v1 -> v2 migration. The migration matters more than…, Values are JSON so a new setting never needs another migration., store() (+9 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 101 - "_require_memory"
Cohesion: 0.17
Nodes (12): memory_forget(), memory_list(), memory_search(), memory_stats(), memory_update(), Edit a fact, including pinning it. Pinning rides here rather than on its own…, Counts, retrieval latency, and whether embeddings are actually working. The…, The memory services, or a message saying how to turn them on. (+4 more)

### Community 102 - "ConfirmDialog.tsx"
Cohesion: 0.20
Nodes (9): ConfirmRequest, ImagePreview, leaf(), MovePlan, MovePlanView(), Props, tail(), TIER_LABEL (+1 more)

### Community 103 - "useConversation.ts"
Cohesion: 0.30
Nodes (11): appendToStreaming(), clearStreaming(), finalise(), loadRatings(), ToolCall, toTurns(), Turn, TurnCompletePayload (+3 more)

### Community 104 - "package.json"
Cohesion: 0.18
Nodes (10): author, dependencies, ws, description, license, main, name, private (+2 more)

### Community 105 - "PersonaLevel"
Cohesion: 0.24
Nodes (10): fit_to_budget(), overhead_tokens(), PersonaLevel, StrEnum, How much character a model can carry without falling apart. Measured on…, Tokens spent before the conversation even starts. Roll-up decisions must…, Drop oldest turns until the assembled prompt fits. Backstop, not policy.…, It used to omit them, so it trimmed against a budget ~1650 tokens too generous.… (+2 more)

### Community 106 - "FactSource"
Cohesion: 0.09
Nodes (14): _now(), Return an existing session id, or create one., Write one decision. Returns its id, or None if it could not be., FactSource, _now(), StrEnum, Merge one observation into the store, per §8.3. Order matters: 1. **Exact…, §8.3: exact triple → evidence_count += 1, confidence += 0.1 (cap 0.95). (+6 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "snapshot"
Cohesion: 0.18
Nodes (11): BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM unconditionally.…, §9:943 says "regardless of tool tier" — that only means something if *every*…, test_every_browser_tool_carries_the_checkout_escalation(), test_only_fill_carries_the_password_refusal(), test_tiers_deviate_from_build_specs_blanket_confirm_by_design(), T1. It reads and changes nothing; the consent that matters is the online…, test_research_needs_no_confirmation(), BUILD_SPEC's own tier table (§9:474) lists this AUTO — that line is about the… (+3 more)

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

### Community 116 - "database"
Cohesion: 0.29
Nodes (9): conn(), database(), db_path(), Connection, fixture, Path, Shared fixtures. Every test gets a throwaway data dir — never the real data/., A migrated database on a temp path. (+1 more)

### Community 117 - "_cloud_model"
Cohesion: 0.20
Nodes (10): _cloud_model(), ModelInfo, 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement…, The mechanism has to keep working, or banding would just be a way of ignoring…, test_a_measured_tool_score_outranks_latency_on_a_command(), test_a_model_that_is_visibly_worse_still_loses() (+2 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "stable_prefix"
Cohesion: 0.22
Nodes (10): assemble(), Content identical across turns. Everything here is KV-cached. Changing `level`…, Build the final message list, stable content first., stable_prefix(), The KV-cache bargain, asserted directly. CLAUDE.md's measured rule: an…, test_machine_context_sits_after_identity_and_before_the_turns(), test_memory_never_touches_the_stable_prefix(), The KV cache only holds if this never varies (§8.2). (+2 more)

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

### Community 126 - "full"
Cohesion: 0.18
Nodes (12): Content that changes per turn. Everything after this point re-prefills. Phase…, volatile_prefix(), full(), CLAUDE.md: keep the pre-conversation budget near 800 tokens on local., Roll-up decisions subtract this; if it were uncounted, a conversation could…, §8.2's order: temporal, then facts. Memory sits nearest the turns because that…, Uncounted, a roll-up could 'succeed' and still overflow the context — the same…, test_overhead_accounts_for_the_machine_block() (+4 more)

### Community 127 - "_repeated_failures"
Cohesion: 0.32
Nodes (8): Two or more failed tool calls in this session, recently — 'repeated', not 'a…, _repeated_failures(), _log_failure(), Connection, _seed_session(), test_a_failure_outside_the_recent_window_does_not_count(), test_refresh_loads_updates_and_saves_in_one_call(), test_repeated_failures_reads_recent_tool_log()

### Community 129 - "ToolsPanel.tsx"
Cohesion: 0.25
Nodes (6): MODE_COPY, MODE_OPTIONS, PermissionMode, TIER_LABEL, TIER_STYLE, ToolSummary

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

### Community 138 - "gate_permission_modes.py"
Cohesion: 0.67
Nodes (3): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…

### Community 139 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 141 - "BrowserUnavailable"
Cohesion: 0.17
Nodes (11): Browser, Exception, _raising(), `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, test_navigate_reports_browser_unavailable_plainly(), test_no_user_facing_browser_error_names_chrome(), BrowserUnavailable, _connect() (+3 more)

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

### Community 212 - "RpcMethodError"
Cohesion: 0.10
Nodes (21): chat_delete(), chat_rename(), memory_reflect(), models_bias(), models_select(), permissions_mode(), Run the §8.3 pass now, rather than waiting for 3am. Synchronous, like…, Persist the model choice: a catalog id, or "smart". (+13 more)

## Knowledge Gaps
- **302 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+297 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **61 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `ConversationService`, `OllamaEmbeddings`, `test_tts.py`, `test_proactivity.py`, `AvailabilityService`, `finder.py`, `Indexer`, `ConversationStore`, `Role`, `SemanticMemory`, `test_episodic.py`, `EpisodicMemory`, `RoutingLog`, `Fact`, `test_retrieval.py`, `state.py`, `test_db.py`, `test_conversation.py`, `test_reflection.py`, `conversation.py`, `main.py`, `migrate`, `test_affect.py`, `affect.py`, `ToolJournal`, `soak_conversation.py`, `SettingsStore`, `FactSource`, `AffectState`, `database`, `_repeated_failures`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `ConversationService`, `test_tts.py`, `BrowserUnavailable`, `finder.py`, `test_tools.py`, `test_screen.py`, `test_organize.py`, `Tier`, `apps.py`, `conversation.py`, `browser.py`, `test_browser.py`, `FakeLocator`, `registry.py`, `test_research.py`, `test_browser_setup.py`, `_Semantic`, `_suppress_close_errors`, `memory.py`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `catalog.py`, `test_tts.py`, `Database`, `KokoroTTS`, `AvailabilityService`, `ConversationStore`, `Role`, `HealthTracker`, `_start_conversation`, `ProviderUnavailable`, `RoutingLog`, `Router`, `Tier`, `state.py`, `Listener`, `test_conversation.py`, `ToolContext`, `conversation.py`, `ChatMessage`, `main.py`, `Event`, `soak_conversation.py`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Are the 48 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 44 INFERRED edges - model-reasoned connections that need verification._