@echo off
chcp 65001 >nul
echo 🚀 快速运行使用示例
echo ================================================
echo.

cd /d "%~dp0\..\.."
echo 📁 切换到项目根目录: %CD%
echo.

echo 🚀 运行使用示例...
python "%~dp0\usage_example.py"

echo.
echo 📝 示例运行完成
pause
