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
Phase 1.5 complete (multi-provider routing, model control, quality fix).
Next: Phase 2 — Voice. Update this line when a phase's acceptance gate passes.

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

| model | fabricated | quality | TTFT |
|---|---|---|---|
| `qwen2.5:7b` (local default) | 32% | 41/41 | 325ms |
| `qwen3.5:4b` | **5%** | 40/41 | 560ms |
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

## Open issue from Phase 1: TTFT scales with conversation length
The gate ("first token < 700ms, warm model, **short prompt**") passes at
405–531ms. But measured across a 35-turn run, median TTFT was **1720ms** and p95
**3183ms** — because every turn re-prefills the whole conversation.

The KV cache helps but does not flatten it: 593ms at 59 prompt tokens rising to
927ms at 445. Roughly +0.8ms per conversation token.

Consequence: sub-700ms is only reachable for *short* conversations. Holding it
across a long one would need `context_token_budget` near 400 tokens, which is
about four turns — not a real conversation. The current 6000 (per §9 Phase 1)
gives ~3.4s by the time it fills.

Unresolved, deliberately. It is a real trade-off between §1's "latency over
intelligence" and coherence, and it is Eyaas's call, not a silent retune.
Options: lower the budget, roll up far more aggressively, or accept ~1.5s in
long sessions. Phase 2 must decide before voice, where the budget is ~1000ms
end-to-end.

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