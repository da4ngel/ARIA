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
- `graphify update .` — refresh the knowledge graph after code changes

## Keep the knowledge graph current
`graphify-out/` holds a knowledge graph of this repo (`graph.json`, `graph.html`,
`GRAPH_REPORT.md`). **It goes stale the moment code changes, so refresh it as part
of finishing the work — do not wait to be asked.**

Run this at the end of any session that added, deleted, or edited files under
`sidecar/`, `src/`, `electron/`, or `scripts/`:

    graphify update .

It re-extracts code via AST only — **no LLM, no API key, no tokens, seconds not
minutes** — merges into the existing graph, and prints
`No code-graph topology changes detected` and leaves the outputs untouched when
nothing structural moved. Safe to run when unsure.

- **`update` is code-only, by design.** Changes to `BUILD_SPEC.md`, `CLAUDE.md`,
  `README.md`, or any image are invisible to it; those need semantic extraction,
  which means `/graphify --update` in the assistant (it dispatches subagents).
  The command says so itself when it finishes.
- **This CLAUDE.md is in the graph.** Editing it — which every phase does —
  is exactly the case `graphify update .` will *not* pick up. Roughly once a
  phase, or after a substantial edit here, run `/graphify --update` instead.
- **A refactor that deletes code shrinks the graph, and the shrink guard blocks
  that write** (it exists so a failed extraction cannot silently gut a good
  graph). Only then, and only when the shrink is genuinely intended, use
  `graphify update . --force`. Never reach for `--force` to make an error go
  away.
- `graphify cluster-only .` re-clusters and regenerates the report from the
  existing graph without re-extracting anything. Use it when the communities
  look wrong but the code has not moved.
- `graphify check-update .` reports whether a semantic re-extraction is pending;
  it is cron-safe and changes nothing.
- **Two extractors report known gaps here, both benign**: `settings.local.json`
  yields zero nodes, and 4 `.sql` migration files are skipped because
  `tree_sitter_sql` is absent (`pip install "graphifyy[sql]"` to include them).
  Do not treat either warning as a failed update.

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

## Phase 4 — the finder (2026-08-07)
`open_path`, `search_files`, `open_file`, `search_content`, `find`.

- **`num_gpu: 0` on every embedding call.** Rule 2, and CLAUDE.md already
  records what two models on a 6GB card does. Verified with `ollama ps`:
  `nomic-embed-text 376MB 100% CPU` beside `qwen2.5:7b 5.1GB 18%/82%` — both
  resident, generation undisturbed. 752ms cold, ~154ms per chunk after.
- **The throttle is the feature**, not a detail: 20 files/min, and paused
  entirely while `conversation.busy` or the CPU is over 60%. §9 is blunt about
  why — an indexer that makes the machine feel slow gets uninstalled.
- **Everything is not installed here**, so the bounded scan is what runs:
  Documents, Desktop, Downloads, depth- and time-limited, 163–185ms, cached
  45s. A deliberate deviation from "tell him to install it" — a feature that
  does nothing until you install a second program is a poor answer to "say
  open cv and get my CV". The message still names Everything.
- **Ranking reuses `tools/apps.score` unchanged.** A filename is the same
  problem as an app name. Recency is a quarter-weight tiebreaker: "the latest
  CV" still has to be a CV, and a newer `budget_2026.xlsx` must not answer
  "cv" — that is a test.
- **Filler words are stripped first.** Without it "my cv" returned nothing:
  the model forwards the phrase, not the noun inside it.
- **`AppData` is in the skip list**, which is correct and also means anything
  under `%TEMP%` is invisible to the indexer — the first end-to-end probe
  indexed zero files for exactly that reason.
- **Tests must set `ARIA_INDEX_FILES=false`.** The RPC fixture runs the real
  lifespan, which otherwise walks the real Documents of whoever runs the suite.
- **Measured gate**: "the quotation I sent the banquet hall" finds
  `doc_final_v3.txt`, whose name contains none of those words.

## Files, and trusted folders (2026-08-07)
Fifteen tools at the time; twenty-five now — see the Phase 3 completion below.
`read_file`, `list_folder` (T0), `create_folder` (T1), `write_file`,
`rename_file`, `move_file` (T2), `delete_file`, `delete_folder` (T3).

- **A trusted folder is trusted completely**, deletion included, and **nothing
  is trusted until it is added**. Recursive.
- **Trust decides whether she asks, never what is allowed.** The refusals in
  `files.py` — drive roots, `Windows`, `Program Files` — are untouched by it,
  and `allow_danger_tools` still decides whether a DANGER tool exists at all.
- **A call spanning trusted and untrusted still asks.** Moving a file *out* of
  a trusted folder is not covered by trusting it — the destination is the part
  that matters. Mutation-checked: `all` → `any` moves a file out silently.
- **`tool_log.approved_by`** ("user" / "trust" / null, migration 004). An audit
  trail that cannot tell those apart is worth much less than one that can.
- **Approval is never by voice**, by choice — a misheard "yes" would be the
  only thing between a file and deletion. That obliges the *window to come
  forward* on `confirm.request`, or hands-free use dead-ends at a dialog nobody
  can see and the 120s timeout denies it.
- **Relative paths resolve against the named folder**, not the sidecar's
  working directory, which is the repo. The local model reliably emits
  `downloads/hello.txt`, and that has to land in Downloads.
- **`listener.heard` logs the words, not `chars=42`.** The same gap already
  fixed once for `not_addressed`; leaving it here made a voice bug
  undiagnosable.

**Fifteen tools is past §7.2's cap of ~12, and that turned out to be fine.**
Measured on `qwen2.5:7b` with all fifteen: 16/17, including "create a file
named hello.txt in downloads" and correctly *no* tool for "what is the capital
of Australia". Filtering them down scored **9/17** — see the closed
relevance-selection section below before reaching for that cap again.

## Current phase
Phase 2 signed off by Eyaas after live testing (2026-08-07).
Phase 3 built and exercised against real models. Phase 4 built: name search,
find-and-open, and the semantic index. Ten tools registered.
Shell reworked 2026-08-08: sidebar rail, window controls, glass on every
surface, and a catalog that discovers models rather than listing them by hand.
**Phase 3 closed out 2026-08-09**: the seven missing tools, ToolCallCard, and
the delete acceptance gate run for the first time.
Relevance-based tool selection is **closed, measured, and not being built** —
filtering made tool choice worse (16/17 -> 9/17). See its section above.
Remaining: `organize_folder` + undo; focus_window/close_app; ToolCallCard;
Everything for whole-disk search; and the Gemini half of `measure_models.py`,
which could not run while that key is quota-exhausted.

## Phase 2 stage 1 — she speaks (2026-08-06)
kokoro-onnx on CPU, sentence-streamed. `voice_enabled` in config; weights live in
`data/models/` (~340MB, not vendored, downloaded from the kokoro-onnx releases).
Missing weights log a warning and disable voice — they never stop the sidecar.

