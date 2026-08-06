# ARIA

Local-first Windows AI assistant. Electron UI + Python sidecar brain.

Architecture and the phased build plan live in [BUILD_SPEC.md](BUILD_SPEC.md).
Working rules for Claude Code sessions live in [CLAUDE.md](CLAUDE.md).

**Current phase: 0 — Foundation.** The window talks to the sidecar. Nothing
intelligent yet: no model, no voice, no tools.

## Setup

Requires **Python 3.11** (not 3.12 — see BUILD_SPEC §4) and Node 20+.

```powershell
winget install Python.Python.3.11

# Python sidecar
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

# Electron + renderer
npm install
```

## Running

```powershell
npm run dev        # Electron + Vite, auto-spawns the sidecar
npm run sidecar    # sidecar alone on :8765
```

`Ctrl+Space` toggles the window. It also lives in the system tray — Show,
Settings, Restart Brain, Quit.

If another app owns `Ctrl+Space` (IME switchers are the usual culprit), Aria
says so in the tray tooltip and you can open the window from the tray icon.

## Checks

```powershell
.venv\Scripts\python.exe -m pytest sidecar/tests -v
.venv\Scripts\python.exe -m ruff check sidecar
.venv\Scripts\python.exe -m mypy sidecar
npm run typecheck
npm test
```

## Layout

```
electron/   main process — window, tray, hotkey, sidecar supervisor, RPC client
src/        React renderer — a pure view, no domain state
sidecar/    Python brain — FastAPI, JSON-RPC, SQLite. All state lives here.
data/       runtime only, gitignored: aria.db, logs/, .handshake
```

Two log files, on purpose:

- `data/logs/sidecar.log` — structlog JSON lines, written from inside Python.
- `data/logs/sidecar.out.log` — the child's raw stdout/stderr, captured by the
  Electron supervisor. This is where an interpreter traceback or an import error
  shows up, i.e. anything that kills the sidecar before logging exists.

## How the two halves talk

WebSocket JSON-RPC 2.0 on `ws://127.0.0.1:8765/rpc`, plus server-pushed
notifications (BUILD_SPEC §7.1).

The port is reachable by any browser tab on this machine, so every connection
must present `Authorization: Bearer <token>`. Electron mints the token, passes
it to the sidecar via `ARIA_TOKEN`, and the sidecar also writes it to
`data/.handshake` so standalone runs work. The renderer never sees the token or
the port — it goes through the `contextBridge` in `electron/preload.ts`.
