import os
import io
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

# Ruta del logo (se intenta primero en raíz y luego en frontend)
LOGO_PATH = None
for candidate in [
    os.path.join(os.path.dirname(__file__), '..', 'orator_logo.png'),  # raíz del repo
    os.path.join(os.path.dirname(__file__), '..', 'frontend', 'orator_logo.png'),
]:
    if os.path.exists(candidate):
        LOGO_PATH = candidate
        break

def generar_reporte_avanzado(nombre_usuario, duracion, metricas, config):
    """Generar reporte PDF avanzado con todas las métricas"""
    
    # Crear carpeta de reportes
    if not os.path.exists("reportes"):
        os.makedirs("reportes")
        
    # Nombre del archivo
    ahora = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"reportes/reporte_avanzado_{nombre_usuario}_{ahora}.pdf"
    
    # ------------------------------
    #  Funciones de diseño por página
    # ------------------------------
    def _draw_page_background(canvas, doc):
        """Fondo y cabecera común para todas las páginas."""
        canvas.saveState()

        # Fondo suave
        canvas.setFillColor(colors.HexColor('#f5f7fa'))
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)

        # Header band
        canvas.setFillColor(colors.HexColor('#4CAF50'))
        canvas.rect(0, doc.pagesize[1] - 40, doc.pagesize[0], 40, fill=1, stroke=0)

        # Logo en esquina superior derecha (si existe)
        if LOGO_PATH:
            try:
                canvas.drawImage(LOGO_PATH, doc.pagesize[0] - 60, doc.pagesize[1] - 35, width=50, height=30, mask='auto', preserveAspectRatio=True)
            except Exception as _:
                pass

        canvas.restoreState()

    def _draw_first_page(canvas, doc):
        """Portada con logo grande"""
        _draw_page_background(canvas, doc)
        if LOGO_PATH:
            try:
                # Centro de la portada
                logo_width = 200
                logo_height = 120
                x = (doc.pagesize[0] - logo_width) / 2
                y = doc.pagesize[1] - 200
                canvas.drawImage(LOGO_PATH, x, y, width=logo_width, height=logo_height, mask='auto', preserveAspectRatio=True)
            except Exception as _:
                pass

    # Crear documento con callbacks de página
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        topMargin=72,
        bottomMargin=72,
        leftMargin=50,
        rightMargin=50,
    )
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
    elementos.append(Spacer(1, 1.2*inch))
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
        
    # Construir PDF con decoradores
    doc.build(elementos, onFirstPage=_draw_first_page, onLaterPages=_draw_page_background)
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