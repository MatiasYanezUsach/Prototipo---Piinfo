<template>
  <div class="home-container">
    <!-- Header profesional -->
    <header class="header">
      <div class="logo-section">
        <div class="logo-icon">
          <svg viewBox="0 0 32 32" class="logo-svg">
            <defs>
              <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#1a237e"/>
                <stop offset="50%" style="stop-color:#3949ab"/>
                <stop offset="100%" style="stop-color:#42a5f5"/>
              </linearGradient>
            </defs>
            <path d="M8 20 Q10 12 16 12 Q22 12 24 20 Q22 18 16 18 Q10 18 8 20 Z" fill="url(#logoGrad)"/>
            <circle cx="26" cy="16" r="1" fill="url(#logoGrad)" opacity="0.8"/>
            <circle cx="28" cy="14" r="0.8" fill="url(#logoGrad)" opacity="0.6"/>
            <circle cx="29" cy="16" r="0.6" fill="url(#logoGrad)" opacity="0.4"/>
            <circle cx="6" cy="14" r="0.5" fill="url(#logoGrad)" opacity="0.7"/>
            <circle cx="4" cy="16" r="0.4" fill="url(#logoGrad)" opacity="0.5"/>
            <circle cx="3" cy="18" r="0.3" fill="url(#logoGrad)" opacity="0.3"/>
          </svg>
        </div>
        <div class="logo-text">
          <h1>ORATOR.<span class="accent">IA</span></h1>
        </div>
      </div>
      
      <div class="connection-status" :class="getConnectionClass()">
        <div class="status-dot"></div>
      </div>
    </header>

    <!-- Vista de análisis activo CON VIDEO -->
    <div v-if="store.isAnalyzing" class="analysis-view">
      <div class="analysis-header">
        <h2>{{ getAnalysisTitle() }}</h2>
        <div class="live-indicator">
          <div class="live-dot"></div>
          <span>LIVE</span>
        </div>
      </div>

      <!-- Video Preview -->
      <div class="video-section">
        <div v-if="store.videoFrame" class="video-container">
          <img :src="store.videoFrame" alt="Video en vivo" class="video-stream">
          <div class="video-overlay">
            <div class="participant-info">
              <span class="participant-name">{{ store.config.nombre || 'Usuario' }}</span>
              <span class="session-type">Análisis en tiempo real</span>
            </div>
          </div>
        </div>
        
        <!-- Placeholder cuando no hay video -->
        <div v-else class="video-placeholder">
          <div class="microphone-container">
            <div class="microphone">🎤</div>
            <div class="sound-waves">
              <div class="wave wave-1"></div>
              <div class="wave wave-2"></div>
              <div class="wave wave-3"></div>
            </div>
          </div>
          <div class="status-text">
            <span>{{ store.statusMessage || 'Preparando análisis...' }}</span>
          </div>
        </div>
      </div>

      <!-- Progreso del análisis -->
      <div class="analysis-progress">
        <div class="progress-header">
          <span class="progress-label">Progreso del análisis</span>
          <span class="progress-time">{{ formatTime(store.liveMetrics.tiempo_actual) }} / {{ formatTime(store.config.duracion) }}</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: `${store.liveMetrics.progreso}%` }">
            <div class="progress-glow"></div>
          </div>
        </div>
        <span class="progress-percentage">{{ Math.round(store.liveMetrics.progreso) }}%</span>
      </div>

      <!-- Métricas en tiempo real -->
      <div class="live-metrics">
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-icon">👁️</div>
            <div class="metric-content">
              <span class="metric-label">Contacto Visual</span>
              <span class="metric-value">{{ (store.liveMetrics.contacto || 0).toFixed(0) }}%</span>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-icon">🗣️</div>
            <div class="metric-content">
              <span class="metric-label">Fluidez Verbal</span>
              <span class="metric-value">{{ (store.liveMetrics.fluidez || 0).toFixed(1) }}/10</span>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-content">
              <span class="metric-label">Postura</span>
              <span class="metric-value">{{ (store.liveMetrics.postura || 0).toFixed(1) }}/10</span>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-icon">😊</div>
            <div class="metric-content">
              <span class="metric-label">Expresividad</span>
              <span class="metric-value">{{ (store.liveMetrics.expresividad || 0).toFixed(1) }}/10</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Botón para detener -->
      <div class="analysis-actions">
        <button class="btn btn-stop" @click="stopAnalysis">
          <span class="btn-icon">⏹️</span>
          <span class="btn-text">FINALIZAR ANÁLISIS</span>
        </button>
      </div>
    </div>

    <!-- Vista principal cuando NO está analizando -->
    <main v-else class="main-content">
      <!-- Banner promocional -->
      <div class="promo-banner">
        <div class="promo-content">
          <h2>ROMPE TUS BARRERAS Y CONVIÉRTETE EN EXPERTO</h2>
          <button class="btn btn-secondary promo-btn" @click="openConfig">
            ACCEDER AL PLAN PRO
          </button>
        </div>
        
        <div class="promo-rating">
          <h3>EVALÚA TU</h3>
          <div class="stars">
            <span v-for="i in 4" :key="i" class="star">⭐</span>
          </div>
        </div>
      </div>

      <!-- Grid de opciones -->
      <div class="options-grid">
        <div class="option-card" @click="startQuickTest">
          <div class="option-icon">
            <span class="icon">⚡</span>
          </div>
          <div class="option-content">
            <h3>Test Rápido</h3>
            <p>Test inicial que permite orientar tus primeros pasos en ORATOR.IA</p>
          </div>
        </div>

        <div class="option-card" @click="openEvaluation">
          <div class="option-icon">
            <span class="icon">📊</span>
          </div>
          <div class="option-content">
            <h3>Evaluación</h3>
            <p>Evalúa tu nivel actual con un test creado por profesionales del área</p>
          </div>
        </div>
      </div>

      <!-- Casos de éxito -->
      <div class="success-section">
        <div class="success-content">
          <h3>¡ Casos de éxito !</h3>
          <p>Accede al material de expertos oradores, presentadores y conoce los casos de éxito.</p>
        </div>
        <div class="success-visual">
          <span class="presenter-icon">👨‍🏫</span>
        </div>
      </div>

      <!-- Botones de acción principales -->
      <div class="action-buttons">
        <button class="btn btn-primary btn-large" @click="startNewSession">
          <span class="btn-icon">➕</span>
          <span class="btn-text">Nueva Simulación</span>
        </button>
        
        <button class="btn btn-ghost" @click="viewMetrics">
          <span class="btn-icon">📊</span>
          <span class="btn-text">Ver mis métricas</span>
        </button>
      </div>
    </main>

    <!-- La navegación ahora es global en App.vue -->

    <!-- Modal de configuración -->
    <transition name="modal">
      <div v-if="showConfig" class="modal-overlay" @click="closeConfig">
        <div class="config-modal" @click.stop>
          <div class="modal-header">
            <h3>Configuración de Análisis</h3>
            <button class="close-btn" @click="closeConfig">✕</button>
          </div>
          
          <div class="modal-body">
            <div class="form-group">
              <label for="nombre">👤 Nombre del participante</label>
              <input 
                type="text" 
                id="nombre"
                class="input" 
                v-model="store.config.nombre" 
                placeholder="Ingresa tu nombre">
            </div>
            
            <div class="form-group">
              <label for="duracion">⏱️ Duración del análisis</label>
              <select v-model="store.config.duracion" class="input">
                <option value="30">30 segundos</option>
                <option value="60">1 minuto</option>
                <option value="120">2 minutos</option>
                <option value="300">5 minutos</option>
              </select>
            </div>

            <div class="form-group">
              <label>📹 Tipo de cámara</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input type="radio" value="local" v-model="store.config.camera_type">
                  <span class="radio-label">Cámara Local</span>
                </label>
                <label class="radio-option">
                  <input type="radio" value="ip" v-model="store.config.camera_type">
                  <span class="radio-label">Cámara IP</span>
                </label>
              </div>
            </div>

            <div v-if="store.config.camera_type === 'ip'" class="form-group">
              <label for="ip">🌐 Dirección IP</label>
              <input 
                type="text" 
                id="ip"
                class="input" 
                v-model="store.config.ip" 
                placeholder="192.168.1.100:8080">
            </div>

            <div class="form-group">
              <label class="checkbox-option">
                <input type="checkbox" v-model="store.config.guardar_video">
                <span class="checkbox-label">💾 Guardar video para revisión</span>
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-option">
                <input type="checkbox" v-model="store.config.analisis_avanzado">
                <span class="checkbox-label">🔬 Análisis avanzado</span>
              </label>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="closeConfig">Cancelar</button>
            <button 
              class="btn btn-primary" 
              @click="startAnalysis"
              :disabled="!canStartAnalysis">
              <span class="btn-icon">▶️</span>
              <span class="btn-text">Iniciar Análisis</span>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'

