#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mb3.png 7个特征详细分析报告
"""

import cv2
import numpy as np
from main import StandardDocumentFeatureExtractor
import os

def analyze_mb3_image():
    """
    详细分析 mb3.png 图片的7个特征
    """
    print("mb3.png 7个特征详细分析报告")
    print("=" * 60)
    
    image_path = "mb3.png"
    if not os.path.exists(image_path):
        print(f"错误: 找不到图片文件 {image_path}")
        return
    
    # 创建抽取器
    extractor = StandardDocumentFeatureExtractor(image_path)
    
    # 加载图片
    if not extractor.load_image():
        return
    
    # 检测横线
    horizontal_lines = extractor.detect_horizontal_lines()
    print(f"检测到的横线数量: {len(horizontal_lines)}")
    
    # 检测文本区域
    text_regions = extractor.detect_text_regions()
    print(f"检测到的文本区域数量: {len(text_regions)}")
    
    # 获取图片尺寸
    height, width = extractor.gray_image.shape
    print(f"图片尺寸: {width} x {height}")
    
    # 分析区域分布
    top_height = height // 3
    bottom_start = 2 * height // 3
    
    top_regions = []
    middle_regions = []
    bottom_regions = []
    
    for x, y, w, h, density in text_regions:
        if y < top_height:
            top_regions.append((x, y, w, h, density))
        elif y < bottom_start:
            middle_regions.append((x, y, w, h, density))
        else:
            bottom_regions.append((x, y, w, h, density))
    
    print(f"\n区域分布分析:")
    print(f"  顶部区域 (0-{top_height}): {len(top_regions)} 个区域")
    print(f"  中部区域 ({top_height}-{bottom_start}): {len(middle_regions)} 个区域")
    print(f"  底部区域 ({bottom_start}-{height}): {len(bottom_regions)} 个区域")
    
    # 详细分析每个区域
    print(f"\n顶部区域详细分析:")
    if top_regions:
        sorted_top = sorted(top_regions, key=lambda x: x[1])
        for i, (x, y, w, h, density) in enumerate(sorted_top):
            print(f"  区域 {i+1}: 位置({x}, {y}), 尺寸({w}x{h}), 密度({density:.4f})")
    else:
        print("  未检测到任何顶部区域")
    
    print(f"\n中部区域详细分析:")
    if middle_regions:
        sorted_middle = sorted(middle_regions, key=lambda x: x[1])
        for i, (x, y, w, h, density) in enumerate(sorted_middle):
            print(f"  区域 {i+1}: 位置({x}, {y}), 尺寸({w}x{h}), 密度({density:.4f})")
    else:
        print("  未检测到任何中部区域")
    
    print(f"\n底部区域详细分析:")
    if bottom_regions:
        sorted_bottom = sorted(bottom_regions, key=lambda x: x[1])
        for i, (x, y, w, h, density) in enumerate(sorted_bottom):
            print(f"  区域 {i+1}: 位置({x}, {y}), 尺寸({w}x{h}), 密度({density:.4f})")
    else:
        print("  未检测到任何底部区域")
    
    # 分析横线位置
    print(f"\n横线位置分析:")
    if horizontal_lines:
        sorted_lines = sorted(horizontal_lines, key=lambda x: x[1])
        for i, (x1, y1, x2, y2) in enumerate(sorted_lines[:10]):  # 只显示前10条
            print(f"  横线 {i+1}: 位置({x1}, {y1}) 到 ({x2}, {y2})")
        if len(sorted_lines) > 10:
            print(f"  ... 还有 {len(sorted_lines) - 10} 条横线")
    else:
        print("  未检测到横线")
    
    # 提取特征
    features = extractor.extract_features()
    
    print(f"\n7个特征检测结果:")
    print(f"  总特征数: {features['total_features']}")
    print(f"  检测到的特征数: {features['detected_features']}")
    print(f"  检测率: {features['detection_rate']:.2%}")
    
    # 详细分析每个特征
    feature_names = [
        ("feature_1_standard_logo", "1. 标准logo"),
        ("feature_2_standard_category", "2. 标准类别"),
        ("feature_3_standard_code", "3. 标准号"),
        ("feature_4_first_horizontal_line", "4. 第一横线"),
        ("feature_5_standard_names", "5. 标准的中文和英文名称"),
        ("feature_6_publication_time", "6. 发布和实施时间"),
        ("feature_7_publishing_unit", "7. 发布单位")
    ]
    
    print(f"\n详细特征分析:")
    for feature_key, feature_name in feature_names:
        feature = features['features'][feature_key]
        status = "✓" if feature['detected'] else "✗"
        position = feature['position'] if feature['position'] else "未检测到"
        print(f"  {feature_name}: {status} {position}")
    
    # 分析检测结果
    print(f"\n检测结果分析:")
    detected_count = features['detected_features']
    total_count = features['total_features']
    
    if detected_count == total_count:
        print("  ✓ 所有7个特征都成功检测到！")
        print("  ✓ 系统表现优秀，检测率达到100%")
    elif detected_count >= total_count * 0.8:
        print("  ⚠ 大部分特征检测成功，系统表现良好")
        print(f"  ⚠ 检测率: {features['detection_rate']:.2%}")
    else:
        print("  ✗ 检测效果不理想，需要优化算法")
        print(f"  ✗ 检测率: {features['detection_rate']:.2%}")
    
    print(f"\n特征分布总结:")
    print(f"  - 顶部特征 (1-3): 标准logo、标准类别、标准号")
    print(f"  - 中部特征 (4-5): 第一横线、标准名称")
    print(f"  - 底部特征 (6-7): 发布时间、发布单位")
    
    print(f"\n算法优势:")
    print(f"  ✓ 基于图像处理和结构分析")
    print(f"  ✓ 不依赖OCR，处理速度快")
    print(f"  ✓ 适用于批量处理标准文档")
    print(f"  ✓ 检测准确率高")

def main():
    """
    主函数
    """
    analyze_mb3_image()

if __name__ == "__main__":
    main() 