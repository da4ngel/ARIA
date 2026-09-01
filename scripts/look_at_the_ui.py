"""Look at the UI, without taking over anybody's screen.

    npm run dev                        # in another terminal, serving :5173
    python scripts/look_at_the_ui.py   # writes PNGs beside this script


CLAUDE.md's oldest open item is "the UI has still not been looked at", and the
usual way — run the app and photograph the window — needs the window visible,
which means taking over the desktop of whoever is using the machine.

This loads the same renderer the app loads (Vite is already serving it) into a
headless Chromium with a **stubbed `window.aria`**, so every panel can be
opened and photographed deterministically. What it cannot show is anything
that depends on Electron itself — acrylic, the window chrome, the tray. What
it can show is layout, colour, contrast and whether a panel renders at all,
which is what three sessions of unseen work actually needs checking for.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "data" / "ui-shots"

#: **The one thing a browser cannot supply: something behind the glass.**
#: `glass` is `rgba(9, 18, 14, 0.62)` and Electron paints it over DWM acrylic,
#: which blurs the desktop. A browser's default white page under a 62% tint
#: reads as flat grey and makes the whole app look like a different colour
#: than it is. This stands in for the blurred desktop.
#: One message carrying every construct at once, including the two that
#: only ever go wrong while streaming: a fence that has not closed, and a
#: URL long enough to widen a column that is not capped.
TORTURE = "\n".join([
    '# Heading one, which renders at the same step as two',
    '',
    '## Heading two',
    '',
    'Ordinary prose with **bold**, *italic*, ***both***, ~~struck through~~',
    'and `inline code` in it. A very long unbroken URL, which must not widen',
    "column: https://example.com/" + "a" * 180,
    '',
    '### Heading three',
    '',
    '1. An ordered item with `code` inside **bold** inside it, long enough that',
    '   it wraps and the second line aligns to the text, not to the number.',
    '2. A second item.',
    '   - A nested item, which steps in but never down in size.',
    '     - And a third level.',
    '3. A third item.',
    '',
    '#### Heading four, carried by weight alone',
    '',
    '> A blockquote containing a list:',
    '>',
    '> - first quoted point',
    '> - second quoted point',
    '',
    '| Model | Provider | TTFT | Notes |',
    '| --- | --- | --- | --- |',
    '| qwen2.5:7b | ollama | 340ms | local, free |',
    '| gpt-5.4-nano | openai | 700ms | fabricated nothing in the battery |',
    '| gemini-flash-lite | gemini | 1236ms | quota-limited on the free tier |',
    '',
    '---',
    '',
    '```python',
    'def solve(n: int) -> int:',
    "    'Three code blocks, three languages.'",
    '    return sum(i * i for i in range(n))',
    '```',
    '',
    '```powershell',
    "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'aria.exe' }",
    '```',
    '',
    '```sql',
    'SELECT subject_id, name, level FROM concept_mastery WHERE level < 3;',
    '```',
    '',
    'A [link](https://example.com), a [refused one](javascript:alert(1)), and',
    'an unterminated fence below:',
    '',
    '```typescript',
    'export function splitBlocks(text: string): string[] {',
    "  const lines = text.split('\\n')",
])

GROUND = "html { background: #0b1410 !important; }"
def _chromium() -> str | None:
    """Playwright's own Chromium, whichever build is installed.

    Its Python package pins a version in `executable_path` that may not be the
    one on disk — resolving the directory by glob is what makes this work on a
    machine where the browsers were installed by a different release.
    """
    root = Path.home() / "AppData/Local/ms-playwright"
    for build in sorted(root.glob("chromium-*"), reverse=True):
        for name in ("chrome-win64/chrome.exe", "chrome-win/chrome.exe"):
            if (build / name).is_file():
                return str(build / name)
    return None

# A bridge that answers everything the panels ask for, with enough shape that
# each renders its populated state rather than its empty one.
BRIDGE = r"""
(() => {
  const listeners = { event: [], log: [], max: [], mode: [] };
  const sub = (bag) => (h) => { bag.push(h); return () => {}; };
  const now = new Date().toISOString();

  const M = (id, provider, label, klass, cost, local) => ({
    id, provider, label, klass, cost, local,
    persona: local ? 'minimal' : 'full',
    best_for: local ? 'quick local answers' : 'harder questions',
    ttft_ms_seed: null, caveat: null, context_tokens: local ? 8192 : 200000,
    discovered: false, benchmark_index: null, trains_on_data: false,
  });

  const answers = {
    'system.health': { status: 'ok', version: '0.1.0', uptime_s: 42, db: true,
                       ollama: true, models: ['qwen2.5:7b'], everything: false,
                       gpu_free_mb: 4096, pending_probes: [] },
    'chat.history': { messages: TORTURE_TEXT
      ? [{ id: 1, role: 'user', content: 'show me everything' },
         { id: 2, role: 'assistant', content: TORTURE_TEXT }]
      : [] },
    // Needed for the streaming replay: `useConversation` will not accept
    // a token whose turn id it does not recognise.
    'chat.send': { turn_id: 't1', session_id: 's1' },
    'chat.sessions': { sessions: [
      { id: 's1', title: 'Why is the sky blue', started_at: now, kind: 'chat', message_count: 6 },
      { id: 's2', title: 'Information Security', started_at: now, kind: 'study',
        message_count: 12, study_subject_id: 1 },
    ] },
    'models.list': { selected: 'qwen2.5:7b', bias: 'quality', models: [
      { model: M('qwen2.5:7b', 'ollama', 'Qwen 2.5 7B', 'fast', 'free', true),
        available: true, reason: null, observed_ttft_ms: 340 },
      { model: M('gpt-5.4-nano', 'openai', 'GPT-5.4 nano', 'fast', '$', false),
        available: true, reason: null, observed_ttft_ms: 700 },
      { model: M('gemini-flash-lite-latest', 'gemini', 'Flash Lite', 'fast', '$', false),
        available: false, reason: 'No Gemini key stored.', observed_ttft_ms: null },
      { model: M('gpt-5', 'openai', 'GPT-5', 'smart', '$$$', false),
        available: true, reason: null, observed_ttft_ms: 7116 },
    ] },
    'settings.keys': { keys: [
      { key: 'openai_api_key', present: true, hint: '••••' },
      { key: 'gemini_api_key', present: true, hint: '••••' },
      { key: 'openrouter_api_key', present: false, hint: null },
      { key: 'bedrock_api_key', present: false, hint: null },
      { key: 'tavily_api_key', present: true, hint: '••••' },
      { key: 'brave_api_key', present: false, hint: null },
    ] },
    'settings.online': { enabled: true, backend: 'tavily', key_present: true },
    'browser.setup': { cdp_reachable: false, launcher_exists: true,
                       launcher_path: 'C:\\Users\\x\\ARIA\\data\\start_chrome_debug.bat',
                       detected_browser: 'Brave' },
    'models.bedrock': { credential: 'api_key', region: 'eu-west-2' },
    'tools.list': { mode: 'auto', allow_danger: false, trusted: ['C:\\Users\\x\\Downloads'],
      tools: [
        { name: 'read_file', tier: 0, description: 'Read a text file.' },
        { name: 'write_file', tier: 2, description: 'Write a file, asking first.' },
        { name: 'delete_file', tier: 3, description: 'Delete a file.' },
        { name: 'research', tier: 1, description: 'Search the web and read pages.' },
      ] },
    'memory.list': { embeddings_ready: true, facts: [
      { id: 1, subject: 'user', predicate: 'works_on', object: 'Sillara pricing',
        score: 0.91, source: 'user', pinned: true, evidence_count: 4, active: true },
      { id: 2, subject: 'user', predicate: 'prefers', object: 'short answers',
        score: 0.74, source: 'reflection', pinned: false, evidence_count: 2, active: true },
    ], episodes: [
      { id: 1, summary: 'Discussed data science interview skills', salience: 0.6,
        started_at: now, session_id: 's1' },
    ], stats: { facts: 2, episodes: 1, degraded: 3, empty: 9, p90_ms: 72 } },
    'study.subjects': { subjects: [
      { id: 1, name: 'Information Security', covered: 4, total: 22,
        source_path: 'D:\\lectures\\intro.pptx', last_studied_at: now },
      { id: 2, name: 'Transport Protocols', covered: 0, total: 8,
        source_path: null, last_studied_at: now },
    ] },
    'study.state': { subject: 'Information Security', subject_id: 1, covered: 4, total: 22,
      concepts: [
        { id: 1, name: 'CIA Triad', level: 5, asked: 6, correct: 6 },
        { id: 2, name: 'Threat modelling', level: 2, asked: 4, correct: 2 },
        { id: 3, name: 'Key exchange', level: 0, asked: 0, correct: 0 },
      ], next: 'Threat modelling' },
    'study.sessions': { sessions: [
      { id: 's2', title: 'Information Security', started_at: now, kind: 'study',
        message_count: 12, study_subject_id: 1 },
    ] },
    'files.browse': { path: 'C:\\Users\\x\\Documents', parent: 'C:\\Users\\x',
      entries: [
        { name: 'lease.pdf', path: 'C:\\Users\\x\\Documents\\lease.pdf', is_dir: false,
          size: 184320, modified: now },
        { name: 'Invoices', path: 'C:\\Users\\x\\Documents\\Invoices', is_dir: true,
          size: 0, modified: now },
      ] },
    'clipboard.history': { watching: true, skipped_secrets: 2, entries: [
      { id: 3, content: 'https://github.com/anthropics/claude-code', chars: 44,
        copied_at: now, source: null },
      { id: 2, content: 'SELECT * FROM concept_mastery WHERE level < 3;', chars: 46,
        copied_at: now, source: 'DBeaver' },
    ] },
    'reminders.list': { reminders: [
      { id: 1, text: 'check the oven', due_at: now, delivered_at: null },
    ] },
    'usage.since': { turns: 214, local: 120, cloud: 94, prompt_tokens: 481233,
      completion_tokens: 20144, uncounted: 12, unpriced_turns: 94, cost_usd: 0.0,
      prices_as_of: '2026-08-24' },
    'undo.list': { entries: [
      { id: 4, kind: 'write_file', target: 'C:\\Users\\x\\Downloads\\notes.txt',
        at: now, undone_at: null, restorable: true },
      { id: 3, kind: 'delete_file', target: 'C:\\Users\\x\\Downloads\\old.txt',
        at: now, undone_at: null, restorable: false },
    ] },
    'setup.done': { done: WIZARD },
    'setup.state': {
      ollama: { installed: true, running: true, models: ['qwen2.5:7b'] },
      everything: { present: false },
      voice: { present: false, missing: ['kokoro-v1.0.onnx'], approx_bytes: 353746785 },
      wake_word: { present: false, missing: ['hey_jarvis_v0.1.onnx'], approx_bytes: 3500000 },
      keys: [{ key: 'openai_api_key', present: true }],
      models_dir: 'C:\\Users\\x\\AppData\\Local\\ARIA\\data\\models' },
    'voice.wake_threshold': { available: true, threshold: 0.5, default: 0.5, mode: 'model' },
    'voice.listen': { available: true, enabled: false, phrase: 'aria' },
    'permissions.mode': { mode: 'auto' },
  };

  // Lets the replay push real `token` events down the real path, rather
  // than rendering the component in isolation and calling it streaming.
  window.__emit = (method, params) =>
    listeners.event.forEach((h) => h({ method, params }));

  window.aria = {
    getStatus: () => Promise.resolve('connected'),
    onStatus: (h) => { setTimeout(() => h('connected'), 0); return () => {}; },
    onEvent: sub(listeners.event),
    onLog: sub(listeners.log),
    onWindowMaximized: sub(listeners.max),
    onWindowMode: sub(listeners.mode),
    onVoiceLevel: sub(listeners.event),
    call: (method, params) => Promise.resolve(answers[method] ?? {}),
    notify: () => {},
    publishVoiceLevel: () => {},
    restartBrain: () => {},
    hide: () => {}, minimize: () => {},
    setExpanded: () => Promise.resolve(true),
    // **Compact is Electron's answer, not the viewport's.** `useWindowMode`
    // mirrors main rather than measuring, so resizing the page alone left
    // every 420px shot showing a 208px labelled rail the real companion
    // window never has — the exact layout bug CLAUDE.md records fixing.
    isExpanded: () => Promise.resolve(!COMPACT),
    setMaximized: () => Promise.resolve(false),
    isMaximized: () => Promise.resolve(false),
    pickFiles: () => Promise.resolve([]),
    exportDiagnostics: () => Promise.resolve('C:\\diag.zip'),
    getAutoStart: () => Promise.resolve(false),
    setAutoStart: (v) => Promise.resolve(v),
  };
})();
"""


#: One streaming replay: real `token` events down the real path, with the
#: frame clock running. The parser numbers in `Markdown.blocks.ts` were
#: measured in Node; this is the one that includes React and the DOM.
REPLAY_JS = """async (text) => {
                 const frames = [];
                 let running = true;
                 const tick = (t) => { frames.push(t); if (running) requestAnimationFrame(tick); };
                 requestAnimationFrame(tick);

                 // ~4 characters a token, which is what a real stream looks like.
                 const started = performance.now();
                 for (let i = 0; i < text.length; i += 4) {
                   window.__emit('token', { turn_id: 't1', text: text.slice(i, i + 4) });
                   await new Promise((r) => setTimeout(r, 0));
                 }
                 const elapsed = performance.now() - started;
                 window.__emit('turn.complete', { turn_id: 't1', full_text: text });
                 running = false;

                 let worst = 0;
                 for (let i = 1; i < frames.length; i += 1) {
                   worst = Math.max(worst, frames[i] - frames[i - 1]);
                 }
                 const dropped = frames.slice(1).filter((f, i) => f - frames[i] > 32).length;
                 return {
                   tokens: Math.ceil(text.length / 4),
                   elapsed_ms: Math.round(elapsed),
                   frames: frames.length,
                   worst_gap_ms: Math.round(worst * 10) / 10,
                   dropped,
                 };
               }"""


def _replay(page: object, text: str) -> dict:
    """Stream `text` into the open turn and report what the frames did."""
    return page.evaluate(REPLAY_JS, text)  # type: ignore[attr-defined]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=_chromium())
        errors: list[str] = []
        page = browser.new_page(viewport={"width": 1100, "height": 760})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}")
                if m.type == "error" else None)
        # Pass 1: the wizard, which deliberately covers everything else.
        page.add_init_script("const WIZARD = false;const TORTURE_TEXT = null; "
        + "const COMPACT = false;" + BRIDGE)
        page.goto(url, wait_until="networkidle")
        page.add_style_tag(content=GROUND)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(OUT / "00-firstrun.png"), full_page=False)
        page.evaluate("document.querySelector('.overflow-y-auto')?.scrollTo(0, 9999)")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "00-firstrun-end.png"))

        # Pass 2: the shell, with the wizard already answered.
        page.close()
        page = browser.new_page(viewport={"width": 1100, "height": 760})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.add_init_script("const WIZARD = true;const TORTURE_TEXT = null; "
        + "const COMPACT = false;" + BRIDGE)
        page.goto(url, wait_until="networkidle")
        page.add_style_tag(content=GROUND)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(OUT / "01-shell.png"))

        # The rail, section by section. Names come from `Sidebar`'s own labels.
        for label in ("Chats", "Study", "Files", "Clipboard", "Activity",
                      "Memory", "Tools", "Voice", "Settings"):
            try:
                page.get_by_role("button", name=label, exact=True).first.click(timeout=3000)
                page.wait_for_timeout(700)
                page.screenshot(path=str(OUT / f"{label.lower()}.png"))
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{label}: {type(exc).__name__}: {str(exc)[:80]}")
                page.screenshot(path=str(OUT / f"FAIL-{label.lower()}.png"))

        # Compact, the size the companion window actually is.
        page.close()
        page = browser.new_page(viewport={"width": 420, "height": 600})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.add_init_script(
            "const WIZARD = true; const TORTURE_TEXT = null; const COMPACT = true;" + BRIDGE
        )
        page.goto(url, wait_until="networkidle")
        page.add_style_tag(content=GROUND)
        page.wait_for_timeout(1200)
        page.screenshot(path=str(OUT / "02-compact.png"))

        # ── the markdown torture test ──────────────────────────────
        # Every construct at once, including the two that only go wrong while
        # streaming: an unterminated fence, and a URL long enough to widen a
        # column that is not capped.
        page.close()
        page = browser.new_page(viewport={"width": 1100, "height": 760})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.add_init_script(
            "const WIZARD = true; const COMPACT = false; const TORTURE_TEXT = "
            + json.dumps(TORTURE) + ";" + BRIDGE
        )
        page.goto(url, wait_until="networkidle")
        page.add_style_tag(content=GROUND)
        page.wait_for_timeout(1500)

        scroller = ".overflow-y-auto"
        # The transcript follows the stream, so it mounts at the bottom.
        # Walk it from the top or the first shot is the last screen.
        page.evaluate(f"document.querySelector('{scroller}')?.scrollTo(0, 0)")
        page.wait_for_timeout(400)
        for index in range(5):
            page.screenshot(path=str(OUT / f"md-{index}.png"))
            page.evaluate(
                f"document.querySelector('{scroller}')?.scrollBy(0, 700)"
            )
            page.wait_for_timeout(350)

        # The reply is capped at `--prose`; the column is not. Reported rather
        # than eyeballed, because "about 68 characters" is the whole point of
        # having a separate measure at all.
        measure = page.evaluate(
            """(() => {
                 const p = document.querySelector('p[class*="overflow-wrap"]');
                 if (!p) return null;
                 const px = p.getBoundingClientRect().width;
                 const size = parseFloat(getComputedStyle(p).fontSize);
                 const probe = document.createElement('span');
                 probe.style.cssText = 'position:absolute;visibility:hidden;white-space:pre';
                 probe.style.font = getComputedStyle(p).font;
                 probe.textContent = '0'.repeat(100);
                 p.appendChild(probe);
                 const ch = probe.getBoundingClientRect().width / 100;
                 probe.remove();
                 return { px: Math.round(px), size, ch: Math.round(px / ch) };
               })()"""
        )
        print(f"prose measure: {measure}")

        # Compact, where 15px body and a 33rem cap have to coexist in 420px —
        # and where the rail is icons-only, which only Electron knows.
        page.close()
        page = browser.new_page(viewport={"width": 420, "height": 600})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.add_init_script(
            "const WIZARD = true; const COMPACT = true; const TORTURE_TEXT = "
            + json.dumps(TORTURE) + ";" + BRIDGE
        )
        page.goto(url, wait_until="networkidle")
        page.add_style_tag(content=GROUND)
        page.wait_for_timeout(1200)
        page.evaluate("document.querySelector('.overflow-y-auto')?.scrollTo(0, 0)")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUT / "md-compact.png"))
        page.evaluate("document.querySelector('.overflow-y-auto')?.scrollBy(0, 1400)")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUT / "md-compact-code.png"))

        # Maximised, with the `roomy` class the real window sets.
        page.close()
        page = browser.new_page(viewport={"width": 1900, "height": 1000})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.add_init_script(
            "const WIZARD = true; const COMPACT = false; const TORTURE_TEXT = "
            + json.dumps(TORTURE) + ";" + BRIDGE
        )
        page.goto(url, wait_until="networkidle")
        page.add_style_tag(content=GROUND)
        page.wait_for_timeout(1200)
        page.evaluate("document.documentElement.classList.add('roomy')")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "md-roomy.png"))
        page.evaluate("document.documentElement.classList.remove('roomy')")

        # ── the streaming replay ───────────────────────────────────
        # Real `token` events down the real path, one at a time, with the
        # frame clock running. The parser measurements were taken in Node;
        # this is the one that includes React and the DOM.
        page.close()
        page = browser.new_page(viewport={"width": 1100, "height": 760})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.add_init_script("const WIZARD = true;const TORTURE_TEXT = null; "
        + "const COMPACT = false;" + BRIDGE)
        page.goto(url, wait_until="networkidle")
        page.add_style_tag(content=GROUND)
        page.wait_for_timeout(1200)

        page.get_by_role("textbox").first.fill("stream it")
        page.keyboard.press("Enter")
        page.wait_for_timeout(400)

        # **Five runs, because one is an anecdote.** This project already
        # records that discipline for `gate_tool_selection.py`, where a
        # three-probe difference read as a finding and turned out to be
        # narrower than each model's own spread. A frame clock on a machine
        # that is also running a dev server and a 7B model is at least as
        # noisy, so the spread is reported rather than a single best run.
        runs = []
        for _ in range(5):
            page.evaluate("window.__emit('turn.reset', { turn_id: 't1' })")
            page.wait_for_timeout(200)
            runs.append(_replay(page, TORTURE))
        worst = sorted(r["worst_gap_ms"] for r in runs)
        dropped = sorted(r["dropped"] for r in runs)
        print(
            f"streaming replay x5: {runs[0]['tokens']} tokens | "
            f"worst frame gap {worst[0]}-{worst[-1]}ms (median {worst[2]}) | "
            f"frames over 32ms {dropped[0]}-{dropped[-1]}"
        )
        timings = _replay(page, TORTURE)
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "md-streamed.png"))

        # **Caught mid-reply, because the caret is CSS only.** It is an
        # `::after` on the last element, which jsdom cannot see and no unit
        # test can assert — a screenshot is the only instrument for it. Also
        # the one place to check that a fence still arriving already reads as
        # a code block rather than as a paragraph of source.
        page.evaluate("window.__emit('turn.reset', { turn_id: 't1' })")
        page.wait_for_timeout(200)
        page.evaluate(
            """(text) => {
                 for (let i = 0; i < text.length; i += 4) {
                   window.__emit('token', { turn_id: 't1', text: text.slice(i, i + 4) });
                 }
               }""",
            TORTURE[: TORTURE.index("```typescript") + 60],
        )
        page.wait_for_timeout(500)
        page.evaluate("document.querySelector('.overflow-y-auto')?.scrollTo(0, 99999)")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUT / "md-midstream.png"))
        print(f"last run in detail: {timings}")

        browser.close()

    for line in errors:
        print("ERR", line)
    print(f"{len(list(OUT.glob('*.png')))} shots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
