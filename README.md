วิธีทดสอบ Data Collection

1. เปิด Git Bash แล้ว Clone โปรเจกต์

git clone https://github.com/68319090081-arch/Waste.git
cd Waste

2. เปลี่ยนไป Branch ของ Data Collection

git checkout feature/data-collection

3. ติดตั้ง Library

pip install -r requirements.txt

4. Login Kaggle

kaggle auth login

5. ดาวน์โหลด Dataset

python src/data_collection.py

Dataset จะถูกดาวน์โหลดอัตโนมัติลงในโฟลเดอร์ data/