"""Module làm mịn ảnh (Image Smoothing)"""

import numpy as np
import cv2


def apply_gaussian_blur(image, kernel_size=(5, 5)):
    """Gaussian Blur"""
    ksize_h = kernel_size[0] if kernel_size[0] % 2 == 1 else kernel_size[0] + 1
    ksize_w = kernel_size[1] if kernel_size[1] % 2 == 1 else kernel_size[1] + 1
    return cv2.GaussianBlur(image, (ksize_h, ksize_w), 0)


def apply_median_blur(image, kernel_size=5):
    """Median Blur"""
    ksize = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    return cv2.medianBlur(image, ksize)


def apply_bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
    """Bilateral Filter (edge-preserving)"""
    if d % 2 == 0:
        d += 1
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)


def preprocess_for_sketch(image, method='bilateral', intensity='light'):
    """Làm mịn ảnh tối ưu cho sketch"""
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

