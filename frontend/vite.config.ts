import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://web-production-84a3.up.railway.app',
        changeOrigin: true,
        secure: true,
      }
    }
  }
})

