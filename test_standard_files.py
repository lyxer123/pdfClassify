#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试标准文件检测效果
"""

from pdf_processor import PDFProcessor
from pathlib import Path
import os

def test_standard_files():
    """测试标准文件检测"""
    print("PDF标准文档检测测试")
    print("=" * 50)
    
    # 创建处理器
    processor = PDFProcessor()
    
    # 获取PDF文件列表
    pdf_files = processor.get_pdf_files()
    
    if not pdf_files:
        print("未找到PDF文件")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    # 只测试前5个文件
    test_files = pdf_files[:5]
    
    results = []
    
    for i, pdf_path in enumerate(test_files, 1):
        print(f"\n{'='*60}")
        print(f"测试文件 {i}/{len(test_files)}: {pdf_path.name}")
        print(f"{'='*60}")
        
        result = processor.process_pdf(pdf_path)
        results.append({
            'file': pdf_path.name,
            'success': result['success'],
            'copied': result['copied'],
            'features': result.get('features', 0),
            'confidence': result.get('confidence', 0.0),
            'template_similarity': result.get('template_similarity', 0.0)
        })
        
        if result['copied']:
            print(f"✅ 文件被识别为标准文档")
        else:
            print(f"❌ 文件未被识别为标准文档")
    
    # 统计结果
    print(f"\n{'='*60}")
    print("测试结果统计")
    print(f"{'='*60}")
    
    total_files = len(results)
    copied_files = sum(1 for r in results if r['copied'])
    success_rate = copied_files / total_files * 100
    
    print(f"总文件数: {total_files}")
    print(f"成功识别: {copied_files}")
    print(f"识别率: {success_rate:.1f}%")
    
    print(f"\n详细结果:")
    for result in results:
        status = "✅" if result['copied'] else "❌"
        print(f"  {status} {result['file']} - 特征数: {result['features']}/7, 置信度: {result['confidence']:.2f}, 模板相似度: {result['template_similarity']:.3f}")
    
    # 如果识别率不高，建议调整参数
    if success_rate < 80:
        print(f"\n⚠️  识别率较低 ({success_rate:.1f}%)，建议调整检测参数:")
        print(f"  1. 降低特征数量要求（当前>=5个）")
        print(f"  2. 降低位置符合度阈值（当前>0.7）")
        print(f"  3. 降低模板相似度阈值（当前>0.3）")
        print(f"  4. 调整关键特征要求")

if __name__ == "__main__":
    test_standard_files() 