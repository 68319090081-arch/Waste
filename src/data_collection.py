import os
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

# Kaggle Dataset
DATASET = "phenomsg/waste-classification"

# Folder สำหรับเก็บ Dataset
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
# ====== ตั้งค่าฟอนต์ ======
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Tahoma', 'DejaVu Sans']
plt.style.use('ggplot')

# ==================================================
# ✅ ที่อยู่อัตโนมัติ — ใช้ได้กับทุกเครื่อง ไม่ต้องแก้อะไร!
# ==================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
image_dir = os.path.join(PROJECT_ROOT, "data")

# ตรวจสอบโฟลเดอร์
if not os.path.exists(image_dir):
    print("=" * 70)
    print("❌ ERROR: หาโฟลเดอร์ข้อมูลไม่เจอ!")
    print(f"👉 ค้นหาที่: {image_dir}")
    print("💡 ตรวจสอบว่ามีโฟลเดอร์ data/ ไว้ข้างนอกโฟลเดอร์ src/")
    print("=" * 70)
    exit()

print("=" * 70)
print(f"✅ พบข้อมูลที่: {image_dir}")
print("🔍 กำลังสแกนรูปภาพ... กรุณารอสักครู่...")
print("=" * 70)

# ====== นามสกุลไฟล์ที่ยอมรับ ======
image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

# ====== ตัวแปรเก็บข้อมูล ======
main_categories = {}
sub_categories = {}
image_info = []
corrupted_files = []
grayscale_count = 0
total_images = 0

# ====== อ่านข้อมูลรูปภาพทุกรูป ======
for root, dirs, files in os.walk(image_dir):
    for filename in files:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in image_extensions:
            continue

        filepath = os.path.join(root, filename)
        path_parts = os.path.relpath(root, image_dir).split(os.sep)

        main_cat = path_parts[0] if len(path_parts) >= 1 else "Unknown"
        sub_cat = path_parts[1] if len(path_parts) >= 2 else ""

        total_images += 1
        main_categories[main_cat] = main_categories.get(main_cat, 0) + 1
        if sub_cat:
            sub_key = f"{main_cat} / {sub_cat}"
            sub_categories[sub_key] = sub_categories.get(sub_key, 0) + 1

        try:
            with Image.open(filepath) as img:
                width, height = img.size
                mode = img.mode
                is_grayscale = (mode == 'L')
                if is_grayscale:
                    grayscale_count += 1
                file_size_kb = os.path.getsize(filepath) / 1024

                image_info.append({
                    'main_category': main_cat,
                    'sub_category': sub_cat,
                    'width': width,
                    'height': height,
                    'aspect_ratio': round(width / height, 3),
                    'file_size_kb': round(file_size_kb, 2),
                    'mode': mode
                })
        except Exception:
            corrupted_files.append(filepath)
            continue

df = pd.DataFrame(image_info)

# ========== ส่วนที่เหลือของโค้ด EDA ต่อจากตรงนี้เหมือนเดิม ==========