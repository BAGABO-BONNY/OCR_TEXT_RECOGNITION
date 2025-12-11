# Printed Text Scanner GUI

A Python-based GUI application for scanning and extracting text from images or live camera feed using Tesseract OCR.

## Features
- **Image Loading**: Support for `.png`, `.jpg`, `.jpeg`, `.bmp` images.
- **Live Camera Feed**: Capture images directly from your webcam.
- **Region of Interest (ROI)**: Select specific areas of the image to scan.
- **OCR Integration**: Uses Tesseract OCR to extract text.
- **Preprocessing**: Automatically applies grayscale and thresholding for better accuracy.
- **Overlay**: Visualizes detected text regions on the image.

## Prerequisites

### System Dependencies
You must have **Tesseract OCR** installed on your system.

**Linux (Debian/Ubuntu/Kali):**
```bash
sudo apt update
sudo apt install tesseract-ocr
# Optional: Install language packs (e.g., for English)
sudo apt install tesseract-ocr-eng
```

**Windows:**
1. Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install it and add the installation path (e.g., `C:\Program Files\Tesseract-OCR`) to your System PATH environment variable.

## Installation

1.  **Clone or Download** this repository.
2.  **Navigate to the project directory**:
    ```bash
    cd /path/to/printend_text_gui
    ```
3.  **Create a Virtual Environment** (Recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the Application**:
    ```bash
    python main.py
    ```
    *Note: If you experience crashes on Linux/Wayland, try:*
    ```bash
    QT_QPA_PLATFORM=xcb python main.py
    ```

2.  **How to Scan**:
    - **Load Image**: Click "Load Image" to open a file.
    - **Camera**: Click "Start Camera" -> "Capture" to take a photo.
    - **Select Text**: Click and drag on the image to draw a red box around the text.
    - **Run OCR**: Click "Run OCR". The extracted text will appear in the right panel.

## Troubleshooting

-   **"Tesseract Not Found" Error**: Ensure Tesseract is installed and in your system PATH.
-   **Empty Result**: Try selecting a clearer region. The app automatically pre-processes images, but very blurry text may still fail.
-   **Crash on Start**: Common on some Linux distros. Use the `QT_QPA_PLATFORM=xcb` environment variable.
