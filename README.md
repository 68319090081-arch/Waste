Waste Classification

1.ชื่อโปรเจกต์
โปรเจกต์ Waste Classification เป็นระบบสำหรับการจำแนกประเภทขยะ
โดยใช้ Waste Classification Dataset จาก Kaggle

2.ที่มาของ Dataset
Dataset ที่ใช้: Waste Classification Dataset จาก PhenomSG

Kaggle:
https://www.kaggle.com/datasets/phenomsg/waste-classification

Dataset ประกอบด้วยประเภทขยะหลัก ได้แก่
- Hazardous
- Non-Recyclable
- Organic
- Recyclable

การตั้งค่า Kaggle API
ผู้ใช้งานแต่ละคนต้องใช้ Kaggle Account ของตนเอง
เพื่อยืนยันตัวตนก่อนดาวน์โหลด Dataset

รันคำสั่ง
kaggle auth login 
จากนั้นทำตามขั้นตอนที่แสดงบนหน้าจอ

วิธีติดตั้งและวิธีรัน Code
ติดตั้งโปรเจกต์
git clone https://github.com/68319090081-arch/Waste.git
cd Waste

ติดตั้ง Library
pip install -r requirements.txt

ดาวน์โหลด Dataset
python src/data_collection.py

Dataset จะถูกดาวน์โหลดอัตโนมัติไปยังโฟลเดอร์ data/

โครงสร้าง Repository

📁 Root
- `README.md` — รายละเอียดโครงการ
- `requirements.txt` — รายการ Library ที่ต้องใช้
- `.gitignore` — ไฟล์ที่ไม่ต้องการให้ Git ติดตาม

📁 src/
ไฟล์ Python สำหรับประมวลผลข้อมูล
- data_collection.py
- eda.py`
- preprocessing.py
- image_processing.py
- data_split.py

📁 data/
เก็บ Dataset ที่ดาวน์โหลดจาก Kaggle

📁 reports/
เอกสารรายงานผลการดำเนินงาน
- eda_summary.md
- data_collection.md
- data_split.md
- pre-imageprocessing.md

📁 slides/
Waste Classification Dataset.pdf

หมายเหตุ: โฟลเดอร์ data/ จะไม่ถูก Commit ขึ้น GitHub เนื่องจากกำหนดไว้ใน .gitignore


5.สมาชิกและหน้าที่รับผิดชอบ

คนที่ 1: นายอนุชิต เอี่ยมโมฬี
หน้าที่: Data Collection
Branch: feature/data-collection

คนที่ 2: นายอนวัฒน์ เทพนาคิน
หน้าที่: EDA
Branch: feature/eda

คนที่ 3: นายสุวิทย์ ชมวิจิตร
หน้าที่: Preprocessing
Branch: feature/preprocessing

คนที่ 4: นายณัฐพล ผลเจริญ
หน้าที่: Data Split
Branch: feature/data-split