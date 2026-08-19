# Graph Report - ARIA  (2026-08-19)

## Corpus Check
- 235 files · ~338,948 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4910 nodes · 11196 edges · 268 communities (195 shown, 73 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 999 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c9b60424`
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
- KokoroTTS
- apps.py
- finder.py
- test_tools.py
- indexer.py
- Event
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
- test_conversation.py
- RoutingLog
- test_organize.py
- ModelClass
- semantic.py
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
- extract.py
- TextToSpeech
- Retriever
- eval_quality.py
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
- main.py
- compilerOptions
- FakeLocator
- OpenRouterProvider
- test_browser.py
- Indexer
- test_vectors.py
- test_context.py
- test_browser_setup.py
- retrieved_block
- test_affect.py
- gate_latency.py
- test_research.py
- registry.py
- CredentialKey
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- Router
- test_adoption.py
- GeminiProvider
- discovery.py
- test_finder.py
- FilesPanel.tsx
- ModelInfo
- organize.py
- files_rename
- OpenAIProvider
- _suppress_close_errors
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- OllamaSupervisor
- overhead_tokens
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- context.py
- state.py
- PermissionEngine
- WakeWord
- FilesPanel.test.tsx
- invalidate_scan
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- _escalate_current_page
- spawn
- render
- FakeTTS
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
- SpeechUnavailable
- ._prune
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
- handlers.py
- MemoryPanel.test.tsx
- Orb.tsx
- scripts
- core/router.py — model Router
- tools_trust_all_drives
- _Cache
- probes.py
- tts.py
- ChatMessage
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
- ._insert
- ModelVerdict
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
- clear_adopted
- persona_for
- Any
- ._free_vram_for
- useConversationMode.ts
- motion.ts
- clean_query
- test_with_tools_she_is_told_to_look_before_denying
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
- score
- test_the_warm_voice_carries_no_emoji_or_filler_opener
- test_she_is_pointed_at_type_text_for_a_native_app
- AdoptionState
- tokens.js
- test_no_placeholder_survives_in_any_resolved_prompt
- test_archives_are_attachable_but_never_indexed
- test_the_gate_is_the_same_probes_the_scripts_use
- useConversation.test.ts
- Cost
- _undated
- test_a_reply_that_leaks_the_prompt_fails_even_when_correct
- test_read_is_named_as_an_untrusted_source
- test_the_prompt_never_claims_she_remembers_nothing
- test_both_levels_still_forbid_inventing_a_memory
- test_warmth_did_not_displace_the_capacity_to_disagree
- eval/__init__.py
- test_she_is_told_to_use_relative_paths_not_a_guessed_account_name

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

## Communities (268 total, 73 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (106): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+98 more)

### Community 1 - "test_listener.py"
Cohesion: 0.06
Nodes (69): drain(), frame(), interrupt(), Any, ndarray, Hands-free listening: endpointing, the wake word, and barge-in. No audio device…, Transcription runs off the frame path, so tests must wait for it., The gate is the orb reacting within 300ms, so the state change must happen on… (+61 more)

### Community 2 - "main.ts"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 3 - "test_catalog.py"
Cohesion: 0.10
Nodes (29): default_local(), ModelAvailability, A catalog entry plus whether it can actually be used right now., The local fallback. Prefers the instruction-tuned 7B. `pulled` is what Ollama…, Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from., resolve_availability(), usable_ids() (+21 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.10
Nodes (40): files_browse(), One folder's contents, for the panel. Deliberately not `list_folder`: that tool…, _auth(), _call(), client(), fixture, MonkeyPatch, parametrize (+32 more)

### Community 5 - "ConversationService"
Cohesion: 0.06
Nodes (24): SessionSummary, ConversationService, RoutingBias, Name the conversation once it has enough content to name. Deliberately fire-…, Hold until no turn is in flight. False if the user never stops., Ask the local model for a short label. Never raises., Owns in-flight turns. All durable state goes to SQLite., Persisted choice: a catalog id, or "smart" to let the router decide. (+16 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.06
Nodes (60): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no…, One attachment, understood. Never raises. (+52 more)

### Community 7 - "test_tts.py"
Cohesion: 0.13
Nodes (24): Cap one spoken breath at `max_words`, pushing the rest back onto the front of…, shorten_for_speech(), drain_text(), parametrize, Speech chunking and the rule that reasoning is never spoken., The common shape of a reply, and the worst case for silence., A clean, comma-free 24-word sentence sits well under CHUNK_MAX_CHARS, so only…, A comma inside the word budget is a more natural cut than a bare word count —… (+16 more)

### Community 8 - "Database"
Cohesion: 0.07
Nodes (55): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+47 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (42): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday., Sweeps idle sessions, and runs reflection once per day. (+34 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.06
Nodes (66): Candidate, default_candidates(), idle_intention_candidate(), is_stated_intention(), ProactivityScheduler, procedure_offer_candidate(), datetime, Path (+58 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.11
Nodes (29): parse_openai(), Chat models from a `GET /v1/models` body., gemini_ids(), _load(), openai_ids(), Any, fixture, parametrize (+21 more)

### Community 12 - "KokoroTTS"
Cohesion: 0.08
Nodes (24): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+16 more)

### Community 13 - "apps.py"
Cohesion: 0.04
Nodes (76): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, `normalise("notepad++")` is `"notepad"`, which scored an exact 1.00 against the…, Asking for "notepad" may well mean Notepad++; the ranking can decide. Asking…, Only `+` and `#` name a different product. The 7-Zip cases depend on everything…, test_a_shared_symbol_still_matches(), test_hyphens_and_dots_are_still_noise(), test_punctuation_that_names_a_different_product_is_not_folded_away() (+68 more)

### Community 14 - "finder.py"
Cohesion: 0.13
Nodes (26): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), everything_path(), find(), find_files(), FoundFile, _install_hint(), open_file() (+18 more)

