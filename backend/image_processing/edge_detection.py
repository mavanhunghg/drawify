"""Module phát hiện biên (Edge Detection)"""

import numpy as np
import cv2


def canny_edge_detection(image, low_threshold=50, high_threshold=150):
    """Canny Edge Detection"""
    return cv2.Canny(image, low_threshold, high_threshold)


def sobel_edge_detection(image):
    """Sobel Edge Detection"""
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    return np.clip(magnitude, 0, 255).astype(np.uint8)


def laplacian_edge_detection(image):
    """Laplacian Edge Detection"""
    laplacian = cv2.Laplacian(image, cv2.CV_64F, ksize=3)
    laplacian = np.abs(laplacian)
    return np.clip(laplacian, 0, 255).astype(np.uint8)


def detect_edges(image, method='canny', low_threshold=50, high_threshold=150):
    """Hàm chính phát hiện biên"""
    if method == 'canny':
        return canny_edge_detection(image, low_threshold, high_threshold)
    elif method == 'sobel':
        return sobel_edge_detection(image)
    elif method == 'laplacian':
        return laplacian_edge_detection(image)
    else:
        return canny_edge_detection(image, low_threshold, high_threshold)


