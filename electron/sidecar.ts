/**
 * Spawn and supervise the Python sidecar (BUILD_SPEC §9 Phase 0).
 *
 * Restart policy (§9's "exponential backoff on 3 consecutive failures", read as):
 *   - a process exit, or 3 consecutive failed /health polls, triggers a restart
 *   - the first two restarts are immediate, so a killed sidecar is back well
 *     inside the gate's 15s budget
 *   - from the third restart inside a 60s window, back off 1s, 2s, 4s ... 30s
 *   - 60s of healthy uptime resets the counter
 */

import { type ChildProcess, spawn } from 'node:child_process'
import { randomBytes } from 'node:crypto'
import { createWriteStream, existsSync, mkdirSync, readFileSync, type WriteStream } from 'node:fs'
import { join } from 'node:path'

const HEALTH_INTERVAL_MS = 5_000
const HEALTH_TIMEOUT_MS = 2_000
const FAILURES_BEFORE_RESTART = 3
const IMMEDIATE_RESTARTS = 2
const BACKOFF_BASE_MS = 1_000
const BACKOFF_MAX_MS = 30_000
const HEALTHY_RESET_MS = 60_000
const STARTUP_GRACE_MS = 20_000

export interface SidecarOptions {
  repoRoot: string
  host: string
  port: number
  dev: boolean
  onReady: () => void
  onDown: (reason: string) => void
}

export interface HealthBody {
  status: string
  version: string
  uptime_s: number
  db: boolean
}

export class Sidecar {
  private child: ChildProcess | null = null
  private logStream: WriteStream | null = null
  private healthTimer: NodeJS.Timeout | null = null
  private restartTimer: NodeJS.Timeout | null = null
  private consecutiveFailures = 0
  private restartCount = 0
  private lastRestartAt = 0
  private startedAt = 0
  private everHealthy = false
  private adopted = false
  private stopping = false
  private token = ''

  constructor(private readonly options: SidecarOptions) {}

  /** Token for the WS handshake. Regenerated on every spawn (§7.1). */
  getToken(): string {
    return this.token
  }

  get healthUrl(): string {
    return `http://${this.options.host}:${this.options.port}/health`
  }

  get rpcUrl(): string {
    return `ws://${this.options.host}:${this.options.port}/rpc`
  }

  /** True when we attached to a sidecar someone else started (`npm run sidecar`). */
  get isAdopted(): boolean {
    return this.adopted
  }

  async start(): Promise<void> {
    this.stopping = false

    // Adopt an already-running sidecar rather than spawning a duplicate that
    // would fail to bind the port. Its token comes from the handshake file.
    const existing = await this.probeHealth()
    if (existing) {
      const fileToken = this.readHandshake()
      if (fileToken) {
        this.adopted = true
        this.token = fileToken
        this.everHealthy = true
        this.beginHealthPolling()
        this.options.onReady()
        return
      }
      throw new Error(
        `Something is already listening on ${this.options.host}:${this.options.port} but ` +
          `data/.handshake is missing or unreadable, so it cannot be authenticated. ` +
          `Stop that process (or delete data/.handshake and restart it) and try again.`,
      )
    }

    this.spawnChild()
  }

