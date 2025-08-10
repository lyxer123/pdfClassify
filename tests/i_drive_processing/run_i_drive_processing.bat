@echo off
chcp 65001 >nul
echo 🚀 I盘PDF文件批量处理工具
echo ================================================
echo.

echo 📁 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    echo 请先安装Python并确保在PATH中
    pause
    exit /b 1
)

echo ✅ Python环境正常
echo.

echo 📁 检查项目依赖...
cd /d "%~dp0\..\.."
if not exist "requirements.txt" (
    echo ❌ 未找到requirements.txt文件
    pause
    exit /b 1
)

echo 🔧 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖包安装失败
    pause
    exit /b 1
)

echo ✅ 依赖包安装完成
echo.

echo 🚀 开始处理I盘PDF文件...
echo 注意：这可能需要很长时间，请耐心等待
echo 可以按Ctrl+C中断处理过程
echo.

python "%~dp0\process_i_drive_pdfs.py"

echo.
echo 📝 处理完成，请查看日志文件了解详细信息
echo 日志文件位置：tests/logs/
echo 符合条件的PDF文件已复制到：jc/
echo.
pause
