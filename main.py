import sys
import cv2
import numpy as np
import pytesseract
from PIL import Image
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QDockWidget, QMainWindow
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage
from PyQt5.QtCore import Qt, QRect

from camera import CameraThread
from utils import convert_cv_qt

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\user\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.roi_rect = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.roi_rect = None
            self.update()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.end_point = event.pos()
            self.roi_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.start_point and self.end_point:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            rect = QRect(self.start_point, self.end_point).normalized()
            painter.drawRect(rect)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Printed Text Scanner")
        self.resize(1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Left side: Image Display
        self.image_layout = QVBoxLayout()
        self.image_label = ImageLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black; background-color: #f0f0f0;")
        self.image_layout.addWidget(self.image_label)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        self.btn_load = QPushButton("Load Image")
        self.btn_camera = QPushButton("Start Camera")
        self.btn_capture = QPushButton("Capture")
        self.btn_ocr = QPushButton("Run OCR")
        self.btn_clear = QPushButton("Clear")

        self.button_layout.addWidget(self.btn_load)
        self.button_layout.addWidget(self.btn_camera)
        self.button_layout.addWidget(self.btn_capture)
        self.button_layout.addWidget(self.btn_ocr)
        self.button_layout.addWidget(self.btn_clear)
        
        self.image_layout.addLayout(self.button_layout)
        self.layout.addLayout(self.image_layout, 70)

        # Right side: Text Output
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.layout.addWidget(self.text_output, 30)

        # Connections
        self.btn_load.clicked.connect(self.load_image)
        self.btn_camera.clicked.connect(self.start_camera)
        self.btn_capture.clicked.connect(self.capture_image)
        self.btn_ocr.clicked.connect(self.run_ocr)
        self.btn_clear.clicked.connect(self.clear_all)

        # State
        self.current_image = None # OpenCV image (BGR)
        self.camera_thread = None
        self.is_camera_active = False

    def load_image(self):
        if self.is_camera_active:
            self.stop_camera()
            
        fname, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.PNG *.JPG *.JPEG *.BMP)")
        if fname:
            self.current_image = cv2.imread(fname)
            self.display_image(self.current_image)
            self.image_label.roi_rect = None
            self.image_label.start_point = None
            self.image_label.end_point = None

    def start_camera(self):
        if not self.is_camera_active:
            self.camera_thread = CameraThread()
            self.camera_thread.change_pixmap_signal.connect(self.update_image)
            self.camera_thread.start()
            self.is_camera_active = True
            self.btn_camera.setText("Stop Camera")
            self.btn_capture.setEnabled(True)
        else:
            self.stop_camera()

    def stop_camera(self):
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None
        self.is_camera_active = False
        self.btn_camera.setText("Start Camera")

    def update_image(self, cv_img):
        self.current_image = cv_img
        self.display_image(cv_img)

    def capture_image(self):
        if self.is_camera_active:
            self.stop_camera()
            # Current image is already stored in self.current_image
            # Just need to stop updating it
            self.btn_camera.setText("Start Camera")

    def display_image(self, cv_img):
        if cv_img is None:
            return
        qt_img = convert_cv_qt(cv_img, self.image_label.width(), self.image_label.height())
        self.image_label.setPixmap(qt_img)

    def run_ocr(self):
        print("DEBUG: run_ocr called")
        if self.current_image is None:
            print("DEBUG: No image loaded")
            return

        try:
            # Check for ROI
            if self.image_label.roi_rect:
                print("DEBUG: ROI detected")
                # Map ROI from display coordinates to image coordinates
                # This is tricky because of scaling.
                # For simplicity, let's assume we need to calculate the scale factor.
                
                display_width = self.image_label.width()
                display_height = self.image_label.height()
                img_h, img_w, _ = self.current_image.shape
                
                # Calculate scale
                scale_w = display_width / img_w
                scale_h = display_height / img_h
                scale = min(scale_w, scale_h)
                
                # Calculate offsets (centering)
                new_w = int(img_w * scale)
                new_h = int(img_h * scale)
                offset_x = (display_width - new_w) // 2
                offset_y = (display_height - new_h) // 2
                
                rect = self.image_label.roi_rect
                x = int((rect.x() - offset_x) / scale)
                y = int((rect.y() - offset_y) / scale)
                w = int(rect.width() / scale)
                h = int(rect.height() / scale)
                
                # Clamp
                x = max(0, x)
                y = max(0, y)
                w = min(w, img_w - x)
                h = min(h, img_h - y)
                
                print(f"DEBUG: ROI coordinates: x={x}, y={y}, w={w}, h={h}")

                if w > 0 and h > 0:
                    roi = self.current_image[y:y+h, x:x+w]
                    
                    # Debug: Save ROI
                    cv2.imwrite("debug_roi.png", roi)
                    print("DEBUG: Saved debug_roi.png")

                    # Preprocessing
                    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                    # Otsu's thresholding
                    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                    
                    # Debug: Save preprocessed ROI
                    cv2.imwrite("debug_roi_processed.png", gray)

                    # Configure tesseract to be more lenient (psm 6 is assume a single uniform block of text)
                    custom_config = r'--oem 3 --psm 6'
                    text = pytesseract.image_to_string(gray, config=custom_config)
                    
                    print(f"DEBUG: OCR Result (ROI) Raw: {repr(text)}")
                    # User requested to ignore the first letter
                    if len(text) > 0:
                        text = text[1:]
                    self.text_output.setText(text)
                    
                    # Draw box on image (for visualization)
                    vis_img = self.current_image.copy()
                    cv2.rectangle(vis_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    self.display_image(vis_img)
            else:
                print("DEBUG: Full image OCR")
                # Full image OCR
                text = pytesseract.image_to_string(self.current_image)
                print(f"DEBUG: OCR Result (Full): {text[:50]}...")
                # User requested to ignore the first letter
                if len(text) > 0:
                    text = text[1:]
                self.text_output.setText(text)
                
                # Get data for bounding boxes
                data = pytesseract.image_to_data(self.current_image, output_type=pytesseract.Output.DICT)
                n_boxes = len(data['text'])
                vis_img = self.current_image.copy()
                for i in range(n_boxes):
                    if int(data['conf'][i]) > 60:
                        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                        cv2.rectangle(vis_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                self.display_image(vis_img)
        except Exception as e:
            print(f"ERROR in run_ocr: {e}")
            self.text_output.setText(f"Error: {e}")

    def clear_all(self):
        self.current_image = None
        self.image_label.clear()
        self.text_output.clear()
        self.image_label.roi_rect = None
        self.image_label.start_point = None
        self.image_label.end_point = None
        if self.is_camera_active:
            self.stop_camera()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
