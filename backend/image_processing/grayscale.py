"""
Module chuyển đổi ảnh màu sang ảnh xám (Grayscale Conversion)
Người thực hiện: Hiến (Người 1 - Preprocessing)
KHÔNG DÙNG OPENCV - Code thủ công
"""

import numpy as np


def convert_to_grayscale(image):
    """
    Chuyển đổi ảnh màu sang ảnh xám - CODE THỦ CÔNG
    
    Công thức weighted average (giống OpenCV):
    Gray = 0.299*R + 0.587*G + 0.114*B
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào (RGB hoặc BGR format)
    
    Returns:
        numpy.ndarray: Ảnh xám (2D array, uint8)
    """
    # Kiểm tra nếu ảnh đã là grayscale
    if len(image.shape) == 2:
        return image.astype(np.uint8)
    
    # Đảm bảo dtype là float để tính toán chính xác
    image = image.astype(np.float32)
    
    # Nếu ảnh có 3 kênh màu (RGB hoặc BGR)
    if len(image.shape) == 3 and image.shape[2] == 3:
        # Công thức weighted average (ITU-R BT.601) - CHÍNH XÁC 100%
        # Input từ PIL là RGB format: [R, G, B]
        # Công thức: Gray = 0.299*R + 0.587*G + 0.114*B
        r = image[:, :, 0].astype(np.float32)
        g = image[:, :, 1].astype(np.float32)
        b = image[:, :, 2].astype(np.float32)
        gray = 0.299 * r + 0.587 * g + 0.114 * b
        return np.clip(gray, 0, 255).astype(np.uint8)
    
    # Nếu ảnh có 4 kênh (RGBA) - loại bỏ alpha channel
    if len(image.shape) == 3 and image.shape[2] == 4:
        # Chỉ lấy 3 kênh đầu (RGB), bỏ alpha
        rgb = image[:, :, :3]
        gray = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
        return np.clip(gray, 0, 255).astype(np.uint8)
    
    return image.astype(np.uint8)


def convert_to_grayscale_custom(image, method='weighted'):
    """
    Chuyển đổi ảnh sang xám với nhiều phương pháp khác nhau
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào
        method (str): Phương pháp chuyển đổi
            - 'weighted': Trung bình có trọng số (mặc định, giống OpenCV)
            - 'average': Trung bình đơn giản (R+G+B)/3
            - 'luminosity': Công thức ITU-R BT.601 (giống weighted)
    
    Returns:
        numpy.ndarray: Ảnh xám
    """
    if len(image.shape) == 2:
        return image.astype(np.uint8)
    
    image = image.astype(np.float32)
    
    if len(image.shape) == 3 and image.shape[2] >= 3:
        r = image[:, :, 0]
        g = image[:, :, 1]
        b = image[:, :, 2]
        
        if method == 'average':
            # Trung bình đơn giản
            gray = (r + g + b) / 3.0
        elif method == 'luminosity':
            # Công thức ITU-R BT.601 (giống weighted)
            gray = 0.299 * r + 0.587 * g + 0.114 * b
        else:  # 'weighted' - default
            # Công thức weighted average (giống OpenCV)
            gray = 0.299 * r + 0.587 * g + 0.114 * b
        
        return np.clip(gray, 0, 255).astype(np.uint8)
    
    return image.astype(np.uint8)


# Hàm test độc lập
if __name__ == "__main__":
    """
    Test module độc lập - không cần người 2
    """
    print("=== Test Grayscale Module (KHÔNG DÙNG OPENCV) ===")
    
    # Tạo ảnh test màu đơn giản
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    print(f"Ảnh gốc shape: {test_image.shape}")
    print(f"Ảnh gốc dtype: {test_image.dtype}")
    
    # Test chuyển đổi grayscale
    gray = convert_to_grayscale(test_image)
    print(f"Ảnh xám shape: {gray.shape}")
    print(f"Ảnh xám dtype: {gray.dtype}")
    print(f"Giá trị pixel min: {gray.min()}, max: {gray.max()}")
    
    # Test các phương pháp khác
    gray_avg = convert_to_grayscale_custom(test_image, 'average')
    gray_lum = convert_to_grayscale_custom(test_image, 'luminosity')
    print(f"Average method shape: {gray_avg.shape}")
    print(f"Luminosity method shape: {gray_lum.shape}")
    
    print("✅ Grayscale module hoạt động tốt!")

