import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({command, mode}) => ({
  plugins: [
    vue({template: {compilerOptions: {comments: true}}})
  ],
  server: {
    hmr: {
      host: 'localhost',
      port: 5173,
    },
    watch: {
      usePolling: false,
      interval: 200,
    },
  },
  esbuild: false,
  build: {
    minify: false,
    rollupOptions: {output: {
      manualChunks(id) {
        if (id.includes('node_modules')) {
          return 'vendor'
        }
      },
    },
  }},
}))
