import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite configuration for React application
export default defineConfig({
    plugins: [react()],
    server: {
        port: 3000,
        // Proxy API requests to backend during development
        proxy: {
            '/api': {
                target: 'http://localhost:5000',
                changeOrigin: true,
            }
        }
    },
    build: {
        outDir: 'dist',
        sourcemap: true
    }
})
