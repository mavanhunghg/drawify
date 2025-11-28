"""
Image I/O utilities - Đọc/ghi ảnh dùng PIL (không dùng OpenCV)
"""

import numpy as np
from PIL import Image
import io


def load_image(file_path):
    """
    Đọc ảnh từ file path
    
    Args:
        file_path: Đường dẫn file ảnh
    
    Returns:
        PIL Image object
    """
    return Image.open(file_path)


def save_image(image, file_path):
    """
    Lưu ảnh ra file
    
    Args:
        image: PIL Image hoặc numpy array
        file_path: Đường dẫn file để lưu
    """
    if isinstance(image, np.ndarray):
        image = array_to_image(image)
    image.save(file_path)


def image_to_array(image, mode='RGB'):
    """
    Chuyển PIL Image sang numpy array
    
    Args:
        image: PIL Image
        mode: 'RGB', 'L' (grayscale), 'RGBA'
    
    Returns:
        numpy array (uint8)
    """
    if isinstance(image, np.ndarray):
        return image
    
    # Convert mode nếu cần
    if mode == 'RGB' and image.mode != 'RGB':
        if image.mode == 'RGBA':
            # Tạo background trắng
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # Dùng alpha channel làm mask
            image = background
        else:
            image = image.convert('RGB')
    elif mode == 'L' and image.mode != 'L':
        image = image.convert('L')
    
    return np.array(image, dtype=np.uint8)


def array_to_image(array, mode='RGB'):
    """
    Chuyển numpy array sang PIL Image
    
    Args:
        array: numpy array (uint8)
        mode: 'RGB', 'L' (grayscale), 'RGBA'
    
    Returns:
        PIL Image
    """
    # Đảm bảo dtype là uint8
    if array.dtype != np.uint8:
        # Clip và convert
        array = np.clip(array, 0, 255).astype(np.uint8)
    
    # Chuyển sang PIL Image
    if len(array.shape) == 2:
        # Grayscale
        return Image.fromarray(array, mode='L')
    elif len(array.shape) == 3:
        if array.shape[2] == 3:
            # RGB
            return Image.fromarray(array, mode='RGB')
        elif array.shape[2] == 4:
            # RGBA
            return Image.fromarray(array, mode='RGBA')
    
    return Image.fromarray(array)


def decode_base64_image(base64_string):
    """
    Decode ảnh từ base64 string
    Hỗ trợ: JPG, PNG, WEBP, AVIF và tất cả format Pillow hỗ trợ
    
    Args:
        base64_string: Base64 string (có thể có prefix data:image/...;base64,)
    
    Returns:
        numpy array (RGB format)
    """
    import base64
    
    # Loại bỏ prefix nếu có
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    # Decode
    image_bytes = base64.b64decode(base64_string)
    
    # Đọc bằng PIL (hỗ trợ AVIF nếu có pillow-avif-plugin)
    try:
        # Thử import pillow-avif để enable AVIF support
        try:
            import pillow_avif
        except ImportError:
            pass  # Không có plugin thì bỏ qua, PIL vẫn đọc được các format khác
        
        pil_image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise ValueError(f"Không thể đọc ảnh: {str(e)}. Format có thể không được hỗ trợ.")
    
    # Convert sang RGB nếu cần
    if pil_image.mode != 'RGB':
        if pil_image.mode == 'RGBA':
            background = Image.new('RGB', pil_image.size, (255, 255, 255))
            background.paste(pil_image, mask=pil_image.split()[3])
            pil_image = background
        else:
            pil_image = pil_image.convert('RGB')
    
    return image_to_array(pil_image, mode='RGB')


def encode_image_to_base64(image, format='PNG'):
    """
    Encode ảnh sang base64 string
    
    Args:
        image: PIL Image hoặc numpy array
        format: 'PNG', 'JPEG'
    
    Returns:
        Base64 string với prefix data:image/...
    """
    import base64
    
    # Convert sang PIL nếu cần
    if isinstance(image, np.ndarray):
        image = array_to_image(image)
    
    # Encode
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    image_bytes = buffer.getvalue()
    
    # Base64 encode
    base64_string = base64.b64encode(image_bytes).decode('utf-8')
    
    # Thêm prefix
    mime_type = 'image/png' if format == 'PNG' else 'image/jpeg'
    return f"data:{mime_type};base64,{base64_string}"

