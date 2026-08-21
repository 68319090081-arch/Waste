"""
Image Preprocessing Pipeline
=============================
ครอบคลุม 4 ขั้นตอนหลัก:
1. Resize เป็นขนาดมาตรฐาน (224x224 - เทียบเท่า ImageNet pretrained models)
2. Normalization (0-1 scale หรือ mean-std normalize)
3. Noise Reduction / Denoising (median / gaussian / bilateral / NL-means)
4. Data Augmentation (flip, rotate, crop, brightness adjust)

ต้องติดตั้ง: pip install opencv-python numpy pillow --break-system-packages
"""

import cv2
import numpy as np
import random
import os

# ----------------------------
# ค่าคงที่ (ปรับได้ตาม dataset)
# ----------------------------
TARGET_SIZE = (224, 224)  # (width, height) — มาตรฐาน ImageNet, หาร 32 ลงตัว
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


# ============================================================
# 1) RESIZE — ทำแบบ letterbox เพื่อรักษา aspect ratio (ไม่บิดเบี้ยว)
# ============================================================
def resize_with_padding(image: np.ndarray, target_size=TARGET_SIZE, pad_color=(0, 0, 0)):
    """
    Resize ภาพให้พอดีกับ target_size โดยรักษาสัดส่วนเดิม
    แล้วเติม padding (letterbox) ในส่วนที่เหลือ
    - ใช้ INTER_AREA เมื่อย่อ (ลด aliasing), INTER_LINEAR เมื่อขยาย
    """
    h, w = image.shape[:2]
    tw, th = target_size
    scale = min(tw / w, th / h)
    new_w, new_h = int(w * scale), int(h * scale)

    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    resized = cv2.resize(image, (new_w, new_h), interpolation=interp)

    canvas = np.full((th, tw, 3), pad_color, dtype=np.uint8)
    top = (th - new_h) // 2
    left = (tw - new_w) // 2
    canvas[top:top + new_h, left:left + new_w] = resized
    return canvas


# ============================================================
# 2) NORMALIZATION
# ============================================================
def normalize_0_1(image: np.ndarray) -> np.ndarray:
    """Scale พิกเซลจาก [0,255] -> [0,1]"""
    return image.astype(np.float32) / 255.0


def normalize_mean_std(image: np.ndarray, mean=IMAGENET_MEAN, std=IMAGENET_STD) -> np.ndarray:
    """
    Mean-Std normalize: ใช้เมื่อจะทำ transfer learning กับ pretrained model
    (image ต้องอยู่ในช่วง [0,1] ก่อน แล้วค่อย normalize)
    """
    img = image.astype(np.float32) / 255.0
    return (img - mean) / std


# ============================================================
# 3) NOISE REDUCTION / DENOISING
# ============================================================
def denoise_median(image: np.ndarray, ksize: int = 3) -> np.ndarray:
    """เหมาะกับ salt-and-pepper noise"""
    return cv2.medianBlur(image, ksize)


def denoise_gaussian(image: np.ndarray, ksize=(3, 3), sigma: float = 0) -> np.ndarray:
    """เหมาะกับ Gaussian noise ทั่วไป"""
    return cv2.GaussianBlur(image, ksize, sigma)


def denoise_bilateral(image: np.ndarray, d: int = 9, sigma_color: float = 75, sigma_space: float = 75) -> np.ndarray:
    """ลด noise แต่รักษาขอบภาพ (edge-preserving) — เหมาะกับภาพทางการแพทย์/detail สำคัญ"""
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)


def denoise_nl_means(image: np.ndarray, h: float = 10) -> np.ndarray:
    """Non-local means — คุณภาพสูงสำหรับภาพถ่ายจริง แต่ compute cost สูง"""
    return cv2.fastNlMeansDenoisingColored(image, None, h, h, 7, 21)


def auto_denoise(image: np.ndarray, method: str = "bilateral") -> np.ndarray:
    """เลือก method ตามความเหมาะสมของ dataset"""
    methods = {
        "median": denoise_median,
        "gaussian": denoise_gaussian,
        "bilateral": denoise_bilateral,
        "nl_means": denoise_nl_means,
    }
    if method not in methods:
        raise ValueError(f"Unknown method: {method}. เลือกจาก {list(methods.keys())}")
    return methods[method](image)


# ============================================================
# 4) DATA AUGMENTATION
# ============================================================
def random_horizontal_flip(image: np.ndarray, p: float = 0.5) -> np.ndarray:
    """กลับด้านซ้าย-ขวา"""
    if random.random() < p:
        return cv2.flip(image, 1)
    return image


