"""
Convolution utilities - Hàm helper cho convolution 2D
Không dùng OpenCV, chỉ dùng NumPy
"""

import numpy as np


def pad_image(image, kernel_size, mode='reflect'):
    """
    Padding ảnh để convolution không mất biên
    
    Args:
        image: Ảnh numpy array (2D hoặc 3D)
        kernel_size: Kích thước kernel (height, width)
        mode: 'reflect' (mirror), 'constant' (zero), 'edge' (replicate)
    
    Returns:
        Ảnh đã được padding
    """
    if len(image.shape) == 2:
        h, w = image.shape
        kh, kw = kernel_size
        pad_h = kh // 2
        pad_w = kw // 2
        
        if mode == 'reflect':
            return np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='reflect')
        elif mode == 'constant':
            return np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='constant', constant_values=0)
        elif mode == 'edge':
            return np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
        else:
            return np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='reflect')
    
    elif len(image.shape) == 3:
        # Ảnh màu (3 channels)
        h, w, c = image.shape
        kh, kw = kernel_size
        pad_h = kh // 2
        pad_w = kw // 2
        
        if mode == 'reflect':
            return np.pad(image, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='reflect')
        elif mode == 'constant':
            return np.pad(image, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='constant', constant_values=0)
        elif mode == 'edge':
            return np.pad(image, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='edge')
        else:
            return np.pad(image, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='reflect')
    
    return image


def convolve2d(image, kernel, mode='reflect'):
    """
    Convolution 2D - Tự implement không dùng OpenCV
    
    Args:
        image: Ảnh numpy array (2D hoặc 3D)
        kernel: Kernel 2D (ma trận)
        mode: Padding mode ('reflect', 'constant', 'edge')
    
    Returns:
        Ảnh đã được convolution
    """
    # Đảm bảo kernel là 2D
    kernel = np.array(kernel)
    if len(kernel.shape) != 2:
        raise ValueError("Kernel phải là ma trận 2D")
    
    kh, kw = kernel.shape
    
    # Padding
    padded = pad_image(image, (kh, kw), mode=mode)
    
    # Convolution
    if len(image.shape) == 2:
        # Grayscale
        h, w = image.shape
        output = np.zeros((h, w), dtype=np.float64)
        
        for i in range(h):
            for j in range(w):
                output[i, j] = np.sum(padded[i:i+kh, j:j+kw] * kernel)
        
        return output.astype(image.dtype)
    
    elif len(image.shape) == 3:
        # Color image
        h, w, c = image.shape
        output = np.zeros((h, w, c), dtype=np.float64)
        
        for channel in range(c):
            for i in range(h):
                for j in range(w):
                    output[i, j, channel] = np.sum(padded[i:i+kh, j:j+kw, channel] * kernel)
        
        return output.astype(image.dtype)
    
    return image


def correlate2d(image, kernel, mode='reflect'):
    """
    Correlation 2D (giống convolution nhưng không flip kernel)
    Một số thuật toán dùng correlation thay vì convolution
    """
    # Flip kernel để convert correlation → convolution
    kernel_flipped = np.flip(np.flip(kernel, 0), 1)
    return convolve2d(image, kernel_flipped, mode=mode)


