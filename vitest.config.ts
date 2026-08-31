import { resolve } from 'node:path'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': resolve(__dirname, 'src') },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    // `electron/` too: the main process has real logic in it — which build's
    // command to spawn, from which working directory — and that had no test
    // at all until a `cwd` regression stopped the app from starting. Those
    // files declare `@vitest-environment node` for themselves.
    include: ['src/**/*.test.{ts,tsx}', 'electron/**/*.test.ts'],
    css: false,
  },
})
