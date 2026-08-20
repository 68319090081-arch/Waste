import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

# ====== Font setup ======
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Tahoma', 'DejaVu Sans']
plt.style.use('ggplot')

# ==================================================
# ✅ Auto-detect project path — works on every computer!
# ==================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
image_dir = os.path.join(PROJECT_ROOT, "data")

# Check data folder
if not os.path.exists(image_dir):
    print("=" * 70)
    print("❌ ERROR: Data folder not found!")
    print(f"👉 Looking at: {image_dir}")
    print("💡 Make sure the 'data/' folder is outside the 'src/' folder")
    print("=" * 70)
    exit()

print("=" * 70)
print(f"✅ Data found at: {image_dir}")
print("🔍 Scanning images... please wait...")
print("=" * 70)

# ====== Allowed image extensions ======
image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

# ====== Variables ======
main_categories = {}
sub_categories = {}
image_info = []
corrupted_files = []
grayscale_files = []
duplicate_check = {}
total_images = 0

# ====== Scan all images ======
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
                
                # Check grayscale
                is_grayscale = (mode == 'L')
                if is_grayscale:
                    grayscale_files.append(filepath)
                
                # Calculate average brightness
                if is_grayscale:
                    brightness = np.mean(np.array(img))
                    mean_r = mean_g = mean_b = brightness
                else:
                    arr = np.array(img.convert('RGB'))
                    mean_r = np.mean(arr[:, :, 0])
                    mean_g = np.mean(arr[:, :, 1])
                    mean_b = np.mean(arr[:, :, 2])
                
                # Check duplicates
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

# Create output folder for figures
os.makedirs(os.path.join(PROJECT_ROOT, "figures"), exist_ok=True)
FIGURES_DIR = os.path.join(PROJECT_ROOT, "figures")

# ══════════════════════════════════════════════════════════════
# 📊 PART 1: Quantitative Analysis — Print to console
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 PART 1: Quantitative Analysis")
print("=" * 70)

print("\n[1.1] Total images and count per category")
print("-" * 55)
print(f"  Total images: {total_images:,}")
print(f"  Main categories: {len(main_categories)}")
for cat, count in sorted(main_categories.items(), key=lambda x: -x[1]):
    pct = (count / total_images * 100) if total_images > 0 else 0
    imbalance = "⚠️ Imbalanced" if pct > 35 or pct < 15 else "✅ Balanced"
    print(f"  {cat:20} : {count:6,} images  ({pct:5.1f}%)  {imbalance}")

print("\n[1.2] Distribution of resolution, aspect ratio, and file size")
print("-" * 55)
print(f"  Width (px)  : Min {df['width'].min():4.0f}  Max {df['width'].max():4.0f}  Mean {df['width'].mean():.0f}")
print(f"  Height (px) : Min {df['height'].min():4.0f}  Max {df['height'].max():4.0f}  Mean {df['height'].mean():.0f}")
print(f"  Aspect Ratio: Min {df['aspect_ratio'].min():.2f}  Max {df['aspect_ratio'].max():.2f}  Mean {df['aspect_ratio'].mean():.2f}")
print(f"  File Size (KB): Min {df['file_size_kb'].min():6.1f}  Max {df['file_size_kb'].max():7.1f}  Mean {df['file_size_kb'].mean():6.1f}")

print("\n[1.3] Color intensity and brightness distribution")
print("-" * 55)
print(f"  Red channel (R)  : Min {df['mean_r'].min():6.1f}  Max {df['mean_r'].max():6.1f}  Mean {df['mean_r'].mean():6.1f}")
print(f"  Green channel (G): Min {df['mean_g'].min():6.1f}  Max {df['mean_g'].max():6.1f}  Mean {df['mean_g'].mean():6.1f}")
print(f"  Blue channel (B) : Min {df['mean_b'].min():6.1f}  Max {df['mean_b'].max():6.1f}  Mean {df['mean_b'].mean():6.1f}")
print(f"  Avg Brightness    : Min {df['brightness'].min():6.1f}  Max {df['brightness'].max():6.1f}  Mean {df['brightness'].mean():6.1f}")

