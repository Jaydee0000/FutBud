import { defineConfig } from 'astro/config';

import react from '@astrojs/react';

export default defineConfig({
  vite: {
    server: {
      watch: {
        usePolling: true,
      },
    },
  },

  integrations: [react()],
});