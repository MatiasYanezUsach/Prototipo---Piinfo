import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  // Establecer la URL base para que los recursos estáticos se resuelvan
  // correctamente cuando la aplicación se despliegue desde la IP
  // 192.168.100.65:5173. Esto afecta tanto al modo de desarrollo como
  // a la compilación para producción.
  base: 'http://192.168.100.65:5173/',

  // Configuración del servidor de desarrollo para escuchar en la IP y puerto
  // indicados, de modo que se pueda acceder desde otros dispositivos en la
  // misma red.
  server: {
    host: '192.168.100.65',
    port: 5173,
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
}) 