**Synthesis cost here is `230ms fixed + ~26ms per character`**, measured end to
end with Ollama generating concurrently. Contention matters: RTF is ~0.35 when
synthesising alone and ~0.5 while the model is streaming.

That arithmetic is the whole design. `FIRST_CHUNK_MAX_CHARS` was 90 and the
opening fragment alone cost 2470ms, putting first audio at 3.5s. At 32 chars:

| reply | first audio |
|---|---|
| "Canberra." | **872ms** |
| three primary colours | 1289ms |
| two sentences on why the sky is blue | 1400ms |

**The 900ms gate is met only for short replies.** 230ms of fixed cost plus
~310ms TTFT leaves room for roughly a dozen characters, which is not a sentence.
Do not "fix" this by enlarging the first chunk — that is the thing that made it
3.5s. Faster first audio needs a cheaper voice model, not a tuning change.

Sustained playback is fine either way: RTF 0.5 means synthesis stays ahead of
speech, so once started she does not stutter.

- **Reasoning is never spoken.** `SpeechStream` reads `delta.text` and never
  `delta.thinking`; `test_tts.py` asserts it rather than assuming it.
- **Cancel emits `audio.stop`** before the task unwinds, or queued audio keeps
  talking for seconds after the stop button. Stage 3's barge-in reuses it.
- Chunks carry an index. Synthesis is dispatched per fragment, so a short one
  can finish before a long one sent earlier; the renderer plays by index and
  schedules on the WebAudio clock so sentences do not seam.

## Phase 2 stage 3 — hands free (2026-08-07)
Wake phrase, VAD and endpointing all live in the sidecar. The renderer streams
80ms frames and renders what it is told; it never decides that a phrase fired.

**She answers to "aria", and that decision is made from the transcript, not by
a wake word model.** openWakeWord ships six pretrained phrases and "aria" is
not among them, so gating on the model would have meant answering to "hey
jarvis". Instead the VAD opens capture on any speech, Whisper writes it down,
and it becomes a turn only if it starts with her name (`WakeMode.PHRASE`, the
default). "aria", "hey aria", "ok aria" and "arya"/"area" all count; the name
mid-sentence does not.

The cost is real and belongs in the open: **everything spoken near the
microphone is transcribed in order to be thrown away.** It never leaves the
machine and nothing failing the check is kept, but Whisper runs on the room
rather than only on her — roughly 450ms per utterance, and nothing at all while
nobody is speaking, because the VAD gates it. `wake_mode = "model"` is the
cheap alternative for anyone who would rather say "hey jarvis"; it costs a
fraction as much CPU and never transcribes what was not for it.

Measured end to end on synthesised speech, phrase mode: 6/6 correct — three
"Aria, ..." answered with the name stripped, three ignored including "I was
reading about the aria in that opera", where the name is present but not first.
End of speech to turn: 470-520ms.

    python scripts/fetch_wakeword.py     # ~3.5MB of ONNX, not vendored
    python scripts/gate_wakeword.py      # the machine-checkable part of the gate

**Always-on costs 2.5% of one core**, which is the whole reason it is viable:

| | load | per frame | realtime |
|---|---|---|---|
| openWakeWord `hey_jarvis` (ONNX) | 127ms | 1.68ms / 80ms | 2.1% |
| Silero VAD | 173ms | 0.14ms / 32ms | 0.4% |

- **`webrtcvad` (§4) is not used and cannot be.** It ships source-only and its
  C extension needs MSVC; `pip install webrtcvad==2.0.10` fails here. faster-
  whisper already bundles Silero VAD as ONNX — the same model `vad_filter=True`
  runs — so `providers/vad.py` uses that. No new dependency, no compiler, and a
  neural detector rather than a GMM. Do not re-add webrtcvad.
- **openWakeWord must be told `inference_framework="onnx"`.** Its default is
  tflite and `tflite-runtime` is marked `platform_system == "Linux"`, so the
  default fails on Windows. Model paths are passed explicitly too, or it
  downloads weights mid-conversation.
- **Its `[full]` extra pulls torch** (rule 3). The base install does not — it is
  onnxruntime, scipy, scikit-learn. Never install the extra; it is for training
  new wake words.
- **Phrase mode needs no downloaded weights**, only the VAD and the recogniser
  stage 2 already loads. Model mode falls back to phrase mode when its weights
  are absent, rather than leaving hands-free unavailable — being able to talk
  to her matters more than which phrase opens the conversation.
- **The UI never hardcodes the phrase.** `voice.listen` returns it, because
  which one is live depends on the mode and a label naming the wrong one is
  worse than no label.
- **Hands-free is on by default**, at Eyaas's explicit request (2026-08-07):
  reaching for a key before speaking is the thing it exists to remove. It was
  briefly off-by-default on privacy grounds; that was overruled, and the
  compromise is that it stays *visible* rather than quiet — Windows shows its
  indicator, the header switch says "Listening" in words, and turning it off
  persists so the answer is not re-asked.
- **The renderer must act on the persisted setting, not just read it.** The
  sidecar remembers the answer but owns no microphone, so `useHandsFree` opens
  the device itself when `voice.listen` comes back enabled. Without that the
  setting was stored and then silently ignored, and hands-free needed a click
  on every launch — which is exactly the complaint that prompted the change.
- **Frames go over a JSON-RPC *notification*, not a call.** 12.5 a second with a
  reply each would be 12.5 round-trips a second to hear "received". `notify()`
  exists on the bridge for exactly this and drops frames when the socket is
  closed, which is correct — a frame is only useful immediately.
- **`VoiceAura` is driven by real amplitude, over a getter, not React state.**
  Both `useAudio` and `useHandsFree` expose `getLevel()`; the canvas reads it
  once a frame. Sixty renders a second to move a waveform costs more than the
  waveform. The rAF loop is *cancelled* when idle, not left spinning on a
  cleared canvas — this runs next to Whisper, Kokoro and a 7B model.
- **Listening and speaking differ by direction of travel, not only hue**:
  inward for listening, outward for speaking. Colour alone does not survive a
  glance, and the orb is already carrying the hue.
- The ribbon is drawn 78px off the bottom. Lower and it hides behind the
  composer, which is what the first version did — it typechecked, looked like
  nothing, and only a screenshot showed it.
- A leading "hey jarvis" is stripped from the transcript (`strip_wake_word`).
  It arrives in the same utterance as the question and would otherwise be sent
  to the model as part of it.

### Measured (synthesised speech, `gate_wakeword.py`)
| | result | gate |
|---|---|---|
| fires on the phrase | 5/5, peak 0.73–0.95 | — |
| detection point | 127–207ms **before** the phrase's audio ends | orb <300ms |
| false positives | 0 over 20s of near-miss speech + 60s of silence | 0 in 1 hour |
| barge-in decision | 480ms of speech | — |
| barge-in compute | 18ms | <150ms |

