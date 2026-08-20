✅ Sure! Here is everything in English 🎉
📋 File Execution Order
plaintext
📂 src
 ├ 📜 data_collection.py    # ① Download dataset from Kaggle
 ├ 📜 eda.py                 # ② Analyze data + Generate charts
 ├ 📜 preprocessing.py       # ③ Prepare & clean data
 ├ 📜 image_processing.py    # ④ Process images
 └ 📜 data_split.py          # ⑤ Split into train/test sets
🚀 Option 1 — Run manually in order
bash
# ① Download dataset first
python src/data_collection.py

# ② Analyze & visualize
python src/eda.py

# ③ Preprocess data
python src/preprocessing.py

# ④ Process images
python src/image_processing.py

# ⑤ Split dataset
python src/data_split.py
🚀 Option 2 — Full Auto start.bat (Recommended)
batch
@echo off
chcp 65001 >nul 2>&1
title Waste Classification Pipeline
echo ========================================
echo    WASTE CLASSIFICATION PIPELINE
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] Installing required packages...
pip install matplotlib pandas numpy pillow kaggle opencv-python --quiet
echo Done.
echo.

echo [2/6] Checking Kaggle configuration...
set "KAGGLE_FILE=%USERPROFILE%\.kaggle\kaggle.json"

if exist "%KAGGLE_FILE%" (
    echo Kaggle API configured OK.
) else (
    echo ============================================================
    echo  KAGGLE API KEY NOT FOUND
    echo.
    echo  How to get your key:
    echo   1. Go to Kaggle.com and sign in
    echo   2. Click your profile --^> Settings --^> API
    echo   3. Click "Create New API Token"
    echo   4. The file kaggle.json will download automatically
    echo   5. Copy kaggle.json to THIS folder:
    echo      %cd%
    echo.
    echo  Place the file here, then press any key to continue...
    echo ============================================================
    pause

    if exist "%cd%\kaggle.json" (
        echo Setting up Kaggle...
        if not exist "%USERPROFILE%\.kaggle" mkdir "%USERPROFILE%\.kaggle"
        copy "%cd%\kaggle.json" "%USERPROFILE%\.kaggle\kaggle.json" >nul
        echo Configuration complete.
    ) else (
        echo File not found. Please try again.
        pause
        exit /b
    )
)
echo.

echo [3/6] Step 1/5 - Downloading dataset...
python src\data_collection.py
echo Dataset ready.
echo.

echo [4/6] Step 2/5 - Exploratory Data Analysis...
python src\eda.py
echo Analysis complete.
echo.

echo [5/6] Step 3/5 - Preprocessing data...
python src\preprocessing.py
echo Preprocessing complete.
echo.

echo [6/6] Step 4-5/5 - Processing images & Splitting dataset...
python src\image_processing.py
python src\data_split.py
echo Processing complete.
echo.

echo ========================================
echo ✅ ALL TASKS COMPLETED SUCCESSFULLY!
echo ========================================
echo.
pause