import os
import shutil
import hashlib
from pathlib import Path

import cv2
import torch
from PIL import Image
import imagehash
from tqdm import tqdm
from transformers import pipeline


# ============================================================
# CONFIG
# ============================================================

DATASET_DIR = "data"
REMOVED_DIR = "removed"
CLEANED_DIR = "cleaned"

# ความเบลอขั้นต่ำ
# ค่ายิ่งสูง = เข้มงวดมากขึ้น
BLUR_THRESHOLD = 50

# นามสกุลไฟล์ที่รองรับ
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
}


# ============================================================
# CREATE FOLDERS
# ============================================================

def create_folders():
    folders = [
        "corrupted",
        "duplicate",
        "blurry",
        "irrelevant"
    ]

    for folder in folders:
        os.makedirs(
            os.path.join(REMOVED_DIR, folder),
            exist_ok=True
        )


# ============================================================
# FIND IMAGES
# ============================================================

def get_images():
    images = []

    for root, _, files in os.walk(DATASET_DIR):

        for file in files:

            path = os.path.join(root, file)

            if Path(file).suffix.lower() in IMAGE_EXTENSIONS:
                images.append(path)

    return images


# ============================================================
# CHECK CORRUPTED IMAGE
# ============================================================

def is_corrupted(path):

    try:

        with Image.open(path) as img:
            img.verify()

        return False

    except Exception:
        return True


# ============================================================
# IMAGE HASH
# ============================================================

def get_hash(path):

    try:

        with Image.open(path) as img:

            return str(
                imagehash.phash(img)
            )

    except Exception:

        return None


# ============================================================
# BLUR DETECTION
# ============================================================

def blur_score(path):

    try:

        image = cv2.imread(path)

        if image is None:
            return 0

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        score = cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()

        return score

    except Exception:

        return 0


# ============================================================
# MOVE IMAGE
# ============================================================

def move_image(path, category):

    filename = os.path.basename(path)

    destination_folder = os.path.join(
        REMOVED_DIR,
        category
    )

    os.makedirs(
        destination_folder,
        exist_ok=True
    )

    destination = os.path.join(
        destination_folder,
        filename
    )

    # ป้องกันชื่อไฟล์ซ้ำ
    counter = 1

    while os.path.exists(destination):

        name = Path(filename).stem
        extension = Path(filename).suffix

        destination = os.path.join(
            destination_folder,
            f"{name}_{counter}{extension}"
        )

        counter += 1

    shutil.move(
        path,
        destination
    )


# ============================================================
# LOAD AI MODEL
# ============================================================

print("\nกำลังโหลด AI Model...")

classifier = pipeline(
    "image-classification",
    model="google/vit-base-patch16-224"
)

print("โหลด AI Model สำเร็จ\n")


# ============================================================
# CHECK IRRELEVANT IMAGE
# ============================================================