The near-miss set matters more than the count: "Travis said he would call
back", "Harvest season starts", "Jarvis is a character in those films" and
"Hey, can you pass me that?" all score below threshold.

**Two of the gate's numbers are not measured and cannot be here.** "20 triggers
with under 2 false negatives" and "1 hour idle with no false positive" need a
person speaking across a real room into a real microphone; synthesised speech at
zero distance says nothing about either. The script says so rather than
reporting a pass.

**Barge-in is the one piece that depends on hardware.** The microphone hears her
own voice out of the speakers. The renderer asks for echo cancellation and the
listener requires a sustained 300ms run rather than one frame, but on a machine
with the speakers facing the microphone it can still trip — `barge_in_enabled`
turns it off without touching the wake word. The 480ms figure is *by design*:
300ms of sustained speech plus the VAD's own ramp. The 150ms budget is about how
fast audio stops once the decision is made, which is the renderer's flush.

## The screen overlay — her presence with the window closed (2026-08-07)
`Ctrl+Space` means "put the chat away", not "turn her off". Hidden, she still
listens, and a second window glows around the edge of the display while she
listens or speaks, with a caption showing what was asked and answered.

- **`backgroundThrottling: false` is not optional and not sufficient.** Chromium
  suspends renderers nobody is watching, and the microphone lives in one. The
  per-window flag does not stop the *renderer-process* backgrounder, so
  `main.ts` also appends `disable-renderer-backgrounding`,
  `disable-background-timer-throttling` and
  `disable-backgrounding-occluded-windows` before `whenReady` — appended after,
  they are ignored.
- **`listener.frame_rate` is the instrument for this.** A throttled capture goes
  quiet without erroring, so "is she still hearing me" is not answerable by
  looking at the app. Measured 12.5/s sustained with the window confirmed
  hidden via `IsWindowVisible`, identical to the visible baseline.
- **The overlay shows only when the main window is hidden.** With the window
  open `VoiceAura` already says the same thing, and a glow around a window you
  are looking at is glare.
- **Its window flags are the whole risk.** Verified via `GetWindowLong`:
  `WS_EX_TRANSPARENT` (clicks pass through), `WS_EX_TOOLWINDOW` (out of
  Alt+Tab), `WS_EX_NOACTIVATE` (never takes the caret), topmost, hidden until
  needed. If any of those regress it becomes an obstacle permanently on top of
  the user's work, which is far worse than no overlay.
- **`showInactive`, never `show`** — showing activates, and activating a
  non-focusable window drops the user's caret.
- It is constructed at startup, not on first use: a window plus a page load
  does not fit in the 300ms budget between wake word and reaction.
- **No `backgroundMaterial` on it.** Acrylic requires `transparent: false` and
  this window needs a real alpha channel.
- The overlay owns no audio. The window that does publishes level and mode at
  ~30Hz over `aria:voice-level`, and sends one final zero when idle so the glow
  fades instead of freezing. Nothing is sent while she is quiet.
- `sendToRenderer` broadcasts to both windows — one conversation, two views.

## She holds a conversation now (2026-08-07)
    python scripts/gate_conversation.py    # 10/10; the baseline was 15%

**Requiring the name and the question in one breath answered 12 of 80
utterances in a real session.** 64 were dropped as "not addressed" and 4 as
empty. The cause was structural, not tuning: everyone says the name, waits to
be acknowledged, then asks — and that is two utterances, of which the first
strips to `""` and the second does not name her.

- **`ListenerState` gained `ARMED`.** Called by name → armed for 10s, any
  speech is the question. A cancellable timer falling back to `WAITING`,
  because a window that never shuts is a microphone answering the room.
- **A follow-up window briefly existed and was removed.** For 12s after an
  answer any speech became a turn, which is how she ends up answering a
  sentence meant for someone else. **Every turn needs her name.** The gate
  cases were flipped rather than deleted, so the record shows it.
- **The one-breath form still works** and is in the gate so it cannot regress.
- **Name matching is fuzzy on the first word** (`difflib`, ≤1 edit) because
  `base.en` on a single short word is unreliable. **The first letter must
  match** — without that guard "Maria" is one edit from "aria" and every Maria
  in earshot wakes her.
- **`listener.not_addressed` logs the transcript, not a character count.** The
  old log made 64 dropped utterances impossible to explain: there was no way to
  see what she had mistaken the name for. It also emits `misheard`, captioned
  dimly for 2s — silence is indistinguishable from a dead app.
- **A chime on waking**, synthesised in WebAudio (`useWakeChime`). The glow says
  the same thing only if you happen to be looking at the screen you just spoke
  at.
- Windows are constructor arguments, not constants, so tests use 50ms instead
  of sleeping ten seconds.

### Interrupting her, and the bug I reported as passing
**Barge-in never worked.** `AssistantState.SPEAKING` was read exactly once —
the barge-in guard — and **written nowhere in the sidecar**, so the branch was
unreachable. Zero `listener.barge_in` events across the whole log while Eyaas
said "Stop." over her four times.

`gate_wakeword.py` reported it passing because the script itself called
`set_state(SPEAKING)`. **A gate that supplies the precondition the product
never supplies is testing the mechanism, not the feature.** Check what writes
the state, not only what reads it.

- **The renderer reports playback** over `voice.playing`, on transitions. It is
  the only thing that knows, including for the tail still playing after
  generation ends — which is exactly when someone interrupts. `Listener` keeps
  its own `_playing` flag rather than overloading `AssistantState`, so the
  listener and the UI stop competing for one field.
- **Duck first, decide after.** Confirming "stop" needs a whole utterance plus
  a transcription — over a second, all of it with her still talking. Sustained
  speech drops playback to 20% immediately (`audio.duck`); the transcript then
  either stops her or resumes. A false alarm costs a dip that comes back rather
  than a lost sentence, and ducking makes the microphone hear the speaker
  better while it decides.
- **Only her name or a stop word cuts her off**, chosen over "any speech"
  because her own voice reaches the microphone through the speakers. Stop words
  match the *whole* utterance, so "stop by the shop later" is a sentence.
- A bare stop word sends **no turn** — "stop" is not a question. Her name arms
  her; her name plus a question answers it.

### Latency, measured and cut (2026-08-07)
    python scripts/gate_latency.py     # recognition, both models, speed and mistakes

Measured over a real session, then fixed:

| stage | was | now |
|---|---|---|
| trailing silence | 700ms | 500ms |
| recognition median | 534ms | ~307ms |
| recognition p90 | **5244ms** | serialised |
| recognition max | **34.3s** | serialised |

