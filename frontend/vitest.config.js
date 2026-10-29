import { defineConfig } from "vitest/config";

export default defineConfig({
  // @vitejs/plugin-react is deliberately not used here.
  //
  // package.json pins Vite 8, but vitest ships its own bundled Vite. The React
  // plugin ends up resolving against the other copy and its JSX transform
  // silently never runs, which surfaces as "React is not defined" in every
  // test that renders an element.
  //
  // esbuild's automatic JSX runtime does the same job for tests, needs no
  // plugin, and does not care which Vite version is loaded. Fast Refresh is
  // the only thing lost, and tests do not use it.
  esbuild: {
    jsx: "automatic",
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.js"],
    include: ["src/**/*.test.{js,jsx}"],
    css: false,
  },
});
