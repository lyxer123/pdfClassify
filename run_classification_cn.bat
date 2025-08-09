@echo off
chcp 65001 >nul

echo ========================================
echo    PDF标准文档分类系统
echo ========================================
echo.

echo [1/3] 检查环境配置...
python setup.py
if errorlevel 1 (
    echo 错误：环境检查失败，请检查Python和依赖包安装
    pause
    exit /b 1
)
echo ✓ 环境检查完成
echo.

echo [2/3] 开始处理PDF文件...
echo 输入目录：input_pdfs
echo 输出目录：jc
echo.
python main.py input_pdfs --output-dir jc
if errorlevel 1 (
    echo 错误：PDF处理失败
    pause
    exit /b 1
)
echo.

echo [3/3] 处理完成！
echo ========================================
echo ✓ 匹配成功的PDF文件已复制到 jc 目录
echo ✓ 详细日志请查看 pdf_classify.log
echo ✓ 可视化结果：feature_visualization.png
echo ========================================
echo.
echo 按任意键退出...
pause >nul
