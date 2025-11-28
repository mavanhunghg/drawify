"""
Module làm mịn ảnh (Image Smoothing)
Người thực hiện: Hiến (Người 1 - Preprocessing)
KHÔNG DÙNG OPENCV - Code thủ công

Sử dụng:
- Gaussian Blur: Làm mịn cơ bản
- Bilateral Filter: Làm mịn nhưng giữ biên (edge-preserving) - TỐT cho sketch
- Median Blur: Loại bỏ nhiễu muối tiêu
"""

import numpy as np
import sys
import os

# Add parent directory to path để import utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.convolution import convolve2d


def create_gaussian_kernel(size, sigma=None):
    """
    Tạo Gaussian kernel 2D
    
    Args:
        size: Kích thước kernel (phải là số lẻ)
        sigma: Độ lệch chuẩn (None = tự động tính)
    
    Returns:
        Gaussian kernel 2D (normalized)
    """
    # Đảm bảo size là số lẻ
    if size % 2 == 0:
        size += 1
    
    # Tính sigma nếu không có
    if sigma is None:
        sigma = size / 6.0
    
    # Tạo kernel
    kernel = np.zeros((size, size), dtype=np.float64)
    center = size // 2
    
    # Công thức Gaussian 2D
    for i in range(size):
        for j in range(size):
            x = i - center
            y = j - center
            kernel[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
    
    # Normalize để tổng = 1
    kernel = kernel / np.sum(kernel)
    
    return kernel


def apply_gaussian_blur(image, kernel_size=(5, 5), sigma=0):
    """
    Làm mịn ảnh bằng Gaussian Blur - CODE THỦ CÔNG
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào (grayscale hoặc color)
        kernel_size (tuple): Kích thước kernel (phải là số lẻ)
        sigma (float): Độ lệch chuẩn, 0 = tự động tính
    
    Returns:
        numpy.ndarray: Ảnh đã làm mịn
    """
    # Đảm bảo kernel_size là số lẻ
    ksize_h = kernel_size[0] if kernel_size[0] % 2 == 1 else kernel_size[0] + 1
    ksize_w = kernel_size[1] if kernel_size[1] % 2 == 1 else kernel_size[1] + 1
    
    # Tính sigma nếu không có
    if sigma == 0:
        sigma = min(ksize_h, ksize_w) / 6.0
    
    # Tạo Gaussian kernel
    kernel = create_gaussian_kernel(max(ksize_h, ksize_w), sigma)
    
    # Convolution
    smoothed = convolve2d(image, kernel, mode='reflect')
    
    # Đảm bảo output là uint8
    if smoothed.dtype != np.uint8:
        smoothed = np.clip(smoothed, 0, 255).astype(np.uint8)
    
    return smoothed


def apply_median_blur(image, kernel_size=5):
    """
    Làm mịn ảnh bằng Median Blur - CODE THỦ CÔNG
    Loại bỏ nhiễu muối tiêu
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào
        kernel_size (int): Kích thước kernel (phải là số lẻ)
    
    Returns:
        numpy.ndarray: Ảnh đã làm mịn
    """
    ksize = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    radius = ksize // 2
    
    # Padding
    if len(image.shape) == 2:
        h, w = image.shape
        padded = np.pad(image, radius, mode='reflect')
        output = np.zeros_like(image, dtype=np.uint8)
        
        for i in range(h):
            for j in range(w):
                window = padded[i:i+ksize, j:j+ksize]
                output[i, j] = np.median(window)
        
        return output
    
    elif len(image.shape) == 3:
        h, w, c = image.shape
        padded = np.pad(image, ((radius, radius), (radius, radius), (0, 0)), mode='reflect')
        output = np.zeros_like(image, dtype=np.uint8)
        
        for channel in range(c):
            for i in range(h):
                for j in range(w):
                    window = padded[i:i+ksize, j:j+ksize, channel]
                    output[i, j, channel] = np.median(window)
        
        return output
    
    return image


def apply_bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
    """
    Làm mịn ảnh bằng Bilateral Filter - CODE THỦ CÔNG
    ⭐ ĐÂY LÀ KỸ THUẬT TỐT NHẤT cho bài tập này (đề nghị dùng)
    
    Bilateral filter làm mịn nhiễu nhưng vẫn giữ sắc nét các cạnh/biên
    → Rất tốt cho việc tạo hiệu ứng vẽ tay
    
    Thuật toán:
    1. Với mỗi pixel, xét các pixel lân cận trong radius d
    2. Tính weight dựa trên:
       - Khoảng cách không gian (spatial): exp(-||p-q||²/(2σs²))
       - Khác biệt màu (color): exp(-||I(p)-I(q)||²/(2σr²))
    3. Weighted average với 2 weights trên
    
    Args:
        image (numpy.ndarray): Ảnh đầu vào (grayscale hoặc color)
        d (int): Đường kính vùng lọc (neighbor pixels)
        sigma_color (float): Bộ lọc trong không gian màu
        sigma_space (float): Bộ lọc trong không gian tọa độ
    
    Returns:
        numpy.ndarray: Ảnh đã làm mịn (edge-preserved)
    """
    # Đảm bảo d là số lẻ
    if d % 2 == 0:
        d += 1
    
    radius = d // 2
    
    # Chuyển sang float để tính toán
    image_float = image.astype(np.float64)
    
    # Padding
    if len(image.shape) == 2:
        # Grayscale
        h, w = image.shape
        padded = np.pad(image_float, radius, mode='reflect')
        output = np.zeros_like(image_float)
        
        # Pre-compute spatial weights (chỉ phụ thuộc vào vị trí)
        spatial_weights = np.zeros((d, d), dtype=np.float64)
        for i in range(d):
            for j in range(d):
                x = i - radius
                y = j - radius
                spatial_weights[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma_space**2))
        
        # Apply bilateral filter
        for i in range(h):
            for j in range(w):
                center_value = padded[i + radius, j + radius]
                
                # Lấy window
                window = padded[i:i+d, j:j+d]
                
                # Tính color weights
                color_diff = window - center_value
                color_weights = np.exp(-(color_diff**2) / (2 * sigma_color**2))
                
                # Kết hợp weights
                weights = spatial_weights * color_weights
                
                # Weighted average
                output[i, j] = np.sum(weights * window) / np.sum(weights)
        
        return np.clip(output, 0, 255).astype(np.uint8)
    
    elif len(image.shape) == 3:
        # Color image
        h, w, c = image.shape
        padded = np.pad(image_float, ((radius, radius), (radius, radius), (0, 0)), mode='reflect')
        output = np.zeros_like(image_float)
        
        # Pre-compute spatial weights
        spatial_weights = np.zeros((d, d), dtype=np.float64)
        for i in range(d):
            for j in range(d):
                x = i - radius
                y = j - radius
                spatial_weights[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma_space**2))
        
        # Apply bilateral filter
        for i in range(h):
            for j in range(w):
                center_pixel = padded[i + radius, j + radius, :]
                
                # Lấy window cho từng channel
                window = padded[i:i+d, j:j+d, :]
                
                # Tính color weights (dựa trên Euclidean distance trong RGB space)
                color_diff = window - center_pixel
                color_dist = np.sqrt(np.sum(color_diff**2, axis=2))
                color_weights = np.exp(-(color_dist**2) / (2 * sigma_color**2))
                
                # Kết hợp weights
                weights = spatial_weights[:, :, np.newaxis] * color_weights[:, :, np.newaxis]
                
                # Weighted average cho từng channel
                for channel in range(c):
                    output[i, j, channel] = np.sum(weights[:, :, 0] * window[:, :, channel]) / np.sum(weights[:, :, 0])
        
        return np.clip(output, 0, 255).astype(np.uint8)
    
    return image


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
        return apply_bilateral_filter(
            image,
            d=p['bilateral_d'],
            sigma_color=p['bilateral_sigma'],
            sigma_space=p['bilateral_sigma']
        )


