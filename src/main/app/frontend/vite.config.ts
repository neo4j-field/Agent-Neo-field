import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
// @ts-ignore
import packageJson from "./package.json";

export default defineConfig({
  plugins: [react()],
  define: {
    "import.meta.env.PACKAGE_VERSION": JSON.stringify(packageJson.version),
  },
  server: {
    port: 3000,
  },
});
