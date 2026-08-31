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

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "data" / "ui-shots"

#: **The one thing a browser cannot supply: something behind the glass.**
#: `glass` is `rgba(9, 18, 14, 0.62)` and Electron paints it over DWM acrylic,
#: which blurs the desktop. A browser's default white page under a 62% tint
#: reads as flat grey and makes the whole app look like a different colour
#: than it is. This stands in for the blurred desktop.
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
    'chat.history': { messages: [] },
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
    isExpanded: () => Promise.resolve(true),
    setMaximized: () => Promise.resolve(false),
    isMaximized: () => Promise.resolve(false),
    pickFiles: () => Promise.resolve([]),
    exportDiagnostics: () => Promise.resolve('C:\\diag.zip'),
    getAutoStart: () => Promise.resolve(false),
    setAutoStart: (v) => Promise.resolve(v),
  };
})();
"""


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
        page.add_init_script("const WIZARD = false;" + BRIDGE)
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
        page.add_init_script("const WIZARD = true;" + BRIDGE)
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
        page.set_viewport_size({"width": 420, "height": 600})
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUT / "02-compact.png"))

        browser.close()

    for line in errors:
        print("ERR", line)
    print(f"{len(list(OUT.glob('*.png')))} shots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
