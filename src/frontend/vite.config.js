import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0", // ← esto es lo que permite acceder desde fuera del contenedor
    port: 5173,
  },
});
