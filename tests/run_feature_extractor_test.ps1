#!/usr/bin/env pwsh
# PDF特征提取器功能测试脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PDF特征提取器功能测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python环境
Write-Host "正在检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python环境检查通过: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python命令执行失败"
    }
} catch {
    Write-Host "❌ 错误: 未找到Python环境" -ForegroundColor Red
    Write-Host "请确保已安装Python并添加到PATH环境变量" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""

# 检查依赖包
Write-Host "正在检查依赖包..." -ForegroundColor Yellow
try {
    python -c "import cv2, numpy, PIL, fitz" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 依赖包检查通过" -ForegroundColor Green
    } else {
        throw "依赖包检查失败"
    }
} catch {
    Write-Host "⚠️ 警告: 部分依赖包未安装" -ForegroundColor Yellow
    Write-Host "正在尝试安装依赖包..." -ForegroundColor Yellow
    
    try {
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 依赖包安装成功" -ForegroundColor Green
        } else {
            throw "依赖包安装失败"
        }
    } catch {
        Write-Host "❌ 依赖包安装失败" -ForegroundColor Red
        Write-Host "请手动安装: pip install opencv-python numpy pillow PyMuPDF" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

Write-Host ""

# 运行测试
Write-Host "正在运行PDF特征提取器测试..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

try {
    python test_pdf_feature_extractor.py
    $testExitCode = $LASTEXITCODE
} catch {
    Write-Host "❌ 测试执行失败: $($_.Exception.Message)" -ForegroundColor Red
    $testExitCode = 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "测试完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($testExitCode -eq 0) {
    Write-Host "🎉 测试成功完成！" -ForegroundColor Green
} else {
    Write-Host "⚠️ 测试过程中遇到问题" -ForegroundColor Yellow
}

Read-Host "按回车键退出"
exit $testExitCode