- **Nothing serialised Whisper.** `_lock` guarded `start()` only, so every
  utterance in the room began its own thread and they fought each other,
  Ollama and Kokoro for cores. That is the entire p90 and max. Concurrency
  never made any of them finish sooner. Utterances queued behind a newer one
  are now dropped — an old one is almost always room noise nobody awaits.
- **`tiny.en` over `base.en`, on evidence**: 307ms vs 528ms median, and *the
  same* 5/8 clips with a missed word — both fail on "pytest",
  "onomatopoeia", "Thiruvananthapuram". The corpus is synthesised speech
  though, which is cleaner than a person across a room, and tiny is the model
  that degrades first on accented input. `ARIA_STT_MODEL=base.en` reverts it.
- **The wake check reads only the opening** of utterances over 4s. The name is
  the first word, so a long stretch of room speech no longer gets transcribed
  in full purely to be thrown away. Short requests still transcribe once —
  paying twice would add ~300ms to the path the user is actually waiting on.
- **Esc stops her, claimed only while she speaks.** Saying "stop" cannot beat
  500ms of silence plus recognition; a key can. Space was asked for first and
  rejected: a global Space is swallowed mid-word in whatever you are typing.
- **A duck must always resume.** `set_playing(False)` used to clear the flag
  with no event, so finishing a sentence while ducked left the renderer's gain
  node at 20% — for that answer and every one after. 13 ducks, 0 resumes in one
  log. `_unduck()` is the single exit and `useAudio` also resets gain on a new
  answer, because that one cannot be allowed to be wrong.

### She could not hear her own name (2026-08-07)
    python scripts/gate_name.py    # every kokoro voice, name alone and in front of a question

"It doesn't respond" was never the state machine. The log showed the name
arriving as `'Hallelujah.'`, `'Ah, yeah.'` and `"Oh yeah, what's your full
name?"` — all of them "Aria", all correctly rejected, so she was never called.

- **`hotwords="Aria"` makes it worse, measured.** 24/36 with it against 32/36
  without, plus a false wake. Biasing the decoder toward the word makes it
  treat a *leading* name as context already given and drop it: "Aria, what is
  the capital of Australia?" comes back without the "Aria". It also turned
  "Ah, yeah, that makes sense." into "Aria, that makes sense.". Do not re-add
  it without re-running that gate.
- **"hay" is a greeting.** Whisper writes "Hay Area" for "Hey Aria" on four of
  six voices — the only remaining miss once the hint was dropped. With it,
  both models score 36/36 with 0 false wakes.
- **`tiny.en` is reverted.** Its accuracy win was measured on *one* synthesised
  voice, which is why the gate passed while the thing was broken. **A corpus of
  one speaker cannot measure a wake word.**
- **The synthetic gate can no longer separate the models** (both 36/36), which
  is itself the finding: it is a floor, not a verdict. The live log is what
  chose base.en.

### Two silence thresholds, not one
- Scanning the room needs only an utterance boundary (500ms). Somebody
  composing a question pauses to think, and cutting them off there is what
  makes her feel absent — so an *armed* capture allows 1100ms
  (`ARMED_TRAILING_SILENCE_MS`).
- **A false start must not disarm her.** A cough after "Aria" used to open a
  capture, produce nothing, and drop to `WAITING` with the window gone, so the
  question needed a second "Aria". `_rearm()` restores the window with whatever
  time is left.
- **Blue means she is listening to *you*.** `_begin_capture` set `LISTENING` on
  every speculative capture, so the rim lit for any noise in the room and then
  went out — saying "I heard you" to someone about to be ignored. It is set
  only once the name is confirmed, or when the wake *model* fires, which is
  its own confirmation.

## Phase 3 — the tool contract (2026-08-07)
Six tools so far, one per tier boundary: `list_windows`, `get_system_info`
(T0), `open_app`, `set_volume` (T1), `move_file` (T2), `delete_file` (T3).

- **A confirmation timeout resolves to DENIED.** §7.1's words, and the whole
  safety property — somebody who walked away has not agreed to anything.
  Mutation-checked: flipping that one return fails four tests and logs
  `tool.ran ok=True tier=3 tool=obliterate`.
- **DANGER is off by default *and absent from `schemas()`*.** The model is not
  told those tools exist, which is stronger than asking it not to use them.
- **Schemas are derived from type hints and the docstring**, never written
  twice (§7.2). `ctx` is excluded — offered as a field, models try to fill it.
- **Only `summary` goes back into the context**, never `data` or `display`.
  §7.2 names pasting tool output into the prompt as the #2 failure mode.
- **The continuation pass is not offered tools again.** One tool per turn until
  Phase 6; a model handed its own tools straight after using one will loop.
  Extra calls in a single response are dropped and the model is told so.
- **`pycaw`'s API changed**: `GetSpeakers()` returns a wrapper with
  `.EndpointVolume`, so every `Activate(IID, CLSCTX_ALL, None)` example online
  now fails with `'AudioDevice' object has no attribute 'Activate'`.
- **`registry.clear()` needs `snapshot`/`restore` in tests.** A bare clear left
  the real tools missing for every later test — passed alone, failed in the run.
- **Cloud providers call tools too.** They were built accepting-and-ignoring
  `tools`, and the result was her telling Eyaas "I cannot check the running
  processes" — routed to Gemini Flash Lite, which had been handed the tools and
  dropped them. Denying a capability she has is worse than not having it.
  - OpenAI streams a tool call in *fragments* — name in one frame, argument
    JSON a character at a time — so they are accumulated and emitted whole.
  - Gemini nests differently from everyone else: one `tools` entry holding
    every `functionDeclarations`, and the OpenAI wrapper unwrapped to the
    function itself. Replies carry `functionCall` parts.
- **The prompt has two capability paragraphs, and using the wrong one is
  visible.** `_GROUNDING_TEMPLATE` in `core/context.py` said "you have no
  tools… you cannot run programs" long after Phase 3 gave her some — she opened
  Calculator and then told Eyaas she could not run programs, reading her own
  instructions back over what she had just done. `stable_prefix(has_tools=...)`
  now picks. **Only that paragraph changed**: the rest of the block took
  qwen2.5:7b from 57% fabrication to 27%, so the anti-invention clauses stay.
  Both variants are resolved at import, so the KV prefix is still constant.
- **`os.startfile` only finds PATH.** Notion, Calendar and most of what people
  name are Store or Electron apps with no executable anywhere. `open_app` now
  falls back to `Get-StartApps` (214 entries here) and launches through
  `explorer.exe shell:AppsFolder\<AppID>`. The index is cached, and a miss
  refreshes it once in case the app was installed since. Match order is exact,
  then prefix, then substring, shortest name winning — substring first would
  open "Calculator Help" ahead of "Calculator".
