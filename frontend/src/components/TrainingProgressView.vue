<template>
    <div class="training-container">
      <!-- Header -->
      <header class="training-header">
        <button class="back-btn" @click="$emit('back')">
          <span>←</span>
        </button>
        <h1>Plan de Entrenamiento</h1>
        <button class="settings-btn">
          <span>⚙️</span>
        </button>
      </header>
  
      <!-- Progreso general circular -->
      <div class="overall-progress">
        <div class="progress-circle" :style="getCircleStyle(overallProgress)">
          <div class="progress-inner">
            <span class="progress-value">{{ overallProgress }}%</span>
          </div>
        </div>
        <div class="progress-label">
          <h2>PLAN DE ENTRENAMIENTO</h2>
        </div>
      </div>
  
      <!-- Pestañas Verbal/No Verbal -->
      <div class="tab-selector">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'verbal' }"
          @click="activeTab = 'verbal'">
          VERBAL
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'nonverbal' }"
          @click="activeTab = 'nonverbal'">
          NO VERBAL
        </button>
      </div>
  
      <!-- Selector de tiempo -->
      <div class="time-selector">
        <select v-model="selectedPeriod" class="period-select">
          <option value="7">Últimos 7 días</option>
          <option value="30">Últimos 30 días</option>
          <option value="90">Últimos 90 días</option>
        </select>
      </div>
  
      <!-- Lista de entrenamientos -->
      <div class="training-list">
        <div 
          v-for="training in filteredTrainings" 
          :key="training.id"
          class="training-item"
          @click="openTraining(training)">
          
          <div class="training-progress">
            <div class="circular-progress" :style="getProgressStyle(training.progress)">
              <span class="progress-text">{{ training.progress }}%</span>
            </div>
          </div>
          
          <div class="training-info">
            <h3>{{ training.title }}</h3>
            <div class="training-meta">
              <span class="training-date">{{ formatDate(training.date) }}</span>
              <span class="training-sessions">
                Simulaciones completadas<br>
                {{ training.completed }}/{{ training.total }}
              </span>
            </div>
          </div>
          
          <div class="training-status">
            <div class="status-badge" :class="getStatusClass(training.progress)">
              {{ getStatusText(training.progress) }}
            </div>
          </div>
        </div>
      </div>
  
      <!-- Estadísticas rápidas -->
      <div class="quick-stats">
        <div class="stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.totalSessions }}</span>
            <span class="stat-label">Sesiones</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">⏱️</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.totalTime }}h</span>
            <span class="stat-label">Tiempo</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">📈</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.improvement }}%</span>
            <span class="stat-label">Mejora</span>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  
  const emit = defineEmits(['back', 'navigate'])
  
  // Estado reactivo
  const activeTab = ref('verbal')
  const selectedPeriod = ref('7')
  const overallProgress = ref(85)
  
  // Datos de entrenamiento
  const trainings = ref([
    {
      id: 1,
      title: 'Tono de voz',
      date: new Date(),
      progress: 100,
      completed: 1,
      total: 1,
      type: 'verbal'
    },
    {
      id: 2,
      title: 'Fluidez Verbal',
      date: new Date(Date.now() - 86400000),
      progress: 33,
      completed: 1,
      total: 3,
      type: 'verbal'
    },
    {
      id: 3,
      title: 'Uso adecuado de vocabulario',
      date: new Date(Date.now() - 172800000),
      progress: 66,
      completed: 2,
      total: 3,
      type: 'verbal'
    },
    {
      id: 4,
      title: 'Lenguaje corporal',
      date: new Date(Date.now() - 259200000),
      progress: 50,
      completed: 2,
      total: 4,
      type: 'nonverbal'
    },
    {
      id: 5,
      title: 'Contacto visual',
      date: new Date(Date.now() - 345600000),
      progress: 80,
      completed: 4,
      total: 5,
      type: 'nonverbal'
    }
  ])
  
  // Estadísticas
  const stats = ref({
    totalSessions: 12,
    totalTime: 8.5,
    improvement: 23
  })
  
  // Computed
  const filteredTrainings = computed(() => {
    return trainings.value.filter(training => training.type === activeTab.value)
  })
  
  // Métodos
  const getCircleStyle = (percentage) => {
    const angle = (percentage / 100) * 360
    return {
      background: `conic-gradient(var(--color-accent) 0deg ${angle}deg, var(--color-gray-200) ${angle}deg 360deg)`
    }
  }
  
  const getProgressStyle = (percentage) => {
    const angle = (percentage / 100) * 360
    return {
      background: `conic-gradient(var(--color-primary) 0deg ${angle}deg, var(--color-gray-300) ${angle}deg 360deg)`
    }
  }
  
  const getStatusClass = (progress) => {
    if (progress === 100) return 'completed'
    if (progress >= 50) return 'in-progress'
    return 'started'
  }
  
  const getStatusText = (progress) => {
    if (progress === 100) return 'Completado'
    if (progress >= 50) return 'En progreso'
    return 'Iniciado'
  }
  
  const formatDate = (date) => {
    const today = new Date()
    const diffTime = Math.abs(today - date)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 1) return 'Hoy'
    if (diffDays === 2) return '1 día atrás'
    return `${diffDays - 1} días atrás`
  }
  
  const openTraining = (training) => {
    console.log('Abrir entrenamiento:', training.title)
    // Aquí podrías navegar a una vista de detalle del entrenamiento
  }
  </script>
  
  <style scoped>
  .training-container {
    min-height: 100vh;
    background: var(--gradient-background);
    display: flex;
    flex-direction: column;
    padding: 0;
    padding-bottom: 80px; /* Espacio para navegación inferior */
  }
  
  .training-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-lg) var(--spacing-md);
    background: var(--gradient-primary);
    color: var(--color-white);
    border-bottom: 1px solid var(--color-gray-200);
  }
  
  .back-btn, .settings-btn {
    width: 36px;
    height: 36px;
    border: none;
    background: rgba(255, 255, 255, 0.15);
    color: var(--color-white);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .back-btn:hover, .settings-btn:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: scale(1.05);
  }
  
  .training-header h1 {
    font-size: var(--font-size-xl);
    font-weight: 600;
    color: var(--color-white);
  }
  
  .overall-progress {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: var(--spacing-2xl) var(--spacing-md);
    background: var(--color-white);
    margin: var(--spacing-md);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-card);
  }
  
  .progress-circle {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    margin-bottom: var(--spacing-lg);
  }
  
  .progress-inner {
    width: 110px;
    height: 110px;
    background: var(--color-white);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.05);
  }
  
  .progress-value {
    font-size: var(--font-size-3xl);
    font-weight: 800;
    color: var(--color-primary);
  }
  
  .progress-label h2 {
    color: var(--color-gray-600);
    font-size: var(--font-size-base);
    font-weight: 500;
    text-align: center;
    letter-spacing: 1px;
  }
  
  .tab-selector {
    display: flex;
    margin: 0 var(--spacing-md) var(--spacing-md);
    background: var(--color-white);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xs);
    box-shadow: var(--shadow-sm);
  }
  
  .tab-btn {
    flex: 1;
    padding: var(--spacing-md);
    border: none;
    background: transparent;
    border-radius: var(--radius-md);
    font-weight: 600;
    color: var(--color-gray-500);
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .tab-btn.active {
    background: var(--color-primary);
    color: var(--color-white);
    box-shadow: var(--shadow-sm);
  }
  
  .time-selector {
    padding: 0 var(--spacing-md);
    margin-bottom: var(--spacing-md);
  }
  
  .period-select {
    width: 100%;
    padding: var(--spacing-md);
    border: 2px solid var(--color-gray-300);
    border-radius: var(--radius-md);
    font-size: var(--font-size-sm);
    background: var(--color-white);
    color: var(--color-gray-700);
  }
  
  .training-list {
    flex: 1;
    padding: 0 var(--spacing-md);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
  }
  
  .training-item {
    background: var(--color-white);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    box-shadow: var(--shadow-card);
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .training-item:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
  
  .training-progress {
    flex-shrink: 0;
  }
  
  .circular-progress {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }
  
  .circular-progress::before {
    content: '';
    position: absolute;
    width: 38px;
    height: 38px;
    background: var(--color-white);
    border-radius: 50%;
  }
  
  .progress-text {
    position: relative;
    z-index: 1;
    font-size: var(--font-size-xs);
    font-weight: 700;
    color: var(--color-primary);
  }
  
  .training-info {
    flex: 1;
  }
  
  .training-info h3 {
    font-size: var(--font-size-lg);
    font-weight: 600;
    color: var(--color-primary);
    margin-bottom: var(--spacing-xs);
  }
  
  .training-meta {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }
  
  .training-date {
    font-size: var(--font-size-sm);
    color: var(--color-gray-500);
  }
  
  .training-sessions {
    font-size: var(--font-size-xs);
    color: var(--color-gray-600);
    line-height: 1.3;
  }
  
  .training-status {
    flex-shrink: 0;
  }
  
  .status-badge {
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-xs);
    font-weight: 600;
    text-align: center;
  }
  
  .status-badge.completed {
    background: rgba(16, 185, 129, 0.1);
    color: var(--color-success);
  }
  
  .status-badge.in-progress {
    background: rgba(59, 130, 246, 0.1);
    color: var(--color-info);
  }
  
  .status-badge.started {
    background: rgba(245, 158, 11, 0.1);
    color: var(--color-warning);
  }
  
  .quick-stats {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
    gap: var(--spacing-md);
    padding: 0 var(--spacing-md);
    margin-bottom: var(--spacing-xl);
  }
  
  .stat-card {
    flex: 1;
    background: var(--color-white);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    box-shadow: var(--shadow-sm);
  }
  
  .stat-icon {
    font-size: 1.5rem;
  }
  
  .stat-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }
  
  .stat-value {
    font-size: var(--font-size-lg);
    font-weight: 700;
    color: var(--color-primary);
  }
  
  .stat-label {
    font-size: var(--font-size-xs);
    color: var(--color-gray-500);
  }
  </style>