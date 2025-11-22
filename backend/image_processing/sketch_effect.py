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

def sketch_effect(image, smoothing_method='bilateral', intensity='medium', edge_method='canny', threshold_method='otsu'):
    """
    Tạo hiệu ứng sketch từ ảnh đầu vào - CHẤT LƯỢNG TỐI ĐA
    
    Args:
        threshold_method: 'otsu' (default - TỐT NHẤT), 'median', 'hybrid'
    
    Pipeline tối ưu:
    1. Grayscale
    2. Làm mịn (bilateral tốt nhất - giữ biên)
    3. Phát hiện biên MULTI-SCALE (nhiều threshold)
    4. Đảo màu + Tăng nét CLAHE
    5. Post-processing làm sạch
    """
    # Bước 1: Grayscale
    gray = convert_to_grayscale(image)
    
    # Bước 2: Làm mịn NÂNG CAO
    # Bilateral với d lớn hơn để mịn hơn nhưng vẫn giữ biên
    if smoothing_method == 'bilateral':
        # Tăng d từ 7 → 9 và sigma để mịn hơn
        smooth = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    else:
        smooth = preprocess_for_sketch(gray, method=smoothing_method, intensity=intensity)
    
    # Bước 3: PHÁT HIỆN BIÊN MULTI-SCALE (Kỹ thuật nâng cao)
    # Kết hợp nhiều threshold để bắt cả chi tiết mảnh VÀ nét chính
    
    if edge_method in ['canny', 'sobel']:
        # ADAPTIVE THRESHOLD - Tự động tính ngưỡng tối ưu cho từng ảnh
        from .edge_detect import calculate_adaptive_threshold
        base_low, base_high = calculate_adaptive_threshold(smooth, method=threshold_method)
        
        # MULTI-SCALE: Phát hiện ở 3 mức độ dựa trên adaptive threshold
        # Scale 1: Chi tiết CỰC mảnh (0.4x base)
        edges_ultra_fine = detect_edges(smooth, method=edge_method, 
                                       threshold1=int(base_low*0.4), threshold2=int(base_high*0.4))
        # Scale 2: Chi tiết vừa (0.8x base)
        edges_fine = detect_edges(smooth, method=edge_method,
                                 threshold1=int(base_low*0.8), threshold2=int(base_high*0.8))
        # Scale 3: Nét chính (1.3x base)
        edges_coarse = detect_edges(smooth, method=edge_method,
                                   threshold1=int(base_low*1.3), threshold2=int(base_high*1.3))
        
        # Kết hợp 3 scales: Tăng trọng số cho chi tiết mảnh
        edges = cv2.addWeighted(edges_coarse, 0.4, edges_fine, 0.35, 0)
        edges = cv2.add(edges, cv2.multiply(edges_ultra_fine, np.array([0.25])))
        _, edges = cv2.threshold(edges, 40, 255, cv2.THRESH_BINARY)
        
        # Làm dày nét nhẹ để rõ hơn
        kernel_thicken = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.dilate(edges, kernel_thicken, iterations=1)
    else:
        # Laplacian & LoG: Multi-scale nhẹ để tăng chi tiết
        edges_fine = detect_edges(smooth, method=edge_method, threshold1=40, threshold2=120)
        edges_coarse = detect_edges(smooth, method=edge_method, threshold1=50, threshold2=150)
        edges = cv2.addWeighted(edges_fine, 0.6, edges_coarse, 0.4, 0)
        _, edges = cv2.threshold(edges, 50, 255, cv2.THRESH_BINARY)
    
    # Bước 4: Đảo màu
    sketch = cv2.bitwise_not(edges)
    
    # Bước 5: TĂNG NẾT với CLAHE
    clahe = cv2.createCLAHE(clipLimit=4.5, tileGridSize=(8, 8))
    sketch = clahe.apply(sketch)
    
    # Bước 6: POST-PROCESSING - Làm sạch nhiễu nhỏ nhẹ nhàng
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    sketch = cv2.morphologyEx(sketch, cv2.MORPH_OPEN, kernel)
    
    # Bước 7: UNSHARP MASKING nhẹ - Tăng độ sắc nét
    gaussian = cv2.GaussianBlur(sketch, (0, 0), 1.5)
    sketch = cv2.addWeighted(sketch, 1.3, gaussian, -0.3, 0)
    
    # Bước 8: Tăng tương phản vừa phải
    alpha = 1.25  # Tăng tương phản
    beta = -12    # Giảm độ sáng để nét hơn
    sketch = cv2.convertScaleAbs(np.clip(sketch.astype(np.float32) * alpha + beta, 0, 255))
    
    return sketch