print("\n[1.4] File quality check")
print("-" * 55)
print(f"  ✅ Normal RGB images : {total_images - len(grayscale_files) - len(corrupted_files):,}")
print(f"  ⚠️ Grayscale images   : {len(grayscale_files):,}")
print(f"  ❌ Corrupted files    : {len(corrupted_files):,}")
print(f"  ⚠️ Possible duplicates : {dup_count:,}")

# ══════════════════════════════════════════════════════════════
# 👁️ PART 2: Qualitative Analysis
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("👁️ PART 2: Qualitative Analysis")
print("=" * 70)
print("""
[2.1] Sample images from each category
  → See the figure plots below
  → Evaluate clarity, viewing angle, and label consistency
""")
print("""
[2.2] Potential issues and impact on model training
──────────────────────────────────────────────────────────────
  • Blurry images           → Features unclear → Hard to learn
  • Strange angles/sizes    → Shape varies → Hard to recognize
  • Watermarks/noise        → Model may learn artifacts instead of objects
  • Incorrect labels         → Wrong from the start → Predictions will be wrong
  • Too dark/bright          → Inconsistent colors → Normalize before use
  • Mixed image sizes        → Must resize to same size before input
  • Imbalanced data           → Rare classes will be less accurate
  • Mixed RGB/Grayscale      → Different channels → Convert all to RGB
""")
print("""
[2.3] Recommendations before training
──────────────────────────────────────────────────────────────
  1. Resize all images to same size, e.g. 224×224 or 512×512
  2. Convert all images to RGB 3-channel format
  3. Normalize pixel values to range 0–1, and standardize mean/std
  4. If imbalanced → Use class weights or apply Data Augmentation
  5. Remove corrupted files and check duplicates before training
  6. Visually verify all labels
""")

# ══════════════════════════════════════════════════════════════
# 📈 PART 3: Plotting — All titles in English
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📈 PART 3: Generating plots...")
print("=" * 70)

colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
names_main = sorted(main_categories.keys())
counts_main = [main_categories[k] for k in names_main]

# ---------- Plot 1: Count per category ----------
plt.figure(figsize=(8, 5))
bars = plt.bar(names_main, counts_main, color=colors, edgecolor='white', linewidth=2)
plt.title('1. Number of Images per Category', fontsize=14, fontweight='bold', pad=15)
plt.ylabel('Number of Images', fontsize=11)
plt.xticks(rotation=15)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.ylim(0, max(counts_main) * 1.15)
for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, h + max(counts_main)*0.03,
             f'{h:,}', ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '01_count_by_category.png'), dpi=150, bbox_inches='tight')
print("✅ Saved: 01_count_by_category.png")

# ---------- Plot 2: Proportion Pie Chart ----------
plt.figure(figsize=(7, 6))
plt.pie(counts_main, labels=names_main, colors=colors,
        autopct='%1.1f%%', startangle=90, pctdistance=0.85,
        textprops={'fontweight': 'bold'})
plt.title('2. Proportion of Images by Category', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '02_proportion_pie.png'), dpi=150, bbox_inches='tight')
print("✅ Saved: 02_proportion_pie.png")

# ---------- Plot 3: Resolution Scatter ----------
plt.figure(figsize=(8, 5))
plt.scatter(df['width'], df['height'], alpha=0.4, s=15, color='#34495e')
plt.xlabel('Width (pixels)', fontsize=11)
plt.ylabel('Height (pixels)', fontsize=11)
plt.title('3. Distribution of Image Resolution', fontsize=14, fontweight='bold', pad=15)
plt.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '03_resolution_scatter.png'), dpi=150, bbox_inches='tight')
print("✅ Saved: 03_resolution_scatter.png")

# ---------- Plot 4: Aspect Ratio Histogram ----------
plt.figure(figsize=(8, 5))
plt.hist(df['aspect_ratio'], bins=30, color='#16a085', alpha=0.7, edgecolor='white')
plt.xlabel('Aspect Ratio (Width / Height)', fontsize=11)
plt.ylabel('Number of Images', fontsize=11)
plt.title('4. Distribution of Aspect Ratio', fontsize=14, fontweight='bold', pad=15)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '04_aspect_ratio.png'), dpi=150, bbox_inches='tight')
print("✅ Saved: 04_aspect_ratio.png")

