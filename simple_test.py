#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试脚本
"""

from pathlib import Path

def main():
    """主函数"""
    print("简化测试")
    print("=" * 30)
    
    # 检查路径
    path = Path("E:\\1T硬盘D\\2个项目资料\\充电控制器\\办公\\国网控制器\\国网2.0控制器\\国网六统一\\发布版")
    
    print(f"检查路径: {path}")
    print(f"路径存在: {path.exists()}")
    
    if not path.exists():
        print("❌ 路径不存在")
        return
    
    # 查找PDF文件
    try:
        pdf_files = list(path.rglob("*.pdf"))
        print(f"✅ 找到 {len(pdf_files)} 个PDF文件")
        
        if pdf_files:
            print("前3个文件:")
            for i, pdf_file in enumerate(pdf_files[:3], 1):
                print(f"  {i}. {pdf_file.name}")
        else:
            print("❌ 未找到PDF文件")
            return
        
        # 测试第一个文件
        if pdf_files:
            test_file = pdf_files[0]
            print(f"\n测试第一个文件: {test_file.name}")
            
            # 这里可以添加实际的PDF处理测试
            print("✅ 路径和文件检查通过")
            
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main() 