- **A tool turn is not a text turn, and getting that wrong is invisible until
  she contradicts herself.** She opened WhatsApp and said "I cannot open
  WhatsApp directly": Gemini was receiving her own tool call as an *empty model
  turn* and the result as a plain user message, so it never learned it had done
  anything. Gemini needs `functionCall` / `functionResponse` parts (and the
  response must be an object, not a bare string); OpenAI needs `type:
  "function"`, an `id`, and arguments as a **JSON string** where Ollama wants
  an object — one shared `to_wire` cannot serve both.
- **Gemini requires `thoughtSignature` echoed back** on a replayed
  `functionCall`, or it rejects the follow-up outright: *"Function call is
  missing a thought_signature in functionCall parts"*. `ToolCall.signature`
  carries it opaquely for every provider.
- **`open_app` matches on a scorer, and the bands are ordered by how badly
  each can go wrong** — exact, then shared words, then prefix, then substring,
  then run-together spelling, then edit distance last. Measured 29/29 on names
  said the way people say them (`scripts/gate_apps.py`), against 20/24 for the
  if-ladder it replaced. The four it used to miss were a hyphen ("7 zip"), a
  number word ("seven zip") and two typos — one of which Eyaas typed unprompted.
- **`MATCH_FLOOR` is what stops nonsense resolving to something.** Opening the
  wrong app is worse than opening nothing.
- **"Help" and "Uninstall" entries are demoted**, but only when the user did not
  ask for them: "7 zip" matched "7-Zip Help" over "7-Zip File Manager" purely
  because Help is the shorter name, while "7 zip help" must still find it.
- **Three sources, merged and cached**: `Get-StartApps` (214), registry
  `App Paths` (+42), and PATH. Each entry carries how to launch it, because
  the three need different launchers.
- **`_ALIASES` is a fallback, never a rewrite.** It used to replace the query
  before matching, so "terminal" became "wt" and the real "Terminal" entry was
  never considered — an alias could make matching *worse*.
- **A miss names the near misses.** "I could not find X" is a dead end; the
  closest three let the model or the user retry immediately.
- **Exact beats fuzzy, or she opens the wrong thing.** "open youtube" matched
  the *YouTube Music* app by prefix. Order is now: exact app, exact website,
  then fuzzy app — so "youtube" opens the site, "youtube music" opens the app,
  and "spotify" still opens the app rather than the web player.
- **Measured against the real APIs**, not assumed: gemini-flash-lite calls
  `list_windows`; qwen2.5:7b is 4/4 including correctly *not* calling a tool
  for "what is the capital of Australia". OpenAI could not be verified — that
  account returns "Your account is not active".
- Relevance-based tool selection is **sequenced, not skipped**: the cap is ~12
  and there are six, so it lands with the remaining tools. It needs
  `nomic-embed-text` (274MB, not pulled) on the turn path.

## Measuring answer quality
Two suites, both mechanical — no model grades another model.

    python scripts/eval_quality.py                     # both suites, local models
    python scripts/eval_quality.py --suite hallucination --all-models
    python scripts/soak_conversation.py                # 30-turn contamination soak

Run them before and after any prompt, persona or model change.

**Always read `fabricated` and `over-refused` together.** A model that invents
nothing because it refuses everything has been broken, not fixed. The `grounded`
category is the control group and must stay at 100%.

### Measured baseline (2026-08-06, 117 probes)

| model | fabricated | overall | TTFT |
|---|---|---|---|
| `qwen2.5:7b` (local default) | 24% | 111/124 | 340ms |
| `qwen3.5:4b` | **0%** | 118/124 | 664ms |
| `gpt-4.1-mini` | 3% | — | 866ms |
| `gpt-4o` | 5% | — | 822ms |
| `gpt-5` | 0% | — | 7116ms |

- **`qwen2.5:7b` is the local default, and the battery argues against it.** Read
  the next section before changing this.
- The 7B's weakness is real but narrow: it describes non-existent packages and
  CLI flags as though they existed. `quality` bias sends substantive questions
  to cloud anyway, and its catalog caveat says so in the picker.

### The battery picked the wrong model; transcripts caught it
`PREFERRED_LOCAL` was briefly set to `qwen3.5:4b` on the strength of a 92%-vs-79%
score. Ten turns of actual conversation reversed it:

- Asked why Einstein won the Nobel for relativity, the 4B replied that he "never
  won the Nobel Prize" and that the 1921 physics prize "went instead to Henri
  Poincaré" — fluent, confident, entirely invented. The 7B answers correctly 5
  times out of 5 in near-identical words. **The check had passed the fabrication
  because it matched the substring "was not"** — it tested the *shape* of a
  correction, not the fact.
- The 4B hedges settled facts into mush: "Canberra is approximated as the
  capital. It is an approximation since official status may vary by source."
- It recites its own system prompt mid-refusal, and takes 60 words to say what
  the 7B says in eight.

None of that was visible in an aggregate score, because probes are single-turn
and the checks looked for markers rather than answers. **An aggregate over
single-turn probes is not a substitute for reading a conversation** — run
`chat` transcripts by hand before trusting a model swap. `universal_failures`
now flags prompt leakage, and the false-premise probes demand the correct
replacement fact.
- **Persona is per model and `MINIMAL` is not a downgrade.** Over 8 runs, `FULL`
  made `qwen2.5:7b` invent a breakfast *every time*; `MINIMAL` declined every
  time. Do not raise a model's level without re-running `--category honesty`
  several times.
- **The prompt is the only lever that worked.** Adding the "you have no tools /
  you know nothing beyond this conversation / never state an identifier you
  cannot verify" block to `core/context.py` took the 7B from 57% fabrication to
  27%, and false-capability from 30% to 90%.
- **Temperature does nothing for hallucination.** Swept 0.0 / 0.3 / 0.8: the 7B
  scored 57 / 57 / 54%, the 4B 16 / 30 / 16%. Flat within noise. `ModelInfo`
  carries the field, unset. Do not re-litigate this without new evidence.
- **Never set `temperature` on a reasoning model.** GPT-5, GPT-5 mini and the
  Gemini Pro preview reject any value but their default, and `openai.py`
  forwards whatever it is given. `test_catalog.py` guards this.
- **The 30-turn soak is clean.** The Phase 1 failure — an invented rotting roof
  referenced for 25 turns — does not reproduce on either local model.
- **Ollama's `qwen2.5:7b` tag already is 7.6B/Q4_K_M.** The catalog previously
  said `qwen2.5:7b-instruct-q4_K_M`, which `ollama list` never reports, so the
  model was greyed out as "not pulled" while sitting on disk.
- **Switching local models evicts the old one first** (`OllamaProvider.unload`).
  `keep_alive=30m` plus a 6GB card means two models do not fit; measured, that
  does not fail cleanly, it stalls generation for minutes and reads as a hang.
