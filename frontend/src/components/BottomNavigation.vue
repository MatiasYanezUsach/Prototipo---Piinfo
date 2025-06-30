<template>
    <nav class="bottom-navigation">
      <div class="nav-items">
        <button 
          v-for="item in navItems" 
          :key="item.id"
          class="nav-item"
          :class="{ active: activeItem === item.id }"
          @click="$emit('navigate', item.view)">
          
          <div class="nav-icon-container">
            <div class="nav-icon">{{ item.icon }}</div>
            <div v-if="item.badge" class="nav-badge">{{ item.badge }}</div>
          </div>
          <span class="nav-label">{{ item.label }}</span>
          
          <!-- Indicador de activo -->
          <div v-if="activeItem === item.id" class="active-indicator"></div>
        </button>
      </div>
    </nav>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  
  const props = defineProps({
    activeView: {
      type: String,
      default: 'HomeView'
    },
    analysisActive: {
      type: Boolean,
      default: false
    }
  })
  
  const emit = defineEmits(['navigate'])
  
  // Mapeo de vistas a items de navegación
  const viewToNavItem = {
    'HomeView': 'home',
    'AnalysisView': 'analysis',
    'SimulationsView': 'simulations',
    'TrainingProgressView': 'progress',
    'CalendarView': 'calendar'
  }
  
  const activeItem = computed(() => {
    return viewToNavItem[props.activeView] || 'home'
  })
  
  // Items de navegación
  const navItems = computed(() => [
    {
      id: 'home',
      icon: '🏠',
      label: 'Inicio',
      view: 'HomeView'
    },
    {
      id: 'analysis',
      icon: '🎯',
      label: 'Análisis',
      view: 'AnalysisView',
      badge: props.analysisActive ? '●' : null
    },
    {
      id: 'simulations',
      icon: '➕',
      label: 'Nuevo',
      view: 'SimulationsView'
    },
    {
      id: 'progress',
      icon: '📊',
      label: 'Progreso',
      view: 'TrainingProgressView'
    },
    {
      id: 'calendar',
      icon: '📅',
      label: 'Calendario',
      view: 'CalendarView'
    }
  ])
  </script>
  
  <style scoped>
  .bottom-navigation {
    background: var(--color-white);
    /* Eliminamos el borde superior para evitar contornos */
    padding: var(--spacing-sm) 0;
    position: sticky;
    bottom: 0;
    z-index: var(--z-fixed);
    backdrop-filter: blur(8px);
    box-shadow: 0 -2px 20px rgba(0, 0, 0, 0.1);
  }
  
  .nav-items {
    display: flex;
    justify-content: space-around;
    align-items: center;
    width: 100%;
    padding: 0 var(--spacing-sm);
  }
  
  .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-sm);
    border: none;
    background: transparent;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    min-width: 60px;
    border-radius: var(--radius-md);
  }
  
  .nav-item:hover {
    background: rgba(66, 165, 245, 0.05);
    transform: translateY(-1px);
  }
  
  .nav-item.active {
    color: var(--color-primary);
  }
  
  .nav-icon-container {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .nav-icon {
    font-size: 1.4rem;
    transition: all 0.3s ease;
    filter: grayscale(100%);
  }
  
  .nav-item.active .nav-icon {
    filter: grayscale(0%);
    transform: scale(1.1);
  }
  
  .nav-badge {
    position: absolute;
    top: -8px;
    right: -8px;
    background: var(--color-error);
    color: var(--color-white);
    font-size: 0.7rem;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    animation: pulse 1.5s ease-in-out infinite;
  }
  
  .nav-label {
    font-size: var(--font-size-xs);
    font-weight: 500;
    color: var(--color-gray-500);
    transition: all 0.3s ease;
    text-align: center;
    line-height: 1.2;
  }
  
  .nav-item.active .nav-label {
    color: var(--color-primary);
    font-weight: 600;
  }
  
  .active-indicator {
    position: absolute;
    bottom: -var(--spacing-sm);
    left: 50%;
    transform: translateX(-50%);
    width: 20px;
    height: 3px;
    background: var(--color-primary);
    border-radius: 2px;
    animation: slideUp 0.3s ease-out;
  }
  
  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }
  
  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
      opacity: 1;
    }
    50% {
      transform: scale(1.2);
      opacity: 0.8;
    }
  }
  
  /* Responsive adjustments */
  @media (max-width: 320px) {
    .nav-items {
      padding: 0 var(--spacing-xs);
    }
    
    .nav-item {
      min-width: 50px;
      padding: var(--spacing-xs);
    }
    
    .nav-icon {
      font-size: 1.2rem;
    }
    
    .nav-label {
      font-size: 0.65rem;
    }
  }
  
  @media (min-width: 768px) {
    .bottom-navigation {
      position: static;
      border-top: none;
      border-bottom: 1px solid var(--color-gray-200);
      order: -1;
    }
    
    .nav-items {
      max-width: 768px;
    }
  }
  </style>