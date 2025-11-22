"""
Script demo và lưu ảnh kết quả so sánh 4 phương pháp
"""

import cv2
import numpy as np
import os
from pathlib import Path
import sys

sys.path.append(os.path.dirname(__file__))
from image_processing.sketch_effect import sketch_effect

def create_comparison_grid(image_path, output_path):
    """
    Tạo lưới so sánh 4 phương pháp: Original + Canny + Sobel + Laplacian + LoG
    """
    # Đọc ảnh
    try:
        from PIL import Image
        import pillow_avif
        
        pil_image = Image.open(image_path)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    except:
        image = cv2.imread(image_path)
    
    if image is None:
        print(f"❌ Không đọc được: {image_path}")
        return False
    
    # Resize nếu quá lớn (để tiết kiệm bộ nhớ)
    h, w = image.shape[:2]
    max_size = 800
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        image = cv2.resize(image, None, fx=scale, fy=scale)
        h, w = image.shape[:2]
    
    # Tạo sketch với 4 phương pháp
    methods = {
        'Canny': 'canny',
        'Sobel': 'sobel', 
        'Laplacian': 'laplacian',
        'LoG': 'log'
    }
    
    sketches = {}
    for name, method in methods.items():
        print(f"  ⏳ Đang xử lý {name}...")
        sketch = sketch_effect(image, smoothing_method='bilateral', 
                             intensity='medium', edge_method=method)
        sketches[name] = sketch
    
    # Tạo lưới 2x3: [Original] [Canny] [Sobel]
    #                [Empty]   [Laplacian] [LoG]
    
    # Chuyển original sang grayscale để cùng format
    original_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Thêm text label
    def add_label(img, text, score=None):
        img_with_label = img.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Vẽ nền cho text
        text_display = f"{text}"
        if score:
            text_display += f" ({score:.1f})"
        
        (text_w, text_h), _ = cv2.getTextSize(text_display, font, 0.7, 2)
        cv2.rectangle(img_with_label, (5, 5), (text_w + 15, text_h + 20), (0, 0, 0), -1)
        cv2.putText(img_with_label, text_display, (10, text_h + 15), 
                   font, 0.7, (255, 255, 255), 2)
        return img_with_label
    
    # Điểm số
    scores = {
        'Canny': 66.2,
        'Sobel': 54.6,
        'Laplacian': 66.5,
        'LoG': 65.6
    }
    
    # Thêm label
    original_labeled = add_label(original_gray, "Original")
    canny_labeled = add_label(sketches['Canny'], "Canny", scores['Canny'])
    sobel_labeled = add_label(sketches['Sobel'], "Sobel", scores['Sobel'])
    laplacian_labeled = add_label(sketches['Laplacian'], "Laplacian", scores['Laplacian'])
    log_labeled = add_label(sketches['LoG'], "LoG", scores['LoG'])
    
    # Tạo ảnh trống cùng kích thước
    empty = np.ones_like(original_gray) * 255
    
    # Ghép hàng 1: Original | Canny | Sobel
    row1 = np.hstack([original_labeled, canny_labeled, sobel_labeled])
    
    # Ghép hàng 2: Empty | Laplacian | LoG
    row2 = np.hstack([empty, laplacian_labeled, log_labeled])
    
    # Ghép thành lưới
    grid = np.vstack([row1, row2])
    
    # Thêm tiêu đề lớn
    header_height = 60
    header = np.ones((header_height, grid.shape[1]), dtype=np.uint8) * 240
    
    title_text = "DRAWIFY - So sanh 4 phuong phap Edge Detection"
    (title_w, title_h), _ = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
    title_x = (grid.shape[1] - title_w) // 2
    cv2.putText(header, title_text, (title_x, 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    
    # Ghép header + grid
    final = np.vstack([header, grid])
    
    # Lưu file
    cv2.imwrite(output_path, final)
    print(f"  ✅ Đã lưu: {output_path}")
    
    return True

def main():
    """Tạo ảnh so sánh cho tất cả ảnh test"""
    
    print("🎨 DRAWIFY - TẠO ẢNH SO SÁNH")
    print("="*80)
    
    # Thư mục
    test_dir = Path(__file__).parent / "sample_images"
    output_dir = Path(__file__).parent / "comparison_results"
    output_dir.mkdir(exist_ok=True)
    
    # Lấy TẤT CẢ ảnh trong thư mục
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp', '*.avif']:
        image_files.extend(test_dir.glob(ext))
    
    if not image_files:
        print(f"❌ Không có ảnh nào trong {test_dir}")
        return
    
    print(f"📂 Tìm thấy {len(image_files)} ảnh test\n")
    
    success_count = 0
    
    for img_path in sorted(image_files):
        print(f"📸 Xử lý: {img_path.name}")
        
        output_name = f"comparison_{img_path.stem}.jpg"
        output_path = str(output_dir / output_name)
        
        if create_comparison_grid(str(img_path), output_path):
            success_count += 1
    
    print(f"\n{'='*80}")
    print(f"✨ Hoàn thành! Đã tạo {success_count} ảnh so sánh")
    print(f"📂 Thư mục kết quả: {output_dir}")
    print(f"{'='*80}\n")
    
    # Mở thư mục kết quả
    print("💡 Mở thư mục kết quả để xem...")
    os.startfile(output_dir)

if __name__ == "__main__":
    main()
