"""
Module chuyển đổi ảnh màu sang ảnh xám (Grayscale Conversion)
Người thực hiện: Hiến (Người 1 - Preprocessing)
"""

import cv2
import numpy as np


def convert_to_grayscale(image):
    """
    Chuyển đổi ảnh màu sang ảnh xám
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào (RGB hoặc BGR)
    
    Returns:
        numpy.ndarray: Ảnh xám
    """
    # Kiểm tra nếu ảnh đã là grayscale
    if len(image.shape) == 2:
        return image
    
    # Nếu ảnh có 3 kênh màu (RGB/BGR)
    if len(image.shape) == 3 and image.shape[2] == 3:
        # Sử dụng công thức weighted average của OpenCV
        # Gray = 0.299*R + 0.587*G + 0.114*B
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray_image
    
    # Nếu ảnh có 4 kênh (RGBA/BGRA) - loại bỏ alpha channel
    if len(image.shape) == 3 and image.shape[2] == 4:
        # Chuyển BGRA -> BGR trước, sau đó -> Gray
        bgr_image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        return gray_image
    
    return image


def convert_to_grayscale_custom(image, method='weighted'):
    """
    Chuyển đổi ảnh sang xám với nhiều phương pháp khác nhau
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào
        method (str): Phương pháp chuyển đổi
            - 'weighted': Trung bình có trọng số (mặc định OpenCV)
            - 'average': Trung bình đơn giản
            - 'luminosity': Công thức ITU-R BT.601
    
    Returns:
        numpy.ndarray: Ảnh xám
    """
    if len(image.shape) == 2:
        return image
    
    if len(image.shape) == 3 and image.shape[2] >= 3:
        # OpenCV lưu ảnh dưới dạng BGR
        b, g, r = image[:,:,0], image[:,:,1], image[:,:,2]
        
        if method == 'average':
            # Trung bình đơn giản
            gray = (b.astype(np.float32) + g.astype(np.float32) + r.astype(np.float32)) / 3
            return gray.astype(np.uint8)
        
        elif method == 'luminosity':
            # Công thức ITU-R BT.601 (gần giống OpenCV)
            gray = 0.114 * b + 0.587 * g + 0.299 * r
            return gray.astype(np.uint8)
        
        else:  # 'weighted' - default
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    return image


# Hàm test độc lập
if __name__ == "__main__":
    """
    Test module độc lập - không cần người 2
    """
    print("=== Test Grayscale Module ===")
    
    # Tạo ảnh test màu đơn giản
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    print(f"Ảnh gốc shape: {test_image.shape}")
    
    # Test chuyển đổi grayscale
    gray = convert_to_grayscale(test_image)
    print(f"Ảnh xám shape: {gray.shape}")
    print(f"Giá trị pixel min: {gray.min()}, max: {gray.max()}")
    
    # Test các phương pháp khác
    gray_avg = convert_to_grayscale_custom(test_image, 'average')
    gray_lum = convert_to_grayscale_custom(test_image, 'luminosity')
    print(f"Average method shape: {gray_avg.shape}")
    print(f"Luminosity method shape: {gray_lum.shape}")
    
    print("✅ Grayscale module hoạt động tốt!")
