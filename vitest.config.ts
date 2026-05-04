import { join } from 'node:path'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// Vitest is configured separately from vite.config.mts because the renderer
// build pipeline pulls in Electron/Cesium plugins we don't want during tests.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@render': join(__dirname, 'src/render'),
      '@main': join(__dirname, 'src/main'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test-setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules', 'dist', 'e2e'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: [
        'src/render/app/store/**/*.ts',
        'src/render/app/pages/**/utils/**/*.ts',
      ],
    },
  },
})
