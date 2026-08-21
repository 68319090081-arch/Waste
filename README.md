# Waste Dataset Split Report

## Split Strategy

- Train: 70%
- Validation: 15%
- Test: 15%
- Random Seed: 42

ใช้ Stratified Split โดยแบ่งแยกภายในแต่ละ Class เพื่อรักษาสัดส่วนของ Class ในแต่ละชุดข้อมูล

## Dataset Summary

| Class | Total | Train | Val | Test |
|---|---:|---:|---:|---:|
| batteries | 1070 | 749 | 160 | 161 |
| cans_all_type | 2690 | 1883 | 404 | 403 |
| ceramic_product | 1360 | 952 | 204 | 204 |
| coffee_tea_bags | 1470 | 1029 | 220 | 221 |
| diapers | 1440 | 1008 | 216 | 216 |
| e-waste | 2660 | 1862 | 399 | 399 |
| egg_shells | 1230 | 861 | 184 | 185 |
| food_scraps | 1470 | 1029 | 220 | 221 |
| glass_containers | 1350 | 945 | 202 | 203 |
| kitchen_waste | 1140 | 798 | 171 | 171 |
| paints | 1500 | 1050 | 225 | 225 |
| paper_products | 1180 | 826 | 177 | 177 |
| pesticides | 1350 | 945 | 202 | 203 |
| plastic_bottles | 1260 | 882 | 189 | 189 |
| platics_bags_wrappers | 1330 | 931 | 200 | 199 |
| sanitary_napkin | 1100 | 770 | 165 | 165 |
| stroform_product | 1170 | 819 | 176 | 175 |
| yard_trimmings | 1270 | 889 | 190 | 191 |

## Manifest

- train_manifest.csv
- val_manifest.csv
- test_manifest.csv

## Graphs

- dataset_class_distribution.png
- dataset_split_distribution.png
- dataset_split_pie.png
