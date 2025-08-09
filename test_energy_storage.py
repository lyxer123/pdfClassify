#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试储能标准PDF文件
"""

import os
import sys
from pathlib import Path
from main import PDFFeatureExtractor

def test_energy_storage_pdfs():
    """测试储能文件夹下的PDF文件"""
    print("=== 测试储能标准PDF文件 ===\n")
    
    folder_path = Path("F:/标准规范要求/储能")
    if not folder_path.exists():
        print(f"❌ 文件夹不存在: {folder_path}")
        return
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor()
    
    print("当前优化后的参数:")
    for key, value in extractor.color_thresholds.items():
        print(f"  {key}: {value}")
    
    # 查找PDF文件
    pdf_files_lower = list(folder_path.glob("*.pdf"))
    pdf_files_upper = list(folder_path.glob("*.PDF"))
    pdf_files = list(set(pdf_files_lower + pdf_files_upper))
    
    print(f"\n找到 {len(pdf_files)} 个PDF文件")
    
    # 测试前10个文件
    test_files = pdf_files[:10]
    print(f"测试前 {len(test_files)} 个文件:\n")
    
    compliant_count = 0
    results = []
    
    for i, pdf_file in enumerate(test_files, 1):
        try:
            print(f"正在处理 {i}/{len(test_files)}: {pdf_file.name}")
            result = extractor.process_pdf_file(pdf_file, max_pages=1)
            
            if result['success']:
                compliance = result['overall_compliance']
                if compliance:
                    compliant_count += 1
                    status = "✅ 符合"
                else:
                    status = "❌ 不符合"
                
                # 获取特征信息
                if result['page_results'] and result['page_results'][0]['features']:
                    features = result['page_results'][0]['features']
                    feature_info = f"(白背景:{features['white_bg_ratio']:.1%}, 黑文字:{features['black_text_ratio']:.1%}, 对比度:{features['contrast']:.1f}, 亮度:{sum(features['mean_rgb'])/3:.1f})"
                else:
                    feature_info = "(特征分析失败)"
                
                print(f"  {status} {feature_info}")
                
                results.append({
                    'file_name': pdf_file.name,
                    'compliance': compliance,
                    'features': result['page_results'][0]['features'] if result['page_results'] else None
                })
            else:
                print(f"  ❌ 处理失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")
        
        print()  # 空行分隔
    
    # 汇总结果
    print(f"📊 测试结果汇总:")
    print(f"  测试文件数: {len(test_files)}")
    print(f"  符合标准: {compliant_count}")
    print(f"  不符合标准: {len(results) - compliant_count}")
    print(f"  符合率: {compliant_count/len(results)*100:.1f}%" if results else "  符合率: 0%")
    
    # 分析不符合的原因
    non_compliant = [r for r in results if not r['compliance']]
    if non_compliant:
        print(f"\n❌ 不符合标准的文件分析:")
        for result in non_compliant:
            print(f"  - {result['file_name']}")
            if result['features']:
                f = result['features']
                issues = []
                if f['white_bg_ratio'] < extractor.color_thresholds['bg_ratio_min']:
                    issues.append(f"白背景不足({f['white_bg_ratio']:.1%})")
                if f['black_text_ratio'] < extractor.color_thresholds['text_ratio_min']:
                    issues.append(f"黑文字不足({f['black_text_ratio']:.1%})")
                if f['contrast'] < extractor.color_thresholds['contrast_min']:
                    issues.append(f"对比度不足({f['contrast']:.1f})")
                brightness = sum(f['mean_rgb'])/3
                if brightness < extractor.color_thresholds['brightness_min']:
                    issues.append(f"亮度不足({brightness:.1f})")
                
                if issues:
                    print(f"    问题: {', '.join(issues)}")
    
    return results

if __name__ == "__main__":
    test_energy_storage_pdfs()
