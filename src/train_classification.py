import os
from ultralytics import YOLO


# ================= CONFIG =================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET = os.path.join(ROOT, "dataset_classification")

MODEL_NAME = "yolo11n-cls.pt"

EPOCHS = 30
IMAGE_SIZE = 224
BATCH_SIZE = 16


# ================= MAIN =================

def train_model():

    print("=" * 65)
    print("      WASTE CLASSIFICATION - YOLO TRAINING")
    print("=" * 65)

    # ตรวจสอบ Dataset
    if not os.path.exists(DATASET):
        print(f"❌ ไม่พบ Dataset: {DATASET}")
        return

    print(f"\n📂 Dataset : {DATASET}")
    print(f"📦 Model   : {MODEL_NAME}")
    print(f"🖼️ Image Size : {IMAGE_SIZE}")
    print(f"🔁 Epochs  : {EPOCHS}")
    print(f"📊 Batch   : {BATCH_SIZE}")

    # โหลด Pretrained YOLO Classification
    print("\n📦 Loading YOLO Classification model...")

    model = YOLO(MODEL_NAME)

    # เริ่ม Training
    print("\n🚀 Starting training...")

    results = model.train(
        data=DATASET,
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        project="runs_classify",
        name="waste_classification",
        exist_ok=True,
        verbose=True
    )

    print("\n" + "=" * 65)
    print("✅ TRAINING COMPLETED")
    print("=" * 65)

    print(
        "💾 Best Model : "
        "runs_classify/waste_classification/weights/best.pt"
    )


if __name__ == "__main__":
    train_model()