import cv2
from ultralytics import YOLO
import time
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from datetime import datetime
import matplotlib.pyplot as plt
import io
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from collections import deque
import json
from PIL import Image as PILImage, ImageTk

class ThreadedCamera:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        # Minimizar buffer y latencia
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv2.CAP_PROP_FPS, 15)

        self.stopped = False
        self.frame = None

    def start(self):
        threading.Thread(target=self._update, daemon=True).start()
        return self

    def _update(self):
        while not self.stopped:
            ret, fr = self.cap.read()
            if ret:
                self.frame = fr
        self.cap.release()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

class OratoriaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ORATOR.IA - Análisis Profesional de Presentaciones")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Variables de control
        self.analizando = False
        self.previewing = False
        self.cam = None
        self.modelo = None
        self.metricas = {
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
            'uso_espacio': {'izquierda': 0, 'centro': 0, 'derecha': 0}
        }
        
        # Configuración personalizable
        self.config = {
            'duracion': 30,
            'zona_contacto_min': 0.3,
            'zona_contacto_max': 0.7,
            'sensibilidad_movimiento': 10,
            'fps_objetivo': 20,
            'guardar_video': True,
            'analisis_avanzado': True
        }
        
        self.setup_ui()
        self.load_model()
        
    def setup_ui(self):
        # Frame principal con estilo moderno
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar estilos
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header con logo y título
        header_frame = tk.Frame(main_frame, bg='#2c2c2c', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🎤 ORATOR.IA", 
                              font=('Arial', 24, 'bold'), 
                              fg='#4CAF50', bg='#2c2c2c')
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(header_frame, 
                                 text="Sistema Avanzado de Análisis de Presentaciones", 
                                 font=('Arial', 12), 
                                 fg='#888', bg='#2c2c2c')
        subtitle_label.pack()
        
        # Frame de configuración
        config_frame = tk.LabelFrame(main_frame, text="⚙️ Configuración", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#2c2c2c', fg='white',
                                    relief=tk.FLAT, borderwidth=2)
        config_frame.pack(fill=tk.X, pady=10)
        
        # Configuración en columnas
        config_left = tk.Frame(config_frame, bg='#2c2c2c')
        config_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        config_right = tk.Frame(config_frame, bg='#2c2c2c')
        config_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Nombre del usuario
        tk.Label(config_left, text="👤 Nombre:", bg='#2c2c2c', fg='white',
                font=('Arial', 10)).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.nombre_entry = tk.Entry(config_left, font=('Arial', 10), width=20,
                                    bg='#3c3c3c', fg='white', insertbackground='white')
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        self.nombre_entry.insert(0, "Usuario")
        
        # Tipo de cámara
        tk.Label(config_left, text="📹 Cámara:", bg='#2c2c2c', fg='white',
                font=('Arial', 10)).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.camera_type = tk.StringVar(value="local")
        camera_frame = tk.Frame(config_left, bg='#2c2c2c')
        camera_frame.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Radiobutton(camera_frame, text="Local", variable=self.camera_type, 
                      value="local", bg='#2c2c2c', fg='white', 
                      selectcolor='#2c2c2c').pack(side=tk.LEFT)
        tk.Radiobutton(camera_frame, text="IP", variable=self.camera_type, 
                      value="ip", bg='#2c2c2c', fg='white',
                      selectcolor='#2c2c2c').pack(side=tk.LEFT)
        
        # IP de la cámara
        tk.Label(config_left, text="🌐 IP Cámara:", bg='#2c2c2c', fg='white',
                font=('Arial', 10)).grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.ip_entry = tk.Entry(config_left, font=('Arial', 10), width=20,
                                bg='#3c3c3c', fg='white', insertbackground='white')
        self.ip_entry.grid(row=2, column=1, padx=5, pady=5)
        self.ip_entry.insert(0, "192.168.1.100:8080")
        
        # Duración del análisis
        tk.Label(config_right, text="⏱️ Duración (seg):", bg='#2c2c2c', fg='white',
                font=('Arial', 10)).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.duracion_var = tk.IntVar(value=30)
        self.duracion_spin = tk.Spinbox(config_right, from_=10, to=300, 
                                       textvariable=self.duracion_var,
                                       font=('Arial', 10), width=10,
                                       bg='#3c3c3c', fg='white')
        self.duracion_spin.grid(row=0, column=1, padx=5, pady=5)
        
        # Opciones avanzadas
        self.guardar_video_var = tk.BooleanVar(value=True)
        tk.Checkbutton(config_right, text="💾 Guardar video", 
                      variable=self.guardar_video_var,
                      bg='#2c2c2c', fg='white', selectcolor='#2c2c2c',
                      font=('Arial', 10)).grid(row=1, column=0, columnspan=2, 
                                               sticky='w', padx=5, pady=5)
        
        self.analisis_avanzado_var = tk.BooleanVar(value=True)
        tk.Checkbutton(config_right, text="🔬 Análisis avanzado", 
                      variable=self.analisis_avanzado_var,
                      bg='#2c2c2c', fg='white', selectcolor='#2c2c2c',
                      font=('Arial', 10)).grid(row=2, column=0, columnspan=2, 
                                               sticky='w', padx=5, pady=5)
        
        # Frame de vista previa y métricas
        display_frame = tk.Frame(main_frame, bg='#2c2c2c')
        display_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Vista previa de video
        preview_frame = tk.LabelFrame(display_frame, text="📷 Vista Previa", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#2c2c2c', fg='white',
                                     relief=tk.FLAT, borderwidth=2)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.video_label = tk.Label(preview_frame, bg='black', text="Vista previa aquí",
                                   fg='white', font=('Arial', 14))
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel de métricas en vivo
        metrics_frame = tk.LabelFrame(display_frame, text="📊 Métricas en Tiempo Real", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#2c2c2c', fg='white',
                                     relief=tk.FLAT, borderwidth=2,
                                     width=400)
        metrics_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        metrics_frame.pack_propagate(False)
        
        # Métricas individuales con barras de progreso
        self.metric_widgets = {}
        metrics_list = [
            ("👁️ Contacto Visual", "contacto", "%"),
            ("🙌 Gestos/segundo", "gestos", ""),
            ("🚶 Movimiento", "movimiento", "px"),
            ("🎯 Postura", "postura", "/10"),
            ("😊 Expresividad", "expresividad", "/10"),
            ("🗣️ Fluidez Verbal", "fluidez", "/10")
        ]
        
        for i, (label, key, unit) in enumerate(metrics_list):
            frame = tk.Frame(metrics_frame, bg='#2c2c2c')
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(frame, text=label, bg='#2c2c2c', fg='white',
                    font=('Arial', 10)).pack(anchor='w')
            
            # Barra de progreso
            progress = ttk.Progressbar(frame, length=300, mode='determinate',
                                      style='Green.Horizontal.TProgressbar')
            progress.pack(fill=tk.X, pady=2)
            
            # Valor
            value_label = tk.Label(frame, text=f"0{unit}", bg='#2c2c2c', 
                                  fg='#4CAF50', font=('Arial', 10, 'bold'))
            value_label.pack(anchor='e')
            
            self.metric_widgets[key] = {
                'progress': progress,
                'label': value_label,
                'unit': unit
            }
        
        # Frame de control
        control_frame = tk.Frame(main_frame, bg='#2c2c2c')
        control_frame.pack(fill=tk.X, pady=10)
        
        # Botones de control con estilo moderno
        self.start_button = tk.Button(control_frame, text="▶️ INICIAR ANÁLISIS",
                                     command=self.start_analysis,
                                     bg='#4CAF50', fg='white',
                                     font=('Arial', 12, 'bold'),
                                     relief=tk.FLAT, padx=20, pady=10,
                                     cursor='hand2')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="⏹️ DETENER",
                                    command=self.stop_analysis,
                                    bg='#f44336', fg='white',
                                    font=('Arial', 12, 'bold'),
                                    relief=tk.FLAT, padx=20, pady=10,
                                    state=tk.DISABLED,
                                    cursor='hand2')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.preview_button = tk.Button(control_frame, text="👁️ VISTA PREVIA",
                                       command=self.toggle_preview,
                                       bg='#2196F3', fg='white',
                                       font=('Arial', 12, 'bold'),
                                       relief=tk.FLAT, padx=20, pady=10,
                                       cursor='hand2')
        self.preview_button.pack(side=tk.LEFT, padx=5)
        
        # Barra de progreso general
        self.progress_frame = tk.Frame(main_frame, bg='#2c2c2c')
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(self.progress_frame, text="Progreso del análisis:", 
                bg='#2c2c2c', fg='white',
                font=('Arial', 10)).pack(anchor='w', padx=10)
        
        self.main_progress = ttk.Progressbar(self.progress_frame, length=600, 
                                           mode='determinate',
                                           style='Green.Horizontal.TProgressbar')
        self.main_progress.pack(fill=tk.X, padx=10, pady=5)
        
        self.time_label = tk.Label(self.progress_frame, text="0 / 0 segundos", 
                                  bg='#2c2c2c', fg='white',
                                  font=('Arial', 10))
        self.time_label.pack(anchor='e', padx=10)
        
        # Configurar estilos de progressbar
        style.configure("Green.Horizontal.TProgressbar",
                       background='#4CAF50',
                       troughcolor='#3c3c3c',
                       bordercolor='#2c2c2c',
                       lightcolor='#4CAF50',
                       darkcolor='#4CAF50')
        
    def load_model(self):
        """Cargar el modelo YOLO"""
        try:
            self.modelo = YOLO("yolov8n.pt")
            print("✅ Modelo YOLO cargado correctamente")
        except Exception as e:
            print(f"❌ Error al cargar el modelo: {str(e)}")
            self.modelo = None
            
    def toggle_preview(self):
        """Activar/desactivar vista previa"""
        if not self.previewing:
            self.previewing = True
            self.preview_thread = threading.Thread(target=self.show_preview)
            self.preview_thread.daemon = True
            self.preview_thread.start()
            self.preview_button.config(text="⏹️ DETENER VISTA", bg='#f44336')
        else:
            self.previewing = False
            self.preview_button.config(text="👁️ VISTA PREVIA", bg='#2196F3')
            
    def show_preview(self):
        """Mostrar vista previa de la cámara"""
        try:
            src = 0 if self.camera_type.get()=="local" else f"http://{self.ip_entry.get()}/video"
            cam = ThreadedCamera(src).start()
            if cam is None:
                return
                
            while self.previewing:
                frame = cam.read()
                if frame is None:
                    continue
                frame = cv2.resize(frame, (640, 480))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = PILImage.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Actualizar en el hilo principal
                self.root.after(0, self.actualizar_video, imgtk)
                    
                time.sleep(0.03)
                
            cam.stop()
        except Exception as e:
            print(f"Error en vista previa: {e}")
            self.previewing = False
        
    def get_camera(self):
        """Obtener objeto de cámara según configuración"""
        try:
            if self.camera_type.get() == "local":
                cam = cv2.VideoCapture(0)
            else:
                ip = self.ip_entry.get()
                cam = cv2.VideoCapture(f"http://{ip}/video")
                
            if not cam.isOpened():
                messagebox.showerror("❌ Error", "No se pudo conectar a la cámara")
                return None
                
            return cam
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al acceder a la cámara: {str(e)}")
            return None
            
    def update_metric_display(self, key, value, max_value=100):
        """Actualizar visualización de métrica"""
        if key in self.metric_widgets:
            widget = self.metric_widgets[key]
            widget['progress']['value'] = (value / max_value) * 100
            widget['label']['text'] = f"{value:.1f}{widget['unit']}"
            
    def start_analysis(self):
        """Iniciar análisis de presentación"""
        if not self.nombre_entry.get():
            messagebox.showwarning("⚠️ Advertencia", "Por favor ingresa tu nombre")
            return
            
        if self.modelo is None:
            messagebox.showerror("❌ Error", "El modelo YOLO no está cargado. Por favor reinicia la aplicación.")
            return
            
        # Detener vista previa si está activa
        if self.previewing:
            self.previewing = False
            time.sleep(0.1)  # Dar tiempo para que se cierre
            
        self.analizando = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.config['duracion'] = self.duracion_var.get()
        
        # Reiniciar métricas
        self.reset_metrics()
        
        # Mostrar mensaje de inicio
        print(f"🎬 Iniciando análisis para {self.nombre_entry.get()}")
        print(f"⏱️ Duración: {self.config['duracion']} segundos")
        print(f"📹 Tipo de cámara: {self.camera_type.get()}")
        if self.camera_type.get() == "ip":
            print(f"🌐 IP: {self.ip_entry.get()}")
        
        # Iniciar análisis en thread separado
        self.analysis_thread = threading.Thread(target=self.run_analysis)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
    def stop_analysis(self):
        """Detener análisis"""
        self.analizando = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Detener vista previa si está activa
        if self.previewing:
            self.previewing = False
            self.preview_button.config(text="👁️ VISTA PREVIA", bg='#2196F3')
        
    def reset_metrics(self):
        """Reiniciar todas las métricas"""
        self.metricas = {
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
        
    def analyze_posture(self, bbox):
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
            
    def analyze_expression(self, frame, bbox):
        """Análisis simplificado de expresión facial"""
        # Aquí se podría integrar un modelo de detección de emociones
        # Por ahora, retornamos valores simulados
        return np.random.choice(['neutral', 'sonrisa', 'seria'], p=[0.6, 0.3, 0.1])
        
    def analyze_space_usage(self, cx, width):
        """Analizar uso del espacio"""
        tercio = width / 3
        if cx < tercio:
            return 'izquierda'
        elif cx < 2 * tercio:
            return 'centro'
        else:
            return 'derecha'
            
    def calculate_fluency(self):
        """Calcular fluidez verbal (simulado)"""
        # En una implementación real, aquí se analizaría el audio
        base_fluency = 6
        if isinstance(self.metricas.get('pausas_detectadas', 0), int):
            base_fluency -= self.metricas['pausas_detectadas'] * 0.5
        return max(1, min(10, base_fluency + np.random.uniform(-1, 1)))
        
    def actualizar_progreso(self, tiempo_actual, duracion):
        """Actualizar barra de progreso en el hilo principal"""
        try:
            progress = (tiempo_actual / duracion) * 100
            self.main_progress['value'] = progress
            self.time_label['text'] = f"{int(tiempo_actual)} / {duracion} segundos"
        except Exception as e:
            print(f"Error actualizando progreso: {e}")
            
    def actualizar_video(self, imgtk):
        """Actualizar video en el hilo principal"""
        try:
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        except Exception as e:
            print(f"Error actualizando video: {e}")
            
    def actualizar_metricas_gui(self, metricas):
        """Actualizar todas las métricas en la GUI desde el hilo principal"""
        try:
            self.update_metric_display('contacto', metricas.get('contacto', 0))
            self.update_metric_display('gestos', metricas.get('gestos', 0), 3)
            self.update_metric_display('movimiento', metricas.get('movimiento', 0), 50)
            self.update_metric_display('postura', metricas.get('postura', 5), 10)
            self.update_metric_display('expresividad', metricas.get('expresividad', 5), 10)
            self.update_metric_display('fluidez', metricas.get('fluidez', 5), 10)
        except Exception as e:
            print(f"Error actualizando métricas: {e}")
        
    def run_analysis(self):
        """Ejecutar el análisis principal"""
        try:
            src = 0 if self.camera_type.get()=="local" else f"http://{self.ip_entry.get()}/video"
            cam = ThreadedCamera(src).start()
            if cam is None:
                self.stop_analysis()
                return
                
            # Configuración de video
            ancho, alto = 640, 480
            cam.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
            cam.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)
            
            # Preparar grabación si está habilitada
            salida = None
            if self.guardar_video_var.get():
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"presentacion_{self.nombre_entry.get()}_{timestamp}.avi"
                salida = cv2.VideoWriter(filename, fourcc, 20, (ancho, alto))
                
            # Variables de análisis
            inicio = time.time()
            duracion = self.config['duracion']
            prev_centro_persona = None
            
            # Inicializar listas de métricas temporales
            self.metricas['contacto_por_tiempo'] = []
            self.metricas['gestos_por_tiempo'] = []
            self.metricas['mov_por_tiempo'] = []
            self.metricas['postura_por_tiempo'] = []
            self.metricas['fluidez_por_tiempo'] = []
            
            # Zonas de contacto visual
            zona_contacto_x_min = ancho * self.config['zona_contacto_min']
            zona_contacto_x_max = ancho * self.config['zona_contacto_max']
            
            print(f"🎬 Iniciando análisis de {duracion} segundos...")
            
            while self.analizando and (time.time() - inicio) < duracion:
                frame = cam.read()
                if frame is None:
                    continue
                    
                self.metricas['frames_totales'] += 1
                tiempo_actual = time.time() - inicio
                
                # Actualizar barra de progreso principal en el hilo principal
                self.root.after(0, self.actualizar_progreso, tiempo_actual, duracion)
                
                # Detección con YOLO
                try:
                    resultados = self.modelo.predict(source=frame, conf=0.4, verbose=False)
                    frame_anotado = frame.copy()
                    
                    if len(resultados) > 0 and resultados[0].boxes is not None:
                        objetos = resultados[0].boxes.cls.tolist()
                        nombres = [resultados[0].names[int(cls)] for cls in objetos]
                        cajas = resultados[0].boxes.xyxy.cpu().numpy()
                        
                        # Dibujar las detecciones
                        frame_anotado = resultados[0].plot()
                        
                        # Análisis de métricas
                        contacto = False
                        gestos = 0
                        bbox_persona = None
                        area_mayor = 0
                        
                        for i, nombre in enumerate(nombres):
                            x1, y1, x2, y2 = cajas[i]
                            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                            area = (x2 - x1) * (y2 - y1)
                            
                            if nombre == "person":
                                if area > area_mayor:
                                    bbox_persona = (x1, y1, x2, y2, cx, cy)
                                    area_mayor = area
                                    
                                # Verificar contacto visual
                                if zona_contacto_x_min < cx < zona_contacto_x_max:
                                    contacto = True
                                    self.metricas['frames_contacto'] += 1
                                    
                                # Análisis de movimiento
                                if prev_centro_persona:
                                    dx = abs(cx - prev_centro_persona[0])
                                    dy = abs(cy - prev_centro_persona[1])
                                    dist = (dx**2 + dy**2)**0.5
                                    self.metricas['distancias_mov'].append(dist)
                                    
                                prev_centro_persona = (cx, cy)
                                
                                # Uso del espacio
                                zona = self.analyze_space_usage(cx, ancho)
                                self.metricas['uso_espacio'][zona] += 1
                                
                            elif nombre in ["hand", "face"]:
                                gestos += 1
                                
                        self.metricas['gestos_totales'] += gestos
                        
                        # Análisis avanzado si está habilitado
                        if self.analisis_avanzado_var.get() and bbox_persona:
                            # Postura
                            postura = self.analyze_posture(bbox_persona)
                            self.metricas['postura_evaluacion'].append(postura)
                            
                            # Expresión facial (simulado)
                            expresion = self.analyze_expression(frame, bbox_persona)
                            self.metricas['expresiones_faciales'][expresion] += 1
                            
                        # Calcular métricas actuales
                        contacto_pct = (self.metricas['frames_contacto'] / 
                                       max(1, self.metricas['frames_totales'])) * 100
                        gestos_seg = self.metricas['gestos_totales'] / max(1, tiempo_actual)
                        mov_prom = (sum(self.metricas['distancias_mov']) / 
                                   max(1, len(self.metricas['distancias_mov']))) if self.metricas['distancias_mov'] else 0
                        
                        # Actualizar métricas en la GUI (en el hilo principal)
                        self.root.after(0, self.actualizar_metricas_gui, {
                            'contacto': contacto_pct,
                            'gestos': gestos_seg,
                            'movimiento': mov_prom,
                            'postura': sum(self.metricas['postura_evaluacion']) / len(self.metricas['postura_evaluacion']) if self.metricas['postura_evaluacion'] else 5,
                            'expresividad': min(10, gestos_seg * 3 + 3),
                            'fluidez': self.calculate_fluency()
                        })
                        
                        # Guardar métricas temporales
                        if int(tiempo_actual) > len(self.metricas['contacto_por_tiempo']):
                            self.metricas['contacto_por_tiempo'].append(contacto_pct)
                            self.metricas['gestos_por_tiempo'].append(gestos_seg)
                            self.metricas['mov_por_tiempo'].append(mov_prom)
                            self.metricas['postura_por_tiempo'].append(
                                sum(self.metricas['postura_evaluacion']) / len(self.metricas['postura_evaluacion']) 
                                if self.metricas['postura_evaluacion'] else 5
                            )
                            self.metricas['fluidez_por_tiempo'].append(self.calculate_fluency())
                    
                    # Dibujar zona de contacto visual
                    cv2.rectangle(frame_anotado, 
                                 (int(zona_contacto_x_min), 0), 
                                 (int(zona_contacto_x_max), alto), 
                                 (0, 255, 0), 2)
                    cv2.putText(frame_anotado, "Zona de Contacto Visual", 
                               (int(zona_contacto_x_min), 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                 
                    # Mostrar en GUI (en el hilo principal)
                    frame_rgb = cv2.cvtColor(frame_anotado, cv2.COLOR_BGR2RGB)
                    img = PILImage.fromarray(frame_rgb)
                    img = img.resize((640, 480), PILImage.Resampling.LANCZOS)
                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    # Actualizar imagen en el hilo principal
                    self.root.after(0, self.actualizar_video, imgtk)
                    
                    # Guardar video si está habilitado
                    if salida:
                        salida.write(frame_anotado)
                        
                    # Guardar último frame
                    if tiempo_actual > duracion - 2:
                        cv2.imwrite(f"captura_final_{self.nombre_entry.get()}.jpg", frame_anotado)
                        
                except Exception as e:
                    print(f"❌ Error en análisis de frame: {str(e)}")
                    
                # Pequeña pausa para no saturar
                time.sleep(0.03)
                    
            # Finalizar
            print("📊 Finalizando análisis...")
            cam.stop()
            if salida:
                salida.release()
                
            # Generar reporte si se completó el análisis
            if self.analizando and tiempo_actual >= duracion * 0.8:
                print("📄 Generando reporte...")
                self.root.after(100, self.generate_report)
                
        except Exception as e:
            print(f"❌ Error en run_analysis: {str(e)}")
            messagebox.showerror("Error", f"Error durante el análisis: {str(e)}")
        finally:
            self.root.after(0, self.stop_analysis)
        
    def generate_report(self):
        """Generar reporte PDF mejorado"""
        try:
            # Verificar que haya datos suficientes
            if self.metricas['frames_totales'] == 0:
                messagebox.showwarning("⚠️ Advertencia", 
                                     "No hay datos suficientes para generar el reporte")
                return
                
            # Preparar datos para el reporte
            contacto_pct = (self.metricas['frames_contacto'] / 
                           max(1, self.metricas['frames_totales'])) * 100
            gestos_seg = self.metricas['gestos_totales'] / max(1, self.config['duracion'])
            mov_prom = (sum(self.metricas['distancias_mov']) / 
                       max(1, len(self.metricas['distancias_mov']))) if self.metricas['distancias_mov'] else 0
            
            print(f"📊 Generando reporte con métricas:")
            print(f"   - Contacto visual: {contacto_pct:.1f}%")
            print(f"   - Gestos/seg: {gestos_seg:.2f}")
            print(f"   - Movimiento promedio: {mov_prom:.1f}")
            
            # Generar reporte
            pdf_file = generar_reporte_avanzado(
                nombre_usuario=self.nombre_entry.get(),
                duracion=self.config['duracion'],
                metricas=self.metricas,
                config=self.config
            )
            
            messagebox.showinfo("✅ Éxito", 
                               f"Reporte generado exitosamente:\n{pdf_file}")
                               
        except Exception as e:
            print(f"❌ Error al generar el reporte: {str(e)}")
            messagebox.showerror("❌ Error", 
                                f"Error al generar el reporte: {str(e)}")

def generar_reporte_avanzado(nombre_usuario, duracion, metricas, config):
    """Generar reporte PDF avanzado con todas las métricas"""
    
    # Crear carpeta de reportes
    if not os.path.exists("reportes"):
        os.makedirs("reportes")
        
    # Nombre del archivo
    ahora = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"reportes/reporte_avanzado_{nombre_usuario}_{ahora}.pdf"
    
    # Crear documento
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    elementos = []
    
    # Estilos
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'CustomTitle',
        parent=estilos['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c2c2c'),
        spaceAfter=30,
        alignment=1
    )
    
    estilo_subtitulo = ParagraphStyle(
        'CustomSubtitle',
        parent=estilos['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#4CAF50'),
        spaceBefore=20,
        spaceAfter=10
    )
    
    # Portada
    elementos.append(Paragraph("ORATOR.IA", estilo_titulo))
    elementos.append(Paragraph("Reporte de Análisis de Presentación", estilos['Heading2']))
    elementos.append(Spacer(1, 0.5*inch))
    
    # Información básica
    info_data = [
        ["Presentador:", nombre_usuario],
        ["Fecha:", datetime.now().strftime('%d/%m/%Y %H:%M')],
        ["Duración:", f"{duracion} segundos"],
        ["Tipo de análisis:", "Avanzado" if config.get('analisis_avanzado', True) else "Básico"]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(info_table)
    elementos.append(Spacer(1, 0.5*inch))
    
    # Calcular métricas finales (con manejo de errores)
    frames_totales = max(1, metricas.get('frames_totales', 1))
    contacto_pct = (metricas.get('frames_contacto', 0) / frames_totales) * 100
    gestos_seg = metricas.get('gestos_totales', 0) / max(1, duracion)
    
    distancias = metricas.get('distancias_mov', [])
    mov_prom = sum(distancias) / max(1, len(distancias)) if distancias else 0
    
    posturas = metricas.get('postura_evaluacion', [])
    postura_prom = sum(posturas) / max(1, len(posturas)) if posturas else 5
    
    # Resumen ejecutivo
    elementos.append(Paragraph("Resumen Ejecutivo", estilo_subtitulo))
    
    # Puntuación general (sobre 100)
    puntuacion_general = calcular_puntuacion_general(metricas, contacto_pct, gestos_seg, mov_prom, postura_prom)
    
    resumen_data = [
        ["Puntuación General", f"{puntuacion_general}/100", get_evaluacion_color(puntuacion_general)],
        ["Contacto Visual", f"{contacto_pct:.1f}%", get_evaluacion_color(contacto_pct)],
        ["Gesticulación", f"{gestos_seg:.2f}/seg", "Óptimo" if 0.5 < gestos_seg < 2 else "Ajustar"],
        ["Dinamismo", f"{mov_prom:.1f} px", "Bueno" if 5 < mov_prom < 30 else "Mejorar"],
        ["Postura", f"{postura_prom:.1f}/10", get_evaluacion_color(postura_prom * 10)]
    ]
    
    resumen_table = Table(resumen_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elementos.append(resumen_table)
    elementos.append(PageBreak())
    
    # Análisis detallado con gráficos
    elementos.append(Paragraph("Análisis Detallado", estilo_titulo))
    
    # Crear y añadir gráficos mejorados
    try:
        graficos = crear_graficos_avanzados(metricas, contacto_pct, gestos_seg, mov_prom)
        
        for titulo, grafico_data in graficos:
            elementos.append(Paragraph(titulo, estilo_subtitulo))
            img = Image(grafico_data, width=5*inch, height=3*inch)
            elementos.append(img)
            elementos.append(Spacer(1, 0.3*inch))
    except Exception as e:
        print(f"Error creando gráficos: {e}")
        elementos.append(Paragraph("No se pudieron generar los gráficos de análisis", estilos['Normal']))
        
    # Análisis de uso del espacio
    elementos.append(Paragraph("Uso del Espacio Escénico", estilo_subtitulo))
    
    uso_espacio = metricas.get('uso_espacio', {'izquierda': 0, 'centro': 0, 'derecha': 0})
    total_espacio = sum(uso_espacio.values())
    
    if total_espacio > 0:
        espacio_data = [
            ["Zona", "Tiempo", "Porcentaje"],
            ["Izquierda", uso_espacio['izquierda'], 
             f"{(uso_espacio['izquierda']/total_espacio)*100:.1f}%"],
            ["Centro", uso_espacio['centro'],
             f"{(uso_espacio['centro']/total_espacio)*100:.1f}%"],
            ["Derecha", uso_espacio['derecha'],
             f"{(uso_espacio['derecha']/total_espacio)*100:.1f}%"]
        ]
    else:
        espacio_data = [
            ["Zona", "Tiempo", "Porcentaje"],
            ["Izquierda", "0", "0%"],
            ["Centro", "0", "0%"],
            ["Derecha", "0", "0%"]
        ]
    
    espacio_table = Table(espacio_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
    espacio_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elementos.append(espacio_table)
    elementos.append(PageBreak())
    
    # Recomendaciones personalizadas
    elementos.append(Paragraph("Recomendaciones Personalizadas", estilo_titulo))
    
    recomendaciones = generar_recomendaciones_personalizadas(
        contacto_pct, gestos_seg, mov_prom, postura_prom, metricas
    )
    
    for categoria, recomendacion in recomendaciones:
        elementos.append(Paragraph(f"<b>{categoria}:</b>", estilos['Heading3']))
        elementos.append(Paragraph(recomendacion, estilos['Normal']))
        elementos.append(Spacer(1, 0.2*inch))
        
    # Plan de mejora
    elementos.append(Paragraph("Plan de Mejora Sugerido", estilo_subtitulo))
    plan = generar_plan_mejora(puntuacion_general, metricas)
    
    for semana, actividades in plan.items():
        elementos.append(Paragraph(f"<b>{semana}</b>", estilos['Heading4']))
        for actividad in actividades:
            elementos.append(Paragraph(f"• {actividad}", estilos['Normal']))
        elementos.append(Spacer(1, 0.1*inch))
        
    # Construir PDF
    doc.build(elementos)
    print(f"✅ PDF generado: {pdf_filename}")
    return pdf_filename

def calcular_puntuacion_general(metricas, contacto_pct, gestos_seg, mov_prom, postura_prom):
    """Calcular puntuación general sobre 100"""
    # Ponderaciones
    peso_contacto = 0.3
    peso_gestos = 0.2
    peso_movimiento = 0.15
    peso_postura = 0.2
    peso_espacio = 0.15
    
    # Normalizar valores
    contacto_score = min(100, contacto_pct)
    gestos_score = min(100, (gestos_seg / 1.5) * 100) if 0.5 < gestos_seg < 2 else 50
    mov_score = min(100, (mov_prom / 20) * 100) if 5 < mov_prom < 30 else 50
    postura_score = postura_prom * 10 if postura_prom > 0 else 50
    
    # Uso del espacio
    total_espacio = sum(metricas['uso_espacio'].values())
    if total_espacio > 0:
        centro_pct = metricas['uso_espacio']['centro'] / total_espacio
        espacio_score = 100 if centro_pct > 0.5 else centro_pct * 200
    else:
        espacio_score = 50
        
    # Calcular puntuación final
    puntuacion = (
        contacto_score * peso_contacto +
        gestos_score * peso_gestos +
        mov_score * peso_movimiento +
        postura_score * peso_postura +
        espacio_score * peso_espacio
    )
    
    return int(puntuacion)

def get_evaluacion_color(valor):
    """Obtener evaluación basada en valor"""
    if valor >= 80:
        return "Excelente"
    elif valor >= 60:
        return "Bueno"
    elif valor >= 40:
        return "Regular"
    else:
        return "Mejorar"

def crear_graficos_avanzados(metricas, contacto_pct, gestos_seg, mov_prom):
    """Crear gráficos avanzados para el reporte"""
    graficos = []
    
    # Gráfico 1: Evolución temporal de métricas
    contacto_tiempo = metricas.get('contacto_por_tiempo', [])
    gestos_tiempo = metricas.get('gestos_por_tiempo', [])
    mov_tiempo = metricas.get('mov_por_tiempo', [])
    postura_tiempo = metricas.get('postura_por_tiempo', [])
    
    if any([contacto_tiempo, gestos_tiempo, mov_tiempo, postura_tiempo]):
        plt.figure(figsize=(8, 5))
        
        # Determinar el número máximo de puntos de tiempo
        max_tiempo = max(
            len(contacto_tiempo) if contacto_tiempo else 0,
            len(gestos_tiempo) if gestos_tiempo else 0,
            len(mov_tiempo) if mov_tiempo else 0,
            len(postura_tiempo) if postura_tiempo else 0
        )
        
        if max_tiempo > 0:
            tiempo = range(max_tiempo)
            
            subplot_num = 1
            
            if contacto_tiempo:
                plt.subplot(2, 2, subplot_num)
                plt.plot(range(len(contacto_tiempo)), contacto_tiempo, 'b-', linewidth=2)
                plt.title('Contacto Visual')
                plt.ylabel('%')
                plt.grid(True, alpha=0.3)
                subplot_num += 1
            
            if gestos_tiempo:
                plt.subplot(2, 2, subplot_num)
                plt.plot(range(len(gestos_tiempo)), gestos_tiempo, 'g-', linewidth=2)
                plt.title('Gesticulación')
                plt.ylabel('Gestos/seg')
                plt.grid(True, alpha=0.3)
                subplot_num += 1
            
            if mov_tiempo:
                plt.subplot(2, 2, subplot_num)
                plt.plot(range(len(mov_tiempo)), mov_tiempo, 'r-', linewidth=2)
                plt.title('Movimiento')
                plt.ylabel('Píxeles')
                plt.xlabel('Tiempo (seg)')
                plt.grid(True, alpha=0.3)
                subplot_num += 1
            
            if postura_tiempo and subplot_num <= 4:
                plt.subplot(2, 2, subplot_num)
                plt.plot(range(len(postura_tiempo)), postura_tiempo, 'm-', linewidth=2)
                plt.title('Postura')
                plt.ylabel('Puntuación')
                plt.xlabel('Tiempo (seg)')
                plt.grid(True, alpha=0.3)
                
            plt.tight_layout()
            
            img_data = io.BytesIO()
            plt.savefig(img_data, format='png', dpi=150)
            img_data.seek(0)
            plt.close()
            
            graficos.append(("Evolución Temporal de Métricas", img_data))
        
    # Gráfico 2: Distribución de expresiones faciales
    expresiones = metricas.get('expresiones_faciales', {})
    if expresiones and sum(expresiones.values()) > 0:
        plt.figure(figsize=(6, 4))
        labels = list(expresiones.keys())
        valores = list(expresiones.values())
        
        plt.pie(valores, labels=labels, autopct='%1.1f%%',
                colors=['#ff9999', '#66b3ff', '#99ff99'])
        plt.title('Distribución de Expresiones Faciales')
        
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png', dpi=150)
        img_data.seek(0)
        plt.close()
        
        graficos.append(("Análisis de Expresividad", img_data))
        
    # Gráfico 3: Radar de competencias
    plt.figure(figsize=(6, 6))
    
    categorias = ['Contacto\nVisual', 'Gestos', 'Movimiento', 'Postura', 'Uso del\nEspacio']
    
    # Calcular valores con manejo de errores
    postura_val = 50
    if metricas.get('postura_evaluacion'):
        postura_val = (sum(metricas['postura_evaluacion']) / len(metricas['postura_evaluacion'])) * 10
    
    espacio_val = 50
    uso_espacio = metricas.get('uso_espacio', {'izquierda': 0, 'centro': 0, 'derecha': 0})
    total_espacio = sum(uso_espacio.values())
    if total_espacio > 0 and uso_espacio.get('centro', 0) > total_espacio * 0.5:
        espacio_val = 80
    
    valores = [
        min(100, contacto_pct),
        min(100, (gestos_seg / 1.5) * 100) if 0.5 < gestos_seg < 2 else 50,
        min(100, (mov_prom / 20) * 100) if 5 < mov_prom < 30 else 50,
        postura_val,
        espacio_val
    ]
    
    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False)
    valores_plot = valores + [valores[0]]
    angulos_plot = np.append(angulos, angulos[0])
    
    ax = plt.subplot(111, projection='polar')
    ax.plot(angulos_plot, valores_plot, 'o-', linewidth=2, color='#4CAF50')
    ax.fill(angulos_plot, valores_plot, alpha=0.25, color='#4CAF50')
    ax.set_xticks(angulos)
    ax.set_xticklabels(categorias)
    ax.set_ylim(0, 100)
    ax.set_title('Perfil de Competencias de Presentación', pad=20)
    ax.grid(True)
    
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=150)
    img_data.seek(0)
    plt.close()
    
    graficos.append(("Perfil de Competencias", img_data))
    
    return graficos

def generar_recomendaciones_personalizadas(contacto_pct, gestos_seg, mov_prom, postura_prom, metricas):
    """Generar recomendaciones personalizadas basadas en el análisis"""
    recomendaciones = []
    
    # Contacto visual
    if contacto_pct < 50:
        recomendaciones.append((
            "Contacto Visual",
            "Tu contacto visual fue del {:.1f}%, lo cual está por debajo del ideal (70-80%). "
            "Practica mirando directamente a la cámara o audiencia. Intenta mantener contacto "
            "visual durante al menos 3-5 segundos antes de desviar la mirada. Puedes practicar "
            "frente a un espejo o grabándote para mejorar esta habilidad.".format(contacto_pct)
        ))
    elif contacto_pct > 90:
        recomendaciones.append((
            "Contacto Visual",
            "Excelente contacto visual ({:.1f}%). Considera variar ocasionalmente tu mirada "
            "para no parecer demasiado intenso. Un contacto visual natural incluye breves "
            "pausas para reflexionar.".format(contacto_pct)
        ))
        
    # Gesticulación
    if gestos_seg < 0.5:
        recomendaciones.append((
            "Gesticulación",
            "Tu nivel de gesticulación ({:.2f} gestos/seg) es bajo. Los gestos ayudan a "
            "enfatizar puntos importantes y mantener la atención. Practica incorporando "
            "gestos naturales que acompañen tu discurso, especialmente al explicar "
            "conceptos o enumerar puntos.".format(gestos_seg)
        ))
    elif gestos_seg > 2:
        recomendaciones.append((
            "Gesticulación",
            "Tu gesticulación ({:.2f} gestos/seg) es muy frecuente. Intenta ser más "
            "selectivo con tus gestos para que cada uno tenga mayor impacto. Los gestos "
            "deben complementar tu mensaje, no distraer de él.".format(gestos_seg)
        ))
        
    # Movimiento
    if mov_prom < 5:
        recomendaciones.append((
            "Dinamismo y Movimiento",
            "Tu movimiento fue mínimo ({:.1f} px promedio). Un poco más de movimiento "
            "puede ayudar a transmitir energía y mantener la atención. Intenta cambiar "
            "de posición ocasionalmente o usar el espacio disponible.".format(mov_prom)
        ))
    elif mov_prom > 30:
        recomendaciones.append((
            "Dinamismo y Movimiento",
            "Tu nivel de movimiento ({:.1f} px promedio) fue alto. Intenta encontrar un "
            "balance entre dinamismo y estabilidad. Los movimientos deben ser intencionales "
            "y pausados para no distraer del mensaje.".format(mov_prom)
        ))
        
    # Postura
    if postura_prom < 6:
        recomendaciones.append((
            "Postura",
            "Tu postura promedio ({:.1f}/10) puede mejorar. Mantén la espalda recta, "
            "hombros relajados y pies firmemente plantados. Una buena postura transmite "
            "confianza y profesionalismo.".format(postura_prom)
        ))
        
    # Uso del espacio
    total_espacio = sum(metricas['uso_espacio'].values())
    if total_espacio > 0:
        centro_pct = metricas['uso_espacio']['centro'] / total_espacio * 100
        if centro_pct < 40:
            recomendaciones.append((
                "Uso del Espacio",
                "Pasaste solo {:.1f}% del tiempo en el centro del escenario. Intenta "
                "mantener una posición más centrada para mejor conexión con toda la "
                "audiencia.".format(centro_pct)
            ))
            
    return recomendaciones

def generar_plan_mejora(puntuacion_general, metricas):
    """Generar plan de mejora de 4 semanas"""
    plan = {}
    
    if puntuacion_general < 60:
        plan["Semana 1: Fundamentos"] = [
            "Practicar frente al espejo 10 minutos diarios enfocándose en mantener contacto visual",
            "Grabarse presentando un tema de 2 minutos y analizar la postura",
            "Ejercicios de respiración para controlar nervios (5 min/día)"
        ]
        plan["Semana 2: Gesticulación"] = [
            "Ver videos de grandes oradores y analizar sus gestos",
            "Practicar gestos específicos para enfatizar puntos clave",
            "Grabarse y contar la frecuencia de gestos"
        ]
        plan["Semana 3: Dinamismo"] = [
            "Practicar movimientos intencionales en el espacio",
            "Ejercicios de expresión corporal",
            "Presentar ante amigos o familiares para feedback"
        ]
        plan["Semana 4: Integración"] = [
            "Presentaciones completas de 5-10 minutos",
            "Autoevaluación usando ORATOR.IA",
            "Ajustes finales basados en métricas"
        ]
    else:
        plan["Semanas 1-2: Refinamiento"] = [
            "Identificar y pulir áreas específicas de mejora",
            "Practicar transiciones suaves entre temas",
            "Trabajar en la variación vocal y pausas estratégicas"
        ]
        plan["Semanas 3-4: Maestría"] = [
            "Incorporar storytelling en las presentaciones",
            "Practicar manejo de preguntas difíciles",
            "Desarrollar un estilo personal único"
        ]
        
    return plan

def main():
    """Función principal"""
    root = tk.Tk()
    app = OratoriaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()