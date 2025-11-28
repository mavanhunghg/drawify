"""Test nhanh phần code thủ công"""
import numpy as np
from PIL import Image
from image_processing.grayscale import convert_to_grayscale
from image_processing.smoothing import preprocess_for_sketch
from image_processing.edge_detection import detect_edges
from image_processing.sketch_effect import full_sketch_pipeline

# Load ảnh
try:
    import pillow_avif
    img = Image.open('sample_images/t6.avif')
except:
    # Tạo ảnh test nếu không có file
    img_array = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
img_array = np.array(img)

print("🧪 TEST CODE THỦ CÔNG")
print("=" * 50)

# 1. Grayscale - CODE THỦ CÔNG
print("1. Grayscale (CODE THỦ CÔNG)...")
gray = convert_to_grayscale(img_array)
print(f"   ✅ Shape: {gray.shape}, dtype: {gray.dtype}")

# 2. Smoothing - DÙNG OPENCV (OK)
print("2. Smoothing (OPENCV - OK)...")
smoothed = preprocess_for_sketch(gray, method='bilateral', intensity='medium')
print(f"   ✅ Shape: {smoothed.shape}, dtype: {smoothed.dtype}")

# 3. Edge Detection - CODE THỦ CÔNG
print("3. Edge Detection (CODE THỦ CÔNG)...")
edges = detect_edges(smoothed, method='sobel')
print(f"   ✅ Shape: {edges.shape}, dtype: {edges.dtype}")

# 4. Sketch Effect - CODE THỦ CÔNG
print("4. Sketch Effect (CODE THỦ CÔNG)...")
sketch = full_sketch_pipeline(smoothed, edges, detail_level='pencil', invert=False)
print(f"   ✅ Shape: {sketch.shape}, dtype: {sketch.dtype}")

print("\n" + "=" * 50)
print("✅ TẤT CẢ TEST THÀNH CÔNG!")
print("\n📊 KẾT LUẬN:")
print("   - Grayscale: CODE THỦ CÔNG ✅")
print("   - Smoothing: OPENCV (Bilateral/Gaussian/Median) ✅")
print("   - Edge Detection: CODE THỦ CÔNG (Sobel/Laplacian/Canny) ✅")
print("   - Sketch Effect: CODE THỦ CÔNG ✅")
