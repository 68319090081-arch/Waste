@echo off
chcp 65001 >nul 2>&1
title Waste Classification Pipeline
echo ========================================
echo    WASTE CLASSIFICATION PIPELINE
echo ========================================
echo.
cd /d "%~dp0"

echo [1/6] Installing required packages...
pip install opencv-python pillow imagehash tqdm transformers torch pandas matplotlib kaggle numpy --quiet
echo All packages installed successfully.
echo.

echo [2/6] Checking Kaggle configuration...
set "KAGGLE_FILE=%USERPROFILE%\.kaggle\kaggle.json"
if exist "%KAGGLE_FILE%" (
    echo Kaggle API configured OK.
) else (
    echo ============================================================
    echo  KAGGLE API KEY NOT FOUND
    echo.
    echo  Place your kaggle.json in THIS folder, then press any key!
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

echo [3/6] Downloading dataset...
python src\data_collection.py
echo Dataset ready.
echo.

echo [4/6] Analyzing data (EDA)...
python src\eda.py
echo Analysis complete.
echo.

echo [5/6] Cleaning and preprocessing data...
python src\preprocessing.py
echo Preprocessing complete.
echo.

echo [6/6] Processing images and Splitting dataset...
python src\image_processing.py
python src\data_split.py
echo All processing complete.
echo.

echo ========================================
echo ALL TASKS FINISHED SUCCESSFULLY!
echo ========================================
echo.
pause