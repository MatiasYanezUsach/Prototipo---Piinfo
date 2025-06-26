<template>
  <div id="app" class="app-container">
    <!-- Vista actual -->
    <component 
      :is="currentComponent" 
      @navigate="handleNavigation"
      @back="goBack"
      @startEvent="handleStartEvent"
      @startSimulation="handleStartSimulation"
      @finish="handleFinish" />

    <!-- Navegación global única (solo si no estamos en análisis activo) -->
    <BottomNavigation 
      v-if="!store.isAnalyzing"
      :activeView="currentView"
      :analysisActive="store.isAnalyzing"
      @navigate="handleNavigation" />

    <!-- Notificaciones -->
    <Notification />

    <!-- Indicador offline -->
    <transition name="slide-down">
      <div v-if="isOffline" class="offline-banner">
        <span>📡 Sin conexión a internet</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'

// Importar TODAS las vistas y componentes
import HomeView from '@/views/HomeView.vue'
import AnalysisView from '@/components/AnalysisView.vue'
import SimulationsView from '@/components/SimulationsView.vue'
import CalendarView from '@/components/CalendarView.vue'
import TrainingProgressView from '@/components/TrainingProgressView.vue'
import BottomNavigation from '@/components/BottomNavigation.vue'
import Notification from '@/components/Notification.vue'

const store = useAnalysisStore()

// Estado de navegación
const currentView = ref('HomeView')
const isOffline = ref(!navigator.onLine)

// Componente actual
const currentComponent = computed(() => {
  const components = {
    'HomeView': HomeView,
    'AnalysisView': AnalysisView,
    'SimulationsView': SimulationsView,
    'CalendarView': CalendarView,
    'TrainingProgressView': TrainingProgressView
  }
  return components[currentView.value] || HomeView
})

// Navegación
const handleNavigation = (viewName) => {
  console.log('Navegando a:', viewName)
  currentView.value = viewName
}

const goBack = () => {
  currentView.value = 'HomeView'
}

// Manejo de eventos específicos
const handleStartEvent = (event) => {
  console.log('Iniciando evento:', event)
  store.config.nombre = event.title
  store.config.duracion = event.duration * 60
  currentView.value = 'AnalysisView'
}

const handleStartSimulation = (simulation) => {
  console.log('Iniciando simulación:', simulation)
  store.config.nombre = simulation.title
  store.config.duracion = simulation.duration * 60
  currentView.value = 'AnalysisView'
}

const handleFinish = () => {
  console.log('Análisis finalizado')
  currentView.value = 'HomeView'
}

// Manejo de conexión
const handleOnline = () => { isOffline.value = false }
const handleOffline = () => { isOffline.value = true }

onMounted(() => {
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
  store.connect()
  console.log('✅ App montada correctamente')
})

onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
  store.disconnect()
})
</script>