const emit = defineEmits(['navigate'])
const store = useAnalysisStore()

// Estado local
const showConfig = ref(false)

// Computed
const getConnectionClass = () => ({
  'connected': store.isConnected && !store.error,
  'error': store.error,
  'connecting': !store.isConnected && !store.error
})

const canStartAnalysis = computed(() => {
  return store.config.nombre?.trim() && store.isConnected
})

// Métodos principales
const openConfig = () => {
  showConfig.value = true
}

const closeConfig = () => {
  showConfig.value = false
}

const startQuickTest = () => {
  console.log('📝 Iniciando test rápido...')
  openConfig()
}

const startNewSession = () => {
  console.log('🎯 Nueva simulación...')
  if (!store.isAnalyzing) {
    // Navegar a SimulationsView
    emit('navigate', 'SimulationsView')
  }
}

const startAnalysis = () => {
  console.log('▶️ Iniciando análisis...')
  if (canStartAnalysis.value) {
    store.startAnalysis()
    closeConfig()
  }
}

const stopAnalysis = () => {
  console.log('⏹️ Deteniendo análisis...')
  store.stopAnalysis()
}

const openEvaluation = () => {
  console.log('📊 Abriendo evaluación avanzada...')
  // Navegar a AnalysisView para evaluación
  emit('navigate', 'AnalysisView')
}

