#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
递归PDF分类工具演示脚本
展示如何使用RecursivePDFClassifier类
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入测试包配置
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR
from pdf_analyzer import UnifiedPDFAnalyzer

def demo_basic_usage():
    """演示基本用法"""
    print("🚀 递归PDF分类工具演示")
    print("=" * 60)
    
    # 示例1：使用默认jc文件夹
    print("\n📋 示例1：使用默认jc文件夹")
    print("-" * 40)
    
    # 检查是否有input_pdfs文件夹
    source_folder = Path("input_pdfs")
    if source_folder.exists():
        print(f"✅ 找到源文件夹: {source_folder}")
        
        # 创建分析器
        analyzer = UnifiedPDFAnalyzer()
        
        # 开始处理
        print("🔄 开始处理...")
        analyzer.recursive_classify_pdfs(source_folder)
        
    else:
        print(f"❌ 未找到源文件夹: {source_folder}")
        print("💡 请创建input_pdfs文件夹并放入一些PDF文件进行测试")

def demo_custom_target():
    """演示自定义目标文件夹"""
    print("\n📋 示例2：自定义目标文件夹")
    print("-" * 40)
    
    source_folder = Path("input_pdfs")
    custom_target = Path("符合标准的文档")
    
    if source_folder.exists():
        print(f"✅ 找到源文件夹: {source_folder}")
        print(f"🎯 自定义目标文件夹: {custom_target}")
        
        # 创建分析器
        analyzer = UnifiedPDFAnalyzer()
        
        # 开始处理
        print("🔄 开始处理...")
        analyzer.recursive_classify_pdfs(source_folder, custom_target)
        
    else:
        print(f"❌ 未找到源文件夹: {source_folder}")

def demo_error_handling():
    """演示错误处理"""
    print("\n📋 示例3：错误处理演示")
    print("-" * 40)
    
    # 尝试处理不存在的文件夹
    non_existent_folder = Path("不存在的文件夹")
    print(f"🔍 尝试处理不存在的文件夹: {non_existent_folder}")
    
    try:
        analyzer = UnifiedPDFAnalyzer()
        analyzer.recursive_classify_pdfs(non_existent_folder)
    except Exception as e:
        print(f"✅ 正确捕获错误: {str(e)}")

def demo_statistics():
    """演示统计功能"""
    print("\n📋 示例4：统计功能演示")
    print("-" * 40)
    
    source_folder = Path("input_pdfs")
    if source_folder.exists():
        print(f"✅ 找到源文件夹: {source_folder}")
        
        # 创建分析器
        analyzer = UnifiedPDFAnalyzer()
        
        # 只扫描文件，不处理
        print("🔍 扫描文件...")
        pdf_files = []
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_path = Path(root) / file
                    pdf_files.append(pdf_path)
        
        print(f"📊 找到 {len(pdf_files)} 个PDF文件")
        
        if pdf_files:
            print("📁 文件列表:")
            for i, pdf_path in enumerate(pdf_files[:5]):  # 只显示前5个
                print(f"  {i+1}. {pdf_path.name}")
            if len(pdf_files) > 5:
                print(f"  ... 还有 {len(pdf_files) - 5} 个文件")
        
    else:
        print(f"❌ 未找到源文件夹: {source_folder}")

def main():
    """主函数"""
    print("🎯 递归PDF分类工具演示")
    print("=" * 60)
    
    # 检查依赖
    print("🔍 检查依赖...")
    try:
        import fitz
        import cv2
        import numpy as np
        from PIL import Image
        print("✅ 所有依赖包已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("💡 请运行: pip install -r requirements.txt")
        return
    
    # 运行演示
    demo_basic_usage()
    demo_custom_target()
    demo_error_handling()
    demo_statistics()
    
    print("\n" + "=" * 60)
    print("🎉 演示完成!")
    print("\n💡 使用提示:")
    print("1. 运行 'python recursive_pdf_classify.py \"文件夹路径\"' 开始分类")
    print("2. 运行 'python test_recursive_classify.py' 进行测试")
    print("3. 查看 usage_recursive_classify.md 了解详细用法")
    print("4. 查看 README_recursive_classify.md 了解项目详情")

if __name__ == "__main__":
    main()