  private spawnChild(): void {
    const python = this.resolvePython()
    const dataDir = join(this.options.repoRoot, 'data')
    const logDir = join(dataDir, 'logs')
    mkdirSync(logDir, { recursive: true })

    this.token = randomBytes(32).toString('hex')
    this.adopted = false
    this.startedAt = Date.now()

    // Raw stdout/stderr goes to its own file. structlog already writes JSON
    // lines to sidecar.log from inside the process; piping the child's console
    // output into that same file would interleave pretty-printed duplicates and
    // leave neither stream parseable. This file is the safety net for output
    // structlog can never produce — interpreter tracebacks, import errors, and
    // anything that dies before logging is configured.
    this.logStream = createWriteStream(join(logDir, 'sidecar.out.log'), { flags: 'a' })

    const child = spawn(python, ['-m', 'sidecar.main'], {
      cwd: this.options.repoRoot,
      env: {
        ...process.env,
        ARIA_TOKEN: this.token,
        ARIA_HOST: this.options.host,
        ARIA_PORT: String(this.options.port),
        ARIA_DEV: String(this.options.dev),
        ARIA_DATA_DIR: dataDir,
        PYTHONUNBUFFERED: '1',
        PYTHONUTF8: '1',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true,
    })
    this.child = child

    child.stdout?.pipe(this.logStream, { end: false })
    child.stderr?.pipe(this.logStream, { end: false })

    child.on('exit', (code, signal) => {
      if (this.child !== child) return
      this.child = null
      this.logStream?.end()
      this.logStream = null
      if (this.stopping) return
      this.options.onDown(`Sidecar exited (code ${code ?? 'null'}, signal ${signal ?? 'none'}).`)
      this.scheduleRestart()
    })

    child.on('error', (error) => {
      this.options.onDown(
        `Could not start the sidecar with "${python}": ${error.message}. ` +
          `Create the venv with: py -3.11 -m venv .venv && ` +
          `.venv\\Scripts\\pip install -r requirements-dev.txt`,
      )
    })

    this.beginHealthPolling()
  }

  /** venv first; ARIA_PYTHON overrides; bare `python` is the last resort. */
  private resolvePython(): string {
    const override = process.env.ARIA_PYTHON
    if (override) return override
    const venv = join(this.options.repoRoot, '.venv', 'Scripts', 'python.exe')
    return existsSync(venv) ? venv : 'python'
  }

  private readHandshake(): string | null {
    try {
      const token = readFileSync(join(this.options.repoRoot, 'data', '.handshake'), 'utf-8').trim()
      return token || null
    } catch {
      return null
    }
  }

  // ── health polling ──────────────────────────────────────────────────

  private beginHealthPolling(): void {
    this.stopHealthPolling()
    this.healthTimer = setInterval(() => {
      void this.pollOnce()
    }, HEALTH_INTERVAL_MS)
    void this.pollOnce()
  }

  private stopHealthPolling(): void {
    if (this.healthTimer) {
      clearInterval(this.healthTimer)
      this.healthTimer = null
    }
  }

  private async pollOnce(): Promise<void> {
    if (this.stopping) return
    const body = await this.probeHealth()

    if (body) {
      this.consecutiveFailures = 0
      if (!this.everHealthy) {
        this.everHealthy = true
        this.options.onReady()
      }
      if (Date.now() - this.startedAt > HEALTHY_RESET_MS) this.restartCount = 0
      return
    }

    // Don't count failures while a freshly spawned interpreter is still booting.
    if (!this.everHealthy && Date.now() - this.startedAt < STARTUP_GRACE_MS) return

    this.consecutiveFailures += 1
    if (this.consecutiveFailures >= FAILURES_BEFORE_RESTART) {
      this.options.onDown(
        `Sidecar failed ${this.consecutiveFailures} consecutive health checks. Restarting.`,
      )
      this.restart()
    }
  }

  private async probeHealth(): Promise<HealthBody | null> {
    try {
      const response = await fetch(this.healthUrl, {
        signal: AbortSignal.timeout(HEALTH_TIMEOUT_MS),
      })
      if (!response.ok) return null
      return (await response.json()) as HealthBody
    } catch {
      return null
    }
  }

  // ── restart policy ──────────────────────────────────────────────────

  /** Kill and respawn now. Backing the tray's "Restart Brain". */
  restart(): void {
    this.killChild()
    this.consecutiveFailures = 0
    this.everHealthy = false
    this.scheduleRestart()
  }

  private scheduleRestart(): void {
    if (this.stopping) return
    this.stopHealthPolling()
    if (this.restartTimer) clearTimeout(this.restartTimer)

    if (Date.now() - this.lastRestartAt > HEALTHY_RESET_MS) this.restartCount = 0
    this.lastRestartAt = Date.now()
    this.restartCount += 1

    const delay =
      this.restartCount <= IMMEDIATE_RESTARTS
        ? 0
        : Math.min(BACKOFF_BASE_MS * 2 ** (this.restartCount - IMMEDIATE_RESTARTS - 1), BACKOFF_MAX_MS)

    this.restartTimer = setTimeout(() => {
      this.everHealthy = false
      this.spawnChild()
    }, delay)
  }

  private killChild(): void {
    const child = this.child
    if (!child) return
    this.child = null
    child.removeAllListeners('exit')
    child.kill()
    this.logStream?.end()
    this.logStream = null
  }

  /** Shut down for good. Called on app quit. */
  stop(): void {
    this.stopping = true
    this.stopHealthPolling()
    if (this.restartTimer) clearTimeout(this.restartTimer)
    this.restartTimer = null
    this.killChild()
  }
}
