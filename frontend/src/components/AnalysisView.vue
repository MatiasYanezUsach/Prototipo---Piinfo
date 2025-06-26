<template>
  <div class="analysis-container">
    <!-- Header con título del análisis -->
    <header class="analysis-header">
      <button class="back-btn" @click="$emit('back')">
        <span>←</span>
      </button>
      <h1>{{ analysisTitle }}</h1>
      <div class="live-indicator">
        <div class="live-dot"></div>
        <span>LIVE</span>
      </div>
    </header>

    <!-- Video/Micrófono principal -->
    <div class="main-visual">
      <div class="video-container" v-if="store.videoFrame">
        <img :src="store.videoFrame" alt="Video en vivo" class="video-stream">
        <!-- Overlay con información -->
        <div class="video-overlay">
          <div class="participant-info">
            <span class="participant-name">{{ store.config.nombre }}</span>
            <span class="session-type">{{ getSessionType() }}</span>
          </div>
        </div>
      </div>
      
      <!-- Placeholder con micrófono cuando no hay video -->
      <div v-else class="microphone-view">
        <div class="microphone-container">
          <div class="microphone">
            <div class="mic-body"></div>
            <div class="mic-stand"></div>
          </div>
          <!-- Ondas de sonido animadas -->
          <div class="sound-waves">
            <div class="wave wave-1"></div>
            <div class="wave wave-2"></div>
            <div class="wave wave-3"></div>
          </div>
        </div>
        <div class="audio-status">
          <span>Escuchando...</span>
          <div class="audio-bars">
            <div v-for="i in 5" :key="i" class="audio-bar" :style="getAudioBarStyle(i)"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Progreso de la sesión -->
    <div class="session-progress">
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: `${store.liveMetrics.progreso}%` }">
          <div class="progress-glow"></div>
        </div>
      </div>
      <div class="time-display">
        <span class="current-time">{{ formatTime(store.liveMetrics.tiempo_actual) }}</span>
        <span class="total-time">{{ formatTime(store.config.duracion) }}</span>
      </div>
    </div>

    <!-- Métricas en tiempo real -->
    <div class="metrics-section">
      <div class="metric-card verbal-card" :class="{ active: verbalMetricHigh }">
        <div class="metric-header">
          <h3>Análisis Verbal</h3>
          <div class="metric-icon">🗣️</div>
        </div>
        <div class="metric-visualizer">
          <div class="waveform">
            <div v-for="i in 20" :key="i" class="wave-bar" :style="getWaveBarStyle(i, 'verbal')"></div>
          </div>
        </div>
        <div class="metric-values">
          <div class="metric-item">
            <span class="label">Fluidez</span>
            <span class="value">{{ store.liveMetrics.fluidez.toFixed(1) }}/10</span>
          </div>
          <div class="metric-item">
            <span class="label">Pausas</span>
            <span class="value">{{ calculatePauses() }}</span>
          </div>
        </div>
      </div>

      <div class="metric-card nonverbal-card" :class="{ active: nonverbalMetricHigh }">
        <div class="metric-header">
          <h3>Análisis No Verbal</h3>
          <div class="metric-icon">👁️</div>
        </div>
        <div class="metric-visualizer">
          <div class="gesture-tracker">
            <div class="gesture-point" v-for="i in 8" :key="i" :style="getGesturePointStyle(i)"></div>
          </div>
        </div>
        <div class="metric-values">
          <div class="metric-item">
            <span class="label">Contacto Visual</span>
            <span class="value">{{ store.liveMetrics.contacto.toFixed(0) }}%</span>
          </div>
          <div class="metric-item">
            <span class="label">Gestos</span>
            <span class="value">{{ store.liveMetrics.gestos.toFixed(1) }}/s</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Indicadores rápidos -->
    <div class="quick-indicators">
      <div class="indicator" :class="getIndicatorClass('postura')">
        <div class="indicator-icon">🎯</div>
        <span class="indicator-label">Postura</span>
        <span class="indicator-value">{{ store.liveMetrics.postura.toFixed(1) }}</span>
      </div>
      
      <div class="indicator" :class="getIndicatorClass('expresividad')">
        <div class="indicator-icon">😊</div>
        <span class="indicator-label">Expresión</span>
        <span class="indicator-value">{{ store.liveMetrics.expresividad.toFixed(1) }}</span>
      </div>
      
      <div class="indicator" :class="getIndicatorClass('movimiento')">
        <div class="indicator-icon">🚶</div>
        <span class="indicator-label">Movimiento</span>
        <span class="indicator-value">{{ store.liveMetrics.movimiento.toFixed(0) }}px</span>
      </div>
    </div>

    <!-- Botón de finalizar -->
    <div class="action-footer">
      <button class="btn btn-primary btn-large finish-btn" @click="finishAnalysis">
        <span class="btn-icon">📊</span>
        <span class="btn-text">FINALIZAR</span>
      </button>
    </div>

    <!-- Notificación de análisis -->
    <div v-if="store.statusMessage" class="status-notification">
      <div class="notification-content">
        <div class="notification-icon">⚡</div>
        <span>{{ store.statusMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'

const emit = defineEmits(['back', 'finish'])
const store = useAnalysisStore()

const analysisTitle = ref('PRESENTACIÓN CON PÚBLICO MASIVO')
const audioLevels = ref(Array(5).fill(0))

// Computed properties
const verbalMetricHigh = computed(() => store.liveMetrics.fluidez > 7)
const nonverbalMetricHigh = computed(() => store.liveMetrics.contacto > 70)

// Methods
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const getSessionType = () => {
  switch (store.config.camera_type) {
    case 'ip': return 'Cámara Externa'
    default: return 'Análisis Local'
  }
}

const calculatePauses = () => {
  // Simular cálculo de pausas basado en fluidez
  const pausesPerMinute = Math.max(0, 5 - store.liveMetrics.fluidez)
  return pausesPerMinute.toFixed(1)
}

const getAudioBarStyle = (index) => {
  const height = audioLevels.value[index - 1] || Math.random() * 100
  return {
    height: `${height}%`,
    animationDelay: `${index * 0.1}s`
  }
}

const getWaveBarStyle = (index, type) => {
  const baseValue = type === 'verbal' ? store.liveMetrics.fluidez : store.liveMetrics.contacto
  const variation = Math.sin(Date.now() / 1000 + index) * 20 + baseValue * 8
  return {
    height: `${Math.max(10, Math.min(100, variation))}%`,
    animationDelay: `${index * 0.05}s`
  }
}

const getGesturePointStyle = (index) => {
  const angle = (index / 8) * 360
  const radius = 30 + Math.sin(Date.now() / 1000 + index) * 10
  const x = Math.cos(angle * Math.PI / 180) * radius
  const y = Math.sin(angle * Math.PI / 180) * radius
  
  return {
    transform: `translate(${x}px, ${y}px)`,
    opacity: store.liveMetrics.gestos > 1 ? 1 : 0.3
  }
}

const getIndicatorClass = (metric) => {
  const value = store.liveMetrics[metric]
  const max = metric === 'movimiento' ? 50 : 10
  const percentage = (value / max) * 100
  
  if (percentage >= 80) return 'excellent'
  if (percentage >= 60) return 'good'
  if (percentage >= 40) return 'average'
  return 'poor'
}

const finishAnalysis = () => {
  store.stopAnalysis()
  emit('finish')
}

// Simular niveles de audio
const updateAudioLevels = () => {
  audioLevels.value = audioLevels.value.map(() => Math.random() * 100)
}

onMounted(() => {
  const interval = setInterval(updateAudioLevels, 200)
  onUnmounted(() => clearInterval(interval))
})
</script>

<style scoped>
.analysis-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
  display: flex;
  flex-direction: column;
  padding-bottom: 100px; /* Espacio para navegación global */
}

.analysis-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) var(--spacing-md);
  background: var(--color-primary);
  color: var(--color-white);
}

