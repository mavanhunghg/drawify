# Drawify

Convert photos to paintings/sketches


## Team
- **Hiến**: Grayscale Conversion + Image Smoothing
- **Hùng**: Edge Detection + Sketch Effect

## Features
- Grayscale Conversion
- Image Smoothing (Bilateral, Gaussian, Median)
- Edge Detection (Sobel, Laplacian, Canny)
- Sketch Effect (Dodge blending)

## Structure

```
drawify/
├── backend/          # Flask API (Python)
│   ├── app.py
│   ├── image_processing/
│   └── utils/
└── frontend/         # React UI
    └── src/
```

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Usage
1. Start backend: http://localhost:5000
2. Start frontend: http://localhost:5173
3. Upload image and process

## Tech Stack
- Backend: Flask, NumPy, OpenCV, Pillow, Scipy
- Frontend: React, Vite
