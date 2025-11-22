"""
Script tạo ảnh test cho demo - Các loại ảnh khác nhau
Tạo ảnh minh họa cho: y tế, tự nhiên, công nghiệp, kiến trúc, chân dung
"""

import cv2
import numpy as np
import os

def create_medical_xray():
    """Tạo ảnh giả lập X-ray y tế (xương tay)"""
    img = np.ones((600, 400), dtype=np.uint8) * 240
    
    # Vẽ xương bàn tay
    # Xương cổ tay
    cv2.rectangle(img, (150, 50), (250, 100), 180, -1)
    
    # 5 ngón tay (xương ngón)
    fingers = [
        [(180, 100), (170, 250)],  # Ngón cái
        [(200, 100), (195, 300)],  # Ngón trỏ
        [(220, 100), (220, 320)],  # Ngón giữa
        [(240, 100), (240, 310)],  # Ngón áp út
        [(260, 100), (255, 280)],  # Ngón út
    ]
    
    for start, end in fingers:
        cv2.line(img, start, end, 160, 15)
        # Khớp ngón
        cv2.circle(img, (start[0], start[1] + 50), 10, 140, -1)
        cv2.circle(img, (end[0], end[1] - 30), 8, 140, -1)
    
    # Bàn tay
    cv2.ellipse(img, (210, 150), (60, 80), 0, 0, 180, 170, -1)
    
    # Thêm noise giả lập X-ray
    noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)
    
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