### Community 15 - "test_tools.py"
Cohesion: 0.02
Nodes (134): _focused(), MonkeyPatch, parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V… (+126 more)

### Community 16 - "indexer.py"
Cohesion: 0.12
Nodes (24): chunk(), _pack(), The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, Whether this file is worth reading at all., sqlite-vec takes raw little-endian float32., Overlapping windows, so a sentence spanning a boundary stays findable., should_index(), parametrize (+16 more)

### Community 17 - "Event"
Cohesion: 0.06
Nodes (32): frames(), main(), NullConversation, NullSTT, ndarray, Stage 3 gate, for the parts a machine can check. python…, say(), SilentBus (+24 more)

### Community 18 - "test_modes.py"
Cohesion: 0.05
Nodes (50): ConversationMode, Persist whatever was generated — a half reply is still conversation., Start a turn. Returns immediately; the reply streams as events. Omitting…, This conversation's mode, NORMAL until it is set., Set it for one conversation. NORMAL is stored as an absence, so a session that…, policy_for(), ConversationMode, The policy, or Normal's. Never raises. A mode arriving from a stale client is a… (+42 more)

### Community 19 - "ConversationStore"
Cohesion: 0.07
Nodes (41): ConversationStore, CRUD over `sessions` and `messages`., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's…, When the last proactive message went out, anywhere, for the 90-minute spacing…, When anything was last said, in any session. The whole precondition for §9's…, A fresh id with no row behind it yet. `ensure_session` creates a row for any id…, Name a conversation. The `with conn:` is load-bearing. Python's sqlite3 opens… (+33 more)

### Community 20 - "OllamaEmbeddings"
Cohesion: 0.07
Nodes (31): _age_days(), _percentile(), datetime, Retrieval — putting the right memory in front of the model (§9 Phase 5). **The…, 1.0 today, 0.5 after a month, never quite zero., §9 Phase 5: 0.6·cosine + 0.25·recency + 0.15·salience, boosted by access. Two…, What `memory.stats` reports and `gate_memory.py` asserts against., Word overlap in place of cosine. Sub-millisecond, and honest about it. Not a… (+23 more)

