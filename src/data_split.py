import csv
import random
import shutil
import hashlib
from pathlib import Path
import matplotlib.pyplot as plt

# ================= CONFIG =================
ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "data"
OUTPUT = ROOT / "dataset_split"

TRAIN, VAL, TEST = 70, 15, 15
SEED = 42
EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".jfif", ".tif", ".tiff"}

# ================= FUNCTIONS =================

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_classes():
    classes = {}

    if not DATASET.exists():
        print(f"❌ ไม่พบ Dataset: {DATASET}")
        return {}

    for f in DATASET.rglob("*"):
        if f.is_file() and f.suffix.lower() in EXT:
            cls = f.parent.name
            classes.setdefault(cls, []).append(f)

    return dict(sorted(classes.items()))


def remove_duplicates(images):
    seen = set()
    result = []

    for img in images:
        h = file_hash(img)
        if h not in seen:
            seen.add(h)
            result.append(img)

    return result


def split_data(images):
    images = images.copy()
    random.shuffle(images)

    n = len(images)
    n_train = round(n * TRAIN / 100)
    n_val = round(n * VAL / 100)

    train = images[:n_train]
    val = images[n_train:n_train + n_val]
    test = images[n_train + n_val:]

    return train, val, test


def copy_images(images, folder):
    folder.mkdir(parents=True, exist_ok=True)

    for img in images:
        target = folder / img.name
        i = 1

        while target.exists():
            target = folder / f"{img.stem}_{i}{img.suffix}"
            i += 1

        shutil.copy2(img, target)


def save_manifest(name, data):
    path = OUTPUT / f"{name}_manifest.csv"

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["filename", "class", "split", "source_path"])

        for cls, images in data.items():
            for img in images:
                w.writerow([img.name, cls, name, str(img)])


def check_leakage(train, val, test):
    sets = [
        {file_hash(x) for x in train},
        {file_hash(x) for x in val},
        {file_hash(x) for x in test}
    ]

    if sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2]:
        raise Exception("❌ พบ Data Leakage")

    print("✓ Data Leakage Check ผ่าน")


def create_graph(report, totals):
    classes = [x["class"] for x in report]
    counts = [x["total"] for x in report]

    # Class Graph
    plt.figure(figsize=(12, 6))
    bars = plt.bar(classes, counts)

    plt.title("Waste Dataset - Images per Class", fontsize=16)
    plt.xlabel("Class")
    plt.ylabel("Number of Images")
    plt.xticks(rotation=45, ha="right")

    for bar, n in zip(bars, counts):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(n),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    plt.savefig(ROOT / "dataset_class_distribution.png", dpi=300)
    plt.show()
    plt.close()

    # Split Graph
    names = ["Train", "Validation", "Test"]

    plt.figure(figsize=(8, 6))
    bars = plt.bar(names, totals)

    plt.title("Train / Validation / Test", fontsize=16)
    plt.ylabel("Number of Images")

    for bar, n in zip(bars, totals):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(n),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    plt.savefig(ROOT / "dataset_split_distribution.png", dpi=300)
    plt.show()
    plt.close()

    # Pie Graph
    plt.figure(figsize=(7, 7))
    plt.pie(
        totals,
        labels=names,
        autopct="%1.1f%%",
        startangle=90
    )
    plt.title("Dataset Split Ratio")
    plt.savefig(ROOT / "dataset_split_pie.png", dpi=300)
    plt.show()
    plt.close()


def create_readme(report, totals):
    path = ROOT / "README.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Waste Dataset Split Report\n\n")
        f.write("## Split Strategy\n\n")
        f.write("- Train: 70%\n")
        f.write("- Validation: 15%\n")
        f.write("- Test: 15%\n")
        f.write(f"- Random Seed: {SEED}\n\n")

        f.write("ใช้ Stratified Split โดยแบ่งแยกภายในแต่ละ Class "
                "เพื่อรักษาสัดส่วนของ Class ในแต่ละชุดข้อมูล\n\n")

        f.write("## Dataset Summary\n\n")
        f.write("| Class | Total | Train | Val | Test |\n")
        f.write("|---|---:|---:|---:|---:|\n")

        for x in report:
            f.write(
                f"| {x['class']} | {x['total']} | "
                f"{x['train']} | {x['val']} | {x['test']} |\n"
            )

        f.write("\n## Manifest\n\n")
        f.write("- train_manifest.csv\n")
        f.write("- val_manifest.csv\n")
        f.write("- test_manifest.csv\n\n")

        f.write("## Graphs\n\n")
        f.write("- dataset_class_distribution.png\n")
        f.write("- dataset_split_distribution.png\n")
        f.write("- dataset_split_pie.png\n")


# ================= MAIN =================

def main():

    print("=" * 55)
    print("       WASTE DATASET SPLIT PROGRAM")
    print("=" * 55)

    random.seed(SEED)

    if TRAIN + VAL + TEST != 100:
        print("❌ Ratio ไม่ถูกต้อง")
        return

    classes = find_classes()

    if not classes:
        print("❌ ไม่พบ Class หรือรูปภาพ")
        return

    # ลบ Dataset Split เดิม
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)

    OUTPUT.mkdir(parents=True)

    train_data = {}
    val_data = {}
    test_data = {}
    report = []

    total_train = total_val = total_test = 0
    duplicate_total = 0

    # ================= SPLIT =================

    for cls, images in classes.items():

        before = len(images)
        images = remove_duplicates(images)
        duplicate_total += before - len(images)

        train, val, test = split_data(images)

        check_leakage(train, val, test)

        copy_images(train, OUTPUT / "train" / cls)
        copy_images(val, OUTPUT / "val" / cls)
        copy_images(test, OUTPUT / "test" / cls)

        train_data[cls] = train
        val_data[cls] = val
        test_data[cls] = test

        report.append({
            "class": cls,
            "total": len(images),
            "train": len(train),
            "val": len(val),
            "test": len(test)
        })

        total_train += len(train)
        total_val += len(val)
        total_test += len(test)

        print(
            f"{cls}: {len(images)} | "
            f"Train {len(train)} | "
            f"Val {len(val)} | "
            f"Test {len(test)}"
        )

    # ================= OUTPUT =================

    save_manifest("train", train_data)
    save_manifest("val", val_data)
    save_manifest("test", test_data)

    totals = [total_train, total_val, total_test]

    create_graph(report, totals)
    create_readme(report, totals)

    total = sum(totals)

    print("\n" + "=" * 55)
    print("✅ ทำงานสำเร็จ")
    print("=" * 55)
    print(f"Total : {total}")
    print(f"Train : {total_train} ({total_train / total * 100:.1f}%)")
    print(f"Val   : {total_val} ({total_val / total * 100:.1f}%)")
    print(f"Test  : {total_test} ({total_test / total * 100:.1f}%)")
    print(f"รูปซ้ำที่ตัดออก : {duplicate_total}")
    print(f"Output : {OUTPUT}")


if __name__ == "__main__":
    main()