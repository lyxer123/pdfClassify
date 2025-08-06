#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试调整后的参数
"""

from pdf_processor import PDFProcessor
from pathlib import Path

def test_adjusted_parameters():
    """测试调整后的参数"""
    print("测试调整后的检测参数")
    print("=" * 50)
    
    # 创建处理器
    processor = PDFProcessor()
    
    # 获取PDF文件列表
    pdf_files = processor.get_pdf_files()
    
    if not pdf_files:
        print("未找到PDF文件")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    # 测试前5个文件
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
    
    if success_rate >= 80:
        print(f"\n🎉 调整后的参数效果良好！识别率: {success_rate:.1f}%")
    else:
        print(f"\n⚠️  识别率仍然较低 ({success_rate:.1f}%)，可能需要进一步调整参数")

if __name__ == "__main__":
    test_adjusted_parameters() 