@echo off
REM 运行PDF特征提取器使用示例
REM 作者: AI Assistant
REM 日期: 2025-01-10

echo ========================================
echo PDF特征提取器使用示例
echo ========================================
echo.

REM 切换到项目根目录
cd /d "%~dp0\..\.."

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo 开始运行示例...
echo.

REM 运行示例
python tests\root_tests\example_usage.py

echo.
echo 示例运行完成！
pause
