import os
import kaggle


# ==========================================================
# 1. กำหนด Dataset จาก Kaggle
# ==========================================================

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