import csv
import random
import shutil
import hashlib
from pathlib import Path

import matplotlib.pyplot as plt


# =========================================================
# CONFIG
# =========================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

DATASET_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "dataset_split"

# 70 / 15 / 15
TRAIN_RATIO = 70
VAL_RATIO = 15
TEST_RATIO = 15

RANDOM_SEED = 42

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".jfif",
    ".tif",
    ".tiff"
}


# =========================================================
# FIND CLASSES
# =========================================================

def find_classes():

    print("\nกำลังค้นหา Class และรูปภาพ...")

    if not DATASET_DIR.exists():

        print("\n❌ ไม่พบโฟลเดอร์ data")
        print(f"Path: {DATASET_DIR}")

        return {}

    classes = {}

    # ค้นหารูปทั้งหมดแบบ Recursive
    all_images = []

    for file in DATASET_DIR.rglob("*"):

        if not file.is_file():
            continue

        if file.suffix.lower() in IMAGE_EXTENSIONS:
            all_images.append(file)

    print(
        f"\n✓ พบรูปทั้งหมด: {len(all_images)} รูป"
    )

    # -----------------------------------------------------
    # หา Class
    # -----------------------------------------------------

    for image in all_images:

        relative_parts = image.relative_to(
            DATASET_DIR
        ).parts

        if len(relative_parts) < 2:
            continue

        # ใช้โฟลเดอร์ที่อยู่ติดกับรูปเป็น Class
        class_name = image.parent.name

        if class_name not in classes:
            classes[class_name] = []

        classes[class_name].append(image)

    return dict(
        sorted(
            classes.items(),
            key=lambda item: item[0].lower()
        )
    )


# =========================================================
# FILE HASH
# =========================================================

def get_file_hash(file_path):

    sha256 = hashlib.sha256()

    try:

        with open(file_path, "rb") as f:

            while True:

                data = f.read(1024 * 1024)

                if not data:
                    break

                sha256.update(data)

        return sha256.hexdigest()

    except Exception:

        return None


# =========================================================
# REMOVE DUPLICATE IMAGES
# =========================================================

def remove_duplicate_images(images):

    unique_images = []
    hashes = set()

    duplicate_count = 0

    for image in images:

        file_hash = get_file_hash(image)

        if file_hash is None:
            continue

        if file_hash in hashes:

            duplicate_count += 1
            continue

        hashes.add(file_hash)
        unique_images.append(image)

    return unique_images, duplicate_count


# =========================================================
# STRATIFIED SPLIT
# =========================================================

def split_images(images):

    images = images.copy()

    random.shuffle(images)

    total = len(images)

    train_count = round(
        total * TRAIN_RATIO / 100
    )

    val_count = round(
        total * VAL_RATIO / 100
    )

    # ป้องกันจำนวนเกิน
    if train_count + val_count > total:

        val_count = total - train_count

    train = images[:train_count]

    val = images[
        train_count:
        train_count + val_count
    ]

    test = images[
        train_count + val_count:
    ]

    return train, val, test


# =========================================================
# COPY IMAGES
# =========================================================

def copy_images(
    images,
    destination
):

    destination.mkdir(
        parents=True,
        exist_ok=True
    )

    for image in images:

        target = destination / image.name

        counter = 1

        while target.exists():

            target = (
                destination
                / f"{image.stem}_{counter}"
                f"{image.suffix}"
            )

            counter += 1

        shutil.copy2(
            image,
            target
        )


# =========================================================
# DATA LEAKAGE CHECK
# =========================================================

def check_data_leakage(
    train,
    val,
    test
):

    train_hashes = {
        get_file_hash(image)
        for image in train
    }

    val_hashes = {
        get_file_hash(image)
        for image in val
    }

    test_hashes = {
        get_file_hash(image)
        for image in test
    }

    train_hashes.discard(None)
    val_hashes.discard(None)
    test_hashes.discard(None)

    train_val = train_hashes & val_hashes
    train_test = train_hashes & test_hashes
    val_test = val_hashes & test_hashes

    if train_val:

        raise Exception(
            "❌ พบ Data Leakage ระหว่าง Train และ Validation"
        )

    if train_test:

        raise Exception(
            "❌ พบ Data Leakage ระหว่าง Train และ Test"
        )

    if val_test:

        raise Exception(
            "❌ พบ Data Leakage ระหว่าง Validation และ Test"
        )

    print(
        "✓ ตรวจสอบ Data Leakage ผ่าน"
    )


