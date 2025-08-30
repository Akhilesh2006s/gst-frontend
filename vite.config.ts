import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: process.env.NODE_ENV === 'production' 
          ? 'https://web-production-84a3.up.railway.app'
          : 'http://localhost:5000',
        changeOrigin: true,
        secure: process.env.NODE_ENV === 'production',
      }
    }
  }
})

