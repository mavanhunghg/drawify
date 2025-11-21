# 🎨 Drawify Backend - Chuyển Ảnh Thành Tranh Vẽ

## 📚 Đề tài 4: Xây dựng phần mềm chuyển ảnh thành tranh vẽ (Chương 5)

### 🎯 Yêu cầu đề bài:
- ✅ Phát hiện biên (Edge Detection)
- ✅ Chuyển đổi mức xám (Grayscale)
- ✅ Kỹ thuật làm mịn (Smoothing)
- ✅ Tạo hiệu ứng vẽ tay (Sketch Effect)
- ✅ Sử dụng Bilateral Filter hoặc Edge-Preserving Filter

---

## 👥 Phân công công việc

### 👤 Người 1 (Hiến) - PREPROCESSING ✅ HOÀN THÀNH
**Công việc**: Tiền xử lý ảnh (Grayscale + Smoothing)

**Các module đã hoàn thành**:
- ✅ `image_processing/grayscale.py` - Chuyển đổi mức xám
- ✅ `image_processing/smoothing.py` - Làm mịn ảnh (Gaussian, Bilateral, Median)
- ✅ API `/api/preprocess` - Grayscale + Smoothing
- ✅ API `/api/grayscale` - Test chuyển xám

**Tính năng**:
- Chuyển ảnh màu sang xám (RGB/BGR → Grayscale)
- 3 phương pháp làm mịn:
  - **Bilateral Filter** ⭐ KHUYÊN DÙNG (giữ biên, loại nhiễu)
  - Gaussian Blur (làm mịn đều)
  - Median Blur (loại nhiễu muối tiêu)
- 3 mức độ: light, medium, strong

**API Endpoint**:
```
POST /api/preprocess
Body: {
  "image": "base64 string",
  "method": "bilateral",  // gaussian, median
  "intensity": "medium"   // light, strong
}
```

**Trạng thái**: ✅ Độc lập 100%, có thể demo ngay

---

### 👤 Người 2 (Hùng) - EDGE DETECTION + SKETCH
**Công việc**: Phát hiện biên + Tạo hiệu ứng sketch

**Các module cần làm**:
- `image_processing/edge_detect.py` - Phát hiện biên (Sobel, Canny, Laplacian)
- `image_processing/sketch_effect.py` - Tạo hiệu ứng vẽ tay
- API `/api/sketch` - Edge Detection + Sketch Effect

**Trạng thái**: ⏳ Chưa làm (placeholder có sẵn trong app.py)

---

## 📦 Cấu trúc dự án

```
backend/
├── app.py                          # Flask API server
├── requirements.txt                 # Dependencies
├── test_api.py                      # Script test API
├── demo_preprocessing.py            # Demo với ảnh thực
├── HUONG_DAN_NGUOI_1.md            # Hướng dẫn chi tiết Người 1
│
├── image_processing/                # Package xử lý ảnh
│   ├── __init__.py
│   ├── grayscale.py                 # ✅ Người 1: Chuyển xám
│   ├── smoothing.py                 # ✅ Người 1: Làm mịn
│   ├── edge_detect.py               # ⏳ Người 2: Phát hiện biên
│   └── sketch_effect.py             # ⏳ Người 2: Hiệu ứng sketch
│
├── sample_images/                   # Ảnh mẫu để test
│   ├── sample_gradient.png
│   ├── sample_geometric.png
│   └── sample_noisy.png
│
└── demo_results/                    # Kết quả demo
    ├── *_0_original.png             # Ảnh gốc
    ├── *_1_grayscale.png            # Ảnh xám
    └── *_2_*.png                    # Ảnh đã làm mịn
```

---

## 🚀 Hướng dẫn sử dụng

### 1️⃣ Cài đặt môi trường

```powershell
# Clone/download dự án
cd backend

# (Đã có virtual environment: .venv)
# Activate (nếu cần):
.\.venv\Scripts\Activate.ps1

# Cài packages (đã cài sẵn):
pip install -r requirements.txt
```

**Dependencies**:
- Flask 3.0.0
- opencv-python 4.8.1.78
- numpy 1.26.2
- Pillow 10.1.0
- flask-cors 4.0.0

---

### 2️⃣ Test modules độc lập

```powershell
# Test grayscale module
python image_processing/grayscale.py

# Test smoothing module
python image_processing/smoothing.py
```

Kết quả: Hiển thị "✅ Module hoạt động tốt!"

---

### 3️⃣ Chạy Flask Server

```powershell
python app.py
```

Server chạy tại: **http://localhost:5000**