def sketch_effect_enhanced(image, smoothing_method='bilateral', intensity='medium', 
                           edge_method='canny', sharpness='medium', threshold_method='otsu'):
    """
    Sketch NÂNG CAO - CHẤT LƯỢNG PROFESSIONAL
    
    Cải tiến:
    - Multi-scale edge detection (bắt cả chi tiết mảnh và nét chính)
    - Adaptive denoising (giảm nhiễu thông minh)
    - Advanced post-processing
    
    Args:
        image: Ảnh đầu vào
        smoothing_method: 'bilateral', 'gaussian', 'median'
        intensity: 'light', 'medium', 'strong'
        edge_method: 'canny', 'sobel', 'laplacian', 'log'
        sharpness: 'light', 'medium', 'strong' - Độ nét chi tiết
    """
    # Bước 1: Grayscale
    gray = convert_to_grayscale(image)
    
    # Bước 2: Làm mịn NÂNG CAO với bilateral tối ưu
    # d=9 là cân bằng tốt - đủ mịn nhưng không làm mất chi tiết
    if smoothing_method == 'bilateral':
        smooth = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    else:
        smooth = preprocess_for_sketch(gray, method=smoothing_method, intensity=intensity)
    
    # Bước 3: MULTI-SCALE EDGE DETECTION với ADAPTIVE THRESHOLD
    if edge_method in ['canny', 'sobel']:
        from .edge_detect import calculate_adaptive_threshold
        base_low, base_high = calculate_adaptive_threshold(smooth, method=threshold_method)
        
        # Scale 1: Chi tiết cực mảnh (0.4x base adaptive)
        edges_ultra_fine = detect_edges(smooth, method=edge_method, 
                                       threshold1=int(base_low*0.4), threshold2=int(base_high*0.4))
        # Scale 2: Chi tiết vừa (0.8x base adaptive)
        edges_fine = detect_edges(smooth, method=edge_method,
                                 threshold1=int(base_low*0.8), threshold2=int(base_high*0.8))
        # Scale 3: Nét chính (1.3x base adaptive)
        edges_coarse = detect_edges(smooth, method=edge_method,
                                   threshold1=int(base_low*1.3), threshold2=int(base_high*1.3))
        
        # Kết hợp 3 scales với trọng số tối ưu
        edges = cv2.addWeighted(edges_coarse, 0.5, edges_fine, 0.35, 0)
        edges = cv2.add(edges, cv2.multiply(edges_ultra_fine, np.array([0.15])))
        _, edges = cv2.threshold(edges, 30, 255, cv2.THRESH_BINARY)
    else:
        # Laplacian/LoG: Multi-scale cũng tốt
        edges_fine = detect_edges(smooth, method=edge_method, threshold1=30, threshold2=100)
        edges_coarse = detect_edges(smooth, method=edge_method, threshold1=60, threshold2=180)
        edges = cv2.addWeighted(edges_coarse, 0.6, edges_fine, 0.4, 0)
        _, edges = cv2.threshold(edges, 50, 255, cv2.THRESH_BINARY)
    
    # Bước 4: Đảo màu
    sketch = cv2.bitwise_not(edges)
    
    # ========== POST-PROCESSING NÂNG CAO ==========
    
    # 1. Loại bỏ nhiễu isolated pixels
    kernel_denoise = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    sketch = cv2.morphologyEx(sketch, cv2.MORPH_OPEN, kernel_denoise)
    
    # 2. CLAHE cực mạnh - Tăng tương phản
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(6, 6))
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
