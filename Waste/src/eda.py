import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

# ====== ตั้งค่าฟอนต์ ======
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Tahoma', 'DejaVu Sans']
plt.style.use('ggplot')

# ==================================================
# ✅ หาที่อยู่อัตโนมัติ — ใช้ได้กับทุกเครื่อง!
# ==================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
image_dir = os.path.join(PROJECT_ROOT, "data")

# ตรวจสอบโฟลเดอร์
if not os.path.exists(image_dir):
    print("=" * 70)
    print("❌ ERROR: หาโฟลเดอร์ข้อมูลไม่เจอ!")
    print(f"👉 ค้นหาที่: {image_dir}")
    print("💡 ตรวจสอบว่ามีโฟลเดอร์ data/ ไว้ข้างนอกโฟลเดอร์ src/")
    print("=" * 70)
    exit()

print("=" * 70)
print(f"✅ พบข้อมูลที่: {image_dir}")
print("🔍 กำลังสแกนรูปภาพ... กรุณารอสักครู่...")
print("=" * 70)

# ====== นามสกุลไฟล์ที่ยอมรับ ======
image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

# ====== ตัวแปรเก็บข้อมูล ======
main_categories = {}
sub_categories = {}
image_info = []
corrupted_files = []
grayscale_files = []
duplicate_check = {}
total_images = 0

# ====== อ่านข้อมูลรูปภาพทุกรูป ======
for root, dirs, files in os.walk(image_dir):
    for filename in files:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in image_extensions:
            continue

        filepath = os.path.join(root, filename)
        path_parts = os.path.relpath(root, image_dir).split(os.sep)

        main_cat = path_parts[0] if len(path_parts) >= 1 else "Unknown"
        sub_cat = path_parts[1] if len(path_parts) >= 2 else ""

        total_images += 1
        main_categories[main_cat] = main_categories.get(main_cat, 0) + 1
        if sub_cat:
            sub_key = f"{main_cat} / {sub_cat}"
            sub_categories[sub_key] = sub_categories.get(sub_key, 0) + 1

        try:
            with Image.open(filepath) as img:
                width, height = img.size
                mode = img.mode
                file_size_kb = os.path.getsize(filepath) / 1024

                # ตรวจสอบภาพขาว-ดำ
                is_grayscale = (mode == 'L')
                if is_grayscale:
                    grayscale_files.append(filepath)

                # คำนวณค่าความสว่างเฉลี่ย
                if is_grayscale:
                    brightness = np.mean(np.array(img))
                    mean_r = mean_g = mean_b = brightness
                else:
                    arr = np.array(img.convert('RGB'))
                    mean_r = np.mean(arr[:, :, 0])
                    mean_g = np.mean(arr[:, :, 1])
                    mean_b = np.mean(arr[:, :, 2])

                # ตรวจสอบภาพซ้ำ
                img_hash = f"{width}x{height}_R{mean_r:.0f}G{mean_g:.0f}B{mean_b:.0f}"
                duplicate_check[img_hash] = duplicate_check.get(img_hash, 0) + 1

                image_info.append({
                    'main_category': main_cat,
                    'sub_category': sub_cat,
                    'width': width,
                    'height': height,
                    'aspect_ratio': round(width / height, 3),
                    'file_size_kb': round(file_size_kb, 2),
                    'mode': mode,
                    'mean_r': round(mean_r, 1),
                    'mean_g': round(mean_g, 1),
                    'mean_b': round(mean_b, 1),
                    'brightness': round(np.mean([mean_r, mean_g, mean_b]), 1),
                    'filepath': filepath
                })
        except Exception:
            corrupted_files.append(filepath)
            continue

df = pd.DataFrame(image_info)
duplicates = {k: v for k, v in duplicate_check.items() if v > 1}
dup_count = sum(v - 1 for v in duplicates.values())

