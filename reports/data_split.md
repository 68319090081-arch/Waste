# Waste Dataset Data Splitting Report

## Overview

โปรเจกต์นี้จัดทำขึ้นเพื่อเตรียมชุดข้อมูล Waste Dataset สำหรับการพัฒนาโมเดล Machine Learning โดยทำการแบ่งข้อมูลออกเป็นชุด Training, Validation และ Test พร้อมตรวจสอบข้อมูลซ้ำ (Duplicate Images) และป้องกันปัญหา Data Leakage เพื่อให้การประเมินผลโมเดลมีความถูกต้องและน่าเชื่อถือ

---

## Data Splitting Strategy

ชุดข้อมูลถูกแบ่งออกเป็น 3 ส่วน ดังนี้

| Dataset    | Ratio |
| ---------- | ----- |
| Train      | 70%   |
| Validation | 15%   |
| Test       | 15%   |

เลือกใช้สัดส่วน 70:15:15 เนื่องจากเป็นสัดส่วนที่เหมาะสมสำหรับการฝึกโมเดล โดยมีข้อมูลเพียงพอสำหรับการเรียนรู้ และยังคงเหลือข้อมูลสำหรับการตรวจสอบและประเมินผลประสิทธิภาพของโมเดล

---

## Class-wise Split

การแบ่งข้อมูลดำเนินการภายในแต่ละ Class แยกกัน เพื่อรักษาสัดส่วนของข้อมูลแต่ละประเภทให้ใกล้เคียงกันในทุกชุดข้อมูล ส่งผลให้ Train, Validation และ Test มีการกระจายตัวของข้อมูลที่สมดุลมากขึ้น

---

## Reproducibility

กำหนดค่า Random Seed เท่ากับ 42

```python
SEED = 42
```

เพื่อให้การแบ่งข้อมูลสามารถทำซ้ำได้และได้ผลลัพธ์เดิมทุกครั้งที่รันโปรแกรม

---

## Duplicate Removal

ก่อนแบ่งข้อมูล โปรแกรมทำการตรวจสอบรูปภาพซ้ำโดยใช้ SHA-256 Hash

วัตถุประสงค์

* ลดข้อมูลซ้ำใน Dataset
* เพิ่มคุณภาพของข้อมูล
* ลดความลำเอียงในการฝึกโมเดล

---

## Data Leakage Prevention

มีการตรวจสอบไม่ให้รูปภาพเดียวกันปรากฏอยู่ในหลายชุดข้อมูล โดยเปรียบเทียบค่า Hash ของไฟล์ใน Train, Validation และ Test

ผลลัพธ์

* ไม่มีรูปภาพซ้ำข้ามชุดข้อมูล
* ลดความเสี่ยงของ Data Leakage
* เพิ่มความน่าเชื่อถือของผลการประเมินโมเดล

---

## Manifest Files

โปรแกรมสร้างไฟล์ Manifest สำหรับบันทึกรายชื่อข้อมูลในแต่ละชุด

* train_manifest.csv
* val_manifest.csv
* test_manifest.csv

ข้อมูลที่จัดเก็บใน Manifest ประกอบด้วย

* Filename
* Class
* Split
* Source Path

ช่วยให้สามารถตรวจสอบย้อนหลังและติดตามข้อมูลต้นฉบับได้

---

## Results

ผลการแบ่งข้อมูลหลังจากลบรูปภาพซ้ำและตรวจสอบข้อมูลเรียบร้อยแล้ว

| Dataset    | Images | Percentage |
| ---------- | -----: | ---------: |
| Train      |  1,737 |      70.2% |
| Validation |    373 |      15.1% |
| Test       |    366 |      14.8% |
| Total      |  2,476 |       100% |

ผลลัพธ์ที่ได้ใกล้เคียงกับสัดส่วนที่กำหนดไว้ (70:15:15) โดยความแตกต่างเล็กน้อยเกิดจากการปัดเศษจำนวนรูปภาพในแต่ละ Class

---

## Generated Outputs

โปรแกรมสร้างผลลัพธ์อัตโนมัติ ดังนี้

### Dataset Split

* dataset_split/train/
* dataset_split/val/
* dataset_split/test/

### Manifest Files

* train_manifest.csv
* val_manifest.csv
* test_manifest.csv

### Reports and Graphs

* README.md
* dataset_class_distribution.png
* dataset_split_distribution.png
* dataset_split_pie.png

---

## Conclusion

โปรแกรมสามารถแบ่งข้อมูล Waste Dataset ได้สำเร็จตามสัดส่วน 70:15:15 พร้อมทั้งตรวจสอบข้อมูลซ้ำ ป้องกัน Data Leakage และสร้างไฟล์ Manifest สำหรับการตรวจสอบย้อนหลัง ส่งผลให้ Dataset มีความพร้อมสำหรับการนำไปใช้พัฒนาโมเดล Image Classification ได้อย่างมีประสิทธิภาพ
