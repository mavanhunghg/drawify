# 🎨 Drawify Backend - Preprocessing Module

## 👤 Người thực hiện: Hiến

## 📚 Đề tài: Xây dựng phần mềm chuyển ảnh thành tranh vẽ - PHẦN TIỀN XỬ LÝ

### 🎯 Chức năng:
- ✅ Chuyển đổi ảnh màu sang xám (Grayscale Conversion)
- ✅ Làm mịn ảnh với 3 phương pháp:
  - **Bilateral Filter** ⭐ KHUYÊN DÙNG (giữ biên, loại nhiễu)
  - Gaussian Blur (làm mịn đều)
  - Median Blur (loại nhiễu muối tiêu)
- ✅ 3 mức độ: light, medium, strong

### ⚠️ **QUAN TRỌNG: KHÔNG DÙNG OPENCV**
Code được viết **hoàn toàn thủ công**, chỉ dùng:
- ✅ NumPy (array operations, math)
- ✅ PIL/Pillow (đọc/ghi ảnh)
- ✅ Flask (API server)

---

## 📦 Cấu trúc dự án

```
backend/
├── app.py                          # Flask API server (chỉ Hiến)
├── requirements.txt                # NumPy + Pillow + Flask
├── test_hiến.py                    # Test file độc lập
├── README.md                       # File này
├── image_processing/
│   ├── __init__.py
│   ├── grayscale.py                # Chuyển xám (CODE THỦ CÔNG)
│   └── smoothing.py                # Làm mịn (CODE THỦ CÔNG)
├── utils/
│   ├── __init__.py
│   ├── convolution.py              # Helper: 2D convolution
│   └── image_io.py                 # Helper: Đọc/ghi ảnh
└── sample_images/                   # Ảnh test
```

---

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Test module (không cần server)

```bash
python test_hiến.py
```

### 3. Chạy API server

```bash
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

---

## 📡 API Endpoints

### 1. `/api/preprocess` - Tiền xử lý ảnh

**Chức năng**: Grayscale + Smoothing

**Method**: POST

**Input** (JSON hoặc FormData):
```json
{
  "image": "base64_string_hoặc_file_upload",
  "method": "bilateral",  // bilateral, gaussian, median
  "intensity": "medium"    // light, medium, strong
}
```

**Output**:
```json
{
  "success": true,
  "image": "data:image/png;base64,...",
  "message": "Xử lý thành công với bilateral filter (medium)",
  "shape": [height, width],
  "method": "bilateral",
  "intensity": "medium"
}
```

### 2. `/api/grayscale` - Chỉ chuyển xám

**Chức năng**: Test riêng grayscale (không smoothing)

**Method**: POST

**Input**:
```json
{
  "image": "base64_string_hoặc_file_upload"
}
```

**Output**:
```json
{
  "success": true,
  "image": "data:image/png;base64,...",
  "message": "Chuyển sang xám thành công",
  "shape": [height, width]
}
```

### 3. `/` - Trang chủ API

**Method**: GET

**Output**: Thông tin API

### 4. `/health` - Health check

**Method**: GET

**Output**: Trạng thái server

---

## 🔬 Chi tiết kỹ thuật

### 1. Grayscale Conversion (`grayscale.py`)

**Công thức**: Weighted Average (ITU-R BT.601)
```
Gray = 0.299*R + 0.587*G + 0.114*B
```

**Code thủ công**:
```python
def convert_to_grayscale(image):
    r = image[:, :, 0].astype(np.float32)
    g = image[:, :, 1].astype(np.float32)
    b = image[:, :, 2].astype(np.float32)
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    return np.clip(gray, 0, 255).astype(np.uint8)
```

### 2. Smoothing (`smoothing.py`)

#### a. Bilateral Filter ⭐ TỐT NHẤT

**Đặc điểm**:
- Làm mịn nhiễu nhưng GIỮ SẮC NÉT cạnh/biên
- Rất tốt cho bài tập sketch (cần giữ biên)

**Thuật toán**:
1. Với mỗi pixel, xét các pixel lân cận trong radius `d`
2. Tính weight dựa trên:
   - Khoảng cách không gian: `exp(-||p-q||²/(2σs²))`
   - Khác biệt màu: `exp(-||I(p)-I(q)||²/(2σr²))`
3. Weighted average

**Tham số**:
- `d`: Đường kính vùng lân cận (9 mặc định)
- `sigma_color`: Sigma cho màu sắc (75)
- `sigma_space`: Sigma cho không gian (75)

**Code**:
```python
def apply_bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
    # CODE THỦ CÔNG - không dùng OpenCV
    # ... (xem chi tiết trong file)
```

#### b. Gaussian Blur

**Đặc điểm**: Làm mịn đều, giảm nhiễu Gaussian

**Công thức kernel**:
```
G(x,y) = (1/(2πσ²)) * exp(-(x²+y²)/(2σ²))
```

#### c. Median Blur

**Đặc điểm**: Loại bỏ nhiễu muối tiêu (salt-and-pepper noise)

**Thuật toán**: Lấy giá trị median trong window kích thước `kernel_size`

---

## ✅ Kết quả test

```
TEST 1: GRAYSCALE CONVERSION          ✅ PASSED
TEST 2: GAUSSIAN BLUR                 ✅ PASSED
TEST 3: MEDIAN BLUR                   ✅ PASSED
TEST 4: BILATERAL FILTER              ✅ PASSED (QUAN TRỌNG NHẤT)
TEST 5: PREPROCESS_FOR_SKETCH         ✅ PASSED
TEST 6: TEST VỚI ẢNH THẬT             ✅ PASSED
```

**Tất cả test đều PASSED!** ✅

---

## 📊 So sánh các phương pháp

| Phương pháp | Ưu điểm | Nhược điểm | Dùng khi nào |
|------------|---------|------------|--------------|
| **Bilateral** ⭐ | Giữ biên, loại nhiễu tốt | Chậm hơn Gaussian | **KHUYÊN DÙNG** cho sketch |
| Gaussian | Nhanh, mịn đều | Làm mờ biên | Ảnh ít chi tiết |
| Median | Tốt với nhiễu muối tiêu | Không giữ biên tốt | Ảnh có nhiễu đốm |

---

## 🎯 Kết luận

Module preprocessing của Hiến đã:
- ✅ Hoàn thành 100% yêu cầu
- ✅ Code thủ công không dùng OpenCV
- ✅ Bilateral Filter hoạt động xuất sắc (edge-preserving)
- ✅ API độc lập, test thành công
- ✅ Sẵn sàng tích hợp với frontend

**Phương pháp khuyên dùng**: `bilateral` với intensity `medium` hoặc `strong`

---

## 📞 Liên hệ

**Người thực hiện**: Hiến  
**Phần**: Preprocessing (Grayscale + Smoothing)  
**Trạng thái**: ✅ Hoàn thành, đã test


