#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试递归PDF分类工具
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recursive_pdf_classify import RecursivePDFClassifier

def test_recursive_classifier():
    """测试递归PDF分类器"""
    
    # 创建测试用的jc文件夹（如果不存在）
    jc_folder = Path("jc")
    jc_folder.mkdir(exist_ok=True)
    
    # 检查是否有input_pdfs文件夹
    input_folder = Path("input_pdfs")
    if not input_folder.exists():
        print("❌ 未找到input_pdfs文件夹，请先创建该文件夹并放入一些PDF文件进行测试")
        print("或者使用其他包含PDF文件的文件夹路径")
        return
    
    print("🧪 开始测试递归PDF分类器...")
    print(f"📁 源文件夹: {input_folder}")
    print(f"📁 目标文件夹: {jc_folder}")
    
    # 创建分类器
    classifier = RecursivePDFClassifier(input_folder, jc_folder)
    
    # 开始扫描和处理
    try:
        classifier.scan_and_process()
        print("\n✅ 测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_with_custom_folder(folder_path):
    """使用自定义文件夹进行测试"""
    
    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return
    
    print(f"🧪 使用自定义文件夹测试: {folder_path}")
    
    # 创建分类器
    classifier = RecursivePDFClassifier(folder_path, "jc")
    
    # 开始扫描和处理
    try:
        classifier.scan_and_process()
        print("\n✅ 测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("递归PDF分类工具测试")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 使用命令行指定的文件夹
        custom_folder = sys.argv[1]
        test_with_custom_folder(custom_folder)
    else:
        # 使用默认的input_pdfs文件夹
        test_recursive_classifier()
    
    print("\n💡 提示:")
    print("1. 使用 'python test_recursive_classify.py' 测试默认文件夹")
    print("2. 使用 'python test_recursive_classify.py \"F:\\标准规范要求\\充电\"' 测试指定文件夹")
    print("3. 使用 'python recursive_pdf_classify.py \"F:\\标准规范要求\\充电\"' 直接运行分类工具")
