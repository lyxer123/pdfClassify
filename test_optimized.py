#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化版标准文档分类系统
"""

import os
from main_optimized import OptimizedStandardDocumentFeatureExtractor

def test_mb5_analysis():
    """测试mb5.png的分析"""
    print("=" * 60)
    print("测试mb5.png分析")
    print("=" * 60)
    
    if not os.path.exists("mb5.png"):
        print("❌ mb5.png文件不存在")
        return
    
    extractor = OptimizedStandardDocumentFeatureExtractor("mb5.png")
    result = extractor.extract_features()
    
    if 'error' in result:
        print(f"❌ 分析失败: {result['error']}")
        return
    
    print(f"✅ 分析成功!")
    print(f"标准文档判断: {'✅ 是' if result['is_standard_document'] else '❌ 否'}")
    print(f"综合评分: {result['overall_score']:.3f}")
    print(f"mb4相似度: {result['mb4_similarity']:.3f}")
    
    print(f"\n区域分析:")
    for region_name, analysis in result['region_analysis'].items():
        region_name_cn = {'upper': '上部', 'middle': '中部', 'lower': '下部'}[region_name]
        print(f"  {region_name_cn}:")
        print(f"    留白比例: {analysis['whitespace_ratio']:.3f}")
        print(f"    关键词检测: {'✅' if analysis['has_keywords'] else '❌'}")
        if analysis['text'].strip():
            print(f"    提取文字: {analysis['text'][:100]}...")

def test_mb4_analysis():
    """测试mb4.png的分析"""
    print(f"\n{'='*60}")
    print("测试mb4.png分析")
    print("=" * 60)
    
    if not os.path.exists("mb4.png"):
        print("❌ mb4.png文件不存在")
        return
    
    extractor = OptimizedStandardDocumentFeatureExtractor("mb4.png")
    result = extractor.extract_features()
    
    if 'error' in result:
        print(f"❌ 分析失败: {result['error']}")
        return
    
    print(f"✅ 分析成功!")
    print(f"标准文档判断: {'✅ 是' if result['is_standard_document'] else '❌ 否'}")
    print(f"综合评分: {result['overall_score']:.3f}")
    print(f"mb4相似度: {result['mb4_similarity']:.3f}")

def test_blue_box_detection():
    """测试蓝色框检测功能"""
    print(f"\n{'='*60}")
    print("测试蓝色框检测")
    print("=" * 60)
    
    if not os.path.exists("mb5.png"):
        print("❌ mb5.png文件不存在")
        return
    
    extractor = OptimizedStandardDocumentFeatureExtractor("mb5.png")
    if not extractor.load_image():
        print("❌ 无法加载图片")
        return
    
    blue_boxes = extractor.detect_blue_boxes()
    print(f"✅ 检测到 {len(blue_boxes)} 个蓝色框:")
    
    for region_name, box_info in blue_boxes.items():
        print(f"  {region_name}: x={box_info.get('x', 0)}, y={box_info.get('y', 0)}, "
              f"w={box_info.get('w', 0)}, h={box_info.get('h', 0)}")

def test_whitespace_calculation():
    """测试留白比例计算"""
    print(f"\n{'='*60}")
    print("测试留白比例计算")
    print("=" * 60)
    
    if not os.path.exists("mb5.png"):
        print("❌ mb5.png文件不存在")
        return
    
    extractor = OptimizedStandardDocumentFeatureExtractor("mb5.png")
    if not extractor.load_image():
        print("❌ 无法加载图片")
        return
    
    blue_boxes = extractor.detect_blue_boxes()
    
    for region_name, box_info in blue_boxes.items():
        whitespace_ratio = extractor.calculate_whitespace_ratio(box_info)
        region_name_cn = {'upper': '上部', 'middle': '中部', 'lower': '下部'}[region_name]
        print(f"  {region_name_cn}: 留白比例 = {whitespace_ratio:.3f}")

def test_text_extraction():
    """测试文字提取功能"""
    print(f"\n{'='*60}")
    print("测试文字提取")
    print("=" * 60)
    
    if not os.path.exists("mb5.png"):
        print("❌ mb5.png文件不存在")
        return
    
    extractor = OptimizedStandardDocumentFeatureExtractor("mb5.png")
    if not extractor.load_image():
        print("❌ 无法加载图片")
        return
    
    blue_boxes = extractor.detect_blue_boxes()
    
    for region_name, box_info in blue_boxes.items():
        text = extractor.extract_text_from_region(box_info)
        region_name_cn = {'upper': '上部', 'middle': '中部', 'lower': '下部'}[region_name]
        print(f"  {region_name_cn}:")
        if text.strip():
            print(f"    提取文字: {text[:100]}...")
        else:
            print(f"    提取文字: (无文字)")

def main():
    """主测试函数"""
    print("PDF标准文档分类系统 - 优化版测试")
    print("基于mb5.png的3个蓝色框区域分析")
    
    # 测试各个功能
    test_blue_box_detection()
    test_whitespace_calculation()
    test_text_extraction()
    test_mb5_analysis()
    test_mb4_analysis()
    
    print(f"\n{'='*60}")
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
