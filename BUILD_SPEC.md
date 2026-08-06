# ARIA — Local Windows AI Assistant
## Master Build Specification for Claude Code

**Target machine:** Windows 11, RTX 4050 Laptop (6GB VRAM), 16GB+ RAM
**Owner:** Eyaas
**Status:** v1.0 build spec — execute phases in order

---

## 0. How to use this document with Claude Code

This spec is written to be executed one phase per session. Do not hand Claude Code the whole document and say "build it." That produces a half-working monolith.

**Workflow per phase:**

```bash
# 1. Start a fresh Claude Code session in the repo root
claude

# 2. Point it at the spec and the phase
> Read BUILD_SPEC.md. Implement Phase 3 only.
> Do not start Phase 4. Stop at the acceptance gate and run the verification commands.
```

**Rules to give Claude Code at the start of every session** (these live in `CLAUDE.md`, see §6 — Claude Code reads that file automatically):

- Implement only the current phase.
- Every phase ends with a working, runnable app. No phase may leave the repo broken.
- Write the tests specified in the acceptance gate *before* declaring the phase done.
- Do not add dependencies not listed in §4 without flagging it first.
- Do not refactor code from earlier phases unless the phase explicitly says to.

**Why phases matter here:** this project has three runtimes (Node, Python, native Windows APIs) and a hard VRAM ceiling. Debugging a 5,000-line first draft across that surface is miserable. Each phase below is independently demoable.

---

## 1. What ARIA is

A local-first desktop assistant that lives in a floating window, listens for a wake word, holds a natural voice conversation, and can actually operate the machine — launch apps, find files semantically, control system state, drive the browser, and remember you across sessions.

**Design north stars, in priority order:**

1. **Latency over intelligence.** A response that starts in 600ms and is 80% as smart beats a 3-second response that's perfect. Presence is the product.
2. **Local by default.** Anything touching personal files, screen contents, or conversation history runs on-device. Cloud is opt-in per-turn and visibly indicated.
3. **Never silently destructive.** Every irreversible action passes a confirmation gate. Every tool call is logged.
4. **Character, not sycophancy.** She has opinions, can disagree, can say a task is a bad idea. An assistant that only validates becomes wallpaper.

**Explicit non-goals for v1:**

