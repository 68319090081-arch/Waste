# Waste Classification

## Dataset Collection

โปรเจกต์นี้ใช้ Waste Classification Dataset จาก Kaggle ของ PhenomSG

Dataset:
https://www.kaggle.com/datasets/phenomsg/waste-classification

## วิธีดาวน์โหลด Dataset

### 1. Clone Repository

เปิด Git Bash แล้วรันคำสั่ง:

```bash
git clone https://github.com/68319090081-arch/Waste.git
cd Waste

pip install -r requirements.txt

kaggle auth login

python src/data_collection.py