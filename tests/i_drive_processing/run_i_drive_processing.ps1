# I盘PDF文件批量处理工具 - PowerShell版本
# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 获取脚本所在目录并切换到项目根目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
Set-Location $projectRoot

Write-Host "🚀 I盘PDF文件批量处理工具" -ForegroundColor Green
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

# 检查I盘访问权限
Write-Host "📁 检查I盘访问权限..." -ForegroundColor Yellow
$iDrivePath = "I:\1T硬盘D"
if (Test-Path $iDrivePath) {
    try {
        $items = Get-ChildItem $iDrivePath -ErrorAction Stop
        Write-Host "✅ I盘访问正常，根目录包含 $($items.Count) 个项目" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ 无法访问I盘: $($_.Exception.Message)" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}
else {
    Write-Host "❌ I盘路径不存在: $iDrivePath" -ForegroundColor Red
    Write-Host "请检查驱动器是否已连接" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 开始处理
Write-Host ""
Write-Host "🚀 开始处理I盘PDF文件..." -ForegroundColor Green
Write-Host "注意：这可能需要很长时间，请耐心等待" -ForegroundColor Yellow
Write-Host "可以按Ctrl+C中断处理过程" -ForegroundColor Yellow
Write-Host ""

try {
    # 运行Python脚本
    python "$scriptDir\process_i_drive_pdfs.py"
    
    Write-Host ""
    Write-Host "📝 处理完成，请查看日志文件了解详细信息" -ForegroundColor Green
    Write-Host "日志文件位置：tests/logs/" -ForegroundColor Cyan
    Write-Host "符合条件的PDF文件已复制到：jc/" -ForegroundColor Cyan
}
catch {
    Write-Host ""
    Write-Host "❌ 处理过程中发生错误: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Write-Host ""
    Read-Host "按回车键退出"
}
