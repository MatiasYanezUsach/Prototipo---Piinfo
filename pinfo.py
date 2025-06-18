import cv2
from ultralytics import YOLO
import time
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime
import matplotlib.pyplot as plt
import io
import os

# Función para crear gráficos
def crear_grafico(datos, titulo, nombre_archivo, tipo="linea"):
    plt.figure(figsize=(6, 4))
    if tipo == "linea":
        plt.plot(datos, color='#3366cc', linewidth=2)
        plt.xlabel("Tiempo (segundos)")
        plt.ylabel("Valor")
        # Añadir puntos en la línea para mayor claridad
        plt.scatter(range(len(datos)), datos, color='#3366cc', s=30)
    elif tipo == "barras":
        plt.bar(range(len(datos)), datos, color='#3366cc')
        plt.xlabel("Tiempo (segundos)")
        plt.ylabel("Valor")
    elif tipo == "pastel":
        plt.pie([datos, 100-datos], labels=['Contacto visual', 'Sin contacto'], 
                autopct='%1.1f%%', colors=['#3366cc', '#dc3912'])
        
    plt.title(titulo)
    plt.tight_layout()
    
    # Guardar gráfico como imagen temporal
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=100)
    img_data.seek(0)
    plt.close()
    
    # Guardar también como archivo para referencia
    plt.figure(figsize=(6, 4))
    if tipo == "linea":
        plt.plot(datos, color='#3366cc', linewidth=2)
        plt.xlabel("Tiempo (segundos)")
        plt.ylabel("Valor")
        plt.scatter(range(len(datos)), datos, color='#3366cc', s=30)
    elif tipo == "barras":
        plt.bar(range(len(datos)), datos, color='#3366cc')
        plt.xlabel("Tiempo (segundos)")
        plt.ylabel("Valor")
    elif tipo == "pastel":
        plt.pie([datos, 100-datos], labels=['Contacto visual', 'Sin contacto'], 
                autopct='%1.1f%%', colors=['#3366cc', '#dc3912'])
    plt.title(titulo)
    plt.tight_layout()
    plt.savefig(nombre_archivo)
    plt.close()
    
    return img_data

