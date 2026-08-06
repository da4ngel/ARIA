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

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        aria: {
          // Ground. The window is transparent; this is what the panel sits on.
          void: '#07080b',

          // Layered glass. Alpha carries the depth, so these compose over the
          // acrylic backdrop and over each other without extra borders.
          //
          // The panel tint is deliberately heavy. At 0.72 the editor behind was
          // legible *through* the conversation — glass has to obscure to be
          // readable, and the blur underneath supplies the depth, not the alpha.
          glass: 'rgba(13, 16, 22, 0.86)',
          raised: 'rgba(255, 255, 255, 0.06)',
          sunk: 'rgba(0, 0, 0, 0.28)',

          // Edges are light, not lines.
          rim: 'rgba(255, 255, 255, 0.07)',
          'rim-strong': 'rgba(255, 255, 255, 0.12)',

          text: '#e9ecf3',
          muted: '#8d95a9',
          faint: '#5d6478',

          // Focus rings and selection. Nothing else may use this.
          accent: '#6fd3e0',

          // Semantic. Unchanged meanings from the previous palette.
          ok: '#4ade80',
          warn: '#fbbf24',
          bad: '#f87171',

          // Assistant state, the only other place saturation is allowed.
          idle: '#9fb0c9',
          listening: '#5ec8e8',
          thinking: '#a78bfa',
          speaking: '#4ade80',
          acting: '#fbbf24',
        },
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
        // Every number and identifier — latency, model ids, timestamps — so
        // data reads as data.
        mono: ['Cascadia Code', 'Cascadia Mono', 'Consolas', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        // One scale, used everywhere.
        micro: ['0.6875rem', { lineHeight: '1rem' }], // 11
        tiny: ['0.75rem', { lineHeight: '1.125rem' }], // 12
        small: ['0.8125rem', { lineHeight: '1.25rem' }], // 13
        body: ['0.9375rem', { lineHeight: '1.55rem' }], // 15
        lead: ['1.0625rem', { lineHeight: '1.6rem' }], // 17
        hero: ['1.75rem', { lineHeight: '2rem' }], // 28
      },
      boxShadow: {
        // One window shadow, deep enough to lift glass off any wallpaper.
        window: '0 24px 60px -12px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(0, 0, 0, 0.35)',
        bloom: '0 0 24px -4px currentColor',
      },
      backdropBlur: {
        glass: '32px',
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
