import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import Toast, { POSITION } from 'vue-toastification'
import 'vue-toastification/dist/index.css'

// Importar estilos globales
import './assets/main.css'

// Configurar meta tags dinámicamente
document.title = 'ORATOR.IA - Análisis de Oratoria con IA'
const metaDescription = document.createElement('meta')
metaDescription.name = 'description'
metaDescription.content = 'Plataforma avanzada de análisis de oratoria utilizando inteligencia artificial para mejorar tus habilidades de presentación en tiempo real.'
document.head.appendChild(metaDescription)

const metaViewport = document.querySelector('meta[name="viewport"]')
if (metaViewport) {
  metaViewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
}

// Agregar fuente Inter si no está cargada
if (!document.querySelector('link[href*="Inter"]')) {
  const fontLink = document.createElement('link')
  fontLink.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap'
  fontLink.rel = 'stylesheet'
  document.head.appendChild(fontLink)
}

// Crear la aplicación
const app = createApp(App)

// Configurar Pinia
const pinia = createPinia()

// Plugin para manejo global de errores
app.config.errorHandler = (err, instance, info) => {
  console.error('Error global capturado:', err, info)
  
  // Aquí podrías enviar el error a un servicio de monitoreo
  // como Sentry, LogRocket, etc.
  
  // Mostrar notificación de error al usuario
  if (instance && instance.$store) {
    instance.$store.showNotification(
      'Ha ocurrido un error inesperado. Por favor, intenta nuevamente.',
      'error'
    )
  }
}

// Plugin para manejo de promesas rechazadas
window.addEventListener('unhandledrejection', (event) => {
  console.error('Promesa rechazada no manejada:', event.reason)
  event.preventDefault()
})

// Directiva personalizada para animaciones de entrada
app.directive('animate-in', {
  mounted(el, binding) {
    const animationType = binding.value || 'fadeInUp'
    const delay = binding.arg || 0
    
    el.style.opacity = '0'
    el.style.transform = 'translateY(20px)'
    
    setTimeout(() => {
      el.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)'
      el.style.opacity = '1'
      el.style.transform = 'translateY(0)'
      
      if (animationType === 'slideIn') {
        el.style.transform = 'translateX(0)'
      }
    }, delay)
  }
})

// Filtro global para formatear números
app.config.globalProperties.$formatNumber = (value, decimals = 1) => {
  if (isNaN(value)) return '0'
  return Number(value).toFixed(decimals)
}

// Filtro global para formatear tiempo
app.config.globalProperties.$formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Usar plugins
app.use(pinia)
app.use(router)

// Toast plugin
const toastOptions = {
  position: POSITION.TOP_RIGHT,
  timeout: 5000,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
}
app.use(Toast, toastOptions)

// Montar la aplicación
app.mount('#app')

// Optimización para Performance
// Preload de recursos críticos
const preloadResources = () => {
  // Precargar iconos o imágenes importantes aquí si es necesario
}

// Lazy loading para componentes no críticos
const observeIntersection = () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in')
        observer.unobserve(entry.target)
      }
    })
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  })

  // Observar elementos con clase lazy-animate
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.lazy-animate').forEach(el => {
      observer.observe(el)
    })
  })
}

// Service Worker para PWA (opcional)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  navigator.serviceWorker.register('/sw.js')
    .then(registration => {
      console.log('SW registrado:', registration)
    })
    .catch(error => {
      console.log('SW falló:', error)
    })
}

// Inicializar optimizaciones
preloadResources()
observeIntersection()

// Exportar la instancia de la aplicación para debugging en desarrollo
if (import.meta.env.DEV) {
  window.__VUE_APP__ = app
}