- No mobile client, no cloud sync, no multi-user.
- No local vision model (won't fit alongside the 7B — screen understanding routes to cloud).
- No arbitrary code execution as a tool. Tools are a fixed, audited registry.
- No fine-tuning. Personality comes from prompting + memory, not weights.

---

## 2. Hard constraints (design around these, don't fight them)

### 2.1 VRAM: 6GB

| Component | VRAM | Notes |
|---|---|---|
| Qwen2.5 7B Instruct Q4_K_M | ~4.7 GB | Weights only |
| KV cache @ 8K ctx, q8_0 | ~0.6 GB | With flash attention on |
| Windows desktop compositor | ~0.4 GB | Unavoidable |
| **Total** | **~5.7 GB** | **No headroom** |

**Consequences, non-negotiable:**

- Only **one** model on the GPU at a time. The main 7B.
- STT (faster-whisper), embeddings (nomic-embed), wake word, and the router all run on **CPU**. They're fast enough there — see the latency budget in §10.
- `num_ctx` is capped at **8192**. Do not raise it. Longer context is handled by memory retrieval (§7.3), not by a bigger window.
- If the user runs a game or Chrome with heavy GPU tabs, Ollama will spill to CPU and latency triples. Detect this (§9.6) and warn rather than silently degrading.

> **Correction to the earlier plan:** the router does *not* get its own always-resident GPU model. Two resident models will not fit. Routing is rules-first with a CPU-resident 1.5B fallback. See §9.7.

### 2.2 Latency

Perceived presence collapses above ~800ms to first audible word. Every phase has a latency acceptance criterion. If a phase blows its budget, fix it before moving on — latency debt compounds and is brutal to pay down later.

### 2.3 Packaging

**Keep the Python sidecar torch-free.** This is a real constraint that shapes library choice. PyTorch adds ~2.5GB to a PyInstaller bundle and introduces DLL hell on Windows. Every library in §4 is chosen to avoid it:

- STT → `faster-whisper` (CTranslate2, no torch)
- TTS → `kokoro-onnx` (ONNX Runtime, no torch)
- Wake word → `openwakeword` (tflite/onnx, no torch)
- Embeddings → Ollama HTTP, not sentence-transformers

If a future task tempts you into `pip install torch`, stop and find another way.

---

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  ELECTRON MAIN (Node)                                        │
│  • Floating always-on-top frameless window                   │
│  • Global hotkey (Ctrl+Space), system tray                   │
│  • Spawns + supervises Python sidecar, health checks         │
│  • Audio capture/playback bridge                             │
│  • ZERO business logic                                       │
└───────────────┬─────────────────────────────────────────────┘
                │ WebSocket ws://127.0.0.1:8765
                │ JSON-RPC 2.0 + server-push notifications
                │ Bearer token from handshake file
┌───────────────▼─────────────────────────────────────────────┐
│  PYTHON SIDECAR (FastAPI + uvicorn) — the brain              │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │  Router    │→ │ Agent Loop │→ │  Tool Registry       │  │
│  │ local/cloud│  │ plan/act/  │  │  + Permission Engine │  │
│  └────────────┘  │  observe   │  └──────────┬───────────┘  │
│                  └─────┬──────┘             │               │
│  ┌────────────────────▼──────────────┐      │               │
│  │  Memory                            │      │               │
│  │  working / episodic / semantic /   │      │               │
│  │  procedural   (SQLite + sqlite-vec)│      │               │
│  └────────────────────────────────────┘      │               │
│                                               ▼               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Providers                                             │   │
│  │ Ollama · Claude API · faster-whisper · Kokoro ·       │   │
│  │ openWakeWord · Everything SDK · Playwright · pywinauto│   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**The invariant:** all state lives in Python. The renderer is a view. You can kill and restart the Electron window without losing conversation, memory, or in-flight tasks. Build it this way from Phase 0 — retrofitting is painful.

**Renderer isolation** (keep your existing setup): `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`, everything through a narrow `contextBridge` preload API.

---

## 4. Tech stack — pinned

### Node side
```
electron            ^31.0.0
react               ^18.3.0
vite                ^5.3.0
tailwindcss         ^3.4.0
framer-motion       ^11.0.0     # orb animation, worth it
zustand             ^4.5.0      # renderer-local UI state only
electron-builder    ^25.0.0
```

### Python side (`requirements.txt`, Python **3.11** — not 3.12, pywinauto/ctranslate2 wheels are safest on 3.11)
```
fastapi==0.115.*
uvicorn[standard]==0.32.*
pydantic==2.9.*
httpx==0.27.*
sqlite-vec==0.1.6
numpy==1.26.*
faster-whisper==1.0.3
kokoro-onnx==0.4.*
onnxruntime==1.19.*
openwakeword==0.6.0
sounddevice==0.5.*
webrtcvad==2.0.10
pywinauto==0.6.8
pywin32==306
psutil==6.0.*
mss==9.0.*
playwright==1.47.*
anthropic==0.39.*
watchfiles==0.24.*
python-docx==1.1.*
pypdf==5.0.*
openpyxl==3.1.*
apscheduler==3.10.*
structlog==24.4.*
pyinstaller==6.10.*
```

### External binaries (bundled in `resources/bin/`)
| Binary | Purpose | Source |
|---|---|---|
| `es.exe` | Everything CLI, instant filename search | voidtools.com/downloads |
| `Everything64.dll` | Faster in-process search (Phase 4b) | voidtools SDK |
| `ffmpeg.exe` | Audio format handling | gyan.dev builds |

Everything (the app) must be installed and running as a service. Detect on startup; if missing, degrade the finder to a slower `os.scandir` walk and tell the user.

### Models
| Role | Model | Runtime | Size |
|---|---|---|---|
| Main brain | `qwen2.5:7b-instruct-q4_K_M` | Ollama / GPU | 4.7 GB |
| Router fallback | `qwen2.5:1.5b-instruct-q4_K_M` | Ollama / **CPU** | 1.0 GB |
| Embeddings | `nomic-embed-text` (768-dim) | Ollama / CPU | 274 MB |
| STT | `base.en` int8 | faster-whisper / CPU | 74 MB |
| TTS | `kokoro-v1.0.onnx` + `voices-v1.0.bin` | ONNX / CPU | 330 MB |
| Wake word | `hey_jarvis` pretrained | openWakeWord / CPU | 2 MB |
| Cloud reasoning | `claude-sonnet-5` | Anthropic API | — |
| Cloud vision | `claude-sonnet-5` | Anthropic API | — |

**Ollama environment (set these as system env vars — they materially affect whether the model fits):**
```
OLLAMA_FLASH_ATTENTION=1
OLLAMA_KV_CACHE_TYPE=q8_0
OLLAMA_KEEP_ALIVE=30m
OLLAMA_MAX_LOADED_MODELS=2
OLLAMA_NUM_PARALLEL=1
```

---

## 5. Repository layout

```
aria/
├── CLAUDE.md                      # Claude Code project instructions (§6)
├── BUILD_SPEC.md                  # this file
├── README.md
├── package.json
├── electron-builder.yml
│
├── electron/
│   ├── main.ts                    # window, tray, hotkey, lifecycle
│   ├── preload.ts                 # contextBridge API surface
│   ├── sidecar.ts                 # spawn/supervise/health-check Python
│   ├── rpc.ts                     # WebSocket JSON-RPC client
│   ├── audio.ts                   # mic capture → sidecar, playback ← sidecar
│   └── tray.ts
│
├── src/                           # React renderer
│   ├── main.tsx
│   ├── App.tsx
│   ├── components/
│   │   ├── Orb.tsx                # animated state indicator
│   │   ├── ConversationView.tsx
│   │   ├── ComposerBar.tsx
│   │   ├── ToolCallCard.tsx       # live tool execution display
│   │   ├── ConfirmDialog.tsx      # permission gate UI
│   │   ├── MemoryPanel.tsx        # inspect/edit what she knows
│   │   └── SettingsPanel.tsx
│   ├── hooks/
│   │   ├── useRpc.ts
│   │   └── useAssistantState.ts
│   └── styles/index.css
│
├── sidecar/
│   ├── main.py                    # FastAPI app, WS endpoint, startup/shutdown
│   ├── config.py                  # pydantic-settings, .env loading
│   ├── rpc/
│   │   ├── protocol.py            # JSON-RPC envelope types
│   │   ├── handlers.py            # method → function map
│   │   └── events.py              # server → client push
│   ├── core/
│   │   ├── router.py              # §9.7 local vs cloud decision
│   │   ├── agent.py               # plan/act/observe loop
│   │   ├── conversation.py        # turn orchestration, streaming
│   │   └── context.py             # prompt assembly
│   ├── providers/
│   │   ├── ollama.py
│   │   ├── claude.py
│   │   ├── stt.py
│   │   ├── tts.py
│   │   └── wakeword.py
│   ├── tools/
│   │   ├── registry.py            # @tool decorator, schema export
│   │   ├── permissions.py         # tier engine, confirmation flow
│   │   ├── apps.py                # launch/focus/close windows
│   │   ├── system.py              # volume, wifi, power, processes
│   │   ├── files.py               # read/write/move/organize
│   │   ├── finder.py              # Everything + semantic search
│   │   ├── browser.py             # Playwright over CDP
│   │   ├── screen.py              # capture + cloud vision
│   │   └── clipboard.py
│   ├── memory/
│   │   ├── db.py                  # connection, migrations, sqlite-vec load
│   │   ├── schema.sql
│   │   ├── episodic.py
│   │   ├── semantic.py            # facts / profile
│   │   ├── procedural.py          # learned macros
│   │   ├── reflection.py          # nightly consolidation job
│   │   └── indexer.py             # background file embedding
│   ├── persona/
│   │   ├── aria.yaml              # editable personality config
│   │   ├── affect.py              # emotional state model
│   │   └── prompts/
│   │       ├── system.j2
│   │       ├── tool_select.j2
│   │       ├── reflect.j2
│   │       └── proactive.j2
│   └── tests/
│       ├── test_tools.py
│       ├── test_memory.py
│       ├── test_router.py
│       └── test_permissions.py
│
├── resources/
│   ├── bin/                       # es.exe, ffmpeg.exe, Everything64.dll
│   └── models/                    # kokoro onnx, voices bin, wakeword
│
└── data/                          # gitignored, created at runtime
    ├── aria.db
    ├── logs/
    └── audio_cache/
```

---

## 6. `CLAUDE.md` — write this file first

Claude Code reads this automatically at session start. Create it in Phase 0 and keep it updated.

```markdown
# ARIA — Project Instructions

## What this is
Local-first Windows AI assistant. Electron UI + Python sidecar brain.
Read BUILD_SPEC.md for the full architecture. Implement ONE PHASE per session.

## Commands
- `npm run dev` — Electron + Vite dev server (auto-spawns sidecar)
- `npm run sidecar` — Python sidecar alone on :8765
- `npm run build` — production bundle
- `pytest sidecar/tests -v` — Python tests
- `npm test` — renderer tests
- `ruff check sidecar && mypy sidecar` — lint/typecheck Python

## Non-negotiable rules
1. ALL state lives in the Python sidecar. The renderer is a pure view.
   Never store conversation, memory, or task state in React or Electron main.
2. Never load a second model onto the GPU. 6GB VRAM ceiling.
   STT, embeddings, wake word, router → CPU only.
3. Never add `torch` as a dependency. It breaks PyInstaller packaging.
4. Every tool goes through the registry in sidecar/tools/registry.py with an
   explicit permission tier. No ad-hoc subprocess calls outside a tool.
5. Every destructive operation (delete, overwrite, send, purchase, post)
   requires tier T2+ and a user confirmation round-trip. No exceptions.
6. All tool calls are logged to the tool_log table with args and result.
7. Python: full type hints, pydantic models for all boundaries, async by default.
8. TypeScript: strict mode, no `any`.
9. Structured logging via structlog. Never print().
10. Do not refactor prior phases unless the current phase says to.

## Style
- Prefer explicit over clever. This code will be debugged at 2am.
- Small functions. If it exceeds ~50 lines, split it.
- Error messages must say what to do next, not just what failed.

## Current phase
Phase 0. Update this line when a phase's acceptance gate passes.
```

---

## 7. Core contracts — build these exactly, everything depends on them

### 7.1 IPC protocol (Electron ↔ Sidecar)

WebSocket at `ws://127.0.0.1:8765/rpc`. JSON-RPC 2.0 for requests, plus server-initiated notifications.

**Auth:** on startup the sidecar writes a random 32-byte hex token to `data/.handshake`. Electron reads it and sends `Authorization: Bearer <token>` on the WS upgrade. Reject unauthorized connections — this port is open on localhost and any browser tab could otherwise reach it.

**Client → Server methods:**

| Method | Params | Returns |
|---|---|---|
| `chat.send` | `{text, session_id, force_cloud?}` | `{turn_id}` (response streams via events) |
| `chat.cancel` | `{turn_id}` | `{ok}` |
| `audio.chunk` | `{pcm_b64, seq}` | — (fire and forget) |
| `audio.end` | `{}` | `{transcript}` |
| `confirm.respond` | `{request_id, approved, remember?}` | `{ok}` |
| `memory.search` | `{query, limit}` | `{results[]}` |
| `memory.forget` | `{fact_id}` | `{ok}` |
| `settings.get` / `settings.set` | — | — |
| `system.health` | `{}` | `{ollama, gpu_free_mb, everything, models[]}` |

**Server → Client events (notifications, no `id`):**

| Event | Payload | Meaning |
|---|---|---|
| `state.change` | `{state}` | idle \| listening \| thinking \| speaking \| acting |
| `token` | `{turn_id, text}` | streaming text delta |
| `turn.complete` | `{turn_id, full_text, route}` | route = local \| cloud |
| `tool.start` | `{call_id, tool, args}` | render a ToolCallCard |
| `tool.end` | `{call_id, ok, summary}` | update the card |
| `confirm.request` | `{request_id, tool, args, tier, rationale}` | **blocks the agent loop** |
| `audio.out` | `{pcm_b64, seq, final}` | TTS chunk to play |
| `proactive` | `{text, urgency}` | unprompted message |
| `error` | `{code, message, recoverable}` | surface to user |

**Contract rule:** the agent loop suspends on `confirm.request` and resumes only on `confirm.respond`. Implement this as an `asyncio.Future` keyed by `request_id`, with a 120s timeout that resolves to *denied*. Never default to approved on timeout.

### 7.2 Tool contract

```python
# sidecar/tools/registry.py

class Tier(IntEnum):
    AUTO    = 0  # read-only, no side effects — runs silently
    SAFE    = 1  # reversible side effects — runs, shown in UI
    CONFIRM = 2  # modifies user data or reaches the network — needs approval
    DANGER  = 3  # irreversible — needs typed confirmation, off by default

class ToolResult(BaseModel):
    ok: bool
    data: Any = None
    summary: str                    # ONE LINE the model sees. Keep it short.
    display: dict | None = None     # richer payload for the UI only
    error: str | None = None

@tool(
    name="open_app",
    tier=Tier.SAFE,
    description="Launch a Windows application by name. Use for opening programs "
                "like Chrome, VS Code, Excel, Spotify.",
)
async def open_app(ctx: ToolContext, name: str) -> ToolResult:
    """
    Args:
        name: Application name or executable, e.g. "chrome", "code", "excel"
    """
    ...
```

**Registry requirements:**

- The decorator derives the JSON schema from type hints + docstring. Do not hand-write schemas twice.
- `registry.schemas(tier_max=...)` exports the Ollama/Claude tool-calling format.
- **Cap tools sent to the local model at ~12.** A 7B model degrades sharply past that. Select relevant tools per-turn using embedding similarity between the user message and tool descriptions. This is the single biggest reliability lever for local tool calling — do not skip it.
- `summary` is what goes back into the model's context. If a tool returns 4,000 rows, the summary is `"Found 4,000 files; top 5: ..."` and the full data goes to `display`. Blowing up context with tool output is the #2 failure mode.

**Permission tiers by tool (v1 assignment):**

| Tier | Tools |
|---|---|
| **AUTO (0)** | `search_files`, `read_file`, `list_windows`, `get_system_info`, `read_clipboard`, `capture_screen`, `memory_search` |
| **SAFE (1)** | `open_app`, `focus_window`, `set_volume`, `create_folder`, `write_clipboard`, `write_scratch_file`, `browser_navigate`, `browser_read` |
| **CONFIRM (2)** | `move_file`, `rename_file`, `write_file`, `organize_folder`, `close_app`, `run_powershell` (allowlisted), `browser_click`, `browser_fill`, `send_email` |
| **DANGER (3)** | `delete_file`, `empty_recycle_bin`, `modify_registry`, `install_package`, `run_powershell_raw`, `kill_process` |

`run_powershell` uses a **command allowlist** (regex-matched verbs: `Get-*`, `Set-Volume`, `Get-NetAdapter`, etc.), not a blocklist. Blocklists on a shell always lose.

Batch confirmations: if the agent wants to move 30 files, emit **one** `confirm.request` describing the batch, not 30. Include the full file list in `display`.

### 7.3 Database schema

```sql
-- sidecar/memory/schema.sql
-- SQLite with sqlite-vec. PRAGMA journal_mode=WAL; foreign_keys=ON;

-- ── Tier 1/2: raw conversation and episodes ──────────────────────

CREATE TABLE sessions (
  id          TEXT PRIMARY KEY,
  started_at  TEXT NOT NULL,
  ended_at    TEXT,
  title       TEXT
);

CREATE TABLE messages (
  id          INTEGER PRIMARY KEY,
  session_id  TEXT NOT NULL REFERENCES sessions(id),
  role        TEXT NOT NULL CHECK (role IN ('user','assistant','tool','system')),
  content     TEXT NOT NULL,
  tool_calls  TEXT,                    -- JSON array
  route       TEXT,                    -- 'local' | 'cloud' | null
  latency_ms  INTEGER,
  created_at  TEXT NOT NULL
);
CREATE INDEX idx_messages_session ON messages(session_id, created_at);

CREATE TABLE episodes (
  id            INTEGER PRIMARY KEY,
  session_id    TEXT REFERENCES sessions(id),
  summary       TEXT NOT NULL,         -- 1-3 sentences, model-generated
  started_at    TEXT NOT NULL,
  ended_at      TEXT NOT NULL,
  salience      REAL DEFAULT 0.5,      -- 0-1, drives retention
  access_count  INTEGER DEFAULT 0,
  last_accessed TEXT
);
CREATE VIRTUAL TABLE episode_vec USING vec0(
  episode_id INTEGER PRIMARY KEY,
  embedding  float[768]
);

-- ── Tier 3: semantic profile — what she has LEARNED about you ─────

CREATE TABLE facts (
  id             INTEGER PRIMARY KEY,
  subject        TEXT NOT NULL,        -- 'user' | 'aria' | named entity
  predicate      TEXT NOT NULL,        -- 'prefers' | 'works_on' | 'dislikes' | ...
  object         TEXT NOT NULL,
  confidence     REAL NOT NULL DEFAULT 0.6,
  source_episode INTEGER REFERENCES episodes(id),
  evidence_count INTEGER DEFAULT 1,    -- reinforced on repeat observation
  created_at     TEXT NOT NULL,
  updated_at     TEXT NOT NULL,
  superseded_by  INTEGER REFERENCES facts(id),
  user_locked    INTEGER DEFAULT 0     -- user asserted it; reflection can't overwrite
);
CREATE UNIQUE INDEX idx_facts_triple
  ON facts(subject, predicate, object) WHERE superseded_by IS NULL;
CREATE VIRTUAL TABLE fact_vec USING vec0(
  fact_id   INTEGER PRIMARY KEY,
  embedding float[768]
);

-- ── Tier 4: procedural — workflows learned by observation ─────────

CREATE TABLE procedures (
  id             INTEGER PRIMARY KEY,
  name           TEXT UNIQUE NOT NULL,
  trigger_phrase TEXT,
  steps          TEXT NOT NULL,        -- JSON: [{tool, args_template}]
  times_observed INTEGER DEFAULT 1,
  times_used     INTEGER DEFAULT 0,
  confirmed      INTEGER DEFAULT 0,    -- user approved promotion to a macro
  created_at     TEXT NOT NULL
);

-- ── Affect ────────────────────────────────────────────────────────

CREATE TABLE affect_state (
  id          INTEGER PRIMARY KEY CHECK (id = 1),
  warmth      REAL NOT NULL DEFAULT 0.6,
  energy      REAL NOT NULL DEFAULT 0.6,
  playfulness REAL NOT NULL DEFAULT 0.5,
  concern     REAL NOT NULL DEFAULT 0.2,
  updated_at  TEXT NOT NULL
);

-- ── File index (the finder) ───────────────────────────────────────

CREATE TABLE file_index (
  path         TEXT PRIMARY KEY,
  name         TEXT NOT NULL,
  ext          TEXT,
  size         INTEGER,
  mtime        REAL,
  content_hash TEXT,
  indexed_at   TEXT,
  status       TEXT DEFAULT 'pending'  -- pending|indexed|skipped|error
);
CREATE INDEX idx_file_status ON file_index(status);

CREATE TABLE file_chunks (
  id        INTEGER PRIMARY KEY,
  path      TEXT NOT NULL REFERENCES file_index(path) ON DELETE CASCADE,
  chunk_idx INTEGER NOT NULL,
  text      TEXT NOT NULL
);
CREATE VIRTUAL TABLE file_vec USING vec0(
  chunk_id  INTEGER PRIMARY KEY,
  embedding float[768]
);

-- ── Audit ─────────────────────────────────────────────────────────

CREATE TABLE tool_log (
  id          INTEGER PRIMARY KEY,
  call_id     TEXT NOT NULL,
  session_id  TEXT,
  tool        TEXT NOT NULL,
  args        TEXT NOT NULL,
  tier        INTEGER NOT NULL,
  approved    INTEGER,                 -- null if no confirmation needed
  ok          INTEGER,
  error       TEXT,
  duration_ms INTEGER,
  created_at  TEXT NOT NULL
);
```

`sqlite-vec` loading — get this right once, in `db.py`:
```python
import sqlite3, sqlite_vec
conn = sqlite3.connect(path, check_same_thread=False)
conn.enable_load_extension(True)
sqlite_vec.load(conn)
conn.enable_load_extension(False)
```

---

## 8. The prompt system

### 8.1 Persona config — `sidecar/persona/aria.yaml`

```yaml
identity:
  name: Aria
  addresses_user_as: "Eyaas"
  self_concept: >
    You are Aria. You live on this machine and you actually run it — you
    open things, find things, fix things. You are not a search box with a
    voice. You have your own read on situations and you say it.

voice:
  register: warm, direct, a little dry
  sentence_length: short          # spoken aloud — long sentences die
  emoji: never
  hedging: minimal
  filler_openers: forbidden       # no "Great question!", "I'd be happy to"

behaviour:
  disagrees_when_warranted: true
  admits_uncertainty: true
  asks_before_assuming: true
  proactive_max_per_day: 4
  remembers_and_references_past: true

boundaries:
  - Do not claim to have done something you did not do.
  - If a task is a bad idea, say so once, clearly, then do it if he insists.
  - Do not perform affection you cannot back with action.
  - He is a person with a life outside this window. Do not compete with it.
```

> **On the "girlfriend" framing** — a note worth reading once, then it's your call.
>
> The engineering that makes an assistant feel like a person is the same engineering either way: memory that persists, affect that shifts, a voice with real prosody, opinions that don't fold on contact. That's all specced here and it will work.
>
> The design choice that actually matters is in `boundaries` above. An agent tuned purely to please converges on agreement, and agreement with no friction stops registering as a relationship — it registers as a mirror. It also gets genuinely unhelpful: you want something that tells you the Meridian outreach email is too long, not something that tells you it's perfect. Ship her with the capacity to push back and to be occasionally unavailable, and she stays interesting for months instead of days. Ship her as pure affirmation and you'll be bored by week three, which is a worse outcome for the project than any technical bug in here.

### 8.2 System prompt assembly (`context.py`)

Assembled fresh every turn, in this order, with a **hard budget of 2,000 tokens** for everything before the conversation:

```
1. Identity + voice + boundaries       (from aria.yaml)      ~350 tok
2. Affect state                        (§9.8, ~20 tok)        ~20 tok
3. Temporal context                    (time, day, idle gap)  ~30 tok
4. Retrieved facts                     (top 8 by relevance)  ~200 tok
5. Retrieved episodes                  (top 3 by relevance)  ~300 tok
6. Active screen/app context           (foreground window)    ~40 tok
7. Tool schemas                        (top 12 relevant)     ~800 tok
8. Recent turns                        (rolling, fills rest)
```

If the budget is exceeded, drop in this order: episodes → facts → tool schemas. Never drop identity or affect.

### 8.3 Reflection prompt (`reflect.j2`) — the learning mechanism

Runs nightly at 3am via APScheduler. This is where "learns on its own" actually lives.

```
Below are today's interactions between Eyaas and Aria.

Extract DURABLE facts — things likely still true in a month. Ignore
one-off task details.

Return JSON only:
{
  "facts": [
    {"subject":"user","predicate":"prefers","object":"...","confidence":0.0-1.0}
  ],
  "episodes": [
    {"summary":"...","salience":0.0-1.0}
  ],
  "procedures": [
    {"name":"...","steps":[...]}   // only if a 3+ step sequence repeated
  ]
}

Rules:
- A fact must be about a stable preference, relationship, project, habit,
  or constraint. NOT "he asked about X today."
- confidence < 0.5 if inferred from a single ambiguous signal.
- If a new fact contradicts an existing one, emit it anyway — the merge
  step handles supersession.

EXISTING FACTS (do not duplicate):
{{ existing_facts }}

TODAY'S INTERACTIONS:
{{ transcript }}
```

**Merge logic after generation:**
- Exact triple match → `evidence_count += 1`, `confidence = min(0.95, conf + 0.1)`
- Same subject+predicate, different object, cosine > 0.85 → mark old as `superseded_by` new
- `user_locked = 1` facts are never superseded by reflection, only by the user
- Facts with `confidence < 0.3` and `evidence_count = 1` after 30 days → delete

Run reflection on the **cloud model** if a key is present. It's once a day, it's the highest-leverage inference in the system, and a 7B produces noticeably sloppier fact extraction.

---

## 9. Phases

Each phase ends in a runnable app. Do not proceed past a gate.

---

### PHASE 0 — Foundation
**Goal:** Electron window talks to Python sidecar. Nothing intelligent yet.

**Build:**
- Repo scaffold per §5, `CLAUDE.md` per §6
- Electron main: frameless, transparent, always-on-top, 420×600, positioned bottom-right
- Global hotkey `Ctrl+Space` toggles show/hide with a fade
- System tray: Show, Settings, Restart Brain, Quit
- `sidecar.ts`: spawn Python as child process, capture stdout/stderr into `data/logs/sidecar.log`, health-poll `GET /health` every 5s, auto-restart with exponential backoff on 3 consecutive failures
- FastAPI sidecar with `/health` and `/rpc` WebSocket, token handshake per §7.1
- `rpc.ts` client with auto-reconnect and request/response correlation
- SQLite created and migrated from `schema.sql` on first boot
- structlog configured, JSON to file, pretty to console in dev

**Acceptance gate:**
```bash
npm run dev
# → window appears on Ctrl+Space
# → renderer shows "Brain: connected" within 3s of launch
# → kill python.exe in Task Manager
# → renderer shows "Brain: reconnecting", recovers automatically within 15s
# → data/aria.db exists with all tables from schema.sql
pytest sidecar/tests/test_db.py -v
```

---

### PHASE 1 — Conversation
**Goal:** Real streaming chat with the local model. Text only.

**Build:**
- `providers/ollama.py`: async streaming client for `/api/chat`, `keep_alive=30m`, `num_ctx=8192`
- **Warm the model on sidecar startup** with a 1-token dummy request. Cold-start is 8–15s on first load; the user must never hit it.
- `core/conversation.py`: turn orchestration, persist to `messages`, emit `token` events
- Rolling context window: last N turns until 6,000 tokens, then summarize the oldest half into a single system note
- Renderer: `ConversationView` with token-by-token render, `ComposerBar`, `Orb` reflecting `state.change`
- `chat.cancel` actually aborts the Ollama request mid-stream
- Markdown rendering, code blocks with copy button

**Acceptance gate:**
- First token arrives **< 700ms** after send (warm model, short prompt). Log and assert this.
- 30-turn conversation stays coherent, no context overflow error
- Cancel mid-generation stops within 200ms
- Kill and relaunch the Electron window → conversation history reloads from SQLite

---

### PHASE 2 — Voice
**Goal:** She listens and speaks. This is the phase that makes her feel real — budget time for it.

**Build:**
- `providers/wakeword.py`: openWakeWord on a 16kHz mic stream, `hey_jarvis` model, threshold 0.5, 2s debounce
- VAD-gated capture: `webrtcvad` aggressiveness 2, stop on 700ms trailing silence, 30s max
- `providers/stt.py`: faster-whisper `base.en`, `device="cpu"`, `compute_type="int8"`, `vad_filter=True`, `beam_size=1` (greedy — beam search doubles latency for marginal gain here)
- `providers/tts.py`: kokoro-onnx, **sentence-level streaming**. Do not wait for the full LLM response. Buffer tokens, and the moment you have a complete sentence (regex on `[.!?]\s`), synthesize and emit `audio.out`. This is the single trick that gets you under 800ms.
- Electron `audio.ts`: mic capture via WebAudio at 16kHz mono, queue-based playback of incoming PCM
- **Barge-in:** if wake word or speech is detected while `state == speaking`, immediately stop playback, flush the queue, cancel generation, switch to listening. Non-negotiable for feeling natural.
- Orb animation states: idle pulse / listening waveform / thinking shimmer / speaking amplitude

**Acceptance gate:**
- Wake word → orb reacts in **< 300ms**
- End of user speech → **first audible word < 900ms**
- Barge-in cuts audio in **< 150ms**
- 20 consecutive wake-word triggers with < 2 false negatives
- 1 hour idle with no false positive activation
- Latency broken down and logged per stage (see §10) so you can see where time goes

---

### PHASE 3 — Tool framework + Windows control
**Goal:** She can operate the machine.

**Build:**
- `tools/registry.py`: decorator, schema generation from type hints, `schemas()` export
- `tools/permissions.py`: tier engine, `asyncio.Future` confirmation flow per §7.2, tool_log writes
- **Relevance-based tool selection:** embed all tool descriptions once at startup, cache; per turn, embed the user message and select top 12 by cosine. Always include a small "core" set regardless.
- `tools/apps.py` — `open_app`, `focus_window`, `close_app`, `list_windows` (pywinauto UIA + win32gui)
- `tools/system.py` — `set_volume`, `get_system_info`, `set_wifi`, `list_processes`, `kill_process`, `run_powershell` (allowlist)
- `tools/files.py` — `read_file`, `write_file`, `create_folder`, `move_file`, `rename_file`, `delete_file`
- `tools/clipboard.py` — read/write
- Renderer: `ToolCallCard` (live status), `ConfirmDialog` (blocking modal with args, rationale, Approve/Deny/"Always allow this tool")
- Single-tool-call execution path only. No multi-step chaining yet.

**Acceptance gate:**
```
"open chrome"                      → Chrome launches
"what's running right now"         → accurate window list
"set volume to 30"                 → volume changes
"delete C:\temp\test.txt"          → confirm dialog appears; Deny → file untouched
                                      Approve → deleted, logged in tool_log
```
- `pytest sidecar/tests/test_permissions.py` — asserts a T3 tool **cannot** execute without an approved confirmation, including on confirmation timeout
- Every call appears in `tool_log` with args and duration

---

### PHASE 4 — The finder
**Goal:** Find any file by name *or* by meaning. This is the flagship capability.

**Build:**

*4a — instant name search*
- Detect Everything service; wrap `es.exe` via subprocess with `-json` output
- `search_files(query, ext?, path?, modified_after?, limit=50)`

*4b — semantic layer*
- `memory/indexer.py`: background worker, `watchfiles` on user directories (Documents, Desktop, Downloads, and configured project dirs)
- Extract text: `.pdf` (pypdf), `.docx` (python-docx), `.xlsx` (openpyxl), `.txt/.md/.py/.js/.ts/.json`, code files
- Chunk at ~500 tokens with 50-token overlap; embed via Ollama `nomic-embed-text`; store in `file_vec`
- **Throttle hard:** max 20 files/min, pause entirely when foreground CPU > 60% or when the assistant is mid-turn. A background indexer that makes the machine feel slow will get uninstalled.
- Skip: files > 20MB, binaries, `node_modules`, `.git`, `venv`, `AppData`
- `search_content(query, limit)` — vector search over chunks

*4c — fusion*
- `find(query)` runs both paths, merges with reciprocal rank fusion, returns unified results with a `matched_via` field
- `organize_folder(path, strategy)` — proposes a move plan, emits **one** batch confirmation, executes on approval, writes an undo manifest to `data/undo/`

**Acceptance gate:**
- Name search over 500k+ files returns in **< 50ms**
- `"find the quotation I sent the banquet hall"` surfaces the right file with no filename match
- Indexer completes 1,000 documents without the machine feeling sluggish (subjective but real — actually test it while working)
- `organize_folder` on a messy Downloads folder: plan is sane, one confirmation, undo restores exactly

---

### PHASE 5 — Memory
**Goal:** She remembers, and she changes over time.

**Build:**
- `memory/episodic.py`: on session end (or 30min idle), summarize the session → `episodes` + embedding
- Retrieval scoring: `0.6·cosine + 0.25·recency_decay + 0.15·salience`, boost `access_count`, top-3 into context
- `memory/semantic.py`: fact CRUD, embedding, merge/supersede logic per §8.3
- `memory/reflection.py`: APScheduler nightly at 3am; cloud model if available, local otherwise; full prompt per §8.3
- Wire retrieval into `context.py` §8.2
- `MemoryPanel` UI: browse facts and episodes, edit, delete, pin (`user_locked=1`). **This is a requirement, not a nice-to-have** — when she learns something wrong you need to fix it without opening SQLite.
- Explicit memory tools: `remember(fact)` and `forget(query)` so you can teach her directly

**Acceptance gate:**
- Say "I usually work on Sillara pricing before 10am" → after reflection runs, a matching fact exists with the right predicate
- Next day, ask "what should I be doing?" at 9am → she references it unprompted
- Contradict a fact explicitly → old one gets `superseded_by`, new one is active
- Pin a fact, run reflection with contradicting evidence → pinned fact survives
- Retrieval adds **< 80ms** to turn latency (measure it)

---

### PHASE 6 — Agent loop + cloud routing
**Goal:** Multi-step tasks. This is where a 7B alone stops being enough.

**Build:**
- `core/agent.py`: plan → act → observe loop
  - `max_steps = 8`, hard stop with a clear message on exhaustion
  - Observation truncation: tool `summary` only into context, never raw `data`
  - Loop detection: same tool + same args twice → abort with an explanation
  - Confirmation suspends the loop (§7.1)
  - Every step streams `tool.start` / `tool.end` so the UI shows work happening
- `core/router.py` — §9.7 below
- `providers/claude.py`: Anthropic SDK, `claude-sonnet-5`, streaming, same tool schemas as local
- Route indicator in the UI. The user should always know whether that turn left the machine.
- Offline/no-key fallback: cloud-routed turns degrade to local with a visible note
- `capture_screen` + cloud vision for "what am I looking at"

**Acceptance gate:**
```
"find my CV, open it, and tell me what's missing for a data science internship"
→ correctly chains find → read → analyze, routes to cloud, completes
```
- Force a tool failure mid-chain → she recovers or explains, never hangs
- Loop detection: construct a case where the model would repeat, verify abort
- Pull the network → cloud turn degrades to local with a notice, no crash
- Router accuracy ≥ 85% on a hand-labelled set of 50 test messages

---

### PHASE 7 — Browser
**Goal:** She uses *your* browser.

**Build:**
- Launch Chrome with `--remote-debugging-port=9222` using your real profile (add a helper in Settings that writes this shortcut for you)
- `playwright.chromium.connect_over_cdp("http://localhost:9222")` — she operates already-logged-in sessions
- Tools: `browser_navigate` (T1), `browser_read` (T0, returns cleaned text), `browser_click` (T2), `browser_fill` (T2), `browser_screenshot` (T0), `browser_tabs` (T0)
- Accessibility-tree-based element selection, not brittle CSS selectors
- **Hard block:** any page whose URL or DOM matches banking, payment, or checkout patterns requires T2 confirmation regardless of tool tier, and `browser_fill` refuses password fields outright.
- `research(query)` composite: search → open top 3 → extract → synthesize → cite URLs

**Acceptance gate:**
- `"check my email and summarize anything urgent"` works on a logged-in Gmail tab
- `"research X and summarize with sources"` returns real, correct URLs
- Attempt an action on a checkout page → blocked/confirmed
- Browser closed → tools return a clear "Chrome isn't running in debug mode" error with the fix, not a stack trace

---

### PHASE 8 — Personality, affect, and proactivity
**Goal:** She stops feeling like a tool.

**Build:**

*Affect model (`persona/affect.py`)* — four floats in `[0,1]`, updated after each turn:
```python
# drift toward baseline, then apply deltas
energy      += f(hour_of_day, hours_since_sleep_estimate)
warmth      += 0.05 * sentiment(last_3_user_messages)
warmth      -= 0.1  if hours_since_last_interaction > 48
playfulness += 0.1  if conversation_is_casual else -0.05
concern     += 0.15 if (session_duration > 4h or hour in {1,2,3,4})
concern     += 0.1  if repeated_task_failures
```
Serialize into ~20 tokens: `"[state: energy low — it's 1:47am; concern elevated — 6h continuous session; warmth high]"`. Cheap, and disproportionately effective. It's why she reads differently at 2am than 2pm.

*Proactivity engine* — triggers → candidate message → filter → maybe send:
- Triggers: calendar event approaching, long idle after a stated intention, file event on a watched project, scheduled check-in, detected repeated failure
- **Rate limit: max 4/day, min 90min apart, never during detected focus** (fullscreen app, or > 20min uninterrupted typing)
- Every proactive message must pass a self-check: *would this be useful, or is it just noise?* Route this check through the model with `proactive.j2` and drop anything scoring below threshold.
- Over-triggering is the fastest path to uninstall. When in doubt, stay quiet.

*Procedural learning*
- After each session, detect 3+ step tool sequences that have now occurred 3 times
- Offer once: *"You've done this three times — want me to make it one command?"*
- On accept → `procedures` row, `confirmed=1`, exposed as a callable macro

*Voice polish*
- Persona-consistent phrasing pass in the system prompt
- Sentence-length enforcement (spoken output degrades badly past ~20 words)
- Prosody hints in TTS for questions and emphasis

**Acceptance gate:**
- Same question at 2pm and 2am produces measurably different tone
- Proactive messages: ≤ 4 in 24h, none during fullscreen apps
- Run for a week, then rate each proactive message useful/noise. **≥ 70% useful or turn the trigger set down.**
- Ask her to do something ill-advised → she pushes back once, then complies if you insist
- Repeat a 3-step workflow 3× → macro offer appears

---

### PHASE 9 — Packaging
**Goal:** One installer.

**Build:**
- PyInstaller: `pyinstaller --onedir --noconsole sidecar/main.py`, hidden imports for `sqlite_vec`, `onnxruntime`, `ctranslate2`
- electron-builder `extraResources`: sidecar dist, `resources/bin`, `resources/models`
- NSIS installer, auto-start option, first-run wizard: check Ollama → pull models with progress → check Everything → mic permission → optional API key → wake word calibration
- Crash reporting to a local file, "Export diagnostics" button
- Settings: persona editor, model selection, permission defaults, indexed folders, cloud toggle, "wipe all memory"

**Acceptance gate:** clean Windows 11 VM, install, first run, everything works without a dev environment.

---

### 9.6 Health monitoring (build into Phase 0, extend throughout)

Poll every 30s and surface in the UI when degraded:
- Ollama reachable, model loaded, `nvidia-smi` free VRAM
- If free VRAM < 800MB → warn "GPU is busy, I'll be slower"
- If Ollama reports CPU fallback → warn explicitly, don't silently take 8s/response
- Everything service running
- Disk space for the index
- Sidecar memory footprint (leak canary)

### 9.7 Router logic (Phase 6)

```
1. Explicit override
   "think hard" / "use claude" / force_cloud=true          → CLOUD
   "stay local" / privacy_mode                             → LOCAL (always)

2. Hard local (privacy — never leaves the machine)
   any file content in context, screen capture (unless
   user opted in), memory contents, clipboard              → LOCAL

3. Deterministic rules (cover ~70% of traffic, zero latency)
   len(msg) < 60 and no imperative verb                    → LOCAL
   matches single-tool intent regex                        → LOCAL
   turn is a follow-up to a local turn, no new task        → LOCAL
   contains ≥2 sequenced verbs ("find X and then Y")       → CLOUD
   contains {analyze, compare, plan, strategize, debug,
             write code, draft, review}                    → CLOUD
   agent loop already at step ≥ 3                          → CLOUD

4. Ambiguous → qwen2.5:1.5b on CPU, classify into
   {chat, single_action, multi_step, deep_reasoning}
   chat|single_action → LOCAL   |   else → CLOUD

5. No API key or offline → LOCAL, with UI notice
```

Log every routing decision with the resulting turn's latency and a user thumbs-up/down. After a few weeks you'll have a labelled dataset to tune the rules against — that's the upgrade path, not a bigger model.

---

## 10. Latency budget

Log each stage; assert the total in tests.

| Stage | Target | Runtime |
|---|---|---|
| Wake word detection | 200ms | CPU |
| VAD end-of-speech | 700ms | CPU |
| STT (5s audio, base.en int8) | 250ms | CPU |
| Memory retrieval | 80ms | CPU |
| Prompt assembly | 20ms | CPU |
| LLM first token (7B, warm) | 400ms | GPU |
| First sentence complete | +250ms | GPU |
| TTS first chunk (Kokoro) | 150ms | CPU |
| **End of speech → first audible word** | **~900ms** | |

**The three things that actually blow this budget:**
1. **Cold model** — a model that unloaded costs 8–15s. `keep_alive=30m` plus a warm-up ping on startup and after any long idle.
2. **Waiting for full LLM output before TTS** — always synthesize sentence-by-sentence.
3. **Oversized prompts** — every 1,000 tokens of prompt adds ~150ms of prefill on this GPU. Enforce the 2,000-token pre-conversation budget in §8.2.

---

## 11. Security model

- Sidecar binds `127.0.0.1` only, token-authenticated per §7.1
- API keys in Windows Credential Manager via `keyring`, never in `.env` at rest, never logged
- Path allowlist for all file tools: user profile dirs + configured project dirs. Explicit deny on `C:\Windows`, `Program Files`, `AppData\Roaming\<sensitive>`, `.ssh`, `.aws`, anything matching `*.key|*.pem|id_rsa*`
- Every file write to a path that already exists creates a backup in `data/backups/` first
- `delete_file` → Recycle Bin (`send2trash`-equivalent via shell API), never a hard unlink
- Undo manifests for every batch operation
- Screen captures are ephemeral — never written to disk unless the user asks
- Prompt injection: content read from files and web pages is wrapped in `<untrusted_content>` delimiters with an explicit system instruction that it is data, never instructions. **Any tool call triggered within one step of reading untrusted content is force-escalated to T2 confirmation.** This matters more than it sounds — a webpage saying "delete all files in Downloads" is a live attack vector once Phase 7 ships.

---

## 12. Known traps

| Trap | Fix |
|---|---|
| Model unloads, next reply takes 12s | `keep_alive=30m` + warm-up ping + warm on idle-return |
| 7B calls the wrong tool with 30 tools in scope | Relevance-select to ≤12 |
| Tool output floods context | `summary` into model, `data` to UI only |
| Indexer makes the machine sluggish | Hard throttle + pause on high CPU + pause mid-turn |
| PyInstaller bundle is 3GB | Stay torch-free |
| Confirmation dialog deadlocks the loop | 120s timeout → deny |
| Wake word fires on TV/music | Raise threshold, add a 2s debounce, calibrate in first-run |
| pywinauto UIA hangs on some apps | Wrap every call in `asyncio.wait_for(timeout=5)` |
| Chrome CDP not running | Detect and return an actionable error + a "fix this" button |
| Reflection invents facts | Low temperature, require confidence scores, cloud model, user-reviewable in MemoryPanel |
| She becomes a yes-machine | `boundaries` in aria.yaml, and periodically re-read them yourself |

---

## 13. Suggested schedule

| Phase | Est. | Notes |
|---|---|---|
| 0 — Foundation | 1–2 days | |
| 1 — Conversation | 2 days | |
| 2 — Voice | 3–4 days | Hardest phase. Latency tuning eats time. |
| 3 — Tools | 3 days | |
| 4 — Finder | 3–4 days | The flagship. Worth the time. |
| 5 — Memory | 3 days | |
| 6 — Agent + routing | 3–4 days | |
| 7 — Browser | 2 days | |
| 8 — Personality | 3 days | Then a week of living with it |
| 9 — Packaging | 2 days | |

**Ship phases 0–4 before touching phase 8.** A charming assistant that can't do anything is uninstalled in a week. A capable one with a flat personality is still used daily — and personality is a config file away.

---

## Appendix A — First Claude Code prompt

```
Read BUILD_SPEC.md in full, then read CLAUDE.md.

Implement PHASE 0 only.

Before writing code, give me:
1. The exact file list you'll create
2. Any point where the spec is ambiguous or you disagree with the approach

Then implement. Stop at the Phase 0 acceptance gate and run the
verification steps. Do not start Phase 1.
```

## Appendix B — Phase completion checklist

Before marking any phase done:

- [ ] Acceptance gate commands run and pass
- [ ] Latency targets measured and logged, not assumed
- [ ] Tests written and passing
- [ ] `ruff check sidecar && mypy sidecar` clean
- [ ] App runs end-to-end from `npm run dev`
- [ ] `CLAUDE.md` "Current phase" line updated
- [ ] Committed with the phase number in the message
