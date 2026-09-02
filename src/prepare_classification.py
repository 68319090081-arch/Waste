import random
import shutil
from pathlib import Path

# ================= CONFIG =================

ROOT = Path(__file__).resolve().parent.parent

SOURCE = ROOT / "data"
OUTPUT = ROOT / "dataset_classification"

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

SEED = 42

EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".jfif",
    ".tif",
    ".tiff"
}

CLASSES = [
    "Hazardous",
    "Non-Recyclable",
    "Organic",
    "Recyclable"
]


# ================= FUNCTIONS =================

def find_images(class_name):
    """
    ค้นหารูปทั้งหมดภายใน Class
    รวมถึงโฟลเดอร์ย่อย เช่น batteries, e-waste
    """
    class_path = SOURCE / class_name

    images = []

    if not class_path.exists():
        print(f"❌ ไม่พบโฟลเดอร์: {class_path}")
        return []

    for file in class_path.rglob("*"):
        if file.is_file() and file.suffix.lower() in EXTENSIONS:
            images.append(file)

    return images


def split_images(images):
    """
    แบ่งรูปเป็น Train / Val / Test
    """
    images = images.copy()

    random.shuffle(images)

    total = len(images)

    train_count = int(total * TRAIN_RATIO)
    val_count = int(total * VAL_RATIO)

    train = images[:train_count]

    val = images[
        train_count:
        train_count + val_count
    ]

    test = images[
        train_count + val_count:
    ]

    return train, val, test


def copy_images(images, class_name, split):
    """
    Copy รูปไปยังโฟลเดอร์ปลายทาง
    """
    destination = OUTPUT / split / class_name

    destination.mkdir(
        parents=True,
        exist_ok=True
    )

    for index, image in enumerate(images):

        # ป้องกันชื่อไฟล์ซ้ำ
        filename = image.name

        target = destination / filename

        if target.exists():

            target = destination / (
                f"{image.stem}_{index}{image.suffix}"
            )

        shutil.copy2(image, target)


# ================= MAIN =================

def main():

    print("=" * 60)
    print("   PREPARE YOLO CLASSIFICATION DATASET")
    print("=" * 60)

    random.seed(SEED)

    # ตรวจสอบ Ratio
    if TRAIN_RATIO + VAL_RATIO + TEST_RATIO != 1:
        print("❌ Ratio ไม่ถูกต้อง")
        return

    # ลบ Dataset เดิม
    if OUTPUT.exists():

        print("\n🗑️ ลบ Dataset เดิม...")

        shutil.rmtree(OUTPUT)

    OUTPUT.mkdir(parents=True)

    total_train = 0
    total_val = 0
    total_test = 0

    print("\n📦 กำลังเตรียม Dataset...\n")

    # ================= PROCESS EACH CLASS =================

    for class_name in CLASSES:

        print(f"🔍 Class: {class_name}")

        images = find_images(class_name)

        if not images:
            print("   ❌ ไม่พบรูป")
            continue

        print(f"   พบรูปทั้งหมด: {len(images)}")

        train, val, test = split_images(images)

        # Copy
        copy_images(
            train,
            class_name,
            "train"
        )

        copy_images(
            val,
            class_name,
            "val"
        )

        copy_images(
            test,
            class_name,
            "test"
        )

        total_train += len(train)
        total_val += len(val)
        total_test += len(test)

        print(
            f"   Train : {len(train)}"
        )

        print(
            f"   Val   : {len(val)}"
        )

        print(
            f"   Test  : {len(test)}"
        )

        print()

    # ================= SUMMARY =================

    total = (
        total_train +
        total_val +
        total_test
    )

    print("=" * 60)
    print("✅ DATASET PREPARATION COMPLETED")
    print("=" * 60)

    print(f"Total : {total}")
    print(
        f"Train : {total_train} "
        f"({total_train / total * 100:.1f}%)"
    )

    print(
        f"Val   : {total_val} "
        f"({total_val / total * 100:.1f}%)"
    )

    print(
        f"Test  : {total_test} "
        f"({total_test / total * 100:.1f}%)"
    )

    print(f"\n📁 Output: {OUTPUT}")

    print("\nโครงสร้างที่สร้าง:")

    print("""
dataset_classification/
├── train/
│   ├── Hazardous/
│   ├── Non-Recyclable/
│   ├── Organic/
│   └── Recyclable/
│
├── val/
│   ├── Hazardous/
│   ├── Non-Recyclable/
│   ├── Organic/
│   └── Recyclable/
│
└── test/
    ├── Hazardous/
    ├── Non-Recyclable/
    ├── Organic/
    └── Recyclable/
""")


if __name__ == "__main__":
    main()