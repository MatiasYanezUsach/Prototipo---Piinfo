<template>
  <transition name="slide-up">
    <div class="progress-panel" v-if="store.isAnalyzing">
      <div class="progress-header">
        <div class="progress-icon">⏱️</div>
        <div class="progress-info">
          <h4>Análisis en Progreso</h4>
          <p>{{ getProgressMessage() }}</p>
        </div>
        <div class="time-info">
          <span class="time-current">{{ formatTime(store.liveMetrics.tiempo_actual) }}</span>
          <span class="time-separator">/</span>
          <span class="time-total">{{ formatTime(store.config.duracion) }}</span>
        </div>
      </div>
      
      <div class="progress-container">
        <div class="progress-track">
          <div 
            class="progress-fill" 
            :style="{ width: `${store.liveMetrics.progreso}%` }">
            <div class="progress-shine"></div>
          </div>
        </div>
        <div class="progress-percentage">
          {{ Math.round(store.liveMetrics.progreso) }}%
        </div>
      </div>
      
      <div class="progress-milestones">
        <div 
          v-for="milestone in milestones" 
          :key="milestone.percent"
          class="milestone"
          :class="{ 
            'completed': store.liveMetrics.progreso >= milestone.percent,
            'current': getCurrentMilestone() === milestone.percent 
          }">
          <div class="milestone-dot"></div>
          <span class="milestone-label">{{ milestone.label }}</span>
        </div>
      </div>
      
      <div class="progress-stats">
        <div class="stat-item">
          <span class="stat-icon">📊</span>
          <span class="stat-label">Datos procesados</span>
          <span class="stat-value">{{ Math.round(store.liveMetrics.progreso * 1.2) }}MB</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">🎯</span>
          <span class="stat-label">Precisión</span>
          <span class="stat-value">{{ Math.round(85 + store.liveMetrics.progreso * 0.15) }}%</span>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { useAnalysisStore } from '@/stores/analysis';
import { computed } from 'vue';

const store = useAnalysisStore();

const milestones = [
  { percent: 0, label: 'Iniciando' },
  { percent: 25, label: 'Calibrando' },
  { percent: 50, label: 'Analizando' },
  { percent: 75, label: 'Procesando' },
  { percent: 100, label: 'Completado' }
];

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const getProgressMessage = () => {
  const progress = store.liveMetrics.progreso;
  if (progress < 25) return 'Iniciando análisis y configuración de cámara...';
  if (progress < 50) return 'Calibrando sistemas de detección...';
  if (progress < 75) return 'Analizando patrones de comportamiento...';
  if (progress < 100) return 'Procesando resultados finales...';
  return 'Análisis completado exitosamente';
};

const getCurrentMilestone = () => {
  const progress = store.liveMetrics.progreso;
  for (let i = milestones.length - 1; i >= 0; i--) {
    if (progress >= milestones[i].percent) {
      return milestones[i].percent;
    }
  }
  return 0;
};
</script>

<style scoped>
.progress-panel {
  background: var(--gradient-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-hover);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.progress-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--gradient-accent);
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.progress-icon {
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: var(--gradient-accent);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  animation: pulse 2s ease-in-out infinite;
}

.progress-info {
  flex: 1;
}

.progress-info h4 {
  color: var(--color-heading);
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.progress-info p {
  color: var(--color-text);
  font-size: 0.95rem;
  margin: 0;
  opacity: 0.9;
}

.time-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'Courier New', monospace;
  font-size: 1.2rem;
  font-weight: 700;
}

.time-current {
  color: var(--color-accent);
}

.time-separator {
  color: var(--color-text);
  opacity: 0.5;
}

.time-total {
  color: var(--color-text);
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.progress-track {
  flex: 1;
  height: 12px;
  background: var(--color-background-mute);
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.progress-fill {
  height: 100%;
  background: var(--gradient-accent);
  border-radius: 6px;
  transition: width 0.3s ease;
  position: relative;
  overflow: hidden;
}

.progress-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s ease-in-out infinite;
}

.progress-percentage {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-accent);
  min-width: 50px;
  text-align: right;
}

.progress-milestones {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  position: relative;
}

.progress-milestones::before {
  content: '';
  position: absolute;
  top: 10px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-border);
  z-index: 1;
}

.milestone {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 2;
}

.milestone-dot {
  width: 20px;
  height: 20px;
  border: 3px solid var(--color-border);
  border-radius: 50%;
  background: var(--color-background);
  transition: all 0.3s ease;
}

.milestone.completed .milestone-dot {
  border-color: var(--color-accent);
  background: var(--color-accent);
  box-shadow: 0 0 10px rgba(102, 174, 244, 0.5);
}

.milestone.current .milestone-dot {
  border-color: var(--color-accent);
  background: var(--color-accent);
  animation: pulse 1.5s ease-in-out infinite;
  box-shadow: 0 0 15px rgba(102, 174, 244, 0.7);
}

.milestone-label {
  font-size: 0.8rem;
  color: var(--color-text);
  font-weight: 500;
  text-align: center;
}

.milestone.completed .milestone-label,
.milestone.current .milestone-label {
  color: var(--color-accent);
  font-weight: 600;
}

.progress-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  border-top: 1px solid var(--color-border);
  padding-top: 1.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.stat-icon {
  font-size: 1.3rem;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 174, 244, 0.1);
  border-radius: var(--radius-sm);
}

.stat-label {
  flex: 1;
  font-size: 0.9rem;
  color: var(--color-text);
}

.stat-value {
  font-weight: 700;
  color: var(--color-accent);
  font-size: 0.95rem;
}

/* Transiciones */
.slide-up-enter-active {
  transition: all 0.4s ease-out;
}

.slide-up-leave-active {
  transition: all 0.3s ease-in;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}
</style>