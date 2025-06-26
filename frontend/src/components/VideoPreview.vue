<template>
  <div class="video-preview-panel animate-fadeInUp">
    <div class="panel-header">
      <div class="header-icon">📷</div>
      <h3>Vista Previa</h3>
      <div class="recording-indicator" v-if="store.isAnalyzing">
        <div class="recording-dot"></div>
        <span>REC</span>
      </div>
    </div>
    
    <div class="video-container" :class="{ 'has-video': store.videoFrame, 'analyzing': store.isAnalyzing }">
      <div v-if="store.videoFrame" class="video-wrapper">
        <img :src="store.videoFrame" alt="Video Stream" class="video-stream">
        <div class="video-overlay">
          <div class="overlay-info">
            <div class="info-item">
              <span class="info-icon">📊</span>
              <span>Analizando en tiempo real</span>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="placeholder" :class="{ 'connecting': store.statusMessage }">
        <div class="placeholder-content">
          <div class="placeholder-icon">
            <div v-if="store.statusMessage" class="loading-spinner"></div>
            <span v-else>📹</span>
          </div>
          <h4>{{ store.statusMessage || 'Vista Previa del Video' }}</h4>
          <p v-if="!store.statusMessage">
            La transmisión del video aparecerá aquí cuando inicie el análisis
          </p>
          <div v-if="store.statusMessage" class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
      
      <!-- Indicadores de esquina -->
      <div class="corner-indicators" v-if="store.isAnalyzing">
        <div class="corner-indicator top-left">
          <div class="indicator-line horizontal"></div>
          <div class="indicator-line vertical"></div>
        </div>
        <div class="corner-indicator top-right">
          <div class="indicator-line horizontal"></div>
          <div class="indicator-line vertical"></div>
        </div>
        <div class="corner-indicator bottom-left">
          <div class="indicator-line horizontal"></div>
          <div class="indicator-line vertical"></div>
        </div>
        <div class="corner-indicator bottom-right">
          <div class="indicator-line horizontal"></div>
          <div class="indicator-line vertical"></div>
        </div>
      </div>
    </div>
    
    <!-- Controles de video -->
    <div class="video-controls" v-if="store.videoFrame">
      <div class="controls-left">
        <div class="resolution-info">
          <span class="info-label">Calidad:</span>
          <span class="info-value">HD</span>
        </div>
        <div class="fps-info">
          <span class="info-label">FPS:</span>
          <span class="info-value">30</span>
        </div>
      </div>
      
      <div class="controls-right">
        <button class="control-btn" title="Pantalla completa">
          🔍
        </button>
        <button class="control-btn" title="Configuración">
          ⚙️
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAnalysisStore } from '@/stores/analysis';
const store = useAnalysisStore();
</script>

<style scoped>
.video-preview-panel {
  background: var(--gradient-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-hover);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  flex-grow: 1;
  position: relative;
  overflow: hidden;
}

.video-preview-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--gradient-primary);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  position: relative;
}

.header-icon {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--gradient-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}

.panel-header h3 {
  color: var(--color-heading);
  font-weight: 700;
  font-size: 1.3rem;
  margin: 0;
  flex: 1;
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--color-error);
  background: rgba(255, 68, 68, 0.1);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 68, 68, 0.3);
}

.recording-dot {
  width: 8px;
  height: 8px;
  background: var(--color-error);
  border-radius: 50%;
  animation: pulse 1s ease-in-out infinite;
}

.video-container {
  background: #000;
  min-height: 480px;
  border-radius: var(--radius-md);
  overflow: hidden;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
}

.video-container.analyzing {
  box-shadow: 
    inset 0 0 20px rgba(0, 0, 0, 0.5),
    0 0 30px rgba(102, 174, 244, 0.3);
}

.video-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-stream {
  max-width: 100%;
  max-height: 100%;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-md);
}

.video-overlay {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  right: 1rem;
  background: rgba(0, 0, 0, 0.7);
  border-radius: var(--radius-sm);
  padding: 0.75rem;
  backdrop-filter: blur(10px);
}

.overlay-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
}

.info-icon {
  font-size: 1.1rem;
}

.placeholder {
  color: var(--color-text);
  text-align: center;
  padding: 3rem 2rem;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-content {
  max-width: 400px;
}

.placeholder-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.7;
  display: flex;
  justify-content: center;
}

.placeholder h4 {
  color: var(--color-heading);
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.placeholder p {
  color: var(--color-text);
  font-size: 1rem;
  line-height: 1.5;
  opacity: 0.8;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top: 3px solid var(--color-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-dots {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: var(--color-accent);
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

.corner-indicators {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.corner-indicator {
  position: absolute;
  width: 20px;
  height: 20px;
}

.corner-indicator.top-left { top: 1rem; left: 1rem; }
.corner-indicator.top-right { top: 1rem; right: 1rem; }
.corner-indicator.bottom-left { bottom: 1rem; left: 1rem; }
.corner-indicator.bottom-right { bottom: 1rem; right: 1rem; }

.indicator-line {
  background: var(--color-accent);
  position: absolute;
  opacity: 0.8;
}

.indicator-line.horizontal {
  width: 20px;
  height: 2px;
}

.indicator-line.vertical {
  width: 2px;
  height: 20px;
}

.top-left .horizontal { top: 0; left: 0; }
.top-left .vertical { top: 0; left: 0; }

.top-right .horizontal { top: 0; right: 0; }
.top-right .vertical { top: 0; right: 0; }

.bottom-left .horizontal { bottom: 0; left: 0; }
.bottom-left .vertical { bottom: 0; left: 0; }

.bottom-right .horizontal { bottom: 0; right: 0; }
.bottom-right .vertical { bottom: 0; right: 0; }

.video-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding: 1rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.controls-left {
  display: flex;
  gap: 1.5rem;
}

.resolution-info, .fps-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-label {
  color: var(--color-text);
  font-size: 0.9rem;
}

.info-value {
  color: var(--color-accent);
  font-weight: 600;
  font-size: 0.9rem;
}

.controls-right {
  display: flex;
  gap: 0.5rem;
}

.control-btn {
  background: var(--color-background-mute);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.control-btn:hover {
  background: var(--color-border);
  transform: translateY(-1px);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}
</style>