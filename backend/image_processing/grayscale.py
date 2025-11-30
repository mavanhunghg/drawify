
import numpy as np


def convert_to_grayscale(image):

    if len(image.shape) == 2:
        return image.astype(np.uint8)
    
    image = image.astype(np.float32)
    
    if len(image.shape) == 3 and image.shape[2] == 3:
        r = image[:, :, 0]
        g = image[:, :, 1]
        b = image[:, :, 2]
        gray = 0.299 * r + 0.587 * g + 0.114 * b
        return np.clip(gray, 0, 255).astype(np.uint8)
    
    if len(image.shape) == 3 and image.shape[2] == 4:
        rgb = image[:, :, :3]
        gray = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
        return np.clip(gray, 0, 255).astype(np.uint8)
    
    return image.astype(np.uint8)

