#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试统一PDF分析器
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

from pdf_analyzer import UnifiedPDFAnalyzer

def test_unified_analyzer():
    """测试统一分析器的基本功能"""
    print("=== 测试统一PDF分析器 ===\n")
    
    # 测试初始化
    source_folder = str(PROJECT_ROOT / "input_pdfs")  # 使用项目根目录下的input_pdfs
    target_folder = str(PROJECT_ROOT / "test_output")
    
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