### Community 21 - "HealthTracker"
Cohesion: 0.08
Nodes (30): HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture (+22 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.07
Nodes (49): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:… (+41 more)

### Community 23 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 24 - "soak_conversation.py"
Cohesion: 0.29
Nodes (9): concrete_tokens(), main(), novel_tokens(), Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., run(), get_settings() (+1 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.09
Nodes (35): FakeOllama, Any, Path, Starting Ollama, and noticing when it comes back. Eyaas: *"sometimes when…, Somebody running Ollama on another machine, or keeping it off on purpose, still…, **The bug this whole file exists for.** Coming back up is worth nothing on its…, Ollama stays up for hours. Re-listing its models every 20 seconds would be a…, Killing Ollama mid-session and starting it again is exactly the case Eyaas hit.… (+27 more)

### Community 26 - "test_router.py"
Cohesion: 0.09
Nodes (43): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort. (+35 more)

### Community 27 - "test_extract.py"
Cohesion: 0.13
Nodes (30): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+22 more)

### Community 28 - "method"
Cohesion: 0.05
Nodes (76): chat_cancel(), chat_delete(), chat_history(), chat_mode(), chat_new(), chat_rename(), chat_send(), chat_sessions() (+68 more)

### Community 29 - "test_conversation.py"
Cohesion: 0.07
Nodes (70): A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, _drain(), OpenEngine, Path, ToolCall, Turn orchestration, cancellation, persistence and context roll-up., §11 escalates the step after *reading* untrusted content. A `research` that was… (+62 more)

### Community 30 - "RoutingLog"
Cohesion: 0.10
Nodes (25): Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Writes and reads `routing_log`. Never raises into the turn path., Write one decision. Returns its id, or None if it could not be., RoutingLog, Connection, fixture (+17 more)

### Community 31 - "test_organize.py"
Cohesion: 0.08
Nodes (55): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+47 more)

### Community 32 - "ModelClass"
Cohesion: 0.11
Nodes (24): is_tool_shaped(), needs_deep_model(), BaseModel, ModelInfo, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, A request to act on the machine rather than to talk about something., Reasoning, code, or a multi-step request: the `smart` class earns its cost., Whether this endpoint may train on what is sent to it. Unknown ids read as… (+16 more)

### Community 33 - "semantic.py"
Cohesion: 0.07
Nodes (27): Fact, FactHit, MergeOutcome, normalise_triple(), _now(), BaseModel, Row, StrEnum (+19 more)

### Community 34 - "test_retrieval.py"
Cohesion: 0.12
Nodes (32): FactSource, Who asserted this. Decides whether a pin can block it., anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice., `_build_context` runs once per attempt inside the failover loop, so without… (+24 more)

### Community 35 - "Tier"
Cohesion: 0.06
Nodes (39): EscalateFn, PreviewFn, RefuseFn, Holds the pieces the content search needs. A module-level holder rather than…, _Semantic, Bus, Denied, Journal (+31 more)

### Community 36 - "WakeMode"
Cohesion: 0.07
Nodes (22): ListenerState, StrEnum, Where she is in a conversation. ``WAITING`` and ``CAPTURING`` are the whole…, How an utterance is decided to be for her. ``PHRASE`` gates on the transcript:…, WakeMode, Endpoint, Accumulates frames and decides when the speaker has finished. Deliberately not…, Why capture stopped, so the caller can tell an utterance from a timeout. (+14 more)

### Community 37 - "listener.py"
Cohesion: 0.06
Nodes (38): clips(), main(), ndarray, Can she hear her own name? Across many voices, because one is not a test.…, score(), is_stop_word(), _near_the_name(), Hands-free listening (BUILD_SPEC §9 Phase 2 stage 3). The renderer opens the… (+30 more)

### Community 38 - "Listener"
Cohesion: 0.09
Nodes (19): Listener, ndarray, Owns the always-on audio path. One instance per process., Told by the renderer when audio starts and stops coming out. Transitions only,…, What to say to get her attention, in the words a person would use., Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as… (+11 more)

### Community 39 - "test_db.py"
Cohesion: 0.07
Nodes (41): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, Run ``fn`` against the connection off the event loop, serialised., Every table in the database, including vec0 virtual tables. (+33 more)

