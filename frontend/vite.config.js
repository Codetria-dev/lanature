import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '@assets': path.resolve(__dirname, '../assets'),
    },
  },
  plugins: [
    react({
      // Configure esbuild options for React Fast Refresh
      jsxRuntime: 'automatic',
      babel: {
        plugins: [],
      },
      // Use esbuild for JSX transformation (faster than Babel)
      jsxImportSource: undefined,
    }),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  esbuild: {
    // Target modern browsers
    target: 'es2020',
    // Format output
    format: 'esm',
    // Enable minification in production
    minify: process.env.NODE_ENV === 'production',
    // Tree shaking
    treeShaking: true,
    // Drop console and debugger in production
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
    // Legal comments
    legalComments: 'none',
    // Source maps
    sourcemap: process.env.NODE_ENV === 'development',
    // Keep names for better debugging
    keepNames: true,
    // JSX factory (React 17+ automatic JSX)
    jsx: 'automatic',
    // Log level
    logLevel: 'info',
    // Charset
    charset: 'utf8',
  },
  build: {
    // Optimize build output
    minify: 'esbuild',
    // Target modern browsers
    target: 'es2020',
    // Chunk size warning limit
    chunkSizeWarningLimit: 1000,
    // Source maps for production debugging
    sourcemap: false,
    // CSS code splitting
    cssCodeSplit: true,
    // Rollup options
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
        },
        // Asset file naming
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
      },
    },
  },
  optimizeDeps: {
    // Use esbuild for dependency pre-bundling
    esbuildOptions: {
      target: 'es2020',
      // Define global constants
      define: {
        global: 'globalThis',
      },
    },
  },
})