- **Smart-mode bias is a persisted setting**, not a constant: `fastest`,
  `balanced`, `quality` (default). Phase 2 should flip it to `fastest` rather
  than editing the router, which rule 10 freezes.
- `send()` with no `session_id` continues the latest session. It used to mint a
  new one per call, so any client that forgot to echo the id back lost all
  context one turn at a time. `chat.new` is the only way to start fresh.

### She has a clock, and "no tool" is not "offline"
- **Being reached over the internet is not having internet.** The OpenAI and
  Gemini APIs are text-in / text-out: no browsing, no live prices, no clock,
  knowledge frozen at training time. A cloud model fails "what is the Bitcoin
  price" for the same reason the local one does. Live data is Phase 7's
  `research(query)` over the real browser, and nothing before it.
- **The date and time are injected** by `context.machine_context()`, along with
  the answering model, session age and connectivity. All facts the process
  already holds — no query, no probe on the turn path.
- **Rendered to the minute, never the second.** This block sits before the
  conversation, so a string that changed every turn would invalidate the KV
  cache for every turn after it (~1s). Turns are seconds apart, so consecutive
  turns share the prefix. Measured after: 292–387ms on turns 2+.
- `providers/connectivity.py` caches reachability on a 60s timer, so she can
  tell "I have no web tool" from "you are offline". Reads never touch the
  network — §9.7 is explicit that probing per turn would put a round-trip in
  front of every reply.
- **A refusal names the limit once, then points somewhere.** "I cannot check the
  current price of Bitcoin." is true and worth nothing. The `helpful-refusal`
  category enforces this; both local models pass 4/4.

### Writing probes: the checks lie before the model does
Most "failures" in the first passes were bugs in the checker, not the model.
Verify a new check against known-good *and* known-bad strings before believing
a score. Ones that actually bit:
- GPT-5 writes `don’t` with U+2019. Every `don'?t` pattern missed it and scored
  a perfect refusal as a fabrication — 78% vs the real 0%. `probes.normalise()`
  now folds punctuation before matching.
- Correcting a false premise requires negation, so premise probes read as
  refusals. They have their own `Expect.CORRECTION` and are excluded from the
  over-refusal metric.
- Reasoning tokens count against `max_tokens`, so GPT-5 returned empty strings
  and scored them as inventions.
- OpenAI's quota error does not contain the string "429"; detect rate limiting
  on `ProviderRateLimited`, not on message text.

## Closed: TTFT does *not* scale with conversation length (re-measured 2026-08-06)
This was recorded as a blocker — median 1720ms, p95 3183ms, "+0.8ms per
conversation token", "Phase 2 must decide before voice". **Re-measured on the
current build, it is not reproducible.**

| turns | prompt tokens | TTFT |
|---|---|---|
| 1 | 495 | 611ms |
| 9 | 1,102 | 429ms |
| 17 | 1,804 | 478ms |
| 29 | 2,895 | 498ms |
| — | 5,407 | 431ms |

Median **483ms**, p95 **611ms** over a real 30-turn conversation where each turn
appends to the prefix. Growth is **+0.03ms per token**, flat inside the noise.

Two reasons the old number was wrong. The default was `qwen3.5:4b` then — a
reasoning model that pays for reasoning on every turn even with `think=false`.
And Ollama's KV cache means a growing conversation prefills only the *new*
message, not the whole history, so length is nearly free as long as the prefix
is byte-identical. That is exactly what the stable-first ordering buys.

**The remaining latency cliff is roll-up, not length.** `_summarize` is a second
model call, and it used to run inline on the turn that crossed the budget. It is
now a background job (see `_maybe_roll_up`), so the turn that triggers it is not
the turn that pays for it. Do not move it back onto the critical path: voice has
a ~1000ms end-to-end budget and a second model call does not fit in it.

## The catalog is measured; discovery is only a listing (2026-08-08)
`providers/discovery.py` asks OpenAI and Gemini what the account can reach.
**Discovery is a filtering problem, not a fetching one.** Measured against the
live APIs: OpenAI returns **124** models, Gemini **58**, and most cannot hold a
conversation — embeddings, Whisper, TTS, image, Sora, moderation. After
filtering: 32 and 16.

- **Gemini's `generateContent` flag is not a sufficient filter.** It is set on
  Lyria (music), Nano Banana (image), the TTS previews, `gemini-robotics-er-*`
  and Deep Research. Reject by name as well.
- OpenAI returns `{id, created, owned_by}` and nothing else — no context window,
  no modality. Every judgement is made on the id, which is why the filters are
  tested against **real payloads** in `tests/fixtures/`, not a mock that agrees
  with whatever the filter happens to do.
- Dated snapshots (`gpt-4o-2024-08-06`) and Gemini's `-001` / `-preview` aliases
  collapse **only when the plain id is also present** — otherwise dropping them
  removes the model rather than de-duplicating it.

**Discovered models sit beside `CATALOG`, never inside it.** `get()`/`require()`
read the overlay so an explicit choice resolves; **`by_class()` does not**, and
that is the router's only way to reach for a model. So Smart mode keeps routing
among models measured here — hand-pick-only is a property of the data structure,
not a flag. Mutation-checked: pointing `by_class` at `all_models()` fails
`test_smart_never_routes_to_a_discovered_model`.

**Nothing invents a measurement.** `best_for`, `caveat`, `ttft_ms_seed` and
`cost` come from measurement; a discovered model has none, so it gets `Cost.
UNKNOWN`, no blurb, and `MINIMAL` persona. The picker shows blanks — an early
version fell through to `cost` and rendered a column of `?`. Curated ids win on
collision, so `gpt-5` keeps its caveat when the API returns it as a bare id.

Never on the turn path (§10, ~1000ms voice budget): cached in `settings`, loaded
at startup, refreshed only when stale (24h), behind the button, or after a key
is added.

## "Apps open well for Flash Lite, not other models" — it was the matcher (2026-08-09)
Two things, and the models were neither. **Smart *is* Flash Lite for these
turns**: in `quality` bias every non-trivial message went to the FAST class,
ranked by latency, which flash-lite always won.

The rest was `tools/apps.py`. Probed five models with the real prompt and the
real 15 schemas — **every one picks `open_app` correctly, 6/6**. They differ in
the *argument*, and the matcher substituted:

| said | matcher opened |
|---|---|
| `notepad++` | **Notepad**, on every model |
| `browser` | **LockDown Browser** (0.88); the default is Brave |
| `music` | YouTube Music |
| `email` | Mail |

- **`normalise("notepad++")` is `"notepad"`**, an exact 1.00 against a different
  program — so she opened one and reported the other. Only `+` and `#` name a
  different product; hyphens and dots stay noise, or the 7-Zip cases regress.
  The guard is **one-directional**: "notepad" may mean Notepad++ and ranking can
  decide; "notepad++" cannot mean Notepad.
