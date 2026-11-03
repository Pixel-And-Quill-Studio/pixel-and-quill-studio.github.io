// Astro configuration for the Pixel & Quill Studio website.
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://pixelandquillstudio.com",
  trailingSlash: "always",
  build: { format: "directory" },
  // Keep the generated markup readable and identical to the hand-written templates.
  compressHTML: false,
});
