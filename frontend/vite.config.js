import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // ensures assets are correctly resolved when deploying under subpaths
  root: './',
  base: './',

  server: {
    // automatically open the browser when you run `npm run dev`
    open: true,

    // enable CORS (optional, but helpful for local API testing)
    cors: true,

    // proxy API requests to your backend
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // change this if your backend runs elsewhere
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },

  // optional — improves build output compatibility
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
