# -*- coding: utf-8 -*-
"""
PDF标准文档分类系统 - 快速部署脚本
一键部署到生产环境
"""

import os
import sys
import subprocess
import shutil
import json
from datetime import datetime

def create_deployment_config():
    """创建部署配置文件"""
    config = {
        "version": "2.0.0",
        "deployment_date": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment": {
            "input_directory": "./input_pdfs",
            "output_directory": "./jc",
            "template_file": "./mb6.png",
            "log_file": "./pdf_classify.log"
        },
        "processing_settings": {
            "timeout_seconds": 15,
            "max_pages_per_pdf": 5,
            "dpi_resolution": 300,
            "validation_threshold": 70
        },
        "ocr_settings": {
            "language": "chi_sim",
            "configs": [
                "--psm 6 -l chi_sim",
                "--psm 7 -l chi_sim",
                "--psm 8 -l chi_sim",
                "--psm 13 -l chi_sim"
            ]
        }
    }
    
    with open("deployment_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ 部署配置文件已创建: deployment_config.json")

def create_directory_structure():
    """创建标准目录结构"""
    directories = [
        "input_pdfs",      # 输入PDF目录
        "jc",              # 匹配成功输出目录
        "logs",            # 日志目录
        "templates",       # 自定义模板目录
        "backup",          # 备份目录
        "reports"          # 报告目录
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    # 复制模板文件
    if os.path.exists("mb6.png"):
        shutil.copy2("mb6.png", "templates/mb6.png")
        print("✅ 模板文件已复制到templates目录")

def create_batch_scripts():
    """创建批处理脚本"""
    
    # Windows批处理脚本
    windows_script = """@echo off
echo PDF标准文档分类系统
echo =====================

echo 检查环境...
python setup.py

echo.
echo 开始处理PDF文件...
python main.py input_pdfs --output-dir jc

echo.
echo 处理完成！
echo 结果文件位于 jc 目录
echo 日志文件：pdf_classify.log
pause
"""
    
    with open("run_classification.bat", "w", encoding="gbk") as f:
        f.write(windows_script)
    
    # Linux/macOS脚本
    unix_script = """#!/bin/bash
echo "PDF标准文档分类系统"
echo "===================="

echo "检查环境..."
python3 setup.py

echo ""
echo "开始处理PDF文件..."
python3 main.py input_pdfs --output-dir jc

echo ""
echo "处理完成！"
echo "结果文件位于 jc 目录"
echo "日志文件：pdf_classify.log"
"""
    
    with open("run_classification.sh", "w", encoding="utf-8") as f:
        f.write(unix_script)
    
    # 设置执行权限（Linux/macOS）
    try:
        os.chmod("run_classification.sh", 0o755)
    except:
        pass
    
    print("✅ 批处理脚本已创建:")
    print("   Windows: run_classification.bat")
    print("   Linux/macOS: run_classification.sh")

def create_monitoring_script():
    """创建监控脚本"""
    monitoring_script = """# -*- coding: utf-8 -*-
import os
import time
import json
from datetime import datetime
from pdf_processor import PDFProcessor

def monitor_processing():
    \"\"\"监控处理状态\"\"\"
    print("PDF处理监控系统启动...")
    
    while True:
        # 检查输入目录
        input_dir = "input_pdfs"
        if os.path.exists(input_dir):
            pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
            print(f"待处理PDF文件数: {len(pdf_files)}")
            
            if pdf_files:
                print("发现新文件，开始自动处理...")
                processor = PDFProcessor()
                results = processor.batch_process(input_dir, "jc")
                
                # 记录处理结果
                report = {
                    "timestamp": datetime.now().isoformat(),
                    "total_files": results['total_files'],
                    "successful_files": results['successful_files'],
                    "failed_files": results['failed_files']
                }
                
                with open(f"reports/processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
                    json.dump(report, f, indent=2)
                
                print(f"处理完成: {results['successful_files']}/{results['total_files']} 成功")
        
        time.sleep(30)  # 每30秒检查一次

if __name__ == "__main__":
    monitor_processing()
"""
    
    with open("monitor.py", "w", encoding="utf-8") as f:
        f.write(monitoring_script)
    
    print("✅ 监控脚本已创建: monitor.py")

def create_service_installer():
    """创建Windows服务安装脚本"""
    service_script = """# -*- coding: utf-8 -*-
import os
import sys

def install_windows_service():
    \"\"\"安装Windows服务\"\"\"
    print("正在安装PDF分类服务...")
    
    # 这里可以添加Windows服务安装逻辑
    # 需要额外的依赖包如pywin32
    
    print("服务安装功能需要管理员权限")
    print("请手动创建计划任务或使用任务计划程序")

def create_systemd_service():
    \"\"\"创建Linux systemd服务\"\"\"
    service_content = f\"\"\"[Unit]
Description=PDF Standard Document Classification Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
\"\"\"
    
    with open("pdf-classifier.service", "w") as f:
        f.write(service_content)
    
    print("✅ systemd服务文件已创建: pdf-classifier.service")
    print("安装命令:")
    print("  sudo cp pdf-classifier.service /etc/systemd/system/")
    print("  sudo systemctl enable pdf-classifier")
    print("  sudo systemctl start pdf-classifier")

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        install_windows_service()
    else:
        create_systemd_service()
"""
    
    with open("install_service.py", "w", encoding="utf-8") as f:
        f.write(service_script)
    
    print("✅ 服务安装脚本已创建: install_service.py")

def create_readme_production():
    """创建生产环境README"""
    readme_content = """# PDF标准文档分类系统 - 生产环境

## 🏗️ 部署完成

系统已成功部署到生产环境，包含以下组件：

### 📁 目录结构
```
pdf-classifier/
├── input_pdfs/          # 放置待处理的PDF文件
├── jc/                 # 匹配成功的PDF文件输出
├── logs/               # 系统日志
├── templates/          # 模板文件
├── backup/             # 备份文件
├── reports/            # 处理报告
├── main.py             # 主程序
├── pdf_processor.py    # 核心处理器
└── deployment_config.json  # 部署配置
```

### 🚀 快速使用

#### 方法1：批处理脚本（推荐）
- Windows: 双击 `run_classification.bat`
- Linux/macOS: 运行 `./run_classification.sh`

#### 方法2：命令行
```bash
# 处理input_pdfs目录的文件
python main.py input_pdfs

# 查看帮助
python main.py --help
```

#### 方法3：自动监控
```bash
# 启动监控服务（自动处理新文件）
python monitor.py
```

### 📋 使用流程

1. **放置文件**：将PDF文件复制到 `input_pdfs/` 目录
2. **运行处理**：执行批处理脚本或命令行
3. **查看结果**：检查 `jc/` 目录中的匹配文件
4. **查看日志**：检查 `pdf_classify.log` 了解处理详情

### 📊 系统监控

- **处理日志**：`pdf_classify.log`
- **处理报告**：`reports/` 目录
- **系统配置**：`deployment_config.json`

### 🔧 配置调整

编辑 `deployment_config.json` 修改系统参数：
- 超时时间
- 验证阈值  
- OCR配置
- 目录路径

### 📞 技术支持

- 查看详细文档：`USAGE_GUIDE.md`
- 运行诊断：`python demo.py`
- 测试功能：`python test_features.py`

---
部署时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系统版本：2.0.0
"""
    
    with open("README_PRODUCTION.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ 生产环境README已创建: README_PRODUCTION.md")

def main():
    """主部署函数"""
    print("🚀 PDF标准文档分类系统 - 快速部署")
    print("="*50)
    
    print("\n📦 创建部署配置...")
    create_deployment_config()
    
    print("\n📁 创建目录结构...")
    create_directory_structure()
    
    print("\n📝 创建批处理脚本...")
    create_batch_scripts()
    
    print("\n🔍 创建监控脚本...")
    create_monitoring_script()
    
    print("\n⚙️ 创建服务安装脚本...")
    create_service_installer()
    
    print("\n📚 创建生产环境文档...")
    create_readme_production()
    
    print("\n🎉 部署完成！")
    print("="*50)
    print("📋 下一步操作：")
    print("1. 将PDF文件放入 input_pdfs/ 目录")
    print("2. 运行批处理脚本开始处理")
    print("3. 查看 jc/ 目录中的结果文件")
    print("4. 查看 README_PRODUCTION.md 了解详细使用方法")
    
    print("\n💡 快速开始：")
    if sys.platform.startswith('win'):
        print("双击运行: run_classification.bat")
    else:
        print("命令行运行: ./run_classification.sh")

if __name__ == "__main__":
    main()
