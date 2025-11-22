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

def calculate_adaptive_threshold_median(image):
    """
    Phương pháp 1: MEDIAN-based (robust với outliers)
    """
    v = np.median(image)
    sigma = 0.33
    low_threshold = int(max(0, (1.0 - sigma) * v))
    high_threshold = int(min(255, (1.0 + sigma) * v))
    if high_threshold < low_threshold * 2:
        high_threshold = low_threshold * 2
    return low_threshold, high_threshold

def calculate_adaptive_threshold_otsu(image):
    """
    Phương pháp 2: OTSU's Method (tối ưu cho bimodal histogram)
    """
    otsu_threshold, _ = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    low_threshold = int(otsu_threshold * 0.5)
    high_threshold = int(otsu_threshold * 1.0)
    low_threshold = max(10, min(low_threshold, 100))
    high_threshold = max(30, min(high_threshold, 200))
    return low_threshold, high_threshold

def calculate_adaptive_threshold_hybrid(image):
    """
    Phương pháp 3: HYBRID (kết hợp Otsu + Median)
    - Dùng Otsu nếu histogram rõ ràng (high standard deviation)
    - Dùng Median nếu histogram phân tán (low standard deviation)
    """
    # Tính histogram và standard deviation
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    hist = hist.flatten() / hist.sum()
    std = np.sqrt(np.sum((np.arange(256) - np.mean(image))**2 * hist))
    
    # Nếu std cao (>50) -> histogram rõ ràng -> dùng Otsu
    # Nếu std thấp (<50) -> histogram phân tán -> dùng Median
    if std > 50:
        return calculate_adaptive_threshold_otsu(image)
    else:
        return calculate_adaptive_threshold_median(image)

def calculate_adaptive_threshold(image, method='otsu'):
    """
    Tính threshold tự động - HỖ TRỢ 3 PHƯƠNG PHÁP
    
    Args:
        image: Ảnh grayscale
        method: 'otsu' (default - TỐT NHẤT), 'median', 'hybrid'
        
    Returns:
        tuple: (low_threshold, high_threshold)
    """
    if method == 'median':
        return calculate_adaptive_threshold_median(image)
    elif method == 'hybrid':
        return calculate_adaptive_threshold_hybrid(image)
    else:  # otsu (default - best performance)
        return calculate_adaptive_threshold_otsu(image)

def detect_edges(image, method='canny', threshold1=None, threshold2=None):
    """
    Phát hiện biên - ADAPTIVE THRESHOLD tự động
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào (xám hoặc màu)
        method (str): 'canny' (KHUYÊN DÙNG), 'sobel', 'laplacian', 'log'
        threshold1 (int): Ngưỡng dưới (None = tự động tính)
        threshold2 (int): Ngưỡng trên (None = tự động tính)
    
    Returns:
        numpy.ndarray: Ảnh biên rõ nét
    """
    # Chuyển sang xám
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # TỰ ĐỘNG TÍNH THRESHOLD nếu không được cung cấp
    if threshold1 is None or threshold2 is None:
        auto_low, auto_high = calculate_adaptive_threshold(image)
        threshold1 = auto_low if threshold1 is None else threshold1
        threshold2 = auto_high if threshold2 is None else threshold2

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
        # Bước 1: Làm mịn nhẹ để giảm nhiễu
        blurred = cv2.GaussianBlur(image, (3, 3), 0.5)
        
        # Bước 2: Laplacian (ksize=5 để ổn định hơn)
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F, ksize=5)
        laplacian = cv2.convertScaleAbs(laplacian)
        
        # Bước 3: Adaptive threshold để tự động điều chỉnh
        # THRESH_BINARY + OTSU để tự động tìm ngưỡng tối ưu
        _, edges = cv2.threshold(laplacian, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Bước 4: Morphology để làm sạch nhiễu nhỏ
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)  # Đóng lỗ hổng
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        return edges

    # ========== LoG (Laplacian of Gaussian - Cân bằng tốt) ==========
    elif method == 'log':
        # Bước 1: Gaussian Blur với sigma lớn hơn để giảm nhiễu tốt
        blurred = cv2.GaussianBlur(image, (5, 5), 1.4)
        
        # Bước 2: Laplacian trên ảnh đã blur
        log = cv2.Laplacian(blurred, cv2.CV_64F, ksize=5)
        log = cv2.convertScaleAbs(log)
        
        # Bước 3: Adaptive threshold (OTSU) thay vì threshold cố định
        _, edges = cv2.threshold(log, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Bước 4: Morphology để làm sạch và nét hơn
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)  # Đóng lỗ hổng nhỏ
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
        blurred = cv2.GaussianBlur(image, (3, 3), 0.5)
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F, ksize=5)
        laplacian = cv2.convertScaleAbs(laplacian)
        _, edges = cv2.threshold(laplacian, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    else:  # log
        blurred = cv2.GaussianBlur(image, (5, 5), 1.4)
        log = cv2.Laplacian(blurred, cv2.CV_64F, ksize=5)
        log = cv2.convertScaleAbs(log)
        _, edges = cv2.threshold(log, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Dilate theo mức độ nét
    if cfg['dilate'] > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=cfg['dilate'])

    return edges
