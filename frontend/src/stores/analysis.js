import { defineStore } from 'pinia'
import { io } from 'socket.io-client'

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
  }),

  actions: {
    connect() {
      // Conectar al backend de FastAPI
      this.socket = io('http://localhost:8000')

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
        this.liveMetrics = data
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

    startAnalysis() {
      if (this.socket && this.isConnected) {
        console.log('▶️ Enviando evento start_analysis con config:', this.config)
        this.isAnalyzing = true
        this.reportPath = null
        this.error = null
        this.statusMessage = "Solicitando inicio de análisis...";
        this.socket.emit('start_analysis', this.config)
      } else {
        console.error('No se puede iniciar el análisis, no hay conexión de socket.')
        this.error = 'No estás conectado al servidor.'
      }
    },

    stopAnalysis() {
      if (this.socket && this.isConnected && this.isAnalyzing) {
        console.log('⏹️ Enviando evento stop_analysis')
        this.isAnalyzing = false
        this.socket.emit('stop_analysis')
      }
    },
    
    showNotification(message, type = 'success') {
      this.notification.message = message;
      this.notification.type = type;
      this.notification.show = true;

      setTimeout(() => {
        this.hideNotification();
      }, 6000); // Ocultar después de 6 segundos
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