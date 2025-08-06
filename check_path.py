#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查路径是否存在
"""

from pathlib import Path

def check_path():
    """检查路径"""
    path = Path("E:\\1T硬盘D\\2个项目资料\\充电控制器\\办公\\国网控制器\\国网2.0控制器\\国网六统一\\发布版")
    
    print(f"检查路径: {path}")
    print(f"路径存在: {path.exists()}")
    
    if path.exists():
        print(f"路径类型: {'文件夹' if path.is_dir() else '文件'}")
        
        # 查找PDF文件
        pdf_files = list(path.rglob("*.pdf"))
        print(f"找到PDF文件数量: {len(pdf_files)}")
        
        if pdf_files:
            print("前5个PDF文件:")
            for i, pdf_file in enumerate(pdf_files[:5], 1):
                print(f"  {i}. {pdf_file.name}")
        else:
            print("未找到PDF文件")
    else:
        print("路径不存在，请检查路径是否正确")

if __name__ == "__main__":
    check_path() 