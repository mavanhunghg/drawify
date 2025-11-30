
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
from image_processing.edge_detection import detect_edges
from image_processing.sketch_effect import full_sketch_pipeline

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

def decode_image_from_request(request_data):
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
#  Chuyển numpy array thành base64 string
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
#  API preprocessing: Grayscale + Smoothing
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        image = decode_image_from_request({**data, **request.files})
        method = request.form.get('method', 'bilateral') if not request.is_json else data.get('method', 'bilateral')
        intensity = request.form.get('intensity', 'medium') if not request.is_json else data.get('intensity', 'medium')
        
        gray_image = convert_to_grayscale(image)
        smooth_image = preprocess_for_sketch(gray_image, method=method, intensity=intensity)
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
        print(f"Error in /api/preprocess: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Lỗi xử lý: {str(e)}'
        }), 400

@app.route('/api/grayscale', methods=['POST'])
def grayscale_only():
#  API chỉ chuyển ảnh sang xám
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
#  Trang chủ API
    return jsonify({
        'project': 'Drawify - Photo to Sketch',
        'version': '2.0',
        'features': [
            'Grayscale Conversion',
            'Image Smoothing (Bilateral, Gaussian, Median)',
            'Edge Detection (Canny, Sobel, Laplacian)',
            'Sketch Effect (Pencil, Enhanced)'
        ],
        'endpoints': {
            '/api/preprocess': 'Grayscale + Smoothing',
            '/api/grayscale': 'Grayscale only',
            '/api/sketch': 'Edge Detection + Sketch',
            '/api/full-pipeline': 'Full Pipeline'
        },
        'status': 'running'
    })

@app.route('/api/sketch', methods=['POST'])
def create_sketch():
#  API tạo sketch effect
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        image = decode_image_from_request({**data, **request.files})
        
        smoothing_method = request.form.get('smoothing_method', 'bilateral') if not request.is_json else data.get('smoothing_method', 'bilateral')
        intensity = request.form.get('intensity', 'medium') if not request.is_json else data.get('intensity', 'medium')
        edge_method = request.form.get('edge_method', 'canny') if not request.is_json else data.get('edge_method', 'canny')
        detail_level = request.form.get('detail_level', 'pencil') if not request.is_json else data.get('detail_level', 'pencil')
        low_threshold = int(request.form.get('low_threshold', '50')) if not request.is_json else data.get('low_threshold', 50)
        high_threshold = int(request.form.get('high_threshold', '150')) if not request.is_json else data.get('high_threshold', 150)
        invert = request.form.get('invert', 'false').lower() == 'true' if not request.is_json else data.get('invert', False)
        
        gray_image = convert_to_grayscale(image)
        smooth_image = preprocess_for_sketch(gray_image, method=smoothing_method, intensity=intensity)
        edges = detect_edges(smooth_image, method=edge_method, low_threshold=low_threshold, high_threshold=high_threshold)
        sketch = full_sketch_pipeline(smooth_image, edges, detail_level=detail_level, invert=invert)
        
        result_base64 = encode_image_to_base64(sketch)
        
        return jsonify({
            'success': True,
            'image': result_base64,
            'message': f'Tạo sketch thành công: {edge_method} + {detail_level}',
            'shape': list(sketch.shape),
            'pipeline': {
                'smoothing': smoothing_method,
                'edge_detection': edge_method,
                'detail_level': detail_level
            }
        })
    
    except Exception as e:
        print(f"Error in /api/sketch: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 400


@app.route('/api/full-pipeline', methods=['POST'])
def full_pipeline_endpoint():
#  API pipeline đầy đủ
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        image = decode_image_from_request({**data, **request.files})
        
        smoothing_method = request.form.get('smoothing_method', 'bilateral') if not request.is_json else data.get('smoothing_method', 'bilateral')
        intensity = request.form.get('intensity', 'light') if not request.is_json else data.get('intensity', 'light')
        edge_method = request.form.get('edge_method', 'canny') if not request.is_json else data.get('edge_method', 'canny')
        detail_level = request.form.get('detail_level', 'pencil') if not request.is_json else data.get('detail_level', 'pencil')
        low_threshold = int(request.form.get('low_threshold', '50')) if not request.is_json else data.get('low_threshold', 50)
        high_threshold = int(request.form.get('high_threshold', '150')) if not request.is_json else data.get('high_threshold', 150)
        invert = request.form.get('invert', 'false').lower() == 'true' if not request.is_json else data.get('invert', False)
        
        gray_image = convert_to_grayscale(image)
        smooth_image = preprocess_for_sketch(gray_image, method=smoothing_method, intensity=intensity)
        edges = detect_edges(smooth_image, method=edge_method, low_threshold=low_threshold, high_threshold=high_threshold)
        sketch = full_sketch_pipeline(smooth_image, edges, detail_level=detail_level, invert=invert)
        
        result_base64 = encode_image_to_base64(sketch)
        
        return jsonify({
            'success': True,
            'image': result_base64,
            'message': 'Xử lý pipeline đầy đủ thành công',
            'shape': list(sketch.shape),
            'pipeline': {
                'preprocessing': {
                    'grayscale': 'weighted_average',
                    'smoothing': smoothing_method,
                    'intensity': intensity
                },
                'sketch': {
                    'edge_detection': edge_method,
                    'sketch_effect': detail_level
                }
            }
        })
    
    except Exception as e:
        print(f"Error in /api/full-pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 400


@app.route('/health')
def health_check():
    """Health check"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("Starting Drawify API - Photo to Sketch")
    print("Server: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
