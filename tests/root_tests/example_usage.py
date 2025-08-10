#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF特征提取器使用示例
展示如何使用新的页面选择模式功能
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

def example_first_n_pages():
    """示例1: 分析前N页"""
    print("示例1: 分析前3页")
    print("-" * 30)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
    except ImportError as e:
        print(f"❌ 无法导入 PDFFeatureExtractor: {e}")
        return
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor()
    
    # 示例PDF文件路径
    pdf_file = PROJECT_ROOT / "input_pdfs" / "example.pdf"
    
    if not pdf_file.exists():
        print(f"请确保PDF文件存在: {pdf_file}")
        return
    
    try:
        result = extractor.process_pdf_file(str(pdf_file), max_pages=3, page_mode="first_n")
        print(f"处理结果: {'成功' if result['success'] else '失败'}")
        if result['success']:
            print(f"分析页数: {result['pages_analyzed']}")
            print(f"页面模式: {result['page_mode']}")
            print(f"整体符合性: {'是' if result['overall_compliance'] else '否'}")
    except Exception as e:
        print(f"处理出错: {str(e)}")

def example_first_page():
    """示例2: 只分析第一页"""
    print("示例2: 只分析第一页")
    print("-" * 30)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
    except ImportError as e:
        print(f"❌ 无法导入 PDFFeatureExtractor: {e}")
        return
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor()
    
    # 示例PDF文件路径
    pdf_file = PROJECT_ROOT / "input_pdfs" / "example.pdf"
    
    if not pdf_file.exists():
        print(f"请确保PDF文件存在: {pdf_file}")
        return
    
    try:
        result = extractor.process_pdf_file(str(pdf_file), page_mode="first_page")
        print(f"处理结果: {'成功' if result['success'] else '失败'}")
        if result['success']:
            print(f"分析页数: {result['pages_analyzed']}")
            print(f"页面模式: {result['page_mode']}")
            print(f"整体符合性: {'是' if result['overall_compliance'] else '否'}")
    except Exception as e:
        print(f"处理出错: {str(e)}")

def example_all_pages():
    """示例3: 分析所有页面"""
    print("示例3: 分析所有页面")
    print("-" * 30)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
    except ImportError as e:
        print(f"❌ 无法导入 PDFFeatureExtractor: {e}")
        return
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor()
    
    # 示例PDF文件路径
    pdf_file = PROJECT_ROOT / "input_pdfs" / "example.pdf"
    
    if not pdf_file.exists():
        print(f"请确保PDF文件存在: {pdf_file}")
        return
    
    try:
        result = extractor.process_pdf_file(str(pdf_file), page_mode="all_pages")
        print(f"处理结果: {'成功' if result['success'] else '失败'}")
        if result['success']:
            print(f"分析页数: {result['pages_analyzed']}")
            print(f"页面模式: {result['page_mode']}")
            print(f"整体符合性: {'是' if result['overall_compliance'] else '否'}")
    except Exception as e:
        print(f"处理出错: {str(e)}")

def example_last_n_pages():
    """示例4: 分析后N页"""
    print("示例4: 分析后2页")
    print("-" * 30)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
    except ImportError as e:
        print(f"❌ 无法导入 PDFFeatureExtractor: {e}")
        return
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor()
    
    # 示例PDF文件路径
    pdf_file = PROJECT_ROOT / "input_pdfs" / "example.pdf"
    
    if not pdf_file.exists():
        print(f"请确保PDF文件存在: {pdf_file}")
        return
    
    try:
        result = extractor.process_pdf_file(str(pdf_file), max_pages=2, page_mode="last_n")
        print(f"处理结果: {'成功' if result['success'] else '失败'}")
        if result['success']:
            print(f"分析页数: {result['pages_analyzed']}")
            print(f"页面模式: {result['page_mode']}")
            print(f"整体符合性: {'是' if result['overall_compliance'] else '否'}")
            
            # 显示每页的页码信息
            if result['page_results']:
                print("页面详情:")
                for page in result['page_results']:
                    print(f"  第{page['page_number']}页: {'符合' if page['compliance'] else '不符合'}标准")
    except Exception as e:
        print(f"处理出错: {str(e)}")

def main():
    """主函数示例"""
    print("=== PDF特征提取器 - 页面选择模式示例 ===\n")
    print(f"项目根目录: {PROJECT_ROOT}")
    print()
    
    # 运行所有示例
    example_first_n_pages()
    print()
    
    example_first_page()
    print()
    
    example_all_pages()
    print()
    
    example_last_n_pages()
    
    print("\n=== 示例完成 ===")

if __name__ == "__main__":
    main()
