#!/usr/bin/env pwsh
<#
.SYNOPSIS
    运行PDF页面选择模式测试
    
.DESCRIPTION
    此脚本用于测试PDF特征提取器的页面选择模式功能，
    包括前N页、第一页、所有页面和后N页模式。
    
.PARAMETER Verbose
    显示详细输出
    
.EXAMPLE
    .\run_page_modes_test.ps1
    
.EXAMPLE
    .\run_page_modes_test.ps1 -Verbose
    
.NOTES
    作者: AI Assistant
    日期: 2025-01-10
#>

param(
    [switch]$Verbose
)

# 设置错误操作首选项
$ErrorActionPreference = "Stop"

# 显示标题
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PDF页面选择模式测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# 切换到项目根目录
Set-Location $ProjectRoot
Write-Host "项目根目录: $ProjectRoot" -ForegroundColor Green

# 检查Python是否可用
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python命令执行失败"
    }
    Write-Host "Python版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未找到Python，请确保Python已安装并添加到PATH" -ForegroundColor Red
    Write-Host "错误详情: $_" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查测试文件是否存在
$testFile = Join-Path $ProjectRoot "tests\root_tests\test_page_modes.py"
if (-not (Test-Path $testFile)) {
    Write-Host "错误: 测试文件不存在: $testFile" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "开始运行测试..." -ForegroundColor Yellow
Write-Host ""

# 运行测试
try {
    $testResult = python $testFile 2>&1
    $exitCode = $LASTEXITCODE
    
    # 显示测试结果
    Write-Host $testResult
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "✅ 测试完成！" -ForegroundColor Green
    } else {
        Write-Host "❌ 测试失败，退出代码: $exitCode" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ 运行测试时发生错误: $_" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""
Read-Host "按回车键退出"

exit $exitCode
