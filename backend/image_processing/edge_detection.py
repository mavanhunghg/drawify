
import numpy as np
from scipy import ndimage


def sobel_edge_detection(image):
    sobel_x = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]], dtype=np.float64)
    
    sobel_y = np.array([[-1, -2, -1],
                        [ 0,  0,  0],
                        [ 1,  2,  1]], dtype=np.float64)
    

    image_float = image.astype(np.float64)
    grad_x = ndimage.convolve(image_float, sobel_x)
    grad_y = ndimage.convolve(image_float, sobel_y)

    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    magnitude = np.clip(magnitude, 0, 255)
    return magnitude.astype(np.uint8)


def laplacian_edge_detection(image):

    laplacian_kernel = np.array([[0,  1, 0],
                                 [1, -4, 1],
                                 [0,  1, 0]], dtype=np.float64)
    
    image_float = image.astype(np.float64)
    laplacian = ndimage.convolve(image_float, laplacian_kernel)
    laplacian = np.abs(laplacian)
    laplacian = np.clip(laplacian, 0, 255)
    return laplacian.astype(np.uint8)


def canny_edge_detection(image, low_threshold=50, high_threshold=150):
    rows, cols = image.shape[:2]
    
    # 1. Gaussian smoothing
    gaussian_kernel = np.array([[1, 2, 1],
                                [2, 4, 2],
                                [1, 2, 1]], dtype=np.float64) / 16
    smoothed = ndimage.convolve(image.astype(np.float64), gaussian_kernel)
    
    # 2. Sobel gradient
    sobel_x = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]], dtype=np.float64)
    sobel_y = np.array([[-1, -2, -1],
                        [ 0,  0,  0],
                        [ 1,  2,  1]], dtype=np.float64)
    
    grad_x = ndimage.convolve(smoothed, sobel_x)
    grad_y = ndimage.convolve(smoothed, sobel_y)
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    
    # Tính góc gradient (radian → degree), chuẩn hóa về [0, 180)
    angle = np.arctan2(grad_y, grad_x) * 180.0 / np.pi
    angle[angle < 0] += 180
    
    # 3. Non-Maximum Suppression (NMS)
    
    nms = np.zeros_like(magnitude)
    
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            q, r = 255, 255  
            
            # Xác định 2 pixel lân cận theo hướng gradient
            # 0° (ngang): so sánh trái-phải
            if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                q = magnitude[i, j + 1]
                r = magnitude[i, j - 1]
            # 45° (chéo): so sánh trên-phải và dưới-trái
            elif 22.5 <= angle[i, j] < 67.5:
                q = magnitude[i - 1, j + 1]
                r = magnitude[i + 1, j - 1]
            # 90° (dọc): so sánh trên-dưới
            elif 67.5 <= angle[i, j] < 112.5:
                q = magnitude[i - 1, j]
                r = magnitude[i + 1, j]
            # 135° (chéo): so sánh trên-trái và dưới-phải
            elif 112.5 <= angle[i, j] < 157.5:
                q = magnitude[i - 1, j - 1]
                r = magnitude[i + 1, j + 1]
            
            # Giữ lại nếu là cực đại cục bộ
            if magnitude[i, j] >= q and magnitude[i, j] >= r:
                nms[i, j] = magnitude[i, j]
            else:
                nms[i, j] = 0
    
    # 4. Double Threshold
    strong_val = 255
    weak_val = 75  # giá trị tạm cho weak edges
    
    strong_edges = nms >= high_threshold
    weak_edges = (nms >= low_threshold) & (nms < high_threshold)
    
    result = np.zeros_like(nms, dtype=np.uint8)
    result[strong_edges] = strong_val
    result[weak_edges] = weak_val
    
    # 5. Hysteresis - Edge tracking by connectivity
    # Weak edge chỉ được giữ nếu kết nối với strong edge
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if result[i, j] == weak_val:
                # Kiểm tra 8-connectivity với strong edge
                neighborhood = result[i-1:i+2, j-1:j+2]
                if np.any(neighborhood == strong_val):
                    result[i, j] = strong_val
                else:
                    result[i, j] = 0
    
    return result


def detect_edges(image, method='canny', low_threshold=50, high_threshold=150):
    if method == 'canny':
        return canny_edge_detection(image, low_threshold, high_threshold)
    elif method == 'sobel':
        return sobel_edge_detection(image)
    elif method == 'laplacian':
        return laplacian_edge_detection(image)
    else:
        return canny_edge_detection(image, low_threshold, high_threshold)


