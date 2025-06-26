<template>
  <div class="config-panel animate-fadeInUp">
    <div class="panel-header">
      <div class="header-icon">⚙️</div>
      <h3>Configuración</h3>
      <div class="header-accent"></div>
    </div>
    
    <div class="form-grid">
      <div class="form-group">
        <label for="nombre">
          <span class="label-icon">👤</span>
          Nombre
        </label>
        <div class="input-wrapper">
          <input type="text" id="nombre" v-model="store.config.nombre" placeholder="Ingresa tu nombre">
        </div>
      </div>
      
      <div class="form-group">
        <label>
          <span class="label-icon">📹</span>
          Tipo de Cámara
        </label>
        <div class="radio-group">
          <div class="radio-option">
            <input type="radio" id="local" value="local" v-model="store.config.camera_type">
            <label for="local" class="radio-label">
              <span class="radio-custom"></span>
              Local
            </label>
          </div>
          <div class="radio-option">
            <input type="radio" id="ip" value="ip" v-model="store.config.camera_type">
            <label for="ip" class="radio-label">
              <span class="radio-custom"></span>
              IP Camera
            </label>
          </div>
        </div>
      </div>

      <div class="form-group" v-if="store.config.camera_type === 'ip'">
        <label for="ip_addr">
          <span class="label-icon">🌐</span>
          Dirección IP
        </label>
        <div class="input-wrapper">
          <input type="text" id="ip_addr" v-model="store.config.ip" placeholder="192.168.1.100:8080">
        </div>
      </div>

      <div class="form-group">
        <label for="duracion">
          <span class="label-icon">⏱️</span>
          Duración
        </label>
        <div class="input-wrapper number-input">
          <input type="number" id="duracion" min="10" max="300" v-model.number="store.config.duracion">
          <span class="input-suffix">seg</span>
        </div>
      </div>

      <div class="form-group toggle-group">
        <div class="toggle-item">
          <input type="checkbox" id="guardar_video" v-model="store.config.guardar_video" class="toggle-input">
          <label for="guardar_video" class="toggle-label">
            <span class="toggle-switch"></span>
            <span class="toggle-text">
              <span class="label-icon">💾</span>
              Guardar Video
            </span>
          </label>
        </div>

        <div class="toggle-item">
          <input type="checkbox" id="analisis_avanzado" v-model="store.config.analisis_avanzado" class="toggle-input">
          <label for="analisis_avanzado" class="toggle-label">
            <span class="toggle-switch"></span>
            <span class="toggle-text">
              <span class="label-icon">🔬</span>
              Análisis Avanzado
            </span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAnalysisStore } from '@/stores/analysis';
const store = useAnalysisStore();
</script>

<style scoped>
.config-panel {
  background: var(--gradient-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-hover);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.config-panel::before {
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
  font-size: 1.5rem;
  margin: 0;
  flex: 1;
}

.header-accent {
  width: 60px;
  height: 3px;
  background: var(--gradient-accent);
  border-radius: 2px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-heading);
}

.label-icon {
  font-size: 1.1rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper input[type="text"], 
.input-wrapper input[type="number"] {
  width: 100%;
  background: var(--color-background);
  color: var(--color-heading);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.875rem 1rem;
  font-size: 1rem;
  transition: all 0.3s ease;
  outline: none;
}

.input-wrapper input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(102, 174, 244, 0.1);
  transform: translateY(-1px);
}

.number-input {
  position: relative;
}

.input-suffix {
  position: absolute;
  right: 1rem;
  color: var(--color-text);
  font-size: 0.9rem;
  pointer-events: none;
}

.radio-group {
  display: flex;
  gap: 1rem;
}

.radio-option {
  flex: 1;
}

.radio-option input[type="radio"] {
  display: none;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: var(--color-background);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.radio-label:hover {
  border-color: var(--color-accent);
  transform: translateY(-1px);
}

.radio-custom {
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border);
  border-radius: 50%;
  position: relative;
  transition: all 0.3s ease;
}

.radio-option input:checked + .radio-label {
  border-color: var(--color-accent);
  background: rgba(102, 174, 244, 0.1);
}

.radio-option input:checked + .radio-label .radio-custom {
  border-color: var(--color-accent);
  background: var(--color-accent);
}

.radio-option input:checked + .radio-label .radio-custom::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
}

.toggle-group {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.toggle-item {
  display: flex;
  align-items: center;
}

.toggle-input {
  display: none;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  padding: 1rem;
  background: var(--color-background);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
  width: 100%;
}

.toggle-label:hover {
  border-color: var(--color-accent);
  transform: translateY(-1px);
}

.toggle-switch {
  width: 48px;
  height: 24px;
  background: var(--color-border);
  border-radius: 12px;
  position: relative;
  transition: all 0.3s ease;
}

.toggle-switch::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.toggle-input:checked + .toggle-label .toggle-switch {
  background: var(--color-accent);
}

.toggle-input:checked + .toggle-label .toggle-switch::after {
  transform: translateX(24px);
}

.toggle-input:checked + .toggle-label {
  border-color: var(--color-accent);
  background: rgba(102, 174, 244, 0.05);
}

.toggle-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: var(--color-heading);
}
</style>