- **A category is not a name.** Windows already knows which program answers
  "browser" — it is the handler the user chose. Read `UserChoice`, resolve the
  ProgId through **`HKEY_CLASSES_ROOT`** (the merged view associations actually
  resolve through). Checked *after* exact, so "chrome" still opens Chrome.
- Some ProgIds carry no readable name — the music handler's `ApplicationName`
  is an unresolved `@{…ms-resource…}` and its default value is empty, which
  showed the literal `AppXqj98qxeaynz6…` as what was opened. Borrow the Start
  menu's label for the same target.
- One prompt line telling her to pass a category phrase through unchanged. It
  is what Flash Lite already did and the others did not, so it lifts the
  weakest model rather than the best.

After: all four models agree. `gate_apps.py` **37/37**, up from 29.

## Smart mode routed real work to the cheapest model (2026-08-09)
Measured: **"write me a python script to sort a file" → `gemini-flash-lite`.**
`_CODE_HINTS` wanted a code fence or a literal `def `/`import `/`class`, and
**`_quality_first` never consulted `_DEEP_VERBS` at all**. Both fixed;
`_WRITES_CODE` catches the plain-English form, and named languages and file
extensions count as code hints. In `fastest`, the code check now runs **before**
the short-message shortcut — "fix this python script" is 22 characters and a 7B
answer to it is worth nothing. Mutation-checked.

## Adopting a discovered model costs a measurement (2026-08-09)
    python scripts/measure_models.py --models gpt-5.4-mini,gpt-5.4-nano

| model | TTFT | battery | fabricated | over-refused | |
|---|---|---|---|---|---|
| `gpt-5.4-nano` | **700ms** | 76/83 | **0** | 0 | adopted |
| `gpt-5.4-mini` | 960ms | **78/83** | 2 | 0 | adopted |
| `gpt-5.6-luna` | 1177ms | 74/83 | 3 | 1 | **rejected** |
| `o4-mini` | 1619ms | 69/83 | 7 | 2 | **rejected** |

**The newest model lost.** Both rejections failed the `grounded` category — the
control group, plain facts they should simply know. Reading the aggregate alone
would have adopted luna at 74/83; that is the `qwen3.5:4b` mistake exactly.

`gpt-5.4-nano` at 700ms replaces `gemini-flash-lite` (1236ms) as what Smart
reaches for first — faster *and* the only model that fabricated nothing.

**Adoption means moving into `CATALOG` by hand**, which is what makes a model
routable. `by_class` is untouched, so the hand-pick-only property still holds.

**The Gemini free tier is quota-exhausted** — 429 on a one-word call to
flash-lite. Not a bug here; the whole Gemini half of the battery could not run.

## Phase 3 finished — the rest of the tools, and a flag that never worked (2026-08-09)
Twenty-five tools. Added: `focus_window`, `close_app` (T1/T2), `list_processes`
(T0), `kill_process` (T2), `set_wifi` (T2), `run_powershell` (T1),
`read_clipboard` (T0), `write_clipboard` (T1).

- **`pywinauto` is still not a dependency and does not need to be.**
  requirements.txt deferred it twice for `focus_window`/`close_app`
  specifically; `pywin32` does both. `WM_CLOSE` is also the *better* close — it
  is what the X button sends, so the app prompts about unsaved work instead of
  being destroyed.
- **The foreground lock is real**: Windows refuses `SetForegroundWindow` from a
  background process, which the sidecar always is. `AttachThreadInput` for the
  duration of the call gets through it. **And the success check has to poll** —
  reading `GetForegroundWindow` immediately after returned the *old* window and
  reported failure for a raise that had plainly worked.
- **`run_powershell`'s allowlist is the security boundary, not its tier.** The
  first token must be one of fifteen `Get-` cmdlets, and any of
  ``|;&><$`(){}[]#'"`` or a newline refuses the whole string — so no
  `Get-Process | Stop-Process`. Fifteen escape attempts are a parametrised test
  and none get through. Refuse rather than sanitise; sanitising is where these
  go wrong.
- **`kill_process` refuses `lsass`, `csrss`, `services`… below the tier
  system.** Being allowed to ask is not the same as it being sane to permit —
  killing `lsass` bluescreens the machine.
- **`read_clipboard` is `local_only`, a new field on `Tool`.** `_PRIVATE`
  decides from the user's *words*, before the tool runs: "what did I just copy"
  did not match it, routed to a cloud provider, and that provider would have
  been handed the clipboard on the continuation. So the swap to the local model
  happens **after** the call, in `_continuation_model`, because the
  continuation is where the result enters a prompt. Mutation-checked both ways.
- **`ToolCallCard` finally consumes `tool.call`/`tool.result`**, which the
  sidecar had broadcast since Phase 3 with nothing listening. A turn that
  opened an app looked identical to one that talked about opening it — which is
  also how "Opened Calculator" followed by "I cannot run programs" survived a
  whole phase.

**`allow_danger_tools` was dead code end to end.** It let `PermissionEngine`
*execute* a DANGER tool, but `_tool_schemas()` always asked `schemas()` for the
`CONFIRM` ceiling, so the model was never told `delete_file` existed and
nothing could ever request one. Asked to delete a real file with the flag on,
she answered *"I cannot delete files with my current tools"* — true of what she
had been given. The ceiling now follows the flag.

### The acceptance gate, run for the first time
    ARIA_ALLOW_DANGER_TOOLS=true npm run dev
    python scripts/gate_delete.py

| | file | `tool_log` |
|---|---|---|
| **Deny** | still there | `approved=0 by=None ok=0 error=denied` |
| **Approve** | gone | `approved=1 by=user ok=1 2ms` |

It had never been run before today. `test_permissions.py` proved the *logic*;
`tool_log` held zero denied rows and no tier-3 call had ever executed.

**Known, not fixed:** a confirmation answered by one client leaves any other
connected client showing a stale dialog — there is no "resolved" broadcast.
With one window it does not bite.

**Screenshots: use `PrintWindow` with `PW_RENDERFULLCONTENT` (2)**, not
`CopyFromScreen`. A fullscreen game overrides even a topmost window, and screen
capture then photographs the game. `PrintWindow` asks the window to redraw
itself into your DC and ignores what is on top of it.

**`test_indexer.py::test_it_does_not_run_while_she_is_answering` is flaky under
load** and always has been: it waits for CPU below `BUSY_CPU_PERCENT` (60) and
this machine idles at 48–60% with the app running. Not a regression.

## Closed: relevance-based tool selection is NOT worth building (2026-08-09)
    python scripts/gate_tool_selection.py

Carried as "overdue" since Phase 3 on the strength of §7.2's ~12-tool cap. It
was never measured. Measured now, on `qwen2.5:7b` with 17 probes:

| tools offered | correct |
|---|---|
| **all 15** | **16/17** |
| a filtered 8 | **9/17** |

**Filtering makes it worse, badly.** A correct tool that was filtered out cannot
be chosen, so selection converts right answers into wrong ones — `set_volume`,
`list_windows` and `rename_file` all became "no tool at all", and
`move budget.xlsx to documents` became `open_path`.

And the selector cannot be made safe by tuning `k`. Embedding recall is
**14/15 at every size from 6 to 12**, because the one miss — `find` for "the
quotation I sent the banquet hall" — ranks **dead last of fifteen**. The
semantic-search tool scores worst for a semantic-search query, so no threshold
rescues it.

There is a third reason that needs no measurement: **tool schemas live in the
stable prefix so Ollama's KV cache can hold them.** A set that changes with the
message invalidates that prefix whenever the topic moves, so selection would
*spend* prefill rather than save it. The 1654 tokens of schemas are prefilled
once and reused; that is the whole point of stable-first ordering.

§7.2's cap is a rule of thumb. This machine's evidence overrides it. Re-run the
gate when the tool count grows — the number to watch is recall, not the cap.

## Acrylic was on, and painted over (2026-08-09)
"I asked for glass everywhere and I can't see it" was correct.
`backgroundMaterial: 'acrylic'` was set **together with an opaque
`backgroundColor: '#0a0c11'`**, which composites straight over the DWM material
and hides it completely. The acrylic was being applied and then covered on
every frame. `#00000000` is the fix.

