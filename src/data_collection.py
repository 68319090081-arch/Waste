import os
feature/my-work
import json
from pathlib import Path
import kaggle
import sys

import kaggle

main

# ==========================================================
# 1. กำหนด Dataset จาก Kaggle
# ==========================================================
feature/my-work
DATASET = "phenomsg/waste-classification"

# ==========================================================
# 2. หาตำแหน่ง Project อัตโนมัติ
# ==========================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# ==========================================================
# 3. ตั้งค่า Kaggle อัตโนมัติ — ครั้งเดียว จดจำตลอดไป
# ==========================================================
def setup_kaggle():
    kaggle_dir = Path.home() / ".kaggle"
    json_path = kaggle_dir / "kaggle.json"

    # ✅ ถ้ามีไฟล์อยู่แล้ว → ข้ามเลย ใช้ของเดิม
    if json_path.exists():
        print("✅ Kaggle already configured")
        return True

    # ❌ ถ้ายังไม่มี → ถามครั้งเดียว
    print("=" * 60)
    print("⚠️  Kaggle setup required (only once per computer)")
    print("👉 Get your API key from: Kaggle.com → Settings → Create New API Token")
    print("=" * 60)
    
    username = input("Enter Kaggle Username: ").strip()
    api_key = input("Enter Kaggle API Key: ").strip()

    if not username or not api_key:
        print("❌ Error: Username or Key cannot be empty")
        sys.exit(1)

    # ✅ สร้างไฟล์ให้อัตโนมัติ
    kaggle_dir.mkdir(exist_ok=True)
    json_path.write_text(json.dumps({"username": username, "key": api_key}))
    os.chmod(str(json_path), 0o600)
    print("✅ Saved successfully! Ready to download.")
    print("-" * 60)
    return True

# ==========================================================
# 4. ดาวน์โหลด + แตกไฟล์ ถ้ายังไม่มี
# ==========================================================
def download_dataset():
    os.makedirs(DATA_DIR, exist_ok=True)

    # ✅ ถ้ามีข้อมูลอยู่แล้ว → ข้าม
    if len(os.listdir(DATA_DIR)) > 0:
        print(f"✅ Dataset already exists at: {DATA_DIR}")
        return DATA_DIR

    print("📥 Downloading dataset from Kaggle...")
    print("⚠️  Dataset size ~900MB — please wait...")

    try:
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(
            DATASET,
            path=DATA_DIR,
            unzip=True
        )
        print(f"✅ Download complete → {DATA_DIR}")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("💡 Please check your internet connection and API credentials")
        sys.exit(1)

    return DATA_DIR

# ==========================================================
# 5. เริ่มทำงาน
# ==========================================================
if __name__ == "__main__":
    print("=" * 60)
    print("        KAGGLE DATASET DOWNLOADER")
    print("=" * 60)
    print()

    setup_kaggle()
    download_dataset()

    print()
    print("✅ data_collection.py finished — Dataset is ready!")

DATASET = "phenomsg/waste-classification"


# ==========================================================
# 2. หาตำแหน่ง Project อัตโนมัติ
# ==========================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# สร้างโฟลเดอร์ data ไว้ข้างนอก src
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


# ==========================================================
# 3. สร้างโฟลเดอร์ data อัตโนมัติ
# ==========================================================

os.makedirs(DATA_DIR, exist_ok=True)

print("=" * 60)
print("        KAGGLE DATASET DOWNLOADER")
print("=" * 60)

print(f"📁 โฟลเดอร์ปลายทาง:")
print(DATA_DIR)
print()


# ==========================================================
# 4. ดาวน์โหลด Dataset จาก Kaggle
# ==========================================================

try:

    print("🔐 กำลังเชื่อมต่อ Kaggle...")

    kaggle.api.authenticate()

    print("✅ เชื่อมต่อ Kaggle สำเร็จ")
    print()

    print("⬇️ กำลังดาวน์โหลด Dataset...")
    print(f"Dataset: {DATASET}")
    print()

    kaggle.api.dataset_download_files(
        DATASET,
        path=DATA_DIR,
        unzip=True
    )

    print()
    print("=" * 60)
    print("✅ ดาวน์โหลด Dataset สำเร็จ!")
    print("=" * 60)

    print(f"📂 ข้อมูลถูกเก็บไว้ที่:")
    print(DATA_DIR)

    print()
    print("🎉 พร้อมนำ Dataset ไปใช้ในขั้นตอนต่อไป")


except Exception as e:

    print()
    print("=" * 60)
    print("❌ ดาวน์โหลด Dataset ไม่สำเร็จ")
    print("=" * 60)

    print(f"Error: {e}")

    print()
    print("กรุณาตรวจสอบ Kaggle API")
main
