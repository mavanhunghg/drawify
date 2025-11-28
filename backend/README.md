# Drawify Backend - Photo to Sketch

## Team
- **Hiến**: Grayscale Conversion + Image Smoothing (Preprocessing)
- **Hùng**: Edge Detection + Sketch Effect

## Features
- ✅ Grayscale Conversion (weighted average)
- ✅ Image Smoothing (Bilateral, Gaussian, Median)
- ✅ Edge Detection (Canny, Sobel, Laplacian)
- ✅ Sketch Effect (Pencil, Natural, Enhanced)

## API Endpoints

### POST `/api/preprocess` (Hiến)
Grayscale + Smoothing preprocessing

**Parameters:**
- `image`: base64 string hoặc file upload
- `method`: bilateral (default), gaussian, median
- `intensity`: light, medium (default), strong

### POST `/api/sketch` (Hùng)
Edge Detection + Sketch Effect

**Parameters:**
- `image`: base64 string
- `smoothing_method`: bilateral (default)
- `intensity`: light, medium (default), strong
- `edge_method`: canny (default), sobel, laplacian
- `detail_level`: pencil (default), natural, medium, enhanced

### POST `/api/full-pipeline` (Hiến + Hùng)
Full pipeline: Preprocessing → Edge Detection → Sketch

**Parameters:**
- `image`: base64 string
- `smoothing_method`: bilateral (default)
- `intensity`: light (default), medium, strong
- `edge_method`: canny (default), sobel, laplacian
- `detail_level`: pencil (default), natural, enhanced

**Response:**
```json
{
  "success": true,
  "image": "data:image/png;base64,...",
  "message": "Success",
  "shape": [height, width],
  "pipeline": {
    "preprocessing": {...},
    "sketch": {...}
  }
}
```

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Server: http://localhost:5000

## Tech Stack
- NumPy, OpenCV, Pillow
- Flask + CORS
- Custom algorithms with OpenCV optimization
