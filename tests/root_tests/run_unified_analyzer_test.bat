@echo off
chcp 65001 >nul
echo 🚀 快速运行统一分析器测试
echo ================================================
echo.

cd /d "%~dp0\..\.."
echo 📁 切换到项目根目录: %CD%
echo.

echo 🚀 运行统一分析器测试...
python "%~dp0\test_unified_analyzer.py"

echo.
echo 📝 测试完成
pause
