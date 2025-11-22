"""
Script đánh giá chất lượng sketch từ nhiều ảnh test
So sánh các phương pháp edge detection
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path

# Import modules
sys.path.append(os.path.dirname(__file__))
from image_processing.grayscale import convert_to_grayscale
from image_processing.smoothing import preprocess_for_sketch
from image_processing.sketch_effect import sketch_effect

def calculate_edge_density(edges):
    """Tính mật độ biên (số pixel trắng / tổng pixel)"""
    return np.sum(edges == 255) / edges.size

def calculate_contrast(image):
    """Tính độ tương phản (std deviation của intensity)"""
    return np.std(image)

def calculate_detail_score(edges):
    """
    Tính điểm chi tiết - Score cao hơn = nhiều chi tiết hơn
    Dựa vào: số contours, độ dài, độ phức tạp
    """
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return 0
    
    # Số contours (nhiều = chi tiết)
    num_contours = len(contours)
    
    # Tổng độ dài tất cả contours
    total_length = sum([cv2.arcLength(cnt, True) for cnt in contours])
    
    # Độ phức tạp trung bình (số điểm / contour)
    avg_complexity = np.mean([len(cnt) for cnt in contours])
    
    # Score kết hợp - scale để 40-50 là tốt
    score = (num_contours / 10) + (total_length / 500) + (avg_complexity / 5)
    return score

def evaluate_image(image_path, methods=['canny', 'sobel', 'laplacian', 'log']):
    """
    Đánh giá chất lượng sketch từ 1 ảnh với nhiều phương pháp
    """
    print(f"\n{'='*80}")
    print(f"📸 Đánh giá: {os.path.basename(image_path)}")
    print(f"{'='*80}")
    
    # Đọc ảnh (hỗ trợ AVIF, WEBP...)
    try:
        from PIL import Image
        import pillow_avif  # Enable AVIF support
        
        # Thử Pillow trước (hỗ trợ nhiều format)
        pil_image = Image.open(image_path)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    except:
        # Fallback: cv2.imread cho JPG/PNG
        image = cv2.imread(image_path)
    
    if image is None:
        print(f"❌ Không đọc được ảnh: {image_path}")
        return None
    
    h, w = image.shape[:2]
    print(f"📐 Kích thước: {w} × {h} pixels")
    print(f"📦 Dung lượng: {os.path.getsize(image_path) / 1024:.1f} KB")
    
    # Đánh giá từng phương pháp
    results = []
    
    for method in methods:
        try:
            # Tạo sketch
            sketch = sketch_effect(image, smoothing_method='bilateral', 
                                 intensity='medium', edge_method=method)
            
            # Tính metrics
            # Lấy edges (đảo ngược sketch để có edges trắng trên nền đen)
            edges = cv2.bitwise_not(sketch)
            
            edge_density = calculate_edge_density(edges)
            contrast = calculate_contrast(sketch)
            detail_score = calculate_detail_score(edges)
            
            # Tính overall score (0-100)
            # Công thức mới: Scale detail_score và normalize contrast
            # Detail score thường trong khoảng 0-50, contrast 0-130
            normalized_detail = min(detail_score * 2, 100)  # Scale lên 2x
            normalized_contrast = min((contrast / 130) * 100, 100)  # Normalize về 0-100
            
            overall_score = (
                normalized_detail * 0.50 +       # Chi tiết là quan trọng nhất
                normalized_contrast * 0.40 +     # Contrast cao = nét rõ
                (1 - edge_density) * 100 * 0.10  # Không quá nhiều nhiễu
            )
            overall_score = min(100, overall_score)  # Cap ở 100
            
            results.append({
                'method': method,
                'edge_density': edge_density,
                'contrast': contrast,
                'detail_score': detail_score,
                'overall_score': overall_score
            })
            
        except Exception as e:
            print(f"❌ Lỗi với {method}: {str(e)}")
            results.append({
                'method': method,
                'edge_density': 0,
                'contrast': 0,
                'detail_score': 0,
                'overall_score': 0
            })
    
    # In kết quả
    print(f"\n{'Phương pháp':<15} {'Chi tiết':<12} {'Tương phản':<15} {'Mật độ biên':<15} {'Tổng điểm':<12}")
    print(f"{'-'*80}")
    
    for r in results:
        # Icon đánh giá
        if r['overall_score'] >= 70:
            icon = "🏆"
        elif r['overall_score'] >= 50:
            icon = "✅"
        elif r['overall_score'] >= 30:
            icon = "⚠️"
        else:
            icon = "❌"
        
        print(f"{r['method']:<15} {r['detail_score']:<12.2f} {r['contrast']:<15.2f} "
              f"{r['edge_density']*100:<14.1f}% {icon} {r['overall_score']:<8.1f}/100")
    
    # Tìm phương pháp tốt nhất
    best = max(results, key=lambda x: x['overall_score'])
    print(f"\n🌟 Phương pháp tốt nhất: {best['method'].upper()} ({best['overall_score']:.1f}/100)")
    
    return results

def main():
    """Đánh giá tất cả ảnh test"""
    
    print("🎨 ĐÁNH GIÁ CHẤT LƯỢNG SKETCH - DRAWIFY")
    print("="*80)
    
    # Tìm tất cả ảnh trong thư mục sample_images
    test_dir = Path(__file__).parent / "sample_images"
    
    if not test_dir.exists():
        print(f"❌ Không tìm thấy thư mục: {test_dir}")
        print("Tạo ảnh test bằng: python create_test_images.py")
        return
    
    # Lấy tất cả file ảnh
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp', '*.avif']:
        image_files.extend(test_dir.glob(ext))
    
    if not image_files:
        print(f"❌ Không có ảnh nào trong {test_dir}")
        return
    
    print(f"📂 Tìm thấy {len(image_files)} ảnh test")
    
    # Đánh giá từng ảnh
    all_results = {}
    
    for img_path in sorted(image_files):
        results = evaluate_image(str(img_path))
        if results:
            all_results[img_path.name] = results
    
    # Tổng kết
    print(f"\n\n{'='*80}")
    print("📊 TỔNG KẾT ĐÁNH GIÁ")
    print(f"{'='*80}")
    
    # Tính điểm trung bình cho mỗi phương pháp
    methods = ['canny', 'sobel', 'laplacian', 'log']
    method_scores = {m: [] for m in methods}
    
    for img_name, results in all_results.items():
        for r in results:
            method_scores[r['method']].append(r['overall_score'])
    
    print(f"\n{'Phương pháp':<15} {'Điểm TB':<12} {'Đánh giá'}")
    print(f"{'-'*50}")
    
    rankings = []
    for method in methods:
        scores = method_scores[method]
        if scores:
            avg_score = np.mean(scores)
            rankings.append((method, avg_score))
            
            # Đánh giá
            if avg_score >= 70:
                rating = "🏆 Xuất sắc"
            elif avg_score >= 60:
                rating = "✅ Tốt"
            elif avg_score >= 50:
                rating = "⚠️ Trung bình"
            else:
                rating = "❌ Yếu"
            
            print(f"{method.upper():<15} {avg_score:<12.1f} {rating}")
    
    # Xếp hạng
    rankings.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🏆 XẾP HẠNG TỔNG THỂ:")
    for i, (method, score) in enumerate(rankings, 1):
        medal = ["🥇", "🥈", "🥉", "4️⃣"][i-1] if i <= 4 else ""
        print(f"   {medal} {i}. {method.upper():<12} - {score:.1f} điểm")
    
    print(f"\n{'='*80}")
    print("✨ Hoàn thành đánh giá!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