def random_vertical_flip(image: np.ndarray, p: float = 0.5) -> np.ndarray:
    """กลับด้านบน-ล่าง"""
    if random.random() < p:
        return cv2.flip(image, 0)
    return image


def random_rotate(image: np.ndarray, max_angle: float = 180.0) -> np.ndarray:
    """
    หมุนภาพแบบสุ่มได้ทุกทิศทาง (0-360 องศา)
    max_angle=180 หมายถึงสุ่มมุมในช่วง -180 ถึง +180 องศา ครอบคลุมการหมุนได้ทุกทิศ
    ใช้เมื่อวัตถุในภาพไม่มีทิศทางตายตัว (เช่น ภาพถ่ายดาวเทียม, เซลล์, ชิ้น[...]
    ถ้าวัตถุมีทิศทางที่มีความหมาย (เช่น คน, รถ ที่ควรตั้งตรงเสมอ) ควรใช้มุ�[...]
    """
    h, w = image.shape[:2]
    angle = random.uniform(-max_angle, max_angle)
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)


def random_crop(image: np.ndarray, crop_ratio: float = 0.85) -> np.ndarray:
    """
    สุ่มตัดบางส่วนของภาพแล้ว resize กลับเป็นขนาดเดิม
    บังคับให้โมเดลเรียนรู้ feature จากหลายตำแหน่ง ลด overfitting
    """
    h, w = image.shape[:2]
    ch, cw = int(h * crop_ratio), int(w * crop_ratio)
    top = random.randint(0, h - ch)
    left = random.randint(0, w - cw)
    cropped = image[top:top + ch, left:left + cw]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)


def random_brightness_contrast(image: np.ndarray, brightness_range=(-30, 30), contrast_range=(0.8, 1.2)) -> np.ndarray:
    """
    ปรับความสว่าง/contrast แบบสุ่ม
    จำลองสภาพแสงที่แตกต่างกัน (กลางแจ้ง/ในร่ม/กลางคืน)
    """
    brightness = random.uniform(*brightness_range)
    contrast = random.uniform(*contrast_range)
    img = image.astype(np.float32)
    img = img * contrast + brightness
    return np.clip(img, 0, 255).astype(np.uint8)


def rotate_fixed_angle(image: np.ndarray, angle: float) -> np.ndarray:
    """หมุนภาพด้วยมุมที่กำหนดตายตัว (ไม่สุ่ม) ใช้สำหรับสร้างไฟล์แยกแต่ละอง[...]
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)


def augment_image(image: np.ndarray) -> np.ndarray:
    """รวม augmentation หลายแบบเข้าด้วยกัน (สุ่มแต่ละครั้ง) — ใช้เมื่อต้องการภาพ augment เ[...]
    img = random_horizontal_flip(image)
    img = random_vertical_flip(img)
    img = random_rotate(img)
    img = random_crop(img)
    img = random_brightness_contrast(img)
    return img


