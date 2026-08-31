/**
 * The packaged app's paths, guarded across four files that must agree.
 *
 * **Stage 2 of Phase 9 is the part with a silent failure mode.** Packaged,
 * `repoRoot` is `process.resourcesPath` — under Program Files. Two things
 * used to be resolved against it and both are wrong there:
 *
 *   - `ARIA_DATA_DIR`, which *overrides* `sidecar/config.py`'s own frozen
 *     rule. The database would land in a read-only directory that the next
 *     upgrade replaces, taking the conversation history with it. That bug
 *     was already found and fixed once on the Python side; passing the
 *     wrong directory from here would have quietly undone it.
 *   - `data/.handshake`, which Electron reads to adopt an already-running
 *     sidecar. The frozen sidecar writes it to `%LOCALAPPDATA%`, so
 *     Electron would look in a different file, find nothing, spawn a
 *     second sidecar, and *that* one would lose the port race — with no
 *     error anywhere, because both processes behaved correctly.
 *
 * None of this can be caught by running the dev build, where every path
 * happens to coincide. These read the sources, the way `acrylic.test.ts`
 * and `tray.test.ts` already do, because what needs guarding is the literal
 * configuration rather than a behaviour a mock could stand in for.
 */

import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

const read = (path: string): string => readFileSync(join(process.cwd(), path), 'utf8')

/**
 * Source with comments removed, for assertions about what the code does *not*
 * do.
 *
 * **The third time this trap has been walked into in this repo** — the Python
 * side has `code_only()` in `test_email.py` for exactly this, after a scan for
 * "SMTP" matched the docstring explaining there is none, and `test_reminders`
 * hit it before that. A comment saying "not localStorage" is precisely what a
 * naive search for "localStorage" finds. Crude, and enough: these files are
 * ours and contain no `//` inside a string literal that matters here.
 */
const code = (path: string): string =>
  read(path)
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/^\s*\/\/.*$/gm, '')

const MAIN = read('electron/main.ts')
const SIDECAR = read('electron/sidecar.ts')
const BUILDER = read('electron-builder.yml')
const CONFIG_PY = read('sidecar/config.py')
const PACKAGE = JSON.parse(read('package.json')) as {
  scripts: Record<string, string>
  dependencies: Record<string, string>
  devDependencies?: Record<string, string>
}

describe('where the data lives', () => {
  it('does not put the packaged data directory under resourcesPath', () => {
    // The whole bug in one assertion: `join(repoRoot, 'data')` is correct in
    // development and read-only Program Files once installed.
    const packagedBranch = MAIN.slice(MAIN.indexOf('function resolveDataDir'))
    const body = packagedBranch.slice(0, packagedBranch.indexOf('\n}'))
    expect(body).toContain("if (isDev) return join(repoRoot, 'data')")
    expect(body).toContain('LOCALAPPDATA')
    expect(body).toContain("'ARIA', 'data'")
  })

  it('agrees with the sidecar about where that is', () => {
    // Both sides act on this directory — Python writes the handshake there,
    // Electron reads it — so a disagreement is not cosmetic.
    expect(CONFIG_PY).toContain('LOCALAPPDATA')
    expect(CONFIG_PY).toContain('"ARIA" / "data"')
  })

  it('reads the handshake from the data directory, not the repo root', () => {
    expect(SIDECAR).toContain("join(this.options.dataDir, '.handshake')")
    expect(SIDECAR).not.toContain("join(this.options.repoRoot, 'data'")
  })

  it('picks the working directory by build, and both halves matter', () => {
    // **This test used to assert `cwd: dataDir` flat, and that was a bug it
    // enshrined rather than caught.** Packaged, `resourcesPath` is read-only
    // Program Files, so the data directory is right. In development the
    // command is `python -m sidecar.main`, and `-m` finds the package
    // through the working directory — pointing it anywhere else exits 1 with
    // `No module named 'sidecar'`, which is exactly what shipping the flat
    // version did. A string assertion passed because the string was true of
    // the branch that almost never runs.
    expect(SIDECAR).toContain('cwd: this.options.frozenExe ? dataDir : this.options.repoRoot')
  })
})

