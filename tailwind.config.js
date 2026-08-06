// CommonJS on purpose: package.json has no "type": "module", because Electron 31
// preloads must be CJS when sandbox: true (BUILD_SPEC §3 renderer isolation).
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        aria: {
          bg: '#0b0d12',
          panel: '#12151d',
          edge: '#232838',
          text: '#e6e9f0',
          muted: '#8b93a7',
          ok: '#4ade80',
          warn: '#fbbf24',
          bad: '#f87171',
        },
      },
    },
  },
  plugins: [],
}