# =========================================================
# MANIFEST
# =========================================================

def save_manifest(
    split_name,
    manifest_data
):

    csv_file = (
        OUTPUT_DIR
        / f"{split_name}_manifest.csv"
    )

    with open(
        csv_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "filename",
                "class",
                "split",
                "source_path"
            ]
        )

        for class_name, images in manifest_data.items():

            for image in images:

                writer.writerow(
                    [
                        image.name,
                        class_name,
                        split_name,
                        str(image)
                    ]
                )

    print(
        f"✓ สร้าง {split_name}_manifest.csv"
    )


# =========================================================
# CREATE GRAPH
# =========================================================

def create_graph(
    report,
    total_train,
    total_val,
    total_test
):

    print(
        "\nกำลังสร้างกราฟ..."
    )

    # =====================================================
    # GRAPH 1 : CLASS DISTRIBUTION
    # =====================================================

    class_names = [
        item["class"]
        for item in report
    ]

    class_counts = [
        item["total"]
        for item in report
    ]

    plt.figure(
        figsize=(15, 8)
    )

    bars = plt.bar(
        class_names,
        class_counts
    )

    plt.title(
        "Waste Dataset - Images per Class",
        fontsize=16
    )

    plt.xlabel(
        "Class"
    )

    plt.ylabel(
        "Number of Images"
    )

    plt.xticks(
        rotation=60,
        ha="right"
    )

    # ตัวเลขบนแท่ง
    for bar, value in zip(
        bars,
        class_counts
    ):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            bar.get_height(),
            str(value),
            ha="center",
            va="bottom",
            fontsize=9
        )

    plt.tight_layout()

    graph_class = (
        PROJECT_DIR
        / "dataset_class_distribution.png"
    )

    plt.savefig(
        graph_class,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    plt.close()

    print(
        f"✓ บันทึกกราฟ Class:"
        f"\n  {graph_class}"
    )


    # =====================================================
    # GRAPH 2 : TRAIN / VAL / TEST
    # =====================================================

    split_names = [
        "Train",
        "Validation",
        "Test"
    ]

    split_counts = [
        total_train,
        total_val,
        total_test
    ]

    plt.figure(
        figsize=(9, 6)
    )

    bars = plt.bar(
        split_names,
        split_counts
    )

    plt.title(
        "Train / Validation / Test Distribution",
        fontsize=16
    )

    plt.xlabel(
        "Dataset Split"
    )

    plt.ylabel(
        "Number of Images"
    )

    # ตัวเลขบนแท่ง
    for bar, value in zip(
        bars,
        split_counts
    ):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            bar.get_height(),
            str(value),
            ha="center",
            va="bottom",
            fontsize=11
        )

    plt.tight_layout()

    graph_split = (
        PROJECT_DIR
        / "dataset_split_distribution.png"
    )

    plt.savefig(
        graph_split,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    plt.close()

    print(
        f"✓ บันทึกกราฟ Split:"
        f"\n  {graph_split}"
    )


    # =====================================================
    # GRAPH 3 : PIE CHART
    # =====================================================

    plt.figure(
        figsize=(8, 8)
    )

    plt.pie(
        split_counts,
        labels=split_names,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title(
        "Dataset Split Ratio"
    )

    graph_pie = (
        PROJECT_DIR
        / "dataset_split_pie.png"
    )

    plt.savefig(
        graph_pie,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    plt.close()

    print(
        f"✓ บันทึกกราฟ Pie:"
        f"\n  {graph_pie}"
    )


# =========================================================
# CREATE README
# =========================================================

def create_readme(
    report,
    total_all,
    total_train,
    total_val,
    total_test
):

    readme_file = (
        PROJECT_DIR
        / "README.md"
    )

    with open(
        readme_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "# Waste Dataset Split Report\n\n"
        )

        f.write(
            "## Split Strategy\n\n"
        )

        f.write(
            "แบ่ง Dataset แบบ Stratified Split "
            "เพื่อรักษาสัดส่วนของแต่ละ Class "
            "ให้กระจายอยู่ใน Train / Validation / Test\n\n"
        )

        f.write(
            "| Split | Ratio |\n"
        )

        f.write(
            "|---|---:|\n"
        )

        f.write(
            "| Train | 70% |\n"
        )

        f.write(
            "| Validation | 15% |\n"
        )

        f.write(
            "| Test | 15% |\n\n"
        )

        f.write(
            "### เหตุผลที่เลือก 70/15/15\n\n"
        )

        f.write(
            "Train 70% ใช้สำหรับฝึกโมเดล "
            "และให้ข้อมูลส่วนใหญ่กับการเรียนรู้\n\n"
        )

        f.write(
            "Validation 15% ใช้ตรวจสอบและปรับโมเดล "
            "ระหว่างการพัฒนา\n\n"
        )

        f.write(
            "Test 15% ใช้ประเมินประสิทธิภาพโมเดล "
            "ด้วยข้อมูลที่ไม่ได้ใช้ในการฝึก\n\n"
        )

        f.write(
            f"Random Seed: **{RANDOM_SEED}**\n\n"
        )

        f.write(
            "## Dataset Summary\n\n"
        )

        f.write(
            "| Class | Total | Train | Val | Test |\n"
        )

        f.write(
            "|---|---:|---:|---:|---:|\n"
        )

        for item in report:

            f.write(
                f"| {item['class']} "
                f"| {item['total']} "
                f"| {item['train']} "
                f"| {item['val']} "
                f"| {item['test']} |\n"
            )

        f.write("\n")

        f.write(
            "## Total\n\n"
        )

        f.write(
            f"- Total: **{total_all}** images\n"
        )

        f.write(
            f"- Train: **{total_train}** images\n"
        )

        f.write(
            f"- Validation: **{total_val}** images\n"
        )

        f.write(
            f"- Test: **{total_test}** images\n\n"
        )

        f.write(
            "## Manifest\n\n"
        )

        f.write(
            "- `train_manifest.csv`\n"
        )

        f.write(
            "- `val_manifest.csv`\n"
        )

        f.write(
            "- `test_manifest.csv`\n\n"
        )

        f.write(
            "## Graphs\n\n"
        )

        f.write(
            "- `dataset_class_distribution.png`\n"
        )

        f.write(
            "- `dataset_split_distribution.png`\n"
        )

        f.write(
            "- `dataset_split_pie.png`\n"
        )

    print(
        "\n✓ สร้าง README.md สำเร็จ"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 60)

    print(
        "       WASTE DATASET SPLIT PROGRAM"
    )

    print("=" * 60)


    # =====================================================
    # CHECK RATIO
    # =====================================================

    if (
        TRAIN_RATIO
        + VAL_RATIO
        + TEST_RATIO
        != 100
    ):

        print(
            "\n❌ Ratio ไม่ถูกต้อง"
        )

        return

    print(
        "\n✓ Split Ratio = 70 / 15 / 15"
    )

    print(
        f"✓ Random Seed = {RANDOM_SEED}"
    )


    # =====================================================
    # FIND DATASET
    # =====================================================

    classes = find_classes()

    if not classes:

        print(
            "\n❌ ไม่พบ Class หรือรูปภาพ"
        )

        return


    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    print(
        "\nกำลังตรวจสอบรูปซ้ำ..."
    )

    cleaned_classes = {}

    duplicate_total = 0

    for class_name, images in classes.items():

        unique_images, duplicates = (
            remove_duplicate_images(images)
        )

        cleaned_classes[class_name] = (
            unique_images
        )

        duplicate_total += duplicates

    classes = cleaned_classes

    print(
        f"✓ พบรูปซ้ำและตัดออก: "
        f"{duplicate_total} รูป"
    )


    # =====================================================
    # SHOW CLASSES
    # =====================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "              DATASET CLASS"
    )

    print(
        "=" * 60
    )

    for number, (
        class_name,
        images
    ) in enumerate(
        classes.items(),
        start=1
    ):

        print(
            f"\n[{number}] {class_name}"
        )

        print(
            f"    ทั้งหมด : {len(images)} รูป"
        )


    # =====================================================
    # DELETE OLD OUTPUT
    # =====================================================

    if OUTPUT_DIR.exists():

        print(
            "\nกำลังลบ Dataset Split เดิม..."
        )

        shutil.rmtree(
            OUTPUT_DIR
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # =====================================================
    # RANDOM SEED
    # =====================================================

    random.seed(
        RANDOM_SEED
    )


    # =====================================================
    # SPLIT
    # =====================================================

    report = []

    train_manifest = {}
    val_manifest = {}
    test_manifest = {}

    total_all = 0
    total_train = 0
    total_val = 0
    total_test = 0

    print(
        "\nกำลังแบ่ง Dataset..."
    )


    for class_name, images in classes.items():

        # Stratified Split
        train, val, test = split_images(
            images
        )


        # ตรวจ Data Leakage
        check_data_leakage(
            train,
            val,
            test
        )


        # Copy Train
        copy_images(
            train,
            OUTPUT_DIR
            / "train"
            / class_name
        )


        # Copy Validation
        copy_images(
            val,
            OUTPUT_DIR
            / "val"
            / class_name
        )


        # Copy Test
        copy_images(
            test,
            OUTPUT_DIR
            / "test"
            / class_name
        )


        # Manifest
        train_manifest[class_name] = train
        val_manifest[class_name] = val
        test_manifest[class_name] = test


        total = len(images)

        train_count = len(train)
        val_count = len(val)
        test_count = len(test)


        total_all += total
        total_train += train_count
        total_val += val_count
        total_test += test_count


        report.append(
            {
                "class": class_name,
                "total": total,
                "train": train_count,
                "val": val_count,
                "test": test_count
            }
        )


        print(
            "\n" + "-" * 50
        )

        print(
            class_name
        )

        print(
            f"Total : {total}"
        )

        print(
            f"Train : {train_count} "
            f"({TRAIN_RATIO}%)"
        )

        print(
            f"Val   : {val_count} "
            f"({VAL_RATIO}%)"
        )

        print(
            f"Test  : {test_count} "
            f"({TEST_RATIO}%)"
        )


    # =====================================================
    # SAVE MANIFEST
    # =====================================================

    print(
        "\nกำลังสร้าง Manifest..."
    )

    save_manifest(
        "train",
        train_manifest
    )

    save_manifest(
        "val",
        val_manifest
    )

    save_manifest(
        "test",
        test_manifest
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "                 SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        f"\nClass ทั้งหมด : {len(classes)}"
    )

    print(
        f"รูปทั้งหมด    : {total_all} รูป"
    )

    print(
        f"Train         : {total_train} รูป"
    )

    print(
        f"Validation    : {total_val} รูป"
    )

    print(
        f"Test          : {total_test} รูป"
    )


    # =====================================================
    # CREATE GRAPH
    # =====================================================

    create_graph(
        report,
        total_train,
        total_val,
        total_test
    )


    # =====================================================
    # CREATE README
    # =====================================================

    create_readme(
        report,
        total_all,
        total_train,
        total_val,
        total_test
    )


    # =====================================================
    # FINISH
    # =====================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "✅ Split Dataset + Manifest + Graph + README สำเร็จ!"
    )

    print(
        "=" * 60
    )

    print(
        "\nไฟล์ที่สร้าง:"
    )

    print(
        f"📁 {OUTPUT_DIR}"
    )

    print(
        "📊 dataset_class_distribution.png"
    )

    print(
        "📊 dataset_split_distribution.png"
    )

    print(
        "📊 dataset_split_pie.png"
    )

    print(
        "📄 README.md"
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()