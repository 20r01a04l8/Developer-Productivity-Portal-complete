import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Why proxy:
//   In dev, the browser calls /api/v1/... and Vite forwards to the correct service.
//   No CORS headers needed. In production, a real reverse proxy (nginx/ALB) does this.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api/projects': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/projects/, '/api/v1/projects'),
      },
      '/api/tasks': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/tasks/, '/api/v1/tasks'),
      },
    },
  },
})
