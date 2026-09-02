import os
from ultralytics import YOLO


# ================= CONFIG =================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    ROOT,
    "runs",
    "classify",
    "runs_classify",
    "waste_classification",
    "weights",
    "best.pt"
)


# ================= PREDICT =================

def predict_image():

    print("=" * 60)
    print("       WASTE CLASSIFICATION - PREDICTION")
    print("=" * 60)

    # ตรวจสอบโมเดล
    if not os.path.exists(MODEL_PATH):
        print(f"❌ ไม่พบโมเดล: {MODEL_PATH}")
        return

    # รับ path รูปจากผู้ใช้
    image_path = input("\n📷 ใส่ที่อยู่รูปภาพ: ").strip().strip('"')

    if not os.path.exists(image_path):
        print("❌ ไม่พบรูปภาพ")
        return

    print("\n📦 Loading model...")
    model = YOLO(MODEL_PATH)

    print("🔍 กำลังวิเคราะห์รูป...")

    results = model.predict(
        source=image_path,
        imgsz=224,
        verbose=False
    )

    result = results[0]

    # ผลการทำนาย
    top1_index = result.probs.top1
    confidence = float(result.probs.top1conf)
    class_name = result.names[top1_index]

    print("\n" + "=" * 60)
    print("              RESULT")
    print("=" * 60)

    print(f"🗑️ ประเภทขยะ : {class_name}")
    print(f"🎯 ความมั่นใจ : {confidence * 100:.2f}%")

    print("=" * 60)


if __name__ == "__main__":
    predict_image()