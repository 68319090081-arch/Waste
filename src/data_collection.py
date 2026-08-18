import os
import subprocess

DATASET = "phenomsg/waste-classification"

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "raw"
)

def download_dataset():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

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

    subprocess.run(command, check=True)


if __name__ == "__main__":
    download_dataset()