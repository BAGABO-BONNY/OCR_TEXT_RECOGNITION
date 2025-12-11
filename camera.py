import cv2
import time
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            print("ERROR: Cannot open camera")
            return
        
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
                time.sleep(0.03)  # ~30 FPS, adjust as needed
            else:
                print("ERROR: Failed to read frame from camera")
                break
        
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()