#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF特征提取器的页面选择模式功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
def setup_paths():
    """设置路径，确保能够导入项目模块"""
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root

# 设置路径
PROJECT_ROOT = setup_paths()

# 尝试导入测试包配置，如果失败则使用本地配置
try:
    from tests import PROJECT_ROOT as TEST_PROJECT_ROOT
    PROJECT_ROOT = TEST_PROJECT_ROOT
except ImportError:
    pass  # 使用本地设置的PROJECT_ROOT

def test_page_modes():
    """测试不同的页面选择模式"""
    
    # 检查是否有测试PDF文件
    test_pdf = PROJECT_ROOT / "input_pdfs" / "test.pdf"
    if not test_pdf.exists():
        print("请确保 input_pdfs/test.pdf 文件存在")
        print(f"当前检查路径: {test_pdf}")
        return
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
    except ImportError as e:
        print(f"❌ 无法导入 PDFFeatureExtractor: {e}")
        return
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor()
    
    print("=== 测试PDF页面选择模式 ===\n")
    
    # 测试前N页模式
    print("1. 测试前N页模式 (first_n):")
    try:
        result = extractor.process_pdf_file(str(test_pdf), max_pages=3, page_mode="first_n")
        if result['success']:
            print(f"   成功处理 {result['pages_analyzed']} 页")
            for page in result['page_results']:
                print(f"   第{page['page_number']}页: {'符合' if page['compliance'] else '不符合'}标准")
        else:
            print(f"   处理失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"   测试失败: {str(e)}")
    
    print()
    
    # 测试第一页模式
    print("2. 测试第一页模式 (first_page):")
    try:
        result = extractor.process_pdf_file(str(test_pdf), max_pages=3, page_mode="first_page")
        if result['success']:
            print(f"   成功处理 {result['pages_analyzed']} 页")
            for page in result['page_results']:
                print(f"   第{page['page_number']}页: {'符合' if page['compliance'] else '不符合'}标准")
        else:
            print(f"   处理失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"   测试失败: {str(e)}")
    
    print()
    
    # 测试所有页面模式
    print("3. 测试所有页面模式 (all_pages):")
    try:
        result = extractor.process_pdf_file(str(test_pdf), max_pages=3, page_mode="all_pages")
        if result['success']:
            print(f"   成功处理 {result['pages_analyzed']} 页")
            for page in result['page_results']:
                print(f"   第{page['page_number']}页: {'符合' if page['compliance'] else '不符合'}标准")
        else:
            print(f"   处理失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"   测试失败: {str(e)}")
    
    print()
    
    # 测试后N页模式
    print("4. 测试后N页模式 (last_n):")
    try:
        result = extractor.process_pdf_file(str(test_pdf), max_pages=3, page_mode="last_n")
        if result['success']:
            print(f"   成功处理 {result['pages_analyzed']} 页")
            for page in result['page_results']:
                print(f"   第{page['page_number']}页: {'符合' if page['compliance'] else '不符合'}标准")
        else:
            print(f"   处理失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"   测试失败: {str(e)}")
    
    print("\n=== 测试完成 ===")

def main():
    """主函数"""
    print("🔍 开始测试PDF页面选择模式功能...")
    print(f"项目根目录: {PROJECT_ROOT}")
    print()
    
    test_page_modes()

if __name__ == "__main__":
    main()
