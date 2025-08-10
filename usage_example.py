#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一PDF分析器使用示例
"""

from pdf_analyzer import UnifiedPDFAnalyzer
import os

def example_recursive_mode():
    """示例：递归分类模式"""
    print("=== 递归分类模式示例 ===\n")
    
    # 设置路径（请根据实际情况修改）
    source_folder = "input_pdfs"  # 源文件夹
    target_folder = "jc"          # 目标文件夹
    
    if not os.path.exists(source_folder):
        print(f"❌ 源文件夹不存在: {source_folder}")
        print("请修改 source_folder 为实际存在的文件夹路径")
        return
    
    print(f"源文件夹: {source_folder}")
    print(f"目标文件夹: {target_folder}")
    
    # 创建分析器
    analyzer = UnifiedPDFAnalyzer(source_folder, target_folder)
    
    # 运行递归分类
    print("\n开始递归分类...")
    analyzer.run_analysis(mode="recursive")
    
    print("\n✅ 递归分类完成！")

def example_specific_mode():
    """示例：特定文件分析模式"""
    print("=== 特定文件分析模式示例 ===\n")
    
    # 设置路径（请根据实际情况修改）
    source_folder = "input_pdfs"  # 源文件夹
    target_folder = "jc"          # 目标文件夹
    
    if not os.path.exists(source_folder):
        print(f"❌ 源文件夹不存在: {source_folder}")
        print("请修改 source_folder 为实际存在的文件夹路径")
        return
    
    print(f"源文件夹: {source_folder}")
    print(f"目标文件夹: {target_folder}")
    
    # 创建分析器
    analyzer = UnifiedPDFAnalyzer(source_folder, target_folder)
    
    # 运行特定文件分析
    print("\n开始特定文件分析...")
    results = analyzer.run_analysis(mode="specific")
    
    print(f"\n✅ 特定文件分析完成！")
    print(f"分析了 {len(results)} 个文件")
    print("结果图片已保存到目标文件夹")

def example_programmatic_usage():
    """示例：编程接口使用"""
    print("=== 编程接口使用示例 ===\n")
    
    # 设置路径
    source_folder = "input_pdfs"
    target_folder = "jc"
    
    if not os.path.exists(source_folder):
        print(f"❌ 源文件夹不存在: {source_folder}")
        return
    
    # 创建分析器
    analyzer = UnifiedPDFAnalyzer(source_folder, target_folder)
    
    # 检查统计信息
    print("初始统计信息:")
    print(f"  总PDF文件数: {analyzer.stats['total_pdfs']}")
    print(f"  第一特征通过: {analyzer.stats['first_feature_passed']}")
    print(f"  第二特征通过: {analyzer.stats['second_feature_passed']}")
    print(f"  复制文件数: {analyzer.stats['copied_files']}")
    
    # 可以手动调用各种方法
    print("\n可以手动调用的方法:")
    print("  - analyzer.find_pdf_file(filename)")
    print("  - analyzer.pdf_to_image(pdf_path)")
    print("  - analyzer.check_first_feature(image)")
    print("  - analyzer.check_second_feature(image)")
    print("  - analyzer.detectAnd_visualize_lines(image, filename)")

def main():
    """主函数"""
    print("统一PDF分析器使用示例\n")
    
    # 检查依赖
    try:
        from pdf_analyzer import UnifiedPDFAnalyzer
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 依赖检查失败: {e}")
        print("请确保 pdf_analyzer.py 在同一目录下")
        return
    
    print("\n可用的示例:")
    print("1. 递归分类模式")
    print("2. 特定文件分析模式")
    print("3. 编程接口使用")
    
    # 运行示例
    print("\n" + "="*50)
    example_programmatic_usage()
    
    print("\n" + "="*50)
    print("注意：要运行完整的分析示例，请确保:")
    print("1. 有包含PDF文件的源文件夹")
    print("2. 修改示例中的文件夹路径")
    print("3. 有足够的磁盘空间存储结果")
    
    print("\n命令行使用:")
    print("  python pdf_analyzer.py input_pdfs --mode recursive")
    print("  python pdf_analyzer.py input_pdfs --mode specific")

if __name__ == "__main__":
    main()
