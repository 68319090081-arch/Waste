import os
import subprocess

# Kaggle Dataset
DATASET = "phenomsg/waste-classification"

# Folder สำหรับเก็บ Dataset
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def download_dataset():
    # สร้างโฟลเดอร์ data ถ้ายังไม่มี
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("====================================")
    print(" Waste Classification Dataset")
    print("====================================")
    print("Downloading dataset from Kaggle...")

    command = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        DATASET,
        "-p",
        OUTPUT_DIR,
        "--unzip"
    ]

    try:
        subprocess.run(command, check=True)

        print("\nDownload completed successfully!")
        print(f"Dataset location: {OUTPUT_DIR}/")

    except subprocess.CalledProcessError:
        print("\nDownload failed!")
        print("Please check your Kaggle API configuration.")


if __name__ == "__main__":
    download_dataset()