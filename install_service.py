# -*- coding: utf-8 -*-
import os
import sys

def install_windows_service():
    """安装Windows服务"""
    print("正在安装PDF分类服务...")
    
    # 这里可以添加Windows服务安装逻辑
    # 需要额外的依赖包如pywin32
    
    print("服务安装功能需要管理员权限")
    print("请手动创建计划任务或使用任务计划程序")

def create_systemd_service():
    """创建Linux systemd服务"""
    service_content = f"""[Unit]
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
"""
    
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
