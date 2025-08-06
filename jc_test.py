#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jc.png 7个特征测试脚本
"""

import cv2
import numpy as np
from main import StandardDocumentFeatureExtractor
import os

def test_jc_image():
    """
    测试 jc.png 是否满足7个特征要求
    """
    print("jc.png 7个特征测试报告")
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
        print("  ✅ 所有7个特征都成功检测到！")
        print("  ✅ 系统表现优秀，检测率达到100%")
        print("  ✅ jc.png 完全满足7个特征要求")
    elif detected_count >= total_count * 0.8:
        print("  ⚠ 大部分特征检测成功，系统表现良好")
        print(f"  ⚠ 检测率: {features['detection_rate']:.2%}")
        print("  ⚠ jc.png 基本满足7个特征要求")
    else:
        print("  ❌ 检测效果不理想，需要优化算法")
        print(f"  ❌ 检测率: {features['detection_rate']:.2%}")
        print("  ❌ jc.png 不完全满足7个特征要求")
    
    # 分析缺失特征
    missing_features = []
    for feature_key, feature_name in feature_names:
        feature = features['features'][feature_key]
        if not feature['detected']:
            missing_features.append(feature_name)
    
    if missing_features:
        print(f"\n缺失的特征: {', '.join(missing_features)}")
        print("可能原因:")
        print("  - 文本区域检测阈值可能过高")
        print("  - 底部区域文本密度较低")
        print("  - 图片质量或分辨率影响")
        print("  - 区域划分需要调整")
    else:
        print(f"\n✅ 所有特征都已检测到，jc.png 完全满足要求！")
    
    print(f"\n总结:")
    print(f"  - 图片: jc.png")
    print(f"  - 尺寸: {width} x {height}")
    print(f"  - 横线数量: {len(horizontal_lines)}")
    print(f"  - 文本区域: {len(text_regions)}")
    print(f"  - 检测率: {features['detection_rate']:.2%}")
    print(f"  - 是否满足要求: {'是' if detected_count == total_count else '否'}")

def main():
    """
    主函数
    """
    test_jc_image()

if __name__ == "__main__":
    main() 