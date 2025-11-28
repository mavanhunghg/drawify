"""Module tạo hiệu ứng tranh vẽ (Sketch Effect) - CODE THỦ CÔNG"""

import numpy as np
from scipy import ndimage
from .smoothing import apply_gaussian_blur, apply_bilateral_filter


def gaussian_blur_manual(image, kernel_size=21):
    """Gaussian blur thủ công với scipy"""
    sigma = kernel_size / 6.0
    return ndimage.gaussian_filter(image.astype(np.float64), sigma=sigma).astype(np.uint8)


def create_pencil_sketch(gray_image, edges):
    """Tạo hiệu ứng vẽ chì (pencil sketch) - CODE THỦ CÔNG"""
    # Invert image
    inverted = 255 - gray_image
    
    # Blur inverted image - DÙNG THUYẾT THU CÔNG
    blurred = gaussian_blur_manual(inverted, kernel_size=21)
    
    # Dodge blending
    def dodge(front, back):
        result = back.astype(np.float64) / (255 - front.astype(np.float64) + 1e-7) * 255
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    
    sketch = dodge(blurred, gray_image)
    
    # Blend with edges
    edges_inv = 255 - edges
    sketch = (sketch.astype(np.float64) / 255.0 * 
              edges_inv.astype(np.float64) / 255.0 * 255).astype(np.uint8)
    
    return sketch


def create_artistic_sketch(gray_image, edges, style='strong'):
    """Tạo hiệu ứng sketch nghệ thuật - CODE THỦ CÔNG"""
    if style == 'strong':
        # Threshold edges - CODE THỦ CÔNG
        edges_binary = (edges > 100).astype(np.uint8) * 255
        
        # Shading - DÙNG BILATERAL FILTER TỪ SMOOTHING (OpenCV OK)
        shading = apply_bilateral_filter(gray_image, d=9, sigma_color=75, sigma_space=75)
        
        # Blend
        edges_inv = 255 - edges_binary
        sketch = (edges_inv.astype(np.float64) / 255.0 * 
                 shading.astype(np.float64) / 255.0 * 255).astype(np.uint8)
        return sketch
    else:
        return create_pencil_sketch(gray_image, edges)


def invert_sketch(sketch):
    """Đảo ngược sketch - CODE THỦ CÔNG"""
    return (255 - sketch).astype(np.uint8)


def full_sketch_pipeline(gray_image, edges, detail_level='pencil', invert=False):
    """Pipeline đầy đủ tạo sketch - CODE THỦ CÔNG"""
    if detail_level == 'pencil':
        sketch = create_pencil_sketch(gray_image, edges)
    elif detail_level == 'enhanced':
        sketch = create_artistic_sketch(gray_image, edges, 'strong')
    else:
        sketch = create_pencil_sketch(gray_image, edges)
    
    if invert:
        sketch = invert_sketch(sketch)
    
    return sketch
