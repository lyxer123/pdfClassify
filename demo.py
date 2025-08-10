#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一PDF分析器演示脚本
演示所有可用的功能和用法
"""

import os
import sys
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖是否完整"""
    print("🔍 检查依赖...")
    
    try:
        import fitz  # PyMuPDF
        print("✅ PyMuPDF (fitz)")
    except ImportError:
        print("❌ PyMuPDF (fitz) - 请安装: pip install PyMuPDF")
        return False
    
    try:
        import cv2
        print("✅ OpenCV (cv2)")
    except ImportError:
        print("❌ OpenCV (cv2) - 请安装: pip install opencv-python")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy")
    except ImportError:
        print("❌ NumPy - 请安装: pip install numpy")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow (PIL)")
    except ImportError:
        print("❌ Pillow (PIL) - 请安装: pip install Pillow")
        return False
    
    try:
        from pdf_analyzer import UnifiedPDFAnalyzer
        print("✅ 统一PDF分析器")
    except ImportError as e:
        print(f"❌ 统一PDF分析器: {e}")
        return False
    
    print("✅ 所有依赖检查通过！\n")
    return True

def create_test_structure():
    """创建测试目录结构"""
    print("📁 创建测试目录结构...")
    
    # 创建测试目录
    test_dirs = ["input_pdfs", "jc", "test_output"]
    for dir_name in test_dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ 创建目录: {dir_name}")
    
    print()

def demonstrate_analyzer_creation():
    """演示分析器创建"""
    print("🔧 演示分析器创建...")
    
    try:
        from pdf_analyzer import UnifiedPDFAnalyzer
        
        # 创建分析器实例
        analyzer = UnifiedPDFAnalyzer("input_pdfs", "jc")
        print("✅ 分析器创建成功")
        
        # 显示初始统计信息
        print("📊 初始统计信息:")
        for key, value in analyzer.stats.items():
            print(f"  {key}: {value}")
        
        print()
        return analyzer
        
    except Exception as e:
        print(f"❌ 分析器创建失败: {e}")
        return None

def demonstrate_file_search(analyzer):
    """演示文件搜索功能"""
    print("🔍 演示文件搜索功能...")
    
    if not analyzer:
        print("❌ 分析器未初始化")
        return
    
    # 测试文件名搜索
    test_filenames = [
        "test.pdf",
        "充电控制器.pdf",
        "mb_template.pdf"
    ]
    
    for filename in test_filenames:
        result = analyzer.find_pdf_file(filename)
        if result:
            print(f"✅ 找到文件: {filename} -> {result}")
        else:
            print(f"❌ 未找到文件: {filename}")
    
    print()

def demonstrate_feature_extraction():
    """演示特征提取功能"""
    print("🔬 演示特征提取功能...")
    
    try:
        from main import PDFFeatureExtractor
        
        # 创建特征提取器
        extractor = PDFFeatureExtractor()
        print("✅ 特征提取器创建成功")
        
        # 显示配置信息
        print("⚙️ 特征提取配置:")
        for key, value in extractor.color_thresholds.items():
            print(f"  {key}: {value}")
        
        print()
        
    except Exception as e:
        print(f"❌ 特征提取器创建失败: {e}")
        print()

def demonstrate_analysis_modes():
    """演示分析模式"""
    print("🎯 演示分析模式...")
    
    print("可用的分析模式:")
    print("1. 递归分类模式 (recursive)")
    print("   - 自动扫描整个文件夹")
    print("   - 进行两阶段特征验证")
    print("   - 复制符合条件的文件")
    
    print("2. 特定文件分析模式 (specific)")
    print("   - 分析指定文件")
    print("   - 生成可视化结果")
    print("   - 保存分析图片")
    
    print()

def demonstrate_command_line_usage():
    """演示命令行用法"""
    print("💻 演示命令行用法...")
    
    print("基本用法:")
    print("  python pdf_analyzer.py <源文件夹> [选项]")
    
    print("\n选项:")
    print("  --target, -t <目标文件夹>    指定目标文件夹 (默认: jc)")
    print("  --mode, -m <模式>           指定分析模式 (recursive/specific)")
    print("  --verbose, -v               详细输出模式")
    
    print("\n示例:")
    print("  # 递归分类模式")
    print("  python pdf_analyzer.py input_pdfs --mode recursive")
    
    print("  # 特定文件分析模式")
    print("  python pdf_analyzer.py input_pdfs --mode specific")
    
    print("  # 指定目标文件夹")
    print("  python pdf_analyzer.py input_pdfs --target output --mode recursive")
    
    print()

def demonstrate_programmatic_usage():
    """演示编程接口用法"""
    print("🐍 演示编程接口用法...")
    
    print("基本用法:")
    print("""
from pdf_analyzer import UnifiedPDFAnalyzer

# 创建分析器
analyzer = UnifiedPDFAnalyzer("input_pdfs", "jc")

# 运行递归分类
analyzer.run_analysis(mode="recursive")

# 运行特定文件分析
results = analyzer.run_analysis(mode="specific")

# 手动调用方法
pdf_path = analyzer.find_pdf_file("filename.pdf")
if pdf_path:
    image = analyzer.pdf_to_image(pdf_path)
    first_pass = analyzer.check_first_feature(image)
    second_pass = analyzer.check_second_feature(image)
    analyzer.detectAnd_visualize_lines(image, "filename")
""")
    
    print()

def demonstrate_error_handling():
    """演示错误处理"""
    print("⚠️ 演示错误处理...")
    
    print("常见错误及解决方案:")
    print("1. 文件夹不存在")
    print("   - 确保源文件夹路径正确")
    print("   - 检查文件夹权限")
    
    print("2. PDF文件损坏")
    print("   - 尝试重新下载文件")
    print("   - 使用其他PDF阅读器验证")
    
    print("3. 内存不足")
    print("   - 减少同时处理的文件数量")
    print("   - 降低图像分辨率")
    
    print("4. 依赖缺失")
    print("   - 运行: pip install -r requirements.txt")
    print("   - 检查Python版本兼容性")
    
    print()

def main():
    """主函数"""
    print("🚀 统一PDF分析器演示脚本")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，请先安装缺失的包")
        return
    
    # 创建测试结构
    create_test_structure()
    
    # 演示各种功能
    demonstrate_analyzer_creation()
    demonstrate_file_search(None)  # 暂时跳过，因为没有PDF文件
    demonstrate_feature_extraction()
    demonstrate_analysis_modes()
    demonstrate_command_line_usage()
    demonstrate_programmatic_usage()
    demonstrate_error_handling()
    
    print("=" * 50)
    print("🎉 演示完成！")
    print("\n下一步:")
    print("1. 将PDF文件放入 input_pdfs 文件夹")
    print("2. 运行: python pdf_analyzer.py input_pdfs --mode recursive")
    print("3. 或运行: python usage_example.py")
    print("4. 查看 jc 文件夹中的结果")

if __name__ == "__main__":
    main()
