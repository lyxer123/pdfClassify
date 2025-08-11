@echo off
chcp 65001 >nul
echo ========================================
echo PDF特征提取器功能测试
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python环境
    echo 请确保已安装Python并添加到PATH环境变量
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

echo 正在检查依赖包...
python -c "import cv2, numpy, PIL, fitz" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 警告: 部分依赖包未安装
    echo 正在尝试安装依赖包...
            pip install -r ../../requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败
        echo 请手动安装: pip install opencv-python numpy pillow PyMuPDF
        pause
        exit /b 1
    )
)

echo ✅ 依赖包检查通过
echo.

echo 正在运行PDF特征提取器测试...
echo ========================================
python test_pdf_feature_extractor.py

echo.
echo ========================================
echo 测试完成
echo ========================================
pause
