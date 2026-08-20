@echo off
chcp 65001 >nul 2>&1
title โปรแกรมวิเคราะห์ข้อมูลขยะ
echo ========================================
echo    🚀 เริ่มทำงานอัตโนมัติ
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] กำลังติดตั้งแพ็กเกจที่จำเป็น...
pip install matplotlib pandas numpy pillow kaggle --quiet
echo ✅ ติดตั้งเสร็จเรียบร้อย
echo.

echo [2/4] ตรวจสอบไฟล์ Kaggle...
set "KAGGLE_FILE=%USERPROFILE%\.kaggle\kaggle.json"

if exist "%KAGGLE_FILE%" (
    echo ✅ พบไฟล์ kaggle.json พร้อมใช้งาน
) else (
    echo ============================================================
    echo ❌ ไม่พบไฟล์ kaggle.json
    echo.
    echo 📥 วิธีดำเนินการ:
    echo    1. เข้าเว็บ Kaggle.com --^> เข้าสู่ระบบ
    echo    2. คลิกรูปโปรไฟล์ --^> Settings --^> เลื่อนลงหา API
    echo    3. กดปุ่ม "Create New API Token"
    echo    4. ไฟล์ kaggle.json จะถูกดาวน์โหลดมา
    echo    5. นำไฟล์ kaggle.json มาวางไว้ที่ โฟลเดอร์นี้:
    echo       %cd%
    echo.
    echo 💡 เมื่อนำไฟล์มาวางเสร็จแล้ว กดปุ่มอะไรก็ได้เพื่อดำเนินการต่อ
    echo ============================================================
    pause

    if exist "%cd%\kaggle.json" (
        echo ✅ พบไฟล์ kaggle.json กำลังนำไปวางที่ถูกที่...
        if not exist "%USERPROFILE%\.kaggle" mkdir "%USERPROFILE%\.kaggle"
        copy "%cd%\kaggle.json" "%USERPROFILE%\.kaggle\kaggle.json" >nul
        echo ✅ นำไฟล์ไปวางเรียบร้อยแล้ว
    ) else (
        echo ❌ ยังไม่พบไฟล์ในโฟลเดอร์นี้ โปรดลองใหม่อีกครั้ง
        pause
        exit /b
    )
)
echo.

echo [3/4] กำลังตรวจสอบและดาวน์โหลดข้อมูล...
python src\data_collection.py
echo ✅ ข้อมูลพร้อมใช้งาน
echo.

echo [4/4] กำลังวิเคราะห์ข้อมูล...
echo ========================================
python src\eda.py
echo ========================================
echo.
echo ✅ ทุกขั้นตอนเสร็จสิ้นเรียบร้อยแล้ว!
echo.
pause