# สร้างโฟลเดอร์เก็บกราฟ
os.makedirs(os.path.join(PROJECT_ROOT, "figures"), exist_ok=True)
FIGURES_DIR = os.path.join(PROJECT_ROOT, "figures")

# ══════════════════════════════════════════════════════════════
# 📊 PART 1: การวิเคราะห์เชิงปริมาณ — แสดงทางหน้าจอ
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 PART 1: การวิเคราะห์เชิงปริมาณ (Quantitative Analysis)")
print("=" * 70)

print("\n[1.1] จำนวนรูปภาพทั้งหมด และจำนวนต่อหมวดหมู่")
print("-" * 55)
print(f"  รูปภาพทั้งหมด: {total_images:,} รูป")
print(f"  จำนวนหมวดหลัก: {len(main_categories)} หมวด")
for cat, count in sorted(main_categories.items(), key=lambda x: -x[1]):
    pct = (count / total_images * 100) if total_images > 0 else 0
    imbalance = "⚠️ ไม่สมดุล" if pct > 35 or pct < 15 else "✅ สมดุลดี"
    print(f"  {cat:20} : {count:6,} รูป  ({pct:5.1f}%)  {imbalance}")

print("\n[1.2] การกระจายของขนาดภาพ, สัดส่วนภาพ และขนาดไฟล์")
print("-" * 55)
print(f"  ความกว้าง (px)   : ต่ำสุด {df['width'].min():4.0f}  สูงสุด {df['width'].max():4.0f}  เฉลี่ย {df['width'].mean():.0f}")
print(f"  ความสูง (px)      : ต่ำสุด {df['height'].min():4.0f}  สูงสุด {df['height'].max():4.0f}  เฉลี่ย {df['height'].mean():.0f}")
print(f"  อัตราส่วนภาพ (W/H): ต่ำสุด {df['aspect_ratio'].min():.2f}  สูงสุด {df['aspect_ratio'].max():.2f}  เฉลี่ย {df['aspect_ratio'].mean():.2f}")
print(f"  ขนาดไฟล์ (KB)     : ต่ำสุด {df['file_size_kb'].min():6.1f}  สูงสุด {df['file_size_kb'].max():7.1f}  เฉลี่ย {df['file_size_kb'].mean():6.1f}")

print("\n[1.3] การกระจายค่าสีและความสว่าง (Pixel Intensity Distribution)")
print("-" * 55)
print(f"  ช่องสีแดง (R)     : ต่ำสุด {df['mean_r'].min():6.1f}  สูงสุด {df['mean_r'].max():6.1f}  เฉลี่ย {df['mean_r'].mean():6.1f}")
print(f"  ช่องสีเขียว (G)   : ต่ำสุด {df['mean_g'].min():6.1f}  สูงสุด {df['mean_g'].max():6.1f}  เฉลี่ย {df['mean_g'].mean():6.1f}")
print(f"  ช่องสีน้ำเงิน (B) : ต่ำสุด {df['mean_b'].min():6.1f}  สูงสุด {df['mean_b'].max():6.1f}  เฉลี่ย {df['mean_b'].mean():6.1f}")
print(f"  ความสว่างเฉลี่ย   : ต่ำสุด {df['brightness'].min():6.1f}  สูงสุด {df['brightness'].max():6.1f}  เฉลี่ย {df['brightness'].mean():6.1f}")

print("\n[1.4] ตรวจสอบไฟล์ผิดปกติ")
print("-" * 55)
print(f"  ✅ รูปภาพปกติ (RGB) : {total_images - len(grayscale_files) - len(corrupted_files):,} รูป")
print(f"  ⚠️  รูปภาพขาว-ดำ        : {len(grayscale_files):,} รูป")
print(f"  ❌ ไฟล์เสีย/อ่านไม่ได้   : {len(corrupted_files):,} รูป")
print(f"  ⚠️  รูปภาพที่อาจซ้ำกัน    : {dup_count:,} รูป")

