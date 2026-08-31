// @vitest-environment node
/**
 * What actually gets spawned, and where from.
 *
 * **Written after shipping a bug that `packaging.test.ts` asserted.** Adding
 * the packaged branch, I set `cwd` to the data directory unconditionally —
 * correct once installed, where `resourcesPath` is read-only Program Files,
 * and fatal in development, where the command is `python -m sidecar.main` and
 * `-m` resolves the package through the working directory. Every launch died
 * with `No module named 'sidecar'` and exit code 1.
 *
 * The reason it survived a full green run is the shape of the test that was
 * supposed to guard it: it read the source for the literal string
 * `cwd: dataDir`, which was true, of a branch that almost never executes.
 * **A string assertion cannot tell a build apart.** These drive the real
 * class down both paths and read back what it asked the OS for.
 *
 * It lives beside its subject rather than under `src/` because that is where
 * the node tsconfig covers, and `vitest.config.ts` includes `electron/` for
 * exactly this file — a main-process test importing main-process code.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest'

const spawn = vi.fn()

vi.mock('node:child_process', () => ({
  spawn: (...args: unknown[]) => {
    spawn(...args)
    // Enough of a ChildProcess for `spawnChild` to wire up, and for `stop()`
    // to tear down again — the teardown path is what these tests run through.
    return {
      stdout: null,
      stderr: null,
      on: () => {},
      removeAllListeners: () => {},
      kill: () => {},
    }
  },
}))

vi.mock('node:fs', () => ({
  createWriteStream: () => ({ end: () => {} }),
  existsSync: () => true,
  mkdirSync: () => {},
  readFileSync: () => '',
}))

const { Sidecar } = await import('./sidecar')

function build(frozenExe: string | null) {
  return new Sidecar({
    repoRoot: 'C:\\repo',
    dataDir: 'C:\\data',
    frozenExe,
    host: '127.0.0.1',
    port: 8765,
    dev: frozenExe === null,
    onReady: () => {},
    onDown: () => {},
  })
}

beforeEach(() => {
  spawn.mockClear()
  // Nothing is listening, so `start()` spawns rather than adopting.
  vi.stubGlobal('fetch', () => Promise.reject(new Error('nothing there')))
})

describe('what the sidecar spawns', () => {
  it('runs the interpreter from the repo root in development', async () => {
    // `python -m sidecar.main` finds the package through the cwd. Anywhere
    // else and the interpreter exits 1 before a line of ARIA has run.
    const sidecar = build(null)
    await sidecar.start()
    sidecar.stop()

    const [command, args, options] = spawn.mock.calls[0] as [string, string[], { cwd: string }]
    expect(command).toContain('python')
    expect(args).toEqual(['-m', 'sidecar.main'])
    expect(options.cwd).toBe('C:\\repo')
  })

  it('runs the frozen exe from the data directory when packaged', async () => {
    // There is no package to find — the exe carries its own — and
    // `resourcesPath` is read-only for a normal user.
    const sidecar = build('C:\\app\\resources\\sidecar\\aria-sidecar.exe')
    await sidecar.start()
    sidecar.stop()

    const [command, args, options] = spawn.mock.calls[0] as [string, string[], { cwd: string }]
    expect(command).toBe('C:\\app\\resources\\sidecar\\aria-sidecar.exe')
    expect(args).toEqual([])
    expect(options.cwd).toBe('C:\\data')
  })

  it('tells the sidecar where its data lives, in both builds', async () => {
    // `ARIA_DATA_DIR` *overrides* `config.py`'s own frozen rule, so getting
    // this wrong would silently undo a fix made on the Python side.
    for (const frozen of [null, 'C:\\app\\aria-sidecar.exe']) {
      spawn.mockClear()
      const sidecar = build(frozen)
      await sidecar.start()
      sidecar.stop()
      const options = spawn.mock.calls[0][2] as { env: Record<string, string> }
      expect(options.env.ARIA_DATA_DIR).toBe('C:\\data')
    }
  })
})
