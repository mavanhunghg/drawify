"""
Module phát hiện biên trong ảnh (Edge Detection)
Tham khảo: Chương 5 - Phát hiện biên (Canny, Sobel, Laplacian, LoG)
Mục tiêu: Phát hiện biên tối ưu để tạo sketch rõ nét

Các phương pháp:
1. Canny: Phương pháp phát hiện biên tối ưu (threshold kép, non-maximum suppression)
2. Sobel: Đạo hàm bậc 1 (gradient), nhanh nhưng có thể mờ
3. Laplacian: Đạo hàm bậc 2, phát hiện biên mảnh nhưng nhạy với nhiễu
4. LoG (Laplacian of Gaussian): Kết hợp Gaussian + Laplacian, cân bằng tốt
"""

import cv2
import numpy as np

def detect_edges(image, method='canny', threshold1=50, threshold2=150):
    """
    Phát hiện biên - Phiên bản tối ưu cho sketch rõ nét
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào (xám hoặc màu)
        method (str): 'canny' (KHUYÊN DÙNG), 'sobel', 'laplacian', 'log'
        threshold1 (int): Ngưỡng dưới Canny (mặc định 50 - nhạy hơn)
        threshold2 (int): Ngưỡng trên Canny (mặc định 150)
    
    Returns:
        numpy.ndarray: Ảnh biên rõ nét
    """
    # Chuyển sang xám
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ========== CANNY (KHUYÊN DÙNG - TỐI ƯU NHẤT) ==========
    if method == 'canny':
        # Bước 1: Gaussian Blur để giảm nhiễu (kích thước nhỏ để giữ chi tiết)
        blurred = cv2.GaussianBlur(image, (3, 3), 1.0)
        
        # Bước 2: Canny edge detection
        # Canny = Gaussian + Sobel + Non-maximum suppression + Hysteresis thresholding
        edges = cv2.Canny(blurred, threshold1, threshold2, apertureSize=3, L2gradient=True)
        
        # Bước 3: Dilate để làm dày nét (nét sẽ nhìn rõ hơn)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        return edges

    # ========== SOBEL (Đạo hàm bậc 1 - Gradient) ==========
    elif method == 'sobel':
        # Tính Sobel X và Y (ksize=3 để giữ chi tiết mảnh)
        sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        
        # Tính magnitude (độ lớn gradient)
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)
        
        # Áp dụng threshold để có nét nhị phân
        _, edges = cv2.threshold(magnitude, 50, 255, cv2.THRESH_BINARY)
        
        # Dilate để nét hơn
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        return edges

    # ========== LAPLACIAN (Đạo hàm bậc 2 - Phát hiện biên mảnh) ==========
    elif method == 'laplacian':
        # Laplacian trực tiếp (nhạy, phát hiện biên mảnh)
        laplacian = cv2.Laplacian(image, cv2.CV_64F, ksize=3)
        laplacian = cv2.convertScaleAbs(laplacian)
        
        # Threshold để tạo biên nhị phân
        _, edges = cv2.threshold(laplacian, 30, 255, cv2.THRESH_BINARY)
        
        # Dilate để nét hơn
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        return edges

    # ========== LoG (Laplacian of Gaussian - Cân bằng tốt) ==========
    elif method == 'log':
        # Gaussian Blur trước (sigma=1.0 để không quá mờ)
        blurred = cv2.GaussianBlur(image, (5, 5), 1.0)
        
        # Laplacian trên ảnh đã blur
        log = cv2.Laplacian(blurred, cv2.CV_64F, ksize=5)
        log = cv2.convertScaleAbs(log)
        
        # Threshold
        _, edges = cv2.threshold(log, 15, 255, cv2.THRESH_BINARY)
        
        # Dilate
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        return edges

    else:
        # Mặc định: Canny
        blurred = cv2.GaussianBlur(image, (3, 3), 1.0)
        edges = cv2.Canny(blurred, threshold1, threshold2, apertureSize=3, L2gradient=True)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=1)
        return edges


def detect_edges_advanced(image, method='canny', enhancement='medium'):
    """
    Phát hiện biên NÂNG CAO - Tự động tối ưu hóa
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào
        method (str): 'canny', 'sobel', 'laplacian', 'log'
        enhancement (str): 'light', 'medium', 'strong' - Độ nét
    
    Returns:
        numpy.ndarray: Ảnh biên tối ưu
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Cấu hình theo mức độ nét
    config = {
        'light': {'threshold1': 100, 'threshold2': 200, 'dilate': 0},
        'medium': {'threshold1': 50, 'threshold2': 150, 'dilate': 1},
        'strong': {'threshold1': 30, 'threshold2': 100, 'dilate': 2}
    }
    
    cfg = config.get(enhancement, config['medium'])
    
    if method == 'canny':
        blurred = cv2.GaussianBlur(image, (3, 3), 1.0)
        edges = cv2.Canny(blurred, cfg['threshold1'], cfg['threshold2'], apertureSize=3, L2gradient=True)
    elif method == 'sobel':
        sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)
        _, edges = cv2.threshold(magnitude, cfg['threshold1']//2, 255, cv2.THRESH_BINARY)
    elif method == 'laplacian':
        laplacian = cv2.Laplacian(image, cv2.CV_64F, ksize=3)
        laplacian = cv2.convertScaleAbs(laplacian)
        _, edges = cv2.threshold(laplacian, 20, 255, cv2.THRESH_BINARY)
    else:  # log
        blurred = cv2.GaussianBlur(image, (5, 5), 1.0)
        log = cv2.Laplacian(blurred, cv2.CV_64F, ksize=5)
        log = cv2.convertScaleAbs(log)
        _, edges = cv2.threshold(log, 15, 255, cv2.THRESH_BINARY)

    # Dilate theo mức độ nét
    if cfg['dilate'] > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=cfg['dilate'])

    return edges
