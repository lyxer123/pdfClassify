#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jc.png 详细分析报告
"""

import cv2
import numpy as np
from main import StandardDocumentFeatureExtractor
import os

def analyze_jc_image():
    """
    详细分析 jc.png 图片
    """
    print("jc.png 详细分析报告")
    print("=" * 60)
    
    image_path = "jc.png"
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
    
    # 详细分析底部区域（缺失特征7和9）
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
        for i, (x1, y1, x2, y2) in enumerate(sorted_lines):
            print(f"  横线 {i+1}: 位置({x1}, {y1}) 到 ({x2}, {y2})")
    else:
        print("  未检测到横线")
    
    # 提取特征
    features = extractor.extract_features()
    
    print(f"\n特征检测结果:")
    print(f"  总特征数: {features['total_features']}")
    print(f"  检测到的特征数: {features['detected_features']}")
    print(f"  检测率: {features['detection_rate']:.2%}")
    
    # 详细分析每个特征
    feature_names = [
        ("feature_1_gb_icon", "1. GB图标"),
        ("feature_2_national_standard_text", "2. 中华人民共和国国家标准"),
        ("feature_3_standard_code", "3. 标准文号"),
        ("feature_4_first_horizontal_line", "4. 第一横线"),
        ("feature_5_standard_name", "5. 标准名称"),
        ("feature_6_english_translation", "6. 英文翻译"),
        ("feature_7_publication_date", "7. 发布日期"),
        ("feature_8_second_horizontal_line", "8. 第二横线"),
        ("feature_9_publishing_organization", "9. 发布机构")
    ]
    
    print(f"\n详细特征分析:")
    for feature_key, feature_name in feature_names:
        feature = features['features'][feature_key]
        status = "✓" if feature['detected'] else "✗"
        position = feature['position'] if feature['position'] else "未检测到"
        print(f"  {feature_name}: {status} {position}")
    
    # 分析缺失特征的原因
    print(f"\n缺失特征分析:")
    missing_features = []
    for feature_key, feature_name in feature_names:
        feature = features['features'][feature_key]
        if not feature['detected']:
            missing_features.append(feature_name)
    
    if missing_features:
        print(f"  缺失的特征: {', '.join(missing_features)}")
        print(f"  可能原因:")
        print(f"    - 文本区域检测阈值可能过高")
        print(f"    - 底部区域文本密度较低")
        print(f"    - 图片质量或分辨率影响")
    else:
        print("  所有特征都已检测到")

def main():
    """
    主函数
    """
    analyze_jc_image()

if __name__ == "__main__":
    main() 