import os
import hashlib
import random
from collections import defaultdict

from PIL import Image
import imagehash


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# Dataset ที่ได้จาก download_dataset.py
INPUT_DIR = os.path.join(
    BASE_DIR,
    "..",
    "data"
)

# Dataset หลังทำความสะอาด
OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "..",
    "cleaned_dataset"
)

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
)


# =========================================================
# 1. CHECK CORRUPTED IMAGES
# =========================================================

def is_valid_image(path):

    try:

        with Image.open(path) as img:
            img.verify()

        with Image.open(path) as img:
            img.convert("RGB")

        return True

    except Exception:

        return False


def find_valid_images():

    valid_images = []
    corrupted_images = []

    print("\n====================================")
    print(" Checking Corrupted Images")
    print("====================================")

    for root, dirs, files in os.walk(INPUT_DIR):

        for file in files:

            if not file.lower().endswith(
                IMAGE_EXTENSIONS
            ):
                continue

            path = os.path.join(
                root,
                file
            )

            if is_valid_image(path):

                valid_images.append(path)

            else:

                corrupted_images.append(path)

                print(
                    "Corrupted:",
                    path
                )

    # -----------------------------------------
    # แสดงจำนวนรูปหลังคัดรูปเสีย
    # -----------------------------------------

    total_images = (
        len(valid_images)
        + len(corrupted_images)
    )

    print("\n------------------------------------")
    print("ผลการตรวจสอบรูปภาพ")
    print("------------------------------------")

    print(
        "รูปทั้งหมด:",
        total_images
    )

    print(
        "รูปเสียที่ถูกคัดออก:",
        len(corrupted_images)
    )

    print(
        "รูปที่เหลือหลังคัดรูปเสีย:",
        len(valid_images)
    )

    print("------------------------------------")

    return valid_images


# =========================================================
# 2. EXACT DUPLICATE DETECTION
# =========================================================

def md5_hash(path):

    hash_md5 = hashlib.md5()

    with open(path, "rb") as f:

        for chunk in iter(
            lambda: f.read(4096),
            b""
        ):

            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def remove_exact_duplicates(images):

    print("\n====================================")
    print(" Exact Duplicate Detection")
    print("====================================")

    hashes = set()

    unique_images = []

    duplicate_count = 0

    for path in images:

        file_hash = md5_hash(path)

        if file_hash in hashes:

            duplicate_count += 1

            print(
                "Duplicate:",
                path
            )

        else:

            hashes.add(file_hash)

            unique_images.append(path)

    # -----------------------------------------
    # แสดงจำนวนหลังลบรูปซ้ำ
    # -----------------------------------------

    print("\n------------------------------------")

    print(
        "รูปก่อนลบรูปซ้ำ:",
        len(images)
    )

    print(
        "รูปซ้ำที่ถูกลบ:",
        duplicate_count
    )

    print(
        "รูปที่เหลือหลังลบรูปซ้ำ:",
        len(unique_images)
    )

    print("------------------------------------")

    return unique_images


# =========================================================
# 3. PERCEPTUAL HASH
# =========================================================

def remove_similar_duplicates(images):

    print("\n====================================")
    print(" Perceptual Hash Detection")
    print("====================================")

    hash_list = []

    unique_images = []

    duplicate_count = 0

    for path in images:

        try:

            with Image.open(path) as img:

                img = img.convert("RGB")

                phash = imagehash.phash(img)

            duplicate = False

            for old_hash in hash_list:

                # ค่า <= 5 = รูปมีความคล้ายกันมาก
                if phash - old_hash <= 5:

                    duplicate = True

                    duplicate_count += 1

                    print(
                        "Similar duplicate:",
                        path
                    )

                    break

            if not duplicate:

                hash_list.append(
                    phash
                )

                unique_images.append(
                    path
                )

        except Exception:

            pass

    # -----------------------------------------
    # แสดงจำนวนหลังลบรูปคล้ายกัน
    # -----------------------------------------

    print("\n------------------------------------")

    print(
        "รูปก่อนตรวจรูปคล้าย:",
        len(images)
    )

    print(
        "รูปคล้ายที่ถูกลบ:",
        duplicate_count
    )

    print(
        "รูปที่เหลือหลังลบรูปคล้าย:",
        len(unique_images)
    )

    print("------------------------------------")

    return unique_images


# =========================================================
# 4. CONVERT FORMAT + RGB
# =========================================================

def convert_images(images):

    print("\n====================================")
    print(" Converting Images")
    print(" JPG + RGB")
    print("====================================")

    class_images = defaultdict(list)

    conversion_count = 0

    for path in images:

        try:

            with Image.open(path) as img:

                # แปลง Color Space เป็น RGB
                img = img.convert("RGB")

                # ใช้ชื่อโฟลเดอร์เป็น Class
                class_name = os.path.basename(
                    os.path.dirname(path)
                )

                class_images[
                    class_name
                ].append(
                    img.copy()
                )

                conversion_count += 1

        except Exception as e:

            print(
                "Conversion error:",
                path,
                e
            )

    # -----------------------------------------
    # แสดงจำนวนหลังแปลง
    # -----------------------------------------

    print("\n------------------------------------")

    print(
        "จำนวนรูปที่แปลงเป็น RGB:",
        conversion_count
    )

    print(
        "จำนวน Class:",
        len(class_images)
    )

    print("------------------------------------")

    return class_images


