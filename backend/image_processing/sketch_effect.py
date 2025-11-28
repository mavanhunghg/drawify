"""Module tạo hiệu ứng tranh vẽ (Sketch Effect)"""

import numpy as np
import cv2


def create_pencil_sketch(gray_image, edges):
    """Tạo hiệu ứng vẽ chì (pencil sketch)"""
    inverted = 255 - gray_image
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
    
    def dodge(front, back):
        result = back / (255 - front + 1e-7) * 255
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    
    sketch = dodge(blurred, gray_image)
    edges_inv = 255 - edges
    sketch = cv2.multiply(sketch.astype(float) / 255,
                          edges_inv.astype(float) / 255,
                          scale=255).astype(np.uint8)
    return sketch


def create_artistic_sketch(gray_image, edges, style='strong'):
    """Tạo hiệu ứng sketch nghệ thuật"""
    if style == 'strong':
        edges = cv2.threshold(edges, 100, 255, cv2.THRESH_BINARY)[1]
        shading = cv2.bilateralFilter(gray_image, 9, 75, 75)
        edges_inv = 255 - edges
        sketch = cv2.multiply(edges_inv.astype(float) / 255,
                             shading.astype(float) / 255,
                             scale=255).astype(np.uint8)
        return sketch
    else:
        return create_pencil_sketch(gray_image, edges)


def invert_sketch(sketch):
    """Đảo ngược sketch"""
    return 255 - sketch


def full_sketch_pipeline(gray_image, edges, detail_level='pencil', invert=False):
    """Pipeline đầy đủ tạo sketch"""
    if detail_level == 'pencil':
        sketch = create_pencil_sketch(gray_image, edges)
    elif detail_level == 'enhanced':
        sketch = create_artistic_sketch(gray_image, edges, 'strong')
    else:
        sketch = create_pencil_sketch(gray_image, edges)
    
    if invert:
        sketch = invert_sketch(sketch)
    
    return sketch
