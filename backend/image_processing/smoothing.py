"""
Module làm mịn ảnh (Image Smoothing)
Người thực hiện: Hiến (Người 1 - Preprocessing)

Sử dụng:
- Gaussian Blur: Làm mịn cơ bản
- Bilateral Filter: Làm mịn nhưng giữ biên (edge-preserving) - TỐT cho sketch
"""

import cv2
import numpy as np


def apply_gaussian_blur(image, kernel_size=(5, 5), sigma=0):
    """
    Làm mịn ảnh bằng Gaussian Blur
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào (grayscale hoặc color)
        kernel_size (tuple): Kích thước kernel (phải là số lẻ)
        sigma (float): Độ lệch chuẩn, 0 = tự động tính
    
    Returns:
        numpy.ndarray: Ảnh đã làm mịn
    """
    # Đảm bảo kernel_size là số lẻ
    ksize = (kernel_size[0] if kernel_size[0] % 2 == 1 else kernel_size[0] + 1,
             kernel_size[1] if kernel_size[1] % 2 == 1 else kernel_size[1] + 1)
    
    smoothed = cv2.GaussianBlur(image, ksize, sigma)
    return smoothed


def apply_bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
    """
    Làm mịn ảnh bằng Bilateral Filter - GIỮ BIÊN
    ⭐ ĐÂY LÀ KỸ THUẬT TỐT NHẤT cho bài tập này (đề nghị dùng)
    
    Bilateral filter làm mịn nhiễu nhưng vẫn giữ sắc nét các cạnh/biên
    → Rất tốt cho việc tạo hiệu ứng vẽ tay
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào (grayscale hoặc color)
        d (int): Đường kính vùng lọc (neighbor pixels)
        sigma_color (float): Bộ lọc trong không gian màu
        sigma_space (float): Bộ lọc trong không gian tọa độ
    
    Returns:
        numpy.ndarray: Ảnh đã làm mịn (edge-preserved)
    """
    smoothed = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
    return smoothed


def apply_median_blur(image, kernel_size=5):
    """
    Làm mịn ảnh bằng Median Blur - Loại bỏ nhiễu muối tiêu
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào
        kernel_size (int): Kích thước kernel (phải là số lẻ)
    
    Returns:
        numpy.ndarray: Ảnh đã làm mịn
    """
    ksize = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    smoothed = cv2.medianBlur(image, ksize)
    return smoothed


def preprocess_for_sketch(image, method='bilateral', intensity='medium'):
    """
    Làm mịn ảnh tối ưu cho việc tạo sketch
    Đây là hàm CHÍNH mà bạn sẽ dùng trong API
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào (grayscale)
        method (str): 'bilateral' (khuyên dùng), 'gaussian', hoặc 'median'
        intensity (str): 'light', 'medium', 'strong'
    
    Returns:
        numpy.ndarray: Ảnh đã làm mịn, sẵn sàng cho edge detection
    """
    # Cấu hình tham số theo intensity
    params = {
        'light': {
            'gaussian_kernel': (3, 3),
            'bilateral_d': 5,
            'bilateral_sigma': 50,
            'median_kernel': 3
        },
        'medium': {
            'gaussian_kernel': (5, 5),
            'bilateral_d': 9,
            'bilateral_sigma': 75,
            'median_kernel': 5
        },
        'strong': {
            'gaussian_kernel': (7, 7),
            'bilateral_d': 15,
            'bilateral_sigma': 100,
            'median_kernel': 7
        }
    }
    
    p = params.get(intensity, params['medium'])
    
    if method == 'bilateral':
        # ⭐ KHUYÊN DÙNG - giữ biên tốt nhất
        return apply_bilateral_filter(
            image, 
            d=p['bilateral_d'],
            sigma_color=p['bilateral_sigma'],
            sigma_space=p['bilateral_sigma']
        )
    
    elif method == 'gaussian':
        return apply_gaussian_blur(image, kernel_size=p['gaussian_kernel'])
    
    elif method == 'median':
        return apply_median_blur(image, kernel_size=p['median_kernel'])
    
    else:
        # Mặc định: bilateral
        return apply_bilateral_filter(image, d=p['bilateral_d'], 
                                      sigma_color=p['bilateral_sigma'],
                                      sigma_space=p['bilateral_sigma'])


# Hàm test độc lập
if __name__ == "__main__":
    """
    Test module độc lập - không cần người 2
    """
    print("=== Test Smoothing Module ===")
    
    # Tạo ảnh test với nhiễu
    test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    print(f"Ảnh gốc shape: {test_image.shape}")
    print(f"Giá trị pixel - min: {test_image.min()}, max: {test_image.max()}")
    
    # Test Gaussian Blur
    gaussian = apply_gaussian_blur(test_image)
    print(f"\n✅ Gaussian Blur - shape: {gaussian.shape}")
    
    # Test Bilateral Filter
    bilateral = apply_bilateral_filter(test_image)
    print(f"✅ Bilateral Filter - shape: {bilateral.shape}")
    
    # Test Median Blur
    median = apply_median_blur(test_image)
    print(f"✅ Median Blur - shape: {median.shape}")
    
    # Test hàm chính
    print("\n=== Test Hàm Chính (preprocess_for_sketch) ===")
    for intensity in ['light', 'medium', 'strong']:
        result = preprocess_for_sketch(test_image, method='bilateral', intensity=intensity)
        print(f"✅ Bilateral {intensity}: shape {result.shape}")
    
    print("\n✅ Smoothing module hoạt động tốt!")