def is_irrelevant(path):

    try:

        result = classifier(path)

        # แสดงผล AI
        top_result = result[0]

        label = top_result["label"].lower()
        score = top_result["score"]

        # กลุ่มคำที่ถือว่าเกี่ยวข้องกับขยะ/สิ่งของ
        relevant_words = [
            "plastic",
            "bottle",
            "container",
            "bag",
            "can",
            "tin",
            "paper",
            "cardboard",
            "carton",
            "glass",
            "jar",
            "metal",
            "box",
            "cup",
            "wrapper",
            "packet",
            "trash",
            "garbage",
            "waste",
            "bin"
        ]

        # ถ้า label ไม่เกี่ยวข้อง
        if score >= 0.70:

            for word in relevant_words:

                if word in label:
                    return False

            return True

        # ถ้า AI ไม่มั่นใจ
        return False

    except Exception as e:

        print(
            f"\nAI ตรวจสอบไม่ได้: {path}"
        )

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    create_folders()

    print("=" * 60)
    print("       DATASET CLEANING SYSTEM")
    print("=" * 60)

    images = get_images()

    total_before = len(images)

    print(
        f"\nพบรูปทั้งหมด: {total_before} รูป\n"
    )

    corrupted_count = 0
    duplicate_count = 0
    blurry_count = 0
    irrelevant_count = 0

    valid_images = []

    # --------------------------------------------------------
    # 1. CHECK CORRUPTED
    # --------------------------------------------------------

    print("\n[1/4] กำลังตรวจรูปเสีย...")

    for image in tqdm(images):

        if is_corrupted(image):

            move_image(
                image,
                "corrupted"
            )

            corrupted_count += 1

        else:

            valid_images.append(image)


    # --------------------------------------------------------
    # 2. CHECK DUPLICATE
    # --------------------------------------------------------

    print("\n[2/4] กำลังตรวจรูปซ้ำ...")

    hashes = {}

    valid_after_duplicate = []

    for image in tqdm(valid_images):

        image_hash = get_hash(image)

        if image_hash is None:

            continue

        if image_hash in hashes:

            move_image(
                image,
                "duplicate"
            )

            duplicate_count += 1

        else:

            hashes[image_hash] = image
            valid_after_duplicate.append(image)


    # --------------------------------------------------------
    # 3. CHECK BLUR
    # --------------------------------------------------------

    print("\n[3/4] กำลังตรวจภาพเบลอ...")

    valid_after_blur = []

    for image in tqdm(valid_after_duplicate):

        score = blur_score(image)

        if score < BLUR_THRESHOLD:

            move_image(
                image,
                "blurry"
            )

            blurry_count += 1

        else:

            valid_after_blur.append(image)


    # --------------------------------------------------------
    # 4. CHECK IRRELEVANT
    # --------------------------------------------------------

    print(
        "\n[4/4] กำลังตรวจรูปที่อาจไม่เกี่ยวข้องกับขยะ..."
    )

    final_images = []

    for image in tqdm(valid_after_blur):

        if is_irrelevant(image):

            move_image(
                image,
                "irrelevant"
            )

            irrelevant_count += 1

        else:

            final_images.append(image)


    # ========================================================
    # RESULT
    # ========================================================

    removed_total = (
        corrupted_count
        + duplicate_count
        + blurry_count
        + irrelevant_count
    )

    total_after = len(final_images)

    print("\n")
    print("=" * 60)
    print("              CLEANING RESULT")
    print("=" * 60)

    print(
        f"\nจำนวนรูปก่อนทำความสะอาด : {total_before}"
    )

    print(
        f"รูปเสีย                    : {corrupted_count}"
    )

    print(
        f"รูปซ้ำ                     : {duplicate_count}"
    )

    print(
        f"รูปเบลอ                    : {blurry_count}"
    )

    print(
        f"รูปไม่เกี่ยวข้อง           : {irrelevant_count}"
    )

    print(
        f"\nจำนวนรูปที่ถูกคัดออก       : {removed_total}"
    )

    print(
        f"จำนวนรูปที่เหลือ           : {total_after}"
    )

    print(
        f"\nDataset ลดลง              : "
        f"{removed_total / total_before * 100:.2f}%"
        if total_before > 0
        else "\nDataset ลดลง              : 0%"
    )

    print("\n" + "=" * 60)
    print("เสร็จสิ้น")
    print("=" * 60)

    print(
        f"\nรูปที่ผ่านการคัดอยู่ในโฟลเดอร์:"
        f" {DATASET_DIR}"
    )

    print(
        f"รูปที่ถูกคัดออกอยู่ใน:"
        f" {REMOVED_DIR}"
    )


# ============================================================
# SAVE CLEANED IMAGES
# ============================================================

def save_cleaned_images(images):
    os.makedirs(CLEANED_DIR, exist_ok=True)

    for image in images:
        relative_path = os.path.relpath(image, DATASET_DIR)
        destination = os.path.join(CLEANED_DIR, relative_path)

        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy2(image, destination)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()