<template>
  <transition name="slide-fade">
    <div 
      v-if="store.notification.show" 
      :class="['notification', store.notification.type]"
      @click="store.hideNotification()">
      
      <div class="notification-icon">
        <span v-if="store.notification.type === 'success'">✓</span>
        <span v-if="store.notification.type === 'error'">✕</span>
        <span v-if="store.notification.type === 'warning'">⚠</span>
        <span v-if="store.notification.type === 'info'">ℹ</span>
      </div>
      
      <div class="notification-content">
        <p class="notification-message">{{ store.notification.message }}</p>
        <div class="notification-progress" :class="store.notification.type"></div>
      </div>
      
      <button @click.stop="store.hideNotification()" class="close-btn">
        <span>×</span>
      </button>
      
      <div class="notification-glow"></div>
    </div>
  </transition>
</template>

<script setup>
import { useAnalysisStore } from '@/stores/analysis'
import { onMounted, watch } from 'vue'

const store = useAnalysisStore()

// Agregar auto-hide con animación de progreso
watch(() => store.notification.show, (newValue) => {
  if (newValue) {
    // Reiniciar la animación de progreso
    setTimeout(() => {
      const progressBar = document.querySelector('.notification-progress')
      if (progressBar) {
        progressBar.style.animation = 'none'
        progressBar.offsetHeight // Trigger reflow
        progressBar.style.animation = 'progress 4s linear forwards'
      }
    }, 50)
  }
})
</script>

<style scoped>
.notification {
  position: fixed;
  bottom: 30px;
  right: 20px;
  left: 20px;
  max-width: 390px;
  margin: 0 auto;
  background: var(--white);
  backdrop-filter: blur(16px);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-2xl);
  border: 1px solid;
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  padding: var(--space-5);
  z-index: var(--z-modal);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification:hover {
  transform: translateY(-4px) scale(1.02);
}

.notification.success {
  border-color: rgba(16, 185, 129, 0.3);
  background: linear-gradient(135deg, 
    rgba(16, 185, 129, 0.08) 0%, 
    var(--white) 100%);
}

.notification.error {
  border-color: rgba(239, 68, 68, 0.3);
  background: linear-gradient(135deg, 
    rgba(239, 68, 68, 0.08) 0%, 
    var(--white) 100%);
}

.notification.warning {
  border-color: rgba(245, 158, 11, 0.3);
  background: linear-gradient(135deg, 
    rgba(245, 158, 11, 0.08) 0%, 
    var(--white) 100%);
}

.notification.info {
  border-color: rgba(66, 165, 245, 0.3);
  background: linear-gradient(135deg, 
    rgba(66, 165, 245, 0.08) 0%, 
    var(--white) 100%);
}

.notification-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xl);
  font-weight: 700;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.notification.success .notification-icon {
  background: linear-gradient(135deg, var(--success), #34d399);
  color: var(--white);
}

.notification.error .notification-icon {
  background: linear-gradient(135deg, var(--error), #f87171);
  color: var(--white);
}

.notification.warning .notification-icon {
  background: linear-gradient(135deg, var(--warning), #fbbf24);
  color: var(--white);
}

.notification.info .notification-icon {
  background: var(--gradient-card);
  color: var(--white);
}

.notification-content {
  flex: 1;
  min-height: 44px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}

.notification-message {
  color: var(--gray-900);
  font-size: var(--font-size-base);
  font-weight: 600;
  line-height: 1.4;
  margin: 0;
}

.notification-progress {
  position: absolute;
  bottom: -var(--space-5);
  left: 0;
  height: 3px;
  background: currentColor;
  border-radius: var(--radius-full);
  width: 0%;
  opacity: 0.6;
}

.notification-progress.success {
  color: var(--success);
}

.notification-progress.error {
  color: var(--error);
}

.notification-progress.warning {
  color: var(--warning);
}

.notification-progress.info {
  color: var(--color-accent);
}

.close-btn {
  background: var(--gray-100);
  border: none;
  color: var(--gray-600);
  font-size: var(--font-size-xl);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  flex-shrink: 0;
  line-height: 1;
}

.close-btn:hover {
  background: var(--gray-200);
  transform: scale(1.1);
}

.close-btn:active {
  transform: scale(0.95);
}

.notification-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  border-radius: var(--radius-xl);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.notification:hover .notification-glow {
  opacity: 1;
}

.notification.success:hover .notification-glow {
  box-shadow: 0 0 40px rgba(16, 185, 129, 0.2);
}

.notification.error:hover .notification-glow {
  box-shadow: 0 0 40px rgba(239, 68, 68, 0.2);
}

.notification.warning:hover .notification-glow {
  box-shadow: 0 0 40px rgba(245, 158, 11, 0.2);
}

.notification.info:hover .notification-glow {
  box-shadow: 0 0 40px rgba(66, 165, 245, 0.2);
}

/* Transiciones */
.slide-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from {
  transform: translateY(100%) scale(0.9);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(100%) scale(0.9);
  opacity: 0;
}

/* Animación de progreso */
@keyframes progress {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}

/* Responsive */
@media (max-width: 480px) {
  .notification {
    bottom: 20px;
    right: 16px;
    left: 16px;
    max-width: none;
  }
}

@media (min-width: 768px) {
  .notification {
    max-width: 420px;
    right: 30px;
    left: auto;
  }
}
</style>