# ══════════════════════════════════════════════════════════════
# 👁️ PART 2: การวิเคราะห์เชิงคุณภาพ
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("👁️ PART 2: การวิเคราะห์เชิงคุณภาพ (Qualitative Analysis)")
print("=" * 70)

print("""
[2.1] ตัวอย่างภาพจากแต่ละหมวดหมู่
  → ดูภาพตัวอย่างทางกราฟที่แสดงข้างล่างนี้
  → เพื่อประเมินความชัดเจน, มุมมอง, ความสอดคล้องกับป้ายกำกับ
""")

print("""
[2.2] ปัญหาที่อาจพบและผลกระทบต่อการฝึกสอนโมเดล
──────────────────────────────────────────────────────────────
  • ภาพเบลอ / ไม่ชัดเจน     → คุณลักษณะของวัตถุไม่ชัด → โมเดลเรียนรู้ยาก
  • มุมกล้องแปลก / ระยะต่างกัน → รูปร่างเปลี่ยนไป → จดจำยาก
  • มีลายน้ำ / สิ่งรบกวน     → โมเดลอาจเรียนรู้ลายน้ำแทนวัตถุจริง
  • ป้ายกำกับผิด             → สอนผิดตั้งแต่ต้น → ทำนายผิดตลอด
  • ภาพสว่าง/มืดเกินไป       → ค่าสีไม่สม่ำเสมอ → ควรปรับมาตรฐานก่อนใช้
  • ขนาดภาพต่างกันมาก        → ต้องปรับให้เท่ากันก่อนส่งเข้าโมเดล
  • ข้อมูลไม่สมดุล            → หมวดที่มีรูปน้อยจะทำนายได้แม่นยำน้อยกว่า
  • มีภาพขาว-ดำปนกับสี        → จำนวนช่องสีไม่เท่ากัน → ต้องแปลงให้สอดคล้องกัน
""")

print("""
[2.3] ข้อเสนอแนะก่อนนำไปฝึกสอนโมเดล
──────────────────────────────────────────────────────────────
  1. ปรับขนาดภาพทุกรูปให้เท่ากัน เช่น 224×224 หรือ 512×512 พิกเซล
  2. แปลงภาพทุกรูปให้เป็น RGB 3 ช่องสี (แปลงภาพขาว-ดำให้เป็นสี)
  3. ปรับค่าสีให้อยู่ในช่วง 0–1 และปรับค่าเฉลี่ย–ส่วนเบี่ยงเบนให้มาตรฐาน
  4. หากข้อมูลไม่สมดุล → ใช้การถ่วงน้ำหนัก หรือสร้างภาพเพิ่ม (Data Augmentation)
  5. ลบไฟล์เสีย และตรวจสอบภาพซ้ำก่อนฝึกสอน
  6. ตรวจสอบความถูกต้องของป้ายกำกับด้วยสายตาอย่างละเอียด
""")

# ══════════════════════════════════════════════════════════════
# 📈 PART 3: กราฟแยกแต่ละหัวข้อ — คนละกราฟ ไม่เบียดกัน!
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📈 PART 3: กำลังสร้างกราฟ... (แยกแต่ละหัวข้อ)")
print("=" * 70)

colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
names_main = sorted(main_categories.keys())
counts_main = [main_categories[k] for k in names_main]

# ---------- กราฟที่ 1: จำนวนรูปภาพแต่ละหมวด ----------
plt.figure(figsize=(8, 5))
bars = plt.bar(names_main, counts_main, color=colors, edgecolor='white', linewidth=2)
plt.title('1. จำนวนรูปภาพแยกตามหมวดหมู่', fontsize=14, fontweight='bold', pad=15)
plt.ylabel('จำนวนรูปภาพ', fontsize=11)
plt.xticks(rotation=15)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.ylim(0, max(counts_main) * 1.15)
for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, h + max(counts_main)*0.03,
             f'{h:,}', ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '01_count_by_category.png'), dpi=150, bbox_inches='tight')
