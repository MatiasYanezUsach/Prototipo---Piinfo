<template>
    <div class="calendar-container">
      <!-- Header -->
      <header class="calendar-header">
        <button class="back-btn" @click="$emit('back')">
          <span>←</span>
        </button>
        <h1>CALENDARIO</h1>
        <button class="today-btn" @click="goToToday">
          <span>📅</span>
        </button>
      </header>
  
      <!-- Navegación del mes -->
      <div class="month-navigation">
        <button class="nav-btn" @click="previousMonth">
          <span>‹</span>
        </button>
        <div class="month-year">
          <h2>{{ getMonthName(currentDate.getMonth()) }} {{ currentDate.getFullYear() }}</h2>
        </div>
        <button class="nav-btn" @click="nextMonth">
          <span>›</span>
        </button>
      </div>
  
      <!-- Calendario -->
      <div class="calendar-grid">
        <!-- Días de la semana -->
        <div class="calendar-header-row">
          <div v-for="day in weekDays" :key="day" class="day-header">
            {{ day }}
          </div>
        </div>
        
        <!-- Días del mes -->
        <div class="calendar-days">
          <div
            v-for="day in calendarDays"
            :key="`${day.date}-${day.month}`"
            class="calendar-day"
            :class="{
              'other-month': day.otherMonth,
              'today': isToday(day.date),
              'selected': isSelected(day.date),
              'has-events': hasEvents(day.date)
            }"
            @click="selectDay(day)">
            <span class="day-number">{{ day.date }}</span>
            <div v-if="hasEvents(day.date)" class="event-indicator">
              <div class="event-dot"></div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Planes del día seleccionado -->
      <div class="daily-plans">
        <div class="plans-header">
          <h3>Planes del Día</h3>
          <button class="add-btn" @click="showAddPlan = true">
            <span>➕</span>
          </button>
        </div>
        
        <div v-if="selectedDayEvents.length > 0" class="events-list">
          <div
            v-for="event in selectedDayEvents"
            :key="event.id"
            class="event-card"
            :class="getEventTypeClass(event.type)">
            
            <div class="event-content">
              <h4>{{ event.title }}</h4>
              <div class="event-details">
                <div class="event-meta">
                  <span class="event-duration">Duración: {{ event.duration }}</span>
                  <span class="event-difficulty">Dificultad: {{ event.difficulty }}</span>
                </div>
                <div class="event-analysis">
                  <span class="analysis-type" v-if="event.verbal">Verbal: {{ event.verbal }}</span>
                  <span class="analysis-type" v-if="event.nonVerbal">No Verbal: {{ event.nonVerbal }}</span>
                </div>
              </div>
            </div>
            
            <div class="event-actions">
              <button class="event-btn start-btn" @click="startEvent(event)">
                <span>▶️</span>
              </button>
              <button class="event-btn edit-btn" @click="editEvent(event)">
                <span>✏️</span>
              </button>
            </div>
          </div>
        </div>
        
        <div v-else class="no-events">
          <div class="no-events-icon">📅</div>
          <p>No hay planes programados para este día</p>
          <button class="btn btn-primary" @click="showAddPlan = true">
            Agregar Plan
          </button>
        </div>
      </div>
  
      <!-- Historial -->
      <div class="history-section">
        <button class="btn btn-ghost" @click="showHistory = true">
          <span>📊</span>
          Historial
        </button>
      </div>
  
      <!-- Modal para agregar plan -->
      <div v-if="showAddPlan" class="modal-overlay" @click="closeAddPlan">
        <div class="add-plan-modal" @click.stop>
          <div class="modal-header">
            <h3>Agregar Plan</h3>
            <button class="close-btn" @click="closeAddPlan">
              <span>✕</span>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="form-group">
              <label>Título del plan</label>
              <input type="text" v-model="newPlan.title" class="input" placeholder="Ej: Presentación PIINFO">
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Duración</label>
                <select v-model="newPlan.duration" class="input">
                  <option value="30 minutos">30 minutos</option>
                  <option value="45 minutos">45 minutos</option>
                  <option value="60 minutos">60 minutos</option>
                  <option value="90 minutos">90 minutos</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Dificultad</label>
                <select v-model="newPlan.difficulty" class="input">
                  <option value="3/10">3/10 - Básico</option>
                  <option value="5/10">5/10 - Intermedio</option>
                  <option value="8/10">8/10 - Avanzado</option>
                  <option value="10/10">10/10 - Experto</option>
                </select>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Análisis Verbal</label>
                <select v-model="newPlan.verbal" class="input">
                  <option value="Sí">Sí</option>
                  <option value="No">No</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Análisis No Verbal</label>
                <select v-model="newPlan.nonVerbal" class="input">
                  <option value="Sí">Sí</option>
                  <option value="No">No</option>
                  <option value="No disponible">No disponible</option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label>Tipo de simulación</label>
              <select v-model="newPlan.type" class="input">
                <option value="presentation">Presentación</option>
                <option value="meeting">Reunión</option>
                <option value="interview">Entrevista</option>
                <option value="conversation">Conversación</option>
              </select>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="closeAddPlan">
              Cancelar
            </button>
            <button class="btn btn-primary" @click="addPlan">
              <span>➕</span>
              Añadir Plan
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  
  const emit = defineEmits(['back', 'navigate', 'startEvent'])
  
  // Estado reactivo
  const currentDate = ref(new Date())
  const selectedDate = ref(new Date())
  const showAddPlan = ref(false)
  const showHistory = ref(false)
  
  // Datos
  const weekDays = ['D', 'L', 'M', 'W', 'J', 'V', 'S']
  const monthNames = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ]
  
  // Eventos del calendario
  const events = ref([
    {
      id: 1,
      title: 'Presentación PIINFO',
      date: new Date(),
      duration: '30 minutos',
      difficulty: '8/10',
      verbal: 'Sí',
      nonVerbal: 'Sí',
      type: 'presentation'
    },
    {
      id: 2,
      title: 'Reunión Profe Arturo',
      date: new Date(),
      duration: '20 minutos',
      difficulty: '5/10',
      verbal: 'Sí',
      nonVerbal: 'No',
      type: 'meeting'
    },
    {
      id: 3,
      title: 'Práctica de Entrevista',
      date: new Date(Date.now() + 86400000), // Mañana
      duration: '45 minutos',
      difficulty: '6/10',
      verbal: 'Sí',
      nonVerbal: 'Sí',
      type: 'interview'
    }
  ])
  
  // Nuevo plan
  const newPlan = ref({
    title: '',
    duration: '30 minutos',
    difficulty: '5/10',
    verbal: 'Sí',
    nonVerbal: 'Sí',
    type: 'presentation'
  })
  
  // Computed
  const calendarDays = computed(() => {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    
    // Primer día del mes
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    
    // Días a mostrar
    const days = []
    
    // Días del mes anterior
    const startDay = firstDay.getDay()
    for (let i = startDay - 1; i >= 0; i--) {
      const date = new Date(year, month, -i)
      days.push({
        date: date.getDate(),
        month: date.getMonth(),
        otherMonth: true,
        fullDate: date
      })
    }
    
    // Días del mes actual
    for (let i = 1; i <= lastDay.getDate(); i++) {
      const date = new Date(year, month, i)
      days.push({
        date: i,
        month: month,
        otherMonth: false,
        fullDate: date
      })
    }
    
    // Días del siguiente mes
    const totalCells = 42 // 6 semanas
    const remainingCells = totalCells - days.length
    for (let i = 1; i <= remainingCells; i++) {
      const date = new Date(year, month + 1, i)
      days.push({
        date: i,
        month: date.getMonth(),
        otherMonth: true,
        fullDate: date
      })
    }
    
    return days
  })
  
  const selectedDayEvents = computed(() => {
    return events.value.filter(event => 
      isSameDay(event.date, selectedDate.value)
    )
  })
  
  // Métodos
  const getMonthName = (monthIndex) => {
    return monthNames[monthIndex]
  }
  
  const previousMonth = () => {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
  }
  
  const nextMonth = () => {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
  }
  
  const goToToday = () => {
    const today = new Date()
    currentDate.value = new Date(today.getFullYear(), today.getMonth(), 1)
    selectedDate.value = today
  }
  
  const isToday = (date) => {
    const today = new Date()
    return date === today.getDate() && 
           currentDate.value.getMonth() === today.getMonth() &&
           currentDate.value.getFullYear() === today.getFullYear()
  }
  
  const isSelected = (date) => {
    return date === selectedDate.value.getDate() && 
           currentDate.value.getMonth() === selectedDate.value.getMonth() &&
           currentDate.value.getFullYear() === selectedDate.value.getFullYear()
  }
  
  const isSameDay = (date1, date2) => {
    return date1.getDate() === date2.getDate() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getFullYear() === date2.getFullYear()
  }
  
  const hasEvents = (date) => {
    const dayDate = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), date)
    return events.value.some(event => isSameDay(event.date, dayDate))
  }
  
  const selectDay = (day) => {
    selectedDate.value = day.fullDate
  }
  
  const getEventTypeClass = (type) => {
    const classes = {
      'presentation': 'event-presentation',
      'meeting': 'event-meeting',
      'interview': 'event-interview',
      'conversation': 'event-conversation'
    }
    return classes[type] || 'event-default'
  }
  
  const startEvent = (event) => {
    emit('startEvent', event)
  }
  
  const editEvent = (event) => {
    console.log('Editar evento:', event.title)
  }
  
  const closeAddPlan = () => {
    showAddPlan.value = false
    resetNewPlan()
  }
  
  const resetNewPlan = () => {
    newPlan.value = {
      title: '',
      duration: '30 minutos',
      difficulty: '5/10',
      verbal: 'Sí',
      nonVerbal: 'Sí',
      type: 'presentation'
    }
  }
  
  const addPlan = () => {
    if (newPlan.value.title.trim()) {
      events.value.push({
        id: events.value.length + 1,
        title: newPlan.value.title,
        date: new Date(selectedDate.value),
        duration: newPlan.value.duration,
        difficulty: newPlan.value.difficulty,
        verbal: newPlan.value.verbal,
        nonVerbal: newPlan.value.nonVerbal,
        type: newPlan.value.type
      })
      closeAddPlan()
    }
  }
  
  onMounted(() => {
    selectedDate.value = new Date()
  })
  </script>
  
  <style scoped>
  .calendar-container {
    min-height: 100vh;
    background: var(--gradient-background);
    display: flex;
    flex-direction: column;
    padding-bottom: 100px; /* Espacio para navegación global */
  }
  
  .calendar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-lg) var(--spacing-md);
    background: var(--color-white);
    border-bottom: 1px solid var(--color-gray-200);
  }
  
  .back-btn, .today-btn {
    width: 36px;
    height: 36px;
    border: none;
    background: var(--color-gray-100);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .back-btn:hover, .today-btn:hover {
    background: var(--color-gray-200);
    transform: scale(1.05);
  }
  
  .calendar-header h1 {
    font-size: var(--font-size-xl);
    font-weight: 600;
    color: var(--color-primary);
    letter-spacing: 1px;
  }
  
  .month-navigation {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-lg) var(--spacing-md);
    background: var(--color-white);
    border-bottom: 1px solid var(--color-gray-200);
  }
  
  .nav-btn {
    width: 40px;
    height: 40px;
    border: none;
    background: var(--color-primary);
    color: var(--color-white);
    border-radius: var(--radius-md);
    font-size: var(--font-size-lg);
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .nav-btn:hover {
    background: var(--color-primary-light);
    transform: scale(1.05);
  }
  
  .month-year h2 {
    font-size: var(--font-size-xl);
    font-weight: 600;
    color: var(--color-primary);
  }
  
  .calendar-grid {
    background: var(--color-white);
    margin: var(--spacing-md);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-card);
  }
  
  .calendar-header-row {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    background: var(--color-primary);
  }
  
  .day-header {
    padding: var(--spacing-md);
    text-align: center;
    font-weight: 600;
    color: var(--color-white);
    font-size: var(--font-size-sm);
  }
  
  .calendar-days {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
  }
  
  .calendar-day {
    aspect-ratio: 1;
    border: 1px solid var(--color-gray-200);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    color: black;
  }
  
  .calendar-day:hover {
    background: var(--color-gray-50);
  }
  
  .calendar-day.other-month {
    color: var(--color-gray-400);
    background: var(--color-gray-50);
  }
  
  .calendar-day.today {
    background: var(--color-accent);
    color: var(--color-white);
    font-weight: 700;
  }
  
  .calendar-day.selected {
    background: var(--color-primary);
    color: var(--color-white);
    font-weight: 600;
  }
  
  .calendar-day.has-events .day-number {
    font-weight: 600;
    color: var(--color-primary);
  }
  
  .calendar-day.has-events.today .day-number,
  .calendar-day.has-events.selected .day-number {
    color: var(--color-white);
  }
  
  .day-number {
    font-size: var(--font-size-sm);
  }
  
  .event-indicator {
    position: absolute;
    bottom: 4px;
    right: 4px;
  }
  
  .event-dot {
    width: 6px;
    height: 6px;
    background: var(--color-accent);
    border-radius: 50%;
  }
  
  .calendar-day.today .event-dot,
  .calendar-day.selected .event-dot {
    background: var(--color-white);
  }
  
  .daily-plans {
    background: var(--color-white);
    margin: var(--spacing-md);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    box-shadow: var(--shadow-card);
    flex: 1;
  }
  
  .plans-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
  }
  
  .plans-header h3 {
    font-size: var(--font-size-lg);
    font-weight: 600;
    color: var(--color-primary);
  }
  
  .add-btn {
    width: 32px;
    height: 32px;
    border: none;
    background: var(--color-accent);
    color: var(--color-white);
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
  }
  
  .add-btn:hover {
    transform: scale(1.1);
    box-shadow: var(--shadow-md);
  }
  
  .events-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .event-card {
    padding: var(--spacing-lg);
    border-radius: var(--radius-md);
    border-left: 4px solid;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    transition: all 0.3s ease;
  }
  
  .event-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
  
  .event-presentation {
    background: rgba(66, 165, 245, 0.05);
    border-left-color: var(--color-info);
  }
  
  .event-meeting {
    background: rgba(16, 185, 129, 0.05);
    border-left-color: var(--color-success);
  }
  
  .event-interview {
    background: rgba(245, 158, 11, 0.05);
    border-left-color: var(--color-warning);
  }
  
  .event-conversation {
    background: rgba(139, 92, 246, 0.05);
    border-left-color: #8b5cf6;
  }
  
  .event-content {
    flex: 1;
  }
  
  .event-content h4 {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--color-primary);
    margin-bottom: var(--spacing-sm);
  }
  
  .event-details {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }
  
  .event-meta {
    display: flex;
    gap: var(--spacing-md);
  }
  
  .event-duration, .event-difficulty {
    font-size: var(--font-size-xs);
    color: var(--color-gray-600);
  }
  
  .event-analysis {
    display: flex;
    gap: var(--spacing-sm);
  }
  
  .analysis-type {
    font-size: var(--font-size-xs);
    color: var(--color-primary);
    font-weight: 500;
  }
  
  .event-actions {
    display: flex;
    gap: var(--spacing-sm);
    flex-shrink: 0;
  }
  
  .event-btn {
    width: 36px;
    height: 36px;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
  }
  
  .start-btn {
    background: var(--color-success);
    color: var(--color-white);
  }
  
  .edit-btn {
    background: var(--color-gray-200);
    color: var(--color-gray-600);
  }
  
  .event-btn:hover {
    transform: scale(1.1);
  }
  
  .no-events {
    text-align: center;
    padding: var(--spacing-2xl);
    color: var(--color-gray-500);
  }
  
  .no-events-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-lg);
    opacity: 0.5;
  }
  
  .no-events p {
    margin-bottom: var(--spacing-lg);
    font-size: var(--font-size-base);
  }
  
  .history-section {
    padding: var(--spacing-lg) var(--spacing-md);
    display: flex;
    justify-content: center;
  }
  
  /* Modal */
  .modal-overlay {
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
  
  .add-plan-modal {
    background: var(--color-white);
    border-radius: var(--radius-lg);
    max-width: 400px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    animation: modalSlideUp 0.3s ease-out;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--color-gray-200);
  }
  
  .modal-header h3 {
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
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .form-group label {
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--color-gray-700);
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-md);
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
  </style>