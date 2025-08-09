#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示脚本：PDF特征提取工具使用演示
"""

import argparse
import sys
from pathlib import Path
from main import PDFFeatureExtractor


def demo_usage():
    """演示基本使用方法"""
    print("=== PDF特征提取工具演示 ===\n")
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor(
        template_path="templates/mb.png",
        data_dir="data"
    )
    
    print("✓ 特征提取器初始化完成")
    print(f"✓ 模板路径: {extractor.template_path}")
    print(f"✓ 数据保存目录: {extractor.data_dir}")
    
    # 显示当前配置
    print(f"\n当前阈值配置:")
    for key, value in extractor.color_thresholds.items():
        print(f"  {key}: {value}")
    
    print(f"\n特征检测标准:")
    print(f"  1. 白色背景比例 >= {extractor.color_thresholds['bg_ratio_min']*100}%")
    print(f"  2. 黑色文字比例 >= {extractor.color_thresholds['text_ratio_min']*100}%")
    print(f"  3. 整体RGB亮度 >= {extractor.color_thresholds['brightness_min']}")
    print(f"  4. 图像对比度 >= {extractor.color_thresholds['contrast_min']}")
    print(f"  5. 彩色文字比例 <= {extractor.color_thresholds['colored_text_max']*100}%")


def demo_with_folder(folder_path):
    """演示文件夹处理"""
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"❌ 文件夹不存在: {folder_path}")
        return False
    
    print(f"\n=== 处理PDF文件夹: {folder_path} ===")
    
    extractor = PDFFeatureExtractor()
    
    # 处理文件夹
    results = extractor.process_pdf_folder(folder_path, max_pages=3)
    
    if results:
        print(f"\n📊 处理结果汇总:")
        print(f"  文件夹: {results['folder_path']}")
        print(f"  总文件数: {results['total_files']}")
        print(f"  符合标准: {results['summary']['compliant']} 个")
        print(f"  不符合标准: {results['summary']['non_compliant']} 个")
        print(f"  处理错误: {results['summary']['errors']} 个")
        
        # 显示每个文件的详细结果
        print(f"\n📋 详细结果:")
        for result in results['results']:
            status = "✓" if result.get('overall_compliance', False) else "✗"
            print(f"  {status} {result['file_name']}: {'符合标准' if result.get('overall_compliance', False) else '不符合标准'}")
        
        # 保存结果
        output_file = f"demo_analysis_{folder_path.name}.json"
        extractor.save_results(results, output_file)
        print(f"\n💾 结果已保存到: data/{output_file}")
        
        return True
    else:
        print("❌ 处理失败")
        return False


def demo_with_single_file(file_path):
    """演示单文件处理"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    if file_path.suffix.lower() != '.pdf':
        print(f"❌ 不是PDF文件: {file_path}")
        return False
    
    print(f"\n=== 处理单个PDF文件: {file_path} ===")
    
    extractor = PDFFeatureExtractor()
    
    # 处理文件
    result = extractor.process_pdf_file(file_path, max_pages=3)
    
    if result['success']:
        status = "✓ 符合标准" if result['overall_compliance'] else "✗ 不符合标准"
        print(f"\n📊 处理结果: {status}")
        print(f"  文件: {result['file_name']}")
        print(f"  分析页数: {result['pages_analyzed']}")
        
        # 显示每页的结果
        print(f"\n📋 各页面分析:")
        for page_result in result['page_results']:
            page_status = "✓" if page_result['compliance'] else "✗"
            print(f"  {page_status} 第{page_result['page_number']}页: {'符合' if page_result['compliance'] else '不符合'}")
            
            if page_result['features']:
                features = page_result['features']
                print(f"    - 白色背景比例: {features['white_bg_ratio']:.3f}")
                print(f"    - 黑色文字比例: {features['black_text_ratio']:.3f}")
                print(f"    - 对比度: {features['contrast']:.1f}")
        
        # 保存结果
        output_file = f"demo_single_{file_path.stem}.json"
        extractor.save_results(result, output_file)
        print(f"\n💾 结果已保存到: data/{output_file}")
        
        return True
    else:
        print(f"❌ 处理失败: {result.get('error', '未知错误')}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='PDF特征提取工具演示')
    parser.add_argument('path', nargs='?', help='PDF文件或文件夹路径（可选）')
    parser.add_argument('--demo-only', action='store_true', help='仅演示基本功能，不处理文件')
    
    args = parser.parse_args()
    
    # 基本演示
    demo_usage()
    
    if args.demo_only:
        print(f"\n✨ 演示完成！")
        print(f"使用方法:")
        print(f"  python demo.py path/to/file.pdf     # 处理单个PDF文件")
        print(f"  python demo.py path/to/folder/      # 处理PDF文件夹")
        print(f"  python main.py --help               # 查看完整命令行选项")
        return 0
    
    if args.path:
        path = Path(args.path)
        
        if path.is_file():
            success = demo_with_single_file(path)
        elif path.is_dir():
            success = demo_with_folder(path)
        else:
            print(f"❌ 无效路径: {path}")
            success = False
        
        return 0 if success else 1
    else:
        print(f"\n💡 提示:")
        print(f"  要处理PDF文件，请提供文件或文件夹路径:")
        print(f"  python demo.py input_pdfs/")
        print(f"  python demo.py sample.pdf")
        return 0


if __name__ == "__main__":
    sys.exit(main())
