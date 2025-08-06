#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试指定路径下的PDF文件
"""

from pathlib import Path
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_specific_path():
    """测试指定路径下的PDF文件"""
    print("测试指定路径下的PDF文件")
    print("=" * 60)
    
    # 指定路径
    target_path = "E:\\1T硬盘D\\2个项目资料\\充电控制器\\办公\\国网控制器\\国网2.0控制器\\国网六统一\\发布版"
    
    print(f"目标路径: {target_path}")
    
    # 检查路径是否存在
    path = Path(target_path)
    if not path.exists():
        print(f"❌ 路径不存在: {target_path}")
        return
    
    print(f"✅ 路径存在")
    
    # 查找PDF文件
    try:
        pdf_files = list(path.rglob("*.pdf"))
        print(f"✅ 找到 {len(pdf_files)} 个PDF文件")
        
        if not pdf_files:
            print("❌ 未找到PDF文件")
            return
        
        # 显示前几个文件
        print("\n前5个PDF文件:")
        for i, pdf_file in enumerate(pdf_files[:5], 1):
            print(f"  {i}. {pdf_file.name}")
        
        # 创建处理器并测试
        processor = PDFProcessor(source_drive=target_path)
        
        # 测试前3个文件
        test_files = pdf_files[:3]
        results = []
        
        print(f"\n{'='*60}")
        print("开始测试PDF文件")
        print(f"{'='*60}")
        
        for i, pdf_path in enumerate(test_files, 1):
            print(f"\n测试文件 {i}/{len(test_files)}: {pdf_path.name}")
            print(f"完整路径: {pdf_path}")
            
            try:
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
                    
            except Exception as e:
                print(f"❌ 处理文件时出错: {e}")
                results.append({
                    'file': pdf_path.name,
                    'success': False,
                    'copied': False,
                    'features': 0,
                    'confidence': 0.0,
                    'template_similarity': 0.0
                })
        
        # 统计结果
        print(f"\n{'='*60}")
        print("测试结果统计")
        print(f"{'='*60}")
        
        total_files = len(results)
        copied_files = sum(1 for r in results if r['copied'])
        success_rate = copied_files / total_files * 100 if total_files > 0 else 0
        
        print(f"总文件数: {total_files}")
        print(f"成功识别: {copied_files}")
        print(f"识别率: {success_rate:.1f}%")
        
        print(f"\n详细结果:")
        for result in results:
            status = "✅" if result['copied'] else "❌"
            print(f"  {status} {result['file']} - 特征数: {result['features']}/7, 置信度: {result['confidence']:.2f}, 模板相似度: {result['template_similarity']:.3f}")
        
        if success_rate >= 80:
            print(f"\n🎉 检测效果良好！识别率: {success_rate:.1f}%")
        elif success_rate >= 50:
            print(f"\n⚠️  检测效果一般，识别率: {success_rate:.1f}%")
        else:
            print(f"\n❌ 检测效果较差，识别率: {success_rate:.1f}%")
            print("建议进一步调整检测参数")
        
    except Exception as e:
        print(f"❌ 搜索PDF文件时出错: {e}")

if __name__ == "__main__":
    test_specific_path() 