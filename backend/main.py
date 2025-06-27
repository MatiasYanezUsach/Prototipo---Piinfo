import asyncio
import base64
import cv2
import time
import json
from datetime import datetime

from fastapi import FastAPI, Form
import socketio
from ultralytics import YOLO
from PIL import Image as PILImage, ImageTk
import numpy as np

from camera import ThreadedCamera
from analysis import (
    analyze_posture,
    analyze_expression,
    analyze_space_usage,
    calculate_fluency,
    reset_metrics,
    analyze_eye_contact,
)
from reporting import generar_reporte_avanzado

# Configuración de la aplicación FastAPI y Socket.IO
app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)
app.mount("/", socket_app)

# Estado global (simplificado, para producción se recomienda una mejor gestión)
analizando = False
# Soporta ahora dos modos:
#   • "local" / "ip"  → se usa ThreadedCamera y run_analysis_loop()
#   • "browser"        → el cliente envía cada fotograma con el evento "browser_frame"
#     y se procesan aquí manteniendo el estado en browser_session.

modelo = YOLO("yolov8n.pt")

# Estructura para mantener el estado de la sesión cuando la cámara proviene del navegador
browser_session = {
    "metricas": None,
    "inicio": None,
    "duracion": None,
    "prev_centro": None,
    "config": None,
    "sid": None,
}

@sio.on("connect")
async def connect(sid, environ):
    print(f"Socket.IO client connected: {sid}")

@sio.on("disconnect")
async def disconnect(sid):
    print(f"Socket.IO client disconnected: {sid}")
    global analizando
    analizando = False

@sio.on("start_analysis")
async def start_analysis(sid, config):
    print(f"Iniciando análisis con configuración: {config}")
    global analizando
    if analizando:
        print("El análisis ya está en curso.")
        return

    analizando = True

    # Si la cámara viene del navegador, se inicializa la sesión y se espera a los frames
    if config.get("camera_type") == "browser":
        browser_session["metricas"] = reset_metrics()
        browser_session["inicio"] = time.time()
        browser_session["duracion"] = config.get("duracion", 30)
        browser_session["prev_centro"] = None
        browser_session["config"] = config
        browser_session["sid"] = sid
        await sio.emit("status_update", {"message": "Enviando vídeo desde navegador..."}, room=sid)
    else:
        # Para cámara local o IP se mantiene la lógica existente
        asyncio.create_task(run_analysis_loop(sid, config))

@sio.on("stop_analysis")
async def stop_analysis(sid):
    global analizando
    print("Deteniendo análisis...")
    analizando = False

    # Si la sesión es de navegador limpiamos y notificamos
    if browser_session.get("sid") == sid:
        await finalize_browser_session()

