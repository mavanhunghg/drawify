# Drawify Backend - Preprocessing Module

## Tác giả
Hiến

## Chức năng
- Grayscale Conversion: Chuyển ảnh màu sang xám
- Image Smoothing: Bilateral Filter, Gaussian Blur, Median Blur

## API Endpoints

### POST `/api/preprocess`
Xử lý grayscale + smoothing

**Parameters:**
- `image`: base64 string hoặc file upload
- `method`: bilateral (default), gaussian, median
- `intensity`: light, medium (default), strong
- `use_opencv`: true (default), false

**Response:**
```json
{
  "success": true,
  "image": "data:image/png;base64,...",
  "message": "Xử lý thành công",
  "shape": [height, width]
}
```

### POST `/api/grayscale`
Chỉ chuyển sang grayscale

### GET `/health`
Kiểm tra server status

## Cài đặt

```bash
pip install -r requirements.txt
python app.py
```

Server: http://localhost:5000
