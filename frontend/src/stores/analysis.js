import { defineStore } from 'pinia'
import { io } from 'socket.io-client'
import { useToast } from 'vue-toastification'

export const useAnalysisStore = defineStore('analysis', {
  state: () => ({
    socket: null,
    isConnected: false,
    isAnalyzing: false,
    isPreviewing: false,
    config: {
      nombre: 'Usuario',
      camera_type: 'local',
      ip: '192.168.1.100:8080',
      duracion: 30,
      guardar_video: true,
      analisis_avanzado: true,
    },
    liveMetrics: {
      contacto: 0,
      gestos: 0,
      movimiento: 0,
      postura: 0,
      expresividad: 0,
      fluidez: 0,
      progreso: 0,
      tiempo_actual: 0,
    },
    videoFrame: null,
    reportPath: null,
    error: null,
    statusMessage: null,
    notification: {
      show: false,
      message: '',
      type: 'success', // 'success' | 'error'
    },
    // 📷 Streaming desde el navegador
    localStream: null,
    browserTimer: null,
  }),

  actions: {
    connect() {
      // Determinar URL del backend.
      // 1. Si existe la variable de entorno VITE_BACKEND_URL la utilizamos.
      // 2. En caso contrario usamos el hostname actual (útil para acceder desde móviles en la misma red)
      //    añadiendo el puerto por defecto 8000.
      //    Por ejemplo: http://192.168.100.65:8000
      const defaultHost = typeof window !== 'undefined'
        ? `http://${window.location.hostname}:8000`
        : 'http://localhost:8000'

      const backendUrl = import.meta.env.VITE_BACKEND_URL || defaultHost

      // Conectar al backend de FastAPI usando la URL determinada
      this.socket = io(backendUrl)

      this.socket.on('connect', () => {
        console.log('✅ Conectado al servidor de Socket.IO')
        this.isConnected = true
        this.error = null
        this.statusMessage = null
      })

      this.socket.on('disconnect', () => {
        console.log('❌ Desconectado del servidor de Socket.IO')
        this.isConnected = false
        this.isAnalyzing = false
      })

      this.socket.on('status_update', (data) => {
        this.statusMessage = data.message;
      });

      this.socket.on('live_metrics', (data) => {
        this.statusMessage = null; // Clear status message once we get data
        Object.assign(this.liveMetrics, data) // Mantiene la misma referencia reactiva
      })

      this.socket.on('video_frame', (data) => {
        this.videoFrame = `data:image/jpeg;base64,${data.image}`
      })

      this.socket.on('report_generated', (data) => {
        console.log(`📄 Reporte generado: ${data.file_path}`)
        this.reportPath = data.file_path
        this.showNotification(`Reporte generado con éxito.`)
      })
      
      this.socket.on('analysis_finished', () => {
        this.isAnalyzing = false;
        this.statusMessage = null;
        console.log('El análisis ha finalizado desde el servidor.');
      });

      this.socket.on('analysis_error', (data) => {
        console.error(`❌ Error en el análisis: ${data.error}`)
        this.error = data.error
        this.showNotification(`Error en el análisis: ${data.error}`, 'error');
        this.isAnalyzing = false
        this.statusMessage = null;
      })
    },

    disconnect() {
      if (this.socket) {
        this.socket.disconnect()
      }
    },

    async startAnalysis() {
      if (this.socket && this.isConnected) {
        console.log('▶️ Enviando evento start_analysis con config:', this.config)
        this.isAnalyzing = true
        this.reportPath = null
        this.error = null
        this.statusMessage = "Solicitando inicio de análisis...";

        // Si la cámara es del navegador, primero obtenemos permisos y comenzamos a enviar frames
        if (this.config.camera_type === 'browser') {
          const ok = await this.startBrowserStreaming()
          if (!ok) {
            this.isAnalyzing = false
            return
          }
        }

        this.socket.emit('start_analysis', this.config)
      } else {
        console.error('No se puede iniciar el análisis, no hay conexión de socket.')
        this.error = 'No estás conectado al servidor.'
      }
    },

    stopAnalysis() {
      if (this.socket && this.isConnected && this.isAnalyzing) {
        console.log('⏹️ Enviando evento stop_analysis')
        // Si estamos usando cámara del navegador detenemos streaming local
        if (this.config.camera_type === 'browser') {
          this.stopBrowserStreaming()
        }
        this.isAnalyzing = false
        this.socket.emit('stop_analysis')
      }
    },

    async startBrowserStreaming() {
      try {
        const constraints = {
          video: { facingMode: 'user', width: 640, height: 480 },
          audio: false,
        }
        this.localStream = await navigator.mediaDevices.getUserMedia(constraints)

        const videoEl = document.createElement('video')
        videoEl.srcObject = this.localStream

        // Esperar a que se tengan los metadatos para conocer dimensiones reales
        await new Promise((resolve) => {
          videoEl.onloadedmetadata = () => resolve()
        })

        await videoEl.play()

        // Ajustar canvas manteniendo la relación de aspecto para evitar distorsión
        const MAX_WIDTH = 640
        let vw = videoEl.videoWidth
        let vh = videoEl.videoHeight

        if (vw > MAX_WIDTH) {
          const scale = MAX_WIDTH / vw
          vw = Math.floor(vw * scale)
          vh = Math.floor(vh * scale)
        }

        const canvas = document.createElement('canvas')
        canvas.width = vw
        canvas.height = vh
        const ctx = canvas.getContext('2d')

        // Enviar ~10fps para balancear calidad y ancho de banda
        this.browserTimer = setInterval(() => {
          ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height)
          const dataURL = canvas.toDataURL('image/jpeg', 0.7)
          const base64 = dataURL.split(',')[1]
          if (this.socket && this.isConnected) {
            this.socket.emit('browser_frame', { image: base64 })
          }
        }, 100)
        return true
      } catch (err) {
        console.error('No se pudo acceder a la cámara', err)
        if (err.name === 'NotAllowedError' && window.isSecureContext === false) {
          this.showNotification('El navegador bloquea la cámara porque la página no es segura (HTTPS). Abre el sitio con https:// o localhost.', 'error')
        } else {
          this.showNotification('Permiso de cámara denegado o no disponible', 'error')
        }
        return false
      }
    },

    stopBrowserStreaming() {
      if (this.browserTimer) clearInterval(this.browserTimer)
      this.browserTimer = null
      if (this.localStream) {
        this.localStream.getTracks().forEach(t => t.stop())
        this.localStream = null
      }
    },

    showNotification(message, type = 'success') {
      const toast = useToast()
      toast(message, { type })
      // Mantener compatibilidad con el componente Notification (opcional)
      this.notification.message = message;
      this.notification.type = type;
      this.notification.show = true;
      setTimeout(() => {
        this.hideNotification();
      }, 6000)
    },

    hideNotification() {
      this.notification.show = false;
      this.notification.message = '';
    },

    resetMetrics() {
        this.liveMetrics = {
            contacto: 0,
            gestos: 0,
            movimiento: 0,
            postura: 0,
            expresividad: 0,
            fluidez: 0,
            progreso: 0,
            tiempo_actual: 0,
        };
        this.videoFrame = null;
        this.reportPath = null;
        this.error = null;
        this.statusMessage = null;
    }
  },
}) 