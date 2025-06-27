import numpy as np
import cv2

try:
    import mediapipe as mp  # type: ignore

    _mp_face_mesh = mp.solutions.face_mesh
    # Reutilizamos la misma instancia para evitar crearla en cada frame
    _face_mesh = _mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
except (ImportError, AttributeError):
    # Si MediaPipe no está instalado o falla la inicialización, continuamos con None.
    _face_mesh = None

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

def analyze_eye_contact(frame, yaw_threshold: float = 0.08) -> bool | None:
    """Determina si el orador mantiene contacto visual aproximado.

    Parámetros
    ----------
    frame : np.ndarray
        Fotograma BGR.
    yaw_threshold : float
        Umbral (normalizado) de desviación lateral del eje de la nariz respecto
        al centro de los ojos para considerar que mira al frente.

    Returns
    -------
    bool | None
        • True  → Se detecta contacto visual.
        • False → No se detecta contacto visual.
        • None  → No se pudo determinar (MediaPipe no disponible o no se detecta rostro).
    """
    if _face_mesh is None:
        return None

    # Conversión BGR → RGB (MediaPipe trabaja en RGB)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = _face_mesh.process(rgb)

    if not result.multi_face_landmarks:
        return False

    # Tomamos la primera cara encontrada
    face_landmarks = result.multi_face_landmarks[0].landmark

    # Índices de referencia según FaceMesh
    NOSE_TIP = 1
    LEFT_EYE_OUTER = 33
    RIGHT_EYE_OUTER = 263

    nose = face_landmarks[NOSE_TIP]
    left_eye = face_landmarks[LEFT_EYE_OUTER]
    right_eye = face_landmarks[RIGHT_EYE_OUTER]

    # Centro horizontal de los ojos
    eyes_center_x = (left_eye.x + right_eye.x) / 2.0

    # Si la proyección horizontal de la nariz está cerca del centro de los ojos
    # asumimos que la cabeza está orientada al frente.
    if abs(nose.x - eyes_center_x) < yaw_threshold:
        return True
    return False 