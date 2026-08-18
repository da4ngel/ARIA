// CommonJS on purpose: package.json has no "type": "module", because Electron 31
// preloads must be CJS when sandbox: true (BUILD_SPEC §3 renderer isolation).

/**
 * Ambient glass, dark only.
 *
 * The chrome is near-monochrome and saturated colour always means something —
 * assistant state, route, success, warning, failure. Nothing is coloured for
 * decoration. That rule is what lets the orb read at a glance, and what stops a
 * translucent window turning to soup over an arbitrary wallpaper.
 *
 * Surfaces are translucency over a near-black void rather than flat greys, and
 * an "edge" is a 1px inner highlight (`rim`) rather than a drawn line.
 */

const { COLORS } = require('./src/styles/tokens.js')

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // One source, shared with the renderer and the two canvases — see
        // `src/styles/tokens.js`. The palette used to be restated in five
        // files and a recolour half-applied inside frame loops.
        aria: COLORS,
      },
      fontFamily: {
        // Native Windows faces. No webfont: this is a desktop app that must work
        // offline, and Segoe UI Variable is the right voice for something
        // claiming to belong to the OS.
        sans: [
          'Segoe UI Variable Text',
          'Segoe UI',
          'system-ui',
          '-apple-system',
          'sans-serif',
        ],
        // **Segoe UI Variable ships three optical sizes and this app was using
        // one.** `Text` is drawn for 12-17px; `Display` is tighter with higher
        // stroke contrast for 18px and up, and `Small` opens up below 11px.
        // Rendering a 28px heading in the Text optical size is why large type
        // here looked soft and slightly wide. Costs nothing — the faces are
        // already installed, and the fallbacks are what was being used anyway.
        display: ['Segoe UI Variable Display', 'Segoe UI', 'system-ui', 'sans-serif'],
        small: ['Segoe UI Variable Small', 'Segoe UI', 'system-ui', 'sans-serif'],
        // Every number and identifier — latency, model ids, timestamps — so
        // data reads as data.
        mono: ['Cascadia Code', 'Cascadia Mono', 'Consolas', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        // One scale, used everywhere.
        micro: ['0.6875rem', { lineHeight: '1rem' }], // 11
        tiny: ['0.75rem', { lineHeight: '1.125rem' }], // 12
        small: ['0.8125rem', { lineHeight: '1.25rem' }], // 13
        // 1.65 was generous for a 420px column — a two-line reply floated
        // rather than sat. 1.6 keeps it readable and anchored.
        body: ['0.9375rem', { lineHeight: '1.5rem' }], // 15
        // `lead` heads things rather than carrying paragraphs, so it wants
        // less air than body text does.
        lead: ['1.0625rem', { lineHeight: '1.45rem' }], // 17
        hero: ['1.75rem', { lineHeight: '2rem' }], // 28
      },
      letterSpacing: {
        // Light text on a dark surface blooms, which visually adds space —
        // so large type at default tracking reads loose, and small labels get
        // the opposite problem and need opening up.
        tightest: '-0.014em',
        tight: '-0.008em',
        wide: '0.02em',
      },
      fontWeight: {
        // Segoe UI Variable is a variable font. 600 already blooms slightly on
        // near-black glass; 620 is the difference between a heading that reads
        // crisp and one that reads smudged.
        strong: '620',
      },
      // `shadow-window` and `shadow-bloom` lived here with zero uses in the
      // whole app — `.glass-pop` inlines its own shadow. Removed rather than
      // left as decoration nobody can find a use for.

      backdropBlur: {
        glass: '32px',
        // Docked chrome sits inside the window, so it only has the panel to
        // blur — a heavier radius there buys nothing and costs compositing.
        panel: '20px',
        // Floating sheets blur the conversation underneath, which is text.
        // This is the radius at which it stops being readable through them.
        pop: '28px',
      },
      keyframes: {
        rise: {
          from: { opacity: '0', transform: 'translateY(4px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        caret: {
          '0%, 100%': { opacity: '0.25' },
          '50%': { opacity: '1' },
        },
      },
      animation: {
        rise: 'rise 160ms cubic-bezier(0.2, 0.8, 0.2, 1)',
        caret: 'caret 1.1s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
