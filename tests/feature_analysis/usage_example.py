#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例：PDF特征提取工具
"""

from main import PDFFeatureExtractor
from pathlib import Path

def example_usage():
    """使用示例"""
    
    # 创建特征提取器实例
    extractor = PDFFeatureExtractor(
        template_path="templates/mb.png",  # 标准模板路径
        data_dir="data"                    # 特征数据保存目录
    )
    
    # 示例1：处理单个PDF文件
    print("=== 示例1：处理单个PDF文件 ===")
    pdf_file = "input_pdfs/sample.pdf"  # 替换为实际的PDF文件路径
    if Path(pdf_file).exists():
        result = extractor.process_pdf_file(pdf_file, max_pages=3)
        print(f"处理结果：{'符合标准' if result.get('overall_compliance') else '不符合标准'}")
        
        # 保存结果
        extractor.save_results(result, "single_file_result.json")
    else:
        print(f"文件不存在: {pdf_file}")
    
    # 示例2：处理整个PDF文件夹
    print("\n=== 示例2：处理PDF文件夹 ===")
    pdf_folder = "input_pdfs"  # PDF文件夹路径
    if Path(pdf_folder).exists():
        results = extractor.process_pdf_folder(pdf_folder, max_pages=5)
        
        if results:
            print(f"文件夹：{results['folder_path']}")
            print(f"总文件数：{results['total_files']}")
            print(f"符合标准：{results['summary']['compliant']}")
            print(f"不符合标准：{results['summary']['non_compliant']}")
            print(f"处理错误：{results['summary']['errors']}")
            
            # 保存结果
            extractor.save_results(results, "folder_analysis_result.json")
    else:
        print(f"文件夹不存在: {pdf_folder}")

if __name__ == "__main__":
    example_usage()
