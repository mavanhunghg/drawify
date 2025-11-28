

import numpy as np
from scipy import ndimage

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️ OpenCV không có - sẽ dùng manual bilateral filter (chậm hơn)")


def apply_gaussian_blur(image, kernel_size=(5, 5)):
    """Gaussian Blur - Sử dụng scipy.ndimage"""
    ksize_h = kernel_size[0] if kernel_size[0] % 2 == 1 else kernel_size[0] + 1
    ksize_w = kernel_size[1] if kernel_size[1] % 2 == 1 else kernel_size[1] + 1
    
    # Tính sigma từ kernel size
    sigma = max(ksize_h, ksize_w) / 6.0
    
    # Sử dụng scipy.ndimage.gaussian_filter (tối ưu C backend)
    return ndimage.gaussian_filter(image.astype(np.float64), sigma=sigma).astype(np.uint8)


def apply_median_blur(image, kernel_size=5):
    """Median Blur - Sử dụng scipy.ndimage"""
    ksize = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    
    # Sử dụng scipy.ndimage.median_filter 
    return ndimage.median_filter(image, size=ksize).astype(np.uint8)


def apply_bilateral_filter_opencv(image, d=9, sigma_color=75, sigma_space=75):
    """
    Bilateral Filter với OpenCV (NHANH - MẶC ĐỊNH)
    """
    if not OPENCV_AVAILABLE:
        return apply_bilateral_filter_manual(image, d, sigma_color, sigma_space)
    
    if d % 2 == 0:
        d += 1
    
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)


def apply_bilateral_filter_manual(image, d=9, sigma_color=75, sigma_space=75):
    """
    Bilateral Filter CODE THỦ CÔNG ( dự phòng)
    """
    if d % 2 == 0:
        d += 1
    
    # Tối ưu: Giới hạn d để tăng tốc (d càng lớn càng chậm)
    original_d = d
    if d > 9:
        d = 9
        print(f"  Bilateral Manual: Giảm d từ {original_d} xuống {d} để tối ưu tốc độ")
    
    # Tối ưu: Giảm kích thước ảnh nếu quá lớn (ảnh lớn = chậm rất nhiều)
    original_shape = image.shape
    scale_factor = 1.0
    max_dimension = 1500  # Giới hạn chiều dài tối đa
    
    if max(image.shape[:2]) > max_dimension:
        scale_factor = max_dimension / max(image.shape[:2])
        new_h = int(image.shape[0] * scale_factor)
        new_w = int(image.shape[1] * scale_factor)
        from scipy.ndimage import zoom
        image = zoom(image.astype(np.float64), 
                    (new_h/image.shape[0], new_w/image.shape[1]), 
                    order=1).astype(np.uint8)
        print(f"  Bilateral Manual: Giảm ảnh từ {original_shape[:2]} xuống {image.shape[:2]} để tăng tốc (scale={scale_factor:.2f})")
    
    radius = d // 2
    height, width = image.shape[:2]
    
    # Pre-compute spatial Gaussian weights
    y_coords, x_coords = np.ogrid[-radius:radius+1, -radius:radius+1]
    spatial_weights = np.exp(-(x_coords**2 + y_coords**2) / (2 * sigma_space**2))
    
    # Pad image
    padded = np.pad(image.astype(np.float64), radius, mode='reflect')
    filtered = np.zeros_like(image, dtype=np.float64)
    
    # Apply bilateral filter - vẫn dùng loops nhưng đã tối ưu bằng cách giảm kích thước
    image_float = image.astype(np.float64)
    
    for i in range(height):
        for j in range(width):
            neighborhood = padded[i:i+d, j:j+d]
            center_value = image_float[i, j]
            
            # Compute color weights
            color_diff = neighborhood - center_value
            color_weights = np.exp(-(color_diff**2) / (2 * sigma_color**2))
            
            # Combined weights
            weights = spatial_weights * color_weights
            weights_sum = np.sum(weights)
            
            # Weighted average
            if weights_sum > 0:
                filtered[i, j] = np.sum(weights * neighborhood) / weights_sum
            else:
                filtered[i, j] = center_value
    
    result = np.clip(filtered, 0, 255).astype(np.uint8)
    
    # Scale lại nếu đã giảm kích thước
    if scale_factor < 1.0:
        from scipy.ndimage import zoom
        result = zoom(result.astype(np.float64), 
                     (original_shape[0]/result.shape[0], original_shape[1]/result.shape[1]), 
                     order=1).astype(np.uint8)
    
    return result


def apply_bilateral_filter(image, d=9, sigma_color=75, sigma_space=75, use_opencv=True):
    """
    Bilateral Filter - Wrapper function (MẶC ĐỊNH DÙNG OPENCV)
    
    Args:
        image: Input image
        d: Diameter of pixel neighborhood
        sigma_color: Filter sigma in the color space
        sigma_space: Filter sigma in the coordinate space
        use_opencv: True = dùng OpenCV (nhanh), False = dùng code thủ công (chậm)
                   Mặc định: True (dùng OpenCV)
    
    Returns:
        Filtered image
    """
    if use_opencv and OPENCV_AVAILABLE:
        # MẶC ĐỊNH: Dùng OpenCV (nhanh)
        return apply_bilateral_filter_opencv(image, d, sigma_color, sigma_space)
    else:
        # Fallback: Dùng manual code (chậm)
        if use_opencv and not OPENCV_AVAILABLE:
            print("  ⚠️ OpenCV không có - tự động chuyển sang manual")
        return apply_bilateral_filter_manual(image, d, sigma_color, sigma_space)


def preprocess_for_sketch(image, method='bilateral', intensity='light'):
    """
    Làm mịn ảnh tối ưu cho sketch effect
    
    Args:
        image: Input image
        method: 'bilateral', 'gaussian', hoặc 'median'
        intensity: 'light', 'medium', hoặc 'strong'
    
    Returns:
        Smoothed image
    """
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
    
    p = params.get(intensity, params['light'])
    
    if method == 'bilateral':
        # MẶC ĐỊNH: Bilateral sẽ dùng OpenCV (nhanh)
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
        return apply_bilateral_filter(
            image,
            d=p['bilateral_d'],
            sigma_color=p['bilateral_sigma'],
            sigma_space=p['bilateral_sigma']
        )

