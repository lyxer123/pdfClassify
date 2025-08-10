#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试统一PDF分析器
"""

from pdf_analyzer import UnifiedPDFAnalyzer
import os

def test_unified_analyzer():
    """测试统一分析器的基本功能"""
    print("=== 测试统一PDF分析器 ===\n")
    
    # 测试初始化
    source_folder = "input_pdfs"  # 使用现有的测试文件夹
    target_folder = "test_output"
    
    if not os.path.exists(source_folder):
        print(f"❌ 测试文件夹不存在: {source_folder}")
        print("请确保 input_pdfs 文件夹存在并包含一些PDF文件")
        return False
    
    print(f"✓ 源文件夹: {source_folder}")
    print(f"✓ 目标文件夹: {target_folder}")
    
    try:
        # 创建分析器
        analyzer = UnifiedPDFAnalyzer(source_folder, target_folder)
        print("✓ 分析器初始化成功")
        
        # 测试特定文件分析模式
        print("\n--- 测试特定文件分析模式 ---")
        try:
            results = analyzer.run_analysis(mode="specific")
            print(f"✓ 特定文件分析完成，分析了 {len(results)} 个文件")
        except Exception as e:
            print(f"⚠️ 特定文件分析模式测试失败: {e}")
        
        # 测试递归分类模式（如果文件夹中有PDF文件）
        print("\n--- 测试递归分类模式 ---")
        try:
            analyzer.run_analysis(mode="recursive")
            print("✓ 递归分类模式测试完成")
        except Exception as e:
            print(f"⚠️ 递归分类模式测试失败: {e}")
        
        print("\n=== 测试完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_unified_analyzer()