**Endpoints có sẵn**:
- `GET /` - API info
- `GET /health` - Health check
- `POST /api/grayscale` - Chỉ chuyển xám
- `POST /api/preprocess` - ⭐ Grayscale + Smoothing (Người 1)
- `POST /api/sketch` - ⏳ Edge + Sketch (Người 2 - chưa có)

---

### 4️⃣ Test API

**Cách 1: Dùng test_api.py** (Khuyên dùng)

```powershell
# Mở terminal mới (server vẫn chạy)
python test_api.py
```

**Cách 2: Dùng Postman/Thunder Client**

Request:
```
POST http://localhost:5000/api/preprocess
Content-Type: application/json

{
  "image": "data:image/png;base64,iVBORw0KG...",
  "method": "bilateral",
  "intensity": "medium"
}
```

---

### 5️⃣ Demo với ảnh thực

```powershell
# Demo với ảnh có sẵn
python demo_preprocessing.py path/to/your/image.jpg

# Hoặc tự tạo ảnh mẫu và demo
python demo_preprocessing.py
```

Kết quả lưu trong thư mục `demo_results/`

---

## 🧪 Kết quả kiểm thử

### ✅ Đã test thành công:
- [x] Module grayscale.py - Chuyển xám OK
- [x] Module smoothing.py - Làm mịn OK (Bilateral, Gaussian, Median)
- [x] API /api/preprocess - Hoạt động tốt
- [x] API /api/grayscale - Test OK
- [x] Demo với 3 ảnh mẫu - Tạo 21 files kết quả

### 📸 So sánh kết quả:

| Phương pháp | Đặc điểm | Dùng cho |
|------------|----------|---------|
| **Bilateral Filter** ⭐ | Giữ biên, loại nhiễu | **Sketch effect** (khuyên dùng) |
| Gaussian Blur | Làm mịn đều toàn bộ | Ảnh mịn chung |
| Median Blur | Loại nhiễu muối tiêu | Ảnh có nhiễu điểm |

---

## 🔗 Tích hợp 2 phần

### Cách 1: Frontend gọi 2 API tuần tự
```javascript
// Step 1: Preprocess (Người 1)
const preprocessed = await fetch('/api/preprocess', {
  method: 'POST',
  body: JSON.stringify({ image: base64Image })
});
const smoothImage = await preprocessed.json();

// Step 2: Sketch (Người 2)
const sketch = await fetch('/api/sketch', {
  method: 'POST',
  body: JSON.stringify({ image: smoothImage.image })
});
```

### Cách 2: Backend tự ghép (1 API)
```python
@app.route('/api/full-sketch', methods=['POST'])
def full_sketch():
    # Người 1
    gray = convert_to_grayscale(image)
    smooth = preprocess_for_sketch(gray)
    
    # Người 2
    edges = detect_edges(smooth)  # Hùng viết
    sketch = create_sketch(edges)  # Hùng viết
    
    return sketch
```

---

## 📊 Đánh giá

### ✅ Điểm mạnh:
- **Phân công rõ ràng**: Người 1 & 2 làm song song, không phụ thuộc
- **Độc lập 100%**: Mỗi người test riêng, không chặn nhau
- **Đúng yêu cầu đề bài**: Grayscale + Smoothing + Edge Detection
- **Áp dụng kỹ thuật tốt**: Bilateral Filter (edge-preserving)
- **API RESTful**: Dễ tích hợp với frontend
- **Có demo trực quan**: Lưu ảnh kết quả để so sánh

### 🎯 Đạt yêu cầu nghiệm thu:
- ✅ Tải/lưu ảnh (API nhận base64 hoặc file upload)
- ✅ Xử lý ảnh y tế, tự nhiên, công nghiệp (test với nhiều loại ảnh)
- ✅ Xem kết quả trực quan (API trả về ảnh base64, frontend hiển thị)
- ✅ Dùng Bilateral Filter (edge-preserving filter)

---

## 📝 Tài liệu tham khảo

- [Hướng dẫn chi tiết Người 1](HUONG_DAN_NGUOI_1.md)
- OpenCV Documentation: https://docs.opencv.org/
- Bilateral Filter: https://en.wikipedia.org/wiki/Bilateral_filter

---

## 👨‍💻 Tác giả

- **Người 1 (Hiến)**: Preprocessing (Grayscale + Smoothing) ✅
- **Người 2 (Hùng)**: Edge Detection + Sketch Effect ⏳

---

## 📞 Hỗ trợ

Gặp vấn đề kỹ thuật:
1. Kiểm tra Python virtual environment đã activate chưa
2. Kiểm tra packages đã cài đầy đủ: `pip list`
3. Kiểm tra server đang chạy: http://localhost:5000/health
4. Xem log lỗi trong terminal

---

**⭐ Good luck với dự án! 🚀**
