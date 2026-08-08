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
          // 0.86 was measured **when the window was `transparent: true` and
          // had no compositor blur at all** — the editor behind read straight
          // through the conversation, so the alpha had to do all the work.
          //
          // DWM acrylic changes that premise: it blurs the backdrop itself, so
          // legibility no longer depends on being nearly opaque, and at 0.86
          // the blur it supplies is invisible. This is the number that makes
          // the glass a glass rather than a dark rectangle. Verified on screen
          // over a bright editor before it was committed; if it ever fights
          // readability, readability wins and it goes back up.
          glass: 'rgba(13, 16, 22, 0.62)',

          // Docked chrome — the navigation rail. Lifted off the panel by a
          // white wash rather than tinted darker, so the rail reads as nearer
          // the viewer than the conversation instead of as a cut-out.
          panel: 'rgba(255, 255, 255, 0.035)',

          // Floating sheets. Denser than the panel behind them: a sheet that
          // shares its backdrop's alpha reads as a hole in the window. These
          // hold forms and dense text, so they stay the most opaque surface.
          pop: 'rgba(17, 21, 28, 0.80)',

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
