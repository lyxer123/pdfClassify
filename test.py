#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF标准文档分类系统 - 简单测试
"""

import os

def test_basic():
    """基本测试"""
    print("PDF标准文档分类系统 - 基本测试")
    print("=" * 40)
    
    # 检查必要文件
    files = ["main.py", "pdf_processor.py", "config.py"]
    for file in files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
    
    # 检查可选文件
    optional_files = ["mb3.png", "requirements.txt"]
    for file in optional_files:
        if os.path.exists(file):
            print(f"✅ {file} (可选)")
        else:
            print(f"⚠️  {file} (可选)")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_basic() 