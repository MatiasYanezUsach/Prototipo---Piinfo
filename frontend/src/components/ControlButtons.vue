<template>
  <div class="control-buttons animate-fadeInUp">
    <button 
      @click="store.startAnalysis()"
      :disabled="!store.isConnected || store.isAnalyzing"
      class="control-btn start-button">
      <span class="btn-icon">▶️</span>
      <span class="btn-text">INICIAR ANÁLISIS</span>
      <div class="btn-shine"></div>
    </button>
    
    <button 
      @click="store.stopAnalysis()"
      :disabled="!store.isAnalyzing"
      class="control-btn stop-button">
      <span class="btn-icon">⏹️</span>
      <span class="btn-text">DETENER</span>
      <div class="btn-shine"></div>
    </button>
    
    <!-- Indicador de estado -->
    <div class="status-indicator" :class="{ 
      'connected': store.isConnected && !store.isAnalyzing,
      'analyzing': store.isAnalyzing,
      'disconnected': !store.isConnected 
    }">
      <div class="status-dot"></div>
      <span class="status-text">
        {{ store.isAnalyzing ? 'Analizando...' : store.isConnected ? 'Listo' : 'Desconectado' }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { useAnalysisStore } from '@/stores/analysis';
const store = useAnalysisStore();
</script>

<style scoped>
.control-buttons {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background: var(--gradient-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-hover);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.control-buttons::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--gradient-primary);
}

.control-btn {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: white;
  font-size: 1rem;
  font-weight: 700;
  border: none;
  border-radius: var(--radius-lg);
  padding: 1rem 2rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  min-width: 180px;
  justify-content: center;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.btn-icon {
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.btn-text {
  position: relative;
  z-index: 2;
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.6s ease;
}

.start-button {
  background: var(--gradient-accent);
  color: var(--color-background);
  box-shadow: var(--shadow-md);
}

.start-button:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.05);
  box-shadow: var(--shadow-glow), var(--shadow-lg);
}

.start-button:hover:not(:disabled) .btn-shine {
  left: 100%;
}

.start-button:hover:not(:disabled) .btn-icon {
  transform: scale(1.2);
}

.start-button:active:not(:disabled) {
  transform: translateY(-1px) scale(1.02);
}

.stop-button {
  background: linear-gradient(135deg, #e53935 0%, #c62828 100%);
  box-shadow: var(--shadow-md);
}

.stop-button:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 0 20px rgba(229, 57, 53, 0.4), var(--shadow-lg);
}

.stop-button:hover:not(:disabled) .btn-shine {
  left: 100%;
}

.stop-button:hover:not(:disabled) .btn-icon {
  transform: scale(1.2);
}

.stop-button:active:not(:disabled) {
  transform: translateY(-1px) scale(1.02);
}

.control-btn:disabled {
  background: var(--color-background-mute);
  color: var(--color-text);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  opacity: 0.6;
}

.control-btn:disabled .btn-icon {
  opacity: 0.5;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  background: var(--color-background);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: relative;
}

.status-dot::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  opacity: 0.6;
}

.status-indicator.connected .status-dot {
  background: var(--color-success);
}

.status-indicator.connected .status-dot::after {
  background: var(--color-success);
  animation: pulse 2s ease-in-out infinite;
}

.status-indicator.analyzing .status-dot {
  background: var(--color-accent);
}

.status-indicator.analyzing .status-dot::after {
  background: var(--color-accent);
  animation: pulse 1s ease-in-out infinite;
}

.status-indicator.disconnected .status-dot {
  background: var(--color-error);
}

.status-indicator.disconnected .status-dot::after {
  background: var(--color-error);
  animation: pulse 2s ease-in-out infinite;
}

.status-text {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-heading);
}

@media (max-width: 768px) {
  .control-buttons {
    flex-direction: column;
    gap: 1rem;
  }
  
  .control-btn {
    width: 100%;
    min-width: auto;
  }
  
  .status-indicator {
    order: -1;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.5);
    opacity: 0.2;
  }
}
</style>