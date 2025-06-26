import numpy as np

def analyze_posture(bbox):
    """Analizar postura basada en bounding box"""
    if bbox is None:
        return 5
        
    x1, y1, x2, y2 = bbox[:4]
    altura = y2 - y1
    ancho = x2 - x1
    ratio = altura / max(ancho, 1)
    
    # Evaluar postura (1-10)
    if 1.8 < ratio < 2.5:  # Proporción ideal de pie
        return 9
    elif 1.5 < ratio < 3:
        return 7
    else:
        return 5
        
def analyze_expression(frame, bbox):
    """Análisis simplificado de expresión facial"""
    # Aquí se podría integrar un modelo de detección de emociones
    # Por ahora, retornamos valores simulados
    return np.random.choice(['neutral', 'sonrisa', 'seria'], p=[0.6, 0.3, 0.1])
    
def analyze_space_usage(cx, width):
    """Analizar uso del espacio"""
    tercio = width / 3
    if cx < tercio:
        return 'izquierda'
    elif cx < 2 * tercio:
        return 'centro'
    else:
        return 'derecha'
        
def calculate_fluency(metricas):
    """Calcular fluidez verbal (simulado)"""
    # En una implementación real, aquí se analizaría el audio
    base_fluency = 6
    if isinstance(metricas.get('pausas_detectadas', 0), int):
        base_fluency -= metricas['pausas_detectadas'] * 0.5
    return max(1, min(10, base_fluency + np.random.uniform(-1, 1)))

def reset_metrics():
    """Reiniciar todas las métricas"""
    return {
        'frames_totales': 0,
        'frames_contacto': 0,
        'gestos_totales': 0,
        'distancias_mov': [],
        'volumen_voz': [],
        'pausas_detectadas': 0,
        'palabras_por_minuto': 0,
        'postura_evaluacion': [],
        'expresiones_faciales': {'neutral': 0, 'sonrisa': 0, 'seria': 0},
        'tiempo_hablando': 0,
        'tiempo_silencio': 0,
        'cambios_postura': 0,
        'uso_espacio': {'izquierda': 0, 'centro': 0, 'derecha': 0},
        'contacto_por_tiempo': [],
        'gestos_por_tiempo': [],
        'mov_por_tiempo': [],
        'postura_por_tiempo': [],
        'fluidez_por_tiempo': []
    } 