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
)
from reporting import generar_reporte_avanzado

# Configuración de la aplicación FastAPI y Socket.IO
app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)
app.mount("/", socket_app)

# Estado global (simplificado, para producción se recomienda una mejor gestión)
analizando = False
modelo = YOLO("yolov8n.pt")

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
    asyncio.create_task(run_analysis_loop(sid, config))


@sio.on("stop_analysis")
async def stop_analysis(sid):
    global analizando
    print("Deteniendo análisis...")
    analizando = False


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

            resultados = modelo.predict(source=frame, conf=0.4, verbose=False)
            frame_anotado = frame.copy()

            if len(resultados) > 0 and resultados[0].boxes is not None:
                frame_anotado = resultados[0].plot()
                objetos = resultados[0].boxes.cls.tolist()
                nombres = [resultados[0].names[int(cls)] for cls in objetos]
                cajas = resultados[0].boxes.xyxy.cpu().numpy()

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
                        if zona_contacto_x_min < cx < zona_contacto_x_max:
                            contacto = True
                            metricas['frames_contacto'] += 1
                        if prev_centro_persona:
                            dist = ((cx - prev_centro_persona[0])**2 + (cy - prev_centro_persona[1])**2)**0.5
                            metricas['distancias_mov'].append(dist)
                        prev_centro_persona = (cx, cy)
                        zona = analyze_space_usage(cx, ancho)
                        metricas['uso_espacio'][zona] += 1
                    elif nombre in ["hand", "face"]:
                        gestos += 1
                
                metricas['gestos_totales'] += gestos

                if config.get('analisis_avanzado') and bbox_persona:
                    postura = analyze_posture(bbox_persona)
                    metricas['postura_evaluacion'].append(postura)
                    expresion = analyze_expression(frame, bbox_persona)
                    metricas['expresiones_faciales'][expresion] += 1

            # Calcular y emitir métricas en tiempo real, convirtiendo tipos de NumPy a nativos de Python
            contacto_pct = (metricas['frames_contacto'] / metricas['frames_totales']) * 100 if metricas['frames_totales'] > 0 else 0
            gestos_seg = metricas['gestos_totales'] / tiempo_actual if tiempo_actual > 0 else 0
            mov_prom = float(np.mean(metricas['distancias_mov'])) if metricas['distancias_mov'] else 0.0
            postura_prom = float(np.mean(metricas['postura_evaluacion'])) if metricas['postura_evaluacion'] else 5.0
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