async def run_analysis_loop(sid, config):
    global analizando, modelo
    
    try:
        await sio.emit('status_update', {'message': 'Iniciando cámara...'}, room=sid)
        src = 0 if config.get("camera_type") == "local" else f"http://{config.get('ip')}/video"
        cam = ThreadedCamera(src).start()
        if cam is None:
            await sio.emit("analysis_error", {"error": "No se pudo conectar a la cámara."}, room=sid)
            analizando = False
            return

        ancho, alto = 640, 480
        # salida = None # Implementar guardado de video si es necesario

        inicio = time.time()
        duracion = config.get('duracion', 30)
        metricas = reset_metrics()
        prev_centro_persona = None
        
        zona_contacto_x_min = ancho * 0.3
        zona_contacto_x_max = ancho * 0.7

        print(f"🎬 Iniciando bucle de análisis de {duracion} segundos...")

        while analizando and (time.time() - inicio) < duracion:
            frame = cam.read()
            if frame is None:
                await asyncio.sleep(0.01)
                continue

            metricas['frames_totales'] += 1
            tiempo_actual = time.time() - inicio

            # --- Detección de contacto visual (MediaPipe) ---
            contact_already = False
            eye_contact = analyze_eye_contact(frame)
            if eye_contact is True:
                metricas['frames_contacto'] += 1
                contact_already = True

            resultados = modelo.predict(source=frame, conf=0.4, verbose=False)
            frame_anotado = frame.copy()
            bbox_persona = None  # Se inicializa para evitar referencia no definida

            if len(resultados) > 0 and resultados[0].boxes is not None:
                frame_anotado = resultados[0].plot()
                objetos = resultados[0].boxes.cls.tolist()
                nombres = [resultados[0].names[int(cls)] for cls in objetos]
                cajas = resultados[0].boxes.xyxy.cpu().numpy()

                contacto = False
                gestos = 0
                area_mayor = 0

                for i, nombre in enumerate(nombres):
                    x1, y1, x2, y2 = cajas[i]
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    area = (x2 - x1) * (y2 - y1)
                    
                    if nombre == "person":
                        if area > area_mayor:
                            bbox_persona = (x1, y1, x2, y2, cx, cy)
                            area_mayor = area
                        if zona_contacto_x_min < cx < zona_contacto_x_max:
                            if not contact_already:
                                metricas['frames_contacto'] += 1
                                contact_already = True
                        if prev_centro_persona:
                            dist = ((cx - prev_centro_persona[0])**2 + (cy - prev_centro_persona[1])**2)**0.5
                            metricas['distancias_mov'].append(dist)
                        prev_centro_persona = (cx, cy)
                        zona = analyze_space_usage(cx, ancho)
                        metricas['uso_espacio'][zona] += 1
                    elif nombre in ["hand", "face"]:
                        gestos += 1
                
                metricas['gestos_totales'] += gestos
                metricas['gestos_por_tiempo'].append((tiempo_actual, gestos))

                if bbox_persona is not None:
                    postura = analyze_posture(bbox_persona)
                    metricas['postura_evaluacion'].append(postura)
                    metricas['postura_por_tiempo'].append((tiempo_actual, postura))

            # Expresiones faciales solo en modo avanzado para ahorrar recursos
            if config.get('analisis_avanzado') and bbox_persona:
                expresion = analyze_expression(frame, bbox_persona)
                metricas['expresiones_faciales'][expresion] += 1

            # Calcular y emitir métricas en tiempo real, convirtiendo tipos de NumPy a nativos de Python
            contacto_pct = (metricas['frames_contacto'] / metricas['frames_totales']) * 100 if metricas['frames_totales'] > 0 else 0
            # Ventana deslizante de 3 segundos para gestos y postura
            VENTANA = 3.0
            gestos_ventana = [g for t, g in metricas['gestos_por_tiempo'] if tiempo_actual - t <= VENTANA]
            gestos_seg = sum(gestos_ventana) / VENTANA if gestos_ventana else 0
            mov_prom = float(np.mean(metricas['distancias_mov'])) if metricas['distancias_mov'] else 0.0
            posturas_ventana = [p for t, p in metricas['postura_por_tiempo'] if tiempo_actual - t <= VENTANA]
            postura_prom = float(np.mean(posturas_ventana)) if posturas_ventana else 5.0
            expresividad = min(10, gestos_seg * 3 + 3)
            fluidez = float(calculate_fluency(metricas))

            live_metrics = {
                'contacto': contacto_pct,
                'gestos': gestos_seg,
                'movimiento': mov_prom,
                'postura': postura_prom,
                'expresividad': expresividad,
                'fluidez': fluidez,
                'progreso': (tiempo_actual / duracion) * 100,
                'tiempo_actual': tiempo_actual,
            }
            await sio.emit('live_metrics', live_metrics, room=sid)

            # Codificar y emitir frame de video
            _, buffer = cv2.imencode('.jpg', frame_anotado)
            frame_b64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
            await sio.emit('video_frame', {'image': frame_b64}, room=sid)

            await asyncio.sleep(0.05) # Controla el FPS del stream

        print("📊 Finalizando análisis...")
        cam.stop()
        
        if analizando: # Si no fue detenido manualmente
            print("📄 Generando reporte...")
            report_config = {
                'analisis_avanzado': config.get('analisis_avanzado', True)
            }
            pdf_file = generar_reporte_avanzado(
                nombre_usuario=config.get('nombre', 'Usuario'),
                duracion=duracion,
                metricas=metricas,
                config=report_config
            )
            await sio.emit("report_generated", {"file_path": pdf_file}, room=sid)
        
    except Exception as e:
        print(f"❌ Error en run_analysis_loop: {str(e)}")
        await sio.emit("analysis_error", {"error": str(e)}, room=sid)
    finally:
        analizando = False
        print("Análisis finalizado.")
        await sio.emit("analysis_finished", room=sid)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# -----------------------------------------------
# NUEVO: Manejo de frames enviados desde el navegador
# -----------------------------------------------

