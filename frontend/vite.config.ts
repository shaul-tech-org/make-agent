import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss(), react()],
  server: {
    port: 8700,
    host: "0.0.0.0",
    allowedHosts: ["make-agent.shaul.kr"],
    proxy: {
      "/api": {
        target: "http://localhost:8701",
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test-setup.ts",
  },
});
