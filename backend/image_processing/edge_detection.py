
import numpy as np
from scipy import ndimage


def sobel_edge_detection(image):
    sobel_x = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]], dtype=np.float64)
    
    sobel_y = np.array([[-1, -2, -1],
                        [ 0,  0,  0],
                        [ 1,  2,  1]], dtype=np.float64)
    

    image_float = image.astype(np.float64)
    grad_x = ndimage.convolve(image_float, sobel_x)
    grad_y = ndimage.convolve(image_float, sobel_y)

    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    magnitude = np.clip(magnitude, 0, 255)
    return magnitude.astype(np.uint8)


def laplacian_edge_detection(image):

    laplacian_kernel = np.array([[0,  1, 0],
                                 [1, -4, 1],
                                 [0,  1, 0]], dtype=np.float64)
    
    image_float = image.astype(np.float64)
    laplacian = ndimage.convolve(image_float, laplacian_kernel)
    laplacian = np.abs(laplacian)
    laplacian = np.clip(laplacian, 0, 255)
    return laplacian.astype(np.uint8)


def canny_edge_detection(image, low_threshold=50, high_threshold=150):
    # 1. Gaussian smoothing
    gaussian_kernel = np.array([[1, 2, 1],
                                [2, 4, 2],
                                [1, 2, 1]], dtype=np.float64) / 16
    smoothed = ndimage.convolve(image.astype(np.float64), gaussian_kernel)
    
    # 2. Sobel gradient
    sobel_x = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]], dtype=np.float64)
    sobel_y = np.array([[-1, -2, -1],
                        [ 0,  0,  0],
                        [ 1,  2,  1]], dtype=np.float64)
    
    grad_x = ndimage.convolve(smoothed, sobel_x)
    grad_y = ndimage.convolve(smoothed, sobel_y)
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    
    angle = np.arctan2(grad_y, grad_x)
    
    #  Double threshold
    strong_edges = (magnitude > high_threshold).astype(np.uint8) * 255
    weak_edges = ((magnitude >= low_threshold) & (magnitude <= high_threshold)).astype(np.uint8) * 255
    

    edges = strong_edges + weak_edges
    edges = np.clip(edges, 0, 255).astype(np.uint8)
    
    return edges


def detect_edges(image, method='canny', low_threshold=50, high_threshold=150):
    if method == 'canny':
        return canny_edge_detection(image, low_threshold, high_threshold)
    elif method == 'sobel':
        return sobel_edge_detection(image)
    elif method == 'laplacian':
        return laplacian_edge_detection(image)
    else:
        return canny_edge_detection(image, low_threshold, high_threshold)