@sio.on("browser_frame")
async def browser_frame(sid, data):
    """Recibe fotogramas base64 desde el navegador del cliente."""
    global analizando, browser_session, modelo

    # Ignorar si no estamos en modo análisis o el sid no coincide
    if not analizando or browser_session.get("sid") != sid:
        return

    try:
        # Decodificar la imagen
        img_bytes = base64.b64decode(data.get("image", ""))
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            return

        ancho, alto = frame.shape[1], frame.shape[0]

        # Iniciales de la sesión
        metricas = browser_session["metricas"]
        prev_centro_persona = browser_session["prev_centro"]

        duracion = browser_session["duracion"]
        tiempo_actual = time.time() - browser_session["inicio"]

        # --------------------------------------------------
        # Lógica de análisis (idéntica a la de run_analysis_loop)
        # --------------------------------------------------
        metricas["frames_totales"] += 1

        # --- Detección de contacto visual (MediaPipe) ---
        contact_already = False
        eye_contact = analyze_eye_contact(frame)
        if eye_contact is True:
            metricas["frames_contacto"] += 1
            contact_already = True

        resultados = modelo.predict(source=frame, conf=0.4, verbose=False)
        frame_anotado = frame.copy()
        bbox_persona = None  # Se inicializa para evitar referencia no definida

        zona_contacto_x_min = ancho * 0.3
        zona_contacto_x_max = ancho * 0.7

        if len(resultados) > 0 and resultados[0].boxes is not None:
            frame_anotado = resultados[0].plot()
            objetos = resultados[0].boxes.cls.tolist()
            nombres = [resultados[0].names[int(cls)] for cls in objetos]
            cajas = resultados[0].boxes.xyxy.cpu().numpy()

            gestos = 0
            area_mayor = 0

            for i, nombre in enumerate(nombres):
                x1, y1, x2, y2 = cajas[i]
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                area = (x2 - x1) * (y2 - y1)

                if nombre == "person":
                    if area > area_mayor:
                        bbox_persona = (x1, y1, x2, y2, cx, cy)
                        area_mayor = area
                    if zona_contacto_x_min < cx < zona_contacto_x_max:
                        if not contact_already:
                            metricas["frames_contacto"] += 1
                            contact_already = True
                    if prev_centro_persona:
                        dist = ((cx - prev_centro_persona[0])**2 + (cy - prev_centro_persona[1])**2)**0.5
                        metricas["distancias_mov"].append(dist)
                    prev_centro_persona = (cx, cy)
                    zona = analyze_space_usage(cx, ancho)
                    metricas["uso_espacio"][zona] += 1
                elif nombre in ["hand", "face"]:
                    gestos += 1

            metricas["gestos_totales"] += gestos
            metricas["gestos_por_tiempo"].append((tiempo_actual, gestos))

            if bbox_persona is not None:
                postura = analyze_posture(bbox_persona)
                metricas["postura_evaluacion"].append(postura)
                metricas["postura_por_tiempo"].append((tiempo_actual, postura))

            # Expresiones faciales solo en modo avanzado para ahorrar recursos
            if browser_session["config"].get("analisis_avanzado") and bbox_persona:
                expresion = analyze_expression(frame, bbox_persona)
                metricas["expresiones_faciales"][expresion] += 1

        # Calcular métricas en tiempo real
        contacto_pct = (
            metricas["frames_contacto"] / metricas["frames_totales"] * 100
            if metricas["frames_totales"] > 0 else 0
        )
        # Ventana deslizante de 3 segundos para gestos y postura
        VENTANA = 3.0
        gestos_ventana = [g for t, g in metricas["gestos_por_tiempo"] if tiempo_actual - t <= VENTANA]
        gestos_seg = sum(gestos_ventana) / VENTANA if gestos_ventana else 0
        mov_prom = float(np.mean(metricas["distancias_mov"])) if metricas["distancias_mov"] else 0.0
        posturas_ventana = [p for t, p in metricas["postura_por_tiempo"] if tiempo_actual - t <= VENTANA]
        postura_prom = float(np.mean(posturas_ventana)) if posturas_ventana else 5.0
        expresividad = min(10, gestos_seg * 3 + 3)
        fluidez = float(calculate_fluency(metricas))

        live_metrics = {
            "contacto": contacto_pct,
            "gestos": gestos_seg,
            "movimiento": mov_prom,
            "postura": postura_prom,
            "expresividad": expresividad,
            "fluidez": fluidez,
            "progreso": (tiempo_actual / duracion) * 100,
            "tiempo_actual": tiempo_actual,
        }
        await sio.emit("live_metrics", live_metrics, room=sid)

        # Enviar frame anotado de vuelta al cliente
        _, buffer = cv2.imencode('.jpg', frame_anotado)
        frame_b64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
        await sio.emit('video_frame', {'image': frame_b64}, room=sid)

        # Guardar estado actualizado
        browser_session["metricas"] = metricas
        browser_session["prev_centro"] = prev_centro_persona

        # ¿Terminó la sesión por tiempo?
        if tiempo_actual >= duracion:
            await finalize_browser_session()

    except Exception as e:
        print(f"❌ Error en browser_frame: {e}")
        await sio.emit("analysis_error", {"error": str(e)}, room=sid)

async def finalize_browser_session():
    """Genera el reporte y notifica fin de análisis para la sesión de navegador."""
    global analizando, browser_session

    if not browser_session["metricas"]:
        return

    try:
        config = browser_session["config"]
        sid = browser_session["sid"]

        print("📄 Generando reporte (browser)...")
        pdf_file = generar_reporte_avanzado(
            nombre_usuario=config.get("nombre", "Usuario"),
            duracion=browser_session["duracion"],
            metricas=browser_session["metricas"],
            config={"analisis_avanzado": config.get("analisis_avanzado", True)},
        )
        await sio.emit("report_generated", {"file_path": pdf_file}, room=sid)
    except Exception as e:
        print(f"❌ Error al generar reporte (browser): {e}")
        await sio.emit("analysis_error", {"error": str(e)}, room=browser_session["sid"])
    finally:
        # Limpiar estado global
        analizando = False
        await sio.emit("analysis_finished", room=browser_session["sid"])
        browser_session = {
            "metricas": None,
            "inicio": None,
            "duracion": None,
            "prev_centro": None,
            "config": None,
            "sid": None,
        } 