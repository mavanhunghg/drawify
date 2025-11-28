"""
Flask API cho dự án Drawify - Preprocessing Module
Người thực hiện: Hiến
Chức năng: Grayscale + Smoothing (Bilateral, Gaussian, Median)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import pillow_avif
import io
import base64
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from image_processing.grayscale import convert_to_grayscale
from image_processing.smoothing import preprocess_for_sketch

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

def decode_image_from_request(request_data):
    """Giải mã ảnh từ request (base64 hoặc file upload)"""
    if 'image' in request_data:
        try:
            image_data = request_data['image']
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            return np.array(pil_image)
        except Exception as e:
            raise ValueError(f"Lỗi decode base64: {str(e)}")
    
   
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            raise ValueError("Không có file được chọn")
        
        try:
            file_bytes = file.read()
            pil_image = Image.open(io.BytesIO(file_bytes))
            
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            return np.array(pil_image)
        except Exception as e:
            raise ValueError(f"Lỗi đọc file: {str(e)}")
    
    raise ValueError("Không tìm thấy ảnh trong request")

def encode_image_to_base64(image):
    """Encode ảnh numpy array sang base64 string"""
    if len(image.shape) == 2:
        pil_image = Image.fromarray(image.astype(np.uint8), mode='L')
    else:
        pil_image = Image.fromarray(image.astype(np.uint8), mode='RGB')
    
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"

@app.route('/api/preprocess', methods=['POST'])
def preprocess_image():
    """API xử lý tiền xử lý ảnh: Grayscale + Smoothing"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        image = decode_image_from_request({**data, **request.files})
        method = request.form.get('method', 'bilateral') if not request.is_json else data.get('method', 'bilateral')
        intensity = request.form.get('intensity', 'medium') if not request.is_json else data.get('intensity', 'medium')
        use_opencv = request.form.get('use_opencv', 'true').lower() == 'true' if not request.is_json else data.get('use_opencv', True)
        
        gray_image = convert_to_grayscale(image)
        smooth_image = preprocess_for_sketch(gray_image, method=method, intensity=intensity, use_opencv=use_opencv)
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
        print(f"❌ Error in /api/preprocess: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Lỗi xử lý: {str(e)}'
        }), 400

@app.route('/api/grayscale', methods=['POST'])
def grayscale_only():
    """API chỉ chuyển ảnh sang xám"""
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

@app.route('/')
def home():
    """Trang chủ API"""
    return jsonify({
        'project': 'Drawify - Image Preprocessing',
        'version': '1.0',
        'author': 'Hiến',
        'features': [
            'Grayscale Conversion',
            'Bilateral Filter (Edge-Preserving)',
            'Gaussian Blur',
            'Median Blur'
        ],
        'endpoints': {
            '/api/preprocess': 'Grayscale + Smoothing',
            '/api/grayscale': 'Grayscale only (test)',
        },
        'status': 'running'
    })

@app.route('/health')
def health_check():
    """Kiểm tra server hoạt động"""
    return jsonify({'status': 'healthy', 'message': 'Server đang chạy tốt!'})

if __name__ == '__main__':
    print("🚀 Starting Drawify Preprocessing API...")
    print("👤 Module: Hiến - Grayscale + Smoothing")
    print("📍 API /api/preprocess - Tiền xử lý ảnh")
    print("📍 API /api/grayscale - Chuyển xám (test)")
    print("\n✅ Server sẵn sàng tại: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