const viewMetrics = () => {
  console.log('📈 Viendo métricas históricas...')
  // Navegar a TrainingProgressView
  emit('navigate', 'TrainingProgressView')
}

// Navegación ahora es manejada globalmente en App.vue

// Utilidades
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const getAnalysisTitle = () => {
  if (store.config.camera_type === 'ip') {
    return 'ANÁLISIS CON CÁMARA IP'
  }
  return 'ANÁLISIS CON CÁMARA LOCAL'
}

onMounted(() => {
  console.log('🚀 HomeView montado')
  store.connect()
})

onUnmounted(() => {
  console.log('👋 HomeView desmontado')
  store.disconnect()
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--gradient-background);
}

/* Header profesional */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6) var(--space-4);
  background: var(--white);
  border-bottom: 1px solid var(--gray-200);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  backdrop-filter: blur(8px);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: var(--gradient-primary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
}

.logo-svg {
  width: 32px;
  height: 32px;
}

.logo-text h1 {
  font-size: var(--font-size-2xl);
  font-weight: 900;
  color: var(--color-primary);
  letter-spacing: -1px;
}

.accent {
  background: var(--gradient-card);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.connection-status {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-dot {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--gray-400);
  transition: all 0.3s ease;
}

.connection-status.connected .status-dot {
  background: var(--success);
  animation: pulse-success 2s ease-in-out infinite;
}

.connection-status.error .status-dot {
  background: var(--error);
}

.connection-status.connecting .status-dot {
  background: var(--color-accent);
  animation: pulse-connecting 1s ease-in-out infinite;
}

/* Vista de análisis */
.analysis-view {
  flex: 1;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding-bottom: 100px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-primary);
  color: var(--white);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
}

.analysis-header h2 {
  font-size: var(--font-size-lg);
  font-weight: 700;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  font-weight: 700;
  background: rgba(255, 255, 255, 0.2);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--error);
  animation: pulse-live 1s ease-in-out infinite;
}

/* Video Section */
.video-section {
  background: var(--white);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  min-height: 300px;
}

.video-container {
  position: relative;
  width: 100%;
  height: 300px;
}

.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: var(--white);
  padding: var(--space-4);
}

.participant-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.participant-name {
  font-size: var(--font-size-lg);
  font-weight: 700;
}

.session-type {
  font-size: var(--font-size-sm);
  opacity: 0.9;
}

.video-placeholder {
  height: 300px;
  background: var(--gradient-primary);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--white);
  text-align: center;
  position: relative;
}

.microphone-container {
  position: relative;
  margin-bottom: var(--space-6);
}

.microphone {
  font-size: 4rem;
  margin-bottom: var(--space-4);
}

.sound-waves {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.wave {
  position: absolute;
  border: 2px solid rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: ripple 2s ease-out infinite;
}

.wave-1 {
  width: 80px;
  height: 80px;
  margin: -40px;
}

.wave-2 {
  width: 120px;
  height: 120px;
  margin: -60px;
  animation-delay: 0.5s;
}

.wave-3 {
  width: 160px;
  height: 160px;
  margin: -80px;
  animation-delay: 1s;
}

.status-text {
  font-size: var(--font-size-lg);
  font-weight: 600;
}

/* Progreso del análisis */
.analysis-progress {
  background: var(--white);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.progress-label {
  font-weight: 600;
  color: var(--color-primary);
}

.progress-time {
  font-size: var(--font-size-sm);
  color: var(--gray-600);
  font-family: monospace;
}

.progress-track {
  height: 8px;
  background: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--space-2);
  position: relative;
}

.progress-fill {
  height: 100%;
  background: var(--gradient-card);
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
  position: relative;
}

.progress-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5));
  animation: glow 2s ease-in-out infinite;
}

.progress-percentage {
  font-weight: 700;
  color: var(--color-primary);
  text-align: center;
  display: block;
}

/* Métricas en tiempo real */
.live-metrics {
  background: var(--white);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.metric-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--gray-50);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--color-accent);
}

.metric-icon {
  font-size: var(--font-size-xl);
}