<style>
/* Reset y configuración base */
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Variables CSS profesionales */
:root {
  /* Colores basados en mockups */
  --color-primary: #1a237e;
  --color-primary-light: #3949ab;
  --color-accent: #42a5f5;
  --color-accent-light: #64b5f6;
  --color-secondary: #7986cb;
  
  /* Gradientes exactos como mockups */
  --gradient-primary: linear-gradient(135deg, #1a237e 0%, #3949ab 50%, #42a5f5 100%);
  --gradient-card: linear-gradient(135deg, #3949ab 0%, #42a5f5 100%);
  --gradient-background: linear-gradient(180deg, #f5f7fa 0%, #e2e8f0 100%);
  
  /* Colores neutros */
  --white: #ffffff;
  --color-white: #ffffff;
  --gray-50: #f8fafc;
  --gray-100: #f1f5f9;
  --gray-200: #e2e8f0;
  --gray-300: #cbd5e1;
  --gray-400: #94a3b8;
  --gray-500: #64748b;
  --gray-600: #475569;
  --gray-700: #334155;
  --gray-800: #1e293b;
  --gray-900: #0f172a;
  
  /* Colores de estado */
  --success: #10b981;
  --color-success: #10b981;
  --warning: #f59e0b;
  --color-warning: #f59e0b;
  --error: #ef4444;
  --color-error: #ef4444;
  --info: #3b82f6;
  --color-info: #3b82f6;
  
  /* Espaciado sistema 8pt */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  
  /* Bordes redondeados */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 24px;
  --radius-full: 9999px;
  
  /* Sombras profesionales */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  --shadow-card: 0 8px 32px rgba(26, 35, 126, 0.12);
  
  /* Tipografía */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  
  /* Z-index */
  --z-base: 0;
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;

  /* Variables adicionales */
  --color-heading: var(--gray-900);
  --color-text: var(--gray-600);
  --color-background: var(--white);
  --color-background-mute: var(--gray-50);
  --color-border: var(--gray-300);
  --color-border-hover: var(--gray-400);
  --gradient-accent: var(--gradient-card);
  --shadow-glow: 0 0 20px rgba(66, 165, 245, 0.3);

  /* Espaciado adicional */
  --spacing-xs: var(--space-1);
  --spacing-sm: var(--space-2);
  --spacing-md: var(--space-4);
  --spacing-lg: var(--space-6);
  --spacing-xl: var(--space-8);
  --spacing-2xl: var(--space-12);
}

/* Configuración global */
html {
  scroll-behavior: smooth;
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

body {
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  line-height: 1.6;
  color: var(--gray-900);
  background: var(--gradient-background);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
  min-height: 100vh;
}

/* Contenedor principal */
.app-container {
  min-height: 100vh;
  max-width: 430px;
  margin: 0 auto;
  background: var(--white);
  box-shadow: var(--shadow-2xl);
  position: relative;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
}

/* Banner offline */
.offline-banner {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  z-index: var(--z-fixed);
  background: var(--error);
  color: var(--white);
  padding: var(--space-2) var(--space-6);
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-width: 430px;
  width: 100%;
  font-size: var(--font-size-sm);
  font-weight: 600;
  text-align: center;
}

/* Transiciones */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-100%);
}

/* Botones globales */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border: none;
  border-radius: var(--radius-full);
  font-family: inherit;
  font-weight: 600;
  font-size: var(--font-size-sm);
  line-height: 1;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.btn:active {
  transform: scale(0.98);
}

.btn-primary {
  background: var(--gradient-card);
  color: var(--white);
  box-shadow: var(--shadow-md);
}

.btn-primary:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-1px);
}

.btn-secondary {
  background: var(--white);
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.btn-secondary:hover {
  background: var(--color-primary);
  color: var(--white);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-ghost {
  background: transparent;
  color: var(--color-primary);
  border: 1px solid var(--gray-300);
}

.btn-ghost:hover {
  background: var(--gray-50);
  border-color: var(--color-primary);
  transform: translateY(-1px);
}

.btn-large {
  padding: var(--space-4) var(--space-8);
  font-size: var(--font-size-base);
}

/* Input global */
.input {
  width: 100%;
  padding: var(--space-4);
  border: 2px solid var(--gray-300);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: var(--font-size-base);
  line-height: 1.5;
  color: var(--gray-900);
  background: var(--white);
  transition: all 0.3s ease;
  outline: none;
}

.input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(66, 165, 245, 0.1);
}

.input::placeholder {
  color: var(--gray-400);
}

/* Animaciones */
.animate-fadeInUp {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Responsive */
@media (min-width: 768px) {
  .app-container {
    max-width: 768px;
  }
  
  .offline-banner {
    max-width: 768px;
  }
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: var(--gray-100);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: var(--color-accent);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary);
}

/* Accesibilidad */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

*:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* iOS fix */
@media screen and (max-width: 767px) {
  input[type="text"],
  input[type="email"],
  input[type="number"],
  input[type="tel"],
  input[type="password"],
  select,
  textarea {
    font-size: 16px !important;
  }
}
</style>