.back-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: var(--color-white);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.analysis-header h1 {
  flex: 1;
  text-align: center;
  font-size: var(--font-size-base);
  font-weight: 600;
  margin: 0 var(--spacing-md);
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-error);
  animation: pulse 1s ease-in-out infinite;
}

.main-visual {
  height: 300px;
  margin: var(--spacing-md);
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
}

.video-container {
  width: 100%;
  height: 100%;
  position: relative;
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
  padding: var(--spacing-lg);
}

.participant-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  color: var(--color-white);
}

.participant-name {
  font-size: var(--font-size-lg);
  font-weight: 600;
}

.session-type {
  font-size: var(--font-size-sm);
  opacity: 0.8;
}

.microphone-view {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.microphone-container {
  position: relative;
  z-index: 2;
}

.microphone {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.mic-body {
  width: 60px;
  height: 80px;
  background: var(--color-white);
  border-radius: 30px 30px 0 0;
  position: relative;
  box-shadow: var(--shadow-lg);
}

.mic-body::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 40px;
  background: var(--color-gray-300);
  border-radius: 15px;
}

.mic-stand {
  width: 4px;
  height: 40px;
  background: var(--color-white);
  margin-top: 5px;
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
  width: 100px;
  height: 100px;
  margin: -50px;
}

.wave-2 {
  width: 150px;
  height: 150px;
  margin: -75px;
  animation-delay: 0.5s;
}

.wave-3 {
  width: 200px;
  height: 200px;
  margin: -100px;
  animation-delay: 1s;
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

.audio-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  color: var(--color-white);
  z-index: 2;
}

.audio-bars {
  display: flex;
  gap: 3px;
  align-items: end;
  height: 30px;
}

.audio-bar {
  width: 4px;
  background: var(--color-white);
  border-radius: 2px;
  animation: audioBar 0.5s ease-in-out infinite alternate;
  min-height: 4px;
}

@keyframes audioBar {
  from { opacity: 0.3; }
  to { opacity: 1; }
}

.session-progress {
  padding: 0 var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.progress-track {
  height: 6px;
  background: var(--color-gray-300);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: var(--spacing-sm);
}

.progress-fill {
  height: 100%;
  background: var(--gradient-secondary);
  border-radius: 3px;
  position: relative;
  transition: width 0.3s ease;
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

@keyframes glow {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}

.time-display {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
  color: var(--color-gray-600);
  font-family: monospace;
}

.metrics-section {
  padding: 0 var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.metric-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-md);
  border-left: 4px solid var(--color-gray-300);
  transition: all 0.3s ease;
}

.metric-card.active {
  border-left-color: var(--color-accent);
  box-shadow: var(--shadow-lg);
}

.verbal-card.active {
  border-left-color: var(--color-success);
}

.nonverbal-card.active {
  border-left-color: var(--color-info);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.metric-header h3 {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-primary);
}

.metric-icon {
  font-size: 1.5rem;
}

.metric-visualizer {
  height: 80px;
  margin-bottom: var(--spacing-md);
  position: relative;
  display: flex;
  align-items: end;
  justify-content: center;
}

.waveform {
  display: flex;
  gap: 2px;
  align-items: end;
  height: 100%;
}

.wave-bar {
  width: 3px;
  background: var(--gradient-secondary);
  border-radius: 2px;
  animation: waveBar 1s ease-in-out infinite alternate;
  min-height: 5px;
}

@keyframes waveBar {
  from { opacity: 0.3; }
  to { opacity: 1; }
}

.gesture-tracker {
  position: relative;
  width: 80px;
  height: 80px;
  border: 2px dashed var(--color-gray-300);
  border-radius: 50%;
  margin: 0 auto;
}

.gesture-point {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--color-accent);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  margin: -4px;
  transition: all 0.3s ease;
}

.metric-values {
  display: flex;
  justify-content: space-between;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.metric-item .label {
  font-size: var(--font-size-xs);
  color: var(--color-gray-600);
}

.metric-item .value {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-primary);
}

.quick-indicators {
  display: flex;
  justify-content: space-around;
  padding: 0 var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-md);
  background: var(--color-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  min-width: 80px;
}

.indicator-icon {
  font-size: 1.5rem;
}

.indicator-label {
  font-size: var(--font-size-xs);
  color: var(--color-gray-600);
  text-align: center;
}

.indicator-value {
  font-size: var(--font-size-base);
  font-weight: 600;
}

.indicator.excellent {
  border-top: 3px solid var(--color-success);
}

.indicator.excellent .indicator-value {
  color: var(--color-success);
}

.indicator.good {
  border-top: 3px solid var(--color-info);
}

.indicator.good .indicator-value {
  color: var(--color-info);
}

.indicator.average {
  border-top: 3px solid var(--color-warning);
}

.indicator.average .indicator-value {
  color: var(--color-warning);
}

.indicator.poor {
  border-top: 3px solid var(--color-error);
}

.indicator.poor .indicator-value {
  color: var(--color-error);
}

.action-footer {
  padding: var(--spacing-lg) var(--spacing-md);
  margin-top: auto;
}

.finish-btn {
  width: 100%;
  background: var(--gradient-secondary);
  box-shadow: var(--shadow-lg);
}

.status-notification {
  position: fixed;
  top: 80px;
  left: var(--spacing-md);
  right: var(--spacing-md);
  background: var(--color-white);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  box-shadow: var(--shadow-lg);
  border-left: 4px solid var(--color-accent);
  z-index: var(--z-fixed);
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.notification-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.notification-icon {
  font-size: 1.3rem;
}
</style>