### Community 40 - "AdoptionService"
Cohesion: 0.13
Nodes (12): AdoptionService, Any, date, datetime, ModelInfo, Works through free candidates, a few probes at a time, and decides. Injected…, Put previously adopted models back into the routing pool. Called at startup.…, One pass. Never raises — a scheduler that dies stops everything. (+4 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "test_reflection.py"
Cohesion: 0.05
Nodes (49): build_prompt(), choose_model(), _extract_json(), Any, datetime, ModelInfo, §8.3's prompt, with the two slots filled., §8.3: cloud if a key is present, local otherwise. Walks SMART then BALANCED,… (+41 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "ToolContext"
Cohesion: 0.05
Nodes (80): test_system_info_reports_this_machine(), tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, The clipboard's text, or None when it holds something else. An image, a file…, Replace the clipboard's contents. Public for the same reason as `read_text`…, Read the clipboard's text., read_clipboard() (+72 more)

### Community 45 - "conversation.py"
Cohesion: 0.04
Nodes (61): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through…, Told to the model, not just logged — it should know why it stopped. (+53 more)

### Community 46 - "browser.py"
Cohesion: 0.13
Nodes (26): Page, test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), browser_click(), browser_fill(), browser_navigate(), browser_read(), browser_screenshot() (+18 more)