# Función para generar el PDF con los resultados
def generar_reporte_pdf(nombre_usuario, duracion, contacto_pct, gestos_por_seg, mov_promedio, 
                       contacto_por_tiempo, gestos_por_tiempo, mov_por_tiempo, 
                       ruta_imagen_usuario="captura_final.jpg"):
    
    # Crear la carpeta de reportes si no existe
    if not os.path.exists("reportes"):
        os.makedirs("reportes")
    
    # Nombre del archivo con fecha y hora
    ahora = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"reportes/reporte_oratoria_{nombre_usuario}_{ahora}.pdf"
    
    # Crear documento PDF
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    elementos = []
    
    # Estilos
    estilos = getSampleStyleSheet()
    estilo_titulo = estilos['Heading1']
    estilo_titulo.alignment = 1  # Centrado
    estilo_subtitulo = estilos['Heading2']
    estilo_normal = estilos['Normal']
    
    # Título del documento
    elementos.append(Paragraph(f"Análisis de Presentación Oral", estilo_titulo))
    elementos.append(Spacer(1, 0.25*inch))
    
    # Información del usuario
    elementos.append(Paragraph(f"Reporte para: {nombre_usuario}", estilo_subtitulo))
    elementos.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", estilo_normal))
    elementos.append(Paragraph(f"Duración del análisis: {duracion} segundos", estilo_normal))
    elementos.append(Spacer(1, 0.25*inch))
    
    # Crear gráficos
    img_contacto = crear_grafico(contacto_pct, "Contacto Visual", "reportes/grafico_contacto.png", "pastel")
    img_gestos = crear_grafico(gestos_por_tiempo, "Gestos por Segundo", "reportes/grafico_gestos.png", "linea")
    img_movimiento = crear_grafico(mov_por_tiempo, "Movimiento durante la Presentación", "reportes/grafico_movimiento.png", "linea")
    
    # Resultados principales
    datos = [
        ["Métrica", "Resultado", "Evaluación"],
        ["Contacto visual", f"{contacto_pct:.1f}%", "Excelente" if contacto_pct > 70 else "Bueno" if contacto_pct > 50 else "Mejorable"],
        ["Gestos por segundo", f"{gestos_por_seg:.2f}", "Adecuado" if 0.5 < gestos_por_seg < 2 else "Revisar"],
        ["Dinamismo de movimiento", f"{mov_promedio:.1f} px", "Adecuado" if 5 < mov_promedio < 30 else "Revisar"]
    ]
    
    tabla = Table(datos, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elementos.append(Paragraph("Resumen de Resultados", estilo_subtitulo))
    elementos.append(tabla)
    elementos.append(Spacer(1, 0.25*inch))
    
    # Añadir gráficos
    if os.path.exists(ruta_imagen_usuario):
        img = Image(ruta_imagen_usuario, width=4*inch, height=3*inch)
        elementos.append(Paragraph("Captura de la Presentación", estilo_subtitulo))
        elementos.append(img)
        elementos.append(Spacer(1, 0.25*inch))
    
    # Gráfico de contacto visual
    img = Image(img_contacto, width=3*inch, height=2.5*inch)
    elementos.append(Paragraph("Análisis de Contacto Visual", estilo_subtitulo))
    elementos.append(img)
    elementos.append(Spacer(1, 0.25*inch))
    
    # Gráfico de gestos
    img = Image(img_gestos, width=5*inch, height=2.5*inch)
    elementos.append(Paragraph("Análisis de Gesticulación", estilo_subtitulo))
    elementos.append(img)
    elementos.append(Spacer(1, 0.25*inch))
    
    # Gráfico de movimiento
    img = Image(img_movimiento, width=5*inch, height=2.5*inch)
    elementos.append(Paragraph("Análisis de Movimiento", estilo_subtitulo))
    elementos.append(img)
    elementos.append(Spacer(1, 0.25*inch))
    
    # Recomendaciones
    elementos.append(Paragraph("Recomendaciones", estilo_subtitulo))
    
    if contacto_pct < 50:
        elementos.append(Paragraph("• Intenta mantener más contacto visual con la audiencia. Mira directamente a la cámara con más frecuencia.", estilo_normal))
    
    if gestos_por_seg < 0.5:
        elementos.append(Paragraph("• Usa más gestos para enfatizar puntos importantes en tu presentación.", estilo_normal))
    elif gestos_por_seg > 2:
        elementos.append(Paragraph("• Considera reducir la frecuencia de gestos para no distraer a la audiencia.", estilo_normal))
    
    if mov_promedio < 5:
        elementos.append(Paragraph("• Intenta moverte un poco más para dar dinamismo a tu presentación.", estilo_normal))
    elif mov_promedio > 30:
        elementos.append(Paragraph("• Trata de mantener un poco más de estabilidad en tu posición para no distraer.", estilo_normal))
    
    # Generación del PDF
    doc.build(elementos)
    
    return pdf_filename

# Cargar el modelo YOLOv8-nano (debe estar en la carpeta actual)
modelo = YOLO("yolov8n.pt")

# Conectar a la cámara del celular (IP Webcam en Android)
cam = cv2.VideoCapture("http://192.168.100.11:8080/video")

# Si no se puede conectar a la cámara IP, intentar con la cámara local
if not cam.isOpened():
    print("No se pudo conectar a la cámara IP, intentando con la cámara local...")
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("No se pudo acceder a ninguna cámara. Saliendo...")
        exit()

# Configuración del video
ancho, alto, fps = 640, 480, 20
cam.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
salida = cv2.VideoWriter("demo_oratoria_yolo.avi", fourcc, fps, (ancho, alto))

# Parámetros de análisis
duracion = 30  # segundos
inicio = time.time()
frames_totales = 0
frames_contacto = 0
gestos_totales = 0
prev_centro_persona = None
distancias_mov = []

# Variables para el seguimiento temporal
contacto_por_tiempo = []
gestos_por_tiempo = []
mov_por_tiempo = []
capturando_cada = 1  # capturas cada segundo
ultima_captura = 0
captura_final = None

# Zona de contacto visual (ampliada para ser más sensible)
zona_contacto_x_min = ancho * 0.3  # Antes era 0.35
zona_contacto_x_max = ancho * 0.7  # Antes era 0.65

print("🎬 Grabando presentación con análisis en vivo...")
print("📝 Al finalizar, se generará un PDF con los resultados")
print("👁️ Zona de contacto visual configurada entre", zona_contacto_x_min, "y", zona_contacto_x_max)

# Definimos una función para detectar el contacto visual más efectivamente
def detectar_contacto_visual(frame, cajas, nombres):
    """Detecta si hay contacto visual analizando la posición de la cara/ojos"""
    hay_contacto = False
    
    # Buscar cajas específicas de cara, persona u ojos
    for i, clase in enumerate(nombres):
        nombre = clase
        if nombre in ["person", "face"]:
            x1, y1, x2, y2 = cajas[i]
            cx = (x1 + x2) / 2  # Centro horizontal
            # Verificar si el centro está en la zona de contacto
            if zona_contacto_x_min < cx < zona_contacto_x_max:
                hay_contacto = True
                break
    
    return hay_contacto

while int(time.time() - inicio) < duracion:
    ret, frame = cam.read()
    if not ret:
        print("❌ No se pudo capturar el frame.")
        break
    
    frames_totales += 1
    tiempo_actual = time.time() - inicio
    
    resultados = modelo.predict(source=frame, conf=0.4, verbose=False)
    objetos = resultados[0].boxes.cls.tolist()
    nombres = [resultados[0].names[int(cls)] for cls in objetos]
    cajas = resultados[0].boxes.xyxy.cpu().numpy()
    
    # Mejoramos la detección de contacto visual
    contacto = False
    gestos = 0
    bbox_mayor = None
    area_mayor = 0
    movimiento_actual = 0
    
    # Dibujar la zona de contacto visual en el frame para referencia
    frame_guia = frame.copy()
    cv2.line(frame_guia, (int(zona_contacto_x_min), 0), (int(zona_contacto_x_min), alto), (0, 255, 0), 1)
    cv2.line(frame_guia, (int(zona_contacto_x_max), 0), (int(zona_contacto_x_max), alto), (0, 255, 0), 1)
    
    for i, nombre in enumerate(nombres):
        x1, y1, x2, y2 = cajas[i]
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        area = (x2 - x1) * (y2 - y1)
        
        if nombre == "person":
            gestos += 1
            if area > area_mayor:
                bbox_mayor = (x1, y1, x2, y2, cx)
                area_mayor = area
            
            if prev_centro_persona:
                dx = abs(cx - prev_centro_persona[0])
                dy = abs(cy - prev_centro_persona[1])
                dist = (dx**2 + dy**2)**0.5
                distancias_mov.append(dist)
                movimiento_actual = dist
            
            prev_centro_persona = (cx, cy)
            
            # Verificar contacto visual
            if zona_contacto_x_min < cx < zona_contacto_x_max:
                contacto = True
                # Dibujar indicador de contacto visual
                cv2.circle(frame_guia, (int(cx), int(cy)), 5, (0, 255, 0), -1)
        
        elif nombre == "hand" or nombre == "face":
            gestos += 1
            
            if nombre == "face" and zona_contacto_x_min < cx < zona_contacto_x_max:
                contacto = True
    
    # Si se detecta contacto visual, incrementar contador
    if contacto:
        frames_contacto += 1
    
    gestos_totales += gestos
    
    # Registrar métricas a lo largo del tiempo
    if int(tiempo_actual) > ultima_captura:
        ultima_captura = int(tiempo_actual)
        # Contacto visual acumulado hasta este momento
        contacto_pct_acumulado = (frames_contacto / frames_totales) * 100
        contacto_por_tiempo.append(contacto_pct_acumulado)
        
        # Gestos por segundo en este momento
        gestos_por_tiempo.append(gestos_totales / max(1, tiempo_actual))
        
        # Movimiento promedio hasta este momento
        if distancias_mov:
            mov_por_tiempo.append(sum(distancias_mov) / len(distancias_mov))
        else:
            mov_por_tiempo.append(0)
    
    # Métricas acumuladas para mostrar en pantalla
    contacto_pct = (frames_contacto / frames_totales) * 100
    gestos_por_seg = gestos_totales / max(1, tiempo_actual)
    mov_promedio = sum(distancias_mov) / max(1, len(distancias_mov)) if distancias_mov else 0
    
    # Anotar el frame con el modelo y las métricas
    anotado = resultados[0].plot()
    
    # Dibujar la zona de contacto visual
    cv2.rectangle(anotado, 
                 (int(zona_contacto_x_min), 0), 
                 (int(zona_contacto_x_max), alto), 
                 (0, 255, 0, 128), 2)
    
    # Texto con indicadores
    texto1 = f"Contacto visual: {contacto_pct:.1f}% {'✓' if contacto else '✗'}"
    texto2 = f"Gestos/seg: {gestos_por_seg:.1f} | Movimiento: {mov_promedio:.1f}px"
    texto3 = f"Tiempo: {int(tiempo_actual)}/{duracion}s"
    
    cv2.putText(anotado, texto1, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if contacto else (0, 0, 255), 2)
    cv2.putText(anotado, texto2, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(anotado, texto3, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Guardar el último frame para el PDF
    if int(tiempo_actual) == duracion - 1 or int(tiempo_actual) > duracion - 2:
        captura_final = anotado.copy()
        cv2.imwrite("captura_final.jpg", captura_final)
    
    cv2.imshow("ORATOR.IA - Demo Prototipo", anotado)
    salida.write(anotado)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        # Si el usuario presiona 'q', guardar una captura final
        captura_final = anotado.copy()
        cv2.imwrite("captura_final.jpg", captura_final)
        break

# Cierre y métricas
cam.release()
salida.release()
cv2.destroyAllWindows()

print("✅ Grabación finalizada.")
print("🎥 Video guardado como 'demo_oratoria_yolo.avi'")
print(f"🧠 Contacto visual promedio: {contacto_pct:.2f}%")
print(f"✋ Gestos por segundo estimados: {gestos_por_seg:.2f}")
print(f"📈 Movimiento promedio estimado: {mov_promedio:.2f} píxeles por frame")

# Solicitar nombre de usuario para el PDF
nombre_usuario = input("📋 Ingresa tu nombre para generar el reporte PDF: ")

try:
    # Generar y guardar el PDF con los resultados
    pdf_generado = generar_reporte_pdf(
        nombre_usuario=nombre_usuario,
        duracion=duracion,
        contacto_pct=contacto_pct,
        gestos_por_seg=gestos_por_seg,
        mov_promedio=mov_promedio,
        contacto_por_tiempo=contacto_por_tiempo,
        gestos_por_tiempo=gestos_por_tiempo,
        mov_por_tiempo=mov_por_tiempo
    )
    
    print(f"📊 Reporte PDF generado: {pdf_generado}")
except Exception as e:
    print(f"❌ Error al generar el PDF: {e}")
    print("Guardando los datos para un nuevo intento...")
    # Guardar datos en CSV por si acaso
    with open("datos_analisis.csv", "w") as f:
        f.write(f"Contacto Visual,{contacto_pct}\n")
        f.write(f"Gestos por Segundo,{gestos_por_seg}\n")
        f.write(f"Movimiento Promedio,{mov_promedio}\n")

print("¡Gracias por usar ORATOR.IA!")
