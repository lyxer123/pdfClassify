#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析不符合标准的PDF文件
"""

import json

def analyze_non_compliant(file_path):
    """分析不符合标准的PDF文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"=== 储能PDF文件分析结果 ===")
    print(f"总文件数: {data['total_files']}")
    print(f"符合标准: {data['summary']['compliant']}")
    print(f"不符合标准: {data['summary']['non_compliant']}")
    print(f"处理错误: {data['summary']['errors']}")
    
    # 找出不符合标准的文件
    non_compliant = [r for r in data['results'] if not r['overall_compliance']]
    
    print(f"\n❌ 不符合标准的文件 ({len(non_compliant)}个):")
    for i, result in enumerate(non_compliant, 1):
        print(f"\n{i}. {result['file_name']}")
        
        if result['page_results'] and result['page_results'][0]['features']:
            features = result['page_results'][0]['features']
            print(f"   白色背景比例: {features['white_bg_ratio']:.3f}")
            print(f"   黑色文字比例: {features['black_text_ratio']:.3f}")
            print(f"   彩色文字比例: {features['colored_text_ratio']:.3f}")
            print(f"   对比度: {features['contrast']:.1f}")
            brightness = sum(features['mean_rgb'])/3
            print(f"   亮度: {brightness:.1f}")
            
            # 分析不符合的原因
            issues = []
            if features['white_bg_ratio'] < 0.95:
                issues.append(f"白色背景不足({features['white_bg_ratio']:.1%})")
            if features['black_text_ratio'] < 0.011:
                issues.append(f"黑色文字不足({features['black_text_ratio']:.1%})")
            if features['colored_text_ratio'] > 0.05:
                issues.append(f"彩色文字过多({features['colored_text_ratio']:.1%})")
            if features['contrast'] < 29:
                issues.append(f"对比度不足({features['contrast']:.1f})")
            if brightness < 246:
                issues.append(f"亮度不足({brightness:.1f})")
            
            if issues:
                print(f"   ❌ 问题: {', '.join(issues)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_non_compliant(sys.argv[1])
    else:
        analyze_non_compliant('data/energy_storage_fixed_analysis.json')
