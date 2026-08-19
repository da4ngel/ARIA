# Graph Report - ARIA  (2026-08-19)

## Corpus Check
- 231 files · ~326,731 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4817 nodes · 10988 edges · 258 communities (192 shown, 66 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 972 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `447b8b42`
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
- discovery.py
- state.py
- AvailabilityService
- finder.py
- MonkeyPatch
- Indexer
- Listener
- read_one
- ConversationStore
- OllamaEmbeddings
- HealthTracker
- SemanticMemory
- test_screen.py
- main.py
- test_ollama_supervisor.py
- test_router.py
- test_extract.py
- handlers.py
- type_text
- RoutingLog
- Tier
- Router
- Fact
- test_retrieval.py
- registry.py
- best
- strip_wake_word
- ._transcribe_and_send
- db.py
- OpenEngine
- test_focus.py
- Reflector
- ARIA — Project Instructions
- ToolContext
- browser.py
- apps.py
- extract.py
- conversation.py
- Retriever
- PersonaLevel
- test_text.py
- GenerationOptions
- FakeProvider
- compilerOptions
- ProactivityScheduler
- Connectivity
- test_episodic.py
- _escalate_current_page
- Tool contract — decorator, ToolResult, derived schemas
- ARIA Sidecar Runtime Dependencies (requirements.txt)
- Result
- compilerOptions
- Role
- test_browser.py
- FakeLocator
- _parse_episode
- test_vectors.py
- test_an_unrelated_reply_falls_through_to_a_normal_turn
- browser_setup
- test_context.py
- test_affect.py
- Utterance
- test_research.py
- WebSearch
- to_text
- bridge.d.ts
- Electron main + Python sidecar architecture
- affect.py
- soak_conversation.py
- test_adoption.py
- search.py
- AppEntry
- CredentialKey
- FilesPanel.tsx
- render
- _reset_connection
- MemoryServices
- OpenAIProvider
- _suppress_close_errors
- Sidebar.tsx
- sidecar/tools/browser.py — CDP browser tools
- Source
- test_tools.py
- Query: missing parts, flaws, and high-value intelligence improvements
- devDependencies
- ChatMessage
- SettingsStore
- PermissionEngine
- missing_models
- FilesPanel.test.tsx
- BrowserUnavailable
- ConfirmDialog.tsx
- useConversation.ts
- package.json
- test_reflection.py
- HealthReport
- render
- snapshot
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
- files_browse
- .prune
- SettingsPanel.tsx
- preload.ts
- gate_organize.py
- make_tray_icons.py
- PermissionModeChip.tsx
- _repeated_failures
- ToolsPanel.tsx
- Phase 8 — moods, procedural learning, proactivity, voice polish
- Query: QA assessment against BUILD_SPEC
- Phase 2 stage 3 — hands free (wake word, VAD, endpointing)
- protocol.py
- MemoryPanel.test.tsx
- Orb.tsx
- scripts
- core/router.py — model Router
- test_the_warm_voice_carries_no_emoji_or_filler_opener
- gate_research.py
- probes.py
- test_openrouter.py
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
- OpenRouterProvider
- typescript
- vite
- @vitejs/plugin-react
- vitest
- sidecar/__init__.py
- persona/__init__.py
- test_both_levels_still_forbid_inventing_a_memory
- test_no_placeholder_survives_in_any_resolved_prompt
- ModelInfo
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
- stable_prefix
- tokens.js
- parametrize
- clipboard.py
- test_conversation.py
- .reset
- tools_trust_all_drives
- _Semantic
- eval/__init__.py
- test_read_is_named_as_an_untrusted_source
- test_the_prompt_never_claims_she_remembers_nothing
- test_she_is_pointed_at_type_text_for_a_native_app
- test_she_is_told_to_use_relative_paths_not_a_guessed_account_name

## God Nodes (most connected - your core abstractions)
1. `Database` - 260 edges
2. `ConversationStore` - 164 edges
3. `ConversationService` - 108 edges
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

## Communities (258 total, 66 thin omitted)

### Community 0 - "test_permissions.py"
Cohesion: 0.05
Nodes (106): Collection, engine(), Any, fixture, Path, The tier engine, tested on what it refuses. BUILD_SPEC §9 Phase 3 names this…, The property §9 Phase 3 names., **Never default to approved on timeout** (§7.1). Somebody who walked away has… (+98 more)

### Community 1 - "test_listener.py"
Cohesion: 0.04
Nodes (83): Endpoint, Why capture stopped, so the caller can tell an utterance from a timeout., build(), drain(), _drain_windows(), FakeConversation, frame(), interrupt() (+75 more)

### Community 2 - "main.ts"
Cohesion: 0.05
Nodes (38): animateBounds(), bottomRightPosition(), centredExpandedBounds(), createWindow(), fadeTo(), hideWindow(), launchedAt, publishStatus() (+30 more)

### Community 3 - "test_catalog.py"
Cohesion: 0.06
Nodes (43): default_local(), persona_for(), The local fallback. Prefers the instruction-tuned 7B. `pulled` is what Ollama…, Persona level for a model; unknown ids get the safe, minimal prompt., Every catalog entry with a live verdict and a reason fit to display., The ids the router is allowed to choose from., resolve_availability(), usable_ids() (+35 more)

### Community 4 - "test_rpc.py"
Cohesion: 0.11
Nodes (37): _port_is_free(), Whether we can actually have the port, checked before anything else. **A second…, method_names(), _auth(), _call(), client(), fixture, MonkeyPatch (+29 more)

### Community 5 - "ConversationService"
Cohesion: 0.03
Nodes (47): main(), _ok(), Permission modes (manual / auto / full_access), against the real sidecar.…, SessionSummary, ConversationService, Any, ConversationMode, ModelInfo (+39 more)

### Community 6 - "test_attachments.py"
Cohesion: 0.12
Nodes (25): MonkeyPatch, Path, Files the user hands her. Eyaas: *"i should be also be able to file uploads…, There is no local vision model (rule 2), so no key is a real state with an…, `Image.open` on a file that is not one raises. One bad attachment must not take…, §11: content read from files is **data, never instructions**. That a human…, An empty fence would spend prompt tokens saying nothing, and tell the model a…, Nothing was understood, so there is nothing worth recalling — and a memory… (+17 more)

### Community 7 - "test_tts.py"
Cohesion: 0.04
Nodes (64): ToolCall, Turns a token stream into audio while it is still arriving. BUILD_SPEC §9 Phase…, Emit every chunk the buffer can currently yield., Speak whatever is left, then wait for the synthesisers to land., Stream one model's reply into `collected`. Returns TTFT in ms. `tool_calls`…, SpeechStream, ndarray, RuntimeError (+56 more)

### Community 8 - "Database"
Cohesion: 0.07
Nodes (56): Database, Async-safe wrapper around the single sqlite connection., confirm(), context_hint(), detect(), DetectedSequence, discard(), pending_offers() (+48 more)

### Community 9 - "test_scheduler.py"
Cohesion: 0.09
Nodes (43): MemoryScheduler, most_recent_boundary(), datetime, ReflectionReport, timedelta, The clock behind memory: idle sweeps, and reflection at 3am (§8.3). §8.3 names…, Two reasons to reflect: the night has turned, or a conversation has. The…, The last time the clock passed `hour`:00, today or yesterday. (+35 more)

### Community 10 - "test_proactivity.py"
Cohesion: 0.10
Nodes (47): Candidate, default_candidates(), default_self_check(), idle_intention_candidate(), is_stated_intention(), procedure_offer_candidate(), Unprompted messages — rate-limited, focus-aware, self-checked (BUILD_SPEC §9…, The most concrete, lowest-noise-risk trigger, and checked first for that… (+39 more)

### Community 11 - "discovery.py"
Cohesion: 0.07
Nodes (55): discover_all(), discover_gemini(), discover_openai(), discover_openrouter(), _fetch(), _gemini_class(), _gemini_is_chat(), _gemini_is_duplicate() (+47 more)

### Community 12 - "state.py"
Cohesion: 0.05
Nodes (39): main(), measure(), missing_words(), normalise(), ndarray, Where the time goes between you stopping and her starting. python…, Words that actually went missing, ignoring differences nothing downstream cares…, clips() (+31 more)

### Community 13 - "AvailabilityService"
Cohesion: 0.12
Nodes (13): ModelAvailability, AvailabilityService, Which models are usable right now. One object answers this for both…, Every catalog model with a verdict and a displayable reason., The ids the router may choose from., Live view of what can actually answer a turn., What Ollama has pulled. Discovered at startup, refreshed on demand., Re-read the Credential Manager. Call after any key change. (+5 more)

### Community 14 - "finder.py"
Cohesion: 0.05
Nodes (69): Nearest chunks to `query`, as (path, text, distance)., search_chunks(), _counting_scan(), f(), MonkeyPatch, parametrize, Path, Finding files by name: the ranking, and the words people wrap around it. The… (+61 more)

### Community 15 - "MonkeyPatch"
Cohesion: 0.06
Nodes (46): _focused(), MonkeyPatch, A claim is for one call. Left behind, it would answer for a later, unrelated…, `_preview` runs inside `_ask`, *after* its "always allow" early return, and…, 32 seconds of keystrokes is what made the incident possible at all. One Ctrl+V…, Below the threshold, nothing touches the clipboard — it belongs to the user,…, `read_text()` returns None when the clipboard held an image or a file list.…, The last gate. Between the claim and the send sit the dialog and… (+38 more)

### Community 16 - "Indexer"
Cohesion: 0.08
Nodes (33): chunk(), _digest(), Indexer, IndexStats, _pack(), Path, The background file indexer (BUILD_SPEC §9 Phase 4b). Reads documents, chunks…, Whether this file is worth reading at all. (+25 more)

### Community 17 - "Listener"
Cohesion: 0.04
Nodes (62): Case, Bus, Conv, main(), ndarray, Can she hold a conversation? Measured, not assumed. python…, Talk over her and see what happens. This is the part that was unreachable: the…, Speak, then go quiet long enough to end the utterance. (+54 more)

### Community 18 - "read_one"
Cohesion: 0.14
Nodes (22): Attachment, classify(), Path, Files the user hands her, understood and kept. Eyaas: *"I should be also be…, Downscale and re-encode, because `describe_image` hardcodes `data:image/jpeg`.…, Text out of a document, or a reason the user can act on. **`extract_or_raise`,…, Images need a model, and there is no local one (rule 2). So an image with no…, One attachment, understood. Never raises. (+14 more)

### Community 19 - "ConversationStore"
Cohesion: 0.06
Nodes (47): The message store, for callers that need to resolve a session id., ConversationStore, _now(), Sessions and messages — the durable conversation (BUILD_SPEC §7.3). This is…, CRUD over `sessions` and `messages`., Return an existing session id, or create one., Most recently started session, for reload-on-launch., How many proactive messages have gone out, this recently — the rate limiter's… (+39 more)

### Community 20 - "OllamaEmbeddings"
Cohesion: 0.08
Nodes (30): Episode, BaseModel, Episodes — what happened, compressed and kept (BUILD_SPEC §7.3 tier 2). One…, A row from `episodes`, as the panel and retrieval see it., _age_days(), _percentile(), datetime, Retrieval — putting the right memory in front of the model (§9 Phase 5). **The… (+22 more)

### Community 21 - "HealthTracker"
Cohesion: 0.05
Nodes (43): HealthTracker, ModelHealth, BaseModel, Per-model health and observed latency. Two jobs: 1. **Observed TTFT (EWMA).**…, Observed latency if we have it, else the catalog seed, else pessimistic.…, Rolling health for one model id., In-memory health per model. Rebuilt on restart, which is fine — a fresh process…, fixture (+35 more)

### Community 22 - "SemanticMemory"
Cohesion: 0.07
Nodes (49): Fact CRUD, plus the §8.3 merge. Never raises on a missing embedder., Delete a fact outright. Returns whether it existed., SemanticMemory, memory(), anyio, Connection, fixture, The §8.3 merge rules, one test per branch. The pin test is the important one:… (+41 more)

### Community 23 - "test_screen.py"
Cohesion: 0.10
Nodes (45): _clean_stash(), _fake_capture(), _fake_thumbnail(), Exception, fixture, MonkeyPatch, `capture_screen(question)` — the confirmation preview, the stash, §11. The…, Never raises — losing the thumbnail is far better than losing the confirmation… (+37 more)

### Community 24 - "main.py"
Cohesion: 0.04
Nodes (66): BaseSettings, FastAPI, get, _default_data_dir(), get_settings(), Path, Sidecar configuration. Single source of truth for paths, port, and auth token.…, Speech model weights. Gitignored with the rest of `data/`, and large enough… (+58 more)

### Community 25 - "test_ollama_supervisor.py"
Cohesion: 0.06
Nodes (46): find_ollama(), OllamaSupervisor, Path, Keep Ollama running, and notice when it comes back. Eyaas: *"sometimes when…, Starts Ollama if it is down, and re-arms local models when it returns., Last known state. Never probes, never awaits, never raises., Probe, start Ollama if it is down, and wait for it to answer. Returns whether…, One pass. Never raises — a supervisor that dies takes the thing it was… (+38 more)

### Community 26 - "test_router.py"
Cohesion: 0.08
Nodes (46): is_trivial(), A greeting or acknowledgement — nothing a 4B model can get wrong., is_local(), parametrize, RoutingBias, Routing decisions, asserted over a labelled message set. No network. The router…, The whole point of the setting: same message, different destination., §9.7 stage 7: siblings first, then local as the last resort. (+38 more)

### Community 27 - "test_extract.py"
Cohesion: 0.12
Nodes (32): extract_or_raise(), Same, but an unsupported type raises `Unsupported` with the fix in it. The…, _odt(), _pptx(), parametrize, Path, Getting text out of whatever he hands over. The bug behind this file: Eyaas…, What is in this zip" is a real question with a real answer even when nothing… (+24 more)

### Community 28 - "handlers.py"
Cohesion: 0.05
Nodes (78): build_health(), chat_cancel(), chat_delete(), chat_history(), chat_new(), chat_rename(), chat_send(), chat_sessions() (+70 more)

### Community 29 - "type_text"
Cohesion: 0.10
Nodes (24): §7.2's second failure mode: the model gets one line, the UI gets the lot., test_listing_windows_summarises_rather_than_dumps(), test_type_text_refuses_empty_text(), test_type_text_refuses_when_nothing_has_focus(), _bring_to_front(), close_app(), focus_window(), _is_arias_own_window() (+16 more)

### Community 30 - "RoutingLog"
Cohesion: 0.09
Nodes (26): Attach a thumbs-up or thumbs-down to the turn that message answered. Keyed on…, Un-rate a turn. Pressing the same thumb twice means "never mind"., Every rating in one conversation, so the panel can render them., Per-model tallies. The dataset §9.7 wants, as far as it has grown., Writes and reads `routing_log`. Never raises into the turn path., Write one decision. Returns its id, or None if it could not be., RoutingLog, Connection (+18 more)

### Community 31 - "Tier"
Cohesion: 0.06
Nodes (75): messy(), fixture, MonkeyPatch, Path, Tidying a folder, and putting it back exactly (§9 Phase 4c). The acceptance…, A `.crdownload` is a browser mid-write, and moving it corrupts the download. A…, Otherwise "organise Downloads" twice gives you Documents/Documents., Rule 5 calls overwriting destructive, and silently replacing one invoice.pdf… (+67 more)

### Community 32 - "Router"
Cohesion: 0.10
Nodes (28): is_tool_shaped(), needs_deep_model(), BaseModel, ModelInfo, StrEnum, Smart model selection (BUILD_SPEC §9.7). The router returns a *decision*, never…, A request to act on the machine rather than to talk about something., Reasoning, code, or a multi-step request: the `smart` class earns its cost. (+20 more)

### Community 33 - "Fact"
Cohesion: 0.07
Nodes (23): Fact, FactHit, normalise_triple(), _now(), BaseModel, Row, The form that gets embedded and shown in the prompt., A fact with its retrieval scoring, for the panel and the prompt. (+15 more)

### Community 34 - "test_retrieval.py"
Cohesion: 0.10
Nodes (35): 1.0 today, 0.5 after a month, never quite zero., recency_decay(), anyio, parametrize, Retrieval, and the 80ms budget that shapes it (§9 Phase 5). The mechanisms are…, A fresh install answers every turn with no memory to search., Cancelling it outright would mean paying for the same string twice., `_build_context` runs once per attempt inside the failover loop, so without… (+27 more)

### Community 35 - "registry.py"
Cohesion: 0.05
Nodes (51): EscalateFn, PreviewFn, RefuseFn, Bus, Denied, Journal, paths_in(), Pending (+43 more)

### Community 36 - "best"
Cohesion: 0.11
Nodes (18): 7 zip" matched "7-Zip Help" purely because it is the shorter name., The demotion must not make the entry unreachable., Opening the wrong app is worse than opening nothing., This is what stops "open youtube" launching the YouTube Music app: the website…, `normalise("notepad++")` is `"notepad"`, which scored an exact 1.00 against the…, Asking for "notepad" may well mean Notepad++; the ranking can decide. Asking…, Only `+` and `#` name a different product. The 7-Zip cases depend on everything…, test_a_help_entry_never_beats_the_app() (+10 more)

### Community 37 - "strip_wake_word"
Cohesion: 0.14
Nodes (16): is_stop_word(), _near_the_name(), Is this whole utterance just a request to stop talking?, Is this first word a plausible mishearing of her name? `base.en` on a single…, Remove a leading wake phrase. Leaves the name alone mid-sentence., strip_wake_word(), parametrize, Only a leading phrase is the wake word. The rest is what was said. (+8 more)

### Community 38 - "._transcribe_and_send"
Cohesion: 0.08
Nodes (16): ndarray, Told by the renderer when audio starts and stops coming out. Transitions only,…, Begin accepting frames. The renderer opens the device separately — this only…, Cancel any open listening window. Safe to call repeatedly., Listen without the name for a while, then stop. The timer matters as much as…, One frame of float32 audio at 16kHz from the renderer. Frames are handled one…, Waiting: decide whether this frame starts something worth hearing., Capturing: accumulate until the speaker stops or runs out of time. (+8 more)

### Community 39 - "db.py"
Cohesion: 0.07
Nodes (42): _apply_sql(), connect(), current_version(), migrate(), Connection, Path, SQLite connection, sqlite-vec loading, and the migration runner. One connection…, Run ``fn`` against the connection off the event loop, serialised. (+34 more)

### Community 40 - "OpenEngine"
Cohesion: 0.12
Nodes (37): A model asking for a tool to be run. `id` is the provider's handle for the call…, ToolCall, OpenEngine, ToolCall, §11 escalates the step after *reading* untrusted content. A `research` that was…, Decided with Eyaas (2026-08-18): §11 guards against untrusted content reaching…, The half that did not move, asserted beside the half that did — the narrowing…, Asks for a tool on the first pass, then answers on the second. The two-pass… (+29 more)

### Community 41 - "test_focus.py"
Cohesion: 0.10
Nodes (34): _cleanup_probes(), _clear_other_pending_offers(), _focus_section(), main(), _ok(), _procedure_confirmed(), §9 Phase 8's proactivity-engine acceptance gate. a pending procedure offer ->…, `pending_offers` has no ordering, so a real pattern already detected from… (+26 more)

### Community 42 - "Reflector"
Cohesion: 0.10
Nodes (29): ExtractedEpisode, ExtractedFact, BaseModel, datetime, ModelInfo, Reflection — where "learns on its own" actually lives (BUILD_SPEC §8.3). Once a…, What the model returned, once it survives validation., What one run did. Shown in MemoryPanel and asserted by the gate. (+21 more)

### Community 43 - "ARIA — Project Instructions"
Cohesion: 0.06
Nodes (34): Acrylic was on, and painted over (2026-08-09), Adopting a discovered model costs a measurement (2026-08-09), Also fixed the same day: the browser launcher assumed Chrome, and it was wrong, "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09), ARIA — Project Instructions, browser_click / browser_fill: judging the action, not the tool (2026-08-13), Closed: relevance-based tool selection is NOT worth building (2026-08-09), Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06) (+26 more)

### Community 44 - "ToolContext"
Cohesion: 0.06
Nodes (68): create_folder(), delete_file(), delete_folder(), _GUID, known_folder(), list_folder(), move_file(), open_path() (+60 more)

### Community 45 - "browser.py"
Cohesion: 0.13
Nodes (26): Page, test_locate_finds_a_single_role_match(), test_locate_returns_none_when_nothing_matches(), browser_click(), browser_fill(), browser_navigate(), browser_read(), browser_screenshot() (+18 more)

### Community 46 - "apps.py"
Cohesion: 0.07
Nodes (37): main(), Can she find the app you meant? Resolves only — nothing is launched. python…, A dead end is useless; naming the closest lets the model retry., browser" scored 0.88 against LockDown Browser and won. A category is not a…, test_category_words_are_recognised_before_they_are_matched(), test_normalisation_folds_what_should_not_matter(), test_ranking_offers_the_near_misses(), clear_type_targets() (+29 more)

### Community 47 - "extract.py"
Cohesion: 0.11
Nodes (24): _extract_bytes(), extract_text(), _members(), Exception, Path, Getting text out of whatever the user hands over. Eyaas: *"it should be able to…, This file cannot be read, and the message says what would work., `ppt/slides/slide10.xml` -> 10. **Numeric, not lexical.** Sorting the names as… (+16 more)

### Community 48 - "conversation.py"
Cohesion: 0.05
Nodes (43): call_key(), exhausted_note(), LoopState, Any, The agent loop's pure decision logic (BUILD_SPEC §9 Phase 6). Multi-step tool…, Whether the model should be handed tools on the next pass. False exactly on…, §11: the call immediately after reading untrusted content is forced through…, Told to the model, not just logged — it should know why it stopped. (+35 more)

### Community 49 - "Retriever"
Cohesion: 0.13
Nodes (11): Task, What one turn recalled, plus what it cost., Turns a user message into the memory worth putting in front of the model., Start retrieval now, await it later. Called from `send()` so the embed overlaps…, Facts and episodes worth injecting. Never raises, never over budget., Whether there is anything to search. Cached once it is true. This was two…, Embed within the deadline, or give up and say so. On timeout the embed is…, Keep a strong ref so the timed-out embed still reaches the cache. (+3 more)

### Community 50 - "PersonaLevel"
Cohesion: 0.09
Nodes (34): Namespace, build_messages(), _is_reasoning(), main(), provider_for(), _pulled_models(), ModelInfo, Answer-quality and hallucination battery. Run it, change something, run again.… (+26 more)

### Community 51 - "test_text.py"
Cohesion: 0.11
Nodes (30): content_words(), coverage(), idf(), Word-level matching, shared by retrieval and by episode salience. **This is the…, `runn` -> `run`, but `press` stays `press`., The words in `text` worth matching on, stemmed., How rare each word is across the candidate set. Computed over the rows actually…, How much of the query's meaning this document accounts for, 0..1. IDF-weighted,… (+22 more)

### Community 52 - "GenerationOptions"
Cohesion: 0.05
Nodes (44): HTTPError, GenerationOptions, ProviderRateLimited, ProviderUnavailable, Any, BaseModel, The interface every LLM backend implements. Phase 1 only ships the Ollama…, HTTP 429. Measured on a free-tier Gemini key, so this is a normal routing input… (+36 more)

### Community 53 - "FakeProvider"
Cohesion: 0.08
Nodes (37): chat_mode(), Read or set a conversation's mode. Omit `mode` to read. The read-or-write shape…, FakeProvider, make_service(), fixture, MonkeyPatch, The whole point of writing a `routing_log` row for it: the *existing*…, The whole reason this is per-conversation rather than a setting: a mode chosen… (+29 more)

### Community 54 - "compilerOptions"
Cohesion: 0.07
Nodes (28): DOM, DOM.Iterable, src/**/*.d.ts, src/**/*.ts, src/**/*.tsx, vite/client, compilerOptions, baseUrl (+20 more)

### Community 55 - "ProactivityScheduler"
Cohesion: 0.10
Nodes (23): ProactivityScheduler, datetime, Path, timedelta, One pass. Never raises — a scheduler that dies stops everything, the same…, Names of files under `root` modified inside `window`. Bounded, and never raises…, Notice that a watched folder is being worked in right now. Empty by default:…, Sweeps for something worth saying, at most once per tick, and only when nothing… (+15 more)

### Community 56 - "Connectivity"
Cohesion: 0.12
Nodes (21): Connectivity, Is this machine on the internet? BUILD_SPEC §9.7 asks for "offline detection…, Cached reachability. Reads never block; the refresh is a background task., Last known state. Never probes, never awaits, never raises., _client_raising(), _client_returning(), _FakeResponse, Exception (+13 more)

### Community 57 - "test_episodic.py"
Cohesion: 0.13
Nodes (32): _conversation(), _episodic(), anyio, Connection, fixture, Closing a conversation into an episode, and the foreign key that bites. The…, `ended_at` is the guard as well as the record, so an idle sweep racing a New…, The regression test for the whole bug. Eyaas asked one question about data… (+24 more)

### Community 58 - "_escalate_current_page"
Cohesion: 0.17
Nodes (13): The URL check catches the common case; a card-number field on an unlisted…, No page has loaded yet at this point — only the URL being navigated *to* is…, test_a_generic_domain_can_still_be_caught_by_its_dom(), test_known_checkout_and_banking_urls_are_recognised(), test_navigate_escalates_on_the_target_url_before_loading_it(), test_no_checkout_fields_means_no_dom_match(), _dom_confirms_checkout(), _escalate_current_page() (+5 more)

### Community 59 - "Tool contract — decorator, ToolResult, derived schemas"
Cohesion: 0.07
Nodes (27): Affect model — four floats serialized to ~20 tokens, One batch confirmation, not N, SQLite + sqlite-vec memory schema, Everything (es.exe) instant name search, file_index / file_chunks / file_vec tables, Indexer hard throttle — 20 files/min, pause on load, Known traps table, End-to-end latency budget (~1000ms to first word) (+19 more)

### Community 60 - "ARIA Sidecar Runtime Dependencies (requirements.txt)"
Cohesion: 0.07
Nodes (27): ARIA Sidecar Runtime Dependencies (requirements.txt), anthropic==0.39.* (NOT adopted, Anthropic excluded), apscheduler==3.10.* (deferred, Phase 5), fastapi==0.115.*, faster-whisper==1.0.3, httpx==0.27.*, keyring==25.7.* (Windows Credential Manager), kokoro-onnx==0.4.* (+19 more)

### Community 61 - "Result"
Cohesion: 0.16
Nodes (12): Answered something that has no answer, or claimed an action it cannot perform.…, Declined or hedged a solid fact. The counter-metric — a hallucination fix that…, The individual failures worth a human reading. A rate tells you there is a…, report(), _report_offenders(), Result, claimed_action(), Expect (+4 more)

### Community 62 - "compilerOptions"
Cohesion: 0.08
Nodes (25): electron/**/*.ts, electron.vite.config.ts, electron-vite/node, node, compilerOptions, composite, esModuleInterop, exactOptionalPropertyTypes (+17 more)

### Community 63 - "Role"
Cohesion: 0.21
Nodes (10): MessageHit, BaseModel, Oldest-first turns for a session., Find past turns that mention what `query` is about. **This is the layer that…, A row from `messages`, as the UI and context assembly see it., One past turn that matched a `recall` query., StoredMessage, StrEnum (+2 more)

### Community 64 - "test_browser.py"
Cohesion: 0.14
Nodes (30): FakePage, MonkeyPatch, Browser control: the checkout/banking hard block, password refusal, and element…, The page-level check runs first, and an ordinary-looking "OK" button on a…, The actual point of this whole change: a routine click on an ordinary page…, A target that does not exist is the tool's "not found" to report, not a reason…, Implements exactly the `Page` surface `browser.py` calls., _returning() (+22 more)

### Community 65 - "FakeLocator"
Cohesion: 0.09
Nodes (12): Locator, FakeLocator, An icon-only button ("🛒") can carry the meaning in its label with no visible…, No telltale wording anywhere — only `type="submit"` says what it does. The…, Refusing to act on an ambiguous-but-real description is worse than picking the…, test_a_bare_submit_button_is_caught_structurally(), test_an_ordinary_link_is_not_a_commit_action(), test_commit_wording_in_the_aria_label_alone_is_caught() (+4 more)

### Community 66 - "_parse_episode"
Cohesion: 0.22
Nodes (9): _clamp_summary(), _parse_episode(), Read the summariser's JSON, tolerating a model that wrapped it in prose. A…, max_tokens is a request, not a guarantee, and this is read for months., A dropped episode is a lost conversation; a guessed salience is not., test_a_fenced_json_reply_parses(), test_an_empty_reply_produces_no_episode(), test_plain_prose_is_kept_as_the_summary() (+1 more)

### Community 67 - "test_vectors.py"
Cohesion: 0.11
Nodes (24): cosine(), cosine_from_l2(), normalise(), pack(), Vector arithmetic for the memory tables (Phase 5). **Why this exists next to…, Scale to unit length, so L2 distance carries cosine exactly. A zero vector has…, Raw little-endian float32, which is sqlite-vec's wire format., Recover cosine from the L2 distance between two *unit* vectors. Only valid for… (+16 more)

### Community 68 - "test_an_unrelated_reply_falls_through_to_a_normal_turn"
Cohesion: 0.31
Nodes (8): Connection, A pending offer must never swallow an unrelated message as if it were a decline…, Only the very next `send()` after the offer can resolve it — a second "yes"…, _seed_procedure(), test_a_no_reply_discards_the_pending_offer(), test_a_yes_reply_confirms_the_pending_offer_without_a_model_call(), test_an_unrelated_reply_falls_through_to_a_normal_turn(), test_the_pending_offer_window_is_one_shot()

### Community 69 - "browser_setup"
Cohesion: 0.29
Nodes (8): browser_setup(), _cdp_reachable(), Write the CDP-debug launcher for the user's real browser, and report…, A `.bat`, not a `.lnk` — no COM dependency, and a plain text file the user can…, _write_browser_launcher(), Path, test_a_failed_detection_falls_back_to_a_guess_not_a_crash(), test_the_launcher_names_the_detected_browser_by_full_path()

### Community 70 - "test_context.py"
Cohesion: 0.07
Nodes (65): assemble(), estimate_tokens(), fit_to_budget(), machine_context(), MachineContext, overhead_tokens(), Facts the process already holds. Nothing here is inferred or guessed., What she can say about right now without being told. Rendered **to the minute,… (+57 more)

### Community 71 - "test_affect.py"
Cohesion: 0.16
Nodes (21): speech_speed(), _neutral(), datetime, The affect model (BUILD_SPEC §9 Phase 8). `update()` and `render()` are pure —…, 48 hours is the named threshold — a same-day gap must not be read as "returning…, Banding matters here too — a nudge just off baseline should not already be…, `update()` called with every delta switched off, so a test can turn on exactly…, test_a_casual_turn_raises_playfulness_a_task_shaped_one_lowers_it() (+13 more)

### Community 72 - "Utterance"
Cohesion: 0.11
Nodes (8): ndarray, Protocol, Accumulates frames and decides when the speaker has finished. Deliberately not…, Add a frame. Returns an `Endpoint` when the utterance is over. Trailing silence…, Everything captured, as one float32 array., Speech probability for one 512-sample float32 frame., Utterance, VoiceActivity

### Community 73 - "test_research.py"
Cohesion: 0.16
Nodes (17): MonkeyPatch, `research(query)`, the untrusted-content boundary, and the online gate. Two…, It has a title, a URL and a snippet. Citing it beats pretending the search did…, The whole point of `SearchUnavailable` carrying a message., A model that asks for fifty pages would blow the context budget §8.2 exists to…, Belt to `_tool_schemas`' braces. `allow_danger_tools` was dead for a whole…, Stronger than asking it not to use one: §7.2's own reasoning for hiding DANGER,…, test_a_source_that_would_not_load_is_still_cited() (+9 more)

### Community 74 - "WebSearch"
Cohesion: 0.18
Nodes (9): Any, Response, RuntimeError, Search, then read the results. One client, closed on shutdown., Top results for `query`. Raises `SearchUnavailable` with the fix., Fetch and strip anything that arrived without text. Concurrently, and failures…, No usable search key, or the provider refused. Carries the fix., SearchUnavailable (+1 more)

### Community 75 - "to_text"
Cohesion: 0.12
Nodes (12): AsyncClient, HTMLParser, An epub is a zip of XHTML. Tags are stripped rather than parsed — the same call…, _read_epub(), Readable text from a page, truncated on a word boundary., Strip a page to its readable text. Not readability, not an article extractor,…, _Reader, to_text() (+4 more)

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
Cohesion: 0.21
Nodes (10): concrete_tokens(), main(), novel_tokens(), Any, Long-conversation contamination soak — the Phase 1 regression, restated. The…, Proper nouns and numbers, ignoring words capitalised only by position., Concrete tokens in `reply` that nobody has grounded yet., Collects turn completions without needing a socket. (+2 more)

### Community 80 - "test_adoption.py"
Cohesion: 0.05
Nodes (74): AdoptionService, AdoptionState, Any, BaseModel, date, ModelInfo, Everything the scheduler needs to resume, and nothing else., Works through free candidates, a few probes at a time, and decides. Injected… (+66 more)

### Community 82 - "AppEntry"
Cohesion: 0.09
Nodes (31): main(), Console entrypoint for ``python -m sidecar.main``., _default_browser(), (exe path, profile dir) for the user's actual default browser., MonkeyPatch, `browser.setup`'s launcher detection. The bug this guards against was real, not…, Firefox is a real default browser some people have, and CDP does not work with…, test_a_non_chrome_default_is_detected_and_used() (+23 more)

### Community 83 - "CredentialKey"
Cohesion: 0.20
Nodes (15): all_status(), CredentialKey, CredentialStatus, delete_key(), BaseModel, StrEnum, API keys, stored in Windows Credential Manager (BUILD_SPEC §11). Never `.env`,…, Credential Manager entry names under the ARIA service. (+7 more)

### Community 84 - "FilesPanel.tsx"
Cohesion: 0.47
Nodes (5): Entry, FilesPanel(), humanDate(), humanSize(), Listing

### Community 85 - "render"
Cohesion: 0.25
Nodes (8): A model that has just read 6,000 characters of someone else's writing has…, Returns real, correct URLs" is the acceptance line, and only `summary` reaches…, test_a_source_is_truncated_rather_than_dropped(), test_every_source_carries_its_url(), test_fetched_text_is_fenced_as_untrusted(), test_the_warning_is_repeated_after_the_content(), Sources into the block the model reads. Fenced, cited, truncated., render()

### Community 86 - "_reset_connection"
Cohesion: 0.67
Nodes (3): fixture, `_get_page`/`_connect` are monkeypatched per test; nothing here should carry a…, _reset_connection()

### Community 87 - "MemoryServices"
Cohesion: 0.29
Nodes (7): MemoryServices, Everything Phase 5 hands to the conversation, as one argument.…, anyio, `episodes.session_id` is a foreign key, so the store's delete raises unless the…, Every memory call site is a no-op when `memory` is None — Phase 4's behaviour,…, test_a_turn_without_memory_behaves_exactly_as_before(), test_deleting_a_conversation_clears_its_episodes_first()

### Community 88 - "OpenAIProvider"
Cohesion: 0.10
Nodes (16): get_key(), Read a key, or None if unset. Never logs the value., _assemble(), OpenAIProvider, Any, Response, ToolCall, No-op: cloud models have no local load step to pay for. (+8 more)

### Community 89 - "_suppress_close_errors"
Cohesion: 0.33
Nodes (4): aclose(), Release the CDP connection. For shutdown and for tests., A closed CDP connection raising on its own teardown is not worth a traceback in…, _suppress_close_errors

### Community 90 - "Sidebar.tsx"
Cohesion: 0.13
Nodes (5): Section, SidebarProps, storedCollapsed(), stroke, useSidebar

### Community 91 - "sidecar/tools/browser.py — CDP browser tools"
Cohesion: 0.25
Nodes (8): sidecar/tools/browser.py — CDP browser tools, tool.escalate/refuse received args as one positional dict instead of unpacked kwargs, silently disabling both checks, Phase 7 — a real, logged-in browser (CDP), Online mode — research(query) over search API, Tool.escalate/Tool.refuse hooks: checkout/banking pages force CONFIRM, password fields refused, _default_browser() detects the real default (Brave) via UserChoice registry rather than assuming Chrome, §11 untrusted_content boundary: fetched text is data, labelled and unfiltered, §11 force_confirm: next tool call after research/browser_read is force-escalated to T2

### Community 92 - "Source"
Cohesion: 0.18
Nodes (11): One result, and whatever text could be got out of it., The best text available, preferring the fetched page., Source, online(), Exception, fixture, Stripping is a losing game — there are unlimited phrasings. The content is…, Stands in for the network. Returns whatever it was handed. (+3 more)

### Community 93 - "test_tools.py"
Cohesion: 0.04
Nodes (69): parametrize, Path, The six tools, and mostly the paths where they refuse. `delete_file` is tested…, Overwriting is a different destructive act from moving, and the user approved a…, It did not, and `remember` shipped `...e.g. "I work on Sillara` — cut mid-…, `read_file` did a plain UTF-8 read of whatever it was given, so "what does this…, A scanned PDF with no text layer is a normal thing to be handed. Saying so…, OneDrive relocates Documents and Desktop by default, so joining onto… (+61 more)

### Community 94 - "Query: missing parts, flaws, and high-value intelligence improvements"
Cohesion: 0.18
Nodes (13): sidecar/core/agent.py — agent loop (Phase 6), Degrade-then-immediately-undone loop: post-degrade router reselect walked the entire model catalog, Phase 4 finder / file indexer, gate_agent find→read→answer gate fails: freshly-written file invisible to throttled indexer, File indexer is a one-shot sweep: no watcher, no mutation queue, no deletion reconciliation, Query: missing parts, flaws, and high-value intelligence improvements, Answer, Outcome (+5 more)

### Community 95 - "devDependencies"
Cohesion: 0.15
Nodes (13): autoprefixer, electron, devDependencies, autoprefixer, electron, postcss, react, react-dom (+5 more)

### Community 96 - "ChatMessage"
Cohesion: 0.09
Nodes (30): clean_title(), ConversationMode, episode_request(), _mode_block(), mode_label(), _persona(), datetime, StoredMessage (+22 more)

### Community 97 - "SettingsStore"
Cohesion: 0.09
Nodes (21): Any, Durable key-value settings (BUILD_SPEC §7.1 settings.get / settings.set).…, SettingsStore, ModelInfo, Ask both providers what they offer, then remember the answer. A provider being…, Fill the overlay from cache. Returns whether it is still fresh. A stale cache…, Connection, fixture (+13 more)

### Community 98 - "PermissionEngine"
Cohesion: 0.21
Nodes (12): allow_danger_tools flag was dead code: schemas() always used the CONFIRM ceiling, PermissionEngine, Permission tier system (T0/SAFE .. T3/DANGER), Phase 3 — the tool contract, A confirmation timeout resolves to DENIED (§7.1), DANGER tools are off by default and absent from schemas() entirely, local_only tools (read_clipboard) force the continuation model local, open_app matcher: exact→shared words→prefix→substring→edit distance scoring bands (+4 more)

### Community 99 - "missing_models"
Cohesion: 0.14
Nodes (10): main(), Download the wake word weights into data/models/openwakeword. python…, missing_models(), ndarray, Path, RuntimeError, Score one frame of int16 audio. Returns 0.0 while debounced. Callers must await…, The wake word could not start. Never fatal — typing and push-to-talk both still… (+2 more)

### Community 101 - "BrowserUnavailable"
Cohesion: 0.17
Nodes (11): Browser, Exception, _raising(), `LAUNCH_HINT` was made browser-agnostic when Eyaas's real default turned out to…, test_navigate_reports_browser_unavailable_plainly(), test_no_user_facing_browser_error_names_chrome(), BrowserUnavailable, _connect() (+3 more)

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
Cohesion: 0.08
Nodes (40): build_prompt(), choose_model(), _extract_json(), Any, §8.3's prompt, with the two slots filled., §8.3: cloud if a key is present, local otherwise. Walks SMART then BALANCED,…, Find the JSON object in whatever the model actually returned. A local 7B wraps…, anyio (+32 more)

### Community 106 - "HealthReport"
Cohesion: 0.33
Nodes (6): HealthReport, BaseModel, Rich health snapshot for the UI (§7.1 ``system.health``, §9.6)., Launch, StrEnum, How an entry has to be started. Three sources, three launchers.

### Community 107 - "render"
Cohesion: 0.18
Nodes (11): _band(), ~20 tokens, `machine_context()`'s own style — words, not floats. None when…, render(), A state that has not moved should not cost a token saying so — the same "byte-…, Concern only ever reads as "elevated" — there is no natural English phrase for…, The mechanism half of BUILD_SPEC's own acceptance line — the string fed to the…, test_a_2am_state_and_a_2pm_state_render_differently(), test_baseline_renders_nothing() (+3 more)

### Community 108 - "snapshot"
Cohesion: 0.18
Nodes (11): BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM unconditionally.…, §9:943 says "regardless of tool tier" — that only means something if *every*…, test_every_browser_tool_carries_the_checkout_escalation(), test_only_fill_carries_the_password_refusal(), test_tiers_deviate_from_build_specs_blanket_confirm_by_design(), T1. It reads and changes nothing; the consent that matters is the online…, test_research_needs_no_confirmation(), BUILD_SPEC's own tier table (§9:474) lists this AUTO — that line is about the… (+3 more)

### Community 109 - "EpisodicMemory"
Cohesion: 0.08
Nodes (17): EpisodicMemory, _now(), datetime, Row, StoredMessage, Writes and reads `episodes`. Never raises into the turn path., Summarize every conversation that has gone quiet. Returns how many., Summarize one session into an episode. Idempotent; never raises. `ended_at` is… (+9 more)

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
Cohesion: 0.12
Nodes (17): _cloud_model(), ModelInfo, 300ms of extra latency is a pause. A model that picks the wrong tool produces…, Nothing invents a measurement — the same rule the catalog already keeps for…, The three measured models sit within 0.03 of each other, and the measurement…, The mechanism has to keep working, or banding would just be a way of ignoring…, The gap `_PRIVATE` structurally cannot cover. That regex reads the *words* of…, A paid cloud model is a fine place to send a document. Forcing local would make… (+9 more)

### Community 118 - "ModelPicker.tsx"
Cohesion: 0.24
Nodes (8): BIAS_HINT, BIAS_LABEL, DetailSheet(), PROVIDER_LABEL, PROVIDER_ORDER, Row(), RowProps, speedLabel()

### Community 119 - "memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py"
Cohesion: 0.31
Nodes (9): delete_session broke on episodes FK constraint until forget_session ran first, She forgot a conversation she had just had — six independent causes (2026-08-12), Faster CPU semantic embedding path is the primary intelligence improvement (retrieval degrades to lexical under load), memory/{vectors,semantic,episodic,retrieval,reflection,scheduler}.py, Phase 5 — she remembers (facts, episodes, reflection), Embedding retrieval deadline: falls back to lexical search when over budget, marked degraded, last_reflected_message_id high-water mark replaces wall-clock reflection window, Fact merge key widened to same-subject (predicate wording unreliable from local model) (+1 more)

### Community 120 - "files_browse"
Cohesion: 0.13
Nodes (20): files_browse(), files_delete(), files_rename(), files_reveal(), _invalidate_finder_scan(), Path, One folder's contents, for the panel. Deliberately not `list_folder`: that tool…, Show it in Explorer. The escape hatch for anything this panel does not do. (+12 more)

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

### Community 131 - "Query: QA assessment against BUILD_SPEC"
Cohesion: 0.15
Nodes (13): ARIA (local-first Windows AI assistant), Electron UI (renderer), QA evidence strong through Phase 8; packaging and hardware/live acceptance gates remain incomplete, Query: QA assessment against BUILD_SPEC, Answer, Outcome, Q: QA assessment: how good is the implementation against BUILD_SPEC?, Source Nodes (+5 more)

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

### Community 138 - "test_the_warm_voice_carries_no_emoji_or_filler_opener"
Cohesion: 0.33
Nodes (4): `recall` is a tool, so the instruction to search only makes sense when tools…, `universal_failures` fails *every* probe in *every* category on either of…, test_the_warm_voice_carries_no_emoji_or_filler_opener(), test_with_tools_she_is_told_to_look_before_denying()

### Community 139 - "gate_research.py"
Cohesion: 0.47
Nodes (5): _check(), main(), _ok(), §9 Phase 7's research half, against the running sidecar. "research X and…, Does each cited URL actually exist? The whole point of this gate.

### Community 141 - "probes.py"
Cohesion: 0.07
Nodes (42): Check, admits_ignorance(), answers_flatly(), contains(), contains_any(), denies_capability(), exact(), excludes() (+34 more)

### Community 142 - "test_openrouter.py"
Cohesion: 0.06
Nodes (42): Replace what the providers said they offer. A curated id always wins: `gpt-5`…, set_discovered(), _openrouter_class(), _openrouter_expired(), parse_openrouter(), date, Free models come and go, and OpenRouter says when. An expired id 404s mid-turn,…, Prefer the number; fall back to what the vendor called it. The other two… (+34 more)

### Community 143 - "LLMProvider"
Cohesion: 0.09
Nodes (26): choose_with(), cosine(), main(), measure_choice(), measure_per_model(), measure_recall(), provider_for(), ModelInfo (+18 more)

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

### Community 202 - "OpenRouterProvider"
Cohesion: 0.07
Nodes (23): _as_int(), OpenRouterProvider, Any, Headers, RateLimitState, OpenAI's wire format, someone else's models. Subclassing rather than copying is…, Turn reasoning off where the endpoint allows it, and count the call. This is…, Reachability, and a free chance to read the quota headers. (+15 more)

### Community 212 - "ModelInfo"
Cohesion: 0.07
Nodes (39): adopt(), adopted(), all_models(), clear_adopted(), discovered(), get(), local_models(), ModelInfo (+31 more)

### Community 213 - "useConversationMode.ts"
Cohesion: 0.33
Nodes (5): ConversationMode, MODE_OPTIONS, ModeState, NORMAL, useConversationMode

### Community 214 - "motion.ts"
Cohesion: 0.33
Nodes (4): DURATION, EASE, SPRING, TWEEN

### Community 244 - "stable_prefix"
Cohesion: 0.17
Nodes (16): Content identical across turns. Everything here is KV-cached. Changing `level`…, stable_prefix(), ConversationMode, parametrize, The property that makes modes free for anyone who never uses them. NORMAL…, Resolved once at import, so the same configuration always yields the same bytes…, `_INSTRUCTION_PRIORITY` exists because "reply with only the number 7" once…, `_FULL` says "Short sentences; you are often spoken aloud" — which Study and… (+8 more)

### Community 253 - "tokens.js"
Cohesion: 0.40
Nodes (3): COLORS, HUES, RGB

### Community 255 - "parametrize"
Cohesion: 0.25
Nodes (9): parametrize, test_ordinary_targets_are_not_refused(), test_ordinary_urls_are_not_flagged(), test_password_shaped_targets_are_refused(), test_role_name_strips_the_leading_article_and_trailing_noun(), A hard block, not a dialog — see the module docstring. Reads only the call's…, the Send button" -> "Send" — a role lookup wants the label, not the description…, _refuse_password_field() (+1 more)

### Community 256 - "clipboard.py"
Cohesion: 0.19
Nodes (11): tool, The clipboard (BUILD_SPEC §9 Phase 3). `win32clipboard` ships with pywin32,…, Put text on the clipboard. Args: text: What to copy, The clipboard's text, or None when it holds something else. An image, a file…, Replace the clipboard's contents. Public for the same reason as `read_text`…, Read the clipboard's text., read_clipboard(), read_text() (+3 more)

### Community 258 - "test_conversation.py"
Cohesion: 0.08
Nodes (34): _drain(), _proactivity_service(), parametrize, Path, Turn orchestration, cancellation, persistence and context roll-up., The control. Forcing every continuation local would throw away the cloud model…, A proactive message needs somewhere to live even before the user has ever said…, Wait for all in-flight turns. (+26 more)

### Community 260 - "tools_trust_all_drives"
Cohesion: 0.50
Nodes (4): _enumerate_drives(), Every fixed drive letter Windows reports, as root paths ("C:\\").…, Trust every drive letter on the machine, in one call. The direct answer to…, tools_trust_all_drives()

## Knowledge Gaps
- **329 isolated node(s):** `sidecar`, `rpc`, `launchedAt`, `singleInstance`, `BrainStatus` (+324 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **66 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_conversation.py`, `ConversationService`, `test_tts.py`, `test_proactivity.py`, `state.py`, `finder.py`, `Indexer`, `ConversationStore`, `OllamaEmbeddings`, `SemanticMemory`, `main.py`, `RoutingLog`, `Fact`, `test_retrieval.py`, `db.py`, `OpenEngine`, `Reflector`, `conversation.py`, `FakeProvider`, `ProactivityScheduler`, `test_episodic.py`, `Role`, `test_an_unrelated_reply_falls_through_to_a_normal_turn`, `test_affect.py`, `affect.py`, `soak_conversation.py`, `MemoryServices`, `SettingsStore`, `test_reflection.py`, `EpisodicMemory`, `AffectState`, `_repeated_failures`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `ConversationService` connect `ConversationService` to `test_permissions.py`, `test_conversation.py`, `test_tts.py`, `Database`, `state.py`, `LLMProvider`, `Listener`, `ConversationStore`, `HealthTracker`, `main.py`, `RoutingLog`, `Tier`, `Router`, `registry.py`, `OpenEngine`, `Reflector`, `ToolContext`, `conversation.py`, `Retriever`, `GenerationOptions`, `FakeProvider`, `Role`, `soak_conversation.py`, `ModelInfo`, `MemoryServices`, `ChatMessage`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `ToolContext` connect `ToolContext` to `test_permissions.py`, `clipboard.py`, `ConversationService`, `test_tts.py`, `_Semantic`, `finder.py`, `test_screen.py`, `type_text`, `Tier`, `registry.py`, `browser.py`, `apps.py`, `conversation.py`, `test_browser.py`, `FakeLocator`, `test_research.py`, `search.py`, `AppEntry`, `_suppress_close_errors`, `Source`, `test_tools.py`, `BrowserUnavailable`, `HealthReport`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `Database` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`Database` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `ConversationStore` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`ConversationStore` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `ConversationService` (e.g. with `Recorder` and `LoopState`) actually correct?**
  _`ConversationService` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `HealthTracker` (e.g. with `Recorder` and `ConversationHistory`) actually correct?**
  _`HealthTracker` has 22 INFERRED edges - model-reasoned connections that need verification._