# ---------- Plot 5: File Size Histogram ----------
plt.figure(figsize=(8, 5))
plt.hist(df['file_size_kb'], bins=30, color='#9b59b6', alpha=0.7, edgecolor='white')
plt.xlabel('File Size (KB)', fontsize=11)
plt.ylabel('Number of Images', fontsize=11)
plt.title('5. Distribution of File Sizes', fontsize=14, fontweight='bold', pad=15)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '05_file_size.png'), dpi=150, bbox_inches='tight')
print("✅ Saved: 05_file_size.png")

# ---------- Plot 6: RGB Histogram ----------
plt.figure(figsize=(8, 5))
plt.hist(df['mean_r'], bins=30, color='#e74c3c', alpha=0.45, label='Red Channel', density=True)
plt.hist(df['mean_g'], bins=30, color='#2ecc71', alpha=0.45, label='Green Channel', density=True)
plt.hist(df['mean_b'], bins=30, color='#3498db', alpha=0.45, label='Blue Channel', density=True)
plt.xlabel('Pixel Intensity (0–255)', fontsize=11)
plt.ylabel('Density', fontsize=11)
plt.title('6. RGB Color Intensity Distribution', fontsize=14, fontweight='bold', pad=15)
plt.legend(fontsize=10)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '06_rgb_histogram.png'), dpi=150, bbox_inches='tight')
print("✅ Saved: 06_rgb_histogram.png")

# ---------- Plot 7: Brightness Histogram ----------
plt.figure(figsize=(8, 5))
plt.hist(df['brightness'], bins=30, color='#f39c12', alpha=0.7, edgecolor='white')
plt.xlabel('Average Brightness (0–255)', fontsize=11)
plt.ylabel('Number of Images', fontsize=11)
plt.title('7. Distribution of Average Brightness', fontsize=14, fontweight='bold', pad=15)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '07_brightness.png'), dpi=150, bbox_inches='tight')
print("✅ Saved: 07_brightness.png")

# ---------- Plot 8: Sample Images ----------
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
            ax.text(0.5, 0.5, 'Image not available', ha='center', va='center')
        ax.set_title(f'{cat}', fontsize=10, fontweight='bold')
        ax.axis('off')
plt.suptitle('8. Sample Images from Each Category', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '08_sample_images.png'), dpi=150, bbox_inches='tight')
print("✅ Saved: 08_sample_images.png")

plt.close('all')

# ══════════════════════════════════════════════════════════════
# 🎯 Summary
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("🎉 Analysis Complete")
print("=" * 70)

most_common = max(main_categories.items(), key=lambda x: x[1])
least_common = min(main_categories.items(), key=lambda x: x[1])
imbalance_ratio = most_common[1] / least_common[1] if least_common[1] > 0 else 999

print(f"""
📌 Summary
─────────────────────────────────────────────────────────────
• Total Images          : {total_images:,}
• Main Categories       : {len(main_categories)}
• Most Frequent Category: {most_common[0]} ({most_common[1]:,})
• Least Frequent Category: {least_common[0]} ({least_common[1]:,})
• Imbalance Ratio       : {imbalance_ratio:.1f}:1 → {'⚠️ Imbalanced' if imbalance_ratio > 2 else '✅ Well Balanced'}
• Grayscale Images      : {len(grayscale_files)}
• Corrupted Files       : {len(corrupted_files)}
• Possible Duplicates    : {dup_count}

📁 Figures saved to: {FIGURES_DIR}/
   01_count_by_category.png   → Image Count by Category
   02_proportion_pie.png      → Category Proportions
   03_resolution_scatter.png   → Resolution Distribution
   04_aspect_ratio.png         → Aspect Ratio Distribution
   05_file_size.png            → File Size Distribution
   06_rgb_histogram.png        → RGB Color Intensities
   07_brightness.png           → Brightness Distribution
   08_sample_images.png        → Sample Gallery
""")
print("=" * 70)