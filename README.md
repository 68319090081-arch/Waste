# Waste Dataset Split Report

## Split Strategy

แบ่ง Dataset แบบ Stratified Split เพื่อรักษาสัดส่วนของแต่ละ Class ให้กระจายอยู่ใน Train / Validation / Test

| Split | Ratio |
|---|---:|
| Train | 70% |
| Validation | 15% |
| Test | 15% |

### เหตุผลที่เลือก 70/15/15

Train 70% ใช้สำหรับฝึกโมเดล และให้ข้อมูลส่วนใหญ่กับการเรียนรู้

Validation 15% ใช้ตรวจสอบและปรับโมเดล ระหว่างการพัฒนา

Test 15% ใช้ประเมินประสิทธิภาพโมเดล ด้วยข้อมูลที่ไม่ได้ใช้ในการฝึก

Random Seed: **42**

## Dataset Summary

| Class | Total | Train | Val | Test |
|---|---:|---:|---:|---:|
| batteries | 110 | 77 | 16 | 17 |
| cans_all_type | 271 | 190 | 41 | 40 |
| ceramic_product | 138 | 97 | 21 | 20 |
| coffee_tea_bags | 157 | 110 | 24 | 23 |
| diapers | 145 | 102 | 22 | 21 |
| e-waste | 268 | 188 | 40 | 40 |
| egg_shells | 124 | 87 | 19 | 18 |
| food_scraps | 147 | 103 | 22 | 22 |
| glass_containers | 140 | 98 | 21 | 21 |
| kitchen_waste | 114 | 80 | 17 | 17 |
| paints | 153 | 107 | 23 | 23 |
| paper_products | 78 | 55 | 12 | 11 |
| pesticides | 138 | 97 | 21 | 20 |
| platics_bags_wrappers | 134 | 94 | 20 | 20 |
| sanitary_napkin | 110 | 77 | 16 | 17 |
| stroform_product | 118 | 83 | 18 | 17 |
| yard_trimmings | 131 | 92 | 20 | 19 |

## Total

- Total: **2476** images
- Train: **1737** images
- Validation: **373** images
- Test: **366** images

## Manifest

- `train_manifest.csv`
- `val_manifest.csv`
- `test_manifest.csv`

## Graphs

- `dataset_class_distribution.png`
- `dataset_split_distribution.png`
- `dataset_split_pie.png`
