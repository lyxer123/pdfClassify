@echo off
chcp 65001 >nul
echo 🚀 Root Tests 测试工具
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

echo 📋 可用的测试选项：
echo 1. 基本功能测试 (test_simple.py)
echo 2. 统一分析器测试 (test_unified_analyzer.py)
echo 3. 使用示例 (usage_example.py)
echo 4. 运行所有测试
echo.

set /p choice="请选择要运行的测试 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🚀 运行基本功能测试...
    python "%~dp0\test_simple.py"
) else if "%choice%"=="2" (
    echo.
    echo 🚀 运行统一分析器测试...
    python "%~dp0\test_unified_analyzer.py"
) else if "%choice%"=="3" (
    echo.
    echo 🚀 运行使用示例...
    python "%~dp0\usage_example.py"
) else if "%choice%"=="4" (
    echo.
    echo 🚀 运行所有测试...
    echo.
    echo === 基本功能测试 ===
    python "%~dp0\test_simple.py"
    echo.
    echo === 统一分析器测试 ===
    python "%~dp0\test_unified_analyzer.py"
    echo.
    echo === 使用示例 ===
    python "%~dp0\usage_example.py"
) else (
    echo ❌ 无效选择，请重新运行脚本
    pause
    exit /b 1
)

echo.
echo 📝 测试完成，请查看输出结果
echo 日志文件位置：tests/logs/
echo.
pause
