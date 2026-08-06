/**
 * JSON-RPC 2.0 client over WebSocket (BUILD_SPEC §7.1).
 *
 * Lives in the main process, not the renderer, for two reasons: the browser
 * WebSocket API cannot set an `Authorization` header on the upgrade, and
 * `sandbox: true` bars Node from the renderer. The renderer reaches the sidecar
 * only through the contextBridge — it never learns the token or the port.
 */

import WebSocket from 'ws'

export type BrainStatus =
  | 'starting' // sidecar spawned, not yet answering
  | 'connecting' // first WS attempt
  | 'connected' // authenticated and live
  | 'reconnecting' // dropped, retrying
  | 'disconnected' // given up / shutting down

export interface RpcNotification {
  method: string
  params: Record<string, unknown>
}

interface RpcErrorShape {
  code: number
  message: string
  data?: unknown
}

interface RpcEnvelope {
  jsonrpc: '2.0'
  id?: number | string | null
  method?: string
  params?: Record<string, unknown>
  result?: unknown
  error?: RpcErrorShape
}

interface Pending {
  resolve: (value: unknown) => void
  reject: (reason: Error) => void
  timer: NodeJS.Timeout
}

export interface RpcClientOptions {
  url: string
  /** Read lazily — the token changes every time the sidecar is respawned. */
  getToken: () => string
  onStatus: (status: BrainStatus) => void
  onNotification: (notification: RpcNotification) => void
}

const REQUEST_TIMEOUT_MS = 30_000
const RECONNECT_BASE_MS = 250
const RECONNECT_MAX_MS = 5_000

/** A JSON-RPC error returned by the sidecar, preserving its code. */
export class RpcError extends Error {
  constructor(
    readonly code: number,
    message: string,
    readonly data?: unknown,
  ) {
    super(message)
    this.name = 'RpcError'
  }
}

export class RpcClient {
  private socket: WebSocket | null = null
  private pending = new Map<number, Pending>()
  private nextId = 1
  private attempts = 0
  private reconnectTimer: NodeJS.Timeout | null = null
  private status: BrainStatus = 'disconnected'
  /** Starts true so a reset() before start() cannot open a stray socket. */
  private stopped = true
  /** Token the current socket was opened with, to detect a respawn. */
  private activeToken = ''

  constructor(private readonly options: RpcClientOptions) {}

  get connected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN
  }

  /** Begin connecting and keep reconnecting until {@link stop} is called. */
  start(): void {
    this.stopped = false
    this.open()
  }

  stop(): void {
    this.stopped = true
    this.clearReconnect()
    this.failAllPending(new Error('The connection to the brain was closed.'))
    this.socket?.removeAllListeners()
    this.socket?.close()
    this.socket = null
    this.setStatus('disconnected')
  }

  /**
   * Reconnect only if the sidecar's token has changed.
   *
   * The supervisor reports "ready" on every successful health poll, not just the
   * first after a respawn. Resetting unconditionally would tear down a perfectly
   * healthy socket and flap the UI status.
   */
  syncToken(token: string): void {
    if (this.connected && this.activeToken === token) return
    this.reset()
  }

  /** Drop the current socket and reconnect immediately (new token after respawn). */
  reset(): void {
    this.attempts = 0
    this.clearReconnect()
    this.failAllPending(new Error('The brain restarted; this request was abandoned.'))
    this.socket?.removeAllListeners()
    this.socket?.close()
    this.socket = null
    if (!this.stopped) this.open()
  }

  async call<T = unknown>(method: string, params: Record<string, unknown> = {}): Promise<T> {
    const socket = this.socket
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      throw new Error(
        `Cannot call ${method}: the brain is not connected (status: ${this.status}). ` +
          `Wait for "connected", or use the tray's "Restart Brain" if it stays down.`,
      )
    }

    const id = this.nextId++
    return new Promise<T>((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id)
        reject(new Error(`${method} timed out after ${REQUEST_TIMEOUT_MS / 1000}s.`))
      }, REQUEST_TIMEOUT_MS)

      this.pending.set(id, {
        resolve: resolve as (value: unknown) => void,
        reject,
        timer,
      })
      socket.send(JSON.stringify({ jsonrpc: '2.0', id, method, params }))
    })
  }

  // ── connection lifecycle ────────────────────────────────────────────

  private open(): void {
    this.clearReconnect()
    this.setStatus(this.attempts === 0 ? 'connecting' : 'reconnecting')

    this.activeToken = this.options.getToken()
    const socket = new WebSocket(this.options.url, {
      headers: { Authorization: `Bearer ${this.activeToken}` },
      handshakeTimeout: 5_000,
    })
    this.socket = socket

    socket.on('open', () => {
      this.attempts = 0
      this.setStatus('connected')
    })
    socket.on('message', (data: WebSocket.RawData) => this.handleMessage(data.toString()))
    socket.on('error', () => {
      /* 'close' always follows; scheduling there keeps retry logic in one place */
    })
    socket.on('close', () => {
      if (this.socket === socket) this.socket = null
      this.failAllPending(new Error('The brain disconnected before replying.'))
      if (!this.stopped) this.scheduleReconnect()
    })
  }

  private scheduleReconnect(): void {
    this.setStatus('reconnecting')
    const delay = Math.min(RECONNECT_BASE_MS * 2 ** this.attempts, RECONNECT_MAX_MS)
    this.attempts += 1
    this.reconnectTimer = setTimeout(() => this.open(), delay)
  }

  private clearReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  // ── message handling ────────────────────────────────────────────────

  private handleMessage(raw: string): void {
    let envelope: RpcEnvelope
    try {
      envelope = JSON.parse(raw) as RpcEnvelope
    } catch {
      return
    }

    // No id means a server-initiated notification (§7.1 events table).
    if (envelope.id === undefined || envelope.id === null) {
      if (envelope.method) {
        this.options.onNotification({
          method: envelope.method,
          params: envelope.params ?? {},
        })
      }
      return
    }

    const id = typeof envelope.id === 'number' ? envelope.id : Number(envelope.id)
    const pending = this.pending.get(id)
    if (!pending) return
    this.pending.delete(id)
    clearTimeout(pending.timer)

    if (envelope.error) {
      pending.reject(new RpcError(envelope.error.code, envelope.error.message, envelope.error.data))
    } else {
      pending.resolve(envelope.result)
    }
  }

  private failAllPending(reason: Error): void {
    for (const pending of this.pending.values()) {
      clearTimeout(pending.timer)
      pending.reject(reason)
    }
    this.pending.clear()
  }

  private setStatus(status: BrainStatus): void {
    if (status === this.status) return
    this.status = status
    this.options.onStatus(status)
  }
}
