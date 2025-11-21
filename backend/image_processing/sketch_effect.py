"""
Module tạo hiệu ứng sketch/tranh vẽ tay
Tham khảo: Chương 5 - Phát hiện biên + Xử lý hình thái
Mục tiêu: Sketch rõ nét chi tiết cao
"""

import cv2
import numpy as np
from .grayscale import convert_to_grayscale
from .smoothing import preprocess_for_sketch
from .edge_detect import detect_edges, detect_edges_advanced

def sketch_effect(image, smoothing_method='bilateral', intensity='medium', edge_method='canny'):
    """
    Tạo hiệu ứng sketch từ ảnh đầu vào
    
    Pipeline:
    1. Chuyển xám (Grayscale)
    2. Làm mịn (Bilateral/Gaussian/Median) - bảo toàn biên
    3. Phát hiện biên (Canny/Sobel/Laplacian)
    4. Đảo màu để tạo nét vẽ đen
    5. Tăng nét bằng CLAHE
    """
    # Bước 1: Grayscale
    gray = convert_to_grayscale(image)
    
    # Bước 2: Làm mịn (bilateral tốt nhất - giữ biên)
    smooth = preprocess_for_sketch(gray, method=smoothing_method, intensity=intensity)
    
    # Bước 3: Phát hiện biên (threshold tối ưu = nhạy hơn để chi tiết hơn)
    # Canny với threshold thấp sẽ bắt được chi tiết mảnh
    edges = detect_edges(smooth, method=edge_method, threshold1=50, threshold2=150)
    
    # Bước 4: Đảo màu - tạo nét đen trên nền trắng
    sketch = cv2.bitwise_not(edges)
    
    # Bước 5: TĂNG NẾT CỰC ĐẠI bằng CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    sketch = clahe.apply(sketch)
    
    # Bước 6: Tăng tương phản nhẹ (làm nét biên)
    alpha = 1.2  # Tăng tương phản
    beta = -10   # Giảm độ sáng để nét hơn
    sketch = cv2.convertScaleAbs(cv2.Mat(sketch.astype(np.float32) * alpha + beta))
    
    return sketch


def sketch_effect_enhanced(image, smoothing_method='bilateral', intensity='medium', 
                           edge_method='canny', sharpness='medium'):
    """
    Sketch NÂNG CAO - Chi tiết cực kỳ cao
    
    Args:
        image: Ảnh đầu vào
        smoothing_method: 'bilateral', 'gaussian', 'median'
        intensity: 'light', 'medium', 'strong'
        edge_method: 'canny', 'sobel', 'laplacian', 'log'
        sharpness: 'light', 'medium', 'strong' - Độ nét chi tiết
    """
    # Grayscale
    gray = convert_to_grayscale(image)
    
    # Làm mịn
    smooth = preprocess_for_sketch(gray, method=smoothing_method, intensity=intensity)
    
    # Phát hiện biên nâng cao
    edges = detect_edges_advanced(smooth, method=edge_method, enhancement=sharpness)
    
    # Đảo màu
    sketch = cv2.bitwise_not(edges)
    
    # ========== TĂNG NẾT CỰC ĐẠI ==========
    
    # 1. CLAHE - Tăng tương phản thích ứng
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(6, 6))
    sketch = clahe.apply(sketch)
    
    # 2. Morphological operations - Làm sắc nét biên
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    sketch = cv2.morphologyEx(sketch, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    # 3. Unsharp mask - Làm sắc nét chi tiết
    # Cách 1: Blur nhẹ + trừ từ original = unsharpen
    blurred = cv2.GaussianBlur(sketch, (3, 3), 1.0)
    sketch = cv2.addWeighted(sketch, 1.5, blurred, -0.5, 0)
    sketch = np.clip(sketch, 0, 255).astype(np.uint8)
    
    # 4. Histogram equalization - Tăng nét overall
    sketch = cv2.equalizeHist(sketch)
    
    # 5. Thresholding cuối cùng - Làm nét nhị phân
    _, sketch = cv2.threshold(sketch, 127, 255, cv2.THRESH_BINARY)
    
    return sketch


def sketch_effect_maximum_detail(image, smoothing_method='bilateral', intensity='medium'):
    """
    Sketch CHI TIẾT CỰC ĐẠI - Dùng khi muốn nét nhất
    Kết hợp ALL kỹ thuật tăng nét
    """
    # Grayscale
    gray = convert_to_grayscale(image)
    
    # Làm mịn nhẹ (bilateral tốt nhất)
    smooth = preprocess_for_sketch(gray, method=smoothing_method, intensity=intensity)
    
    # Phát hiện biên siêu nhạy (threshold rất thấp)
    blurred = cv2.GaussianBlur(smooth, (3, 3), 1.0)
    edges = cv2.Canny(blurred, 30, 100, apertureSize=3, L2gradient=True)
    
    # Morphological enhancement
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    # Đảo màu
    sketch = cv2.bitwise_not(edges)
    
    # Các lớp tăng nét
    # Lớp 1: CLAHE
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4, 4))
    sketch = clahe.apply(sketch)
    
    # Lớp 2: Unsharp mask mạnh
    blurred_sketch = cv2.GaussianBlur(sketch, (3, 3), 1.0)
    sketch = cv2.addWeighted(sketch, 2.0, blurred_sketch, -1.0, 0)
    sketch = np.clip(sketch, 0, 255).astype(np.uint8)
    
    # Lớp 3: Morphological sharpening
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
    sketch = cv2.morphologyEx(sketch, cv2.MORPH_CLOSE, kernel2, iterations=1)
    
    # Lớp 4: Histogram equalization
    sketch = cv2.equalizeHist(sketch)
    
    # Lớp 5: Adaptive threshold (tạo nét tối đa)
    sketch = cv2.adaptiveThreshold(sketch, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY, 11, 2)
    
    return sketch
