/**
 * Every colour in the app, in one place.
 *
 * Before this the state palette was restated in **five** files —
 * `tailwind.config.js`, `Orb.tsx`'s `HUE` map, `Orb.tsx`'s separate
 * disconnected value, and RGB triples hand-derived from the hex in both
 * `VoiceAura.tsx` and `ScreenRim.tsx`. A recolour therefore half-applied:
 * three of those live inside canvas frame loops where nothing but sampling
 * pixels would have caught it, which this project has already had to do once.
 *
 * **ESM, and the Tailwind config is `.mjs` to match.** The first version of
 * this file was CommonJS so the config could `require()` it — and the
 * renderer then imported `HUES` from it through Vite, which treats `.js` in
 * `src/` as ESM, so the module had no exports, `Orb` failed to evaluate and
 * the whole window came up blank.
 *
 * Neither `npm run typecheck` nor `npm test` caught it: tsc reads the `.d.ts`
 * beside this file, and vitest runs in Node where CJS interop is transparent.
 * **Only an actual renderer build exercises this path**, which is why
 * `npm run build` now belongs in the verification loop.
 *
 * **The palette rule, unchanged:** the chrome is near-monochrome and
 * saturation always *means* something — assistant state, success, warning,
 * failure. Nothing is coloured decoratively. An edge is a 1px inner highlight,
 * never a drawn line.
 */

/** @param {string} hex @returns {[number, number, number]} */
export function hexToRgb(hex) {
  const clean = hex.replace('#', '')
  return [
    parseInt(clean.slice(0, 2), 16),
    parseInt(clean.slice(2, 4), 16),
    parseInt(clean.slice(4, 6), 16),
  ]
}

export const COLORS = {
  // Ground. The window is transparent; this is what shows through where
  // acrylic cannot. **Dark green, and only just** — the fallback should read
  // as absence, not as a colour. The old note said "not as navy"; the same
  // trap in green is a ground that reads as a felt table.
  void: '#050a08',

  // Layered glass. Alpha carries the depth, so these compose over the acrylic
  // backdrop and over each other without extra borders.
  //
  // **0.62 does not move.** It was measured on screen over a bright editor
  // once DWM acrylic arrived — 0.86 came from the era when the window was
  // `transparent: true` with no compositor blur and the alpha had to do all
  // the work. Only the hue shifts here, a few degrees warmer and slightly
  // desaturated, so the acrylic's own colour shows through instead of
  // fighting a blue tint. If it ever fights readability, readability wins and
  // it goes back up.
  glass: 'rgba(9, 18, 14, 0.62)',

  // Docked chrome — the navigation rail. Lifted off the panel by a white wash
  // rather than tinted darker, so it reads as nearer the viewer than the
  // conversation instead of as a cut-out. A shade stronger than before: at
  // 420px the rail needs to separate without a drawn line.
  panel: 'rgba(255, 255, 255, 0.042)',

  // Floating sheets. Denser than the panel behind them — a sheet sharing its
  // backdrop's alpha reads as a hole in the window. These hold forms and
  // dense text, so they stay the most opaque surface.
  pop: 'rgba(12, 24, 19, 0.82)',

  raised: 'rgba(255, 255, 255, 0.055)',
  sunk: 'rgba(0, 0, 0, 0.30)',

  // Edges are light, not lines.
  rim: 'rgba(255, 255, 255, 0.08)',
  'rim-strong': 'rgba(255, 255, 255, 0.14)',

  // **Four steps, evenly spaced, where there used to be three.** The old ramp
  // jumped 93 -> 62 -> 44 in lightness, so anything one notch below body text
  // fell two notches and the hierarchy read flat. `dim` is the missing step:
  // what a paragraph inside a panel should be, where before it was either
  // full `text` (too loud everywhere) or `muted` (too quiet to read).
  text: '#ecf3ef',
  dim: '#b3c5ba',
  muted: '#889b90',
  faint: '#5f7067',

  // **Focus rings and selection only. Nothing else may use this.**
  //
  // Moved off cyan, and this is the single most defensible change in the
  // palette: at `#6fd3e0` the accent sat eight hue-degrees from `listening`
  // (`#5ec8e8`), so a focus ring and "she is listening" were the same colour
  // — in a palette whose entire rule is that saturated colour means
  // something. Blue at moderate saturation is also Windows' own focus idiom,
  // which matters for something claiming to belong to the OS.
  accent: '#6d8cff',

  // Semantic. Unchanged meanings; the values come down ~8% in lightness and
  // ~10% in saturation from Tailwind's 400s, which were tuned for white
  // backgrounds and read plasticky on near-black glass.
  ok: '#57d38a',
  warn: '#e8b23c',
  bad: '#f0736e',

  // Assistant state, the only other place saturation is allowed.
  //
  // `speaking` matching `ok` and `acting` matching `warn` is **deliberate and
  // carried over**: speaking is a good outcome, acting is a caution. It is
  // not a copy-paste mistake to be tidied up.
  idle: '#93a1b8',
  listening: '#4ec3e6',
  thinking: '#9b83f5',
  speaking: '#57d38a',
  acting: '#e8b23c',
}

/** The five assistant states — what `Orb` and the two canvases draw. */
export const HUES = {
  idle: COLORS.idle,
  listening: COLORS.listening,
  thinking: COLORS.thinking,
  speaking: COLORS.speaking,
  acting: COLORS.acting,
}

/**
 * The same hues as RGB triples, **derived rather than typed**.
 *
 * The canvases draw with `rgba(r, g, b, a)` and used to carry the conversion
 * by hand, which is exactly how they drifted from the hex in the config.
 */
export const RGB = Object.fromEntries(Object.entries(HUES).map(([k, v]) => [k, hexToRgb(v)]))
