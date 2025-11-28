"""
Script test tất cả ảnh trong sample_images
"""
import requests
import base64
import os
from pathlib import Path
import time

API_URL = "http://localhost:5000/api/preprocess"

def test_image(image_path):
    """Test một ảnh"""
    file_name = os.path.basename(image_path)
    file_size = os.path.getsize(image_path) / 1024  # KB
    
    print(f"\n{'='*60}")
    print(f"📸 Testing: {file_name}")
    print(f"📊 Size: {file_size:.2f} KB")
    print(f"{'='*60}")
    
    try:
        # Đọc ảnh
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Encode base64
        print("⏳ Encoding base64...")
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        base64_size = len(image_base64) / 1024
        print(f"✅ Base64 size: {base64_size:.2f} KB")
        
        # Call API
        print("⏳ Calling API...")
        start_time = time.time()
        
        response = requests.post(
            API_URL,
            json={
                "image": f"data:image/jpeg;base64,{image_base64}",
                "method": "bilateral",
                "intensity": "medium"
            },
            timeout=120  # 2 minutes timeout
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS in {elapsed:.2f}s")
            print(f"   Shape: {result.get('shape', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
        else:
            print(f"❌ FAILED with status {response.status_code} in {elapsed:.2f}s")
            print(f"   Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

def main():
    print("\n🚀 Testing All Images in sample_images/\n")
    
    # Lấy tất cả file ảnh
    image_dir = Path("backend/sample_images")
    image_files = []
    
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.avif']:
        image_files.extend(image_dir.glob(ext))
    
    if not image_files:
        print("❌ No images found!")
        return
    
    print(f"Found {len(image_files)} images\n")
    
    # Test từng ảnh
    results = []
    for img_path in sorted(image_files, key=lambda x: x.stat().st_size):
        try:
            test_image(str(img_path))
            results.append((img_path.name, "✅ PASS"))
        except Exception as e:
            results.append((img_path.name, f"❌ FAIL: {str(e)}"))
        
        time.sleep(1)  # Chờ 1s giữa các test
    
    # Summary
    print(f"\n\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    for name, status in results:
        print(f"{status:20} {name}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