describe('finding the brain', () => {
  it('runs the frozen exe when packaged and the interpreter when not', () => {
    // There is no `.venv` inside an installed app; the dev resolution order
    // would hunt for a virtualenv under resources/.
    expect(MAIN).toContain("join(process.resourcesPath, 'sidecar', 'aria-sidecar.exe')")
    expect(SIDECAR).toContain('if (frozen) return { command: frozen, args: [] }')
    expect(SIDECAR).toContain("args: ['-m', 'sidecar.main']")
  })

  it('is placed where main.ts looks for it', () => {
    // The one cross-file coupling with no runtime error to announce it:
    // electron-builder's destination and main.ts's path are written twice.
    expect(BUILDER).toContain('from: packaging/dist/aria-sidecar')
    expect(BUILDER).toContain('to: sidecar')
  })

  it('ships the icon main.ts loads by path', () => {
    // `win.icon` dresses the .exe and the installer only. The running window
    // is given an absolute path, so the file has to actually be there.
    expect(MAIN).toContain("join(repoRoot, 'resources', 'icon.ico')")
    expect(BUILDER).toContain('from: resources')
    expect(BUILDER).toContain('icon: resources/icon.ico')
  })

  it('builds the sidecar bundle before the installer that copies it', () => {
    // Expressed as scripts rather than remembered: `extraResources` copies a
    // directory that must already exist, and its absence is not an error —
    // electron-builder simply ships an app with no brain in it.
    expect(PACKAGE.scripts['dist:sidecar']).toContain('packaging/sidecar.spec')
    expect(PACKAGE.scripts['dist:sidecar']).toContain('--distpath packaging/dist')
    expect(PACKAGE.scripts.dist).toContain('electron-builder')
  })
})

describe('auto-start', () => {
  it('comes up hidden, and honours the flag it sets', () => {
    // Opening a window on every login is the fastest way to make somebody
    // remove a startup item. The flag and the check are written separately,
    // so they are asserted together.
    expect(MAIN).toContain("args: ['--hidden']")
    expect(MAIN).toContain("process.argv.includes('--hidden')")
    expect(MAIN).toContain('if (!startHidden) showWindow()')
  })

  it('reports what the OS says rather than what was asked for', () => {
    // This is registry state, not app state. A copy kept anywhere else would
    // still read as on after somebody turned it off in Task Manager.
    const handler = MAIN.slice(MAIN.indexOf("ipcMain.handle('aria:set-auto-start'"))
    expect(handler.slice(0, handler.indexOf('\n  })'))).toContain(
      'return app.getLoginItemSettings().openAtLogin',
    )
  })
})

describe('when something goes wrong', () => {
  it('writes an Electron crash to a file the diagnostics export collects', () => {
    // The sidecar has had two log files since Phase 0; an Electron-side
    // crash left nothing at all, because a packaged window has no console
    // for stderr to reach. `electron.log` is the smallest thing that makes
    // "it just closed" answerable, and the export picks it up by name.
    expect(MAIN).toContain("process.on('uncaughtException'")
    expect(MAIN).toContain("process.on('unhandledRejection'")
    expect(MAIN).toContain("join(DATA_DIR, 'logs', 'electron.log')")
    expect(read('sidecar/core/diagnostics.py')).toContain('"electron.log"')
  })

  it('offers the export from the tray as well as from Settings', () => {
    // The moment you need diagnostics is the moment the window may not be
    // working, which is the whole reason it is in two places.
    expect(read('electron/tray.ts')).toContain("label: 'Export diagnostics'")
    expect(MAIN).toContain("ipcMain.handle('aria:export-diagnostics'")
  })
})

describe('the first run', () => {
  const HOOK = read('src/hooks/useFirstRun.ts')
  const SETUP_PY = read('sidecar/core/setup.py')

  it('is gated on a settings row rather than on browser storage', () => {
    // Rule 1, and the practical half of it: a wizard that reappears because
    // somebody cleared their storage is worse than no wizard.
    expect(HOOK).toContain("call<{ done: boolean }>('setup.done'")
    expect(code('src/hooks/useFirstRun.ts')).not.toContain('localStorage')
    expect(read('sidecar/memory/settings_store.py')).toContain('FIRST_RUN_DONE = "first_run_done"')
  })

  it('answers the microphone request explicitly rather than by default', () => {
    // `setPermissionRequestHandler` was never called at all, which happened
    // to work because Electron grants everything to a page it loaded itself.
    // A default is not a decision.
    expect(MAIN).toContain('setPermissionRequestHandler')
    expect(MAIN).toContain("permission === 'media'")
  })

  it('never writes a partial download to the path speech checks', () => {
    // `tts.py` decides speech is available by `Path.exists()`, so a truncated
    // file at that name turns "the weights are missing" — which says what to
    // do — into an ONNX parse error on every launch, which does not.
    expect(SETUP_PY).toContain('target.with_name(target.name + ".part")')
    expect(SETUP_PY).toContain('partial.replace(target)')
  })
})

