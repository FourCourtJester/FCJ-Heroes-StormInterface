import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwind from '@tailwindcss/vite'

// Relative asset paths, so one build works on GitHub Pages, on a custom domain, or
// opened straight off disk -- OBS loads these URLs directly.
export default defineConfig({
  base: './',
  plugins: [react(), tailwind()],
  // `target` is a JavaScript target, and `cssTarget` falls back to it -- so without
  // this line the CSS pipeline is told nothing and lowers nothing. Anything Tailwind
  // processes is fine either way; a stylesheet imported straight from a component is
  // not, and ships nesting that does nothing at all on any browser older than Chrome
  // 112. Silent, and invisible on anything new enough to develop on.
  //
  // These are the versions `MINIMUM_VERSIONS` promises, in the spelling esbuild
  // wants. `CSS_TARGET` in @single-studio/core is the same list, and a test keeps
  // this line matching it.
  build: { target: 'es2022', cssTarget: ['chrome83', 'firefox114', 'safari16'] },
  worker: { format: 'es' },

  // One copy of Yjs, however it is imported. Collaboration breaks in confusing ways
  // with two.
  resolve: { dedupe: ['yjs'] },
})