# =========================================================
# 5. OVERSAMPLING
# =========================================================

def balance_dataset(class_images):

    print("\n====================================")
    print(" Class Imbalance")
    print(" Oversampling")
    print("====================================")

    if not class_images:

        print(
            "No images found."
        )

        return

    # หาจำนวนรูปของ Class ที่มากที่สุด
    target_count = max(
        len(images)
        for images in class_images.values()
    )

    print(
        "Target per class:",
        target_count
    )

    total_before = 0
    total_after = 0

    for class_name, images in class_images.items():

        output_class_dir = os.path.join(
            OUTPUT_DIR,
            class_name
        )

        os.makedirs(
            output_class_dir,
            exist_ok=True
        )

        original_count = len(images)

        total_before += original_count

        print(
            f"\n{class_name}: "
            f"{original_count} -> "
            f"{target_count}"
        )

        # -----------------------------------
        # ORIGINAL IMAGES
        # -----------------------------------

        for i, img in enumerate(images):

            output_path = os.path.join(
                output_class_dir,
                f"{i:05d}.jpg"
            )

            img.save(
                output_path,
                "JPEG",
                quality=95
            )

        # -----------------------------------
        # OVERSAMPLING
        # -----------------------------------

        additional = (
            target_count
            - original_count
        )

        for i in range(additional):

            img = random.choice(
                images
            )

            output_path = os.path.join(
                output_class_dir,
                f"oversample_{i:05d}.jpg"
            )

            img.save(
                output_path,
                "JPEG",
                quality=95
            )

        total_after += target_count

    # -----------------------------------------
    # แสดงจำนวนหลัง Oversampling
    # -----------------------------------------

    print("\n------------------------------------")

    print(
        "จำนวนรูปก่อน Oversampling:",
        total_before
    )

    print(
        "จำนวนรูปหลัง Oversampling:",
        total_after
    )

    print("------------------------------------")


# =========================================================
# 6. SUMMARY
# =========================================================

def print_summary(
    original_count,
    after_corrupted,
    after_exact_duplicate,
    after_similar_duplicate
):

    print("\n")
    print("=" * 60)
    print(" FINAL PREPROCESSING SUMMARY")
    print("=" * 60)

    print(
        f"{'ขั้นตอน':<35}"
        f"{'จำนวนรูป':>15}"
    )

    print("-" * 60)

    print(
        f"{'รูปทั้งหมด':<35}"
        f"{original_count:>15}"
    )

    print(
        f"{'หลังคัดรูปเสีย':<35}"
        f"{after_corrupted:>15}"
    )

    print(
        f"{'หลังลบรูปซ้ำ MD5':<35}"
        f"{after_exact_duplicate:>15}"
    )

    print(
        f"{'หลังลบรูปคล้าย Perceptual Hash':<35}"
        f"{after_similar_duplicate:>15}"
    )

    print("-" * 60)

    print(
        "Dataset พร้อมสำหรับขั้นตอนถัดไป"
    )

    print("=" * 60)


# =========================================================
# MAIN
# =========================================================

def main():

    print("\n")
    print("=" * 60)
    print(" IMAGE DATASET PREPROCESSING")
    print("=" * 60)

    # -----------------------------------------
    # ตรวจสอบ Dataset
    # -----------------------------------------

    if not os.path.exists(INPUT_DIR):

        print(
            "\nไม่พบ Dataset:"
        )

        print(
            INPUT_DIR
        )

        print(
            "\nกรุณารัน download_dataset.py ก่อน"
        )

        return

    # -----------------------------------------
    # 1. ตรวจรูปเสีย
    # -----------------------------------------

    images = find_valid_images()

    if not images:

        print(
            "\nไม่พบรูปภาพ"
        )

        return

    after_corrupted = len(images)

    original_count = (
        after_corrupted
    )

    # -----------------------------------------
    # 2. ลบรูปซ้ำ MD5
    # -----------------------------------------

    images = remove_exact_duplicates(
        images
    )

    after_exact_duplicate = len(
        images
    )

    # -----------------------------------------
    # 3. ลบรูปคล้าย
    # -----------------------------------------

    images = remove_similar_duplicates(
        images
    )

    after_similar_duplicate = len(
        images
    )

    # -----------------------------------------
    # 4. แปลง JPG + RGB
    # -----------------------------------------

    class_images = convert_images(
        images
    )

    # -----------------------------------------
    # 5. Oversampling
    # -----------------------------------------

    balance_dataset(
        class_images
    )

    # -----------------------------------------
    # 6. สรุปผล
    # -----------------------------------------

    print_summary(
        original_count,
        after_corrupted,
        after_exact_duplicate,
        after_similar_duplicate
    )

    print("\n====================================")
    print(" PROCESS COMPLETED")
    print("====================================")

    print(
        "\nCleaned Dataset:"
    )

    print(
        OUTPUT_DIR
    )


# =========================================================

if __name__ == "__main__":

    main()