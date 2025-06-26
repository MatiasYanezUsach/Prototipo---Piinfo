import cv2
import threading
import platform

class ThreadedCamera:
    def __init__(self, src):
        # Usar CAP_DSHOW en Windows para una inicialización de cámara más rápida
        if platform.system() == "Windows" and isinstance(src, int):
            self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        else:
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