# ============================================================
# PIPELINE รวมทั้งหมด
# ============================================================
def preprocess_image_base(
    image_path: str,
    denoise_method: str = "bilateral",
) -> np.ndarray:
    """
    Pipeline พื้นฐาน (ไม่ augment): read -> resize -> denoise
    ใช้เป็นภาพตั้งต้นก่อนนำไปสร้าง variant หมุน/กลับด้านแต่ละแบบ
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"ไม่พบไฟล์ภาพ: {image_path}")

    image = resize_with_padding(image, TARGET_SIZE)
    image = auto_denoise(image, method=denoise_method)
    return image


# มุมและ transform ที่จะสร้างเป็นไฟล์แยก (ปรับเพิ่ม/ลดได้ตามต้องการ)
ROTATION_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]


def preprocess_dataset(
    input_dir: str,
    output_dir: str,
    jpg_quality: int = 95,
    denoise_method: str = "bilateral",
    angles=ROTATION_ANGLES,
    include_flips: bool = True,
):
    """
    ประมวลผลทั้งโฟลเดอร์ dataset โดยใช้ os.walk เดินหาไฟล์ภาพในทุก subfolder
    (เผื่อ dataset จัดเก็บแบบแยกคลาสเป็นโฟลเดอร์ย่อย เช่น data/cat, data/dog)
    โครงสร้างโฟลเดอร์ย่อยจะถูกสร้างซ้ำใน output_dir ด้วย

    สำหรับแต่ละภาพ จะสร้างไฟล์แยกดังนี้:
      - ชื่อ_rot0.jpg, ชื่อ_rot45.jpg, ชื่อ_rot90.jpg, ... (หมุนตามมุมใน angles)
      - ชื่อ_fliph.jpg (กลับซ้าย-ขวา), ชื่อ_flipv.jpg (กลับบน-ล่าง) ถ้า include_flips=True
    ทุกไฟล์ยังไม่ normalize — ให้ normalize ตอนโหลดเข้าโมเดล
    """
    exts = (".jpg", ".jpeg", ".png", ".bmp")

    image_paths = []
    for root, dirs, files in os.walk(input_dir):
        for fname in files:
            if fname.lower().endswith(exts):
                image_paths.append(os.path.join(root, fname))

    n_variants = len(angles) + (2 if include_flips else 0)
    print(f"พบภาพต้นฉบับ {len(image_paths)} ไฟล์ -> จะสร้าง {n_variants} variant/ภาพ "
          f"(รวม {len(image_paths) * n_variants} ไฟล์)")

    success, failed = 0, 0
    for in_path in image_paths:
        rel_path = os.path.relpath(in_path, input_dir)
        rel_dir = os.path.dirname(rel_path)
        out_subdir = os.path.join(output_dir, rel_dir)
        os.makedirs(out_subdir, exist_ok=True)

        fname = os.path.basename(in_path)
        base_name = os.path.splitext(fname)[0]

        try:
            base_img = preprocess_image_base(in_path, denoise_method=denoise_method)

            # สร้างไฟล์แยกตามมุมหมุน
            for angle in angles:
                rotated = rotate_fixed_angle(base_img, angle)
                out_path = os.path.join(out_subdir, f"{base_name}_rot{angle}.jpg")
                cv2.imwrite(out_path, rotated, [cv2.IMWRITE_JPEG_QUALITY, jpg_quality])
                success += 1

            # สร้างไฟล์แยกสำหรับ flip
            if include_flips:
                flip_h = cv2.flip(base_img, 1)  # ซ้าย-ขวา
                out_path = os.path.join(out_subdir, f"{base_name}_fliph.jpg")
                cv2.imwrite(out_path, flip_h, [cv2.IMWRITE_JPEG_QUALITY, jpg_quality])
                success += 1

                flip_v = cv2.flip(base_img, 0)  # บน-ล่าง
                out_path = os.path.join(out_subdir, f"{base_name}_flipv.jpg")
                cv2.imwrite(out_path, flip_v, [cv2.IMWRITE_JPEG_QUALITY, jpg_quality])
                success += 1

        except Exception as e:
            print(f"ข้ามไฟล์ {rel_path}: {e}")
            failed += 1

    print(f"เสร็จสิ้น! สร้างไฟล์สำเร็จ {success} ไฟล์, ข้ามภาพต้นฉบับที่ error {failed} ไฟล์")
    print(f"ผลลัพธ์อยู่ที่: {output_dir}")


if __name__ == "__main__":
    # สคริปต์จะอ่านภาพทั้งหมดจากโฟลเดอร์ "data" ที่อยู่ระดับเดียวกับไฟล์นี้โ[...]
    # และบันทึกผลลัพธ์ไว้ที่โฟลเดอร์ "data_processed"
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(SCRIPT_DIR)  # ถอยออกไปหนึ่งระดับ
    INPUT_DIR = os.path.join(PARENT_DIR, "data")
    OUTPUT_DIR = os.path.join(PARENT_DIR, "data_processed")

    if not os.path.isdir(INPUT_DIR):
        print(f"ไม่พบโฟลเดอร์ 'data' ที่: {INPUT_DIR}")
        print("กรุณาสร้างโฟลเดอร์ชื่อ 'data' ไว้ที่ parent directory ของสคริปต์นี้ แล้วใส่ภาพล��[...]")
    else:
        preprocess_dataset(
            INPUT_DIR,
            OUTPUT_DIR,
            denoise_method="bilateral",
            angles=ROTATION_ANGLES,   # [0, 45, 90, 135, 180, 225, 270, 315] ปรับได้ตรงนี้
            include_flips=True,       # สร้างไฟล์ fliph / flipv เพิ่มด้วย
            jpg_quality=95,
        )
        print("\nหมายเหตุ: ไฟล์ที่ได้เป็น .jpg แยกไฟล์ตามองศา/การกลับด้าน (ยังไม่ normalize)")
        print("ให้เรียก normalize_0_1() หรือ normalize_mean_std() ตอนโหลดภาพเข้าโมเดลใน DataLoader แทน")