print("✅ บันทึก: 01_count_by_category.png")

# ---------- กราฟที่ 2: สัดส่วนรูปภาพแต่ละหมวด (วงกลม) ----------
plt.figure(figsize=(7, 6))
plt.pie(counts_main, labels=names_main, colors=colors,
        autopct='%1.1f%%', startangle=90, pctdistance=0.85,
        textprops={'fontweight': 'bold'})
plt.title('2. สัดส่วนรูปภาพแต่ละหมวดหมู่', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '02_proportion_pie.png'), dpi=150, bbox_inches='tight')
print("✅ บันทึก: 02_proportion_pie.png")

# ---------- กราฟที่ 3: การกระจายขนาดภาพ (กว้าง x สูง) ----------
plt.figure(figsize=(8, 5))
plt.scatter(df['width'], df['height'], alpha=0.4, s=15, color='#34495e')
plt.xlabel('ความกว้าง (พิกเซล)', fontsize=11)
plt.ylabel('ความสูง (พิกเซล)', fontsize=11)
plt.title('3. การกระจายขนาดภาพ (ความกว้าง × ความสูง)', fontsize=14, fontweight='bold', pad=15)
plt.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '03_resolution_scatter.png'), dpi=150, bbox_inches='tight')
print("✅ บันทึก: 03_resolution_scatter.png")

# ---------- กราฟที่ 4: การกระจายอัตราส่วนภาพ ----------
plt.figure(figsize=(8, 5))
plt.hist(df['aspect_ratio'], bins=30, color='#16a085', alpha=0.7, edgecolor='white')
plt.xlabel('อัตราส่วนภาพ (ความกว้าง ÷ ความสูง)', fontsize=11)
plt.ylabel('จำนวนรูปภาพ', fontsize=11)
plt.title('4. การกระจายอัตราส่วนภาพ', fontsize=14, fontweight='bold', pad=15)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '04_aspect_ratio.png'), dpi=150, bbox_inches='tight')
print("✅ บันทึก: 04_aspect_ratio.png")

# ---------- กราฟที่ 5: การกระจายขนาดไฟล์ ----------
plt.figure(figsize=(8, 5))
plt.hist(df['file_size_kb'], bins=30, color='#9b59b6', alpha=0.7, edgecolor='white')
plt.xlabel('ขนาดไฟล์ (KB)', fontsize=11)
plt.ylabel('จำนวนรูปภาพ', fontsize=11)
plt.title('5. การกระจายขนาดไฟล์', fontsize=14, fontweight='bold', pad=15)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '05_file_size.png'), dpi=150, bbox_inches='tight')
print("✅ บันทึก: 05_file_size.png")

# ---------- กราฟที่ 6: ฮิสโตแกรมค่าสี RGB ----------
plt.figure(figsize=(8, 5))
plt.hist(df['mean_r'], bins=30, color='#e74c3c', alpha=0.45, label='ช่องสีแดง', density=True)
plt.hist(df['mean_g'], bins=30, color='#2ecc71', alpha=0.45, label='ช่องสีเขียว', density=True)
plt.hist(df['mean_b'], bins=30, color='#3498db', alpha=0.45, label='ช่องสีน้ำเงิน', density=True)
plt.xlabel('ค่าความเข้มสี (0–255)', fontsize=11)
plt.ylabel('ความหนาแน่น', fontsize=11)
plt.title('6. การกระจายค่าสีแต่ละช่อง (RGB Histogram)', fontsize=14, fontweight='bold', pad=15)
plt.legend(fontsize=10)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '06_rgb_histogram.png'), dpi=150, bbox_inches='tight')
print("✅ บันทึก: 06_rgb_histogram.png")

