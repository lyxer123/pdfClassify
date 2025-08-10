# Root Tests 测试工具 - PowerShell版本
# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 获取脚本所在目录并切换到项目根目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
Set-Location $projectRoot

Write-Host "🚀 Root Tests 测试工具" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# 检查PowerShell执行策略
Write-Host "📁 检查PowerShell执行策略..." -ForegroundColor Yellow
$executionPolicy = Get-ExecutionPolicy
Write-Host "当前执行策略: $executionPolicy" -ForegroundColor Cyan

if ($executionPolicy -eq "Restricted") {
    Write-Host "⚠️ 执行策略受限，尝试临时更改..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "✅ 执行策略已临时更改" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ 无法更改执行策略，请手动运行: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

# 检查Python环境
Write-Host "📁 检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python环境正常: $pythonVersion" -ForegroundColor Green
    }
    else {
        throw "Python命令执行失败"
    }
}
catch {
    Write-Host "❌ Python未安装或不在PATH中" -ForegroundColor Red
    Write-Host "请先安装Python并确保在PATH中" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查项目依赖
Write-Host "📁 检查项目依赖..." -ForegroundColor Yellow
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ 未找到requirements.txt文件" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 安装依赖包
Write-Host "🔧 安装依赖包..." -ForegroundColor Yellow
try {
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 依赖包安装完成" -ForegroundColor Green
    }
    else {
        throw "依赖包安装失败"
    }
}
catch {
    Write-Host "❌ 依赖包安装失败" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查测试目录结构
Write-Host "📁 检查测试目录结构..." -ForegroundColor Yellow
$testDir = "$scriptDir"
$requiredFiles = @("test_simple.py", "test_unified_analyzer.py", "usage_example.py")

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path "$testDir\$file")) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "❌ 缺少测试文件: $($missingFiles -join ', ')" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "✅ 测试文件检查完成" -ForegroundColor Green

# 显示测试选项
Write-Host ""
Write-Host "📋 可用的测试选项：" -ForegroundColor Cyan
Write-Host "1. 基本功能测试 (test_simple.py)" -ForegroundColor White
Write-Host "2. 统一分析器测试 (test_unified_analyzer.py)" -ForegroundColor White
Write-Host "3. 使用示例 (usage_example.py)" -ForegroundColor White
Write-Host "4. 运行所有测试" -ForegroundColor White
Write-Host ""

$choice = Read-Host "请选择要运行的测试 (1-4)"

# 执行选择的测试
switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 运行基本功能测试..." -ForegroundColor Green
        python "$testDir\test_simple.py"
    }
    "2" {
        Write-Host ""
        Write-Host "🚀 运行统一分析器测试..." -ForegroundColor Green
        python "$testDir\test_unified_analyzer.py"
    }
    "3" {
        Write-Host ""
        Write-Host "🚀 运行使用示例..." -ForegroundColor Green
        python "$testDir\usage_example.py"
    }
    "4" {
        Write-Host ""
        Write-Host "🚀 运行所有测试..." -ForegroundColor Green
        Write-Host ""
        Write-Host "=== 基本功能测试 ===" -ForegroundColor Yellow
        python "$testDir\test_simple.py"
        Write-Host ""
        Write-Host "=== 统一分析器测试 ===" -ForegroundColor Yellow
        python "$testDir\test_unified_analyzer.py"
        Write-Host ""
        Write-Host "=== 使用示例 ===" -ForegroundColor Yellow
        python "$testDir\usage_example.py"
    }
    default {
        Write-Host "❌ 无效选择，请重新运行脚本" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

Write-Host ""
Write-Host "📝 测试完成，请查看输出结果" -ForegroundColor Green
Write-Host "日志文件位置：tests/logs/" -ForegroundColor Cyan
Write-Host ""
Read-Host "按回车键退出"