.metric-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.metric-label {
  font-size: var(--font-size-xs);
  color: var(--gray-600);
}

.metric-value {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-primary);
}

/* Acciones del análisis */
.analysis-actions {
  display: flex;
  justify-content: center;
}

.btn-stop {
  background: linear-gradient(135deg, var(--error), #f87171);
  color: var(--white);
  border: none;
  padding: var(--space-4) var(--space-8);
  border-radius: var(--radius-full);
  font-weight: 700;
  box-shadow: var(--shadow-lg);
  transition: all 0.3s ease;
}

.btn-stop:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}

/* Vista principal */
.main-content {
  flex: 1;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  padding-bottom: 100px; /* Espacio para navegación global */
}

/* Banner promocional */
.promo-banner {
  background: var(--gradient-primary);
  color: var(--white);
  padding: var(--space-6);
  border-radius: var(--radius-2xl);
  position: relative;
  overflow: hidden;
  min-height: 140px;
  display: flex;
  align-items: center;
  box-shadow: var(--shadow-card);
}

.promo-content {
  flex: 1;
  z-index: 2;
}

.promo-content h2 {
  font-size: var(--font-size-lg);
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: var(--space-4);
}

.promo-btn {
  background: var(--white);
  color: var(--color-primary);
  border: none;
  font-weight: 700;
  box-shadow: var(--shadow-sm);
}

.promo-rating {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  text-align: center;
  z-index: 2;
}

.promo-rating h3 {
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-1);
}

.stars {
  display: flex;
  gap: 1px;
}

.star {
  font-size: var(--font-size-sm);
}

/* Grid de opciones */
.options-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.option-card {
  background: var(--white);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-card);
  border: 1px solid rgba(26, 35, 126, 0.08);
  text-align: center;
}

.option-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-xl);
}

.option-icon {
  width: 64px;
  height: 64px;
  background: var(--gradient-card);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-4);
  box-shadow: var(--shadow-md);
}

.icon {
  font-size: 1.8rem;
}

.option-content h3 {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: var(--space-2);
}

.option-content p {
  font-size: var(--font-size-sm);
  color: var(--gray-600);
  line-height: 1.5;
}

/* Casos de éxito */
.success-section {
  background: var(--white);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-card);
  text-align: center;
}

.success-content h3 {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: var(--space-3);
}

.success-content p {
  color: var(--gray-600);
  line-height: 1.6;
  margin-bottom: var(--space-4);
}

.success-visual {
  height: 80px;
  background: var(--gray-50);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.presenter-icon {
  font-size: 2rem;
}

/* Botones de acción */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border: none;
  border-radius: var(--radius-full);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  font-size: var(--font-size-sm);
}

.btn-primary {
  background: var(--gradient-card);
  color: var(--white);
  box-shadow: var(--shadow-md);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.btn-secondary {
  background: var(--white);
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
}

.btn-ghost {
  background: var(--white);
  color: var(--color-accent);
  border: 1px solid var(--gray-300);
}

.btn-large {
  padding: var(--space-4) var(--space-8);
  font-size: var(--font-size-base);
  min-height: 56px;
}

/* Estilos de navegación movidos a BottomNavigation.vue */

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: var(--z-modal);
  backdrop-filter: blur(4px);
}

.config-modal {
  background: var(--white);
  border-radius: var(--radius-2xl) var(--radius-2xl) 0 0;
  max-width: 430px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-2xl);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6);
  border-bottom: 1px solid var(--gray-200);
}

.modal-header h3 {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-primary);
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: var(--gray-100);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: var(--font-size-lg);
}

.modal-body {
  flex: 1;
  padding: var(--space-6);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-group label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--gray-700);
}

.input {
  width: 100%;
  padding: var(--space-3);
  border: 2px solid var(--gray-300);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
}

.input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.radio-group {
  display: flex;
  gap: var(--space-4);
}

.radio-option {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.radio-label {
  font-size: var(--font-size-sm);
}

.checkbox-option {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.checkbox-label {
  font-size: var(--font-size-sm);
}

.modal-footer {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-6);
  border-top: 1px solid var(--gray-200);
}

.modal-footer .btn {
  flex: 1;
  justify-content: center;
  min-height: 48px;
}

/* Transiciones */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .config-modal,
.modal-leave-to .config-modal {
  transform: translateY(100%);
}

/* Animaciones */
@keyframes pulse-success {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.1); }
}

@keyframes pulse-connecting {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.9); }
}

@keyframes pulse-live {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

@keyframes ripple {
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}

@keyframes glow {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}

/* Responsive */
@media (min-width: 768px) {
  .modal-overlay {
    align-items: center;
  }
  
  .config-modal {
    border-radius: var(--radius-2xl);
    max-height: 80vh;
  }
}
</style>