# Hàm test độc lập
if __name__ == "__main__":
    """
    Test module độc lập - không cần người 2
    """
    print("=== Test Smoothing Module (KHÔNG DÙNG OPENCV) ===")
    
    # Tạo ảnh test với nhiễu
    test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    print(f"Ảnh gốc shape: {test_image.shape}")
    print(f"Giá trị pixel - min: {test_image.min()}, max: {test_image.max()}")
    
    # Test Gaussian Blur
    print("\nTesting Gaussian Blur...")
    gaussian = apply_gaussian_blur(test_image)
    print(f"✅ Gaussian Blur - shape: {gaussian.shape}, dtype: {gaussian.dtype}")
    
    # Test Bilateral Filter
    print("\nTesting Bilateral Filter...")
    bilateral = apply_bilateral_filter(test_image)
    print(f"✅ Bilateral Filter - shape: {bilateral.shape}, dtype: {bilateral.dtype}")
    
    # Test Median Blur
    print("\nTesting Median Blur...")
    median = apply_median_blur(test_image)
    print(f"✅ Median Blur - shape: {median.shape}, dtype: {median.dtype}")
    
    # Test hàm chính
    print("\n=== Test Hàm Chính (preprocess_for_sketch) ===")
    for intensity in ['light', 'medium', 'strong']:
        result = preprocess_for_sketch(test_image, method='bilateral', intensity=intensity)
        print(f"✅ Bilateral {intensity}: shape {result.shape}")
    
    print("\n✅ Smoothing module hoạt động tốt!")

