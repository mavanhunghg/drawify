"""
Flask API cho dự án Drawify - Chuyển ảnh thành tranh vẽ
Người 1 (Hiến): API /preprocess - Grayscale + Smoothing
Người 2 (Hùng): API /sketch - Edge Detection + Sketch Effect (CHI TIẾT CAO)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
import io
import base64
import os
import sys

# Import các module xử lý ảnh
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import image_processing.grayscale as grayscale_module
import image_processing.smoothing as smoothing_module
from image_processing.sketch_effect import sketch_effect, sketch_effect_enhanced, sketch_effect_maximum_detail

convert_to_grayscale = grayscale_module.convert_to_grayscale
preprocess_for_sketch = smoothing_module.preprocess_for_sketch

# Khởi tạo Flask app
app = Flask(__name__)
CORS(app)  # Cho phép frontend gọi API

# Cấu hình
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB

def decode_image_from_request(request_data):
    """
    Giải mã ảnh từ request (base64 hoặc file upload)
    Hỗ trợ: JPG, PNG, WEBP, AVIF và tất cả format Pillow hỗ trợ
    
    Returns:
        numpy.ndarray: Ảnh đã decode (BGR format cho OpenCV)
    """
    # Case 1: Base64 string
    if 'image' in request_data:
        try:
            # Loại bỏ prefix data:image/...;base64, nếu có
            image_data = request_data['image']
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Thử decode bằng Pillow trước (hỗ trợ AVIF, WEBP...)
            try:
                import pillow_avif  # Import để enable AVIF support
                pil_image = Image.open(io.BytesIO(image_bytes))
                # Convert sang RGB nếu cần
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                # Convert PIL → numpy → BGR (OpenCV format)
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                return image
            except:
                # Fallback: Dùng cv2.imdecode cho JPG/PNG thông thường
                image_array = np.frombuffer(image_bytes, dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                if image is None:
                    raise ValueError("Không thể decode ảnh")
                return image
        except Exception as e:
            raise ValueError(f"Lỗi decode base64: {str(e)}")
    
    # Case 2: File upload
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            raise ValueError("Không có file được chọn")
        
        try:
            # Đọc file thành bytes
            file_bytes = file.read()
            
            # Thử decode bằng Pillow trước (hỗ trợ AVIF, WEBP...)
            try:
                import pillow_avif  # Import để enable AVIF support
                pil_image = Image.open(io.BytesIO(file_bytes))
                # Convert sang RGB nếu cần
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                # Convert PIL → numpy → BGR (OpenCV format)
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                return image
            except:
                # Fallback: Dùng cv2.imdecode cho JPG/PNG thông thường
                image_array = np.frombuffer(file_bytes, dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                if image is None:
                    raise ValueError("Không thể decode ảnh")
                return image
        except Exception as e:
            raise ValueError(f"Lỗi đọc file: {str(e)}")
    
    raise ValueError("Không tìm thấy ảnh trong request")

def encode_image_to_base64(image):
    """
    Encode ảnh numpy array sang base64 string
    
    Args:
        image (numpy.ndarray): Ảnh cần encode
    
    Returns:
        str: Base64 string
    """
    # Encode ảnh thành PNG
    success, buffer = cv2.imencode('.png', image)
    if not success:
        raise ValueError("Lỗi encode ảnh")
    
    # Chuyển sang base64
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"

# ============================================
# API CỦA NGƯỜI 1 (HIẾN) - PREPROCESSING
# ============================================

@app.route('/api/preprocess', methods=['POST'])
def preprocess_image():
    """
    API xử lý tiền xử lý ảnh: Grayscale + Smoothing
    
    Input (JSON hoặc FormData):
        - image: base64 string HOẶC file upload
        - method: 'bilateral' (khuyên dùng), 'gaussian', 'median' (optional)
        - intensity: 'light', 'medium', 'strong' (optional)
    
    Output (JSON):
        - success: True/False
        - image: base64 string (ảnh đã xử lý)
        - message: thông báo
    """
    try:
        # 1. Nhận ảnh từ request
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        image = decode_image_from_request({**data, **request.files})
        
        # 2. Lấy tham số
        method = request.form.get('method', 'bilateral') if not request.is_json else data.get('method', 'bilateral')
        intensity = request.form.get('intensity', 'medium') if not request.is_json else data.get('intensity', 'medium')
        
        # 3. Xử lý: Grayscale
        gray_image = convert_to_grayscale(image)
        
        # 4. Xử lý: Smoothing
        smooth_image = preprocess_for_sketch(gray_image, method=method, intensity=intensity)
        
        # 5. Encode kết quả
        result_base64 = encode_image_to_base64(smooth_image)
        
        return jsonify({
            'success': True,
            'image': result_base64,
            'message': f'Xử lý thành công với {method} filter ({intensity})',
            'shape': list(smooth_image.shape),
            'method': method,
            'intensity': intensity
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi xử lý: {str(e)}'
        }), 400

@app.route('/api/grayscale', methods=['POST'])
def grayscale_only():
    """
    API chỉ chuyển ảnh sang xám (không smoothing)
    Để test riêng grayscale
    """
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        image = decode_image_from_request({**data, **request.files})
        gray_image = convert_to_grayscale(image)
        result_base64 = encode_image_to_base64(gray_image)
        
        return jsonify({
            'success': True,
            'image': result_base64,
            'message': 'Chuyển sang xám thành công',
            'shape': list(gray_image.shape)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 400

# ============================================
# API CỦA NGƯỜI 2 (HÙNG) - SKETCH (CHI TIẾT CAO)
# ============================================

@app.route('/api/sketch', methods=['POST'])
def sketch_image():
    """
    API tạo sketch - Chi tiết cao với nhiều tùy chọn nét
    
    Input:
        - image: base64 string hoặc file upload
        - smoothing_method: 'bilateral' (khuyên dùng), 'gaussian', 'median'
        - intensity: 'light', 'medium', 'strong'
        - edge_method: 'canny', 'sobel', 'laplacian', 'log'
        - detail_level: 'light', 'medium', 'enhanced', 'maximum'
    
    Output:
        - success: True/False
        - image: base64 string (ảnh sketch nét)
        - message: thông báo
        - detail_level: mức độ chi tiết đã dùng
    """
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        image = decode_image_from_request({**data, **request.files})
        
        # Lấy tham số
        smoothing_method = data.get('smoothing_method', 'bilateral')
        intensity = data.get('intensity', 'medium')
        edge_method = data.get('edge_method', 'canny')
        detail_level = data.get('detail_level', 'medium')  # light, medium, enhanced, maximum
        
        # Chọn hàm phù hợp theo mức độ chi tiết
        if detail_level == 'maximum':
            sketch = sketch_effect_maximum_detail(image, smoothing_method, intensity)
            detail_msg = 'Chi tiết cực đại'
        elif detail_level == 'enhanced':
            sketch = sketch_effect_enhanced(image, smoothing_method, intensity, edge_method, 'strong')
            detail_msg = 'Chi tiết nâng cao'
        else:  # medium (mặc định)
            sketch = sketch_effect(image, smoothing_method, intensity, edge_method)
            detail_msg = 'Chi tiết vừa'
        
        result_base64 = encode_image_to_base64(sketch)
        
        return jsonify({
            'success': True,
            'image': result_base64,
            'message': f'Tạo sketch thành công! ({detail_msg})',
            'shape': list(sketch.shape),
            'detail_level': detail_level
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi xử lý sketch: {str(e)}'
        }), 400

# ============================================
# HEALTH CHECK & INFO
# ============================================

@app.route('/')
def home():
    """
    Trang chủ API
    """
    return jsonify({
        'project': 'Drawify - Image to Sketch',
        'version': '2.0 (Chi tiết cao)',
        'endpoints': {
            'preprocessing': {
                '/api/preprocess': 'Grayscale + Smoothing (Người 1 - Hiến)',
                '/api/grayscale': 'Chỉ chuyển xám (test)',
            },
            'sketch': {
                '/api/sketch': 'Edge Detection + Sketch chi tiết cao (Người 2 - Hùng)'
            }
        },
        'status': 'running'
    })

@app.route('/health')
def health_check():
    """
    Kiểm tra server hoạt động
    """
    return jsonify({'status': 'healthy', 'message': 'Server đang chạy tốt!'})

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    print("🚀 Starting Drawify API Server...")
    print("📍 Người 1 (Hiến) - Preprocessing API: /api/preprocess")
    print("📍 Test grayscale: /api/grayscale")
    print("📍 Người 2 (Hùng) - Sketch API: /api/sketch (CHI TIẾT CAO)")
    print("\n✅ Server sẵn sàng tại: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
