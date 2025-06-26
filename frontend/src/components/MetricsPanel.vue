<template>
  <div class="metrics-panel animate-fadeInUp">
    <div class="panel-header">
      <div class="header-icon">📊</div>
      <h3>Métricas en Tiempo Real</h3>
      <div class="live-indicator">
        <div class="live-dot"></div>
        <span>LIVE</span>
      </div>
    </div>
    
    <div class="metrics-grid">
      <div v-for="metric in metrics" :key="metric.key" class="metric-card">
        <div class="metric-header">
          <span class="metric-icon">{{ metric.icon }}</span>
          <span class="metric-label">{{ metric.label }}</span>
        </div>
        
        <div class="metric-value">
          <span class="value-number">{{ formatValue(store.liveMetrics[metric.key], metric) }}</span>
          <span class="value-unit">{{ metric.unit }}</span>
        </div>
        
        <div class="progress-container">
          <div class="progress-track">
            <div 
              class="progress-fill" 
              :class="getProgressClass(store.liveMetrics[metric.key], metric)"
              :style="{ width: getProgressWidth(store.liveMetrics[metric.key], metric) }">
              <div class="progress-glow"></div>
            </div>
          </div>
          <div class="progress-labels">
            <span>0</span>
            <span>{{ metric.max }}{{ metric.unit }}</span>
          </div>
        </div>
        
        <div class="metric-status" :class="getStatusClass(store.liveMetrics[metric.key], metric)">
          {{ getStatusText(store.liveMetrics[metric.key], metric) }}
        </div>
      </div>
    </div>
    
    <!-- Resumen general -->
    <div class="metrics-summary">
      <div class="summary-item">
        <span class="summary-label">Puntuación General</span>
        <div class="summary-score" :class="getOverallScoreClass()">
          {{ getOverallScore() }}/10
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAnalysisStore } from '@/stores/analysis';
import { computed } from 'vue';

const store = useAnalysisStore();

const metrics = [
  { key: 'contacto', label: 'Contacto Visual', icon: '👁️', max: 100, unit: '%', type: 'percentage' },
  { key: 'gestos', label: 'Gestos/seg', icon: '🙌', max: 3, unit: '', type: 'rate' },
  { key: 'movimiento', label: 'Movimiento', icon: '🚶', max: 50, unit: 'px', type: 'movement' },
  { key: 'postura', label: 'Postura', icon: '🎯', max: 10, unit: '/10', type: 'score' },
  { key: 'expresividad', label: 'Expresividad', icon: '😊', max: 10, unit: '/10', type: 'score' },
  { key: 'fluidez', label: 'Fluidez Verbal', icon: '🗣️', max: 10, unit: '/10', type: 'score' },
];

const formatValue = (value, metric) => {
  if (metric.type === 'percentage') {
    return Math.round(value);
  }
  return value.toFixed(1);
};

const getProgressWidth = (value, metric) => {
  const percentage = Math.min((value / metric.max) * 100, 100);
  return `${percentage}%`;
};

const getProgressClass = (value, metric) => {
  const percentage = (value / metric.max) * 100;
  if (percentage >= 80) return 'excellent';
  if (percentage >= 60) return 'good';
  if (percentage >= 40) return 'average';
  return 'needs-improvement';
};

const getStatusClass = (value, metric) => {
  const percentage = (value / metric.max) * 100;
  if (percentage >= 80) return 'status-excellent';
  if (percentage >= 60) return 'status-good';
  if (percentage >= 40) return 'status-average';
  return 'status-poor';
};

const getStatusText = (value, metric) => {
  const percentage = (value / metric.max) * 100;
  if (percentage >= 80) return 'Excelente';
  if (percentage >= 60) return 'Bueno';
  if (percentage >= 40) return 'Regular';
  return 'Mejorar';
};

const getOverallScore = () => {
  const scores = ['contacto', 'postura', 'expresividad', 'fluidez']
    .map(key => {
      const metric = metrics.find(m => m.key === key);
      return (store.liveMetrics[key] / metric.max) * 10;
    });
  
  const average = scores.reduce((sum, score) => sum + score, 0) / scores.length;
  return average.toFixed(1);
};

const getOverallScoreClass = () => {
  const score = parseFloat(getOverallScore());
  if (score >= 8) return 'score-excellent';
  if (score >= 6) return 'score-good';
  if (score >= 4) return 'score-average';
  return 'score-poor';
};
</script>

<style scoped>
.metrics-panel {
  background: var(--gradient-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-hover);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  width: 450px;
  position: relative;
  overflow: hidden;
}

.metrics-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--gradient-accent);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  position: relative;
}

.header-icon {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--gradient-accent);
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

.live-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-accent);
}

.live-dot {
  width: 8px;
  height: 8px;
  background: var(--color-accent);
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.metrics-grid {
  display: grid;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.metric-card:hover {
  border-color: var(--color-accent);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.metric-icon {
  font-size: 1.4rem;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 174, 244, 0.1);
  border-radius: var(--radius-sm);
}

.metric-label {
  color: var(--color-heading);
  font-weight: 600;
  font-size: 0.95rem;
}

.metric-value {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.value-number {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-accent);
  line-height: 1;
}

.value-unit {
  font-size: 1rem;
  color: var(--color-text);
  font-weight: 500;
}

.progress-container {
  margin-bottom: 1rem;
}

.progress-track {
  width: 100%;
  height: 8px;
  background: var(--color-background-mute);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.progress-fill.excellent {
  background: linear-gradient(90deg, #00C851, #00E659);
}

.progress-fill.good {
  background: linear-gradient(90deg, var(--color-accent), #87CEEB);
}

.progress-fill.average {
  background: linear-gradient(90deg, var(--color-warning), #FFB84D);
}

.progress-fill.needs-improvement {
  background: linear-gradient(90deg, var(--color-error), #FF7777);
}

.progress-glow {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: shimmer 2s ease-in-out infinite;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-text);
  margin-top: 0.5rem;
}

.metric-status {
  font-size: 0.85rem;
  font-weight: 600;
  text-align: center;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
}

.status-excellent {
  background: rgba(0, 200, 81, 0.2);
  color: #00E659;
}

.status-good {
  background: rgba(102, 174, 244, 0.2);
  color: var(--color-accent);
}

.status-average {
  background: rgba(255, 136, 0, 0.2);
  color: var(--color-warning);
}

.status-poor {
  background: rgba(255, 68, 68, 0.2);
  color: var(--color-error);
}

.metrics-summary {
  border-top: 1px solid var(--color-border);
  padding-top: 1.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-label {
  font-weight: 600;
  color: var(--color-heading);
}

.summary-score {
  font-size: 1.5rem;
  font-weight: 800;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
}

.score-excellent {
  background: rgba(0, 200, 81, 0.2);
  color: #00E659;
}

.score-good {
  background: rgba(102, 174, 244, 0.2);
  color: var(--color-accent);
}

.score-average {
  background: rgba(255, 136, 0, 0.2);
  color: var(--color-warning);
}

.score-poor {
  background: rgba(255, 68, 68, 0.2);
  color: var(--color-error);
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}
</style>