# ---------- กราฟที่ 7: ฮิสโตแกรมความสว่าง ----------
plt.figure(figsize=(8, 5))
plt.hist(df['brightness'], bins=30, color='#f39c12', alpha=0.7, edgecolor='white')
plt.xlabel('ค่าความสว่างเฉลี่ย (0–255)', fontsize=11)
plt.ylabel('จำนวนรูปภาพ', fontsize=11)
plt.title('7. การกระจายค่าความสว่างของภาพ', fontsize=14, fontweight='bold', pad=15)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '07_brightness.png'), dpi=150, bbox_inches='tight')
print("✅ บันทึก: 07_brightness.png")

# ---------- กราฟที่ 8: ตัวอย่างภาพแต่ละหมวด ----------
plt.figure(figsize=(12, 7))
unique_cats = list(df['main_category'].unique())
sample_count = min(4, len(unique_cats))
for i in range(sample_count):
    cat = unique_cats[i]
    sample_rows = df[df['main_category'] == cat].head(3)
    for j in range(min(3, len(sample_rows))):
        ax = plt.subplot(4, 3, i*3 + j + 1)
        try:
            img = Image.open(sample_rows.iloc[j]['filepath'])
            ax.imshow(img)
        except:
            ax.text(0.5, 0.5, 'ไม่สามารถแสดงภาพได้', ha='center', va='center')
        ax.set_title(f'{cat}', fontsize=10, fontweight='bold')
        ax.axis('off')
plt.suptitle('8. ตัวอย่างภาพจากแต่ละหมวดหมู่', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '08_sample_images.png'), dpi=150, bbox_inches='tight')
print("✅ บันทึก: 08_sample_images.png")

plt.close('all')  # ปิดกราฟทั้งหมด เพื่อไม่ให้แสดงซ้อนกัน

# ══════════════════════════════════════════════════════════════
# 🎯 สรุปผลรวม
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("🎉 สรุปผลการวิเคราะห์ข้อมูลเสร็จสิ้น")
print("=" * 70)
most_common = max(main_categories.items(), key=lambda x: x[1])
least_common = min(main_categories.items(), key=lambda x: x[1])
imbalance_ratio = most_common[1] / least_common[1] if least_common[1] > 0 else 999

print(f"""
📌 ข้อมูลสรุป
─────────────────────────────────────────────────────────────
• จำนวนรูปภาพทั้งหมด     : {total_images:,} รูป
• จำนวนหมวดหลัก           : {len(main_categories)} หมวด
• หมวดที่มีรูปมากที่สุด    : {most_common[0]} ({most_common[1]:,} รูป)
• หมวดที่มีรูปน้อยที่สุด    : {least_common[0]} ({least_common[1]:,} รูป)
• อัตราส่วนมาก/น้อยสุด     : {imbalance_ratio:.1f}:1 → {'⚠️ ข้อมูลไม่สมดุล' if imbalance_ratio > 2 else '✅ ข้อมูลสมดุลดี'}
• รูปภาพขาว-ดำปนมา          : {len(grayscale_files)} รูป
• ไฟล์เสีย/อ่านไม่ได้        : {len(corrupted_files)} รูป
• รูปภาพที่อาจซ้ำกัน        : {dup_count} รูป

📁 กราฟทั้งหมดบันทึกไว้ที่: {FIGURES_DIR}/
   01_count_by_category.png   → จำนวนรูปภาพแยกตามหมวด
   02_proportion_pie.png      → สัดส่วนรูปภาพแบบวงกลม
   03_resolution_scatter.png  → การกระจายขนาดภาพ
   04_aspect_ratio.png        → การกระจายอัตราส่วนภาพ
   05_file_size.png           → การกระจายขนาดไฟล์
   06_rgb_histogram.png       → ฮิสโตแกรมค่าสี RGB
   07_brightness.png          → การกระจายค่าความสว่าง
   08_sample_images.png       → ตัวอย่างภาพแต่ละหมวด
""")
print("=" * 70)