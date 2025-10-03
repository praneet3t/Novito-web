import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // If your backend runs on a different port (e.g. 8000),
    // you can configure a proxy here instead of changing API_BASE in code:
    // proxy: { '/api': 'http://localhost:8000' }
  }
})