describe('updating itself', () => {
  const UPDATER = read('electron/updater.ts')
  const WORKFLOW = read('.github/workflows/release.yml')

  it('requires electron-updater at runtime, not as a build tool', () => {
    // Main `require`s it when the app launches, so it has to be a production
    // dependency — electron-builder only bundles those into the asar.
    expect(PACKAGE.dependencies).toHaveProperty('electron-updater')
    expect(PACKAGE.devDependencies ?? {}).not.toHaveProperty('electron-updater')
  })

  it('stops and waits for the sidecar before installing', () => {
    // **The one thing electron-updater cannot know.** The installer
    // overwrites `resources/sidecar/aria-sidecar.exe`, and Windows will not
    // overwrite a file a live process still holds open — so a plain `stop()`,
    // which only sends a kill, races the installer into a half-updated app.
    const install = MAIN.slice(MAIN.indexOf('async function installUpdate'))
    const body = install.slice(0, install.indexOf('\n}'))
    expect(body).toContain('await sidecar.stopAndWait()')
    expect(body.indexOf('stopAndWait')).toBeLessThan(body.indexOf('quitAndInstall'))
  })

  it('offers a restart rather than taking one', () => {
    // Decided with Eyaas: download quietly, then offer. `autoInstallOnAppQuit`
    // is what makes somebody who never clicks the button still end up
    // updated, without anything interrupting a conversation.
    expect(UPDATER).toContain('autoDownload = true')
    expect(UPDATER).toContain('autoInstallOnAppQuit = true')
  })

  it('does nothing in a development build', () => {
    // electron-updater throws without an installed app, and that throw would
    // come out of the module import rather than a call.
    expect(UPDATER).toContain('if (!this.supported) return')
    expect(UPDATER).toContain('app.isPackaged')
  })

  it('publishes only a version nobody has released', () => {
    // Gated on the tag, not on a diff, so a job that fails halfway can be
    // re-run without shipping twice.
    expect(WORKFLOW).toContain('refs/tags/v$version')
    expect(WORKFLOW).toContain("if: steps.gate.outputs.publish == 'true'")
    expect(WORKFLOW).toContain('--publish always')
  })

  it('runs the whole suite on every push, published or not', () => {
    for (const check of ['pytest sidecar/tests', 'ruff check sidecar', 'mypy sidecar', 'npm test']) {
      expect(WORKFLOW).toContain(check)
    }
  })

  it('says where updates come from instead of inferring it', () => {
    expect(BUILDER).toContain('provider: github')
    expect(BUILDER).toContain('owner: da4ngel')
  })
})

describe('the installer', () => {
  it('installs per-user, which is what makes %LOCALAPPDATA% the right home', () => {
    expect(BUILDER).toContain('perMachine: false')
    expect(BUILDER).toContain('oneClick: false')
  })

  it('does not offer the directory page, which crashes NSIS', () => {
    // Not a preference. With it on, double-clicking the installer died with
    // an access violation in NSIS's own System.dll — no window, no message,
    // just three Application Error records. Bisected: silent installs fine,
    // interactive without this page installs fine, interactive with it
    // crashes. `perMachine: false` already puts it under %LOCALAPPDATA%.
    expect(BUILDER).toContain('allowToChangeInstallationDirectory: false')
  })

  it('packs the app but not the sidecar', () => {
    // `asar: true` is safe only because the sidecar is external: an archive
    // is not a real filesystem path, and `spawn` needs one.
    expect(BUILDER).toContain('asar: true')
    expect(BUILDER).toMatch(/files:\s*\n\s*- out\/\*\*/)
  })
})
