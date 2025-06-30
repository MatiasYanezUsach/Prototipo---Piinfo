<template>
    <div class="simulations-container">
      <!-- Header -->
      <header class="simulations-header">
        <button class="back-btn" @click="$emit('back')">
          <span>←</span>
        </button>
        <h1>Simulaciones</h1>
        <button class="filter-btn">
          <span>🔍</span>
        </button>
      </header>
  
      <!-- Lista de simulaciones -->
      <div class="simulations-list">
        <div 
          v-for="simulation in simulations" 
          :key="simulation.id"
          class="simulation-card"
          @click="selectSimulation(simulation)">
          
          <div class="simulation-image">
            <img :src="simulation.image" :alt="simulation.title" />
            <div class="simulation-overlay">
              <div class="play-button">
                <span>▶️</span>
              </div>
            </div>
          </div>
          
          <div class="simulation-content">
            <h3>{{ simulation.title }}</h3>
            <p>{{ simulation.description }}</p>
            
            <div class="simulation-meta">
              <div class="meta-item">
                <span class="meta-icon">⏱️</span>
                <span class="meta-text">{{ simulation.duration }} min</span>
              </div>
              <div class="meta-item">
                <span class="meta-icon">📊</span>
                <span class="meta-text">Nivel {{ simulation.level }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-icon">👥</span>
                <span class="meta-text">{{ simulation.participants }}</span>
              </div>
            </div>
            
            <div class="simulation-tags">
              <span 
                v-for="tag in simulation.tags" 
                :key="tag"
                class="tag"
                :class="getTagClass(tag)">
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Botón cargar más -->
      <div class="load-more">
        <button class="btn btn-ghost" @click="loadMore">
          <span>↻</span>
          Cargar más Contextos
        </button>
      </div>
  
      <!-- Modal de selección de simulación -->
      <div v-if="selectedSimulation" class="simulation-modal" @click="closeModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h2>{{ selectedSimulation.title }}</h2>
            <button class="close-btn" @click="closeModal">
              <span>✕</span>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="simulation-preview">
              <img :src="selectedSimulation.image" :alt="selectedSimulation.title" />
            </div>
            
            <div class="simulation-details">
              <p class="simulation-description">{{ selectedSimulation.fullDescription }}</p>
              
              <div class="details-grid">
                <div class="detail-item">
                  <span class="detail-label">Duración:</span>
                  <span class="detail-value">{{ selectedSimulation.duration }} minutos</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Dificultad:</span>
                  <span class="detail-value">{{ selectedSimulation.difficulty }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Análisis Verbal:</span>
                  <span class="detail-value">{{ selectedSimulation.verbalAnalysis ? 'Sí' : 'No' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Análisis No Verbal:</span>
                  <span class="detail-value">{{ selectedSimulation.nonVerbalAnalysis ? 'Sí' : 'No disponible' }}</span>
                </div>
              </div>
              
              <div class="simulation-objectives">
                <h4>Objetivos de aprendizaje:</h4>
                <ul>
                  <li v-for="objective in selectedSimulation.objectives" :key="objective">
                    {{ objective }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="closeModal">
              Cancelar
            </button>
            <button class="btn btn-primary" @click="startSimulation">
              <span>▶️</span>
              Iniciar Simulación
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import imgMassAudience from '@/assets/simulations/presentacion_publico_masivo.png'
  import imgConversation from '@/assets/simulations/conversacion_1v1.png'
  import imgInterview from '@/assets/simulations/entrevista_practica.png'
  import imgTeamMeeting from '@/assets/simulations/reunion_equipo.png'
  import imgSalesPitch from '@/assets/simulations/presentacion_ventas.png'
  
  const emit = defineEmits(['back', 'navigate', 'startSimulation'])
  
  // Estado reactivo
  const selectedSimulation = ref(null)
  
  // Datos de simulaciones
  const simulations = ref([
    {
      id: 1,
      title: 'Presentación con Público Masivo',
      description: 'Simulación que permite medir tu experiencia frente a gran cantidad de personas',
      fullDescription: 'Esta simulación te coloca frente a una audiencia de más de 100 personas en un auditorio profesional. Practicarás técnicas de proyección de voz, manejo del espacio escénico y conexión con audiencias grandes.',
      image: imgMassAudience,
      duration: 30,
      level: 'Avanzado',
      difficulty: '8/10',
      participants: 'Público masivo',
      verbalAnalysis: true,
      nonVerbalAnalysis: true,
      tags: ['Público', 'Presentación', 'Avanzado'],
      objectives: [
        'Mejorar la proyección de voz para audiencias grandes',
        'Desarrollar presencia escénica',
        'Practicar el manejo de nervios ante multitudes',
        'Optimizar el lenguaje corporal para espacios amplios'
      ]
    },
    {
      id: 2,
      title: 'Conversación 1 vs 1',
      description: 'Simulación de conversación casual que permite medir tu experiencia en una charla personal o profesional.',
      fullDescription: 'Practica conversaciones íntimas y profesionales en un ambiente controlado. Ideal para mejorar habilidades de comunicación interpersonal, escucha activa y construcción de rapport.',
      image: imgConversation,
      duration: 15,
      level: 'Básico',
      difficulty: '3/10',
      participants: '1 persona',
      verbalAnalysis: true,
      nonVerbalAnalysis: true,
      tags: ['Personal', 'Básico', 'Conversación'],
      objectives: [
        'Mejorar la comunicación interpersonal',
        'Desarrollar habilidades de escucha activa',
        'Practicar el contacto visual directo',
        'Optimizar el tono conversacional'
      ]
    },
    {
      id: 3,
      title: 'Entrevista de Práctica Profesional',
      description: 'Simulación que permite medir tu experiencia previa al mundo laboral mediante preguntas y respuestas.',
      fullDescription: 'Simula una entrevista de trabajo real con preguntas típicas y situaciones desafiantes. Perfecto para prepararte para procesos de selección y mejorar tu comunicación profesional.',
      image: imgInterview,
      duration: 20,
      level: 'Intermedio',
      difficulty: '6/10',
      participants: '1-3 entrevistadores',
      verbalAnalysis: true,
      nonVerbalAnalysis: false,
      tags: ['Profesional', 'Entrevista', 'Intermedio'],
      objectives: [
        'Prepararse para entrevistas laborales',
        'Mejorar respuestas bajo presión',
        'Desarrollar comunicación profesional',
        'Practicar el manejo de preguntas difíciles'
      ]
    },
    {
      id: 4,
      title: 'Reunión de Equipo',
      description: 'Simulación de reunión corporativa con múltiples participantes y toma de decisiones.',
      fullDescription: 'Participa en una reunión de equipo donde deberás presentar ideas, debatir propuestas y llegar a consensos. Ideal para líderes y profesionales que trabajan en equipo.',
      image: imgTeamMeeting,
      duration: 25,
      level: 'Intermedio',
      difficulty: '5/10',
      participants: '5-8 personas',
      verbalAnalysis: true,
      nonVerbalAnalysis: true,
      tags: ['Corporativo', 'Liderazgo', 'Equipo'],
      objectives: [
        'Mejorar la comunicación en grupo',
        'Desarrollar habilidades de liderazgo',
        'Practicar la facilitación de reuniones',
        'Optimizar la toma de decisiones colaborativa'
      ]
    },
    {
      id: 5,
      title: 'Presentación de Ventas',
      description: 'Simulación de pitch de ventas para clientes potenciales con objeciones y negociación.',
      fullDescription: 'Perfecciona tu técnica de ventas presentando productos o servicios a clientes exigentes. Incluye manejo de objeciones y técnicas de persuasión.',
      image: imgSalesPitch,
      duration: 18,
      level: 'Intermedio',
      difficulty: '7/10',
      participants: '2-4 clientes',
      verbalAnalysis: true,
      nonVerbalAnalysis: true,
      tags: ['Ventas', 'Persuasión', 'Negociación'],
      objectives: [
        'Desarrollar técnicas de persuasión',
        'Mejorar el manejo de objeciones',
        'Practicar el cierre de ventas',
        'Optimizar la presentación de beneficios'
      ]
    }
  ])
  
  // Métodos
  const selectSimulation = (simulation) => {
    selectedSimulation.value = simulation
  }
  
  const closeModal = () => {
    selectedSimulation.value = null
  }
  
  const startSimulation = () => {
    emit('startSimulation', selectedSimulation.value)
    closeModal()
  }
  
  const loadMore = () => {
    console.log('Cargar más simulaciones...')
    // Aquí podrías cargar más simulaciones desde una API
  }
  
  const getTagClass = (tag) => {
    const tagTypes = {
      'Público': 'tag-audience',
      'Presentación': 'tag-presentation',
      'Avanzado': 'tag-advanced',
      'Personal': 'tag-personal',
      'Básico': 'tag-basic',
      'Conversación': 'tag-conversation',
      'Profesional': 'tag-professional',
      'Entrevista': 'tag-interview',
      'Intermedio': 'tag-intermediate',
      'Corporativo': 'tag-corporate',
      'Liderazgo': 'tag-leadership',
      'Equipo': 'tag-team',
      'Ventas': 'tag-sales',
      'Persuasión': 'tag-persuasion',
      'Negociación': 'tag-negotiation'
    }
    return tagTypes[tag] || 'tag-default'
  }
  </script>
  
  <style scoped>
  .simulations-container {
    min-height: 100vh;
    background: var(--gradient-background);
    display: flex;
    flex-direction: column;
    padding-bottom: 100px; /* Espacio para navegación global */
  }
  
  .simulations-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-lg) var(--spacing-md);
    background: var(--gradient-primary);
    color: var(--color-white);
    border-bottom: 1px solid var(--color-gray-200);
  }
  
  .back-btn, .filter-btn {
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
  
  .back-btn:hover, .filter-btn:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: scale(1.05);
  }
  
  .simulations-header h1 {
    font-size: var(--font-size-xl);
    font-weight: 600;
    color: var(--color-white);
  }
  
  .simulations-list {
    flex: 1;
    padding: var(--spacing-md);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }
  
  .simulation-card {
    background: var(--color-white);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-card);
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .simulation-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
  }
  
  .simulation-image {
    position: relative;
    /* Mantener una relación de aspecto 16:9 para evitar distorsión o recortes inesperados */
    aspect-ratio: 16 / 9;
    overflow: hidden;
  }
  
  .simulation-image img {
    width: 100%;
    height: 100%;
    /* Cubrir todo el contenedor manteniendo la proporción y centrando la imagen */
    object-fit: cover;
    object-position: center;
  }
  
  .simulation-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(26, 35, 126, 0.8) 0%, rgba(66, 165, 245, 0.6) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .simulation-card:hover .simulation-overlay {
    opacity: 1;
  }
  
  .play-button {
    width: 60px;
    height: 60px;
    background: var(--color-white);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: var(--shadow-lg);
    animation: pulse 2s ease-in-out infinite;
  }
  
  .simulation-content {
    padding: var(--spacing-lg);
  }
  
  .simulation-content h3 {
    font-size: var(--font-size-lg);
    font-weight: 600;
    color: var(--color-primary);
    margin-bottom: var(--spacing-sm);
  }
  
  .simulation-content p {
    color: var(--color-gray-600);
    font-size: var(--font-size-sm);
    line-height: 1.5;
    margin-bottom: var(--spacing-md);
  }
  
  .simulation-meta {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);
  }
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
  }
  
  .meta-icon {
    font-size: 0.9rem;
  }
  
  .meta-text {
    font-size: var(--font-size-xs);
    color: var(--color-gray-600);
    font-weight: 500;
  }
  
  .simulation-tags {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
  }
  
  .tag {
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-xs);
    font-weight: 500;
  }
  
  .tag-audience, .tag-presentation { background: rgba(66, 165, 245, 0.1); color: var(--color-info); }
  .tag-advanced { background: rgba(239, 68, 68, 0.1); color: var(--color-error); }
  .tag-personal, .tag-conversation { background: rgba(16, 185, 129, 0.1); color: var(--color-success); }
  .tag-basic { background: rgba(245, 158, 11, 0.1); color: var(--color-warning); }
  .tag-professional, .tag-interview, .tag-corporate { background: rgba(99, 102, 241, 0.1); color: #6366f1; }
  .tag-intermediate { background: rgba(245, 158, 11, 0.1); color: var(--color-warning); }
  .tag-leadership, .tag-team { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }
  .tag-sales, .tag-persuasion, .tag-negotiation { background: rgba(236, 72, 153, 0.1); color: #ec4899; }
  .tag-default { background: var(--color-gray-100); color: var(--color-gray-600); }
  
  .load-more {
    padding: var(--spacing-lg) var(--spacing-md);
    display: flex;
    justify-content: center;
  }
  
  /* Modal */
  .simulation-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: var(--z-modal);
    padding: var(--spacing-md);
  }
  
  .modal-content {
    background: var(--color-white);
    border-radius: var(--radius-lg);
    max-width: 400px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    animation: modalSlideUp 0.3s ease-out;
  }
  
  @keyframes modalSlideUp {
    from {
      opacity: 0;
      transform: translateY(50px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--color-gray-200);
  }
  
  .modal-header h2 {
    font-size: var(--font-size-xl);
    font-weight: 600;
    color: var(--color-primary);
  }
  
  .close-btn {
    width: 32px;
    height: 32px;
    border: none;
    background: var(--color-gray-100);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .modal-body {
    padding: var(--spacing-lg);
  }
  
  .simulation-preview {
    margin-bottom: var(--spacing-lg);
  }
  
  .simulation-preview img {
    width: 100%;
    height: 120px;
    object-fit: cover;
    border-radius: var(--radius-md);
  }
  
  .simulation-description {
    color: var(--color-gray-600);
    line-height: 1.6;
    margin-bottom: var(--spacing-lg);
  }
  
  .details-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
  }
  
  .detail-item {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }
  
  .detail-label {
    font-size: var(--font-size-xs);
    color: var(--color-gray-500);
    font-weight: 500;
  }
  
  .detail-value {
    font-size: var(--font-size-sm);
    color: var(--color-primary);
    font-weight: 600;
  }
  
  .simulation-objectives h4 {
    color: var(--color-primary);
    font-size: var(--font-size-base);
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
  }
  
  .simulation-objectives ul {
    list-style: none;
    padding: 0;
  }
  
  .simulation-objectives li {
    padding: var(--spacing-xs) 0;
    color: var(--color-gray-600);
    font-size: var(--font-size-sm);
    position: relative;
    padding-left: var(--spacing-lg);
  }
  
  .simulation-objectives li::before {
    content: '✓';
    position: absolute;
    left: 0;
    color: var(--color-success);
    font-weight: bold;
  }
  
  .modal-footer {
    display: flex;
    gap: var(--spacing-md);
    padding: var(--spacing-lg);
    border-top: 1px solid var(--color-gray-200);
  }
  
  .modal-footer .btn {
    flex: 1;
  }
  </style>