### Community 47 - "extract.py"
Cohesion: 0.10
Nodes (26): _extract_bytes(), extract_text(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as… (+18 more)

### Community 48 - "TextToSpeech"
Cohesion: 0.20
Nodes (5): Protocol, What `core/conversation.py` depends on, so it never imports onnxruntime. Same…, False until warmed. The turn loop stays silent rather than blocking., int16 PCM and its sample rate. `speed` overrides the instance default for this…, TextToSpeech

### Community 49 - "Retriever"
Cohesion: 0.13
Nodes (11): Task, What one turn recalled, plus what it cost., Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache. (+3 more)

### Community 50 - "eval_quality.py"
Cohesion: 0.09
Nodes (37): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+29 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "ProviderUnavailable"
Cohesion: 0.09
Nodes (18): HTTPError, ProviderUnavailable, Any, Common `[{role, content}]` shape most chat APIs accept. Tool fields are only…, The backend could not be reached — offline, not running, DNS, refused. Distinct…, to_wire(), OllamaProvider, Any (+10 more)

### Community 53 - "FakeProvider"
Cohesion: 0.07
Nodes (45): FakeProvider, make_service(), _proactivity_service(), anyio, Connection, fixture, MonkeyPatch, A proactive message needs somewhere to live even before the user has ever said… (+37 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "SpeechStream"
Cohesion: 0.16
Nodes (9): ToolCall, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Phase 8 voice polish's affect-driven nudge to `KokoroTTS.synthesize`. Same…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, SpeechStream, Voice is additive. No engine must not mean no reply. (+1 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "test_episodic.py"
Cohesion: 0.10
Nodes (39): _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, _conversation(), _episodic(), anyio, Connection, fixture, Closing a conversation into an episode, and the foreign key that bites. The… (+31 more)

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
Nodes (68): BaseSettings, FastAPI, get, _default_data_dir(), Path, Sidecar configuration. Single source of truth for paths, port, and auth token.…, Speech model weights. Gitignored with the rest of `data/`, and large enough…, Manifests for batch operations (§11: "undo manifests for every one"). A batch… (+60 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "FakeLocator"
Cohesion: 0.09
Nodes (12): Locator, FakeLocator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, Refusing to act on an ambiguous-but-real description is worse than picking the…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught() (+4 more)

### Community 64 - "OpenRouterProvider"
Cohesion: 0.12
Nodes (11): _as_int(), OpenRouterProvider, Any, Headers, RateLimitState, OpenAI's wire format, someone else's models. Subclassing rather than copying is…, Turn reasoning off where the endpoint allows it, and count the call. This is…, Reachability, and a free chance to read the quota headers. (+3 more)

### Community 65 - "test_browser.py"
Cohesion: 0.14
Nodes (30): FakePage, MonkeyPatch, Browser control: the checkout/banking hard block, password refusal, and element…, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, Implements exactly the `Page` surface `browser.py` calls., _returning() (+22 more)

### Community 66 - "Indexer"
Cohesion: 0.19
Nodes (9): _digest(), Indexer, IndexStats, Path, Cheap identity: re-reading a 10MB PDF to decide whether to re-read it would…, Walks, reads, embeds and stores — slowly, and out of the way., Hold here while the machine is busy or she is answering., One pass over everything, at the throttled rate. (+1 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "test_context.py"
Cohesion: 0.15
Nodes (29): machine_context(), MachineContext, Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,…, Content that changes per turn. Everything after this point re-prefills. Phase…, volatile_prefix(), full(), Machine context: the clock, the model, and what it costs to carry them. (+21 more)

### Community 69 - "test_browser_setup.py"
Cohesion: 0.18
Nodes (17): browser_setup(), _cdp_reachable(), _default_browser(), (exe path, profile dir) for the user's actual default browser., Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), MonkeyPatch (+9 more)

### Community 70 - "retrieved_block"
Cohesion: 0.17
Nodes (12): Render remembered facts and episodes into one system message. Returns None when…, _render_memory(), retrieved_block(), A turn about something she has no memory of must leave the prompt byte-…, A fact is a standing truth; an episode is one conversation., A clipped fact beats silence — the cap is a prefill guard, not a correctness…, Uncounted, a roll-up could 'succeed' and still overflow the context — the same…, test_episodes_are_dropped_before_facts() (+4 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "gate_latency.py"
Cohesion: 0.10
Nodes (14): main(), measure(), missing_words(), normalise(), ndarray, Where the time goes between you stopping and her starting. python…, Words that actually went missing, ignoring differences nothing downstream cares…, ndarray (+6 more)

### Community 73 - "test_research.py"
Cohesion: 0.07
Nodes (45): RuntimeError, Readable text from a page, truncated on a word boundary., Fetch and strip anything that arrived without text. Concurrently, and failures…, No usable search key, or the provider refused. Carries the fix., One result, and whatever text could be got out of it., The best text available, preferring the fetched page., SearchUnavailable, Source (+37 more)

### Community 74 - "registry.py"
Cohesion: 0.11
Nodes (18): It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, It is a strong constraint — it overrides the router — so it should be…, test_a_wrapped_argument_description_survives_the_line_break(), test_no_registered_tool_documents_an_argument_it_then_truncates(), test_nothing_else_claims_local_only(), all_tools(), _arg_docs(), build_parameters() (+10 more)

### Community 75 - "CredentialKey"
Cohesion: 0.08
Nodes (21): AsyncClient, HTMLParser, all_status(), CredentialKey, CredentialStatus, get_key(), BaseModel, StrEnum (+13 more)

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
Cohesion: 0.06
Nodes (37): Chooses a model for a turn., Router, _cloud_model(), ModelInfo, The line that was missing. Without it these went to the FAST class., Even in the latency-first bias. Fast and wrong is not the trade., The control. Widening the detector must not make everything SMART., §10 budgets ~1000ms end to end; a network hop does not fit in it. (+29 more)

### Community 80 - "test_adoption.py"
Cohesion: 0.11
Nodes (47): a_model(), Asker, Clock, perfect_reply(), Any, ModelInfo, Measuring a free model, and the line it has to cross to be routed to.…, A scripted model, and a count of what it cost to ask it. (+39 more)

### Community 81 - "GeminiProvider"
Cohesion: 0.16
Nodes (9): _function_call_part(), GeminiProvider, Any, Response, ToolCall, Split system messages out; map assistant -> model. **Tool turns are not text.**…, Replay a tool call in the shape Gemini demands back. The signature is not…, Implements `LLMProvider` against the Gemini generateContent API. (+1 more)

### Community 82 - "discovery.py"
Cohesion: 0.17
Nodes (19): discover_all(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch(), _gemini_class(), _gemini_is_chat(), _gemini_is_duplicate() (+11 more)

### Community 83 - "test_finder.py"
Cohesion: 0.15
Nodes (18): f(), Finding files by name: the ranking, and the words people wrap around it. The…, §7.2 sends `summary` back into the context and keeps `data`/`display` out of…, if I say open cv … fetch the latest cv" — this is that, with an old draft and a…, budget_2026 is newer than every CV, and must not answer "cv"., Recency is a tiebreaker, never the whole answer., Opening the wrong document is worse than opening none., test_a_search_summary_names_the_full_path() (+10 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "ModelInfo"
Cohesion: 0.08
Nodes (37): adopted(), all_models(), by_class(), discovered(), get(), local_models(), ModelInfo, ModelListing (+29 more)

### Community 86 - "organize.py"
Cohesion: 0.19
Nodes (16): _apply(), _bucket(), _key(), Move, Plan, Path, Tidying a folder, reversibly (§9 Phase 4c, §11). The last unbuilt item of Phase…, Whether this entry is not ours to move. (+8 more)

### Community 87 - "files_rename"
Cohesion: 0.20
Nodes (12): files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, Show it in Explorer. The escape hatch for anything this panel does not do., Rename in place, from a click in the panel. Reuses `tools/files.py`'s own…, **To the Recycle Bin, not gone.** This is the one place in the codebase that… (+4 more)

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

### Community 92 - "OllamaSupervisor"
Cohesion: 0.14
Nodes (10): find_ollama(), OllamaSupervisor, Path, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was…, The `ollama` executable, or None if it is not installed. PATH first, because… (+2 more)

### Community 93 - "overhead_tokens"
Cohesion: 0.17
Nodes (15): estimate_tokens(), fit_to_budget(), overhead_tokens(), Tokens spent before the conversation even starts. Roll-up decisions must…, Drop oldest turns until the assembled prompt fits. Backstop, not policy.…, CLAUDE.md: keep the pre-conversation budget near 800 tokens **on local**. It…, Roll-up decisions subtract this; if it were uncounted, a conversation could…, It used to omit them, so it trimmed against a budget ~1650 tokens too generous.… (+7 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): autoprefixer, electron, devDependencies, autoprefixer, electron, postcss, react, react-dom (+5 more)

### Community 96 - "context.py"
Cohesion: 0.07
Nodes (31): clean_title(), ConversationMode, episode_request(), _mode_block(), mode_done_when(), mode_label(), _persona(), datetime (+23 more)

### Community 97 - "state.py"
Cohesion: 0.05
Nodes (34): ModelAvailability, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, What the router decided, and what the user made of it (§9.7). §9.7's closing…, Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, AvailabilityService, ModelInfo (+26 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "WakeWord"
Cohesion: 0.09
Nodes (14): main(), Download the wake word weights into data/models/openwakeword. python…, missing_models(), ndarray, Path, Protocol, RuntimeError, Wake word — openWakeWord on CPU (BUILD_SPEC §9 Phase 2 stage 3). CPU only (rule… (+6 more)

### Community 101 - "invalidate_scan"
Cohesion: 0.21
Nodes (14): _counting_scan(), MonkeyPatch, Path, Make `find_files` deterministic and count how often it really walks., The reason the cache exists at all — two questions in a row must not walk three…, The bug, end to end: write a file, and the next search must not be answered…, Invalidation happens after the filesystem actually changed, never on the way in…, test_a_refused_write_does_not_throw_away_a_good_scan() (+6 more)

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
Cohesion: 0.14
Nodes (10): ModelInfo, Which model gets to see the tool's result. `router._PRIVATE` already keeps a…, Record the decision for §9.7's labelled dataset. Off the turn path. Spawned…, Deliver a message with no preceding question. Called by…, Collect what `send()` started. None when memory is off or it failed. Retrieval…, Any, Task, Fire-and-forget work that must not take the process down with it. Two rules,… (+2 more)

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "FakeTTS"
Cohesion: 0.15
Nodes (9): FakeTTS, Records what it was asked to say, without loading onnxruntime., Synthesis is dispatched per fragment, so a short chunk can finish before a…, Every pre-Phase-8 call site omits `speed` — the engine's own instance default…, Direct against `KokoroTTS`, not `FakeTTS` — proves the override reaches…, test_chunks_carry_an_index_so_playback_can_order_them(), test_kokoro_synthesize_uses_the_override_when_given(), test_speech_stream_defaults_to_no_speed_override() (+1 more)

### Community 109 - "EpisodicMemory"
Cohesion: 0.07
Nodes (23): _build_memory(), Facts, episodes and retrieval, as one handle for the conversation., _clamp_summary(), Episode, EpisodicMemory, _now(), BaseModel, datetime (+15 more)

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

### Community 120 - "SpeechUnavailable"
Cohesion: 0.17
Nodes (11): ndarray, RuntimeError, float32 [-1, 1] -> little-endian int16, which is what WebAudio wants and half…, One chunk of speech as int16 PCM. Runs in a thread — onnxruntime is blocking,…, Voice could not start. Never fatal — she still types., SpeechUnavailable, to_pcm16(), Wrapping turns a loud sample into a click at the opposite polarity. (+3 more)

### Community 121 - "._prune"
Cohesion: 0.33
Nodes (4): datetime, Drop the audit trail once it is old enough to be history. `prune` above…, §8.3: drop weak, single-sighting, unpinned facts after 30 days., Drop adoptions for models OpenRouter no longer lists. Free models are retired,…

### Community 122 - "SettingsPanel.tsx"
Cohesion: 0.25
Nodes (7): BrowserState, KEY_HELP, KEY_LABEL, OnlineState, RowProps, SEARCH_KEYS, SettingsPanel()

### Community 123 - "preload.ts"
Cohesion: 0.25
Nodes (6): api, AriaApi, BrainStatus, LogLine, SidecarEvent, Unsubscribe

### Community 124 - "Client"
Cohesion: 0.07
Nodes (34): main(), _ok(), §9 Phase 6's agent loop, against the running sidecar. "find <scratch file>,…, main(), _ok(), §9 Phase 7's browser half, against a real, CDP-attached Chrome. "open…, main(), _ok() (+26 more)

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

### Community 133 - "handlers.py"
Cohesion: 0.11
Nodes (31): delete_key(), Store a key. Callers must never log `value`., set_key(), build_health(), dispatch(), HealthReport, _invoke(), method_names() (+23 more)

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

### Community 139 - "_Cache"
Cohesion: 0.22
Nodes (7): parametrize, A guard against the next one being added without it. Reads (`read_file`,…, test_every_mutating_file_tool_invalidates_the_scan(), test_filler_words_are_dropped(), test_reads_do_not_invalidate_the_scan(), _Cache, The fallback scan, kept for a short while. Walking three directory trees per…

### Community 141 - "probes.py"
Cohesion: 0.07
Nodes (44): Check, Answered something that has no answer, or claimed an action it cannot perform.…, admits_ignorance(), answers_flatly(), claimed_action(), contains(), contains_any(), denies_capability() (+36 more)

### Community 142 - "tts.py"
Cohesion: 0.25
Nodes (7): Speech synthesis — kokoro-onnx on CPU (BUILD_SPEC §9 Phase 2). CPU only, per…, Take one speakable chunk off the front. Returns (chunk, remainder). `chunk` is…, Load and warm. The first synthesis is ~5x slower than the rest, and the user…, split_for_speech(), _split_for_speech_raw(), test_blank_input_yields_nothing(), test_nothing_is_emitted_mid_sentence()

### Community 143 - "ChatMessage"
Cohesion: 0.04
Nodes (73): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+65 more)

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

### Community 159 - "._insert"
Cohesion: 0.29
Nodes (4): _now(), Return an existing session id, or create one., Write the fact and its vector in one transaction. One transaction is not…, Any

### Community 160 - "ModelVerdict"
Cohesion: 0.29
Nodes (5): ModelVerdict, BaseModel, Per-model tallies. The dataset §9.7 wants, as far as it has grown., How a model has actually been received, per `routing_log`., Liked as a fraction of rated, or None while it would be noise.

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
Cohesion: 0.05
Nodes (48): _openrouter_class(), _openrouter_expired(), parse_openrouter(), date, Free models come and go, and OpenRouter says when. An expired id 404s mid-turn,…, Prefer the number; fall back to what the vendor called it. The other two…, Free, tool-capable chat models from a `GET /api/v1/models` body. **Tool-capable…, payload() (+40 more)

### Community 209 - "clear_adopted"
Cohesion: 0.11
Nodes (21): adopt(), clear_adopted(), Record a model as measured-and-passed, making it routable. Curated ids still…, Tests only. The overlay is process-global, like `_DISCOVERED`., _clean_overlay(), fixture, adopted(), discovered() (+13 more)

### Community 210 - "persona_for"
Cohesion: 0.40
Nodes (5): persona_for(), Persona level for a model; unknown ids get the safe, minimal prompt., Nothing is known about how it behaves, so it gets the safe prompt., test_persona_for_a_discovered_model_is_minimal(), test_persona_for_unknown_model_is_the_safe_minimal_prompt()

### Community 211 - "Any"
Cohesion: 0.40
Nodes (5): _openrouter_benchmark(), _openrouter_is_free(), Any, Free on **both** sides of the meter. `pricing.prompt == "0"` alone would admit…, Artificial Analysis' published intelligence index, if OpenRouter has one. A…

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.33
Nodes (4): DURATION, EASE, SPRING, TWEEN

### Community 215 - "clean_query"
Cohesion: 0.50
Nodes (4): Stripping everything would search for the empty string, which matches the…, test_a_query_of_only_filler_keeps_something_to_match_on(), clean_query(), Drop the words that do not name anything. Everything left is what the file is…

### Community 241 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 244 - "PersonaLevel"
Cohesion: 0.11
Nodes (28): assemble(), PersonaLevel, StrEnum, Content identical across turns. Everything here is KV-cached. Changing `level`…, How much character a model can carry without falling apart. Measured on…, Build the final message list, stable content first., stable_prefix(), ConversationMode (+20 more)

### Community 245 - "score"
Cohesion: 0.50
Nodes (4): _closest_ratio(), How well `candidate` answers `query`, 0..1, over normalised text. The bands are…, Best similarity between `query` and any contiguous run of `tokens`., score()

### Community 248 - "AdoptionState"
Cohesion: 0.18
Nodes (9): AdoptionState, BaseModel, Everything the scheduler needs to resume, and nothing else., What happened to one candidate, and why — kept whatever the answer. A rejection…, Verdict, datetime, An audit trail that cannot say what the model actually said is worth much less…, test_a_verdict_records_why_not_just_what() (+1 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

## Knowledge Gaps
- **330 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+325 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **73 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `test_attachments.py`, `test_tts.py`, `Database`, `ChatMessage`, `Event`, `test_modes.py`, `ConversationStore`, `HealthTracker`, `soak_conversation.py`, `test_conversation.py`, `RoutingLog`, `ModelClass`, `Tier`, `WakeMode`, `listener.py`, `Listener`, `ToolContext`, `conversation.py`, `TextToSpeech`, `Retriever`, `ProviderUnavailable`, `FakeProvider`, `SpeechStream`, `main.py`, `Router`, `._free_vram_for`, `ModelInfo`, `context.py`, `state.py`, `spawn`, `FakeTTS`, `Client`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `ConversationService`, `test_tts.py`, `test_proactivity.py`, `finder.py`, `ChatMessage`, `indexer.py`, `Event`, `ConversationStore`, `OllamaEmbeddings`, `SemanticMemory`, `soak_conversation.py`, `test_conversation.py`, `RoutingLog`, `ModelVerdict`, `semantic.py`, `test_retrieval.py`, `test_db.py`, `test_reflection.py`, `conversation.py`, `FakeProvider`, `SpeechStream`, `test_episodic.py`, `main.py`, `Indexer`, `test_affect.py`, `affect.py`, `context.py`, `state.py`, `FakeTTS`, `EpisodicMemory`, `AffectState`, `_repeated_failures`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `ConversationService`, `_Cache`, `apps.py`, `finder.py`, `test_tools.py`, `test_screen.py`, `test_organize.py`, `Tier`, `conversation.py`, `browser.py`, `SpeechStream`, `FakeLocator`, `test_browser.py`, `test_research.py`, `registry.py`, `test_finder.py`, `organize.py`, `_suppress_close_errors`, `invalidate_scan`, `BrowserUnavailable`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._