**The 0.86 tint was measured in a world that no longer exists.** It dates from
`transparent: true` with no compositor blur, where the editor behind read
straight through. DWM acrylic blurs the backdrop itself, so legibility no
longer depends on being nearly opaque. Now 0.62.

Verified both directions rather than assumed, by putting known surfaces behind
the window: a saturated magenta form **bleeds through blurred** (so the acrylic
composites), and a white document full of black text stays **completely
unreadable through the panel** while Aria's own text stays crisp (so the tint
still does its job). If those two ever fight, readability wins and the tint
goes back up.

The dark fallback for machines without transparency effects moved into CSS
under `prefers-reduced-transparency`, where it sits *under* the tint instead of
over the material.

## Look at the UI. Typecheck and tests do not see it. (2026-08-08)
Same lesson as VoiceAura, and it bit again. `npm run typecheck`, 56 renderer
tests and 400+ sidecar tests were all green while the sidebar took **208px of a
420px window** and squeezed the conversation into a column. Only a screenshot
showed it. The rail is now icons-only whenever the window is compact — a
preference for labels cannot conjure the width to show them in.

Capturing it: find the window by title with `EnumWindows`, `SetForegroundWindow`,
then `CopyFromScreen` over its `GetWindowRect`. Guessed crop rectangles waste
turns; the window moves. `Ctrl+Space` toggles visibility, so a stray SendKeys
hides the thing you are trying to photograph — and toggles hands-free, which is
a **persisted** setting, so put it back.

## Provider strategy (decided 2026-08-06, supersedes BUILD_SPEC §4/§9.7)
Cloud is **OpenAI and Gemini via API keys**, not Anthropic. Ollama is the
offline/no-key fallback, not merely the "cheap" path.
- `providers/` gets one module per cloud vendor behind a shared interface;
  `core/router.py` picks a *provider*, not just local-vs-cloud.
- Design the Phase 1 Ollama client against that interface from the start.
  Rule 10 forbids refactoring it later, so the seam has to be right now.
- Keys go in Windows Credential Manager via `keyring` (§11), never `.env`.
  Done in Phase 1.5: `keyring` is in `requirements.txt`; `openai` and
  `google-genai` are deliberately *not* — both vendors are reached over `httpx`,
  which is two fewer dependency trees to survive PyInstaller (§2.3).
- Route indicator in the UI must name the provider, not just "cloud".

## Local model (decided 2026-08-06)
`qwen3.5:4b` for now; `qwen2.5:7b-instruct-q4_K_M` once pulled. Note `qwen3.5:9b`
is 6.6 GB and CANNOT stay resident on this 6 GB card — do not use it.

**Always send `"think": false` to Ollama.** qwen3.5 is a reasoning model: it
streams into `message.thinking` and leaves `message.content` empty until
reasoning ends. Measured with reasoning on, it produced *zero* content tokens in
200 tokens / ~6s. Consequences:
- Phase 1: read `message.content`, never `thinking`.
- Phase 2: the TTS sentence buffer must key off `content`. Never speak thinking.

## Prompt latency (measured on this machine, 2026-08-06)
Prefill costs **~480ms per 1000 tokens** here — over 3× what BUILD_SPEC §10
originally assumed. Full tables live in §10 and §8.2; the operational rules:
1. **Assemble the prompt stable-first.** Identity, voice, boundaries and tool
   schemas go before anything that changes per turn. Ollama caches the KV for an
   unchanged prefix — worth ~1s/turn. Affect, temporal context, retrieved facts
   and episodes go last, nearest the conversation.
2. Keep the pre-conversation budget near 800 tokens on local, not 2000.
3. Measure turn 2, not turn 1. Cache-busting is invisible on a first turn.

Phase 1 is unaffected — its prompt is identity + recent turns. This bites in
Phase 3 (tool schemas) and Phase 5 (retrieval).

## Phase 0 notes for later phases
- Python is **3.11** in `.venv`. `sidecar.ts` resolves it via `ARIA_PYTHON` env,
  then `.venv\Scripts\python.exe`, then bare `python`.
- `requirements.txt` grows one phase at a time; the deferred BUILD_SPEC §4 pins
  are listed in a comment block there with the phase that introduces each.
- Auth token flows Electron → sidecar via `ARIA_TOKEN` (not sidecar → file →
  Electron as §7.1 describes) to avoid a stale-token race on restart. The
  sidecar still writes `data/.handshake` for standalone runs.
- `system.health` returns every §9.6 field; unprobed ones are `null` and named
  in `pending_probes`. Fill in your phase's probe, don't change the shape.
- Two log files: `sidecar.log` is structlog JSON from inside Python;
  `sidecar.out.log` is the child's raw stdout/stderr captured by Electron.
- New JSON-RPC methods: register with `@method("name")` in `rpc/handlers.py`.
  Unregistered methods return -32601 rather than a stub.
- **Vite hot-reloads the renderer; the sidecar is spawned once.** Python edits
  need "Restart Brain" in the tray (or killing the process — Electron respawns
  it). A new method lands as *"Unknown method 'x'. Available in this build: …"*,
  which is the old process answering, not a registration bug. `sidecar.ready`
  logs the method list at startup — compare it before reading further.
- The venv's `python.exe` spawns the base interpreter as a child on Windows, so
  `Started server process [pid]` names a pid whose exe is `…\Python311\`, not
  `.venv\`. That is the venv launcher and it is normal; site-packages still
  resolve to the venv.