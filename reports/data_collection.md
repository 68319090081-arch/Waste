### Data Collection



##### วัตถุประสงค์

จัดเตรียม Image Dataset สำหรับใช้ในการพัฒนาและทดสอบระบบจำแนกประเภทขยะ โดยเลือก Dataset ที่มี Label/Class ชัดเจนและเหมาะสมกับโครงงาน



##### แหล่งข้อมูล

ใช้ Image Dataset จาก Kaggle โดยดาวน์โหลดผ่าน Kaggle API ด้วย Python Script



##### Dataset:

`phenomsg/waste-classification`



##### การดำเนินงาน

1\.กำหนด Dataset ที่ต้องการจาก Kaggle

2\.ใช้ Python Script สำหรับดาวน์โหลด Dataset ผ่าน Kaggle API

3\.สร้างโฟลเดอร์ `data/` สำหรับจัดเก็บ Dataset ที่ดาวน์โหลด

4\.ตรวจสอบและจัดเตรียมข้อมูลรูปภาพสำหรับขั้นตอน Data Splitting และ Preprocessing

5\.ไม่อัปโหลดรูปภาพ Dataset ขึ้น GitHub เนื่องจากไฟล์มีขนาดใหญ่

6\.ใช้ `.gitignore` เพื่อป้องกันไม่ให้โฟลเดอร์ `data/` ถูก commit ขึ้น GitHub

##### 

##### การตั้งค่า Kaggle API

ผู้ใช้งานต้องตั้งค่า Kaggle API Key ของตนเอง (`kaggle.json`) ตามคำแนะนำใน README ก่อนใช้งาน Script



##### ผลลัพธ์

เมื่อรัน `src/data\_collection.py` ระบบจะดาวน์โหลด Dataset จาก Kaggle และจัดเก็บไว้ภายในโฟลเดอร์ `data/` โดยอัตโนมัติ เพื่อเตรียมข้อมูลสำหรับขั้นตอนถัดไปของโครงงาน