def create_nature_landscape():
    """Tạo ảnh phong cảnh tự nhiên"""
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Bầu trời (gradient xanh)
    for i in range(250):
        color = (255 - i//3, 220 - i//4, 150 + i//2)
        cv2.line(img, (0, i), (800, i), color, 1)
    
    # Núi xa (xám xanh)
    mountain1 = np.array([[0, 250], [200, 150], [400, 200], [600, 100], [800, 180], [800, 250], [0, 250]])
    cv2.fillPoly(img, [mountain1], (120, 140, 100))
    
    # Núi gần (xanh đậm hơn)
    mountain2 = np.array([[0, 300], [150, 220], [300, 250], [500, 180], [700, 240], [800, 280], [800, 300], [0, 300]])
    cv2.fillPoly(img, [mountain2], (80, 110, 60))
    
    # Đồng cỏ (gradient xanh lá)
    for i in range(250, 600):
        intensity = int(50 + (i - 250) * 0.3)
        color = (intensity, 180 - (i - 250)//5, intensity//2)
        cv2.line(img, (0, i), (800, i), color, 1)
    
    # Cây
    trees_x = [100, 250, 350, 500, 650, 720]
    for x in trees_x:
        # Thân cây
        cv2.rectangle(img, (x-10, 400), (x+10, 500), (50, 70, 30), -1)
        # Tán cây
        cv2.ellipse(img, (x, 380), (40, 60), 0, 0, 360, (40, 100, 20), -1)
        cv2.ellipse(img, (x-20, 400), (30, 45), 0, 0, 360, (45, 105, 25), -1)
        cv2.ellipse(img, (x+20, 400), (30, 45), 0, 0, 360, (45, 105, 25), -1)
    
    # Mặt trời
    cv2.circle(img, (650, 100), 40, (100, 200, 255), -1)
    cv2.circle(img, (650, 100), 45, (120, 210, 255), 3)
    
    # Mây
    clouds = [(150, 80), (400, 60), (600, 90)]
    for cx, cy in clouds:
        cv2.ellipse(img, (cx, cy), (50, 25), 0, 0, 360, (240, 240, 240), -1)
        cv2.ellipse(img, (cx+30, cy), (40, 20), 0, 0, 360, (245, 245, 245), -1)
        cv2.ellipse(img, (cx-30, cy), (40, 20), 0, 0, 360, (245, 245, 245), -1)
    
    return img

def create_industrial_factory():
    """Tạo ảnh nhà máy công nghiệp"""
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Bầu trời xám
    for i in range(300):
        color = (200 - i//4, 200 - i//4, 210 - i//4)
        cv2.line(img, (0, i), (800, i), color, 1)
    
    # Mặt đất
    cv2.rectangle(img, (0, 400), (800, 600), (120, 120, 110), -1)
    
    # Nhà máy 1
    cv2.rectangle(img, (50, 250), (250, 400), (100, 100, 100), -1)
    cv2.rectangle(img, (50, 250), (250, 400), (70, 70, 70), 3)
    
    # Ống khói
    cv2.rectangle(img, (90, 150), (120, 250), (80, 80, 80), -1)
    cv2.rectangle(img, (180, 180), (210, 250), (80, 80, 80), -1)
    
    # Khói
    for i in range(5):
        cv2.ellipse(img, (105, 120 - i*20), (15+i*3, 12+i*2), 0, 0, 360, (180-i*10, 180-i*10, 180-i*10), -1)
        cv2.ellipse(img, (195, 150 - i*20), (15+i*3, 12+i*2), 0, 0, 360, (180-i*10, 180-i*10, 180-i*10), -1)
    
    # Cửa sổ
    for i in range(3):
        for j in range(5):
            cv2.rectangle(img, (70 + j*35, 270 + i*40), (95 + j*35, 300 + i*40), (200, 220, 150), -1)
    
    # Nhà máy 2 (lớn hơn)
    cv2.rectangle(img, (300, 200), (600, 400), (90, 90, 90), -1)
    cv2.rectangle(img, (300, 200), (600, 400), (60, 60, 60), 3)
    
    # Mái nhà
    roof = np.array([[280, 200], [450, 150], [620, 200]])
    cv2.fillPoly(img, [roof], (70, 70, 70))
    cv2.polylines(img, [roof], True, (50, 50, 50), 3)
    
    # Cửa sổ nhà máy 2
    for i in range(4):
        for j in range(8):
            cv2.rectangle(img, (320 + j*35, 220 + i*40), (345 + j*35, 250 + i*40), (180, 200, 140), -1)
    
    # Cửa lớn
    cv2.rectangle(img, (420, 320), (520, 400), (60, 60, 60), -1)
    cv2.rectangle(img, (420, 320), (520, 400), (40, 40, 40), 3)
    
    # Bồn chứa
    cv2.ellipse(img, (700, 350), (60, 80), 0, 0, 360, (110, 110, 110), -1)
    cv2.ellipse(img, (700, 350), (60, 80), 0, 0, 360, (80, 80, 80), 3)
    cv2.rectangle(img, (640, 340), (760, 400), (110, 110, 110), -1)
    cv2.rectangle(img, (640, 340), (760, 400), (80, 80, 80), 3)
    
    # Đường ống
    cv2.rectangle(img, (250, 300), (300, 320), (100, 100, 100), -1)
    cv2.rectangle(img, (600, 280), (640, 300), (100, 100, 100), -1)
    
    return img

def create_architecture_building():
    """Tạo ảnh kiến trúc tòa nhà"""
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Bầu trời xanh nhạt
    for i in range(400):
        color = (255 - i//5, 240 - i//6, 200 + i//8)
        cv2.line(img, (0, i), (800, i), color, 1)
    
    # Mặt đất
    cv2.rectangle(img, (0, 500), (800, 600), (140, 140, 130), -1)
    
    # Tòa nhà chính (hiện đại)
    cv2.rectangle(img, (200, 150), (500, 500), (180, 180, 180), -1)
    cv2.rectangle(img, (200, 150), (500, 500), (120, 120, 120), 3)
    
    # Cửa sổ tòa nhà (lưới)
    for i in range(10):
        for j in range(5):
            if (i + j) % 2 == 0:
                cv2.rectangle(img, (220 + j*55, 170 + i*33), (265 + j*55, 195 + i*33), (100, 150, 200), -1)
            else:
                cv2.rectangle(img, (220 + j*55, 170 + i*33), (265 + j*55, 195 + i*33), (80, 130, 180), -1)
    
    # Tòa nhà bên trái (thấp hơn)
    cv2.rectangle(img, (50, 300), (200, 500), (160, 160, 160), -1)
    cv2.rectangle(img, (50, 300), (200, 500), (100, 100, 100), 3)
    
    for i in range(6):
        for j in range(3):
            cv2.rectangle(img, (65 + j*45, 320 + i*30), (100 + j*45, 345 + i*30), (120, 160, 190), -1)
    
    # Tòa nhà bên phải (cao hơn)
    cv2.rectangle(img, (500, 100), (650, 500), (170, 170, 170), -1)
    cv2.rectangle(img, (500, 100), (650, 500), (110, 110, 110), 3)
    
    for i in range(12):
        for j in range(3):
            cv2.rectangle(img, (515 + j*45, 120 + i*31), (550 + j*45, 145 + i*31), (90, 140, 180), -1)
    
    # Cửa vào chính
    cv2.rectangle(img, (320, 420), (380, 500), (80, 80, 80), -1)
    cv2.rectangle(img, (320, 420), (380, 500), (60, 60, 60), 3)
    
    # Mái tòa nhà chính (hiện đại)
    cv2.rectangle(img, (190, 140), (510, 150), (150, 150, 150), -1)
    
    # Cây xanh trang trí
    cv2.ellipse(img, (120, 480), (25, 35), 0, 0, 360, (60, 120, 40), -1)
    cv2.rectangle(img, (115, 480), (125, 500), (80, 60, 40), -1)
    
    cv2.ellipse(img, (580, 480), (25, 35), 0, 0, 360, (60, 120, 40), -1)
    cv2.rectangle(img, (575, 480), (585, 500), (80, 60, 40), -1)
    
    return img

def create_portrait_face():
    """Tạo ảnh chân dung đơn giản"""
    img = np.ones((600, 500, 3), dtype=np.uint8) * 255
    
    # Nền gradient
    for i in range(600):
        color = (240 - i//5, 240 - i//4, 250 - i//6)
        cv2.line(img, (0, i), (500, i), color, 1)
    
    # Đầu (hình elip)
    cv2.ellipse(img, (250, 280), (120, 150), 0, 0, 360, (230, 200, 180), -1)
    cv2.ellipse(img, (250, 280), (120, 150), 0, 0, 360, (200, 170, 150), 2)
    
    # Tóc
    cv2.ellipse(img, (250, 200), (130, 100), 0, 180, 360, (50, 40, 30), -1)
    cv2.ellipse(img, (250, 200), (130, 100), 0, 180, 360, (40, 30, 20), 2)
    
    # Mắt trái
    cv2.ellipse(img, (210, 260), (25, 15), 0, 0, 360, (255, 255, 255), -1)
    cv2.circle(img, (215, 260), 12, (100, 80, 60), -1)
    cv2.circle(img, (218, 257), 7, (30, 20, 10), -1)
    cv2.circle(img, (220, 255), 3, (255, 255, 255), -1)
    
    # Mắt phải
    cv2.ellipse(img, (290, 260), (25, 15), 0, 0, 360, (255, 255, 255), -1)
    cv2.circle(img, (285, 260), 12, (100, 80, 60), -1)
    cv2.circle(img, (282, 257), 7, (30, 20, 10), -1)
    cv2.circle(img, (280, 255), 3, (255, 255, 255), -1)
    
    # Lông mày
    cv2.ellipse(img, (210, 240), (30, 8), -10, 0, 180, (60, 50, 40), 3)
    cv2.ellipse(img, (290, 240), (30, 8), 10, 0, 180, (60, 50, 40), 3)
    
    # Mũi
    cv2.line(img, (250, 270), (245, 310), (200, 170, 150), 2)
    cv2.ellipse(img, (240, 315), (8, 5), 0, 0, 180, (200, 170, 150), 1)
    cv2.ellipse(img, (255, 315), (8, 5), 0, 0, 180, (200, 170, 150), 1)
    
    # Miệng (nụ cười)
    cv2.ellipse(img, (250, 350), (40, 25), 0, 0, 180, (180, 100, 100), -1)
    cv2.ellipse(img, (250, 345), (40, 20), 0, 0, 180, (220, 180, 180), -1)
    cv2.ellipse(img, (250, 350), (40, 25), 0, 0, 180, (150, 80, 80), 2)
    
    # Tai trái
    cv2.ellipse(img, (140, 280), (20, 35), 0, 0, 360, (220, 190, 170), -1)
    cv2.ellipse(img, (145, 280), (12, 25), 0, 0, 360, (200, 170, 150), -1)
    
    # Tai phải
    cv2.ellipse(img, (360, 280), (20, 35), 0, 0, 360, (220, 190, 170), -1)
    cv2.ellipse(img, (355, 280), (12, 25), 0, 0, 360, (200, 170, 150), -1)
    
    # Cổ
    cv2.rectangle(img, (210, 410), (290, 500), (220, 190, 170), -1)
    cv2.rectangle(img, (210, 410), (290, 500), (190, 160, 140), 2)
    
    # Vai (áo)
    points = np.array([[150, 500], [210, 450], (290, 450), [350, 500]])
    cv2.fillPoly(img, [points], (100, 120, 150))
    cv2.polylines(img, [points], False, (80, 100, 130), 2)
    
    return img

def create_circuit_board():
    """Tạo ảnh mạch điện tử"""
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Nền xanh lá (PCB)
    img[:] = (80, 120, 60)
    
    # Các đường mạch (dây đồng)
    circuit_lines = [
        [(50, 100), (200, 100)], [(200, 100), (200, 300)], [(200, 300), (400, 300)],
        [(100, 200), (300, 200)], [(300, 200), (300, 400)], [(300, 400), (500, 400)],
        [(400, 150), (600, 150)], [(600, 150), (600, 350)], [(600, 350), (750, 350)],
        [(150, 450), (350, 450)], [(350, 450), (350, 550)], [(450, 500), (650, 500)],
    ]
    
    for start, end in circuit_lines:
        cv2.line(img, start, end, (200, 180, 100), 4)
        cv2.line(img, start, end, (220, 200, 120), 2)
    
    # IC chips (màu đen)
    chips = [(120, 180), (280, 320), (520, 250), (420, 480), (680, 400)]
    for x, y in chips:
        cv2.rectangle(img, (x-30, y-20), (x+30, y+20), (30, 30, 30), -1)
        cv2.rectangle(img, (x-30, y-20), (x+30, y+20), (200, 180, 100), 2)
        # Chân IC
        for i in range(-3, 4):
            cv2.line(img, (x-30, y + i*6), (x-35, y + i*6), (200, 180, 100), 2)
            cv2.line(img, (x+30, y + i*6), (x+35, y + i*6), (200, 180, 100), 2)
    
    # Tụ điện (hình trụ)
    capacitors = [(200, 200), (400, 300), (350, 450), (600, 250)]
    for x, y in capacitors:
        cv2.circle(img, (x, y), 18, (180, 180, 180), -1)
        cv2.circle(img, (x, y), 18, (150, 150, 150), 2)
        cv2.rectangle(img, (x-3, y-20), (x+3, y-25), (200, 180, 100), -1)
    
    # Điện trở (hình chữ nhật nhỏ)
    resistors = [(150, 100), (250, 300), (450, 150), (580, 350), (280, 450)]
    for x, y in resistors:
        cv2.rectangle(img, (x-20, y-5), (x+20, y+5), (200, 160, 120), -1)
        cv2.rectangle(img, (x-20, y-5), (x+20, y+5), (150, 120, 80), 2)
        # Dải màu
        for i in range(4):
            cv2.line(img, (x-15+i*10, y-5), (x-15+i*10, y+5), (100, 50, 30), 2)
    
    # LED
    leds = [(200, 100), (300, 400), (600, 150), (500, 400)]
    for x, y in leds:
        cv2.circle(img, (x, y), 10, (50, 50, 200), -1)
        cv2.circle(img, (x, y), 10, (200, 180, 100), 2)
    
    # Connector (cổng kết nối)
    cv2.rectangle(img, (50, 50), (100, 80), (40, 40, 40), -1)
    cv2.rectangle(img, (50, 50), (100, 80), (200, 180, 100), 2)
    for i in range(5):
        cv2.circle(img, (60 + i*8, 65), 3, (220, 200, 120), -1)
    
    return img

# ============================================
# MAIN - TẠO TẤT CẢ ẢNH TEST
# ============================================

def main():
    """Tạo tất cả ảnh test và lưu vào thư mục"""
    
    # Tạo thư mục
    output_dir = "sample_images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("🎨 Đang tạo ảnh test cho demo...")
    print("=" * 50)
    
    # Tạo và lưu từng loại ảnh
    images = [
        ("medical_xray.png", create_medical_xray(), "Ảnh X-ray y tế (xương tay)"),
        ("nature_landscape.png", create_nature_landscape(), "Phong cảnh tự nhiên (núi, cây)"),
        ("industrial_factory.png", create_industrial_factory(), "Nhà máy công nghiệp"),
        ("architecture_building.png", create_architecture_building(), "Kiến trúc tòa nhà"),
        ("portrait_face.png", create_portrait_face(), "Chân dung khuôn mặt"),
        ("circuit_board.png", create_circuit_board(), "Mạch điện tử PCB"),
    ]
    
    for filename, image, description in images:
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, image)
        print(f"✅ Đã tạo: {filename:30} - {description}")
    
    print("=" * 50)
    print(f"✨ Hoàn thành! Đã tạo {len(images)} ảnh test trong thư mục '{output_dir}/'")
    print("\n📋 Các loại ảnh đã tạo:")
    print("   1. Y tế: medical_xray.png")
    print("   2. Tự nhiên: nature_landscape.png")
    print("   3. Công nghiệp: industrial_factory.png")
    print("   4. Kiến trúc: architecture_building.png")
    print("   5. Chân dung: portrait_face.png")
    print("   6. Điện tử: circuit_board.png")
    print("\n🚀 Bạn có thể dùng các ảnh này để test ứng dụng!")

if __name__ == "__main__":
    main()
